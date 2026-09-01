"""``python -m autopopulate`` — fill one exercise's templates into an output_dir."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from autopopulate.fillmap import FillMapError
from autopopulate.orchestrator import populate_phase
from autopopulate.sidecar import SidecarError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m autopopulate",
        description=(
            "Fill COPIES of a Strategy Sprint exercise's mapped Office templates "
            "into a per-run output directory. Originals are never modified."
        ),
    )
    p.add_argument("--artifact-dir", required=True, help="client artifact dir (holds output/)")
    p.add_argument("--exercise-id", required=True, help="e.g. company-overview")
    p.add_argument("--output-dir", required=True, help="per-run destination; tree is mirrored")
    p.add_argument("--templates-root", required=True, help="root of the Strategy Sprint templates")
    p.add_argument("--fillmap", default=None, help="override autopopulate/fillmap.yaml")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = populate_phase(
            args.artifact_dir,
            args.exercise_id,
            args.output_dir,
            args.templates_root,
            fillmap_path=args.fillmap,
        )
    except (SidecarError, FillMapError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out = Path(args.output_dir)
    print(f"{result.exercise_id}: {len(result.filled)} filled, "
          f"{len(result.copied_blank)} copied as-is, {len(result.warnings)} field(s) not filled")
    for rel in result.filled:
        print(f"  filled     {rel}")
    for rel in result.copied_blank:
        print(f"  as-is      {rel}")
    # Skips reach the terminal too — not only the report on disk.
    for w in result.warnings:
        print(f"  NOT FILLED {w}")
    print(f"report: {out / result.report_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
