"""Fetch supplementary economic variables for Greece and the EU aggregate."""
import pandas as pd
from eurostat import fetch

RAW = "../data/raw"
OUT = "../data/processed"
YEARS = range(2000, 2026)
GEOS = ["EL", "EU27_2020", "EU27_2007", "EU28", "EU", "EA19", "EA20"]


def save(df, name, value_col):
    if df.empty:
        print(f"[WARN] {name} empty")
        return None
    df = df[["geo", "time", "value"]].rename(columns={"value": value_col})
    df.to_csv(f"{RAW}/{name}.csv", index=False)
    gr = df[df.geo == "EL"].sort_values("time")
    print(f"{name}: {len(df)} rows | GR {gr.time.min()}-{gr.time.max()} n={len(gr)}")
    return df


specs = {
    "real_gdp_pc": dict(dataset="sdg_08_10", unit="CLV20_EUR_HAB", na_item="B1GQ"),
    "real_hh_income_idx2008": dict(dataset="tepsr_wc310", direct="PAID", na_item="B6G_R_HAB_2008", sector="S14_S15"),
    "unemployment_rate": dict(dataset="une_rt_a", age="Y15-74", sex="T", unit="PC_ACT"),
    "employment_rate_20_64": dict(dataset="sdg_08_30", sex="T", unit="PC_POP", indic_em="EMP_LFS"),
    "hicp_headline_rate": dict(dataset="prc_hicp_aind", coicop="CP00", unit="RCH_A_AVG"),
    "hicp_food_rate": dict(dataset="prc_hicp_aind", coicop="CP01", unit="RCH_A_AVG"),
    "hicp_housing_energy_rate": dict(dataset="prc_hicp_aind", coicop="CP04", unit="RCH_A_AVG"),
    "consumption_pc": dict(dataset="nama_10_pc", na_item="P31_S14_S15", unit="CLV10_EUR_HAB"),
    "severe_mat_soc_deprivation_new": dict(dataset="ilc_mdsd11", age="TOTAL", sex="T", unit="PC"),
    "severe_mat_deprivation_legacy": dict(dataset="ilc_mddd11", age="TOTAL", sex="T", unit="PC"),
    "unexpected_expenses_inability": dict(dataset="ilc_mdes04", hhcomp="TOTAL", rskpovth="TOTAL", unit="PC"),
    "housing_cost_overburden": dict(dataset="ilc_lvho07a", rskpovth="TOTAL", age="TOTAL", sex="T", unit="PC"),
    "arrears": dict(dataset="ilc_mdes05", hhcomp="TOTAL", rskpovth="TOTAL", unit="PC"),
    "cannot_keep_home_warm": dict(dataset="ilc_mdes01", hhcomp="TOTAL", rskpovth="TOTAL", unit="PC"),
}

results = {}
for name, spec in specs.items():
    dataset = spec.pop("dataset")
    try:
        df = fetch(dataset, geo=GEOS, time=YEARS, **spec)
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {name} ({dataset}): {e}")
        continue
    results[name] = save(df, name, name)

# minimum wage: semi-annual -> take S1 of each year as the annual reference point
mw = fetch("earn_mw_cur", currency="EUR", geo=["EL"])
if not mw.empty:
    mw = mw[mw["time"].astype(str).str.endswith("S1")].copy()
    mw["time"] = mw["time"].astype(str).str.replace("-S1", "").astype(int)
    mw = mw[["geo", "time", "value"]].rename(columns={"value": "minimum_wage_eur_month"})
    mw.to_csv(f"{RAW}/minimum_wage_eur_month.csv", index=False)
    print(f"minimum_wage: {len(mw)} rows, {mw.time.min()}-{mw.time.max()}")
    results["minimum_wage_eur_month"] = mw

print("\nDone. Fetched:", list(results.keys()))
