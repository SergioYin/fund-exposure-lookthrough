# Final Release Handoff

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

- Project: fund-exposure-lookthrough
- Version: 1.0.1
- Repository: REPO_URL_PLACEHOLDER
- Handoff: release owner handoff for v1.0.1 stabilization

## Boundaries

- zero runtime dependencies
- no workflow automation
- no live data fetching
- no broker connectivity
- no financial advice, recommendations, target allocations, trades, or return predictions

## Verification Commands

| Check | Command | Expected result |
| --- | --- | --- |
| tests | `python -m pytest -q` | All local tests pass. |
| selfcheck | `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .` | JSON reports ok=true with no missing required files or hygiene findings. |
| public-scan | `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .` | JSON reports ok=true with no private terms or credential-shaped strings. |
| wheel-build | `python -m pip wheel . --no-deps -w dist` | A fund_exposure_lookthrough wheel is created using the local zero-dependency backend. |
| wheel-smoke | `python -m pip install --force-reinstall --no-deps dist/fund_exposure_lookthrough-1.0.1-py3-none-any.whl && fund-exposure-lookthrough --version && fund-exposure-lookthrough selfcheck --root .` | Installed CLI reports 1.0.1 and selfcheck passes. |

## Handoff Artifacts

| Artifact | Status | SHA-256 prefix |
| --- | --- | --- |
| `demo/exposure_packet.md` | ready | `cf497f898c35ab04` |
| `demo/policy_profile.md` | ready | `35126960d1247e60` |
| `demo/policy_gallery.md` | ready | `54e10610f7c796a8` |
| `demo/public_readiness.md` | ready | `22ce114567f33446` |
| `demo/promotion_pack.md` | ready | `73157f41a12119f3` |
| `demo/command_matrix.json` | ready | `bd104384894eadb1` |
| `demo/release_checklist.json` | ready | `d3c2e1e233b3d21b` |
| `demo/asset_health.json` | ready | `d5e015d46e4e6870` |

## Risks

| Risk | Owner action |
| --- | --- |
| Fixture staleness | Use fixture-doctor with an explicit --as-of date before relying on a new static snapshot. |
| Generated artifact drift | Regenerate command-matrix, release-manifest, artifact-catalog, and final-handoff after source or demo changes. |
| Packaging smoke not performed by automation | Run the wheel build and installed CLI smoke commands manually before tagging. |
| Scope creep into advice or live-data behavior | Reject changes that add live fetches, broker connectivity, orders, recommendations, target allocations, or return predictions. |

## Next Steps

- Replace REPO_URL_PLACEHOLDER with the public repository URL before publishing release notes.
- Run the verification commands from a clean checkout and record results in the release owner notes.
- Inspect demo/index.html, demo/public_readiness.md, and demo/final_handoff.md as the first-screen reviewer path.
- Tag v1.0.1 only after tests, selfcheck, public-scan, and wheel smoke pass.
