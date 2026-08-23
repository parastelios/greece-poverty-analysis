"""E7 step 1: pair-specific CONDITIONAL minimum detectable effects.

POWER ONLY. No conditional outcome coefficient is reported here. This runs
before the joint models are fitted, so E7's nulls can be labelled against a
threshold that was published rather than chosen afterwards.

WHY THE FAMILY MDE DOES NOT TRANSFER. The published 0.70 residual SD applies to
a single regressor added to the baseline. In a joint model the focal predictor
competes with its own current/accumulated counterpart, and only the part of it
that is INDEPENDENT of that counterpart carries information. The more collinear
the pair, the less independent variation remains and the larger the detectable
effect becomes -- roughly by a factor of 1/sqrt(1 - r^2), where r is the partial
correlation after AROP and year effects are removed.

Method follows 61_e_mde.py, including both bugs fixed there:
  * noise is drawn from ESTIMATED VARIANCE COMPONENTS, not by permuting
    residuals within country, which would correlate the noise with the regressor
  * detection requires the CORRECT SIGN, not merely p < 0.05
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
prereg = json.loads((PROC / "e7_preregistration.json").read_text())
PAIRS = prereg["pairs"]
BASE = "subjective_poverty ~ arop + C(time)"
REPS, TARGET = 400, 0.80
GRID = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0, 3.0]

panel = pd.read_csv(PROC / "e4_accumulated_panel.csv")
frozen = pd.read_csv(PROC / "cumulative_hardship_candidate_panel.csv")
for c in [c for c in frozen.columns if c not in panel.columns and c not in ("geo", "time")]:
    panel = panel.merge(frozen[["geo", "time", c]], on=["geo", "time"], how="left")


def variance_components(d):
    """Between- and within-country SD of the baseline residual."""
    m = smf.ols(BASE, data=d).fit()
    r = d.assign(_r=m.resid)
    b = r.groupby("geo")._r.mean()
    w = r._r - r.geo.map(b)
    return float(b.std(ddof=1)), float(w.std(ddof=1)), float(np.std(m.resid, ddof=1))


def partial_corr(d, a, b):
    """Correlation between the two focal predictors after AROP and year FE."""
    ra = smf.ols(f"{a} ~ arop + C(time)", data=d).fit().resid
    rb = smf.ols(f"{b} ~ arop + C(time)", data=d).fit().resid
    return float(np.corrcoef(ra, rb)[0, 1])


bar = "=" * 96
print(bar); print("E7 STEP 1: PAIR-SPECIFIC CONDITIONAL MDEs"); print(bar)
print("  POWER ONLY. No conditional outcome coefficient is reported.")
print(f"  {REPS} simulations per point, target power {TARGET:.0%}.\n")

def design(d, cols):
    """Design matrix with year dummies, built ONCE per pair.

    statsmodels re-parses the formula and rebuilds the dummies on every call,
    which made this 45,000 formula parses. The matrix is fixed across
    simulations; only y changes.
    """
    X = [np.ones(len(d))]
    for c in cols:
        X.append(d[c].to_numpy(float))
    for y in sorted(d.time.unique())[1:]:
        X.append((d.time == y).to_numpy(float))
    return np.column_stack(X)


def cluster_ols(XtX_inv, X, y, group_slices, k):
    """OLS with country-clustered SEs. Returns (coef, se) for column k."""
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    for m in group_slices:
        Xu = X[m].T @ resid[m]
        meat += np.outer(Xu, Xu)
    V = XtX_inv @ meat @ XtX_inv
    return float(beta[k]), float(np.sqrt(max(V[k, k], 0)))


rows, curves = [], []
for pr in PAIRS:
    cur, acc, pid = pr["current"], pr["accumulated"], pr["id"]
    if cur not in panel.columns or acc not in panel.columns:
        print(f"  {pid:18} SKIP: not in panel")
        continue
    d = panel.dropna(subset=[cur, acc, "subjective_poverty", "arop"]).copy()
    sd_b, sd_w, sd_r = variance_components(d)
    r_partial = partial_corr(d, cur, acc)
    # Two designs, identical machinery, so the inflation factor is meaningful.
    # Comparing against the published 0.70 family MDE would NOT be
    # apples-to-apples: that was computed on a different design in script 61.
    X_joint = design(d, ["arop", cur, acc])
    X_marg = design(d, ["arop", acc])
    XtX_joint = np.linalg.pinv(X_joint.T @ X_joint)
    XtX_marg = np.linalg.pinv(X_marg.T @ X_marg)
    K_JOINT, K_MARG = 3, 2
    geos = d.geo.unique()
    slices = [(d.geo == g).to_numpy() for g in geos]
    gidx = {g: i for i, g in enumerate(geos)}
    gmap = np.array([gidx[g] for g in d.geo])
    sd_acc = d[acc].std()
    xacc = d[acc].to_numpy(float)
    rng = np.random.default_rng(20250827 + abs(hash(pid)) % 1000)

    def run(XtX, X, k, label):
        found = None
        for eff in GRID:
            beta = eff * sd_r / sd_acc
            hits = 0
            for _ in range(REPS):
                y = (beta * xacc + rng.normal(0, sd_b, len(geos))[gmap]
                     + rng.normal(0, sd_w, len(d)))
                c, se = cluster_ols(XtX, X, y, slices, k)
                if se > 0 and abs(c / se) > 1.96 and np.sign(c) == np.sign(beta):
                    hits += 1
            power = hits / REPS
            curves.append({"pair": pid, "design": label,
                           "effect_sd": eff, "power": power})
            if power >= TARGET:
                found = eff
                break
        return found

    mde = run(XtX_joint, X_joint, K_JOINT, "conditional")
    mde_marg = run(XtX_marg, X_marg, K_MARG, "marginal")
    rows.append({"pair": pid, "construct": pr["construct"],
                 "current": cur, "accumulated": acc, "n": len(d),
                 "countries": d.geo.nunique(), "partial_corr": r_partial,
                 "residual_sd": sd_r, "between_sd": sd_b, "within_sd": sd_w,
                 "conditional_mde_sd": mde, "marginal_mde_sd": mde_marg,
                 "inflation": (mde / mde_marg) if (mde and mde_marg) else None})
    m_s = f"{mde:.2f}" if mde else f">{GRID[-1]:.1f}"
    g_s = f"{mde_marg:.2f}" if mde_marg else f">{GRID[-1]:.1f}"
    infl = f"{mde / mde_marg:.2f}x" if (mde and mde_marg) else "n/a"
    print(f"  {pid:18} n={len(d):4d}  partial r={r_partial:+.3f}   "
          f"marginal {g_s:>5}  conditional {m_s:>5} SD   inflation {infl}")

res = pd.DataFrame(rows)
pd.DataFrame(curves).to_csv(PROC / "e7_mde_curves.csv", index=False)
res.to_csv(PROC / "e7_conditional_mde.csv", index=False)

print(f"\n{bar}\nREADING\n{bar}")
print("  Both columns use IDENTICAL machinery on the same rows, so the")
print("  inflation factor is meaningful. It is NOT comparable to the published")
print("  0.70 family MDE, which came from a different design in script 61.")
print("\n  Inflation above 1 means the pair is harder to test conditionally")
print("  than marginally: the two measures share variation, so less independent")
print("  signal remains once the counterpart is controlled.")
print("\n  THE CONDITIONAL COLUMN IS THE OPERATIVE THRESHOLD FOR E7.")
none_found = res[res.conditional_mde_sd.isna()]
if len(none_found):
    print(f"\n  NO conditional MDE reached {TARGET:.0%} power within the grid for: "
          f"{', '.join(none_found.pair)}")
    print("  Every failed conditional test for these pairs is INCONCLUSIVE.")
    print("  No adequate-power claim may be made about them.")
print(f"\nWritten to {PROC}/e7_conditional_mde.csv, e7_mde_curves.csv")
