"""P0: reconcile the project's constructed subjective-hardship series against
Eurostat's official published indicator.

Protocol: docs/project_description_v3.md section 4a. Four checks, run in this
order, with the tolerance declared before any value is inspected.

  Constructed : ilc_mdes09, lev_diff = DIF + GRT, hhcomp TOTAL, rskpovth TOTAL
  Official    : ilc_sbjp01, age TOTAL, sex T, unit PC

--------------------------------------------------------------------------
TOLERANCE, DECLARED IN ADVANCE (before any numerical comparison was run)
--------------------------------------------------------------------------
The two series are known from their dimension structures to differ in
population base (see check 1), so exact agreement is not expected and a strict
equality test would fail by construction rather than by evidence. The declared
bar is therefore:

  WITHIN TOLERANCE  if median |difference| <= 2.0 pp
                    AND 90% of country-years within 5.0 pp
  RANK AGREEMENT    if the cross-country Spearman correlation is >= 0.90 in
                    every overlapping year
  TREND AGREEMENT   if the within-Greece Pearson correlation over the overlap
                    is >= 0.90

Passing all three would mean the series carry the same signal at different
levels. Failing rank or trend agreement means they measure different things,
which under section 4a makes the official series a SEPARATE PRIMARY OUTCOME
rather than a robustness check.
--------------------------------------------------------------------------
"""
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, ".")
from eurostat import fetch
from eu_membership import eu_members

OUT = "../data/processed"
M = sorted(eu_members(2025))
TOL_MEDIAN, TOL_TAIL, TOL_TAIL_SHARE = 2.0, 5.0, 0.90
TOL_RANK, TOL_TREND = 0.90, 0.90

# ---------------------------------------------------------------- check 1: definitions ----
print("=" * 74)
print("CHECK 1 - DEFINITIONAL EQUIVALENCE (run before any numerical comparison)")
print("=" * 74)
dims = {}
for code in ["ilc_sbjp01", "ilc_mdes09"]:
    d = fetch(code, time=[2024])
    dims[code] = {c: sorted(d[c].dropna().unique())
                  for c in d.columns if c not in ("value", "time", "geo", "geo_label", "flags", "freq")}
for code, dd in dims.items():
    print(f"\n  {code}")
    for k, v in dd.items():
        print(f"     {k:10} ({len(v):2}): {v[:8]}")

print("""
  WHAT THE DIMENSIONS SHOW

  The two datasets offer DIFFERENT BREAKDOWNS of the same measure:
    - ilc_mdes09 carries hhcomp (17 household-composition categories) and the
      six response levels (VEASY, FEASY, EASY, SOME, DIF, GRT). The project
      aggregates DIF + GRT itself, so that choice is auditable.
    - ilc_sbjp01 carries age and sex, and exposes no response-level dimension:
      its aggregation is fixed by Eurostat and is not recoverable from the API.

  A dimension difference is NOT by itself a population-base difference -- these
  are alternative breakdowns published from the same survey, and whether the
  TOTAL figures share a base is an empirical question, settled by check 2 below.
  (An earlier draft of this script inferred a household-vs-person base difference
  from the dimensions alone. Checks 2 and 3 refute that inference; the note is
  kept so the reasoning error is on record rather than silently corrected.)

  Comparability window DIFFERS, and this part is definitional:
    - constructed: 2003-2025, >=25 reporters from 2005
    - official:    2010-2025 only

  CONSEQUENCE FOR P2: Eurostat does not publish ilc_sbjp01 before 2010, so the
  official series cannot supply a 2003-2009 pre-crisis baseline on its own. If
  the two series prove equivalent where they overlap, the constructed series is
  a backward EXTENSION of the official indicator rather than a bespoke measure,
  and the comparative design may use it on that basis.
""")

# ---------------------------------------------------------------- data ----
off = fetch("ilc_sbjp01", time=range(2000, 2026), age=["TOTAL"], sex=["T"], unit=["PC"])
off = off[off.geo.isin(M)][["geo", "time", "value"]].rename(columns={"value": "official"})
con = fetch("ilc_mdes09", time=range(2000, 2026), hhcomp=["TOTAL"], rskpovth=["TOTAL"],
            unit=["PC"], lev_diff=["DIF", "GRT"])
con = (con[con.geo.isin(M)].groupby(["geo", "time"], as_index=False)["value"].sum()
       .rename(columns={"value": "constructed"}))
m = off.merge(con, on=["geo", "time"], how="inner")
m["diff"] = m.constructed - m.official
print(f"Overlap: {len(m)} country-years, {m.geo.nunique()} countries, "
      f"{int(m.time.min())}-{int(m.time.max())}\n")

# ---------------------------------------------------------------- check 2: tolerance ----
print("=" * 74)
print("CHECK 2 - ANNUAL NUMERICAL TOLERANCE")
print("=" * 74)
med, tail = m["diff"].abs().median(), (m["diff"].abs() <= TOL_TAIL).mean()
print(f"  median |difference|      {med:6.2f} pp   (bar: <= {TOL_MEDIAN})")
print(f"  share within {TOL_TAIL} pp      {tail:6.1%}      (bar: >= {TOL_TAIL_SHARE:.0%})")
print(f"  mean signed difference   {m['diff'].mean():+6.2f} pp")
print(f"  range                    {m['diff'].min():+.1f} to {m['diff'].max():+.1f} pp")
pass2 = (med <= TOL_MEDIAN) and (tail >= TOL_TAIL_SHARE)
print(f"  -> {'WITHIN TOLERANCE' if pass2 else 'OUTSIDE TOLERANCE'}")

# ---------------------------------------------------------------- check 3: rank/trend ----
print("\n" + "=" * 74)
print("CHECK 3 - RANK AND TREND AGREEMENT")
print("=" * 74)
rho = {int(y): spearmanr(g.constructed, g.official).statistic
       for y, g in m.groupby("time") if len(g) >= 10}
print("  cross-country Spearman by year:")
print("   " + "  ".join(f"{y}:{r:.2f}" for y, r in sorted(rho.items())))
print(f"  min {min(rho.values()):.3f}, median {np.median(list(rho.values())):.3f}   "
      f"(bar: min >= {TOL_RANK})")
gr = m[m.geo == "EL"].sort_values("time")
trend = gr.constructed.corr(gr.official)
print(f"\n  within-Greece trend correlation over the overlap: {trend:.3f}   "
      f"(bar: >= {TOL_TREND})")
print(f"  Greece rank on each, latest year:")
last = m[m.time == m.time.max()]
for col in ["constructed", "official"]:
    s = last.set_index("geo")[col].sort_values(ascending=False)
    print(f"     {col:12} Greece {s['EL']:5.1f}, rank {list(s.index).index('EL')+1}/{len(s)}")
pass3 = (min(rho.values()) >= TOL_RANK) and (trend >= TOL_TREND)
print(f"  -> {'AGREE' if pass3 else 'DISAGREE'}")

m.to_csv(f"{OUT}/p0_outcome_reconciliation.csv", index=False)
pd.DataFrame([{"median_abs_diff": med, "share_within_5pp": tail,
               "min_spearman": min(rho.values()), "greece_trend_corr": trend,
               "pass_tolerance": pass2, "pass_rank_trend": pass3}]
             ).to_csv(f"{OUT}/p0_verdict.csv", index=False)
print(f"\nWritten to {OUT}/p0_outcome_reconciliation.csv and p0_verdict.csv")
