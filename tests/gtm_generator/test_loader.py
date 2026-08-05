# Tests for pipelines.gtm_generator.loader.
#
# Fixture-based: each error class in the 4-way state matrix (per the schema
# envelope's manifest-plus-sidecar design) has a corresponding fixture
# artifact directory under tests/gtm_generator/fixtures/artifacts/, and one
# test asserts the loader raises the specific ContractError subclass for
# that fixture. Happy-minimal exercises the same code path with a valid
# manifest + one confirmed company-overview sidecar.
#
# Layered verification framing (per the schema PRs' review discussion):
# the schema catches "definition accepts what it shouldn't";
# these tests catch "loader does the wrong thing with accepted input." The
# small overlap is intentional and the union covers the failure modes that
# would otherwise ship silently. If any of these tests fails against a
# payload the schema accepted, the schema is buggy — file an issue rather
# than working around at loader layer.

from __future__ import annotations

from pathlib import Path

import pytest

from pipelines.gtm_generator.loader import (
    ContractError,
    ExerciseNotYetRun,
    ManifestMissing,
    SidecarMissingUnexpected,
    UnconfirmedPayloadRejected,
    load_from_artifact_dir,
)

FIXTURES = Path(__file__).parent / "fixtures" / "artifacts"


def test_happy_minimal_loads_without_error():
    """Minimal-valid manifest (company-overview complete, others optional-unrun)
    loads cleanly + returns a populated StrategySprintInput."""
    result = load_from_artifact_dir(FIXTURES / "happy-minimal", "test-client")
    assert result.company_name == "Acme Corp"


def test_missing_manifest_raises():
    """Empty output dir (no sprint-manifest.yaml) fails ManifestMissing."""
    with pytest.raises(ManifestMissing) as exc_info:
        load_from_artifact_dir(FIXTURES / "missing-manifest", "test-client")
    assert "sprint-manifest.yaml" in str(exc_info.value).lower() or "manifest" in str(exc_info.value).lower()


def test_unrun_required_exercise_raises():
    """Required exercise (positioning) with status=unrun triggers ExerciseNotYetRun
    with the specific exercise-id in the message so an operator knows which
    /slash-command to run."""
    with pytest.raises(ExerciseNotYetRun) as exc_info:
        load_from_artifact_dir(FIXTURES / "unrun-required", "test-client")
    assert "positioning" in str(exc_info.value)


def test_missing_sidecar_when_complete_raises():
    """Manifest says company-overview is complete but the sidecar file is
    absent (write partially succeeded, envelope wrote but sidecar didn't)."""
    with pytest.raises(SidecarMissingUnexpected) as exc_info:
        load_from_artifact_dir(FIXTURES / "missing-sidecar", "test-client")
    assert "company-overview" in str(exc_info.value)


def test_unconfirmed_payload_rejected_in_strict_mode():
    """Sidecar with confirmedByClient=false on a required exercise triggers
    UnconfirmedPayloadRejected. Draft-generate is a separate flag; strict
    mode does NOT weaken to accept unratified content since downstream
    automation (outreach, CRM config) acts on it."""
    with pytest.raises(UnconfirmedPayloadRejected) as exc_info:
        load_from_artifact_dir(FIXTURES / "unconfirmed", "test-client")
    assert "company-overview" in str(exc_info.value)


def test_client_slug_mismatch_raises():
    """Caller passes a slug that doesn't match the manifest's clientSlug.
    Pre-load defect surfaced here rather than downstream so the caller can
    correct the invocation."""
    with pytest.raises(ContractError) as exc_info:
        load_from_artifact_dir(FIXTURES / "happy-minimal", "wrong-slug")
    msg = str(exc_info.value)
    assert "wrong-slug" in msg
    assert "test-client" in msg


def test_all_contract_errors_are_subclasses_of_contract_error_base():
    """cli.py catches ContractError as the base class and maps to exit code 2.
    Any new error added to the loader's hierarchy MUST inherit from
    ContractError or cli.py will misroute it as an internal error (exit 3).
    Pin the invariant here so a new error added without inheritance fails
    loudly rather than silently misrouting."""
    from pipelines.gtm_generator import loader
    error_classes = [
        cls for name, cls in vars(loader).items()
        if isinstance(cls, type) and issubclass(cls, Exception) and cls is not Exception
    ]
    for cls in error_classes:
        if cls is ContractError:
            continue
        assert issubclass(cls, ContractError), (
            f"{cls.__name__} in loader.py does not subclass ContractError; "
            f"cli.py would misroute it as an internal error (exit 3) instead "
            f"of a contract violation (exit 2)."
        )
