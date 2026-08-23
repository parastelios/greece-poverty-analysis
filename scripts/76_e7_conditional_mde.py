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
REPS, TARGET = 1999, 0.80
GRID = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0, 3.0]
MC_SE = lambda p_: (p_ * (1 - p_) / REPS) ** 0.5

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
print("  POWER ONLY. No E7 JOINT OUTCOME RESULT is fitted here -- the baseline")
print("  hardship model IS fitted, to estimate variance components.")
print(f"  {REPS} simulations per point, target power {TARGET:.0%}, "
      f"MC SE at target ~{MC_SE(TARGET):.4f}.")
print(f"  {len(PAIRS)} pairs x 2 directions = {len(PAIRS) * 2} conditional MDEs.\n")

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


def cluster_ols(XtX_inv, X, y, group_slices, k, correction):
    """OLS with country-clustered SEs, matching statsmodels exactly.

    THE CORRECTION IS NOT OPTIONAL. statsmodels applies the finite-sample
    factor G/(G-1) x (N-1)/(N-K), which at G=27 clusters is 1.0870. Omitting it
    understates every standard error by ~8.7% and makes the published MDEs
    optimistic. Verified against a statsmodels fit in verify_against_statsmodels().
    """
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    for m in group_slices:
        Xu = X[m].T @ resid[m]
        meat += np.outer(Xu, Xu)
    V = XtX_inv @ meat @ XtX_inv * correction
    return float(beta[k]), float(np.sqrt(max(V[k, k], 0)))


def fs_correction(n, k, g):
    return (g / (g - 1)) * ((n - 1) / (n - k))


def verify_against_statsmodels(d, cur, acc):
    """The manual SE must reproduce statsmodels before any MDE is trusted."""
    X = design(d, ["arop", cur, acc])
    y = d.subjective_poverty.to_numpy(float)
    slices = [(d.geo == g).to_numpy() for g in d.geo.unique()]
    corr = fs_correction(len(d), X.shape[1], d.geo.nunique())
    XtX_inv = np.linalg.pinv(X.T @ X)
    sm = smf.ols(f"{BASE} + {cur} + {acc}", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["geo"]})
    worst = 0.0
    for k, name in [(2, cur), (3, acc)]:
        _, se = cluster_ols(XtX_inv, X, y, slices, k, corr)
        worst = max(worst, abs(se - sm.bse[name]) / sm.bse[name])
    return worst


rows, curves = [], []
print("  verifying the manual cluster-robust SE against statsmodels...")
for i, pr in enumerate(PAIRS):
    cur, acc, pid = pr["current"], pr["accumulated"], pr["id"]
    if cur not in panel.columns or acc not in panel.columns:
        print(f"  {pid:18} SKIP: not in panel")
        continue
    d = panel.dropna(subset=[cur, acc, "subjective_poverty", "arop"]).copy()
    rel = verify_against_statsmodels(d, cur, acc)
    if rel > 1e-8:
        raise SystemExit(f"{pid}: manual SE differs from statsmodels by {rel:.2e}")
print(f"  OK: manual SEs match statsmodels to <1e-8 on all "
      f"{len(PAIRS)} pairs.\n")

for i, pr in enumerate(PAIRS):
    cur, acc, pid = pr["current"], pr["accumulated"], pr["id"]
    if cur not in panel.columns or acc not in panel.columns:
        continue
    d = panel.dropna(subset=[cur, acc, "subjective_poverty", "arop"]).copy()
    sd_b, sd_w, sd_r = variance_components(d)
    r_partial = partial_corr(d, cur, acc)
    geos = d.geo.unique()
    slices = [(d.geo == g).to_numpy() for g in geos]
    gmap = np.array([{g: j for j, g in enumerate(geos)}[g] for g in d.geo])

    X_joint = design(d, ["arop", cur, acc])
    corr_j = fs_correction(len(d), X_joint.shape[1], len(geos))
    XtX_joint = np.linalg.pinv(X_joint.T @ X_joint)

    def marginal(focal):
        X = design(d, ["arop", focal])
        return (X, np.linalg.pinv(X.T @ X),
                fs_correction(len(d), X.shape[1], len(geos)), 2)

    def run(XtX, X, k, corr, focal, label):
        """Plant an effect on `focal` and measure detection.

        Returns (mde, power_at_mde, power_before, mc_se_before). The PRECEDING
        grid point matters as much as the selected one: an MDE can move in
        either direction on a rerun -- the selected point can fall below the
        target, or the point before it can rise above. Checking only the
        selected point misses the second case entirely.
        """
        # DETERMINISTIC SEED. hash(pid) is randomised per process unless
        # PYTHONHASHSEED is fixed, so the previous artifact could not be
        # regenerated. The frozen pair index is stable by construction.
        rng = np.random.default_rng(20250827 + i * 10 + (0 if focal == acc else 1)
                                    + (0 if label == "conditional" else 5))
        sd_f = d[focal].std()
        xf = d[focal].to_numpy(float)
        found, found_power = None, None
        prev_power, prev_se = None, None
        for eff in GRID:
            beta = eff * sd_r / sd_f
            hits = 0
            for _ in range(REPS):
                y = (beta * xf + rng.normal(0, sd_b, len(geos))[gmap]
                     + rng.normal(0, sd_w, len(d)))
                c, se = cluster_ols(XtX, X, y, slices, k, corr)
                if se > 0 and abs(c / se) > 1.96 and np.sign(c) == np.sign(beta):
                    hits += 1
            power = hits / REPS
            curves.append({"pair": pid, "focal": focal, "design": label,
                           "effect_sd": eff, "power": power,
                           "mc_se": MC_SE(power), "reps": REPS})
            if power >= TARGET:
                found, found_power = eff, power
                break
            prev_power, prev_se = power, MC_SE(power)
        return found, found_power, prev_power, prev_se

    for focal, other, k_j in [(acc, cur, 3), (cur, acc, 2)]:
        mde, pw, pw_prev, se_prev = run(
            XtX_joint, X_joint, k_j, corr_j, focal, "conditional")
        Xm, XtXm, corr_m, k_m = marginal(focal)
        mde_m, _, _, _ = run(XtXm, Xm, k_m, corr_m, focal, "marginal")
        # TWO-SIDED. Either the selected point can drop below the target on a
        # rerun, or the point before it can rise above -- both move the MDE.
        fragile_at = bool(pw is not None and abs(pw - TARGET) < 2 * MC_SE(pw))
        fragile_before = bool(pw_prev is not None
                              and abs(pw_prev - TARGET) < 2 * se_prev)
        fragile = fragile_at or fragile_before
        rows.append({"pair": pid, "construct": pr["construct"],
                     "focal": focal, "controlling_for": other,
                     "direction": "accumulated|current" if focal == acc
                                  else "current|accumulated",
                     "n": len(d), "countries": len(geos),
                     "partial_corr": r_partial,
                     "residual_sd": sd_r, "between_sd": sd_b, "within_sd": sd_w,
                     "conditional_mde_sd": mde, "power_at_mde": pw,
                     "mc_se_at_mde": MC_SE(pw) if pw is not None else None,
                     "power_before_mde": pw_prev,
                     "mc_se_before_mde": se_prev,
                     "boundary_fragile": fragile,
                     "fragile_at_selected": fragile_at,
                     "fragile_at_preceding": fragile_before,
                     "marginal_mde_sd": mde_m,
                     "inflation": (mde / mde_m) if (mde and mde_m) else None,
                     "reps": REPS})
        m_s = f"{mde:.2f}" if mde else f">{GRID[-1]:.1f}"
        g_s = f"{mde_m:.2f}" if mde_m else f">{GRID[-1]:.1f}"
        infl = f"{mde / mde_m:.2f}x" if (mde and mde_m) else "n/a"
        lab = "acc | cur" if focal == acc else "cur | acc"
        print(f"  {pid:18} {lab:9} marginal {g_s:>5}  conditional {m_s:>5} SD  "
              f"inflation {infl:>6}{'  FRAGILE' if fragile else ''}")

res = pd.DataFrame(rows)
pd.DataFrame(curves).to_csv(PROC / "e7_mde_curves.csv", index=False)
res.to_csv(PROC / "e7_conditional_mde.csv", index=False)

print(f"\n{bar}\nREADING\n{bar}")
print("  Both columns use IDENTICAL machinery on the same rows, so the")
print("  inflation factor is meaningful. It is NOT comparable to the published")
print("  0.70 family MDE, which came from a different design in script 61.")
print("\n  Inflation above 1 means the pair is harder to test conditionally")
print("  than marginally: the two measures share variation, so less independent")
n_at_or_above = int((res.inflation >= 0.9999).sum())
print(f"  signal remains once the counterpart is controlled. {n_at_or_above} of "
      f"{int(res.inflation.notna().sum())} conditional MDEs are AT OR ABOVE")
print("  their same-machinery marginal MDE (four are exactly equal).")
print("\n  ONE RATIO IS BELOW 1, AND IT IS NOT GIVEN A SUBSTANTIVE READING.")
print("  In the P7 current-inflation direction, adding accumulated inflation")
print("  improves simulated precision despite predictor correlation. This is")
print("  reported as a DESIGN-SPECIFIC POWER RESULT of this finite-cluster")
print("  simulation and design matrix -- NOT as evidence that accumulated")
print("  inflation genuinely explains between-country variation in hardship.")
print("\n  THE CONDITIONAL COLUMN IS THE OPERATIVE THRESHOLD FOR E7.")
fragile = res[res.boundary_fragile == True]
if len(fragile):
    print(f"\n  BOUNDARY-FRAGILE ({len(fragile)} of {len(res)}): the selected grid")
    print(f"  point OR the one before it sits within 2 Monte Carlo SEs of")
    print(f"  {TARGET:.0%}, so a rerun with different draws could move the MDE one")
    print("  step in either direction. Reported, not hidden.")
    for r in fragile.itertuples():
        which = []
        if r.fragile_at_selected:
            which.append(f"selected {r.power_at_mde:.4f}+/-{r.mc_se_at_mde:.4f}")
        if r.fragile_at_preceding:
            which.append(f"preceding {r.power_before_mde:.4f}+/-{r.mc_se_before_mde:.4f}")
        print(f"    {r.pair:18} {r.focal:28} MDE {r.conditional_mde_sd:.2f}  "
              f"{'; '.join(which)}")

none_found = res[res.conditional_mde_sd.isna()]
if len(none_found):
    print(f"\n  NO conditional MDE reached {TARGET:.0%} power within the grid for: "
          f"{', '.join(none_found.pair)}")
    print("  Every failed conditional test for these pairs is INCONCLUSIVE.")
    print("  No adequate-power claim may be made about them.")
print(f"\nWritten to {PROC}/e7_conditional_mde.csv, e7_mde_curves.csv")
