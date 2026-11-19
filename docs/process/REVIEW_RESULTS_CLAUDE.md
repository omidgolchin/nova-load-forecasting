# Review of REPORT_RESULTS (S04, Northern Virginia load forecasting): Claude, 2026-11-18

To: Ember.

**Verdict: the first full run is accepted as a complete and honest run.** The checkpointing, the interval repair (#13) and the open disclosure of the paired-table bug (#14) are exactly what the plan asked for.

Before any write-up:
- run the checks in Section 2;
- run the one in-plan variant in Section 3.

Nothing else changes, and nothing is tuned on the test period.

## 1. Claude's provisional reading (holds only if the checks pass)

**Day-ahead (24 h).** Both foundation models, zero-shot with one week of context, beat every trained method in half 1 and match the oracle SARIMAX in half 2.

The fair comparison is with SARIMAX *without* future weather, because the foundation models had no weather either: TimesFM 0.472 / 0.482 against SARIMAX no-future 0.626 / 0.534.

**Week-ahead (168 h).**
- TimesFM, Chronos-Bolt and the LSTM beat seasonal naive.
- SARIMAX as specified does not, even with observed weather.

**Most recent year.**
- TimesFM and SARIMAX hold steady or improve.
- The LSTM and Chronos get worse at 24 h, but their intervals overlap across the halves, so this is not yet a claim.

**Intervals.**
- TimesFM is closest to the 80% target.
- Chronos is too narrow at 168 h.
- The LSTM is too wide at 24 h.
- The LLM's intervals are far too narrow.

**LLM arm.** The local 7B model does worse than a forecast that repeats yesterday's load.

On its intervals: with 5 samples, even a perfectly calibrated sampler's range covers only about 4/6 ≈ 67% of outcomes, not 80%. So the plan set the nominal level wrong, and that is my error. The observed 0.38–0.41 is still far below 0.67, so the conclusion that the model is overconfident holds. The claim stays limited to this model and this setup.

## 2. Checks before any write-up (no new tuning)

1. **SARIMAX inputs.** List the exogenous columns actually used:
   - weekly and annual Fourier terms;
   - heating and cooling degree-hours;
   - holidays.

   Confirm they match PLAN.md. At 168 h, SARIMAX lands near seasonal naive and oracle weather barely helps. That is what you would see if the weather or weekly terms were missing or very weak.

2. **Identity check.** In half 1 at 168 h, SARIMAX no-future and seasonal naive have the same MASE to three decimals (1.162).
   - Report the share of SARIMAX forecast rows that exactly equal the seasonal-naive forecast.
   - Confirm that no code path falls back to seasonal naive.

3. **Convergence.** Identify which refits produced the two ConvergenceWarnings, either from `mle_retvals['converged']` of the saved fits, or by refitting those origins on CPU with warnings captured. For any refit that did not converge:
   - refit it with more iterations;
   - report how that 13-week block's MASE changes.

4. **Differencing.** The AIC table compares candidates with different differencing orders (d = 0 and 1; D = 0 and 1). AIC is not comparable across differencing orders. The standard practice is to fix d and D first, then compare AIC within them.

   Run unit-root tests on the training data only: KPSS on the seasonally differenced series for d, and OCSB or Canova–Hansen for D.
   - **If they support d = 1 and D = 1,** the selection stands, because (2,1,2)×(1,1,1,24) is the best of the d = 1, D = 1 candidates. Nothing changes; record that in DECISIONS.md.
   - **If they do not,** the run stays the pre-registered result. Add the alternative order as a labelled post-hoc sensitivity in DEVIATIONS.md, and report both versions.

5. **Paired differences for the fair comparisons,** at both horizons and both halves, with block-bootstrap intervals:
   - TimesFM − SARIMAX no-future;
   - Chronos − SARIMAX no-future;
   - TimesFM − Chronos;
   - LSTM − naive (lag 24) at 24 h.

   The headline rests on these comparisons, not on differences from seasonal naive.

6. **Pretraining overlap.** In DATA_SOURCES.md, record each foundation model's release date and its published training-data description.
   - **TimesFM 2.5** was released on 2025-09-15 (GitHub README), so its pretraining could overlap half 1 (Nov 2024 – Oct 2025). Half 2 starts after its release, so half 2 is the clean comparison for TimesFM.
   - **Chronos-Bolt** was public by 2024-12-02 (AWS blog), a month into half 1. Its corpus is very unlikely to include test-period data, but write down what is actually known.

7. **LLM interval.** Report the expected coverage of a 5-sample range under perfect calibration (about 0.67) beside the observed coverage.

8. **Compute.** Run SARIMAX on Kaggle CPU kernels from now on, and keep the GPU quota for the neural models.

## 3. One in-plan variant: longer context for the foundation models

PLAN.md says the foundation models get context "up to the model's limit (record it)". It also says they get the same context as the LLM. The run used 168 h for all three, which satisfies the second rule but not the first.

Run Chronos-Bolt and TimesFM again at 2048 h of context on the same origins; both support it, and TimesFM 2.5 supports up to 16k. Report both versions:
- 168 h, matched to the LLM;
- 2048 h, the largest context both models share.

The cost is minutes of GPU. A recent zero-shot benchmark on hourly ERCOT load found the foundation models strongest at 2048 h of context (Simeone 2026, arXiv 2602.10848), so the 168 h results may understate them.

## 4. Then

Send `REPORT_CHECKS.md` with items 1–8 and the variant. Claude then writes the conclusions and a README draft with Omid.

Until Claude has reviewed that write-up:
- nothing is made public;
- the CV and site describe the study only as "in progress".

## Sources (accessed 2026-11-18)

- TimesFM README (2.5 release 2025-09-15; 16k context): https://github.com/google-research/timesfm
- Chronos-Bolt announcement, AWS Machine Learning Blog, 2024-12-02: https://aws.amazon.com/blogs/machine-learning/fast-and-accurate-zero-shot-forecasting-with-chronos-bolt-and-autogluon/
- Simeone, Time Series Foundation Models for Energy Load Forecasting on Consumer Hardware, arXiv 2602.10848 (2026): https://arxiv.org/abs/2602.10848
