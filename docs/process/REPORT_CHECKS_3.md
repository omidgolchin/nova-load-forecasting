# S04 — Checks round 3 (the review of REPORT_CHECKS_2, 2026-11-18)

Items 1, 2 and 4 of the round-2 review, plus item 3's
DEVIATIONS.md changes. Numbers only, as in REPORT_CHECKS.md.
Training data and saved forecasts only; nothing was refit or
re-selected on the test period, and the pre-registered run is
unchanged everywhere. Item 1's full working record is
results/checks3_item1.md; the round is DECISIONS #28.

## Item 1 — The (0, 1) selection, settled with converged fits

**Verdict: (2,0,2)×(1,1,1,24) still wins within (0, 1) on
converged fits** — AIC 219,995.4, ahead of the runner-up
(2,0,1)×(0,1,1,24) at 220,774.2 by **778.8 points**, not the
~130 the non-converged numbers suggested. Per the review's
decision rule the (0, 1) backtest stands as run; no order is
superseded by this item.

All five candidates were refit on the order-selection window
(2022-11-01 → 2024-11-01, n = 17,544, the same 13 exogenous
columns; the reconstruction reproduces item A's OLS benchmarks
exactly: R² = 0.7688, residual sd 1,132.1 MW). Every fit in the
right-hand column reports `mle_retvals['converged'] == True`.

| Order | Seasonal | First run (REPORT_RESULTS) | Checks round 2 | **Converged** |
|---|---|---:|---:|---:|
| (1, 0, 1) | (1, 1, 1, 24) | 224,678.9 | 224,679.2 | **224,098.2** |
| (2, 0, 1) | (1, 1, 1, 24) | 220,793.7 | 220,793.7 | **220,793.8** |
| (1, 0, 2) | (1, 1, 1, 24) | 221,095.7 | 221,120.5 | **221,003.3** |
| **(2, 0, 2)** | **(1, 1, 1, 24)** | 230,938.2 | 220,663.7 | **219,995.4 — selected** |
| (2, 0, 1) | (0, 1, 1, 24) | — (not a first-run candidate) | 221,440.3 | **220,774.2** |

How convergence was reached: the two rounds' procedure
(statsmodels-default L-BFGS, maxiter 50, no start values) was
replicated first — all five fits hit the 50-iteration cap and
warned, as in both rounds (14 of 14 executions of that
procedure on these candidates, across the first run, checks
round 2 and the local replication, stopped at the cap). Each
fit was then warm-started from its capped endpoint with the
cap raised to 1,000; all five converged there, in 1–37
additional iterations, with no ConvergenceWarning and final
gradient max |component| ≤ 4.8 × 10⁻⁴. No candidate needed a
Powell or Nelder–Mead stage. The binding constraint in both
historical rounds was the default 50-iteration cap. The
checks-2 values sat above the converged optima by 668.2
((2,0,2)), 666.1 ((2,0,1)×(0,1,1,24)), 581.0 ((1,0,1)) and
117.2 ((1,0,2)); (2,0,1)×(1,1,1,24) had effectively already
arrived (0.04, cross-environment floating-point noise), which
is why all three executions agreed on it to 0.1.

**The 230,938.2 → 220,663.7 difference, from evidence.** None
of settings, start values or data explains it; both numbers
are non-converged stops of the same capped procedure, and
this candidate's stop point is highly path-dependent:

- Data identical: the pinned PUDL file's SHA-256 was verified
  inside both kernels and again locally; the two runs' saved
  weather series are bit-identical (max |difference| 0.0 °C
  over all 70,872 hours).
- Design and settings identical: series construction, the
  exogenous design and the window slicing are textually
  identical between the first-run notebook and the checks2
  kernel; same SARIMAX arguments, same `.fit(disp=False)`
  defaults (maxiter 50, per the first run's own run record),
  no `start_params` in either selection loop.
- Both fits warned: a ConvergenceWarning immediately precedes
  the (2,0,2) candidate print in each round's kernel log.
- The stop point scatters by candidate: three executions of
  the identical procedure stopped at 230,938.2 / 220,663.7 /
  220,680.1 for (2,0,2) and at 221,095.7 / 221,120.5 /
  221,107.1 for (1,0,2), while agreeing to 0.1 on the one
  candidate whose capped fit was already at its optimum.
- The converged optimum, 219,995.4, lies below both
  historical values, so 230,938.2 was a poor stop of the
  optimizer — the review's likeliest story, now with the
  converged fit behind it. The one documented environmental
  difference is the container image (first run
  `kaggle-private-byod@sha256:de153e6d…`, checks2
  `kaggle-images/python@sha256:7de5e149…`); different
  library/BLAS builds are the plausible source of the
  trajectory differences a capped optimizer amplifies into
  a 10,274-point gap. That last step is stated as plausible,
  not proven; the converged fit is what settles the
  selection.

**First run: did the pre-registered selection fits warn?
Yes.** In the v4 kernel's log, a ConvergenceWarning
immediately precedes the candidate print for six of the
eight selection fits. The two that did not warn are
(1,1,1)×(1,1,1,24) and the selected pre-registered order
(2,1,2)×(1,1,1,24) itself. The pre-registered result does
not change: its own fit is one of the two that did not warn.

## Item 2 — Fair comparisons against the sensitivity order

Same block bootstrap as REPORT_CHECKS check 5 (blocks of 4
origins, B = 2000, seed 20261117), per-origin MASE differences
on origins scored for both methods, saved forecasts only.
Validation before any new number: the pipeline reproduces
check 5's published table exactly (maximum absolute deviation
0.0 across all 14 rows), the sensitivity's published MASE and
coverage exactly, and the 2048 h variant's MASE values to
that file's 4-decimal rounding. Full table:
results/scores_paired_sensitivity2.csv.

| Comparison | Horizon | Half | Diff [95% CI] | n |
|---|---|---|---|---|
| TimesFM − SARIMAX (0,1) no-future | 24 | 1 | −0.074 [−0.138, +0.008] | 53 |
| TimesFM − SARIMAX (0,1) no-future | 24 | 2 | −0.070 [−0.123, −0.015] | 51 |
| TimesFM − SARIMAX (0,1) no-future | 168 | 1 | +0.022 [−0.032, +0.075] | 53 |
| TimesFM − SARIMAX (0,1) no-future | 168 | 2 | +0.023 [−0.022, +0.066] | 51 |
| TimesFM 2048 h − SARIMAX (0,1) no-future | 24 | 1 | −0.011 [−0.076, +0.059] | 53 |
| TimesFM 2048 h − SARIMAX (0,1) no-future | 24 | 2 | −0.043 [−0.092, +0.007] | 51 |
| TimesFM 2048 h − SARIMAX (0,1) no-future | 168 | 1 | +0.020 [−0.064, +0.100] | 53 |
| TimesFM 2048 h − SARIMAX (0,1) no-future | 168 | 2 | +0.040 [−0.037, +0.124] | 51 |
| Chronos-Bolt − SARIMAX (0,1) no-future | 24 | 1 | −0.098 [−0.168, −0.010] | 53 |
| Chronos-Bolt − SARIMAX (0,1) no-future | 24 | 2 | −0.017 [−0.087, +0.056] | 51 |
| Chronos-Bolt − SARIMAX (0,1) no-future | 168 | 1 | +0.077 [+0.010, +0.142] | 53 |
| Chronos-Bolt − SARIMAX (0,1) no-future | 168 | 2 | +0.115 [+0.027, +0.202] | 51 |
| Chronos-Bolt 2048 h − SARIMAX (0,1) no-future | 24 | 1 | −0.090 [−0.167, +0.005] | 53 |
| Chronos-Bolt 2048 h − SARIMAX (0,1) no-future | 24 | 2 | −0.110 [−0.181, −0.047] | 51 |
| Chronos-Bolt 2048 h − SARIMAX (0,1) no-future | 168 | 1 | +0.032 [−0.026, +0.095] | 53 |
| Chronos-Bolt 2048 h − SARIMAX (0,1) no-future | 168 | 2 | +0.019 [−0.019, +0.060] | 51 |
| SARIMAX (0,1) no-future − seasonal naive | 24 | 1 | −0.639 [−0.867, −0.437] | 53 |
| SARIMAX (0,1) no-future − seasonal naive | 24 | 2 | −0.802 [−1.006, −0.585] | 51 |
| SARIMAX (0,1) no-future − seasonal naive | 168 | 1 | −0.290 [−0.352, −0.225] | 53 |
| SARIMAX (0,1) no-future − seasonal naive | 168 | 2 | −0.335 [−0.426, −0.242] | 51 |

Against the pre-registered order (check 5), TimesFM at 168 h
was −0.269 / −0.315 with intervals excluding 0, and
Chronos-Bolt −0.213 / −0.223 excluding 0. Against the
sensitivity order at the same horizon: TimesFM's differences
are +0.022 / +0.023, intervals spanning 0, at both contexts;
Chronos-Bolt's are +0.077 / +0.115 with intervals excluding
0 at 168 h context, and +0.032 / +0.019 spanning 0 at 2048 h
context. At 24 h, the intervals excluding 0 are TimesFM in
half 2 (−0.070), Chronos-Bolt in half 1 at 168 h context
(−0.098) and in half 2 at 2048 h context (−0.110); the other
five 24 h differences span 0. The sensitivity against
seasonal naive excludes 0 in all four cells — at 168 h
−0.290 / −0.335, where the pre-registered order's differences
were +0.000 / +0.003, spanning 0 (check 5).

**The sensitivity's main-table metrics** (same scoring as
scores_main.csv; full precision in
results/scores_sensitivity2_metrics.csv):

| Variant | Horizon | Half | MASE [95% CI] | MAPE % | Peak-hour err (MW) | Cov80 | Winkler80 |
|---|---|---|---|---:|---:|---:|---:|
| No-future | 24 | 1 | 0.546 [0.457, 0.630] | 4.56 | 1,227 | 0.700 | 3,610 |
| No-future | 24 | 2 | 0.552 [0.466, 0.640] | 4.24 | 1,231 | 0.777 | 3,702 |
| No-future | 168 | 1 | 0.872 [0.684, 1.067] | 7.47 | 1,497 | 0.680 | 6,187 |
| No-future | 168 | 2 | 0.902 [0.756, 1.078] | 7.06 | 1,568 | 0.723 | 6,058 |
| Oracle | 24 | 1 | 0.479 [0.398, 0.559] | 3.97 | 1,116 | 0.781 | 3,181 |
| Oracle | 24 | 2 | 0.484 [0.406, 0.567] | 3.69 | 1,128 | 0.836 | 3,291 |
| Oracle | 168 | 1 | 0.799 [0.633, 0.971] | 6.83 | 1,389 | 0.709 | 5,505 |
| Oracle | 168 | 2 | 0.841 [0.707, 1.004] | 6.57 | 1,483 | 0.750 | 5,618 |

## Item 3 — DEVIATIONS.md disclosure changes

Applied to the (d = 0, D = 1) section of DEVIATIONS.md:

1. **Timing of the ruling.** DEVIATIONS.md now records that
   the ruling on A (DECISIONS #26) was relayed at ~18:38 EST
   and applied at 18:41 EST on 2026-11-18, while the (0, 1)
   backtest was still running, and that the backtest
   completed at ~22:23 EST the same day — the ruling was
   given before any of the sensitivity's results existed.
2. **Two of three criteria.** The disclosure now states
   plainly that two of the three seasonal criteria pointed
   to D = 0 (OCSB, and the seasonal-strength rule: 0.595 /
   0.627 against 0.64); only Canova–Hansen pointed to D = 1.
3. **Weekly-harmonics hypothesis.** It does not appear in
   DEVIATIONS.md — the only place it stands in the repo is
   the round-1 checks review (item
   E) — so there was nothing to remove;
   the write-up gives no cause for the week-ahead gap beyond
   the differencing order. The README's one-sentence mention
   of the superseded (0, 0) result (review item 3.3) belongs
   to the README itself and is outstanding for the README
   step, not this round.

## Item 4 — Chart

results/chart_mase.png regenerated from scores_main.csv plus
the sensitivity's metrics, with the original chart code's
style, data and headline unchanged. The sensitivity SARIMAX
(no-future variant) appears directly below the pre-registered
SARIMAX (no future weather) row in both panels as **hollow
markers** (circle half 1, square half 2, in the same half
colours, with the same CI bars), labelled "SARIMAX (no future
weather) — post-hoc order": 24 h 0.546 / 0.552, 168 h
0.872 / 0.902. The pre-registered run stays the headline.

## Run records

All work local (repo `.venv`); no kernels this round; no
credentials anywhere. Spend: $0.00. Item 1 local compute
≈ 3,633 s across its ten fit stages; items 2–4 are seconds of
scoring and plotting on saved forecasts. Scripts and
per-stage records: the goal workspace's hidden_files
(checks3_item1/, checks3_items234/).
