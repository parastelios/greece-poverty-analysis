"""Build the AROPE (at-risk-of-poverty-or-social-exclusion) series: Greece, EU
aggregate, EU ranking, and correlation with subjective poverty. AROPE is the
union of AROP, severe material & social deprivation, and very-low-work-intensity
households -- a broader Eurostat headline indicator, distinct from plain AROP.
Same legacy/new methodology break as the material deprivation series (2020/2021
boundary), handled the same way: two series, spliced at the point where legacy
data simply stops and new data starts, not blended."""
import pandas as pd
from scipy.stats import pearsonr
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
EU_AGG_PRIORITY = ["EU27_2020", "EU27_2007", "EU28", "EU"]

legacy = pd.read_csv(f"{RAW}/arope_legacy_all_countries.csv")
new = pd.read_csv(f"{RAW}/arope_new_all_countries.csv")

# combined primary series per country: legacy through 2020, new from 2021
legacy_pre = legacy[legacy.time <= 2020][["geo", "time", "arope_legacy"]].rename(columns={"arope_legacy": "arope"})
new_post = new[new.time >= 2021][["geo", "time", "arope_new"]].rename(columns={"arope_new": "arope"})
combined = pd.concat([legacy_pre, new_post], ignore_index=True)
combined.to_csv(f"{RAW}/arope_combined_all_countries.csv", index=False)

# Greece series
gr = combined[combined.geo == "EL"][["time", "arope"]].rename(columns={"arope": "gr_arope"})

# EU aggregate with fallback priority, per year
eu_rows = []
for year in sorted(combined["time"].unique()):
    year_df = combined[combined["time"] == year]
    chosen = None
    for code in EU_AGG_PRIORITY:
        m = year_df[year_df["geo"] == code]
        if len(m) and pd.notna(m.iloc[0]["arope"]):
            chosen = (m.iloc[0]["arope"], code)
            break
    eu_rows.append({"time": year, "eu_arope": chosen[0] if chosen else None,
                     "eu_arope_source": chosen[1] if chosen else None})
eu_df = pd.DataFrame(eu_rows)

# EU ranking (1 = highest AROPE) among EU member states, using each year's membership
rank_rows = []
for year in sorted(combined["time"].unique()):
    members = set(eu_members(int(year)))
    year_df = combined[(combined.time == year) & combined.geo.isin(members) & combined.arope.notna()]
    if not len(year_df):
        rank_rows.append({"time": year, "gr_arope_rank": None, "n_countries_arope": 0})
        continue
    ranked = year_df.sort_values("arope", ascending=False).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1
    gr_row = ranked[ranked.geo == "EL"]
    rank_rows.append({
        "time": year,
        "gr_arope_rank": int(gr_row["rank"].iloc[0]) if len(gr_row) else None,
        "n_countries_arope": len(ranked),
    })
rank_df = pd.DataFrame(rank_rows)

master = gr.merge(eu_df, on="time").merge(rank_df, on="time")
master["gr_eu_arope_gap"] = master["gr_arope"] - master["eu_arope"]
master.to_csv(f"{OUT}/arope_master.csv", index=False)
pd.set_option("display.width", 160)
print(master.to_string(index=False))

# merge into analysis_dataset.csv
analysis = pd.read_csv(f"{OUT}/analysis_dataset.csv")
analysis = analysis.merge(master.rename(columns={"time": "year"}), on="year", how="left")
analysis.to_csv(f"{OUT}/analysis_dataset.csv", index=False)

# correlations with subjective poverty: level, first-diff, detrended
import numpy as np
df = analysis.sort_values("year").reset_index(drop=True)


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


target = df["gr_subjective_poverty"]
target_diff = target.diff()
target_detrend = detrend(target, df["year"])

x = df["gr_arope"]
x_diff = x.diff()
x_detrend = detrend(x, df["year"])


def r(a, b):
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    if len(d) < 4:
        return None, None
    return pearsonr(d["a"], d["b"])


r_level, p_level = r(x, target)
r_diff, p_diff = r(x_diff, target_diff)
r_det, p_det = r(x_detrend, target_detrend)
print(f"\nAROPE vs subjective poverty:")
print(f"  level:      r={r_level:.3f}, p={p_level:.4f}")
print(f"  first-diff: r={r_diff:.3f}, p={p_diff:.4f}")
print(f"  detrended:  r={r_det:.3f}, p={p_det:.4f}")

with open(f"{OUT}/arope_correlation.txt", "w") as f:
    f.write(f"level r={r_level:.3f} p={p_level:.4f}\n")
    f.write(f"firstdiff r={r_diff:.3f} p={p_diff:.4f}\n")
    f.write(f"detrended r={r_det:.3f} p={p_det:.4f}\n")
