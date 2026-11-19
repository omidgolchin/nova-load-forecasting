# Deviations

Changes after PLAN.md was committed are logged here with dates and
reasons. Results show both versions when a change follows test results.

## 2026-11-18 — SARIMAX differencing: post-hoc sensitivity at (d = 0, D = 0)

**SUPERSEDED 2026-11-18** by the (d = 0, D = 1) sensitivity in
the next section: the review of REPORT_CHECKS (item A)
moved the differencing tests onto the OLS regression residuals,
the tests there pointed to (0, 1), and the ruling on A made that
the one post-hoc sensitivity. The (2,0,2)×(1,0,1,24) results
below and in docs/process/REPORT_CHECKS.md check 4 stay on record, labelled
superseded; the write-up reports the (0, 1) sensitivity, not
this one.

Raised by the review of REPORT_RESULTS (check 4): the first
run's AIC table compared candidate orders with different
differencing orders (d = 0 and 1; D = 0 and 1), and AIC is not
comparable across differencing orders.

Unit-root tests on training data only (order-selection window
2022-11-01 → 2024-11-01, filled input series, n = 17,544;
DECISIONS #18):

- d: KPSS on the seasonally differenced series — statistic
  0.0098, p ≥ 0.10, stationarity not rejected; ADF on the same
  series −24.4, p ≈ 0. No regular differencing is supported once
  D = 1 is applied.
- D: Canova–Hansen (period 24) — statistic 5.075 vs the 5%
  critical value 5.099 for m = 24, seasonal stability not
  rejected (marginally); OCSB also returns D = 0.

The tests do not support the pre-registered order's d = 1, D = 1.
Per the review:

- **The first full run stands as the pre-registered result.**
  Its SARIMAX numbers are unchanged everywhere they are reported.
- The test-supported orders (d = 0, D = 0) are run once, as this
  labelled post-hoc sensitivity: the order is selected by AIC
  among (p, 0, q) × (P, 0, Q, 24) candidates on the same
  training window, then run through the identical backtest
  (same origins, refit schedule, warm-start chain, exog, scoring).
  Both versions are reported side by side in docs/process/REPORT_CHECKS.md.
  The sensitivity is not a replacement result and was not used
  to tune anything.

## 2026-11-18 — SARIMAX differencing: the sensitivity moves to (d = 0, D = 1)

the review of REPORT_CHECKS (item A) found the round-1
tests were run on the wrong series: SARIMAX here is a regression
with ARIMA errors, so the differencing question is about the
errors. The tests were rerun on the OLS residuals (load on the
13 exogenous columns; order-selection window 2022-11-01 →
2024-11-01, filled input series, n = 17,544; R² = 0.769,
residual sd 1,132 MW), D decided before d (DECISIONS #22).

**The two D tests disagree** (full disclosure, as the ruling on
A requires):

- Canova–Hansen (m = 24) on the residuals: statistic 8.759
  against the 5% critical value 5.099 → **D = 1**. On the full
  training window: 10.654 → D = 1.
- OCSB (m = 24) on the residuals: **D = 0**, on both windows.
  OCSB alone would have pointed to D = 0.
- Seasonal strength of the residuals (Wang–Smith–Hyndman, STL
  at period 24): 0.595 on the selection window, 0.627 on the
  full training window — both below the forecast package's
  0.64 threshold, so its current default test would also have
  given D = 0.

Stated plainly: **two of the three seasonal criteria pointed
to D = 0** — OCSB, and the seasonal-strength rule (0.595 /
0.627 against the 0.64 threshold). Only Canova–Hansen pointed
to D = 1.

- d, on the D = 1 branch: KPSS on the seasonally differenced
  residuals 0.0033 (p ≥ 0.10), ADF on the residuals −11.5
  (p ≈ 0) → d = 0. On the D = 0 branch the d tests contradict
  each other (KPSS 13.25, p = 0.01, against ADF −11.5).

**The ruling (DECISIONS #26): keep
(d = 0, D = 1).** The review's instruction named both tests and set no
tie-break, so the gap was in the review. Its two reasons, which do not
depend on the sensitivity's result:

1. The residuals still carry most of the daily cycle — no
   deterministic regressor has a 24 h period (the weekly
   Fourier terms have periods of 168, 84 and 56 h, and the
   degree-hours carry only the weather-driven part of the
   daily shape) — so a seasonal difference at lag 24 is what
   makes these errors plausibly stationary.
2. The d step only works under D = 1: KPSS on residuals that
   keep a strong daily cycle is not a valid test, so d can
   only be chosen coherently after the lag-24 difference.

The ruling pre-committed to standing whatever the seasonal
strength showed.

**Timing of the ruling (recorded in checks round 3, per
the round-2 review, item 3).** The ruling was relayed at
~18:38 EST on 2026-11-18 and applied at 18:41 EST
(DECISIONS #26), while the (0, 1) backtest was still running
on the CPU kernel; the backtest completed at ~22:23 EST the
same day (DECISIONS #27). The ruling was therefore given
before any of the sensitivity's results existed, and its two
reasons above do not depend on them.

The (0, 1) sensitivity: order selected by AIC
within (0, 1) on the same training window —
(2,0,2)×(1,1,1,24), AIC 220,663.7 — then run through the
identical backtest (CPU kernel nova-load-checks2-cpu, 104
origins). Its no-future MASE: 24 h 0.546/0.552, 168 h
0.872/0.902; oracle: 24 h 0.479/0.484, 168 h 0.799/0.841
(halves 1/2), against the pre-registered order's no-future
168 h 1.162/1.240, which is indistinguishable from seasonal
naive (1.162/1.236). Full table: docs/process/REPORT_CHECKS_2.md item A;
scores in results/scores_sensitivity2.csv.

- **The first full run stands as the pre-registered result.**
  Its SARIMAX numbers are unchanged everywhere they are
  reported.
- This is now the one post-hoc sensitivity the write-up
  reports. The (d = 0, D = 0) sensitivity above is superseded
  and stays on record labelled as such.
- The sensitivity is not a replacement result and was not used
  to tune anything.

**Converged-fits confirmation (checks round 3, 2026-11-19;
DECISIONS #28; accepted on review).**
The five (0, 1) candidates were refit to convergence on the
same order-selection window. Each fit was warm-started from
its capped endpoint with the L-BFGS iteration cap raised from
50 to 1,000; all five report `mle_retvals['converged'] ==
True`, with no ConvergenceWarning and final gradient max
|component| ≤ 4.8 × 10⁻⁴. Converged AICs:
(2,0,2)×(1,1,1,24) **219,995.4** — still the winner;
(2,0,1)×(0,1,1,24) 220,774.2; (2,0,1)×(1,1,1,24) 220,793.8;
(1,0,2)×(1,1,1,24) 221,003.3; (1,0,1)×(1,1,1,24) 224,098.2.
The margin over the runner-up is 778.8 points, not the ~130
the capped fits suggested. The AIC of 220,663.7 quoted above
for the selection was a non-converged stop of the same capped
procedure (three executions of it stopped at 230,938.2 /
220,663.7 / 220,680.1). The (0, 1) backtest stands as run.
Full record: docs/process/REPORT_CHECKS_3.md item 1;
results/checks3_item1.md.

**The pre-registered selection hit the same cap.** In the
first run's kernel log, a ConvergenceWarning immediately
precedes the candidate print for six of the eight selection
fits — those fits also stopped at statsmodels' default
50-iteration cap. The two that did not warn are
(1,1,1)×(1,1,1,24) and the selected pre-registered order
(2,1,2)×(1,1,1,24) itself. The pre-registered result stands
as run: its own fit is one of the two that did not warn.
