# Release Checklist

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Status: ready

| Area | Ready | Owner action | Evidence |
| --- | --- | --- | --- |
| tests | yes | Run `python -m pytest -q` from the source checkout. | tests/ |
| package | yes | Build with the local zero-dependency backend and inspect metadata. | pyproject.toml, build_backend.py |
| wheel-smoke | yes | Install the built wheel in a clean environment and run `fund-exposure-lookthrough --version` plus `selfcheck --root .`. | build_backend.py, src/fund_exposure_lookthrough/__init__.py |
| public-scan | yes | Run `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .`. | clean public hygiene scan |
| no-advice-boundaries | yes | Confirm docs and generated reports preserve static research-only language. | render.DISCLAIMER, README.md |
| no-workflows | yes | Confirm no workflow automation files are present. | no .github/workflows directory |
