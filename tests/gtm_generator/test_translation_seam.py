"""The integration seam: sprint payloads all the way through to a valid input.

WHY THIS FILE EXISTS. Every suite here tested one half against fixtures its own
author wrote, so all of them stayed green while the halves disagreed. The loader
read snake_case GTM keys the camelCase payload schemas forbid, and the pipeline
had never produced a plan from any input, including this repo's own reference
fixture. Nothing went red.

The existing happy-path test asserts `company_name == "Acme Corp"` and stops
there, while its docstring claims it "returns a populated StrategySprintInput".
Every other field on that object is a dataclass default. These tests assert the
claim the docstring was already making.

Written BEFORE the translation layer, and they fail. That order is the point:
had the loader tests asserted populated fields instead of error shapes, the seam
defect would have been caught the day the loader landed.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "artifacts"

sys.path.insert(0, str(ROOT))

from pipelines.gtm_generator.loader import load_from_artifact_dir  # noqa: E402
from pipelines.gtm_generator.input_models import validate_strategy_input  # noqa: E402


# Fields the generator refuses to run without. Kept as data rather than prose so
# a new required field in the generator shows up here as a failure instead of as
# a surprise at run time.
REQUIRED = [
    ("company_name", lambda i: i.company_name.strip()),
    ("industry", lambda i: i.industry.strip()),
    ("pain_points", lambda i: i.pain_points),
    ("target_market.industries", lambda i: i.target_market.industries),
    ("icp.criteria", lambda i: i.icp.criteria),
    ("icp.titles", lambda i: i.icp.titles),
    ("value_proposition.headline", lambda i: i.value_proposition.headline.strip()),
]


@pytest.fixture(scope="module")
def loaded():
    return load_from_artifact_dir(FIXTURES / "happy-full", "test-client")


@pytest.mark.parametrize("name,get", REQUIRED, ids=[n for n, _ in REQUIRED])
def test_required_field_is_populated_through_the_loader(loaded, name, get):
    """Each required field arrives populated, not defaulted.

    Asserted one field per case on purpose. A single test over all of them
    reports only the first gap, and the whole failure mode here was a gap that
    nobody could see the shape of.
    """
    assert get(loaded), (
        f"{name} came through empty. The loader read a key the payload schema "
        f"does not define, so no exercise could ever populate it."
    )


def test_loaded_input_passes_the_generators_own_validation(loaded):
    """The seam test proper.

    Both halves can be internally correct and still not compose. This asserts
    the generator accepts what the loader produces, which is the single check
    whose absence let the two vocabularies drift apart.
    """
    errors = validate_strategy_input(loaded)
    assert not errors, "generator rejected the loader's output: " + "; ".join(errors)


def test_cli_end_to_end_writes_a_plan(tmp_path):
    """Run the real entry point, not the functions it calls.

    Everything above could pass while the CLI still fails on wiring. Verifying
    the thing that actually runs is the whole lesson of this seam.
    """
    import shutil
    art = tmp_path / "artifact"
    shutil.copytree(FIXTURES / "happy-full", art)
    proc = subprocess.run(
        [sys.executable, "-m", "pipelines.gtm_generator.cli",
         "--artifact-dir", str(art), "--client-slug", "test-client", "--strict"],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, (
        f"cli exited {proc.returncode}, stderr: {proc.stderr[:600]}"
    )
    plan = art / "output" / "gtm-plan.json"
    assert plan.exists(), "cli reported success but wrote no plan"
    assert plan.stat().st_size > 0, "plan file is empty"


def test_happy_minimal_still_reports_its_own_incompleteness():
    """The mirror bound.

    A translation layer that satisfies the generator by inventing defaults would
    make every fixture pass, including one that genuinely lacks the exercises
    those fields come from. happy-minimal has only company-overview complete, so
    ICP and positioning fields have no source and MUST still come through empty.
    Without this, 'all required fields populated' could be achieved by
    fabrication, which is the failure the payload schemas were designed against.
    """
    minimal = load_from_artifact_dir(FIXTURES / "happy-minimal", "test-client")
    assert not minimal.icp.titles, (
        "icp.titles was populated from an artifact where icp-prioritization "
        "never ran. The translation layer is inventing values."
    )
    assert not minimal.value_proposition.headline.strip(), (
        "value_proposition.headline was populated from an artifact where "
        "positioning never ran."
    )
