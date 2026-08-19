"""Robustness check: do the level correlations survive first-differencing and
linear detrending? Two trending series can produce spuriously huge Pearson r's
even with a weak short-run relationship -- this tests whether the year-to-year
CHANGES (not just the shared trend) move together."""
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

OUT = "../data/processed"
df = pd.read_csv(f"{OUT}/analysis_dataset.csv").sort_values("year").reset_index(drop=True)
target = "gr_subjective_poverty"

predictors = {
    "gr_arop": "AROP",
    "gr_arope": "AROPE (poverty or social exclusion)",
    "gr_real_hh_income_idx2008": "Real household disposable income",
    "gr_real_gdp_pc": "Real GDP per capita",
    "gr_consumption_pc": "Real household consumption per capita",
    "gr_unemployment_rate": "Unemployment rate",
    "gr_employment_rate_20_64": "Employment rate 20-64",
    "gr_severe_mat_deprivation_legacy": "Severe material deprivation, legacy",
    "gr_severe_mat_soc_deprivation_new": "Severe material & social deprivation, new",
    "gr_unexpected_expenses_inability": "Cannot face unexpected expense",
    "gr_housing_cost_overburden": "Housing cost overburden",
    "gr_arrears": "Households in arrears",
    "gr_cannot_keep_home_warm": "Cannot keep home adequately warm",
    "gr_hicp_headline_rate": "HICP inflation, headline",
    "gr_arop_threshold_real_idx2008": "AROP threshold, real terms",
    "gr_real_wage_idx2008": "Real wages, compensation per employee",
    "gr_panel_long_term_unemployment": "Long-term unemployment rate (12mo+)",
}


def corr_pair(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 4:
        return None, None, len(d)
    r, p = pearsonr(d["x"], d["y"])
    return r, p, len(d)


def detrend(series, years):
    d = pd.DataFrame({"y": series, "t": years}).dropna()
    if len(d) < 4:
        return pd.Series([np.nan] * len(series), index=series.index)
    coeffs = np.polyfit(d["t"], d["y"], 1)
    fitted = np.polyval(coeffs, d["t"])
    resid = d["y"] - fitted
    out = pd.Series([np.nan] * len(series), index=series.index)
    out.loc[d.index] = resid
    return out


rows = []
target_diff = df[target].diff()
target_detrend = detrend(df[target], df["year"])

for col, label in predictors.items():
    if col not in df.columns:
        continue
    # level correlation (as originally reported)
    r_level, p_level, n_level = corr_pair(df[col], df[target])
    # first-difference (year-over-year change) correlation
    col_diff = df[col].diff()
    r_diff, p_diff, n_diff = corr_pair(col_diff, target_diff)
    # detrended correlation
    col_detrend = detrend(df[col], df["year"])
    r_det, p_det, n_det = corr_pair(col_detrend, target_detrend)
    rows.append({
        "variable": label,
        "r_level": round(r_level, 3) if r_level is not None else None,
        "r_firstdiff": round(r_diff, 3) if r_diff is not None else None,
        "p_firstdiff": round(p_diff, 4) if p_diff is not None else None,
        "n_firstdiff": n_diff,
        "r_detrended": round(r_det, 3) if r_det is not None else None,
        "p_detrended": round(p_det, 4) if p_det is not None else None,
    })

result = pd.DataFrame(rows).sort_values("r_level", key=lambda s: s.abs(), ascending=False)
result.to_csv(f"{OUT}/correlations_robustness.csv", index=False)
pd.set_option("display.width", 200)
print(result.to_string(index=False))
