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
    shutil.copytree(ROOT / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(ROOT / "skills", tmp_path / "skills")


def test_cli_routes_generate_expected_artifacts(tmp_path):
    copy_project_inputs(tmp_path)
    commands = [
        ("build-packet",),
        ("compare-history",),
        ("overlap-matrix",),
        ("review-ledger",),
        ("static-dashboard",),
        ("release-manifest",),
        ("maturity-report",),
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
        "demo/static_dashboard.html",
        "demo/release_manifest.md",
        "demo/release_manifest.json",
        "demo/maturity_report.md",
        "demo/maturity_report.json",
    ]
    for rel in expected:
        assert (tmp_path / rel).exists(), rel

    packet = json.loads((tmp_path / "demo/exposure_packet.json").read_text(encoding="utf-8"))
    assert packet["portfolio_id"] == "2026Q2_SAMPLE"
    assert packet["total_exposure"] == 1.0


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
