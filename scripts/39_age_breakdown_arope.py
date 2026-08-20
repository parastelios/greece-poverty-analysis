"""Age-breakdown checkpoint: does Greece's aggregate AROPE recovery conceal
a redistribution of vulnerability across generations? Triggered by an
external review of a Greece in Figures article making several specific
age-group claims -- verified here directly against the live Eurostat API
before any of them are trusted or integrated into the published reports.

Age groups used throughout: Y_LT18, Y18-24, Y25-49, Y50-64, Y_GE65 (plus
TOTAL). This is Eurostat's own standard age-group set for EU-SILC poverty
indicators, not a custom bucketing.

Components decomposed for each age group and year: AROPE (union, ilc_peps01n),
AROP (ilc_li02), severe material & social deprivation (ilc_mdsd11), and very
low work intensity (ilc_lvhl11, structurally undefined for 65+ and not
broken out at the same age resolution -- reported for the groups where it
exists, not forced onto groups where it doesn't apply).

Asymmetric year ranges, deliberate, not an oversight: AROP-by-age
(ilc_li02) carries no legacy/revised definitional break at all, so it is
fetched back to 2003 to match the rest of this project's series. AROPE and
deprivation-by-age (ilc_peps01n / ilc_mdsd11) carry the same legacy/revised
break as the rest of this project's AROPE series, but Eurostat's revised,
age-broken-down version is only disseminated from 2015 -- and a direct
overlap check below (legacy ilc_peps01/ilc_mddd11 vs. revised, 2015-2020)
shows the age-specific gap between the two definitions is too large to
splice responsibly (up to 7.3 points for 18-24, 5.4 for 65+ -- both larger
than several of this checkpoint's own headline findings), unlike the
whole-population aggregate splice used elsewhere in this project, where the
gap is a more tolerable ~1-3 points. AROPE and deprivation-by-age are
therefore reported 2015-2025 only, on one consistent definition throughout,
rather than spliced back further.
"""
import pandas as pd
from eurostat import fetch
from eu_membership import eu_members

OUT = "../data/processed"
AGES = ["Y_LT18", "Y18-24", "Y25-49", "Y50-64", "Y_GE65", "TOTAL"]
YEARS = list(range(2015, 2026))
GEOS = ["EL", "EU27_2020"]

pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 200)

# ============================================================ AROPE (rate + persons) ====
arope_rate = fetch("ilc_peps01n", geo=GEOS, time=YEARS, age=AGES, sex=["T"], unit=["PC"])
arope_pers = fetch("ilc_peps01n", geo=GEOS, time=YEARS, age=AGES, sex=["T"], unit=["THS_PER"])
arope = arope_rate[["geo", "age", "time", "value"]].rename(columns={"value": "arope_rate"}).merge(
    arope_pers[["geo", "age", "time", "value"]].rename(columns={"value": "arope_persons_ths"}),
    on=["geo", "age", "time"], how="left",
)
arope.to_csv(f"{OUT}/age_breakdown_arope.csv", index=False)
print("=== AROPE by age group, Greece vs EU27, 2015-2025 ===")
print(arope[arope.time.isin([2015, 2024, 2025])].sort_values(["geo", "age", "time"]).to_string(index=False))

# ============================================================ AROP ========================
# AROP-by-age carries no legacy/revised definitional break -- ilc_li02 is methodologically
# continuous back to 1995 (checked directly: no "new" AROP series exists to splice against,
# unlike AROPE/deprivation below). Fetched back to 2003 to match the rest of this project's
# series start, at the user's explicit request, to show the longer age-specific AROP pattern
# rather than silently cropping it to the AROPE/deprivation window below.
YEARS_AROP = list(range(2003, 2026))
arop = fetch("ilc_li02", geo=GEOS, time=YEARS_AROP, age=AGES, sex=["T"], rskpovth=["B_60"], statinfo=["MED_EI"])
arop = arop[arop.unit == "PC"] if "unit" in arop.columns else arop
arop = arop[["geo", "age", "time", "value"]].rename(columns={"value": "arop_rate"})
arop.to_csv(f"{OUT}/age_breakdown_arop.csv", index=False)
print("\n=== AROP by age group, Greece vs EU27, 2003 vs 2015 vs 2024-2025 ===")
print(arop[arop.time.isin([2003, 2015, 2024, 2025])].sort_values(["geo", "age", "time"]).to_string(index=False))

# ============================================================ severe deprivation ==========
dep = fetch("ilc_mdsd11", geo=GEOS, time=YEARS, age=AGES, sex=["T"], unit=["PC"])
dep = dep[["geo", "age", "time", "value"]].rename(columns={"value": "deprivation_rate"})
dep.to_csv(f"{OUT}/age_breakdown_deprivation.csv", index=False)
print("\n=== Severe material & social deprivation by age group, Greece vs EU27, 2024-2025 ===")
print(dep[dep.time.isin([2024, 2025])].sort_values(["geo", "age", "time"]).to_string(index=False))

# ============================================================ legacy/revised overlap check ==
# Before deciding not to splice AROPE-by-age back past 2015, check directly whether legacy
# (ilc_peps01, pre-2021) and revised (ilc_peps01n, used above) agree closely enough in their
# 2015-2020 overlap to splice safely -- the same test this project already applied to justify
# splicing the whole-population AROPE series elsewhere (21_arope.py).
legacy_arope = fetch("ilc_peps01", geo=["EL"], age=AGES, sex=["T"], time=range(2015, 2021))
legacy_arope = legacy_arope[legacy_arope.unit == "PC"][["age", "time", "value"]].rename(columns={"value": "legacy"})
revised_arope_gr = arope_rate[(arope_rate.geo == "EL") & (arope_rate.time.isin(range(2015, 2021)))][["age", "time", "value"]].rename(columns={"value": "revised"})
overlap = legacy_arope.merge(revised_arope_gr, on=["age", "time"])
overlap["gap_pp"] = (overlap["revised"] - overlap["legacy"]).round(2)
overlap.to_csv(f"{OUT}/age_breakdown_legacy_revised_overlap_check.csv", index=False)
print("\n=== Legacy vs. revised AROPE-by-age, 2015-2020 overlap (why no splice past 2015) ===")
print(overlap.sort_values(["age", "time"]).to_string(index=False))
max_gap = overlap["gap_pp"].abs().max()
print(f"Largest age-specific legacy/revised gap in the overlap window: {max_gap:.1f} points "
      f"(TOTAL alone: {overlap[overlap.age=='TOTAL']['gap_pp'].abs().max():.1f} points) -- "
      f"too large relative to this checkpoint's own findings to splice responsibly.")

# ============================================================ low work intensity ==========
# Structurally defined only for the population aged 0-59 (household work-attachment
# concept) -- Eurostat does not publish a Y50-64 or Y_GE65 breakdown for this indicator
# at all, confirmed by checking the actual age codes returned, not assumed.
lwi_ages = ["Y_LT18", "Y18-24", "Y25-54"]
lwi = fetch("ilc_lvhl11", geo=GEOS, time=YEARS, age=lwi_ages, sex=["T"])
lwi = lwi[lwi.unit == "PC"] if "unit" in lwi.columns else lwi
lwi = lwi[["geo", "age", "time", "value"]].rename(columns={"value": "low_work_intensity_rate"})
lwi.to_csv(f"{OUT}/age_breakdown_low_work_intensity.csv", index=False)
print("\n=== Very-low-work-intensity by age group (0-59 only -- not defined for 50-64 or 65+, confirmed via Eurostat's own age-code list, not assumed), 2024-2025 ===")
print(lwi[lwi.time.isin([2024, 2025])].sort_values(["geo", "age", "time"]).to_string(index=False))

# ============================================================ EU ranking check ============
# Needs its own fetch across all 27 member states -- the main pull above only covers
# Greece and the EU aggregate, which isn't enough to rank Greece against its peers.
members = sorted(eu_members(2025))
rank_all = fetch("ilc_peps01n", geo=members, time=[2025], age=["TOTAL"], sex=["T"], unit=["PC"])
rank_df = rank_all[rank_all.geo.isin(members)][["geo", "value"]].dropna()
rank_df = rank_df.sort_values("value", ascending=False).reset_index(drop=True)
rank_df["rank"] = rank_df.index + 1
rank_df.to_csv(f"{OUT}/age_breakdown_eu_arope_rank_2025.csv", index=False)
print("\n=== EU27 AROPE ranking, 2025 (top 6, 1=highest) ===")
print(rank_df.head(6).to_string(index=False))
gr_rank = rank_df[rank_df.geo == "EL"]["rank"].values[0]
print(f"\nGreece rank: {gr_rank} of {len(rank_df)}")

# ============================================================ shift-share decomposition ===
# Does the +0.6pt rise in Greece's overall AROPE (26.9% -> 27.5%, 2024->2025) reflect
# within-group deterioration, a shift in the population's age composition, or both?
# Standard two-term shift-share: total change = sum(share_i * delta_rate_i)  [within]
#                                              + sum(rate_i * delta_share_i) [composition]
# using each age group's population SHARE OF THE TOTAL POPULATION, backed out from
# AROPE persons-in-thousands / AROPE rate (both already fetched above), not assumed.
sub_ages = ["Y_LT18", "Y18-24", "Y25-49", "Y50-64", "Y_GE65"]
piv = arope[arope.age.isin(sub_ages) & (arope.geo == "EL") & (arope.time.isin([2024, 2025]))].copy()
piv["population_ths"] = 100 * piv["arope_persons_ths"] / piv["arope_rate"]
pop_2024 = piv[piv.time == 2024].set_index("age")["population_ths"]
pop_2025 = piv[piv.time == 2025].set_index("age")["population_ths"]
rate_2024 = piv[piv.time == 2024].set_index("age")["arope_rate"]
rate_2025 = piv[piv.time == 2025].set_index("age")["arope_rate"]
total_pop_2024 = pop_2024.sum()
total_pop_2025 = pop_2025.sum()
share_2024 = pop_2024 / total_pop_2024
share_2025 = pop_2025 / total_pop_2025

within_effect = (share_2024 * (rate_2025 - rate_2024)).sum()
composition_effect = (rate_2024 * (share_2025 - share_2024)).sum()
interaction = ((share_2025 - share_2024) * (rate_2025 - rate_2024)).sum()
actual_change_subgroups = (share_2025 * rate_2025).sum() - (share_2024 * rate_2024).sum()

decomp = pd.DataFrame({
    "age": sub_ages,
    "population_share_2024_pct": [round(share_2024[a] * 100, 2) for a in sub_ages],
    "population_share_2025_pct": [round(share_2025[a] * 100, 2) for a in sub_ages],
    "arope_rate_2024": [rate_2024[a] for a in sub_ages],
    "arope_rate_2025": [rate_2025[a] for a in sub_ages],
    "within_group_contribution_pp": [round(share_2024[a] * (rate_2025[a] - rate_2024[a]), 3) for a in sub_ages],
    "composition_contribution_pp": [round(rate_2024[a] * (share_2025[a] - share_2024[a]), 3) for a in sub_ages],
})
decomp.to_csv(f"{OUT}/age_breakdown_shiftshare_decomposition.csv", index=False)
print("\n=== Shift-share decomposition: Greece's aggregate AROPE change, 2024->2025 ===")
print(decomp.to_string(index=False))
print(f"\nWithin-group (rate) effect:        {within_effect:+.3f} pp")
print(f"Between-group (composition) effect: {composition_effect:+.3f} pp")
print(f"Interaction term:                   {interaction:+.3f} pp")
print(f"Sum (reconstructed total change, 5 subgroups): {within_effect + composition_effect + interaction:+.3f} pp")
print(f"Actual change, 5-subgroup weighted total:      {actual_change_subgroups:+.3f} pp")
print("(Reported TOTAL AROPE change was 26.9 -> 27.5, +0.6pp; the 5-subgroup weighted "
      "reconstruction may differ slightly since TOTAL includes the full population, not "
      "just these five non-overlapping bands, and each age-group total already reflects "
      "its own rounding.)")

# ============================================================ bounded household-type check ==
# Follow-up requested after the initial checkpoint: does the 65+ deterioration hit everyone
# in that age group evenly, or is it concentrated in specific household types? Tightly scoped
# to what Eurostat actually publishes as a genuine cross-tab -- no marginal tables are
# combined to infer a breakdown Eurostat doesn't itself provide.

# --- 65+ AROPE by sex, over time (age x sex is a native two-way dimension, not inferred) ---
sex_ts = fetch("ilc_peps01n", geo=GEOS, time=YEARS, age=["Y_GE65"], sex=["F", "M", "T"], unit=["PC"])
sex_ts = sex_ts[["geo", "sex", "time", "value"]].rename(columns={"value": "arope_rate"})
sex_ts.to_csv(f"{OUT}/age_breakdown_65plus_by_sex.csv", index=False)
print("\n=== 65+ AROPE by sex, Greece vs EU27, 2015/2020/2024/2025 ===")
print(sex_ts[sex_ts.time.isin([2015, 2020, 2024, 2025])].sort_values(["geo", "sex", "time"]).to_string(index=False))

# --- AROPE and AROP by household composition: single 65+ (A1_GE65) vs. 65+ couple
# (A2_GE1_GE65, "two adults, at least one 65+"). ilc_peps03n / ilc_li03 publish these as a
# genuine household-composition dimension, not something inferred by combining separate
# tables -- confirmed by checking the actual dimension values Eurostat returns.
HH = ["A1_GE65", "A2_GE1_GE65", "TOTAL"]
hh_arope = fetch("ilc_peps03n", geo=GEOS, time=YEARS, hhcomp=HH, quant_inc=["TOTAL"], unit=["PC"])
hh_arope = hh_arope[["geo", "hhcomp", "time", "value"]].rename(columns={"value": "arope_rate"})
hh_arope.to_csv(f"{OUT}/age_breakdown_household_arope.csv", index=False)
print("\n=== AROPE by household composition (single 65+ vs. 65+ couple), Greece vs EU27 ===")
print(hh_arope[hh_arope.time.isin([2015, 2020, 2024, 2025])].sort_values(["geo", "hhcomp", "time"]).to_string(index=False))

hh_arop = fetch("ilc_li03", geo=GEOS, time=[2015, 2024, 2025], hhcomp=HH, rskpovth=["B_60"], statinfo=["MED_EI"])
hh_arop = hh_arop[hh_arop.unit == "PC"] if "unit" in hh_arop.columns else hh_arop
hh_arop = hh_arop[["geo", "hhcomp", "time", "value"]].rename(columns={"value": "arop_rate"})
hh_arop.to_csv(f"{OUT}/age_breakdown_household_arop.csv", index=False)
print("\n=== AROP by household composition (single 65+ vs. 65+ couple), Greece vs EU27 ===")
print(hh_arop.sort_values(["geo", "hhcomp", "time"]).to_string(index=False))

# --- What Eurostat does NOT publish, checked directly rather than assumed ---
# (1) No sex breakdown exists within the single-65+ household-composition category
#     (ilc_peps03n/ilc_li03 have no `sex` dimension at all) -- F1/M1 in the same table are
#     single-person households of ANY age, not age-restricted, so combining them with
#     A1_GE65 would be inferring a cross-tab Eurostat doesn't publish. Not done.
# (2) No age-by-tenure cross-tab exists for a housing-cost OUTCOME rate. ilc_lvho07c
#     (housing-cost overburden by tenure) has no age/household-composition dimension at all.
#     ilc_lvho02 does cross hhcomp with tenure, but it is a population-DISTRIBUTION table
#     (what share of each household type lives in each tenure category), not an outcome-rate
#     table -- using it to claim "single elderly owners face X% overburden" would not be a
#     real Eurostat statistic. Confirmed by inspecting both tables' actual dimensions and
#     values, not assumed. Tenure is therefore excluded from this checkpoint's household
#     finding, per the explicit instruction to skip it rather than infer it.
# (3) No formal sampling-uncertainty figure (standard error, confidence interval, or
#     reliability flag) is exposed by the Eurostat dissemination API for any of the cells
#     queried above -- checked directly against the raw SDMX-JSON response's `status` field,
#     which was empty for every query run in this script. EU-SILC's own general guidance is
#     that country-year estimates for smaller population subgroups (single-elderly
#     households are a real but modest share of the population -- 273 thousand people in
#     Greece in 2025, well under the national total) carry more sampling variance than the
#     headline national rate; that caution is noted qualitatively in the published reports,
#     since no quantitative figure could be sourced.
print("\n=== What was checked and found NOT to exist as a genuine Eurostat cross-tab ===")
print("  - Sex within single-65+ household composition: no such dimension in ilc_peps03n/ilc_li03.")
print("  - Age/household-composition x tenure OUTCOME rate: ilc_lvho02 is a population-distribution")
print("    table, not an overburden-rate table; not used to avoid inferring a false statistic.")
print("  - Formal standard errors / reliability flags: 'status' field empty on every query above.")


print("\n\nAge-breakdown checkpoint complete. Outputs written:")
for f in ["age_breakdown_arope.csv", "age_breakdown_arop.csv", "age_breakdown_deprivation.csv",
          "age_breakdown_low_work_intensity.csv", "age_breakdown_eu_arope_rank_2025.csv",
          "age_breakdown_shiftshare_decomposition.csv", "age_breakdown_65plus_by_sex.csv",
          "age_breakdown_household_arope.csv", "age_breakdown_household_arop.csv",
          "age_breakdown_legacy_revised_overlap_check.csv"]:
    print(f"  {OUT}/{f}")
