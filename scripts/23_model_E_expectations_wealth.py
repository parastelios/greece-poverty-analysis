"""Model E: test whether financial expectations (pessimism about the household's
own future) and household saving rate (wealth depletion / dis-saving) explain
more of Greece's cross-country residual than the null debt-to-income /
transfer-effect variables did in Model D. Both are conceptually different from
every variable tested so far: they aren't material-hardship snapshots, they're
forward-looking sentiment and a stock (wealth trajectory) rather than a flow."""
import pandas as pd
import statsmodels.formula.api as smf

RAW = "../data/raw"
OUT = "../data/processed"

panel = pd.read_csv(f"{OUT}/panel_extended.csv")
fin_exp = pd.read_csv(f"{RAW}/panel_financial_expectations.csv")
saving = pd.read_csv(f"{RAW}/panel_saving_rate.csv").rename(columns={"time": "year"})

panel = panel.merge(fin_exp, left_on=["geo", "time"], right_on=["geo", "year"], how="left").drop(columns=["year"])
panel = panel.merge(saving, left_on=["geo", "time"], right_on=["geo", "year"], how="left").drop(columns=["year"])

vars_c = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
          "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_e = vars_c + ["fin_expectations", "saving_rate"]

MODELS = {
    "C_baseline": vars_c,
    "E_plus_expectations_wealth": vars_e,
}

print("Coverage check:")
for v in ["fin_expectations", "saving_rate"]:
    print(f"  {v}: {panel[v].notna().sum()} / {len(panel)} obs, {panel[panel[v].notna()].geo.nunique()} countries")

results = {}
for name, vars_ in MODELS.items():
    d = panel.dropna(subset=vars_ + ["subjective_poverty"])
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d = d.copy()
    d["predicted"] = model.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr = d[d.geo == "EL"].sort_values("time")
    print(f"\n=== {name} === (n={len(d)}, countries={d.geo.nunique()})")
    print(f"R2={model.rsquared:.3f}")
    show_vars = ["Intercept"] + vars_
    print(model.params[show_vars].round(3).to_string())
    print(model.pvalues[show_vars].round(4).rename("p-value").to_string())
    print(f"Greece avg residual: {gr['residual'].mean():.1f}, last-year: {gr['residual'].iloc[-1]:.1f}")
    results[name] = (model, d, gr)

# leave-Greece-out for Model E specifically
d = panel.dropna(subset=vars_e + ["subjective_poverty"])
train = d[d.geo != "EL"]
formula_e = "subjective_poverty ~ " + " + ".join(vars_e) + " + C(time)"
model_lgo = smf.ols(formula_e, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
gr_test = d[d.geo == "EL"].copy()
gr_test["predicted_lgo"] = model_lgo.predict(gr_test)
gr_test["residual_lgo"] = gr_test["subjective_poverty"] - gr_test["predicted_lgo"]
print("\n=== Leave-Greece-out, Model E ===")
print(gr_test[["time", "subjective_poverty", "predicted_lgo", "residual_lgo"]].round(1).to_string(index=False))
gr_test[["time", "subjective_poverty", "predicted_lgo", "residual_lgo"]].to_csv(f"{OUT}/leave_greece_out_modelE.csv", index=False)

# leave-one-out for ALL countries, Model E, for the outlier-context check
rows = []
for c in sorted(d["geo"].unique()):
    tr = d[d.geo != c]
    te = d[d.geo == c].copy()
    m = smf.ols(formula_e, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
    te["predicted"] = m.predict(te)
    te["residual"] = te["subjective_poverty"] - te["predicted"]
    rows.append({"geo": c, "avg_residual": te["residual"].mean(), "n_years": len(te)})
loo_e = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
loo_e["rank"] = loo_e.index + 1
loo_e.to_csv(f"{OUT}/leave_one_out_modelE.csv", index=False)
print("\n=== Leave-one-out, Model E, all countries ===")
print(loo_e.round(1).to_string(index=False))
