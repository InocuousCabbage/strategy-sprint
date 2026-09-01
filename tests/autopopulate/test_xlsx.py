"""World-asserting tests for the xlsx engine: every test reopens the workbook and
reads the exact coordinate back.
"""

import pytest
from openpyxl import load_workbook

from autopopulate.engines.xlsx import (
    CellTarget,
    MergedCellError,
    ValidationValueError,
    fill_xlsx,
)


def test_writes_values_to_the_exact_coordinates(make_icp_xlsx):
    src = make_icp_xlsx()
    n = fill_xlsx(
        src,
        "ICP",
        [CellTarget("C2", "Emergency downtime costs more than the repair"),
         CellTarget("C3", "Guaranteed response time")],
    )

    ws = load_workbook(src)["ICP"]
    assert ws["C2"].value == "Emergency downtime costs more than the repair"
    assert ws["C3"].value == "Guaranteed response time"
    assert ws["A2"].value == "Regional property managers", "a label column was overwritten"
    assert ws["B2"].value is None, "an untargeted cell was written"
    assert n == 2


def test_list_validated_value_is_written_as_the_sheet_spells_it(make_icp_xlsx):
    """Allowed option is "Core " with a trailing space; Excel only matches exactly."""
    src = make_icp_xlsx()
    fill_xlsx(src, "ICP", [CellTarget("B2", "Core")])

    ws = load_workbook(src)["ICP"]
    assert ws["B2"].value == "Core "


def test_range_backed_validation_is_honoured(make_icp_xlsx):
    src = make_icp_xlsx()
    fill_xlsx(src, "ICP", [CellTarget("F2", "Scaling")])
    assert load_workbook(src)["ICP"]["F2"].value == "Scaling"


def test_rejects_a_value_outside_the_list_validation(make_icp_xlsx):
    """Can-fail control: never write an option the sheet's dropdown would reject."""
    src = make_icp_xlsx()
    with pytest.raises(ValidationValueError):
        fill_xlsx(src, "ICP", [CellTarget("B2", "Tier One")])
    assert load_workbook(src)["ICP"]["B2"].value is None, "workbook was mutated anyway"


def test_rejects_a_value_outside_a_range_backed_validation(make_icp_xlsx):
    src = make_icp_xlsx()
    with pytest.raises(ValidationValueError):
        fill_xlsx(src, "ICP", [CellTarget("F2", "Tier One")])


def test_refuses_a_non_top_left_merged_cell(make_icp_xlsx):
    """Can-fail control: writing to E2 of a D2:E2 merge is silently lost in Excel."""
    src = make_icp_xlsx()
    with pytest.raises(MergedCellError):
        fill_xlsx(src, "ICP", [CellTarget("E2", "value")])


def test_writes_the_top_left_of_a_merge(make_icp_xlsx):
    src = make_icp_xlsx()
    fill_xlsx(src, "ICP", [CellTarget("D2", "merged value")])
    assert load_workbook(src)["ICP"]["D2"].value == "merged value"


def test_formulas_survive_a_fill(make_icp_xlsx):
    """Loading data_only would replace formulas with cached values and destroy them."""
    src = make_icp_xlsx()
    fill_xlsx(src, "ICP", [CellTarget("C2", "x")])
    assert load_workbook(src)["ICP"]["C4"].value == "=LEN(A2)"


def test_unknown_sheet_is_reported(make_icp_xlsx):
    from autopopulate.engines.xlsx import SheetNotFoundError

    src = make_icp_xlsx()
    with pytest.raises(SheetNotFoundError):
        fill_xlsx(src, "NoSuchSheet", [CellTarget("A1", "x")])


def test_nothing_is_written_when_any_target_is_invalid(make_icp_xlsx):
    """All-or-nothing per call: a rejected target must not leave a half-filled sheet."""
    src = make_icp_xlsx()
    with pytest.raises(ValidationValueError):
        fill_xlsx(src, "ICP", [CellTarget("C2", "good"), CellTarget("B2", "Tier One")])

    ws = load_workbook(src)["ICP"]
    assert ws["C2"].value is None
    assert ws["B2"].value is None
