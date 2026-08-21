"""Checkpoint (family B): does the RATE of change, or persistent low standing
relative to the rest of the EU, explain Greece's subjective-poverty gap better
than the accumulation and duration measures already screened?

Pre-registered in docs/publication_strategy.md before this script was run: the
five candidates, the construction rules, the decision to exclude second
derivatives, and the stopping rule are all fixed there.

Declared as its own FDR family, deliberately NOT appended to the 18-candidate
family in 38_cumulative_hardship.py. Benjamini-Hochberg scales every adjusted
p-value by family size, and wage_years_below_2008 (FDR 0.0408) survives only
while that family has <=22 members -- adding to it would retire a published
result as a side effect of asking a different question.

Method is identical to the existing battery so the numbers are comparable:
each candidate added one at a time to Model C-LTU, year fixed effects, errors
clustered by country, judged by leave-one-country-out prediction of Greece.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from eu_membership import eu_members

RAW, OUT = "../data/raw", "../data/processed"
BASE_YEAR = 2008
WINDOW = 5           # trailing years for the slope, inclusive of the current year
WORST_Q = 0.80       # "worst quintile" = 80th percentile or above on a bad-is-high series
MEMBERS = sorted(eu_members(2025))

panel = pd.read_csv(f"{OUT}/cumulative_hardship_candidate_panel.csv")
vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]


# ------------------------------------------------------------------ constructions ----
def trailing_slope(df, value_col, out_col, window=WINDOW):
    """OLS slope of value_col on time over the trailing `window` years, inclusive.
    Requires a full window -- no partial-window slopes, which would make the
    early years noisier than the late ones for no stated reason."""
    rows = []
    for g, grp in df.sort_values("time").groupby("geo"):
        t = grp["time"].values.astype(float)
        v = grp[value_col].values.astype(float)
        for i in range(len(grp)):
            lo = i - window + 1
            if lo < 0:
                continue
            tt, vv = t[lo:i + 1], v[lo:i + 1]
            ok = ~np.isnan(vv)
            if ok.sum() < window:
                continue
            rows.append({"geo": g, "time": int(t[i]),
                         out_col: float(np.polyfit(tt[ok], vv[ok], 1)[0])})
    return pd.DataFrame(rows)


def years_in_worst_quintile(df, value_col, out_col, higher_is_worse=True,
                            base_year=BASE_YEAR):
    """Cumulative count of years since base_year spent in the worst-performing
    quintile of that year's EU distribution. Ranked within each year, so it is a
    relative-standing measure: a country improving in absolute terms still counts
    a year if everyone else improved faster."""
    d = df[df.geo.isin(MEMBERS)].copy()
    pct = d.groupby("time")[value_col].rank(pct=True)
    d["_worst"] = ((pct >= WORST_Q) if higher_is_worse else (pct <= 1 - WORST_Q)).astype(int)
    d = d[d.time >= base_year].sort_values(["geo", "time"])
    d[out_col] = d.groupby("geo")["_worst"].cumsum()
    return d[["geo", "time", out_col]]


wages = pd.read_csv(f"{RAW}/real_wage_idx2008.csv")
gdp = pd.read_csv(f"{RAW}/panel_gdp_history_2008_2024.csv")[["geo", "time", "real_gdp_pc"]]
unemp = pd.read_csv(f"{RAW}/panel_unemployment_history.csv")

feats = [
    trailing_slope(wages, "real_wage_idx2008", "slope5_real_wage"),
    trailing_slope(gdp, "real_gdp_pc", "slope5_real_gdp"),
    trailing_slope(unemp, "unemployment_rate", "slope5_unemployment"),
    years_in_worst_quintile(unemp, "unemployment_rate", "years_worst_quintile_unemp",
                            higher_is_worse=True),
    years_in_worst_quintile(wages, "real_wage_idx2008", "years_worst_quintile_wage",
                            higher_is_worse=False),
]
CANDIDATES = ["slope5_real_wage", "slope5_real_gdp", "slope5_unemployment",
              "years_worst_quintile_unemp", "years_worst_quintile_wage"]

for f in feats:
    panel = panel.merge(f, on=["geo", "time"], how="left")
panel.to_csv(f"{OUT}/direction_persistence_panel.csv", index=False)

print("=== Coverage of the five candidates in the model window ===")
for c in CANDIDATES:
    sub = panel.dropna(subset=[c])
    print(f"  {c:28} {len(sub):4} country-years, {sub.geo.nunique():2} countries, "
          f"{int(sub.time.min())}-{int(sub.time.max())}")

print("\n=== Where Greece stands on each (latest year with data) ===")
for c in CANDIDATES:
    sub = panel.dropna(subset=[c])
    yr = sub.time.max()
    s = sub[sub.time == yr].set_index("geo")[c].sort_values(ascending=False)
    pos = list(s.index).index("EL") + 1 if "EL" in s.index else None
    print(f"  {c:28} {int(yr)}: Greece {s.get('EL', float('nan')):8.2f}  "
          f"rank {pos}/{len(s)} (1 = highest)  EU median {s.median():8.2f}")


# ------------------------------------------------------------------ model battery ----
def run_model(vars_extra, panel, base_vars=vars_c_ltu, outcome="subjective_poverty"):
    vars_ = base_vars + vars_extra
    d = panel.dropna(subset=vars_ + [outcome]).copy()
    formula = f"{outcome} ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d["residual"] = d[outcome] - m.predict(d)
    gr_in = d[d.geo == "EL"]["residual"].mean()
    rows = []
    for c in sorted(d["geo"].unique()):
        train, test = d[d.geo != c], d[d.geo == c].copy()
        mc = smf.ols(formula, data=train).fit(cov_type="cluster",
                                              cov_kwds={"groups": train["geo"]})
        rows.append({"geo": c, "avg_residual": (test[outcome] - mc.predict(test)).mean()})
    loo = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
    loo["rank"] = loo.index + 1
    gr = loo[loo.geo == "EL"].iloc[0]
    return dict(r2=round(m.rsquared, 3), n=len(d), n_geo=d.geo.nunique(),
                gr_in=round(gr_in, 2), gr_oos=round(gr["avg_residual"], 2),
                rank=f"{int(gr['rank'])}/{len(loo)}", model=m)


base = run_model([], panel)
print(f"\n=== Baseline Model C-LTU on this panel ===\n"
      f"  R2={base['r2']}  n={base['n']} ({base['n_geo']} countries)  "
      f"Greece in-sample {base['gr_in']}  out-of-sample {base['gr_oos']}  rank {base['rank']}")

res = []
for v in CANDIDATES:
    r = run_model([v], panel)
    res.append(dict(variable=v, r2=r["r2"], n=r["n"], n_geo=r["n_geo"],
                    coef=round(float(r["model"].params[v]), 4),
                    p_raw=float(r["model"].pvalues[v]),
                    gr_in=r["gr_in"], gr_oos=r["gr_oos"], rank=r["rank"]))
df = pd.DataFrame(res).sort_values("p_raw").reset_index(drop=True)

df["p_fdr_bh"] = multipletests(df.p_raw.values, alpha=0.05, method="fdr_bh")[1]
df["significant_after_fdr"] = df["p_fdr_bh"] < 0.05
# Pre-registered stopping rule: survive FDR *and* improve on the baseline gap.
df["improves_gr_oos"] = df["gr_oos"].abs() < abs(base["gr_oos"])
df["promotable"] = df["significant_after_fdr"] & df["improves_gr_oos"]

print("\n=== Family B battery: each candidate added individually to Model C-LTU ===")
print(f"(baseline Greek out-of-sample gap = {base['gr_oos']})")
print(df[["variable", "r2", "n", "coef", "p_raw", "p_fdr_bh",
          "significant_after_fdr", "gr_oos", "improves_gr_oos", "promotable"]].to_string(index=False))

df.to_csv(f"{OUT}/direction_persistence_battery.csv", index=False)

n_ok = int(df.promotable.sum())
print(f"\n=== Verdict ===")
print(f"  {int(df.significant_after_fdr.sum())} of {len(df)} survive FDR at 5%")
print(f"  {n_ok} of {len(df)} meet the pre-registered promotion rule "
      f"(survive FDR AND improve Greece's out-of-sample gap)")
print("  -> " + ("NULL FAMILY: nothing promoted, the 18-candidate family and every "
                 "published result stand unchanged."
                 if n_ok == 0 else
                 f"{n_ok} candidate(s) qualify for consideration -- report before integrating."))
print("\nThe existing 18-candidate family is untouched: this battery was corrected "
      "within itself, so wage_years_below_2008 remains at FDR 0.0408.")
