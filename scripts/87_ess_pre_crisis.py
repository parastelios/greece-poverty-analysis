"""ESS descriptive extension: was Greece already unusually dissatisfied before
the crisis, or did its exceptional position emerge afterwards?

SEPARATE FROM EUROSTAT, ALWAYS. The Eurostat wellbeing module begins in 2013,
at the crisis trough, so it cannot answer this. ESS runs from 2002 and reaches
back before 2008 -- but it is a different instrument with a different sample
design, and joining the two into one line would manufacture continuity that does
not exist. This script never merges them and never models anything.

DATA IS NOT FETCHED HERE. ESS distributes free of charge for non-commercial use
but requires a registered account, so the file has to be downloaded by hand:

    https://www.europeansocialsurvey.org/data-portal

  1. Sign in, build a cumulative file across rounds, or download per round.
  2. Keep at minimum: cntry, essround, stflife, and the design weights
     (dweight, pspwght or anweight depending on round).
  3. Save as data/raw/ess_life_satisfaction.csv

Greece participated in rounds 1 (2002/03), 2 (2004/05), 4 (2008/09),
5 (2010/11), 10 (2020-22) and 11 (2023/24). That gives TWO genuinely pre-crisis
observations and no continuous crisis trajectory, which bounds what this can
show.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
SRC = RAW / "ess_life_satisfaction.csv"

ROUND_YEARS = {1: "2002/03", 2: "2004/05", 3: "2006/07", 4: "2008/09",
               5: "2010/11", 6: "2012/13", 7: "2014/15", 8: "2016/17",
               9: "2018/19", 10: "2020-22", 11: "2023/24"}
PRE_CRISIS = {1, 2, 4}          # round 4 fieldwork straddles the onset
GREEK_ROUNDS = {1, 2, 4, 5, 10, 11}

if not SRC.exists():
    print(f"ESS source not found: {SRC.relative_to(ROOT)}")
    print(__doc__.split("DATA IS NOT FETCHED HERE.")[1].strip())
    raise SystemExit(0)     # not an error: the extension is simply not built yet

d = pd.read_csv(SRC)
d.columns = [c.lower() for c in d.columns]
need = {"cntry", "essround", "stflife"}
missing = need - set(d.columns)
if missing:
    raise SystemExit(f"ESS file is missing required columns: {sorted(missing)}")

# Official design weights. anweight is the analysis weight from round 9 onward;
# earlier rounds combine dweight with pspwght. Using unweighted means would
# misrepresent every country's population.
if "anweight" in d.columns:
    d["w"] = d.anweight
elif {"dweight", "pspwght"} <= set(d.columns):
    d["w"] = d.dweight * d.pspwght
elif "dweight" in d.columns:
    d["w"] = d.dweight
else:
    raise SystemExit(
        "no design weight found (anweight, or dweight with pspwght). "
        "Unweighted country means are not acceptable here.")

# stflife is 0-10; 77/88/99 are refusal, don't know and no answer.
d = d[(d.stflife >= 0) & (d.stflife <= 10)]
d = d.dropna(subset=["w"])


def wmean(g):
    return float(np.average(g.stflife, weights=g.w))


rows = []
by = d.groupby(["essround", "cntry"], as_index=False).apply(
    lambda g: pd.Series({"mean": wmean(g), "n": len(g)}), include_groups=False)
for rnd, grp in by.groupby("essround"):
    grp = grp.sort_values("mean").reset_index(drop=True)
    med = float(grp["mean"].median())
    if "GR" not in set(grp.cntry):
        continue
    i = int(grp.index[grp.cntry == "GR"][0])
    rows.append({
        "essround": int(rnd), "fieldwork": ROUND_YEARS.get(int(rnd), "?"),
        "pre_crisis": int(rnd) in PRE_CRISIS,
        "greece_mean": round(float(grp.loc[i, "mean"]), 3),
        "greece_n": int(grp.loc[i, "n"]),
        "european_median": round(med, 3),
        "gap_vs_median": round(float(grp.loc[i, "mean"]) - med, 3),
        "rank_from_lowest": i + 1,
        "n_countries": len(grp),
        "percentile_from_lowest": round(100 * (i + 1) / len(grp), 1),
    })

res = pd.DataFrame(rows).sort_values("essround")

# Sensitivity: only countries present in EVERY Greek round, so a changing rank
# cannot be an artefact of a changing country set.
greek = sorted(set(res.essround))
present = by[by.essround.isin(greek)].groupby("cntry").essround.nunique()
balanced = set(present[present == len(greek)].index)
brows = []
for rnd in greek:
    grp = by[(by.essround == rnd) & (by.cntry.isin(balanced))].sort_values("mean")
    grp = grp.reset_index(drop=True)
    if "GR" not in set(grp.cntry):
        continue
    i = int(grp.index[grp.cntry == "GR"][0])
    brows.append({"essround": int(rnd), "fieldwork": ROUND_YEARS.get(int(rnd), "?"),
                  "greece_mean": round(float(grp.loc[i, "mean"]), 3),
                  "european_median": round(float(grp["mean"].median()), 3),
                  "rank_from_lowest": i + 1, "n_countries": len(grp)})
bal = pd.DataFrame(brows)

bar = "=" * 92
print(bar); print("ESS: WAS GREECE ALREADY DISSATISFIED BEFORE THE CRISIS?"); print(bar)
print("  Descriptive only. Never joined to the Eurostat series, never modelled.\n")
print(f"  {'round':6} {'fieldwork':10} {'pre':4} {'Greece':>8} {'Eur med':>8} "
      f"{'gap':>7} {'rank':>10} {'pct':>6}")
for r in res.itertuples():
    print(f"  {r.essround:<6} {r.fieldwork:10} {'yes' if r.pre_crisis else '':4} "
          f"{r.greece_mean:8.2f} {r.european_median:8.2f} {r.gap_vs_median:+7.2f} "
          f"{str(r.rank_from_lowest) + '/' + str(r.n_countries):>10} "
          f"{r.percentile_from_lowest:5.0f}%")

if len(bal):
    print(f"\n{bar}\nBALANCED PANEL: only countries present in every Greek round "
          f"({len(balanced)})\n{bar}")
    for r in bal.itertuples():
        print(f"  {r.fieldwork:10} Greece {r.greece_mean:.2f}  median "
              f"{r.european_median:.2f}  rank {r.rank_from_lowest}/{r.n_countries}")

pre = res[res.pre_crisis]
post = res[~res.pre_crisis]
print(f"\n{bar}\nREADING\n{bar}")
if len(pre) and len(post):
    print(f"  pre-crisis rounds:  Greece {pre.greece_mean.mean():.2f} against a "
          f"European median of {pre.european_median.mean():.2f}")
    print(f"  later rounds:       Greece {post.greece_mean.mean():.2f} against "
          f"{post.european_median.mean():.2f}")
print("  A LEVEL and a RANK are different things: report both, and never read a")
print("  changing rank as changing Greek satisfaction without showing the level.")
print("  Low pre-crisis satisfaction would NOT establish reporting bias -- it")
print("  could reflect real pre-crisis conditions.")

res.to_csv(PROC / "ess_greece_life_satisfaction.csv", index=False)
if len(bal):
    bal.to_csv(PROC / "ess_greece_balanced_panel.csv", index=False)
print(f"\nWritten to {PROC}/ess_greece_life_satisfaction.csv")
