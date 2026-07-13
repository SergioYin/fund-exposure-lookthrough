# fund-exposure-lookthrough

Zero-runtime-dependency, broker-free Python CLI for static portfolio and fund look-through exposure research.

Target user: analysts, reviewers, and engineers who need reproducible exposure packets from user-supplied portfolio and fund constituent files without live data access.

## Quickstart

From a source checkout:

```bash
PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli compare-history --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli overlap-matrix --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli review-ledger --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli fixture-doctor --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .
PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .
PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .
```

Or install locally first:

```bash
python -m pip install .
fund-exposure-lookthrough build-packet --root .
fund-exposure-lookthrough selfcheck --root .
```

The commands default to the bundled CSV examples when `examples/` is not present in the selected root.
Use `python -B` for source-tree hygiene checks so the interpreter does not create bytecode caches while scanning.

Installed module invocation also works after `python -m pip install .`:

```bash
python -m fund_exposure_lookthrough.cli build-packet --root .
```

## Demo Paths

- `demo/exposure_packet.md` and `demo/exposure_packet.json`
- `demo/history_comparison.md` and `demo/history_comparison.json`
- `demo/overlap_matrix.md` and `demo/overlap_matrix.json`
- `demo/review_ledger.md` and `demo/review_ledger.json`
- `demo/fixture_doctor.md` and `demo/fixture_doctor.json`
- `demo/static_dashboard.html`
- `demo/release_manifest.md` and `demo/release_manifest.json`
- `demo/maturity_report.md` and `demo/maturity_report.json`

## Input Format

Portfolio CSV files use `portfolio_id,fund_id,fund_name,weight`. Fund constituent CSV files use `fund_id,asset_id,asset_name,weight,sector,region,asset_class`. Weights are decimal fractions, so `0.25` means 25%.

Both fixture types may also include optional `source_date` and `source_url` columns. The calculation commands ignore those columns, while `fixture-doctor` uses them to flag stale, missing, malformed, or non-HTTP source metadata without fetching live data.

## Fixture Doctor

`fixture-doctor` writes deterministic Markdown and JSON reports for fixture review. It checks:

- portfolio funds missing from the constituent file
- constituent funds that are not held in the portfolio
- portfolio or per-fund constituent weights that do not sum to `1.0000`
- duplicate portfolio fund rows and duplicate fund/asset constituent rows
- optional source metadata freshness using `--as-of` and `--max-source-age-days`

The default `--as-of 2026-07-14` keeps bundled demo outputs stable. Override it when reviewing a real fixture snapshot.

## Safety Boundaries

This project is research tooling only. It does not fetch live data, connect to brokers, place orders, recommend buys, sells, holds, target allocations, or trades, predict returns, or produce personalized financial advice. Reports are based only on static files provided by the user.

## Roadmap

- Additional static import validators for common custodian exports.
- More grouping dimensions while preserving deterministic output.
- Optional schema export for downstream review systems.
- Expanded examples for multi-asset and multi-currency research packets.
