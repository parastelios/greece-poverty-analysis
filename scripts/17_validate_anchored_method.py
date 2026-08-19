"""Validate the anchored-poverty method: replicate it anchored at 2019 (where
Eurostat publishes an official anchored series, ilc_li22) and check how well the
4-point lognormal approximation reproduces the real thing -- MAE, max error, bias,
correlation, and whether error grows with how far the anchor threshold sits
outside the observed 40-70% range that year (the extrapolation-distance check)."""
import numpy as np
import pandas as pd
from scipy.stats import norm, pearsonr
from eurostat import fetch

RAW = "../data/raw"
OUT = "../data/processed"

thresh = pd.read_csv(f"{RAW}/anchor_thresholds.csv").pivot(index="time", columns="rskpovth", values="threshold_eur")
rates = pd.read_csv(f"{RAW}/anchor_rates.csv").pivot(index="time", columns="rskpovth", values="rate_pct")
analysis = pd.read_csv(f"{OUT}/analysis_dataset.csv").set_index("year")

# official anchored-at-2019 series
official = fetch("ilc_li22", statinfo="MED_EI", rskpovth="B_60", sex="T", age="TOTAL", unit="PC", geo=["EL"])
official = official[["time", "value"]].rename(columns={"value": "official_anchor2019"}).set_index("time")

anchor_2019_nominal = thresh.loc[2019, "B_60"]  # 4917 EUR

rows = []
for year in thresh.index:
    if year not in official.index:
        continue
    x = np.log(thresh.loc[year, ["B_40", "B_50", "B_60", "B_70"]].astype(float).values)
    y = norm.ppf(rates.loc[year, ["B_40", "B_50", "B_60", "B_70"]].astype(float).values / 100.0)
    b, a = np.polyfit(x, y, 1)

    # rebase the HICP cumulative index to 2019=1.0 using the same headline HICP series
    cum_2008base = analysis.loc[year, "hicp_cum_index_2008base"]
    cum_2019base_at_2019 = analysis.loc[2019, "hicp_cum_index_2008base"]
    cum_2019base = cum_2008base / cum_2019base_at_2019  # re-reference so 2019 = 1.0

    anchored_nominal = anchor_2019_nominal * cum_2019base
    estimated_rate = 100 * norm.cdf(a + b * np.log(anchored_nominal))

    # extrapolation distance: how far outside the observed 40-70% threshold range
    # (in log-EUR) does the anchored threshold fall this year?
    obs_min, obs_max = x.min(), x.max()
    log_anchor = np.log(anchored_nominal)
    if log_anchor < obs_min:
        extrap_dist = obs_min - log_anchor
    elif log_anchor > obs_max:
        extrap_dist = log_anchor - obs_max
    else:
        extrap_dist = 0.0

    rows.append({
        "year": year,
        "estimated_anchor2019": round(estimated_rate, 1),
        "official_anchor2019": official.loc[year, "official_anchor2019"],
        "error": round(estimated_rate - official.loc[year, "official_anchor2019"], 2),
        "extrapolation_distance": round(extrap_dist, 4),
    })

val = pd.DataFrame(rows)
val["abs_error"] = val["error"].abs()
val.to_csv(f"{OUT}/anchored_validation_2019.csv", index=False)

print(val.to_string(index=False))
print(f"\nMean absolute error: {val.abs_error.mean():.2f} pp")
print(f"Max absolute error:  {val.abs_error.max():.2f} pp")
print(f"Bias (mean signed error): {val.error.mean():+.2f} pp")
r, p = pearsonr(val.estimated_anchor2019, val.official_anchor2019)
print(f"Correlation: r={r:.3f}, p={p:.4f}, n={len(val)}")

r2, p2 = pearsonr(val.extrapolation_distance, val.abs_error)
print(f"\nDoes absolute error grow with extrapolation distance? r={r2:.3f}, p={p2:.4f}")
print("(extrapolation_distance = 0 means the anchor threshold fell inside the observed 40-70% range that year)")
