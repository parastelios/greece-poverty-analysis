"""P2b: long-term unemployment. Hypothesis (user's framing): headline
unemployment has fallen a lot since the crisis peak, but hardship may stay
"sticky" because a chunk of that unemployment never really left -- it's
long-term (12+ months), which erodes savings, skills, and eligibility for
support in a way a short unemployment spell doesn't. Tests whether LTU adds
anything headline unemployment (already the single strongest labor-market
predictor in Model C) doesn't already capture.

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
YEARS = range(2003, 2025)
EU = eu_members(2024)

# LTU = unemployed 12 months or more, as % of active population (labour force)
ltu = fetch("une_ltu_a", sex="T", age="Y15-74", unit="PC_ACT", indic_em="LTU", time=YEARS)
ltu = ltu[["geo", "time", "value"]].rename(columns={"value": "ltu_rate"})
ltu.to_csv(f"{RAW}/panel_long_term_unemployment.csv", index=False)

panel = ltu[ltu.geo.isin(EU)].copy()
print(f"Coverage: {panel.geo.nunique()} of {len(EU)} EU countries")
print(panel.groupby("geo").time.count().describe())

print("\n=== Greece: long-term unemployment rate (% of active population) ===")
gr = panel[panel.geo == "EL"].sort_values("time")
print(gr.round(1).to_string(index=False))
peak_row = gr.loc[gr["ltu_rate"].idxmax()]
last_row = gr[gr.time == gr.time.max()].iloc[0]
print(f"\nGreece LTU peak: {peak_row['ltu_rate']:.1f} in {int(peak_row['time'])}")
print(f"Greece LTU latest ({int(last_row['time'])}): {last_row['ltu_rate']:.1f}")

# cross-country comparison, latest common year
latest_year = panel.time.max()
comp = panel[panel.time == latest_year][["geo", "ltu_rate"]].sort_values("ltu_rate", ascending=False)
comp.to_csv(f"{OUT}/ltu_cross_country_latest.csv", index=False)
print(f"\n=== Long-term unemployment rate, {latest_year}, all 27 EU countries, highest first ===")
print(comp.round(1).to_string(index=False))

# Greece-only correlation with subjective poverty (matches Section 4 table format)
gr_ltu = gr[["time", "ltu_rate"]].rename(columns={"time": "year"})
subj = pd.read_csv(f"{OUT}/master_table.csv")[["year", "gr_subjective_poverty"]]
merged = gr_ltu.merge(subj, on="year").dropna()
print(f"\n=== Greece: LTU rate vs subjective poverty (n={len(merged)}) ===")
if len(merged) >= 5:
    r0, p0 = pearsonr(merged["ltu_rate"], merged["gr_subjective_poverty"])
    d1 = merged.diff().dropna()
    r1, p1 = pearsonr(d1["ltu_rate"], d1["gr_subjective_poverty"])
    print(f"Level correlation: r={r0:.3f}, p={p0:.4f}, n={len(merged)}")
    print(f"First-difference correlation: r={r1:.3f}, p={p1:.4f}, n={len(d1)}")

# multicollinearity check against existing Model C predictors, Greece-only
print("\n=== Multicollinearity check: LTU rate vs existing Model C predictors (Greece-only levels) ===")
ext = pd.read_csv(f"{OUT}/panel_extended.csv")
gr_ext = ext[ext.geo == "EL"][["time", "unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation",
                                "arop", "housing_cost_overburden", "arrears", "unexpected_expenses"]]
check = gr_ltu.rename(columns={"year": "time"}).merge(gr_ext, on="time").dropna()
for col in ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
            "housing_cost_overburden", "arrears", "unexpected_expenses"]:
    d = check[["ltu_rate", col]].dropna()
    if len(d) >= 5:
        r, p = pearsonr(d["ltu_rate"], d[col])
        print(f"  vs {col:28s} r={r:+.3f}  p={p:.4f}  n={len(d)}")

# model-feasibility test: does adding ltu_rate to Model C improve fit / reduce Greece's out-of-sample gap?
print("\n=== Model C feasibility test: does ltu_rate add independent explanatory power? ===")
panel_c = ext.merge(panel.rename(columns={"time": "time"}), on=["geo", "time"], how="inner")
vars_c = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
          "housing_cost_overburden", "arrears", "unexpected_expenses"]
vars_c_ltu = vars_c + ["ltu_rate"]


def fit_and_loo(vars_, label):
    d = panel_c.dropna(subset=vars_ + ["subjective_poverty"]).copy()
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
    print(f"  Greece LOO (out-of-sample) residual: {gr_row['avg_residual']:.2f}  rank {int(gr_row['rank'])}/{len(loo)}")
    if "ltu_rate" in vars_:
        coef = m.params.get("ltu_rate")
        pval = m.pvalues.get("ltu_rate")
        print(f"  ltu_rate coefficient: {coef:.3f}  p={pval:.4f}")
    return m, gr_row


m_base, gr_base = fit_and_loo(vars_c, "Model C (baseline)")
m_ltu, gr_ltu_row = fit_and_loo(vars_c_ltu, "Model C + ltu_rate")
