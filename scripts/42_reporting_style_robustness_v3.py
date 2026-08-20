"""Reporting-style robustness, round 3: standardized (not just ranked)
cross-indicator deviations with explicit annual coverage counts, and
specification-sensitivity checks for the residual-trend result.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
pd.set_option("display.width", 220)

sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")
fin_exp = pd.read_csv(f"{RAW}/panel_financial_expectations.csv").rename(columns={"year": "time"})
life_sat = pd.read_csv(f"{OUT}/reporting_style_life_satisfaction.csv")
members_2025 = set(eu_members(2025))

# ================================================================ standardized deviations ====
rows = []
common_years = sorted(set(life_sat.time.unique()) & set(fin_exp.time.unique()) & set(sub.time.unique()))
for y in common_years:
    sp = sub[(sub.time == y) & (sub.geo.isin(members_2025))].dropna(subset=["subjective_poverty"])
    fe = fin_exp[(fin_exp.time == y) & (fin_exp.geo.isin(members_2025))].dropna(subset=["fin_expectations"])
    ls = life_sat[(life_sat.time == y) & (life_sat.geo.isin(members_2025))].dropna(subset=["life_satisfaction"])
    row = {"year": y, "n_subj_poverty": len(sp), "n_fin_exp": len(fe), "n_life_sat": len(ls)}
    if len(sp) >= 5 and "EL" in sp.geo.values:
        z = (sp.set_index("geo")["subjective_poverty"] - sp["subjective_poverty"].mean()) / sp["subjective_poverty"].std()
        row["gr_subj_poverty_z"] = z["EL"]
    if len(fe) >= 5 and "EL" in fe.geo.values:
        z = (fe.set_index("geo")["fin_expectations"] - fe["fin_expectations"].mean()) / fe["fin_expectations"].std()
        row["gr_fin_exp_z"] = -z["EL"]  # sign-flipped so positive = more pessimistic, same direction as the other two
    if len(ls) >= 5 and "EL" in ls.geo.values:
        z = (ls.set_index("geo")["life_satisfaction"] - ls["life_satisfaction"].mean()) / ls["life_satisfaction"].std()
        row["gr_life_sat_z"] = -z["EL"]  # sign-flipped so positive = worse (less satisfied), same direction
    rows.append(row)
z_df = pd.DataFrame(rows)
z_df.to_csv(f"{OUT}/reporting_style_v3_standardized_deviations.csv", index=False)
print("=== Standardized (z-score) deviations, Greece vs. EU mean each year ===")
print("Sign convention: positive = Greece worse/more negative than the EU average, for all three,")
print("so they're directly comparable in magnitude, not just rank.")
print(z_df.to_string(index=False))
print(f"\nAverage |z| across years -- subjective poverty: {z_df['gr_subj_poverty_z'].mean():.2f}, "
      f"financial expectations: {z_df['gr_fin_exp_z'].mean():.2f}, "
      f"life satisfaction: {z_df['gr_life_sat_z'].mean():.2f}")
print("(If this were a generic response-style effect, these three z-scores should be of similar "
      "magnitude. If it's specific to financial self-assessment, life satisfaction's z-score "
      "should be visibly smaller than the other two.)")

# ================================================================ residual-trend sensitivity =
panel = pd.read_csv(f"{OUT}/panel_extended.csv")
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")[["geo", "time", "ltu_rate"]]
panel = panel.merge(ltu, on=["geo", "time"], how="left")

SPECS = {
    "Model A (basic: unemployment, income, deprivation, AROP)":
        ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"],
    "Model C (+ housing, arrears, unexpected expenses, headline unemployment)":
        ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
         "housing_cost_overburden", "arrears", "unexpected_expenses"],
    "Model C-LTU (as Model C, long-term unemployment replacing headline)":
        ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
         "housing_cost_overburden", "arrears", "unexpected_expenses"],
}

print("\n\n=== Residual-trend sensitivity: does the +1.8pt/year trend survive across model specs? ===")
print("Methodology, stated explicitly: ONE model is fit on the other 26 countries' pooled panel "
      "(year fixed effects, country-clustered SEs), excluding Greece entirely from estimation; "
      "that single fitted model is then used to predict Greece's value in every year. This is a "
      "genuine out-of-sample prediction for every year shown -- not a fresh refit per year, and "
      "not a specification that ever sees Greece's own data at any point.")
spec_rows = []
for name, vars_ in SPECS.items():
    d = panel.dropna(subset=vars_ + ["subjective_poverty"]).copy()
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    train = d[d.geo != "EL"]
    test = d[d.geo == "EL"].copy()
    m = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
    test["predicted"] = m.predict(test)
    test["residual"] = test["subjective_poverty"] - test["predicted"]
    test = test.sort_values("time")
    trend = np.polyfit(test["time"], test["residual"], 1)[0]
    spec_rows.append({"model": name, "n_years": len(test), "mean_residual": test["residual"].mean(),
                       "std_residual": test["residual"].std(), "trend_pt_per_year": trend})
    print(f"\n{name}:")
    print(test[["time", "subjective_poverty", "predicted", "residual"]].to_string(index=False))
spec_df = pd.DataFrame(spec_rows)
spec_df.to_csv(f"{OUT}/reporting_style_v3_residual_spec_sensitivity.csv", index=False)
print("\n\n=== Summary across specifications ===")
print(spec_df.to_string(index=False))

print("\n\nOutputs written:")
for f in ["reporting_style_v3_standardized_deviations.csv", "reporting_style_v3_residual_spec_sensitivity.csv"]:
    print(f"  {OUT}/{f}")
