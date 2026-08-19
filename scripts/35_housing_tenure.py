"""Housing tenure checkpoint. User's framing: a different question from
prior P2 items -- not "is housing expensive" (already covered via the
existing housing_cost_overburden variable) but "who is exposed, and how
does tenure status change the burden." Treated as its own careful
checkpoint, not combined with other items.

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
"""
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import pearsonr

from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
EU = eu_members(2024)

# --- 1. Feasibility ---
print("=== Feasibility ===")
dist = fetch("ilc_lvho02", rskpovth="TOTAL", hhcomp="TOTAL", unit="PC", time=range(2003, 2025))
dist_eu = dist[dist.geo.isin(EU)]
print(f"ilc_lvho02 (tenure distribution): {dist_eu.geo.nunique()} countries, "
      f"years {dist_eu.time.min()}-{dist_eu.time.max()}")

burden = fetch("ilc_lvho07c", unit="PC", time=range(2003, 2025))
burden_eu = burden[burden.geo.isin(EU)]
print(f"ilc_lvho07c (housing cost overburden BY TENURE): {burden_eu.geo.nunique()} countries")
print(burden_eu.groupby("geo").time.count().describe())
dist.to_csv(f"{RAW}/panel_tenure_distribution.csv", index=False)
burden.to_csv(f"{RAW}/panel_housing_overburden_by_tenure.csv", index=False)

# --- 2. Descriptive: Greece tenure distribution over time, vs EU ---
print("\n=== Greece: tenure distribution over time ===")
gr_dist = dist[dist.geo == "EL"].pivot_table(index="time", columns="tenure", values="value")
print(gr_dist[["OWN", "OWN_L", "OWN_NL", "RENT", "RENT_FR", "RENT_MKT"]].round(1).to_string())

eu_dist = dist[dist.geo == "EU27_2020"].pivot_table(index="time", columns="tenure", values="value")
print("\n=== EU27 average: tenure distribution over time ===")
print(eu_dist[["OWN", "OWN_L", "OWN_NL", "RENT", "RENT_FR", "RENT_MKT"]].round(1).to_string())

own_2020 = gr_dist.loc[2020, "OWN"] if 2020 in gr_dist.index else None
own_latest = gr_dist.loc[gr_dist.index.max(), "OWN"]
print(f"\nGreece ownership rate: {own_2020:.1f} (2020) -> {own_latest:.1f} ({gr_dist.index.max()})")
eu_own_2020 = eu_dist.loc[2020, "OWN"] if 2020 in eu_dist.index else None
eu_own_latest = eu_dist.loc[eu_dist.index.max(), "OWN"]
print(f"EU27 ownership rate: {eu_own_2020:.1f} (2020) -> {eu_own_latest:.1f} ({eu_dist.index.max()})")

# --- 3. Housing cost overburden BY tenure, Greece, latest year ---
latest_year = burden.time.max()
print(f"\n=== Housing cost overburden by tenure, Greece, {latest_year} ===")
gr_burden = burden[(burden.geo == "EL") & (burden.time == latest_year)]
print(gr_burden[["tenure", "value"]].to_string(index=False))

print("\n=== Data-quality note: Greece's by-tenure series over time (renter subsamples are noisy) ===")
gr_burden_hist = burden[burden.geo == "EL"].pivot_table(index="time", columns="tenure", values="value")
print(gr_burden_hist[["OWN_L", "OWN_NL", "RENT_FR", "RENT_MKT", "TOTAL"]].round(1).to_string())

# --- Cross-country ranking, OWN_NL overburden (mortgage-free owners) ---
print(f"\n=== OWN_NL (mortgage-free owner) overburden rate, {latest_year}, all 27 EU countries ===")
own_nl_latest = burden[(burden.tenure == "OWN_NL") & (burden.time == latest_year) & (burden.geo.isin(EU))]
own_nl_latest = own_nl_latest.sort_values("value", ascending=False)
own_nl_latest.to_csv(f"{OUT}/own_nl_overburden_cross_country.csv", index=False)
print(own_nl_latest[["geo", "value"]].to_string(index=False))

# --- Owner-renter gap, cross-country ---
print(f"\n=== Owner-renter overburden gap (RENT_MKT - OWN_NL), {latest_year} ===")
piv_latest = burden[(burden.time == latest_year) & (burden.geo.isin(EU))].pivot_table(
    index="geo", columns="tenure", values="value")
piv_latest["gap"] = piv_latest["RENT_MKT"] - piv_latest["OWN_NL"]
piv_latest = piv_latest.sort_values("gap", ascending=False)
piv_latest.to_csv(f"{OUT}/tenure_overburden_gap_cross_country.csv")
print(piv_latest[["OWN_NL", "RENT_MKT", "TOTAL", "gap"]].round(1).to_string())
gr_gap_rank = list(piv_latest.index).index("EL") + 1
print(f"\nGreece's owner-renter gap rank: {gr_gap_rank} of {len(piv_latest)} (1=largest gap)")

# --- 4. Cross-country correlation: OWN_NL overburden vs subjective poverty (single year) ---
print("\n=== Cross-country correlation: OWN_NL overburden vs subjective poverty (single year, latest) ===")
ext = pd.read_csv(f"{OUT}/panel_extended.csv")
subj_latest = ext[ext.time == ext.time.max()][["geo", "subjective_poverty", "housing_cost_overburden"]]
own_nl_merge = own_nl_latest[["geo", "value"]].rename(columns={"value": "own_nl_overburden"})
merged = own_nl_merge.merge(subj_latest, on="geo")
r, p = pearsonr(merged["own_nl_overburden"], merged["subjective_poverty"])
print(f"OWN_NL overburden vs subjective poverty: r={r:.3f}, p={p:.4f}, n={len(merged)}")

# --- Greece-only time series correlation (TOTAL housing overburden already tested; check OWN_NL specifically) ---
gr_own_nl_series = burden[(burden.geo == "EL") & (burden.tenure == "OWN_NL")][["time", "value"]].rename(
    columns={"value": "own_nl_overburden", "time": "year"})
subj = pd.read_csv(f"{OUT}/master_table.csv")[["year", "gr_subjective_poverty"]]
gr_merged = gr_own_nl_series.merge(subj, on="year").dropna()
print(f"\n=== Greece-only: OWN_NL overburden vs subjective poverty over time (n={len(gr_merged)}) ===")
if len(gr_merged) >= 5:
    r0, p0 = pearsonr(gr_merged["own_nl_overburden"], gr_merged["gr_subjective_poverty"])
    print(f"Level correlation: r={r0:.3f}, p={p0:.4f}")

# --- 5. Multicollinearity + model test: OWN_NL overburden vs existing housing_cost_overburden ---
print("\n=== Multicollinearity check: OWN_NL overburden vs existing housing_cost_overburden (TOTAL) ===")
own_nl_panel = burden[burden.tenure == "OWN_NL"][["geo", "time", "value"]].rename(columns={"value": "own_nl_overburden"})
panel_check = ext.merge(own_nl_panel, on=["geo", "time"], how="inner")
r_panel, p_panel = pearsonr(panel_check["own_nl_overburden"], panel_check["housing_cost_overburden"])
print(f"Panel-wide (all countries/years): r={r_panel:.3f}, p={p_panel:.4g}, n={len(panel_check)}")
gr_check = panel_check[panel_check.geo == "EL"]
if len(gr_check) >= 5:
    r_gr, p_gr = pearsonr(gr_check["own_nl_overburden"], gr_check["housing_cost_overburden"])
    print(f"Greece-only: r={r_gr:.3f}, p={p_gr:.4f}, n={len(gr_check)}")

print("\n=== Model test: does OWN_NL overburden add anything on top of Model C (which already has TOTAL housing_cost_overburden)? ===")
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")
panel_full = ext.merge(ltu, on=["geo", "time"], how="left").merge(own_nl_panel, on=["geo", "time"], how="left")

vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu_plus_ownnl = vars_c_ltu + ["own_nl_overburden"]


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
    if "own_nl_overburden" in vars_:
        print(f"  own_nl_overburden coefficient: {m.params['own_nl_overburden']:.4f}  p={m.pvalues['own_nl_overburden']:.4f}")
    return m


fit_and_loo(vars_c_ltu, "Model C-LTU (baseline, already has TOTAL housing_cost_overburden)")
fit_and_loo(vars_c_ltu_plus_ownnl, "Model C-LTU + own_nl_overburden (robustness)")
