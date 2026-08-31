"""Dataclasses shared across the autopopulate component."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Sidecar:
    """A typed exercise sidecar YAML, already gated on ``confirmedByClient``."""

    exercise_id: str
    confirmed: bool
    payload: dict[str, Any] = field(default_factory=dict)
    markdown: str | None = None


@dataclass(frozen=True)
class CellTarget:
    """A single xlsx write: a coordinate on a sheet and the value for it."""

    coord: str
    value: object


@dataclass(frozen=True)
class FillTarget:
    """One resolved write: where the value came from, where it goes, what it is."""

    source: str  # dotted path into the sidecar payload
    kind: str  # token | heading | alias | cell
    dest: str  # the token text / heading text / sdt alias / cell coord
    value: object


@dataclass
class FileFillSpec:
    """Everything to do to one template file for one exercise.

    ``warnings`` carries the VISIBLE SKIPS: payload fields this file wanted but
    could not get. They travel with the spec so the orchestrator can put them in
    the fill report and the .FILL-MANUALLY flag rather than dropping them.
    """

    template: str  # path relative to templates_root
    engine: str
    targets: list[FillTarget] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sheet: str | None = None


@dataclass
class PopulateResult:
    """What one ``populate_phase`` run did — and, crucially, what it did NOT do.

    ``warnings`` is the visible-skip channel: every field that could not be filled
    appears here, in the run's fill report, and in a ``.FILL-MANUALLY.txt`` beside
    the file it belongs to. Nothing is skipped quietly.
    """

    exercise_id: str
    output_dir: str
    filled: list[str] = field(default_factory=list)
    copied_blank: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    #: files already present in output_dir from an earlier exercise in this phase,
    #: which this exercise does not source and therefore left untouched
    carried_over: list[str] = field(default_factory=list)
    report_path: str | None = None
