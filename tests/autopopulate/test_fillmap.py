"""Tests for the declarative fill-map + resolver.

The fill-map is DATA: extending coverage to more templates means adding entries
to autopopulate/fillmap.yaml, not writing code.

The central rule under test: a payload field that cannot be resolved is NEVER
fabricated and NEVER silently dropped — it produces a warning that names the
field and the template, so the skip reaches the consultant.
"""

import pytest

from autopopulate.fillmap import FillMapError, load_fillmap, resolve_fills
from autopopulate.models import Sidecar
from autopopulate.sidecar import load_sidecar


@pytest.fixture
def company_sidecar(happy_full_dir):
    return load_sidecar(happy_full_dir / "company-overview.yaml")


@pytest.fixture
def positioning_sidecar(happy_full_dir):
    return load_sidecar(happy_full_dir / "positioning.yaml")


@pytest.fixture
def icp_sidecar(happy_full_dir):
    return load_sidecar(happy_full_dir / "icp-prioritization.yaml")


def test_shipped_fillmap_loads_and_validates():
    fm = load_fillmap()
    assert "company-overview" in fm
    assert "positioning" in fm
    assert "icp-prioritization" in fm


def test_resolves_the_annual_planning_company_token(company_sidecar):
    specs = resolve_fills("company-overview", company_sidecar)

    assert len(specs) == 1
    spec = specs[0]
    assert spec.template.endswith("Annual Planning TEMPLATE.docx")
    assert spec.engine == "docx-token"
    assert spec.warnings == []
    assert [(t.dest, t.value) for t in spec.targets] == [("[COMPANY]", "Acme Corp")]


def test_resolves_the_positioning_statement_under_its_heading(positioning_sidecar):
    specs = resolve_fills("positioning", positioning_sidecar)

    heading_specs = [s for s in specs if s.engine == "docx-heading"]
    assert heading_specs, "no docx-heading spec for positioning"
    target = heading_specs[0].targets[0]
    assert target.source == "statement"
    assert target.dest == "POSITIONING STATEMENT"
    assert target.value.startswith("For regional property managers")


def test_resolves_icp_grid_cells_from_a_list_indexed_path(icp_sidecar):
    specs = resolve_fills("icp-prioritization", icp_sidecar)

    xlsx = [s for s in specs if s.engine == "xlsx"]
    assert xlsx, "no xlsx spec for icp-prioritization"
    spec = xlsx[0]
    assert spec.sheet
    by_dest = {t.dest: t.value for t in spec.targets}
    # tiers.0.* must resolve through the list index
    assert by_dest["C3"] == "Regional property managers"
    assert by_dest["C4"] == "Core"
    assert by_dest["C5"] == "Commercial real estate, Light manufacturing"


def test_missing_payload_field_warns_and_fills_nothing(tmp_path):
    """VISIBLE SKIP: the field is absent, so no target — and a warning that names it."""
    fm = tmp_path / "fm.yaml"
    fm.write_text(
        "demo-exercise:\n"
        "  - template: 'Some/Template.docx'\n"
        "    engine: docx-token\n"
        "    targets:\n"
        "      - source: company.name\n"
        "        token: '[COMPANY]'\n"
        "      - source: company.tagline\n"
        "        token: '[TAGLINE]'\n"
    )
    s = Sidecar("demo-exercise", True, {"company": {"name": "Acme Corp"}})

    specs = resolve_fills("demo-exercise", s, fillmap_path=fm)

    spec = specs[0]
    assert [(t.dest, t.value) for t in spec.targets] == [("[COMPANY]", "Acme Corp")]
    assert len(spec.warnings) == 1
    w = spec.warnings[0]
    assert "company.tagline" in w and "[TAGLINE]" in w and "Template.docx" in w


def test_null_payload_value_warns_rather_than_writing_blank(tmp_path):
    """A present-but-empty field is still an unfilled field. Warn, don't write ''."""
    fm = tmp_path / "fm.yaml"
    fm.write_text(
        "demo-exercise:\n"
        "  - template: 'T.docx'\n"
        "    engine: docx-token\n"
        "    targets:\n"
        "      - source: evidence\n"
        "        token: '[EVIDENCE]'\n"
    )
    s = Sidecar("demo-exercise", True, {"evidence": None})

    spec = resolve_fills("demo-exercise", s, fillmap_path=fm)[0]

    assert spec.targets == []
    assert len(spec.warnings) == 1 and "evidence" in spec.warnings[0]


def test_list_value_needs_an_explicit_join_else_it_warns(tmp_path):
    """Never silently stringify a list into a cell. Either join is declared, or warn."""
    fm = tmp_path / "fm.yaml"
    fm.write_text(
        "a:\n"
        "  - template: 'T.docx'\n"
        "    engine: docx-token\n"
        "    targets:\n"
        "      - source: industries\n"
        "        token: '[INDUSTRIES]'\n"
        "b:\n"
        "  - template: 'T.docx'\n"
        "    engine: docx-token\n"
        "    targets:\n"
        "      - source: industries\n"
        "        token: '[INDUSTRIES]'\n"
        "        join: ', '\n"
    )
    s = Sidecar("a", True, {"industries": ["Commercial real estate", "Light manufacturing"]})

    unjoined = resolve_fills("a", s, fillmap_path=fm)[0]
    assert unjoined.targets == []
    assert "list" in unjoined.warnings[0].lower()

    s_b = Sidecar("b", True, s.payload)
    joined = resolve_fills("b", s_b, fillmap_path=fm)[0]
    assert joined.targets[0].value == "Commercial real estate, Light manufacturing"


def test_unknown_exercise_resolves_to_nothing(company_sidecar):
    assert resolve_fills("no-such-exercise", company_sidecar) == []


def test_unknown_engine_is_rejected_at_load(tmp_path):
    fm = tmp_path / "bad.yaml"
    fm.write_text(
        "a:\n  - template: 'T.docx'\n    engine: telepathy\n    targets: []\n"
    )
    with pytest.raises(FillMapError):
        load_fillmap(fm)


def test_target_without_a_destination_is_rejected_at_load(tmp_path):
    fm = tmp_path / "bad2.yaml"
    fm.write_text(
        "a:\n  - template: 'T.docx'\n    engine: docx-token\n"
        "    targets:\n      - source: company.name\n"
    )
    with pytest.raises(FillMapError):
        load_fillmap(fm)


def test_xlsx_entry_must_declare_a_sheet(tmp_path):
    fm = tmp_path / "bad3.yaml"
    fm.write_text(
        "a:\n  - template: 'T.xlsx'\n    engine: xlsx\n"
        "    targets:\n      - source: x\n        cell: A1\n"
    )
    with pytest.raises(FillMapError):
        load_fillmap(fm)


def test_whitespace_only_payload_value_warns_rather_than_writing_blank(tmp_path):
    """A whitespace-only field is an unfilled field. Writing it would look filled."""
    fm = tmp_path / "ws.yaml"
    fm.write_text(
        "a:\n  - template: 'T.docx'\n    engine: docx-token\n"
        "    targets:\n      - source: tagline\n        token: '[TAGLINE]'\n"
    )
    s = Sidecar("a", True, {"tagline": "   "})

    spec = resolve_fills("a", s, fillmap_path=fm)[0]

    assert spec.targets == [], "a blank value was written as if it were content"
    assert len(spec.warnings) == 1 and "tagline" in spec.warnings[0]


def test_absent_and_empty_are_reported_differently(tmp_path):
    """The warning must say WHICH problem it was — 'absent' and 'empty' need
    different fixes (bad fill-map path vs thin sidecar), so they cannot be merged."""
    fm = tmp_path / "d.yaml"
    fm.write_text(
        "a:\n  - template: 'T.docx'\n    engine: docx-token\n"
        "    targets:\n"
        "      - source: nope\n        token: '[A]'\n"
        "      - source: blank\n        token: '[B]'\n"
    )
    s = Sidecar("a", True, {"blank": ""})

    spec = resolve_fills("a", s, fillmap_path=fm)[0]

    assert spec.targets == []
    absent, empty = spec.warnings
    assert "absent" in absent
    assert "empty" in empty and "absent" not in empty
