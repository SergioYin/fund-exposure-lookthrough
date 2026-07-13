"""Render reports into public-safe static artifacts."""

from __future__ import annotations

from html import escape
from typing import Any, Iterable

from . import __version__
from .models import ExposureRow, Holding

DISCLAIMER = (
    "Research use only. This static report is not investment advice, does not recommend buys, "
    "sells, holds, target allocations, or trades, and uses only user-supplied fixture data."
)


def packet_payload(portfolio_id: str, holdings: list[Holding], exposures: list[ExposureRow], warnings: list[str]) -> dict[str, Any]:
    return {
        "tool": "fund-exposure-lookthrough",
        "version": __version__,
        "portfolio_id": portfolio_id,
        "safety": DISCLAIMER,
        "fund_count": len(holdings),
        "asset_count": len(exposures),
        "total_exposure": round(sum(row.exposure for row in exposures), 10),
        "warnings": warnings,
        "top_assets": [exposure_dict(row) for row in exposures[:10]],
    }


def exposure_dict(row: ExposureRow) -> dict[str, Any]:
    return {
        "asset_id": row.asset_id,
        "asset_name": row.asset_name,
        "exposure": row.exposure,
        "sector": row.sector,
        "region": row.region,
        "asset_class": row.asset_class,
    }


def packet_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Exposure Packet: {payload['portfolio_id']}",
        "",
        DISCLAIMER,
        "",
        f"- Funds: {payload['fund_count']}",
        f"- Look-through assets: {payload['asset_count']}",
        f"- Total look-through exposure: {_pct(payload['total_exposure'])}",
        "",
        "## Top Assets",
        "",
        "| Asset | Exposure | Sector | Region |",
        "| --- | ---: | --- | --- |",
    ]
    for row in payload["top_assets"]:
        lines.append(f"| {row['asset_name']} | {_pct(row['exposure'])} | {row['sector']} | {row['region']} |")
    if payload["warnings"]:
        lines.extend(["", "## Input Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    return "\n".join(lines) + "\n"


def comparison_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Exposure History Comparison",
        "",
        DISCLAIMER,
        "",
        "| Asset | Current | Prior | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['asset_name']} | {_pct(row['current'])} | {_pct(row['prior'])} | {_signed_pct(row['change'])} |")
    return "\n".join(lines) + "\n"


def overlap_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Fund Overlap Matrix",
        "",
        DISCLAIMER,
        "",
        "| Fund A | Fund B | Shared constituent weight |",
        "| --- | --- | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['left_fund_id']} | {row['right_fund_id']} | {_pct(row['overlap'])} |")
    return "\n".join(lines) + "\n"


def ledger_markdown(flags: list[dict[str, Any]], warnings: list[str], threshold: float) -> str:
    lines = [
        "# Review Ledger",
        "",
        DISCLAIMER,
        "",
        f"Concentration review threshold: {_pct(threshold)}",
        "",
        "| Item | Detail |",
        "| --- | --- |",
    ]
    if warnings:
        for warning in warnings:
            lines.append(f"| Input warning | {warning} |")
    if flags:
        for row in flags:
            lines.append(f"| Concentration flag | {row['asset_name']} at {_pct(row['exposure'])} |")
    if not warnings and not flags:
        lines.append("| No review flags | Static inputs passed configured checks |")
    return "\n".join(lines) + "\n"


def dashboard_html(payload: dict[str, Any], sectors: Iterable[dict[str, Any]], regions: Iterable[dict[str, Any]]) -> str:
    asset_rows = "\n".join(
        f"<tr><td>{escape(row['asset_name'])}</td><td>{_pct(row['exposure'])}</td><td>{escape(row['sector'])}</td><td>{escape(row['region'])}</td></tr>"
        for row in payload["top_assets"]
    )
    sector_items = "\n".join(f"<li>{escape(row['name'])}: {_pct(row['exposure'])}</li>" for row in sectors)
    region_items = "\n".join(f"<li>{escape(row['name'])}: {_pct(row['exposure'])}</li>" for row in regions)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fund Exposure Look-through Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2933; background: #f7f8fa; }}
    main {{ max-width: 960px; margin: 0 auto; }}
    section {{ margin: 1.25rem 0; padding: 1rem; background: white; border: 1px solid #d9dee7; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    th, td {{ border-bottom: 1px solid #d9dee7; padding: 0.55rem; text-align: left; }}
    th:nth-child(2), td:nth-child(2) {{ text-align: right; }}
    .notice {{ border-left: 4px solid #596579; padding-left: 0.75rem; }}
  </style>
</head>
<body>
<main>
  <h1>Fund Exposure Look-through Dashboard</h1>
  <p class="notice">{escape(DISCLAIMER)}</p>
  <section>
    <h2>Summary</h2>
    <p>Portfolio {escape(str(payload["portfolio_id"]))}: {payload["fund_count"]} funds, {payload["asset_count"]} look-through assets, {_pct(payload["total_exposure"])} total exposure.</p>
  </section>
  <section>
    <h2>Top Assets</h2>
    <table><thead><tr><th>Asset</th><th>Exposure</th><th>Sector</th><th>Region</th></tr></thead><tbody>{asset_rows}</tbody></table>
  </section>
  <section>
    <h2>Sector Exposure</h2>
    <ul>{sector_items}</ul>
  </section>
  <section>
    <h2>Region Exposure</h2>
    <ul>{region_items}</ul>
  </section>
</main>
</body>
</html>
"""


def manifest_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Release Manifest", "", DISCLAIMER, ""]
    for key in sorted(payload):
        lines.append(f"- {key}: {payload[key]}")
    return "\n".join(lines) + "\n"


def maturity_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Maturity Report",
        "",
        DISCLAIMER,
        "",
        "| Capability | Status |",
        "| --- | --- |",
    ]
    for item in payload["capabilities"]:
        lines.append(f"| {item['name']} | {item['status']} |")
    return "\n".join(lines) + "\n"


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"
