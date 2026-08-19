"""Year-by-year dynamics: does the RATE of change (and its acceleration) in each
predictor explain subjective poverty better than the LEVEL, and does Greece's
sensitivity to those changes differ from other EU countries? Also tests the
user's own "wealth loss compounds over time" hypothesis properly: not as a
single cross-sectional peak-to-trough number per country (script 12's approach)
but as a time-varying "how far below your own historical peak are you THIS
YEAR" stock variable inside the full panel regression.
"""
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import statsmodels.formula.api as smf
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"

panel = pd.read_csv(f"{OUT}/panel_extended.csv")
gdp_hist = pd.read_csv(f"{RAW}/panel_gdp_history_2008_2024.csv")

VARS = ["subjective_poverty", "arop", "unemployment_rate", "real_gdp_pc",
        "severe_mat_soc_deprivation", "aic_pps_pc", "housing_cost_overburden",
        "arrears", "unexpected_expenses"]

# ---------------------------------------------------------------------------
# 1. Time-varying "scarring stock": % below running historical peak, per year
#    (uses the longer 2008-2024 GDP history so the peak isn't clipped to 2015)
# ---------------------------------------------------------------------------
gdp_hist = gdp_hist.sort_values(["geo", "time"]).reset_index(drop=True)
gdp_hist["running_peak"] = gdp_hist.groupby("geo")["real_gdp_pc"].cummax()
gdp_hist["pct_below_peak"] = 100 * (gdp_hist["running_peak"] - gdp_hist["real_gdp_pc"]) / gdp_hist["running_peak"]
scarring = gdp_hist[["geo", "time", "pct_below_peak"]]

panel = panel.merge(scarring, on=["geo", "time"], how="left")

print("=== Scarring stock (% below own historical real-GDP/capita peak), latest year ===")
latest = panel.sort_values("time").groupby("geo").tail(1)[["geo", "time", "pct_below_peak"]]
print(latest.sort_values("pct_below_peak", ascending=False).round(1).to_string(index=False))

# ---------------------------------------------------------------------------
# 2. First and second differences, per country, for every variable
# ---------------------------------------------------------------------------
panel = panel.sort_values(["geo", "time"]).reset_index(drop=True)
for v in VARS:
    panel[f"d_{v}"] = panel.groupby("geo")[v].diff()
    panel[f"d2_{v}"] = panel.groupby("geo")[f"d_{v}"].diff()

panel.to_csv(f"{OUT}/panel_with_diffs.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Country-by-country sensitivity: within each country, correlate
#    Δpredictor with Δsubjective_poverty across its own year-over-year moves.
#    This is different from the pooled first-diff correlations already run in
#    script 10/18 — it asks "whose subjective poverty moves in step with its
#    own economic swings the most/least," not just "does the pooled EU pattern
#    hold." Report Greece's rank in this distribution for each predictor.
# ---------------------------------------------------------------------------
predictors = ["arop", "unemployment_rate", "real_gdp_pc", "severe_mat_soc_deprivation",
              "aic_pps_pc", "housing_cost_overburden", "arrears", "unexpected_expenses",
              "pct_below_peak"]

print("\n=== Country-by-country sensitivity: corr(Δpredictor, Δsubjective_poverty) ===")
sensitivity = {}
for p in predictors:
    rows = []
    for geo, g in panel.groupby("geo"):
        d = g.dropna(subset=[f"d_{p}" if p != "pct_below_peak" else "pct_below_peak", "d_subjective_poverty"]) \
            if p != "pct_below_peak" else g.dropna(subset=["pct_below_peak", "d_subjective_poverty"])
        x = d[f"d_{p}"] if p != "pct_below_peak" else d["pct_below_peak"]
        y = d["d_subjective_poverty"]
        if len(d) >= 5 and x.std() > 0:
            r, pv = pearsonr(x, y)
            rows.append({"geo": geo, "r": r, "n": len(d)})
    df = pd.DataFrame(rows).sort_values("r", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    sensitivity[p] = df
    df.to_csv(f"{OUT}/sensitivity_{p}.csv", index=False)
    gr = df[df.geo == "EL"]
    if len(gr):
        print(f"{p:28s} Greece r={gr.r.values[0]:+.2f}  rank {gr['rank'].values[0]}/{len(df)}  "
              f"(median r={df.r.median():+.2f}, EU range [{df.r.min():+.2f}, {df.r.max():+.2f}])")

# ---------------------------------------------------------------------------
# 4. Model F: add the time-varying scarring stock to the Model C predictor set
#    in the full panel regression (year FE, country-clustered SEs). This is
#    the properly-specified test of "does being further below your own past
#    peak, right now, predict extra subjective poverty, controlling for
#    current income/unemployment/deprivation/arrears levels?"
# ---------------------------------------------------------------------------
vars_c = ["unemployment_rate", "aic_pps_pc", "severe_mat_soc_deprivation", "arop",
          "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_f = vars_c + ["pct_below_peak"]

print("\n=== Model F: Model C + time-varying scarring stock (% below own peak) ===")
d = panel.dropna(subset=vars_f + ["subjective_poverty"])
d = d[d.geo.isin(eu_members(2024))]
formula_c = "subjective_poverty ~ " + " + ".join(vars_c) + " + C(time)"
formula_f = "subjective_poverty ~ " + " + ".join(vars_f) + " + C(time)"
mc = smf.ols(formula_c, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
mf = smf.ols(formula_f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
d = d.copy()
d["resid_c"] = d["subjective_poverty"] - mc.predict(d)
d["resid_f"] = d["subjective_poverty"] - mf.predict(d)
print(f"Model C: R2={mc.rsquared:.3f}, n={len(d)}, countries={d.geo.nunique()}")
print(f"Model F: R2={mf.rsquared:.3f}")
print(f"pct_below_peak coef={mf.params['pct_below_peak']:.4f}  p={mf.pvalues['pct_below_peak']:.4f}")
gr = d[d.geo == "EL"].sort_values("time")
print(f"Greece avg residual, Model C: {gr.resid_c.mean():.1f}  ->  Model F: {gr.resid_f.mean():.1f}")

# leave-Greece-out for Model F
train = d[d.geo != "EL"]
mf_lgo = smf.ols(formula_f, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
gr_test = d[d.geo == "EL"].copy()
gr_test["predicted_lgo"] = mf_lgo.predict(gr_test)
gr_test["residual_lgo"] = gr_test["subjective_poverty"] - gr_test["predicted_lgo"]
print(f"\nLeave-Greece-out, Model F: avg out-of-sample residual = {gr_test.residual_lgo.mean():.1f}")

# leave-one-out all countries, Model F
rows = []
for c in sorted(d["geo"].unique()):
    tr = d[d.geo != c]
    te = d[d.geo == c].copy()
    m = smf.ols(formula_f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
    te["predicted"] = m.predict(te)
    te["residual"] = te["subjective_poverty"] - te["predicted"]
    rows.append({"geo": c, "avg_residual": te["residual"].mean(), "n_years": len(te)})
loo_f = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
loo_f["rank"] = loo_f.index + 1
loo_f.to_csv(f"{OUT}/leave_one_out_modelF.csv", index=False)
print("\n=== Leave-one-out, Model F, all countries (top 8) ===")
print(loo_f.head(8).round(1).to_string(index=False))
print(f"Greece rank: {loo_f[loo_f.geo=='EL']['rank'].values[0]} / {len(loo_f)}")

# ---------------------------------------------------------------------------
# 5. Second differences ("acceleration"): does an ACCELERATING deterioration
#    predict accelerating subjective pain more than a steady one?
# ---------------------------------------------------------------------------
print("\n=== Pooled: corr(Δ² predictor, Δ² subjective_poverty) ===")
for p in ["arop", "unemployment_rate", "real_gdp_pc", "severe_mat_soc_deprivation", "arrears"]:
    dd = panel.dropna(subset=[f"d2_{p}", "d2_subjective_poverty"])
    if len(dd) >= 10:
        r, pv = pearsonr(dd[f"d2_{p}"], dd["d2_subjective_poverty"])
        print(f"{p:28s} r={r:+.3f}  p={pv:.4f}  n={len(dd)}")

# ---------------------------------------------------------------------------
# 6. Does a country's DIFF-sensitivity (section 3) relate to the SIZE of its
#    cross-country outlier gap (Section 9's Model C leave-one-out residual)?
#    This is the direct test of "do the year-by-year diffs relate to the gap,
#    or are they a separate question" — sensitivity and gap-size are distinct
#    metrics, so this checks whether they're correlated at all across the 27
#    countries, not just within Greece.
# ---------------------------------------------------------------------------
loo_c = pd.read_csv(f"{OUT}/leave_one_out_all_countries.csv")[["geo", "avg_residual"]]
print("\n=== Does Δ-sensitivity relate to a country's own outlier gap (Model C LOO residual)? ===")
gap_rows = []
for p in predictors:
    sens = pd.read_csv(f"{OUT}/sensitivity_{p}.csv")[["geo", "r"]]
    m = loo_c.merge(sens, on="geo", how="inner")
    r_all, p_all = pearsonr(m["avg_residual"], m["r"])
    m_excl = m[m.geo != "EL"]
    r_excl, p_excl = pearsonr(m_excl["avg_residual"], m_excl["r"])
    gap_rows.append({"predictor": p, "r_with_greece": r_all, "p_with_greece": p_all,
                      "r_excl_greece": r_excl, "p_excl_greece": p_excl, "n": len(m)})
    print(f"{p:28s} with Greece: r={r_all:+.3f} p={p_all:.4f}  |  excl. Greece: r={r_excl:+.3f} p={p_excl:.4f}")
pd.DataFrame(gap_rows).to_csv(f"{OUT}/sensitivity_vs_gap.csv", index=False)
