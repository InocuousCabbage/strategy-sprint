"""The phase-done signal.

``sprint-manifest.yaml`` is the sprint's own state file. An exercise row flipping
to ``complete`` is what says "this phase's content is ready to populate". This
module is a PURE diff of two manifest snapshots — no daemon, no polling. The
sprint is human-orchestrated, so the component is called, not run in the
background.
"""

from __future__ import annotations

from pathlib import Path

import yaml

COMPLETE = "complete"


def load_manifest(path: str | Path) -> dict:
    """Read a sprint-manifest.yaml into a plain dict."""
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _statuses(manifest) -> dict[str, str]:
    if not manifest:
        return {}
    return {
        s["exerciseId"]: s.get("status")
        for s in (manifest.get("steps") or [])
        if s.get("exerciseId")
    }


def exercises_now_complete(prev_manifest, cur_manifest) -> list[str]:
    """Exercise ids that are ``complete`` now and were not ``complete`` before.

    Idempotent by construction: a row complete in both snapshots is not returned,
    so re-running the hook cannot re-populate a finished exercise. ``None`` for
    ``prev_manifest`` means "no prior observation", so every currently-complete
    row counts as new. Order follows the manifest.
    """
    before = _statuses(prev_manifest)
    return [
        eid
        for eid, status in _statuses(cur_manifest).items()
        if status == COMPLETE and before.get(eid) != COMPLETE
    ]
