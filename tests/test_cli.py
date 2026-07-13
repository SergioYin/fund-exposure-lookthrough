import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "fund_exposure_lookthrough.cli", *args],
        cwd=tmp_path,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def copy_project_inputs(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "examples", tmp_path / "examples")
    shutil.copy(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    shutil.copy(ROOT / "README.md", tmp_path / "README.md")
    shutil.copy(ROOT / "LICENSE", tmp_path / "LICENSE")
    shutil.copy(ROOT / "CHANGELOG.md", tmp_path / "CHANGELOG.md")
    shutil.copy(ROOT / "RELEASE_NOTES.md", tmp_path / "RELEASE_NOTES.md")
    shutil.copytree(ROOT / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(ROOT / "skills", tmp_path / "skills")


def test_cli_routes_generate_expected_artifacts(tmp_path):
    copy_project_inputs(tmp_path)
    commands = [
        ("build-packet",),
        ("compare-history",),
        ("overlap-matrix",),
        ("review-ledger",),
        ("fixture-doctor",),
        ("static-dashboard",),
        ("case-gallery",),
        ("reviewer-scorecard",),
        ("visual-receipt",),
        ("release-manifest",),
        ("maturity-report",),
        ("readme-snippet",),
        ("asset-health",),
        ("bundle-export",),
    ]

    for command in commands:
        result = run_cli(tmp_path, *command, "--root", ".")
        assert result.returncode == 0, result.stderr

    expected = [
        "demo/exposure_packet.md",
        "demo/exposure_packet.json",
        "demo/history_comparison.md",
        "demo/history_comparison.json",
        "demo/overlap_matrix.md",
        "demo/overlap_matrix.json",
        "demo/review_ledger.md",
        "demo/review_ledger.json",
        "demo/fixture_doctor.md",
        "demo/fixture_doctor.json",
        "demo/static_dashboard.html",
        "demo/case_gallery.md",
        "demo/case_gallery.json",
        "demo/reviewer_scorecard.md",
        "demo/reviewer_scorecard.json",
        "demo/visual_receipt.svg",
        "demo/release_manifest.md",
        "demo/release_manifest.json",
        "demo/maturity_report.md",
        "demo/maturity_report.json",
        "demo/readme_snippet.md",
        "demo/bundle_export/manifest.md",
        "demo/bundle_export/manifest.json",
        "demo/bundle_export/artifacts/demo/exposure_packet.md",
        "demo/asset_health.md",
        "demo/asset_health.json",
    ]
    for rel in expected:
        assert (tmp_path / rel).exists(), rel

    packet = json.loads((tmp_path / "demo/exposure_packet.json").read_text(encoding="utf-8"))
    assert packet["portfolio_id"] == "2026Q2_SAMPLE"
    assert packet["total_exposure"] == 1.0

    gallery = json.loads((tmp_path / "demo/case_gallery.json").read_text(encoding="utf-8"))
    assert [case["name"] for case in gallery["cases"]] == [
        "Bundled current portfolio",
        "Bundled prior portfolio",
        "Direct holding and ETF wrapper",
    ]
    assert gallery["cases"][2]["portfolio_id"] == "2026Q2_DIRECT_WRAPPER"

    scorecard = json.loads((tmp_path / "demo/reviewer_scorecard.json").read_text(encoding="utf-8"))
    assert scorecard["score"] == scorecard["max_score"]
    assert "Public Showcase Receipt" in (tmp_path / "demo/visual_receipt.svg").read_text(encoding="utf-8")

    bundle = json.loads((tmp_path / "demo/bundle_export/manifest.json").read_text(encoding="utf-8"))
    assert bundle["artifact_count"] >= 20
    assert bundle["missing"] == []

    health = json.loads((tmp_path / "demo/asset_health.json").read_text(encoding="utf-8"))
    assert health["ok"] is True
    assert {row["name"] for row in health["commands"]} >= {"bundle-export", "asset-health", "readme-snippet"}
    assert all(health["package_data"].values())
    assert all(health["safety_boundaries"].values())
    assert "Quickstart Demo" in (tmp_path / "demo/readme_snippet.md").read_text(encoding="utf-8")


def test_selfcheck_and_safety_language(tmp_path):
    copy_project_inputs(tmp_path)
    result = run_cli(tmp_path, "selfcheck", "--root", ".")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "not investment advice" in payload["safety"]
    assert "recommend" in payload["safety"]


def test_public_scan_reports_no_private_leakage(tmp_path):
    copy_project_inputs(tmp_path)
    result = run_cli(tmp_path, "public-scan", "--root", ".")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["findings"] == []


def test_package_data_fallback_without_examples_directory(tmp_path):
    result = run_cli(tmp_path, "build-packet", "--root", ".")

    assert result.returncode == 0, result.stderr
    packet = json.loads((tmp_path / "demo/exposure_packet.json").read_text(encoding="utf-8"))
    assert packet["portfolio_id"] == "2026Q2_SAMPLE"
    assert packet["total_exposure"] == 1.0

    gallery = run_cli(tmp_path, "case-gallery", "--root", ".")
    assert gallery.returncode == 0, gallery.stderr
    payload = json.loads((tmp_path / "demo/case_gallery.json").read_text(encoding="utf-8"))
    assert payload["cases"][2]["portfolio_id"] == "2026Q2_DIRECT_WRAPPER"


def test_deterministic_outputs_for_packet(tmp_path):
    copy_project_inputs(tmp_path)
    first = run_cli(tmp_path, "build-packet", "--root", ".")
    assert first.returncode == 0, first.stderr
    first_json = (tmp_path / "demo/exposure_packet.json").read_bytes()
    first_md = (tmp_path / "demo/exposure_packet.md").read_bytes()

    second = run_cli(tmp_path, "build-packet", "--root", ".")
    assert second.returncode == 0, second.stderr

    assert (tmp_path / "demo/exposure_packet.json").read_bytes() == first_json
    assert (tmp_path / "demo/exposure_packet.md").read_bytes() == first_md


def test_deterministic_showcase_outputs(tmp_path):
    copy_project_inputs(tmp_path)
    for command in [("case-gallery",), ("reviewer-scorecard",), ("visual-receipt",), ("readme-snippet",), ("bundle-export",)]:
        first = run_cli(tmp_path, *command, "--root", ".")
        assert first.returncode == 0, first.stderr
    first_gallery = (tmp_path / "demo/case_gallery.json").read_bytes()
    first_scorecard = (tmp_path / "demo/reviewer_scorecard.json").read_bytes()
    first_receipt = (tmp_path / "demo/visual_receipt.svg").read_bytes()
    first_snippet = (tmp_path / "demo/readme_snippet.md").read_bytes()
    first_bundle = (tmp_path / "demo/bundle_export/manifest.json").read_bytes()

    for command in [("case-gallery",), ("reviewer-scorecard",), ("visual-receipt",), ("readme-snippet",), ("bundle-export",)]:
        second = run_cli(tmp_path, *command, "--root", ".")
        assert second.returncode == 0, second.stderr

    assert (tmp_path / "demo/case_gallery.json").read_bytes() == first_gallery
    assert (tmp_path / "demo/reviewer_scorecard.json").read_bytes() == first_scorecard
    assert (tmp_path / "demo/visual_receipt.svg").read_bytes() == first_receipt
    assert (tmp_path / "demo/readme_snippet.md").read_bytes() == first_snippet
    assert (tmp_path / "demo/bundle_export/manifest.json").read_bytes() == first_bundle


def test_fixture_doctor_reports_clean_examples(tmp_path):
    copy_project_inputs(tmp_path)
    result = run_cli(tmp_path, "fixture-doctor", "--root", ".")

    assert result.returncode == 0, result.stderr
    payload = json.loads((tmp_path / "demo/fixture_doctor.json").read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["summary"] == {"error": 0, "info": 0, "total": 0, "warning": 0}
    assert "No fixture quality findings" in (tmp_path / "demo/fixture_doctor.md").read_text(encoding="utf-8")


def test_fixture_doctor_flags_bad_fixtures(tmp_path):
    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "current_portfolio.csv").write_text(
        "\n".join(
            [
                "portfolio_id,fund_id,fund_name,weight,source_date,source_url",
                "BAD,FND_CORE,Core,0.60,2024-01-01,https://example.com/core",
                "BAD,FND_CORE,Core duplicate,0.20,2024-01-01,https://example.com/core",
                "BAD,FND_MISSING,Missing Fund,0.10,2024-01-01,not-a-url",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (examples / "fund_constituents.csv").write_text(
        "\n".join(
            [
                "fund_id,asset_id,asset_name,weight,sector,region,asset_class,source_date,source_url",
                "FND_CORE,AST_ALPHA,Alpha,0.40,Technology,North America,Equity,2024-01-01,https://example.com/constituents",
                "FND_CORE,AST_ALPHA,Alpha duplicate,0.40,Technology,North America,Equity,2024-01-01,https://example.com/constituents",
                "FND_ORPHAN,AST_BETA,Beta,1.00,Consumer,Europe,Equity,2024-01-01,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_cli(tmp_path, "fixture-doctor", "--root", ".", "--as-of", "2026-07-14", "--max-source-age-days", "370")

    assert result.returncode == 1
    payload = json.loads((tmp_path / "demo/fixture_doctor.json").read_text(encoding="utf-8"))
    codes = {item["code"] for item in payload["findings"]}
    assert "portfolio_weight_total" in codes
    assert "missing_constituents" in codes
    assert "constituent_weight_total" in codes
    assert "portfolio_duplicate_fund" in codes
    assert "constituent_duplicate_asset" in codes
    assert "unheld_constituent_fund" in codes
    assert "stale_source_date" in codes
    assert "missing_source_url" in codes
    assert "non_http_source_url" in codes
