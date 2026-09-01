"""The demo is production code, so it gets a test too."""

from autopopulate.demo import main

ARTIFACTS = "tests/gtm_generator/fixtures/artifacts"


def test_demo_runs_and_reports_filled_and_flagged(
    repo_root, mini_templates_root, tmp_path, capsys
):
    out = tmp_path / "demo-out"
    code = main(
        [
            "--artifact-dir", str(repo_root / ARTIFACTS / "happy-full"),
            "--templates-root", str(mini_templates_root),
            "--output-dir", str(out),
        ]
    )

    assert code == 0
    printed = capsys.readouterr().out
    assert "FILLED" in printed and "Annual Planning TEMPLATE.docx" in printed
    assert ".FILL-MANUALLY" in printed
    assert "visible skips" in printed
    assert "company-overview" in printed and "positioning" in printed


def test_demo_reports_a_missing_templates_root(repo_root, tmp_path, capsys):
    code = main(
        [
            "--artifact-dir", str(repo_root / ARTIFACTS / "happy-full"),
            "--templates-root", str(tmp_path / "nope"),
            "--output-dir", str(tmp_path / "o"),
        ]
    )
    assert code == 2
    assert "not found" in capsys.readouterr().out
