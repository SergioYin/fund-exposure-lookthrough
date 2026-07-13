"""CSV and output helpers with no runtime dependencies."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

from .models import Constituent, Holding


def read_holdings(path: Path) -> list[Holding]:
    rows: list[Holding] = []
    for row in _read_csv(path, {"portfolio_id", "fund_id", "fund_name", "weight"}):
        rows.append(
            Holding(
                portfolio_id=row["portfolio_id"].strip(),
                fund_id=row["fund_id"].strip(),
                fund_name=row["fund_name"].strip(),
                weight=_parse_weight(row["weight"], path),
            )
        )
    if not rows:
        raise ValueError(f"{path} has no holdings")
    return rows


def read_constituents(path: Path) -> list[Constituent]:
    rows: list[Constituent] = []
    required = {"fund_id", "asset_id", "asset_name", "weight", "sector", "region", "asset_class"}
    for row in _read_csv(path, required):
        rows.append(
            Constituent(
                fund_id=row["fund_id"].strip(),
                asset_id=row["asset_id"].strip(),
                asset_name=row["asset_name"].strip(),
                weight=_parse_weight(row["weight"], path),
                sector=row["sector"].strip(),
                region=row["region"].strip(),
                asset_class=row["asset_class"].strip(),
            )
        )
    if not rows:
        raise ValueError(f"{path} has no constituents")
    return rows


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text, encoding="utf-8")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_csv(path: Path, required: set[str]) -> Iterable[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} is missing a header")
        missing = required.difference(reader.fieldnames)
        if missing:
            fields = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required column(s): {fields}")
        for row in reader:
            yield {key: value or "" for key, value in row.items()}


def _parse_weight(value: str, path: Path) -> float:
    try:
        weight = float(value)
    except ValueError as exc:
        raise ValueError(f"{path} contains invalid weight {value!r}") from exc
    if weight < 0:
        raise ValueError(f"{path} contains negative weight {value!r}")
    return weight
