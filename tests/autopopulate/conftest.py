from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HAPPY_FULL_OUTPUT = REPO_ROOT / "tests" / "gtm_generator" / "fixtures" / "artifacts" / "happy-full" / "output"


@pytest.fixture
def happy_full_dir():
    """The repo's real confirmed sidecars — the content source for autopopulate TDD."""
    assert HAPPY_FULL_OUTPUT.is_dir(), f"missing fixture dir: {HAPPY_FULL_OUTPUT}"
    return HAPPY_FULL_OUTPUT


@pytest.fixture
def repo_root():
    return REPO_ROOT


# --- docx fixture builders -------------------------------------------------

@pytest.fixture
def make_docx_with_token(tmp_path):
    """Build a tiny .docx carrying `token` in a body paragraph AND a table cell.

    Deliberately includes decoy paragraphs that must NOT be touched, and puts the
    token in a *formatted* run so a replacement that collapses runs is detectable.
    Returns a callable(token) -> path to the docx.
    """
    from docx import Document

    counter = {"n": 0}

    def _make(token: str = "[COMPANY]") -> str:
        from docx.shared import Pt

        doc = Document()
        # p0: decoy — no token. A fill that lands here instead is a wrong-location bug.
        doc.add_paragraph("Annual Planning Worksheet")
        # p1: the target. Token sits in its own bold+italic run between plain runs.
        p = doc.add_paragraph()
        p.add_run("Prepared for ")
        r = p.add_run(token)
        r.bold = True
        r.italic = True
        r.font.size = Pt(14)
        p.add_run(" — FY plan")
        # p2: another decoy
        doc.add_paragraph("Do not edit this line.")

        t = doc.add_table(rows=1, cols=2)
        cr = t.rows[0].cells[0].paragraphs[0].add_run(token)
        cr.bold = True
        t.rows[0].cells[1].paragraphs[0].add_run("static")

        counter["n"] += 1
        out = tmp_path / f"tokened-{counter['n']}.docx"
        doc.save(out)
        return str(out)

    return _make


@pytest.fixture
def make_docx_split_token(tmp_path):
    """A .docx where the token is SPLIT across adjacent runs (Word does this a lot)."""
    from docx import Document

    def _make(parts=("[COM", "PANY]")) -> str:
        doc = Document()
        p = doc.add_paragraph()
        p.add_run("Client: ")
        for part in parts:
            run = p.add_run(part)
            run.bold = True
        out = tmp_path / "split-token.docx"
        doc.save(out)
        return str(out)

    return _make


@pytest.fixture
def make_docx_header_footer_token(tmp_path):
    """A .docx carrying the token in the section header and footer."""
    from docx import Document

    def _make(token: str = "[COMPANY]") -> str:
        doc = Document()
        doc.add_paragraph("body, no token")
        sec = doc.sections[0]
        sec.header.paragraphs[0].add_run(f"{token} confidential")
        sec.footer.paragraphs[0].add_run(f"(c) {token}")
        out = tmp_path / "hf-token.docx"
        doc.save(out)
        return str(out)

    return _make


# The Positioning template's real dropdown allowed-lists, verbatim (mind the
# trailing space on "New way " — it is in the actual template).
PRODUCT_TYPE_ITEMS = [
    "10x better than existing solution",
    "New way ",
    "Vertical solution",
    "Buy vs. Build",
]
COMPARATOR_ITEMS = [
    "Current product leader(s) in category",
    "Combo of multiple workflows, tools, and services",
    "Horizontal solution not tailored to audience",
    "Combo of workflows specific to audience",
    "Building & managing internal process or tool",
]


@pytest.fixture
def make_docx_with_headings(tmp_path):
    """A docx shaped like the Positioning worksheet: headings each followed by a blank line.

    Includes decoy blanks (before the target heading, and under a different heading)
    that a correct fill must leave alone.
    """
    from docx import Document

    def _make() -> str:
        doc = Document()
        doc.add_paragraph("")  # decoy blank BEFORE any heading
        doc.add_heading("Positioning Statement", level=1)
        doc.add_paragraph("")  # <- the target
        doc.add_paragraph("Guidance: keep it to one sentence.")
        doc.add_heading("Competitive Map", level=1)
        doc.add_paragraph("")  # decoy blank under a DIFFERENT heading
        out = tmp_path / "headings.docx"
        doc.save(out)
        return str(out)

    return _make


@pytest.fixture
def make_docx_with_dropdown(tmp_path):
    """A docx carrying real w:sdt dropdown content controls, as Word writes them."""
    from docx import Document
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls, qn

    def _sdt_xml(alias, items, placeholder="Choose an item."):
        listitems = "".join(
            '<w:listItem w:displayText="{0}" w:value="{0}"/>'.format(
                i.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
            )
            for i in items
        )
        return (
            f'<w:sdt {nsdecls("w")}>'
            f"<w:sdtPr>"
            f'<w:alias w:val="{alias}"/><w:tag w:val="{alias.replace(" ", "")}"/>'
            f'<w:id w:val="{abs(hash(alias)) % 100000}"/>'
            f"<w:showingPlcHdr/>"
            f"<w:dropDownList>{listitems}</w:dropDownList>"
            f"</w:sdtPr>"
            f"<w:sdtContent><w:r><w:rPr><w:b/></w:rPr>"
            f"<w:t>{placeholder}</w:t></w:r></w:sdtContent>"
            f"</w:sdt>"
        )

    def _make() -> str:
        doc = Document()
        p1 = doc.add_paragraph()
        p1.add_run("Product type: ")
        p1._p.append(parse_xml(_sdt_xml("Product Type", PRODUCT_TYPE_ITEMS)))
        p2 = doc.add_paragraph()
        p2.add_run("Comparator: ")
        p2._p.append(parse_xml(_sdt_xml("Comparator", COMPARATOR_ITEMS)))
        out = tmp_path / "dropdowns.docx"
        doc.save(out)
        assert doc.element.body.findall(f".//{qn('w:sdt')}"), "fixture built no sdt"
        return str(out)

    return _make


def sdt_text(path, alias):
    """Read back the displayed text of the sdt with this alias — world-assertion helper."""
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(path)
    for sdt in doc.element.body.iter(qn("w:sdt")):
        a = sdt.find(f"{qn('w:sdtPr')}/{qn('w:alias')}")
        if a is not None and a.get(qn("w:val")) == alias:
            content = sdt.find(qn("w:sdtContent"))
            return "".join(t.text or "" for t in content.iter(qn("w:t")))
    raise AssertionError(f"no sdt with alias {alias!r}")


def sdt_has_placeholder_flag(path, alias):
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(path)
    for sdt in doc.element.body.iter(qn("w:sdt")):
        pr = sdt.find(qn("w:sdtPr"))
        a = pr.find(qn("w:alias")) if pr is not None else None
        if a is not None and a.get(qn("w:val")) == alias:
            return pr.find(qn("w:showingPlcHdr")) is not None
    raise AssertionError(f"no sdt with alias {alias!r}")


# --- xlsx fixture builders -------------------------------------------------

@pytest.fixture
def make_icp_xlsx(tmp_path):
    """A tiny workbook shaped like the ICP grid.

    - label column A, empty fill columns
    - B2:B10 carries an INLINE type=list validation whose first option has a
      trailing space ("Core ") — real templates do this and Word/Excel match exactly
    - F2:F10 carries a RANGE-backed type=list validation (Lists!$A$1:$A$2)
    - D2:E2 is merged, so E2 is a non-top-left merged cell
    - C4 holds a formula, which must survive a fill (workbook is not data_only)
    """
    from openpyxl import Workbook
    from openpyxl.worksheet.datavalidation import DataValidation

    def _make() -> str:
        wb = Workbook()
        ws = wb.active
        ws.title = "ICP"
        ws["A1"], ws["B1"], ws["C1"] = "Segment", "Priority", "Notes"
        ws["A2"] = "Regional property managers"
        ws["A3"] = "Light manufacturing"
        ws["C4"] = "=LEN(A2)"

        dv = DataValidation(type="list", formula1='"Core ,Scaling"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add("B2:B10")

        lists = wb.create_sheet("Lists")
        lists["A1"], lists["A2"] = "Core ", "Scaling"
        dv2 = DataValidation(type="list", formula1="Lists!$A$1:$A$2", allow_blank=True)
        ws.add_data_validation(dv2)
        dv2.add("F2:F10")

        ws.merge_cells("D2:E2")

        out = tmp_path / "icp.xlsx"
        wb.save(out)
        return str(out)

    return _make


@pytest.fixture
def mini_templates_root(tmp_path):
    """A 2-file templates_root mirroring the real folder tree from MAPPING.md:
    one COVERED docx (Annual Planning, carries [COMPANY]) and one UNCOVERED xlsx.
    """
    from docx import Document
    from openpyxl import Workbook

    root = tmp_path / "templates"
    covered = root / "3. Planning" / "3.3. Annual Planning" / "Annual Planning TEMPLATE.docx"
    covered.parent.mkdir(parents=True)
    doc = Document()
    doc.add_paragraph("Annual Marketing Plan")
    p = doc.add_paragraph()
    p.add_run("Prepared for ")
    p.add_run("[COMPANY]").bold = True
    # The real Annual Planning doc has heading sections with blank paragraphs
    # beneath them, so the fixture carries one too.
    doc.add_heading("OBJECTIVES", level=1)
    doc.add_paragraph("")
    doc.save(covered)

    positioning = (
        root / "1. Foundations" / "1.2. Product Marketing Research"
        / "1.2.3. Product-Service" / "Positioning statement TEMPLATE.docx"
    )
    positioning.parent.mkdir(parents=True)
    pdoc = Document()
    pdoc.add_heading("POSITIONING STATEMENT", level=1)  # verbatim from the real template
    pdoc.add_paragraph("")
    pdoc.add_paragraph("Guidance: one sentence.")
    pdoc.save(positioning)

    uncovered = root / "2. Fuel + Engine" / "2.1. Fuel" / "Website Conversion Assessment TEMPLATE.xlsx"
    uncovered.parent.mkdir(parents=True)
    wb = Workbook()
    wb.active["A1"] = "Page"
    wb.save(uncovered)

    return root


def tree_hashes(root):
    """{relpath: sha256} for every file under root — proves originals are untouched."""
    import hashlib
    from pathlib import Path

    out = {}
    for f in sorted(Path(root).rglob("*")):
        if f.is_file():
            out[str(f.relative_to(root))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


@pytest.fixture
def make_docx_with_toc_cache(tmp_path):
    """A docx shaped like the real Annual Planning doc: a Heading 2 carrying the
    token, plus a Table of Contents whose CACHED entry repeats that heading text.

    Word stores the TOC as a block-level w:sdt; its entries live in w:sdtContent,
    which is NOT a direct child of w:body — so a walk over doc.paragraphs misses it
    entirely and leaves a visible literal token in the deliverable.
    """
    from docx import Document
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    def _make(token: str = "[COMPANY]") -> str:
        doc = Document()
        toc = (
            f'<w:sdt {nsdecls("w")}>'
            "<w:sdtPr><w:docPartObj>"
            '<w:docPartGallery w:val="Table of Contents"/>'
            "</w:docPartObj></w:sdtPr>"
            "<w:sdtContent>"
            '<w:p><w:hyperlink w:anchor="_Toc1"><w:r>'
            f'<w:t xml:space="preserve">Vision and strategy 2025: How {token} '
            "wins with marketing\t1</w:t>"
            "</w:r></w:hyperlink></w:p>"
            "</w:sdtContent></w:sdt>"
        )
        doc.element.body.insert(0, parse_xml(toc))
        doc.add_heading(f"Vision and strategy 2025: How {token} wins with marketing", level=2)
        out = tmp_path / "toc.docx"
        doc.save(out)
        return str(out)

    return _make


@pytest.fixture
def make_docx_with_field_instruction(tmp_path):
    """A docx with the token inside a w:instrText field instruction.

    run.text only reads w:t, so this is genuinely unreachable by the fill engine.
    It exists to prove the residual GUARANTEE: what cannot be filled must be reported.
    """
    from docx import Document
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    def _make(token: str = "[COMPANY]") -> str:
        doc = Document()
        doc.add_paragraph().add_run("nothing to fill here")
        field = (
            f'<w:p {nsdecls("w")}>'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> HYPERLINK "http://{token}.example" '
            "</w:instrText></w:r>"
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            "</w:p>"
        )
        doc.element.body.append(parse_xml(field))
        out = tmp_path / "field.docx"
        doc.save(out)
        return str(out)

    return _make


@pytest.fixture
def make_docx_with_textbox_token(tmp_path):
    """A docx with the token inside a TEXT BOX (w:txbxContent).

    Deliberately a DIFFERENT container from the TOC's w:sdtContent. The fill engine
    does not traverse it, which is the point: it is the probe for the general
    output-scan guarantee, not for any one traversal. Tomorrow's container
    (SmartArt, a comment, an embedded object) behaves the same way.
    """
    from docx import Document
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    def _make(token: str = "[COMPANY]") -> str:
        doc = Document()
        doc.add_paragraph().add_run("body text with no token")
        box = (
            f'<w:p {nsdecls("w")}>'
            "<w:r><w:pict><w:shape><w:txbxContent>"
            f'<w:p><w:r><w:t xml:space="preserve">Callout: {token} at a glance</w:t>'
            "</w:r></w:p>"
            "</w:txbxContent></w:shape></w:pict></w:r></w:p>"
        )
        doc.element.body.append(parse_xml(box))
        out = tmp_path / "textbox.docx"
        doc.save(out)
        return str(out)

    return _make
