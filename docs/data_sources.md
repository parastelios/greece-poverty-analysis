# Data sources

Every number in this project traces to the Eurostat API dissemination
endpoint, fetched via `scripts/eurostat.py`'s generic `fetch()` client —
nothing is hand-entered. This document lists every Eurostat dataset code
used, grouped by what it feeds, with the script that fetches it where one
exists. See `docs/comparability_notes.md` for definitions, breaks, and
reference-year caveats on the series below, not repeated here.

## Part I — Greece-only time series (2003–2025)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `ilc_li02` | AROP (at-risk-of-poverty rate) | `rskpovth=B_60`, `statinfo=MED_EI` | `01_fetch_core.py` |
| `ilc_mdes09` | Subjective poverty ("ability to make ends meet") | `lev_diff=DIF`+`GRT` | `01_fetch_core.py` |
| `ilc_sbjp01` | Eurostat's own official subjective-poverty product | population-weighted | used to verify `ilc_mdes09`-derived series (Methods) |
| `ilc_li01` | AROP threshold in euros | `statinfo=MED_EI`, `rskpovth=B_60`, `hhcomp=A1` | `05_threshold_hypothesis.py` |
| `ilc_li22` | Eurostat's official anchored-poverty rate (2019 base) | `rskpovth=B_60` | `17_validate_anchored_method.py` (validation only) |
| `ilc_peps01` / `ilc_peps01n` | AROPE, legacy / revised definition | spliced at 2020/2021 | `21_arope.py` |
| `ilc_mddd11` | Severe material deprivation, legacy 9-item | 2003–2020 | `03_fetch_supplementary.py` |
| `ilc_mdsd11` | Severe material & social deprivation, new 13-item | 2021 onward (usable ~2015+) | `03_fetch_supplementary.py` |
| `ilc_mdes04` | Cannot face an unexpected expense | | `03_fetch_supplementary.py` |
| `ilc_mdes05` | Households in arrears | | `03_fetch_supplementary.py` |
| `ilc_mdes01` | Cannot keep home adequately warm | | `03_fetch_supplementary.py` |
| `ilc_lvho07a` | Housing cost overburden rate | | `03_fetch_supplementary.py` |
| `sdg_08_10` | Real GDP per capita | `unit=CLV20_EUR_HAB`, `na_item=B1GQ` | `03_fetch_supplementary.py`, `07_panel_fetch.py`, `12_scarring_hypothesis.py` |
| `tepsr_wc310` | Real household disposable income (index, 2008=100) | `na_item=B6G_R_HAB_2008` | `03_fetch_supplementary.py` |
| `sdg_08_30` | Employment rate, 20–64 | `indic_em=EMP_LFS` | `03_fetch_supplementary.py` |
| `une_rt_a` | Unemployment rate | `age=Y15-74`, `unit=PC_ACT` | `03_fetch_supplementary.py`, `07_panel_fetch.py` |
| `prc_hicp_aind` | HICP inflation | `coicop=CP00` (headline) / `CP01` (food) / `CP04` (housing & energy) | `03_fetch_supplementary.py` |
| `nama_10_pc` | Household consumption per capita | `na_item=P31_S14_S15`, `unit=CLV10_EUR_HAB` | `03_fetch_supplementary.py` |
| `earn_mw_cur` | Minimum wage (nominal, EUR/month) | S1 half-year taken as annual reference | `03_fetch_supplementary.py` |

## Part II — Cross-country panel (28 EU countries, 2015–2024)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `une_rt_a` | Unemployment rate | as above | `07_panel_fetch.py` |
| `sdg_08_10` | Real GDP per capita | as above | `07_panel_fetch.py` |
| `ilc_mdsd11` | Severe material & social deprivation | as above | `07_panel_fetch.py` |
| `nama_10_pc` | AIC per capita, PPS-adjusted | `na_item=P41` (household actual individual consumption) | fetched ad hoc; see note below |
| Housing cost overburden, arrears, unexpected-expense inability (panel versions) | same concepts as the Greece-only series above, multi-country | presumed `ilc_lvho07a` / `ilc_mdes05` / `ilc_mdes04` | fetched ad hoc; see note below |
| Household debt-to-income | `panel_debt_to_income.csv` | exact code not preserved | fetched ad hoc; see note below |
| AROP before social transfers | `panel_arop_before_transfers.csv`, used to derive `transfer_effect` | exact code not preserved | fetched ad hoc; see note below |

**Traceability note**: the six panel files above (AIC-PPS, GDP-PPS, panel
housing/arrears/unexpected-expenses, debt-to-income, and pre-transfer AROP)
were fetched via the same `eurostat.py` client during earlier analysis
sessions, but the exact fetch commands weren't saved as a numbered script —
only the resulting CSVs in `data/raw/` persist. The concepts and general
Eurostat source are documented in the report's Methods section; the specific
dataset codes for debt-to-income and pre-transfer AROP specifically are not
independently re-verifiable from this repo alone. Re-deriving and saving
proper fetch scripts for these (so every raw file has a reproducible origin,
not just the ones fetched since script 03 onward) is flagged as a small
follow-up, not yet done.

## Section 10/11 additions (scarring, expectations, saving rate)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `sdg_08_10` | Real GDP per capita, 2008–2024 (for the scarring-stock variable) | | `12_scarring_hypothesis.py` (peak-to-trough), re-fetched in `24_year_over_year_dynamics.py`'s merge |
| `ei_bsco_m` | Household financial expectations (consumer survey) | `indic=BS-FS-NY`, "financial situation over next 12 months" | fetched ad hoc for `23_model_E_expectations_wealth.py` |
| `tec00131` | Household gross saving rate | | fetched ad hoc for `23_model_E_expectations_wealth.py` |

## P1a/P1b additions (recovery trajectory, migration)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `sdg_08_10` | Real GDP per capita, 2008–2024 (recovery trajectory: current-peak distance and separately, worst-drawdown/recovery-time detection) | | `28_recovery_trajectory.py` |
| `migr_emi1ctz` | Emigration flow | `citizen=NAT`, `agedef=COMPLET`, `unit=NR`, `sex=T` | `29_migration_brain_drain.py` |
| `migr_imm1ctz` | Immigration flow (return migration of nationals) | same params as above | `29_migration_brain_drain.py` |
| `demo_pjan` | Population (rate denominator) | `sex=T`, `age=TOTAL` | `29_migration_brain_drain.py` |
| `demo_gind` (`MIGTRT`) | Eurostat's headline "net migration rate" | **checked and rejected** — see note below | `29_migration_brain_drain.py` |

**Rejection note**: `demo_gind`'s `MIGTRT`/`MIGT` indicators are officially
"net migration plus statistical adjustment" — a residual (population change
minus natural change) that absorbs census and population-register
revisions, not just real migration. For Greece it shows strongly *positive*
net migration every year 2011–2024, directly contradicting Greece's own
falling population and the well-documented emigration pattern — clear
evidence it's dominated by statistical noise for this country. Caught by
cross-checking against `GROW`/`NATGROW` before use. `migr_emi1ctz` /
`migr_imm1ctz` (actual flow registrations) used instead; all 27 EU
countries report into them with near-full 2008–2024 coverage.

## Non-Eurostat sources (corroboration only, not modeled)

These are cited in the literature/discussion section as independent
corroboration — none are merged into any model or panel.

- **diaNEOsis / University of Macedonia** (2016 opinion survey): financial-pessimism and basic-needs-difficulty figures, PDF `ftwxeia2_version_060616_2.pdf`.
- **diaNEOsis** (Jan 2026 housing article, summarizing an IOBE/Vettas study): housing-cost-share and arrears figures.
- **Mantés & Marinakis / Greekonomics.gr** (2025 report, MIT-licensed companion code at `github.com/AMantes/Greekonomics`): "Bottom-10" comparator income/housing/healthcare figures.
- **Greece in Figures** (`greeceinfigures.com`): independently-reported AROPE/subjective-poverty headline figures, matched against this project's own Eurostat pull.
- **Andriopoulou, Kanavitsa & Tsakloglou** (2019/2020): microdata-based anchored-poverty comparison — full citation in report Methods.
- **Gourinchas, Philippon & Vayanos** (2016, VoxEU/CEPR): "compound crisis" framing for the recovery-trajectory section.
- **European Stability Mechanism** explainer: domestic drivers of the Greek crisis (cheap euro-era borrowing, weak tax administration, 2009 data-misreporting revelation).
- **OECD** (2026, "A Review of Greek Emigrants" / "Talent Abroad"): return-migration flow numbers and age/education profile of returnees (census-based — not this project's own Eurostat flow data).
- **Kathimerini** (3 July 2026): public-facing coverage of the same OECD report, cross-checked against this project's own migration figures.
- **Greekonomics.gr** brain-drain article (staff, 3 Aug 2026, distinct from the Mantés & Marinakis report): stock-based ("brain drain reversal premature") counterpoint to this project's own flow-based finding.
- **Labrianidis & Vogiatzis** (2013): pre-crisis skilled-emigration/crisis mutual-reinforcement argument.
- **Pratsinakis** (2022, open-access book chapter, *Challenging Mobilities... The Case of Greece*, IMISCOE/Springer): "brain drain is an incomplete frame" argument, survey stats (27% "enforced," 43% "always wanted to leave," two-in-three crisis emigrants university-educated), and a third independent shape check on the emigration timeline (peak 2012, plateau through late 2010s per this source and OECD, vs. a steadier decline in this project's own Eurostat extraction — reported as an open, unresolved discrepancy in the report itself). PDF supplied by the user at `docs/978-3-031-11574-5.pdf`.
- **Ervasti, Kouvo & Venetoklis** (2019, *Social Indicators Research*): institutional vs. interpersonal trust during the crisis — the crisis damaged the former, not the latter.
- **OECD** (2026, "Survey on Drivers of Trust in Public Institutions: Greece"): the load-bearing trust source — pre-crisis baseline (44% average, not high), the 2012 collapse to 7%, and the puzzling 2023-2025 renewed decline despite economic recovery.
- **Economou et al.** (2014, *Social Science & Medicine*): trust/social-capital and mental-health link during the crisis — cited lightly.

## Non-Eurostat data considered and rejected or deferred

- **Institutional trust (Eurobarometer/ESS/OECD)**: feasibility checked
  directly against Eurostat's own catalogue (see `publication_strategy.md`,
  P1c) — Eurostat's entire institutional-trust holdings are one dataset
  (`ilc_pw03b`) covering a single year, 2013, which fails the
  comparable-years bar outright. Not modeled as a result. Added instead as
  literature-backed narrative context (Section 11 and the literature
  section), using the three non-Eurostat sources above. A future version
  that expands beyond Eurostat's own API could revisit this.
- Income inequality (Gini/S80:S20), housing tenure, real wages, long-term
  unemployment, youth unemployment, and wage-adjusted cost-of-living
  pressure: all named in `docs/project_description.md` and have since
  been fetched and integrated — see the dedicated sections below and
  `docs/publication_strategy.md` for the full log of each. P2 is
  complete; see `docs/todo_plan.md` for what remains outside its scope.

## P2e addition (wage-adjusted cost-of-living pressure)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `prc_ppp_ind_1` | Comparative price level indices, EU27=100 | `indic_ppp=PLI_EU27_2020`, `ppp_cat18` (category code) | `34_wage_adjusted_cost_of_living.py` |
| `nama_10_lp_ulc` | Nominal compensation per employee (wage benchmark, reused from P2a) | `na_item=D1_SAL_PER`, `unit=EUR` | `34_wage_adjusted_cost_of_living.py` |

Wage-adjusted price pressure = price level (EU=100) ÷ wage level (Greece's
nominal compensation per employee as % of the EU27 average) × 100. Full
27-country coverage for the broad "overall household consumption" category
(`ppp_cat18=A01`) back to 2000; the narrower categories used in the report
(food, housing/utilities, transport, restaurants, communication) have full
27-country coverage for only 2022–2024 — checked directly against
Eurostat, not assumed, and documented as a real feasibility constraint in
report Methods ("Wage-adjusted price pressure: source, method, and
limits"). On raw price level Greece ranks only 18th-most-expensive of 27
on overall consumption; on wage-adjusted pressure it ranks 1st. Descriptive
only — the category-level data's short time span rules out a proper
cross-country panel-regression test, and the overall-consumption series
that does have enough years shows the same level-only correlation pattern
(r=0.70 level, not significant on first differences) that real wages
already showed without adding independent model power. Not added to the
scorecard.

## P2b addition (long-term unemployment)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `une_ltu_a` | Long-term unemployment rate (12mo+, % of active population) | `sex=T`, `age=Y15-74`, `unit=PC_ACT`, `indic_em=LTU` | `31_long_term_unemployment.py` |

Full 27-country coverage, 2009&ndash;2024 (Eurostat does not publish this
series further back). Unlike real wages, this variable became a genuine
scorecard-changing finding: swapped in for headline unemployment in the
Section 10 model (as Model C-LTU, not simply added alongside it — the two
are collinear enough, r=0.91 panel-wide, that adding both destabilizes
headline unemployment's own coefficient), it cuts Greece's out-of-sample
gap from 11.6 to 3.9 points and moves Greece from the largest unexplained
outlier in the EU to 6th-largest. See report Methods ("Long-term
unemployment: source, method, and why it replaces rather than adds to
headline unemployment") for the full multicollinearity check, coefficient
stability test, and interaction checks against the scarring-stock and
financial-expectations variables.

## P2a addition (real wages)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `nama_10_lp_ulc` | Nominal compensation per employee | `na_item=D1_SAL_PER`, `unit=EUR` | `30_real_wages.py` |
| `prc_hicp_aind` | HICP price index (deflator) | `coicop=CP00`, `unit=INX_A_AVG` | `30_real_wages.py` |

Real wages = nominal compensation per employee deflated by the HICP index,
rebased so each of the 27 EU countries' own 2008 value = 100
(`real_wage_idx2008`). 2000–2024 coverage. Checked for multicollinearity
against the existing panel predictors (PPS income, real GDP, scarring stock
— all r&le;0.33) and tested as a candidate cross-country model addition
before deciding not to add it to the scorecard; see report Methods
("Real wages: source, method, and why it isn't a scorecard model") for the
full test result.

## P2c addition (youth unemployment)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `une_rt_a` | Youth unemployment rate (15-24, % of youth labor force) | `sex=T`, `age=Y15-24`, `unit=PC_ACT` | `33_youth_unemployment.py` |

Full 27-country coverage, 2009&ndash;2024. Note the denominator: this is
the share of the youth *labor force* unemployed, not the share of the
youth *population* (Eurostat's separate `yth_empl_090` product, not used
here). Strongly correlated with subjective poverty on its own (level
r=0.71, first-difference r=0.79, detrended r=0.81 — survives FDR
correction) but overlaps so heavily with long-term unemployment (r=0.85
panel-wide, r=0.99 for Greece's own series) that it adds no independent
explanatory power once long-term unemployment is already in the
cross-country model: replacing headline unemployment with youth
unemployment alone leaves Greece the largest unexplained outlier
(R&sup2; 0.899, gap 10.8, rank unchanged at 1st of 27), and adding it on
top of Model C-LTU changes almost nothing (its own coefficient p=0.815).
**Not added to the scorecard as a result.** Kept as supporting descriptive
context in the migration/brain-drain subsection (its 2013 peak fell
within a year of the 2012 emigration peak) and documented in full in
report Methods ("Youth unemployment: checked, strongly correlated, and
not a scorecard model").

## Housing tenure addition (2026-08-21)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `ilc_lvho07c` | Housing cost overburden rate by tenure status | `unit=PC`, `tenure=OWN_L/OWN_NL/RENT_FR/RENT_MKT/TOTAL` | `35_housing_tenure.py` |
| `ilc_lvho02` | Distribution of population by tenure status | `rskpovth=TOTAL`, `hhcomp=TOTAL`, `unit=PC` | `35_housing_tenure.py` |

Full 27-country coverage on both, 15–22 years depending on country. The
`ilc_lvho07c` "TOTAL" row exactly matches the `housing_cost_overburden`
variable already used throughout the report and the cross-country model —
checked directly. Greece's mortgage-free-owner overburden rate (25.7% in
2024) is the EU's highest by a wide margin (next: Sweden, 14.0%; typical
EU range 1–7%) — homeownership does not shield Greek households from
housing-cost pressure the way it does almost everywhere else in the EU.
Renters are still worse off (37.4%), but the owner-renter gap is one of
the EU's narrowest (Greece ranks 22nd of 27) precisely because owners are
unusually burdened too. Correlates strongly with subjective poverty
(Greece-only over time, r=0.90; cross-country single-year, r=0.66) but is
highly collinear with the `housing_cost_overburden` variable already in
Model C-LTU (r≈0.9) and adds no independent explanatory power when tested
— not added to the scorecard. Note: the renter-specific subseries show
implausible year-to-year swings in Greece's pre-2021 data, consistent with
a small underlying renter subsample historically — the report relies on
the stable 2022–2024 window for the by-tenure comparison, not the full
historical series. Full detail in report Methods ("Housing tenure: source,
method, and why it's descriptive depth, not a new model variable").

## Income inequality addition (2026-08-21) — final P2 item

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `ilc_di11` | S80/S20 income quintile share ratio | `age=TOTAL`, `sex=T`, `unit=RAT` | `36_income_inequality.py` |
| `ilc_di12` | Gini coefficient, equivalised disposable income | `age=TOTAL`, `statinfo=GINI_HND` | `36_income_inequality.py` |

S80/S20 has full 27-country coverage, 2003–2024; Gini's age-broken-down
series is shorter, 2014–2024 only — checked directly against Eurostat,
not assumed. Greece is elevated but not extreme on either measure (6th of
27 in 2024). Level correlation with subjective poverty is weak and does
not survive FDR correction (r=0.15, adjusted p=0.54) — the only variable
in the correlation table with a non-significant level reading. Added to
Model C-LTU, it contributes no independent explanatory power (R² barely
moves, Greece's out-of-sample gap gets worse, coefficient not
significant). **Not added to the scorecard, and deliberately given no
dedicated subsection or chart** — the finding here is the negative one:
Greece's subjective-poverty gap is not mainly an inequality story. Full
detail in report Methods ("Variables tested but not central to the
story").

## AROP cross-country snapshot addition (2026-08-20)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `ilc_li02` | AROP (reused from Part I) | as above | `37_arop_snapshot.py` |

Mirrors `22_arope_snapshot.py` exactly but for AROP instead of AROPE, producing
`arop_subjective_snapshot_2025.csv` (27 countries + EU aggregate). Built to
support the AROP/AROPE Core Reframe (AROP as the primary object, AROPE as a
secondary bridge) — see `docs/publication_strategy.md` for the full framing
discussion and the 7-point spine it produced.

## Cumulative-hardship checkpoint addition (2026-08-20)

| Dataset code | What it is | Key params | Fetched by |
|---|---|---|---|
| `ilc_li01` | AROP poverty threshold, **national currency** (not EUR) | `statinfo=MED_EI`, `rskpovth=B_60`, `hhcomp=A1`, `unit=NAC` | `38_cumulative_hardship.py` |
| `une_rt_a` | Headline unemployment, full history | `age=Y15-74`, `unit=PC_ACT`, 2003–2025 requested (usable from 2009) | `38_cumulative_hardship.py` (new full-history fetch, `panel_unemployment_history.csv`, distinct from the shorter 2015–2024 panel `07_panel_fetch.py` uses) |

Tests whether accumulated exposure since the crisis — not just current-year
conditions — explains Greece's residual gap better than any single-year
snapshot. Reuses already-fetched panels for GDP (`panel_gdp_history_2008_2024.csv`),
real wages (`real_wage_idx2008.csv`), and long-term unemployment
(`panel_long_term_unemployment.csv`); the AROP threshold is fetched fresh in
**national currency**, not EUR, specifically to avoid exchange-rate
contamination for non-euro EU countries when deflating by each country's own
HICP (`panel_hicp_index.csv`).

**Baseline years, and why they differ by variable**: GDP, real wages, and the
AROP threshold are baselined to **2008** (matching this project's existing
anchored-poverty convention). Headline unemployment and long-term
unemployment are baselined to **2009** — confirmed via a direct coverage
check inside the script (not assumed) that both series lack near-complete
27-country coverage in 2008. Croatia lacks both 2008 and 2009 data for the
AROP-threshold series specifically (starts 2010) and is baselined to 2010,
flagged explicitly in the script's own printed output.

**Construction**: every cumulative variable uses a floored, monotonically
non-decreasing running sum — `max(0, value - baseline)` per year, summed —
so a good year can't cancel out an earlier bad one. Tested initially as a
literal permanent accumulation since the baseline year; a later robustness
round (below) found this framing needed softening.

**Headline result**: `cum_excess_unemployment` (cumulative excess
unemployment since 2009), added to the existing Model C-LTU, lifts R²
from 0.914 to 0.930 and moves Greece's out-of-sample residual from 3.9
points to −0.8 (the model slightly overpredicts Greece's reported hardship).
A closely related duration measure, `wage_years_below_2008` (consecutive
years Greek real wages stayed below their own 2008 level), independently
supports the same story. **Both are the two candidates that survive
Benjamini-Hochberg FDR correction** across the full 18-candidate screening
family (the original 8-variable cumulative battery + a 10-variable
duration/direction battery) — cumulative excess unemployment comfortably
(adjusted p=0.0024), the wage-duration measure narrowly (adjusted p=0.0408).

**Two robustness rounds, run in response to external methodological
review, materially changed how this finding is framed** (full accounting
in `docs/publication_strategy.md`, "Second-round methodological review"):

1. **Selection-leakage check.** Cumulative excess unemployment was
   originally selected using the full 27-country panel, Greece included.
   Rerunning the complete 18-candidate screening with Greece dropped from
   the panel *entirely* (not just held out for out-of-sample evaluation)
   found the wage-duration measure actually edges ahead of cumulative
   excess unemployment (p=0.0036 vs. p=0.0064 without Greece in the
   screening data). Both remain the two strongest candidates either way —
   the set doesn't change — but which one ranks first does. All three
   published documents now present the two as jointly supporting evidence
   for the same mechanism, not one uniquely identified variable with a
   clear runner-up.
2. **Rolling-window / decay-rate robustness.** Because the permanent
   cumulative sum can only grow, it can't on its own distinguish real
   accumulated exposure from simply encoding elapsed time since the
   crisis began. Tested trailing 3-, 5-, and 10-year rolling sums and two
   exponentially-decayed running sums (20%/year, 10%/year decay) as
   alternatives. A 3-year window is not significant; a 10-year window
   fits *at least as well as* the permanent since-2009 sum. All three
   documents now describe the mechanism as **sustained excess
   unemployment over roughly the past decade**, not literal permanent,
   non-fading accumulation since one fixed baseline year.

Both the FDR correction and both robustness batteries are now computed
*inside* `38_cumulative_hardship.py` itself, from full-precision p-values,
and declared as script outputs — not generated by a separate one-off
analysis, which was flagged as a reproducibility gap in the same review
round and fixed at the source.

**Outputs** (all in `data/processed/`): `cumulative_hardship_checkpoint.csv`,
`cumulative_hardship_duration_battery.csv`, `cumulative_hardship_replacement_test.csv`,
`cumulative_hardship_loo_stability_cum_excess_unemployment.csv`,
`cumulative_hardship_loo_stability_wage_years_below_2008.csv`,
`cumulative_hardship_final_model_year_by_year.csv`,
`cumulative_hardship_stage1_individual.csv`, `cumulative_hardship_stage2_bridge.csv`,
`cumulative_hardship_fdr_correction.csv`, `cumulative_hardship_selection_excl_greece.csv`,
`cumulative_hardship_rolling_decay_battery.csv`.

### Pipeline bug found and fixed during this round

Re-running `04_merge_all.py` (needed to get FDR status for the inequality
correlation) triggered a cascading many-to-many join blowup: three raw
files created in earlier P2 rounds —
`panel_housing_overburden_by_tenure.csv`, `panel_price_levels_by_category.csv`,
and `panel_tenure_distribution.csv` — have multiple rows per country/year
(one per tenure or price category, by design, for their own dedicated
checkpoint scripts) and had never been run through the generic merge
before, since it hadn't been re-run since those files were created. Fixed
at the root in `04_merge_all.py` with a general `geo`/`time` uniqueness
check that skips any raw file with more than one row per country/year,
rather than special-casing the three offending files — this protects
against any future multi-dimensional raw file causing the same issue.
Confirmed directly afterward that every previously-published correlation
number (long-term unemployment r=0.933, real wages r=−0.785, youth
unemployment r=0.711, etc.) is unchanged — the corruption never reached
any already-published report content, since this was the first time the
merge had run with those three files present.

---

## Scripts 40–44: reporting-style robustness, work-effort squeeze, nested validation

Added 2026-08-20. Documented here to close a gap flagged in external review:
these five scripts' datasets were previously undocumented in this file.

### 40–42: reporting-style / cultural-premium robustness

| Dataset | Filters | Feeds |
|---|---|---|
| `ilc_pw01` | `sex=T`, `age=Y_GE16`, `isced11=TOTAL`, `unit=RTG` | Overall life satisfaction, used as the non-financial self-report comparator in the cross-indicator test (scripts 40, 42) |

Everything else in scripts 40–42 is built from series already documented above:
`subjective_poverty_all_countries.csv`, `arop_all_countries.csv`,
`panel_extended.csv`, `panel_long_term_unemployment.csv`, and
`panel_financial_expectations.csv`.

**Outputs** (`data/processed/`): `reporting_style_precrisis_level.csv`,
`reporting_style_gap_widening.csv`, `reporting_style_diff_in_diff.csv`,
`reporting_style_cltu_year_by_year.csv`, `reporting_style_life_satisfaction.csv`,
`reporting_style_cross_indicator.csv`, `reporting_style_v2_coverage_2003_2008.csv`,
`reporting_style_v2_balanced_rankings.csv`, `reporting_style_v2_event_study.csv`,
`reporting_style_v2_alt_treatment_dates.csv`, `reporting_style_v2_country_placebo.csv`,
`reporting_style_v2_loo_controls.csv`, `reporting_style_v2_periphery_comparison.csv`,
`reporting_style_v2_synthetic_control.csv`, `reporting_style_v2_synthetic_control_v2.csv`,
`reporting_style_v3_standardized_deviations.csv`,
`reporting_style_v3_residual_spec_sensitivity.csv`.

**Note on the two synthetic controls**: the first (`..._synthetic_control.csv`)
is a documented failure, kept deliberately — its donor pool was restricted to
the five countries with full 2003–2008 *and* post-period coverage, all wealthy
Northern/Western European economies that cannot match Greece's pre-crisis level
(RMSE 25.3pt, degenerate 100%-Ireland weighting). The corrected version
(`..._v2.csv`) matches on 2007–2008 instead — the first near-universal-coverage
window per the same script's own coverage audit — opening the donor pool to 25
countries and achieving RMSE≈0.

### 43: work-effort squeeze

| Dataset | Filters | Feeds |
|---|---|---|
| `lfsa_ewhan2` | `nace_r2=TOTAL`, `age=Y20-64`, `sex=T`, `unit=HR`, `wstatus=EMP/SAL/SELF`, `worktime=TOTAL/FT/PT` | Actual weekly hours by employment status and work-time |
| `nama_10_lp_ulc` | `na_item=D1_SAL_HW` (EUR, NAC, PPS_EU27_2020), plus `HW_EMP`, `RLPR_HW`, `NLPR_HW` | Compensation per hour worked — the "reward" side of the squeeze index |
| `nama_10_a10_e` | `nace_r2=TOTAL`, `na_item=SAL_DC`, `unit=THS_HW`/`THS_PER` | National-accounts annual hours per employee (matched employee construction) |
| `ilc_sbjp03` | `wstatus=EMP/SAL/NSAL/POP`, `unit=PC` | Subjective poverty by activity status — the salaried-worker headline |
| `ilc_iw01` | `wstatus=EMP/SAL/NSAL`, `sex=T`, `age=Y_GE18`, `unit=PC` | In-work AROP by activity status |
| `ilc_peps02n` | `wstatus=EMP/SAL/NSAL`, `sex=T`, `age=Y_GE18`, `unit=PC` | In-work AROPE by activity status |
| `prc_hicp_aind` | `coicop=CP00`, `unit=INX_A_AVG` | Deflator for real hourly compensation (own-2008=100) |

**Outputs**: `work_effort_panel.csv`, `work_effort_hours_by_status.csv`,
`work_effort_cross_country_latest.csv`, `work_effort_status_latest.csv`,
`work_effort_employed_hardship_panel.csv`, `work_effort_employed_hardship_latest.csv`,
`work_effort_model_battery.csv`, `work_effort_employed_model_battery.csv`,
`work_effort_stage1_arop_bridge.csv`, `work_effort_final_model_increment.csv`,
`work_effort_within_change_robustness.csv`, `work_effort_greece_correlations.csv`,
`work_effort_interaction_test.csv`, `work_effort_interaction_vif.csv`,
`work_effort_loo_*.csv`, `work_effort_rich_model_loo.csv`,
`work_effort_cumulative_hourly_pay_stage1_loo.csv`, plus five preview figures in
`work_effort_figures/`.

### 44: nested selection validation

No new Eurostat datasets. Reads `cumulative_hardship_candidate_panel.csv`
(exported by `38_cumulative_hardship.py` specifically so this script reuses the
exact screening inputs rather than rebuilding them). Repeats the full
18-candidate screening inside each of the 27 leave-one-country-out folds.

**Outputs**: `nested_selection_validation_folds.csv`,
`nested_selection_validation_detail.csv`.

### 00: acquisition of previously-orphaned raw inputs

`00_fetch_missing_raw.py` re-fetches the fifteen raw files that had no
producing script. Datasets and filters: `ilc_li02` (`statinfo=MED_EI`,
four `rskpovth` cutoffs, Greece) and `ilc_li01` (same cutoffs, `hhcomp=A1`,
`unit=EUR`) for the anchored-poverty inputs; `ilc_peps01`/`ilc_peps01n` for
legacy and revised AROPE; `nama_10_pc` (`P41` and `B1GQ`, `CP_PPS_EU27_2020_HAB`),
`ilc_mdes05`, `ilc_lvho07a`, `ilc_mdes04`, `ilc_li09` (`statinfo=MED_EI`,
`rskpovth=B_60`), `tec00104`, `tec00131` for the 2015–2024 cross-country panels;
`une_rt_a` (`age=Y15-74`) for the unemployment history; `ei_bsco_m`
(`indic=BS-FS-NY`, `s_adj=NSA`, monthly → annual mean) for financial
expectations; and `nama_10_lp_ulc` (`D1_SAL_PER`) deflated by `prc_hicp_aind`
for the real-wage index. Three of these filters were only pinned down by
diffing a fresh fetch against the archive — `statinfo=MED_EI` on both `ilc_li02`
and `ilc_li09`, and `s_adj=NSA` rather than `SA` on `ei_bsco_m` — which is
exactly the kind of undocumented choice the missing acquisition step had been
hiding.
