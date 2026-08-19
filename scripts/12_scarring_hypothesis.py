"""Test the 'scarring' hypothesis: does the DEPTH of each country's post-2008 real
income collapse (not its current level) predict the size of its unexplained
subjective-poverty residual?"""
import pandas as pd
from scipy.stats import pearsonr
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"

gdp_hist = fetch("sdg_08_10", unit="CLV20_EUR_HAB", na_item="B1GQ", time=range(2008, 2025))
gdp_hist = gdp_hist[["geo", "time", "value"]].rename(columns={"value": "real_gdp_pc"})
gdp_hist.to_csv(f"{RAW}/panel_gdp_history_2008_2024.csv", index=False)

# Maximum drawdown per country: the deepest peak-to-later-trough decline
# anywhere in the window (not just from the single highest peak), so a
# 2009-2013 crisis that's since been fully recovered still counts.
rows = []
for geo, g in gdp_hist.groupby("geo"):
    g = g.sort_values("time").reset_index(drop=True)
    running_peak = g["real_gdp_pc"].cummax()
    drawdown_pct = 100 * (running_peak - g["real_gdp_pc"]) / running_peak
    worst_idx = drawdown_pct.idxmax()
    worst_decline = drawdown_pct.loc[worst_idx]
    trough_year = g.loc[worst_idx, "time"]
    # the peak this trough fell from
    peak_val_at_worst = running_peak.loc[worst_idx]
    peak_year = g.loc[g["real_gdp_pc"] == peak_val_at_worst, "time"].iloc[0]
    rows.append({"geo": geo, "peak_year": peak_year, "peak_val": peak_val_at_worst,
                 "trough_year": trough_year, "trough_val": g.loc[worst_idx, "real_gdp_pc"],
                 "decline_pct": worst_decline})
decline = pd.DataFrame(rows)
decline.to_csv(f"{OUT}/peak_to_trough_decline.csv", index=False)

# bring in the residuals from both the baseline (M1) and extended (M4) panel models
panel_resid = pd.read_csv(f"{OUT}/panel_with_residuals.csv")  # M1 baseline, from script 08
avg_resid_m1 = panel_resid.groupby("geo")["residual"].mean().reset_index().rename(columns={"residual": "avg_residual_m1"})

merged = decline.merge(avg_resid_m1, on="geo", how="inner")
merged = merged[merged["geo"].isin(eu_members(2024))]
merged = merged.dropna(subset=["decline_pct", "avg_residual_m1"])

r, p = pearsonr(merged["decline_pct"], merged["avg_residual_m1"])
print(f"Correlation: depth of peak-to-trough real GDP/capita decline vs. avg M1 residual")
print(f"r = {r:.3f}, p = {p:.4f}, n = {len(merged)}\n")
print(merged.sort_values("decline_pct", ascending=False)[["geo", "peak_year", "trough_year", "decline_pct", "avg_residual_m1"]].round(1).to_string(index=False))

merged.to_csv(f"{OUT}/scarring_hypothesis_test.csv", index=False)
