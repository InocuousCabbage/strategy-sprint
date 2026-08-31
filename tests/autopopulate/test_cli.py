"""CLI tests: python -m autopopulate --artifact-dir X --exercise-id Y --output-dir Z."""

import pytest
from docx import Document

from autopopulate.cli import main

ARTIFACTS = "tests/gtm_generator/fixtures/artifacts"


def test_cli_populates_and_summarises(repo_root, mini_templates_root, tmp_path, capsys):
    out = tmp_path / "out"
    code = main(
        [
            "--artifact-dir", str(repo_root / ARTIFACTS / "happy-full"),
            "--exercise-id", "company-overview",
            "--output-dir", str(out),
            "--templates-root", str(mini_templates_root),
        ]
    )

    assert code == 0
    copy = out / "3. Planning" / "3.3. Annual Planning" / "Annual Planning TEMPLATE.docx"
    assert Document(str(copy)).paragraphs[1].text == "Prepared for Acme Corp"

    printed = capsys.readouterr().out
    assert "filled" in printed.lower()
    assert "company-overview.fill-report.md" in printed


def test_cli_surfaces_skips_in_its_summary(repo_root, mini_templates_root, tmp_path, capsys):
    """VISIBLE SKIP reaches the terminal too, not just the files."""
    fm = tmp_path / "thin.yaml"
    fm.write_text(
        "company-overview:\n"
        "  - template: '3. Planning/3.3. Annual Planning/Annual Planning TEMPLATE.docx'\n"
        "    engine: docx-token\n"
        "    targets:\n"
        "      - source: company.name\n        token: '[COMPANY]'\n"
        "      - source: company.tagline\n        token: '[TAGLINE]'\n"
    )
    code = main(
        [
            "--artifact-dir", str(repo_root / ARTIFACTS / "happy-full"),
            "--exercise-id", "company-overview",
            "--output-dir", str(tmp_path / "out"),
            "--templates-root", str(mini_templates_root),
            "--fillmap", str(fm),
        ]
    )

    assert code == 0
    printed = capsys.readouterr().out
    assert "company.tagline" in printed


def test_cli_refuses_an_unconfirmed_exercise(repo_root, mini_templates_root, tmp_path, capsys):
    out = tmp_path / "out"
    code = main(
        [
            "--artifact-dir", str(repo_root / ARTIFACTS / "unconfirmed"),
            "--exercise-id", "company-overview",
            "--output-dir", str(out),
            "--templates-root", str(mini_templates_root),
        ]
    )

    assert code != 0
    assert not out.exists() or list(out.rglob("*")) == []
    assert "confirmedByClient" in capsys.readouterr().err
