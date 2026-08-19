"""Cross-country panel regression: is Greece's subjective poverty higher than its
objective economic conditions would predict, relative to other EU countries?"""
import pandas as pd
import statsmodels.formula.api as smf

OUT = "../data/processed"
panel = pd.read_csv(f"{OUT}/panel_dataset.csv").dropna()
panel["real_gdp_pc_k"] = panel["real_gdp_pc"] / 1000.0  # per 1,000 EUR, for readable coefficients

# Pooled OLS with year fixed effects: does Greece deviate from what unemployment,
# real GDP/capita, material deprivation and AROP predict for subjective poverty
# across the whole EU panel?
model = smf.ols(
    "subjective_poverty ~ unemployment_rate + real_gdp_pc_k + severe_mat_soc_deprivation + arop + C(time)",
    data=panel,
).fit(cov_type="cluster", cov_kwds={"groups": panel["geo"]})

print(model.summary())

panel["predicted"] = model.predict(panel)
panel["residual"] = panel["subjective_poverty"] - panel["predicted"]

# Rank every country-year's residual (largest positive = "more subjectively poor than
# objective conditions predict")
panel["residual_rank"] = panel.groupby("time")["residual"].rank(ascending=False)

gr = panel[panel.geo == "EL"].sort_values("time")
print("\n=== Greece: actual vs. model-predicted subjective poverty ===")
print(gr[["time", "subjective_poverty", "predicted", "residual", "residual_rank"]].to_string(index=False))

n_countries_per_year = panel.groupby("time")["geo"].count()
print(f"\nCountries per year in panel: {n_countries_per_year.to_dict()}")

avg_resid_by_country = panel.groupby("geo")["residual"].mean().sort_values(ascending=False)
print("\n=== Average residual by country (2015-2024), most positive = biggest positive outlier ===")
print(avg_resid_by_country.round(2).to_string())

panel.to_csv(f"{OUT}/panel_with_residuals.csv", index=False)

with open(f"{OUT}/../../docs/panel_regression_summary.txt", "w") as f:
    f.write(str(model.summary()))
    f.write("\n\n=== Greece actual vs predicted ===\n")
    f.write(gr[["time", "subjective_poverty", "predicted", "residual", "residual_rank"]].to_string(index=False))
    f.write("\n\n=== Average residual by country ===\n")
    f.write(avg_resid_by_country.round(2).to_string())
