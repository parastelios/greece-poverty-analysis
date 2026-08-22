"""EA: the deprivation-free companion audit. Pre-registered at 70a5078.

Runs exactly the model frozen in data/processed/ea_preregistration.json --
frozen P3's sample, frozen P3's year effects, the five remaining predictors,
severe_mat_soc_deprivation removed -- and applies ea_rule.decide().

THE EQUAL-SAMPLE TRAP. The companion has one fewer predictor, so re-deriving
complete cases for it could admit rows P3 dropped, and the two models would be
compared on different data. Both are therefore fitted on the SAME frame: the
complete cases of the SIX-variable P3 specification. Verified by row count and
index before anything is estimated.

Nothing here alters p5f-frozen. Frozen P3 is re-fitted only to confirm it
reproduces its frozen values on this run.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outcome import official_hardship
from ea_rule import decide, retained_narrowing, OUTCOMES

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
YEARS = range(2015, 2025)

P3 = ["severe_mat_soc_deprivation", "housing_cost_overburden", "ltu_rate",
      "aic_pps_pc_k", "wage_years_below_2008", "cum_excess_unemployment"]
REMOVED = "severe_mat_soc_deprivation"
COMPANION = [v for v in P3 if v != REMOVED]

prereg = json.loads((OUT / "ea_preregistration.json").read_text())
assert prereg["two_roles"]["companion"]["predictors"] == COMPANION, \
    "companion predictors do not match the pre-registration"
assert prereg["two_roles"]["companion"]["removed"] == REMOVED

p = pd.read_csv(OUT / "persistence_share_panel.csv")
off = official_hardship().rename(columns={"value": "hardship"})[["geo", "time", "hardship"]]
p = p.merge(off, on=["geo", "time"], how="left")
p = p[p.time.isin(YEARS)]

# The one frame both models use: complete cases of the SIX-variable P3 spec.
SAMPLE = p.dropna(subset=P3 + ["hardship"]).copy()


def formula(vars_):
    return "hardship ~ " + " + ".join(vars_) + " + C(time)"


def fit(vars_, data):
    return smf.ols(formula(vars_), data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["geo"]})


def loo_residuals(vars_, data):
    """Greece's out-of-sample residual and rank, exactly as P3 computes them."""
    rows = []
    for c in sorted(data.geo.unique()):
        tr, te = data[data.geo != c], data[data.geo == c].copy()
        mc = smf.ols(formula(vars_), data=tr).fit(
            cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        rows.append({"geo": c, "resid": (te["hardship"] - mc.predict(te)).mean()})
    lad = pd.DataFrame(rows).sort_values("resid", ascending=False).reset_index(drop=True)
    lad["rank"] = lad.index + 1
    g = lad[lad.geo == "EL"].iloc[0]
    return lad, float(g["resid"]), int(g["rank"])


def loo_coefficients(vars_, data, var):
    out = []
    for c in sorted(data.geo.unique()):
        tr = data[data.geo != c]
        mc = smf.ols(formula(vars_), data=tr).fit(
            cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        out.append(mc.params[var])
    return np.array(out)


def wild_bootstrap(vars_, data, var, seed, reps=1999):
    """Restricted (null-imposed) wild cluster bootstrap, as pre-declared.

    The null is IMPOSED: fit without `var`, resample THOSE residuals. An
    unrestricted version returned p=0.82 against t=9.69 in P5 -- nonsense.
    """
    rng = np.random.default_rng(seed)
    m = fit(vars_, data)
    t_obs = m.params[var] / m.bse[var]
    restricted = [x for x in vars_ if x != var]
    m_r = smf.ols(formula(restricted), data=data).fit()
    fitted_null = m_r.predict(data)
    resid_null = data["hardship"] - fitted_null
    geos = data.geo.unique()
    ts = []
    for _ in range(reps):
        w = pd.Series(rng.choice([-1.0, 1.0], size=len(geos)), index=geos)
        db = data.copy()
        db["hardship"] = fitted_null + resid_null.values * data.geo.map(w).values
        mb = smf.ols(formula(vars_), data=db).fit(
            cov_type="cluster", cov_kwds={"groups": db["geo"]})
        ts.append(abs(mb.params[var] / mb.bse[var]))
    return float(t_obs), float((np.sum(np.array(ts) >= abs(t_obs)) + 1) / (reps + 1))


bar = "=" * 74
print(bar); print("EA: DEPRIVATION-FREE COMPANION AUDIT"); print(bar)
print(f"  pre-registration: {prereg['status']}")
print(f"  removed: {REMOVED}")
print(f"  companion predictors: {', '.join(COMPANION)}\n")

# ---- equal-sample verification, before anything is estimated ----
print(bar); print("EQUAL-SAMPLE VERIFICATION"); print(bar)
naive = p.dropna(subset=COMPANION + ["hardship"])
print(f"  frozen P3 complete cases            : {len(SAMPLE)} rows, {SAMPLE.geo.nunique()} countries")
print(f"  companion complete cases if re-derived: {len(naive)} rows")
print(f"  rows the equal-sample rule excludes  : {len(naive) - len(SAMPLE)}")
print(f"  both models fitted on               : {len(SAMPLE)} rows (identical index)")
assert SAMPLE.index.equals(SAMPLE.index), "index mismatch"

# ---- frozen P3, refitted only to confirm reproduction ----
print(f"\n{bar}"); print("FROZEN P3 (reproduction check, values must not change)"); print(bar)
m_p3 = fit(P3, SAMPLE)
lad_p3, resid_p3, rank_p3 = loo_residuals(P3, SAMPLE)
frozen = json.loads((OUT / "p5f_frozen_result.json").read_text())["p3"]
print(f"  Greece residual {resid_p3:+.2f} (frozen {frozen['greece_oos_residual']:+.2f})"
      f"   rank {rank_p3}/27 (frozen {frozen['rank']})")
print(f"  R2 {m_p3.rsquared:.3f} (frozen {frozen['r2']:.3f})   n {len(SAMPLE)} (frozen {frozen['n']})")
assert abs(resid_p3 - frozen["greece_oos_residual"]) < 0.005, "frozen P3 did not reproduce"
assert rank_p3 == int(str(frozen["rank"]).split("/")[0]), "frozen P3 rank did not reproduce"
print("  REPRODUCED. Frozen values unchanged.")

# ---- the companion ----
print(f"\n{bar}"); print("COMPANION: severe_mat_soc_deprivation REMOVED"); print(bar)
m_c = fit(COMPANION, SAMPLE)
lad_c, resid_c, rank_c = loo_residuals(COMPANION, SAMPLE)
print(f"  n = {len(SAMPLE)}   R2 = {m_c.rsquared:.3f}")
print(f"  Greece out-of-sample residual = {resid_c:+.2f} pp, rank {rank_c}/27\n")
print("  coefficients (cluster-robust by country):")
for v in COMPANION:
    print(f"    {v:28} {m_c.params[v]:+9.4f}  se {m_c.bse[v]:7.4f}  p {m_c.pvalues[v]:.4f}")

cum = "cum_excess_unemployment"
print(f"\n  {cum} in each specification:")
print(f"    frozen P3  {m_p3.params[cum]:+9.4f}  se {m_p3.bse[cum]:7.4f}  p {m_p3.pvalues[cum]:.4f}")
print(f"    companion  {m_c.params[cum]:+9.4f}  se {m_c.bse[cum]:7.4f}  p {m_c.pvalues[cum]:.4f}")

print("\n  wild cluster bootstrap (Rademacher, 1999 reps, null imposed):")
t_obs, p_boot = wild_bootstrap(COMPANION, SAMPLE, cum, seed=20250822)
print(f"    {cum:28} t={t_obs:+6.2f}  bootstrap p = {p_boot:.4f}")

coefs = loo_coefficients(COMPANION, SAMPLE, cum)
sign_stable = bool((np.sign(coefs) == np.sign(coefs[0])).all())
print(f"\n  {cum} across 27 LOO folds: {coefs.min():+.4f} to {coefs.max():+.4f}, "
      f"sign stable = {sign_stable}")

print("\n  VIF:")
X = SAMPLE[COMPANION].astype(float)
vifs = {c: variance_inflation_factor(X.values, i) for i, c in enumerate(X.columns)}
for c, v in vifs.items():
    print(f"    {c:28} {v:6.2f}")
max_vif = max(vifs.values())

# ---- no-accumulation counterpart, for the retained-narrowing report ----
_, resid_c_noacc, _ = loo_residuals([v for v in COMPANION if v != cum], SAMPLE)

# ---- the pre-registered decision ----
print(f"\n{bar}"); print("PRE-REGISTERED DECISION RULE"); print(bar)
outcome, degradation, notes = decide(
    companion_residual=resid_c,
    companion_rank=rank_c,
    n_countries=len(lad_c),
    cum_coef_positive=bool(m_c.params[cum] > 0),
    bootstrap_supports=bool(p_boot < 0.05),
    loo_sign_stable=sign_stable,
    max_vif=max_vif,
)
print(f"  frozen P3 residual   {resid_p3:+.2f}  rank {rank_p3}/27")
print(f"  companion residual   {resid_c:+.2f}  rank {rank_c}/27")
print(f"  degradation          {degradation:+.2f} points "
      f"(band A <= 3.0, band B <= 8.0)")
print(f"  retained narrowing   {retained_narrowing(resid_c, resid_c_noacc):.1%} "
      f"(companion without accumulation: {resid_c_noacc:+.2f})")
for n in notes:
    print(f"    - {n}")
print(f"\n  -> OUTCOME {outcome}: {OUTCOMES[outcome]}")

pd.DataFrame([{
    "outcome": outcome,
    "p3_residual": resid_p3, "p3_rank": rank_p3, "p3_r2": m_p3.rsquared,
    "companion_residual": resid_c, "companion_rank": rank_c,
    "companion_r2": m_c.rsquared,
    "degradation": degradation,
    "companion_residual_no_accumulation": resid_c_noacc,
    "retained_narrowing": retained_narrowing(resid_c, resid_c_noacc),
    "cum_coef_p3": m_p3.params[cum], "cum_coef_companion": m_c.params[cum],
    "cum_se_companion": m_c.bse[cum],
    "bootstrap_t": t_obs, "bootstrap_p": p_boot,
    "loo_coef_min": coefs.min(), "loo_coef_max": coefs.max(),
    "loo_sign_stable": sign_stable, "max_vif": max_vif,
    "n": len(SAMPLE), "rows_excluded_by_equal_sample": len(naive) - len(SAMPLE),
}]).to_csv(OUT / "ea_results.csv", index=False)
lad_c.to_csv(OUT / "ea_companion_residuals.csv", index=False)
print(f"\nWritten to {OUT}/ea_results.csv, ea_companion_residuals.csv")
