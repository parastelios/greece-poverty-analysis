# Greece Poverty Analysis

A data-driven investigation into why Greek households report the EU's highest
subjective financial strain despite an official (relative-income) poverty
rate that is elevated but not exceptional. Published report:
[The Greek Poverty Paradox](https://claude.ai/code/artifact/81651c87-c049-476b-b481-49adadf42181).

All data is fetched live from the Eurostat API dissemination endpoint; nothing
in `data/` is hand-entered. See `docs/comparability_notes.md` for methodology,
`docs/data_sources.md` for every Eurostat dataset code used and what it
feeds, `docs/publication_strategy.md` for the research/decision log behind
every addition made after the first draft, `docs/project_description.md` for
the original project brief (treated as a north-star spec — the live report
is Version 1, built around its own two research questions; several items in
the brief are intentionally future work, not V1 requirements), and
`docs/todo_plan.md` for the current checkpointed plan and its progress.

## Setup

```bash
pip install -r requirements.txt
```

Python 3.11+ recommended. No API key needed — the Eurostat dissemination API
is public.

## Project structure

```
scripts/            All analysis code, run from inside this directory
  eurostat.py        Generic Eurostat SDMX-JSON API client (fetch() helper)
  eu_membership.py    EU member-state lists by year, for correctly-scoped rankings
  inject_data.py       Utility: embeds data/processed/report_data.json into output/report.html
data/raw/            Raw fetched series, one file per Eurostat dataset/query
data/processed/      Merged/derived tables (master_table.csv, analysis_dataset.csv, etc.)
docs/                Methodology notes and the research/publication-strategy log
output/              report.html (the published artifact) and report_data.json
```

## Run order

Scripts are numbered in dependency order. Run all from inside `scripts/`:

| # | Script | Produces |
|---|---|---|
| 01 | `01_fetch_core.py` | AROP + subjective poverty, all countries |
| 02 | `02_build_master_table.py` | Core Greece/EU master table + rankings |
| 03 | `03_fetch_supplementary.py` | Income, unemployment, deprivation, housing, etc. |
| 04 | `04_merge_all.py` | `analysis_dataset.csv` (the main merged table) |
| 05 | `05_threshold_hypothesis.py` | Real AROP threshold vs. real income |
| 06 | `06_correlations.py` | Level + 1-year-lag correlations |
| 07 | `07_panel_fetch.py` | Cross-country panel for the regression models |
| 08 | `08_panel_regression.py` | First cross-country outlier regression |
| 09 | `09_export_report_data.py` | `output/report_data.json` (run again after any data change) |
| 10 | `10_robustness_correlations.py` | First-difference / detrended correlations |
| 11 | `11_panel_extended.py` | Extended panel (+ PPS income, housing, arrears) |
| 12 | `12_scarring_hypothesis.py` | Peak-to-trough decline vs. residual (exploratory) |
| 13 | `13_anchored_poverty.py` | Approximate 2008-anchored poverty series |
| 14 | `14_spearman_leadlag.py` | Spearman + level-based lead/lag (superseded by 18) |
| 15 | `15_within_country_panel.py` | Two-way fixed-effects (within-country) panel |
| 16 | `16_nested_models.py` | Nested models A-D, balanced-panel check, leave-Greece-out |
| 17 | `17_validate_anchored_method.py` | Anchored-poverty method validated against `ilc_li22` |
| 18 | `18_leadlag_firstdiff.py` | Lead/lag scan on first differences (the one actually used) |
| 19 | `19_leave_one_out_all_countries.py` | Leave-one-out, Model C, all 27 countries |
| 20 | `20_nested_leave_one_out.py` | Leave-one-out repeated for Models A/B/C |
| 21 | `21_arope.py` | AROPE (poverty-or-social-exclusion) series + ranking |
| 22 | `22_arope_snapshot.py` | Cross-country AROPE-vs-subjective snapshot (latest year) |
| 23 | `23_model_E_expectations_wealth.py` | + financial expectations & saving rate |
| 24 | `24_year_over_year_dynamics.py` | Scarring-stock variable, Δ/Δ² diffs, Model F |
| 25 | `25_near_zero_gap_countries.py` | Near-zero AROPE-vs-subjective-gap country comparison |
| 26 | `26_model_scorecard.py` | All six models (A-F) side by side, in- and out-of-sample: `model_scorecard.csv` |
| 27 | `27_multiple_testing.py` | FDR correction on the exploratory test families: `fdr_*.csv` |
| 28 | `28_recovery_trajectory.py` | Years-to-recovery per country, indexed trajectory chart data |
| 29 | `29_migration_brain_drain.py` | Net migration of Greek nationals, cross-country comparison |
| 30 | `30_real_wages.py` | Real wage index (2008=100), 27-country comparison + correlation test |
| 31 | `31_long_term_unemployment.py` | Long-term unemployment rate, correlation + multicollinearity + Model C feasibility test |
| 32 | `32_ltu_model_test.py` | Full model battery: C-LTU scorecard row, 27-country LOO ranking, scarring/expectations interaction checks |
| 33 | `33_youth_unemployment.py` | Youth unemployment: feasibility, correlation, overlap with LTU/migration, model tests (swap and add-to-C-LTU) |
| 34 | `34_wage_adjusted_cost_of_living.py` | Price level vs. wage level by category, wage-adjusted price pressure ranking, time series since 2008 |
| — | `09_export_report_data.py` again | Re-run to pick up any new columns before... |
| — | `inject_data.py` | ...embedding the refreshed JSON into `output/report.html` |

`09_export_report_data.py` and `inject_data.py` are re-run every time the
underlying data changes, not just once — the report's embedded `DATA` object
always reflects the last export.

**Ordering caveat**: `04_merge_all.py` rebuilds `analysis_dataset.csv` from
`master_table.csv` *from scratch* every time it runs — it doesn't merge into
the existing file. `05_threshold_hypothesis.py` computes a derived column
(`gr_arop_threshold_real_idx2008`) and writes it *back into*
`analysis_dataset.csv`. If you re-run `04` after `05` has already run, that
derived column is silently wiped and needs `05` re-run to restore it. Always
run in numeric order (04 before 05) when regenerating from raw data, not
just when adding a genuinely new script.

## Notes

- `eurostat.py`'s `fetch()` is a general-purpose SDMX-JSON parser — reusable
  for any Eurostat dataset, not specific to this project.
- Several scripts fetch cross-country panels independently rather than
  sharing one big pull; this is intentional (each is scoped to what its
  analysis needs) but means re-running everything from scratch takes a few
  minutes of API calls.
- See `docs/publication_strategy.md` for what's been tried, what came back
  null, and what's flagged as not yet done or deliberately out of scope.
