"""Deterministic exposure calculations."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import Constituent, ExposureRow, Holding


def fund_weight_total(holdings: Iterable[Holding]) -> float:
    return round(sum(row.weight for row in holdings), 10)


def validate_inputs(holdings: list[Holding], constituents: list[Constituent]) -> list[str]:
    warnings: list[str] = []
    total = fund_weight_total(holdings)
    if abs(total - 1.0) > 0.0001:
        warnings.append(f"portfolio fund weights sum to {total:.4f}, not 1.0000")

    by_fund: dict[str, float] = defaultdict(float)
    for row in constituents:
        by_fund[row.fund_id] += row.weight
    for fund_id in sorted({row.fund_id for row in holdings}):
        if fund_id not in by_fund:
            warnings.append(f"fund {fund_id} has no constituent rows")
        elif abs(by_fund[fund_id] - 1.0) > 0.0001:
            warnings.append(f"fund {fund_id} constituent weights sum to {by_fund[fund_id]:.4f}, not 1.0000")
    return warnings


def lookthrough(holdings: list[Holding], constituents: list[Constituent]) -> list[ExposureRow]:
    by_fund: dict[str, list[Constituent]] = defaultdict(list)
    for row in constituents:
        by_fund[row.fund_id].append(row)

    exposures: dict[str, dict[str, object]] = {}
    for holding in holdings:
        for constituent in by_fund.get(holding.fund_id, []):
            exposure = holding.weight * constituent.weight
            current = exposures.setdefault(
                constituent.asset_id,
                {
                    "asset_name": constituent.asset_name,
                    "exposure": 0.0,
                    "sector": constituent.sector,
                    "region": constituent.region,
                    "asset_class": constituent.asset_class,
                },
            )
            current["exposure"] = float(current["exposure"]) + exposure

    return [
        ExposureRow(
            asset_id=asset_id,
            asset_name=str(data["asset_name"]),
            exposure=round(float(data["exposure"]), 10),
            sector=str(data["sector"]),
            region=str(data["region"]),
            asset_class=str(data["asset_class"]),
        )
        for asset_id, data in sorted(exposures.items(), key=lambda item: (-float(item[1]["exposure"]), item[0]))
    ]


def group_exposure(rows: Iterable[ExposureRow], field: str) -> list[dict[str, float | str]]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        key = getattr(row, field)
        totals[key] += row.exposure
    return [
        {"name": key, "exposure": round(value, 10)}
        for key, value in sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    ]


def compare_exposures(current: list[ExposureRow], prior: list[ExposureRow]) -> list[dict[str, float | str]]:
    current_map = {row.asset_id: row for row in current}
    prior_map = {row.asset_id: row for row in prior}
    all_ids = sorted(set(current_map) | set(prior_map))
    rows: list[dict[str, float | str]] = []
    for asset_id in all_ids:
        current_row = current_map.get(asset_id)
        prior_row = prior_map.get(asset_id)
        name = current_row.asset_name if current_row else prior_row.asset_name  # type: ignore[union-attr]
        current_value = current_row.exposure if current_row else 0.0
        prior_value = prior_row.exposure if prior_row else 0.0
        rows.append(
            {
                "asset_id": asset_id,
                "asset_name": name,
                "current": round(current_value, 10),
                "prior": round(prior_value, 10),
                "change": round(current_value - prior_value, 10),
            }
        )
    return sorted(rows, key=lambda row: (-abs(float(row["change"])), str(row["asset_id"])))


def overlap_matrix(holdings: list[Holding], constituents: list[Constituent]) -> list[dict[str, float | str]]:
    by_fund_assets: dict[str, dict[str, float]] = defaultdict(dict)
    for row in constituents:
        by_fund_assets[row.fund_id][row.asset_id] = row.weight
    funds = sorted({row.fund_id for row in holdings})
    matrix: list[dict[str, float | str]] = []
    for left in funds:
        for right in funds:
            left_assets = by_fund_assets.get(left, {})
            right_assets = by_fund_assets.get(right, {})
            shared = set(left_assets) & set(right_assets)
            overlap = sum(min(left_assets[asset], right_assets[asset]) for asset in shared)
            matrix.append({"left_fund_id": left, "right_fund_id": right, "overlap": round(overlap, 10)})
    return matrix


def concentration_flags(rows: list[ExposureRow], threshold: float) -> list[dict[str, float | str]]:
    return [
        {"asset_id": row.asset_id, "asset_name": row.asset_name, "exposure": row.exposure}
        for row in rows
        if row.exposure >= threshold
    ]
