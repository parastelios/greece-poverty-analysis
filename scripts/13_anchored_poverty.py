"""Approximate an 'anchored' real-income poverty rate: fixed at the 2008 60%-of-
median threshold, uprated only for inflation thereafter (not for median income
growth) -- the classic anchored-poverty construction, contrasted with AROP's
purely relative (moving-threshold) definition.

Eurostat doesn't publish this anchored at 2008 for Greece (their own ilc_li22 is
anchored at 2019, which misses the crisis). We approximate it: each year, fit a
2-parameter lognormal to the income distribution using the four published
(threshold, poverty-rate) points at 40/50/60/70% of that year's median, then
evaluate that fitted distribution at the inflation-adjusted 2008 threshold.
This is an approximation, not an official Eurostat statistic -- flagged as such
throughout the report.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

RAW = "../data/raw"
OUT = "../data/processed"

thresh = pd.read_csv(f"{RAW}/anchor_thresholds.csv").pivot(index="time", columns="rskpovth", values="threshold_eur")
rates = pd.read_csv(f"{RAW}/anchor_rates.csv").pivot(index="time", columns="rskpovth", values="rate_pct")

analysis = pd.read_csv(f"{OUT}/analysis_dataset.csv").set_index("year")
anchor_2008_nominal = thresh.loc[2008, "B_60"]  # 6480 EUR, single-adult, 60% of 2008 median

rows = []
for year in thresh.index:
    x = np.log(thresh.loc[year, ["B_40", "B_50", "B_60", "B_70"]].astype(float).values)
    y = norm.ppf(rates.loc[year, ["B_40", "B_50", "B_60", "B_70"]].astype(float).values / 100.0)
    # y = a + b*x  =>  F(x) = Phi(a + b*ln(x))
    b, a = np.polyfit(x, y, 1)
    fit_r2 = np.corrcoef(x, y)[0, 1] ** 2

    cum_hicp = analysis.loc[year, "hicp_cum_index_2008base"] if year in analysis.index else np.nan
    anchored_nominal = anchor_2008_nominal * cum_hicp if pd.notna(cum_hicp) else np.nan
    anchored_rate = 100 * norm.cdf(a + b * np.log(anchored_nominal)) if pd.notna(anchored_nominal) else np.nan

    rows.append({
        "year": year, "fit_r2": round(fit_r2, 4), "anchored_threshold_nominal_eur": round(anchored_nominal, 0) if pd.notna(anchored_nominal) else None,
        "anchored_poverty_rate": round(anchored_rate, 1) if pd.notna(anchored_rate) else None,
        "actual_arop_rate": rates.loc[year, "B_60"],
    })

result = pd.DataFrame(rows)
result.to_csv(f"{OUT}/anchored_poverty.csv", index=False)
pd.set_option("display.width", 160)
print(result.to_string(index=False))
print(f"\nAnchor: 2008 threshold = {anchor_2008_nominal} EUR (60% of 2008 median, single-adult household)")
print(f"Fit quality (R^2 of the 4-point lognormal probit fit): min={result.fit_r2.min()}, mean={result.fit_r2.mean():.4f}")
