# Decisions

#1 (2026-11-17) Study approved by Omid; brief by Claude (2026-11-17)
governs. Defaults adopted from the brief's open questions: LLM arm is a
small open instruction model (~7–8B, 4-bit) on the Kaggle GPU, API only
as fallback; weather points Ashburn/Loudoun, Richmond, Norfolk averaged
with fixed weights 1/3 each; repo name nova-load-forecasting (private,
Omid creates; local build until then).
#2 (2026-11-17) Priority: S03 comes first whenever the two compete.
#3 (2026-11-17, Step 0) Demand source: PUDL nightly
`out_eia930__hourly_subregion_demand` (EIA-930), reported values as the
primary series per PLAN, cross-checked against the `core_` table
(identical). Fallbacks (EIA API/bulk, PJM Data Miner) checked and not
needed; PJM Data Miner's terms bar non-members from republishing,
which would conflict with publishing the study. DOM coverage verified
2018-07-01 → 2026-10-31 UTC, but 2018 is partial (39% missing, one
71-day hole): recommended training start is 2019-01-01. Flagged hours
from 2019: 362 of 68,645 (291 missing, 69 anomalous-region on
clock-change days, 2 corrupt global outliers on 2021-10-19 that must
never enter as reported). Whether to use PUDL's imputed series for
flagged/missing hours is left to Claude's Step 0 review; default stays
reported values. Detail: docs/process/REPORT_DATA.md.
#4 (2026-11-17, Claude's Step 0 review; applied on Omid's go) Missing
and flagged hours: neither series is used as it is. Scoring targets
are reported values on unflagged hours only; a missing,
`anomalous_region` or `global_outlier` target hour is dropped from
every method's score, identically across methods, with the dropped
count reported per test half (this covers the November 2024 and
November 2025 fall-back days in the test period). Model inputs use
reported values with every flagged or missing hour replaced by the
value 168 hours earlier, stepping back another week if that hour is
also flagged, applied once to the whole series so every method sees
the same input; this covers the two 2021-10-19 `global_outlier`
hours. The PUDL imputed series is not used: PUDL imputes each year as
a whole, drawing on later days and other regions, so an imputed hour
just before a forecast origin can carry information from later in the
same year — look-ahead in a backtest that a backward-only fill
removes. The imputed column stays in the raw extract for reference.
#5 (2026-11-17, Claude's Step 0 review) Training history starts
2019-01-01, as Step 0 recommended. 2018 is excluded: 39% of its hours
are missing, including one 71-day hole.
#6 (2026-11-17, Claude's Step 0 review) Data version pinned to the
stable PUDL release v2026.11.0 (2026-11-10), not the nightly build,
so the study can be re-run on identical data. If the stable release's
DOM series ends before 2026-10-31 04:00 UTC, the 2026-11-16 nightly
is kept instead and DATA_SOURCES.md says so. Either way DATA_SOURCES.md
records the release (with DOI if any) or nightly date, the file
hashes and a hash of the DOM extract, and reported values are checked
against the nightly where the two overlap.
#7 (2026-11-17, Claude's Step 0 review) MASE uses a single fixed
scale for all methods, origins and halves: the mean absolute error of
the lag-168 seasonal naive forecast over the training history
(2019-01-01 to the start of the test period), computed under the same
flagged-hour rules as the scores (#4). With a fixed scale, a MASE
difference between methods is a difference in error, not in scaling.
#8 (2026-11-17, Claude's Step 0 review) Test period on record:
2024-11-01 to 2026-10-31, in two halves (November 2024 – October
2025; November 2025 – October 2026). Forecast origins are weekly at
00:00 US Eastern; the last origin is the latest one whose full
168-hour horizon has data. Disclosure: the Step 0 growth table and
plot covered the test years. No method, setting or ruling was chosen
from them: PLAN.md fixed the design beforehand, and the rulings above
concern data handling only. The README's "What this does not show"
repeats this in one line.
#9 (2026-11-17, Claude's Step 0 review) Running the notebook through
the Kaggle API is approved, with conditions: kernels stay private
(`"is_private": true`), any uploaded dataset stays private, nothing
becomes public without Omid's approval; no Kaggle, EIA or Hugging
Face credentials go in the repo, the notebook or its outputs; every
run records kernel version, accelerator type, runtime and GPU hours
used against the weekly quota; results are pulled back into results/
(CSV plus PNG) so the review can read them from GitHub. The second
stop point is unchanged: stop after the first full run and send
docs/process/REPORT_RESULTS.md. Priority is unchanged (#2): S03 first, S04 fills
the gaps.
#10 (2026-11-17, notebook build; implementation choices where PLAN.md
leaves a detail open — each picked to make the comparison fairer or
the claim smaller)
(a) Test halves are assigned by forecast origin: origins before
2025-11-01 are half 1 (53 origins), the rest half 2 (51).
(b) The MASE scale's seasonal-naive predictions come from the filled
input series (what a method can see); its targets are clean reported
values on unflagged hours, as for all scores. Scale = 1,329.7 MW.
(c) Baseline intervals: seasonal naive and naive get 80% intervals
from their own pre-origin residuals on clean targets (residual 10th–
90th percentiles over all history before the origin), so the
coverage comparison includes the baselines.
(d) SARIMAX order is selected by AIC over the eight candidate orders
on the last two years of the initial training window (2022-11-01 to
2024-11-01, training data only), then held fixed; parameters are
refit every 13 weeks on the expanding window, and between refits the
fitted model is extended to each origin with new data and no refit
(statsmodels `apply`, refit=False). The two weather variants share
each refit's fitted parameters and differ only in the temperature
used over the horizon (observed vs lag-168), which isolates the
value of future weather.
(e) SARIMAX estimation numerics: `concentrate_scale=True` and each
fit warm-started from the previous fit's parameters. Same model,
data, orders and refit schedule; this is an optimizer detail, taken
because a cold full-window fit took ~27 minutes on Kaggle in the
smoke run (two fits, 3,307 s).
(f) LSTM is a single method: inputs are the past 168 h (load,
temperature with heating/cooling degree-hours as in SARIMAX,
calendar features) plus known future calendar features in the
output head; it uses no future temperature, matching the
no-future-weather SARIMAX variant. Point forecast is the mean over
the 3 seeds of the median; the interval is the mean over seeds of
the 10/90 quantiles; seed spread is reported per origin.
(g) Chronos-Bolt and TimesFM use the same 168 h context as the LLM,
per PLAN's "same context window" sentence for the zero-shot
methods; the Chronos bullet's "up to the model's limit" is
reconciled in favour of the fairer comparison (168 h is within
both models' limits). Models: Chronos-Bolt base, TimesFM
2.5-200M (the 2.5 API path verified in the smoke run).
(h) Naive and the LLM are scored at the 24 h horizon only (PLAN
defines both as 24 h methods); their table rows appear only there.
(i) The LLM arm runs fully locally (Qwen2.5-7B-Instruct, 4-bit, on
the Kaggle GPU), so the ≤$3 API fallback in PLAN.md is not used and
spend stays $0; prompt, decoding settings and the unparseable share
are recorded in the run record.
#11 (2026-11-17/18, first full run and resume) The first full run
(Kaggle kernel nova-load-backtest v4, private, T4) completed data
prep, the AIC order selection — winner (2,1,2)x(1,1,1,24), AIC
219,741.8 on the selection slice — baselines (all 104 origins) and
SARIMAX refits at origins 0/13/26/39 (52 origins), then the kernel
process died (nbclient DeadKernelError) during the SARIMAX refit at
origin 52, after ~2 h. The pattern (death at the largest fitting
window yet, with several statsmodels results objects holding
full-sample filtered covariances) is consistent with memory
exhaustion; Kaggle reports no failure message. Forecasts were
checkpointed to the kernel output after every method and refit, so
no completed work was lost. The run is completed by a second,
private resume kernel that attaches v4's output as a kernel source,
loads the checkpoint (baselines 104 origins; SARIMAX 52), takes the
selected order from v4 instead of re-running selection, and runs
SARIMAX origins 52–103 plus LSTM, Chronos-Bolt, TimesFM, the LLM arm
and scoring. Two memory-hygiene changes apply from the resume onward
(optimizer/storage details only; same model, data, orders and
schedule): statsmodels fits use low_memory=True, and results objects
are deleted with an explicit garbage collection after each origin
and refit. The repo notebook carries these fixes; v4 ran the
pre-fix build. Final results are reported across both runs in
docs/process/REPORT_RESULTS.md.
#12 (2026-11-18, resume mechanics) The resume kernel's first
version attached v4 as a kernel source, but v4's outputs were not
mounted (its run ended in error status, and Kaggle exposes only
successful runs' outputs as sources, apparently) — the resume
asserted and stopped before any modelling, at no cost. The resume
therefore carries v4's checkpoint embedded in an extra first cell
of the resume notebook only (the plain CSV exceeded Kaggle's 1 MB
kernel-source limit; the forecasts are packed as float32 arrays in
a compressed npz, ~0.44 MB of base64 — float32 rounding is at most
~0.001 MW on values of ~15,000 MW), which rebuilds the checkpoint
as a CSV in the working directory before the study code loads it;
the loader recomputes target_pos from origin and step. The repo
notebook does not contain the embedded data.
#13 (2026-11-18, low_memory intervals) The resume run completed
all methods, but the SARIMAX interval bounds are NaN at exactly
the four resume refit origins (52, 65, 78, 91; all 168 steps, both
variants): a statsmodels fit made with low_memory=True returns
NaN confidence bounds when forecasting directly from the fit
object, while the apply path used for the other origins is
unaffected, as are all point forecasts. The intervals for those
four origins are produced by a small top-up kernel that refits
the identical warm-start chain (cold at 52, then 65/78/91)
without low_memory and forecasts only those origins; its point
forecasts are checked against the resume run's values before its
intervals are spliced into forecasts_long.csv. The repo notebook
no longer uses low_memory (the del + gc hygiene of #11 is kept,
including in order selection): the memory problem is managed by
freeing results objects, not by low-memory storage.
#14 (2026-11-18, paired-table units bug) The first computed
scores_paired.csv was wrong: the paired difference subtracted
the seasonal naive's per-origin MAE in MW from each method's
per-origin MASE, so every method showed ≈ −1,576. The bug was in
the scoring code only (forecasts and the main table unaffected).
Fixed by converting the baseline to MASE units before
differencing; scores_main.csv and scores_paired.csv in results/
are recomputed from forecasts_long.csv with the fixed code and
cross-checked against the kernel's main table.
#15 (2026-11-18, top-up v1 death and subprocess isolation) The
first top-up kernel (four full-memory fits in one process)
completed the origin-52 fit and its forecasts, then the kernel
died during the origin-65 fit — the same failure signature as
v4, despite del + gc between fits; its in-memory rows were lost.
Full-memory SARIMAX fits on ~65k hours are therefore run one per
process: top-up v2 fits each origin in a fresh subprocess
(prep arrays passed via a pickle, fitted parameters chained
through files exactly as the warm-start chain requires), and
writes the top-up CSV after every origin. The study design is
unchanged; this is execution isolation only.


#16 (2026-11-18, Claude's review of REPORT_RESULTS; adopted on
Omid's go) The first full run is accepted as a complete and honest
run. Before any write-up: run the review's Section 2 checks (1–8)
and the one in-plan variant in its Section 3 (Chronos-Bolt and
TimesFM at 2048 h context), with no new tuning and nothing fitted
or selected on the test period. Full text: docs/process/REVIEW_RESULTS_CLAUDE.md.
Results go in docs/process/REPORT_CHECKS.md to Claude; nothing is public, and
the CV/site describe the study only as "in progress" until Claude
has reviewed the write-up.
#17 (2026-11-18, review check 8 — compute rule) From now on
SARIMAX runs on Kaggle CPU kernels; the GPU quota is reserved for
the neural models. This governs the check-3 refits and the check-4
sensitivity backtest in this round.
#18 (2026-11-18, review check 4 — differencing tests, training
data only) Unit-root tests on the order-selection window
(2022-11-01 → 2024-11-01, filled input series, n = 17,544):
KPSS on the seasonally differenced series (the review's prescribed
test for d): statistic 0.0098, p ≥ 0.10 — stationarity not
rejected, so no regular differencing is needed once D = 1 is
applied (d = 0); ADF on the same series agrees (−24.4, p ≈ 0).
Canova–Hansen for D (period 24, pmdarima implementation of the R
forecast test): statistic 5.075 against the 5% critical value
5.099 for m = 24 — seasonal stability not rejected, marginally;
OCSB (same window, pmdarima) also returns D = 0. The tests
therefore do not support d = 1 and D = 1, so per the review's
second branch the first full run stands as the pre-registered
result, and the test-supported orders (d = 0, D = 0) are run as a
labelled post-hoc sensitivity (DEVIATIONS.md): order selected by
AIC within (0, 0) on the same training window, same backtest.
#19 (2026-11-18, review check 3 — convergence) The resume
segment's SARIMAX refits were replicated on a CPU kernel with
warnings captured (DECISIONS #17). Exactly one refit did not
converge: origin 52 (cold start of the resume segment), which
emitted the ConvergenceWarning; the two warning lines in the
resume log are that single warning printed twice by the notebook
runner. Refits at 65, 78 and 91 converged with no warnings.
Refitting origin 52 with maxiter=500 converges, and its 13-origin
block MASE changes by only +0.0002 to +0.0005 (both variants,
both horizons); applied-origin interval coverage is unchanged to
three decimals. No published number changes. Detail:
docs/process/REPORT_CHECKS.md check 3; results/sarimax_convergence.csv,
results/sarimax_block_mase_maxiter.csv.
#20 (2026-11-18, review check 4 — sensitivity outcome) The
(d = 0, D = 0) post-hoc sensitivity of DEVIATIONS.md ran on the
CPU kernel: selected within (0, 0) by AIC on the training window,
(2,0,2)×(1,0,1,24), AIC 244,368.8. Its MASE against the
pre-registered order: oracle 24 h 0.527/0.566 vs 0.602/0.484,
oracle 168 h 1.054/1.092 vs 1.115/1.202, no-future 24 h
0.739/0.845 vs 0.626/0.534, no-future 168 h 1.239/1.291 vs
1.162/1.240 (halves 1/2). The pre-registered run remains the
result of record; the sensitivity is reported alongside it in
docs/process/REPORT_CHECKS.md check 4 and changes nothing else.
#21 (2026-11-18, Claude's review of REPORT_CHECKS; adopted on
Omid's go) Checks 1, 2, 3, 5, 7 and 8 are accepted as they
stand. Four follow-ups before the write-up: (A) the differencing
tests rerun on the OLS regression residuals, D decided before
d; (B) two DATA_SOURCES.md corrections (the TimesFM 2.5 corpus
list; the Chronos-Bolt corpus attribution); (C) verify the
context the foundation models actually received in the 2048 h
variant, re-running TimesFM if its max_context was below 2048;
(D) paired block-bootstrap intervals for the variant
differences. Deliverable: docs/process/REPORT_CHECKS_2.md. Full text:
docs/process/REVIEW_CHECKS_CLAUDE.md. The review also records that the
GitHub repo omidgolchin/nova-load-forecasting exists and is
public and empty: nothing is pushed to it until Omid makes it
private or decides to publish after Claude reviews the README.
#22 (2026-11-18, review item A — differencing tests on the
regression residuals, training data only) Procedure as
prescribed: OLS of load on the 13 exogenous columns over the
order-selection window (2022-11-01 → 2024-11-01, filled input
series, n = 17,544; OLS R² = 0.769, residual sd 1,132 MW), then
Canova–Hansen and OCSB (m = 24) on the residuals for D, then
KPSS for d on the residuals, seasonally differenced only if
D = 1. The local pipeline first reproduced round 1's raw-series
numbers exactly (KPSS on (1−B²⁴)y: 0.0098; Canova–Hansen on the
raw series: 5.075 against the 5% critical value 5.099; OCSB:
D = 0), so the data and implementations match round 1. On the
residuals the two D tests disagree: Canova–Hansen statistic
8.759 against 5.099 → D = 1; OCSB → D = 0. The same split
appears on the full training window (CH 10.654 → D = 1; OCSB
D = 0). Resolution, recorded here for Claude: Canova–Hansen is
followed, as in round 1 (DECISIONS #18), where CH was the
primary test — its statistic reported against its critical
value — and OCSB the corroboration. The D = 1 branch is also
the only one on which the d step is coherent: KPSS on the
seasonally differenced residuals is 0.0033 (p ≥ 0.10) and ADF
on the residuals is −11.5 (p ≈ 0), agreeing on d = 0, while on
the D = 0 branch KPSS on the residuals (13.25, p = 0.01) and
ADF (−11.5) contradict each other. Result: (d = 0, D = 1).
That is another order than round 1's (0, 0), so per the review
it becomes the post-hoc sensitivity — best AIC within (0, 1),
run on a CPU kernel (DECISIONS #17) — and the
(2,0,2)×(1,0,1,24) sensitivity is superseded in DEVIATIONS.md.
The pre-registered run stays the headline. Had OCSB been
followed instead, the order would have been (d = 1, D = 0);
the disagreement is reported in docs/process/REPORT_CHECKS_2.md for
Claude's ruling.
#23 (2026-11-18, review item B — DATA_SOURCES corrections)
TimesFM 2.5: the model card's four pretraining sources are now
listed (GiftEvalPretrain; Wikimedia Pageviews, cutoff November
2023; Google Trends top queries to end-2022; synthetic and
augmented data) — every documented source predates the test
period; half 2 stays the strictly clean comparison because the
model was released inside half 1 and the list is high-level.
Chronos-Bolt: the ~84B observations / 28 datasets description
is now attributed to the original Chronos paper (Ansari et
al. 2024), not Bolt; Bolt's card says "nearly 100 billion time
series observations" and does not name the corpus, which was
fixed before the 2024-12-02 release, so at most the first
month of half 1 could overlap, with no evidence it did.
#24 (2026-11-18, review item C — context actually received)
The variant kernel's source compiled TimesFM with
ForecastConfig(max_context=2048, max_horizon=168,
normalize_inputs=True, use_continuous_quantile_head=True,
fix_quantile_crossing=True) and passed 2048-length inputs; the
1024 cap in the review is the model card's example, not this
run. A GPU verification kernel (nova-load-checks2-gpu,
private) logged the inputs at the forecast call at origin 0:
TimesFM received a 2048-length input; Chronos-Bolt's forward
received context tensors of length 2048. Forecasting the same
origin from only its most recent 1024 h changes the outputs
materially (max point-forecast change 545 MW for TimesFM,
391 MW for the Chronos median), so both models used the hours
beyond 1024; the verification forecasts reproduce the variant
run's saved origin-0 forecasts exactly. No re-run; no variant
number changes. Main (168 h) run, for the record: TimesFM was
compiled with max_context=512 and received the 168-length
inputs in full; Chronos received the 168-length context as
passed.
#25 (2026-11-18, review item D — paired intervals for the
variant) 2048 h − 168 h per-origin MASE differences, same
block bootstrap as check 5 (blocks of 4 origins, B = 2000,
seed 20261117); full table results/scores_paired_variant.csv.
Chronos-Bolt improves with intervals excluding 0 in half 2 at
both horizons (24 h: −0.093 [−0.161, −0.037]; 168 h: −0.096
[−0.165, −0.026]); its half-1 differences span 0 (+0.008
[−0.018, +0.033] at 24 h; −0.045 [−0.106, +0.013] at 168 h).
TimesFM is worse with the interval excluding 0 only at 24 h in
half 1 (+0.063 [+0.013, +0.119]); its other differences span 0
(24 h half 2 +0.027; 168 h −0.002 and +0.017).
#26 (2026-11-18, Claude's ruling on item A; adopted on Omid's
go) The (d = 0, D = 1) sensitivity stands; the running (0, 1)
backtest finishes as launched. Full text: docs/process/RULING_A_CLAUDE.md.
Claude's grounds: his instruction named Canova–Hansen and
OCSB with no tie-break; D = 1 is defensible because the
residuals still carry most of the daily cycle (no regressor
has a 24 h period) and the d step is coherent only after the
lag-24 difference. Items C and D are accepted as they stand.
Seasonal strength of the residuals, computed as the ruling
asked (Wang–Smith–Hyndman strength from an STL decomposition
at period 24, periodic seasonal window, statsmodels; script
/tmp/s04c2/item_a_strength.py reusing item A's construction —
residuals verified against #22: selection window R² = 0.7688,
sd 1,132 MW, n = 17,544): 0.595 on the order-selection
window, 0.627 on the full training window. Both sit below
the forecast package's 0.64 threshold, so the package's
current default test would have given D = 0; the ruling
pre-committed to standing regardless, and the value is
reported beside the two test results in docs/process/REPORT_CHECKS_2.md
and disclosed in DEVIATIONS.md with both tests, their
values, and Claude's two reasons.
#27 (2026-11-18, review item A — the (0, 1) sensitivity
backtest completed) The backtest left running under #26
finished on the private CPU kernel nova-load-checks2-cpu
(DECISIONS #17): AIC selection within (0, 1) on the training
window picked (2,0,2)×(1,1,1,24), AIC 220,663.7, then the
identical 104-origin backtest (run record: all 104 origins,
fixed MASE scale 1,329.7334 MW, dropped target hours 98 of
8,903 in half 1 and 23 of 8,567 in half 2; elapsed 16,485 s;
PUDL file SHA-256 verified against DATA_SOURCES.md).
Sensitivity MASE (halves 1/2): no-future 24 h 0.546/0.552,
168 h 0.872/0.902; oracle 24 h 0.479/0.484, 168 h 0.799/0.841.
At 168 h no-future the pre-registered order was
indistinguishable from seasonal naive (1.162/1.240 vs
1.162/1.236); the sensitivity order scores 0.872/0.902 there.
Each of the five selection fits emitted one ConvergenceWarning
(each printed twice in the kernel log); none of the eight
backtest refits did. Outputs in results/:
scores_sensitivity2.csv, forecasts_sensitivity2.csv,
forecasts_sensitivity2_scored.csv, sarimax_alt2_selection.csv,
checks_run_record.json, checks2_kernel_log.txt. The kernel's
two downloaded parquets are echoes of its inputs (the pinned
PUDL table and the weather extract), not results, and are not
committed (.gitignore excludes *.parquet; the repo carries no
input data). docs/process/REPORT_CHECKS_2.md is written; DEVIATIONS.md
carries the full item-A disclosure and marks the (0, 0)
sensitivity superseded. Checks round 2 is complete; the
write-up (review item E) and publishing follow Claude's
conclusions and README draft with Omid.
#28 (2026-11-19, checks round 3 — REVIEW_CHECKS2_CLAUDE
items 1–4 complete) Item 1: the five (0, 1) candidates
refit to convergence (warm-started L-BFGS, cap 1,000, from
the capped fits' endpoints; all five report converged ==
True, no warnings). (2,0,2)×(1,1,1,24) still wins: converged
AIC 219,995.4, margin 778.8 over the runner-up
(2,0,1)×(0,1,1,24) at 220,774.2 — so the (0, 1) backtest
stands as run and nothing is superseded. The
230,938.2 → 220,663.7 gap is explained from evidence: data,
design and settings identical across the two rounds (PUDL
SHA-256 verified in both kernels and locally; the runs'
weather series bit-identical), both fits warned, and three
executions of the identical capped procedure scatter
(230,938.2 / 220,663.7 / 220,680.1) because the binding
constraint was the default 50-iteration cap; the converged
optimum lies below both values. First run's selection fits:
six of eight warned; the selected pre-registered order's own
fit did not. Full record: results/checks3_item1.md. Item 2:
paired block-bootstrap differences against the sensitivity
order (results/scores_paired_sensitivity2.csv; the pipeline
reproduces check 5's table exactly). At 168 h: TimesFM
+0.022/+0.023 (intervals span 0, both contexts), Chronos-Bolt
+0.077/+0.115 (exclude 0 at 168 h context; span 0 at 2048 h);
sensitivity − seasonal naive −0.290/−0.335 (exclude 0). The
sensitivity's coverage/Winkler/MAPE/peak-hour metrics are in
results/scores_sensitivity2_metrics.csv (no-future Cov80:
24 h 0.700/0.777, 168 h 0.680/0.723). Item 3: DEVIATIONS.md
now records the ruling's timing (relayed ~18:38 EST, applied
18:41 EST, 2026-11-18; backtest completed ~22:23 EST — the
ruling preceded all sensitivity results) and states plainly
that two of three seasonal criteria pointed to D = 0; the
weekly-harmonics hypothesis appears nowhere in DEVIATIONS.md
(it stands only in Claude's verbatim review text), so
nothing was removed. Item 4: results/chart_mase.png
regenerated with the sensitivity as a hollow "post-hoc
order" marker row under the pre-registered SARIMAX
no-future row. docs/process/REPORT_CHECKS_3.md is written. Checks round 3
is complete; the README fill (including the one-sentence
(0, 0) mention, review item 3.3) and publishing follow with
Omid and Claude.
#29 (2026-11-19, README filled) README.md is written from
Claude's draft v1 (README_DRAFT_V1_CLAUDE.md), with every
[pending] slot filled from docs/process/REPORT_CHECKS_3.md and every
[confirm] slot from PLAN.md, DECISIONS.md and
DATA_SOURCES.md. [pending]: the post-hoc order's coverage
(24 h 0.700/0.777, 168 h 0.680/0.723, from
results/scores_sensitivity2_metrics.csv via REPORT_CHECKS_3
item 2); the paired comparisons against the post-hoc order
(REPORT_CHECKS_3 item 2 — at 168 h TimesFM ties it in both
years, Chronos-Bolt is behind it at 168 h context and ties
at 2,048 h; at 24 h only TimesFM's year-2 and Chronos-Bolt's
year-1 intervals exclude 0); the Summary's two claims are
worded by those intervals. [confirm]: PUDL licence CC-BY-4.0
and Zenodo concept DOI 10.5281/zenodo.3653158
(DATA_SOURCES.md); weather points Ashburn/Richmond/Norfolk
at fixed weights 1/3 each, Open-Meteo CC BY 4.0 attribution
(PLAN.md, DATA_SOURCES.md); the no-future SARIMAX variant
uses the lag-168 temperature over the horizon, the two
variants sharing each refit's fitted parameters
(DECISIONS #10(d)); the LSTM is one layer of 64 hidden
units with quantile (pinball) loss at 10/50/90, its point
forecast the seed-averaged median and its interval the
seed-averaged 10–90% band (notebook §7; DECISIONS #10(f));
the Reproduce section carries the PUDL SHA-256 check, the
kernel order from the run records, regeneration of the
results tables from forecasts_long.csv (#14), and the
compute totals from the reports (≈9.2 GPU h first run;
checks round 1 ≈0.2 GPU h / ≈8.5 CPU h; checks round 2
16,485 s CPU plus a short GPU verification run; checks
round 3 ≈3,633 s local; $0 throughout). DEVIATIONS.md
gains the two disclosures from Claude's acceptance of
checks-3 item 1 (ACCEPTANCE_ITEM1_CLAUDE.md): the post-hoc
order confirmed on converged fits (AIC 219,995.4, margin
778.8; warm-start L-BFGS, maxiter 1,000, gradient
≤ 4.8 × 10⁻⁴), and the pre-registered selection's own cap
history (six of eight fits stopped at the 50-iteration cap;
the selected order's fit did not; the pre-registered result
stands as run). Nothing is published; publishing stays
Omid's step.
#30 (2026-11-19, code rule from Claude's acceptance of
checks-3 item 1) Any future SARIMAX fit in this repo sets
an explicit maxiter and checks `mle_retvals['converged']`;
a fit that has not converged is not reported as a result.
Origin: the 50-iteration default cap silently stopped 14
of 14 executions of the (0, 1) selection procedure and six
of the eight pre-registered selection fits (REPORT_CHECKS_3
item 1).#31 (2026-11-19, correction after publication) Two coverage
cells in the README's day-ahead table were mis-rounded in
the draft the README was filled from: Chronos-Bolt year 2
read 0.77 where scores_main.csv holds 0.7647, and TimesFM
year 1 read 0.84 where it holds 0.8349. Both now read as
the CSV rounds (0.76 and 0.83), in the README and in the
Kaggle notebook. Every other MASE and coverage cell in
both tables was re-checked against scores_main.csv and
scores_sensitivity2_metrics.csv and matches. Omid's call.
