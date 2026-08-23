"""E4: accumulated exposure. BH family 2, pre-registered at a747e7a.

Runs the five decisive comparisons:

  1. current level versus accumulated exposure ON IDENTICAL SAMPLES
  2. accumulated loss against countries' own past (C3)
  3. accumulated inflation versus annual inflation (C5)
  4. FIRST DIFFERENCES before any dynamic interpretation
  5. FDR within the pre-registered accumulation family

And carries the discipline that governs all of it: a strong accumulated
cross-country association may identify long-run country differences without
showing that hardship rose within Greece as exposure accumulated. Every
accumulated result therefore gets a between/within decomposition, and no
dynamic wording is permitted unless first differences support it.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_rule import decide, benjamini_hochberg, direction_ok, MDE_SD

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
GR = "EL"
BASE = "subjective_poverty ~ arop + C(time)"

panel = pd.read_csv(PROC / "e4_accumulated_panel.csv")
feas = pd.read_csv(PROC / "e4_feasibility.csv")

# construct, accumulated column, its current-level counterpart, adverse direction
TESTS = [
    ("C2", "acc_cum_excess_unemployment", "ltu_rate", "higher_is_worse"),
    ("C3", "acc_real_wages_shortfall", "real_wages_idx", "higher_is_worse"),
    ("C3", "acc_pct_below_peak", "pct_below_peak", "higher_is_worse"),
    ("C3", "acc_threshold_shortfall", "arop_threshold_real", "higher_is_worse"),
    ("C4", "acc_wadj_excess", "wadj_a01", "higher_is_worse"),
    ("C5", "acc_hicp_compounded", "hicp", "higher_is_worse"),
    ("C6", "acc_housing_excess", "housing_cost_overburden", "higher_is_worse"),
]
DURATIONS = [("C3", "dur_real_wages_below", "higher_is_worse")]

# Outside BH family 2. The mixed-baseline threshold series cannot be the
# primary (the pre-registration fixes 2008 and Croatia falls back to 2010), so
# it is reported as a sensitivity and is NOT corrected with the family.
SENSITIVITIES = [("C3", "acc_threshold_shortfall_mixed", "higher_is_worse")]


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
    n_ex = int(np.sum(np.array(ts) >= abs(t_obs)))
    return float((n_ex + 1) / (reps + 1)), n_ex


def mundlak(d, var):
    """Between/within decomposition. The between term is the country mean; the
    within term is the deviation from it."""
    x = d.copy()
    x["_m"] = x.groupby("geo")[var].transform("mean")
    x["_w"] = x[var] - x["_m"]
    m = smf.ols(f"subjective_poverty ~ arop + C(time) + _m + _w",
                data=x).fit(cov_type="cluster", cov_kwds={"groups": x["geo"]})
    ci = m.conf_int().loc["_w"]
    return (float(m.params["_m"]), float(m.pvalues["_m"]),
            float(m.params["_w"]), float(m.pvalues["_w"]),
            float(ci[0]), float(ci[1]))


def first_difference(d, var):
    """Do YEAR-ON-YEAR changes move together? Required before dynamic wording."""
    x = d.sort_values(["geo", "time"]).copy()
    x["d_y"] = x.groupby("geo")["subjective_poverty"].diff()
    x["d_x"] = x.groupby("geo")[var].diff()
    x["d_a"] = x.groupby("geo")["arop"].diff()
    x = x.dropna(subset=["d_y", "d_x", "d_a"])
    if len(x) < 30:
        return np.nan, np.nan, len(x)
    m = smf.ols("d_y ~ d_x + d_a + C(time)", data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["geo"]})
    return float(m.params["d_x"]), float(m.pvalues["d_x"]), len(x)


bar = "=" * 100
print(bar); print("E4: ACCUMULATED EXPOSURE"); print(bar)
print(f"  feasible: {int(feas.feasible.sum())} of {len(feas)} pre-registered accumulations")
print(f"  INFEASIBLE, reported as such: {', '.join(feas[~feas.feasible].variable)}\n")

rows = []
for cid, acc, cur, adv in TESTS + [(c, v, None, a) for c, v, a in DURATIONS]:
    if acc not in panel.columns:
        print(f"  SKIP {acc}: not built")
        continue
    d = panel.dropna(subset=[acc, "subjective_poverty", "arop"])
    f = f"{BASE} + {acc}"
    m, m0 = fit(f, d), fit(BASE, d)
    ci = m.conf_int().loc[acc]
    sd_x, rsd = d[acc].std(), float(np.std(m0.resid, ddof=1))
    rows.append({"construct": cid, "var": acc, "counterpart": cur, "adverse": adv,
                 "coef": m.params[acc], "se": m.bse[acc], "p_raw": m.pvalues[acc],
                 "std_effect": abs(m.params[acc]) * sd_x / rsd,
                 "ci_abs_std_upper": max(abs(ci[0]), abs(ci[1])) * sd_x / rsd,
                 "greece_improves": bool(abs(greece_residual(f, d))
                                         < abs(greece_residual(BASE, d))),
                 "n": len(d), "formula": f, "is_duration": cur is None})

res = pd.DataFrame(rows)
adj, rej = benjamini_hochberg(res.p_raw.tolist())
res["p_fdr"], res["fdr_rejected"] = adj, rej

print(f"{bar}\n1 & 5. BH FAMILY 2: ACCUMULATED PRIMARIES\n{bar}")
res["boot_p"], res["loo_sign_stable"] = np.nan, False
res["boot_exceedances"], res["bootstrap_borderline"] = np.nan, False
for i, r in res.iterrows():
    if not r.fdr_rejected:
        continue
    d = panel.dropna(subset=[r["var"], "subjective_poverty", "arop"])
    bp, n_ex = wild_bootstrap(r.formula, d, r["var"], 20250825 + i)
    res.at[i, "boot_p"] = bp
    res.at[i, "boot_exceedances"] = n_ex
    # A result at p=0.046 is not as secure as one at p=0.0025, though the
    # pre-registered rule classes both as supported. Flagged, never reclassified,
    # and NEVER re-run with another seed to obtain a friendlier number.
    res.at[i, "bootstrap_borderline"] = bool(0.025 < bp <= 0.05)
    cs = np.array([fit(r.formula, d[d.geo != g]).params[r["var"]]
                   for g in sorted(d.geo.unique())])
    res.at[i, "loo_sign_stable"] = bool((np.sign(cs) == np.sign(cs[0])).all())

outs, gates = [], []
for r in res.itertuples():
    o, notes, gate = decide(
        coefficient=r.coef, adverse=r.adverse, fdr_rejected=bool(r.fdr_rejected),
        bootstrap_p=None if np.isnan(r.boot_p) else float(r.boot_p),
        loo_sign_stable=bool(r.loo_sign_stable),
        greece_residual_improves=bool(r.greece_improves),
        proximity_violation=False, ci_abs_std_upper=float(r.ci_abs_std_upper))
    outs.append(o); gates.append(gate)
res["outcome"], res["failed_gate"] = outs, gates

print(f"  {'con':>4} {'accumulated':30} {'coef':>10} {'p_raw':>7} {'p_FDR':>7} "
      f"{'boot':>7} {'SD':>5} {'n':>4}  outcome")
for r in res.sort_values("p_raw").itertuples():
    bp = "  --  " if np.isnan(r.boot_p) else f"{r.boot_p:.4f}"
    print(f"  {r.construct:>4} {r.var:30} {r.coef:+10.4f} {r.p_raw:7.4f} "
          f"{r.p_fdr:7.4f} {bp:>7} {r.std_effect:5.2f} {r.n:4d}  {r.outcome}"
          f"{'' if not r.failed_gate else '  [' + r.failed_gate + ']'}"
          f"{'  BORDERLINE' if r.bootstrap_borderline else ''}")

# ---- mixed-baseline threshold SENSITIVITY, outside family 2 ---------------
print(f"\n{bar}\nSENSITIVITY: mixed-baseline threshold, NOT in BH family 2\n{bar}")
print("  The pre-registration fixes baseline 2008. Croatia has no 2008")
print("  observation and falls back to 2010, so the 27-country series is not a")
print("  uniform-baseline test and cannot carry the primary. Shown for comparison;")
print("  NOT FDR-corrected with the family and cannot change any status.\n")
sens_rows = []
for cid, v, adv in SENSITIVITIES:
    if v not in panel.columns:
        continue
    d = panel.dropna(subset=[v, "subjective_poverty", "arop"])
    m = fit(f"{BASE} + {v}", d)
    prim = res[res["var"] == "acc_threshold_shortfall"]
    pc = float(prim.coef.iloc[0]) if len(prim) else float("nan")
    pp = float(prim.p_raw.iloc[0]) if len(prim) else float("nan")
    print(f"  {'primary (26 countries, uniform 2008)':44} coef {pc:+8.4f}  p {pp:.4f}")
    print(f"  {'sensitivity (27, mixed baseline)':44} coef {m.params[v]:+8.4f}  "
          f"p {m.pvalues[v]:.4f}  n={len(d)}")
    sens_rows.append({"construct": cid, "var": v, "coef": m.params[v],
                      "se": m.bse[v], "p_raw": m.pvalues[v], "n": len(d),
                      "in_bh_family": False,
                      "note": "mixed baseline: 2008 for 26 countries, 2010 for HR"})
pd.DataFrame(sens_rows).to_csv(PROC / "e4_threshold_sensitivity.csv", index=False)

# ---- 1. current vs accumulated, EQUAL SAMPLES -----------------------------
print(f"\n{bar}\n1. CURRENT VERSUS ACCUMULATED, ON IDENTICAL OBSERVATIONS\n{bar}")
print(f"  {'con':>4} {'current':26} {'accumulated':30} {'cur coef':>10} "
      f"{'acc coef':>10} {'cur p':>8} {'acc p':>8} {'n':>5}")
cmp_rows = []
for cid, acc, cur, adv in TESTS:
    if acc not in panel.columns or cur not in panel.columns:
        continue
    d = panel.dropna(subset=[acc, cur, "subjective_poverty", "arop"])
    mc, ma = fit(f"{BASE} + {cur}", d), fit(f"{BASE} + {acc}", d)
    rc, ra = greece_residual(f"{BASE} + {cur}", d), greece_residual(f"{BASE} + {acc}", d)
    print(f"  {cid:>4} {cur:26} {acc:30} {mc.params[cur]:+10.4f} "
          f"{ma.params[acc]:+10.4f} {mc.pvalues[cur]:8.4f} {ma.pvalues[acc]:8.4f} {len(d):5d}")
    cmp_rows.append({"construct": cid, "current": cur, "accumulated": acc,
                     "n_common": len(d), "cur_coef": mc.params[cur],
                     "acc_coef": ma.params[acc], "cur_p": mc.pvalues[cur],
                     "acc_p": ma.pvalues[acc], "cur_greece_resid": rc,
                     "acc_greece_resid": ra,
                     "accumulated_better": bool(abs(ra) < abs(rc))})

# ---- 3. accumulated inflation vs annual inflation -------------------------
print(f"\n{bar}\n3. ACCUMULATED INFLATION VERSUS ANNUAL INFLATION\n{bar}")
c5 = [r for r in cmp_rows if r["construct"] == "C5"]
for r in c5:
    print(f"  annual   `hicp`                 coef {r['cur_coef']:+8.4f}  p {r['cur_p']:.4f}")
    print(f"  compound `acc_hicp_compounded`  coef {r['acc_coef']:+8.4f}  p {r['acc_p']:.4f}")
    print(f"  identical sample n = {r['n_common']}")
    print("  Compounded inflation is cumulative PRICE GROWTH, not affordability")
    print("  and not hardship. Affordability is C4's separate question.")

# ---- 4. between/within and FIRST DIFFERENCES ------------------------------
print(f"\n{bar}\n2 & 4. BETWEEN/WITHIN AND FIRST DIFFERENCES\n{bar}")
print("  A strong between-country association does NOT show that hardship rose")
print("  within Greece as exposure accumulated. First differences decide whether")
print("  any dynamic wording is permitted.\n")
print(f"  {'accumulated':30} {'between':>9} {'p':>8} {'within':>9} {'p':>8} "
      f"{'FD coef':>9} {'FD p':>7} {'dynamic?':>9}")
for r in res.itertuples():
    d = panel.dropna(subset=[r.var, "subjective_poverty", "arop"])
    b, bp, w, wp, wlo, whi = mundlak(d, r.var)
    fd, fdp, fdn = first_difference(d, r.var)
    dynamic = (not np.isnan(fdp)) and fdp < 0.05 and direction_ok(fd, r.adverse)
    print(f"  {r.var:30} {b:+9.4f} {bp:8.4f} {w:+9.4f} {wp:8.4f} "
          f"{fd:+9.4f} {fdp:7.4f} {'YES' if dynamic else 'no':>9}")
    res.loc[res["var"] == r.var, ["between", "between_p", "within", "within_p",
                              "within_ci_lo", "within_ci_hi", "fd_coef",
                              "fd_p", "fd_n", "dynamic_permitted"]] = \
        [b, bp, w, wp, wlo, whi, fd, fdp, fdn, dynamic]

print(f"\n{bar}\nSUMMARY\n{bar}")
for o in res.outcome.value_counts().index:
    vs = res[res.outcome == o]["var"].tolist()
    print(f"  {o:38} {len(vs)}  {', '.join(vs)}")
dyn = res[res["dynamic_permitted"] == True]["var"].tolist()
print(f"\n  Dynamic wording permitted for: {', '.join(dyn) if dyn else 'NONE'}")
if not dyn:
    print("  No accumulated result may be described as hardship rising within a")
    print("  country as exposure accumulated. Between-country markers only.")

res.drop(columns=["formula"]).to_csv(PROC / "e4_results.csv", index=False)
pd.DataFrame(cmp_rows).to_csv(PROC / "e4_current_vs_accumulated.csv", index=False)
print(f"\nWritten to {PROC}/e4_results.csv, e4_current_vs_accumulated.csv")
