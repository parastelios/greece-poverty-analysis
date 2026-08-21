"""Deep interrogation of the one near-miss from family B:
`years_worst_quintile_wage` -- cumulative years since 2008 spent in the EU's
bottom quintile on real wages indexed to each country's own 2008 = 100.

It cut Greece's out-of-sample gap from 3.86 to 1.41, the largest single-variable
improvement in either family, while failing significance (p=0.166, FDR 0.414).
Before treating that as promising, this script asks the questions that decide
whether it is new information or a re-expression of something already tested:

  1. Redundancy   -- how much of it is already in the wage family?
  2. Head-to-head -- put it in the model alongside the existing FDR survivor.
  3. Specificity  -- does it improve Greece only, or everyone (i.e. is it just
                     a better-fitting model)?
  4. Greece-out   -- does the coefficient survive dropping Greece entirely?
  5. The other reading -- rank on the wage LEVEL rather than on recovery, which
                     is the version that matches "low and staying low" literally.

Nothing here is confirmatory. The variable was chosen after seeing its result,
so every number below is post-selection and reported as such.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

from eurostat import fetch
from eu_membership import eu_members

OUT = "../data/processed"
MEMBERS = sorted(eu_members(2025))
V = "years_worst_quintile_wage"
SURVIVOR = "wage_years_below_2008"
vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]

panel = pd.read_csv(f"{OUT}/direction_persistence_panel.csv")


def run_model(extra, panel, outcome="subjective_poverty", drop_geo=None):
    vars_ = vars_c_ltu + extra
    d = panel.dropna(subset=vars_ + [outcome]).copy()
    if drop_geo:
        d = d[d.geo != drop_geo]
    f = f"{outcome} ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    rows = []
    for c in sorted(d.geo.unique()):
        tr, te = d[d.geo != c], d[d.geo == c].copy()
        mc = smf.ols(f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        rows.append({"geo": c, "resid": (te[outcome] - mc.predict(te)).mean()})
    loo = pd.DataFrame(rows)
    return m, d, loo


# ---------------------------------------------------------------- 1. redundancy ----
print("=" * 70)
print("1. REDUNDANCY: is this variable already in the wage family?")
print("=" * 70)
d = panel.dropna(subset=[V, SURVIVOR])
peers = ["cum_wage_shortfall_2008base", "wage_longest_streak_2008", SURVIVOR,
         "wage_years_below_peak", "cum_excess_unemployment"]
for c in peers:
    print(f"  corr({V}, {c:28}) = {d[V].corr(d[c]):+.3f}")
g = d[d.geo == "EL"]
print(f"\n  WITHIN GREECE ONLY, corr with {SURVIVOR} = {g[V].corr(g[SURVIVOR]):+.4f}")
print("  -> for the one country whose residual is the research question, the two")
print("     variables carry the same information; any difference in fit comes from")
print("     the other 26 countries, not from new evidence about Greece.")

# ---------------------------------------------------------------- 2. head to head ----
print("\n" + "=" * 70)
print("2. HEAD-TO-HEAD against the existing FDR survivor")
print("=" * 70)
base_m, base_d, base_loo = run_model([], panel)
base_gr = base_loo.set_index("geo").loc["EL", "resid"]
print(f"  baseline Model C-LTU: Greek out-of-sample gap {base_gr:+.2f}")
for spec in ([V], [SURVIVOR], [V, SURVIVOR]):
    m, dd, loo = run_model(spec, panel)
    gr = loo.set_index("geo").loc["EL", "resid"]
    ps = "  ".join(f"{v}: b={m.params[v]:+.4f} p={m.pvalues[v]:.3f}" for v in spec)
    print(f"  {'+'.join(spec):55} gap {gr:+.2f}   {ps}")
X = base_d[vars_c_ltu + [V, SURVIVOR]].dropna()
vifs = {c: variance_inflation_factor(X.values, i) for i, c in enumerate(X.columns)}
print(f"\n  VIF when both are in: {V}={vifs[V]:.1f}, {SURVIVOR}={vifs[SURVIVOR]:.1f}")

# ---------------------------------------------------------------- 3. specificity ----
print("\n" + "=" * 70)
print("3. SPECIFICITY: does it improve Greece, or every country?")
print("=" * 70)
m_v, d_v, loo_v = run_model([V], panel)
cmp = base_loo.merge(loo_v, on="geo", suffixes=("_base", "_with"))
cmp["improved"] = cmp.resid_with.abs() < cmp.resid_base.abs()
cmp["delta"] = cmp.resid_with.abs() - cmp.resid_base.abs()
print(f"  countries whose |gap| improves: {int(cmp.improved.sum())} of {len(cmp)}")
print("  five largest improvements:")
for r in cmp.nsmallest(5, "delta").itertuples():
    print(f"    {r.geo}: |{r.resid_base:+.2f}| -> |{r.resid_with:+.2f}|  ({r.delta:+.2f})")
gr_rank = int((cmp.delta < cmp[cmp.geo == 'EL'].delta.values[0]).sum()) + 1
print(f"  Greece's improvement ranks {gr_rank}/{len(cmp)} among all countries")

# ---------------------------------------------------------------- 4. Greece out ----
print("\n" + "=" * 70)
print("4. GREECE-EXCLUSION: does the coefficient survive without Greece?")
print("=" * 70)
m_all, _, _ = run_model([V], panel)
m_no, _, _ = run_model([V], panel, drop_geo="EL")
print(f"  all 27 countries : b={m_all.params[V]:+.4f}  p={m_all.pvalues[V]:.3f}")
print(f"  Greece excluded  : b={m_no.params[V]:+.4f}  p={m_no.pvalues[V]:.3f}")
print("  -> " + ("coefficient is carried by Greece" if m_no.pvalues[V] > 0.5
                 else "coefficient does not depend on Greece alone"))

# ---------------------------------------------------------------- 5. level version ----
print("\n" + "=" * 70)
print("5. THE OTHER READING: rank on the wage LEVEL, not on recovery")
print("=" * 70)
lv = fetch("nama_10_lp_ulc", time=range(2008, 2026),
           na_item=["D1_SAL_HW"], unit=["PPS_EU27_2020"])
lv = lv[lv.geo.isin(MEMBERS)][["geo", "time", "value"]].rename(
    columns={"value": "pay_lvl"}).dropna().sort_values(["geo", "time"])
lv["_w"] = (lv.groupby("time")["pay_lvl"].rank(pct=True) <= 0.20).astype(int)
lv["years_worst_quintile_paylevel"] = lv.groupby("geo")["_w"].cumsum()
LV = "years_worst_quintile_paylevel"
panel = panel.merge(lv[["geo", "time", LV]], on=["geo", "time"], how="left")
dd = panel.dropna(subset=[LV])
print(f"  corr with {V:28} = {dd[LV].corr(dd[V]):+.3f}")
print(f"  corr with {SURVIVOR:28} = {dd[LV].corr(dd[SURVIVOR]):+.3f}  <- essentially independent")
top = lv[lv.time == 2024].nlargest(7, LV)
print("  most years in the EU's bottom PAY-LEVEL quintile, 2024: "
      + ", ".join(f"{r.geo}:{int(getattr(r, LV))}" for r in top.itertuples()))
m_l, _, loo_l = run_model([LV], panel)
gr_l = loo_l.set_index("geo").loc["EL", "resid"]
print(f"  in the model: b={m_l.params[LV]:+.4f}  p={m_l.pvalues[LV]:.3f}  "
      f"Greek gap {base_gr:+.2f} -> {gr_l:+.2f}")

pd.DataFrame([{"variable": V, "corr_with_survivor_all": d[V].corr(d[SURVIVOR]),
               "corr_within_greece": g[V].corr(g[SURVIVOR]),
               "corr_with_cum_wage_shortfall": d[V].corr(d["cum_wage_shortfall_2008base"]),
               "p_all": m_all.pvalues[V], "p_greece_excluded": m_no.pvalues[V],
               "countries_improved": int(cmp.improved.sum()),
               "greece_improvement_rank": gr_rank,
               "paylevel_p": m_l.pvalues[LV], "paylevel_greek_gap": gr_l}]
             ).to_csv(f"{OUT}/candidate_interrogation.csv", index=False)
print(f"\nWritten to {OUT}/candidate_interrogation.csv")
