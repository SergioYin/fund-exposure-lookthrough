# Reviewer Scorecard

Research use only. This static report is not investment advice, does not recommend buys, sells, holds, target allocations, or trades, and uses only user-supplied fixture data.

Overall score: 12 / 12

| Rubric item | Score | Evidence |
| --- | ---: | --- |
| Zero runtime dependencies | 2 / 2 | pyproject.toml |
| Packaged example fixtures | 2 / 2 | examples/current_portfolio.csv, examples/prior_portfolio.csv, examples/direct_wrapper_portfolio.csv, src/fund_exposure_lookthrough/data/direct_wrapper_constituents.csv |
| Deterministic Markdown and JSON demos | 2 / 2 | demo/exposure_packet.md, demo/exposure_packet.json, demo/case_gallery.md, demo/case_gallery.json |
| Visual public receipt | 1 / 1 | src/fund_exposure_lookthrough/cli.py, src/fund_exposure_lookthrough/render.py |
| Fixture review and public scan | 2 / 2 | src/fund_exposure_lookthrough/doctor.py, tests/test_public_safety.py |
| Documentation and release notes | 1 / 1 | README.md, CHANGELOG.md, RELEASE_NOTES.md, skills/agent/fund-exposure-lookthrough/SKILL.md |
| No workflow automation | 1 / 1 | no .github/workflows directory |
| Static safety boundary | 1 / 1 | README.md, render.DISCLAIMER |
