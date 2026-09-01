"""Load + gate a Strategy Sprint exercise sidecar.

The sidecar (``${ARTIFACT_DIR}/output/<exercise-id>.yaml``) is the ONLY content
source for auto-populate. Nothing is filled from an unconfirmed sidecar: the
consultant's ``confirmedByClient: true`` is the consent that authorizes writing
client content into a deliverable, so the gate is affirmative — a missing flag
is a refusal, not a default.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from autopopulate.models import Sidecar


class SidecarError(Exception):
    """Base for sidecar loading problems."""


class SidecarNotConfirmed(SidecarError):
    """Raised when a sidecar is not ``confirmedByClient: true``."""


def load_sidecar(path: str | Path) -> Sidecar:
    """Read a sidecar YAML and return it, or raise if it is not confirmed."""
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SidecarError(f"sidecar not found: {p}") from exc
    except (OSError, yaml.YAMLError) as exc:
        # A malformed sidecar must surface as SidecarError, or callers that
        # deliberately catch it (the batch hook, the CLI) miss it entirely and
        # one bad file takes down every other exercise's output.
        raise SidecarError(f"sidecar could not be parsed: {p} — {exc}") from exc

    if not isinstance(raw, dict):
        raise SidecarError(f"sidecar is not a YAML mapping: {p}")

    exercise_id = raw.get("exerciseId")
    if not exercise_id:
        raise SidecarError(f"sidecar has no exerciseId: {p}")

    if raw.get("confirmedByClient") is not True:
        raise SidecarNotConfirmed(
            f"{p} is not confirmedByClient: true "
            f"(got {raw.get('confirmedByClient')!r}) — refusing to populate from it"
        )

    payload = raw.get("payload") or {}
    if not isinstance(payload, dict):
        raise SidecarError(f"sidecar payload is not a mapping: {p}")

    return Sidecar(
        exercise_id=str(exercise_id),
        confirmed=True,
        payload=payload,
        markdown=raw.get("markdown"),
    )
