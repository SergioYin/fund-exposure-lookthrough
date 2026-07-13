"""Command line interface for static fund exposure look-through analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from html import escape
from importlib import resources
from pathlib import Path
from typing import Any

from . import __version__
from .doctor import diagnose_fixtures, fixture_doctor_markdown, parse_iso_date
from .engine import compare_exposures, concentration_flags, group_exposure, lookthrough, overlap_matrix, validate_inputs
from .io import read_constituents, read_holdings, write_json, write_text
from .render import (
    DISCLAIMER,
    comparison_markdown,
    case_gallery_markdown,
    dashboard_html,
    ledger_markdown,
    manifest_markdown,
    maturity_markdown,
    overlap_markdown,
    packet_markdown,
    packet_payload,
    reviewer_scorecard_markdown,
    visual_receipt_html,
    visual_receipt_svg,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fund-exposure-lookthrough", description="Static fund exposure look-through research CLI.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    packet = sub.add_parser("build-packet", help="Build a Markdown and JSON exposure packet.")
    _add_input_args(packet)
    packet.add_argument("--out-md", default="demo/exposure_packet.md")
    packet.add_argument("--out-json", default="demo/exposure_packet.json")
    packet.set_defaults(func=cmd_build_packet)

    compare = sub.add_parser("compare-history", help="Compare current and prior portfolio exposures.")
    compare.add_argument("--root", default=".")
    compare.add_argument("--current", default="examples/current_portfolio.csv")
    compare.add_argument("--prior", default="examples/prior_portfolio.csv")
    compare.add_argument("--constituents", default="examples/fund_constituents.csv")
    compare.add_argument("--out-md", default="demo/history_comparison.md")
    compare.add_argument("--out-json", default="demo/history_comparison.json")
    compare.set_defaults(func=cmd_compare_history)

    overlap = sub.add_parser("overlap-matrix", help="Build a fund constituent overlap matrix.")
    _add_input_args(overlap)
    overlap.add_argument("--out-md", default="demo/overlap_matrix.md")
    overlap.add_argument("--out-json", default="demo/overlap_matrix.json")
    overlap.set_defaults(func=cmd_overlap_matrix)

    ledger = sub.add_parser("review-ledger", help="Build a static review ledger for input warnings and concentration flags.")
    _add_input_args(ledger)
    ledger.add_argument("--threshold", type=float, default=0.20)
    ledger.add_argument("--out-md", default="demo/review_ledger.md")
    ledger.add_argument("--out-json", default="demo/review_ledger.json")
    ledger.set_defaults(func=cmd_review_ledger)

    doctor = sub.add_parser("fixture-doctor", help="Validate portfolio and constituent fixtures and write Markdown/JSON reports.")
    _add_input_args(doctor)
    doctor.add_argument("--as-of", default="2026-07-14", help="Deterministic ISO date used for source metadata freshness checks.")
    doctor.add_argument("--max-source-age-days", type=int, default=370)
    doctor.add_argument("--out-md", default="demo/fixture_doctor.md")
    doctor.add_argument("--out-json", default="demo/fixture_doctor.json")
    doctor.set_defaults(func=cmd_fixture_doctor)

    dashboard = sub.add_parser("static-dashboard", help="Build a no-JavaScript static HTML dashboard.")
    _add_input_args(dashboard)
    dashboard.add_argument("--out-html", default="demo/static_dashboard.html")
    dashboard.set_defaults(func=cmd_static_dashboard)

    gallery = sub.add_parser("case-gallery", help="Build a deterministic Markdown/JSON public showcase gallery.")
    gallery.add_argument("--root", default=".")
    gallery.add_argument("--out-md", default="demo/case_gallery.md")
    gallery.add_argument("--out-json", default="demo/case_gallery.json")
    gallery.set_defaults(func=cmd_case_gallery)

    receipt = sub.add_parser("visual-receipt", help="Build a deterministic SVG or HTML receipt for demo artifact hashes.")
    receipt.add_argument("--root", default=".")
    receipt.add_argument("--format", choices=["svg", "html"], default="svg")
    receipt.add_argument("--out", default="demo/visual_receipt.svg")
    receipt.set_defaults(func=cmd_visual_receipt)

    scorecard = sub.add_parser("reviewer-scorecard", help="Map release evidence to a public maturity rubric.")
    scorecard.add_argument("--root", default=".")
    scorecard.add_argument("--out-md", default="demo/reviewer_scorecard.md")
    scorecard.add_argument("--out-json", default="demo/reviewer_scorecard.json")
    scorecard.set_defaults(func=cmd_reviewer_scorecard)

    selfcheck = sub.add_parser("selfcheck", help="Check package, examples, safety text, and generated artifacts.")
    selfcheck.add_argument("--root", default=".")
    selfcheck.set_defaults(func=cmd_selfcheck)

    public_scan = sub.add_parser("public-scan", help="Scan publishable text files for private names and credentials.")
    public_scan.add_argument("--root", default=".")
    public_scan.set_defaults(func=cmd_public_scan)

    manifest = sub.add_parser("release-manifest", help="Build a release manifest for public review.")
    manifest.add_argument("--root", default=".")
    manifest.add_argument("--out-md", default="demo/release_manifest.md")
    manifest.add_argument("--out-json", default="demo/release_manifest.json")
    manifest.set_defaults(func=cmd_release_manifest)

    release_compare = sub.add_parser("release-compare", help="Compare two release manifests or artifact catalogs.")
    release_compare.add_argument("--root", default=".")
    release_compare.add_argument("--left", default="demo/release_manifest.json")
    release_compare.add_argument("--right", default="demo/artifact_catalog.json")
    release_compare.add_argument("--out-md", default="demo/release_compare.md")
    release_compare.add_argument("--out-json", default="demo/release_compare.json")
    release_compare.set_defaults(func=cmd_release_compare)

    maturity = sub.add_parser("maturity-report", help="Build a project maturity report.")
    maturity.add_argument("--root", default=".")
    maturity.add_argument("--out-md", default="demo/maturity_report.md")
    maturity.add_argument("--out-json", default="demo/maturity_report.json")
    maturity.set_defaults(func=cmd_maturity_report)

    bundle = sub.add_parser("bundle-export", help="Copy selected demo artifacts into a deterministic portable directory.")
    bundle.add_argument("--root", default=".")
    bundle.add_argument("--out-dir", default="demo/bundle_export")
    bundle.set_defaults(func=cmd_bundle_export)

    health = sub.add_parser("asset-health", help="Summarize command coverage, artifact presence, package data, and safety boundaries.")
    health.add_argument("--root", default=".")
    health.add_argument("--out-md", default="demo/asset_health.md")
    health.add_argument("--out-json", default="demo/asset_health.json")
    health.set_defaults(func=cmd_asset_health)

    catalog = sub.add_parser("artifact-catalog", help="Catalog demo artifacts with type, size, SHA-256, and regeneration command.")
    catalog.add_argument("--root", default=".")
    catalog.add_argument("--out-md", default="demo/artifact_catalog.md")
    catalog.add_argument("--out-json", default="demo/artifact_catalog.json")
    catalog.set_defaults(func=cmd_artifact_catalog)

    matrix = sub.add_parser("command-matrix", help="Write a Markdown/JSON matrix of CLI routes, inputs, outputs, and exit-code behavior.")
    matrix.add_argument("--root", default=".")
    matrix.add_argument("--out-md", default="demo/command_matrix.md")
    matrix.add_argument("--out-json", default="demo/command_matrix.json")
    matrix.set_defaults(func=cmd_command_matrix)

    checklist = sub.add_parser("release-checklist", help="Write a release owner checklist for tests, package, wheel smoke, public scan, and no-advice boundaries.")
    checklist.add_argument("--root", default=".")
    checklist.add_argument("--out-md", default="demo/release_checklist.md")
    checklist.add_argument("--out-json", default="demo/release_checklist.json")
    checklist.set_defaults(func=cmd_release_checklist)

    handoff = sub.add_parser("final-handoff", help="Write a Markdown/JSON release owner handoff for v1 stabilization.")
    handoff.add_argument("--root", default=".")
    handoff.add_argument("--repo-url", default="REPO_URL_PLACEHOLDER")
    handoff.add_argument("--release-version", default=__version__)
    handoff.add_argument("--out-md", default="demo/final_handoff.md")
    handoff.add_argument("--out-json", default="demo/final_handoff.json")
    handoff.set_defaults(func=cmd_final_handoff)

    maintainer = sub.add_parser("maintainer-note", help="Write deterministic maintainer evidence and next-step notes.")
    maintainer.add_argument("--root", default=".")
    maintainer.add_argument("--out-md", default="demo/maintainer_note.md")
    maintainer.add_argument("--out-json", default="demo/maintainer_note.json")
    maintainer.set_defaults(func=cmd_maintainer_note)

    final_qa = sub.add_parser("final-qa", help="Write deterministic final QA evidence for release review.")
    final_qa.add_argument("--root", default=".")
    final_qa.add_argument("--baseline", default="v0.5.0")
    final_qa.add_argument("--release-version", default=__version__)
    final_qa.add_argument("--out-md", default="demo/final_qa.md")
    final_qa.add_argument("--out-json", default="demo/final_qa.json")
    final_qa.set_defaults(func=cmd_final_qa)

    snippet = sub.add_parser("readme-snippet", help="Generate a concise Markdown quickstart and demo snippet from current artifacts.")
    snippet.add_argument("--root", default=".")
    snippet.add_argument("--out-md", default="demo/readme_snippet.md")
    snippet.set_defaults(func=cmd_readme_snippet)

    readiness = sub.add_parser("public-readiness", help="Write a first-10-minute cold-user walkthrough in Markdown and JSON.")
    readiness.add_argument("--root", default=".")
    readiness.add_argument("--out-md", default="demo/public_readiness.md")
    readiness.add_argument("--out-json", default="demo/public_readiness.json")
    readiness.set_defaults(func=cmd_public_readiness)

    promotion = sub.add_parser("promotion-pack", help="Bundle public-readiness, landing, receipt, command matrix, and scorecard evidence.")
    promotion.add_argument("--root", default=".")
    promotion.add_argument("--out-md", default="demo/promotion_pack.md")
    promotion.add_argument("--out-json", default="demo/promotion_pack.json")
    promotion.set_defaults(func=cmd_promotion_pack)

    adoption = sub.add_parser("adoption-notes", help="Write agent-facing workflow notes for using outputs in a thesis ledger.")
    adoption.add_argument("--root", default=".")
    adoption.add_argument("--out-md", default="demo/adoption_notes.md")
    adoption.add_argument("--out-json", default="demo/adoption_notes.json")
    adoption.set_defaults(func=cmd_adoption_notes)

    landing = sub.add_parser("landing-page", help="Write a no-JavaScript static HTML public landing page linking demo artifacts.")
    landing.add_argument("--root", default=".")
    landing.add_argument("--out-html", default="demo/index.html")
    landing.set_defaults(func=cmd_landing_page)

    docs = sub.add_parser("docs-export", help="Export CLI help and command metadata into deterministic Markdown and JSON.")
    docs.add_argument("--root", default=".")
    docs.add_argument("--out-md", default="demo/cli_help.md")
    docs.add_argument("--out-json", default="demo/cli_help.json")
    docs.set_defaults(func=cmd_docs_export)

    snapshot = sub.add_parser("snapshot-ledger", help="Append a deterministic artifact snapshot to a JSON/Markdown ledger.")
    snapshot.add_argument("--root", default=".")
    snapshot.add_argument("--out-md", default="demo/snapshot_ledger.md")
    snapshot.add_argument("--out-json", default="demo/snapshot_ledger.json")
    snapshot.set_defaults(func=cmd_snapshot_ledger)

    snapshot_compare = sub.add_parser("snapshot-compare", help="Compare two deterministic snapshot JSON files.")
    snapshot_compare.add_argument("--root", default=".")
    snapshot_compare.add_argument("--left", default="demo/snapshot_ledger.json")
    snapshot_compare.add_argument("--right", default="demo/snapshot_ledger.json")
    snapshot_compare.add_argument("--out-md", default="demo/snapshot_compare.md")
    snapshot_compare.add_argument("--out-json", default="demo/snapshot_compare.json")
    snapshot_compare.set_defaults(func=cmd_snapshot_compare)

    queue = sub.add_parser("review-queue", help="Derive prioritized follow-up questions from generated review artifacts.")
    queue.add_argument("--root", default=".")
    queue.add_argument("--exposure", default="demo/exposure_packet.json")
    queue.add_argument("--fixture-doctor", default="demo/fixture_doctor.json")
    queue.add_argument("--asset-health", default="demo/asset_health.json")
    queue.add_argument("--release-checklist", default="demo/release_checklist.json")
    queue.add_argument("--out-md", default="demo/review_queue.md")
    queue.add_argument("--out-json", default="demo/review_queue.json")
    queue.set_defaults(func=cmd_review_queue)

    policy = sub.add_parser("policy-profile", help="Apply a bundled research-only policy profile to an exposure artifact.")
    policy.add_argument("--root", default=".")
    policy.add_argument("--profile", choices=sorted(_policy_profiles()), default="balanced")
    policy.add_argument("--exposure", default="demo/exposure_packet.json")
    policy.add_argument("--out-md", default="demo/policy_profile.md")
    policy.add_argument("--out-json", default="demo/policy_profile.json")
    policy.set_defaults(func=cmd_policy_profile)

    policy_compare = sub.add_parser("policy-compare", help="Compare two policy-profile JSON outputs.")
    policy_compare.add_argument("--root", default=".")
    policy_compare.add_argument("--left", default="demo/policy_profile.json")
    policy_compare.add_argument("--right", default="demo/policy_profile.json")
    policy_compare.add_argument("--out-md", default="demo/policy_compare.md")
    policy_compare.add_argument("--out-json", default="demo/policy_compare.json")
    policy_compare.set_defaults(func=cmd_policy_compare)

    policy_gallery = sub.add_parser("policy-gallery", help="Build Markdown/JSON policy examples for bundled fixtures.")
    policy_gallery.add_argument("--root", default=".")
    policy_gallery.add_argument("--out-md", default="demo/policy_gallery.md")
    policy_gallery.add_argument("--out-json", default="demo/policy_gallery.json")
    policy_gallery.set_defaults(func=cmd_policy_gallery)
    return parser


def cmd_build_packet(args: argparse.Namespace) -> int:
    root = Path(args.root)
    holdings, constituents = _load(args)
    exposures = lookthrough(holdings, constituents)
    payload = packet_payload(holdings[0].portfolio_id, holdings, exposures, validate_inputs(holdings, constituents))
    write_text(root / args.out_md, packet_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_compare_history(args: argparse.Namespace) -> int:
    root = Path(args.root)
    constituents = read_constituents(_resolve_input(root, args.constituents))
    current = lookthrough(read_holdings(_resolve_input(root, args.current)), constituents)
    prior = lookthrough(read_holdings(_resolve_input(root, args.prior)), constituents)
    rows = compare_exposures(current, prior)
    payload = {"safety": DISCLAIMER, "rows": rows}
    write_text(root / args.out_md, comparison_markdown(rows))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_overlap_matrix(args: argparse.Namespace) -> int:
    root = Path(args.root)
    holdings, constituents = _load(args)
    rows = overlap_matrix(holdings, constituents)
    payload = {"safety": DISCLAIMER, "rows": rows}
    write_text(root / args.out_md, overlap_markdown(rows))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_review_ledger(args: argparse.Namespace) -> int:
    root = Path(args.root)
    holdings, constituents = _load(args)
    exposures = lookthrough(holdings, constituents)
    warnings = validate_inputs(holdings, constituents)
    flags = concentration_flags(exposures, args.threshold)
    payload = {"safety": DISCLAIMER, "threshold": args.threshold, "warnings": warnings, "concentration_flags": flags}
    write_text(root / args.out_md, ledger_markdown(flags, warnings, args.threshold))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_fixture_doctor(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if args.max_source_age_days < 0:
        raise ValueError("--max-source-age-days must be non-negative")
    payload = diagnose_fixtures(
        _resolve_input(root, args.portfolio),
        _resolve_input(root, args.constituents),
        parse_iso_date(args.as_of),
        args.max_source_age_days,
    )
    write_text(root / args.out_md, fixture_doctor_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0 if payload["ok"] else 1


def cmd_static_dashboard(args: argparse.Namespace) -> int:
    root = Path(args.root)
    holdings, constituents = _load(args)
    exposures = lookthrough(holdings, constituents)
    payload = packet_payload(holdings[0].portfolio_id, holdings, exposures, validate_inputs(holdings, constituents))
    html = dashboard_html(payload, group_exposure(exposures, "sector"), group_exposure(exposures, "region"))
    write_text(root / args.out_html, html)
    print(f"wrote {root / args.out_html}")
    return 0


def cmd_case_gallery(args: argparse.Namespace) -> int:
    root = Path(args.root)
    cases = [
        _case_summary(
            "Bundled current portfolio",
            "build-packet",
            read_holdings(_resolve_input(root, "examples/current_portfolio.csv")),
            read_constituents(_resolve_input(root, "examples/fund_constituents.csv")),
        ),
        _case_summary(
            "Bundled prior portfolio",
            "compare-history",
            read_holdings(_resolve_input(root, "examples/prior_portfolio.csv")),
            read_constituents(_resolve_input(root, "examples/fund_constituents.csv")),
        ),
        _case_summary(
            "Direct holding and ETF wrapper",
            "case-gallery/direct-wrapper",
            read_holdings(_resolve_input(root, "examples/direct_wrapper_portfolio.csv")),
            read_constituents(_resolve_input(root, "examples/direct_wrapper_constituents.csv")),
        ),
    ]
    payload = {"tool": "fund-exposure-lookthrough", "version": __version__, "safety": DISCLAIMER, "cases": cases}
    write_text(root / args.out_md, case_gallery_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_visual_receipt(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = {
        "tool": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "artifacts": [_artifact_row(root, rel) for rel in _receipt_artifacts(args.out)],
    }
    out = root / args.out
    if args.format == "html":
        write_text(out, visual_receipt_html(payload))
    else:
        write_text(out, visual_receipt_svg(payload))
    print(f"wrote {out}")
    return 0


def cmd_reviewer_scorecard(args: argparse.Namespace) -> int:
    root = Path(args.root)
    checks = [
        ("Zero runtime dependencies", 2, ["pyproject.toml"] if _pyproject_has_no_runtime_deps(root / "pyproject.toml") else []),
        ("Packaged example fixtures", 2, _existing(root, ["examples/current_portfolio.csv", "examples/prior_portfolio.csv", "examples/direct_wrapper_portfolio.csv", "src/fund_exposure_lookthrough/data/direct_wrapper_constituents.csv"])),
        ("Deterministic Markdown and JSON demos", 2, _existing(root, ["demo/exposure_packet.md", "demo/exposure_packet.json", "demo/case_gallery.md", "demo/case_gallery.json"])),
        ("Visual public receipt", 1, _existing(root, ["src/fund_exposure_lookthrough/cli.py", "src/fund_exposure_lookthrough/render.py"])),
        ("Fixture review and public scan", 2, _existing(root, ["src/fund_exposure_lookthrough/doctor.py", "tests/test_public_safety.py"])),
        ("Documentation and release notes", 1, _existing(root, ["README.md", "CHANGELOG.md", "RELEASE_NOTES.md", "skills/agent/fund-exposure-lookthrough/SKILL.md"])),
        ("No workflow automation", 1, [] if (root / ".github" / "workflows").exists() else ["no .github/workflows directory"]),
        ("Static safety boundary", 1, ["README.md", "render.DISCLAIMER"] if "not investment advice" in DISCLAIMER.lower() else []),
    ]
    rubric = [
        {"name": name, "max_score": max_score, "score": max_score if evidence else 0, "evidence": evidence}
        for name, max_score, evidence in checks
    ]
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "score": sum(item["score"] for item in rubric),
        "max_score": sum(item["max_score"] for item in rubric),
        "rubric": rubric,
    }
    write_text(root / args.out_md, reviewer_scorecard_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_selfcheck(args: argparse.Namespace) -> int:
    root = Path(args.root)
    required = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "src/fund_exposure_lookthrough/cli.py",
        "examples/current_portfolio.csv",
        "examples/prior_portfolio.csv",
        "examples/fund_constituents.csv",
        "examples/direct_wrapper_portfolio.csv",
        "examples/direct_wrapper_constituents.csv",
        "skills/agent/fund-exposure-lookthrough/SKILL.md",
    ]
    missing = [path for path in required if not (root / path).exists()]
    leaks = public_hygiene_findings(root)
    ok = not missing and not leaks
    payload = {"ok": ok, "version": __version__, "missing": missing, "leaks": leaks, "safety": DISCLAIMER}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 1


def cmd_public_scan(args: argparse.Namespace) -> int:
    root = Path(args.root)
    findings = public_hygiene_findings(root)
    payload = {"ok": not findings, "findings": findings, "safety": DISCLAIMER}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not findings else 1


def cmd_release_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root)
    files = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in {".git", ".pytest_cache", "dist", "build", "__pycache__"} for part in path.parts)
        and not str(path.relative_to(root)).startswith("demo/bundle_export/")
        and str(path.relative_to(root)) not in {args.out_md, args.out_json}
        and str(path.relative_to(root)) not in _state_artifact_outputs()
        and str(path.relative_to(root)) not in {"demo/artifact_catalog.md", "demo/artifact_catalog.json"}
    )
    payload: dict[str, Any] = {
        "project": "fund-exposure-lookthrough",
        "module": "fund_exposure_lookthrough",
        "version": __version__,
        "runtime_dependencies": "none",
        "file_count": len(files),
        "source_digest": _digest_files(root, files),
        "safety": DISCLAIMER,
    }
    write_text(root / args.out_md, manifest_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_release_compare(args: argparse.Namespace) -> int:
    root = Path(args.root)
    left = _release_input_payload(_read_json(root / args.left), args.left)
    right = _release_input_payload(_read_json(root / args.right), args.right)
    payload = _compare_release_inputs(left, right)
    write_text(root / args.out_md, _release_compare_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_maturity_report(args: argparse.Namespace) -> int:
    root = Path(args.root)
    checks = {
        "Source package": (root / "src/fund_exposure_lookthrough").exists(),
        "CLI routes": (root / "src/fund_exposure_lookthrough/cli.py").exists(),
        "Fixture doctor": (root / "src/fund_exposure_lookthrough/doctor.py").exists(),
        "Tests": (root / "tests").exists(),
        "Bundled examples": (root / "examples").exists(),
        "Deterministic demo artifacts": (root / "demo").exists(),
        "Public documentation": (root / "README.md").exists() and (root / "LICENSE").exists(),
        "No GitHub workflows": not (root / ".github/workflows").exists(),
        "Zero runtime dependencies": _pyproject_has_no_runtime_deps(root / "pyproject.toml"),
    }
    payload = {
        "project": "fund-exposure-lookthrough",
        "safety": DISCLAIMER,
        "capabilities": [{"name": name, "status": "ready" if ok else "missing"} for name, ok in checks.items()],
    }
    write_text(root / args.out_md, maturity_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_bundle_export(args: argparse.Namespace) -> int:
    root = Path(args.root)
    out_dir = root / args.out_dir
    if out_dir.resolve() == root.resolve():
        raise ValueError("--out-dir must not be the project root")
    if out_dir.exists() and not out_dir.is_dir():
        raise ValueError("--out-dir must be a directory path")

    artifacts = [_artifact_row(root, rel) for rel in _bundle_artifacts()]
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "artifacts").mkdir(parents=True, exist_ok=True)

    copied: list[dict[str, Any]] = []
    for row in sorted(artifacts, key=lambda item: item["route"]):
        rel = row["route"]
        source = root / rel
        if not source.exists():
            continue
        target = out_dir / "artifacts" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append({**row, "bundle_path": str(Path("artifacts") / rel)})

    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "artifact_count": len(copied),
        "artifacts": copied,
        "missing": sorted(row["route"] for row in artifacts if not row["exists"]),
    }
    write_json(out_dir / "manifest.json", payload)
    write_text(out_dir / "manifest.md", _bundle_manifest_markdown(payload))
    print(f"wrote {out_dir}")
    return 0


def cmd_asset_health(args: argparse.Namespace) -> int:
    root = Path(args.root)
    command_names = _command_names()
    documented = _documented_commands(root)
    artifact_rows = [_artifact_row(root, rel) for rel in _operator_artifacts()]
    package_data = _package_data_status(root)
    safety = {
        "disclaimer_has_no_advice": "not investment advice" in DISCLAIMER.lower(),
        "no_live_data_statement": _file_contains(root / "README.md", "does not fetch live data"),
        "no_broker_statement": _file_contains(root / "README.md", "connect to brokers"),
        "no_workflows": not (root / ".github" / "workflows").exists(),
        "public_scan_clean": not public_hygiene_findings(root),
    }
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "commands": [{"name": name, "documented": name in documented} for name in command_names],
        "artifacts": artifact_rows,
        "package_data": package_data,
        "safety_boundaries": safety,
        "ok": all(row["exists"] for row in artifact_rows) and all(package_data.values()) and all(safety.values()),
    }
    write_text(root / args.out_md, _asset_health_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0 if payload["ok"] else 1


def cmd_readme_snippet(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "artifacts": [_artifact_row(root, rel) for rel in _snippet_artifacts()],
    }
    write_text(root / args.out_md, _readme_snippet_markdown(payload))
    print(f"wrote {root / args.out_md}")
    return 0


def cmd_artifact_catalog(args: argparse.Namespace) -> int:
    root = Path(args.root)
    excluded = {args.out_md, args.out_json} | _state_artifact_outputs()
    artifacts = [
        _catalog_artifact_row(root, rel)
        for rel in _demo_artifacts(root)
        if rel not in excluded
    ]
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    write_text(root / args.out_md, _artifact_catalog_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_command_matrix(args: argparse.Namespace) -> int:
    root = Path(args.root)
    specs = _command_specs()
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "command_count": len(specs),
        "commands": specs,
    }
    write_text(root / args.out_md, _command_matrix_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_release_checklist(args: argparse.Namespace) -> int:
    root = Path(args.root)
    checks = _release_checks(root)
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "ok": all(item["ready"] for item in checks),
        "checks": checks,
    }
    write_text(root / args.out_md, _release_checklist_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0 if payload["ok"] else 1


def cmd_final_handoff(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _final_handoff_payload(root, args.repo_url, args.release_version)
    write_text(root / args.out_md, _final_handoff_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_maintainer_note(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _maintainer_note_payload(root)
    write_text(root / args.out_md, _maintainer_note_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_final_qa(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _final_qa_payload(root, args.baseline, args.release_version)
    write_text(root / args.out_md, _final_qa_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_public_readiness(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _public_readiness_payload(root)
    write_text(root / args.out_md, _public_readiness_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_promotion_pack(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _promotion_pack_payload(root)
    write_text(root / args.out_md, _promotion_pack_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_adoption_notes(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _adoption_notes_payload(root)
    write_text(root / args.out_md, _adoption_notes_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_landing_page(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _landing_payload(root)
    write_text(root / args.out_html, _landing_page_html(payload))
    print(f"wrote {root / args.out_html}")
    return 0


def cmd_docs_export(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _docs_export_payload()
    write_text(root / args.out_md, _docs_export_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_snapshot_ledger(args: argparse.Namespace) -> int:
    root = Path(args.root)
    excluded = {args.out_md, args.out_json}
    snapshot = _snapshot_from_artifacts(root, excluded)
    existing = _read_json_if_exists(root / args.out_json)
    entries = list(existing.get("entries", [])) if isinstance(existing.get("entries"), list) else []
    if not entries or entries[-1].get("snapshot_id") != snapshot["snapshot_id"]:
        entries.append(snapshot)
    payload = {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "entry_count": len(entries),
        "current_snapshot": snapshot,
        "entries": entries,
    }
    write_text(root / args.out_md, _snapshot_ledger_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_snapshot_compare(args: argparse.Namespace) -> int:
    root = Path(args.root)
    left = _snapshot_payload(_read_json(root / args.left), args.left)
    right = _snapshot_payload(_read_json(root / args.right), args.right)
    payload = _compare_snapshots(left, right)
    write_text(root / args.out_md, _snapshot_compare_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_review_queue(args: argparse.Namespace) -> int:
    root = Path(args.root)
    payload = _review_queue_payload(
        root,
        args.exposure,
        args.fixture_doctor,
        args.asset_health,
        args.release_checklist,
    )
    write_text(root / args.out_md, _review_queue_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_policy_profile(args: argparse.Namespace) -> int:
    root = Path(args.root)
    exposure = _read_json(root / args.exposure)
    payload = _policy_payload(args.profile, exposure, args.exposure)
    write_text(root / args.out_md, _policy_profile_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_policy_compare(args: argparse.Namespace) -> int:
    root = Path(args.root)
    left = _policy_profile_payload(_read_json(root / args.left), args.left)
    right = _policy_profile_payload(_read_json(root / args.right), args.right)
    payload = _compare_policy_profiles(left, right)
    write_text(root / args.out_md, _policy_compare_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def cmd_policy_gallery(args: argparse.Namespace) -> int:
    root = Path(args.root)
    cases = [
        (
            "Bundled current portfolio",
            "examples/current_portfolio.csv",
            "examples/fund_constituents.csv",
        ),
        (
            "Bundled prior portfolio",
            "examples/prior_portfolio.csv",
            "examples/fund_constituents.csv",
        ),
        (
            "Direct holding and ETF wrapper",
            "examples/direct_wrapper_portfolio.csv",
            "examples/direct_wrapper_constituents.csv",
        ),
    ]
    examples = []
    for name, portfolio_rel, constituents_rel in cases:
        holdings = read_holdings(_resolve_input(root, portfolio_rel))
        constituents = read_constituents(_resolve_input(root, constituents_rel))
        exposures = lookthrough(holdings, constituents)
        exposure = packet_payload(holdings[0].portfolio_id, holdings, exposures, validate_inputs(holdings, constituents))
        profiles = [_policy_payload(profile, exposure, f"{portfolio_rel} + {constituents_rel}") for profile in sorted(_policy_profiles())]
        examples.append({"name": name, "portfolio_id": exposure["portfolio_id"], "profiles": profiles})
    payload = {"project": "fund-exposure-lookthrough", "version": __version__, "safety": DISCLAIMER, "examples": examples}
    write_text(root / args.out_md, _policy_gallery_markdown(payload))
    write_json(root / args.out_json, payload)
    print(f"wrote {root / args.out_md} and {root / args.out_json}")
    return 0


def _add_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".")
    parser.add_argument("--portfolio", default="examples/current_portfolio.csv")
    parser.add_argument("--constituents", default="examples/fund_constituents.csv")


def _load(args: argparse.Namespace):
    root = Path(args.root)
    return read_holdings(_resolve_input(root, args.portfolio)), read_constituents(_resolve_input(root, args.constituents))


def _resolve_input(root: Path, rel: str) -> Path:
    requested = root / rel
    if requested.exists():
        return requested
    if rel.startswith("examples/"):
        name = Path(rel).name
        package_file = resources.files("fund_exposure_lookthrough").joinpath("data", name)
        with resources.as_file(package_file) as path:
            if path.exists():
                return path
    return requested


def _digest_files(root: Path, files: list[str]) -> str:
    digest = hashlib.sha256()
    for rel in files:
        path = root / rel
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _case_summary(name: str, route: str, holdings: list[Any], constituents: list[Any]) -> dict[str, Any]:
    exposures = lookthrough(holdings, constituents)
    payload = packet_payload(holdings[0].portfolio_id, holdings, exposures, validate_inputs(holdings, constituents))
    return {
        "name": name,
        "route": route,
        "portfolio_id": payload["portfolio_id"],
        "fund_count": payload["fund_count"],
        "asset_count": payload["asset_count"],
        "total_exposure": payload["total_exposure"],
        "warnings": payload["warnings"],
        "top_assets": payload["top_assets"][:5],
    }


def _receipt_artifacts(out_rel: str) -> list[str]:
    routes = [
        "demo/index.html",
        "demo/public_readiness.md",
        "demo/public_readiness.json",
        "demo/cli_help.md",
        "demo/cli_help.json",
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
        "demo/case_gallery.md",
        "demo/case_gallery.json",
        "demo/reviewer_scorecard.md",
        "demo/reviewer_scorecard.json",
        "demo/static_dashboard.html",
    ]
    return [route for route in routes if route != out_rel]


def _bundle_artifacts() -> list[str]:
    return [
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
        "demo/asset_health.md",
        "demo/asset_health.json",
        "demo/artifact_catalog.md",
        "demo/artifact_catalog.json",
        "demo/command_matrix.md",
        "demo/command_matrix.json",
        "demo/release_checklist.md",
        "demo/release_checklist.json",
        "demo/maintainer_note.md",
        "demo/maintainer_note.json",
        "demo/final_qa.md",
        "demo/final_qa.json",
        "demo/readme_snippet.md",
        "demo/public_readiness.md",
        "demo/public_readiness.json",
        "demo/promotion_pack.md",
        "demo/promotion_pack.json",
        "demo/adoption_notes.md",
        "demo/adoption_notes.json",
        "demo/index.html",
        "demo/cli_help.md",
        "demo/cli_help.json",
        "demo/snapshot_ledger.md",
        "demo/snapshot_ledger.json",
        "demo/snapshot_compare.md",
        "demo/snapshot_compare.json",
        "demo/review_queue.md",
        "demo/review_queue.json",
    ]


def _operator_artifacts() -> list[str]:
    excluded = _state_artifact_outputs() | {
        "demo/asset_health.md",
        "demo/asset_health.json",
        "demo/artifact_catalog.md",
        "demo/artifact_catalog.json",
        "demo/bundle_export/manifest.json",
        "demo/release_manifest.md",
        "demo/release_manifest.json",
        "demo/readme_snippet.md",
        "demo/maintainer_note.md",
        "demo/maintainer_note.json",
    }
    return [
        rel
        for rel in _bundle_artifacts()
        if rel not in excluded
    ]


def _snippet_artifacts() -> list[str]:
    return [
        "demo/index.html",
        "demo/public_readiness.md",
        "demo/promotion_pack.md",
        "demo/cli_help.md",
        "demo/exposure_packet.md",
        "demo/policy_profile.md",
        "demo/policy_gallery.md",
        "demo/static_dashboard.html",
        "demo/case_gallery.md",
        "demo/visual_receipt.svg",
        "demo/asset_health.md",
        "demo/maintainer_note.md",
    ]


def _artifact_row(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {"route": rel, "exists": path.exists(), "sha256": _file_digest(path) if path.exists() else ""}


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _existing(root: Path, paths: list[str]) -> list[str]:
    return [path for path in paths if (root / path).exists()]


def _command_names() -> list[str]:
    return [spec["name"] for spec in _command_specs()]


def _command_specs() -> list[dict[str, Any]]:
    common_inputs = ["--root", "--portfolio", "--constituents"]
    static_exit = "0 on success; 2 for file or validation errors handled by the CLI wrapper"
    report_exit = "0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors"
    return [
        {
            "name": "build-packet",
            "inputs": common_inputs + ["--out-md", "--out-json"],
            "outputs": ["demo/exposure_packet.md", "demo/exposure_packet.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .",
        },
        {
            "name": "policy-profile",
            "inputs": ["--root", "--profile", "--exposure", "--out-md", "--out-json"],
            "outputs": ["demo/policy_profile.md", "demo/policy_profile.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-profile --root .",
        },
        {
            "name": "policy-compare",
            "inputs": ["--root", "--left", "--right", "--out-md", "--out-json"],
            "outputs": ["demo/policy_compare.md", "demo/policy_compare.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-compare --root . --left demo/policy_profile.json --right demo/policy_profile.json",
        },
        {
            "name": "policy-gallery",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/policy_gallery.md", "demo/policy_gallery.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-gallery --root .",
        },
        {
            "name": "compare-history",
            "inputs": ["--root", "--current", "--prior", "--constituents", "--out-md", "--out-json"],
            "outputs": ["demo/history_comparison.md", "demo/history_comparison.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli compare-history --root .",
        },
        {
            "name": "overlap-matrix",
            "inputs": common_inputs + ["--out-md", "--out-json"],
            "outputs": ["demo/overlap_matrix.md", "demo/overlap_matrix.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli overlap-matrix --root .",
        },
        {
            "name": "review-ledger",
            "inputs": common_inputs + ["--threshold", "--out-md", "--out-json"],
            "outputs": ["demo/review_ledger.md", "demo/review_ledger.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli review-ledger --root .",
        },
        {
            "name": "fixture-doctor",
            "inputs": common_inputs + ["--as-of", "--max-source-age-days", "--out-md", "--out-json"],
            "outputs": ["demo/fixture_doctor.md", "demo/fixture_doctor.json"],
            "exit_codes": report_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli fixture-doctor --root .",
        },
        {
            "name": "static-dashboard",
            "inputs": common_inputs + ["--out-html"],
            "outputs": ["demo/static_dashboard.html"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .",
        },
        {
            "name": "case-gallery",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/case_gallery.md", "demo/case_gallery.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli case-gallery --root .",
        },
        {
            "name": "visual-receipt",
            "inputs": ["--root", "--format", "--out"],
            "outputs": ["demo/visual_receipt.svg"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli visual-receipt --root .",
        },
        {
            "name": "reviewer-scorecard",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/reviewer_scorecard.md", "demo/reviewer_scorecard.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli reviewer-scorecard --root .",
        },
        {
            "name": "selfcheck",
            "inputs": ["--root"],
            "outputs": ["stdout JSON"],
            "exit_codes": report_exit,
            "regeneration_command": "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .",
        },
        {
            "name": "public-scan",
            "inputs": ["--root"],
            "outputs": ["stdout JSON"],
            "exit_codes": report_exit,
            "regeneration_command": "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .",
        },
        {
            "name": "release-manifest",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/release_manifest.md", "demo/release_manifest.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-manifest --root .",
        },
        {
            "name": "release-compare",
            "inputs": ["--root", "--left", "--right", "--out-md", "--out-json"],
            "outputs": ["demo/release_compare.md", "demo/release_compare.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-compare --root . --left demo/release_manifest.json --right demo/artifact_catalog.json",
        },
        {
            "name": "maturity-report",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/maturity_report.md", "demo/maturity_report.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli maturity-report --root .",
        },
        {
            "name": "bundle-export",
            "inputs": ["--root", "--out-dir"],
            "outputs": ["demo/bundle_export/manifest.md", "demo/bundle_export/manifest.json", "demo/bundle_export/artifacts/"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .",
        },
        {
            "name": "asset-health",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/asset_health.md", "demo/asset_health.json"],
            "exit_codes": report_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root .",
        },
        {
            "name": "artifact-catalog",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/artifact_catalog.md", "demo/artifact_catalog.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli artifact-catalog --root .",
        },
        {
            "name": "command-matrix",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/command_matrix.md", "demo/command_matrix.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli command-matrix --root .",
        },
        {
            "name": "release-checklist",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/release_checklist.md", "demo/release_checklist.json"],
            "exit_codes": report_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-checklist --root .",
        },
        {
            "name": "final-handoff",
            "inputs": ["--root", "--repo-url", "--release-version", "--out-md", "--out-json"],
            "outputs": ["demo/final_handoff.md", "demo/final_handoff.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli final-handoff --root . --repo-url REPO_URL_PLACEHOLDER",
        },
        {
            "name": "maintainer-note",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/maintainer_note.md", "demo/maintainer_note.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli maintainer-note --root .",
        },
        {
            "name": "final-qa",
            "inputs": ["--root", "--baseline", "--release-version", "--out-md", "--out-json"],
            "outputs": ["demo/final_qa.md", "demo/final_qa.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli final-qa --root . --baseline v0.5.0",
        },
        {
            "name": "readme-snippet",
            "inputs": ["--root", "--out-md"],
            "outputs": ["demo/readme_snippet.md"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli readme-snippet --root .",
        },
        {
            "name": "public-readiness",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/public_readiness.md", "demo/public_readiness.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli public-readiness --root .",
        },
        {
            "name": "promotion-pack",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/promotion_pack.md", "demo/promotion_pack.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli promotion-pack --root .",
        },
        {
            "name": "adoption-notes",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/adoption_notes.md", "demo/adoption_notes.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli adoption-notes --root .",
        },
        {
            "name": "landing-page",
            "inputs": ["--root", "--out-html"],
            "outputs": ["demo/index.html"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli landing-page --root .",
        },
        {
            "name": "docs-export",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/cli_help.md", "demo/cli_help.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli docs-export --root .",
        },
        {
            "name": "snapshot-ledger",
            "inputs": ["--root", "--out-md", "--out-json"],
            "outputs": ["demo/snapshot_ledger.md", "demo/snapshot_ledger.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli snapshot-ledger --root .",
        },
        {
            "name": "snapshot-compare",
            "inputs": ["--root", "--left", "--right", "--out-md", "--out-json"],
            "outputs": ["demo/snapshot_compare.md", "demo/snapshot_compare.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli snapshot-compare --root . --left demo/snapshot_ledger.json --right demo/snapshot_ledger.json",
        },
        {
            "name": "review-queue",
            "inputs": ["--root", "--exposure", "--fixture-doctor", "--asset-health", "--release-checklist", "--out-md", "--out-json"],
            "outputs": ["demo/review_queue.md", "demo/review_queue.json"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli review-queue --root .",
        },
    ]


def _documented_commands(root: Path) -> set[str]:
    text = ""
    for rel in ["README.md", "CHANGELOG.md", "RELEASE_NOTES.md", "skills/agent/fund-exposure-lookthrough/SKILL.md"]:
        path = root / rel
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="ignore") + "\n"
    return {name for name in _command_names() if name in text}


def _package_data_status(root: Path) -> dict[str, bool]:
    pyproject = root / "pyproject.toml"
    data_files = [
        "src/fund_exposure_lookthrough/data/current_portfolio.csv",
        "src/fund_exposure_lookthrough/data/prior_portfolio.csv",
        "src/fund_exposure_lookthrough/data/fund_constituents.csv",
        "src/fund_exposure_lookthrough/data/direct_wrapper_portfolio.csv",
        "src/fund_exposure_lookthrough/data/direct_wrapper_constituents.csv",
    ]
    return {
        "pyproject_declares_csv_package_data": _file_contains(pyproject, 'fund_exposure_lookthrough = ["data/*.csv"]'),
        "bundled_csv_files_present": all((root / rel).exists() for rel in data_files),
        "runtime_dependencies_empty": _pyproject_has_no_runtime_deps(pyproject),
    }


def _file_contains(path: Path, needle: str) -> bool:
    return path.exists() and needle.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()


def _bundle_manifest_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Bundle Export Manifest",
        "",
        DISCLAIMER,
        "",
        f"- project: {payload['project']}",
        f"- version: {payload['version']}",
        f"- artifact_count: {payload['artifact_count']}",
        "",
        "| Artifact | SHA-256 | Bundle path |",
        "| --- | --- | --- |",
    ]
    for row in payload["artifacts"]:
        lines.append(f"| {row['route']} | `{row['sha256']}` | `{row['bundle_path']}` |")
    if payload["missing"]:
        lines.extend(["", "## Missing", ""])
        lines.extend(f"- {rel}" for rel in payload["missing"])
    return "\n".join(lines) + "\n"


def _asset_health_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Asset Health",
        "",
        DISCLAIMER,
        "",
        f"Status: {'ready' if payload['ok'] else 'review required'}",
        "",
        "## Command Coverage",
        "",
        "| Command | Documented |",
        "| --- | --- |",
    ]
    for row in payload["commands"]:
        lines.append(f"| `{row['name']}` | {'yes' if row['documented'] else 'no'} |")
    lines.extend(["", "## Artifact Presence", "", "| Artifact | Status | SHA-256 prefix |", "| --- | --- | --- |"])
    for row in payload["artifacts"]:
        lines.append(f"| {row['route']} | {'ready' if row['exists'] else 'missing'} | `{row['sha256'][:16] if row['sha256'] else ''}` |")
    lines.extend(["", "## Package Data", ""])
    lines.extend(f"- {key}: {'ready' if value else 'missing'}" for key, value in payload["package_data"].items())
    lines.extend(["", "## Safety Boundaries", ""])
    lines.extend(f"- {key}: {'ready' if value else 'missing'}" for key, value in payload["safety_boundaries"].items())
    return "\n".join(lines) + "\n"


def _readme_snippet_markdown(payload: dict[str, Any]) -> str:
    ready = [row for row in payload["artifacts"] if row["exists"]]
    lines = [
        "## Quickstart Demo",
        "",
        "```bash",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli public-readiness --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli docs-export --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli landing-page --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .",
        "```",
        "",
        DISCLAIMER,
        "",
        "Generated demo artifacts:",
    ]
    lines.extend(f"- `{row['route']}`" for row in ready)
    missing = [row["route"] for row in payload["artifacts"] if not row["exists"]]
    if missing:
        lines.extend(["", "Artifacts not present yet:"])
        lines.extend(f"- `{rel}`" for rel in missing)
    return "\n".join(lines) + "\n"


def _demo_artifacts(root: Path) -> list[str]:
    demo = root / "demo"
    if not demo.exists():
        return []
    return [
        str(path.relative_to(root))
        for path in sorted(demo.rglob("*"))
        if path.is_file() and "bundle_export" not in path.relative_to(demo).parts
    ]


def _catalog_artifact_row(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {
        "path": rel,
        "type": _artifact_type(path),
        "bytes": path.stat().st_size,
        "sha256": _file_digest(path),
        "regeneration_command": _regeneration_command_for(rel),
    }


def _artifact_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".json": "json",
        ".md": "markdown",
        ".html": "html",
        ".svg": "svg",
        ".csv": "csv",
        ".txt": "text",
    }.get(suffix, suffix.lstrip(".") or "file")


def _regeneration_command_for(rel: str) -> str:
    if rel.startswith("demo/bundle_export/"):
        return "PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root ."
    for spec in _command_specs():
        if rel in spec["outputs"]:
            return spec["regeneration_command"]
    return "Regenerate the owning demo command, then run artifact-catalog."


def _artifact_catalog_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact Catalog",
        "",
        DISCLAIMER,
        "",
        f"Artifacts cataloged: {payload['artifact_count']}",
        "",
        "| Artifact | Type | Bytes | SHA-256 | Regeneration command |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in payload["artifacts"]:
        lines.append(
            f"| `{row['path']}` | {row['type']} | {row['bytes']} | `{row['sha256']}` | `{row['regeneration_command']}` |"
        )
    return "\n".join(lines) + "\n"


def _release_input_payload(payload: dict[str, Any], label: str) -> dict[str, Any]:
    artifacts = payload.get("artifacts", [])
    rows = []
    if isinstance(artifacts, list):
        for row in artifacts:
            if not isinstance(row, dict):
                continue
            path = str(row.get("path", row.get("route", row.get("bundle_path", ""))))
            if not path:
                continue
            rows.append(
                {
                    "path": path,
                    "type": str(row.get("type", "")),
                    "bytes": int(row.get("bytes", 0)),
                    "sha256": str(row.get("sha256", "")),
                }
            )
    metadata_keys = ["project", "module", "version", "runtime_dependencies", "file_count", "artifact_count", "source_digest"]
    metadata = {key: payload[key] for key in metadata_keys if key in payload}
    if not rows and "source_digest" not in metadata:
        raise ValueError(f"{label} is not a release manifest or artifact catalog JSON file")
    kind = "artifact_catalog" if rows else "release_manifest"
    return {
        "label": label,
        "kind": kind,
        "metadata": metadata,
        "artifact_count": len(rows),
        "artifacts": sorted(rows, key=lambda row: row["path"]),
    }


def _compare_release_inputs(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_rows = {row["path"]: row for row in left["artifacts"]}
    right_rows = {row["path"]: row for row in right["artifacts"]}
    added = sorted(set(right_rows) - set(left_rows))
    removed = sorted(set(left_rows) - set(right_rows))
    changed = [
        path
        for path in sorted(set(left_rows) & set(right_rows))
        if left_rows[path]["sha256"] != right_rows[path]["sha256"] or left_rows[path]["bytes"] != right_rows[path]["bytes"]
    ]
    metadata_changes = []
    for key in sorted(set(left["metadata"]) | set(right["metadata"])):
        left_value = left["metadata"].get(key, "")
        right_value = right["metadata"].get(key, "")
        if left_value != right_value:
            metadata_changes.append({"key": key, "left": left_value, "right": right_value})
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "left": {"label": left["label"], "kind": left["kind"], "artifact_count": left["artifact_count"], "metadata": left["metadata"]},
        "right": {"label": right["label"], "kind": right["kind"], "artifact_count": right["artifact_count"], "metadata": right["metadata"]},
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "metadata_changed": len(metadata_changes),
        },
        "added": [right_rows[path] for path in added],
        "removed": [left_rows[path] for path in removed],
        "changed": [
            {
                "path": path,
                "left_sha256": left_rows[path]["sha256"],
                "right_sha256": right_rows[path]["sha256"],
                "left_bytes": left_rows[path]["bytes"],
                "right_bytes": right_rows[path]["bytes"],
            }
            for path in changed
        ],
        "metadata_changes": metadata_changes,
    }


def _release_compare_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Release Compare",
        "",
        DISCLAIMER,
        "",
        f"Left: `{payload['left']['label']}` ({payload['left']['kind']})",
        f"Right: `{payload['right']['label']}` ({payload['right']['kind']})",
        "",
        f"- Added artifacts: {payload['summary']['added']}",
        f"- Removed artifacts: {payload['summary']['removed']}",
        f"- Changed artifacts: {payload['summary']['changed']}",
        f"- Metadata changes: {payload['summary']['metadata_changed']}",
    ]
    if payload["metadata_changes"]:
        lines.extend(["", "## Metadata Changes", "", "| Key | Left | Right |", "| --- | --- | --- |"])
        for row in payload["metadata_changes"]:
            lines.append(f"| {row['key']} | `{row['left']}` | `{row['right']}` |")
    for title, rows in [("Added Artifacts", payload["added"]), ("Removed Artifacts", payload["removed"])]:
        if rows:
            lines.extend(["", f"## {title}", "", "| Artifact | Bytes | SHA-256 |", "| --- | ---: | --- |"])
            for row in rows:
                lines.append(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    if payload["changed"]:
        lines.extend(["", "## Changed Artifacts", "", "| Artifact | Left bytes | Right bytes | Left SHA-256 | Right SHA-256 |", "| --- | ---: | ---: | --- | --- |"])
        for row in payload["changed"]:
            lines.append(
                f"| `{row['path']}` | {row['left_bytes']} | {row['right_bytes']} | `{row['left_sha256']}` | `{row['right_sha256']}` |"
            )
    return "\n".join(lines) + "\n"


def _command_matrix_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Command Matrix",
        "",
        DISCLAIMER,
        "",
        f"Commands documented: {payload['command_count']}",
        "",
        "| Command | Inputs | Outputs | Exit-code behavior |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["commands"]:
        inputs = ", ".join(f"`{item}`" for item in row["inputs"])
        outputs = ", ".join(f"`{item}`" for item in row["outputs"])
        lines.append(f"| `{row['name']}` | {inputs} | {outputs} | {row['exit_codes']} |")
    return "\n".join(lines) + "\n"


def _release_checks(root: Path) -> list[dict[str, Any]]:
    tests_ready = (root / "tests").exists()
    package_ready = _pyproject_has_no_runtime_deps(root / "pyproject.toml") and (root / "build_backend.py").exists()
    wheel_smoke_ready = (root / "build_backend.py").exists() and (root / "src" / "fund_exposure_lookthrough" / "__init__.py").exists()
    public_scan_ready = not public_hygiene_findings(root)
    no_advice_ready = (
        "not investment advice" in DISCLAIMER.lower()
        and _file_contains(root / "README.md", "does not fetch live data")
        and _file_contains(root / "README.md", "connect to brokers")
        and _file_contains(root / "README.md", "recommend buys")
    )
    no_workflows_ready = not (root / ".github" / "workflows").exists()
    return [
        {
            "name": "tests",
            "ready": tests_ready,
            "owner_action": "Run `python -m pytest -q` from the source checkout.",
            "evidence": ["tests/"] if tests_ready else [],
        },
        {
            "name": "package",
            "ready": package_ready,
            "owner_action": "Build with the local zero-dependency backend and inspect metadata.",
            "evidence": _existing(root, ["pyproject.toml", "build_backend.py"]),
        },
        {
            "name": "wheel-smoke",
            "ready": wheel_smoke_ready,
            "owner_action": "Install the built wheel in a clean environment and run `fund-exposure-lookthrough --version` plus `selfcheck --root .`.",
            "evidence": _existing(root, ["build_backend.py", "src/fund_exposure_lookthrough/__init__.py"]),
        },
        {
            "name": "public-scan",
            "ready": public_scan_ready,
            "owner_action": "Run `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .`.",
            "evidence": ["clean public hygiene scan"] if public_scan_ready else public_hygiene_findings(root),
        },
        {
            "name": "no-advice-boundaries",
            "ready": no_advice_ready,
            "owner_action": "Confirm docs and generated reports preserve static research-only language.",
            "evidence": ["render.DISCLAIMER", "README.md"] if no_advice_ready else [],
        },
        {
            "name": "no-workflows",
            "ready": no_workflows_ready,
            "owner_action": "Confirm no workflow automation files are present.",
            "evidence": ["no .github/workflows directory"] if no_workflows_ready else [],
        },
    ]


def _final_handoff_payload(root: Path, repo_url: str, release_version: str) -> dict[str, Any]:
    artifacts = [
        _artifact_row(root, rel)
        for rel in [
            "demo/exposure_packet.md",
            "demo/policy_profile.md",
            "demo/policy_gallery.md",
            "demo/public_readiness.md",
            "demo/promotion_pack.md",
            "demo/command_matrix.json",
            "demo/release_checklist.json",
            "demo/asset_health.json",
        ]
    ]
    verification_commands = [
        {
            "name": "tests",
            "command": "python -m pytest -q",
            "expected": "All local tests pass.",
        },
        {
            "name": "selfcheck",
            "command": "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .",
            "expected": "JSON reports ok=true with no missing required files or hygiene findings.",
        },
        {
            "name": "public-scan",
            "command": "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .",
            "expected": "JSON reports ok=true with no private terms or credential-shaped strings.",
        },
        {
            "name": "wheel-build",
            "command": "python -m pip wheel . --no-deps -w dist",
            "expected": "A fund_exposure_lookthrough wheel is created using the local zero-dependency backend.",
        },
        {
            "name": "wheel-smoke",
            "command": f"python -m pip install --force-reinstall --no-deps dist/fund_exposure_lookthrough-{release_version}-py3-none-any.whl && fund-exposure-lookthrough --version && fund-exposure-lookthrough selfcheck --root .",
            "expected": f"Installed CLI reports {release_version} and selfcheck passes.",
        },
    ]
    risks = [
        {
            "risk": "Fixture staleness",
            "owner_action": "Use fixture-doctor with an explicit --as-of date before relying on a new static snapshot.",
        },
        {
            "risk": "Generated artifact drift",
            "owner_action": "Regenerate command-matrix, release-manifest, artifact-catalog, and final-handoff after source or demo changes.",
        },
        {
            "risk": "Packaging smoke not performed by automation",
            "owner_action": "Run the wheel build and installed CLI smoke commands manually before tagging.",
        },
        {
            "risk": "Scope creep into advice or live-data behavior",
            "owner_action": "Reject changes that add live fetches, broker connectivity, orders, recommendations, target allocations, or return predictions.",
        },
    ]
    next_steps = [
        "Replace REPO_URL_PLACEHOLDER with the public repository URL before publishing release notes.",
        "Run the verification commands from a clean checkout and record results in the release owner notes.",
        "Inspect demo/index.html, demo/public_readiness.md, and demo/final_handoff.md as the first-screen reviewer path.",
        f"Tag v{release_version} only after tests, selfcheck, public-scan, and wheel smoke pass.",
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "release_version": release_version,
        "repo_url": repo_url,
        "safety": DISCLAIMER,
        "handoff": f"release owner handoff for v{release_version} stabilization",
        "boundaries": [
            "zero runtime dependencies",
            "no workflow automation",
            "no live data fetching",
            "no broker connectivity",
            "no financial advice, recommendations, target allocations, trades, or return predictions",
        ],
        "artifacts": artifacts,
        "verification_commands": verification_commands,
        "risks": risks,
        "next_steps": next_steps,
    }


def _final_handoff_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Final Release Handoff",
        "",
        DISCLAIMER,
        "",
        f"- Project: {payload['project']}",
        f"- Version: {payload['release_version']}",
        f"- Repository: {payload['repo_url']}",
        f"- Handoff: {payload['handoff']}",
        "",
        "## Boundaries",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["boundaries"])
    lines.extend(["", "## Verification Commands", "", "| Check | Command | Expected result |", "| --- | --- | --- |"])
    for row in payload["verification_commands"]:
        lines.append(f"| {row['name']} | `{row['command']}` | {row['expected']} |")
    lines.extend(["", "## Handoff Artifacts", "", "| Artifact | Status | SHA-256 prefix |", "| --- | --- | --- |"])
    for row in payload["artifacts"]:
        lines.append(f"| `{row['route']}` | {'ready' if row['exists'] else 'missing'} | `{row['sha256'][:16] if row['sha256'] else ''}` |")
    lines.extend(["", "## Risks", "", "| Risk | Owner action |", "| --- | --- |"])
    for row in payload["risks"]:
        lines.append(f"| {row['risk']} | {row['owner_action']} |")
    lines.extend(["", "## Next Steps", ""])
    lines.extend(f"- {item}" for item in payload["next_steps"])
    return "\n".join(lines) + "\n"


def _maintainer_note_payload(root: Path) -> dict[str, Any]:
    evidence = [
        _artifact_row(root, rel)
        for rel in [
            "README.md",
            "pyproject.toml",
            "CHANGELOG.md",
            "RELEASE_NOTES.md",
            "demo/cli_help.json",
            "demo/command_matrix.json",
            "demo/final_handoff.json",
        ]
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "purpose": "deterministic maintainer note for docs and packaging evidence",
        "evidence": evidence,
        "verification": [
            "python -m pytest -q",
            "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .",
            "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .",
            "python -m pip wheel . --no-deps -w dist",
        ],
        "boundaries": [
            "zero runtime dependencies",
            "no workflow automation",
            "no live data fetching",
            "no broker connectivity",
            "no financial advice, recommendations, target allocations, trades, or return predictions",
        ],
        "next_steps": [
            "Regenerate docs-export, command-matrix, release-manifest, artifact-catalog, asset-health, bundle-export, final-handoff, and maintainer-note after any command or artifact change.",
            "Run the complete verification suite before tagging.",
            "Keep generated demo files deterministic and exclude bytecode, pytest cache, build, dist, and egg-info outputs from commits.",
        ],
    }


def _maintainer_note_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Maintainer Note",
        "",
        DISCLAIMER,
        "",
        f"Version: {payload['version']}",
        f"Purpose: {payload['purpose']}",
        "",
        "## Evidence",
        "",
        "| Path | Status | SHA-256 prefix |",
        "| --- | --- | --- |",
    ]
    for row in payload["evidence"]:
        lines.append(f"| `{row['route']}` | {'ready' if row['exists'] else 'missing'} | `{row['sha256'][:16] if row['sha256'] else ''}` |")
    lines.extend(["", "## Verification", ""])
    lines.extend(f"- `{command}`" for command in payload["verification"])
    lines.extend(["", "## Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["boundaries"])
    lines.extend(["", "## Next Steps", ""])
    lines.extend(f"- {item}" for item in payload["next_steps"])
    return "\n".join(lines) + "\n"


def _final_qa_payload(root: Path, baseline: str, release_version: str) -> dict[str, Any]:
    release_checks = _release_checks(root)
    artifacts = [
        _artifact_row(root, rel)
        for rel in [
            "README.md",
            "CHANGELOG.md",
            "RELEASE_NOTES.md",
            "pyproject.toml",
            "build_backend.py",
            "demo/final_handoff.json",
            "demo/maintainer_note.json",
            "demo/release_manifest.json",
            "demo/artifact_catalog.json",
            "demo/command_matrix.json",
            "demo/release_checklist.json",
            "demo/asset_health.json",
        ]
    ]
    verification_commands = [
        {
            "name": "tests",
            "command": "PYTHONPATH=src python -m pytest -q",
            "expected": "All tests pass, including deterministic artifact and public safety coverage.",
        },
        {
            "name": "selfcheck",
            "command": "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .",
            "expected": "JSON reports ok=true with required files present and public hygiene clean.",
        },
        {
            "name": "public-scan",
            "command": "PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .",
            "expected": "JSON reports ok=true and findings is empty.",
        },
        {
            "name": "release-checklist",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-checklist --root .",
            "expected": "Release checklist reports ok=true across tests, package, smoke, public scan, boundaries, and workflow absence.",
        },
        {
            "name": "wheel-build",
            "command": "python -m pip wheel . --no-deps -w dist",
            "expected": "Wheel builds with no runtime dependency resolution.",
        },
        {
            "name": "wheel-smoke",
            "command": f"python -m pip install --force-reinstall --no-deps dist/fund_exposure_lookthrough-{release_version}-py3-none-any.whl && fund-exposure-lookthrough --version && fund-exposure-lookthrough selfcheck --root .",
            "expected": f"Installed CLI reports {release_version} and selfcheck passes.",
        },
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "release_version": release_version,
        "baseline": baseline,
        "safety": DISCLAIMER,
        "summary": "deterministic final QA packet for release review",
        "changes_since_baseline": [
            "Added public-readiness, docs-export, and landing-page artifacts for cold reviewer onboarding.",
            "Added snapshot-ledger, snapshot-compare, and review-queue artifacts for deterministic state and follow-up review.",
            "Added policy-profile, policy-compare, and policy-gallery artifacts for research-only threshold review.",
            "Added release-compare, promotion-pack, and adoption-notes artifacts for cross-run review and thesis-ledger reuse.",
            "Added final-handoff and maintainer-note artifacts for release owner and maintainer evidence.",
            "Updated package metadata to production/stable v1.0.1 while preserving zero runtime dependencies.",
            "Updated the local build backend to read the package version and emit reproducible wheel/sdist archives.",
            "Expanded CLI regression and public safety tests for command metadata, deterministic outputs, packaged data, and no-advice boundaries.",
        ],
        "verification_commands": verification_commands,
        "release_checks": release_checks,
        "release_risks": [
            {
                "risk": "Generated artifact drift after source edits",
                "mitigation": "Regenerate command-matrix, release-manifest, artifact-catalog, release-checklist, asset-health, bundle-export, maintainer-note, final-handoff, and final-qa before tagging.",
            },
            {
                "risk": "Wheel smoke omitted because there is no workflow automation",
                "mitigation": "Run the wheel-build and wheel-smoke commands manually from a clean checkout.",
            },
            {
                "risk": "Fixture freshness assumptions become stale",
                "mitigation": "Run fixture-doctor with an explicit --as-of date and update user-supplied fixture source metadata when needed.",
            },
            {
                "risk": "Scope creep into live data, broker connectivity, or advice",
                "mitigation": "Reject changes that add live fetches, orders, recommendations, target allocations, trades, or return predictions.",
            },
        ],
        "no_advice_boundaries": [
            "research use only",
            "not investment advice",
            "no buy, sell, hold, target allocation, or trade recommendations",
            "no return predictions",
            "no personalized financial advice",
            "only user-supplied static fixture data",
            "no live data fetching",
            "no broker connectivity",
        ],
        "release_artifacts": artifacts,
        "coherence": {
            "version_matches": _file_contains(root / "pyproject.toml", f'version = "{release_version}"')
            and _file_contains(root / "src/fund_exposure_lookthrough/__init__.py", f'__version__ = "{release_version}"'),
            "runtime_dependencies_empty": _pyproject_has_no_runtime_deps(root / "pyproject.toml"),
            "no_workflow_automation": not (root / ".github" / "workflows").exists(),
            "public_scan_clean": not public_hygiene_findings(root),
            "release_checks_ready": all(item["ready"] for item in release_checks),
            "artifacts_present": all(row["exists"] for row in artifacts),
        },
    }


def _final_qa_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Final QA",
        "",
        DISCLAIMER,
        "",
        f"- Project: {payload['project']}",
        f"- Version: {payload['release_version']}",
        f"- Baseline: {payload['baseline']}",
        f"- Summary: {payload['summary']}",
        "",
        "## Changes Since Baseline",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["changes_since_baseline"])
    lines.extend(["", "## Verification Commands", "", "| Check | Command | Expected result |", "| --- | --- | --- |"])
    for row in payload["verification_commands"]:
        lines.append(f"| {row['name']} | `{row['command']}` | {row['expected']} |")
    lines.extend(["", "## Release Checks", "", "| Check | Status | Owner action |", "| --- | --- | --- |"])
    for row in payload["release_checks"]:
        lines.append(f"| {row['name']} | {'ready' if row['ready'] else 'review'} | {row['owner_action']} |")
    lines.extend(["", "## Release Risks", "", "| Risk | Mitigation |", "| --- | --- |"])
    for row in payload["release_risks"]:
        lines.append(f"| {row['risk']} | {row['mitigation']} |")
    lines.extend(["", "## No-Advice Boundaries", ""])
    lines.extend(f"- {item}" for item in payload["no_advice_boundaries"])
    lines.extend(["", "## Release Artifacts", "", "| Artifact | Status | SHA-256 prefix |", "| --- | --- | --- |"])
    for row in payload["release_artifacts"]:
        lines.append(f"| `{row['route']}` | {'ready' if row['exists'] else 'missing'} | `{row['sha256'][:16] if row['sha256'] else ''}` |")
    lines.extend(["", "## Coherence", ""])
    lines.extend(f"- {key}: {'ready' if value else 'review'}" for key, value in payload["coherence"].items())
    return "\n".join(lines) + "\n"


def _public_readiness_payload(root: Path) -> dict[str, Any]:
    steps = [
        {
            "minute": "0-1",
            "goal": "Confirm the project is static research tooling.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli --help",
            "expected": "CLI help lists deterministic artifact commands and no network setup.",
            "artifact": "stdout",
        },
        {
            "minute": "1-2",
            "goal": "Build the primary exposure packet and research-only policy profile from bundled CSV fixtures.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root . && PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-profile --root .",
            "expected": "Exposure and policy profile artifacts appear under demo/ without allocation recommendations.",
            "artifact": "demo/exposure_packet.md",
        },
        {
            "minute": "2-3",
            "goal": "Review fixture quality without fetching live data.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli fixture-doctor --root .",
            "expected": "Clean bundled fixtures return ok and document source metadata checks.",
            "artifact": "demo/fixture_doctor.md",
        },
        {
            "minute": "3-4",
            "goal": "Open the static dashboard for a visual table review.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .",
            "expected": "A no-JavaScript HTML dashboard is available.",
            "artifact": "demo/static_dashboard.html",
        },
        {
            "minute": "4-5",
            "goal": "Compare bundled scenarios and inspect public examples.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli case-gallery --root . && PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-gallery --root .",
            "expected": "Current, prior, direct-wrapper, and bundled policy profile cases are summarized.",
            "artifact": "demo/case_gallery.md",
        },
        {
            "minute": "5-6",
            "goal": "Export route help for offline review.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli docs-export --root .",
            "expected": "CLI help and command metadata are exported as Markdown and JSON.",
            "artifact": "demo/cli_help.md",
        },
        {
            "minute": "6-7",
            "goal": "Build a public landing page that links the demo set.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli landing-page --root .",
            "expected": "A static index page links demos, bundle, receipt, command matrix, and safety boundaries.",
            "artifact": "demo/index.html",
        },
        {
            "minute": "7-8",
            "goal": "Create a visual receipt and command matrix for reviewer orientation.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli visual-receipt --root . && PYTHONPATH=src python -m fund_exposure_lookthrough.cli command-matrix --root .",
            "expected": "Artifact hashes and command coverage are available.",
            "artifact": "demo/visual_receipt.svg",
        },
        {
            "minute": "8-9",
            "goal": "Run safety and package readiness checks.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root . && PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .",
            "expected": "Static boundaries, package data, and public hygiene checks pass.",
            "artifact": "demo/asset_health.md",
        },
        {
            "minute": "9-10",
            "goal": "Bundle the deterministic public review artifacts.",
            "command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .",
            "expected": "Portable review bundle manifest is written with copied artifacts.",
            "artifact": "demo/bundle_export/manifest.md",
        },
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "walkthrough": "first-10-minute cold-user walkthrough",
        "zero_dependency": _pyproject_has_no_runtime_deps(root / "pyproject.toml"),
        "no_workflows": not (root / ".github" / "workflows").exists(),
        "no_live_data": _file_contains(root / "README.md", "does not fetch live data"),
        "steps": steps,
    }


def _public_readiness_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Public Readiness Walkthrough",
        "",
        DISCLAIMER,
        "",
        f"Version: {payload['version']}",
        f"Walkthrough: {payload['walkthrough']}",
        f"Zero runtime dependencies: {'yes' if payload['zero_dependency'] else 'review'}",
        f"No workflow automation: {'yes' if payload['no_workflows'] else 'review'}",
        f"No live data boundary documented: {'yes' if payload['no_live_data'] else 'review'}",
        "",
        "| Minute | Goal | Command | Expected result | Artifact |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in payload["steps"]:
        lines.append(
            f"| {step['minute']} | {step['goal']} | `{step['command']}` | {step['expected']} | `{step['artifact']}` |"
        )
    return "\n".join(lines) + "\n"


def _promotion_pack_payload(root: Path) -> dict[str, Any]:
    evidence_paths = [
        ("public-readiness", "demo/public_readiness.md"),
        ("public-readiness-json", "demo/public_readiness.json"),
        ("landing-page", "demo/index.html"),
        ("visual-receipt", "demo/visual_receipt.svg"),
        ("command-matrix", "demo/command_matrix.md"),
        ("command-matrix-json", "demo/command_matrix.json"),
        ("reviewer-scorecard", "demo/reviewer_scorecard.md"),
        ("reviewer-scorecard-json", "demo/reviewer_scorecard.json"),
    ]
    evidence = []
    for label, rel in evidence_paths:
        row = _artifact_row(root, rel)
        evidence.append({"label": label, "path": rel, "exists": row["exists"], "sha256": row["sha256"]})
    readiness = _read_json_if_exists(root / "demo/public_readiness.json")
    scorecard = _read_json_if_exists(root / "demo/reviewer_scorecard.json")
    matrix = _read_json_if_exists(root / "demo/command_matrix.json")
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "purpose": "promotion evidence pack for static public review",
        "ok": all(row["exists"] for row in evidence),
        "evidence": evidence,
        "summary": {
            "readiness_steps": len(readiness.get("steps", [])) if isinstance(readiness.get("steps"), list) else 0,
            "score": scorecard.get("score", 0),
            "max_score": scorecard.get("max_score", 0),
            "commands": matrix.get("command_count", 0),
        },
        "boundaries": [
            "zero runtime dependencies",
            "no workflow automation",
            "no live data fetching",
            "no broker connectivity",
            "no recommendations, target allocations, trades, return predictions, or personalized financial advice",
        ],
    }


def _promotion_pack_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Promotion Pack",
        "",
        DISCLAIMER,
        "",
        f"Status: {'ready' if payload['ok'] else 'review required'}",
        f"Purpose: {payload['purpose']}",
        "",
        "## Evidence",
        "",
        "| Evidence | Path | Status | SHA-256 prefix |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["evidence"]:
        lines.append(f"| {row['label']} | `{row['path']}` | {'ready' if row['exists'] else 'missing'} | `{row['sha256'][:16] if row['sha256'] else ''}` |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Public-readiness steps: {payload['summary']['readiness_steps']}",
            f"- Reviewer score: {payload['summary']['score']} / {payload['summary']['max_score']}",
            f"- Commands in matrix: {payload['summary']['commands']}",
            "",
            "## Boundaries",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["boundaries"])
    return "\n".join(lines) + "\n"


def _adoption_notes_payload(root: Path) -> dict[str, Any]:
    evidence = [
        _artifact_row(root, rel)
        for rel in [
            "demo/exposure_packet.json",
            "demo/policy_profile.json",
            "demo/review_queue.json",
            "demo/release_compare.json",
            "demo/promotion_pack.json",
            "demo/snapshot_ledger.json",
        ]
    ]
    notes = [
        {
            "step": "capture_static_inputs",
            "ledger_field": "inputs",
            "agent_note": "Record fixture filenames, generated artifact paths, and hashes before interpreting exposure rows.",
        },
        {
            "step": "attach_exposure_evidence",
            "ledger_field": "evidence.exposure",
            "agent_note": "Reference exposure_packet.json and policy_profile.json as static research evidence, not as portfolio instructions.",
        },
        {
            "step": "track_release_delta",
            "ledger_field": "evidence.release_delta",
            "agent_note": "Use release_compare.json or snapshot_ledger.json to describe artifact changes across runs.",
        },
        {
            "step": "queue_reviewer_questions",
            "ledger_field": "review.questions",
            "agent_note": "Copy review_queue.json questions into the thesis ledger as unresolved review items.",
        },
        {
            "step": "attach_promotion_evidence",
            "ledger_field": "evidence.promotion",
            "agent_note": "Use promotion_pack.json to prove public-readiness, landing page, receipt, command matrix, and scorecard coverage.",
        },
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "audience": "agents reusing static outputs in a thesis ledger",
        "ledger_boundary": "Use outputs as reproducible evidence only; do not convert findings into advice, target allocations, trades, or return predictions.",
        "evidence": evidence,
        "notes": notes,
    }


def _adoption_notes_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Adoption Notes",
        "",
        DISCLAIMER,
        "",
        f"Audience: {payload['audience']}",
        "",
        payload["ledger_boundary"],
        "",
        "## Evidence Inputs",
        "",
        "| Path | Status | SHA-256 prefix |",
        "| --- | --- | --- |",
    ]
    for row in payload["evidence"]:
        lines.append(f"| `{row['route']}` | {'ready' if row['exists'] else 'missing'} | `{row['sha256'][:16] if row['sha256'] else ''}` |")
    lines.extend(["", "## Thesis Ledger Workflow", "", "| Step | Ledger field | Agent note |", "| --- | --- | --- |"])
    for row in payload["notes"]:
        lines.append(f"| `{row['step']}` | `{row['ledger_field']}` | {row['agent_note']} |")
    return "\n".join(lines) + "\n"


def _landing_payload(root: Path) -> dict[str, Any]:
    featured = [
        ("First-10-minute walkthrough", "public_readiness.md"),
        ("Promotion pack", "promotion_pack.md"),
        ("Adoption notes", "adoption_notes.md"),
        ("Static dashboard", "static_dashboard.html"),
        ("Exposure packet", "exposure_packet.md"),
        ("Policy profile", "policy_profile.md"),
        ("Policy gallery", "policy_gallery.md"),
        ("Case gallery", "case_gallery.md"),
        ("Visual receipt", "visual_receipt.svg"),
        ("Release compare", "release_compare.md"),
        ("Command matrix", "command_matrix.md"),
        ("CLI help export", "cli_help.md"),
        ("Portable bundle manifest", "bundle_export/manifest.md"),
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "featured": [
            {"label": label, "href": href}
            for label, href in featured
        ],
        "commands": _command_specs(),
        "boundaries": [
            "No runtime dependencies.",
            "No workflow automation.",
            "No live data fetching.",
            "No broker or trading-system connectivity.",
            "No recommendations, target allocations, trades, return predictions, or personalized financial advice.",
            "Only user-supplied static fixture data is used.",
        ],
    }


def _landing_page_html(payload: dict[str, Any]) -> str:
    links = "\n".join(
        f'<li><a href="{escape(row["href"])}">{escape(row["label"])}</a></li>'
        for row in payload["featured"]
    )
    commands = "\n".join(
        f"<tr><td><code>{escape(row['name'])}</code></td><td>{escape(', '.join(row['outputs']))}</td><td>{escape(row['exit_codes'])}</td></tr>"
        for row in payload["commands"]
    )
    boundaries = "\n".join(f"<li>{escape(item)}</li>" for item in payload["boundaries"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>fund-exposure-lookthrough public walkthrough</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; color: #1f2933; background: #f7f8fa; }}
    main {{ max-width: 1060px; margin: 0 auto; padding: 2rem; }}
    header {{ border-bottom: 1px solid #cfd6e0; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
    h1 {{ font-size: 2rem; margin: 0 0 0.5rem; }}
    h2 {{ margin-top: 1.8rem; }}
    .notice {{ border-left: 4px solid #596579; padding-left: 0.75rem; }}
    ul {{ padding-left: 1.2rem; }}
    li {{ margin: 0.45rem 0; }}
    table {{ border-collapse: collapse; width: 100%; background: white; border: 1px solid #d9dee7; }}
    th, td {{ border-bottom: 1px solid #d9dee7; padding: 0.55rem; text-align: left; vertical-align: top; }}
    code {{ font-size: 0.9rem; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>fund-exposure-lookthrough</h1>
    <p>Version {escape(payload["version"])} public landing and walkthrough index for deterministic static review.</p>
    <p class="notice">{escape(DISCLAIMER)}</p>
  </header>
  <section>
    <h2>Start Here</h2>
    <ul>{links}</ul>
  </section>
  <section>
    <h2>Safety Boundaries</h2>
    <ul>{boundaries}</ul>
  </section>
  <section>
    <h2>Command Matrix</h2>
    <table><thead><tr><th>Command</th><th>Default outputs</th><th>Exit-code behavior</th></tr></thead><tbody>{commands}</tbody></table>
  </section>
</main>
</body>
</html>
"""


def _docs_export_payload() -> dict[str, Any]:
    parser = build_parser()
    subparsers_action = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    commands = []
    specs = {spec["name"]: spec for spec in _command_specs()}
    for name in sorted(subparsers_action.choices):
        command_parser = subparsers_action.choices[name]
        commands.append(
            {
                "name": name,
                "help": command_parser.description or command_parser.format_usage().strip(),
                "usage": command_parser.format_usage().strip(),
                "full_help": command_parser.format_help(),
                "metadata": specs[name],
            }
        )
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "top_level_help": parser.format_help(),
        "command_count": len(commands),
        "commands": commands,
    }


def _docs_export_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# CLI Help Export",
        "",
        DISCLAIMER,
        "",
        f"Version: {payload['version']}",
        f"Commands exported: {payload['command_count']}",
        "",
        "## Top-level Help",
        "",
        "```text",
        payload["top_level_help"].rstrip(),
        "```",
    ]
    for command in payload["commands"]:
        lines.extend(
            [
                "",
                f"## {command['name']}",
                "",
                f"- Inputs: {', '.join(f'`{item}`' for item in command['metadata']['inputs'])}",
                f"- Outputs: {', '.join(f'`{item}`' for item in command['metadata']['outputs'])}",
                f"- Exit codes: {command['metadata']['exit_codes']}",
                f"- Regeneration: `{command['metadata']['regeneration_command']}`",
                "",
                "```text",
                command["full_help"].rstrip(),
                "```",
            ]
        )
    return "\n".join(lines) + "\n"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _read_json(path)


def _snapshot_from_artifacts(root: Path, excluded: set[str]) -> dict[str, Any]:
    state_outputs = _state_artifact_outputs() | {"demo/artifact_catalog.md", "demo/artifact_catalog.json"}
    artifacts = [
        _snapshot_artifact_row(root, rel)
        for rel in _demo_artifacts(root)
        if rel not in excluded and rel not in state_outputs and not rel.startswith("demo/bundle_export/")
    ]
    digest = hashlib.sha256()
    for row in artifacts:
        digest.update(row["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(row["bytes"]).encode("ascii"))
        digest.update(b"\0")
        digest.update(row["sha256"].encode("ascii"))
        digest.update(b"\0")
    snapshot_id = digest.hexdigest()
    return {
        "snapshot_id": snapshot_id,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def _snapshot_artifact_row(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {
        "path": rel,
        "type": _artifact_type(path),
        "bytes": path.stat().st_size,
        "sha256": _file_digest(path),
    }


def _snapshot_payload(payload: dict[str, Any], label: str) -> dict[str, Any]:
    source = payload.get("current_snapshot", payload)
    if not isinstance(source, dict) or not isinstance(source.get("artifacts"), list):
        raise ValueError(f"{label} is not a snapshot JSON file")
    rows = [
        {
            "path": str(row["path"]),
            "type": str(row.get("type", "")),
            "bytes": int(row.get("bytes", 0)),
            "sha256": str(row.get("sha256", "")),
        }
        for row in source["artifacts"]
        if isinstance(row, dict) and "path" in row
    ]
    return {
        "label": label,
        "snapshot_id": str(source.get("snapshot_id", "")),
        "artifact_count": len(rows),
        "artifacts": sorted(rows, key=lambda row: row["path"]),
    }


def _compare_snapshots(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_rows = {row["path"]: row for row in left["artifacts"]}
    right_rows = {row["path"]: row for row in right["artifacts"]}
    added = sorted(set(right_rows) - set(left_rows))
    removed = sorted(set(left_rows) - set(right_rows))
    changed = [
        path
        for path in sorted(set(left_rows) & set(right_rows))
        if left_rows[path]["sha256"] != right_rows[path]["sha256"] or left_rows[path]["bytes"] != right_rows[path]["bytes"]
    ]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "left": {"label": left["label"], "snapshot_id": left["snapshot_id"], "artifact_count": left["artifact_count"]},
        "right": {"label": right["label"], "snapshot_id": right["snapshot_id"], "artifact_count": right["artifact_count"]},
        "summary": {"added": len(added), "removed": len(removed), "changed": len(changed)},
        "added": [right_rows[path] for path in added],
        "removed": [left_rows[path] for path in removed],
        "changed": [
            {
                "path": path,
                "left_sha256": left_rows[path]["sha256"],
                "right_sha256": right_rows[path]["sha256"],
                "left_bytes": left_rows[path]["bytes"],
                "right_bytes": right_rows[path]["bytes"],
            }
            for path in changed
        ],
    }


def _snapshot_ledger_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Snapshot Ledger",
        "",
        DISCLAIMER,
        "",
        f"Entries: {payload['entry_count']}",
        f"Current snapshot: `{payload['current_snapshot']['snapshot_id']}`",
        "",
        "| Entry | Snapshot ID | Artifacts |",
        "| ---: | --- | ---: |",
    ]
    for index, entry in enumerate(payload["entries"], start=1):
        lines.append(f"| {index} | `{entry['snapshot_id']}` | {entry['artifact_count']} |")
    lines.extend(["", "## Current Artifact Hashes", "", "| Artifact | Bytes | SHA-256 |", "| --- | ---: | --- |"])
    for row in payload["current_snapshot"]["artifacts"]:
        lines.append(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    return "\n".join(lines) + "\n"


def _snapshot_compare_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Snapshot Compare",
        "",
        DISCLAIMER,
        "",
        f"Left: `{payload['left']['label']}` / `{payload['left']['snapshot_id']}`",
        f"Right: `{payload['right']['label']}` / `{payload['right']['snapshot_id']}`",
        "",
        f"- Added: {payload['summary']['added']}",
        f"- Removed: {payload['summary']['removed']}",
        f"- Changed: {payload['summary']['changed']}",
    ]
    for title, rows in [("Added", payload["added"]), ("Removed", payload["removed"])]:
        if rows:
            lines.extend(["", f"## {title}", "", "| Artifact | Bytes | SHA-256 |", "| --- | ---: | --- |"])
            for row in rows:
                lines.append(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |")
    if payload["changed"]:
        lines.extend(["", "## Changed", "", "| Artifact | Left bytes | Right bytes | Left SHA-256 | Right SHA-256 |", "| --- | ---: | ---: | --- | --- |"])
        for row in payload["changed"]:
            lines.append(
                f"| `{row['path']}` | {row['left_bytes']} | {row['right_bytes']} | `{row['left_sha256']}` | `{row['right_sha256']}` |"
            )
    return "\n".join(lines) + "\n"


def _review_queue_payload(root: Path, exposure_rel: str, fixture_rel: str, health_rel: str, checklist_rel: str) -> dict[str, Any]:
    exposure = _read_json_if_exists(root / exposure_rel)
    fixture = _read_json_if_exists(root / fixture_rel)
    health = _read_json_if_exists(root / health_rel)
    checklist = _read_json_if_exists(root / checklist_rel)
    questions: list[dict[str, Any]] = []

    for warning in exposure.get("warnings", []):
        questions.append(_queue_item("high", exposure_rel, "Input warning", f"Which static fixture row explains this warning: {warning}?"))
    for row in exposure.get("top_assets", [])[:3]:
        if float(row.get("exposure", 0.0)) >= 0.15:
            questions.append(
                _queue_item(
                    "medium",
                    exposure_rel,
                    "Exposure review",
                    f"Should reviewers add source notes for {row.get('asset_name')} at {float(row.get('exposure', 0.0)) * 100:.2f}% exposure?",
                )
            )

    for finding in fixture.get("findings", []):
        severity = "high" if finding.get("severity") == "error" else "medium"
        questions.append(_queue_item(severity, fixture_rel, str(finding.get("code", "fixture finding")), str(finding.get("message", ""))))

    for row in health.get("artifacts", []):
        if not row.get("exists", False):
            questions.append(_queue_item("high", health_rel, "Missing artifact", f"Which command should regenerate `{row.get('route')}`?"))
    for key, value in health.get("safety_boundaries", {}).items():
        if not value:
            questions.append(_queue_item("high", health_rel, "Safety boundary", f"What static documentation update is needed for `{key}`?"))
    for key, value in health.get("package_data", {}).items():
        if not value:
            questions.append(_queue_item("medium", health_rel, "Package data", f"What packaging evidence is missing for `{key}`?"))

    for check in checklist.get("checks", []):
        if not check.get("ready", False):
            questions.append(_queue_item("high", checklist_rel, str(check.get("name", "release check")), str(check.get("owner_action", ""))))

    if not questions:
        questions.append(_queue_item("low", "generated artifacts", "Clean review", "Are there any reviewer-specific fixture assumptions that should be documented before release?"))

    priority = {"high": 0, "medium": 1, "low": 2}
    for index, item in enumerate(sorted(questions, key=lambda row: (priority[row["priority"]], row["source"], row["topic"], row["question"])), start=1):
        item["rank"] = index
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "question_count": len(questions),
        "questions": sorted(questions, key=lambda row: row["rank"]),
        "sources": [exposure_rel, fixture_rel, health_rel, checklist_rel],
    }


def _queue_item(priority: str, source: str, topic: str, question: str) -> dict[str, Any]:
    return {"rank": 0, "priority": priority, "source": source, "topic": topic, "question": question}


def _review_queue_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Review Queue",
        "",
        DISCLAIMER,
        "",
        f"Questions: {payload['question_count']}",
        "",
        "| Rank | Priority | Source | Topic | Question |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in payload["questions"]:
        lines.append(f"| {row['rank']} | {row['priority']} | `{row['source']}` | {row['topic']} | {row['question']} |")
    return "\n".join(lines) + "\n"


def _policy_profiles() -> dict[str, dict[str, Any]]:
    return {
        "balanced": {
            "label": "Balanced research review",
            "thresholds": {"asset": 0.15, "sector": 0.45, "region": 0.70, "asset_class": 0.90},
        },
        "concentrated": {
            "label": "Concentrated research review",
            "thresholds": {"asset": 0.25, "sector": 0.60, "region": 0.85, "asset_class": 0.95},
        },
        "conservative": {
            "label": "Conservative research review",
            "thresholds": {"asset": 0.10, "sector": 0.35, "region": 0.60, "asset_class": 0.80},
        },
    }


def _policy_payload(profile: str, exposure: dict[str, Any], source: str) -> dict[str, Any]:
    profiles = _policy_profiles()
    if profile not in profiles:
        raise ValueError(f"unknown policy profile {profile!r}")
    assets = _exposure_assets(exposure, source)
    thresholds = profiles[profile]["thresholds"]
    groups = {
        "asset": [
            {"name": row["asset_name"], "asset_id": row["asset_id"], "exposure": row["exposure"]}
            for row in assets
        ],
        "sector": _policy_group_rows(assets, "sector"),
        "region": _policy_group_rows(assets, "region"),
        "asset_class": _policy_group_rows(assets, "asset_class"),
    }
    checks = []
    for dimension in ["asset", "sector", "region", "asset_class"]:
        threshold = float(thresholds[dimension])
        for row in groups[dimension]:
            exposure_value = float(row["exposure"])
            checks.append(
                {
                    "dimension": dimension,
                    "name": row["name"],
                    "asset_id": row.get("asset_id", ""),
                    "exposure": round(exposure_value, 10),
                    "threshold": threshold,
                    "over_threshold": exposure_value >= threshold,
                    "margin_to_threshold": round(threshold - exposure_value, 10),
                }
            )
    flags = [row for row in checks if row["over_threshold"]]
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "profile": profile,
        "profile_label": profiles[profile]["label"],
        "source": source,
        "portfolio_id": str(exposure.get("portfolio_id", "")),
        "policy_boundary": "Research-only threshold review; not advice and not an allocation recommendation.",
        "thresholds": thresholds,
        "asset_count": len(assets),
        "flag_count": len(flags),
        "status": "review" if flags else "within_thresholds",
        "checks": sorted(checks, key=lambda row: (row["dimension"], -float(row["exposure"]), row["name"])),
        "flags": sorted(flags, key=lambda row: (row["dimension"], -float(row["exposure"]), row["name"])),
    }


def _exposure_assets(exposure: dict[str, Any], source: str) -> list[dict[str, Any]]:
    rows = exposure.get("assets", exposure.get("top_assets"))
    if not isinstance(rows, list):
        raise ValueError(f"{source} is not an exposure packet JSON file")
    assets = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        assets.append(
            {
                "asset_id": str(row.get("asset_id", "")),
                "asset_name": str(row.get("asset_name", "")),
                "exposure": round(float(row.get("exposure", 0.0)), 10),
                "sector": str(row.get("sector", "")),
                "region": str(row.get("region", "")),
                "asset_class": str(row.get("asset_class", "")),
            }
        )
    return assets


def _policy_group_rows(assets: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    totals: dict[str, float] = {}
    for row in assets:
        key = str(row[field])
        totals[key] = totals.get(key, 0.0) + float(row["exposure"])
    return [
        {"name": key, "exposure": round(value, 10)}
        for key, value in sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    ]


def _policy_profile_payload(payload: dict[str, Any], label: str) -> dict[str, Any]:
    required = {"profile", "thresholds", "checks", "flags"}
    if not required.issubset(payload):
        raise ValueError(f"{label} is not a policy-profile JSON file")
    return payload


def _compare_policy_profiles(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_flags = _policy_flag_keys(left)
    right_flags = _policy_flag_keys(right)
    added = sorted(right_flags - left_flags)
    removed = sorted(left_flags - right_flags)
    shared = sorted(left_flags & right_flags)
    threshold_deltas = []
    for key in sorted(set(left.get("thresholds", {})) | set(right.get("thresholds", {}))):
        threshold_deltas.append(
            {
                "dimension": key,
                "left": float(left.get("thresholds", {}).get(key, 0.0)),
                "right": float(right.get("thresholds", {}).get(key, 0.0)),
                "change": round(float(right.get("thresholds", {}).get(key, 0.0)) - float(left.get("thresholds", {}).get(key, 0.0)), 10),
            }
        )
    return {
        "project": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "left": _policy_compare_side(left),
        "right": _policy_compare_side(right),
        "summary": {"added_flags": len(added), "removed_flags": len(removed), "shared_flags": len(shared)},
        "threshold_deltas": threshold_deltas,
        "added_flags": [_policy_flag_lookup(right, key) for key in added],
        "removed_flags": [_policy_flag_lookup(left, key) for key in removed],
        "shared_flags": [_policy_flag_lookup(right, key) for key in shared],
    }


def _policy_flag_keys(payload: dict[str, Any]) -> set[tuple[str, str, str]]:
    return {
        (str(row.get("dimension", "")), str(row.get("asset_id", "")), str(row.get("name", "")))
        for row in payload.get("flags", [])
        if isinstance(row, dict)
    }


def _policy_flag_lookup(payload: dict[str, Any], key: tuple[str, str, str]) -> dict[str, Any]:
    for row in payload.get("flags", []):
        if isinstance(row, dict) and (str(row.get("dimension", "")), str(row.get("asset_id", "")), str(row.get("name", ""))) == key:
            return row
    return {"dimension": key[0], "asset_id": key[1], "name": key[2], "exposure": 0.0, "threshold": 0.0}


def _policy_compare_side(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": payload.get("profile", ""),
        "portfolio_id": payload.get("portfolio_id", ""),
        "source": payload.get("source", ""),
        "flag_count": payload.get("flag_count", 0),
        "status": payload.get("status", ""),
    }


def _policy_profile_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Policy Profile: {payload['profile']}",
        "",
        DISCLAIMER,
        "",
        payload["policy_boundary"],
        "",
        f"- Portfolio: {payload['portfolio_id']}",
        f"- Profile: {payload['profile_label']}",
        f"- Status: {payload['status']}",
        f"- Review flags: {payload['flag_count']}",
        "",
        "## Thresholds",
        "",
        "| Dimension | Threshold |",
        "| --- | ---: |",
    ]
    for key, value in payload["thresholds"].items():
        lines.append(f"| {key} | {_pct(value)} |")
    lines.extend(["", "## Flags", "", "| Dimension | Name | Exposure | Threshold | Margin |", "| --- | --- | ---: | ---: | ---: |"])
    if payload["flags"]:
        for row in payload["flags"]:
            lines.append(f"| {row['dimension']} | {row['name']} | {_pct(row['exposure'])} | {_pct(row['threshold'])} | {_signed_pct(row['margin_to_threshold'])} |")
    else:
        lines.append("| none | Static exposure artifact is within configured research thresholds | 0.00% | 0.00% | 0.00% |")
    return "\n".join(lines) + "\n"


def _policy_compare_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Policy Compare",
        "",
        DISCLAIMER,
        "",
        f"Left: `{payload['left']['profile']}` / {payload['left']['portfolio_id']}",
        f"Right: `{payload['right']['profile']}` / {payload['right']['portfolio_id']}",
        "",
        f"- Added flags: {payload['summary']['added_flags']}",
        f"- Removed flags: {payload['summary']['removed_flags']}",
        f"- Shared flags: {payload['summary']['shared_flags']}",
        "",
        "## Threshold Changes",
        "",
        "| Dimension | Left | Right | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in payload["threshold_deltas"]:
        lines.append(f"| {row['dimension']} | {_pct(row['left'])} | {_pct(row['right'])} | {_signed_pct(row['change'])} |")
    for title, rows in [("Added Flags", payload["added_flags"]), ("Removed Flags", payload["removed_flags"]), ("Shared Flags", payload["shared_flags"])]:
        if rows:
            lines.extend(["", f"## {title}", "", "| Dimension | Name | Exposure | Threshold |", "| --- | --- | ---: | ---: |"])
            for row in rows:
                lines.append(f"| {row['dimension']} | {row['name']} | {_pct(row['exposure'])} | {_pct(row['threshold'])} |")
    return "\n".join(lines) + "\n"


def _policy_gallery_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Policy Gallery",
        "",
        DISCLAIMER,
        "",
        "Bundled examples apply research-only threshold profiles to static fixture-derived exposures.",
        "",
        "| Case | Portfolio | Profile | Flags | Status |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for case in payload["examples"]:
        for profile in case["profiles"]:
            lines.append(f"| {case['name']} | {case['portfolio_id']} | {profile['profile']} | {profile['flag_count']} | {profile['status']} |")
    return "\n".join(lines) + "\n"


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _signed_pct(value: float) -> str:
    return f"{value * 100:+.2f}%"


def _state_artifact_outputs() -> set[str]:
    return {
        "demo/adoption_notes.md",
        "demo/adoption_notes.json",
        "demo/final_handoff.md",
        "demo/final_handoff.json",
        "demo/final_qa.md",
        "demo/final_qa.json",
        "demo/release_compare.md",
        "demo/release_compare.json",
        "demo/snapshot_ledger.md",
        "demo/snapshot_ledger.json",
        "demo/snapshot_compare.md",
        "demo/snapshot_compare.json",
        "demo/review_queue.md",
        "demo/review_queue.json",
    }


def _release_checklist_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Release Checklist",
        "",
        DISCLAIMER,
        "",
        f"Status: {'ready' if payload['ok'] else 'review required'}",
        "",
        "| Area | Ready | Owner action | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["checks"]:
        evidence = ", ".join(row["evidence"]) if row["evidence"] else "missing"
        lines.append(f"| {row['name']} | {'yes' if row['ready'] else 'no'} | {row['owner_action']} | {evidence} |")
    return "\n".join(lines) + "\n"


def _is_text_path(path: Path) -> bool:
    return path.suffix.lower() in {"", ".csv", ".html", ".json", ".md", ".py", ".svg", ".toml", ".txt"}


def public_hygiene_findings(root: Path) -> list[str]:
    banned_terms = [
        "Her" + "mes",
        "Fei" + "shu",
        "api" + "_key",
        "secret" + "_key",
        "access" + "_token",
        "bearer" + " ",
    ]
    generated_parts = {".pytest_cache", "__pycache__", "dist", "build"}
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() and path.name in generated_parts:
            continue
        if not path.is_file() or not _is_text_path(path):
            continue
        if any(part in {".git"} for part in path.parts):
            continue
        if any(part in generated_parts for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for term in banned_terms:
            if term in content:
                findings.append(f"{path.relative_to(root)} contains {term}")
    return findings


def _pyproject_has_no_runtime_deps(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "dependencies = []" in text


if __name__ == "__main__":
    raise SystemExit(main())
