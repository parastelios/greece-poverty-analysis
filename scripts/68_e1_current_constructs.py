"""E1: the six objective constructs at CURRENT levels, tested individually.

Step 2 of the approved testing order. Pre-registered at a747e7a; the decision
rule is scripts/e_rule.py (40 tests), written before this ran.

  primary outcome:  subjective_poverty ~ arop + C(time) + <construct>
  BH family 1:      current primary representatives, primary outcome
  secondary:        (subjective_poverty - arop) ~ C(time) + <construct>
                    corrected separately, and CANNOT override a primary null

C3 contributes four individual primaries -- there is no composite -- so family 1
holds nine tests. P1 is run but is blocked by the proximity gate by
construction: it is diagnostic only and can never be a headline.

Everything is compared against the common baseline subjective_poverty ~ arop +
C(time), refit on each construct's own complete cases so the Greece residual
comparison is equal-sample.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_rule import decide, benjamini_hochberg, direction_ok, MDE_SD, OUTCOMES

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
GR = "EL"

panel = pd.read_csv(OUT / "e0_extended_panel.csv")
cmap = json.loads((OUT / "construct_map_frozen.json").read_text())
prereg = json.loads((OUT / "e_preregistration.json").read_text())
reg = pd.read_csv(OUT / "e0_variable_registry.csv").set_index("name")

assert prereg["outcomes"]["primary"]["formula"] == \
    "subjective_poverty ~ arop + C(time) + <construct>", "prereg formula changed"

# Family 1: every CURRENT primary representative.
TESTS = []
for cid, c in cmap["constructs"].items():
    prim = c["primary"]
    for v in (prim if isinstance(prim, list) else [prim]):
        if v not in panel.columns:
            print(f"  SKIP {cid}/{v}: not in panel")
            continue
        # The registry ALREADY stores the pre-registration's own vocabulary.
        # An earlier version translated from "high"/"low", values that do not
        # exist in this column, so every variable silently became
        # lower_is_worse and four correct results were reported as
        # direction contradictions. Pass it through and let e_rule validate.
        adverse = reg.loc[v, "adverse_direction"]
        if adverse not in ("higher_is_worse", "lower_is_worse"):
            print(f"  SKIP {cid}/{v}: adverse_direction is {adverse!r}; "
                  "no directional hypothesis can be tested")
            continue
        prox = reg.loc[v, "proximity_class"]
        TESTS.append({"construct": cid, "name": c["name"], "var": v,
                      "adverse": adverse, "proximity": prox,
                      # P1 is diagnostic-only by pre-registration, and any
                      # same-instrument predictor trips the proximity gate.
                      "violation": bool(cid == "P1" or
                                        prox == "proximate_same_instrument")})

BASE = "subjective_poverty ~ arop + C(time)"


def fit(formula, d):
    return smf.ols(formula, data=d).fit(cov_type="cluster",
                                        cov_kwds={"groups": d["geo"]})


def greece_residual(formula, d):
    """Greece's out-of-sample residual, the same leave-one-country-out
    construction P3 and EA use."""
    tr, te = d[d.geo != GR], d[d.geo == GR]
    if tr.empty or te.empty:
        return np.nan
    m = smf.ols(formula, data=tr).fit()
    return float((te["subjective_poverty"] - m.predict(te)).mean())


def wild_bootstrap(formula, d, var, seed, reps=1999):
    """Restricted (null-imposed) wild cluster bootstrap."""
    rng = np.random.default_rng(seed)
    m = fit(formula, d)
    t_obs = m.params[var] / m.bse[var]
    m_r = smf.ols(BASE, data=d).fit()
    fitted_null = m_r.predict(d)
    resid_null = d["subjective_poverty"] - fitted_null
    geos = d.geo.unique()
    ts = []
    for _ in range(reps):
        w = pd.Series(rng.choice([-1.0, 1.0], size=len(geos)), index=geos)
        db = d.copy()
        db["subjective_poverty"] = fitted_null + resid_null.values * d.geo.map(w).values
        mb = fit(formula, db)
        ts.append(abs(mb.params[var] / mb.bse[var]))
    return float(t_obs), float((np.sum(np.array(ts) >= abs(t_obs)) + 1) / (reps + 1))


bar = "=" * 96
print(bar); print("E1: CURRENT-LEVEL CONSTRUCTS"); print(bar)
print(f"  baseline: {BASE}")
print(f"  family 1: {len(TESTS)} current primary representatives")
print(f"  MDE floor: {MDE_SD} residual SD\n")

rows = []
for t in TESTS:
    v = t["var"]
    d = panel.dropna(subset=[v, "subjective_poverty", "arop"]).copy()
    f = f"{BASE} + {v}"
    m, m0 = fit(f, d), fit(BASE, d)
    coef, se, praw = m.params[v], m.bse[v], m.pvalues[v]
    ci = m.conf_int().loc[v]
    # Standardised: effect of one SD of x, in residual-SD units of the baseline.
    sd_x = d[v].std()
    resid_sd = float(np.std(m0.resid, ddof=1))
    std_effect = abs(coef) * sd_x / resid_sd
    ci_abs_std_upper = max(abs(ci[0]), abs(ci[1])) * sd_x / resid_sd
    r_base, r_full = greece_residual(BASE, d), greece_residual(f, d)
    rows.append({**t, "n": len(d), "countries": d.geo.nunique(),
                 "coef": coef, "se": se, "p_raw": praw,
                 "ci_lo": ci[0], "ci_hi": ci[1],
                 "std_effect": std_effect, "ci_abs_std_upper": ci_abs_std_upper,
                 "r2_base": m0.rsquared, "r2_full": m.rsquared,
                 "greece_resid_base": r_base, "greece_resid_full": r_full,
                 "greece_improves": bool(abs(r_full) < abs(r_base)),
                 "formula": f})

res = pd.DataFrame(rows)

# ---- BH within family 1, EXCLUDING proximity-blocked tests --------------
elig = res[~res.violation].copy()
adj, rej = benjamini_hochberg(elig.p_raw.tolist())
elig["p_fdr"], elig["fdr_rejected"] = adj, rej
res = res.merge(elig[["var", "p_fdr", "fdr_rejected"]], on="var", how="left")
res["fdr_rejected"] = res.fdr_rejected.fillna(False).infer_objects(copy=False).astype(bool)
print(f"  BH applied to {len(elig)} eligible tests "
      f"({int(res.violation.sum())} blocked by proximity, excluded from the family)\n")

# ---- bootstrap only where FDR survived, per the pre-registration --------
res["boot_p"] = np.nan
for i, r in res.iterrows():
    if r.fdr_rejected and not r.violation:
        d = panel.dropna(subset=[r["var"], "subjective_poverty", "arop"])
        _, bp = wild_bootstrap(r.formula, d, r["var"], seed=20250823 + i)
        res.at[i, "boot_p"] = bp

# ---- LOO sign stability, likewise ---------------------------------------
res["loo_sign_stable"] = False
res["loo_min"] = np.nan
res["loo_max"] = np.nan
for i, r in res.iterrows():
    if not (r.fdr_rejected and not r.violation):
        continue
    d = panel.dropna(subset=[r["var"], "subjective_poverty", "arop"])
    cs = []
    for c in sorted(d.geo.unique()):
        mc = fit(r.formula, d[d.geo != c])
        cs.append(mc.params[r["var"]])
    cs = np.array(cs)
    res.at[i, "loo_sign_stable"] = bool((np.sign(cs) == np.sign(cs[0])).all())
    res.at[i, "loo_min"], res.at[i, "loo_max"] = cs.min(), cs.max()

# ---- the pre-registered decision ----------------------------------------
outcomes, notelists, gates = [], [], []
for r in res.itertuples():
    o, notes, gate = decide(
        coefficient=r.coef, adverse=r.adverse,
        fdr_rejected=bool(r.fdr_rejected),
        bootstrap_p=None if np.isnan(r.boot_p) else float(r.boot_p),
        loo_sign_stable=bool(r.loo_sign_stable),
        greece_residual_improves=bool(r.greece_improves),
        proximity_violation=bool(r.violation),
        ci_abs_std_upper=float(r.ci_abs_std_upper),
    )
    outcomes.append(o)
    notelists.append(" | ".join(notes))
    gates.append(gate)
res["outcome"], res["notes"], res["failed_gate"] = outcomes, notelists, gates

print(f"  {'con':>4} {'variable':26} {'coef':>9} {'se':>7} {'p_raw':>7} "
      f"{'p_FDR':>7} {'dir':>4} {'SD':>5} {'n':>4}  outcome")
for r in res.sort_values(["construct", "var"]).itertuples():
    d_ok = "ok" if direction_ok(r.coef, r.adverse) else "WRONG"
    pf = "  --  " if np.isnan(r.p_fdr) else f"{r.p_fdr:.4f}"
    print(f"  {r.construct:>4} {r.var:26} {r.coef:+9.4f} {r.se:7.4f} "
          f"{r.p_raw:7.4f} {pf:>7} {d_ok:>5} {r.std_effect:5.2f} {r.n:4d}  "
          f"{r.outcome}{'' if not r.failed_gate else '  [' + r.failed_gate + ']'}")

print(f"\n{bar}\nOUTCOME SUMMARY\n{bar}")
for o in res.outcome.value_counts().index:
    vs = res[res.outcome == o]["var"].tolist()
    print(f"  {o:38} {len(vs)}  {', '.join(vs)}")

# ---- SECONDARY OUTCOME, BH family 3, corrected separately ---------------
# (subjective_poverty - arop) ~ C(time) + <construct>. AROP is NOT re-added on
# the right: it is already inside the outcome by subtraction.
print(f"\n{bar}\nSECONDARY OUTCOME (BH family 3, corrected separately)\n{bar}")
print("  A secondary result CANNOT override a primary null. It may qualify or")
print("  illustrate a primary finding; it may never create one.\n")
panel["hardship_gap"] = panel.subjective_poverty - panel.arop
SEC = "hardship_gap ~ C(time)"
srows = []
for t_ in TESTS:
    v = t_["var"]
    d = panel.dropna(subset=[v, "hardship_gap"]).copy()
    m = fit(f"{SEC} + {v}", d)
    srows.append({"construct": t_["construct"], "var": v,
                  "adverse": t_["adverse"], "violation": t_["violation"],
                  "coef": m.params[v], "se": m.bse[v], "p_raw": m.pvalues[v],
                  "n": len(d)})
sec = pd.DataFrame(srows)
selig = sec[~sec.violation].copy()
sadj, srej = benjamini_hochberg(selig.p_raw.tolist())
selig["p_fdr"], selig["fdr_rejected"] = sadj, srej
sec = sec.merge(selig[["var", "p_fdr", "fdr_rejected"]], on="var", how="left")
sec["fdr_rejected"] = sec.fdr_rejected.fillna(False).infer_objects(copy=False).astype(bool)
sec = sec.merge(res[["var", "outcome"]].rename(columns={"outcome": "primary_outcome"}),
                on="var", how="left")
sec["direction_ok"] = [direction_ok(r.coef, r.adverse) for r in sec.itertuples()]
sec["overrides_blocked"] = (sec.fdr_rejected & sec.direction_ok
                            & (sec.primary_outcome != "supported"))
print(f"  {'con':>4} {'variable':26} {'coef':>9} {'p_raw':>7} {'p_FDR':>7} "
      f"{'dir':>5}  primary outcome")
for r in sec.sort_values(["construct", "var"]).itertuples():
    pf = "  --  " if r.p_fdr != r.p_fdr else f"{r.p_fdr:.4f}"
    flag = "  <- cannot promote" if r.overrides_blocked else ""
    print(f"  {r.construct:>4} {r.var:26} {r.coef:+9.4f} {r.p_raw:7.4f} "
          f"{pf:>7} {'ok' if r.direction_ok else 'WRONG':>5}  "
          f"{r.primary_outcome}{flag}")
blocked = sec[sec.overrides_blocked]["var"].tolist()
print(f"\n  Secondary results that clear FDR with the right sign but whose PRIMARY")
print(f"  did not: {len(blocked)}  {', '.join(blocked) if blocked else '-'}")
print("  These are recorded and may NOT be promoted to findings.")
sec.to_csv(OUT / "e1_secondary.csv", index=False)

res.drop(columns=["formula"]).to_csv(OUT / "e1_results.csv", index=False)
print(f"\nWritten to {OUT}/e1_results.csv")
print("\nNULLS BELOW THE MDE ARE INCONCLUSIVE, NOT UNSUPPORTED.")
