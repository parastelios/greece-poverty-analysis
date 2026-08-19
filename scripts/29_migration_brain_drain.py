"""P1b: migration / brain drain, scoped narrow per the agreed plan -- net
migration of a country's OWN nationals (not the demo_gind residual, which
turned out to be dominated by statistical adjustment, not real migration --
see the feasibility note below), age profile if comparable, and return
migration (immigration of own nationals) if comparable. Framed as a
structural scarring channel, not a variable to bolt onto the regression.

Feasibility note on demo_gind (checked and rejected): Eurostat's headline
"net migration rate" (MIGTRT) is officially "net migration plus statistical
adjustment" -- a residual (population change minus natural change) that
absorbs census revisions and register corrections, not just real migration.
For Greece it's strongly POSITIVE every year 2011-2024 (+150k to +240k),
which flatly contradicts the well-documented emigration story and Greece's
own falling population -- a clear sign this indicator is dominated by
statistical noise for this country, not usable at face value. Used
migr_emi1ctz / migr_imm1ctz (actual flow registrations, citizen=NAT) instead
-- these gave a coherent, plausible pattern and, checked directly, all 27 EU
countries report into this table.

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
"""
import pandas as pd
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
YEARS = range(2008, 2025)
EU = eu_members(2024)

# --- net migration of own nationals, all 27 EU countries ---
from eurostat import fetch as _fetch

emi = _fetch("migr_emi1ctz", citizen="NAT", age="TOTAL", unit="NR", sex="T",
             agedef="COMPLET", time=YEARS)
imm = _fetch("migr_imm1ctz", citizen="NAT", age="TOTAL", unit="NR", sex="T",
             agedef="COMPLET", time=YEARS)
pop = _fetch("demo_pjan", sex="T", age="TOTAL", time=YEARS)

emi = emi[emi.geo.isin(EU)][["geo", "time", "value"]].rename(columns={"value": "emigration_nationals"})
imm = imm[imm.geo.isin(EU)][["geo", "time", "value"]].rename(columns={"value": "immigration_nationals"})
pop = pop[pop.geo.isin(EU)][["geo", "time", "value"]].rename(columns={"value": "population"})

panel = emi.merge(imm, on=["geo", "time"], how="outer").merge(pop, on=["geo", "time"], how="left")
panel["net_migration_nationals"] = panel["emigration_nationals"] - panel["immigration_nationals"]
panel["net_migration_rate_per1000"] = 1000 * panel["net_migration_nationals"] / panel["population"]
panel.to_csv(f"{RAW}/migration_nationals_panel.csv", index=False)

print(f"Coverage: {panel.geo.nunique()} of {len(EU)} EU countries, years {panel.time.min()}-{panel.time.max()}")
missing_years = panel.groupby("geo")["time"].count()
print("\nYears of data per country (17 = full 2008-2024 coverage):")
print(missing_years.sort_values().to_string())

print("\n=== Greece: emigration, immigration (returnees), net, of Greek nationals ===")
gr = panel[panel.geo == "EL"].sort_values("time")
print(gr[["time", "emigration_nationals", "immigration_nationals", "net_migration_nationals", "net_migration_rate_per1000"]].round(2).to_string(index=False))

cum_net = gr["net_migration_nationals"].sum()
print(f"\nCumulative net loss of Greek nationals, 2008-2024: {cum_net:,.0f}")
print(f"As % of 2008 population: {100*cum_net/gr[gr.time==2008]['population'].iloc[0]:.2f}%")

# --- cross-country comparison: cumulative net migration rate, 2008-2024 ---
cum = panel.dropna(subset=["net_migration_nationals"]).groupby("geo").agg(
    total_net_migration=("net_migration_nationals", "sum"),
    avg_population=("population", "mean"),
    n_years=("time", "count"),
).reset_index()
cum = cum[cum.n_years >= 15]  # require near-full coverage for a fair comparison
cum["cum_net_pct_of_pop"] = 100 * cum["total_net_migration"] / cum["avg_population"]
cum = cum.sort_values("cum_net_pct_of_pop", ascending=False)
cum.to_csv(f"{OUT}/migration_cumulative_comparison.csv", index=False)
print(f"\n=== Cumulative net migration of own nationals as % of population, 2008-2024 ({len(cum)} countries with >=15 years data) ===")
print(cum[["geo", "total_net_migration", "cum_net_pct_of_pop", "n_years"]].round(2).to_string(index=False))

# --- age profile of emigration, Greece specifically ---
print("\n=== Age profile check: which age-band codes does Greece actually report? ===")
age_check = _fetch("migr_emi1ctz", geo=["EL"], citizen="NAT", unit="NR", sex="T",
                    agedef="COMPLET", time=[2012, 2019])
print(sorted(age_check.age.unique()))

age_bands = ["Y15-19", "Y20-24", "Y25-29", "Y30-34", "Y15-64", "Y_GE65", "TOTAL"]
age_panel = _fetch("migr_emi1ctz", geo=["EL"], citizen="NAT", unit="NR", sex="T",
                    agedef="COMPLET", age=age_bands, time=YEARS)
age_panel = age_panel[["age", "time", "value"]].pivot(index="time", columns="age", values="value")
age_panel.to_csv(f"{OUT}/greece_emigration_age_profile.csv")
print("\nGreek nationals' emigration by age band, selected years:")
print(age_panel.loc[[2012, 2019, 2024]].to_string() if all(y in age_panel.index for y in [2012,2019,2024]) else age_panel.to_string())
