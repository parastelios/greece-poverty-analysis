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

## Non-Eurostat sources (corroboration only, not modeled)

These are cited in the literature/discussion section as independent
corroboration — none are merged into any model or panel.

- **diaNEOsis / University of Macedonia** (2016 opinion survey): financial-pessimism and basic-needs-difficulty figures, PDF `ftwxeia2_version_060616_2.pdf`.
- **diaNEOsis** (Jan 2026 housing article, summarizing an IOBE/Vettas study): housing-cost-share and arrears figures.
- **Mantés & Marinakis / Greekonomics.gr** (2025 report, MIT-licensed companion code at `github.com/AMantes/Greekonomics`): "Bottom-10" comparator income/housing/healthcare figures.
- **Greece in Figures** (`greeceinfigures.com`): independently-reported AROPE/subjective-poverty headline figures, matched against this project's own Eurostat pull.
- **Andriopoulou, Kanavitsa & Tsakloglou** (2019/2020): microdata-based anchored-poverty comparison — full citation in report Methods.

## Non-Eurostat data considered and rejected or deferred

- Eurobarometer trust-in-institutions data: not yet fetched — feasibility
  (comparable methodology, country/year coverage) is an open checkpoint
  (see the project's task list, P1.3).
- Real wages, youth/long-term unemployment, income inequality (Gini/S80:S20),
  housing tenure: named in `docs/project_description.md` but deliberately
  not fetched for Version 1 — see `docs/publication_strategy.md` for the
  scoping decision.
