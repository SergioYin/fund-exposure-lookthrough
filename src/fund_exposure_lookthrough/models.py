"""Small typed records used by the look-through engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Holding:
    """A portfolio holding row."""

    portfolio_id: str
    fund_id: str
    fund_name: str
    weight: float


@dataclass(frozen=True)
class Constituent:
    """A fund constituent row."""

    fund_id: str
    asset_id: str
    asset_name: str
    weight: float
    sector: str
    region: str
    asset_class: str


@dataclass(frozen=True)
class ExposureRow:
    """Weighted exposure after multiplying portfolio fund weights by constituents."""

    asset_id: str
    asset_name: str
    exposure: float
    sector: str
    region: str
    asset_class: str
