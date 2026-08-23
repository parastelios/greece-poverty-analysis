"""E7: does accumulation add information beyond current conditions?

Runs under the rules frozen at fe28fc5 with power published at 2206620.

Three models per pair on identical rows -- current-only, accumulated-only,
joint -- and the conditional tests are the JOINT-model coefficients in BOTH
directions. Neither direction is privileged.

Superiority is NOT decided by comparing two p-values from two separate models.
Every verdict below comes from the joint model.

E7 CAN ONLY QUALIFY OR WITHDRAW. The pairs were corrected within BH families 1
and 2; family 4 governs what E7 may call conditionally supported among results
that already stood. Nothing here creates support for a construct E1 and E4 did
not already support.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_rule import decide, benjamini_hochberg

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
GR = "EL"
BASE = "subjective_poverty ~ arop + C(time)"

prereg = json.loads((PROC / "e7_preregistration.json").read_text())
PAIRS = prereg["pairs"]
VIF_MAX = prereg["multicollinearity_rule"]["thresholds"]["focal_vif"]
CORR_MAX = prereg["multicollinearity_rule"]["thresholds"]["abs_correlation"]
mde = pd.read_csv(PROC / "e7_conditional_mde.csv")
e1 = pd.read_csv(PROC / "e1_results.csv").set_index("var")
e4 = pd.read_csv(PROC / "e4_results.csv").set_index("var")

panel = pd.read_csv(PROC / "e4_accumulated_panel.csv")
frozen = pd.read_csv(PROC / "cumulative_hardship_candidate_panel.csv")
for c in [c for c in frozen.columns if c not in panel.columns and c not in ("geo", "time")]:
    panel = panel.merge(frozen[["geo", "time", c]], on=["geo", "time"], how="left")

ADVERSE = {  # from the frozen construct map / registry, per E4
    "ltu_rate": "higher_is_worse", "acc_cum_excess_unemployment": "higher_is_worse",
    "real_wages_idx": "lower_is_worse", "acc_real_wages_shortfall": "higher_is_worse",
    "dur_real_wages_below": "higher_is_worse",
    "pct_below_peak": "higher_is_worse", "acc_pct_below_peak": "higher_is_worse",
    "arop_threshold_real": "lower_is_worse", "acc_threshold_shortfall": "higher_is_worse",
    "wadj_a01": "higher_is_worse", "acc_wadj_excess": "higher_is_worse",
    "hicp": "higher_is_worse", "acc_hicp_compounded": "higher_is_worse",
    "housing_cost_overburden": "higher_is_worse", "acc_housing_excess": "higher_is_worse",
}


def fit(f, d):
    return smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})


def greece_resid(f, d):
    tr, te = d[d.geo != GR], d[d.geo == GR]
    return float((te["subjective_poverty"] - smf.ols(f, data=tr).fit().predict(te)).mean())


def focal_vif(d, focal, other):
    """VIF of the FOCAL predictor only, in the joint design.

    NOT the maximum over year dummies, which are collinear by construction and
    would trip the gate on every pair.
    """
    r2 = smf.ols(f"{focal} ~ arop + {other} + C(time)", data=d).fit().rsquared
    return float(1 / max(1 - r2, 1e-12))


def wild_boot(f, d, var, restricted, seed, reps=1999):
    rng = np.random.default_rng(seed)
    m = fit(f, d)
    t_obs = m.params[var] / m.bse[var]
    m_r = smf.ols(restricted, data=d).fit()
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


bar = "=" * 104
print(bar); print("E7: CONDITIONAL TESTS"); print(bar)
print(f"  {len(PAIRS)} pairs x 2 directions = {len(PAIRS) * 2} conditional coefficients")
print(f"  BH family 4, corrected together. Collinearity gate: focal VIF > {VIF_MAX} "
      f"or |partial r| > {CORR_MAX}\n")

rows = []
for i, pr in enumerate(PAIRS):
    cur, acc, pid = pr["current"], pr["accumulated"], pr["id"]
    d = panel.dropna(subset=[cur, acc, "subjective_poverty", "arop"]).copy()
    joint = f"{BASE} + {cur} + {acc}"
    m_cur, m_acc, m_joint = fit(f"{BASE} + {cur}", d), fit(f"{BASE} + {acc}", d), fit(joint, d)
    r_cur, r_acc, r_joint = (greece_resid(f"{BASE} + {cur}", d),
                             greece_resid(f"{BASE} + {acc}", d), greece_resid(joint, d))
    pc = float(mde[mde.pair == pid].partial_corr.iloc[0])
    v_cur, v_acc = focal_vif(d, cur, acc), focal_vif(d, acc, cur)
    gate = (max(v_cur, v_acc) > VIF_MAX) or (abs(pc) > CORR_MAX)

    for focal, other, without in [(acc, cur, f"{BASE} + {cur}"),
                                  (cur, acc, f"{BASE} + {acc}")]:
        row = mde[(mde.pair == pid) & (mde.focal == focal)].iloc[0]
        rows.append({
            "pair": pid, "construct": pr["construct"], "focal": focal,
            "controlling_for": other, "adverse": ADVERSE[focal],
            "n": len(d), "countries": d.geo.nunique(),
            "coef_joint": m_joint.params[focal], "se_joint": m_joint.bse[focal],
            "p_raw": m_joint.pvalues[focal],
            "ci_lo": m_joint.conf_int().loc[focal][0],
            "ci_hi": m_joint.conf_int().loc[focal][1],
            "sd_focal": d[focal].std(), "resid_sd": float(np.std(fit(BASE, d).resid, ddof=1)),
            "focal_vif": v_cur if focal == cur else v_acc,
            "partial_corr": pc, "collinearity_gate": gate,
            "conditional_mde_sd": row.conditional_mde_sd,
            "mde_fragile": bool(row.boundary_fragile),
            "greece_without": r_cur if focal == acc else r_acc,
            "greece_joint": r_joint,
            "restricted": without, "joint_formula": joint,
        })

res = pd.DataFrame(rows)
res["std_effect"] = res.coef_joint.abs() * res.sd_focal / res.resid_sd
res["ci_abs_std_upper"] = res[["ci_lo", "ci_hi"]].abs().max(axis=1) * res.sd_focal / res.resid_sd
res["greece_improves"] = res.greece_joint.abs() < res.greece_without.abs()

# BH family 4: all 16 together, EXCLUDING gate-blocked coefficients
elig = res[~res.collinearity_gate]
adj, rej = benjamini_hochberg(elig.p_raw.tolist())
res.loc[elig.index, "p_fdr"] = adj
res.loc[elig.index, "fdr_rejected"] = rej
res["fdr_rejected"] = res.fdr_rejected.fillna(False).infer_objects(copy=False).astype(bool)

res["boot_p"], res["loo_sign_stable"] = np.nan, False
for i, r in res.iterrows():
    if not r.fdr_rejected:
        continue
    d = panel.dropna(subset=[r.focal, r.controlling_for, "subjective_poverty", "arop"])
    res.at[i, "boot_p"] = wild_boot(r.joint_formula, d, r.focal, r.restricted, 20250828 + i)
    cs = np.array([fit(r.joint_formula, d[d.geo != g]).params[r.focal]
                   for g in sorted(d.geo.unique())])
    res.at[i, "loo_sign_stable"] = bool((np.sign(cs) == np.sign(cs[0])).all())

outs, gates = [], []
for r in res.itertuples():
    if r.collinearity_gate:
        outs.append("uninterpretable_collinear"); gates.append("collinearity")
        continue
    m = r.conditional_mde_sd if r.conditional_mde_sd == r.conditional_mde_sd else None
    o, _, g = decide(coefficient=r.coef_joint, adverse=r.adverse,
                     fdr_rejected=bool(r.fdr_rejected),
                     bootstrap_p=None if np.isnan(r.boot_p) else float(r.boot_p),
                     loo_sign_stable=bool(r.loo_sign_stable),
                     greece_residual_improves=bool(r.greece_improves),
                     proximity_violation=False,
                     ci_abs_std_upper=float(r.ci_abs_std_upper),
                     mde_sd=m if m else 99.0)
    # A fragile MDE cannot support a strong exclusion claim.
    if o == "unsupported_with_adequate_power" and r.mde_fragile:
        o, g = "inconclusive_under_available_power", "power"
    outs.append(o); gates.append(g)
res["outcome"], res["failed_gate"] = outs, gates

# ---- THE CEILING, ENFORCED IN CODE --------------------------------------
# The pre-registration: "E7 may still only QUALIFY or WITHDRAW. A conditional
# coefficient cannot create support for a construct that E1 and E4 did not
# already support." Stating that in prose did not enforce it -- P2's
# accumulated wage shortfall came back `supported` conditionally while E4 had
# recorded it inconclusive, which would have been E7 creating a finding.
prior = {}
for v in res.focal.unique():
    if v in e4.index:
        prior[v] = e4.loc[v, "outcome"]
    elif v in e1.index:
        prior[v] = e1.loc[v, "outcome"]
    else:
        prior[v] = "not tested"
res["prior_outcome"] = res.focal.map(prior)
res["ceiling_applied"] = ((res.outcome == "supported")
                          & (res.prior_outcome != "supported"))
res["reportable_outcome"] = np.where(
    res.ceiling_applied, "capped_by_ceiling_cannot_create_support", res.outcome)
capped = res[res.ceiling_applied]
if len(capped):
    print(f"\n  CEILING APPLIED to {len(capped)} coefficient(s): conditionally")
    print("  supported, but the prior stage did not support them, so E7 may not")
    print("  create the finding. The conditional result stays visible.")
    for r in capped.itertuples():
        print(f"    {r.pair:18} {r.focal:26} E7 supported, prior = {r.prior_outcome}")


print(f"  {'pair':18} {'direction':22} {'coef':>10} {'p_FDR':>8} {'boot':>7} "
      f"{'VIF':>6} {'MDE':>5}  outcome")
for r in res.itertuples():
    d_lab = "acc | cur" if r.focal.startswith(("acc_", "dur_")) else "cur | acc"
    pf = "  --  " if r.p_fdr != r.p_fdr else f"{r.p_fdr:.4f}"
    bp = "  --  " if np.isnan(r.boot_p) else f"{r.boot_p:.4f}"
    md = f"{r.conditional_mde_sd:.2f}" if r.conditional_mde_sd == r.conditional_mde_sd else " -- "
    print(f"  {r.pair:18} {d_lab + ' ' + r.focal[:12]:22} {r.coef_joint:+10.4f} {pf:>8} "
          f"{bp:>7} {r.focal_vif:6.2f} {md:>5}  {r.reportable_outcome}"
          f"{'  [MDE fragile]' if r.mde_fragile else ''}")

# ---- pair verdicts ------------------------------------------------------
print(f"\n{bar}\nPAIR VERDICTS\n{bar}")
verdicts = []
for pid in res.pair.unique():
    sub = res[res.pair == pid]
    a = sub[sub.focal.str.startswith(("acc_", "dur_"))].iloc[0]
    c = sub[~sub.focal.str.startswith(("acc_", "dur_"))].iloc[0]
    ao, co = a.reportable_outcome, c.reportable_outcome
    if a.collinearity_gate:
        v = "collinearity_gate: the data cannot separate current from accumulated"
    elif ao == "supported" and co == "supported":
        v = "BOTH SURVIVE: they capture distinct information"
    elif ao == "supported":
        v = ("ACCUMULATION ADDS: additional cross-country information after the "
             "current measure is controlled; the current measure is inconclusive, "
             "NOT ruled out")
    elif co == "supported":
        v = ("CURRENT SURVIVES CONDITIONING; the accumulated measure is "
             "INCONCLUSIVE, not unsupported with adequate power")
    elif "capped_by_ceiling_cannot_create_support" in (ao, co):
        v = ("CAPPED: a conditional coefficient cleared every gate but its prior "
             "stage did not support it; E7 may not create the finding")
    elif "unsupported_with_adequate_power" in (a.outcome, c.outcome):
        v = "NEITHER SURVIVES, adequate power for at least one direction"
    else:
        v = "UNRESOLVED: neither survives and power is insufficient"
    verdicts.append({"pair": pid, "construct": a.construct, "verdict": v,
                     "acc_outcome": a.reportable_outcome,
                     "cur_outcome": c.reportable_outcome,
                     "acc_raw_outcome": a.outcome, "cur_raw_outcome": c.outcome,
                     "acc_prior": a.prior_outcome, "cur_prior": c.prior_outcome})
    print(f"  {pid:18} {v}")

print(f"\n{bar}\nDYNAMIC EVIDENCE (conditional)\n{bar}")
print("  Mundlak with the CURRENT measure controlled, and conditional first")
print("  differences. E4's separate-model decomposition does NOT satisfy this.")
print("  These eight tests are a RESTRICTION CHECK, not a discovery family, and")
print("  are NOT multiplicity-corrected -- so any 'significant' below is")
print("  NOMINALLY significant.\n")
print(f"  {'pair':18} {'acc between':>12} {'p':>8} {'acc within':>11} {'p':>8} "
      f"{'FD acc':>9} {'p':>8}  dynamic?")
dyn_rows = []
for pr in PAIRS:
    cur, acc, pid = pr["current"], pr["accumulated"], pr["id"]
    d = panel.dropna(subset=[cur, acc, "subjective_poverty", "arop"]).sort_values(["geo", "time"]).copy()
    d["acc_between"] = d.groupby("geo")[acc].transform("mean")
    d["acc_within"] = d[acc] - d["acc_between"]
    mm = fit(f"{BASE} + {cur} + acc_between + acc_within", d)
    for c_ in ["subjective_poverty", cur, acc, "arop"]:
        d["d_" + c_] = d.groupby("geo")[c_].diff()
    dd = d.dropna(subset=["d_subjective_poverty", "d_" + cur, "d_" + acc, "d_arop"])
    fd = fit(f"d_subjective_poverty ~ d_{cur} + d_{acc} + d_arop + C(time)", dd)
    ok = (fd.pvalues[f"d_{acc}"] < 0.05
          and np.sign(fd.params[f"d_{acc}"]) > 0)
    print(f"  {pid:18} {mm.params['acc_between']:+12.4f} {mm.pvalues['acc_between']:8.4f} "
          f"{mm.params['acc_within']:+11.4f} {mm.pvalues['acc_within']:8.4f} "
          f"{fd.params['d_' + acc]:+9.4f} {fd.pvalues['d_' + acc]:8.4f}  "
          f"{'YES' if ok else 'no':>8}")
    dyn_rows.append({"pair": pid, "acc_between": mm.params["acc_between"],
                     "acc_between_p": mm.pvalues["acc_between"],
                     "acc_within": mm.params["acc_within"],
                     "acc_within_p": mm.pvalues["acc_within"],
                     "fd_acc": fd.params["d_" + acc], "fd_acc_p": fd.pvalues["d_" + acc],
                     "fd_n": len(dd), "dynamic_permitted": bool(ok)})

dyn = pd.DataFrame(dyn_rows)
print(f"\n  Dynamic wording permitted for: "
      f"{', '.join(dyn[dyn.dynamic_permitted].pair) if dyn.dynamic_permitted.any() else 'NONE'}")

res.drop(columns=["joint_formula", "restricted"]).to_csv(PROC / "e7_results.csv", index=False)
pd.DataFrame(verdicts).to_csv(PROC / "e7_verdicts.csv", index=False)
dyn.to_csv(PROC / "e7_dynamic.csv", index=False)
print(f"\nWritten to {PROC}/e7_results.csv, e7_verdicts.csv, e7_dynamic.csv")
