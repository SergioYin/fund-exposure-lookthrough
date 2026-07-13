# Release Notes

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
