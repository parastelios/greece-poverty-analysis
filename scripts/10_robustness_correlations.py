"""Robustness check: do the level correlations survive first-differencing and
linear detrending? Two trending series can produce spuriously huge Pearson r's
even with a weak short-run relationship -- this tests whether the year-to-year
CHANGES (not just the shared trend) move together.

Also applies Benjamini-Hochberg FDR correction directly here, within each of
the three displayed families (level, first-difference, detrended) separately,
computed from full-precision p-values before any rounding -- this is the
correction that governs the live Section 4 table's significance flags. It is
distinct from the older 21-variable contemporaneous+lag1 screen corrected by
27_multiple_testing.py, which predates this table and is not what the report
displays; that screen is retained as a separate, earlier exploratory pass and
should not be described as governing this table."""
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from statsmodels.stats.multitest import multipletests

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
    "gr_panel_youth_unemployment": "Youth unemployment rate (15-24)",
    "gr_panel_s80s20": "Income inequality, S80/S20 ratio",
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
        print(f"WARNING: predictor column '{col}' ({label}) not found in analysis_dataset.csv -- skipped")
        continue
    # level correlation (as originally reported)
    r_level, p_level, n_level = corr_pair(df[col], df[target])
    # first-difference (year-over-year change) correlation
    col_diff = df[col].diff()
    r_diff, p_diff, n_diff = corr_pair(col_diff, target_diff)
    # detrended correlation
    col_detrend = detrend(df[col], df["year"])
    r_det, p_det, n_det = corr_pair(col_detrend, target_detrend)
    # full precision kept here -- rounding happens only after FDR correction below
    rows.append({
        "variable": label, "r_level": r_level, "p_level": p_level,
        "r_firstdiff": r_diff, "p_firstdiff": p_diff, "n_firstdiff": n_diff,
        "r_detrended": r_det, "p_detrended": p_det, "n_detrended": n_det,
    })

result = pd.DataFrame(rows)
n_vars = len(result)
print(f"{n_vars} of {len(predictors)} declared predictors found and tested "
      f"(any warnings above indicate a stale predictors dict vs. analysis_dataset.csv).")

# BH-FDR within each displayed family separately, from full-precision p-values,
# before any rounding for display. The level family is included even though the
# live table doesn't show significance stars on r_level, for completeness and to
# support the Methods write-up.
for col, fdr_col, surv_col in [
    ("p_level", "p_level_fdr", "survives_fdr_level"),
    ("p_firstdiff", "p_firstdiff_fdr", "survives_fdr_firstdiff"),
    ("p_detrended", "p_detrended_fdr", "survives_fdr_detrended"),
]:
    mask = result[col].notna()
    result[fdr_col] = np.nan
    result[surv_col] = False
    if mask.any():
        rej, padj, _, _ = multipletests(result.loc[mask, col], alpha=0.05, method="fdr_bh")
        result.loc[mask, fdr_col] = padj
        result.loc[mask, surv_col] = rej

result = result.sort_values("r_level", key=lambda s: s.abs(), ascending=False)

# round only now, for display and export -- FDR above already used full precision
display_cols = ["r_level", "p_level", "p_level_fdr", "r_firstdiff", "p_firstdiff", "p_firstdiff_fdr",
                 "r_detrended", "p_detrended", "p_detrended_fdr"]
for c in display_cols:
    result[c] = result[c].round(4)

result.to_csv(f"{OUT}/correlations_robustness.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 20)
print(result.to_string(index=False))
print(f"\nFDR survivors -- level: {int(result.survives_fdr_level.sum())}/{n_vars}, "
      f"first-difference: {int(result.survives_fdr_firstdiff.sum())}/{n_vars}, "
      f"detrended: {int(result.survives_fdr_detrended.sum())}/{n_vars}")
