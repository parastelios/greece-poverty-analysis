# Greece Poverty Analysis

A data-driven investigation into why Greek households report the EU's highest
subjective financial strain despite an official (relative-income) poverty
rate, AROP, that is elevated but not exceptional (4th-highest of 27 EU
states). The broader official AROPE measure narrows the gap but doesn't
close it; the report's central new finding is that a country's *cumulative*
excess unemployment since 2009 — not just its current-year labor-market
conditions — closes nearly all of what's left. Published report:
[The Greek Poverty Paradox](https://claude.ai/code/artifact/81651c87-c049-476b-b481-49adadf42181).

All data originates from the Eurostat API dissemination endpoint; nothing
in `data/` is hand-entered. Results reproduce from the archived snapshot in
`data/`; see **Reproducibility status** below for what full re-acquisition
does and does not yet guarantee. See `docs/comparability_notes.md` for methodology,
`docs/data_sources.md` for every Eurostat dataset code used and what it
feeds, `docs/publication_strategy.md` for the research/decision log behind
every addition made after the first draft, `docs/project_description.md` for
the original project brief (treated as a north-star spec — the live report
is Version 1, built around its own two research questions; several items in
the brief are intentionally future work, not V1 requirements), and
`docs/todo_plan.md` for the current checkpointed plan and its progress.

## Data vintage

Every file in `data/` and the published report reflect a **Eurostat API pull
dated 2026-08-19**, except the work-effort series behind Section 11's
salaried-worker findings (`scripts/43_work_effort_squeeze.py`), pulled
**2026-08-20**. Eurostat revises its own
published figures over time (methodology updates, late-reported country
data, benchmark revisions); re-running the pipeline against the live API
on a later date will not reproduce these exact numbers byte-for-byte, even
though nothing in this project's own code will have changed. Treat this
date as the reference vintage for any specific number quoted in the report
or in the docs.

## Reproducibility status

**All published results reproduce from the archived source-data snapshot in
`data/raw/` and `data/processed/`.** Verify this at any time, offline, in
seconds:

```bash
make verify
```

That runs `scripts/verify_build.py`, which checks every headline number quoted
in the three published documents against what the pipeline actually produced
(36 checks: headline gaps, the gap-closing ladder, scorecard residuals and
ranks, FDR survivor counts, nested-selection results, the work-effort figures,
and the placebo inference). It exits non-zero on any mismatch.

**Full from-scratch re-acquisition is now scripted but not yet byte-exact.**
An external clean-room review found that a set of raw inputs were read by
numbered scripts but produced by none — they had been fetched ad hoc during
development. `scripts/00_fetch_missing_raw.py` closes that gap: it re-fetches
all fifteen from their documented Eurostat datasets and filters. Run in CHECK
mode (the default, writes nothing) it reports agreement against the archive:

```bash
make fetch
```

Current status, measured by `make fetch` and reported precisely rather than
rounded up: **13 of 15 files are byte-identical to the archive on every
overlapping row.** Two are not:

| File | Status | Detail |
|---|---|---|
| `real_wage_idx2008` | differs | 58.1% of rows byte-identical, 99.6% within 0.05, max difference 0.168 on an index near 100. It is a derived series (compensation deflated by HICP, rebased to 2008), so small floating-point and revision differences accumulate. Also now covers more countries than the archive. |
| `panel_gdp_pps` | differs materially | The archive stored it rounded to the nearest 100 PPS while the API now returns one decimal; ~3% of rows have since been revised by Eurostat. It feeds only the alternative `M3_swap_to_GDP_PPS` specification in `11_panel_extended.py` — every headline model uses `aic_pps_pc_k` instead — so it touches no published result. |

Writing this acquisition step surfaced three filter choices that had been
undocumented precisely *because* the step was missing, each pinned down by
diffing a fresh fetch against the archive: `statinfo=MED_EI` on both `ilc_li02`
and `ilc_li09` (without it the fetch silently returns both mean- and
median-based rows, doubling the table), and `s_adj=NSA` rather than `SA` on
`ei_bsco_m`.

**A true end-to-end reproduction is now available as its own target:**

```bash
make reproduce
```

This exports the committed tree into a temporary directory, re-fetches the raw
inputs there *for real* (`fetch-write`), runs the full build, and verifies —
leaving this working copy completely untouched. It is the target that answers
"does this rebuild from nothing?", where `make verify` only answers "do the
documents match the data currently on disk?".

**Build order is not filename order.** `04_merge_all.py` rebuilds
`analysis_dataset.csv` from scratch, and two later-numbered scripts write
derived columns back into it (`05` → the real AROP threshold, `21` → AROPE),
while `10_robustness_correlations.py` *reads* AROPE as one of its 19 variables.
Plain numeric order would run `10` before `21` and silently produce an
18-variable correlation table. The Makefile hoists the write-back scripts to
run immediately after `04`; if you run scripts by hand, do the same.

## Setup

```bash
pip install -r requirements.txt
```

Python 3.11+ recommended (dependencies pinned to exact versions in
`requirements.txt` for reproducibility). No API key needed — the Eurostat
dissemination API is public.

## Project structure

```
scripts/            All analysis code, run from inside this directory
  eurostat.py        Generic Eurostat SDMX-JSON API client (fetch() helper)
  eu_membership.py    EU member-state lists by year, for correctly-scoped rankings
  inject_data.py       Utility: embeds data/processed/report_data.json into output/report.html
data/raw/            Raw fetched series, one file per Eurostat dataset/query
data/processed/      Merged/derived tables (master_table.csv, analysis_dataset.csv, etc.)
docs/                Methodology notes and the research/publication-strategy log
output/              report.html (the published artifact), report_data.json,
                     narrative_companion.html (a narrative companion piece —
                     the same evidence base, told as one continuous story
                     rather than a section-by-section technical report;
                     self-contained, not regenerated by any script), and
                     academic_paper_draft.html (a formal working-paper draft —
                     same Part I/II evidence base in academic register, plus
                     a three-part Discussion (§7.1 a methodological caution
                     on using AROP alone in prolonged-crisis contexts, §7.2
                     what the measurement and outlier results suggest
                     together, §7.3 situating the findings against the
                     design and record of Greece's three bailout programs);
                     self-contained, not regenerated by any script, and not
                     yet submission-ready — see the open items listed in its
                     own §10)
```

All three outputs are restructured around the same 9-point spine (agreed
2026-08-20, see `docs/publication_strategy.md`): (1) the AROP puzzle, (2)
the shrinking ruler (moving threshold), (3) AROPE as a secondary bridge, not
a replacement primary measure, (4) Part II as decomposing AROPE's intuition
rather than reconstructing it, (5) a gap-closing ladder from the raw AROP
gap down to the final model, (6) sustained excess unemployment over roughly
the past decade as the main new mechanism (with long-term unemployment and
a closely related wage-duration measure as jointly supporting evidence —
see `docs/publication_strategy.md`, "Second-round methodological review,"
for why this isn't framed as one uniquely identified variable), (7) corroborating
evidence that the paradox persists even among salaried workers, in a country
that records the EU's longest working hours (across all employed people and
among full-time workers; salaried employees alone rank 7th of 27) at its
lowest purchasing-power-adjusted hourly pay (a cross-country structural
association, deliberately kept off the scorecard — see
`docs/publication_strategy.md`, "Work-effort-squeeze checkpoint"), (8) a
robustness section testing whether the whole gap could instead reflect
country-specific reporting style rather than material conditions, and (9) a
Discussion generalizing the AROP-in-crisis-contexts lesson beyond Greece
specifically.

## Run order

Scripts are numbered in dependency order. Run all from inside `scripts/`:

| # | Script | Produces |
|---|---|---|
| 00 | `00_fetch_missing_raw.py` | Re-acquires the 15 raw inputs that previously had no producing script. CHECK mode by default (compares against the archive, writes nothing); `--write` to actually overwrite `data/raw/` |
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
| 35 | `35_housing_tenure.py` | Housing cost overburden and tenure distribution by ownership/rental status, cross-country and Greece-only correlation, model test against existing housing_cost_overburden |
| 36 | `36_income_inequality.py` | S80/S20 and Gini: feasibility, correlation, overlap with existing predictors, model test against Model C-LTU |
| 37 | `37_arop_snapshot.py` | Cross-country AROP-vs-subjective snapshot (latest year) — the AROP counterpart to script 22, used as the primary headline comparison |
| 38 | `38_cumulative_hardship.py` | Cumulative-hardship checkpoint: AROP-threshold fetch (NAC currency), full-history unemployment refetch, cumulative/duration/rolling/decay batteries, selection-leakage check, FDR correction — all outputs listed in `docs/data_sources.md` |
| 39 | `39_age_breakdown_arope.py` | Age-breakdown checkpoint: AROPE/AROP/deprivation/low-work-intensity by age group, shift-share decomposition, sex and household-composition breakdown for 65+, Greece vs EU27 — see `docs/data_sources.md` |
| 40 | `40_reporting_style_robustness.py` | Reporting-style checkpoint, first pass: pre-crisis level ranking, raw gap widening, diff-in-differences, out-of-sample residual stability, cross-indicator comparison (life satisfaction vs. financial measures) |
| 41 | `41_reporting_style_robustness_v2.py` | Robustness battery: EU-SILC coverage audit + three balanced panels, event study, alternative treatment dates, country-placebo/randomization inference, leave-one-control-out, periphery-only comparison, two synthetic controls |
| 42 | `42_reporting_style_robustness_v3.py` | Standardized (z-score) cross-indicator deviations; residual-trend sensitivity across three model specifications |
| 43 | `43_work_effort_squeeze.py` | Work-effort squeeze: salaried/self-employed/all-employed hardship decomposition, hours vs. hourly compensation, FDR-corrected 9-candidate battery, within-country robustness (country FE, first differences), preview figures |
| 44 | `44_nested_selection_validation.py` | Nested selection validation: the full 18-candidate screening repeated independently inside all 27 leave-one-country-out folds |
| — | `verify_build.py` | Checks all published headline numbers against pipeline outputs (36 checks); run by `make verify` |
| — | `09_export_report_data.py` again | Re-run to pick up any new columns before... |
| — | `inject_data.py` | ...embedding the refreshed JSON into `output/report.html` |

`09_export_report_data.py` and `inject_data.py` are re-run every time the
underlying data changes, not just once — the report's embedded `DATA` object
always reflects the last export.

**Ordering caveat**: `04_merge_all.py` rebuilds `analysis_dataset.csv` from
`master_table.csv` *from scratch* every time it runs — it doesn't merge into
the existing file. Two other scripts compute a derived column and write it
*back into* `analysis_dataset.csv` rather than into their own separate
output file: `05_threshold_hypothesis.py` (`gr_arop_threshold_real_idx2008`)
and `21_arope.py` (`gr_arope`, `eu_arope`, `gr_eu_arope_gap`). If you re-run
`04` at any point after either of those has already run — not just when
first adding a new script, but any time `04` is re-run for *any* reason
(a new raw file, a bugfix, a routine data refresh) — their columns are
silently wiped from `analysis_dataset.csv` and need re-running to restore.
This bit in practice: several P2-round reruns of `04` this project went
through re-ran `05` (per the documented order below) but not `21`, leaving
`gr_arope`/`eu_arope` null in the committed `analysis_dataset.csv` and
`report_data.json` for an extended stretch — the Section 3 "four measures
of poverty" chart's AROPE line was empty in the published report the whole
time, even though the surrounding text discussed it. The snapshot AROPE
chart (Section 1) was unaffected, since it reads a separate file
(`arope_subjective_snapshot_2025.csv`) not touched by this issue. Caught by
an independent full pipeline rerun, not by this project's own review passes
directly — worth remembering next time `04` changes: **re-run every
write-back script (currently 05 and 21), not just the one you have in mind,
and check `analysis_dataset.csv` for its expected columns afterward.**
Always run in full numeric order (01 through the highest script) when
regenerating from raw data end to end, which sidesteps this by construction
since every write-back script's number is higher than 04's.

**Raw-file shape caveat**: `04_merge_all.py`'s generic merge assumes one
row per `geo`/`time` pair in every raw CSV it picks up from `data/raw/`.
Files with an extra dimension (e.g. a `tenure` or `category` column, with
several rows per country/year) are detected and skipped automatically —
they're meant to be consumed directly by their own dedicated script, not
through the generic cross-country merge. If you add a new multi-dimensional
raw file and want it in the generic merge, filter or pivot it to one row
per `geo`/`time` first (see `real_wage_idx2008.csv` or
`panel_long_term_unemployment.csv` for the expected shape).

## Notes

- `eurostat.py`'s `fetch()` is a general-purpose SDMX-JSON parser — reusable
  for any Eurostat dataset, not specific to this project.
- Several scripts fetch cross-country panels independently rather than
  sharing one big pull; this is intentional (each is scoped to what its
  analysis needs) but means re-running everything from scratch takes a few
  minutes of API calls.
- See `docs/publication_strategy.md` for what's been tried, what came back
  null, and what's flagged as not yet done or deliberately out of scope.
