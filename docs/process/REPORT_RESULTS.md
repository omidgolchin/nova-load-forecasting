# S04 — First full run: results (stop point 2)

Numbers only, per PLAN.md stop point 2. Interpretation is
Omid's step, not this report's.

## Backtest as run

- Zone / series: PJM balancing authority, DOM subregion, hourly
  demand (MW), PUDL v2026.11.0 pinned extract, SHA-256 verified
  in-notebook (`1216ed4f…`).
- Training from 2019-01-01; test 2024-11-01 → 2026-10-31; halves
  by origin: half 1 = Nov 2024–Oct 2025 (53 origins), half 2 =
  Nov 2025–Oct 2026 (51 origins); origins weekly at 00:00 US
  Eastern, 104 total; horizons 24 h and 168 h.
- MASE scale (fixed, DECISIONS #7): 1,329.73 MW.
- Scoring targets: reported values on unflagged hours only.
  Dropped target hours: half 1 = 98 of 8,903; half 2 = 23 of
  8,567 (results/dropped_hours.csv). Flagged/missing input hours
  filled from 168 h earlier; imputed-fallback fills: 0.
- Forecast rows: 126,672; scored rows: 107,223.
- SARIMAX order (AIC on 2022-11-01 → 2024-11-01, training data
  only): (2,1,2)×(1,1,1,24), AIC 219,741.8. Candidate AICs:
  (1,0,1)(1,1,1,24) 224,678.9; (2,0,1)(1,1,1,24) 220,793.7;
  (1,0,2)(1,1,1,24) 221,095.7; (2,0,2)(1,1,1,24) 230,938.2;
  (1,1,1)(1,1,1,24) 220,554.6; (2,1,2)(1,1,1,24) 219,741.8;
  (1,0,1)(0,1,1,24) 225,030.2; (2,0,1)(1,0,1,24) 257,025.8.

## Main table — MASE [95% block-bootstrap CI], MAPE, peak-hour error, 80% coverage, Winkler

Full precision in results/scores_main.csv; charts in
results/chart_mase.png and results/chart_coverage.png.

### 24 h horizon

| Method | Half | MASE [CI] | MAPE % | Peak err MW | Cov80 | Winkler | n |
|---|---|---|---|---|---|---|---|
| Seasonal naive | 1 | 1.185 [0.941, 1.452] | 10.17 | 1,827 | 0.757 | 7,698 | 53 |
| Seasonal naive | 2 | 1.354 [1.111, 1.602] | 10.51 | 2,013 | 0.671 | 8,677 | 51 |
| Naive (lag 24) | 1 | 0.776 [0.610, 0.949] | 6.58 | 1,168 | 0.739 | 5,379 | 53 |
| Naive (lag 24) | 2 | 0.782 [0.678, 0.886] | 6.15 | 1,208 | 0.720 | 5,086 | 51 |
| SARIMAX oracle | 1 | 0.602 [0.488, 0.721] | 5.06 | 1,022 | 0.714 | 4,025 | 53 |
| SARIMAX oracle | 2 | 0.484 [0.410, 0.568] | 3.72 | 1,080 | 0.838 | 3,213 | 51 |
| SARIMAX no-future | 1 | 0.626 [0.508, 0.744] | 5.26 | 1,068 | 0.684 | 4,205 | 53 |
| SARIMAX no-future | 2 | 0.534 [0.452, 0.625] | 4.12 | 1,149 | 0.801 | 3,499 | 51 |
| LSTM (3 seeds) | 1 | 0.711 [0.532, 0.915] | 5.80 | 1,615 | 0.900 | 4,723 | 53 |
| LSTM (3 seeds) | 2 | 0.896 [0.672, 1.181] | 6.58 | 1,985 | 0.883 | 5,549 | 51 |
| Chronos-Bolt base | 1 | 0.448 [0.351, 0.573] | 3.76 | 983 | 0.790 | 3,147 | 53 |
| Chronos-Bolt base | 2 | 0.535 [0.443, 0.641] | 4.14 | 1,100 | 0.765 | 3,321 | 51 |
| TimesFM 2.5-200M | 1 | 0.472 [0.366, 0.595] | 3.89 | 1,143 | 0.835 | 3,028 | 53 |
| TimesFM 2.5-200M | 2 | 0.482 [0.407, 0.558] | 3.67 | 1,144 | 0.842 | 3,124 | 51 |
| LLM Qwen2.5-7B 4-bit | 1 | 1.048 [0.883, 1.198] | 9.07 | 1,501 | 0.381 | 8,392 | 14 |
| LLM Qwen2.5-7B 4-bit | 2 | 1.415 [1.186, 1.626] | 11.42 | 1,573 | 0.406 | 10,700 | 12 |

### 168 h horizon

| Method | Half | MASE [CI] | MAPE % | Peak err MW | Cov80 | Winkler | n |
|---|---|---|---|---|---|---|---|
| Seasonal naive | 1 | 1.162 [0.922, 1.398] | 10.05 | 1,931 | 0.759 | 8,047 | 53 |
| Seasonal naive | 2 | 1.236 [1.082, 1.390] | 9.69 | 2,146 | 0.729 | 8,028 | 51 |
| SARIMAX oracle | 1 | 1.115 [0.893, 1.353] | 9.76 | 1,739 | 0.795 | 7,193 | 53 |
| SARIMAX oracle | 2 | 1.202 [0.983, 1.423] | 9.36 | 1,952 | 0.814 | 7,756 | 51 |
| SARIMAX no-future | 1 | 1.162 [0.929, 1.412] | 10.17 | 1,815 | 0.778 | 7,513 | 53 |
| SARIMAX no-future | 2 | 1.240 [1.018, 1.465] | 9.65 | 2,015 | 0.806 | 7,970 | 51 |
| LSTM (3 seeds) | 1 | 0.974 [0.792, 1.172] | 8.28 | 1,754 | 0.809 | 5,664 | 53 |
| LSTM (3 seeds) | 2 | 1.004 [0.815, 1.249] | 7.58 | 1,983 | 0.860 | 6,410 | 51 |
| Chronos-Bolt base | 1 | 0.949 [0.759, 1.137] | 8.25 | 1,547 | 0.594 | 6,503 | 53 |
| Chronos-Bolt base | 2 | 1.016 [0.882, 1.159] | 8.04 | 1,730 | 0.640 | 6,972 | 51 |
| TimesFM 2.5-200M | 1 | 0.894 [0.681, 1.106] | 7.59 | 1,523 | 0.748 | 5,810 | 53 |
| TimesFM 2.5-200M | 2 | 0.925 [0.788, 1.079] | 7.18 | 1,671 | 0.774 | 5,752 | 51 |

## Paired MASE differences vs seasonal naive [95% CI]

Full table in results/scores_paired.csv. Selected rows:

| Method | Horizon | Half | Diff [CI] | n |
|---|---|---|---|---|
| Chronos-Bolt | 24 | 1 | −0.737 [−1.004, −0.494] | 53 |
| Chronos-Bolt | 24 | 2 | −0.819 [−1.074, −0.567] | 51 |
| TimesFM | 24 | 1 | −0.713 [−0.973, −0.486] | 53 |
| TimesFM | 24 | 2 | −0.872 [−1.095, −0.654] | 51 |
| SARIMAX oracle | 24 | 2 | −0.869 [−1.090, −0.648] | 51 |
| SARIMAX no-future | 168 | 1 | +0.000 [−0.118, +0.115] | 53 |
| SARIMAX no-future | 168 | 2 | +0.003 [−0.123, +0.137] | 51 |
| LSTM | 168 | 2 | −0.233 [−0.351, −0.093] | 51 |
| LLM | 24 | 1 | −0.059 [−0.196, +0.074] | 14 |
| LLM | 24 | 2 | −0.040 [−0.341, +0.289] | 12 |

## Method run records

- LLM arm: Qwen/Qwen2.5-7B-Instruct, 4-bit NF4, local on the
  Kaggle T4; 26 origins, 24 h, 5 samples per origin at
  temperature 0.8 / top-p 0.9, values scaled by 1/100;
  unparseable share 0.0077 (1 of 130 samples). Prompt, decoding
  and per-origin parse counts are in results/run_record.json.
- LSTM seed spread (per-origin SD of the median forecast across
  the 3 seeds, MW): results/lstm_seed_spread.csv.
- TimesFM: the library reported its version string as "unknown";
  model google/timesfm-2.5-200m-pytorch.
- Chronos-Bolt: amazon/chronos-bolt-base, 168 h context.
- Compute seconds recorded by the kernels: baselines ≈ 0;
  LSTM 109.6; Chronos 21.9; TimesFM 18.5; LLM 1,652.4;
  SARIMAX — see run history below (split across three kernels).

## Run history (all kernels private, Tesla T4, internet on)

| Kernel | Version | What | Runtime |
|---|---|---|---|
| nova-load-backtest | v3 (smoke) | 2 origins, all methods | 3,572.8 s, complete |
| nova-load-backtest | v4 (full) | selection + baselines + SARIMAX origins 0–51, then kernel died in the origin-52 refit | ≈ 7,260 s, error |
| nova-load-backtest-resume | v1 | stopped at the checkpoint assert (v4 outputs not mountable) | ≈ 360 s, error |
| nova-load-backtest-resume | v2 | SARIMAX origins 52–103 + LSTM + Chronos + TimesFM + LLM + scoring | 15,508.9 s, complete |
| nova-load-topup-sarimax-intervals | v1 | origin-52 fit done, kernel died in origin-65 fit | ≈ 2,400 s, error |
| nova-load-topup-sarimax-intervals | v2 | build bug in the fit script (NameError), no fitting | ≈ 120 s, error |
| nova-load-topup-sarimax-intervals | v3 | all four origins fitted, one subprocess each (52: 1,834.5 s; 65: 570.4 s; 78: 523.6 s; 91: 646.1 s); error flag is only the final cell's save_record() NameError, after all outputs were written | ≈ 3,900 s |

Total GPU time across all kernels ≈ 9.2 h (Tesla T4), against
Kaggle's documented free-tier quota of 30 GPU h/week. Spend:
$0.00 (no API used anywhere; the LLM arm ran locally).

SARIMAX fitting time in total ≈ 24,100 s: ≈ 6,900 s in v4
(selection + refits at origins 0/13/26/39, from the checkpoint
log), 13,620.1 s in the resume kernel (refits at 52/65/78/91),
3,574.6 s in the top-up kernel (the same four refits, repeated
for the interval repair).

## Anything unexpected

1. Two kernel deaths (v4 and top-up v1), both during full-memory
   SARIMAX fits on ~65k-hour windows, both with no failure
   message from Kaggle (nbclient DeadKernelError). Checkpointing
   meant no completed forecast was lost either time.
   DECISIONS #11, #15.
2. statsmodels low_memory=True fits return NaN interval bounds
   when forecasting directly from the fit (verified in a local
   controlled test: CI NaN share 1.00 vs 0.00, point forecasts
   identical). This affected exactly the four resume refit
   origins; their intervals come from the top-up kernel, whose
   point forecasts match the resume run's to 0.0000 MW over all
   1,344 repaired rows. DECISIONS #13.
3. The paired table in the resume kernel's first output was
   wrong (MW subtracted from MASE, ≈ −1,576 for every method).
   Scoring-code bug only; the tables in results/ are recomputed
   from forecasts_long.csv with the fixed code, and every
   non-SARIMAX value was verified identical to the kernel's
   main table (max abs diff 0; MAPE 1.8e-15). DECISIONS #14.
4. Two statsmodels ConvergenceWarnings ("Maximum Likelihood
   optimization failed to converge") appear in the resume
   kernel's log; the affected fits are not identified in the
   log, and forecasts were produced for all origins.
5. The LLM arm's 80% intervals cover 0.381 (half 1) and 0.406
   (half 2) of scored hours; its sample min/max at n = 5 is the
   interval by construction (DECISIONS #10 design).
6. Chronos-Bolt's 168 h coverage is 0.594 / 0.640 against the
   0.80 nominal level; all other methods at 168 h are between
   0.729 and 0.860.
7. At 168 h, SARIMAX (both variants) sits at MASE 1.115–1.240,
   i.e. at or above the seasonal-naive values of 1.162 / 1.236;
   the paired differences are +0.000 and +0.003 (no-future) with
   CIs spanning zero.
