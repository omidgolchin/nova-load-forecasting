# Ruling on A: Claude, 2026-11-18 (evening)

**Ruling: keep (d = 0, D = 1) as the one post-hoc sensitivity.** Let the running backtest finish.

On the regression residuals, Canova–Hansen gives D = 1 and OCSB gives D = 0. My instruction named both tests and set no tie-break, so that gap is mine. D = 1 is the defensible choice, for two reasons that do not depend on the sensitivity's result:

1. **The residuals still carry most of the daily cycle.** No deterministic regressor has a 24 h period: the weekly Fourier terms have periods of 168, 84 and 56 h. The degree-hours carry only the weather-driven part of the daily shape. A seasonal difference at lag 24 is what makes these errors plausibly stationary.
2. **The d-step only works under D = 1.** KPSS on residuals that keep a strong daily cycle is not a valid test, so d can only be chosen coherently after the lag-24 difference.

**Supporting context, not a new decision rule.** The forecast package's current default seasonal test is neither OCSB nor Canova–Hansen. It is seasonal strength, with D = 1 when strength exceeds 0.64 (`nsdiffs()`, `R/unitRoot.R`). Report the seasonal-strength value of the training residuals beside the two test results. It takes CPU seconds. The ruling stands whatever it shows.

**Disclosure.**
- **DEVIATIONS.md:** record both tests, their values, the seasonal strength, the two reasons above, and the fact that OCSB alone would have pointed to D = 0.
- **The write-up's sensitivity note:** one sentence saying the same.
- **The (2,0,2)×(1,0,1,24) results:** they stay in DEVIATIONS.md, marked as superseded.

**C and D.** Both are accepted. The context check settles my concern: `max_context=2048` was in the code, and the replay reproduced the saved forecasts. The write-up will say:
- longer context helped Chronos in half 2 at both horizons, and is unproven in half 1;
- for TimesFM, longer context was worse only at 24 h in half 1, and the other differences are ties.

Source (accessed 2026-11-18): forecast package, `nsdiffs(test = c("seas", "ocsb", "hegy", "ch"))` and `seas.heuristic(x) > 0.64`: https://github.com/robjhyndman/forecast/blob/master/R/unitRoot.R
