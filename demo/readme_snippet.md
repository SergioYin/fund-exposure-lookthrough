## Quickstart Demo

```bash
PYTHONPATH=src python -m fund_exposure_lookthrough.cli public-readiness --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli docs-export --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli landing-page --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .
```

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Generated demo artifacts:
- `demo/index.html`
- `demo/public_readiness.md`
- `demo/promotion_pack.md`
- `demo/cli_help.md`
- `demo/exposure_packet.md`
- `demo/policy_profile.md`
- `demo/policy_gallery.md`
- `demo/static_dashboard.html`
- `demo/case_gallery.md`
- `demo/visual_receipt.svg`
- `demo/asset_health.md`
- `demo/maintainer_note.md`
