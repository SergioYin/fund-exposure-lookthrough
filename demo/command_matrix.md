# Command Matrix

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Commands documented: 34

| Command | Inputs | Outputs | Exit-code behavior |
| --- | --- | --- | --- |
| `build-packet` | `--root`, `--portfolio`, `--constituents`, `--out-md`, `--out-json` | `demo/exposure_packet.md`, `demo/exposure_packet.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `policy-profile` | `--root`, `--profile`, `--exposure`, `--out-md`, `--out-json` | `demo/policy_profile.md`, `demo/policy_profile.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `policy-compare` | `--root`, `--left`, `--right`, `--out-md`, `--out-json` | `demo/policy_compare.md`, `demo/policy_compare.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `policy-gallery` | `--root`, `--out-md`, `--out-json` | `demo/policy_gallery.md`, `demo/policy_gallery.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `compare-history` | `--root`, `--current`, `--prior`, `--constituents`, `--out-md`, `--out-json` | `demo/history_comparison.md`, `demo/history_comparison.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `overlap-matrix` | `--root`, `--portfolio`, `--constituents`, `--out-md`, `--out-json` | `demo/overlap_matrix.md`, `demo/overlap_matrix.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `review-ledger` | `--root`, `--portfolio`, `--constituents`, `--threshold`, `--out-md`, `--out-json` | `demo/review_ledger.md`, `demo/review_ledger.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `fixture-doctor` | `--root`, `--portfolio`, `--constituents`, `--as-of`, `--max-source-age-days`, `--out-md`, `--out-json` | `demo/fixture_doctor.md`, `demo/fixture_doctor.json` | 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors |
| `static-dashboard` | `--root`, `--portfolio`, `--constituents`, `--out-html` | `demo/static_dashboard.html` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `case-gallery` | `--root`, `--out-md`, `--out-json` | `demo/case_gallery.md`, `demo/case_gallery.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `visual-receipt` | `--root`, `--format`, `--out` | `demo/visual_receipt.svg` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `reviewer-scorecard` | `--root`, `--out-md`, `--out-json` | `demo/reviewer_scorecard.md`, `demo/reviewer_scorecard.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `selfcheck` | `--root` | `stdout JSON` | 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors |
| `public-scan` | `--root` | `stdout JSON` | 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors |
| `release-manifest` | `--root`, `--out-md`, `--out-json` | `demo/release_manifest.md`, `demo/release_manifest.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `release-compare` | `--root`, `--left`, `--right`, `--out-md`, `--out-json` | `demo/release_compare.md`, `demo/release_compare.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `maturity-report` | `--root`, `--out-md`, `--out-json` | `demo/maturity_report.md`, `demo/maturity_report.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `bundle-export` | `--root`, `--out-dir` | `demo/bundle_export/manifest.md`, `demo/bundle_export/manifest.json`, `demo/bundle_export/artifacts/` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `asset-health` | `--root`, `--out-md`, `--out-json` | `demo/asset_health.md`, `demo/asset_health.json` | 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors |
| `artifact-catalog` | `--root`, `--out-md`, `--out-json` | `demo/artifact_catalog.md`, `demo/artifact_catalog.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `command-matrix` | `--root`, `--out-md`, `--out-json` | `demo/command_matrix.md`, `demo/command_matrix.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `release-checklist` | `--root`, `--out-md`, `--out-json` | `demo/release_checklist.md`, `demo/release_checklist.json` | 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors |
| `final-handoff` | `--root`, `--repo-url`, `--release-version`, `--out-md`, `--out-json` | `demo/final_handoff.md`, `demo/final_handoff.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `maintainer-note` | `--root`, `--out-md`, `--out-json` | `demo/maintainer_note.md`, `demo/maintainer_note.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `final-qa` | `--root`, `--baseline`, `--release-version`, `--out-md`, `--out-json` | `demo/final_qa.md`, `demo/final_qa.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `readme-snippet` | `--root`, `--out-md` | `demo/readme_snippet.md` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `public-readiness` | `--root`, `--out-md`, `--out-json` | `demo/public_readiness.md`, `demo/public_readiness.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `promotion-pack` | `--root`, `--out-md`, `--out-json` | `demo/promotion_pack.md`, `demo/promotion_pack.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `adoption-notes` | `--root`, `--out-md`, `--out-json` | `demo/adoption_notes.md`, `demo/adoption_notes.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `landing-page` | `--root`, `--out-html` | `demo/index.html` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `docs-export` | `--root`, `--out-md`, `--out-json` | `demo/cli_help.md`, `demo/cli_help.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `snapshot-ledger` | `--root`, `--out-md`, `--out-json` | `demo/snapshot_ledger.md`, `demo/snapshot_ledger.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `snapshot-compare` | `--root`, `--left`, `--right`, `--out-md`, `--out-json` | `demo/snapshot_compare.md`, `demo/snapshot_compare.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
| `review-queue` | `--root`, `--exposure`, `--fixture-doctor`, `--asset-health`, `--release-checklist`, `--out-md`, `--out-json` | `demo/review_queue.md`, `demo/review_queue.json` | 0 on success; 2 for file or validation errors handled by the CLI wrapper |
