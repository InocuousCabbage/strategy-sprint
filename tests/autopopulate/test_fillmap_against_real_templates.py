"""Check the shipped fill-map against the REAL Strategy Sprint templates.

Everything else in this suite runs on synthetic fixtures, which can only prove
the engines behave. This module proves the DATA is right: that each template the
fill-map names exists, and that every destination it points at is really there —
the heading spelled exactly so, the sdt alias present, the sheet named, the cell
empty and inside any validation.

Skipped when the templates root is not mounted (CI, another machine), so the
suite stays green off this host.
"""

import pytest

from autopopulate.discovery import ENV_VAR, find_templates_root
from autopopulate.fillmap import ENGINE_DEST, load_fillmap


def _templates_root():
    root = find_templates_root()
    if root is None:
        pytest.skip(f"templates root not mounted (set ${ENV_VAR} to point at it)")
    return root


@pytest.fixture(scope="module")
def templates_root():
    return _templates_root()


@pytest.fixture(scope="module")
def fillmap():
    return load_fillmap()


def _entries(fillmap):
    for exercise_id, entries in fillmap.items():
        for entry in entries:
            yield exercise_id, entry


def test_every_named_template_exists(fillmap, templates_root):
    missing = [
        f"{eid} -> {e['template']}"
        for eid, e in _entries(fillmap)
        if not (templates_root / e["template"]).is_file()
    ]
    assert missing == [], f"fill-map names templates that do not exist: {missing}"


def test_every_docx_token_actually_appears_in_its_template(fillmap, templates_root):
    from docx import Document

    from autopopulate.engines.docx import _all_paragraphs

    problems = []
    for eid, entry in _entries(fillmap):
        if entry["engine"] != "docx-token":
            continue
        doc = Document(str(templates_root / entry["template"]))
        text = "\n".join(p.text for p in _all_paragraphs(doc))
        for target in entry["targets"]:
            if target["token"] not in text:
                problems.append(f"{eid}: {target['token']} not in {entry['template']}")
    assert problems == [], problems


def test_every_docx_heading_exists_with_a_blank_paragraph_beneath(fillmap, templates_root):
    from docx import Document

    from autopopulate.engines.docx import _is_body_paragraph

    problems = []
    for eid, entry in _entries(fillmap):
        if entry["engine"] != "docx-heading":
            continue
        paragraphs = Document(str(templates_root / entry["template"])).paragraphs
        for target in entry["targets"]:
            heading = target["heading"]
            found = False
            for i, para in enumerate(paragraphs):
                if para.text.strip() != heading.strip():
                    continue
                for candidate in paragraphs[i + 1 :]:
                    if not _is_body_paragraph(candidate):
                        break
                    if candidate.text.strip() == "":
                        found = True
                        break
                break
            if not found:
                problems.append(
                    f"{eid}: heading {heading!r} with a blank paragraph beneath it "
                    f"not found in {entry['template']}"
                )
    assert problems == [], problems


def test_every_dropdown_alias_exists_in_its_template(fillmap, templates_root):
    from docx import Document

    from autopopulate.engines.docx import _dropdown_items, _sdt_alias
    from docx.oxml.ns import qn

    problems = []
    for eid, entry in _entries(fillmap):
        if entry["engine"] != "docx-dropdown":
            continue
        doc = Document(str(templates_root / entry["template"]))
        found = {}
        for sdt in doc.element.body.iter(qn("w:sdt")):
            alias = _sdt_alias(sdt)
            if alias:
                found[alias] = _dropdown_items(sdt)
        for target in entry["targets"]:
            if target["alias"] not in found:
                problems.append(f"{eid}: no content control {target['alias']!r}")
            elif not found[target["alias"]]:
                problems.append(f"{eid}: {target['alias']!r} is not a dropdown list")
    assert problems == [], problems


def test_every_xlsx_target_names_a_real_empty_cell(fillmap, templates_root):
    """The sheet must exist, the cell must be blank (we fill, never overwrite), and
    it must not be a non-top-left merged cell.
    """
    from openpyxl import load_workbook

    from autopopulate.engines.xlsx import _merge_conflict

    problems = []
    for eid, entry in _entries(fillmap):
        if entry["engine"] != "xlsx":
            continue
        wb = load_workbook(str(templates_root / entry["template"]))
        sheet = entry["sheet"]
        if sheet not in wb.sheetnames:
            problems.append(f"{eid}: no sheet {sheet!r} (has {wb.sheetnames})")
            continue
        ws = wb[sheet]
        for target in entry["targets"]:
            coord = target["cell"]
            if ws[coord].value is not None:
                problems.append(
                    f"{eid}: {sheet}!{coord} is not empty "
                    f"({ws[coord].value!r}) — filling it would overwrite template content"
                )
            conflict = _merge_conflict(ws, coord)
            if conflict:
                problems.append(f"{eid}: {sheet}!{coord} is inside merge {conflict}")
    assert problems == [], problems


def test_every_entry_declares_the_destination_key_its_engine_needs(fillmap):
    for eid, entry in _entries(fillmap):
        key = ENGINE_DEST[entry["engine"]]
        for target in entry["targets"]:
            assert key in target, f"{eid}: {entry['template']} target missing {key!r}"
