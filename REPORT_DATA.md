# Step 0 data check — REPORT_DATA

Date: 2026-11-17. Scope: data verification only; no modelling done.

## Headline

**Hourly demand for PJM's Dominion subregion (DOM) is available from
2019 onward — in fact from 2018-07-01 — via Catalyst Cooperative's PUDL
outputs (EIA Form 930).** The stop rule is not triggered. No fallback
was needed. The usable, near-complete history starts 2019-01-01; the
2018 partial year has a 71-day hole (below) and should not be used as
training history.

## Demand

### Source chosen and why

PUDL nightly parquet outputs on public S3
(`s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/`, files dated
2026-11-16), downloaded 2026-11-17:

| File | Size | Contents |
|---|---|---|
| `out_eia930__hourly_subregion_demand.parquet` | 25.8 MB | reported demand + PUDL-imputed demand + imputation flag, side by side |
| `core_eia930__hourly_subregion_demand.parquet` | 13.6 MB | reported demand only (used as a cross-check) |

The `out_` table is the working table because it carries the reported
series, the imputed series and the per-hour imputation code in one
place. Cross-check: for DOM, the `core_` and `out_` reported values are
identical (max abs difference 0.0 MW; same NaN count, 2,020). Total
download: 39.4 MB. A DOM-only extract (73,056 rows) is saved at
`data/raw/dom_hourly_demand.parquet` (gitignored, like all of
`data/raw/`).

Routes not used, as instructed, recorded for completeness:

- **EIA direct:** the EIA API (v2) requires a free API key obtained by
  registration — no key was registered. EIA also publishes the EIA-930
  six-month consolidated CSVs without a key; PUDL is built from those
  same EIA files, so going direct would add work, not information.
- **PJM Data Miner (fallback 1):** not needed. Its terms (PJM Data
  License Agreement, Data Miner 2) allow internal business use;
  members may republish data but **non-members are specifically
  prohibited from republishing data**; rate limits are 6 requests/min
  for non-members (600 for members); access needs a PJM Tools account
  and a free API key. The non-member republication ban would conflict
  with publishing this study — a further reason to stay on EIA/PUDL.

### Coverage and gaps (DOM, verified from the downloaded files)

- Rows: **73,056 hourly records, 2018-07-01 05:00 UTC to
  2026-10-31 04:00 UTC** (timestamps are end-of-hour, UTC).
- The hourly grid is complete: **0 timestamps absent, 0 duplicates.**
  All gaps are missing *values* inside existing rows.
- **2018 is a partial, poor-quality year:** 1,729 of 4,411 hours
  (39.2%) have no reported value, including one continuous run of
  1,704 hours (2018-07-09 05:00 UTC → 2018-09-18 04:00 UTC, ~71 days).
- **From 2019-01-01 the requirement is met with room to spare:**
  68,645 hours, of which 291 reported values are missing (0.42%) and
  362 hours carry any flag (0.53%).
- Series shape (reported values): median 12,985 MW, 99th percentile
  21,733 MW. The data end (2026-10-31) makes the PLAN's "last 24
  months" test period Nov 2024 – Oct 2026.

### Imputed and anomaly-flagged hours

PUDL's `demand_imputed_pudl_mwh_imputation_code` flags 2,091 of 73,056
hours (2.86%) over the full 2018–2026 span:

| Code | Hours | Where |
|---|---|---|
| `missing_value` | 2,020 | = exactly the NaN count in the reported column; 1,729 of them in 2018, only 291 from 2019 on |
| `anomalous_region` | 69 | 23 hours on each of the Nov 2023, Nov 2024 and Nov 2025 autumn clock-change days |
| `global_outlier` | 2 | 2021-10-19 03:00 and 04:00 UTC, reported as 1.53×10⁹ and 1.04×10⁹ MW — corrupt values, ~5 orders of magnitude too large |

Clock-change artefacts appear in both directions: some fall-back days
show a 25-hour `missing_value` run (Nov 2018, Nov 2019, Nov 2025),
others the 23-hour `anomalous_region` flag above.

An imputed column **does** exist alongside the reported values:
`demand_imputed_pudl_mwh` is complete (0 missing) and is **identical
to the reported value on all 70,965 unflagged hours** — PUDL only
changes flagged hours.

### Handling recommendation

Keep PLAN.md's default: **model on the EIA reported values**
(`demand_reported_mwh`). Specifically:

1. The 2 `global_outlier` hours must never enter as reported values;
   they are corrupt, not extreme weather.
2. Missing hours stay missing (no silent filling) unless PLAN.md is
   amended. Switching flagged/missing hours to the PUDL imputed series
   is a one-line change and the imputed column is already downloaded —
   but it is a PLAN decision for Claude/Omid, flagged here, not taken.
3. Start training history at **2019-01-01** (2018 excluded: partial
   year, 39% missing, 71-day hole). That still leaves ~5.8 years of
   training history before the Nov 2024 test start.

## Growth check

Daily mean and daily peak computed on US Eastern local dates
(EIA timestamps converted UTC → America/New_York), using days with
≥20 reported hours and excluding the 2 corrupt outlier hours:
`results/step0_load_by_year.png`.

| Year | Days used | Mean of daily mean (MW) | Annual peak (MW) |
|---|---|---|---|
| 2018 (Jul–Dec, partial) | 112 | 11,258 | 18,111 |
| 2019 | 364 | 11,687 | 19,803 |
| 2020 | 364 | 11,510 | 20,073 |
| 2021 | 365 | 12,419 | 20,493 |
| 2022 | 363 | 13,118 | 22,415 |
| 2023 | 363 | 13,275 | 22,050 |
| 2024 | 364 | 14,199 | 23,220 |
| 2025 | 364 | 15,403 | 24,957 |
| 2026 (Jan–Oct, partial) | 301 | 16,679 | 25,413 |

**Growth is clearly visible in the plot:** mean daily load rose 31.8%
from 2019 to 2025 (11,687 → 15,403 MW), and the annual peak rose from
19,803 MW (2019) to 24,957 MW (2025) and 25,413 MW (2026). This is
demand growth in the zone; per the brief, data-center load is not
metered separately, so none of this attributes the growth to data
centers.

## Weather

Open-Meteo historical (archive) API, ERA5-based, **no key required** —
verified live on 2026-11-17 for hourly `temperature_2m` at the three
PLAN points:

| Point | Coordinates | Sample weeks checked | Result |
|---|---|---|---|
| Ashburn, VA | 39.04, −77.49 | 2019-01-01→07 and 2026-10-24→31 | 168 + 192 hours, 0 nulls |
| Richmond, VA | 37.54, −77.44 | 2019-01-01→07 | 168 hours, 0 nulls |
| Norfolk, VA | 36.85, −76.29 | 2019-01-01→07 | 168 hours, 0 nulls |

Coverage spans both ends of the demand range. Licence: API data under
**CC BY 4.0**; attribution required — a "Weather data by
Open-Meteo.com" link must sit next to displayed data. The free API is
for non-commercial use only (<10,000 calls/day); this study is
non-commercial research, and the full pull will need only a handful of
calls.

## Licences and versions (summary; full record in DATA_SOURCES.md)

- PUDL data: CC-BY-4.0 (Catalyst Cooperative); underlying EIA-930 data
  is US EIA reporting. Nightly build, S3 files dated 2026-11-16;
  current stable PUDL release v2026.11.0 (2026-11-10) has EIA-930
  updated through the beginning of November 2026.
- Open-Meteo: CC BY 4.0 with attribution (above).
- PJM Data Miner terms recorded above; fallback not used.

## Decisions needed

None to proceed to the notebook build. Two items are flagged for
Claude's Step 0 review, with defaults already in PLAN.md: (1) keep
reported values (default) vs adopt the PUDL imputed series for
flagged/missing hours; (2) training start 2019-01-01 as recommended
above. Spend so far: $0.
