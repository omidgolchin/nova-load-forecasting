# Review of REPORT_CHECKS_2 (S04): Claude, 2026-11-18 (night)

To: Ember.

**Verdict: B, C and D are closed.** For A, the seasonal-strength result and the full disclosure are applied as asked.

Two things stand between this round and the write-up:
- the sensitivity's model selection is not settled yet (item 1);
- the fair comparisons need intervals against the sensitivity order (item 2).

Both use training data or saved forecasts only. No test-period tuning.

## 1. The (0, 1) selection: settle it with converged fits

The same model on the same window has two very different AICs:
- **(2,0,2)×(1,1,1,24) on 2022-11-01 → 2024-11-01:** AIC 230,938.2 in the first run's candidate table (REPORT_RESULTS), and 220,663.7 now.
- **The first run's best within (0, 1)** was a different order: (2,0,1)×(1,1,1,24) at 220,793.7.
- **All five selection fits this round** raised a ConvergenceWarning.

So the winner within (0, 1) rests on fits that did not converge, and the margin is about 130 AIC points. The likeliest story is that the first run's (2,0,2) fit stopped at a poor optimum, but that has to be shown, not assumed.

**Do:**
1. Refit the five (0, 1) candidates until each reports `mle_retvals['converged'] == True`. Use more iterations; if that is not enough, start from a Powell or Nelder–Mead fit and finish with L-BFGS.
2. Report all five AICs from converged fits, next to the first-run and this-round values.
3. Explain the 230,938.2 → 220,663.7 difference: settings, start values or data.

**Then:**
- **If (2,0,2)×(1,1,1,24) still wins,** the backtest stands as run.
- **If another order wins,** backtest that order on CPU, report it as the sensitivity, and mark the current (0, 1) results as superseded in DEVIATIONS.md.

Also record whether the first run's pre-registered selection fits warned, if the logs show it. The pre-registered result does not change either way.

## 2. Fair comparisons against the sensitivity order

Use the same block bootstrap as check 5, at both horizons and in both halves:
- TimesFM − SARIMAX (0, 1) without future weather, at 168 h and 2048 h context;
- Chronos-Bolt − SARIMAX (0, 1) without future weather, at both contexts;
- SARIMAX (0, 1) without future weather − seasonal naive.

Add the sensitivity's 80% coverage, Winkler score, MAPE and peak-hour error to the main table. Run this after item 1 settles the order.

## 3. Disclosure: what changes from my last two notes

1. **The timing of the ruling.** In DEVIATIONS.md, record that my ruling on A (DECISIONS #26) was given while the backtest was still running and before any of its results existed. Give both timestamps.
2. **Two of three seasonal criteria pointed to D = 0.** OCSB did, and so did the forecast package's seasonal-strength rule (0.595 / 0.627 against 0.64). The write-up says this plainly.
3. **The superseded (0, 0) result.** I said the write-up reports one sensitivity. Because the week-ahead result turns on the differencing order, the README also mentions the superseded (0, 0) result in one sentence, linking DEVIATIONS.md. It was worse than the pre-registered order at 168 h without future weather (1.239 / 1.291). Without it, readers would see only the alternative that helped SARIMAX. It is not a second headline.
4. **Drop the weekly-harmonics hypothesis** from my item E. The differencing order now explains most of the week-ahead gap, so the README gives no other cause.

## 4. Charts

On the main chart, show the sensitivity SARIMAX as a hollow marker labelled "post-hoc order", next to the pre-registered SARIMAX. The headline stays the pre-registered run.

## 5. Publishing is not your step

The brief's guardrail stands: never publish, post or make the repo public. Omid decides on publishing after he and Claude have finished the README.

Two consequences:
- `omidgolchin/nova-load-forecasting` is public, so your first push there is publication. Push only when Omid says so, or after he makes the repo private.
- Making the Kaggle notebook public is also publishing, and it is also his call.

## Then

Send `REPORT_CHECKS_3.md` covering items 1, 2 and 4. Claude is drafting the README with Omid in parallel. Its pending numbers are marked, and they come from that report.

---

## Item 1 accepted: Claude, 2026-11-19

**Settled.** On converged fits, (2,0,2)×(1,1,1,24) wins within (0, 1) by 779 AIC points, so the (0, 1) backtest stands. The audit also shows the cause: statsmodels' default 50-iteration cap. Data, design and settings were identical across the runs.

**Two disclosures for DEVIATIONS.md and the README:**
1. **The post-hoc order is confirmed on converged fits.** Record the converged AICs and the warm-start L-BFGS procedure: maxiter 1,000, gradient ≤ 4.8 × 10⁻⁴.
2. **The pre-registered selection hit the same cap.** Six of the eight pre-registered selection fits stopped at the 50-iteration cap. The selected order, (2,1,2)×(1,1,1,24), and (1,1,1)×(1,1,1,24) did not. The pre-registered result stands as run.

**Code.** Any future SARIMAX fit in this repo sets an explicit maxiter and checks `mle_retvals['converged']`. Log it in DECISIONS.md.

**Still open:** items 2 and 4.
