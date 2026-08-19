"""Lead/lag scan on FIRST DIFFERENCES rather than levels -- the level-based scan
in first-differences.py's companion reintroduces the trending-series problem
first-differencing was meant to solve (two smooth crisis/recovery series stay
correlated across small shifts just because they share a trend)."""
import pandas as pd
from scipy.stats import pearsonr

OUT = "../data/processed"
df = pd.read_csv(f"{OUT}/analysis_dataset.csv").sort_values("year").reset_index(drop=True)
anchor = pd.read_csv(f"{OUT}/anchored_poverty.csv")[["year", "anchored_poverty_rate"]]
df = df.merge(anchor, on="year", how="left")
target_diff = df["gr_subjective_poverty"].diff()

predictors = {
    "gr_arop": "AROP (relative)",
    "anchored_poverty_rate": "Anchored poverty (approx., 2008 base)",
    "gr_real_hh_income_idx2008": "Real household disposable income",
    "gr_unemployment_rate": "Unemployment rate",
    "gr_severe_mat_deprivation_legacy": "Severe material deprivation, legacy",
    "gr_housing_cost_overburden": "Housing cost overburden",
    "gr_arrears": "Households in arrears",
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
    col_diff = df[col].diff()
    row = {"variable": label}
    for lag in [-2, -1, 0, 1, 2]:
        shifted = col_diff.shift(-lag)
        r, p, n = corr_pair(shifted, target_diff)
        row[f"lag_{lag:+d}"] = round(r, 3) if r is not None else None
        row[f"n_{lag:+d}"] = n
    rows.append(row)

result = pd.DataFrame(rows)
result.to_csv(f"{OUT}/leadlag_firstdiff.csv", index=False)
pd.set_option("display.width", 200)
print("=== Lead/lag scan on FIRST DIFFERENCES (year-over-year change vs year-over-year change) ===")
print(result[["variable", "lag_-2", "lag_-1", "lag_+0", "lag_+1", "lag_+2"]].to_string(index=False))
print("\nn per lag (smallest n, most fragile):")
print(result[["variable", "n_-2", "n_-1", "n_+0", "n_+1", "n_+2"]].to_string(index=False))
