"""Correlation analysis: subjective poverty vs. objective economic indicators."""
import pandas as pd
from scipy.stats import pearsonr

OUT = "../data/processed"
df = pd.read_csv(f"{OUT}/analysis_dataset.csv").sort_values("year").reset_index(drop=True)

target = "gr_subjective_poverty"

# sign convention note: for indicators where higher = better (income, GDP, employment,
# consumption), we expect a NEGATIVE correlation with subjective poverty; for
# indicators where higher = worse (AROP, unemployment, deprivation, inflation,
# arrears), we expect POSITIVE.
predictors = {
    "gr_arop": "AROP (objective, relative)",
    "gr_real_hh_income_idx2008": "Real household disposable income (idx 2008=100)",
    "gr_real_gdp_pc": "Real GDP per capita (EUR)",
    "gr_consumption_pc": "Real household consumption per capita (EUR)",
    "gr_unemployment_rate": "Unemployment rate (%)",
    "gr_employment_rate_20_64": "Employment rate 20-64 (%)",
    "gr_severe_mat_deprivation_legacy": "Severe material deprivation, legacy 9-item (%)",
    "gr_severe_mat_soc_deprivation_new": "Severe material & social deprivation, new 13-item (%)",
    "gr_unexpected_expenses_inability": "Cannot face unexpected expense (%)",
    "gr_housing_cost_overburden": "Housing cost overburden (%)",
    "gr_arrears": "Households in arrears (%)",
    "gr_cannot_keep_home_warm": "Cannot keep home adequately warm (%)",
    "gr_hicp_headline_rate": "HICP inflation, headline (%)",
    "gr_hicp_food_rate": "HICP inflation, food (%)",
    "gr_hicp_housing_energy_rate": "HICP inflation, housing & energy (%)",
    "gr_arop_threshold_real_idx2008": "AROP threshold, real terms (idx 2008=100)",
    "gr_minimum_wage_eur_month": "Minimum wage (nominal EUR/month)",
}


def corr_pair(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 4:
        return None, None, len(d)
    r, p = pearsonr(d["x"], d["y"])
    return r, p, len(d)


rows = []
for col, label in predictors.items():
    if col not in df.columns:
        continue
    r0, p0, n0 = corr_pair(df[col], df[target])
    # 1-year lag: predictor at year t-1 vs subjective poverty at year t
    lagged = df[col].shift(1)
    r1, p1, n1 = corr_pair(lagged, df[target])
    rows.append({
        "variable": label, "column": col,
        "r_contemporaneous": round(r0, 3) if r0 is not None else None,
        "p_contemporaneous": round(p0, 4) if p0 is not None else None,
        "n_contemporaneous": n0,
        "r_lag1": round(r1, 3) if r1 is not None else None,
        "p_lag1": round(p1, 4) if p1 is not None else None,
        "n_lag1": n1,
    })

result = pd.DataFrame(rows).sort_values("r_contemporaneous", key=lambda s: s.abs(), ascending=False)
result.to_csv(f"{OUT}/correlations.csv", index=False)
pd.set_option("display.width", 200)
print(result.to_string(index=False))
