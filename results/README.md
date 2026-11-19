# Results files

All scores use the fixed MASE scale (1,329.73 MW) and the same scoring code. Year 1 is `half = 1`, and year 2 is `half = 2`.

## Main run (pre-registered)

| File | What it holds |
|---|---|
| `forecasts_long.csv` | Every forecast row from every method, with its target, flags and error. |
| `scores_main.csv` | Main table: MASE with its interval, MAPE, peak-hour error, 80% coverage and Winkler score, by method, horizon and year. |
| `scores_paired.csv` | Paired MASE differences against seasonal naive. |
| `scores_paired_fair.csv` | The fair pairs: each foundation model against SARIMAX without future weather, plus TimesFM against Chronos-Bolt and the LSTM against yesterday's load. |
| `chart_mase.png`, `chart_coverage.png` | The README charts. Redraw them with `python scripts/make_charts.py`. |
| `step0_load_by_year.png` | Daily mean and peak load by year, from the data check. |
| `dropped_hours.csv` | Target hours left out of scoring (flagged or missing). |
| `lstm_seed_spread.csv` | The spread of the LSTM forecast across its 3 seeds. |
| `run_record.json`, `run_record_first_run.json` | Model versions, settings and runtimes. |
| `sarimax_topup.csv`, `topup_record.json` | The interval repair for four SARIMAX refits (`DECISIONS.md` #13). |

## Checks and post-hoc work

| File | What it holds |
|---|---|
| `sarimax_convergence.csv`, `sarimax_block_mase_maxiter.csv` | The one non-converged refit (origin 52) and its refit at maxiter 500. |
| `sarimax_alt_selection.csv`, `forecasts_sensitivity.csv`, `scores_sensitivity.csv` | The superseded (d = 0, D = 0) sensitivity. |
| `sarimax_alt2_selection.csv`, `forecasts_sensitivity2*.csv`, `scores_sensitivity2*.csv`, `scores_paired_sensitivity2.csv` | The post-hoc (d = 0, D = 1) SARIMAX shown in the README. |
| `forecasts_context2048.csv`, `scores_context2048.csv`, `scores_paired_variant.csv` | The foundation models with 2,048 h of context. |
| `checks3_item1.md` | Converged AICs for the post-hoc order selection. |
| `checks_run_record.json`, `checks2_kernel_log.txt` | Run records for the checks kernels. |
