"""E5: accumulation sensitivities.

PURPOSE: test whether reasonable alternative constructions QUALIFY E4's
conclusions. NOT to search for replacements where a primary failed.

TWO CLASSES OF SENSITIVITY, KEPT APART.

  DECLARED     named in the frozen construct map before any result existed.
               Exactly one: C2's cum_excess_ltu.
  ALTERNATIVE  a different reasonable construction of the same quantity,
               identified AFTER E4. These are legitimate as qualification and
               are worthless as discovery, because the set was chosen knowing
               which primaries had succeeded.

Neither class can promote. e_rule.sensitivity_disposition() has no code path
returning a finding from a sensitivity, so the C3 depth measures and compounded
inflation cannot be promoted however their alternatives behave.

Housing's BORDERLINE status is carried through unchanged. A sensitivity that
happens to land at a smaller p does not make the primary less borderline: the
primary's own bootstrap was 0.0460, and that is the number that describes it.

FDR grouping is within construct, which is NOT pre-registered -- the frozen
document names three families and no within-construct sensitivity family. This
is the same deviation recorded as PD-01 at E2, applying again here. The pooled
alternative is reported below.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_rule import (decide, benjamini_hochberg, sensitivity_disposition, MDE_SD)

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
GR = "EL"
BASE = "subjective_poverty ~ arop + C(time)"

panel = pd.read_csv(PROC / "e4_accumulated_panel.csv")
e4 = pd.read_csv(PROC / "e4_results.csv").set_index("var")
frozen = pd.read_csv(PROC / "cumulative_hardship_candidate_panel.csv")
for c in [c for c in frozen.columns if c not in panel.columns and c not in ("geo", "time")]:
    panel = panel.merge(frozen[["geo", "time", c]], on=["geo", "time"], how="left")

# primary -> [(sensitivity, class, what differs)]
PLAN = {
    "acc_cum_excess_unemployment": [
        ("cum_excess_ltu", "DECLARED", "long-term rather than total unemployment"),
    ],
    "dur_real_wages_below": [
        ("wage_years_below_peak", "ALTERNATIVE", "own rolling peak rather than fixed 2008"),
        ("wage_longest_streak_2008", "ALTERNATIVE", "longest run ever, not the current run"),
        ("wage_longest_streak_peak", "ALTERNATIVE", "longest run, own-peak basis"),
    ],
    "acc_real_wages_shortfall": [
        ("cum_wage_shortfall_ownpeak", "ALTERNATIVE", "own rolling peak rather than fixed 2008"),
    ],
    "acc_pct_below_peak": [
        ("cum_gdp_shortfall_2008base", "ALTERNATIVE", "fixed 2008 base rather than own peak"),
    ],
    "acc_hicp_compounded": [],   # see the note printed below
    "acc_housing_excess": [],    # see the note printed below
}
NO_SENSITIVITY = {
    "acc_housing_excess":
        "No alternative construction is available that is not a rebasing "
        "exercise. Trying other baselines until one performs better is the "
        "move the protocol exists to prevent, and the 2010 base is already "
        "forced by coverage.",
    "acc_hicp_compounded":
        "No accumulated inflation sensitivity was PRE-DECLARED. Constructing "
        "category-specific accumulated measures after the primary result was "
        "known would reopen exploratory searching. (E2 excluded ANNUAL food and "
        "housing inflation at one magnitude; it did not exclude every possible "
        "accumulated category measure, and citing it as though it had would "
        "overstate what that stage established.)",
}


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
        ts.append(abs(fit(f, db).params[var] / fit(f, db).bse[var]))
    n_ex = int(np.sum(np.array(ts) >= abs(t_obs)))
    return float((n_ex + 1) / (reps + 1)), n_ex


bar = "=" * 100
print(bar); print("E5: ACCUMULATION SENSITIVITIES"); print(bar)
print("  Purpose: QUALIFY E4's conclusions. Not to replace failed primaries.")
print("  No sensitivity can promote anything, whatever its own result.\n")

rows, seed = [], 20250826
for primary, sens in PLAN.items():
    if primary not in e4.index:
        continue
    p_out = e4.loc[primary, "outcome"]
    p_boot = e4.loc[primary, "boot_p"]
    borderline = bool(e4.loc[primary, "bootstrap_borderline"])
    print(f"\n{bar}")
    print(f"{primary}")
    print(f"  E4 primary: {p_out}"
          f"{f', bootstrap p={p_boot:.4f}' if p_boot == p_boot else ''}"
          f"{'  [BORDERLINE, and it stays borderline]' if borderline else ''}")
    if not sens:
        print(f"  NO SENSITIVITY RUN. {NO_SENSITIVITY[primary]}")
        rows.append({"primary": primary, "primary_outcome": p_out,
                     "primary_boot_p": p_boot, "primary_borderline": borderline,
                     "sensitivity": None, "sens_class": None,
                     "disposition": "none_available",
                     "note": NO_SENSITIVITY[primary]})
        continue

    members = [primary] + [s for s, _, _ in sens if s in panel.columns]
    common = panel.dropna(subset=members + ["subjective_poverty", "arop"])
    print(f"  common sample: {len(common)} rows, {common.geo.nunique()} countries\n")
    fits = []
    for v in members:
        f = f"{BASE} + {v}"
        m, m0 = fit(f, common), fit(BASE, common)
        ci = m.conf_int().loc[v]
        sd_x, rsd = common[v].std(), float(np.std(m0.resid, ddof=1))
        cls = "primary" if v == primary else \
            next(c for s, c, _ in sens if s == v)
        fits.append({"var": v, "class": cls,
                     "differs": "" if v == primary else next(d for s, _, d in sens if s == v),
                     "coef": m.params[v], "se": m.bse[v], "p_raw": m.pvalues[v],
                     "ci_abs_std_upper": max(abs(ci[0]), abs(ci[1])) * sd_x / rsd,
                     "greece_improves": bool(abs(greece_residual(f, common))
                                             < abs(greece_residual(BASE, common))),
                     "formula": f, "n": len(common)})
    fd = pd.DataFrame(fits)
    adj, rej = benjamini_hochberg(fd.p_raw.tolist())
    fd["p_fdr"], fd["fdr_rejected"] = adj, rej
    fd["boot_p"], fd["boot_ex"], fd["loo"] = np.nan, np.nan, False
    for i, r in fd.iterrows():
        if not r.fdr_rejected:
            continue
        seed += 1
        bp, nex = wild_bootstrap(r.formula, common, r["var"], seed)
        fd.at[i, "boot_p"], fd.at[i, "boot_ex"] = bp, nex
        cs = np.array([fit(r.formula, common[common.geo != g]).params[r["var"]]
                       for g in sorted(common.geo.unique())])
        fd.at[i, "loo"] = bool((np.sign(cs) == np.sign(cs[0])).all())

    print(f"  {'class':12} {'variable':28} {'coef':>10} {'p_FDR':>8} {'boot':>8} "
          f"{'outcome':36} disposition")
    for r in fd.itertuples():
        o, _, gate = decide(
            coefficient=r.coef, adverse="higher_is_worse",
            fdr_rejected=bool(r.fdr_rejected),
            bootstrap_p=None if np.isnan(r.boot_p) else float(r.boot_p),
            loo_sign_stable=bool(r.loo),
            greece_residual_improves=bool(r.greece_improves),
            proximity_violation=False, ci_abs_std_upper=float(r.ci_abs_std_upper))
        disp = "—" if r._2 == "primary" else sensitivity_disposition(p_out, o)
        bp = "   --   " if np.isnan(r.boot_p) else f"{r.boot_p:.4f}"
        print(f"  {r._2:12} {r.var:28} {r.coef:+10.4f} {r.p_fdr:8.4f} {bp:>8} "
              f"{o:36} {disp}")
        if r._2 != "primary":
            rows.append({"primary": primary, "primary_outcome": p_out,
                         "primary_boot_p": p_boot, "primary_borderline": borderline,
                         "sensitivity": r.var, "sens_class": r._2,
                         "differs": r.differs, "coef": r.coef, "se": r.se,
                         "p_raw": r.p_raw, "p_fdr": r.p_fdr, "boot_p": r.boot_p,
                         "outcome": o, "disposition": disp, "n": r.n})

res = pd.DataFrame(rows)
print(f"\n{bar}\nSUMMARY\n{bar}")
s = res[res.sensitivity.notna()]
for d_ in s.disposition.value_counts().index:
    vs = s[s.disposition == d_]["sensitivity"].tolist()
    print(f"  {d_:24} {len(vs):2}  {', '.join(vs)}")
promo = s[(s.outcome == "supported") & (s.disposition == "cannot_promote")]
print(f"\n  Sensitivities that would have been findings if the rule allowed it: {len(promo)}")
for r in promo.itertuples():
    print(f"    {r.sensitivity} (primary {r.primary} is {r.primary_outcome})")

print(f"\n  DECLARED sensitivities: {int((s.sens_class == 'DECLARED').sum())}")
print(f"  post-hoc ALTERNATIVES:  {int((s.sens_class == 'ALTERNATIVE').sum())}")
print("  Alternatives are qualification only. The set was chosen knowing which")
print("  primaries had succeeded, so it cannot support discovery.")

bl = res[res.primary_borderline == True]
if len(bl):
    print(f"\n  BORDERLINE PRIMARIES, unchanged by anything here: "
          f"{', '.join(sorted(set(bl.primary)))}")

res.to_csv(PROC / "e5_results.csv", index=False)
print(f"\nWritten to {PROC}/e5_results.csv")
