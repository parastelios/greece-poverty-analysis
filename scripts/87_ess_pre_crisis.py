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

Greek participation, and what each round is a reading of:

    round  1  2002/03   pre-crisis
    round  2  2004/05   pre-crisis
    round  4  2008/09   crisis onset
    round  5  2010/11   early crisis
    round 10  2020-22   later period
    round 11  2023/24   later period

So there are TWO genuinely pre-crisis readings, and the crisis itself is caught
at its onset and again early on. What is missing is the decade AFTER 2010/11:
the gap runs 2010/11 -> 2020-22, which is where the depth of the adjustment and
the recovery both fall. This is a before/onset/early-crisis picture with a
long interruption, not a continuous trajectory, and that bounds what it can show.
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
# Round 4 fieldwork straddles the onset, so it is NOT counted as pre-crisis.
PERIOD = {1: "pre-crisis", 2: "pre-crisis", 4: "crisis onset",
          5: "early crisis", 10: "later period", 11: "later period"}
PRE_CRISIS = {1, 2}
GREEK_ROUNDS = set(PERIOD)
STATUS = PROC / "ess_extension_status.txt"

if not SRC.exists():
    # Exiting 0 keeps `make` moving, but the run must NOT be able to pass for a
    # success. Every downstream consumer reads this marker, and the report
    # prints it verbatim.
    STATUS.write_text("[SKIPPED: authenticated source unavailable]\n"
                      "stage: 7 (optional descriptive extension)\n"
                      "reason: ESS microdata requires a registered account; "
                      "no account is configured for this project\n"
                      "expected input: data/raw/ess_life_satisfaction.csv\n"
                      "blocks publication: no\n")
    print("[SKIPPED: authenticated source unavailable]")
    print(f"ESS source not found: {SRC.relative_to(ROOT)}")
    print(__doc__.split("DATA IS NOT FETCHED HERE.")[1].strip())
    print("\nStatus written to data/processed/ess_extension_status.txt")
    print("This extension is OPTIONAL and does not block the report.")
    raise SystemExit(0)

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
        "period": PERIOD.get(int(rnd), "?"),
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
print(f"  {'round':6} {'fieldwork':10} {'period':14} {'Greece':>8} {'Eur med':>8} "
      f"{'gap':>7} {'rank':>10} {'pct':>6}")
prev = None
for r in res.itertuples():
    if prev is not None and r.essround - prev > 2:
        print(f"  {'':6} {'':10} ---- gap: no Greek round between "
              f"{ROUND_YEARS.get(prev)} and {r.fieldwork} ----")
    print(f"  {r.essround:<6} {r.fieldwork:10} {r.period:14} "
          f"{r.greece_mean:8.2f} {r.european_median:8.2f} {r.gap_vs_median:+7.2f} "
          f"{str(r.rank_from_lowest) + '/' + str(r.n_countries):>10} "
          f"{r.percentile_from_lowest:5.0f}%")
    prev = r.essround

if len(bal):
    print(f"\n{bar}\nBALANCED PANEL: only countries present in every Greek round "
          f"({len(balanced)})\n{bar}")
    for r in bal.itertuples():
        print(f"  {r.fieldwork:10} Greece {r.greece_mean:.2f}  median "
              f"{r.european_median:.2f}  rank {r.rank_from_lowest}/{r.n_countries}")

print(f"\n{bar}\nREADING\n{bar}")
for label in ["pre-crisis", "crisis onset", "early crisis", "later period"]:
    sub = res[res.period == label]
    if len(sub):
        print(f"  {label:14} Greece {sub.greece_mean.mean():.2f} against a "
              f"European median of {sub.european_median.mean():.2f} "
              f"({len(sub)} round{'s' if len(sub) > 1 else ''})")
print("  The decade AFTER 2010/11 is unobserved here: no Greek round falls")
print("  between 2010/11 and 2020-22, so the adjustment's depth and the")
print("  recovery are both outside this picture.")
print("  A LEVEL and a RANK are different things: report both, and never read a")
print("  changing rank as changing Greek satisfaction without showing the level.")
print("  Low pre-crisis satisfaction would NOT establish reporting bias -- it")
print("  could reflect real pre-crisis conditions.")

res.to_csv(PROC / "ess_greece_life_satisfaction.csv", index=False)
if len(bal):
    bal.to_csv(PROC / "ess_greece_balanced_panel.csv", index=False)
print(f"\nWritten to {PROC}/ess_greece_life_satisfaction.csv")
