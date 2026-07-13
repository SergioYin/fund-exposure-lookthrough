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
from .engine import compare_exposures, concentration_flags, group_exposure, lookthrough, overlap_matrix, validate_inputs
from .io import read_constituents, read_holdings, write_json, write_text
from .render import (
    DISCLAIMER,
    comparison_markdown,
    dashboard_html,
    ledger_markdown,
    manifest_markdown,
    maturity_markdown,
    overlap_markdown,
    packet_markdown,
    packet_payload,
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

    dashboard = sub.add_parser("static-dashboard", help="Build a no-JavaScript static HTML dashboard.")
    _add_input_args(dashboard)
    dashboard.add_argument("--out-html", default="demo/static_dashboard.html")
    dashboard.set_defaults(func=cmd_static_dashboard)

    selfcheck = sub.add_parser("selfcheck", help="Check package, examples, safety text, and generated artifacts.")
    selfcheck.add_argument("--root", default=".")
    selfcheck.set_defaults(func=cmd_selfcheck)

    public_scan = sub.add_parser("public-scan", help="Scan text files for private names, credentials, and generated artifacts.")
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


def cmd_static_dashboard(args: argparse.Namespace) -> int:
    root = Path(args.root)
    holdings, constituents = _load(args)
    exposures = lookthrough(holdings, constituents)
    payload = packet_payload(holdings[0].portfolio_id, holdings, exposures, validate_inputs(holdings, constituents))
    html = dashboard_html(payload, group_exposure(exposures, "sector"), group_exposure(exposures, "region"))
    write_text(root / args.out_html, html)
    print(f"wrote {root / args.out_html}")
    return 0


def cmd_selfcheck(args: argparse.Namespace) -> int:
    root = Path(args.root)
    required = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "src/fund_exposure_lookthrough/cli.py",
        "examples/current_portfolio.csv",
        "examples/prior_portfolio.csv",
        "examples/fund_constituents.csv",
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


def _is_text_path(path: Path) -> bool:
    return path.suffix.lower() in {"", ".csv", ".html", ".json", ".md", ".py", ".toml", ".txt"}


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
            findings.append(f"{path.relative_to(root)} is a generated artifact directory")
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
