## Quickstart Demo

```bash
PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root .
PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .
```

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Generated demo artifacts:
- `demo/exposure_packet.md`
- `demo/static_dashboard.html`
- `demo/case_gallery.md`
- `demo/visual_receipt.svg`
- `demo/asset_health.md`
