# Review of REPORT_DATA (S04, Northern Virginia load forecasting): Claude, 2026-11-17

To: Ember. Verdict: **Step 0 passed. Build the notebook.** First apply the five rulings below to PLAN.md, log each in DECISIONS.md and commit, all before any model sees the test period.

The data check was thorough: you confirmed the grid, cross-checked `core_` against `out_`, counted the flags and checked PJM's terms. Leaving PJM out because of its ban on republishing by non-members was the right call.

## Rulings

### 1. Missing and flagged hours

Neither series is used as it is. Inputs and scoring get separate rules.

**Scoring targets.** Score only reported values on hours that carry no flag.
- A target hour that is missing, `anomalous_region` or `global_outlier` is dropped from every method's score.
- The dropped hours are the same for every method.
- Report how many target hours were dropped in each test half. This covers the two fall-back days in the test period, November 2024 and November 2025.

**Model inputs** (training history and forecast context). Use the reported values, with one change: replace every flagged or missing hour by the value 168 hours earlier. If that hour is also flagged, step back another week.
- Apply this once to the whole series, so every method sees exactly the same input.
- The two `global_outlier` hours on 2021-10-19 are flagged, so this rule covers them.

**Why not the PUDL imputed series.** PUDL imputes each year as a whole: it compares all the days of the year and draws on other regions. An imputed hour just before a forecast origin can therefore carry information from later in the same year. That is small at 0.5% of hours, but it is look-ahead in a backtest, and a fill that only looks backwards removes it.

Keep the imputed column in the raw extract for reference. It is not used.

### 2. Training start

Training history starts **2019-01-01**, as you recommend. 2018 is excluded: 39% of its hours are missing, including one 71-day hole.

### 3. Pin the data version

Use the stable PUDL release **v2026.11.0** (2026-11-10), not the nightly build, so the study can be re-run on identical data.
- If the stable release's DOM series ends before 2026-10-31 04:00 UTC, keep the 2026-11-16 nightly instead and say so.
- Either way, record in DATA_SOURCES.md:
  - the release (with its DOI if it has one) or the nightly date;
  - the file hashes;
  - a hash of the DOM extract.
- Check that reported values agree with the nightly where the two overlap.

### 4. MASE scale

Use a single fixed scale for all methods, origins and halves: the mean absolute error of the lag-168 seasonal naive forecast over the training history (2019-01-01 to the start of the test period). It must be computed with the same flagged-hour rules as above.

With a fixed scale, a difference in MASE between two methods is a difference in error, not in scaling.

### 5. Test period on record

The test period is **2024-11-01 to 2026-10-31**, split into two halves:
- November 2024 – October 2025;
- November 2025 – October 2026.

Forecast origins are weekly at 00:00 US Eastern. The last origin is the latest one whose full 168-hour horizon has data.

**Disclosure for DECISIONS.md.** The Step 0 growth table and plot covered the test years. No method, setting or ruling was chosen from them: PLAN.md fixed the design beforehand, and the rulings above concern data handling only. The README's "What this does not show" repeats this in one line.

## Kaggle runs

Running the notebook through the Kaggle API is fine. These conditions apply:
- **Kernels stay private.** Set `"is_private": true` in `kernel-metadata.json`, and keep any dataset you upload private too. Nothing becomes public without Omid's approval.
- **Credentials.** No Kaggle, EIA or Hugging Face credentials go in the repo, the notebook or its outputs.
- **Record per run:**
  - kernel version;
  - accelerator type;
  - runtime;
  - GPU hours used against the weekly quota.
- **Results.** Pull them back into `results/` (CSV plus PNG), so the review can read them from GitHub.

The second stop point is unchanged: stop after the first full run and send `REPORT_RESULTS.md`.

## Priority

S03 comes first whenever its re-pilot needs you. This study fills the gaps.
