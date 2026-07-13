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
PYTHONPATH=src python -m fund_exposure_lookthrough.cli case-gallery --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli reviewer-scorecard --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli visual-receipt --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli readme-snippet --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli command-matrix --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-checklist --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli artifact-catalog --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .
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
- `demo/case_gallery.md` and `demo/case_gallery.json`
- `demo/reviewer_scorecard.md` and `demo/reviewer_scorecard.json`
- `demo/visual_receipt.svg`
- `demo/release_manifest.md` and `demo/release_manifest.json`
- `demo/maturity_report.md` and `demo/maturity_report.json`
- `demo/artifact_catalog.md` and `demo/artifact_catalog.json`
- `demo/command_matrix.md` and `demo/command_matrix.json`
- `demo/release_checklist.md` and `demo/release_checklist.json`
- `demo/readme_snippet.md`
- `demo/asset_health.md` and `demo/asset_health.json`
- `demo/bundle_export/manifest.md`, `demo/bundle_export/manifest.json`, and copied demo artifacts under `demo/bundle_export/artifacts/`

## Input Format

Portfolio CSV files use `portfolio_id,fund_id,fund_name,weight`. Fund constituent CSV files use `fund_id,asset_id,asset_name,weight,sector,region,asset_class`. Weights are decimal fractions, so `0.25` means 25%.

Both fixture types may also include optional `source_date` and `source_url` columns. The calculation commands ignore those columns, while `fixture-doctor` uses them to flag stale, missing, malformed, or non-HTTP source metadata without fetching live data.

The `direct_wrapper_*` examples show a direct-holding plus ETF-wrapper case without adding a second calculation model. Direct positions are represented as transparent one-constituent sleeves with a `1.00` constituent weight, so the same look-through engine and validators apply.

## Fixture Doctor

`fixture-doctor` writes deterministic Markdown and JSON reports for fixture review. It checks:

- portfolio funds missing from the constituent file
- constituent funds that are not held in the portfolio
- portfolio or per-fund constituent weights that do not sum to `1.0000`
- duplicate portfolio fund rows and duplicate fund/asset constituent rows
- optional source metadata freshness using `--as-of` and `--max-source-age-days`

The default `--as-of 2026-07-14` keeps bundled demo outputs stable. Override it when reviewing a real fixture snapshot.

## Showcase Commands

- `case-gallery` compares the bundled current portfolio, bundled prior portfolio, and direct-holding/ETF-wrapper example in deterministic Markdown and JSON.
- `visual-receipt` writes a deterministic SVG or HTML receipt with demo artifact routes and SHA-256 hashes.
- `reviewer-scorecard` maps release evidence to a maturity rubric covering dependencies, fixtures, demos, docs, safety, and workflow absence.

## Operator Workflow

- `asset-health` writes Markdown and JSON status for CLI command coverage, demo artifact presence, packaged CSV data, and static safety boundaries.
- `artifact-catalog` catalogs every existing file under `demo/` except its own outputs, including artifact type, byte size, SHA-256 hash, and regeneration command.
- `command-matrix` writes Markdown and JSON route coverage for CLI inputs, outputs, and exit-code behavior.
- `release-checklist` writes a release owner checklist combining tests, package review, wheel smoke expectations, public scan, no-advice boundaries, and workflow absence.
- `readme-snippet` writes a concise Markdown quickstart/demo block based on artifacts currently present in `demo/`.
- `bundle-export` copies selected demo artifacts into `demo/bundle_export/artifacts/` and writes deterministic Markdown/JSON manifests for portable review.

## Safety Boundaries

This project is research tooling only. It does not fetch live data, connect to brokers, place orders, recommend buys, sells, holds, target allocations, or trades, predict returns, or produce personalized financial advice. Reports are based only on static files provided by the user.

## Roadmap

- Additional static import validators for common custodian exports.
- More grouping dimensions while preserving deterministic output.
- Optional schema export for downstream review systems.
- Expanded examples for multi-asset and multi-currency research packets.
