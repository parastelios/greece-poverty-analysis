"""Export a compact JSON bundle for the final HTML report."""
import json
import pandas as pd

OUT = "../data/processed"
df = pd.read_csv(f"{OUT}/analysis_dataset.csv").sort_values("year")
corr = pd.read_csv(f"{OUT}/correlations.csv")
robust = pd.read_csv(f"{OUT}/correlations_robustness.csv")
spearman = pd.read_csv(f"{OUT}/correlations_spearman.csv")
leadlag = pd.read_csv(f"{OUT}/correlations_leadlag.csv")
anchor = pd.read_csv(f"{OUT}/anchored_poverty.csv")
panel = pd.read_csv(f"{OUT}/panel_with_residuals.csv")  # Model A, for the country bar chart
nested_varying = pd.read_csv(f"{OUT}/nested_models_varying.csv")
nested_balanced = pd.read_csv(f"{OUT}/nested_models_balanced.csv")
lgo = pd.read_csv(f"{OUT}/leave_greece_out_modelC.csv")
within_between = pd.read_csv(f"{OUT}/within_vs_between_comparison.csv", index_col=0)
gr_trend_a = pd.read_csv(f"{OUT}/gr_residual_trend_A_structural.csv")
gr_trend_c = pd.read_csv(f"{OUT}/gr_residual_trend_C_plus_arrears_unexpected.csv")
nested_loo = pd.read_csv(f"{OUT}/nested_loo_summary.csv")
arope_snapshot = pd.read_csv(f"{OUT}/arope_subjective_snapshot_2025.csv")
recovery_idx = pd.read_csv(f"{OUT}/recovery_indexed_trajectories.csv")
migration = pd.read_csv("../data/raw/migration_nationals_panel.csv")


def clean(v):
    if pd.isna(v):
        return None
    if isinstance(v, float) and v == int(v):
        return round(v, 2)
    return round(v, 2) if isinstance(v, float) else v


trend = []
for _, r in df.iterrows():
    trend.append({
        "year": int(r["year"]),
        "gr_arop": clean(r.get("gr_arop")),
        "eu_arop": clean(r.get("eu_arop")),
        "gr_subj": clean(r.get("gr_subjective_poverty")),
        "eu_subj": clean(r.get("eu_subjective_poverty")),
        "gr_arop_rank": clean(r.get("gr_arop_rank")),
        "n_arop": clean(r.get("n_countries_arop")),
        "gr_arope": clean(r.get("gr_arope")),
        "eu_arope": clean(r.get("eu_arope")),
        "gr_arope_rank": clean(r.get("gr_arope_rank")),
        "n_arope": clean(r.get("n_countries_arope")),
        "gr_subj_rank": clean(r.get("gr_subj_rank")),
        "n_subj": clean(r.get("n_countries_subj")),
        "gap_arop": clean(r.get("gr_eu_arop_gap")),
        "gap_subj": clean(r.get("gr_eu_subjective_gap")),
        "unemployment": clean(r.get("gr_unemployment_rate")),
        "real_income_idx": clean(r.get("gr_real_hh_income_idx2008")),
        "real_gdp_pc": clean(r.get("gr_real_gdp_pc")),
        "threshold_real_idx": clean(r.get("gr_arop_threshold_real_idx2008")),
        "severe_dep_legacy": clean(r.get("gr_severe_mat_deprivation_legacy")),
        "severe_dep_new": clean(r.get("gr_severe_mat_soc_deprivation_new")),
    })

# merge anchored poverty into trend by year
anchor_by_year = {int(r["year"]): r for _, r in anchor.iterrows()}
for row in trend:
    a = anchor_by_year.get(row["year"])
    row["anchored_poverty"] = clean(a["anchored_poverty_rate"]) if a is not None else None

correlations = []
for _, r in corr.iterrows():
    correlations.append({
        "variable": r["variable"],
        "r0": clean(r["r_contemporaneous"]),
        "p0": clean(r["p_contemporaneous"]),
        "n0": clean(r["n_contemporaneous"]),
        "r1": clean(r["r_lag1"]),
        "p1": clean(r["p_lag1"]),
    })

robustness = []
for _, r in robust.iterrows():
    robustness.append({
        "variable": r["variable"],
        "r_level": clean(r["r_level"]),
        "r_firstdiff": clean(r["r_firstdiff"]),
        "p_firstdiff": clean(r["p_firstdiff"]),
        "r_detrended": clean(r["r_detrended"]),
        "p_detrended": clean(r["p_detrended"]),
    })

spearman_out = []
for _, r in spearman.iterrows():
    spearman_out.append({
        "variable": r["variable"],
        "pearson_level": clean(r["pearson_level"]),
        "spearman_level": clean(r["spearman_level"]),
        "pearson_diff": clean(r["pearson_diff"]),
        "spearman_diff": clean(r["spearman_diff"]),
    })

leadlag_out = []
for _, r in leadlag.iterrows():
    leadlag_out.append({
        "variable": r["variable"],
        "lag_m2": clean(r["lag_-2"]), "lag_m1": clean(r["lag_-1"]), "lag_0": clean(r["lag_+0"]),
        "lag_p1": clean(r["lag_+1"]), "lag_p2": clean(r["lag_+2"]),
    })

resid_by_country = (
    panel.groupby("geo")["residual"].mean().sort_values(ascending=False).reset_index()
)
residuals = [{"geo": r["geo"], "residual": clean(r["residual"])} for _, r in resid_by_country.iterrows()]

nested_varying_out = [
    {"model": r["model"], "n_countries": int(r["n_countries"]), "r2": clean(r["r2"]),
     "gr_avg_residual": clean(r["gr_avg_residual"]), "gr_first_year_residual": clean(r["gr_first_year_residual"]),
     "gr_last_year_residual": clean(r["gr_last_year_residual"])}
    for _, r in nested_varying.iterrows()
]
nested_balanced_out = [
    {"model": r["model"], "n_countries": int(r["n_countries"]), "r2": clean(r["r2"]),
     "gr_avg_residual": clean(r["gr_avg_residual"]), "gr_last_year_residual": clean(r["gr_last_year_residual"])}
    for _, r in nested_balanced.iterrows()
]
leave_greece_out = [
    {"year": int(r["time"]), "actual": clean(r["subjective_poverty"]), "predicted": clean(r["predicted_lgo"]), "residual": clean(r["residual_lgo"])}
    for _, r in lgo.iterrows()
]
within_between_out = {
    idx: {"pooled_between": clean(row["pooled_between (no country FE)"]), "two_way_fe": clean(row["two_way_FE (within-country)"])}
    for idx, row in within_between.iterrows()
}

gr_resid_trend_ac = []
c_by_year = {int(r["time"]): r["residual"] for _, r in gr_trend_c.iterrows()}
for _, r in gr_trend_a.iterrows():
    yr = int(r["time"])
    gr_resid_trend_ac.append({
        "year": yr,
        "resid_a": clean(r["residual"]),
        "resid_c": clean(c_by_year.get(yr)),
    })

bundle = {
    "trend": trend,
    "correlations": correlations,
    "robustness": robustness,
    "spearman": spearman_out,
    "leadlag": leadlag_out,
    "residuals_by_country": residuals,
    "nested_varying": nested_varying_out,
    "nested_balanced": nested_balanced_out,
    "leave_greece_out": leave_greece_out,
    "within_between": within_between_out,
    "gr_resid_trend_ac": gr_resid_trend_ac,
    "nested_loo": [
        {"model": r["model"], "gr_avg_residual": clean(r["gr_avg_residual"]), "gr_rank": r["gr_rank"],
         "second_highest": clean(r["second_highest"]), "second_highest_country": r["second_highest_country"]}
        for _, r in nested_loo.iterrows()
    ],
    "arope_snapshot": [
        {"geo": r["geo"], "label": r["geo_label"], "subjective": clean(r["subjective_poverty"]),
         "arope": clean(r["arope"]), "gap": clean(r["gap"])}
        for _, r in arope_snapshot.iterrows()
    ],
    "recovery_trajectory": [
        {"time": int(t), **{geo: clean(v) for geo, v in g.set_index("geo")["indexed_to_own_peak"].items()}}
        for t, g in recovery_idx.groupby("time")
    ],
    "migration_nationals": [
        {"year": int(r["time"]), "emigration": clean(r["emigration_nationals"]),
         "immigration": clean(r["immigration_nationals"]), "net": clean(r["net_migration_nationals"])}
        for _, r in migration[migration.geo == "EL"].sort_values("time").iterrows()
    ],
}

with open("../output/report_data.json", "w") as f:
    json.dump(bundle, f, indent=1)

print("Exported", len(trend), "years,", len(correlations), "correlations,", len(residuals), "countries,",
      len(nested_varying_out), "nested models")
