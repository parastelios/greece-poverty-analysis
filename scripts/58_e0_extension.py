"""E0 extension: outcomes in the correlation views, construction taxonomy,
roles, non-independence flags, redundancy and lineage tables.

Infrastructure only. No family freeze, no MDE, no outcome model. Correlations
with the outcomes are produced for the EDA and are explicitly NOT used to
select primary representatives -- representatives are theory-led.

Fixes two E0 defects found in review: the correlation views omitted every
outcome, and "already_indexed" wrongly marked as accumulation-ineligible four
variables the project has already accumulated (one of them an FDR survivor).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from eurostat import fetch
from eu_membership import eu_members

OUT = ROOT / "data" / "processed"
M = sorted(eu_members(2025))
panel = pd.read_csv(OUT / "e0_extended_panel.csv")

# ---------------------------------------------------------------- 1. AROPE ----
AROPE_DATASET, AROPE_FILTERS = "ilc_peps01n", dict(age=["TOTAL"], sex=["T"], unit=["PC"])
ar = fetch(AROPE_DATASET, time=range(2015, 2025), **AROPE_FILTERS)
ar = ar[ar.geo.isin(M)][["geo", "time", "value"]].rename(columns={"value": "arope"})
panel = panel.merge(ar, on=["geo", "time"], how="left")
prov = dict(dataset=AROPE_DATASET, filters={k: v for k, v in AROPE_FILTERS.items()},
            note=("revised AROPE, consistent across the whole 2015-2024 window (27 reporters "
                  "every year) -- no legacy/revised splice is needed here, unlike the long "
                  "descriptive series in the appendix"),
            reporters_per_year=int(ar.groupby("time").geo.nunique().min()))
print(f"AROPE merged from {AROPE_DATASET}: {panel.arope.notna().sum()} obs")

# ---------------------------------------------------------------- 2. comparators ----
panel["gap_subj_arop"] = panel["subjective_poverty"] - panel["arop"]
panel["gap_subj_arope"] = panel["subjective_poverty"] - panel["arope"]
COMPARATORS = ["subjective_poverty", "arop", "arope", "gap_subj_arop", "gap_subj_arope"]
ANCHORED_OMITTED = ("anchored poverty is a Greece-only reconstruction (anchor_rates.csv has no "
                    "geo dimension); it cannot enter a 27-country correlation panel and is "
                    "omitted rather than approximated")
print(f"comparison columns: {COMPARATORS}  (anchored omitted: panel-incompatible)")

# ---------------------------------------------------------------- 3-5. registry v2 ----
reg = pd.read_csv(OUT / "e0_variable_registry.csv")

CONSTRUCTION = {  # six-way taxonomy replacing the binary eligibility field
 **{v: "direct_excess" for v in ["aic_pps_pc","gdp_pps_pc","real_gdp_pc","consumption_pc",
      "hourly_comp","unemployment_rate","ltu_rate","youth_unemployment","employment_rate",
      "severe_mat_soc_deprivation","housing_cost_overburden","s80s20","net_migration",
      "arrears","unexpected_expenses","warm","wadj_a01","work_effort_squeeze","arop",
      "arop_before_transfers","transfer_effect"]},
 **{v: "fixed_base_shortfall" for v in ["real_wages_idx","real_income_idx","arop_threshold_real"]},
 "pct_below_peak": "fixed_base_shortfall",
 **{v: "compounded_change" for v in ["hicp","hicp_food","hicp_housing"]},
 **{v: "ambiguous_direction" for v in ["saving_rate","working_hours","debt_to_income"]},
}
DURATION_ALSO = ["real_wages_idx", "real_income_idx", "arop_threshold_real", "pct_below_peak"]

ROLE = {
 "aic_pps_pc":"primary_representative",
 **{v:"sensitivity_variant" for v in ["gdp_pps_pc","real_gdp_pc","consumption_pc","hourly_comp"]},
 "ltu_rate":"primary_representative",
 **{v:"sensitivity_variant" for v in ["unemployment_rate","youth_unemployment","employment_rate"]},
 **{v:"primary_representative" for v in DURATION_ALSO},
 "wadj_a01":"primary_representative",
 **{v:"sensitivity_variant" for v in ["hicp","hicp_food","hicp_housing"]},
 "housing_cost_overburden":"primary_representative",
 "severe_mat_soc_deprivation":"proximate_diagnostic",
 **{v:"proximate_diagnostic" for v in ["arrears","unexpected_expenses","warm"]},
 "s80s20":"standalone_retest_of_known_null",
 "net_migration":"standalone_retest",
 "work_effort_squeeze":"standalone_retest",
 **{v:"contextual_descriptive" for v in ["saving_rate","debt_to_income","working_hours"]},
 **{v:"mechanical_comparator" for v in ["arop","arop_before_transfers","transfer_effect"]},
}
reg["construction"] = reg.name.map(CONSTRUCTION)
reg["duration_below_base_available"] = reg.name.isin(DURATION_ALSO)
reg["role"] = reg.name.map(ROLE)
reg = reg.drop(columns=["accumulation_eligible"])
reg.to_csv(OUT / "e0_variable_registry.csv", index=False)
print("\nroles:"); print(reg.groupby("role").size().to_string())
print("\nconstruction taxonomy:"); print(reg.groupby("construction").size().to_string())

# ---------------------------------------------------------------- 3. non-independence ----
DEPRIV_COMPONENTS = {"warm", "arrears", "unexpected_expenses"}
SHARED_INPUTS = {"wadj_a01": {"price_level", "wage_level"},
                 "work_effort_squeeze": {"working_hours", "hourly_comp"},
                 "working_hours": {"working_hours"}, "hourly_comp": {"hourly_comp"},
                 "transfer_effect": {"arop", "arop_before_transfers"},
                 "pct_below_peak": {"real_gdp_pc"}}

def nonindependence(a, b):
    p = {a, b}
    if p & {"gap_subj_arop"} and p & {"subjective_poverty", "arop"}:
        return "arithmetic_coupling"
    if p & {"gap_subj_arope"} and p & {"subjective_poverty", "arope"}:
        return "arithmetic_coupling"
    if "arope" in p and (p & {"arop", "severe_mat_soc_deprivation"}):
        return "definitional_overlap"
    if "arope" in p and (p & DEPRIV_COMPONENTS):
        return "component_overlap"
    if "severe_mat_soc_deprivation" in p and (p & DEPRIV_COMPONENTS):
        return "component_overlap"
    sa, sb = SHARED_INPUTS.get(a, set()), SHARED_INPUTS.get(b, set())
    if sa & sb or a in sb or b in sa:
        return "construction_overlap"
    return ""

# ---------------------------------------------------------------- correlation views ----
VARS = [v for v in reg.name if v in panel.columns] + [c for c in COMPARATORS if c != "arop"]
VARS = list(dict.fromkeys(VARS))
views = {
 "pooled":  panel[VARS].corr(),
 "between": panel.groupby("geo")[VARS].mean().corr(),
 "within":  (panel[VARS] - panel.groupby("geo")[VARS].transform("mean")).corr(),
}
flags = pd.DataFrame("", index=VARS, columns=VARS)
for i, a in enumerate(VARS):
    for b in VARS[i+1:]:
        f = nonindependence(a, b)
        flags.loc[a, b] = flags.loc[b, a] = f
for k, v in views.items():
    v.round(4).to_csv(OUT / f"e0_corr_{k}.csv")
flags.to_csv(OUT / "e0_nonindependence_flags.csv")
n_flag = int((flags.values != "").sum() / 2)
print(f"\ncorrelation views rebuilt with {len(VARS)} columns including the comparators")
print(f"non-independent pairs flagged: {n_flag}")
print(pd.Series(flags.values[flags.values != ""]).value_counts().to_string())

# ---------------------------------------------------------------- 6. redundancy ----
GROUPS = {"aic_pps_pc": ["gdp_pps_pc","real_gdp_pc","consumption_pc","hourly_comp"],
          "ltu_rate": ["unemployment_rate","youth_unemployment","employment_rate"],
          "wadj_a01": ["hicp","hicp_food","hicp_housing","work_effort_squeeze"]}
rows = []
for prim, sens in GROUPS.items():
    for s in sens:
        rows.append(dict(primary=prim, sensitivity=s,
                         pooled=round(views["pooled"].loc[prim, s], 3),
                         between=round(views["between"].loc[prim, s], 3),
                         within=round(views["within"].loc[prim, s], 3),
                         flag=nonindependence(prim, s)))
red = pd.DataFrame(rows)
red["sign_flips"] = np.sign(red.pooled) != np.sign(red.within)
red.to_csv(OUT / "e0_redundancy.csv", index=False)
print("\nredundancy: primary vs sensitivity (representatives chosen on theory, NOT on these)")
print(red.to_string(index=False))

# ---------------------------------------------------------------- 9. lineage ----
lin = [dict(derived=k, shares_inputs_with=", ".join(sorted(v))) for k, v in SHARED_INPUTS.items()]
lin += [dict(derived="arope", shares_inputs_with="arop, severe_mat_soc_deprivation, low work intensity (union)"),
        dict(derived="severe_mat_soc_deprivation", shares_inputs_with="warm, arrears, unexpected_expenses (items)"),
        dict(derived="gap_subj_arop", shares_inputs_with="subjective_poverty, arop"),
        dict(derived="gap_subj_arope", shares_inputs_with="subjective_poverty, arope")]
pd.DataFrame(lin).to_csv(OUT / "e0_lineage.csv", index=False)

# ---------------------------------------------------------------- 10. frozen assert ----
fz = json.load(open(OUT / "p5f_frozen_result.json"))
assert fz["branch"].startswith("2"), "frozen branch changed"
assert abs(fz["p3"]["greece_oos_residual"] - 6.93) < 1e-9, "frozen P3 residual changed"
assert abs(fz["p5"]["between"] - 0.3323) < 1e-9, "frozen P5 between changed"
assert fz["p3a"]["incremental_value"] is False, "frozen P3a verdict changed"
tag = subprocess.run(["git", "tag", "-l", "p5f-frozen"], cwd=ROOT,
                     capture_output=True, text=True).stdout.strip()
assert tag == "p5f-frozen", "p5f-frozen tag missing"
print("\nFROZEN ASSERTION: P3, P5, P3a and the p5f-frozen tag are unchanged.")

panel.to_csv(OUT / "e0_extended_panel.csv", index=False)
json.dump({"arope_provenance": prov, "anchored_omitted": ANCHORED_OMITTED,
           "comparators": COMPARATORS,
           "arope_wording": ("AROPE's relationships to AROP, deprivation and low work intensity "
                             "are partly DEFINITIONALLY STRUCTURED, not necessarily mechanically "
                             "deterministic: AROPE is a union, and aggregate data do not reveal "
                             "the component overlaps that would fix the relationship exactly.")},
          open(OUT / "e0_provenance.json", "w"), indent=2)
print("\nE0 extension complete. No family freeze, no MDE, no outcome model.")
