"""P2c: youth unemployment. User's hypothesis: not a "general hardship"
variable like headline or long-term unemployment, but specifically youth
labor-market scarring and exit pressure -- so it's tested directly against
both long-term unemployment (does it add anything LTU doesn't already
capture?) and migration (does it help explain the emigration story?).

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
"""
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import pearsonr
from statsmodels.stats.outliers_influence import variance_inflation_factor

from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
YEARS = range(2000, 2025)
EU = eu_members(2024)

# --- 1. Feasibility + fetch ---
youth = fetch("une_rt_a", sex="T", age="Y15-24", unit="PC_ACT", time=YEARS)
youth = youth[["geo", "time", "value"]].rename(columns={"value": "youth_unemployment_rate"})
youth.to_csv(f"{RAW}/panel_youth_unemployment.csv", index=False)

panel = youth[youth.geo.isin(EU)].copy()
print(f"Coverage: {panel.geo.nunique()} of {len(EU)} EU countries")
print(panel.groupby("geo").time.count().describe())

# --- 2. Descriptive ---
print("\n=== Greece: youth unemployment rate (15-24, % of youth labor force) ===")
gr = panel[panel.geo == "EL"].sort_values("time")
print(gr.round(1).to_string(index=False))
peak_row = gr.loc[gr["youth_unemployment_rate"].idxmax()]
latest_row = gr[gr.time == gr.time.max()].iloc[0]
first_row = gr[gr.time == gr.time.min()].iloc[0]
print(f"\nGreece youth unemployment peak: {peak_row['youth_unemployment_rate']:.1f} in {int(peak_row['time'])}")
print(f"Greece youth unemployment latest ({int(latest_row['time'])}): {latest_row['youth_unemployment_rate']:.1f}")
print(f"Greece youth unemployment first available ({int(first_row['time'])}): {first_row['youth_unemployment_rate']:.1f}")
print(f"Distance from first-available to latest: {latest_row['youth_unemployment_rate'] - first_row['youth_unemployment_rate']:+.1f} points")

latest_year = panel.time.max()
comp = panel[panel.time == latest_year][["geo", "youth_unemployment_rate"]].sort_values("youth_unemployment_rate", ascending=False)
comp.to_csv(f"{OUT}/youth_unemployment_cross_country_latest.csv", index=False)
print(f"\n=== Youth unemployment rate, {latest_year}, all 27 EU countries, highest first ===")
print(comp.round(1).to_string(index=False))

print("\n=== Greece vs. other high-youth-unemployment crisis countries, peak vs latest ===")
for c in ["EL", "ES", "IT", "HR", "PT"]:
    d = panel[panel.geo == c].sort_values("time")
    if d.empty:
        continue
    pk = d.loc[d["youth_unemployment_rate"].idxmax()]
    lt = d[d.time == d.time.max()].iloc[0]
    print(f"  {c}: peak {pk['youth_unemployment_rate']:.1f} ({int(pk['time'])}) -> latest {lt['youth_unemployment_rate']:.1f} ({int(lt['time'])})")

# --- 3. Correlation (Greece-only, matching Section 4 table format) ---
gr_y = gr[["time", "youth_unemployment_rate"]].rename(columns={"time": "year"})
subj = pd.read_csv(f"{OUT}/master_table.csv")[["year", "gr_subjective_poverty"]]
merged = gr_y.merge(subj, on="year").dropna()
print(f"\n=== Greece: youth unemployment vs subjective poverty (n={len(merged)}) ===")
if len(merged) >= 5:
    r0, p0 = pearsonr(merged["youth_unemployment_rate"], merged["gr_subjective_poverty"])
    d1 = merged.diff().dropna()
    r1, p1 = pearsonr(d1["youth_unemployment_rate"], d1["gr_subjective_poverty"])
    import numpy as np
    def detrend(series, years):
        coeffs = np.polyfit(years, series, 1)
        return series - np.polyval(coeffs, years)
    det_x = detrend(merged["youth_unemployment_rate"].values, merged["year"].values)
    det_y = detrend(merged["gr_subjective_poverty"].values, merged["year"].values)
    r2, p2 = pearsonr(det_x, det_y)
    print(f"Level correlation: r={r0:.3f}, p={p0:.4f}, n={len(merged)}")
    print(f"First-difference correlation: r={r1:.3f}, p={p1:.4f}, n={len(d1)}")
    print(f"Detrended correlation: r={r2:.3f}, p={p2:.4f}, n={len(merged)}")

# --- 4. Overlap: vs headline unemployment, vs LTU, vs migration ---
print("\n=== Overlap checks (Greece-only levels) ===")
ext = pd.read_csv(f"{OUT}/panel_extended.csv")
gr_ext = ext[ext.geo == "EL"][["time", "unemployment_rate"]]
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")
gr_ltu = ltu[ltu.geo == "EL"][["time", "ltu_rate"]]
migration = pd.read_csv(f"{RAW}/migration_nationals_panel.csv")
gr_mig = migration[migration.geo == "EL"][["time", "net_migration_nationals"]]

check = gr_y.rename(columns={"year": "time"}).merge(gr_ext, on="time").merge(gr_ltu, on="time").merge(gr_mig, on="time", how="left")
for col in ["unemployment_rate", "ltu_rate", "net_migration_nationals"]:
    d = check[["youth_unemployment_rate", col]].dropna()
    if len(d) >= 5:
        r, p = pearsonr(d["youth_unemployment_rate"], d[col])
        print(f"  vs {col:28s} r={r:+.3f}  p={p:.4f}  n={len(d)}")

# panel-wide (all countries) overlap with headline and LTU
panel_wide = ext.merge(ltu, on=["geo", "time"], how="inner").merge(panel, on=["geo", "time"], how="inner")
print("\n=== Overlap checks (panel-wide, all countries/years) ===")
for col in ["unemployment_rate", "ltu_rate"]:
    d = panel_wide[["youth_unemployment_rate", col]].dropna()
    r, p = pearsonr(d["youth_unemployment_rate"], d[col])
    print(f"  vs {col:28s} r={r:+.3f}  p={p:.4g}  n={len(d)}")

# --- 5. Model tests: replace headline unemployment; add to C-LTU as robustness ---
print("\n=== Model tests ===")
RAW2 = RAW
debt = pd.read_csv(f"{RAW2}/panel_debt_to_income.csv")
before = pd.read_csv(f"{RAW2}/panel_arop_before_transfers.csv")

panel_full = ext.merge(debt, on=["geo", "time"], how="left")
panel_full = panel_full.merge(before, on=["geo", "time"], how="left")
panel_full["transfer_effect"] = panel_full["arop_before_transfers"] - panel_full["arop"]
panel_full = panel_full.merge(ltu, on=["geo", "time"], how="left")
panel_full = panel_full.merge(panel, on=["geo", "time"], how="left")

vars_c = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
          "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_youth_swap = ["youth_unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
                      "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu_plus_youth = vars_c_ltu + ["youth_unemployment_rate"]

MODELS = {
    "C_baseline": vars_c,
    "C_LTU_swap": vars_c_ltu,
    "C_youth_swap": vars_c_youth_swap,
    "C_LTU_plus_youth": vars_c_ltu_plus_youth,
}
LABELS = {
    "C_baseline": "C: headline unemployment (baseline)",
    "C_LTU_swap": "C-LTU: long-term unemployment replaces headline",
    "C_youth_swap": "C-youth: youth unemployment replaces headline",
    "C_LTU_plus_youth": "C-LTU + youth unemployment (robustness: does youth add anything on top of LTU?)",
}

results = []
for name, vars_ in MODELS.items():
    d = panel_full.dropna(subset=vars_ + ["subjective_poverty"]).copy()
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
    gr_row = loo[loo.geo == "EL"].iloc[0]
    loo.to_csv(f"{OUT}/scorecard_loo_{name}.csv", index=False)

    coefs = {}
    for v in ["unemployment_rate", "ltu_rate", "youth_unemployment_rate"]:
        if v in vars_:
            coefs[v] = (round(m.params[v], 4), round(m.pvalues[v], 4))

    print(f"\n{LABELS[name]}: n_countries={d.geo.nunique()} n_obs={len(d)} R2={m.rsquared:.3f}")
    print(f"  Greece in-sample residual: {gr_in:.2f}")
    print(f"  Greece LOO residual: {gr_row['avg_residual']:.2f}  rank {int(gr_row['rank'])}/{len(loo)}")
    print(f"  coefficients: {coefs}")
    results.append({"model": name, "label": LABELS[name], "n_countries": d.geo.nunique(), "n_obs": len(d),
                     "r2": round(m.rsquared, 3), "gr_insample": round(gr_in, 2),
                     "gr_loo": round(gr_row["avg_residual"], 2), "gr_rank": f"{int(gr_row['rank'])}/{len(loo)}"})

pd.DataFrame(results).to_csv(f"{OUT}/model_scorecard_youth.csv", index=False)

# --- VIF check for C-LTU + youth ---
print("\n=== VIF check, C-LTU + youth unemployment ===")
d = panel_full.dropna(subset=vars_c_ltu_plus_youth + ["subjective_poverty"]).copy()
X = d[vars_c_ltu_plus_youth].copy()
X = (X - X.mean()) / X.std()
X["const"] = 1
vifs = {v: variance_inflation_factor(X.values, i) for i, v in enumerate(X.columns) if v != "const"}
for k, v in sorted(vifs.items(), key=lambda x: -x[1]):
    print(f"  {k:28s} {v:.2f}")
