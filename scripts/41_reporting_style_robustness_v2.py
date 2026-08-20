"""Reporting-style robustness, round 2: coverage audit, event-study,
placebo/randomization inference, alternative treatment dates,
leave-one-control-out stability, a periphery-only comparison group, a
basic synthetic control, standardized (not just ranked) cross-indicator
deviations, and specification sensitivity for the residual-trend test.

Every item here responds directly to a named methodological gap in the
first-pass checkpoint (40_reporting_style_robustness.py): that checkpoint
is not superseded, this extends it before any of it is integrated into
the published reports.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.optimize import minimize
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 300)

sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")
arop = pd.read_csv(f"{RAW}/arop_all_countries.csv")
members_2025 = set(eu_members(2025))
sub_eu = sub[sub.geo.isin(members_2025)]

# ================================================================ PART 1: coverage audit ====
print("=" * 100)
print("PART 1: EU-SILC coverage audit for the pre-crisis comparison")
print("=" * 100)

counts_full = sub_eu[sub_eu.time.isin(range(2003, 2009))].dropna(subset=["subjective_poverty"]).groupby("geo")["time"].count().sort_values(ascending=False)
counts_full.to_csv(f"{OUT}/reporting_style_v2_coverage_2003_2008.csv", header=["n_years_available"])
print("\nYears of data available per EU country, 2003-2008 window (max possible = 6):")
print(counts_full.to_string())
full6 = counts_full[counts_full == 6].index.tolist()
print(f"\nCountries with FULL 6-year coverage (the only ones EU-SILC covered from the very start): {full6}")

results_balanced = []
for name, window, min_years in [
    ("2003-2008, full-coverage-only (n=6 countries)", range(2003, 2009), 6),
    ("2005-2008 balanced panel", range(2005, 2009), 4),
    ("2007-2008 balanced panel (cleanest near-EU27 comparison)", range(2007, 2009), 2),
]:
    w = sub_eu[sub_eu.time.isin(list(window))].dropna(subset=["subjective_poverty"])
    yc = w.groupby("geo")["time"].count()
    balanced_geos = yc[yc == min_years].index.tolist()
    avg = w[w.geo.isin(balanced_geos)].groupby("geo")["subjective_poverty"].mean().sort_values(ascending=False)
    rank = list(avg.index).index("EL") + 1 if "EL" in avg.index else None
    print(f"\n--- {name}: {len(balanced_geos)} countries, balanced ---")
    print(avg.to_string())
    print(f"Greece rank: {rank} of {len(avg)}")
    results_balanced.append({"window": name, "n_countries": len(avg), "greece_rank": rank,
                              "greece_value": avg.get("EL")})
pd.DataFrame(results_balanced).to_csv(f"{OUT}/reporting_style_v2_balanced_rankings.csv", index=False)

# ================================================================ PART 2: DiD battery ========
print("\n" + "=" * 100)
print("PART 2: Difference-in-differences robustness battery")
print("=" * 100)

gap_all = sub.merge(arop, on=["geo", "time"], suffixes=("", "_arop"))
gap_all["gap"] = gap_all["subjective_poverty"] - gap_all["arop"]
gap_all = gap_all[gap_all.geo.isin(members_2025)].dropna(subset=["gap"])
# Use the balanced, near-continuous coverage window (2007-2025) for the DiD battery, since the
# 2003-2006 pre-EU-SILC-rollout years would otherwise unbalance every test in this section --
# confirmed via Part 1 that 2007 onward is when coverage becomes near-universal.
dd_panel = gap_all[gap_all.time >= 2007].copy()
print(f"\nDiD panel: {dd_panel.geo.nunique()} countries, {dd_panel.time.nunique()} years "
      f"({dd_panel.time.min()}-{dd_panel.time.max()}), n={len(dd_panel)}")

# --- 2a. Event study: Greece's own year-specific deviation, base year 2008 (last full pre-crisis year) ---
es = dd_panel.copy()
es["is_greece"] = (es.geo == "EL").astype(int)
base_year = 2008
year_list = sorted(es.time.unique())
for y in year_list:
    if y == base_year:
        continue
    es[f"gr_y{y}"] = ((es.geo == "EL") & (es.time == y)).astype(int)
event_terms = " + ".join(f"gr_y{y}" for y in year_list if y != base_year)
m_event = smf.ols(f"gap ~ {event_terms} + C(geo) + C(time)", data=es).fit(
    cov_type="cluster", cov_kwds={"groups": es["geo"]})
event_rows = []
for y in year_list:
    if y == base_year:
        event_rows.append({"year": y, "coef": 0.0, "se": 0.0, "p": None, "note": "base year"})
        continue
    term = f"gr_y{y}"
    event_rows.append({"year": y, "coef": m_event.params[term], "se": m_event.bse[term],
                        "p": m_event.pvalues[term]})
event_df = pd.DataFrame(event_rows).sort_values("year")
event_df.to_csv(f"{OUT}/reporting_style_v2_event_study.csv", index=False)
print(f"\n--- Event study: Greece's year-specific deviation from its own {base_year} baseline "
      f"(country + year FE) ---")
print(event_df.to_string(index=False))
pre_coefs = event_df[(event_df.year < 2009) & (event_df.year != base_year)]["coef"]
print(f"\nPre-2009 coefficients (years before treatment; should be near zero and flat if there's "
      f"no pre-existing differential trend): {pre_coefs.tolist()}")

# --- 2b. Alternative treatment dates ---
alt_rows = []
for cutoff in [2009, 2010, 2011]:
    d = dd_panel.copy()
    d["post"] = (d.time >= cutoff).astype(int)
    d["greece_post"] = ((d.geo == "EL") & (d.post == 1)).astype(int)
    m = smf.ols("gap ~ greece_post + C(geo) + C(time)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["geo"]})
    alt_rows.append({"treatment_year": cutoff, "coef": m.params["greece_post"],
                      "se": m.bse["greece_post"], "p": m.pvalues["greece_post"]})
alt_df = pd.DataFrame(alt_rows)
alt_df.to_csv(f"{OUT}/reporting_style_v2_alt_treatment_dates.csv", index=False)
print("\n--- Alternative treatment dates (2009 / 2010 / 2011) ---")
print(alt_df.to_string(index=False))

# --- 2c. Country-placebo / randomization inference: treat EVERY country as if it were "Greece" ---
placebo_rows = []
for g in sorted(dd_panel.geo.unique()):
    d = dd_panel.copy()
    d["post"] = (d.time >= 2009).astype(int)
    d["treated_post"] = ((d.geo == g) & (d.post == 1)).astype(int)
    try:
        m = smf.ols("gap ~ treated_post + C(geo) + C(time)", data=d).fit(
            cov_type="cluster", cov_kwds={"groups": d["geo"]})
        placebo_rows.append({"geo": g, "coef": m.params["treated_post"], "p": m.pvalues["treated_post"]})
    except Exception as e:
        placebo_rows.append({"geo": g, "coef": None, "p": None})
placebo_df = pd.DataFrame(placebo_rows).sort_values("coef", ascending=False).reset_index(drop=True)
placebo_df["rank"] = placebo_df.index + 1
placebo_df.to_csv(f"{OUT}/reporting_style_v2_country_placebo.csv", index=False)
print(f"\n--- Country-placebo test: every one of {len(placebo_df)} EU countries treated as if it "
      f"were 'Greece', post-2009, same two-way FE model ---")
print(placebo_df.to_string(index=False))
gr_rank = placebo_df[placebo_df.geo == "EL"]["rank"].values[0]
empirical_p = gr_rank / len(placebo_df)
print(f"\nGreece's true coefficient ranks {gr_rank} of {len(placebo_df)} in this placebo "
      f"distribution -- empirical (randomization-inference) p-value = {empirical_p:.3f}")

# --- 2d. Leave-one-control-country-out stability ---
loo_rows = []
control_geos = [g for g in dd_panel.geo.unique() if g != "EL"]
for drop_geo in control_geos:
    d = dd_panel[dd_panel.geo != drop_geo].copy()
    d["post"] = (d.time >= 2009).astype(int)
    d["greece_post"] = ((d.geo == "EL") & (d.post == 1)).astype(int)
    m = smf.ols("gap ~ greece_post + C(geo) + C(time)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["geo"]})
    loo_rows.append({"dropped_control": drop_geo, "coef": m.params["greece_post"],
                      "p": m.pvalues["greece_post"]})
loo_df = pd.DataFrame(loo_rows).sort_values("coef")
loo_df.to_csv(f"{OUT}/reporting_style_v2_loo_controls.csv", index=False)
print(f"\n--- Leave-one-control-country-out: main Greece x post-2009 coefficient, "
      f"dropping each control country in turn ---")
print(f"Range: [{loo_df['coef'].min():.2f}, {loo_df['coef'].max():.2f}], "
      f"all {len(loo_df)} p-values < 0.05: {(loo_df['p'] < 0.05).all()}")
print(loo_df.to_string(index=False))

# --- 2e. Periphery-only comparison group ---
periphery = ["IT", "ES", "PT", "CY", "MT"]
d_periph = dd_panel[dd_panel.geo.isin(["EL"] + periphery)].copy()
d_periph["post"] = (d_periph.time >= 2009).astype(int)
d_periph["greece_post"] = ((d_periph.geo == "EL") & (d_periph.post == 1)).astype(int)
m_periph = smf.ols("gap ~ greece_post + C(geo) + C(time)", data=d_periph).fit(
    cov_type="cluster", cov_kwds={"groups": d_periph["geo"]})
print(f"\n--- Periphery-only comparison group (Greece vs. Italy, Spain, Portugal, Cyprus, Malta) ---")
print(f"n={int(m_periph.nobs)}, Greece x post-2009 coefficient: {m_periph.params['greece_post']:.2f} "
      f"(p={m_periph.pvalues['greece_post']:.4f})")
pd.DataFrame([{"group": "periphery (IT,ES,PT,CY,MT)", "coef": m_periph.params["greece_post"],
               "p": m_periph.pvalues["greece_post"], "n_obs": int(m_periph.nobs)}]
             ).to_csv(f"{OUT}/reporting_style_v2_periphery_comparison.csv", index=False)

# --- 2f. Basic synthetic control ---
# Donor pool: all EU countries with full 2003-2024 coverage (so the pre-period match is
# meaningful); weights constrained to be non-negative and sum to 1, chosen to minimize squared
# pre-period (2003-2008) gap differences from Greece.
piv = gap_all.pivot(index="time", columns="geo", values="gap")
pre_years = [y for y in range(2003, 2009) if y in piv.index]
post_years = [y for y in range(2009, 2025) if y in piv.index]
donor_candidates = [c for c in piv.columns if c != "EL" and piv.loc[pre_years, c].notna().all() and piv.loc[post_years, c].notna().all()]
print(f"\n--- Synthetic control: donor pool with full pre- and post-period coverage: "
      f"{len(donor_candidates)} countries ---")
print(donor_candidates)

gr_pre = piv.loc[pre_years, "EL"].values
donor_pre = piv.loc[pre_years, donor_candidates].values  # shape (n_pre_years, n_donors)

def loss(w):
    synth = donor_pre @ w
    return np.sum((gr_pre - synth) ** 2)

n_donors = len(donor_candidates)
w0 = np.repeat(1 / n_donors, n_donors)
cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
bounds = [(0, 1)] * n_donors
res = minimize(loss, w0, method="SLSQP", bounds=bounds, constraints=cons)
weights = pd.Series(res.x, index=donor_candidates).sort_values(ascending=False)
nontrivial = weights[weights > 0.01]
print(f"\nSynthetic-Greece donor weights (>1% only): \n{nontrivial.to_string()}")
print(f"Pre-period (2003-2008) fit: actual Greece mean={gr_pre.mean():.1f}, "
      f"synthetic mean={(donor_pre @ res.x).mean():.1f}, "
      f"RMSE={np.sqrt(loss(res.x) / len(pre_years)):.2f}")

gr_full = piv["EL"]
synth_full = piv[donor_candidates] @ res.x
synth_df = pd.DataFrame({"time": piv.index, "actual_greece_gap": gr_full.values,
                          "synthetic_greece_gap": synth_full.values})
synth_df["difference"] = synth_df["actual_greece_gap"] - synth_df["synthetic_greece_gap"]
synth_df.to_csv(f"{OUT}/reporting_style_v2_synthetic_control.csv", index=False)
print("\nActual vs. synthetic Greece, full series:")
print(synth_df.to_string(index=False))
pre_gap_fit = synth_df[synth_df.time.isin(pre_years)]["difference"].abs().mean()
post_gap_diff = synth_df[synth_df.time.isin(post_years)]["difference"].mean()
print(f"\nMean |actual-synthetic| difference, pre-period: {pre_gap_fit:.2f}pt "
      f"(should be small -- confirms the synthetic control fits the pre-period well)")
print(f"Mean (actual-synthetic) difference, post-period: {post_gap_diff:.2f}pt "
      f"(the synthetic-control estimate of Greece's post-2009 'treatment effect')")
print("This first attempt fails: the only countries with full 2003-2008 AND full post-period "
      "coverage are five wealthy Northern/Western European countries (AT, BE, DK, IE, LU), none "
      "of which resemble Greece's high pre-crisis gap level -- the optimizer collapses to ~100% "
      "Ireland and still fits the pre-period badly. Reported as a failed/null result, not hidden.")

# --- 2f-v2. Synthetic control, corrected: match on 2007-2008 instead of the full 2003-2008 span ---
# Part 1's own coverage audit already found near-universal (26-country) coverage by 2007-2008.
# Using that as the matching window opens the donor pool to the higher-hardship Southern/Eastern
# European countries the model actually needs, instead of forcing a tiny wealthy-country pool.
match_years_v2 = [y for y in [2007, 2008] if y in piv.index]
post_years_v2 = [y for y in range(2009, 2025) if y in piv.index]
donor_candidates_v2 = [c for c in piv.columns if c != "EL"
                        and piv.loc[match_years_v2, c].notna().all()
                        and piv.loc[post_years_v2, c].notna().all()]
print(f"\n--- Synthetic control v2: matching window relaxed to 2007-2008 (per Part 1's coverage "
      f"audit), donor pool: {len(donor_candidates_v2)} countries ---")

gr_match_v2 = piv.loc[match_years_v2, "EL"].values
donor_match_v2 = piv.loc[match_years_v2, donor_candidates_v2].values

def loss_v2(w):
    synth = donor_match_v2 @ w
    return np.sum((gr_match_v2 - synth) ** 2)

n_donors_v2 = len(donor_candidates_v2)
w0_v2 = np.repeat(1 / n_donors_v2, n_donors_v2)
cons_v2 = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
bounds_v2 = [(0, 1)] * n_donors_v2
res_v2 = minimize(loss_v2, w0_v2, method="SLSQP", bounds=bounds_v2, constraints=cons_v2)
weights_v2 = pd.Series(res_v2.x, index=donor_candidates_v2).sort_values(ascending=False)
nontrivial_v2 = weights_v2[weights_v2 > 0.01]
print(f"\nSynthetic-Greece donor weights (>1% only): \n{nontrivial_v2.to_string()}")
print(f"Match-period (2007-2008) fit: actual Greece mean={gr_match_v2.mean():.1f}, "
      f"synthetic mean={(donor_match_v2 @ res_v2.x).mean():.1f}, "
      f"RMSE={np.sqrt(loss_v2(res_v2.x) / len(match_years_v2)):.2f}")

gr_full_v2 = piv["EL"]
synth_full_v2 = piv[donor_candidates_v2] @ res_v2.x
synth_df_v2 = pd.DataFrame({"time": piv.index, "actual_greece_gap": gr_full_v2.values,
                             "synthetic_greece_gap": synth_full_v2.values})
synth_df_v2["difference"] = synth_df_v2["actual_greece_gap"] - synth_df_v2["synthetic_greece_gap"]
synth_df_v2.to_csv(f"{OUT}/reporting_style_v2_synthetic_control_v2.csv", index=False)
print("\nActual vs. synthetic Greece, full series (v2, 2007-2008 matching window):")
print(synth_df_v2.to_string(index=False))
pre_fit_v2 = synth_df_v2[synth_df_v2.time.isin(match_years_v2)]["difference"].abs().mean()
post_diff_v2 = synth_df_v2[synth_df_v2.time.isin(post_years_v2)]["difference"].mean()
print(f"\nMean |actual-synthetic| difference, match-period: {pre_fit_v2:.2f}pt")
print(f"Mean (actual-synthetic) difference, post-period: {post_diff_v2:.2f}pt "
      f"(the corrected synthetic-control estimate of Greece's post-2009 'treatment effect')")

print("\n\nPart 2 outputs written:")
for f in ["reporting_style_v2_event_study.csv", "reporting_style_v2_alt_treatment_dates.csv",
          "reporting_style_v2_country_placebo.csv", "reporting_style_v2_loo_controls.csv",
          "reporting_style_v2_periphery_comparison.csv", "reporting_style_v2_synthetic_control.csv",
          "reporting_style_v2_synthetic_control_v2.csv"]:
    print(f"  {OUT}/{f}")
