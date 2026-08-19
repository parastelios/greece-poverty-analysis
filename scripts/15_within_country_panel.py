"""EU-wide two-way fixed-effects panel: does WITHIN-country variation in economic
conditions predict WITHIN-country variation in subjective poverty, across Europe
generally? This is a different question from the between-country outlier model --
country fixed effects absorb each country's persistent baseline (including
Greece's), so this cannot detect a Greek level effect. What it tests is whether
subjective poverty responds to genuine economic change as a general EU-wide
phenomenon, not just a Greek one."""
import pandas as pd
import statsmodels.formula.api as smf

OUT = "../data/processed"
panel = pd.read_csv(f"{OUT}/panel_extended.csv")

d = panel.dropna(subset=["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"])
print(f"Two-way FE panel sample: {len(d)} obs, {d.geo.nunique()} countries, {d.time.nunique()} years")

# Two-way FE via dummies (country + year), cluster-robust SEs by country
model_fe = smf.ols(
    "subjective_poverty ~ unemployment_rate + aic_pps_pc_k + severe_mat_soc_deprivation + arop + C(geo) + C(time)",
    data=d,
).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})

# print only the economic coefficients (country/year dummies omitted from display)
econ_vars = ["Intercept", "unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop"]
print("\n=== Two-way FE (country + year) -- economic coefficients only ===")
print(model_fe.params[econ_vars].round(3).to_string())
print(model_fe.pvalues[econ_vars].round(4).rename("p-value").to_string())
print(f"R2 (within, approx via overall R2 with FE absorbed): {model_fe.rsquared:.3f}")

# Compare directly against the pooled (between-country, no country FE) coefficients
model_pooled = smf.ols(
    "subjective_poverty ~ unemployment_rate + aic_pps_pc_k + severe_mat_soc_deprivation + arop + C(time)",
    data=d,
).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
print("\n=== Pooled (between-country, year FE only) -- for comparison ===")
print(model_pooled.params[econ_vars].round(3).to_string())
print(model_pooled.pvalues[econ_vars].round(4).rename("p-value").to_string())

comparison = pd.DataFrame({
    "pooled_between (no country FE)": model_pooled.params[econ_vars],
    "two_way_FE (within-country)": model_fe.params[econ_vars],
}).round(3)
comparison.to_csv(f"{OUT}/within_vs_between_comparison.csv")
print("\n=== Side-by-side ===")
print(comparison.to_string())
