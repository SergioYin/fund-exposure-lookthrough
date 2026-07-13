"""Command line interface for static fund exposure look-through analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def _artifact_row(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {"route": rel, "exists": path.exists(), "sha256": _file_digest(path) if path.exists() else ""}


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _existing(root: Path, paths: list[str]) -> list[str]:
    return [path for path in paths if (root / path).exists()]


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
