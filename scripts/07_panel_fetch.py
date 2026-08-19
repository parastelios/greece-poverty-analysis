"""Fetch all-country panels for cross-country regression (2015-2024, where severe
material & social deprivation new series has its best coverage)."""
import pandas as pd
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
YEARS = range(2015, 2025)

une = fetch("une_rt_a", age="Y15-74", sex="T", unit="PC_ACT", time=YEARS)
une = une[["geo", "time", "value"]].rename(columns={"value": "unemployment_rate"})
une.to_csv(f"{RAW}/panel_unemployment.csv", index=False)

gdp = fetch("sdg_08_10", unit="CLV20_EUR_HAB", na_item="B1GQ", time=YEARS)
gdp = gdp[["geo", "time", "value"]].rename(columns={"value": "real_gdp_pc"})
gdp.to_csv(f"{RAW}/panel_gdp.csv", index=False)

msd = fetch("ilc_mdsd11", age="TOTAL", sex="T", unit="PC", time=YEARS)
msd = msd[["geo", "time", "value"]].rename(columns={"value": "severe_mat_soc_deprivation"})
msd.to_csv(f"{RAW}/panel_deprivation.csv", index=False)

arop = pd.read_csv(f"{RAW}/arop_all_countries.csv")[["geo", "time", "arop"]]
sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")[["geo", "time", "subjective_poverty"]]

panel = sub.merge(arop, on=["geo", "time"], how="inner")
panel = panel.merge(une, on=["geo", "time"], how="left")
panel = panel.merge(gdp, on=["geo", "time"], how="left")
panel = panel.merge(msd, on=["geo", "time"], how="left")

# restrict to actual EU member states, per-year membership, and to the panel years
panel = panel[panel["time"].isin(YEARS)]
panel = panel[panel.apply(lambda r: r["geo"] in eu_members(int(r["time"])), axis=1)]

panel.to_csv(f"{RAW}/../processed/panel_dataset.csv", index=False)
print(f"Panel: {panel.shape[0]} country-year obs, {panel.geo.nunique()} countries, years {panel.time.min()}-{panel.time.max()}")
print(panel.isna().sum())
