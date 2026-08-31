"""Locating the Strategy Sprint templates without baking in a machine or account.

The component itself never needs this — ``populate_phase`` takes ``templates_root``
as a parameter and that is the portability contract. This helper exists only so the
demo and the real-template checks can FIND a root on a given machine, and it does so
without a hardcoded home directory or Google account in the source.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "STRATEGY_SPRINT_TEMPLATES"

#: Where a Drive-synced copy lands on macOS. The account segment is a glob on
#: purpose: it must not name a person.
_DRIVE_GLOB = "Library/CloudStorage/GoogleDrive-*/*/Knowledge Base/Marketing Templates"
_SPRINT_GLOB = "*/Strategy Sprint"


def find_templates_root(env_var: str = ENV_VAR) -> Path | None:
    """Return the templates root, or None if it cannot be located.

    ``$STRATEGY_SPRINT_TEMPLATES`` wins outright: if it is set it is the answer,
    and if it does not point at a directory the answer is None rather than a
    surprising fallback to whatever happens to be mounted.
    """
    override = os.environ.get(env_var)
    if override:
        p = Path(override)
        return p if p.is_dir() else None

    for marketing_templates in sorted(Path.home().glob(_DRIVE_GLOB)):
        for candidate in sorted(marketing_templates.glob(_SPRINT_GLOB)):
            if candidate.is_dir():
                return candidate
    return None
