"""Income inequality checkpoint -- the final P2 item. Tests whether
average-level measures (income, GDP, deprivation, AROP) already in the
model are hiding a worse tail: does inequality itself carry independent
information about Greece's subjective-poverty gap?

Two measures: Gini coefficient (post-transfer, disposable income,
ilc_di12) and S80/S20 income quintile share ratio (ilc_di11). Gini's
age-broken-down series only covers 2014-2024 for Greece; S80/S20 covers
2003-2024 -- both checked directly, not assumed, and both used, with the
coverage difference flagged.

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import pearsonr

from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
EU = eu_members(2024)

# --- 1. Feasibility + fetch ---
gini = fetch("ilc_di12", age="TOTAL", statinfo="GINI_HND", time=range(2000, 2025))
gini = gini[["geo", "time", "value"]].rename(columns={"value": "gini"})
gini.to_csv(f"{RAW}/panel_gini.csv", index=False)

s8020 = fetch("ilc_di11", age="TOTAL", sex="T", unit="RAT", time=range(2000, 2025))
s8020 = s8020[["geo", "time", "value"]].rename(columns={"value": "s80s20"})
s8020.to_csv(f"{RAW}/panel_s80s20.csv", index=False)

gini_eu = gini[gini.geo.isin(EU)]
s8020_eu = s8020[s8020.geo.isin(EU)]
print(f"Gini: {gini_eu.geo.nunique()} countries, years {gini_eu.time.min()}-{gini_eu.time.max()}")
print(f"S80/S20: {s8020_eu.geo.nunique()} countries, years {s8020_eu.time.min()}-{s8020_eu.time.max()}")

# --- 2. Descriptive: Greece trend ---
print("\n=== Greece: Gini coefficient (post-transfer disposable income) ===")
gr_gini = gini[gini.geo == "EL"].sort_values("time")
print(gr_gini[["time", "gini"]].to_string(index=False))

print("\n=== Greece: S80/S20 ratio ===")
gr_s8020 = s8020[s8020.geo == "EL"].sort_values("time")
print(gr_s8020[["time", "s80s20"]].to_string(index=False))

peak_row = gr_s8020.loc[gr_s8020["s80s20"].idxmax()]
trough_row = gr_s8020.loc[gr_s8020["s80s20"].idxmin()]
latest_row = gr_s8020[gr_s8020.time == gr_s8020.time.max()].iloc[0]
first_row = gr_s8020[gr_s8020.time == gr_s8020.time.min()].iloc[0]
print(f"\nS80/S20 peak: {peak_row['s80s20']:.2f} in {int(peak_row['time'])}")
print(f"S80/S20 trough: {trough_row['s80s20']:.2f} in {int(trough_row['time'])}")
print(f"S80/S20 first available ({int(first_row['time'])}): {first_row['s80s20']:.2f}")
print(f"S80/S20 latest ({int(latest_row['time'])}): {latest_row['s80s20']:.2f}")

# --- EU ranking, latest year ---
latest_year_s = s8020.time.max()
comp_s = s8020[(s8020.time == latest_year_s) & (s8020.geo.isin(EU))].sort_values("s80s20", ascending=False)
comp_s.to_csv(f"{OUT}/s80s20_cross_country_latest.csv", index=False)
print(f"\n=== S80/S20, {latest_year_s}, all 27 EU countries, highest first ===")
print(comp_s[["geo", "s80s20"]].to_string(index=False))
gr_rank_s = comp_s.reset_index(drop=True)
gr_rank_s = gr_rank_s[gr_rank_s.geo == "EL"].index[0] + 1
print(f"Greece rank: {gr_rank_s} of {len(comp_s)}")

latest_year_g = gini.time.max()
comp_g = gini[(gini.time == latest_year_g) & (gini.geo.isin(EU))].sort_values("gini", ascending=False)
comp_g.to_csv(f"{OUT}/gini_cross_country_latest.csv", index=False)
print(f"\n=== Gini, {latest_year_g}, all 27 EU countries, highest first ===")
print(comp_g[["geo", "gini"]].to_string(index=False))
gr_rank_g = comp_g.reset_index(drop=True)
gr_rank_g = gr_rank_g[gr_rank_g.geo == "EL"].index[0] + 1
print(f"Greece rank: {gr_rank_g} of {len(comp_g)}")

# --- Compare against countries with high subjective poverty but different inequality ---
print("\n=== Cross-check: subjective poverty vs inequality, selected countries, latest year ===")
ext = pd.read_csv(f"{OUT}/panel_extended.csv")
subj_latest = ext[ext.time == ext.time.max()][["geo", "subjective_poverty"]]
check = comp_s.merge(subj_latest, on="geo", how="left")
print(check.sort_values("subjective_poverty", ascending=False).head(10)[["geo", "s80s20", "subjective_poverty"]].to_string(index=False))

# --- 3. Correlation (Greece-only, matching Section 4 table format) ---
gr_s8020_y = gr_s8020[["time", "s80s20"]].rename(columns={"time": "year"})
subj = pd.read_csv(f"{OUT}/master_table.csv")[["year", "gr_subjective_poverty"]]
merged = gr_s8020_y.merge(subj, on="year").dropna()
print(f"\n=== Greece: S80/S20 vs subjective poverty (n={len(merged)}) ===")
if len(merged) >= 5:
    r0, p0 = pearsonr(merged["s80s20"], merged["gr_subjective_poverty"])
    d1 = merged.diff().dropna()
    r1, p1 = pearsonr(d1["s80s20"], d1["gr_subjective_poverty"])

    def detrend(series, years):
        coeffs = np.polyfit(years, series, 1)
        return series - np.polyval(coeffs, years)
    det_x = detrend(merged["s80s20"].values, merged["year"].values)
    det_y = detrend(merged["gr_subjective_poverty"].values, merged["year"].values)
    r2, p2 = pearsonr(det_x, det_y)
    print(f"Level: r={r0:.3f}, p={p0:.4f}, n={len(merged)}")
    print(f"First-difference: r={r1:.3f}, p={p1:.4f}, n={len(d1)}")
    print(f"Detrended: r={r2:.3f}, p={p2:.4f}")

gr_gini_y = gr_gini[["time", "gini"]].rename(columns={"time": "year"})
merged_g = gr_gini_y.merge(subj, on="year").dropna()
print(f"\n=== Greece: Gini vs subjective poverty (n={len(merged_g)}, short series, 2014-2024) ===")
if len(merged_g) >= 5:
    r0, p0 = pearsonr(merged_g["gini"], merged_g["gr_subjective_poverty"])
    d1 = merged_g.diff().dropna()
    r1, p1 = pearsonr(d1["gini"], d1["gr_subjective_poverty"])
    print(f"Level: r={r0:.3f}, p={p0:.4f}, n={len(merged_g)}")
    print(f"First-difference: r={r1:.3f}, p={p1:.4f}, n={len(d1)}")

# --- 4. Model test: overlap with existing predictors, add to Model C-LTU ---
print("\n=== Overlap check: S80/S20 vs existing Model predictors (Greece-only levels) ===")
gr_ext = ext[ext.geo == "EL"][["time", "unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"]]
check2 = gr_s8020_y.rename(columns={"year": "time"}).merge(gr_ext, on="time").dropna()
for col in ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"]:
    d = check2[["s80s20", col]].dropna()
    if len(d) >= 5:
        r, p = pearsonr(d["s80s20"], d[col])
        print(f"  vs {col:28s} r={r:+.3f}  p={p:.4f}  n={len(d)}")

print("\n=== Model test: does S80/S20 add anything to Model C-LTU? ===")
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")
panel_full = ext.merge(ltu, on=["geo", "time"], how="left").merge(s8020, on=["geo", "time"], how="left")

vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu_plus_ineq = vars_c_ltu + ["s80s20"]


def fit_and_loo(vars_, label):
    d = panel_full.dropna(subset=vars_ + ["subjective_poverty"]).copy()
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d["predicted"] = m.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
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
    print(f"\n{label}: n_countries={d.geo.nunique()} n_obs={len(d)} R2={m.rsquared:.3f}")
    print(f"  Greece in-sample residual: {d[d.geo=='EL']['residual'].mean():.2f}")
    print(f"  Greece LOO residual: {gr_row['avg_residual']:.2f}  rank {int(gr_row['rank'])}/{len(loo)}")
    if "s80s20" in vars_:
        print(f"  s80s20 coefficient: {m.params['s80s20']:.4f}  p={m.pvalues['s80s20']:.4f}")
    return m


fit_and_loo(vars_c_ltu, "Model C-LTU (baseline)")
fit_and_loo(vars_c_ltu_plus_ineq, "Model C-LTU + S80/S20 (robustness)")

# --- FDR status if added to Section 4 correlation family ---
print("\n(FDR status will be checked via the full pipeline re-run, not here -- matches project precedent)")
