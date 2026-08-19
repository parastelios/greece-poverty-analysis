"""Nested leave-one-country-out: for Models A, B, and C, leave each of the 27
countries out in turn, refit on the remaining 26, and predict the excluded
country. This connects the in-sample nested-model result (Section 8: residual
falls 15.1 -> 8.8 -> 2.2 pp) with the out-of-sample leave-one-out result
(Section 9: Greece's Model-C gap is 11.6 pp) by running the SAME nested
progression out-of-sample for every country, not just Greece."""
import pandas as pd
import statsmodels.formula.api as smf

RAW = "../data/raw"
OUT = "../data/processed"

panel = pd.read_csv(f"{OUT}/panel_extended.csv")

MODELS = {
    "A_structural": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"],
    "B_plus_housing": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop", "housing_cost_overburden"],
    "C_plus_arrears_unexpected": ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop", "housing_cost_overburden", "arrears", "unexpected_expenses"],
}

all_results = {}
for model_name, vars_ in MODELS.items():
    d = panel.dropna(subset=vars_ + ["subjective_poverty"])
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    countries = sorted(d["geo"].unique())
    rows = []
    for c in countries:
        train = d[d.geo != c]
        test = d[d.geo == c].copy()
        model = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
        test["predicted"] = model.predict(test)
        test["residual"] = test["subjective_poverty"] - test["predicted"]
        rows.append({
            "geo": c,
            "avg_residual": test["residual"].mean(),
            "n_years": len(test),
        })
    result = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
    result["rank"] = result.index + 1
    all_results[model_name] = result
    result.to_csv(f"{OUT}/nested_loo_{model_name}.csv", index=False)

print("=" * 78)
print("GREECE'S OUT-OF-SAMPLE GAP ACROSS THE NESTED MODEL PROGRESSION")
print("=" * 78)
summary_rows = []
for model_name, result in all_results.items():
    gr_row = result[result.geo == "EL"].iloc[0]
    others = result[result.geo != "EL"]["avg_residual"]
    n = len(result)
    summary_rows.append({
        "model": model_name,
        "gr_avg_residual": round(gr_row["avg_residual"], 1),
        "gr_rank": f"{int(gr_row['rank'])}/{n}",
        "others_mean": round(others.mean(), 1),
        "others_sd": round(others.std(), 1),
        "second_highest": round(others.max(), 1),
        "second_highest_country": result[result.geo != "EL"].sort_values("avg_residual", ascending=False).iloc[0]["geo"],
    })
summary = pd.DataFrame(summary_rows)
print(summary.to_string(index=False))
summary.to_csv(f"{OUT}/nested_loo_summary.csv", index=False)

print("\n\nFull rankings per model:")
for model_name, result in all_results.items():
    print(f"\n--- {model_name} ---")
    print(result.round(1).to_string(index=False))
