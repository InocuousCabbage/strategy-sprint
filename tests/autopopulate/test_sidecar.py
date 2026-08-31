import pytest

from autopopulate.sidecar import SidecarNotConfirmed, load_sidecar


def test_loads_confirmed_sidecar(happy_full_dir):
    s = load_sidecar(f"{happy_full_dir}/company-overview.yaml")
    assert s.exercise_id == "company-overview"
    assert s.confirmed is True
    assert isinstance(s.payload, dict) and s.payload  # non-empty envelope payload
    # world-asserting: the real fixture's content actually came through
    assert s.payload["company"]["name"] == "Acme Corp"
    assert s.markdown is None


def test_unconfirmed_sidecar_raises(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text(
        "schemaVersion: 0.1.0\nexerciseId: positioning\nconfirmedByClient: false\npayload: {}\n"
    )
    with pytest.raises(SidecarNotConfirmed):
        load_sidecar(str(p))


def test_missing_confirmed_flag_raises(tmp_path):
    """Absent confirmedByClient is not consent — the gate must be affirmative."""
    p = tmp_path / "y.yaml"
    p.write_text("schemaVersion: 0.1.0\nexerciseId: positioning\npayload: {}\n")
    with pytest.raises(SidecarNotConfirmed):
        load_sidecar(str(p))


def test_repo_unconfirmed_fixture_raises(repo_root):
    """The repo's own unconfirmed fixture must be refused, not read."""
    p = repo_root / "tests/gtm_generator/fixtures/artifacts/unconfirmed/output/company-overview.yaml"
    with pytest.raises(SidecarNotConfirmed):
        load_sidecar(str(p))
