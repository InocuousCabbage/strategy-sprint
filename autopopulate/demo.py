"""End-to-end demo: populate a phase and show what happened.

Runs ``on_manifest_complete`` for every exercise the manifest reports complete,
into a fresh output_dir, then prints the mirrored tree marking each file as
FILLED / as-is / flagged, followed by every field that could not be filled.

    python -m autopopulate.demo [--templates-root PATH] [--output-dir PATH]

Defaults to the repo's happy-full fixture artifacts and, if it is mounted, the
real Strategy Sprint template folder.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from autopopulate.discovery import ENV_VAR, find_templates_root
from autopopulate.manifest_watch import load_manifest
from autopopulate.orchestrator import FLAG_SUFFIX, NO_SOURCE, on_manifest_complete

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = REPO_ROOT / "tests/gtm_generator/fixtures/artifacts/happy-full"


def print_tree(out: Path, filled: set[str]) -> None:
    """Print the mirrored tree, marking filled files and .FILL-MANUALLY flags."""
    files = sorted(p for p in out.rglob("*") if p.is_file())
    flags = {
        str(p.relative_to(out))[: -len(FLAG_SUFFIX)]: p
        for p in files
        if p.name.endswith(FLAG_SUFFIX)
    }
    shown_dirs: set[Path] = set()
    for f in files:
        if f.name.endswith(FLAG_SUFFIX) or f.suffix == ".md":
            continue
        rel = f.relative_to(out)
        if rel.parent not in shown_dirs:
            shown_dirs.add(rel.parent)
            print(f"\n  {rel.parent}/")
        flag = flags.get(str(rel))
        flag_text = flag.read_text(encoding="utf-8") if flag is not None else ""
        no_source = NO_SOURCE in flag_text
        if str(rel) in filled and flag is None:
            mark = "FILLED  "
        elif str(rel) in filled:
            mark = "PARTIAL "
        elif no_source:
            mark = "no src  "
        else:
            mark = "as-is   "
        suffix = "  [.FILL-MANUALLY]" if flag is not None else ""
        print(f"    {mark} {rel.name}{suffix}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m autopopulate.demo")
    ap.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    ap.add_argument(
        "--templates-root",
        default=None,
        help=f"defaults to ${ENV_VAR}, else a Drive-synced copy if one is present",
    )
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args(argv)

    artifact_dir = Path(args.artifact_dir)
    templates_root = Path(args.templates_root) if args.templates_root else find_templates_root()
    if templates_root is None or not templates_root.is_dir():
        print(
            "templates root not found — pass --templates-root PATH "
            f"or set ${ENV_VAR}"
        )
        return 2

    out = Path(args.output_dir) if args.output_dir else Path(
        tempfile.mkdtemp(prefix="autopopulate-demo-")
    )

    manifest = load_manifest(artifact_dir / "output" / "sprint-manifest.yaml")
    print(f"artifact dir  : {artifact_dir}")
    print(f"templates root: {templates_root}")
    print(f"output dir    : {out}\n")

    results = on_manifest_complete(artifact_dir, None, manifest, out, templates_root)

    filled: set[str] = set()
    for r in results:
        filled.update(r.filled)
        filled.update(r.carried_over)
        print(
            f"{r.exercise_id:22} filled={len(r.filled):2}  as-is={len(r.copied_blank):2}  "
            f"carried={len(r.carried_over):2}  unfilled fields={len(r.warnings)}"
        )

    print("\n--- mirrored output tree ---")
    print_tree(out, filled)

    print("\n--- fields that could NOT be filled (visible skips) ---")
    any_skip = False
    for r in results:
        for w in r.warnings:
            any_skip = True
            print(f"  [{r.exercise_id}] {w}")
    if not any_skip:
        print("  (none)")

    print("\n--- reports written ---")
    for r in results:
        if r.report_path:
            print(f"  {out / r.report_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
