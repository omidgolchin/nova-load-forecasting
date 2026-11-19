# PLAN — Northern Virginia load forecasting study

Working title: "Can forecasting models keep up with data-center-driven
demand? Hourly electricity load in the Dominion Energy zone."

Written and committed 2026-11-17, before any model sees the test period.
Changes after this commit go in DEVIATIONS.md. Brief: 2026-11-17;
approved by Omid, 2026-11-17. Amended 2026-11-17 with the five rulings
of the Step 0 review (DECISIONS #4–#8), still before any modelling;
Omid approved applying them the same day.

## Question

How well do forecasting methods track hourly demand in the Dominion
Energy zone, which has grown with the Northern Virginia data-center
cluster? Do any hold up better in the most recent, fastest-growing
period, and are their prediction intervals honest? Data centers are not
metered separately: the study can show demand growth and forecast
tracking, not how much of the growth is data centers.

## Data (subject to the Step 0 check, REPORT_DATA.md)

- Demand: EIA Form 930 hourly demand, PJM Dominion subregion (DOM),
  from the pinned PUDL release (Step 0 review, ruling 3): the stable
  release v2026.11.0 (2026-11-10); if its DOM series ends before
  2026-10-31 04:00 UTC, the 2026-11-16 nightly is kept instead and
  DATA_SOURCES.md says so. Release identity, file hashes and a hash of
  the DOM extract are recorded in DATA_SOURCES.md, and reported values
  are checked against the nightly where the two overlap. Fallbacks, in
  order: PJM Data Miner hourly metered load for DOM (terms recorded
  first); PJM total hourly demand from EIA-930 (change stated here via
  DEVIATIONS.md).
- Flagged and missing hours (Step 0 review, ruling 1). PUDL's imputed
  series is not used: it imputes a year as a whole, drawing on later
  days and other regions, so an imputed hour just before a forecast
  origin would leak future information into the backtest. The imputed
  column stays in the raw extract for reference only.
  - Scoring targets: only reported values on hours carrying no flag.
    A target hour that is missing, `anomalous_region` or
    `global_outlier` is dropped from every method's score; the dropped
    hours are the same for every method, and the count dropped is
    reported for each test half.
  - Model inputs (training history and forecast context): reported
    values, with every flagged or missing hour replaced by the value
    168 hours earlier, stepping back another week if that hour is also
    flagged. Applied once to the whole series, so every method sees
    exactly the same input. This covers the two corrupt
    `global_outlier` hours on 2021-10-19.
- Weather: hourly 2 m temperature from Open-Meteo's historical API
  (ERA5-based) at three points — Ashburn/Loudoun, Richmond, Norfolk —
  averaged with fixed weights 1/3 each.
- EIA timestamps are UTC; convert to US Eastern for calendar features.

## Design

- Target: hourly demand (MW) for the chosen series.
- Training history starts 2019-01-01 (Step 0 review, ruling 2); 2018
  is excluded (39% of its hours missing, including one 71-day hole).
- Test period (Step 0 review, ruling 5): 2024-11-01 to 2026-10-31,
  split into two halves reported separately — November 2024 to
  October 2025, and November 2025 to October 2026.
- Forecast origins: one every 7 days across the test period at 00:00
  Eastern (~104 origins); the last origin is the latest one whose
  full 168-hour horizon has data. Horizons: 24 h and 168 h.
- Refitting: classic models and the LSTM refit/retrain every 13 weeks on
  all data before the refit date (expanding window). No model ever sees
  data after its forecast origin.
- Weather in models: two SARIMAX variants — with observed temperature
  over the horizon ("oracle weather", an upper bound, labelled as such)
  and without future weather. Optional if time allows: Open-Meteo
  historical forecast archive.

## Methods (same forecast dates, horizons and scoring code for all)

- Seasonal naive (same hour last week) — the baseline every method is
  compared with. Naive (same hour yesterday) — second baseline, 24 h.
- SARIMAX: daily seasonality (s = 24), Fourier terms for weekly and
  annual cycles, heating/cooling degree-hours from temperature, holiday
  dummies; order by AIC on training data only; model prediction
  intervals.
- LSTM: small (1–2 layers); inputs past 168 h of load, calendar
  features, temperature as in the matching SARIMAX variant; 3 seeds,
  spread reported; quantile loss (10/50/90) for intervals.
- Chronos-Bolt (small or base): zero-shot, context up to the model's
  limit (recorded); quantile outputs give intervals.
- TimesFM: zero-shot; same context length as Chronos where possible;
  version and context recorded.
- General LLM (reduced test, stated plainly in results): 26 origins
  (every 4th), 24 h horizon only, past 168 h as scaled text
  (LLMTime-style); 5 samples per origin, interval = 10th–90th percentile
  of samples. Default model: a small open instruction model (~7–8B,
  4-bit) on the Kaggle GPU; an API model only if the local one cannot
  produce parseable forecasts (≤ $3, recorded). Prompt, model, decoding
  settings and the unparseable share are recorded.
- Foundation models and the LLM get the same context window and forecast
  dates as each other. Classic models may use their longer training
  history; each method's input history is reported in the table.

## Scores

- Point: MASE with a single fixed scale for all methods, origins and
  halves (Step 0 review, ruling 4): the mean absolute error of the
  lag-168 seasonal naive forecast over the training history
  (2019-01-01 to the start of the test period), computed under the
  same flagged-hour rules as the scores. Also MAPE and error at the
  daily peak hour.
- Intervals: coverage of the 80% intervals and the interval (Winkler)
  score, for every method that gives intervals.
- Uncertainty: per method vs seasonal naive, the paired difference in
  MASE across origins with a 95% block-bootstrap interval (blocks of 4
  origins), per test half and per horizon.
- No tuning on the test period. Anything changed after seeing test
  results goes in DEVIATIONS.md and results show both versions.

## Outputs

- Main chart: MASE by method with 95% intervals, split by test half,
  24 h horizon; second panel/chart for 168 h.
- Second chart: interval coverage by method against the 80% target.
- Table: method × horizon × test half — MASE, MAPE, peak-hour error,
  coverage, input history, compute time on Kaggle.
- README: question, data and licences, design, results in plain words,
  and "What this does not show" (one zone; oracle weather in one
  SARIMAX variant; the LLM's reduced test; data-center load not
  separated; the Step 0 growth table covered the test years, but no
  method, setting or ruling was chosen from it — the design was fixed
  beforehand and the Step 0 rulings concern data handling only).
- Notebook outputs saved to results/ (CSV + PNG) for review from GitHub.
- One notebook: notebooks/nova_load_backtest.ipynb, runs end to end on
  Kaggle's free tier (CPU classics, GPU LSTM/foundation/LLM).

## Stop points

1. After Step 0: REPORT_DATA.md for review before any modelling.
2. After the first full run: REPORT_RESULTS.md (table, charts, runtimes,
   anything unexpected; no interpretation beyond the numbers).

## Guardrails

Never publish, post or make the repo public; Omid decides after
review. Omid is the named author. Never commit
API keys. Verify every reference before citing it. When unsure, pick the
option that makes the claim smaller or the comparison fairer, log it in
DECISIONS.md, and ask for review. Budget: $0 compute; ≤ $3 optional API.
Kaggle runs (approved in the Step 0 review): kernels stay private
(`"is_private": true` in kernel-metadata.json) and any uploaded dataset
stays private too; no Kaggle, EIA or Hugging Face credentials go in the
repo, the notebook or its outputs; every run records its kernel
version, accelerator type, runtime and GPU hours used against the
weekly quota; results are pulled back into results/ (CSV plus PNG).
