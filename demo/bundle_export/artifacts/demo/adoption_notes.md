# Adoption Notes

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Audience: agents reusing static outputs in a thesis ledger

Use outputs as reproducible evidence only; do not convert findings into advice, target allocations, trades, or return predictions.

## Evidence Inputs

| Path | Status | SHA-256 prefix |
| --- | --- | --- |
| `demo/exposure_packet.json` | ready | `62361eb427920547` |
| `demo/policy_profile.json` | ready | `c88964d8128f48e6` |
| `demo/review_queue.json` | ready | `38fdd89c00c31887` |
| `demo/release_compare.json` | ready | `8fcb45f4895f4948` |
| `demo/promotion_pack.json` | ready | `dea610cc655b7957` |
| `demo/snapshot_ledger.json` | ready | `2bf27982382a8103` |

## Thesis Ledger Workflow

| Step | Ledger field | Agent note |
| --- | --- | --- |
| `capture_static_inputs` | `inputs` | Record fixture filenames, generated artifact paths, and hashes before interpreting exposure rows. |
| `attach_exposure_evidence` | `evidence.exposure` | Reference exposure_packet.json and policy_profile.json as static research evidence, not as portfolio instructions. |
| `track_release_delta` | `evidence.release_delta` | Use release_compare.json or snapshot_ledger.json to describe artifact changes across runs. |
| `queue_reviewer_questions` | `review.questions` | Copy review_queue.json questions into the thesis ledger as unresolved review items. |
| `attach_promotion_evidence` | `evidence.promotion` | Use promotion_pack.json to prove public-readiness, landing page, receipt, command matrix, and scorecard coverage. |
