# How the study was run and reviewed

The study ran in stages. After each stage the build agent stopped and wrote a report. Each report was reviewed, and the review's rulings were applied before the next stage. Every ruling is also logged in `DECISIONS.md` at the repo root, and every change after the first results is in `DEVIATIONS.md`.

The code was written by an AI coding agent working to `PLAN.md`. Claude (Anthropic) reviewed each stage. Omid Golchin defined the study, approved the plan and owns the decisions.

| Stage | Report | Review or ruling |
|---|---|---|
| 0. Data check | `REPORT_DATA.md` | `REVIEW_DATA_CLAUDE.md` |
| 1. First full run | `REPORT_RESULTS.md` | `REVIEW_RESULTS_CLAUDE.md` |
| 2. Checks, round 1 | `REPORT_CHECKS.md` | `REVIEW_CHECKS_CLAUDE.md`, then `RULING_A_CLAUDE.md` on the seasonal-test disagreement |
| 3. Checks, round 2 | `REPORT_CHECKS_2.md` | `REVIEW_CHECKS2_CLAUDE.md` |
| 4. Checks, round 3 | `REPORT_CHECKS_3.md` | Accepted (end of `REVIEW_CHECKS2_CLAUDE.md`) |

The reports are kept exactly as written at the time, so a few of them refer to files at the repo root that now sit in this folder.
