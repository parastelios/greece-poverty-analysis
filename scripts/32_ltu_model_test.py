"""P2b follow-up: the full model battery the user asked for before any
report integration decision on long-term unemployment (LTU). Mirrors
26_model_scorecard.py's panel construction exactly, then adds:

  - Model C-LTU: LTU rate REPLACES headline unemployment (preferred spec,
    avoids the unemployment/LTU collinearity that destabilizes the
    headline-unemployment coefficient when both are included)
  - Model C+LTU: LTU rate ADDED alongside headline unemployment (robustness
    only, not preferred -- see publication_strategy.md for why)
  - Model C-LTU + scarring stock: does LTU still play well with the
    scarring-stock variable (Model F), or do they compete for the same
    signal?
  - Model C-LTU + expectations/wealth: does LTU reduce the apparent role of
    financial expectations (Model E), i.e. are they both partly capturing
    the same "persistent scarring" signal?

For every model: full 27-country leave-one-out ranking (not just Greece's
rank), in-sample R^2, and Greece's in-sample + out-of-sample residual.

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
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
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")

panel = panel.merge(debt, on=["geo", "time"], how="left")
panel = panel.merge(before, on=["geo", "time"], how="left")
panel["transfer_effect"] = panel["arop_before_transfers"] - panel["arop"]
panel = panel.merge(fin_exp, left_on=["geo", "time"], right_on=["geo", "year"], how="left").drop(columns=["year"])
panel = panel.merge(saving, left_on=["geo", "time"], right_on=["geo", "year"], how="left").drop(columns=["year"])
panel = panel.merge(gdp_hist[["geo", "time", "pct_below_peak"]], on=["geo", "time"], how="left")
panel = panel.merge(ltu, on=["geo", "time"], how="left")

vars_a = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"]
vars_c = vars_a + ["housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu_swap = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
                    "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu_add = vars_c + ["ltu_rate"]
vars_c_ltu_scarring = vars_c_ltu_swap + ["pct_below_peak"]
vars_c_ltu_expectations = vars_c_ltu_swap + ["fin_expectations", "saving_rate"]
vars_c_expectations = vars_c + ["fin_expectations", "saving_rate"]  # Model E baseline, for comparison

MODELS = {
    "C_baseline": vars_c,
    "C_LTU_swap": vars_c_ltu_swap,
    "C_LTU_add": vars_c_ltu_add,
    "C_LTU_plus_scarring": vars_c_ltu_scarring,
    "C_expectations_baseline": vars_c_expectations,
    "C_LTU_plus_expectations": vars_c_ltu_expectations,
}
LABELS = {
    "C_baseline": "C: unemployment, income, deprivation, AROP, housing, arrears, unexpected (baseline)",
    "C_LTU_swap": "C-LTU: same as C but LTU REPLACES headline unemployment (preferred)",
    "C_LTU_add": "C+LTU: LTU ADDED alongside headline unemployment (robustness only)",
    "C_LTU_plus_scarring": "C-LTU + scarring stock (% below own GDP peak)",
    "C_expectations_baseline": "C + financial expectations + saving rate (Model E baseline)",
    "C_LTU_plus_expectations": "C-LTU + financial expectations + saving rate",
}

scorecard = []
loo_full_tables = {}
for name, vars_ in MODELS.items():
    d = panel.dropna(subset=vars_ + ["subjective_poverty"]).copy()
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d["predicted"] = m.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr_in = d[d.geo == "EL"]["residual"].mean()

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
    loo_full_tables[name] = loo

    key_coefs = {}
    for v in ["unemployment_rate", "ltu_rate", "fin_expectations", "saving_rate", "pct_below_peak"]:
        if v in vars_:
            key_coefs[v] = (round(m.params[v], 3), round(m.pvalues[v], 4))

    scorecard.append({
        "model": name,
        "label": LABELS[name],
        "n_countries": d.geo.nunique(),
        "n_obs": len(d),
        "r2": round(m.rsquared, 3),
        "gr_avg_residual_insample": round(gr_in, 2),
        "gr_avg_residual_oos": round(gr_loo_row["avg_residual"], 2),
        "gr_rank_oos": f"{int(gr_loo_row['rank'])}/{len(loo)}",
        "key_coefficients": key_coefs,
    })

scorecard_df = pd.DataFrame(scorecard)
scorecard_df.to_csv(f"{OUT}/model_scorecard_ltu.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 200)
print(scorecard_df.drop(columns=["key_coefficients"]).to_string(index=False))
print()
for row in scorecard:
    print(f"{row['model']:28s} key coefficients: {row['key_coefficients']}")

print("\n\n=== Full 27-country LOO ranking, Model C-LTU (swap, preferred spec) ===")
print(loo_full_tables["C_LTU_swap"].round(2).to_string(index=False))

print("\n\n=== Full 27-country LOO ranking, Model C (baseline), for comparison ===")
print(loo_full_tables["C_baseline"].round(2).to_string(index=False))

print("\n\n=== Does LTU reduce the apparent role of financial expectations? ===")
print("Model E baseline (C + fin_expectations + saving_rate), headline unemployment:")
row_e = next(r for r in scorecard if r["model"] == "C_expectations_baseline")
print(f"  R2={row_e['r2']}  fin_expectations coef/p={row_e['key_coefficients'].get('fin_expectations')}  saving_rate coef/p={row_e['key_coefficients'].get('saving_rate')}")
print("Model C-LTU + fin_expectations + saving_rate, LTU instead of headline unemployment:")
row_le = next(r for r in scorecard if r["model"] == "C_LTU_plus_expectations")
print(f"  R2={row_le['r2']}  fin_expectations coef/p={row_le['key_coefficients'].get('fin_expectations')}  saving_rate coef/p={row_le['key_coefficients'].get('saving_rate')}  ltu_rate coef/p={row_le['key_coefficients'].get('ltu_rate')}")
