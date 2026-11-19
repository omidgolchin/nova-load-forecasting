# S04 — Checks round 2 (Claude's review of REPORT_CHECKS, 2026-11-18)

Numbers only, as in REPORT_CHECKS.md. Items A–D of
REVIEW_CHECKS_CLAUDE.md, plus the ruling on A
(RULING_A_CLAUDE.md). Nothing was tuned on the test period; the
pre-registered run is unchanged everywhere. Item B was committed
with DECISIONS #23, item C with #24, item D with #25; item A's
tests and judgement call are DECISIONS #22, the ruling and the
seasonal-strength values #26, and the completed backtest #27.

## Item A — Differencing tests on the regression residuals

Procedure as prescribed in the review: OLS of load on the 13
exogenous columns (the SARIMAX design of REPORT_CHECKS check 1),
order-selection window 2022-11-01 → 2024-11-01, filled input
series, n = 17,544. OLS R² = 0.769, residual sd 1,132 MW. D is
decided first, then d on the series differenced by that D.

Before the residuals were tested, the pipeline reproduced round
1's raw-series numbers exactly (KPSS on (1−B²⁴)y: 0.0098;
Canova–Hansen on the raw series: 5.075 against the 5% critical
value 5.099; OCSB: D = 0), so the data and implementations match
round 1.

| Test | Series | Statistic | Verdict |
|---|---|---|---|
| Canova–Hansen (m = 24) | OLS residuals | 8.759 vs 5% crit 5.099 | D = 1 |
| OCSB (m = 24) | OLS residuals | decision statistic returns D = 0 | D = 0 |
| Canova–Hansen (m = 24) | residuals, full training window | 10.654 vs 5.099 | D = 1 |
| OCSB (m = 24) | residuals, full training window | returns D = 0 | D = 0 |
| KPSS (const, auto lags) | residuals seasonally differenced (D = 1 branch) | 0.0033, p ≥ 0.10 | d = 0 |
| ADF | OLS residuals | −11.5, p ≈ 0 | agrees, d = 0 |

**The two D tests disagree.** On the D = 0 branch the d tests
also contradict each other (KPSS on the undifferenced residuals
13.25, p = 0.01, against ADF −11.5), so d is only coherent under
D = 1. The judgement call recorded in DECISIONS #22 followed
Canova–Hansen — the primary test in round 1, its statistic
reported against its critical value, with OCSB as corroboration —
giving (d = 0, D = 1). Had OCSB been followed instead, the order
would have been (d = 1, D = 0).

**Claude's ruling (RULING_A_CLAUDE.md, DECISIONS #26): keep
(d = 0, D = 1)** as the one post-hoc sensitivity. His grounds:
the instruction named both tests with no tie-break, so the gap
is his; the residuals still carry most of the daily cycle (no
regressor has a 24 h period), so a lag-24 seasonal difference is
what makes the errors plausibly stationary; and the d step is
coherent only after that difference.

**Seasonal strength**, reported beside the test results as the
ruling asked (Wang–Smith–Hyndman strength from an STL
decomposition of the residuals at period 24, periodic seasonal
window, statsmodels): **0.595** on the order-selection window,
**0.627** on the full training window. Both are below the
forecast package's 0.64 threshold, so the package's current
default test would have given D = 0, siding with OCSB. The
ruling pre-committed to standing whatever the strength showed;
all three values stand side by side here and in DEVIATIONS.md.

### The (d = 0, D = 1) sensitivity backtest

Selection by AIC within (0, 1) on the same training window
(results/sarimax_alt2_selection.csv):

| Order | Seasonal order | AIC |
|---|---|---|
| (1, 0, 1) | (1, 1, 1, 24) | 224,679.2 |
| (2, 0, 1) | (1, 1, 1, 24) | 220,793.7 |
| (1, 0, 2) | (1, 1, 1, 24) | 221,120.5 |
| **(2, 0, 2)** | **(1, 1, 1, 24)** | **220,663.7 — selected** |
| (2, 0, 1) | (0, 1, 1, 24) | 221,440.3 |

Same backtest as the pre-registered run: 104 origins, same refit
schedule and warm-start chain, same exog, same scoring (reported
unflagged targets only; dropped target hours 98 of 8,903 in
half 1 and 23 of 8,567 in half 2; fixed MASE scale 1,329.73 MW).
Run on the private CPU kernel nova-load-checks2-cpu
(DECISIONS #17), 16,485 s. Forecasts:
results/forecasts_sensitivity2.csv (34,944 rows) and
results/forecasts_sensitivity2_scored.csv; scores:
results/scores_sensitivity2.csv; run record:
results/checks_run_record.json; kernel log:
results/checks2_kernel_log.txt.

| Variant | Horizon | Half | MASE, pre-registered (2,1,2)×(1,1,1,24) | MASE, sensitivity (2,0,2)×(1,1,1,24) | Cov80, sensitivity |
|---|---|---|---|---|---|
| Oracle | 24 | 1 | 0.602 | 0.479 | 0.781 |
| Oracle | 24 | 2 | 0.484 | 0.484 | 0.836 |
| Oracle | 168 | 1 | 1.115 | 0.799 | 0.709 |
| Oracle | 168 | 2 | 1.202 | 0.841 | 0.750 |
| No-future | 24 | 1 | 0.626 | 0.546 | 0.700 |
| No-future | 24 | 2 | 0.534 | 0.552 | 0.777 |
| No-future | 168 | 1 | 1.162 | 0.872 | 0.680 |
| No-future | 168 | 2 | 1.240 | 0.902 | 0.723 |

Reference: seasonal naive at 168 h scores 1.162 / 1.236 — the
pre-registered no-future order is indistinguishable from it
(REPORT_CHECKS check 5: +0.000 [−0.118, +0.115] and +0.003
[−0.123, +0.137]); the sensitivity order scores 0.872 / 0.902 at
the same horizon. At 24 h the sensitivity is better than the
pre-registered order in half 1 (no-future 0.546 vs 0.626; oracle
0.479 vs 0.602) and level with it in half 2 (0.552 vs 0.534;
0.484 vs 0.484). The pre-registered run remains the headline;
this is the one labelled post-hoc sensitivity the write-up
reports (DEVIATIONS.md), replacing the superseded (0, 0) one.

Convergence note: each of the five AIC selection fits emitted
one ConvergenceWarning (each printed twice in the kernel log,
the same double-printing as round 1). None of the eight
backtest refits (origins 0, 13, 26, 39, 52, 65, 78, 91) emitted
one. The warning on the selected order's selection fit is
recorded here for completeness; no refit behind any forecast
above carries it.

## Item B — DATA_SOURCES.md corrections

Committed in 32307e4 (DECISIONS #23). Two corrections to
REPORT_CHECKS check 6:

- **TimesFM 2.5** — the model card does list its pretraining
  sources: GiftEvalPretrain (the GIFT-Eval pretraining set,
  arXiv 2410.10393); Wikimedia Pageviews, cutoff November 2023;
  Google Trends top queries to end-2022; synthetic and augmented
  data. Every documented source predates the test period. Half 2
  stays the strictly clean comparison, because the model was
  released inside half 1 and the list is high-level.
- **Chronos-Bolt** — the ~84B observations / 28 datasets figure
  belongs to the original Chronos paper (Ansari et al. 2024),
  not to Bolt. Bolt's own card says "nearly 100 billion time
  series observations" and does not name the corpus. The corpus
  was fixed before the 2024-12-02 release, so at most the first
  month of half 1 could overlap, with no evidence it did.

## Item C — Context actually received in the 2048 h variant

No re-run was needed; no variant number changes (DECISIONS #24).
The variant kernel's source compiled TimesFM with
ForecastConfig(max_context=2048, max_horizon=168,
normalize_inputs=True, use_continuous_quantile_head=True,
fix_quantile_crossing=True) and passed 2048-length inputs — the
1024 figure in the review is the model card's example
configuration, not this run. A private GPU verification kernel
(nova-load-checks2-gpu) logged the inputs at the forecast call
at origin 0: TimesFM received a 2048-length input, and
Chronos-Bolt's forward received context tensors of length 2048.
Forecasting the same origin from only its most recent 1024 h
changes the outputs materially (max point-forecast change
545 MW for TimesFM, 391 MW for the Chronos median), so both
models used the hours beyond 1024; the verification forecasts
reproduce the variant run's saved origin-0 forecasts exactly.
For the record, the main (168 h) run compiled TimesFM with
max_context=512 and received the 168-length inputs in full.

## Item D — Paired intervals for the variant

2048 h − 168 h per-origin MASE differences, same block
bootstrap as REPORT_CHECKS check 5 (blocks of 4 origins,
B = 2000, seed 20261117). Full table:
results/scores_paired_variant.csv (DECISIONS #25).

| Model | Horizon | Half | Diff [95% CI] | n |
|---|---|---|---|---|
| Chronos-Bolt | 24 | 1 | +0.008 [−0.018, +0.033] | 53 |
| Chronos-Bolt | 24 | 2 | −0.093 [−0.161, −0.037] | 51 |
| Chronos-Bolt | 168 | 1 | −0.045 [−0.106, +0.013] | 53 |
| Chronos-Bolt | 168 | 2 | −0.096 [−0.165, −0.026] | 51 |
| TimesFM | 24 | 1 | +0.063 [+0.013, +0.119] | 53 |
| TimesFM | 24 | 2 | +0.027 [−0.025, +0.089] | 51 |
| TimesFM | 168 | 1 | −0.002 [−0.073, +0.071] | 53 |
| TimesFM | 168 | 2 | +0.017 [−0.057, +0.096] | 51 |

Chronos-Bolt improves with intervals excluding 0 in half 2 at
both horizons; its half-1 differences span 0. TimesFM is worse
with the interval excluding 0 only at 24 h in half 1; its other
three differences span 0. Claude accepted C and D as they stand
in the ruling on A.

## Run records

All kernels private; no credentials in any kernel or output.
Spend: $0.00.

| Kernel | Accelerator | What | Runtime |
|---|---|---|---|
| nova-load-checks2-gpu | Tesla T4 | item C context verification (inputs logged at origin 0; 1024 h truncation comparison) | short verification run, complete |
| nova-load-checks2-cpu | CPU | item A (d = 0, D = 1) sensitivity: AIC selection within (0, 1) + full 104-origin backtest | 16,485 s, complete |

The two parquets in the CPU kernel's downloaded output
(the pinned PUDL demand table and the weather extract) are
echoes of its inputs, not results; they are not committed
(the repo carries no input data — .gitignore excludes
*.parquet — and the PUDL file is the pinned release verified
by SHA-256 in the run record).
