"""Reporting-style / cultural-premium robustness checkpoint.

The obvious critique of this project's whole argument: if Greece already
reported the highest subjective poverty in the EU before the 2010 crisis
even began, maybe part of the gap is a stable feature of how Greek
respondents answer "can you make ends meet" -- reporting norms, cultural
pessimism, or a general response-style effect -- rather than something
material-conditions can explain.

Six tests, matching the reviewer's own list, run directly rather than
argued from priors:
  1. Greece's pre-crisis (2003-2008) subjective-poverty level vs EU peers.
  2. Raw AROP-gap widening, pre-crisis vs current: did Greece's gap get
     bigger after 2009 by more than other countries' gaps did?
  3. A formal difference-in-differences regression: country + year fixed
     effects, plus a Greece x post-2009 interaction term.
  4. Out-of-sample residual stability for the standard material-conditions
     model (C-LTU, no cumulative-exposure term): is Greece's unexplained
     gap roughly CONSTANT year to year (consistent with a stable premium)
     or does it move with conditions (inconsistent with a pure premium)?
  5. Cross-indicator comparison: is Greece equally extreme on general life
     satisfaction as on financial hardship specifically, or is the
     extremity targeted at financial/material self-assessment?
  6. Institutional trust: reaffirmed, not re-tested -- Eurostat's holdings
     are one single year (2013), already documented elsewhere in this
     project as insufficient for any panel or before/after comparison.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 200)

sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")
arop = pd.read_csv(f"{RAW}/arop_all_countries.csv")
members_2025 = set(eu_members(2025))

# ============================================================ 1. pre-crisis level ==========
PRE = list(range(2003, 2009))
pre_sub = sub[(sub.time.isin(PRE)) & (sub.geo.isin(members_2025))].dropna(subset=["subjective_poverty"])
pre_avg = pre_sub.groupby("geo")["subjective_poverty"].mean().sort_values(ascending=False)
pre_avg.to_csv(f"{OUT}/reporting_style_precrisis_level.csv", header=["avg_subjective_poverty_2003_2008"])
print("=== Pre-crisis (2003-2008) average subjective poverty, EU countries with data, ranked ===")
print(pre_avg.to_string())
gr_pre_rank = (pre_avg.index == "EL").tolist().index(True) + 1 if "EL" in pre_avg.index else None
print(f"\nGreece pre-crisis rank: {gr_pre_rank} of {len(pre_avg)} (n countries with 2003-2008 coverage)")

# ============================================================ 2. raw AROP-gap widening =====
gap_all = sub.merge(arop, on=["geo", "time"], suffixes=("", "_arop"))
gap_all["gap"] = gap_all["subjective_poverty"] - gap_all["arop"]
gap_all = gap_all[gap_all.geo.isin(members_2025)]

PRE_W, POST_W = list(range(2003, 2009)), list(range(2019, 2025))
pre_gap = gap_all[gap_all.time.isin(PRE_W)].groupby("geo")["gap"].mean()
post_gap = gap_all[gap_all.time.isin(POST_W)].groupby("geo")["gap"].mean()
widen = pd.DataFrame({"pre_gap_2003_2008": pre_gap, "post_gap_2019_2024": post_gap}).dropna()
widen["widening"] = widen["post_gap_2019_2024"] - widen["pre_gap_2003_2008"]
widen = widen.sort_values("widening", ascending=False)
widen.to_csv(f"{OUT}/reporting_style_gap_widening.csv")
print("\n\n=== Raw subjective-minus-AROP gap: pre-crisis vs current, and the widening, ranked ===")
print(widen.to_string())
gr_widen_rank = list(widen.index).index("EL") + 1 if "EL" in widen.index else None
print(f"\nGreece's gap-widening rank: {gr_widen_rank} of {len(widen)}")
print(f"Greece: {widen.loc['EL', 'pre_gap_2003_2008']:.1f}pt (2003-08) -> "
      f"{widen.loc['EL', 'post_gap_2019_2024']:.1f}pt (2019-24), "
      f"widened by {widen.loc['EL', 'widening']:.1f}pt")
print(f"Median widening, all other EU countries: {widen.drop('EL')['widening'].median():.1f}pt")

# ============================================================ 3. formal diff-in-differences =
dd = gap_all.dropna(subset=["gap"]).copy()
dd["post"] = (dd.time >= 2009).astype(int)
dd["greece"] = (dd.geo == "EL").astype(int)
dd["greece_post"] = dd["greece"] * dd["post"]
# Two-way FE: country + year, plus the Greece x post interaction. Country FE absorbs Greece's
# own pre-existing baseline entirely; year FE absorbs common EU-wide shocks; the interaction
# term is what's left -- Greece's OWN incremental shift after 2009, beyond its own baseline
# and beyond the common EU-wide year effect.
m_dd = smf.ols("gap ~ greece_post + C(geo) + C(time)", data=dd).fit(
    cov_type="cluster", cov_kwds={"groups": dd["geo"]})
print("\n\n=== Difference-in-differences: Greece x post-2009, country + year fixed effects ===")
print(f"n={int(m_dd.nobs)}, countries={dd.geo.nunique()}, years={dd.time.nunique()}")
print(f"Greece x post-2009 coefficient: {m_dd.params['greece_post']:.2f} points "
      f"(p={m_dd.pvalues['greece_post']:.4f})")
print("(This is Greece's own incremental shift in the subjective-minus-AROP gap after 2009, "
      "net of its own pre-existing baseline (country FE) and the common EU-wide year effect "
      "(year FE). A single treated unit against many controls -- clustering by country is the "
      "project's standard convention but is a real limitation with only one treated country, "
      "noted explicitly in the writeup.)")
pd.DataFrame([{
    "term": "greece_post", "coef": m_dd.params["greece_post"], "se": m_dd.bse["greece_post"],
    "p": m_dd.pvalues["greece_post"], "n_obs": int(m_dd.nobs), "n_countries": dd.geo.nunique(),
}]).to_csv(f"{OUT}/reporting_style_diff_in_diff.csv", index=False)

# ============================================================ 4. OOS residual stability =====
# Model C-LTU alone (current-year material conditions only, no cumulative-exposure term) --
# deliberately the model a pure "stable cultural premium" story would need to survive, since
# adding the cumulative mechanism already explains most of the gap for a different reason.
panel = pd.read_csv(f"{OUT}/panel_extended.csv")
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")[["geo", "time", "ltu_rate"]]
panel = panel.merge(ltu, on=["geo", "time"], how="left")
vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]
d = panel.dropna(subset=vars_c_ltu + ["subjective_poverty"]).copy()
formula = "subjective_poverty ~ " + " + ".join(vars_c_ltu) + " + C(time)"
train = d[d.geo != "EL"]
test = d[d.geo == "EL"].copy()
m_stab = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
test["predicted"] = m_stab.predict(test)
test["residual"] = test["subjective_poverty"] - test["predicted"]
yby = test[["time", "subjective_poverty", "predicted", "residual"]].sort_values("time")
yby.to_csv(f"{OUT}/reporting_style_cltu_year_by_year.csv", index=False)
print("\n\n=== Model C-LTU (current-conditions only) out-of-sample residual, Greece, year by year ===")
print(yby.to_string(index=False))
resid_mean, resid_std = yby["residual"].mean(), yby["residual"].std()
resid_trend = np.polyfit(yby["time"], yby["residual"], 1)[0]
print(f"\nMean residual: {resid_mean:.2f}pt, std dev: {resid_std:.2f}pt, "
      f"linear trend: {resid_trend:+.2f}pt/year")
print("(A pure stable reporting premium would predict a roughly constant residual across years, "
      "not a large standard deviation relative to the mean, and not a systematic trend.)")

# ============================================================ 5. cross-indicator comparison =
life_sat = fetch("ilc_pw01", geo=list(members_2025) + ["EU27_2020"], sex=["T"], age=["Y_GE16"],
                  isced11=["TOTAL"], unit=["RTG"])
life_sat = life_sat[["geo", "time", "value"]].rename(columns={"value": "life_satisfaction"})
life_sat.to_csv(f"{OUT}/reporting_style_life_satisfaction.csv", index=False)

fin_exp = pd.read_csv(f"{RAW}/panel_financial_expectations.csv").rename(columns={"year": "time"})

common_years = sorted(set(life_sat.time.unique()) & set(fin_exp.time.unique()) & set(sub.time.unique()))
print(f"\n\n=== Cross-indicator comparison: is Greece extreme on ALL self-report measures, "
      f"or specifically on financial hardship? Common years: {common_years} ===")
rows = []
for y in common_years:
    ls_y = life_sat[(life_sat.time == y) & (life_sat.geo.isin(members_2025))].dropna(subset=["life_satisfaction"])
    fe_y = fin_exp[(fin_exp.time == y) & (fin_exp.geo.isin(members_2025))].dropna(subset=["fin_expectations"])
    sp_y = sub[(sub.time == y) & (sub.geo.isin(members_2025))].dropna(subset=["subjective_poverty"])
    if len(ls_y) < 5 or len(sp_y) < 5:
        continue
    # life satisfaction: LOWER = worse, so rank ascending puts the least-satisfied country 1st
    ls_rank = ls_y.sort_values("life_satisfaction").reset_index(drop=True)
    ls_rank["rank"] = ls_rank.index + 1
    sp_rank = sp_y.sort_values("subjective_poverty", ascending=False).reset_index(drop=True)
    sp_rank["rank"] = sp_rank.index + 1
    row = {"year": y, "n_life_sat": len(ls_y), "n_subj_poverty": len(sp_y)}
    if "EL" in ls_rank.geo.values:
        gr = ls_rank[ls_rank.geo == "EL"].iloc[0]
        row["gr_life_sat_value"] = gr["life_satisfaction"]
        row["gr_life_sat_rank_worst"] = int(gr["rank"])
    if "EL" in sp_rank.geo.values:
        gr = sp_rank[sp_rank.geo == "EL"].iloc[0]
        row["gr_subj_poverty_value"] = gr["subjective_poverty"]
        row["gr_subj_poverty_rank_worst"] = int(gr["rank"])
    if len(fe_y) >= 5 and "EL" in fe_y.geo.values:
        fe_rank = fe_y.sort_values("fin_expectations").reset_index(drop=True)  # more negative = more pessimistic
        fe_rank["rank"] = fe_rank.index + 1
        gr_fe = fe_rank[fe_rank.geo == "EL"].iloc[0]
        row["gr_fin_expectations_value"] = gr_fe["fin_expectations"]
        row["gr_fin_expectations_rank_worst"] = int(gr_fe["rank"])
        row["n_fin_exp"] = len(fe_y)
    rows.append(row)
cross_df = pd.DataFrame(rows)
cross_df.to_csv(f"{OUT}/reporting_style_cross_indicator.csv", index=False)
print(cross_df.to_string(index=False))

print("\n\n=== Institutional trust: not re-tested ===")
print("Eurostat's institutional-trust holdings (ilc_pw03b) remain a single year (2013), "
      "already documented elsewhere in this project as insufficient for any panel, "
      "before/after, or ranking-over-time comparison. Not re-tested here.")

print("\n\nReporting-style robustness checkpoint complete. Outputs written:")
for f in ["reporting_style_precrisis_level.csv", "reporting_style_gap_widening.csv",
          "reporting_style_diff_in_diff.csv", "reporting_style_cltu_year_by_year.csv",
          "reporting_style_life_satisfaction.csv", "reporting_style_cross_indicator.csv"]:
    print(f"  {OUT}/{f}")
