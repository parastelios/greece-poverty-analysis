"""Build the single scorecard the report was missing: all six nested models
(A-F) side by side, in-sample AND out-of-sample (leave-one-out), so a reader
can see how much of Greece's gap survives after each layer of explanation is
added -- in one table, instead of scattered across Sections 8, 9, and 10.

Fills a real gap first: Model D never had a leave-one-out run (only A/B/C did,
in script 20). Computed here so the scorecard is complete.
"""
import pandas as pd
import statsmodels.formula.api as smf

RAW = "../data/raw"
OUT = "../data/processed"

panel = pd.read_csv(f"{OUT}/panel_extended.csv")
debt = pd.read_csv(f"{RAW}/panel_debt_to_income.csv")
before = pd.read_csv(f"{RAW}/panel_arop_before_transfers.csv")
fin_exp = pd.read_csv(f"{RAW}/panel_financial_expectations.csv")
saving = pd.read_csv(f"{RAW}/panel_saving_rate.csv").rename(columns={"time": "year"})
gdp_hist = pd.read_csv(f"{RAW}/panel_gdp_history_2008_2024.csv").sort_values(["geo", "time"])
gdp_hist["running_peak"] = gdp_hist.groupby("geo")["real_gdp_pc"].cummax()
gdp_hist["pct_below_peak"] = 100 * (gdp_hist["running_peak"] - gdp_hist["real_gdp_pc"]) / gdp_hist["running_peak"]

panel = panel.merge(debt, on=["geo", "time"], how="left")
panel = panel.merge(before, on=["geo", "time"], how="left")
panel["transfer_effect"] = panel["arop_before_transfers"] - panel["arop"]
panel = panel.merge(fin_exp, left_on=["geo", "time"], right_on=["geo", "year"], how="left").drop(columns=["year"])
panel = panel.merge(saving, left_on=["geo", "time"], right_on=["geo", "year"], how="left").drop(columns=["year"])
panel = panel.merge(gdp_hist[["geo", "time", "pct_below_peak"]], on=["geo", "time"], how="left")

vars_a = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"]
vars_b = vars_a + ["housing_cost_overburden"]
vars_c = vars_b + ["arrears", "unexpected_expenses"]
vars_d = vars_c + ["debt_to_income", "transfer_effect"]
vars_e = vars_c + ["fin_expectations", "saving_rate"]
vars_f = vars_c + ["pct_below_peak"]

MODELS = {
    "A_structural": vars_a,
    "B_plus_housing": vars_b,
    "C_plus_arrears_unexpected": vars_c,
    "D_plus_institutional": vars_d,
    "E_plus_expectations_wealth": vars_e,
    "F_plus_scarring_stock": vars_f,
}
LABELS = {
    "A_structural": "A: unemployment, income, deprivation, AROP",
    "B_plus_housing": "B: A + housing cost overburden",
    "C_plus_arrears_unexpected": "C: B + arrears, unexpected-expense capacity",
    "D_plus_institutional": "D: C + household debt-to-income, transfer effect",
    "E_plus_expectations_wealth": "E: C + financial expectations, saving rate",
    "F_plus_scarring_stock": "F: C + scarring stock (% below own income peak)",
}

scorecard = []
for name, vars_ in MODELS.items():
    d = panel.dropna(subset=vars_ + ["subjective_poverty"]).copy()
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d["predicted"] = m.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr_in = d[d.geo == "EL"]["residual"].mean()

    # leave-one-out for every country (needed for D; A/B/C/E/F already exist
    # elsewhere but recomputed here on this exact merged panel for consistency)
    rows = []
    for c in sorted(d["geo"].unique()):
        train = d[d.geo != c]
        test = d[d.geo == c].copy()
        mc = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
        test["predicted_loo"] = mc.predict(test)
        test["residual_loo"] = test["subjective_poverty"] - test["predicted_loo"]
        rows.append({"geo": c, "avg_residual": test["residual_loo"].mean()})
    loo = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
    loo["rank"] = loo.index + 1
    gr_loo_row = loo[loo.geo == "EL"].iloc[0]
    loo.to_csv(f"{OUT}/scorecard_loo_{name}.csv", index=False)

    scorecard.append({
        "model": name,
        "label": LABELS[name],
        "n_countries": d.geo.nunique(),
        "n_obs": len(d),
        "r2": round(m.rsquared, 3),
        "gr_avg_residual_insample": round(gr_in, 1),
        "gr_avg_residual_oos": round(gr_loo_row["avg_residual"], 1),
        "gr_rank_oos": f"{int(gr_loo_row['rank'])}/{len(loo)}",
    })

scorecard_df = pd.DataFrame(scorecard)
scorecard_df.to_csv(f"{OUT}/model_scorecard.csv", index=False)
print(scorecard_df.to_string(index=False))
