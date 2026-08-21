"""Checkpoint (family C): the worst-quintile idea rebuilt as a SHARE, and
applied across indicators rather than to one series.

Pre-registered in docs/publication_strategy.md before running. Family B counted
years in the worst quintile; that count grows with elapsed time and is not
comparable across series with different start years. This uses the share of
observed years spent in the EU's worst quintile since 2008 -- bounded 0 to 1,
1 meaning "at the bottom of the EU every single year".

Five per-series shares mirror the accumulation family's own underlying series,
so the comparison is like-for-like. The sixth is a composite across independent
indicators, built with a circularity guard that removes the outcome and every
Model C-LTU covariate.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from eu_membership import eu_members

OUT, ROOT = "../data/processed", ".."
BASE = 2008
Q = 0.20
MEMBERS = sorted(eu_members(2025))
vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]

series = json.load(open(f"{OUT}/appendix_series_core.json"))["series"]

# direction map: 1 = higher is worse. Derived cumulative/duration candidates are
# excluded (they are built from these same series), as are the 12 price
# sub-categories (near-duplicates of the two kept aggregates).
WORSE_HIGH = {
    'arop': 1, 'arope': 1, 'deprivation_new': 1, 'deprivation_legacy': 1, 's80s20': 1,
    'subjective_poverty': 1, 'arrears': 1, 'housing_overburden': 1, 'unexpected': 1,
    'warm': 1, 'unemployment': 1, 'ltu': 1, 'youth_unemployment': 1, 'debt_to_income': 1,
    'hicp': 1, 'hicp_food': 1, 'hicp_housing': 1, 'working_hours': 1,
    'work_effort_squeeze': 1, 'wadj_a01': 1, 'pct_below_peak': 1,
    'employment_rate': 0, 'hourly_comp': 0, 'income_pps': 0, 'real_gdp_pc': 0,
    'consumption_pc': 0, 'real_income_idx': 0, 'real_wages_idx': 0,
    'arop_threshold_real': 0, 'min_wage': 0, 'saving_rate': 0, 'life_satisfaction': 0,
    'fin_expectations': 0, 'transfer_effect': 0, 'net_migration': 0,
}
# the outcome plus every Model C-LTU covariate -- including these in the
# composite would predict subjective poverty partly from itself
CIRCULAR = {'subjective_poverty', 'arop', 'arope', 'deprivation_new',
            'deprivation_legacy', 'arrears', 'housing_overburden', 'unexpected',
            'ltu', 'income_pps'}
MIN_REPORTERS = 20


def worst_flags(key):
    """Per country-year: 1 if that country is in the EU's worst quintile that year."""
    v, hi = series[key], WORSE_HIGH[key]
    rows = []
    for i, y in enumerate(v["years"]):
        vals = {c: s[i] for c, s in v["countries"].items() if s[i] is not None}
        if len(vals) < MIN_REPORTERS:
            continue
        pct = pd.Series(vals).rank(pct=True)
        flag = (pct >= 1 - Q) if hi else (pct <= Q)
        for c in vals:
            rows.append({"geo": c, "time": int(y), "worst": int(flag[c])})
    return pd.DataFrame(rows)


def share_frame(key, out_col):
    """Cumulative share of observed years since BASE spent in the worst quintile."""
    f = worst_flags(key)
    f = f[(f.time >= BASE) & (f.geo.isin(MEMBERS))].sort_values(["geo", "time"])
    f["_n"] = f.groupby("geo").cumcount() + 1
    f[out_col] = f.groupby("geo")["worst"].cumsum() / f["_n"]
    return f[["geo", "time", out_col]]


PER_SERIES = [("unemployment", "share_worst_unemployment"),
              ("ltu", "share_worst_ltu"),
              ("real_wages_idx", "share_worst_real_wage"),
              ("real_gdp_pc", "share_worst_real_gdp"),
              ("arop_threshold_real", "share_worst_threshold")]

panel = pd.read_csv(f"{OUT}/direction_persistence_panel.csv")
for key, col in PER_SERIES:
    panel = panel.merge(share_frame(key, col), on=["geo", "time"], how="left")

# --- composite across independent indicators ---
indep = [k for k in WORSE_HIGH if k not in CIRCULAR and k in series]
print(f"Composite built from {len(indep)} independent indicators "
      f"(of {len(WORSE_HIGH)} classified; {len(CIRCULAR)} removed by the circularity guard)")
allf = pd.concat([worst_flags(k).assign(series=k) for k in indep])
comp = (allf[allf.geo.isin(MEMBERS)].groupby(["geo", "time"], as_index=False)
        .agg(n_ind=("series", "nunique"), n_worst=("worst", "sum")))
comp = comp[comp.n_ind >= 10].sort_values(["geo", "time"])
comp["share_worst_composite"] = comp.n_worst / comp.n_ind
panel = panel.merge(comp[["geo", "time", "share_worst_composite"]],
                    on=["geo", "time"], how="left")

CANDIDATES = [c for _, c in PER_SERIES] + ["share_worst_composite"]
panel.to_csv(f"{OUT}/persistence_share_panel.csv", index=False)

print("\n=== Greece's standing on each share, latest year ===")
for c in CANDIDATES:
    sub = panel.dropna(subset=[c]); yr = sub.time.max()
    s = sub[sub.time == yr].set_index("geo")[c].sort_values(ascending=False)
    rank = list(s.index).index("EL") + 1
    print(f"  {c:26} {int(yr)}: Greece {s['EL']:.2f}  rank {rank}/{len(s)}  "
          f"EU median {s.median():.2f}  top: " +
          ", ".join(f"{g}:{v:.2f}" for g, v in s.head(3).items()))

# --- the descriptive series the whole idea rests on ---
gr = comp[comp.geo == "EL"].sort_values("time")
print("\n=== Descriptive: share of independent indicators placing Greece in the worst quintile ===")
print("  " + "  ".join(f"{int(t)}:{v*100:.0f}%" for t, v in
                       zip(gr.time, gr.share_worst_composite) if t >= 2005))
pre = gr[gr.time.between(2005, 2010)].share_worst_composite.mean()
post = gr[gr.time >= 2012].share_worst_composite.mean()
print(f"  pre-crisis mean {pre*100:.0f}%  ->  2012 onward {post*100:.0f}%")
comp.to_csv(f"{OUT}/persistence_share_composite.csv", index=False)


def run_model(extra, panel, outcome="subjective_poverty"):
    vars_ = vars_c_ltu + extra
    d = panel.dropna(subset=vars_ + [outcome]).copy()
    f = f"{outcome} ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    rows = []
    for c in sorted(d.geo.unique()):
        tr, te = d[d.geo != c], d[d.geo == c].copy()
        mc = smf.ols(f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        rows.append({"geo": c, "resid": (te[outcome] - mc.predict(te)).mean()})
    loo = pd.DataFrame(rows).sort_values("resid", ascending=False).reset_index(drop=True)
    loo["rank"] = loo.index + 1
    g = loo[loo.geo == "EL"].iloc[0]
    return m, d, round(g["resid"], 2), f"{int(g['rank'])}/{len(loo)}"


_, _, base_gap, base_rank = run_model([], panel)
print(f"\n=== Baseline Model C-LTU: Greek out-of-sample gap {base_gap} (rank {base_rank}) ===")

res = []
for v in CANDIDATES:
    m, d, gap, rank = run_model([v], panel)
    res.append(dict(variable=v, r2=round(m.rsquared, 3), n=len(d), n_geo=d.geo.nunique(),
                    coef=round(float(m.params[v]), 4), p_raw=float(m.pvalues[v]),
                    gr_oos=gap, rank=rank))
df = pd.DataFrame(res).sort_values("p_raw").reset_index(drop=True)
df["p_fdr_bh"] = multipletests(df.p_raw.values, alpha=0.05, method="fdr_bh")[1]
df["sig_fdr"] = df.p_fdr_bh < 0.05
df["improves"] = df.gr_oos.abs() < abs(base_gap)

# pre-registered third condition: head-to-head against the existing survivor
SURV = "wage_years_below_2008"
head = []
for v in CANDIDATES:
    m, _, gap, _ = run_model([v, SURV], panel)
    head.append(dict(variable=v, coef_together=round(float(m.params[v]), 4),
                     p_together=round(float(m.pvalues[v]), 3),
                     surv_p=round(float(m.pvalues[SURV]), 4), gap_together=gap))
df = df.merge(pd.DataFrame(head), on="variable")
df["no_sign_flip"] = np.sign(df.coef) == np.sign(df.coef_together)
df["promotable"] = df.sig_fdr & df.improves & df.no_sign_flip

print("\n=== Family C battery ===")
print(df[["variable", "r2", "coef", "p_raw", "p_fdr_bh", "sig_fdr", "gr_oos",
          "improves", "coef_together", "p_together", "no_sign_flip", "promotable"]]
      .to_string(index=False))
df.to_csv(f"{OUT}/persistence_share_battery.csv", index=False)

n = int(df.promotable.sum())
print(f"\n=== Verdict: {int(df.sig_fdr.sum())}/{len(df)} survive FDR, "
      f"{n}/{len(df)} meet all three pre-registered conditions ===")
print("  -> " + ("NULL FAMILY: nothing promoted." if n == 0 else
                 f"{n} candidate(s) qualify -- report before integrating."))
