# Public Readiness Walkthrough

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Version: 1.0.1
Walkthrough: first-10-minute cold-user walkthrough
Zero runtime dependencies: yes
No workflow automation: yes
No live data boundary documented: yes

| Minute | Goal | Command | Expected result | Artifact |
| --- | --- | --- | --- | --- |
| 0-1 | Confirm the project is static research tooling. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli --help` | CLI help lists deterministic artifact commands and no network setup. | `stdout` |
| 1-2 | Build the primary exposure packet and research-only policy profile from bundled CSV fixtures. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root . && PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-profile --root .` | Exposure and policy profile artifacts appear under demo/ without allocation recommendations. | `demo/exposure_packet.md` |
| 2-3 | Review fixture quality without fetching live data. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli fixture-doctor --root .` | Clean bundled fixtures return ok and document source metadata checks. | `demo/fixture_doctor.md` |
| 3-4 | Open the static dashboard for a visual table review. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .` | A no-JavaScript HTML dashboard is available. | `demo/static_dashboard.html` |
| 4-5 | Compare bundled scenarios and inspect public examples. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli case-gallery --root . && PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-gallery --root .` | Current, prior, direct-wrapper, and bundled policy profile cases are summarized. | `demo/case_gallery.md` |
| 5-6 | Export route help for offline review. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli docs-export --root .` | CLI help and command metadata are exported as Markdown and JSON. | `demo/cli_help.md` |
| 6-7 | Build a public landing page that links the demo set. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli landing-page --root .` | A static index page links demos, bundle, receipt, command matrix, and safety boundaries. | `demo/index.html` |
| 7-8 | Create a visual receipt and command matrix for reviewer orientation. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli visual-receipt --root . && PYTHONPATH=src python -m fund_exposure_lookthrough.cli command-matrix --root .` | Artifact hashes and command coverage are available. | `demo/visual_receipt.svg` |
| 8-9 | Run safety and package readiness checks. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root . && PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .` | Static boundaries, package data, and public hygiene checks pass. | `demo/asset_health.md` |
| 9-10 | Bundle the deterministic public review artifacts. | `PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .` | Portable review bundle manifest is written with copied artifacts. | `demo/bundle_export/manifest.md` |
