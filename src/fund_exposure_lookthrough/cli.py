"""Command line interface for static fund exposure look-through analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
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

    snippet = sub.add_parser("readme-snippet", help="Generate a concise Markdown quickstart and demo snippet from current artifacts.")
    snippet.add_argument("--root", default=".")
    snippet.add_argument("--out-md", default="demo/readme_snippet.md")
    snippet.set_defaults(func=cmd_readme_snippet)
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
    for row in artifacts:
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
        "missing": [row["route"] for row in artifacts if not row["exists"]],
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
    excluded = {args.out_md, args.out_json}
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
        "demo/exposure_packet.md",
        "demo/exposure_packet.json",
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
        "demo/asset_health.md",
        "demo/asset_health.json",
        "demo/artifact_catalog.md",
        "demo/artifact_catalog.json",
        "demo/command_matrix.md",
        "demo/command_matrix.json",
        "demo/release_checklist.md",
        "demo/release_checklist.json",
        "demo/readme_snippet.md",
    ]


def _operator_artifacts() -> list[str]:
    return [
        rel
        for rel in _bundle_artifacts()
        if rel
        not in {
            "demo/asset_health.md",
            "demo/asset_health.json",
            "demo/artifact_catalog.md",
            "demo/artifact_catalog.json",
            "demo/bundle_export/manifest.json",
        }
    ]


def _snippet_artifacts() -> list[str]:
    return [
        "demo/exposure_packet.md",
        "demo/static_dashboard.html",
        "demo/case_gallery.md",
        "demo/visual_receipt.svg",
        "demo/asset_health.md",
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
            "name": "readme-snippet",
            "inputs": ["--root", "--out-md"],
            "outputs": ["demo/readme_snippet.md"],
            "exit_codes": static_exit,
            "regeneration_command": "PYTHONPATH=src python -m fund_exposure_lookthrough.cli readme-snippet --root .",
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
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .",
        "PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .",
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
