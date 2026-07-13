# CLI Help Export

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Version: 1.0.1
Commands exported: 34

## Top-level Help

```text
usage: fund-exposure-lookthrough [-h] [--version]
                                 {build-packet,compare-history,overlap-matrix,review-ledger,fixture-doctor,static-dashboard,case-gallery,visual-receipt,reviewer-scorecard,selfcheck,public-scan,release-manifest,release-compare,maturity-report,bundle-export,asset-health,artifact-catalog,command-matrix,release-checklist,final-handoff,maintainer-note,final-qa,readme-snippet,public-readiness,promotion-pack,adoption-notes,landing-page,docs-export,snapshot-ledger,snapshot-compare,review-queue,policy-profile,policy-compare,policy-gallery}
                                 ...

Static fund exposure look-through research CLI.

positional arguments:
  {build-packet,compare-history,overlap-matrix,review-ledger,fixture-doctor,static-dashboard,case-gallery,visual-receipt,reviewer-scorecard,selfcheck,public-scan,release-manifest,release-compare,maturity-report,bundle-export,asset-health,artifact-catalog,command-matrix,release-checklist,final-handoff,maintainer-note,final-qa,readme-snippet,public-readiness,promotion-pack,adoption-notes,landing-page,docs-export,snapshot-ledger,snapshot-compare,review-queue,policy-profile,policy-compare,policy-gallery}
    build-packet        Build a Markdown and JSON exposure packet.
    compare-history     Compare current and prior portfolio exposures.
    overlap-matrix      Build a fund constituent overlap matrix.
    review-ledger       Build a static review ledger for input warnings and
                        concentration flags.
    fixture-doctor      Validate portfolio and constituent fixtures and write
                        Markdown/JSON reports.
    static-dashboard    Build a no-JavaScript static HTML dashboard.
    case-gallery        Build a deterministic Markdown/JSON public showcase
                        gallery.
    visual-receipt      Build a deterministic SVG or HTML receipt for demo
                        artifact hashes.
    reviewer-scorecard  Map release evidence to a public maturity rubric.
    selfcheck           Check package, examples, safety text, and generated
                        artifacts.
    public-scan         Scan publishable text files for private names and
                        credentials.
    release-manifest    Build a release manifest for public review.
    release-compare     Compare two release manifests or artifact catalogs.
    maturity-report     Build a project maturity report.
    bundle-export       Copy selected demo artifacts into a deterministic
                        portable directory.
    asset-health        Summarize command coverage, artifact presence, package
                        data, and safety boundaries.
    artifact-catalog    Catalog demo artifacts with type, size, SHA-256, and
                        regeneration command.
    command-matrix      Write a Markdown/JSON matrix of CLI routes, inputs,
                        outputs, and exit-code behavior.
    release-checklist   Write a release owner checklist for tests, package,
                        wheel smoke, public scan, and no-advice boundaries.
    final-handoff       Write a Markdown/JSON release owner handoff for v1
                        stabilization.
    maintainer-note     Write deterministic maintainer evidence and next-step
                        notes.
    final-qa            Write deterministic final QA evidence for release
                        review.
    readme-snippet      Generate a concise Markdown quickstart and demo
                        snippet from current artifacts.
    public-readiness    Write a first-10-minute cold-user walkthrough in
                        Markdown and JSON.
    promotion-pack      Bundle public-readiness, landing, receipt, command
                        matrix, and scorecard evidence.
    adoption-notes      Write agent-facing workflow notes for using outputs in
                        a thesis ledger.
    landing-page        Write a no-JavaScript static HTML public landing page
                        linking demo artifacts.
    docs-export         Export CLI help and command metadata into
                        deterministic Markdown and JSON.
    snapshot-ledger     Append a deterministic artifact snapshot to a
                        JSON/Markdown ledger.
    snapshot-compare    Compare two deterministic snapshot JSON files.
    review-queue        Derive prioritized follow-up questions from generated
                        review artifacts.
    policy-profile      Apply a bundled research-only policy profile to an
                        exposure artifact.
    policy-compare      Compare two policy-profile JSON outputs.
    policy-gallery      Build Markdown/JSON policy examples for bundled
                        fixtures.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## adoption-notes

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/adoption_notes.md`, `demo/adoption_notes.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli adoption-notes --root .`

```text
usage: fund-exposure-lookthrough adoption-notes [-h] [--root ROOT]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## artifact-catalog

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/artifact_catalog.md`, `demo/artifact_catalog.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli artifact-catalog --root .`

```text
usage: fund-exposure-lookthrough artifact-catalog [-h] [--root ROOT]
                                                  [--out-md OUT_MD]
                                                  [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## asset-health

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/asset_health.md`, `demo/asset_health.json`
- Exit codes: 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli asset-health --root .`

```text
usage: fund-exposure-lookthrough asset-health [-h] [--root ROOT]
                                              [--out-md OUT_MD]
                                              [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## build-packet

- Inputs: `--root`, `--portfolio`, `--constituents`, `--out-md`, `--out-json`
- Outputs: `demo/exposure_packet.md`, `demo/exposure_packet.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli build-packet --root .`

```text
usage: fund-exposure-lookthrough build-packet [-h] [--root ROOT]
                                              [--portfolio PORTFOLIO]
                                              [--constituents CONSTITUENTS]
                                              [--out-md OUT_MD]
                                              [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --portfolio PORTFOLIO
  --constituents CONSTITUENTS
  --out-md OUT_MD
  --out-json OUT_JSON
```

## bundle-export

- Inputs: `--root`, `--out-dir`
- Outputs: `demo/bundle_export/manifest.md`, `demo/bundle_export/manifest.json`, `demo/bundle_export/artifacts/`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli bundle-export --root .`

```text
usage: fund-exposure-lookthrough bundle-export [-h] [--root ROOT]
                                               [--out-dir OUT_DIR]

options:
  -h, --help         show this help message and exit
  --root ROOT
  --out-dir OUT_DIR
```

## case-gallery

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/case_gallery.md`, `demo/case_gallery.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli case-gallery --root .`

```text
usage: fund-exposure-lookthrough case-gallery [-h] [--root ROOT]
                                              [--out-md OUT_MD]
                                              [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## command-matrix

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/command_matrix.md`, `demo/command_matrix.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli command-matrix --root .`

```text
usage: fund-exposure-lookthrough command-matrix [-h] [--root ROOT]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## compare-history

- Inputs: `--root`, `--current`, `--prior`, `--constituents`, `--out-md`, `--out-json`
- Outputs: `demo/history_comparison.md`, `demo/history_comparison.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli compare-history --root .`

```text
usage: fund-exposure-lookthrough compare-history [-h] [--root ROOT]
                                                 [--current CURRENT]
                                                 [--prior PRIOR]
                                                 [--constituents CONSTITUENTS]
                                                 [--out-md OUT_MD]
                                                 [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --current CURRENT
  --prior PRIOR
  --constituents CONSTITUENTS
  --out-md OUT_MD
  --out-json OUT_JSON
```

## docs-export

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/cli_help.md`, `demo/cli_help.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli docs-export --root .`

```text
usage: fund-exposure-lookthrough docs-export [-h] [--root ROOT]
                                             [--out-md OUT_MD]
                                             [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## final-handoff

- Inputs: `--root`, `--repo-url`, `--release-version`, `--out-md`, `--out-json`
- Outputs: `demo/final_handoff.md`, `demo/final_handoff.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli final-handoff --root . --repo-url REPO_URL_PLACEHOLDER`

```text
usage: fund-exposure-lookthrough final-handoff [-h] [--root ROOT]
                                               [--repo-url REPO_URL]
                                               [--release-version RELEASE_VERSION]
                                               [--out-md OUT_MD]
                                               [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --repo-url REPO_URL
  --release-version RELEASE_VERSION
  --out-md OUT_MD
  --out-json OUT_JSON
```

## final-qa

- Inputs: `--root`, `--baseline`, `--release-version`, `--out-md`, `--out-json`
- Outputs: `demo/final_qa.md`, `demo/final_qa.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli final-qa --root . --baseline v0.5.0`

```text
usage: fund-exposure-lookthrough final-qa [-h] [--root ROOT]
                                          [--baseline BASELINE]
                                          [--release-version RELEASE_VERSION]
                                          [--out-md OUT_MD]
                                          [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --baseline BASELINE
  --release-version RELEASE_VERSION
  --out-md OUT_MD
  --out-json OUT_JSON
```

## fixture-doctor

- Inputs: `--root`, `--portfolio`, `--constituents`, `--as-of`, `--max-source-age-days`, `--out-md`, `--out-json`
- Outputs: `demo/fixture_doctor.md`, `demo/fixture_doctor.json`
- Exit codes: 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli fixture-doctor --root .`

```text
usage: fund-exposure-lookthrough fixture-doctor [-h] [--root ROOT]
                                                [--portfolio PORTFOLIO]
                                                [--constituents CONSTITUENTS]
                                                [--as-of AS_OF]
                                                [--max-source-age-days MAX_SOURCE_AGE_DAYS]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --portfolio PORTFOLIO
  --constituents CONSTITUENTS
  --as-of AS_OF         Deterministic ISO date used for source metadata
                        freshness checks.
  --max-source-age-days MAX_SOURCE_AGE_DAYS
  --out-md OUT_MD
  --out-json OUT_JSON
```

## landing-page

- Inputs: `--root`, `--out-html`
- Outputs: `demo/index.html`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli landing-page --root .`

```text
usage: fund-exposure-lookthrough landing-page [-h] [--root ROOT]
                                              [--out-html OUT_HTML]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-html OUT_HTML
```

## maintainer-note

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/maintainer_note.md`, `demo/maintainer_note.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli maintainer-note --root .`

```text
usage: fund-exposure-lookthrough maintainer-note [-h] [--root ROOT]
                                                 [--out-md OUT_MD]
                                                 [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## maturity-report

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/maturity_report.md`, `demo/maturity_report.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli maturity-report --root .`

```text
usage: fund-exposure-lookthrough maturity-report [-h] [--root ROOT]
                                                 [--out-md OUT_MD]
                                                 [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## overlap-matrix

- Inputs: `--root`, `--portfolio`, `--constituents`, `--out-md`, `--out-json`
- Outputs: `demo/overlap_matrix.md`, `demo/overlap_matrix.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli overlap-matrix --root .`

```text
usage: fund-exposure-lookthrough overlap-matrix [-h] [--root ROOT]
                                                [--portfolio PORTFOLIO]
                                                [--constituents CONSTITUENTS]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --portfolio PORTFOLIO
  --constituents CONSTITUENTS
  --out-md OUT_MD
  --out-json OUT_JSON
```

## policy-compare

- Inputs: `--root`, `--left`, `--right`, `--out-md`, `--out-json`
- Outputs: `demo/policy_compare.md`, `demo/policy_compare.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-compare --root . --left demo/policy_profile.json --right demo/policy_profile.json`

```text
usage: fund-exposure-lookthrough policy-compare [-h] [--root ROOT]
                                                [--left LEFT] [--right RIGHT]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --left LEFT
  --right RIGHT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## policy-gallery

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/policy_gallery.md`, `demo/policy_gallery.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-gallery --root .`

```text
usage: fund-exposure-lookthrough policy-gallery [-h] [--root ROOT]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## policy-profile

- Inputs: `--root`, `--profile`, `--exposure`, `--out-md`, `--out-json`
- Outputs: `demo/policy_profile.md`, `demo/policy_profile.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli policy-profile --root .`

```text
usage: fund-exposure-lookthrough policy-profile [-h] [--root ROOT]
                                                [--profile {balanced,concentrated,conservative}]
                                                [--exposure EXPOSURE]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --profile {balanced,concentrated,conservative}
  --exposure EXPOSURE
  --out-md OUT_MD
  --out-json OUT_JSON
```

## promotion-pack

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/promotion_pack.md`, `demo/promotion_pack.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli promotion-pack --root .`

```text
usage: fund-exposure-lookthrough promotion-pack [-h] [--root ROOT]
                                                [--out-md OUT_MD]
                                                [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## public-readiness

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/public_readiness.md`, `demo/public_readiness.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli public-readiness --root .`

```text
usage: fund-exposure-lookthrough public-readiness [-h] [--root ROOT]
                                                  [--out-md OUT_MD]
                                                  [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## public-scan

- Inputs: `--root`
- Outputs: `stdout JSON`
- Exit codes: 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors
- Regeneration: `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli public-scan --root .`

```text
usage: fund-exposure-lookthrough public-scan [-h] [--root ROOT]

options:
  -h, --help   show this help message and exit
  --root ROOT
```

## readme-snippet

- Inputs: `--root`, `--out-md`
- Outputs: `demo/readme_snippet.md`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli readme-snippet --root .`

```text
usage: fund-exposure-lookthrough readme-snippet [-h] [--root ROOT]
                                                [--out-md OUT_MD]

options:
  -h, --help       show this help message and exit
  --root ROOT
  --out-md OUT_MD
```

## release-checklist

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/release_checklist.md`, `demo/release_checklist.json`
- Exit codes: 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-checklist --root .`

```text
usage: fund-exposure-lookthrough release-checklist [-h] [--root ROOT]
                                                   [--out-md OUT_MD]
                                                   [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## release-compare

- Inputs: `--root`, `--left`, `--right`, `--out-md`, `--out-json`
- Outputs: `demo/release_compare.md`, `demo/release_compare.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-compare --root . --left demo/release_manifest.json --right demo/artifact_catalog.json`

```text
usage: fund-exposure-lookthrough release-compare [-h] [--root ROOT]
                                                 [--left LEFT] [--right RIGHT]
                                                 [--out-md OUT_MD]
                                                 [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --left LEFT
  --right RIGHT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## release-manifest

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/release_manifest.md`, `demo/release_manifest.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli release-manifest --root .`

```text
usage: fund-exposure-lookthrough release-manifest [-h] [--root ROOT]
                                                  [--out-md OUT_MD]
                                                  [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## review-ledger

- Inputs: `--root`, `--portfolio`, `--constituents`, `--threshold`, `--out-md`, `--out-json`
- Outputs: `demo/review_ledger.md`, `demo/review_ledger.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli review-ledger --root .`

```text
usage: fund-exposure-lookthrough review-ledger [-h] [--root ROOT]
                                               [--portfolio PORTFOLIO]
                                               [--constituents CONSTITUENTS]
                                               [--threshold THRESHOLD]
                                               [--out-md OUT_MD]
                                               [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --portfolio PORTFOLIO
  --constituents CONSTITUENTS
  --threshold THRESHOLD
  --out-md OUT_MD
  --out-json OUT_JSON
```

## review-queue

- Inputs: `--root`, `--exposure`, `--fixture-doctor`, `--asset-health`, `--release-checklist`, `--out-md`, `--out-json`
- Outputs: `demo/review_queue.md`, `demo/review_queue.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli review-queue --root .`

```text
usage: fund-exposure-lookthrough review-queue [-h] [--root ROOT]
                                              [--exposure EXPOSURE]
                                              [--fixture-doctor FIXTURE_DOCTOR]
                                              [--asset-health ASSET_HEALTH]
                                              [--release-checklist RELEASE_CHECKLIST]
                                              [--out-md OUT_MD]
                                              [--out-json OUT_JSON]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --exposure EXPOSURE
  --fixture-doctor FIXTURE_DOCTOR
  --asset-health ASSET_HEALTH
  --release-checklist RELEASE_CHECKLIST
  --out-md OUT_MD
  --out-json OUT_JSON
```

## reviewer-scorecard

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/reviewer_scorecard.md`, `demo/reviewer_scorecard.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli reviewer-scorecard --root .`

```text
usage: fund-exposure-lookthrough reviewer-scorecard [-h] [--root ROOT]
                                                    [--out-md OUT_MD]
                                                    [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## selfcheck

- Inputs: `--root`
- Outputs: `stdout JSON`
- Exit codes: 0 when generated and checks pass; 1 when findings require review; 2 for file or validation errors
- Regeneration: `PYTHONPATH=src python -B -m fund_exposure_lookthrough.cli selfcheck --root .`

```text
usage: fund-exposure-lookthrough selfcheck [-h] [--root ROOT]

options:
  -h, --help   show this help message and exit
  --root ROOT
```

## snapshot-compare

- Inputs: `--root`, `--left`, `--right`, `--out-md`, `--out-json`
- Outputs: `demo/snapshot_compare.md`, `demo/snapshot_compare.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli snapshot-compare --root . --left demo/snapshot_ledger.json --right demo/snapshot_ledger.json`

```text
usage: fund-exposure-lookthrough snapshot-compare [-h] [--root ROOT]
                                                  [--left LEFT]
                                                  [--right RIGHT]
                                                  [--out-md OUT_MD]
                                                  [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --left LEFT
  --right RIGHT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## snapshot-ledger

- Inputs: `--root`, `--out-md`, `--out-json`
- Outputs: `demo/snapshot_ledger.md`, `demo/snapshot_ledger.json`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli snapshot-ledger --root .`

```text
usage: fund-exposure-lookthrough snapshot-ledger [-h] [--root ROOT]
                                                 [--out-md OUT_MD]
                                                 [--out-json OUT_JSON]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --out-md OUT_MD
  --out-json OUT_JSON
```

## static-dashboard

- Inputs: `--root`, `--portfolio`, `--constituents`, `--out-html`
- Outputs: `demo/static_dashboard.html`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli static-dashboard --root .`

```text
usage: fund-exposure-lookthrough static-dashboard [-h] [--root ROOT]
                                                  [--portfolio PORTFOLIO]
                                                  [--constituents CONSTITUENTS]
                                                  [--out-html OUT_HTML]

options:
  -h, --help            show this help message and exit
  --root ROOT
  --portfolio PORTFOLIO
  --constituents CONSTITUENTS
  --out-html OUT_HTML
```

## visual-receipt

- Inputs: `--root`, `--format`, `--out`
- Outputs: `demo/visual_receipt.svg`
- Exit codes: 0 on success; 2 for file or validation errors handled by the CLI wrapper
- Regeneration: `PYTHONPATH=src python -m fund_exposure_lookthrough.cli visual-receipt --root .`

```text
usage: fund-exposure-lookthrough visual-receipt [-h] [--root ROOT]
                                                [--format {svg,html}]
                                                [--out OUT]

options:
  -h, --help           show this help message and exit
  --root ROOT
  --format {svg,html}
  --out OUT
```
