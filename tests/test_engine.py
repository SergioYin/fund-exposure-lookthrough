from pathlib import Path

from fund_exposure_lookthrough.engine import compare_exposures, group_exposure, lookthrough, overlap_matrix, validate_inputs
from fund_exposure_lookthrough.io import read_constituents, read_holdings


ROOT = Path(__file__).resolve().parents[1]


def test_lookthrough_math_totals_and_asset_exposure():
    holdings = read_holdings(ROOT / "examples/current_portfolio.csv")
    constituents = read_constituents(ROOT / "examples/fund_constituents.csv")

    rows = lookthrough(holdings, constituents)
    by_asset = {row.asset_id: row.exposure for row in rows}

    assert round(sum(by_asset.values()), 10) == 1.0
    assert by_asset["AST_ALPHA"] == 0.182
    assert by_asset["AST_CASH"] == 0.1175
    assert validate_inputs(holdings, constituents) == []


def test_grouping_and_comparison_are_deterministic():
    constituents = read_constituents(ROOT / "examples/fund_constituents.csv")
    current = lookthrough(read_holdings(ROOT / "examples/current_portfolio.csv"), constituents)
    prior = lookthrough(read_holdings(ROOT / "examples/prior_portfolio.csv"), constituents)

    sectors = group_exposure(current, "sector")
    comparison = compare_exposures(current, prior)

    assert sectors[0] == {"name": "Technology", "exposure": 0.266}
    assert comparison[0]["asset_id"] == "AST_EPSILON"
    assert comparison[0]["change"] == 0.012


def test_overlap_matrix_includes_self_and_cross_fund_overlap():
    holdings = read_holdings(ROOT / "examples/current_portfolio.csv")
    constituents = read_constituents(ROOT / "examples/fund_constituents.csv")

    rows = overlap_matrix(holdings, constituents)
    lookup = {(row["left_fund_id"], row["right_fund_id"]): row["overlap"] for row in rows}

    assert lookup[("FND_CORE", "FND_CORE")] == 1.0
    assert lookup[("FND_CORE", "FND_GLOBAL")] == 0.16
    assert lookup[("FND_CORE", "FND_BOND")] == 0.15
