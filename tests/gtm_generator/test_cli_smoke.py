# Loader-independent smoke tests for pipelines.gtm_generator.cli.
#
# These tests exercise the CLI's failure paths without depending on
# the JSON Schema envelope (which arrives in a follow-up PR). Any
# test that needs a real StrategySprintInput lives in tests/gtm_generator/
# test_cli_integration.py and is added alongside PR-2.
#
# The failure paths are the reason a CLI exists at all: Exercise 7 invokes
# this via subprocess and reads exit code + stderr, so both need to be
# stable + documented. Structured error envelopes (single-line JSON on
# stderr) are the contract; changing the shape without a version bump
# breaks the exercise wrapper.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """Invoke the CLI as a subprocess (matching how Exercise 7 invokes it).

    Deliberately spawn a fresh Python process rather than importing the
    module — this covers the subprocess-invocation contract, not just the
    Python-import contract. Import-time errors that a same-process test
    would hide surface here.
    """
    return subprocess.run(
        [sys.executable, "-m", "pipelines.gtm_generator.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_error_envelope(stderr: str) -> dict:
    """Extract the last non-empty stderr line as an error envelope.

    The CLI emits a single-line JSON envelope to stderr on any non-zero
    exit; argparse output (if any) precedes it. Parsing the LAST
    non-empty line lets us stay tolerant of pre-envelope argparse noise
    while still binding on the structured contract.
    """
    lines = [line for line in stderr.splitlines() if line.strip()]
    assert lines, f"expected at least one non-empty stderr line, got: {stderr!r}"
    return json.loads(lines[-1])


def test_missing_required_args_exits_contract_violation():
    result = _run_cli()
    assert result.returncode == 2, f"expected exit 2, got {result.returncode}: {result.stderr}"
    envelope = _parse_error_envelope(result.stderr)
    assert envelope["kind"] == "invocation_error"
    assert envelope["exit_code"] == 2


def test_nonexistent_artifact_dir_exits_contract_violation():
    result = _run_cli(
        "--artifact-dir", "/nonexistent/path/that/does/not/exist",
        "--client-slug", "smoke-test-client",
        "--strict",
    )
    assert result.returncode == 2, f"expected exit 2, got {result.returncode}: {result.stderr}"
    envelope = _parse_error_envelope(result.stderr)
    assert envelope["kind"] == "contract_violation"
    assert envelope["exit_code"] == 2
    assert "artifact_dir" in envelope["detail"]
    assert "/nonexistent/path/that/does/not/exist" in envelope["message"]


def test_exit_codes_match_documented_constants():
    """The CLI's exit codes are part of the subprocess contract that
    Exercise 7 reads. A drift between the docstring at the top of cli.py
    and the actual constants would be silent otherwise."""
    from pipelines.gtm_generator import cli
    assert cli.EXIT_OK == 0
    assert cli.EXIT_CONTRACT_VIOLATION == 2
    assert cli.EXIT_GENERATOR_ERROR == 3


def test_error_envelope_shape_is_stable():
    """Downstream automation parses this shape. Fail loudly if it drifts."""
    from pipelines.gtm_generator.cli import ErrorEnvelope
    env = ErrorEnvelope(
        kind="contract_violation",
        exit_code=2,
        message="test",
        detail={"foo": "bar"},
    )
    # Emit-then-capture would require patching stderr; simpler to just
    # confirm the fields we care about exist.
    assert env.kind == "contract_violation"
    assert env.exit_code == 2
    assert env.message == "test"
    assert env.detail == {"foo": "bar"}
