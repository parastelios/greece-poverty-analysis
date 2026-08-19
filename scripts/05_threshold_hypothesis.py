"""Test the 'moving relative threshold' hypothesis: did the AROP line itself fall
in real terms during the crisis, masking a broader decline in living standards?"""
import numpy as np
import pandas as pd
from eurostat import fetch

RAW = "../data/raw"
OUT = "../data/processed"

# Nominal at-risk-of-poverty threshold, single-adult household, 60% of median, EUR
thresh = fetch(
    "ilc_li01",
    statinfo="MED_EI", rskpovth="B_60", hhcomp="A1", unit="EUR",
    geo=["EL"], time=range(2003, 2026),
)
thresh = thresh[["time", "value"]].rename(columns={"value": "gr_arop_threshold_nominal_eur"})
thresh.to_csv(f"{RAW}/arop_threshold_nominal.csv", index=False)

df = pd.read_csv(f"{OUT}/analysis_dataset.csv")
df = df.merge(thresh, left_on="year", right_on="time", how="left").drop(columns=["time"])

# Deflate the nominal threshold to 2008 real euros using cumulative Greek HICP
df = df.sort_values("year").reset_index(drop=True)
df["hicp_cum_index"] = np.nan
base_idx = df.index[df["year"] == 2008][0]
cum = 1.0
cum_vals = [None] * len(df)
cum_vals[base_idx] = 1.0
# walk forward from 2008
c = 1.0
for i in range(base_idx + 1, len(df)):
    rate = df.loc[i, "gr_hicp_headline_rate"]
    c = c * (1 + rate / 100.0) if pd.notna(rate) else c
    cum_vals[i] = c
# walk backward from 2008
c = 1.0
for i in range(base_idx - 1, -1, -1):
    rate = df.loc[i + 1, "gr_hicp_headline_rate"]  # rate that took year i -> i+1
    c = c / (1 + rate / 100.0) if pd.notna(rate) else c
    cum_vals[i] = c
df["hicp_cum_index_2008base"] = cum_vals

df["gr_arop_threshold_real_2008eur"] = df["gr_arop_threshold_nominal_eur"] / df["hicp_cum_index_2008base"]
df["gr_arop_threshold_real_idx2008"] = 100 * df["gr_arop_threshold_real_2008eur"] / (
    df.loc[base_idx, "gr_arop_threshold_nominal_eur"]
)

df.to_csv(f"{OUT}/analysis_dataset.csv", index=False)

print(df[["year", "gr_arop", "gr_arop_threshold_nominal_eur", "gr_arop_threshold_real_idx2008",
          "gr_real_hh_income_idx2008", "gr_subjective_poverty"]].to_string(index=False))

trough = df.loc[df["gr_arop_threshold_real_idx2008"].idxmin()]
print(f"\nReal AROP threshold trough: {trough['year']:.0f} at index {trough['gr_arop_threshold_real_idx2008']:.1f} "
      f"(2008=100) -- i.e. the poverty LINE ITSELF fell "
      f"{100 - trough['gr_arop_threshold_real_idx2008']:.1f} index points in real terms.")
print(f"Over the same span, AROP the RATE moved from {df[df.year==2008]['gr_arop'].iloc[0]} "
      f"(2008) to {df[df.year==int(trough['year'])]['gr_arop'].iloc[0]} ({int(trough['year'])}) -- "
      f"barely changed, because the yardstick shrank along with incomes.")
