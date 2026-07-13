# Release Notes

## 1.0.1

Performs a docs and packaging maintenance pass:

- `maintainer-note` writes deterministic Markdown and JSON evidence for docs, package metadata, generated command docs, release artifacts, verification commands, boundaries, and next steps.
- `final-qa` writes deterministic Markdown and JSON final QA evidence covering changes since v0.5.0, verification commands, release risks, artifact hashes, coherence flags, and no-advice boundaries.
- README first-screen commands now include the maintainer evidence and final QA routes.
- Command metadata, generated CLI help, demo artifacts, package version metadata, and regression tests are updated for the patch release.

The release preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, no financial advice surface, no allocation recommendations, and no return predictions.

## 1.0.0

Stabilizes the accumulated v0.6-v0.9 release surface for public handoff:

- `final-handoff` writes Markdown and JSON release-owner notes with repository URL placeholders, verification commands, risks, and next steps.
- The generated demo surface now includes policy profiles, public readiness, promotion evidence, adoption notes, snapshot state, review queue, exported CLI help, landing page, release comparison, and bundle manifests.
- README first-screen CTAs now point reviewers to the exposure packet, public walkthrough, final handoff, selfcheck, and public scan.
- Package metadata and the local zero-dependency build backend are updated to 1.0.0.

The release preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, no financial advice surface, no allocation recommendations, and no return predictions.

## 0.9.0

Adds cross-run comparison and promotion evidence artifacts for static public review:

- `release-compare` compares release manifests or artifact catalogs across metadata changes and artifact hash deltas.
- `promotion-pack` bundles public-readiness, landing page, visual receipt, command matrix, and reviewer scorecard evidence.
- `adoption-notes` writes agent-facing reusable notes for using generated outputs in a thesis ledger as static evidence.

The release also updates generated demo outputs, tests, README guidance, skill guidance, package version metadata, and the local build backend. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, no financial advice surface, and no allocation recommendations.

## 0.8.0

Adds portfolio policy profile artifacts for static research review:

- `policy-profile` applies conservative, balanced, or concentrated research-only thresholds to an exposure packet.
- `policy-compare` compares two policy-profile JSON outputs across thresholds and review flags.
- `policy-gallery` writes deterministic Markdown/JSON examples for bundled fixtures under all bundled profiles.

The release also updates generated demo outputs, tests, README guidance, skill guidance, package version metadata, and the local build backend. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, no financial advice surface, and no allocation recommendations.

## 0.7.0

Adds a state/history workflow for deterministic release review:

- `snapshot-ledger` appends a timestamp-free artifact snapshot only when generated artifact hashes change.
- `snapshot-compare` compares two snapshot JSON files and reports added, removed, and changed artifacts.
- `review-queue` derives prioritized follow-up questions from exposure, fixture-doctor, asset-health, and release-checklist outputs.

The release also updates generated demo outputs, tests, README guidance, skill guidance, package version metadata, and the local build backend. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, and no financial advice surface.

## 0.6.0

Adds a public landing and walkthrough layer for cold reviewers:

- `public-readiness` writes a deterministic first-10-minute Markdown/JSON walkthrough.
- `landing-page` writes a no-JavaScript static `demo/index.html` linking the demo set, bundle, visual receipt, command matrix, exported help, and safety boundaries.
- `docs-export` writes deterministic Markdown/JSON exports of top-level and subcommand CLI help with command metadata.

The release also updates generated demo outputs, tests, README guidance, skill guidance, package version metadata, and the local build backend. It preserves zero runtime dependencies, no workflow files, no live data fetching, no broker connectivity, and no financial advice surface.

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
