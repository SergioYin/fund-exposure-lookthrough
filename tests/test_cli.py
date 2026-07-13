import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from fund_exposure_lookthrough import __version__
from fund_exposure_lookthrough.cli import _command_names, build_parser


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
    shutil.copy(ROOT / "build_backend.py", tmp_path / "build_backend.py")
    shutil.copytree(ROOT / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(ROOT / "skills", tmp_path / "skills")
    shutil.copytree(ROOT / "tests", tmp_path / "tests", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def test_command_matrix_registry_matches_argparse_routes():
    parser = build_parser()
    subparsers_action = next(action for action in parser._actions if getattr(action, "dest", None) == "command")

    assert set(_command_names()) == set(subparsers_action.choices)

    for spec in _command_names():
        command = subparsers_action.choices[spec]
        assert command.format_help().startswith(f"usage: fund-exposure-lookthrough {spec}")


def test_public_release_routes_are_explicitly_covered_by_command_metadata():
    specs = {spec["name"]: spec for spec in build_parser_command_specs()}
    public_routes = {
        "final-handoff": ["demo/final_handoff.md", "demo/final_handoff.json"],
        "public-readiness": ["demo/public_readiness.md", "demo/public_readiness.json"],
        "landing-page": ["demo/index.html"],
        "docs-export": ["demo/cli_help.md", "demo/cli_help.json"],
        "policy-profile": ["demo/policy_profile.md", "demo/policy_profile.json"],
        "policy-compare": ["demo/policy_compare.md", "demo/policy_compare.json"],
        "policy-gallery": ["demo/policy_gallery.md", "demo/policy_gallery.json"],
        "maintainer-note": ["demo/maintainer_note.md", "demo/maintainer_note.json"],
        "final-qa": ["demo/final_qa.md", "demo/final_qa.json"],
    }

    for route, outputs in public_routes.items():
        assert route in specs
        assert specs[route]["outputs"] == outputs
        assert route in specs[route]["regeneration_command"]
        assert specs[route]["exit_codes"]


def build_parser_command_specs():
    from fund_exposure_lookthrough.cli import _command_specs

    return _command_specs()


def test_cli_routes_generate_expected_artifacts(tmp_path):
    copy_project_inputs(tmp_path)
    commands = [
        ("build-packet",),
        ("policy-profile",),
        ("policy-compare",),
        ("policy-gallery",),
        ("compare-history",),
        ("overlap-matrix",),
        ("review-ledger",),
        ("fixture-doctor",),
        ("static-dashboard",),
        ("case-gallery",),
        ("reviewer-scorecard",),
        ("maturity-report",),
        ("command-matrix",),
        ("release-checklist",),
        ("public-readiness",),
        ("docs-export",),
        ("landing-page",),
        ("visual-receipt",),
        ("promotion-pack",),
        ("readme-snippet",),
        ("release-manifest",),
        ("artifact-catalog",),
        ("release-compare",),
        ("snapshot-ledger",),
        ("snapshot-compare",),
        ("adoption-notes",),
        ("asset-health",),
        ("review-queue",),
        ("final-handoff",),
        ("maintainer-note",),
        ("final-qa",),
        ("bundle-export",),
    ]
    assert set(_command_names()) - {"selfcheck", "public-scan"} == {command[0] for command in commands}

    for command in commands:
        result = run_cli(tmp_path, *command, "--root", ".")
        assert result.returncode == 0, result.stderr

    expected = [
        "demo/exposure_packet.md",
        "demo/exposure_packet.json",
        "demo/policy_profile.md",
        "demo/policy_profile.json",
        "demo/policy_compare.md",
        "demo/policy_compare.json",
        "demo/policy_gallery.md",
        "demo/policy_gallery.json",
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
        "demo/release_compare.md",
        "demo/release_compare.json",
        "demo/maturity_report.md",
        "demo/maturity_report.json",
        "demo/artifact_catalog.md",
        "demo/artifact_catalog.json",
        "demo/command_matrix.md",
        "demo/command_matrix.json",
        "demo/release_checklist.md",
        "demo/release_checklist.json",
        "demo/final_handoff.md",
        "demo/final_handoff.json",
        "demo/maintainer_note.md",
        "demo/maintainer_note.json",
        "demo/final_qa.md",
        "demo/final_qa.json",
        "demo/public_readiness.md",
        "demo/public_readiness.json",
        "demo/promotion_pack.md",
        "demo/promotion_pack.json",
        "demo/adoption_notes.md",
        "demo/adoption_notes.json",
        "demo/cli_help.md",
        "demo/cli_help.json",
        "demo/snapshot_ledger.md",
        "demo/snapshot_ledger.json",
        "demo/snapshot_compare.md",
        "demo/snapshot_compare.json",
        "demo/review_queue.md",
        "demo/review_queue.json",
        "demo/index.html",
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
    assert len(packet["assets"]) == packet["asset_count"]

    policy = json.loads((tmp_path / "demo/policy_profile.json").read_text(encoding="utf-8"))
    assert policy["profile"] == "balanced"
    assert policy["policy_boundary"].startswith("Research-only threshold review")
    assert "allocation recommendation" in policy["policy_boundary"]
    assert {"asset", "sector", "region", "asset_class"} == set(policy["thresholds"])

    policy_compare = json.loads((tmp_path / "demo/policy_compare.json").read_text(encoding="utf-8"))
    assert policy_compare["summary"] == {"added_flags": 0, "removed_flags": 0, "shared_flags": policy["flag_count"]}

    policy_gallery = json.loads((tmp_path / "demo/policy_gallery.json").read_text(encoding="utf-8"))
    assert [case["name"] for case in policy_gallery["examples"]] == [
        "Bundled current portfolio",
        "Bundled prior portfolio",
        "Direct holding and ETF wrapper",
    ]
    assert {profile["profile"] for case in policy_gallery["examples"] for profile in case["profiles"]} == {
        "balanced",
        "concentrated",
        "conservative",
    }

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
    assert [row["route"] for row in bundle["artifacts"]] == sorted(row["route"] for row in bundle["artifacts"])

    health = json.loads((tmp_path / "demo/asset_health.json").read_text(encoding="utf-8"))
    assert health["ok"] is True
    assert {row["name"] for row in health["commands"]} >= {
        "bundle-export",
        "asset-health",
        "artifact-catalog",
        "command-matrix",
        "release-checklist",
        "final-handoff",
        "readme-snippet",
        "public-readiness",
        "landing-page",
        "docs-export",
        "snapshot-ledger",
        "snapshot-compare",
        "review-queue",
        "policy-profile",
        "policy-compare",
        "policy-gallery",
        "release-compare",
        "promotion-pack",
        "adoption-notes",
        "final-qa",
    }
    assert all(health["package_data"].values())
    assert all(health["safety_boundaries"].values())
    assert "Quickstart Demo" in (tmp_path / "demo/readme_snippet.md").read_text(encoding="utf-8")

    catalog = json.loads((tmp_path / "demo/artifact_catalog.json").read_text(encoding="utf-8"))
    assert catalog["artifact_count"] >= 20
    assert {"path", "type", "bytes", "sha256", "regeneration_command"} <= set(catalog["artifacts"][0])
    assert any(row["path"] == "demo/exposure_packet.json" for row in catalog["artifacts"])
    assert [row["path"] for row in catalog["artifacts"]] == sorted(row["path"] for row in catalog["artifacts"])

    matrix = json.loads((tmp_path / "demo/command_matrix.json").read_text(encoding="utf-8"))
    assert matrix["command_count"] == len(matrix["commands"])
    assert {row["name"] for row in matrix["commands"]} >= {"artifact-catalog", "command-matrix", "release-checklist", "final-handoff", "maintainer-note", "final-qa", "release-compare", "promotion-pack", "adoption-notes"}
    assert all(row["inputs"] and row["outputs"] and row["exit_codes"] for row in matrix["commands"])

    checklist = json.loads((tmp_path / "demo/release_checklist.json").read_text(encoding="utf-8"))
    assert checklist["ok"] is True
    assert {row["name"] for row in checklist["checks"]} >= {"tests", "package", "wheel-smoke", "public-scan", "no-advice-boundaries"}

    handoff = json.loads((tmp_path / "demo/final_handoff.json").read_text(encoding="utf-8"))
    assert handoff["release_version"] == __version__
    assert handoff["repo_url"] == "REPO_URL_PLACEHOLDER"
    assert {row["name"] for row in handoff["verification_commands"]} >= {"tests", "selfcheck", "public-scan", "wheel-build", "wheel-smoke"}
    assert "no live data fetching" in handoff["boundaries"]
    assert "REPO_URL_PLACEHOLDER" in (tmp_path / "demo/final_handoff.md").read_text(encoding="utf-8")

    maintainer = json.loads((tmp_path / "demo/maintainer_note.json").read_text(encoding="utf-8"))
    assert maintainer["version"] == __version__
    assert maintainer["purpose"] == "deterministic maintainer note for docs and packaging evidence"
    assert "python -m pytest -q" in maintainer["verification"]
    assert "no live data fetching" in maintainer["boundaries"]

    final_qa = json.loads((tmp_path / "demo/final_qa.json").read_text(encoding="utf-8"))
    assert final_qa["baseline"] == "v0.5.0"
    assert final_qa["release_version"] == __version__
    assert {row["name"] for row in final_qa["verification_commands"]} >= {"tests", "selfcheck", "public-scan", "release-checklist", "wheel-build", "wheel-smoke"}
    assert "not investment advice" in final_qa["no_advice_boundaries"]
    assert final_qa["coherence"]["runtime_dependencies_empty"] is True
    assert final_qa["coherence"]["no_workflow_automation"] is True

    readiness = json.loads((tmp_path / "demo/public_readiness.json").read_text(encoding="utf-8"))
    assert readiness["walkthrough"] == "first-10-minute cold-user walkthrough"
    assert len(readiness["steps"]) == 10
    assert readiness["steps"][0]["minute"] == "0-1"

    docs = json.loads((tmp_path / "demo/cli_help.json").read_text(encoding="utf-8"))
    assert docs["command_count"] == len(docs["commands"])
    assert {row["name"] for row in docs["commands"]} >= {"public-readiness", "landing-page", "docs-export", "snapshot-ledger", "snapshot-compare", "review-queue", "policy-profile", "policy-compare", "policy-gallery", "release-compare", "promotion-pack", "adoption-notes", "final-qa"}
    assert "usage: fund-exposure-lookthrough" in docs["top_level_help"]

    landing = (tmp_path / "demo/index.html").read_text(encoding="utf-8")
    assert "public_readiness.md" in landing
    assert "No live data fetching" in landing

    snapshot = json.loads((tmp_path / "demo/snapshot_ledger.json").read_text(encoding="utf-8"))
    assert snapshot["entry_count"] == 1
    assert snapshot["current_snapshot"]["artifact_count"] >= 20
    assert "timestamp" not in json.dumps(snapshot).lower()

    comparison = json.loads((tmp_path / "demo/snapshot_compare.json").read_text(encoding="utf-8"))
    assert comparison["summary"] == {"added": 0, "changed": 0, "removed": 0}

    queue = json.loads((tmp_path / "demo/review_queue.json").read_text(encoding="utf-8"))
    assert queue["question_count"] >= 1
    assert {"rank", "priority", "source", "topic", "question"} <= set(queue["questions"][0])

    release_compare = json.loads((tmp_path / "demo/release_compare.json").read_text(encoding="utf-8"))
    assert release_compare["summary"]["metadata_changed"] >= 1
    assert release_compare["left"]["kind"] == "release_manifest"
    assert release_compare["right"]["kind"] == "artifact_catalog"

    promotion = json.loads((tmp_path / "demo/promotion_pack.json").read_text(encoding="utf-8"))
    assert promotion["ok"] is True
    assert {row["label"] for row in promotion["evidence"]} >= {"public-readiness", "landing-page", "visual-receipt", "command-matrix", "reviewer-scorecard"}

    adoption = json.loads((tmp_path / "demo/adoption_notes.json").read_text(encoding="utf-8"))
    assert adoption["audience"] == "agents reusing static outputs in a thesis ledger"
    assert "do not convert findings into advice" in adoption["ledger_boundary"]


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
    for command in [
        ("build-packet",),
        ("policy-profile",),
        ("policy-compare",),
        ("policy-gallery",),
        ("compare-history",),
        ("overlap-matrix",),
        ("review-ledger",),
        ("fixture-doctor",),
        ("static-dashboard",),
        ("case-gallery",),
        ("reviewer-scorecard",),
        ("maturity-report",),
        ("command-matrix",),
        ("release-checklist",),
        ("public-readiness",),
        ("docs-export",),
        ("landing-page",),
        ("visual-receipt",),
        ("promotion-pack",),
        ("asset-health",),
        ("final-handoff",),
        ("maintainer-note",),
        ("readme-snippet",),
        ("release-manifest",),
        ("artifact-catalog",),
        ("release-compare",),
        ("snapshot-ledger",),
        ("snapshot-compare",),
        ("review-queue",),
        ("adoption-notes",),
        ("final-qa",),
        ("bundle-export",),
    ]:
        first = run_cli(tmp_path, *command, "--root", ".")
        assert first.returncode == 0, first.stderr
    first_gallery = (tmp_path / "demo/case_gallery.json").read_bytes()
    first_policy = (tmp_path / "demo/policy_profile.json").read_bytes()
    first_policy_compare = (tmp_path / "demo/policy_compare.json").read_bytes()
    first_policy_gallery = (tmp_path / "demo/policy_gallery.json").read_bytes()
    first_scorecard = (tmp_path / "demo/reviewer_scorecard.json").read_bytes()
    first_release_compare = (tmp_path / "demo/release_compare.json").read_bytes()
    first_receipt = (tmp_path / "demo/visual_receipt.svg").read_bytes()
    first_catalog = (tmp_path / "demo/artifact_catalog.json").read_bytes()
    first_matrix = (tmp_path / "demo/command_matrix.json").read_bytes()
    first_checklist = (tmp_path / "demo/release_checklist.json").read_bytes()
    first_readiness = (tmp_path / "demo/public_readiness.json").read_bytes()
    first_promotion = (tmp_path / "demo/promotion_pack.json").read_bytes()
    first_adoption = (tmp_path / "demo/adoption_notes.json").read_bytes()
    first_docs = (tmp_path / "demo/cli_help.json").read_bytes()
    first_landing = (tmp_path / "demo/index.html").read_bytes()
    first_snippet = (tmp_path / "demo/readme_snippet.md").read_bytes()
    first_queue = (tmp_path / "demo/review_queue.json").read_bytes()
    first_snapshot = (tmp_path / "demo/snapshot_ledger.json").read_bytes()
    first_compare = (tmp_path / "demo/snapshot_compare.json").read_bytes()
    first_bundle = (tmp_path / "demo/bundle_export/manifest.json").read_bytes()
    first_handoff = (tmp_path / "demo/final_handoff.json").read_bytes()
    first_maintainer = (tmp_path / "demo/maintainer_note.json").read_bytes()
    first_final_qa = (tmp_path / "demo/final_qa.json").read_bytes()

    for command in [
        ("build-packet",),
        ("policy-profile",),
        ("policy-compare",),
        ("policy-gallery",),
        ("compare-history",),
        ("overlap-matrix",),
        ("review-ledger",),
        ("fixture-doctor",),
        ("static-dashboard",),
        ("case-gallery",),
        ("reviewer-scorecard",),
        ("maturity-report",),
        ("command-matrix",),
        ("release-checklist",),
        ("public-readiness",),
        ("docs-export",),
        ("landing-page",),
        ("visual-receipt",),
        ("promotion-pack",),
        ("asset-health",),
        ("final-handoff",),
        ("maintainer-note",),
        ("readme-snippet",),
        ("release-manifest",),
        ("artifact-catalog",),
        ("release-compare",),
        ("snapshot-ledger",),
        ("snapshot-compare",),
        ("review-queue",),
        ("adoption-notes",),
        ("final-qa",),
        ("bundle-export",),
    ]:
        second = run_cli(tmp_path, *command, "--root", ".")
        assert second.returncode == 0, second.stderr

    assert (tmp_path / "demo/case_gallery.json").read_bytes() == first_gallery
    assert (tmp_path / "demo/policy_profile.json").read_bytes() == first_policy
    assert (tmp_path / "demo/policy_compare.json").read_bytes() == first_policy_compare
    assert (tmp_path / "demo/policy_gallery.json").read_bytes() == first_policy_gallery
    assert (tmp_path / "demo/reviewer_scorecard.json").read_bytes() == first_scorecard
    assert (tmp_path / "demo/release_compare.json").read_bytes() == first_release_compare
    assert (tmp_path / "demo/visual_receipt.svg").read_bytes() == first_receipt
    assert (tmp_path / "demo/artifact_catalog.json").read_bytes() == first_catalog
    assert (tmp_path / "demo/command_matrix.json").read_bytes() == first_matrix
    assert (tmp_path / "demo/release_checklist.json").read_bytes() == first_checklist
    assert (tmp_path / "demo/final_handoff.json").read_bytes() == first_handoff
    assert (tmp_path / "demo/public_readiness.json").read_bytes() == first_readiness
    assert (tmp_path / "demo/promotion_pack.json").read_bytes() == first_promotion
    assert (tmp_path / "demo/adoption_notes.json").read_bytes() == first_adoption
    assert (tmp_path / "demo/cli_help.json").read_bytes() == first_docs
    assert (tmp_path / "demo/index.html").read_bytes() == first_landing
    assert (tmp_path / "demo/readme_snippet.md").read_bytes() == first_snippet
    assert (tmp_path / "demo/review_queue.json").read_bytes() == first_queue
    assert (tmp_path / "demo/snapshot_ledger.json").read_bytes() == first_snapshot
    assert (tmp_path / "demo/snapshot_compare.json").read_bytes() == first_compare
    assert (tmp_path / "demo/bundle_export/manifest.json").read_bytes() == first_bundle
    assert (tmp_path / "demo/maintainer_note.json").read_bytes() == first_maintainer
    assert (tmp_path / "demo/final_qa.json").read_bytes() == first_final_qa


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
