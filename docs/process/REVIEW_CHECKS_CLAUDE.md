# Review of REPORT_CHECKS (S04, Northern Virginia load forecasting): Claude, 2026-11-18

To: Ember.

**Verdict: checks 1, 2, 3, 5, 7 and 8 are accepted as they are.** The identity check (0 of 17,472 rows equal), the convergence replication and the fair paired table are exactly what was needed.

Before the write-up, four small items:
- **A and C** can change a reported number;
- **B** corrects wording;
- **D** adds intervals for the variant.

None of them touches the pre-registered results, and nothing is tuned on the test period.

## A. Differencing tests: run them on the regression errors (check 4)

My instruction was imprecise, and the procedure that followed it has two problems.

1. **What to test.** SARIMAX here is a regression with ARIMA errors, so the differencing question is about the errors, not the raw load. The standard implementation does this: when regressors are supplied, `auto.arima` fits `lm(load ~ regressors)` and passes the residuals to `nsdiffs()` and `ndiffs()` (forecast package, `R/newarima2.R`). Testing the raw load mixes the Fourier and weather-driven pattern into the unit-root question.
2. **Order.** Decide D first, then test d on the series differenced by that D. Your KPSS for d ran on the seasonally differenced series, which assumes D = 1, while Canova–Hansen and OCSB then chose D = 0.

**Do this, on the training period only:**
1. Fit OLS of load on the 13 exogenous columns.
2. Run Canova–Hansen and OCSB (m = 24) on the residuals to choose D.
3. Run KPSS on the residuals, seasonally differenced only if D = 1, to choose d.

**What follows:**
- **If the result is still d = 0, D = 0,** nothing changes. Record it in DECISIONS.md.
- **If it is another order,** that order becomes the post-hoc sensitivity: best AIC within it, run on a CPU kernel.
  - In DEVIATIONS.md, mark the (2,0,2)×(1,0,1,24) results as superseded, with the reason.
  - The write-up reports one sensitivity, not two.

The pre-registered run stays the headline either way.

## B. DATA_SOURCES.md: two corrections (check 6)

**TimesFM 2.5.** "No 2.5-specific corpus list published" is not right.

The model card says it was pretrained on four sources:
- GiftEvalPretrain;
- Wikimedia Pageviews, with a cutoff of November 2023;
- Google Trends top queries, to the end of 2022;
- synthetic and augmented data.

GiftEvalPretrain comes from the GIFT-Eval paper (arXiv 2410.10393, October 2024). So every documented source predates the test period.

Keep half 2 as the strictly clean comparison, because the model was released inside half 1 and the list is high-level. Write the list down rather than "none published".

**Chronos-Bolt.** The ~84B observations and 28 datasets come from the original Chronos paper (Ansari et al. 2024), not from Bolt.

Bolt's model card says it "has been trained on nearly 100 billion time series observations" and does not name the corpus. State that.

Whatever the corpus was, it was fixed before the 2024-12-02 public release. So at most the first month of half 1 could overlap, and nothing suggests it did.

## C. Confirm the context the foundation models actually received (variant)

The TimesFM 2.5 model card's example compiles the model with `ForecastConfig(max_context=1024, max_horizon=256, ...)`. If the variant used that configuration, the "2048 h" TimesFM run saw only 1,024 hours. That alone could explain why longer context did not help TimesFM.

Report, for both runs:
- the `ForecastConfig` values used;
- the input length the model actually received at one origin, logged inside the forecast call.

**If `max_context` was below 2048:**
- Re-run the TimesFM variant with `max_context=2048`. This takes minutes of GPU.
- Keep the first run in DEVIATIONS.md.

Do the same check for Chronos-Bolt, whose limit is 2048: confirm that the full 2048 h reached the model.

## D. Paired differences for the variant

The table shows point estimates only. Claims such as "longer context helps Chronos" or "it hurts TimesFM" need intervals.

For each model, horizon and half, add 2048 h − 168 h with the same block bootstrap as check 5. If C forces a TimesFM re-run, compute these after it.

## E. How the write-up will read (for planning; Claude drafts it with Omid)

- **Headline.** The headline numbers are the 168 h run, matched to the LLM, as pre-registered. The 2048 h run sits beside it as the in-plan variant.
  - No "best context per model" figure: picking per model after seeing test scores is selection on the test set.
- **Claims follow the intervals in check 5:**
  - TimesFM beats SARIMAX without future weather at both horizons in both halves, including half 2.
  - Chronos beats it everywhere except 24 h in half 2, which is a tie.
  - TimesFM and Chronos differ only at 168 h in half 2.
  - The LSTM cannot be told apart from yesterday's load (lag 24) at 24 h.
- **SARIMAX at 168 h** is reported as a property of this specification, not a defect. Checks 1–3 rule out missing inputs, a fallback and convergence.
  - One possible reason can be stated, labelled as a hypothesis: the specification carries the weekly cycle with only three weekly harmonics and a 24 h seasonal period, which smooths weekday/weekend differences. Testing that is not this study's job.
- **LLM intervals.** Observed coverage is 0.381 / 0.406 against the 0.667 that a perfectly calibrated 5-sample range would reach. The claim stays limited to this model and setup.

## F. The GitHub repository

`omidgolchin/nova-load-forecasting` exists on GitHub and is **public** (empty as of 17:10 today). Do not push to it until Omid has made it private, or has decided to publish after Claude reviews the README.

Until then:
- nothing goes public;
- the CV and site say "in progress".

## Then

Send `REPORT_CHECKS_2.md` covering A–D. Claude then writes the conclusions and a README draft with Omid.

## Sources (accessed 2026-11-18)

- forecast package, `auto.arima` (`xx[j] <- residuals(lm(x ~ xregg))` before `nsdiffs()`/`ndiffs()`): https://github.com/robjhyndman/forecast/blob/master/R/newarima2.R
- TimesFM 2.5 model card (training data; `max_context=1024` in the example): https://huggingface.co/google/timesfm-2.5-200m-pytorch
- TimesFM README (2.5 supports up to 16k context): https://github.com/google-research/timesfm
- GIFT-Eval pretraining data (arXiv 2410.10393): https://huggingface.co/datasets/Salesforce/GiftEvalPretrain
- Chronos-Bolt model card ("nearly 100 billion time series observations"): https://huggingface.co/amazon/chronos-bolt-base
