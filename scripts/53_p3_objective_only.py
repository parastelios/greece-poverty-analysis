"""P3: the objective-only model. The v3 publication gate.

Pre-committed in docs/archive/pre-v2-publication/project_description_v3.md §5. Nothing here is chosen after
seeing a result: the formula, the sample, the fixed effects, the weighting, the
missing-data rule, the inference method, the decision that LTU and cumulative
unemployment enter TOGETHER, and the four conclusion branches were all fixed in
advance.

Excluded by construction (Tier 0, proximate to the outcome): arrears, inability
to meet an unexpected expense, financial expectations.

Outcome: the backward-extended official subjective-hardship indicator
(scripts/outcome.py). Within the 2015-2024 window this is ilc_sbjp01 throughout.
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.path.insert(0, ".")
from outcome import official_hardship

OUT = "../data/processed"
YEARS = range(2015, 2025)
OBJECTIVE = ["severe_mat_soc_deprivation", "housing_cost_overburden", "ltu_rate",
             "aic_pps_pc_k", "wage_years_below_2008", "cum_excess_unemployment"]
CLTU = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
        "housing_cost_overburden", "arrears", "unexpected_expenses"]

p = pd.read_csv(f"{OUT}/persistence_share_panel.csv")
off = official_hardship().rename(columns={"value": "hardship"})[["geo", "time", "hardship"]]
p = p.merge(off, on=["geo", "time"], how="left")
p = p[p.time.isin(YEARS)]


def loo(vars_, panel, outcome="hardship"):
    d = panel.dropna(subset=vars_ + [outcome]).copy()      # complete cases, no imputation
    f = f"{outcome} ~ " + " + ".join(vars_) + " + C(time)"  # year FE only, unweighted
    m = smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    rows = []
    for c in sorted(d.geo.unique()):
        tr, te = d[d.geo != c], d[d.geo == c].copy()
        mc = smf.ols(f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        rows.append({"geo": c, "resid": (te[outcome] - mc.predict(te)).mean()})
    l = pd.DataFrame(rows).sort_values("resid", ascending=False).reset_index(drop=True)
    l["rank"] = l.index + 1
    g = l[l.geo == "EL"].iloc[0]
    return m, d, l, float(g["resid"]), int(g["rank"])


print("=" * 74); print("P3 OBJECTIVE-ONLY MODEL"); print("=" * 74)
m, d, l, gap, rank = loo(OBJECTIVE, p)
print(f"  n = {len(d)} country-years, {d.geo.nunique()} countries, "
      f"{int(d.time.min())}-{int(d.time.max())}")
print(f"  R2 = {m.rsquared:.3f}")
print(f"  Greece out-of-sample residual = {gap:+.2f} pp, rank {rank}/{len(l)}\n")

print("  coefficients (cluster-robust by country):")
for v in OBJECTIVE:
    print(f"    {v:28} {m.params[v]:+9.4f}  se {m.bse[v]:7.4f}  p {m.pvalues[v]:.4f}")

# ---- wild cluster bootstrap, the pre-declared inference ----
print("\n  wild cluster bootstrap (Rademacher, 1999 reps), pre-declared inference:")
rng = np.random.default_rng(20250821)
f = "hardship ~ " + " + ".join(OBJECTIVE) + " + C(time)"
geos = d.geo.unique()
for v in ["cum_excess_unemployment", "ltu_rate"]:
    # The null must be IMPOSED: fit the RESTRICTED model without v, resample its
    # residuals, and refit the unrestricted model on each bootstrap outcome.
    # An earlier version used unrestricted residuals and fitted values, which
    # does not impose H0 and returned p=0.82 against t=9.69 -- nonsense.
    restricted = [x for x in OBJECTIVE if x != v]
    f_r = "hardship ~ " + " + ".join(restricted) + " + C(time)"
    m_r = smf.ols(f_r, data=d).fit()
    fitted_null, resid_null = m_r.predict(d), d["hardship"] - m_r.predict(d)
    t_obs = m.params[v] / m.bse[v]
    ts = []
    for _ in range(1999):
        w = pd.Series(rng.choice([-1.0, 1.0], size=len(geos)), index=geos)
        db = d.copy()
        db["hardship"] = fitted_null + resid_null.values * d.geo.map(w).values
        mb = smf.ols(f, data=db).fit(cov_type="cluster", cov_kwds={"groups": db["geo"]})
        ts.append(abs(mb.params[v] / mb.bse[v]))
    pboot = float((np.sum(np.array(ts) >= abs(t_obs)) + 1) / (len(ts) + 1))
    print(f"    {v:28} t={t_obs:+6.2f}  bootstrap p = {pboot:.4f}")

# ---- VIF, both key variables in together ----
print("\n  VIF (LTU and cumulative unemployment enter together, as pre-committed):")
X = d[OBJECTIVE].astype(float)
for i, c in enumerate(X.columns):
    print(f"    {c:28} {variance_inflation_factor(X.values, i):6.2f}")

# ---- comparisons ----
print("\n" + "=" * 74); print("COMPARISONS"); print("=" * 74)
_, _, _, g_cltu, r_cltu = loo(CLTU, p)
_, _, _, g_noacc, r_noacc = loo([v for v in OBJECTIVE if v != "cum_excess_unemployment"], p)
print(f"  Model C-LTU (includes Tier 0 predictors) : {g_cltu:+6.2f} pp, rank {r_cltu}/27")
print(f"  objective-only WITHOUT accumulation      : {g_noacc:+6.2f} pp, rank {r_noacc}/27")
print(f"  objective-only WITH accumulation         : {gap:+6.2f} pp, rank {rank}/27")

# ---- LOO coefficient stability ----
coefs = []
for c in sorted(d.geo.unique()):
    tr = d[d.geo != c]
    mc = smf.ols(f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
    coefs.append(mc.params["cum_excess_unemployment"])
coefs = np.array(coefs)
print(f"\n  cum_excess_unemployment across 27 LOO folds: "
      f"{coefs.min():+.4f} to {coefs.max():+.4f}, sign stable = {bool((np.sign(coefs)==np.sign(coefs[0])).all())}")

# ---- prediction interval for Greece ----
el = d[d.geo == "EL"]
tr = d[d.geo != "EL"]
mc = smf.ols(f, data=tr).fit()
pred = mc.get_prediction(el).summary_frame(alpha=0.05)
print(f"  Greece mean predicted {pred['mean'].mean():.1f} vs actual "
      f"{el['hardship'].mean():.1f}; 95% obs interval "
      f"[{pred['obs_ci_lower'].mean():.1f}, {pred['obs_ci_upper'].mean():.1f}]")

# ---- the four pre-committed branches ----
print("\n" + "=" * 74); print("PRE-COMMITTED CONCLUSION BRANCH"); print("=" * 74)
from branch_rule import decide, BRANCHES
sign_stable = bool((np.sign(coefs) == np.sign(coefs[0])).all())
extreme = rank <= 3

# The rule now lives in branch_rule.decide(), covered by test_branch_rule.py --
# 17 tests including boundary values and an exhaustive sweep proving no path
# returns branch 1 unearned. Prose pre-registration did not prevent the first
# run reporting branch 1 at rank 3; a tested function does.
bnum, disagree = decide(gap, rank, len(l), sign_stable)
branch = f"{bnum} - {BRANCHES[bnum]}"
if disagree:
    print("  CRITERIA DISAGREE: residual clears the branch-1 bar (<=10) but Greece")
    print("  remains in the extreme-outlier group (rank <=3). Branch 1 requires both.")
    print("  Taking the more conservative branch, as pre-committed.\n")
print(f"  residual {gap:+.2f} | rank {rank}/27 | extreme-outlier group = {extreme} | sign stable = {sign_stable}")
print(f"  -> BRANCH {branch}")

pd.DataFrame([{"gap": gap, "rank": rank, "r2": m.rsquared, "n": len(d),
               "gap_cltu": g_cltu, "gap_no_accumulation": g_noacc,
               "coef_min": coefs.min(), "coef_max": coefs.max(), "branch": branch}]
             ).to_csv(f"{OUT}/p3_objective_only.csv", index=False)
l.to_csv(f"{OUT}/p3_residuals.csv", index=False)
print(f"\nWritten to {OUT}/p3_*.csv")
