"""Extend robustness checks: Spearman rank correlations (level + first-diff) and
a systematic lead/lag scan (-2..+2 years) for each predictor against Greek
subjective poverty."""
import pandas as pd
from scipy.stats import pearsonr, spearmanr

OUT = "../data/processed"
df = pd.read_csv(f"{OUT}/analysis_dataset.csv").sort_values("year").reset_index(drop=True)
anchor = pd.read_csv(f"{OUT}/anchored_poverty.csv")[["year", "anchored_poverty_rate"]]
df = df.merge(anchor, on="year", how="left")
target = "gr_subjective_poverty"

predictors = {
    "gr_arop": "AROP (relative)",
    "anchored_poverty_rate": "Anchored poverty (approx., 2008 base)",
    "gr_real_hh_income_idx2008": "Real household disposable income",
    "gr_real_gdp_pc": "Real GDP per capita",
    "gr_unemployment_rate": "Unemployment rate",
    "gr_severe_mat_deprivation_legacy": "Severe material deprivation, legacy",
    "gr_housing_cost_overburden": "Housing cost overburden",
    "gr_arrears": "Households in arrears",
}


def corr_pair(x, y, method):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 4:
        return None, None, len(d)
    f = pearsonr if method == "pearson" else spearmanr
    r, p = f(d["x"], d["y"])
    return r, p, len(d)


# Spearman: level and first-difference
rows = []
for col, label in predictors.items():
    if col not in df.columns:
        continue
    rp_level, pp_level, n = corr_pair(df[col], df[target], "pearson")
    rs_level, ps_level, _ = corr_pair(df[col], df[target], "spearman")
    d_col, d_tgt = df[col].diff(), df[target].diff()
    rp_diff, pp_diff, nd = corr_pair(d_col, d_tgt, "pearson")
    rs_diff, ps_diff, _ = corr_pair(d_col, d_tgt, "spearman")
    rows.append({
        "variable": label,
        "pearson_level": round(rp_level, 3) if rp_level is not None else None,
        "spearman_level": round(rs_level, 3) if rs_level is not None else None,
        "pearson_diff": round(rp_diff, 3) if rp_diff is not None else None,
        "spearman_diff": round(rs_diff, 3) if rs_diff is not None else None,
        "n_level": n, "n_diff": nd,
    })
spearman_result = pd.DataFrame(rows)
spearman_result.to_csv(f"{OUT}/correlations_spearman.csv", index=False)
print("=== Pearson vs Spearman, level and first-difference ===")
pd.set_option("display.width", 200)
print(spearman_result.to_string(index=False))

# Lead/lag scan: predictor at year (t + lag) vs subjective poverty at year t
# lag = -2,-1,0,+1,+2 -- negative lag means predictor LEADS (earlier year)
lag_rows = []
for col, label in predictors.items():
    if col not in df.columns:
        continue
    row = {"variable": label}
    for lag in [-2, -1, 0, 1, 2]:
        shifted = df[col].shift(-lag)  # shift(-lag): lag=-1 means predictor from t+1 (leads target by looking ahead)... see note
        r, p, n = corr_pair(shifted, df[target], "pearson")
        row[f"lag_{lag:+d}"] = round(r, 3) if r is not None else None
    lag_rows.append(row)
lag_result = pd.DataFrame(lag_rows)
lag_result.to_csv(f"{OUT}/correlations_leadlag.csv", index=False)
print("\n=== Lead/lag scan (Pearson r): column lag_-1 = predictor value from PRIOR year vs current subjective poverty; lag_+1 = predictor from FOLLOWING year ===")
print(lag_result.to_string(index=False))
