"""Fixture diagnostics for portfolio and constituent CSV files."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from . import __version__
from .engine import fund_weight_total
from .io import read_constituents, read_holdings
from .render import DISCLAIMER


@dataclass(frozen=True)
class FixtureFinding:
    """A deterministic fixture quality finding."""

    severity: str
    code: str
    subject: str
    detail: str


def diagnose_fixtures(portfolio_path: Path, constituents_path: Path, as_of: date, max_source_age_days: int) -> dict[str, Any]:
    holdings = read_holdings(portfolio_path)
    constituents = read_constituents(constituents_path)
    portfolio_rows = _raw_rows(portfolio_path)
    constituent_rows = _raw_rows(constituents_path)
    findings: list[FixtureFinding] = []

    portfolio_total = fund_weight_total(holdings)
    if abs(portfolio_total - 1.0) > 0.0001:
        findings.append(
            FixtureFinding(
                "error",
                "portfolio_weight_total",
                "portfolio",
                f"portfolio fund weights sum to {portfolio_total:.4f}, not 1.0000",
            )
        )

    by_fund: dict[str, float] = defaultdict(float)
    for row in constituents:
        by_fund[row.fund_id] += row.weight
    held_funds = {row.fund_id for row in holdings}
    constituent_funds = set(by_fund)
    for fund_id in sorted(held_funds - constituent_funds):
        findings.append(
            FixtureFinding("error", "missing_constituents", fund_id, f"fund {fund_id} appears in portfolio but has no constituent rows")
        )
    for fund_id in sorted(constituent_funds - held_funds):
        findings.append(
            FixtureFinding("warning", "unheld_constituent_fund", fund_id, f"fund {fund_id} has constituent rows but is not held in the portfolio")
        )
    for fund_id in sorted(constituent_funds):
        total = round(by_fund[fund_id], 10)
        if abs(total - 1.0) > 0.0001:
            findings.append(
                FixtureFinding(
                    "error",
                    "constituent_weight_total",
                    fund_id,
                    f"fund {fund_id} constituent weights sum to {total:.4f}, not 1.0000",
                )
            )

    findings.extend(_duplicate_findings(portfolio_rows, ("fund_id",), "portfolio_duplicate_fund", "portfolio fund row"))
    findings.extend(_duplicate_findings(constituent_rows, ("fund_id", "asset_id"), "constituent_duplicate_asset", "fund constituent asset"))
    findings.extend(_metadata_findings(portfolio_rows, portfolio_path.name, as_of, max_source_age_days))
    findings.extend(_metadata_findings(constituent_rows, constituents_path.name, as_of, max_source_age_days))

    finding_dicts = [_finding_dict(item) for item in sorted(findings, key=lambda item: (item.severity, item.code, item.subject, item.detail))]
    summary = Counter(item["severity"] for item in finding_dicts)
    return {
        "tool": "fund-exposure-lookthrough",
        "version": __version__,
        "safety": DISCLAIMER,
        "ok": not finding_dicts,
        "as_of": as_of.isoformat(),
        "max_source_age_days": max_source_age_days,
        "portfolio": str(portfolio_path),
        "constituents": str(constituents_path),
        "summary": {
            "error": summary.get("error", 0),
            "warning": summary.get("warning", 0),
            "info": summary.get("info", 0),
            "total": len(finding_dicts),
        },
        "findings": finding_dicts,
    }


def fixture_doctor_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Fixture Doctor Report",
        "",
        DISCLAIMER,
        "",
        f"- Status: {'pass' if payload['ok'] else 'review required'}",
        f"- As of: {payload['as_of']}",
        f"- Max source age: {payload['max_source_age_days']} days",
        f"- Portfolio: {payload['portfolio']}",
        f"- Constituents: {payload['constituents']}",
        f"- Findings: {payload['summary']['total']} total, {payload['summary']['error']} errors, {payload['summary']['warning']} warnings",
        "",
        "| Severity | Code | Subject | Detail |",
        "| --- | --- | --- | --- |",
    ]
    if payload["findings"]:
        for item in payload["findings"]:
            lines.append(f"| {item['severity']} | {item['code']} | {item['subject']} | {item['detail']} |")
    else:
        lines.append("| info | clean | fixtures | No fixture quality findings |")
    return "\n".join(lines) + "\n"


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid ISO date {value!r}") from exc


def _raw_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _duplicate_findings(rows: list[dict[str, str]], keys: tuple[str, ...], code: str, label: str) -> list[FixtureFinding]:
    counts = Counter(tuple(row.get(key, "").strip() for key in keys) for row in rows)
    findings: list[FixtureFinding] = []
    for key, count in sorted(counts.items()):
        if count > 1:
            subject = "/".join(key)
            findings.append(FixtureFinding("error", code, subject, f"{label} {subject} appears {count} times"))
    return findings


def _metadata_findings(rows: list[dict[str, str]], source_name: str, as_of: date, max_source_age_days: int) -> list[FixtureFinding]:
    if not rows:
        return []
    has_source_date = any("source_date" in row for row in rows)
    has_source_url = any("source_url" in row for row in rows)
    if not has_source_date and not has_source_url:
        return []

    cutoff = as_of - timedelta(days=max_source_age_days)
    findings: list[FixtureFinding] = []
    for index, row in enumerate(rows, start=2):
        subject = f"{source_name}:row{index}"
        source_date = row.get("source_date", "").strip()
        source_url = row.get("source_url", "").strip()
        if has_source_date and not source_date:
            findings.append(FixtureFinding("warning", "missing_source_date", subject, "source_date is empty"))
        elif source_date:
            try:
                parsed = date.fromisoformat(source_date)
            except ValueError:
                findings.append(FixtureFinding("error", "invalid_source_date", subject, f"source_date {source_date!r} is not YYYY-MM-DD"))
            else:
                if parsed < cutoff:
                    findings.append(
                        FixtureFinding(
                            "warning",
                            "stale_source_date",
                            subject,
                            f"source_date {source_date} is older than {max_source_age_days} days as of {as_of.isoformat()}",
                        )
                    )
                if parsed > as_of:
                    findings.append(FixtureFinding("warning", "future_source_date", subject, f"source_date {source_date} is after as-of date"))
        if has_source_url and not source_url:
            findings.append(FixtureFinding("warning", "missing_source_url", subject, "source_url is empty"))
        elif source_url and not source_url.startswith(("https://", "http://")):
            findings.append(FixtureFinding("warning", "non_http_source_url", subject, f"source_url {source_url!r} is not an HTTP URL"))
    return findings


def _finding_dict(item: FixtureFinding) -> dict[str, str]:
    return {"severity": item.severity, "code": item.code, "subject": item.subject, "detail": item.detail}
