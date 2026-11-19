# S04 — Checks round 3, item 1 (working draft for REPORT_CHECKS_3)

Item 1 of the round-2 review: settle the (d = 0, D = 1)
SARIMAX selection with converged fits. All work on training
data only (the order-selection window 2022-11-01 → 2024-11-01);
nothing in the test period was touched, and the pre-registered
run is unchanged.

## Verdict

**(2,0,2)×(1,1,1,24) still wins within (0, 1) on converged
fits** — AIC 219,995.4, ahead of the runner-up
(2,0,1)×(0,1,1,24) at 220,774.2 by 778.8 points. The margin
on converged fits is ~779 points, not the ~130 points the
non-converged numbers suggested. Per the review's decision
rule, the (0, 1) backtest stands as run; no order is
superseded by this item.

## Three-way AIC table

All five fits in the right-hand column report
`mle_retvals['converged'] == True`. The first three columns
are the same default procedure (statsmodels L-BFGS, maxiter
50) in three executions; every execution of it on these
candidates — four in the first run, five in checks round 2,
five locally, 14 of 14 — stopped at the iteration cap with
a ConvergenceWarning. None of them is a converged optimum.
A local replication of
the default procedure is included because it is part of the
evidence for the explanation below.

| Order | Seasonal | First run (REPORT_RESULTS) | Checks round 2 (sarimax_alt2_selection.csv) | Local default replication (stage A) | **Converged (stage B)** |
|---|---|---:|---:|---:|---:|
| (1, 0, 1) | (1, 1, 1, 24) | 224,678.9 | 224,679.2 | 224,675.7 | **224,098.2** |
| (2, 0, 1) | (1, 1, 1, 24) | 220,793.7 | 220,793.7 | 220,793.8 | **220,793.8** |
| (1, 0, 2) | (1, 1, 1, 24) | 221,095.7 | 221,120.5 | 221,107.1 | **221,003.3** |
| **(2, 0, 2)** | **(1, 1, 1, 24)** | 230,938.2 | 220,663.7 | 220,680.1 | **219,995.4 — selected** |
| (2, 0, 1) | (0, 1, 1, 24) | — (not a first-run candidate) | 221,440.3 | 221,418.7 | **220,774.2** |

Full precision, converged fits (log-likelihood in brackets):
(2,0,2)×(1,1,1,24) 219,995.435 [−109,977.718];
(2,0,1)×(0,1,1,24) 220,774.196 [−110,369.098];
(2,0,1)×(1,1,1,24) 220,793.753 [−110,377.877];
(1,0,2)×(1,1,1,24) 221,003.312 [−110,482.656];
(1,0,1)×(1,1,1,24) 224,098.181 [−112,031.090].

How far each non-converged checks-2 value sat above the
converged optimum: (2,0,2) 668.2; (2,0,1)×(0,1,1,24) 666.1;
(1,0,1) 581.0; (1,0,2) 117.2; (2,0,1)×(1,1,1,24) 0.04 in
absolute terms — its checks-2 stop actually sits 0.04 below
the local converged value, a difference at the
cross-environment floating-point noise level: that one fit
had effectively already arrived, which is why all three
executions agreed on it to 0.1.

## How convergence was achieved (per fit)

Design rebuilt from the checks2 kernel source (pulled from
Kaggle, `omidgolchin/nova-load-checks2-cpu` v1) and verified
identical before any fitting: selection window
2022-11-01 00:00 ET → 2024-11-01 00:00 ET, n = 17,544, the
same 13 exogenous columns; the reconstruction reproduces
item A's OLS benchmarks exactly (R² = 0.7688, residual sd
1,132.1 MW, fallback fills 0). Local environment: the repo
`.venv` — Python 3.12.3, statsmodels 0.15.0, scipy 1.18.1,
numpy 2.5.5, pandas 3.1.1.

- **Stage A — the two rounds' procedure, replicated.**
  `SARIMAX(..., enforce_stationarity=False,
  enforce_invertibility=False, concentrate_scale=True)
  .fit(disp=False)` (default L-BFGS, maxiter 50). All five
  fits hit the 50-iteration cap (1,080–1,300 function calls,
  394–581 s each), each emitted one ConvergenceWarning, none
  converged.
- **Stage B — the escalation that settled every fit.**
  L-BFGS with maxiter 1,000, warm-started from the stage-A
  parameters (`start_params`, statsmodels' transformed
  space — the same convention as the study's backtest
  warm-start chain). All five converged here, in 1–37
  additional iterations, with no ConvergenceWarning,
  `warnflag` 0, and final gradient max |component| ≤
  4.8 × 10⁻⁴:

| Candidate | Extra L-BFGS iterations | Function calls | Time |
|---|---:|---:|---:|
| (2, 0, 2)×(1, 1, 1, 24) | 37 | 880 | 408 s |
| (2, 0, 1)×(1, 1, 1, 24) | 1 | 76 | 71 s |
| (1, 0, 2)×(1, 1, 1, 24) | 27 | 608 | 315 s |
| (2, 0, 1)×(0, 1, 1, 24) | 30 | 612 | 244 s |
| (1, 0, 1)×(1, 1, 1, 24) | 23 | 522 | 221 s |

No candidate needed the further rungs (a fresh-start
maxiter-1,000 L-BFGS, or a Nelder–Mead / Powell stage
finished with L-BFGS): raising the iteration cap and
continuing from the capped fit's endpoint was enough in
every case. The binding constraint in both historical
rounds was the default 50-iteration cap, not the
optimizer or the model.

## The 230,938.2 → 220,663.7 difference, from evidence

The review asked which of settings, start values or data
explains why the same order on the same window shows AIC
230,938.2 in the first run's candidate table and 220,663.7
in checks round 2. The audit says: none of the three —
both numbers are non-converged stops of the same capped
procedure, and the stop point for this candidate is highly
path-dependent.

1. **Data — identical.** The demand file is the pinned
   PUDL release; its SHA-256 (1216ed4f…) was verified
   inside both kernels and again locally. The two runs'
   weather series were compared directly from their own
   saved `weather_utc.parquet` outputs: bit-identical,
   max |difference| 0.0 °C over all 70,872 hours.
2. **Design — identical.** The series construction (flag
   rule, 168 h walk-back fill), the exogenous design
   (`exog_rows`: weekly Fourier k = 1–3, annual Fourier
   k = 1–2, heating/cooling degree-hours, holiday) and the
   window slicing are textually identical between the
   first-run notebook (`notebooks/nova_load_backtest.ipynb`,
   cell `sarimax_order_selection`) and the checks2 kernel;
   the local reconstruction reproduces item A's OLS
   benchmarks to the printed digits (above).
3. **Settings — identical.** Same SARIMAX arguments
   (`enforce_stationarity=False`,
   `enforce_invertibility=False`, `concentrate_scale=True`)
   and the same `.fit(disp=False)`: statsmodels-default
   L-BFGS with maxiter 50 (the first run's own run record
   states "maxiter: statsmodels default (50)"). Neither
   selection loop passes `start_params`; both use
   statsmodels' data-derived default start values.
4. **Both fits warned.** The first run's kernel log shows
   a ConvergenceWarning immediately before the (2,0,2)
   candidate print (see the next section); the checks2
   log shows the same for its (2,0,2) fit. So neither
   historical number is an optimum — each is where a
   50-iteration L-BFGS trajectory happened to stop.
5. **The stop point scatters, by candidate.** Three
   executions of the identical default procedure stopped
   at 230,938.2 / 220,663.7 / 220,680.1 for (2,0,2), and
   at 221,095.7 / 221,120.5 / 221,107.1 for (1,0,2) —
   while for (2,0,1)×(1,1,1,24), whose capped fit was
   already at its optimum, all three agreed to 0.1. The
   scatter is large exactly where 50 iterations are not
   enough to climb the surface.
6. **The one documented environmental difference** is
   the container image: the first run's v4 kernel ran on
   `kaggle-private-byod@sha256:de153e6d…`, the checks2
   kernel on `kaggle-images/python@sha256:7de5e149…`
   (both Python 3.13 per the log paths; neither log prints
   a statsmodels version). Different library/BLAS builds
   are the plausible source of the floating-point-level
   trajectory differences that a capped, non-converged
   optimizer amplifies into a 10,274-point gap. What is
   shown rather than assumed is narrower and sufficient:
   the converged optimum, 219,995.4, lies below both
   historical values, so 230,938.2 was a poor stop of the
   optimizer — the review's likeliest story, now with the
   converged fit behind it.

## First run: did the pre-registered selection fits warn?

**Yes.** The first run's selection ran in kernel
`nova-load-backtest` v4 (its run record carries the
selection result, AIC 219,741.76452664455 for (2,1,2));
the kernel's log was pulled from Kaggle for this check.
A ConvergenceWarning (each printed twice, the same
double-printing as round 1) immediately precedes the
candidate print for six of the eight selection fits:
(1,0,1)×(1,1,1,24), (2,0,1)×(1,1,1,24),
(1,0,2)×(1,1,1,24), (2,0,2)×(1,1,1,24),
(1,0,1)×(0,1,1,24) and (2,0,1)×(1,0,1,24). The two fits
that did **not** warn are (1,1,1)×(1,1,1,24) and the
selected pre-registered order (2,1,2)×(1,1,1,24) itself.
(REPORT_RESULTS already recorded two ConvergenceWarnings
in the resume kernel's log; those belong to backtest
refits, not to the selection — the selection had already
run in v4.) The pre-registered result does not change:
its own fit is one of the two that did not warn, and this
item re-opens nothing about it.

## Provenance and reproducibility

Scripts, per-stage result JSONs, fitted parameters and the
pulled kernel sources/logs for this item are in
`~/workspace/goals/s04-northern-virginia-load-forecasting-study/hidden_files/checks3_item1/`
(`build_design.py`, `fit_stage.py`, `run_fits.py`,
`fit_results.jsonl`, `fits.log`). One incident, for the
record: the first local batch ran in /tmp and was lost to
a runtime restart after its first stage; the batch was
re-run from the durable directory above, and its stage-A
replication reproduced the lost run's AIC to all printed
digits (220,680.1481706661), so no number here rests on
the lost run. Total local compute for the final batch:
≈ 3,633 s across the ten stages. Spend: $0.00.
