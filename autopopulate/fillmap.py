"""The declarative fill-map: exercise field -> template destination.

Coverage is DATA. Adding another template to the covered subset means adding an
entry to ``fillmap.yaml``; it does not mean writing code. Code changes only when
a template needs a genuinely new engine mode.

Resolution never fabricates. If a payload field is absent, null, empty, or is a
container the entry did not say how to flatten, no target is produced and a
warning naming the field, the destination and the template is recorded instead.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml

from autopopulate.models import FileFillSpec, FillTarget, Sidecar

DEFAULT_FILLMAP = Path(__file__).with_name("fillmap.yaml")

#: Only engines that actually exist. PPTX is deferred post-MVP (the Overview deck
#: is UNASSIGNED and copied as-is), and accepting an engine with no implementation
#: turns a data-only fill-map edit into a crash mid-phase.
ENGINES = {"docx-token", "docx-heading", "docx-dropdown", "xlsx"}
DEST_KEYS = {"token": "token", "heading": "heading", "alias": "alias", "cell": "cell"}
#: which destination key each engine expects
ENGINE_DEST = {
    "docx-token": "token",
    "docx-heading": "heading",
    "docx-dropdown": "alias",
    "xlsx": "cell",
}

_MISSING = object()


class FillMapError(Exception):
    """The fill-map is malformed."""


def load_fillmap(path: str | Path | None = None) -> dict:
    """Load and validate the fill-map. Raises ``FillMapError`` on a bad entry."""
    p = Path(path) if path is not None else DEFAULT_FILLMAP
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise FillMapError(f"fill-map not found: {p}") from exc
    except (OSError, yaml.YAMLError) as exc:
        raise FillMapError(f"fill-map could not be parsed: {p} — {exc}") from exc

    if not isinstance(data, dict):
        raise FillMapError(f"fill-map is not a mapping of exercise ids: {p}")

    for exercise_id, entries in data.items():
        if not isinstance(entries, list):
            raise FillMapError(f"{p}: {exercise_id!r} must be a list of file entries")
        for entry in entries:
            _validate_entry(p, exercise_id, entry)
    return data


def _validate_entry(p: Path, exercise_id: str, entry) -> None:
    if not isinstance(entry, dict):
        raise FillMapError(f"{p}: {exercise_id!r} entry is not a mapping")
    template = entry.get("template")
    if not template:
        raise FillMapError(f"{p}: {exercise_id!r} entry has no template")
    engine = entry.get("engine")
    if engine not in ENGINES:
        raise FillMapError(
            f"{p}: {exercise_id!r} -> {template!r} has unknown engine {engine!r}; "
            f"known: {sorted(ENGINES)}"
        )
    if engine == "xlsx" and not entry.get("sheet"):
        raise FillMapError(f"{p}: {exercise_id!r} -> {template!r} (xlsx) declares no sheet")

    expected_dest = ENGINE_DEST[engine]
    for target in entry.get("targets") or []:
        if not isinstance(target, dict):
            raise FillMapError(f"{p}: {template!r} target is not a mapping")
        if not target.get("source"):
            raise FillMapError(f"{p}: {template!r} target has no source")
        if not target.get(expected_dest):
            raise FillMapError(
                f"{p}: {template!r} target {target.get('source')!r} has no "
                f"{expected_dest!r} destination (required by engine {engine!r})"
            )


def resolve_payload_path(payload, dotted: str):
    """Walk a dotted path into the payload. Numeric segments index lists.

    Returns ``_MISSING`` (a private sentinel) when the path does not exist, which
    is deliberately distinct from a path that exists and holds ``None``.
    """
    node = payload
    for part in dotted.split("."):
        if isinstance(node, dict):
            if part not in node:
                return _MISSING
            node = node[part]
        elif isinstance(node, (list, tuple)):
            if not (part.isdigit() or (part.startswith("-") and part[1:].isdigit())):
                return _MISSING
            idx = int(part)
            if not -len(node) <= idx < len(node):
                return _MISSING
            node = node[idx]
        else:
            return _MISSING
    return node


def _is_scalar(value) -> bool:
    return isinstance(
        value, (str, int, float, bool, datetime.date, datetime.datetime, datetime.time)
    )


def _coerce(value, join: str | None):
    """Turn a payload value into something writable, or return a reason it isn't.

    Scalars keep their TYPE. Stringifying everything would land numbers in Excel as
    text cells, which every SUM, sort and chart over that column silently ignores —
    a filled-looking sheet that does not compute.
    """
    if value is _MISSING:
        return None, "field is absent from the sidecar payload"
    if value is None:
        return None, "field is present but null"
    if isinstance(value, (list, tuple)):
        if join is None:
            return None, (
                "field is a list and the fill-map entry declares no 'join', so "
                "flattening it would be a guess"
            )
        nonscalar = [v for v in value if v is not None and not _is_scalar(v)]
        if nonscalar:
            return None, (
                "field is a list containing non-scalar entries "
                f"({type(nonscalar[0]).__name__}); joining them would write raw "
                "Python data structures into the deliverable"
            )
        parts = [str(v) for v in value if v is not None and str(v) != ""]
        if not parts:
            return None, "field is an empty list"
        return join.join(parts), None
    if isinstance(value, dict):
        return None, "field is a mapping; a fill-map entry must target a leaf field"
    if not _is_scalar(value):
        return None, f"field is a {type(value).__name__}, which is not a writable value"
    if isinstance(value, str) and value.strip() == "":
        return None, "field is present but empty"
    return value, None


def resolve_fills(
    exercise_id: str,
    sidecar: Sidecar,
    fillmap_path: str | Path | None = None,
) -> list[FileFillSpec]:
    """Resolve this exercise's fill-map entries against a confirmed sidecar."""
    fillmap = load_fillmap(fillmap_path)
    entries = fillmap.get(exercise_id) or []

    specs: list[FileFillSpec] = []
    for entry in entries:
        engine = entry["engine"]
        dest_key = ENGINE_DEST[engine]
        spec = FileFillSpec(
            template=entry["template"],
            engine=engine,
            sheet=entry.get("sheet"),
        )
        for target in entry.get("targets") or []:
            source = target["source"]
            dest = target[dest_key]
            raw = resolve_payload_path(sidecar.payload, source)
            value, reason = _coerce(raw, target.get("join"))
            if reason is not None:
                spec.warnings.append(
                    f"{entry['template']}: left {dest!r} unfilled — "
                    f"payload field {source!r}: {reason}"
                )
                continue
            spec.targets.append(
                FillTarget(source=source, kind=dest_key, dest=dest, value=value)
            )
        specs.append(spec)
    return specs
