"""E2: sensitivity substitutions within each construct.

Step 3 of the approved testing order. Pre-registered at a747e7a. FDR is applied
WITHIN construct, not across constructs -- each construct asks its own question
("does my conclusion depend on which member I picked?").

THE RULE THAT MATTERS HERE. A sensitivity cannot become a discovery when its
primary failed. Sensitivities qualify a supported primary; they never substitute
for a failed one. Enforced by e_rule.sensitivity_disposition(), which has no
path returning a finding from a sensitivity alone.

EQUAL SAMPLES WITHIN CONSTRUCT. A sensitivity with better coverage than its
primary would otherwise be compared on more data than the primary ever saw.
Every member of a construct is therefore refit on the INTERSECTION of that
construct's complete cases, and the primary is refit there too -- so the
comparison answers "different measure" rather than "different sample".
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_rule import (decide, benjamini_hochberg, sensitivity_disposition,
                    direction_ok, MDE_SD)
from registry import load as load_registry, adverse_direction, blocks_headline

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
GR = "EL"
BASE = "subjective_poverty ~ arop + C(time)"

panel = pd.read_csv(OUT / "e0_extended_panel.csv")
cmap = json.loads((OUT / "construct_map_frozen.json").read_text())
reg = load_registry()
e1 = pd.read_csv(OUT / "e1_results.csv").set_index("var")

# ---- C3's sensitivity is a composite that must be constructed --------------
C3_PARTS = cmap["constructs"]["C3"]["primary"]
z = pd.DataFrame(index=panel.index)
for v in C3_PARTS:
    # orient every part so HIGHER = WORSE before averaging, or the composite
    # would cancel its own components against each other
    s = panel[v]
    if adverse_direction(reg, v) == "lower_is_worse":
        s = -s
    z[v] = (s - s.mean()) / s.std()
panel["c3_composite"] = z.mean(axis=1)
panel.loc[z.isna().any(axis=1), "c3_composite"] = np.nan
COMPOSITE_ADVERSE = {"c3_composite": "higher_is_worse"}

# ---- what E2 tests ---------------------------------------------------------
PLAN = []
for cid, c in cmap["constructs"].items():
    prim = c["primary"]
    prims = prim if isinstance(prim, list) else [prim]
    sens = []
    for s in c.get("sensitivities", []):
        if s in panel.columns:
            sens.append(s)
        elif cid == "C3" and s.startswith("standardised composite"):
            sens.append("c3_composite")
        else:
            print(f"  SKIP {cid} sensitivity {s!r}: not a panel variable")
    if not sens:
        print(f"  {cid}: no testable sensitivity "
              f"({'forbidden pairing' if cid == 'C4' else 'none declared'})")
        continue
    PLAN.append({"construct": cid, "name": c["name"], "primaries": prims,
                 "sensitivities": sens})


def fit(f, d):
    return smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})


def greece_residual(f, d):
    tr, te = d[d.geo != GR], d[d.geo == GR]
    m = smf.ols(f, data=tr).fit()
    return float((te["subjective_poverty"] - m.predict(te)).mean())


def wild_bootstrap(f, d, var, seed, reps=1999):
    rng = np.random.default_rng(seed)
    m = fit(f, d)
    t_obs = m.params[var] / m.bse[var]
    m_r = smf.ols(BASE, data=d).fit()
    fitted, resid = m_r.predict(d), d["subjective_poverty"] - m_r.predict(d)
    geos = d.geo.unique()
    ts = []
    for _ in range(reps):
        w = pd.Series(rng.choice([-1.0, 1.0], size=len(geos)), index=geos)
        db = d.copy()
        db["subjective_poverty"] = fitted + resid.values * d.geo.map(w).values
        mb = fit(f, db)
        ts.append(abs(mb.params[var] / mb.bse[var]))
    return float((np.sum(np.array(ts) >= abs(t_obs)) + 1) / (reps + 1))


bar = "=" * 96
print(bar); print("E2: SENSITIVITY SUBSTITUTIONS WITHIN CONSTRUCT"); print(bar)
print("  FDR applied WITHIN construct. A sensitivity never becomes a finding.\n")

rows, seed = [], 20250824
for plan in PLAN:
    cid = plan["construct"]
    members = plan["primaries"] + plan["sensitivities"]
    common = panel.dropna(subset=members + ["subjective_poverty", "arop"])
    print(f"\n{bar}\n{cid} — {plan['name']}")
    print(f"  common sample across {len(members)} members: {len(common)} rows, "
          f"{common.geo.nunique()} countries")

    fits = []
    for v in members:
        f = f"{BASE} + {v}"
        m, m0 = fit(f, common), fit(BASE, common)
        adv = COMPOSITE_ADVERSE.get(v) or adverse_direction(reg, v)
        ci = m.conf_int().loc[v]
        sd_x, resid_sd = common[v].std(), float(np.std(m0.resid, ddof=1))
        fits.append({
            "construct": cid, "var": v,
            "role": "primary" if v in plan["primaries"] else "sensitivity",
            "adverse": adv, "coef": m.params[v], "se": m.bse[v],
            "p_raw": m.pvalues[v],
            "ci_abs_std_upper": max(abs(ci[0]), abs(ci[1])) * sd_x / resid_sd,
            "std_effect": abs(m.params[v]) * sd_x / resid_sd,
            "violation": bool(cid == "P1" or (v in reg.index and blocks_headline(reg, v))),
            "n": len(common), "formula": f,
            "greece_improves": bool(abs(greece_residual(f, common))
                                    < abs(greece_residual(BASE, common))),
        })
    fd = pd.DataFrame(fits)
    # Initialise before use: when EVERY member of a construct is
    # proximity-blocked (P1), nothing is eligible and these columns would
    # otherwise never be created.
    fd["p_fdr"] = np.nan
    fd["boot_p"] = np.nan
    fd["fdr_rejected"] = False
    fd["loo_sign_stable"] = False

    elig = fd[~fd.violation]
    if len(elig):
        adj, rej = benjamini_hochberg(elig.p_raw.tolist())
        fd.loc[elig.index, "p_fdr"] = adj
        fd.loc[elig.index, "fdr_rejected"] = rej
    fd["fdr_rejected"] = fd.fdr_rejected.fillna(False).infer_objects(copy=False).astype(bool)

    for i, r in fd.iterrows():
        bp, loo = None, False
        if r.fdr_rejected and not r.violation:
            seed += 1
            bp = wild_bootstrap(r.formula, common, r["var"], seed)
            cs = np.array([fit(r.formula, common[common.geo != g]).params[r["var"]]
                           for g in sorted(common.geo.unique())])
            loo = bool((np.sign(cs) == np.sign(cs[0])).all())
        o, notes = decide(
            coefficient=r.coef, adverse=r.adverse,
            fdr_rejected=bool(r.fdr_rejected), bootstrap_p=bp,
            loo_sign_stable=loo, greece_residual_improves=bool(r.greece_improves),
            proximity_violation=bool(r.violation),
            ci_abs_std_upper=float(r.ci_abs_std_upper))
        fd.at[i, "boot_p"] = np.nan if bp is None else bp
        fd.at[i, "loo_sign_stable"] = loo
        fd.at[i, "outcome"] = o
        fd.at[i, "notes"] = " | ".join(notes)

    # E1's verdict is what the sensitivity rule keys on, not this run's.
    e1_out = {v: (e1.loc[v, "outcome"] if v in e1.index else None)
              for v in plan["primaries"]}
    prim_supported = any(v == "supported" for v in e1_out.values())
    prim_state = "supported" if prim_supported else "inconclusive_under_available_power"

    print(f"  E1 primary verdict: "
          f"{', '.join(f'{k}={v}' for k, v in e1_out.items())}")
    print(f"\n  {'role':11} {'variable':26} {'coef':>10} {'p_raw':>7} "
          f"{'p_FDR':>7} {'boot':>7}  {'outcome':36} disposition")
    for r in fd.itertuples():
        disp = ("—" if r.role == "primary"
                else sensitivity_disposition(prim_state, r.outcome))
        pf = "  --  " if r.p_fdr != r.p_fdr else f"{r.p_fdr:.4f}"
        bpx = "  --  " if r.boot_p != r.boot_p else f"{r.boot_p:.4f}"
        print(f"  {r.role:11} {r.var:26} {r.coef:+10.4f} {r.p_raw:7.4f} "
              f"{pf:>7} {bpx:>7}  {r.outcome:36} {disp}")
        rows.append({**{k: getattr(r, k) for k in
                        ["construct", "var", "role", "adverse", "coef", "se",
                         "p_raw", "p_fdr", "boot_p", "loo_sign_stable",
                         "std_effect", "ci_abs_std_upper", "greece_improves",
                         "violation", "n", "outcome", "notes"]},
                     "primary_state": prim_state, "disposition": disp})

res = pd.DataFrame(rows)
print(f"\n{bar}\nDISPOSITION SUMMARY (sensitivities only)\n{bar}")
s = res[res.role == "sensitivity"]
for d_ in s.disposition.value_counts().index:
    vs = s[s.disposition == d_]["var"].tolist()
    print(f"  {d_:24} {len(vs):2}  {', '.join(vs)}")

promo = s[(s.outcome == "supported") & (s.disposition == "cannot_promote")]
print(f"\n  Sensitivities that would have been findings if the rule allowed it: "
      f"{len(promo)}")
for r in promo.itertuples():
    print(f"    {r.construct} {r.var}: {r.outcome}, primary {r.primary_state}")

res.to_csv(OUT / "e2_results.csv", index=False)
print(f"\nWritten to {OUT}/e2_results.csv")
