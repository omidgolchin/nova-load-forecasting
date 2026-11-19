# Data sources

Access date for all entries: 2026-11-17 (Step 0 check, docs/process/REPORT_DATA.md).

## Demand — EIA Form 930, PJM Dominion subregion (DOM)

- **Source as used:** Catalyst Cooperative PUDL parquet outputs,
  public S3 bucket `pudl.catalyst.coop`. Step 0 downloaded the nightly
  build (prefix `nightly/`, files dated 2026-11-16); the version was
  then pinned to the stable release (below) on 2026-11-17.
  - `out_eia930__hourly_subregion_demand.parquet` (25.8 MB) — working
    table: `demand_reported_mwh`, `demand_imputed_pudl_mwh`,
    `demand_imputed_pudl_mwh_imputation_code`.
  - `core_eia930__hourly_subregion_demand.parquet` (13.6 MB) —
    reported values only; used to cross-check (identical for DOM).
- **Version (pinned 2026-11-17, DECISIONS #6):** stable PUDL release
  **v2026.11.0** (2026-11-10), taken from the versioned S3 prefix
  `v2026.11.0/`. PUDL's versioned data releases are archived on Zenodo
  under concept DOI 10.5281/zenodo.3653158. The stable release's DOM
  series ends 2026-10-31 04:00 UTC, so the stable release is the
  version used (the nightly fallback in the ruling is not needed).
  - File hash (SHA-256) of
    `out_eia930__hourly_subregion_demand.parquet`:
    `1216ed4f47617e3b7271af9f723cd5a59fab025a4eeb98aec145a8e1688957b2`.
    The nightly and stable copies of this file are byte-identical
    (same hash), and the DOM rows agree everywhere they overlap:
    reported values max abs difference 0.0 MW with NaN positions
    matching exactly, imputed values identical, flag counts identical
    (2,020 `missing_value`, 69 `anomalous_region`, 2 `global_outlier`,
    70,965 unflagged).
  - Hash (SHA-256) of the pinned DOM extract
    `data/raw/dom_hourly_demand.parquet` (regenerated from the stable
    file in the Step 0 extract's shape):
    `40bca6952cf1b2648b3e3319ac96061172253ba59b75cbfc3f77fd30d2fe7352`.
  - PUDL docs:
    https://docs.catalyst.coop/pudl/en/stable/data_sources/eia930.html
- **Licence:** PUDL data CC-BY-4.0 (Catalyst Cooperative). Underlying
  data: US EIA Form 930 hourly balancing-authority reporting
  (subregion demand published for select BAs from 2018-07-01).
- **Coverage as downloaded:** DOM 2018-07-01 05:00 UTC →
  2026-10-31 04:00 UTC, 73,056 hours; usable history from 2019-01-01
  (2018 partial, 39% missing). Local extract:
  `data/raw/dom_hourly_demand.parquet` (gitignored).
- **Alternatives recorded, not used:** EIA API v2 (free key by
  registration; none registered) and EIA-930 six-month bulk CSVs (no
  key). PJM Data Miner 2 hourly metered load, DOM zone — terms per
  PJM's Data License Agreement (Data Miner 2): internal business use;
  members may republish, non-members are prohibited from republishing
  data; 6 requests/min non-members, 600 members; PJM Tools account +
  free API key required.

## Weather — Open-Meteo historical archive (ERA5)

- **Source:** Open-Meteo archive API
  (`archive-api.open-meteo.com/v1/archive`), hourly `temperature_2m`,
  no API key. Verified 2026-11-17 at the three PLAN points — Ashburn
  (39.04, −77.49), Richmond (37.54, −77.44), Norfolk (36.85, −76.29) —
  at both ends of the demand range (Jan 2019 and Oct 2026 samples,
  0 nulls).
- **Licence/attribution:** API data under CC BY 4.0; attribution
  required — include a "Weather data by Open-Meteo.com" link wherever
  the data is displayed. Free API is non-commercial use only
  (<10,000 calls/day); this study is non-commercial.
- **Use in study:** three points averaged with fixed weights 1/3 each
  (PLAN.md).

## Foundation models — release dates and pretraining corpora

Added 2026-11-18 (the review of REPORT_RESULTS, check 6).
Sources accessed 2026-11-18. Only what the sources state is
recorded. TimesFM's model card lists its pretraining sources at
a high level; Chronos-Bolt's card gives a size but does not name
its corpus. Two statements in the first version of this section
were corrected the same day on the review of
REPORT_CHECKS (item B); the corrections are marked below.

### TimesFM 2.5 (google/timesfm-2.5-200m-pytorch)

- **Release:** 2025-09-15 — the google-research/timesfm README's
  "Update - Sept. 15, 2025" entry announces TimesFM 2.5 (200M
  parameters, down from 500M; context up to 16k, up from 2048;
  continuous quantile head).
  https://github.com/google-research/timesfm
- **Published training-data description (corrected 2026-11-18,
  review of REPORT_CHECKS item B):** the TimesFM 2.5 model card
  (google/timesfm-2.5-200m-pytorch, Hugging Face) lists four
  pretraining sources:
  - GiftEvalPretrain — the pretraining set of the GIFT-Eval
    benchmark (arXiv 2410.10393, October 2024);
  - Wikimedia Pageviews, with a cutoff of November 2023;
  - Google Trends top queries, to the end of 2022;
  - synthetic and augmented data.

  Every documented source predates the test period (from
  November 2024). The list is high-level — it names source
  families, not individual series — so whether any EIA-930 /
  Dominion series is among them is not published. (The first
  version of this section said no 2.5-specific corpus list was
  published and fell back on the TimesFM paper's description,
  Das et al., ICML 2024; that was wrong — the model card does
  list the 2.5 sources.)
  https://huggingface.co/google/timesfm-2.5-200m-pytorch
- **Overlap implication:** the release (2025-09-15) falls
  inside test half 1 (Nov 2024 – Oct 2025) and before test
  half 2 (Nov 2025 – Oct 2026). All four documented sources
  predate the test period, so on the published record the
  corpus contains no test-period data at all. Half 2 remains
  the strictly clean comparison, because the model was
  released inside half 1 and the source list is high-level.

### Chronos-Bolt base (amazon/chronos-bolt-base, 205M)

- **Release:** public by 2024-12-02 — AWS Machine Learning Blog,
  "Fast and accurate zero-shot forecasting with Chronos-Bolt and
  AutoGluon" (2024-12-02), announcing Chronos-Bolt in four sizes
  including Base.
  https://aws.amazon.com/blogs/machine-learning/fast-and-accurate-zero-shot-forecasting-with-chronos-bolt-and-autogluon/
- **Published training-data description (corrected 2026-11-18,
  review of REPORT_CHECKS item B):** Bolt's model card states
  it "has been trained on nearly 100 billion time series
  observations" and does not name the corpus. The often-quoted
  corpus description — ~84 billion tokens from 28 publicly
  available datasets comprising ~890,000 univariate series,
  augmented with KernelSynth synthetic series and TSMixup —
  is from the original Chronos paper (Ansari et al., "Chronos:
  Learning the Language of Time Series", Transactions on
  Machine Learning Research, 2024; arXiv 2403.07815) and
  describes Chronos, not Chronos-Bolt; the first version of
  this section attributed it to Bolt, which was wrong.
  https://huggingface.co/amazon/chronos-bolt-base
- **Overlap implication:** whatever Bolt's corpus was, it was
  fixed before the model's public release on 2024-12-02, one
  month into test half 1. At most the first month of half 1
  (November 2024) could overlap, and nothing in the published
  record suggests it did.
