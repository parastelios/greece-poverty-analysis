"""Fetch core AROP + subjective poverty series: Greece, EU aggregate, and all countries for ranking."""
import pandas as pd
from eurostat import fetch

RAW = "../data/raw"

# ---- AROP (at-risk-of-poverty rate, 60% of national median equivalised income) ----
arop_all = fetch(
    "ilc_li02",
    sex="T", age="TOTAL", unit="PC", statinfo="MED_EI", rskpovth="B_60",
    time=range(2003, 2026),
)
arop_all = arop_all[["geo", "geo_label", "time", "value"]].rename(columns={"value": "arop"})
arop_all.to_csv(f"{RAW}/arop_all_countries.csv", index=False)
print("AROP all countries:", arop_all.shape)
print(arop_all[arop_all.geo == "EL"].sort_values("time").to_string(index=False))

# ---- Subjective poverty: "with difficulty" + "with great difficulty" making ends meet ----
sub_grt = fetch(
    "ilc_mdes09",
    lev_diff="GRT", hhcomp="TOTAL", rskpovth="TOTAL", unit="PC",
    time=range(2003, 2026),
)
sub_dif = fetch(
    "ilc_mdes09",
    lev_diff="DIF", hhcomp="TOTAL", rskpovth="TOTAL", unit="PC",
    time=range(2003, 2026),
)
sub_grt = sub_grt[["geo", "geo_label", "time", "value"]].rename(columns={"value": "great_difficulty"})
sub_dif = sub_dif[["geo", "time", "value"]].rename(columns={"value": "difficulty"})
sub_all = sub_grt.merge(sub_dif, on=["geo", "time"], how="outer")
sub_all["subjective_poverty"] = sub_all["great_difficulty"] + sub_all["difficulty"]
sub_all.to_csv(f"{RAW}/subjective_poverty_all_countries.csv", index=False)
print("\nSubjective poverty all countries:", sub_all.shape)
print(sub_all[sub_all.geo == "EL"].sort_values("time").to_string(index=False))
