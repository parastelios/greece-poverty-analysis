"""Build the cross-country snapshot (latest year) comparing AROP and subjective
poverty across all EU member states plus the EU aggregate -- the AROP-based
counterpart to 22_arope_snapshot.py, used as the primary headline comparison
(AROPE is used as a secondary, motivating diagnostic, not the primary gap)."""
import pandas as pd
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
YEAR = 2025

sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")
arop = pd.read_csv(f"{RAW}/arop_all_countries.csv")

sub_y = sub[sub.time == YEAR][["geo", "geo_label", "subjective_poverty"]]
arop_y = arop[arop.time == YEAR][["geo", "arop"]]

merged = sub_y.merge(arop_y, on="geo", how="inner").dropna()

members = set(eu_members(YEAR))
eu_country_rows = merged[merged.geo.isin(members)].copy()
eu_agg_row = merged[merged.geo == "EU27_2020"].copy()

eu_country_rows["gap"] = eu_country_rows["subjective_poverty"] - eu_country_rows["arop"]
eu_country_rows = eu_country_rows.sort_values("subjective_poverty", ascending=False)

out = pd.concat([eu_country_rows, eu_agg_row.assign(gap=eu_agg_row["subjective_poverty"] - eu_agg_row["arop"])])
out.to_csv(f"{OUT}/arop_subjective_snapshot_{YEAR}.csv", index=False)
pd.set_option("display.width", 160)
print(f"Snapshot year {YEAR}, {len(eu_country_rows)} EU countries + EU aggregate:")
print(out.to_string(index=False))
