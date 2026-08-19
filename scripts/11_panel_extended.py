"""Build the extended cross-country panel and run model-comparison regressions:
baseline (chain-linked EUR GDP) -> PPS-adjusted GDP/AIC swap -> + hardship
variables -> leave-Greece-out robustness check."""
import pandas as pd
import statsmodels.formula.api as smf
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
YEARS = range(2015, 2025)

sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")[["geo", "time", "subjective_poverty"]]
arop = pd.read_csv(f"{RAW}/arop_all_countries.csv")[["geo", "time", "arop"]]
une = pd.read_csv(f"{RAW}/panel_unemployment.csv")
gdp_eur = pd.read_csv(f"{RAW}/panel_gdp.csv")
msd = pd.read_csv(f"{RAW}/panel_deprivation.csv")
aic_pps = pd.read_csv(f"{RAW}/panel_aic_pps.csv")
gdp_pps = pd.read_csv(f"{RAW}/panel_gdp_pps.csv")
housing = pd.read_csv(f"{RAW}/panel_housing_overburden.csv")
arrears = pd.read_csv(f"{RAW}/panel_arrears.csv")
unexp = pd.read_csv(f"{RAW}/panel_unexpected_expenses.csv")

panel = sub.merge(arop, on=["geo", "time"]).merge(une, on=["geo", "time"], how="left")
panel = panel.merge(gdp_eur, on=["geo", "time"], how="left").merge(msd, on=["geo", "time"], how="left")
panel = panel.merge(aic_pps, on=["geo", "time"], how="left").merge(gdp_pps, on=["geo", "time"], how="left")
panel = panel.merge(housing, on=["geo", "time"], how="left").merge(arrears, on=["geo", "time"], how="left")
panel = panel.merge(unexp, on=["geo", "time"], how="left")

panel = panel[panel["time"].isin(YEARS)]
panel = panel[panel.apply(lambda r: r["geo"] in eu_members(int(r["time"])), axis=1)]
panel["real_gdp_pc_k"] = panel["real_gdp_pc"] / 1000.0
panel["aic_pps_pc_k"] = panel["aic_pps_pc"] / 1000.0
panel["gdp_pps_pc_k"] = panel["gdp_pps_pc"] / 1000.0

panel.to_csv(f"{OUT}/panel_extended.csv", index=False)
print(f"Extended panel: {panel.shape[0]} obs, {panel.geo.nunique()} countries")
print(panel[["unemployment_rate","real_gdp_pc","severe_mat_soc_deprivation","aic_pps_pc","gdp_pps_pc","housing_cost_overburden","arrears","unexpected_expenses"]].isna().sum())

MODELS = {
    "M1_baseline_EUR_GDP": "subjective_poverty ~ unemployment_rate + real_gdp_pc_k + severe_mat_soc_deprivation + arop + C(time)",
    "M2_swap_to_AIC_PPS": "subjective_poverty ~ unemployment_rate + aic_pps_pc_k + severe_mat_soc_deprivation + arop + C(time)",
    "M3_swap_to_GDP_PPS": "subjective_poverty ~ unemployment_rate + gdp_pps_pc_k + severe_mat_soc_deprivation + arop + C(time)",
    "M4_plus_hardship_vars": "subjective_poverty ~ unemployment_rate + aic_pps_pc_k + severe_mat_soc_deprivation + arop + housing_cost_overburden + arrears + unexpected_expenses + C(time)",
}

results_summary = []
gr_by_model = {}
for name, formula in MODELS.items():
    d = panel.dropna(subset=[c for c in ["unemployment_rate","real_gdp_pc_k","aic_pps_pc_k","gdp_pps_pc_k",
                                          "severe_mat_soc_deprivation","arop","housing_cost_overburden",
                                          "arrears","unexpected_expenses"] if c in formula])
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d = d.copy()
    d["predicted"] = model.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr = d[d.geo == "EL"].sort_values("time")
    gr_avg_resid = gr["residual"].mean()
    gr_2024_resid = gr[gr.time == gr.time.max()]["residual"].iloc[0] if len(gr) else None
    rank = d.groupby("time").apply(lambda g: g.sort_values("residual", ascending=False).reset_index(drop=True).index[g.sort_values("residual", ascending=False).reset_index(drop=True)["geo"] == "EL"].tolist())
    results_summary.append({
        "model": name, "n": len(d), "r2": round(model.rsquared, 3),
        "gr_avg_residual": round(gr_avg_resid, 1), "gr_latest_residual": round(gr_2024_resid, 1),
    })
    gr_by_model[name] = gr[["time", "subjective_poverty", "predicted", "residual"]].round(1)
    print(f"\n=== {name} ===")
    print(f"R2={model.rsquared:.3f}, n={len(d)}")
    print(model.params.round(3).to_string())

summary_df = pd.DataFrame(results_summary)
print("\n\n=== MODEL COMPARISON: Greece's residual across specifications ===")
print(summary_df.to_string(index=False))
summary_df.to_csv(f"{OUT}/panel_model_comparison.csv", index=False)

for name, gr in gr_by_model.items():
    print(f"\n--- {name}: Greece by year ---")
    print(gr.to_string(index=False))

# Leave-Greece-out: refit M4 (preferred model) excluding Greece, predict Greece out-of-sample
d = panel.dropna(subset=["unemployment_rate","aic_pps_pc_k","severe_mat_soc_deprivation","arop",
                          "housing_cost_overburden","arrears","unexpected_expenses"])
train = d[d.geo != "EL"]
model_lgo = smf.ols(
    "subjective_poverty ~ unemployment_rate + aic_pps_pc_k + severe_mat_soc_deprivation + arop + housing_cost_overburden + arrears + unexpected_expenses + C(time)",
    data=train,
).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
gr_test = d[d.geo == "EL"].copy()
gr_test["predicted_lgo"] = model_lgo.predict(gr_test)
gr_test["residual_lgo"] = gr_test["subjective_poverty"] - gr_test["predicted_lgo"]
print("\n\n=== Leave-Greece-out: model fit on 26 other countries, predicting Greece ===")
print(gr_test[["time", "subjective_poverty", "predicted_lgo", "residual_lgo"]].round(1).to_string(index=False))
gr_test[["time", "subjective_poverty", "predicted_lgo", "residual_lgo"]].to_csv(f"{OUT}/leave_greece_out.csv", index=False)
