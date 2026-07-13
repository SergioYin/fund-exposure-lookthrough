# Final QA

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

- Project: fund-exposure-lookthrough
- Version: 1.0.1
- Baseline: v0.5.0
- Summary: deterministic final QA packet for release review

## Changes Since Baseline

- Added public-readiness, docs-export, and landing-page artifacts for cold reviewer onboarding.
- Added snapshot-ledger, snapshot-compare, and review-queue artifacts for deterministic state and follow-up review.
- Added policy-profile, policy-compare, and policy-gallery artifacts for research-only threshold review.
- Added release-compare, promotion-pack, and adoption-notes artifacts for cross-run review and thesis-ledger reuse.
- Added final-handoff and maintainer-note artifacts for release owner and maintainer evidence.
- Updated package metadata to production/stable v1.0.1 while preserving zero runtime dependencies.
- Updated the local build backend to read the package version and emit reproducible wheel/sdist archives.
- Expanded CLI regression and public safety tests for command metadata, deterministic outputs, packaged data, and no-advice boundaries.

## Verification Commands

| Check | Command | Expected result |
| --- | --- | --- |
| tests | `PYTHONPATH=src python -m pytest -q` | All tests pass, including deterministic artifact and public safety coverage. |
| selfcheck | `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .` | JSON reports ok=true with required files present and public hygiene clean. |
| public-scan | `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .` | JSON reports ok=true and findings is empty. |
| release-checklist | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-checklist --root .` | Release checklist reports ok=true across tests, package, smoke, public scan, boundaries, and workflow absence. |
| wheel-build | `python -m pip wheel . --no-deps -w dist` | Wheel builds with no runtime dependency resolution. |
| wheel-smoke | `python -m pip install --force-reinstall --no-deps dist/fund_exposure_lookthrough-1.0.1-py3-none-any.whl && fund-exposure-lookthrough --version && fund-exposure-lookthrough selfcheck --root .` | Installed CLI reports 1.0.1 and selfcheck passes. |

## Release Checks

| Check | Status | Owner action |
| --- | --- | --- |
| tests | ready | Run `python -m pytest -q` from the source checkout. |
| package | ready | Build with the local zero-dependency backend and inspect metadata. |
| wheel-smoke | ready | Install the built wheel in a clean environment and run `fund-exposure-lookthrough --version` plus `selfcheck --root .`. |
| public-scan | ready | Run `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .`. |
| no-advice-boundaries | ready | Confirm docs and generated reports preserve static research-only language. |
| no-workflows | ready | Confirm no workflow automation files are present. |

## Release Risks

| Risk | Mitigation |
| --- | --- |
| Generated artifact drift after source edits | Regenerate command-matrix, release-manifest, artifact-catalog, release-checklist, asset-health, bundle-export, maintainer-note, final-handoff, and final-qa before tagging. |
| Wheel smoke omitted because there is no workflow automation | Run the wheel-build and wheel-smoke commands manually from a clean checkout. |
| Fixture freshness assumptions become stale | Run fixture-doctor with an explicit --as-of date and update user-supplied fixture source metadata when needed. |
| Scope creep into live data, broker connectivity, or advice | Reject changes that add live fetches, orders, recommendations, target allocations, trades, or return predictions. |

## No-Advice Boundaries

- research use only
- not investment advice
- no buy, sell, hold, target allocation, or trade recommendations
- no return predictions
- no personalized financial advice
- only user-supplied static fixture data
- no live data fetching
- no broker connectivity

## Release Artifacts

| Artifact | Status | SHA-256 prefix |
| --- | --- | --- |
| `README.md` | ready | `2680ab2f2576311b` |
| `CHANGELOG.md` | ready | `bb7b09877840d80e` |
| `RELEASE_NOTES.md` | ready | `c4f848f5f345363d` |
| `pyproject.toml` | ready | `1ec4eeb078e9c2d1` |
| `build_backend.py` | ready | `f8fc0ce763044ce4` |
| `demo/final_handoff.json` | ready | `1bcdb822080ef3cf` |
| `demo/maintainer_note.json` | ready | `1650241e36a84523` |
| `demo/release_manifest.json` | ready | `56a4bf88b965946b` |
| `demo/artifact_catalog.json` | ready | `fcd2ebd5c52f7caa` |
| `demo/command_matrix.json` | ready | `bd104384894eadb1` |
| `demo/release_checklist.json` | ready | `d3c2e1e233b3d21b` |
| `demo/asset_health.json` | ready | `d5e015d46e4e6870` |

## Coherence

- version_matches: ready
- runtime_dependencies_empty: ready
- no_workflow_automation: ready
- public_scan_clean: ready
- release_checks_ready: ready
- artifacts_present: ready
