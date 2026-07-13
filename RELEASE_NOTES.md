# Release Notes

## 0.5.0

Adds an audit and reproducibility layer for release review:

- `artifact-catalog` catalogs existing demo artifacts with file type, byte size, SHA-256 hash, and regeneration command.
- `command-matrix` writes Markdown and JSON coverage of every CLI route, including inputs, outputs, and exit-code behavior.
- `release-checklist` writes a release owner checklist for tests, package review, wheel smoke, public scan, no-advice boundaries, and workflow absence.

The release also updates generated demo outputs, tests, README guidance, skill guidance, package version metadata, and the local build backend. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, and no financial advice surface.

## 0.4.0

Adds an operator workflow layer for portable public review:

- `bundle-export` copies selected deterministic demo artifacts into a portable directory and writes Markdown/JSON manifests with hashes.
- `asset-health` summarizes CLI command coverage, artifact presence, packaged CSV data, and static safety boundaries.
- `readme-snippet` generates a concise Markdown quickstart/demo snippet from the artifacts currently present.

The release also updates generated demo outputs, tests, README guidance, skill guidance, package version metadata, and the local build backend. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, and no financial advice surface.

## 0.3.0

Adds a richer public showcase layer for deterministic review:

- `case-gallery` builds Markdown and JSON comparing bundled current/prior cases and a direct-holding/ETF-wrapper fixture.
- `visual-receipt` builds a deterministic SVG or HTML receipt with demo artifact routes and SHA-256 hashes.
- `reviewer-scorecard` maps release evidence to a maturity rubric for public review.

The release also adds packaged direct-wrapper example CSVs, generated demo outputs, expanded README and skill guidance, and tests for the new routes. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, and no financial advice surface.

## 0.2.0

Adds substantial fixture quality tooling with the new `fixture-doctor` command. The command validates static portfolio and constituent CSVs, writes Markdown and JSON reports, and returns a non-zero exit code when review findings are present.

New checks:

- missing portfolio funds in constituent fixtures
- constituent funds not held in the portfolio
- portfolio and per-fund constituent weights that do not sum to `1.0000`
- duplicate portfolio fund rows and duplicate fund/asset rows
- optional `source_date` and `source_url` metadata freshness and shape

The release preserves zero runtime dependencies, deterministic demo outputs, no workflow files, no live data fetching, no broker connectivity, and no financial advice surface.

## 0.1.0

First public release of `fund-exposure-lookthrough`.

Included commands:

- `build-packet`
- `compare-history`
- `overlap-matrix`
- `review-ledger`
- `fixture-doctor`
- `static-dashboard`
- `selfcheck`
- `release-manifest`
- `maturity-report`

Safety boundary: the CLI performs static research analysis only and does not provide investment advice, broker connectivity, live data fetching, trading, return prediction, or target allocation recommendations.
