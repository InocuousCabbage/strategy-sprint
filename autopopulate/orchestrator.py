"""Orchestrator: turn a confirmed exercise sidecar into a folder of filled COPIES.

Shape of a run:

1. Load the sidecar and gate on ``confirmedByClient``. This happens BEFORE any
   file is touched, so an unconfirmed exercise writes nothing at all.
2. Mirror every file under ``templates_root`` into ``output_dir``, preserving the
   folder tree. Originals are only ever read.
3. Files the fill-map covers for this exercise get their engines applied to the
   COPY. Everything else is left exactly as it came.
4. Anything not fully filled is RECORDED — in the run's fill report and in a
   ``.FILL-MANUALLY.txt`` beside the file. Never fabricate, never fail the whole
   run over one field, and never let a skip go unmentioned.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from autopopulate.engines.docx import (
    fill_docx_token_counts,
    fill_docx_under_heading,
    set_docx_dropdown,
)
from autopopulate.engines.xlsx import fill_xlsx
from autopopulate.models import CellTarget, FileFillSpec, PopulateResult
from autopopulate.fillmap import resolve_fills
from autopopulate.manifest_watch import exercises_now_complete
from autopopulate.sidecar import SidecarError, load_sidecar

FLAG_SUFFIX = ".FILL-MANUALLY.txt"
#: Records which templates each exercise has already filled in this output_dir, so
#: a re-run neither re-fills a copy nor reports its already-consumed tokens as
#: missing. Without it, running the same exercise twice flags correctly-filled
#: files for manual attention — a fabricated skip, as damaging as a hidden one.
STATE_FILE = ".autopopulate-state.json"
NO_SOURCE = "no sprint source yet — fill manually"


def _apply_spec(copy_path: Path, spec: FileFillSpec) -> tuple[int, list[str]]:
    """Run one file's engine over its COPY. Returns (fills_made, warnings).

    An engine refusing a target (heading absent, dropdown option not allowed,
    merged cell, sheet missing) is a REPORTABLE skip, not a crash: the rest of
    the run must still produce output, and the consultant must still be told.
    """
    warnings: list[str] = []
    made = 0

    if spec.engine == "docx-token":
        tokens = {t.dest: str(t.value) for t in spec.targets}
        if tokens:
            counts = fill_docx_token_counts(copy_path, tokens)
            made = sum(counts.values())
            for t in spec.targets:
                if counts.get(t.dest, 0) == 0:
                    warnings.append(
                        f"{spec.template}: left token {t.dest!r} unfilled — the token "
                        f"does not appear in the template (source {t.source!r})"
                    )

    elif spec.engine == "docx-heading":
        for t in spec.targets:
            if fill_docx_under_heading(copy_path, t.dest, str(t.value)):
                made += 1
            else:
                warnings.append(
                    f"{spec.template}: left heading {t.dest!r} unfilled — no such "
                    f"heading with a blank paragraph beneath it (source {t.source!r})"
                )

    elif spec.engine == "docx-dropdown":
        for t in spec.targets:
            try:
                filled = set_docx_dropdown(copy_path, t.dest, str(t.value))
            except Exception as exc:
                warnings.append(
                    f"{spec.template}: left dropdown {t.dest!r} unfilled — {exc}"
                )
                continue
            if filled:
                made += 1
            else:
                warnings.append(
                    f"{spec.template}: left dropdown {t.dest!r} unfilled — no content "
                    f"control with that alias (source {t.source!r})"
                )

    elif spec.engine == "xlsx":
        cells = [CellTarget(t.dest, t.value) for t in spec.targets]
        if cells:
            try:
                made = fill_xlsx(copy_path, spec.sheet, cells)
            except Exception:
                # Batch is all-or-nothing by design; retry per target so one bad
                # cell cannot cost the good ones, and each failure is named.
                made = 0
                for t in spec.targets:
                    try:
                        made += fill_xlsx(copy_path, spec.sheet, [CellTarget(t.dest, t.value)])
                    except Exception as exc:
                        warnings.append(
                            f"{spec.template}: left {spec.sheet}!{t.dest} unfilled — "
                            f"{exc} (source {t.source!r})"
                        )
    else:  # pragma: no cover - load_fillmap rejects unknown engines
        warnings.append(f"{spec.template}: no engine for {spec.engine!r}")

    return made, warnings


def _remove_flag(copy_path: Path) -> None:
    """Drop any existing flag for a file we are about to re-evaluate.

    Flags are rewritten from scratch after every pass over a file, so a flag can
    never describe a skip that has since been resolved.
    """
    flag = copy_path.with_suffix(copy_path.suffix + FLAG_SUFFIX)
    if flag.is_file():
        flag.unlink()


def _load_state(out: Path) -> dict:
    p = out / STATE_FILE
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(out: Path, state: dict) -> None:
    (out / STATE_FILE).write_text(
        json.dumps(state, indent=2, sort_keys=True), encoding="utf-8"
    )


def _write_flag(copy_path: Path, lines: list[str]) -> Path:
    flag = copy_path.with_suffix(copy_path.suffix + FLAG_SUFFIX)
    flag.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return flag


def _write_report(out: Path, result: PopulateResult) -> Path:
    report = out / f"{result.exercise_id}.fill-report.md"
    lines = [
        f"# Fill report — {result.exercise_id}",
        "",
        f"Filled: {len(result.filled)} · copied as-is: {len(result.copied_blank)} · "
        f"carried over: {len(result.carried_over)} · "
        f"unfilled fields: {len(result.warnings)}",
        "",
        "## Filled from the sprint",
        "",
    ]
    lines += [f"- {f}" for f in result.filled] or ["- (none)"]
    lines += ["", "## Copied as-is — no sprint source yet, fill manually", ""]
    lines += [f"- {f}" for f in result.copied_blank] or ["- (none)"]
    lines += ["", "## Carried over from an earlier exercise in this phase", ""]
    lines += [f"- {f}" for f in result.carried_over] or ["- (none)"]
    lines += ["", "## Not filled — needs a human", ""]
    lines += [f"- {w}" for w in result.warnings] or ["- (none)"]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def populate_phase(
    artifact_dir: str | Path,
    exercise_id: str,
    output_dir: str | Path,
    templates_root: str | Path,
    fillmap_path: str | Path | None = None,
) -> PopulateResult:
    """Fill COPIES of this exercise's templates into ``output_dir``."""
    artifact_dir = Path(artifact_dir)
    out = Path(output_dir)
    templates_root = Path(templates_root)

    # Gate FIRST: an unconfirmed exercise must leave output_dir untouched.
    sidecar = load_sidecar(artifact_dir / "output" / f"{exercise_id}.yaml")

    specs = resolve_fills(exercise_id, sidecar, fillmap_path=fillmap_path)
    # A template can need MORE THAN ONE engine — the Positioning doc takes both a
    # heading fill and its two dropdown content controls. Keying by template in a
    # plain dict would drop all but the last, so specs are grouped into a list.
    by_template: dict[str, list[FileFillSpec]] = {}
    for s in specs:
        by_template.setdefault(s.template, []).append(s)

    result = PopulateResult(exercise_id=exercise_id, output_dir=str(out))
    out.mkdir(parents=True, exist_ok=True)
    state = _load_state(out)
    already_filled = set(state.get("filled", {}).get(exercise_id, []))

    for src in sorted(p for p in templates_root.rglob("*") if p.is_file()):
        rel = src.relative_to(templates_root)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        # A phase runs several exercises into ONE output_dir. Re-copying a pristine
        # template over a copy an earlier exercise already filled would silently
        # undo that work, so an existing copy is kept and filled in place.
        if str(rel) in already_filled and dest.exists():
            # This exercise already filled this copy in an earlier run. Re-applying
            # the ENGINES would find the tokens consumed and report them as missing.
            # The PAYLOAD-level skips are re-evaluated though: they do not depend on
            # the copy's state, and the fill-map may have been edited between runs,
            # so the flag is rebuilt from what is unfilled now.
            prior_specs = by_template.pop(str(rel).replace("\\", "/"), None) or []
            skips = [w for spec in prior_specs for w in spec.warnings]
            result.warnings.extend(skips)
            _remove_flag(dest)
            if skips:
                result.flags.append(
                    str(
                        _write_flag(
                            dest,
                            [f"{len(skips)} field(s) could not be filled from the sprint:", ""]
                            + [f"- {s}" for s in skips],
                        ).relative_to(out)
                    )
                )
            result.carried_over.append(str(rel))
            continue

        existed = dest.exists()
        if not existed:
            shutil.copy2(src, dest)  # COPY first; every edit below touches only `dest`

        file_specs = by_template.pop(str(rel).replace("\\", "/"), None)
        if file_specs is None:
            if existed:
                result.carried_over.append(str(rel))
            else:
                result.copied_blank.append(str(rel))
                result.flags.append(str(_write_flag(dest, [NO_SOURCE]).relative_to(out)))
            continue

        made = 0
        skips: list[str] = []
        for spec in file_specs:
            try:
                spec_made, engine_warnings = _apply_spec(dest, spec)
            except Exception as exc:
                # One unreadable or malformed template must not cost the phase its
                # other 36 files. Report it and carry on.
                spec_made, engine_warnings = 0, [
                    f"{spec.template}: engine {spec.engine!r} could not run — {exc}"
                ]
            made += spec_made
            skips.extend(spec.warnings)
            skips.extend(engine_warnings)
        result.warnings.extend(skips)

        # Rewrite this file's flag from scratch below, so a resolved skip's flag
        # cannot survive.
        _remove_flag(dest)

        if made:
            result.filled.append(str(rel))
            state.setdefault("filled", {}).setdefault(exercise_id, [])
            if str(rel) not in state["filled"][exercise_id]:
                state["filled"][exercise_id].append(str(rel))
        elif existed:
            result.carried_over.append(str(rel))
        else:
            result.copied_blank.append(str(rel))
        if skips:
            result.flags.append(
                str(
                    _write_flag(
                        dest,
                        [f"{len(skips)} field(s) could not be filled from the sprint:", ""]
                        + [f"- {s}" for s in skips],
                    ).relative_to(out)
                )
            )

    # Fill-map entries whose template is not under templates_root: a renamed or
    # moved template must not silently stop being filled.
    for template, file_specs in by_template.items():
        result.warnings.append(
            f"{template}: fill-map names this template but it is not under "
            f"templates_root ({templates_root}) — nothing was filled"
        )
        for spec in file_specs:
            result.warnings.extend(spec.warnings)

    _save_state(out, state)
    result.report_path = str(_write_report(out, result).relative_to(out))
    return result


def on_manifest_complete(
    artifact_dir: str | Path,
    prev_manifest,
    cur_manifest,
    output_dir: str | Path,
    templates_root: str | Path,
    fillmap_path: str | Path | None = None,
) -> list[PopulateResult]:
    """Populate every exercise that just flipped to ``complete`` in the manifest.

    One exercise failing (missing sidecar, still unconfirmed) must not cost the
    others their output, so the failure is captured as a warning on that
    exercise's own result rather than raised.
    """
    results: list[PopulateResult] = []
    for exercise_id in exercises_now_complete(prev_manifest, cur_manifest):
        try:
            results.append(
                populate_phase(
                    artifact_dir, exercise_id, output_dir, templates_root, fillmap_path
                )
            )
        except SidecarError as exc:
            results.append(
                PopulateResult(
                    exercise_id=exercise_id,
                    output_dir=str(output_dir),
                    warnings=[
                        f"{exercise_id}: manifest says complete but nothing could be "
                        f"populated — {exc}"
                    ],
                )
            )
    return results
