"""E0: extended panel, coverage table, variable registry, lineage, correlation views.

Infrastructure only. This script deliberately does NOT define families, compute
MDEs, or run any outcome model. Family membership is revisited from this
metadata, not from correlation fit and not from results.

Prompted by review findings that the earlier draft grouping had assigned
variables by empirical fit (net_migration to employment, s80s20 to deprivation),
treated HICP inflation rates as country price levels, and left accumulation
undefined for variables where summing is meaningless.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from eu_membership import eu_members
from validate_outputs import json_safe

OUT = ROOT / "data" / "processed"
M = sorted(eu_members(2025))
YEARS = range(2015, 2025)

# ---------------------------------------------------------------- registry ----
# domain_provisional is a STARTING POINT for the membership discussion, not a
# decision. adverse_direction, stock_flow and accumulation_eligible are
# properties of the measure and are decided here, before any model.
#
# accumulation_eligible = can "summing excess over a baseline" mean anything?
#   rate_of_change  -> a level IS already a change; summing gives a price index, a
#                      different quantity, so eligible only under an explicit
#                      cumulative-inflation construction
#   already_indexed -> the variable is already relative to its own 2008 base
#   ambiguous_sign  -> no unambiguous adverse direction, so "excess" is undefined
REG = [
 # name, label, unit, source, domain_provisional, adverse, stock_flow, accum, proximity, derived_from
 ("aic_pps_pc","Actual individual consumption per capita","PPS","nama_10_pc","income/output","lower_is_worse","stock","eligible","objective",""),
 ("gdp_pps_pc","GDP per capita","PPS","nama_10_pc","income/output","lower_is_worse","stock","eligible","objective",""),
 ("real_gdp_pc","Real GDP per capita","chain-linked EUR","sdg_08_10","income/output","lower_is_worse","stock","eligible","objective",""),
 ("consumption_pc","Real household consumption per capita","chain-linked EUR","nama_10_pc","income/output","lower_is_worse","stock","eligible","objective",""),
 ("hourly_comp","Compensation per hour worked","PPS","nama_10_lp_ulc","income/output","lower_is_worse","stock","eligible","objective",""),
 ("saving_rate","Household saving rate","% of disp. income","tec00131","buffers","ambiguous","flow","ambiguous_sign","objective",
  "low saving may be hardship OR low precaution; high saving may be prudence OR demand collapse"),
 ("unemployment_rate","Unemployment rate","% active","une_rt_a","labour market","higher_is_worse","flow","eligible","objective",""),
 ("ltu_rate","Long-term unemployment","% active","une_ltu_a","labour market","higher_is_worse","flow","eligible","objective",""),
 ("youth_unemployment","Youth unemployment 15-24","% active","une_rt_a","labour market","higher_is_worse","flow","eligible","objective",""),
 ("employment_rate","Employment rate 20-64","% pop","sdg_08_30","labour market","lower_is_worse","flow","eligible","objective",""),
 ("working_hours","Actual weekly hours","hours","lfsa_ewhan2","labour market","ambiguous","flow","ambiguous_sign","objective",
  "long hours may be effort under strain OR simply more work available"),
 ("real_wages_idx","Real wages, own 2008=100","index","derived","loss vs own past","lower_is_worse","stock","already_indexed","objective",
  "nama_10_lp_ulc D1_SAL_PER deflated by prc_hicp_aind, rebased to own 2008"),
 ("real_income_idx","Real household disposable income, 2008=100","index","tepsr_wc310","loss vs own past","lower_is_worse","stock","already_indexed","objective",""),
 ("arop_threshold_real","Real AROP threshold, own 2008=100","index","derived","loss vs own past","lower_is_worse","stock","already_indexed","objective",
  "ilc_li01 NAC, euro-changeover normalised (currency.py), HICP-deflated, own 2008 base"),
 ("pct_below_peak","Distance below own GDP peak","% below peak","derived","loss vs own past","higher_is_worse","stock","already_indexed","objective",
  "running maximum of real_gdp_pc"),
 ("hicp","HICP inflation, headline","% annual change","prc_hicp_aind","inflation","higher_is_worse","flow","rate_of_change","objective",
  "NOT a cross-country price level: an index of change"),
 ("hicp_food","HICP inflation, food","% annual change","prc_hicp_aind","inflation","higher_is_worse","flow","rate_of_change","objective",
  "NOT a cross-country price level"),
 ("hicp_housing","HICP inflation, housing & energy","% annual change","prc_hicp_aind","inflation","higher_is_worse","flow","rate_of_change","objective",
  "NOT a cross-country price level"),
 ("wadj_a01","Wage-adjusted price pressure","index, EU=100","derived","price level","higher_is_worse","stock","eligible","objective",
  "prc_ppp_ind price level / nominal compensation wage level; both EU27=100"),
 ("work_effort_squeeze","Work-effort squeeze","index, EU=100","derived","composite","higher_is_worse","stock","eligible","objective",
  "OVERLAP: built from working_hours and hourly_comp, both also registered here"),
 ("severe_mat_soc_deprivation","Severe material & social deprivation","% people","ilc_mdsd11","deprivation","higher_is_worse","stock","eligible","proximate_same_instrument",
  "EU-SILC affordability items: same instrument as the outcome"),
 ("housing_cost_overburden","Housing cost overburden","% people","ilc_lvho07a","housing","higher_is_worse","stock","eligible","objective",""),
 ("debt_to_income","Household debt to income","% disp. income","tec00104","buffers","ambiguous","stock","ambiguous_sign","objective",
  "low debt may be resilience, deleveraging OR credit exclusion"),
 ("s80s20","Income quintile share ratio","ratio","ilc_di11","inequality","higher_is_worse","stock","eligible","objective",""),
 ("net_migration","Net migration of nationals","per 1,000","derived","demography","lower_is_worse","flow","eligible","contextual",
  "migr_emi1ctz / migr_imm1ctz, citizen=NAT"),
 ("arrears","Arrears on bills","% people","ilc_mdes05","affordability","higher_is_worse","stock","eligible","proximate_same_instrument",
  "EU-SILC self-report, same respondent and instrument as the outcome"),
 ("unexpected_expenses","Cannot meet unexpected expense","% people","ilc_mdes04","affordability","higher_is_worse","stock","eligible","proximate_same_instrument",
  "EU-SILC self-report, same instrument"),
 ("warm","Cannot keep home adequately warm","% people","ilc_mdes01","affordability","higher_is_worse","stock","eligible","proximate_same_instrument",
  "EU-SILC self-report; also a component of severe material deprivation"),
 ("arop","At-risk-of-poverty rate","% people","ilc_li02","comparator","higher_is_worse","stock","eligible","comparator_baseline",""),
 ("arop_before_transfers","AROP before social transfers","% people","ilc_li09","comparator","higher_is_worse","stock","eligible","mechanical_with_arop",""),
 ("transfer_effect","AROP removed by transfers","pp","derived","comparator","lower_is_worse","stock","eligible","mechanical_with_arop",
  "arop_before_transfers minus arop: definitionally AROP"),
]
COLS = ["name","label","unit","source","domain_provisional","adverse_direction",
        "stock_flow","accumulation_eligible","proximity_class","note"]
reg = pd.DataFrame(REG, columns=COLS)

# ---------------------------------------------------------------- panel ----
S = json.load(open(OUT / "appendix_series_core.json"))["series"]
panel = pd.read_csv(OUT / "persistence_share_panel.csv")
merged = []
for n in reg.name:
    if n in panel.columns:
        continue
    if n not in S:
        continue
    v = S[n]
    rows = [(c, int(y), x) for c, ser in v["countries"].items() if c in M
            for y, x in zip(v["years"], ser) if x is not None]
    panel = panel.merge(pd.DataFrame(rows, columns=["geo", "time", n]),
                        on=["geo", "time"], how="left")
    merged.append(n)
panel = panel[panel.geo.isin(M) & panel.time.between(min(YEARS), max(YEARS))]
print(f"merged {len(merged)} series from the appendix: {merged}")
print(f"extended panel: {panel.geo.nunique()} countries x {panel.time.nunique()} years "
      f"= {len(panel)} rows")

present = [n for n in reg.name if n in panel.columns]
missing = [n for n in reg.name if n not in panel.columns]
if missing:
    print(f"REGISTERED BUT ABSENT FROM PANEL: {missing}")

# ---------------------------------------------------------------- coverage ----
cov = []
for n in present:
    s = panel[n]
    per_year = panel.groupby("time")[n].apply(lambda x: x.notna().sum())
    cov.append(dict(name=n, n_obs=int(s.notna().sum()), pct=round(100*s.notna().mean(), 1),
                    countries=int(panel.loc[s.notna(), "geo"].nunique()),
                    min_year_reporters=int(per_year.min()), years=int((per_year > 0).sum())))
cov = pd.DataFrame(cov).sort_values("pct")
print(f"\nweakest coverage:\n{cov.head(5).to_string(index=False)}")

# ---------------------------------------------------------------- correlations ----
# pooled, between (country means) and within (deviations from country means).
# These answer different questions and the earlier draft used only the pooled view.
X = panel[present]
between = panel.groupby("geo")[present].mean()
within = panel[present] - panel.groupby("geo")[present].transform("mean")
views = {"pooled": X.corr(), "between": between.corr(), "within": within.corr()}
for k, v in views.items():
    v.to_csv(OUT / f"e0_corr_{k}.csv")
print(f"\ncorrelation views written: {', '.join(views)}")
print("  mean |r| off-diagonal: " + ", ".join(
    f"{k} {np.nanmean(np.abs(v.values[~np.eye(len(v), dtype=bool)])):.3f}" for k, v in views.items()))

reg.to_csv(OUT / "e0_variable_registry.csv", index=False)
cov.to_csv(OUT / "e0_coverage.csv", index=False)
panel.to_csv(OUT / "e0_extended_panel.csv", index=False)
print(f"\nregistry: {len(reg)} variables")
print(reg.groupby("proximity_class").size().to_string())
print()
print(reg.groupby("accumulation_eligible").size().to_string())
print("\nE0 complete. No families defined, no MDE, no outcome model run.")
