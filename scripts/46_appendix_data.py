"""Assemble every variable used anywhere in the project into one tidy JSON for
the interactive appendix (47_build_appendix.py renders it).

Design rules:
  - Only the 27 current EU members are kept. Eurostat publishes many of these
    datasets for candidate and EFTA countries too (Bosnia, Serbia, Norway,
    Switzerland...), and for the euro-area aggregates EA19/EA20 -- none of which
    are in the estimation panel. Drawing them here would show the reader a
    country set the analysis never used.
  - EU comparator: Eurostat's own EU27_2020 aggregate wherever published
    (population-weighted). Otherwise an unweighted member-state mean, flagged
    per series, with years having <20 reporters dropped -- in the newest year
    only a few countries report and they are not a random subset.
  - Nothing is silently dropped: a failed fetch prints and is recorded.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from eurostat import fetch
from eu_membership import eu_members
from currency import normalise_nac_to_euro

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
MEMBERS = sorted(eu_members(2025))
EU = "EU27_2020"
YEARS = range(2000, 2026)
MIN_REPORTERS = 20

SERIES, PROBLEMS = {}, []

# Every EU27 = 100 index shares this caveat: the file carries no EU27 row, so
# the drawn EU line is the unweighted member mean, which is not the 100 the
# index is defined against.
EU_NOTE = (
    " The plotted EU line is the unweighted mean across the 27 member states, not "
    "the 100 baseline: the index is normalised to the population-weighted EU27 "
    "aggregate, and the typical member state sits below it. Read Greece against the "
    "country lines and against 100, not against the plotted mean.")


def eu_line(d, valcol="value"):
    """Return (eu_series, basis_label). Prefer the official aggregate."""
    eu = d[d.geo == EU].set_index("time")[valcol]
    if not eu.empty:
        return eu, "Eurostat EU27 aggregate (population-weighted)"
    grp = d[d.geo.isin(MEMBERS)].groupby("time")[valcol]
    return grp.mean()[grp.size() >= MIN_REPORTERS], \
        f"unweighted mean of member states (years with <{MIN_REPORTERS} reporting dropped)"


def register(key, label, group, unit, d, valcol="value", note="", decimals=2):
    """d must have geo/time/<valcol>. Stores every country plus the EU line."""
    d = d[["geo", "time", valcol]].dropna()
    # Keep the EU aggregate row (eu_line consumes it) and the 27 members only --
    # see the module docstring on why non-members are excluded.
    d = d[d.geo.isin(MEMBERS + [EU])]
    if d.empty:
        PROBLEMS.append(f"{key}: no rows")
        print(f"  [EMPTY] {key}")
        return
    d = d[d.time.between(min(YEARS), max(YEARS))]
    eu, basis = eu_line(d, valcol)
    years = sorted(d.time.unique())
    countries = {}
    for g, grp in d[d.geo != EU].groupby("geo"):
        s = grp.set_index("time")[valcol]
        countries[g] = [None if pd.isna(v) else round(float(v), decimals)
                        for v in (s.get(y, np.nan) for y in years)]
    SERIES[key] = dict(
        label=label, group=group, unit=unit, note=note, eu_basis=basis,
        years=[int(y) for y in years],
        countries=countries,
        eu=[None if pd.isna(v) else round(float(v), decimals)
            for v in (eu.get(y, np.nan) for y in years)],
    )
    print(f"  {key:34} {len(countries):3} countries, {years[0]}-{years[-1]}")


def try_fetch(key, label, group, unit, code, filt, note="", decimals=2, transform=None):
    try:
        d = fetch(code, geo=None, time=YEARS, **filt) if False else fetch(code, time=YEARS, **filt)
    except Exception as e:
        PROBLEMS.append(f"{key}: fetch failed ({e})")
        print(f"  [FAIL] {key}: {e}")
        return None
    if d.empty or "value" not in d.columns:
        PROBLEMS.append(f"{key}: empty/no value column")
        print(f"  [EMPTY] {key}")
        return None
    if transform is not None:
        d = transform(d)
    register(key, label, group, unit, d, note=note, decimals=decimals)
    return d


print("=== Poverty and hardship ===")
try_fetch("arop", "AROP income poverty", "Poverty measures", "% of people", "ilc_li02",
          dict(age=["TOTAL"], sex=["T"], unit=["PC"], statinfo=["MED_EI"], rskpovth=["B_60"]))
try_fetch("subjective_poverty", "Subjective poverty (difficulty making ends meet)",
          "Poverty measures", "% of households", "ilc_mdes09",
          dict(hhcomp=["TOTAL"], rskpovth=["TOTAL"], unit=["PC"], lev_diff=["DIF", "GRT"]),
          note="Sum of 'with difficulty' and 'with great difficulty'.",
          transform=lambda d: d.groupby(["geo", "time"], as_index=False)["value"].sum())
try_fetch("deprivation_new", "Severe material & social deprivation (13-item, 2015-)",
          "Poverty measures", "% of people", "ilc_mdsd11", dict(age=["TOTAL"], sex=["T"], unit=["PC"]))
try_fetch("deprivation_legacy", "Severe material deprivation (legacy 9-item, to 2020)",
          "Poverty measures", "% of people", "ilc_mddd11", dict(age=["TOTAL"], sex=["T"], unit=["PC"]))
try_fetch("s80s20", "Income inequality (S80/S20 ratio)", "Poverty measures", "ratio",
          "ilc_di11", dict(age=["TOTAL"], sex=["T"], unit=["RAT"]))

# AROPE: legacy + revised spliced at 2020/2021 (project convention)
try:
    leg = fetch("ilc_peps01", time=YEARS, age=["TOTAL"], sex=["T"], unit=["PC"])[["geo", "time", "value"]]
    new = fetch("ilc_peps01n", time=YEARS, age=["TOTAL"], sex=["T"], unit=["PC"])[["geo", "time", "value"]]
    arope = pd.concat([leg[leg.time <= 2020], new[new.time > 2020]])
    register("arope", "AROPE (poverty or social exclusion)", "Poverty measures", "% of people",
             arope, note="Legacy ilc_peps01 to 2020 spliced with revised ilc_peps01n from 2021.")
except Exception as e:
    PROBLEMS.append(f"arope: {e}")

print("\n=== Labour market ===")
try_fetch("unemployment", "Unemployment rate", "Labour market", "% of active pop.",
          "une_rt_a", dict(age=["Y15-74"], sex=["T"], unit=["PC_ACT"]))
try_fetch("ltu", "Long-term unemployment (12 months or more)", "Labour market", "% of active pop.",
          "une_ltu_a", dict(age=["Y15-74"], sex=["T"], unit=["PC_ACT"], indic_em=["LTU"]))
try_fetch("youth_unemployment", "Youth unemployment (ages 15-24)", "Labour market", "% of active pop.",
          "une_rt_a", dict(age=["Y15-24"], sex=["T"], unit=["PC_ACT"]))
try_fetch("employment_rate", "Employment rate (ages 20-64)", "Labour market", "% of population",
          "sdg_08_30", dict(sex=["T"], unit=["PC_POP"], indic_em=["EMP_LFS"]))
try_fetch("working_hours", "Actual weekly working hours (main job)", "Work effort", "hours/week",
          "lfsa_ewhan2", dict(nace_r2=["TOTAL"], age=["Y20-64"], sex=["T"], unit=["HR"],
                              wstatus=["EMP"], worktime=["TOTAL"]))
try_fetch("hourly_comp", "Compensation per hour worked (PPS)", "Work effort", "PPS per hour",
          "nama_10_lp_ulc", dict(na_item=["D1_SAL_HW"], unit=["PPS_EU27_2020"]))

print("\n=== Income, output, prices ===")
try_fetch("real_gdp_pc", "Real GDP per capita", "Income & output", "chain-linked EUR",
          "sdg_08_10", dict(unit=["CLV20_EUR_HAB"], na_item=["B1GQ"]), decimals=0)
try_fetch("income_pps", "Income: actual individual consumption (PPS per capita)",
          "Income & output", "PPS per capita", "nama_10_pc",
          dict(na_item=["P41"], unit=["CP_PPS_EU27_2020_HAB"]), decimals=0)
try_fetch("real_income_idx", "Real household disposable income (2008 = 100)",
          "Income & output", "index, 2008=100", "tepsr_wc310",
          dict(direct=["PAID"], na_item=["B6G_R_HAB_2008"], sector=["S14_S15"]))
try_fetch("consumption_pc", "Real household consumption per capita", "Income & output",
          "chain-linked EUR", "nama_10_pc", dict(na_item=["P31_S14_S15"], unit=["CLV10_EUR_HAB"]),
          decimals=0)
try_fetch("saving_rate", "Household saving rate", "Income & output", "% of disposable income",
          "tec00131", dict())
try_fetch("debt_to_income", "Household debt-to-income", "Income & output", "% of disposable income",
          "tec00104", dict(), note="Tested as a model candidate and returned null.")
try_fetch("hicp", "HICP inflation, headline", "Income & output", "% annual change",
          "prc_hicp_aind", dict(coicop=["CP00"], unit=["RCH_A_AVG"]))
try_fetch("hicp_food", "HICP inflation, food & non-alcoholic beverages", "Income & output",
          "% annual change", "prc_hicp_aind", dict(coicop=["CP01"], unit=["RCH_A_AVG"]))
try_fetch("hicp_housing", "HICP inflation, housing & energy", "Income & output",
          "% annual change", "prc_hicp_aind", dict(coicop=["CP04"], unit=["RCH_A_AVG"]))
# Minimum wage is published semi-annually (e.g. "2024-S1"); the project's
# convention is to take the first semester as each year's reference point.
try:
    mw = fetch("earn_mw_cur", currency=["EUR"])
    mw = mw[mw.time.astype(str).str.endswith("S1")].copy()
    mw["time"] = mw.time.astype(str).str.slice(0, 4).astype(int)
    register("min_wage", "Minimum wage (first semester of each year)", "Income & output",
             "EUR per month", mw, decimals=0,
             note="Semi-annual series; S1 of each year taken as the annual reference point. "
                  "Not every member state has a statutory minimum wage.")
except Exception as e:
    PROBLEMS.append(f"min_wage: {e}")

print("\n=== Housing and material strain ===")
try_fetch("housing_overburden", "Housing cost overburden", "Housing & strain", "% of people",
          "ilc_lvho07a", dict(rskpovth=["TOTAL"], age=["TOTAL"], sex=["T"], unit=["PC"]))
try_fetch("arrears", "Households in arrears (bills, rent or loans)", "Housing & strain",
          "% of people", "ilc_mdes05", dict(hhcomp=["TOTAL"], rskpovth=["TOTAL"], unit=["PC"]))
try_fetch("warm", "Cannot keep home adequately warm", "Housing & strain", "% of people",
          "ilc_mdes01", dict(hhcomp=["TOTAL"], rskpovth=["TOTAL"], unit=["PC"]))
try_fetch("unexpected", "Cannot face an unexpected expense", "Housing & strain", "% of people",
          "ilc_mdes04", dict(hhcomp=["TOTAL"], rskpovth=["TOTAL"], unit=["PC"]))

print("\n=== Expectations and wellbeing ===")
try:
    d = fetch("ei_bsco_m", indic=["BS-FS-NY"], s_adj=["NSA"], unit=["BAL"])
    d["year"] = d["time"].astype(str).str.slice(0, 4).astype(int)
    ann = d.groupby(["geo", "year"], as_index=False)["value"].mean().rename(columns={"year": "time"})
    register("fin_expectations", "Household financial expectations, next 12 months",
             "Expectations", "balance (net %)", ann,
             note="Monthly consumer-survey balance averaged to annual. Negative = more households expect deterioration.")
except Exception as e:
    PROBLEMS.append(f"fin_expectations: {e}")
try_fetch("life_satisfaction", "Overall life satisfaction", "Expectations", "mean rating 0-10",
          "ilc_pw01", dict(sex=["T"], age=["Y_GE16"], isced11=["TOTAL"], unit=["RTG"]))

json.dump({"series": SERIES, "problems": PROBLEMS},
          open(OUT / "appendix_series_core.json", "w"))
print(f"\n{len(SERIES)} core series -> appendix_series_core.json")
if PROBLEMS:
    print("Problems:")
    for p in PROBLEMS:
        print("  -", p)


# ==================================================================== DERIVED ==
print("\n=== Derived series ===")

# Real wages: compensation per employee, HICP-deflated, each country's own 2008 = 100
try:
    comp = fetch("nama_10_lp_ulc", time=YEARS, na_item=["D1_SAL_PER"], unit=["EUR"])[["geo","time","value"]] \
        .rename(columns={"value": "comp"})
    hicp_ix = fetch("prc_hicp_aind", time=YEARS, coicop=["CP00"], unit=["INX_A_AVG"])[["geo","time","value"]] \
        .rename(columns={"value": "hicp"})
    w = comp.merge(hicp_ix, on=["geo", "time"])
    b = w[w.time == 2008][["geo", "comp", "hicp"]].rename(columns={"comp": "c0", "hicp": "h0"})
    w = w.merge(b, on="geo")
    w["value"] = 100 * (w.comp / (w.hicp / w.h0)) / w.c0
    register("real_wages_idx", "Real wages, compensation per employee (own 2008 = 100)",
             "Work effort", "index, 2008=100", w,
             note="Nominal compensation per employee deflated by each country's own HICP.")
    # work-effort squeeze = relative hours / relative PPS hourly pay, EU = 100
    hrs, hc = SERIES.get("working_hours"), SERIES.get("hourly_comp")
    if hrs and hc:
        rows = []
        for g in set(hrs["countries"]) & set(hc["countries"]):
            for i, y in enumerate(hrs["years"]):
                if y not in hc["years"]:
                    continue
                j = hc["years"].index(y)
                h, c = hrs["countries"][g][i], hc["countries"][g][j]
                eh, ec = hrs["eu"][i], hc["eu"][j]
                if None in (h, c, eh, ec) or not ec or not eh or not c:
                    continue
                rows.append(dict(geo=g, time=y, value=100 * (h / eh) / (c / ec)))
        register("work_effort_squeeze", "Work-effort squeeze (hours vs hourly pay, EU = 100)",
                 "Work effort", "index, EU=100", pd.DataFrame(rows),
                 note="Relative weekly hours divided by relative PPS hourly compensation. "
                      "The index is normalised so that the population-weighted EU27 aggregate "
                      "equals 100. The plotted EU line is instead the unweighted mean across "
                      "member states, which sits well above 100: most member states have "
                      "below-average hourly pay, and the weighted aggregate is pulled up by the "
                      "large, high-wage economies. Compare Greece against the individual country "
                      "lines rather than against 100.")
except Exception as e:
    PROBLEMS.append(f"real_wages/squeeze: {e}")

# Real AROP threshold, each country's own 2008 = 100 (the 'shrinking ruler')
try:
    th = pd.read_csv(RAW / "arop_threshold_all_countries_nac.csv")
    hi = pd.read_csv(RAW / "panel_hicp_index.csv")
    # The NAC series is in whatever currency each country used at the time, so
    # for the eight countries that adopted the euro mid-series an index against
    # a 2008 base straddles a currency break (Slovenia's 2005 read 21,686).
    th = normalise_nac_to_euro(th, value_col="arop_threshold_nac", verbose=False)
    t = th.merge(hi, on=["geo", "time"])
    b = t[t.time == 2008][["geo", "arop_threshold_nac", "hicp_index"]] \
        .rename(columns={"arop_threshold_nac": "t0", "hicp_index": "h0"})
    t = t.merge(b, on="geo")
    t["value"] = 100 * (t.arop_threshold_nac / (t.hicp_index / t.h0)) / t.t0
    register("arop_threshold_real", "Real AROP poverty threshold (own 2008 = 100)",
             "Poverty measures", "index, 2008=100", t,
             note="The poverty line itself in real terms -- the 'shrinking ruler'.")
except Exception as e:
    PROBLEMS.append(f"arop_threshold_real: {e}")

# Net migration of nationals, per 1000 population
try:
    m = pd.read_csv(RAW / "migration_nationals_panel.csv")
    register("net_migration", "Net migration of nationals (per 1,000 population)",
             "Demography", "per 1,000 people", m.rename(columns={"net_migration_rate_per1000": "value"}),
             note="Positive = more nationals left than returned. Eurostat migration-flow tables.")
except Exception as e:
    PROBLEMS.append(f"net_migration: {e}")

# Scarring stock and every cumulative/duration candidate, from the screening panel
try:
    cp = pd.read_csv(OUT / "cumulative_hardship_candidate_panel.csv")
    CUM_LABELS = {
        "pct_below_peak": ("% below own GDP peak (scarring stock)", "% below peak"),
        "cum_excess_unemployment": ("Cumulative excess unemployment since 2009", "accumulated pp-years"),
        "cum_excess_ltu": ("Cumulative excess long-term unemployment since 2009", "accumulated pp-years"),
        "cum_gdp_shortfall_2008base": ("Cumulative GDP shortfall (fixed 2008 basis)", "accumulated index-points"),
        "cum_gdp_shortfall_ownpeak": ("Cumulative GDP shortfall (own rolling peak)", "accumulated index-points"),
        "cum_wage_shortfall_2008base": ("Cumulative real-wage shortfall (fixed 2008 basis)", "accumulated index-points"),
        "cum_wage_shortfall_ownpeak": ("Cumulative real-wage shortfall (own rolling peak)", "accumulated index-points"),
        "cum_threshold_shortfall": ("Cumulative AROP-threshold shortfall since 2008", "accumulated index-points"),
        "gdp_years_below_2008": ("Consecutive years GDP has been below its 2008 level", "years, current run"),
        "gdp_years_below_peak": ("Consecutive years GDP has been below its own peak", "years, current run"),
        "gdp_longest_streak_2008": ("Longest run of years GDP below 2008 (running maximum)", "years"),
        "gdp_longest_streak_peak": ("Longest run of years GDP below own peak (running maximum)", "years"),
        "gdp_cum_negative_years": ("Cumulative years of negative GDP growth", "years"),
        "wage_years_below_2008": ("Consecutive years real wages have been below their 2008 level", "years, current run"),
        "wage_years_below_peak": ("Consecutive years real wages have been below their own peak", "years, current run"),
        "wage_longest_streak_2008": ("Longest run of years wages below 2008 (running maximum)", "years"),
        "wage_longest_streak_peak": ("Longest run of years wages below own peak (running maximum)", "years"),
        "wage_cum_negative_years": ("Cumulative years of falling real wages", "years"),
        "transfer_effect": ("Welfare-transfer effectiveness (AROP removed by transfers)", "pp of poverty removed"),
    }
    FAMILY = "Screened as one 18-candidate family; see the technical report's Methods."
    # These three constructions look alike on a chart and are not: the current
    # run resets to zero the year a country recovers (Slovenia reads 7, 8, then
    # 0 in 2017), the running maximum never falls, and the negative-year count
    # only ever rises. Saying which is which on the chart itself matters --
    # "years below 2008" reads as a total, and it is not one.
    RUN_NOTE = (" This is the CURRENT unbroken run, not a total: it climbs by one "
                "for each further year below the line and drops straight back to "
                "zero in the first year the country recovers. A country that fell "
                "behind early and caught up shows 0 here, while its longest-run "
                "chart still records the episode.")
    MAX_NOTE = (" This is a running maximum -- the longest unbroken run seen so "
                "far -- so it never falls, even after a country recovers.")
    NEG_NOTE = (" A count of year-on-year declines since 2008, regardless of the "
                "level: it rises in any year the series falls, including falls "
                "that happen well above the 2008 line.")
    for col, (lab, unit) in CUM_LABELS.items():
        if col in cp.columns:
            grp = "Cumulative & duration candidates" if col.startswith(("cum_", "gdp_", "wage_")) \
                else "Income & output"
            extra = (RUN_NOTE if "years_below" in col
                     else MAX_NOTE if "longest_streak" in col
                     else NEG_NOTE if "negative_years" in col else "")
            register(f"cum_{col}" if col.startswith(("gdp_", "wage_")) else col,
                     lab, grp, unit, cp.rename(columns={col: "value"}),
                     note=(FAMILY + extra) if grp.startswith("Cumulative") else "")
except Exception as e:
    PROBLEMS.append(f"cumulative candidates: {e}")


# The candidate panel is truncated to the model window (2015-2024). For the
# appendix the whole arc matters, so the two headline cumulative measures are
# recomputed over their full history; the model window is marked in the chart.
try:
    for src, col, key, lab in [
        (RAW / "panel_unemployment_history.csv", "unemployment_rate",
         "cum_excess_unemployment", "Cumulative excess unemployment since 2009"),
        (RAW / "panel_long_term_unemployment.csv", "ltu_rate",
         "cum_excess_ltu", "Cumulative excess long-term unemployment since 2009"),
    ]:
        d = pd.read_csv(src)[["geo", "time", col]].dropna().sort_values(["geo", "time"])
        base = d[d.time == 2009][["geo", col]].rename(columns={col: "_b"})
        d = d.merge(base, on="geo")
        d["_x"] = (d[col] - d._b).clip(lower=0)
        d = d[d.time >= 2009]
        d["value"] = d.groupby("geo")["_x"].cumsum()
        register(key, lab, "Cumulative & duration candidates", "accumulated pp-years", d,
                 note="Each country's rate above its own 2009 level, summed year on year and "
                      "floored so recovery cannot cancel earlier damage. Full history shown; "
                      "the models estimate on 2015-2024.")
except Exception as e:
    PROBLEMS.append(f"cumulative full history: {e}")


# ================================================================== PANELS =====
# Multi-line comparisons that are not one-series-per-country.
PANELS = {}
print("\n=== Multi-line panels ===")

def panel(key, label, group, unit, lines, years, note="", eu_basis=""):
    PANELS[key] = dict(label=label, group=group, unit=unit, note=note,
                       eu_basis=eu_basis, years=[int(y) for y in years], lines=lines)
    print(f"  {key:34} {len(lines)} lines, {years[0]}-{years[-1]}")

# AROPE by age group, Greece vs EU
try:
    ages = {"Y_LT18": "Under 18", "Y18-24": "18-24", "Y25-49": "25-49",
            "Y50-64": "50-64", "Y_GE65": "65+"}
    a = fetch("ilc_peps01n", time=range(2015, 2026), age=list(ages), sex=["T"], unit=["PC"],
              geo=["EL", EU])[["geo", "time", "age", "value"]]
    yrs = sorted(a.time.unique())
    lines = []
    for code, nm in ages.items():
        for g, style in [("EL", "solid"), (EU, "dashed")]:
            sub = a[(a.age == code) & (a.geo == g)].set_index("time")["value"]
            if sub.empty:
                continue
            lines.append(dict(name=f"{nm} — {'Greece' if g == 'EL' else 'EU27'}",
                              group=nm, style=style, highlight=(g == "EL"),
                              values=[None if pd.isna(sub.get(y, np.nan)) else round(float(sub.get(y)), 2)
                                      for y in yrs]))
    panel("arope_by_age", "AROPE by age group: Greece vs EU27", "Poverty measures",
          "% of people", lines, yrs,
          note="Solid = Greece, dashed = EU27. Every working-age group improved while 65+ reversed.",
          eu_basis="Eurostat EU27 aggregate (population-weighted)")
except Exception as e:
    PROBLEMS.append(f"arope_by_age: {e}")

# Housing cost overburden by tenure, Greece vs EU
try:
    t = pd.read_csv(RAW / "panel_housing_overburden_by_tenure.csv")
    t = t[t.geo.isin(["EL", EU])]
    TEN = {"OWN_L": "Owner, mortgage/loan", "OWN_NL": "Owner, no loan",
           "RENT_MKT": "Tenant, market rate", "RENT_FR": "Tenant, reduced/free", "TOTAL": "All tenures"}
    t = t[t.tenure.isin(TEN)]
    yrs = sorted(t.time.unique())
    lines = []
    for code, nm in TEN.items():
        for g, style in [("EL", "solid"), (EU, "dashed")]:
            sub = t[(t.tenure == code) & (t.geo == g)].set_index("time")["value"]
            if sub.empty:
                continue
            lines.append(dict(name=f"{nm} — {'Greece' if g == 'EL' else 'EU27'}",
                              group=nm, style=style, highlight=(g == "EL"),
                              values=[None if pd.isna(sub.get(y, np.nan)) else round(float(sub.get(y)), 2)
                                      for y in yrs]))
    panel("housing_by_tenure", "Housing cost overburden by tenure: Greece vs EU27",
          "Housing & strain", "% of people", lines, yrs,
          note="Solid = Greece, dashed = EU27. Greek renter sub-series before ~2021 swing implausibly "
               "(small subsample in an ownership-dominated country) and are not used for trend claims.",
          eu_basis="Eurostat EU27 aggregate (population-weighted)")
except Exception as e:
    PROBLEMS.append(f"housing_by_tenure: {e}")

CAT_LABELS = {
    "A01": "Overall household consumption",
    "A0101": "Food & non-alcoholic beverages",
    "A0104": "Housing, water, electricity, gas & fuels",
    "A0107": "Transport",
    "A0108": "Information & communication",
    "A0111": "Restaurants & accommodation",
}


def wage_level_frame():
    """Wage level as an EU27 = 100 index, which is what the price ratio needs.
    The stored file holds absolute compensation per employee, not an index."""
    wl = pd.read_csv(RAW / "panel_nominal_compensation_wage_level.csv")
    eu = wl[wl.geo == EU][["time", "nominal_comp"]].rename(columns={"nominal_comp": "_eu"})
    if eu.empty:
        eu = (wl[wl.geo.isin(MEMBERS)].groupby("time", as_index=False)["nominal_comp"]
              .mean().rename(columns={"nominal_comp": "_eu"}))
    wl = wl.merge(eu, on="time", how="inner")
    wl["wage_level"] = 100 * wl.nominal_comp / wl._eu
    return wl[["geo", "time", "wage_level"]]


# Prices: raw price level vs wage-adjusted pressure, Greece vs EU
try:
    pl = pd.read_csv(RAW / "panel_price_levels_by_category.csv")
    wl = wage_level_frame()
    overall = pl[pl.category == "A01"]
    pw = overall.merge(wl, on=["geo", "time"], how="inner")
    pw["wage_adj"] = 100 * pw.price_level / pw.wage_level
    yrs = sorted(pw.time.unique())
    lines = []
    sub = pw[pw.geo == "EL"]
    for col, tag, style in [("price_level", "raw price level", "solid"),
                            ("wage_adj", "wage-adjusted pressure", "dashed")]:
        ss = sub.set_index("time")[col]
        lines.append(dict(name=f"Greece — {tag}", group=tag, style=style, highlight=True,
                          values=[None if pd.isna(ss.get(y, np.nan)) else round(float(ss.get(y)), 2)
                                  for y in yrs]))
    # Eurostat publishes no EU27 row in this file, and it does not need to: both
    # measures are defined against EU27 = 100 (the price index is normalised to
    # it, and the wage-adjusted measure divides an EU27=100 index by an EU27=100
    # index). Draw that reference explicitly -- without it the panel is titled
    # "Greece vs EU27" while showing only Greece, and the reader cannot see which
    # side of the comparator Greece is on.
    lines.append(dict(name="EU27 reference (= 100 by construction, both measures)",
                      group="EU reference", style="dashed", highlight=False,
                      values=[100.0] * len(yrs)))
    if len(lines) > 0:
        panel("prices_raw_vs_adjusted", "Price level vs wage-adjusted price pressure: Greece vs EU27",
              "Prices", "index, EU = 100", lines, yrs,
              note="Solid = raw price level (what things cost). Dashed = that price level divided by "
                   "the country's own wage level (what they cost relative to a local paycheck). "
                   "Greece sits below the EU on the first and far above it on the second.",
              eu_basis="Eurostat EU27 aggregate (population-weighted)")
except Exception as e:
    PROBLEMS.append(f"prices_raw_vs_adjusted: {e}")

# Price level and wage-adjusted pressure by category, all countries
try:
    pl = pd.read_csv(RAW / "panel_price_levels_by_category.csv")
    wl = wage_level_frame()
    m = pl.merge(wl, on=["geo", "time"], how="left")
    m["wage_adj"] = 100 * m.price_level / m.wage_level
    for cat in sorted(m.category.unique()):
        sub = m[m.category == cat]
        nm = CAT_LABELS.get(cat, cat)
        slug = cat.lower()
        register(f"price_{slug}", f"Price level — {nm}", "Prices", "index, EU = 100",
                 sub.rename(columns={"price_level": "value"}),
                 note="Comparative price level index, EU27 = 100. Categories other than the overall "
                      "basket are published for 2022 onward only."
                      + EU_NOTE)
        register(f"wadj_{slug}", f"Wage-adjusted price pressure — {nm}", "Prices",
                 "index, EU = 100", sub.rename(columns={"wage_adj": "value"}),
                 note="Price level divided by the country's wage level (EU27 = 100 on both). "
                      "Above 100 = this category costs proportionally more of a local paycheck "
                      "than of an EU-average one."
                      + EU_NOTE)
except Exception as e:
    PROBLEMS.append(f"price categories: {e}")

# Average price level across the specific consumption categories, and the same
# figure expressed against what an hour of work pays. A01 is Eurostat's own
# properly weighted overall index; the mean of the five sub-categories is the
# unweighted "typical category" version the eye actually reads off the six price
# charts. Both are registered so the scatter can be checked against the weighted
# aggregate rather than resting on the unweighted one.
try:
    pl = pd.read_csv(RAW / "panel_price_levels_by_category.csv")
    subcats = [c for c in pl.category.unique() if c != "A01"]
    avg = (pl[pl.category.isin(subcats)]
           .groupby(["geo", "time"], as_index=False)["price_level"].mean()
           .rename(columns={"price_level": "value"}))
    register("price_avg_categories", "Average price level across consumption categories",
             "Prices", "index, EU = 100", avg,
             note=f"Unweighted mean of the {len(subcats)} specific categories "
                  "(food, housing & energy, transport, communications, restaurants), "
                  "published 2022 onward. Eurostat's weighted overall index is the "
                  "separate 'Overall household consumption' chart." + EU_NOTE)
except Exception as e:
    PROBLEMS.append(f"price_avg_categories: {e}")

# Greece: reported vs predicted, model that never saw Greece vs model that did
try:
    yb = pd.read_csv(OUT / "cumulative_hardship_final_model_year_by_year.csv")
    yrs = sorted(yb.time.unique())
    def col(c):
        ss = yb.set_index("time")[c]
        return [None if pd.isna(ss.get(y, np.nan)) else round(float(ss.get(y)), 2) for y in yrs]
    lines = [dict(name="Reported subjective poverty", group="actual", style="solid",
                  highlight=True, values=col("subjective_poverty")),
             dict(name="Predicted — model never saw Greece (out-of-sample)", group="predicted",
                  style="dashed", highlight=False, values=col("predicted"))]
    ins = OUT / "cumulative_hardship_final_model_insample.csv"
    if ins.exists():
        d2 = pd.read_csv(ins).set_index("time")
        lines.append(dict(name="Predicted — model fitted on all countries incl. Greece",
                          group="predicted_in", style="dotted", highlight=False,
                          values=[None if y not in d2.index else round(float(d2.loc[y, "predicted"]), 2)
                                  for y in yrs]))
    panel("model_actual_vs_predicted", "Greece: reported vs predicted subjective poverty",
          "Model diagnostics", "% of households", lines, yrs,
          note="The out-of-sample line comes from the final model fitted on the other 26 countries "
               "only, then applied to Greece.")
except Exception as e:
    PROBLEMS.append(f"model_actual_vs_predicted: {e}")

# Every model side by side: Greece's residual in-sample vs out-of-sample
try:
    frames = []
    for f in ("model_scorecard.csv", "model_scorecard_ltu.csv"):
        fp = OUT / f
        if fp.exists():
            frames.append(pd.read_csv(fp))
    sc = pd.concat(frames, ignore_index=True).dropna(subset=["gr_avg_residual_oos"])
    # The two scorecard files overlap: the same specification appears under
    # different keys (e.g. C_plus_arrears_unexpected and C_baseline are one
    # model). Dedupe on the numbers, not the key, so it is not listed twice.
    # Rounded to 1dp because the two files store the same figure at different
    # precision (11.59 vs 11.6); all three numbers must match to count as a dup.
    sc["_sig"] = (sc.gr_avg_residual_oos.round(1).astype(str) + "|"
                  + sc.r2.round(2).astype(str) + "|"
                  + sc.gr_avg_residual_insample.round(1).astype(str))
    sc = sc.drop_duplicates(subset=["_sig"], keep="first").drop(columns="_sig")
    PANELS["model_scorecard_bars"] = dict(
        label="Every model side by side: Greece's unexplained gap",
        group="Model diagnostics", unit="percentage points", kind="bars",
        note="Solid = out-of-sample (model refit without Greece, then applied to it). "
             "Dashed outline = in-sample (model allowed to see Greece's own data). "
             "The in-sample figure is always the more flattering one.",
        eu_basis="",
        rows=[dict(model=str(r.model), label=str(r.label)[:80],
                   pretty=(str(r.label)[:44] + "\u2026") if len(str(r.label)) > 45 else str(r.label),
                   oos=round(float(r.gr_avg_residual_oos), 2),
                   insample=None if pd.isna(r.gr_avg_residual_insample)
                            else round(float(r.gr_avg_residual_insample), 2),
                   r2=None if pd.isna(r.r2) else round(float(r.r2), 3))
              for r in sc.itertuples()])
    print(f"  model_scorecard_bars               {len(sc)} models")
except Exception as e:
    PROBLEMS.append(f"model_scorecard_bars: {e}")

# Greece-only: anchored (fixed-yardstick) poverty against AROP
try:
    ap = pd.read_csv(OUT / "anchored_poverty.csv")
    yrs = sorted(ap.year.unique())
    def c2(c):
        ss = ap.set_index("year")[c]
        return [None if pd.isna(ss.get(y, np.nan)) else round(float(ss.get(y)), 2) for y in yrs]
    panel("anchored_poverty", "Greece: fixed-yardstick (anchored) poverty vs AROP",
          "Poverty measures", "% of people",
          [dict(name="Anchored to 2008 living standards (approximated)", group="anchored",
                style="solid", highlight=True, values=c2("anchored_poverty_rate")),
           dict(name="AROP, the official moving-threshold rate", group="arop",
                style="dashed", highlight=False, values=c2("actual_arop_rate"))],
          yrs,
          note="Greece only. The anchored series holds the poverty line at its 2008 real value; "
               "AROP lets it move with the collapsing median. Anchored figures are an approximation "
               "from four published summary points, least certain in 2012-2014.")
except Exception as e:
    PROBLEMS.append(f"anchored_poverty: {e}")

# ================================================================ SCATTERS =====
# Cross-country relationships. Each pair is chosen because the report makes a
# claim about it; the scatter is where that claim becomes visible in one frame.
SCATTERS = {}
print("\n=== Scatter relationships ===")

# ================================================== breadth-of-disadvantage composite ====
# Not a model variable -- family C tested it and it is null (see
# docs/publication_strategy.md). It is a DESCRIPTIVE summary: in a given year,
# across indicators where "worse" has an unambiguous direction, what share place
# this country in the EU's worst quintile?
#
# Two rules make it honest. Direction has to be declared per indicator, not
# inferred. And the outcome (subjective poverty) plus every Model C-LTU
# covariate are excluded -- a composite containing them would summarise the
# thing the reports are trying to explain, using the variables used to explain
# it.
WORSE_HIGH = {
    "arop": 1, "arope": 1, "deprivation_new": 1, "deprivation_legacy": 1, "s80s20": 1,
    "subjective_poverty": 1, "arrears": 1, "housing_overburden": 1, "unexpected": 1,
    "warm": 1, "unemployment": 1, "ltu": 1, "youth_unemployment": 1, "debt_to_income": 1,
    "hicp": 1, "hicp_food": 1, "hicp_housing": 1, "working_hours": 1,
    "work_effort_squeeze": 1, "wadj_a01": 1, "pct_below_peak": 1,
    "employment_rate": 0, "hourly_comp": 0, "income_pps": 0, "real_gdp_pc": 0,
    "consumption_pc": 0, "real_income_idx": 0, "real_wages_idx": 0,
    "arop_threshold_real": 0, "min_wage": 0, "saving_rate": 0, "life_satisfaction": 0,
    "fin_expectations": 0, "transfer_effect": 0, "net_migration": 0,
}
CIRCULAR = {"subjective_poverty", "arop", "arope", "deprivation_new",
            "deprivation_legacy", "arrears", "housing_overburden", "unexpected",
            "ltu", "income_pps"}
WORST_Q = 0.20
def _breadth_test_note():
    """The predictive test's outcome, read from its own artifact.

    This sentence was previously hardcoded as "null (p=0.083)". No such value
    exists in p3a_results.csv or anywhere else in data/processed -- the figure
    was asserting a number the artifact does not contain. It is now derived,
    and says so honestly when the test has not been run yet.
    """
    f = OUT / "p3a_results.csv"
    if not f.exists():
        return ("the predictive test (P3a) has not been run in this build, so "
                "treat this purely as a description of the condition.")
    r = pd.read_csv(f)
    alone = r[r.step == "alone"].iloc[0]
    with_ctl = r[r.step == "P3_plus_famD"]
    s = (f"tested as a predictor of reported hardship in P3a. On its own it is "
         f"not significant (coefficient {alone.coef:+.2f}, p = {alone.p:.2f})")
    if len(with_ctl):
        w = with_ctl.iloc[0]
        s += (f", and once the other accumulated measures enter the model the "
              f"coefficient reverses sign ({w.coef:+.2f}). A quantity whose "
              f"sign depends on what else is in the model cannot carry an "
              f"explanatory reading")
    return s + ". It summarises the condition rather than explaining it."


try:
    indep = [k for k in WORSE_HIGH if k not in CIRCULAR and k in SERIES]
    flags = []
    for k in indep:
        v, hi = SERIES[k], WORSE_HIGH[k]
        for i, y in enumerate(v["years"]):
            vals = {c: sv[i] for c, sv in v["countries"].items() if sv[i] is not None}
            if len(vals) < MIN_REPORTERS:
                continue
            pct = pd.Series(vals).rank(pct=True)
            worst = (pct >= 1 - WORST_Q) if hi else (pct <= WORST_Q)
            flags += [dict(geo=c, time=int(y), series=k, worst=int(worst[c])) for c in vals]
    fl = pd.DataFrame(flags)
    comp = (fl.groupby(["geo", "time"], as_index=False)
              .agg(n_ind=("series", "nunique"), n_worst=("worst", "sum")))
    # a country-year needs enough indicators for a share to mean anything
    comp = comp[comp.n_ind >= 10]
    comp["value"] = 100 * comp.n_worst / comp.n_ind
    register("breadth_worst_quintile",
             "Breadth of disadvantage: share of indicators placing the country in the EU's worst fifth",
             "Poverty measures", "% of indicators", comp, decimals=1,
             note=f"Across {len(indep)} indicators with an unambiguous worse-direction, the share "
                  f"that put this country in the EU's bottom quintile that year. The outcome "
                  f"(subjective poverty) and every model covariate are excluded, so this cannot "
                  f"restate what the reports set out to explain. Years with fewer than 10 "
                  f"reporting indicators are dropped. DESCRIPTIVE ONLY: {_breadth_test_note()}")
except Exception as e:
    PROBLEMS.append(f"breadth_worst_quintile: {e}")


# ------------------------------------- the fixed-basket comparison, 2008 vs 2024 ----
# The ladder above uses each indicator's OWN earliest usable year, which is the
# honest way to show the whole universe and a poor way to compare: 25 different
# baselines cannot be added up. The report needs one basket measured twice.
#
# SELECTION RULE, fixed before any result was looked at: every indicator with a
# valid EU position in BOTH 2008 and 2024, chosen without reference to whether
# it improved or deteriorated. Nothing is interpolated and nothing is
# substituted -- an indicator either has both endpoints or it is not in the
# basket.
#
# The cost is stated rather than hidden. Unemployment, youth unemployment and
# the employment rate are absent because comparable EU coverage for them begins
# in 2009, one year late. The basket is not free of labour-market information:
# hours worked, pay per hour, the work-effort squeeze and real wages are all in
# it. What is missing is the unemployment count itself.
BASKET_FIRST, BASKET_LAST = 2008, 2024


def _country_position(v, hi, year, geo="EL"):
    """geo's position in the EU distribution that year, 100 = worst."""
    if year not in v["years"]:
        return None
    i = v["years"].index(year)
    vals = {c: sv[i] for c, sv in v["countries"].items() if sv[i] is not None}
    if len(vals) < MIN_REPORTERS or geo not in vals:
        return None
    signed = pd.Series(vals) if hi else -pd.Series(vals)
    return 100 * float(signed.rank(pct=True)[geo]), float(vals[geo]), len(vals)


def _greek_position(v, hi, year):
    """Greece's position in the EU distribution that year, 100 = worst."""
    return _country_position(v, hi, year, "EL")


WORST_LINE = 100 * (1 - WORST_Q)      # a position at or above this is worst-fifth
STATUS = {
    (True, True): ("already", "already worst fifth"),
    (False, True): ("entered", "entered worst fifth"),
    (True, False): ("left", "left worst fifth"),
    (False, False): ("outside", ""),
}
# New entrants first: they carry the change. Then the ones that were already
# there, then any that left, then the rest.
STATUS_ORDER = {"entered": 0, "already": 1, "left": 2, "outside": 3}

try:
    fixed = []
    for k in [k for k in WORSE_HIGH if k not in CIRCULAR and k in SERIES]:
        v, hi = SERIES[k], WORSE_HIGH[k]
        a = _greek_position(v, hi, BASKET_FIRST)
        b = _greek_position(v, hi, BASKET_LAST)
        if a is None or b is None:
            continue
        key, label = STATUS[(a[0] >= WORST_LINE, b[0] >= WORST_LINE)]
        fixed.append(dict(
            key=k, label=v["label"], unit=v["unit"], worse_high=bool(hi),
            pct_2008=round(a[0], 1), val_2008=round(a[1], 2), n_2008=a[2],
            pct_2024=round(b[0], 1), val_2024=round(b[1], 2), n_2024=b[2],
            status=key, status_label=label))
    if not fixed:
        raise ValueError("the fixed basket is empty")
    fixed.sort(key=lambda r: (STATUS_ORDER[r["status"]], -r["pct_2024"]))

    counts = {s: sum(1 for r in fixed if r["status"] == s) for s in STATUS_ORDER}
    n_2008 = counts["already"] + counts["left"]
    n_2024 = counts["already"] + counts["entered"]
    pd.DataFrame(fixed).to_csv(OUT / "breadth_fixed_basket.csv", index=False)

    # The trajectory on the SAME basket, so the line and the endpoints count the
    # same things every year. Verified to have no gaps before it is written: a
    # constant denominator that quietly varies would be worse than an honest
    # varying one.
    byears = list(range(BASKET_FIRST, BASKET_LAST + 1))
    traj, holes = [], []
    for y in byears:
        ps = [_greek_position(SERIES[r["key"]], WORSE_HIGH[r["key"]], y) for r in fixed]
        if any(p is None for p in ps):
            holes.append(y)
            continue
        traj.append(dict(time=y, n_ind=len(ps),
                         n_worst=sum(1 for p in ps if p[0] >= WORST_LINE),
                         value=round(100 * sum(1 for p in ps if p[0] >= WORST_LINE)
                                     / len(ps), 1)))
    if holes:
        raise ValueError(f"fixed basket has gaps in {holes}; the constant "
                         f"denominator would be a fiction")
    pd.DataFrame(traj).to_csv(OUT / "breadth_fixed_trajectory.csv", index=False)

    # The SAME basket, EVERY country, so the "how many measures" view can
    # answer the question its own tab name asks -- is Greece's trajectory
    # unusual, compared with what? -- rather than showing Greece alone a
    # second time. Coverage is not uniform across all 27: a country-year is
    # plotted only where every one of the 16 indicators is present for that
    # country that year, everything else is a genuine gap (null), the same
    # convention the rest of this project uses for missing data rather than
    # inventing a reading for it. One country (Croatia) is absent in nearly
    # every year on this account; that is reported, not hidden.
    all_countries = sorted(SERIES[fixed[0]["key"]]["countries"].keys())
    traj_all = []
    for geo in all_countries:
        for y in byears:
            ps = [_country_position(SERIES[r["key"]], WORSE_HIGH[r["key"]], y, geo)
                  for r in fixed]
            if any(p is None for p in ps):
                continue
            traj_all.append(dict(
                geo=geo, time=y, n_ind=len(ps),
                n_worst=sum(1 for p in ps if p[0] >= WORST_LINE)))
    _tall = pd.DataFrame(traj_all)
    _tall.to_csv(OUT / "breadth_fixed_trajectory_all.csv", index=False)
    _coverage = _tall.groupby("geo").size()
    _thin = sorted(_coverage[_coverage < len(byears) // 2].index)
    print(f"  fixed basket, all countries: {len(all_countries)} countries, "
          f"{len(_tall)} country-years with full 16-indicator coverage"
          + (f"; sparse coverage (<50% of years): {_thin}" if _thin else ""))

    PANELS["breadth_fixed_basket"] = dict(
        label=f"The same {len(fixed)} indicators in {BASKET_FIRST} and {BASKET_LAST}",
        group="Poverty measures", unit="position in the EU distribution",
        kind="fixed_basket", rows=fixed,
        counts=dict(total=len(fixed), worst_2008=n_2008, worst_2024=n_2024,
                    already=counts["already"], entered=counts["entered"],
                    left=counts["left"], outside=counts["outside"]),
        note=f"Every indicator with a valid EU position in both {BASKET_FIRST} "
             f"and {BASKET_LAST}, selected without reference to whether it "
             f"improved or deteriorated. Unemployment, youth unemployment and "
             f"the employment rate are absent because comparable EU coverage "
             f"for them begins in 2009; hours worked, pay per hour, the "
             f"work-effort squeeze and real wages are all present, so the "
             f"basket is not free of labour-market information.")
    print(f"  fixed basket {BASKET_FIRST}-{BASKET_LAST}: {len(fixed)} indicators, "
          f"{n_2008} -> {n_2024} in the worst fifth "
          f"({100*n_2008/len(fixed):.1f}% -> {100*n_2024/len(fixed):.1f}%); "
          f"{counts['already']} already, {counts['entered']} entered, "
          f"{counts['left']} left")
except Exception as e:
    PROBLEMS.append(f"breadth_fixed_basket: {e}")


# ------------------------------------------------- the composite, indicator by indicator ----
# The composite above is one number a year; this is the audit trail behind it.
# For each contributing indicator: where Greece sat in the EU distribution at its
# earliest usable year, where it sits now, and where the EU itself sits.
#
# Units are incompatible across the 25 (percentages, PPS per capita, hours,
# EUR per month, a 0-10 rating), so the shared axis is POSITION in the EU
# distribution, oriented so that 100 is always the worst place to be regardless
# of whether high or low is the bad direction. Raw values travel with each row
# for the tooltip, so the reader never has to take the position on trust.
try:
    rows = []
    for k in [k for k in WORSE_HIGH if k not in CIRCULAR and k in SERIES]:
        v, hi = SERIES[k], WORSE_HIGH[k]
        usable = []
        for i, y in enumerate(v["years"]):
            vals = {c: sv[i] for c, sv in v["countries"].items() if sv[i] is not None}
            if len(vals) < MIN_REPORTERS or "EL" not in vals:
                continue
            # rank so that 100 = worst, whichever direction "worse" runs in
            signed = pd.Series(vals) if hi else -pd.Series(vals)
            pct = signed.rank(pct=True)
            usable.append((int(y), 100 * float(pct["EL"]), float(vals["EL"]),
                           len(vals), signed, vals))
        if len(usable) < 2:
            continue
        first, last = usable[0], usable[-1]
        eu_pct = None
        eu_val = v["eu"][v["years"].index(last[0])]
        # An EU position is only a real position where Eurostat publishes a
        # weighted aggregate. For an unweighted member mean it would land near
        # the middle by construction, which would look like a finding and is not.
        if "aggregate" in v["eu_basis"] and eu_val is not None:
            pool = dict(last[5]); pool["__EU__"] = eu_val
            sp = pd.Series(pool) if hi else -pd.Series(pool)
            eu_pct = 100 * float(sp.rank(pct=True)["__EU__"])
        rows.append(dict(
            key=k, label=v["label"], unit=v["unit"], worse_high=bool(hi),
            year_first=first[0], pct_first=round(first[1], 1), val_first=round(first[2], 2),
            year_last=last[0], pct_last=round(last[1], 1), val_last=round(last[2], 2),
            n_first=first[3], n_last=last[3],
            eu_last=None if eu_val is None else round(float(eu_val), 2),
            eu_pct=None if eu_pct is None else round(eu_pct, 1),
            eu_basis=v["eu_basis"]))
    rows.sort(key=lambda r: -r["pct_last"])
    PANELS["breadth_indicator_ladder"] = dict(
        label="Every indicator behind the breadth measure: earliest available "
              "year versus latest year",
        group="Poverty measures", unit="position in the EU distribution", kind="position_ladder",
        note="One row per contributing indicator. The hollow dot is Greece's position at that "
             "indicator's earliest usable year, the solid dot its latest; the shaded band is the "
             "EU's worst fifth, which is what the breadth measure counts. The axis is position, "
             "not value \u2014 0 is the best place in the Union to be on that indicator and 100 "
             "the worst, whichever direction 'worse' happens to run in, because the 25 indicators "
             "have no common unit. Hover any row for the underlying figures in their own units. "
             "The diamond is the EU's own position, shown only for the 17 indicators where "
             "Eurostat publishes a population-weighted aggregate; for the other 8 the EU line is "
             "an unweighted mean of member states, which sits mid-distribution by construction "
             "and would read as a finding when it is only arithmetic.",
        eu_basis="", rows=rows)
    print(f"  breadth_indicator_ladder           {len(rows)} indicators, "
          f"{sum(1 for r in rows if r['eu_pct'] is not None)} with a weighted EU position")
except Exception as e:
    PROBLEMS.append(f"breadth_indicator_ladder: {e}")


SCATTER_SPECS = [
    ("prices_vs_pay", "price_avg_categories", "hourly_comp",
     "What things cost against what an hour of work pays",
     "The cost-of-living squeeze as a single frame. The horizontal axis is the average "
     "price level across consumption categories, EU27 = 100; the vertical axis is "
     "compensation per hour worked in PPS. Richer countries are expensive because they "
     "pay well, so the cloud slopes upward. What matters is distance from that line: a "
     "country below it faces prices its hourly pay does not support. Greece is mid-pack "
     "on prices -- 15th of 27, close to the EU average -- and last of 27 on hourly pay. "
     "That combination puts it further below the fitted line than any other member "
     "state, and by a wide margin: its shortfall is roughly twice the next country's. "
     "This is the same squeeze the wage-adjusted price charts show category by "
     "category, here in one picture.", True),
    ("hours_vs_pay", "working_hours", "hourly_comp",
     "Hours worked against what an hour is paid",
     "Greece sits in the corner no country wants: the longest working week in the Union at the "
     "lowest hourly compensation. This is the work-effort squeeze before it is compressed into "
     "a single index.", True),
    ("arop_vs_subjective", "arop", "subjective_poverty",
     "Official income poverty against reported hardship",
     "The project's central paradox in one frame. Most countries cluster along a loose upward "
     "band; Greece sits far above it, reporting hardship no other country reports at a similar "
     "income-poverty rate.", True),
    ("ltu_vs_subjective", "ltu", "subjective_poverty",
     "Long-term unemployment against reported hardship",
     "Long-term unemployment is the single strongest correlate of Greek subjective poverty in "
     "the whole project. Across countries the relationship is real but far from deterministic.", True),
    ("cumulative_vs_subjective", "cum_excess_unemployment", "subjective_poverty",
     "Accumulated unemployment exposure against reported hardship",
     "The headline mechanism. Greece is far out along the x-axis: not merely a bad labour "
     "market now, but more accumulated exposure than any other member state.", True),
    ("income_vs_subjective", "income_pps", "subjective_poverty",
     "Income against reported hardship",
     "Richer countries report less hardship, as expected. Greece reports far more than its "
     "income level alone would predict -- the residual the models spend Part II chasing.", True),
    ("debt_vs_saving", "debt_to_income", "saving_rate",
     "Household debt against household saving",
     "The counter-narrative pair. Greece has lower debt than most of the EU and a negative "
     "saving rate: the problem is not over-borrowing, it is that there is nothing left to save. "
     "Low debt here should not be read as financial health.", True),
    ("housing_vs_arrears", "housing_overburden", "arrears",
     "Housing cost overburden against arrears",
     "Two different cash-flow pressures that tend to travel together. Greece is extreme on both.", True),
    ("lifesat_vs_subjective", "life_satisfaction", "subjective_poverty",
     "Life satisfaction against reported financial hardship",
     "The domain-specificity check. If Greek answers were simply gloomier across the board, "
     "Greece would be extreme on both axes. It is extreme on financial hardship and much less "
     "so on general life satisfaction.", True),
]


def scatter(key, xk, yk, title, note, members_only=True):
    if xk not in SERIES or yk not in SERIES:
        PROBLEMS.append(f"scatter {key}: missing {xk if xk not in SERIES else yk}")
        return
    X, Y = SERIES[xk], SERIES[yk]
    pool = MEMBERS if members_only else sorted(set(X["countries"]) | set(Y["countries"]))
    # latest year where both series cover a decent number of the same countries
    best, best_n = None, 0
    for yr in sorted(set(X["years"]) & set(Y["years"]), reverse=True):
        xi, yi = X["years"].index(yr), Y["years"].index(yr)
        n = sum(1 for c in pool
                if c in X["countries"] and c in Y["countries"]
                and X["countries"][c][xi] is not None and Y["countries"][c][yi] is not None)
        if n > best_n:
            best, best_n = yr, n
        if n >= 20:
            best, best_n = yr, n
            break
    if best is None or best_n < 8:
        PROBLEMS.append(f"scatter {key}: too few overlapping countries")
        return
    xi, yi = X["years"].index(best), Y["years"].index(best)
    pts = []
    for c in pool:
        if c not in X["countries"] or c not in Y["countries"]:
            continue
        xv, yv = X["countries"][c][xi], Y["countries"][c][yi]
        if xv is None or yv is None:
            continue
        pts.append(dict(geo=c, x=xv, y=yv))
    if len(pts) < 8:
        PROBLEMS.append(f"scatter {key}: too few points")
        return
    xs_ = np.array([p["x"] for p in pts]); ys_ = np.array([p["y"] for p in pts])
    r = float(np.corrcoef(xs_, ys_)[0, 1]) if len(pts) > 2 else None
    SCATTERS[key] = dict(
        title=title, note=note, year=int(best),
        x_label=X["label"], y_label=Y["label"], x_unit=X["unit"], y_unit=Y["unit"],
        eu_x=X["eu"][xi], eu_y=Y["eu"][yi],
        eu_basis_x=X["eu_basis"], eu_basis_y=Y["eu_basis"],
        r=None if r is None else round(r, 2), points=pts)
    print(f"  {key:28} {best}  n={len(pts):2}  r={r:+.2f}")


for spec in SCATTER_SPECS:
    scatter(*spec)

json.dump({"series": SERIES, "panels": PANELS, "scatters": SCATTERS, "problems": PROBLEMS},
          open(OUT / "appendix_series_core.json", "w"))
print(f"\n{len(SERIES)} series + {len(PANELS)} panels + {len(SCATTERS)} scatters")
if PROBLEMS:
    print("Problems:")
    for p in PROBLEMS:
        print("  -", p)
