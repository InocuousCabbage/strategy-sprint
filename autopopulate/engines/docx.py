"""DOCX fill engine.

Formatting discipline (non-negotiable): we edit ``run.text`` only. We NEVER assign
``paragraph.text = ...`` — that collapses every run in the paragraph into one and
throws away the bold/italic/size/style the consultant's template carries.

A token may be split across adjacent runs (Word does this constantly, e.g.
``[COM`` + ``PANY]``). We handle that by merging the minimal span of runs that
covers the token into the span's FIRST run, which keeps that run's formatting.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph


def residual_docx_tokens(path: str | Path, tokens) -> dict[str, int]:
    """Count fill-map-declared token literals STILL PRESENT in a finished docx.

    This is the primary guarantee, and it deliberately does NOT use python-docx's
    paragraph tree: it unzips the finished package and greps every xml part. The
    paragraph tree is exactly what missed the TOC cache, and it would miss the next
    container too — a text box, SmartArt, a comment, an embedded object. Scanning
    the written bytes is container-agnostic, so a survivor is reported no matter
    where it hid.

    Note the one thing it cannot see: a token split across runs is not a literal in
    the XML. That case is handled by the fill itself, which merges runs.
    """
    counts = {token: 0 for token in tokens}
    with zipfile.ZipFile(str(path)) as z:
        for name in z.namelist():
            if not name.lower().endswith(".xml"):
                continue
            raw = z.read(name).decode("utf-8", "replace")
            for token in counts:
                counts[token] += raw.count(token)
    return counts


def _sdt_content_paragraphs(root, parent):
    """Paragraphs inside block-level content controls (a TOC is one of these).

    Only OUTERMOST w:sdt elements are entered: a nested control's paragraphs are
    already covered by its ancestor's subtree, and yielding them twice would double
    every replacement count.
    """
    for sdt in root.iter(qn("w:sdt")):
        ancestor = sdt.getparent()
        nested = False
        while ancestor is not None:
            if ancestor.tag == qn("w:sdt"):
                nested = True
                break
            ancestor = ancestor.getparent()
        if nested:
            continue
        content = sdt.find(qn("w:sdtContent"))
        if content is None:
            continue
        for p_el in content.iter(qn("w:p")):
            yield Paragraph(p_el, parent)


def _iter_paragraphs(container):
    """Yield every paragraph in a container, descending into tables (incl. nested)."""
    yield from getattr(container, "paragraphs", [])
    for table in getattr(container, "tables", []):
        for row in table.rows:
            for cell in row.cells:
                yield from _iter_paragraphs(cell)


def _all_paragraphs(doc):
    """Every paragraph in the document, each exactly once.

    Deliberately does NOT de-duplicate by element identity: lxml element proxies
    are transient, so ``id()`` values get recycled and a later paragraph collides
    with a freed one's id and is dropped from the walk — a fill that silently
    never happens. Sections that inherit a header/footer are skipped instead, via
    ``is_linked_to_previous``, which is the actual document-level fact.
    """
    yield from _iter_paragraphs(doc)
    # A block-level content control's paragraphs are NOT children of w:body, so
    # doc.paragraphs never sees them. Word's Table of Contents is one of these, and
    # its cached entries repeat heading text verbatim — a token in a heading appears
    # a second time in the cache. Reporting that residual is not enough: a PDF export
    # or a viewer that does not refresh fields still shows the literal, so it is
    # filled here rather than left for Word to fix.
    yield from _sdt_content_paragraphs(doc.element.body, doc)
    for section in doc.sections:
        for part in (section.header, section.footer):
            if part.is_linked_to_previous:
                continue  # inherited from an earlier section; already walked there
            yield from _iter_paragraphs(part)
            yield from _sdt_content_paragraphs(part._element, part)


#: Elements that wrap runs belonging to the SAME paragraph. A TOC entry's runs sit
#: inside w:hyperlink, so a walk over direct w:p children misses them entirely.
_RUN_WRAPPERS = ("w:hyperlink", "w:ins", "w:smartTag")


def _runs_of(element) -> list:
    """Run elements owned by this paragraph, in document order.

    Descends ONLY into wrappers that hold runs of the same paragraph. It never
    enters w:sdt (an inline content control is the dropdown engine's business) and
    never enters a text box, picture or drawing, whose runs belong to their own
    nested w:p — splicing those into this paragraph's text would corrupt offsets and
    edit content that is not ours.
    """
    found = []
    for child in element:
        if child.tag == qn("w:r"):
            found.append(child)
        elif child.tag in {qn(w) for w in _RUN_WRAPPERS}:
            found.extend(_runs_of(child))
    return found


def _paragraph_runs(paragraph) -> list:
    from docx.text.run import Run

    return [Run(r, paragraph) for r in _runs_of(paragraph._p)]


def _replace_in_paragraph(paragraph, token: str, value: str) -> int:
    """Replace every ``token`` in one paragraph at run level. Returns the count."""
    count = 0
    search_from = 0
    while True:
        runs = _paragraph_runs(paragraph)
        texts = [r.text for r in runs]
        joined = "".join(texts)
        idx = joined.find(token, search_from)
        if idx == -1:
            return count
        end = idx + len(token)

        starts = []
        pos = 0
        for t in texts:
            starts.append(pos)
            pos += len(t)

        first = last = None
        for i, t in enumerate(texts):
            s, e = starts[i], starts[i] + len(t)
            if first is None and s <= idx < e:
                first = i
            if first is not None and s < end <= e:
                last = i
                break
        if first is None or last is None:
            return count

        merged = "".join(texts[first : last + 1])
        local = idx - starts[first]
        runs[first].text = merged[:local] + value + merged[local + len(token) :]
        # Runs consumed by the merge are removed, not left as empty stubs.
        for r in runs[first + 1 : last + 1]:
            r._element.getparent().remove(r._element)

        count += 1
        # Step past the inserted value so a value containing the token can't loop.
        search_from = idx + len(value)


def fill_docx_token_counts(path: str | Path, tokens: dict[str, str]) -> dict[str, int]:
    """Replace each literal ``[TOKEN]`` throughout a docx COPY, preserving runs.

    Walks body paragraphs, table cells (nested included), and every section's
    header and footer. A token with no mapping is left in place verbatim — the
    consultant sees the unfilled placeholder rather than an invented value.

    Returns replacements PER TOKEN. The per-token breakdown is the point: a total
    would let a token that appears nowhere in the template hide behind a sibling
    token that matched, and that field would go unfilled with nothing reported.
    """
    p = Path(path)
    doc = Document(str(p))

    counts = {token: 0 for token in tokens}
    for paragraph in _all_paragraphs(doc):
        for token, value in tokens.items():
            counts[token] += _replace_in_paragraph(paragraph, token, str(value))

    if any(counts.values()):
        _mark_fields_for_update(doc)
        doc.save(str(p))
    return counts


#: Elements that follow w:updateFields in the CT_Settings sequence. Settings is an
#: ordered schema, so the flag is inserted before the first of these rather than
#: appended blindly.
_SETTINGS_AFTER_UPDATE_FIELDS = (
    "hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids",
    "mathPr", "attachedSchema", "themeFontLang", "clrSchemeMapping",
    "doNotIncludeSubdocsInStats", "doNotAutoCompressPictures", "forceUpgrade",
    "captions", "readModeInkLockDown", "smartTagType", "schemaLibrary",
    "shapeDefaults", "doNotEmbedSmartTags", "decimalSymbol", "listSeparator",
)


def _mark_fields_for_update(doc) -> None:
    """Ask Word to refresh fields (the TOC) when the document is opened.

    Belt, not braces: the cached text is replaced directly by the fill above, because
    anything that renders the file without refreshing fields would otherwise still
    show a literal token. This only covers drift introduced later.
    """
    settings = doc.settings.element
    existing = settings.find(qn("w:updateFields"))
    if existing is not None:
        existing.set(qn("w:val"), "true")
        return
    el = settings.makeelement(qn("w:updateFields"), {qn("w:val"): "true"})
    for child in settings:
        if child.tag.split("}")[-1] in _SETTINGS_AFTER_UPDATE_FIELDS:
            child.addprevious(el)
            return
    settings.append(el)


def fill_docx_tokens(path: str | Path, tokens: dict[str, str]) -> int:
    """Total replacements made. See :func:`fill_docx_token_counts` for the detail."""
    return sum(fill_docx_token_counts(path, tokens).values())


class DropdownValueError(ValueError):
    """Raised when a value is not one of a dropdown content control's allowed options."""


_BODY_STYLE_PREFIXES = ("Heading", "Title", "Subtitle", "TOC")


def _is_body_paragraph(paragraph) -> bool:
    """True for a normal prose paragraph — not a heading/title/TOC entry."""
    name = (paragraph.style.name or "") if paragraph.style is not None else ""
    return not name.startswith(_BODY_STYLE_PREFIXES)


def fill_docx_under_heading(path: str | Path, heading_text: str, value: str) -> bool:
    """Write ``value`` into the first blank body paragraph AFTER ``heading_text``.

    Returns True if it filled, False if the heading was not found or had no blank
    paragraph beneath it before the next heading. False is a REPORTABLE skip: the
    caller records it so the consultant sees the field went unfilled — we never
    guess at a different location.
    """
    p = Path(path)
    doc = Document(str(p))
    paragraphs = doc.paragraphs

    for i, para in enumerate(paragraphs):
        if para.text.strip() != heading_text.strip():
            continue
        for candidate in paragraphs[i + 1 :]:
            if not _is_body_paragraph(candidate):
                break  # next heading reached — this section has no blank to fill
            if candidate.text.strip() == "":
                # Add a run rather than assigning .text, so the paragraph keeps its style.
                candidate.add_run(str(value))
                doc.save(str(p))
                return True
        return False
    return False


def _sdt_alias(sdt) -> str | None:
    from docx.oxml.ns import qn

    pr = sdt.find(qn("w:sdtPr"))
    if pr is None:
        return None
    alias = pr.find(qn("w:alias"))
    return None if alias is None else alias.get(qn("w:val"))


def _dropdown_items(sdt) -> list[str] | None:
    """The control's allowed options, read from the DOCUMENT — never hardcoded."""
    from docx.oxml.ns import qn

    pr = sdt.find(qn("w:sdtPr"))
    if pr is None:
        return None
    ddl = pr.find(qn("w:dropDownList"))
    if ddl is None:
        return None
    items = []
    for li in ddl.findall(qn("w:listItem")):
        items.append(li.get(qn("w:displayText")) or li.get(qn("w:value")) or "")
    return items


def set_docx_dropdown(path: str | Path, alias: str, value: str) -> bool:
    """Set the dropdown content control named ``alias`` to ``value``.

    ``value`` is matched against the control's own allowed list, compared trimmed,
    but the option is written back VERBATIM as the template spells it (the real
    Positioning template has "New way " with a trailing space, and Word only
    honours an exact match). A value outside the list raises ``DropdownValueError``
    rather than writing an option Word would reject.

    Returns True if set, False if no control carries that alias (a reportable skip).
    """
    from docx.oxml.ns import qn

    p = Path(path)
    doc = Document(str(p))

    for sdt in doc.element.body.iter(qn("w:sdt")):
        if _sdt_alias(sdt) != alias:
            continue

        allowed = _dropdown_items(sdt)
        if allowed is None:
            raise DropdownValueError(f"content control {alias!r} is not a dropdown list")

        match = next((o for o in allowed if o.strip() == str(value).strip()), None)
        if match is None:
            raise DropdownValueError(
                f"{value!r} is not an allowed option for {alias!r}; allowed: {allowed!r}"
            )

        content = sdt.find(qn("w:sdtContent"))
        # An INLINE sdt holds runs directly; a BLOCK-LEVEL one holds paragraphs.
        # A bare w:r is not a legal child of w:sdtContent, and Word reports a
        # document containing one as corrupt — so descend rather than append.
        runs = content.findall(qn("w:r")) or content.findall(f".//{qn('w:r')}")
        if not runs:
            parent = content.find(qn("w:p"))
            if parent is None:
                parent = content
            run = parent.makeelement(qn("w:r"), {})
            parent.append(run)
            runs = [run]
        # Keep the first run (and its rPr); write into its w:t. Drop the rest.
        first = runs[0]
        for extra in runs[1:]:
            extra.getparent().remove(extra)
        t = first.find(qn("w:t"))
        if t is None:
            t = first.makeelement(qn("w:t"), {})
            first.append(t)
        t.text = match
        t.set(
            "{http://www.w3.org/XML/1998/namespace}space", "preserve"
        )  # trailing space must survive

        # Clear the "showing placeholder" flag — the control now holds real content.
        pr = sdt.find(qn("w:sdtPr"))
        plc = pr.find(qn("w:showingPlcHdr")) if pr is not None else None
        if plc is not None:
            pr.remove(plc)

        doc.save(str(p))
        return True

    return False
