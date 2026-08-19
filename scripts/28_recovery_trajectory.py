"""P1a: recovery trajectory analysis. Not just the current distance below
peak (already in Section 11) but the SHAPE of the story: how deep was each
country's worst crisis-era drawdown, how long did recovery from THAT
specific dip actually take, and how does Greece's "still not recovered"
compare to a real distribution of EU recovery times.

Two distinct questions, kept separate on purpose:
  (a) "Is the country below its own all-time peak, right now?" -- this is
      the already-published Section 11 metric (pct_below_peak_now), kept
      identical here as a consistency check.
  (b) "How long did it take to recover from its WORST historical drawdown?"
      -- uses max-drawdown detection (same method as the older, exploratory
      script 12), which correctly finds the crisis trough even for a
      country that's since climbed to a brand-new peak.
These can disagree: a country can have recovered from its worst crisis
years ago and still be marginally below a very recent, minor peak.

Checkpoint script: computes and prints/saves results only. Does not touch
the report. Findings get reported back before any integration decision.
"""
import pandas as pd
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
LAST_YEAR = 2024

gdp = pd.read_csv(f"{RAW}/panel_gdp_history_2008_2024.csv").sort_values(["geo", "time"])
gdp = gdp[gdp["geo"].isin(eu_members(LAST_YEAR))].copy()

rows = []
for geo, g in gdp.groupby("geo"):
    g = g.sort_values("time").reset_index(drop=True)

    # (a) current distance below the all-time (2008-2024) running peak --
    # identical method to Section 11's already-published pct_below_peak
    running_peak = g["real_gdp_pc"].cummax()
    alltime_peak_val = running_peak.iloc[-1]
    alltime_peak_year = int(g.loc[g["real_gdp_pc"] == g["real_gdp_pc"].cummax().max(), "time"].iloc[0])
    current_val = g[g["time"] == LAST_YEAR]["real_gdp_pc"].iloc[0]
    pct_below_peak_now = 100 * (alltime_peak_val - current_val) / alltime_peak_val
    not_recovered_to_alltime_peak = pct_below_peak_now > 0.05  # tiny float-noise tolerance

    # (b) worst historical drawdown (max-drawdown method) and recovery from it
    drawdown_pct = 100 * (running_peak - g["real_gdp_pc"]) / running_peak
    worst_idx = drawdown_pct.idxmax()
    worst_decline = drawdown_pct.loc[worst_idx]
    crisis_trough_year = int(g.loc[worst_idx, "time"])
    crisis_trough_val = g.loc[worst_idx, "real_gdp_pc"]
    crisis_peak_val = running_peak.loc[worst_idx]
    crisis_peak_year = int(g.loc[g["real_gdp_pc"] == crisis_peak_val, "time"].iloc[0])

    if worst_decline < 0.5:
        # no meaningful crisis dip anywhere in the window (monotonic growth)
        had_crisis = False
        recovered_from_crisis, recovery_year, years_to_recovery = None, None, None
    else:
        had_crisis = True
        post_trough = g[g["time"] > crisis_trough_year]
        recovered_rows = post_trough[post_trough["real_gdp_pc"] >= crisis_peak_val]
        if len(recovered_rows) > 0:
            recovered_from_crisis = True
            recovery_year = int(recovered_rows["time"].min())
            years_to_recovery = recovery_year - crisis_trough_year
        else:
            recovered_from_crisis = False
            recovery_year, years_to_recovery = None, None

    rows.append({
        "geo": geo,
        "alltime_peak_year": alltime_peak_year, "pct_below_peak_now": pct_below_peak_now,
        "not_recovered_to_alltime_peak": not_recovered_to_alltime_peak,
        "had_crisis_dip": had_crisis, "crisis_peak_year": crisis_peak_year if had_crisis else None,
        "crisis_trough_year": crisis_trough_year if had_crisis else None,
        "crisis_decline_pct": worst_decline if had_crisis else 0.0,
        "recovered_from_crisis": recovered_from_crisis,
        "crisis_recovery_year": recovery_year, "years_to_recovery_from_crisis": years_to_recovery,
    })

df = pd.DataFrame(rows).sort_values("pct_below_peak_now", ascending=False).reset_index(drop=True)
df.to_csv(f"{OUT}/recovery_trajectory.csv", index=False)

print("=== (a) Currently below own all-time (2008-2024) peak? ===")
print(df[["geo", "alltime_peak_year", "pct_below_peak_now", "not_recovered_to_alltime_peak"]].round(1).to_string(index=False))

print("\n=== (b) Worst crisis-era drawdown and recovery from it ===")
print(df[["geo", "crisis_peak_year", "crisis_trough_year", "crisis_decline_pct",
          "recovered_from_crisis", "crisis_recovery_year", "years_to_recovery_from_crisis"]].round(1).to_string(index=False))

recovered = df[df["recovered_from_crisis"] == True]
print(f"\n=== Years-to-recovery distribution, {len(recovered)} countries that had a real crisis dip and recovered from it ===")
print(recovered["years_to_recovery_from_crisis"].describe().round(1))
print(f"Median: {recovered['years_to_recovery_from_crisis'].median():.0f} years")

not_recovered_crisis = df[(df["had_crisis_dip"]) & (df["recovered_from_crisis"] == False)]
print(f"\n=== Never recovered from their worst crisis dip ({len(not_recovered_crisis)} of 27) ===")
print(not_recovered_crisis[["geo", "crisis_peak_year", "crisis_trough_year", "crisis_decline_pct"]].round(1).to_string(index=False))

print(f"\n=== Greece specifically ===")
print(df[df.geo == "EL"].T)

# indexed trajectory series (each country indexed to its own all-time peak = 100)
gdp2 = gdp.merge(df[["geo"]], on="geo")
peak_map = df.set_index("geo").apply(lambda r: None, axis=1)  # placeholder not needed
alltime_peaks = gdp.groupby("geo")["real_gdp_pc"].max().rename("alltime_peak_val")
gdp2 = gdp2.merge(alltime_peaks, on="geo")
gdp2["indexed_to_own_peak"] = 100 * gdp2["real_gdp_pc"] / gdp2["alltime_peak_val"]
gdp2[["geo", "time", "real_gdp_pc", "indexed_to_own_peak"]].to_csv(f"{OUT}/recovery_indexed_trajectories.csv", index=False)
print(f"\nSaved indexed trajectory series: recovery_indexed_trajectories.csv ({len(gdp2)} rows)")
