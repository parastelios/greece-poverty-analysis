"""P3a steps 2-8: Family D, accumulated multi-domain deterioration.

Universe, domains, weights, baseline and FDR family frozen at 4e5d54a in
data/processed/p3a_frozen_universe.json, before this script ran.

Exploratory throughout. Family D cannot strengthen P3's evidentiary tier
whatever it returns; P3 is frozen at p5f-frozen.
"""
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.path.insert(0, ".")
from outcome import official_hardship
from eu_membership import eu_members
from validate_outputs import scalar

OUT = "../data/processed"
FZ = json.load(open(f"{OUT}/p3a_frozen_universe.json"))
SERIES = json.load(open(f"{OUT}/appendix_series_core.json"))["series"]
src = open("46_appendix_data.py").read()
WORSE_HIGH = eval("{" + src.split("WORSE_HIGH = {")[1].split("}")[0] + "}")
M = sorted(eu_members(2025))
V = "cum_excess_unemployment"
P3 = ["severe_mat_soc_deprivation", "housing_cost_overburden", "ltu_rate",
      "aic_pps_pc_k", "wage_years_below_2008", V]
print(f"Frozen universe: {FZ['status']}\n")


def flags(key):
    v, hi = SERIES[key], WORSE_HIGH[key]
    rows = []
    for i, y in enumerate(v["years"]):
        vals = {c: s[i] for c, s in v["countries"].items() if s[i] is not None and c in M}
        if len(vals) < 20:
            continue
        pct = pd.Series(vals).rank(pct=True)
        f = (pct >= 0.80) if hi else (pct <= 0.20)
        rows += [dict(geo=c, time=int(y), series=key, worst=int(f[c])) for c in vals]
    return pd.DataFrame(rows)


def accumulate(frame, value_col="breadth"):
    """Excess over own 2008-09 baseline, floored at zero, cumulated."""
    b = (frame[frame.time.between(2008, 2009)].groupby("geo", as_index=False)[value_col]
         .mean().rename(columns={value_col: "_b0"}))
    d = frame.merge(b, on="geo").sort_values(["geo", "time"])
    d["_ex"] = (d[value_col] - d["_b0"]).clip(lower=0)
    d["acc"] = d.groupby("geo")["_ex"].cumsum()
    return d[["geo", "time", "acc"]]


def composite(keys, name):
    """Equal weight WITHIN domain, then equal weight ACROSS domains."""
    dom = {k: g for g, ks in FZ["domains"].items() for k in ks}
    f = pd.concat([flags(k).assign(domain=dom[k]) for k in keys if k in SERIES])
    per_dom = f.groupby(["geo", "time", "domain"], as_index=False)["worst"].mean()
    br = per_dom.groupby(["geo", "time"], as_index=False).agg(
        breadth=("worst", "mean"), n_dom=("domain", "nunique"))
    br = br[br.n_dom >= 4]
    return accumulate(br).rename(columns={"acc": name})


p = pd.read_csv(f"{OUT}/persistence_share_panel.csv")
off = official_hardship().rename(columns={"value": "hardship"})[["geo", "time", "hardship"]]
arop = p[["geo", "time", "arop"]]
panel = p.merge(off, on=["geo", "time"], how="left")
panel["hardship_gap"] = panel["hardship"] - panel["arop"]
for nm, keys in [("famD", FZ["variants"]["primary_objective_only"]),
                 ("famD_all", FZ["variants"]["sensitivity_all_indicators"]),
                 ("famD_nolab", FZ["variants"]["sensitivity_non_labour"])]:
    panel = panel.merge(composite(keys, nm), on=["geo", "time"], how="left")
panel = panel.query("2015 <= time <= 2024")


def loo(vars_, dat, outcome="hardship"):
    d = dat.dropna(subset=vars_ + [outcome]).copy()
    f = f"{outcome} ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    rows = []
    for c in sorted(d.geo.unique()):
        tr, te = d[d.geo != c], d[d.geo == c].copy()
        mc = smf.ols(f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        rows.append({"geo": c, "r": (te[outcome] - mc.predict(te)).mean()})
    l = pd.DataFrame(rows).sort_values("r", ascending=False).reset_index(drop=True)
    g = l[l.geo == "EL"].iloc[0]
    return m, d, float(g["r"]), int(l[l.geo == "EL"].index[0]) + 1, len(l)


# ---------------------------------------------------------- STEP 2: individual ----
print("=" * 74); print("STEP 2: INDIVIDUAL ACCUMULATED INDICATORS, FDR-CORRECTED"); print("=" * 74)
base_vars = [v for v in P3 if v != V]     # minimal common baseline for screening
rows = []
for k in FZ["variants"]["primary_objective_only"]:
    ind = accumulate(flags(k).groupby(["geo", "time"], as_index=False)["worst"].mean()
                     .rename(columns={"worst": "breadth"})).rename(columns={"acc": "x"})
    dd = panel.merge(ind, on=["geo", "time"], how="left")
    for oc in ["hardship", "hardship_gap"]:
        try:
            m, d, gap, rk, n = loo(base_vars + ["x"], dd, oc)
            rows.append({"indicator": k, "outcome": oc,
                         "coef": scalar(m.params["x"], "coefficient", k),
                         "p_raw": scalar(m.pvalues["x"], "p_value", k),
                         "greece_resid": scalar(gap, "residual", k), "rank": rk})
        except Exception as e:
            rows.append({"indicator": k, "outcome": oc, "coef": None,
                         "p_raw": None, "greece_resid": None, "rank": None})
ind_df = pd.DataFrame(rows).dropna(subset=["p_raw"])
for oc in ["hardship", "hardship_gap"]:
    sub = ind_df[ind_df.outcome == oc].copy()
    sub["p_fdr"] = multipletests(sub.p_raw.values, alpha=0.05, method="fdr_bh")[1]
    sub["sig"] = sub.p_fdr < 0.05
    ind_df.loc[sub.index, ["p_fdr", "sig"]] = sub[["p_fdr", "sig"]]
    s = sub.sort_values("p_raw")
    print(f"\n  outcome = {oc}: {int(sub.sig.sum())} of {len(sub)} survive FDR")
    print(s.head(6)[["indicator", "coef", "p_raw", "p_fdr", "sig"]].round(4).to_string(index=False))
ind_df.to_csv(f"{OUT}/p3a_individual_indicators.csv", index=False)

# ---------------------------------------------------------- STEPS 3-5: composite ----
print("\n" + "=" * 74); print("STEP 3: COMPOSITE ALONE (minimal baseline)"); print("=" * 74)
res = []
for oc in ["hardship", "hardship_gap"]:
    m, d, gap, rk, n = loo(["arop", "famD"], panel, oc)
    print(f"  {oc:14} famD {m.params['famD']:+8.4f} (p {m.pvalues['famD']:.4f})  "
          f"Greece {gap:+6.2f}, rank {rk}/{n}")
    res.append({"step": "alone", "outcome": oc, "coef": float(m.params["famD"]),
                "p": float(m.pvalues["famD"]), "greece": gap, "rank": rk})

print("\n" + "=" * 74); print("STEP 4-5: ADDED TO THE FROZEN P3 SPECIFICATION"); print("=" * 74)
m0, d0, g0, r0, n0 = loo(P3, panel)
print(f"  frozen P3 alone:            Greece {g0:+6.2f}, rank {r0}/{n0}, R2 {m0.rsquared:.3f}")
m1, d1, g1, r1, n1 = loo(P3 + ["famD"], panel)
print(f"  frozen P3 + famD:           Greece {g1:+6.2f}, rank {r1}/{n1}, R2 {m1.rsquared:.3f}")
print(f"    famD coefficient {m1.params['famD']:+.4f} (se {m1.bse['famD']:.4f}, p {m1.pvalues['famD']:.4f})")
print(f"    {V} moves {m0.params[V]:+.4f} -> {m1.params[V]:+.4f} "
      f"({100*(m1.params[V]-m0.params[V])/abs(m0.params[V]):+.0f}%)")
X = d1[P3 + ["famD"]].astype(float)
vif = {c: variance_inflation_factor(X.values, i) for i, c in enumerate(X.columns)}
print(f"    VIF famD {vif['famD']:.2f} | {V} {vif[V]:.2f}")
coefs = []
for c in sorted(d1.geo.unique()):
    mc = smf.ols(f"hardship ~ " + " + ".join(P3 + ["famD"]) + " + C(time)",
                 data=d1[d1.geo != c]).fit()
    coefs.append(mc.params["famD"])
coefs = np.array(coefs)
print(f"    famD across 27 LOO folds: {coefs.min():+.4f} to {coefs.max():+.4f}, "
      f"sign stable {bool((np.sign(coefs)==np.sign(coefs[0])).all())}")
print(f"    corr(famD, {V}) = {d1['famD'].corr(d1[V]):+.3f}")

incremental = (abs(g1) < abs(g0)) and (m1.pvalues["famD"] < 0.05)
print(f"\n  INCREMENTAL VALUE? {'YES' if incremental else 'NO'} "
      f"(needs p<0.05 AND a smaller |residual| than {g0:+.2f})")

# ---------------------------------------------------------- STEP 6: within/between ----
print("\n" + "=" * 74); print("STEP 6: MANDATORY WITHIN/BETWEEN AUDIT"); print("=" * 74)
if incremental:
    dm = d1.copy()
    dm["famD_bar"] = dm.groupby("geo")["famD"].transform("mean")
    dm["famD_dev"] = dm["famD"] - dm["famD_bar"]
    fm = ("hardship ~ " + " + ".join(P3) + " + famD_dev + famD_bar + C(time)")
    mu = smf.ols(fm, data=dm).fit(cov_type="cluster", cov_kwds={"groups": dm["geo"]})
    print(f"  WITHIN  {mu.params['famD_dev']:+.4f} (p {mu.pvalues['famD_dev']:.4f})")
    print(f"  BETWEEN {mu.params['famD_bar']:+.4f} (p {mu.pvalues['famD_bar']:.4f})")
else:
    print("  NOT RUN: the audit is mandatory only if Family D shows incremental")
    print("  value. It does not, so there is no dynamic interpretation to guard.")

# ---------------------------------------------------------- STEP 7: sensitivities ----
print("\n" + "=" * 74); print("STEP 7: FROZEN SENSITIVITIES"); print("=" * 74)
for nm, lbl in [("famD_all", "all-indicator"), ("famD_nolab", "non-labour")]:
    m2, d2, g2, r2, n2 = loo(P3 + [nm], panel)
    print(f"  {lbl:14} coef {m2.params[nm]:+8.4f} (p {m2.pvalues[nm]:.4f})  "
          f"Greece {g2:+6.2f}, rank {r2}/{n2}")
    res.append({"step": f"sensitivity_{nm}", "outcome": "hardship",
                "coef": float(m2.params[nm]), "p": float(m2.pvalues[nm]),
                "greece": g2, "rank": r2})

res.append({"step": "frozen_P3", "outcome": "hardship", "coef": float(m0.params[V]),
            "p": float(m0.pvalues[V]), "greece": g0, "rank": r0})
res.append({"step": "P3_plus_famD", "outcome": "hardship", "coef": float(m1.params["famD"]),
            "p": float(m1.pvalues["famD"]), "greece": g1, "rank": r1})
pd.DataFrame(res).to_csv(f"{OUT}/p3a_results.csv", index=False)
print(f"\nWritten to {OUT}/p3a_*.csv")
print("\nSTEP 8: Family D remains EXPLORATORY. P3 stays frozen at post-selection")
print("robustness regardless of what appears above.")
