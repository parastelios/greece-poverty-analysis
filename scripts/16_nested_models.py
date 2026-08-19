"""Nested cross-country model comparison (Models A-D) plus a balanced-panel
sensitivity check and a rebuilt leave-Greece-out test on the preferred model.

Model A: structural economic vars (unemployment, AIC per capita PPS, severe
         material & social deprivation, AROP) -- the least "outcome-adjacent" set.
Model B: A + housing cost overburden.
Model C: B + arrears + inability to face unexpected expenses (closest to
         subjective poverty conceptually -- kept separate from A/B deliberately).
Model D: C + household debt-to-income ratio + poverty-reduction effect of social
         transfers (institutional/balance-sheet variables).
"""
import pandas as pd
import statsmodels.formula.api as smf

RAW = "../data/raw"
OUT = "../data/processed"
YEARS = range(2015, 2025)

panel = pd.read_csv(f"{OUT}/panel_extended.csv")
debt = pd.read_csv(f"{RAW}/panel_debt_to_income.csv")
before = pd.read_csv(f"{RAW}/panel_arop_before_transfers.csv")

panel = panel.merge(debt, on=["geo", "time"], how="left")
panel = panel.merge(before, on=["geo", "time"], how="left")
panel["transfer_effect"] = panel["arop_before_transfers"] - panel["arop"]

ALL_VARS = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
            "housing_cost_overburden", "arrears", "unexpected_expenses",
            "debt_to_income", "transfer_effect"]

MODELS = {
    "A_structural": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"],
    "B_plus_housing": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop", "housing_cost_overburden"],
    "C_plus_arrears_unexpected": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop", "housing_cost_overburden", "arrears", "unexpected_expenses"],
    "D_plus_institutional": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop", "housing_cost_overburden", "arrears", "unexpected_expenses", "debt_to_income", "transfer_effect"],
}

# ---- varying-membership sample (as before) ----
print("=" * 70)
print("VARYING EU MEMBERSHIP SAMPLE (primary, matches earlier report)")
print("=" * 70)
summary_varying = []
fitted_gr = {}
for name, vars_ in MODELS.items():
    d = panel.dropna(subset=vars_ + ["subjective_poverty"])
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d = d.copy()
    d["predicted"] = model.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr = d[d.geo == "EL"].sort_values("time")
    summary_varying.append({
        "model": name, "n": len(d), "n_countries": d.geo.nunique(), "r2": round(model.rsquared, 3),
        "gr_avg_residual": round(gr["residual"].mean(), 1),
        "gr_first_year_residual": round(gr["residual"].iloc[0], 1) if len(gr) else None,
        "gr_last_year_residual": round(gr["residual"].iloc[-1], 1) if len(gr) else None,
    })
    fitted_gr[name] = gr[["time", "subjective_poverty", "predicted", "residual"]].round(1)

summary_df = pd.DataFrame(summary_varying)
print(summary_df.to_string(index=False))
summary_df.to_csv(f"{OUT}/nested_models_varying.csv", index=False)

# per-year Greece residual trend for each model (used to chart A vs C shrinkage over time)
for name, gr in fitted_gr.items():
    gr.assign(model=name).to_csv(f"{OUT}/gr_residual_trend_{name}.csv", index=False)

# ---- balanced panel: countries with complete data on ALL variables, ALL 10 years ----
print("\n" + "=" * 70)
print("BALANCED PANEL SENSITIVITY (fixed country set, all 10 years, all vars)")
print("=" * 70)
complete = panel.dropna(subset=ALL_VARS + ["subjective_poverty"])
counts = complete.groupby("geo")["time"].nunique()
balanced_countries = counts[counts == len(YEARS)].index.tolist()
print(f"Countries with complete data all {len(YEARS)} years on every variable: {len(balanced_countries)}")
print(sorted(balanced_countries))
balanced = panel[panel.geo.isin(balanced_countries)]

summary_balanced = []
for name, vars_ in MODELS.items():
    d = balanced.dropna(subset=vars_ + ["subjective_poverty"])
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d = d.copy()
    d["predicted"] = model.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr = d[d.geo == "EL"].sort_values("time")
    summary_balanced.append({
        "model": name, "n": len(d), "n_countries": d.geo.nunique(), "r2": round(model.rsquared, 3),
        "gr_avg_residual": round(gr["residual"].mean(), 1),
        "gr_last_year_residual": round(gr["residual"].iloc[-1], 1) if len(gr) else None,
    })
summary_balanced_df = pd.DataFrame(summary_balanced)
print(summary_balanced_df.to_string(index=False))
summary_balanced_df.to_csv(f"{OUT}/nested_models_balanced.csv", index=False)

# ---- Leave-Greece-out on preferred model (C: structural + housing + arrears/unexpected,
#      excluding D since institutional vars have more missingness and D's purpose is
#      exploratory) ----
print("\n" + "=" * 70)
print("LEAVE-GREECE-OUT: fit Model C on the other countries, predict Greece")
print("=" * 70)
vars_c = MODELS["C_plus_arrears_unexpected"]
d = panel.dropna(subset=vars_c + ["subjective_poverty"])
train = d[d.geo != "EL"]
formula = "subjective_poverty ~ " + " + ".join(vars_c) + " + C(time)"
model_lgo = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
gr_test = d[d.geo == "EL"].copy()
gr_test["predicted_lgo"] = model_lgo.predict(gr_test)
gr_test["residual_lgo"] = gr_test["subjective_poverty"] - gr_test["predicted_lgo"]
print(gr_test[["time", "subjective_poverty", "predicted_lgo", "residual_lgo"]].round(1).to_string(index=False))
gr_test[["time", "subjective_poverty", "predicted_lgo", "residual_lgo"]].to_csv(f"{OUT}/leave_greece_out_modelC.csv", index=False)

print("\n\n=== Model D coefficients (institutional vars) ===")
d4 = panel.dropna(subset=MODELS["D_plus_institutional"] + ["subjective_poverty"])
formula4 = "subjective_poverty ~ " + " + ".join(MODELS["D_plus_institutional"]) + " + C(time)"
model4 = smf.ols(formula4, data=d4).fit(cov_type="cluster", cov_kwds={"groups": d4["geo"]})
show_vars = ["Intercept"] + MODELS["D_plus_institutional"]
print(model4.params[show_vars].round(3).to_string())
print(model4.pvalues[show_vars].round(4).rename("p-value").to_string())

for name, gr in fitted_gr.items():
    print(f"\n--- {name}: Greece by year (varying-membership sample) ---")
    print(gr.to_string(index=False))
