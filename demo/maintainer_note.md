# Maintainer Note

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Version: 1.0.1
Purpose: deterministic maintainer note for docs and packaging evidence

## Evidence

| Path | Status | SHA-256 prefix |
| --- | --- | --- |
| `README.md` | ready | `2680ab2f2576311b` |
| `pyproject.toml` | ready | `1ec4eeb078e9c2d1` |
| `CHANGELOG.md` | ready | `bb7b09877840d80e` |
| `RELEASE_NOTES.md` | ready | `c4f848f5f345363d` |
| `demo/cli_help.json` | ready | `a6b127344f6cb5f6` |
| `demo/command_matrix.json` | ready | `bd104384894eadb1` |
| `demo/final_handoff.json` | ready | `1bcdb822080ef3cf` |

## Verification

- `python -m pytest -q`
- `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .`
- `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .`
- `python -m pip wheel . --no-deps -w dist`

## Boundaries

- zero runtime dependencies
- no workflow automation
- no live data fetching
- no broker connectivity
- no financial advice, recommendations, target allocations, trades, or return predictions

## Next Steps

- Regenerate docs-export, command-matrix, release-manifest, artifact-catalog, asset-health, bundle-export, final-handoff, and maintainer-note after any command or artifact change.
- Run the complete verification suite before tagging.
- Keep generated demo files deterministic and exclude bytecode, pytest cache, build, dist, and egg-info outputs from commits.
