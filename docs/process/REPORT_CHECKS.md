# S04 — Checks on the first full run (Claude's review, 2026-11-18)

Numbers only, as in REPORT_RESULTS.md. The review's provisional
reading stands or falls on these checks; conclusions are Claude's
step. Nothing was tuned on the test period; no method was refit or
re-selected except where a check explicitly requires it (checks 3
and 4), and those runs are labelled.

## Check 1 — SARIMAX exogenous inputs

From `exog_rows()` in notebooks/nova_load_backtest.ipynb, the
SARIMAX exogenous matrix has 13 columns, in this order:

| # | Column(s) | Count |
|---|---|---|
| 1 | Weekly Fourier terms, period 168 h: sin/cos for k = 1, 2, 3 | 6 |
| 2 | Annual Fourier terms, day-of-year fraction: sin/cos for k = 1, 2 | 4 |
| 3 | Heating degree-hours, max(0, 18.3 − T) | 1 |
| 4 | Cooling degree-hours, max(0, T − 18.3) | 1 |
| 5 | US federal holiday dummy (actual calendar dates, Juneteenth from 2021) | 1 |

This matches PLAN.md exactly ("Fourier terms for weekly and
annual cycles, heating/cooling degree-hours from temperature,
holiday dummies"). History rows always use observed temperature;
the two variants differ only in the horizon temperature (observed
for oracle; the temperature 168 h earlier for no-future). The
weekly and weather terms the review asked about are present and
are used at every fit and forecast.

## Check 2 — Identity check: SARIMAX no-future vs seasonal naive

Computed from results/forecasts_long.csv (17,472 SARIMAX
no-future forecast rows):

- Rows exactly equal to the seasonal-naive forecast: **0 of
  17,472 (0.0%)** — overall, in half 1, in half 2, at steps ≤ 24
  and at steps ≤ 168. Rows within 1 MW of the seasonal-naive
  forecast: 5 of 17,472 (0.03%). Mean absolute difference between
  the two forecasts: 1,489 MW.
- The half-1 168 h MASE values are 1.162445 (SARIMAX no-future)
  and 1.162354 (seasonal naive): equal at three decimals,
  different at the fourth.
- Code inspection: the SARIMAX cell produces forecasts only from
  `applied.get_forecast(...)` on a fitted SARIMAX model; the
  seasonal-naive forecasts are produced only in the separate
  baselines cell. There is no code path that falls back to
  seasonal naive, and no exception handler around the SARIMAX
  forecasts that substitutes another method (a failed method is
  recorded as failed by `run_method`, with no substitute output).

## Check 3 — Convergence of the SARIMAX refits

No fit objects were saved from the first run, so the four refits
of the resume kernel (origins 52, 65, 78, 91 — the segment whose
log carries the warnings) were replicated exactly on a CPU
kernel: same order (2,1,2)×(1,1,1,24), same expanding windows,
low_memory=True, concentrate_scale=True, warm-start chain cold
at origin 52, warnings captured per fit, `mle_retvals['converged']`
recorded. Results (results/sarimax_convergence.csv):

| Refit origin | Converged | Fit time (s) | Warnings |
|---|---|---|---|
| 52 | **No** | 6,356.6 | 1 × ConvergenceWarning |
| 65 | Yes | 3,812.7 | 0 |
| 78 | Yes | 3,785.2 | 0 |
| 91 | Yes | 4,072.4 | 0 |

The resume kernel's log contains two ConvergenceWarning lines,
199 characters apart, both immediately before "sarimax refit at
origin 52 done": they are the same warning from the origin-52
fit, printed twice by the notebook runner (once in the cell's
stderr stream, once in its echo). Exactly one refit failed to
converge — origin 52, the first resume refit (cold start, largest
window fitted to that point in the resume segment). The v4
segment's refits (origins 0–39) are not implicated: no warning
was reported from that log.

Refit of origin 52 with maxiter raised to 500 (same settings and
warm start): **converged**. Its 13-origin block (origins 52–64),
recomputed from the maxiter fit, against the published block
(results/sarimax_block_mase_maxiter.csv):

| Variant | Horizon | Block MASE, original fit | Block MASE, maxiter-500 fit |
|---|---|---|---|
| SARIMAX oracle | 24 | 0.5889 | 0.5891 |
| SARIMAX oracle | 168 | 1.3069 | 1.3071 |
| SARIMAX no-future | 24 | 0.6430 | 0.6435 |
| SARIMAX no-future | 168 | 1.3638 | 1.3643 |

The changes are +0.0002 to +0.0005 MASE. Interval coverage on
the block's applied origins (53–64) is unchanged to three
decimals (e.g. oracle 24 h: 0.7188 both; no-future 168 h:
0.7331 both). The maxiter fit's own-origin (52) interval bounds
are NaN, the known low_memory artifact of DECISIONS #13, so
block coverage is compared on the applied origins only.

## Check 4 — Differencing orders

The first run's AIC table did mix differencing orders (six
candidates with D = 1 and d ∈ {0, 1}, one with D = 0, one with
P = 0 at D = 1), so the review's objection is correct as stated.
Tests run on training data only — the order-selection window
2022-11-01 → 2024-11-01, filled input series, n = 17,544:

| Test | Question | Statistic | Verdict |
|---|---|---|---|
| KPSS (const, auto lags) on the seasonally differenced series (1−B²⁴)y | d, given D = 1 | 0.0098, p ≥ 0.10 (5% crit 0.463) | Stationarity not rejected → d = 0 |
| ADF (BIC lags) on (1−B²⁴)y | d, given D = 1 | −24.4, p ≈ 0 | No unit root → agrees, d = 0 |
| Canova–Hansen (period 24) | D | 5.075 vs 5% crit 5.099 (m = 24) | Seasonal stability not rejected → D = 0, marginally |
| OCSB (period 24) | D | decision statistic returns D = 0 | D = 0 |

Supporting detail: KPSS on the raw level series rejects
stationarity (2.140, p = 0.01), as expected for a trending,
seasonal series; after removing deterministic hour-of-day means
and a linear trend, KPSS does not reject (0.330, p ≥ 0.10) and
ADF rejects a unit root (−8.24, p ≈ 1e-13).

**Outcome (the review's second branch): the tests do not support
d = 1 and D = 1.** The first full run therefore stands as the
pre-registered result, unchanged. The test-supported orders
(d = 0, D = 0) are run once as a labelled post-hoc sensitivity
(DEVIATIONS.md, DECISIONS #18):

Selection within (d = 0, D = 0) on the same training window
(AIC; results/sarimax_alt_selection.csv): (1,0,1)(1,0,1,24)
249,047.8; (2,0,1)(1,0,1,24) 252,162.0; (1,0,2)(1,0,1,24)
254,327.7; **(2,0,2)(1,0,1,24) 244,368.8 — selected**;
(2,0,1)(0,0,1,24) 290,822.8. (These AICs are on the undifferenced
series and are not compared with the first run's table.)

Both versions, same backtest and scoring (sensitivity forecasts:
results/forecasts_sensitivity.csv; scores:
results/scores_sensitivity.csv):

| Variant | Horizon | Half | MASE, pre-registered (2,1,2)×(1,1,1,24) | MASE, sensitivity (2,0,2)×(1,0,1,24) | Cov80, sensitivity |
|---|---|---|---|---|---|
| Oracle | 24 | 1 | 0.602 | 0.527 | 0.855 |
| Oracle | 24 | 2 | 0.484 | 0.566 | 0.847 |
| Oracle | 168 | 1 | 1.115 | 1.054 | 0.774 |
| Oracle | 168 | 2 | 1.202 | 1.092 | 0.773 |
| No-future | 24 | 1 | 0.626 | 0.739 | 0.686 |
| No-future | 24 | 2 | 0.534 | 0.845 | 0.682 |
| No-future | 168 | 1 | 1.162 | 1.239 | 0.687 |
| No-future | 168 | 2 | 1.240 | 1.291 | 0.690 |

## Check 5 — Paired differences for the fair comparisons

Computed from results/forecasts_long.csv with the main run's
block bootstrap (blocks of 4 origins, B = 2000, seed 20261117);
per-origin MASE differences on origins scored for both methods.
Full table: results/scores_paired_fair.csv. Sanity check: the
same code reproduces the published SARIMAX no-future − seasonal
naive differences at 168 h exactly (+0.000 [−0.118, +0.115] and
+0.003 [−0.123, +0.137]).

| Comparison | Horizon | Half | Diff [95% CI] | n |
|---|---|---|---|---|
| TimesFM − SARIMAX no-future | 24 | 1 | −0.153 [−0.201, −0.113] | 53 |
| TimesFM − SARIMAX no-future | 24 | 2 | −0.052 [−0.089, −0.016] | 51 |
| TimesFM − SARIMAX no-future | 168 | 1 | −0.269 [−0.423, −0.122] | 53 |
| TimesFM − SARIMAX no-future | 168 | 2 | −0.315 [−0.472, −0.150] | 51 |
| Chronos-Bolt − SARIMAX no-future | 24 | 1 | −0.177 [−0.229, −0.123] | 53 |
| Chronos-Bolt − SARIMAX no-future | 24 | 2 | +0.001 [−0.052, +0.045] | 51 |
| Chronos-Bolt − SARIMAX no-future | 168 | 1 | −0.213 [−0.311, −0.114] | 53 |
| Chronos-Bolt − SARIMAX no-future | 168 | 2 | −0.223 [−0.376, −0.073] | 51 |
| TimesFM − Chronos-Bolt | 24 | 1 | +0.024 [−0.020, +0.068] | 53 |
| TimesFM − Chronos-Bolt | 24 | 2 | −0.053 [−0.112, +0.004] | 51 |
| TimesFM − Chronos-Bolt | 168 | 1 | −0.055 [−0.142, +0.040] | 53 |
| TimesFM − Chronos-Bolt | 168 | 2 | −0.092 [−0.171, −0.012] | 51 |
| LSTM − naive (lag 24) | 24 | 1 | −0.065 [−0.192, +0.070] | 53 |
| LSTM − naive (lag 24) | 24 | 2 | +0.114 [−0.093, +0.369] | 51 |

## Check 6 — Pretraining overlap

Recorded in DATA_SOURCES.md ("Foundation models — release dates
and pretraining corpora"), from the sources, accessed 2026-11-18:

- **TimesFM 2.5** — released 2025-09-15 (google-research/timesfm
  README). No 2.5-specific corpus list is published; the
  published corpus description is the TimesFM paper's (Das et
  al., ICML 2024): ~100B real-world time points (Google Trends,
  Wikipedia page views, public benchmark collections) plus
  synthetic series. The release date falls inside half 1 and
  before half 2, so pretraining could in principle include
  public series from half 1's window; half 2 is the clean
  comparison.
- **Chronos-Bolt** — public by 2024-12-02 (AWS Machine Learning
  Blog); trained on nearly 100 billion observations. Corpus per
  Ansari et al. (2024): ~84B tokens from 28 published public
  datasets (~890,000 series; energy, transport, healthcare,
  retail, web, weather, finance) plus KernelSynth synthetic
  series and TSMixup. The published list contains no EIA-930 or
  PJM/Dominion series, and the corpus predates the test period
  (assembled for a March 2024 paper).

## Check 7 — LLM interval coverage, expected vs observed

The LLM arm's interval is the range of 5 samples per origin. For
5 iid draws from a perfectly calibrated predictive distribution,
the expected coverage of the sample range is (5 − 1)/(5 + 1) =
0.667, not the 0.80 nominal level of the other methods'
intervals. Against that corrected benchmark:

| Half | Expected (perfect calibration, n = 5) | Observed |
|---|---|---|
| 1 | 0.667 | 0.381 |
| 2 | 0.667 | 0.406 |

## Check 8 — Compute rule

Recorded as DECISIONS #17: SARIMAX runs on Kaggle CPU kernels
from now on; GPU quota is reserved for the neural models. The
check-3 refits and the check-4 sensitivity in this round ran on
a CPU kernel; the 2048 h variant ran on GPU (foundation models).

## Variant — foundation models at 2048 h context

Chronos-Bolt base and TimesFM 2.5-200M rerun with 2048 h of
context (was 168 h), same 104 origins, same scoring (reported
unflagged targets only, same dropped hours, fixed MASE scale
1,329.73 MW, same quantile interval construction: Chronos
q0.1/q0.5/q0.9, TimesFM continuous quantile head). Full table:
results/scores_context2048.csv; forecasts:
results/forecasts_context2048.csv (34,944 rows, 34,702 scored).

| Method | Horizon | Half | MASE 168 h | MASE 2048 h | Cov80 168 h | Cov80 2048 h |
|---|---|---|---|---|---|---|
| Chronos-Bolt | 24 | 1 | 0.448 | 0.456 | 0.790 | 0.777 |
| Chronos-Bolt | 24 | 2 | 0.535 | 0.442 | 0.765 | 0.796 |
| Chronos-Bolt | 168 | 1 | 0.949 | 0.904 | 0.594 | 0.627 |
| Chronos-Bolt | 168 | 2 | 1.016 | 0.921 | 0.640 | 0.684 |
| TimesFM | 24 | 1 | 0.472 | 0.535 | 0.835 | 0.774 |
| TimesFM | 24 | 2 | 0.482 | 0.509 | 0.842 | 0.834 |
| TimesFM | 168 | 1 | 0.894 | 0.892 | 0.748 | 0.725 |
| TimesFM | 168 | 2 | 0.925 | 0.942 | 0.774 | 0.750 |

## Run records

All kernels private; no credentials in any kernel or output.
Spend: $0.00.

| Kernel | Version | Accelerator | What | Runtime |
|---|---|---|---|---|
| nova-load-context-2048 | v1 | Tesla T4 | failed at the series-construction cell (NameError: MODE not defined — the trimmed config cell omitted a variable the reused study cell needs) | ≈ 600 s, error |
| nova-load-context-2048 | v2 | Tesla T4 | Chronos-Bolt + TimesFM at 2048 h context, complete (model time: Chronos 53.9 s, TimesFM 22.2 s) | 165.6 s execution, complete |
| nova-load-checks-cpu | v1 | CPU | failed with the same NameError before any fitting | ≈ 600 s, error |
| nova-load-checks-cpu | v2 | CPU | checks 3 + 4 sensitivity, complete (check-3 fits 18,028 s of it) | 29,933 s, complete |

Total Kaggle time for this round: ≈ 8.7 h (GPU ≈ 0.2 h; CPU
≈ 8.5 h), free tier.

The v1 failures were in the checks harness, not the study code:
the reused data-prep cells are verbatim from the study notebook,
and the fix was one line in the harness config cell.
