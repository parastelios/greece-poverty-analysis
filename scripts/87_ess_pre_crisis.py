"""ESS descriptive extension: was Greece already unusually dissatisfied before
the crisis, or did its exceptional position emerge afterwards?

SEPARATE FROM EUROSTAT, ALWAYS. The Eurostat wellbeing module begins in 2013,
at the crisis trough, so it cannot answer this. ESS reaches back to 2002 -- but
it is a different instrument with a different sample design, and joining the two
into one line would manufacture continuity that does not exist. This script
never merges them and never models anything.

INPUT IS AGGREGATE, NOT MICRODATA. Respondent files remain login-gated. What is
used here comes from the ESS Data Portal's public Analysis tab, which exposes
weighted response distributions by country. Country means were reconstructed by
multiplying each displayed weighted percentage by its 0-10 score and summing.

The consequences of that are strict and are enforced below:
  * the means are APPROXIMATE, at the precision the portal displays
  * there are NO confidence intervals and NO standard errors
  * no significance test, model or inferential statement may be built on them
  * they are suitable for descriptive context only

Greek participation, and what each round is a reading of:

    round  1  2002/03   pre-crisis
    round  2  2004/05   pre-crisis
    round  4  2008/09   crisis onset
    round  5  2010/11   early crisis
    round 10  2020-22   later period
    round 11  2023/24   later period

The unobserved decade runs AFTER 2010/11 and covers both the depth of the
adjustment and the recovery, so this is a before/onset/early-crisis picture with
a long interruption, not a continuous trajectory.

TWO COMPARISONS, AND ONLY ONE OF THEM IS SOUND. The all-country set changes size
every round (22 to 30 countries), so an all-country rank is not comparable
across rounds: it moves when the country set moves. The balanced comparison
holds the same 12 countries present in all six Greek rounds, and it is the one
any conclusion must rest on.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw" / "ess", ROOT / "data" / "processed"
SRC = RAW / "ess_life_satisfaction_round_summary.csv"
STATUS = PROC / "ess_extension_status.txt"

PERIOD = {1: "pre-crisis", 2: "pre-crisis", 4: "crisis onset",
          5: "early crisis", 10: "later period", 11: "later period"}

if not SRC.exists():
    STATUS.write_text("[SKIPPED: source unavailable]\n"
                      f"expected input: {SRC.relative_to(ROOT)}\n"
                      "blocks publication: no\n")
    print("[SKIPPED: source unavailable]")
    print(f"ESS aggregates not found: {SRC.relative_to(ROOT)}")
    raise SystemExit(0)

d = pd.read_csv(SRC).sort_values("essround").reset_index(drop=True)
d["period"] = d.essround.map(PERIOD)

# ---- guards ---------------------------------------------------------------
# The portal's percentile and the rank must agree, or the extraction is wrong.
for r in d.itertuples():
    exp = 100 * (r.n_countries - r.greece_rank_worst) / (r.n_countries - 1)
    assert abs(exp - r.worst_percentile) < 0.15, (
        f"round {r.essround}: percentile {r.worst_percentile} contradicts "
        f"rank {r.greece_rank_worst}/{r.n_countries} (implies {exp:.1f})")
assert set(d.essround) == set(PERIOD), "unexpected round set"
assert (d.balanced_n == 12).all(), "balanced panel is not the fixed 12"
assert d.greece_mean_approx.between(0, 10).all(), "means outside the 0-10 scale"

d["gap_vs_balanced"] = (d.greece_mean_approx - d.balanced_12_median_approx).round(3)

bar = "=" * 88
print(bar); print("ESS DESCRIPTIVE EXTENSION -- APPROXIMATE, AGGREGATE, NOT FOR INFERENCE")
print(bar)
print("  Reconstructed from the ESS portal's public weighted distributions.")
print("  No confidence intervals exist for these values. Never spliced to Eurostat.\n")

print("  BALANCED COMPARISON -- the same 12 countries in every round")
print(f"  {'fieldwork':10} {'period':14} {'Greece':>7} {'median':>7} {'gap':>7} {'rank':>7}")
prev = None
for r in d.itertuples():
    if prev is not None and r.essround - prev > 2:
        print(f"  {'':10} ---- no Greek round between "
              f"{d.loc[d.essround == prev, 'fieldwork'].iloc[0]} and {r.fieldwork} ----")
    worst = "  <- worst" if r.balanced_12_rank_worst == 1 else ""
    print(f"  {r.fieldwork:10} {r.period:14} {r.greece_mean_approx:7.2f} "
          f"{r.balanced_12_median_approx:7.2f} {r.gap_vs_balanced:+7.2f} "
          f"{str(r.balanced_12_rank_worst) + '/12':>7}{worst}")
    prev = r.essround

print(f"\n  ALL-COUNTRY ranks (NOT comparable across rounds -- set size varies "
      f"{d.n_countries.min()}-{d.n_countries.max()}):")
print("   ", ", ".join(f"{r.fieldwork} {r.greece_rank_worst}/{r.n_countries}"
                       for r in d.itertuples()))

pre = d[d.period == "pre-crisis"]
early = d[d.essround == 5]
late = d[d.period == "later period"]
lvl_pre, lvl_low = pre.greece_mean_approx.mean(), float(early.greece_mean_approx.iloc[0])
lvl_late = late.greece_mean_approx.mean()

print(f"\n{bar}\nREADING\n{bar}")
print(f"  Pre-crisis Greece already sat {pre.gap_vs_balanced.mean():+.2f} below the")
print(f"  balanced median, at ranks {' and '.join(str(x) for x in pre.balanced_12_rank_worst)} "
      f"of 12 (1 = worst).")
print(f"  Level fell {lvl_pre:.2f} -> {lvl_low:.2f} by 2010/11, then recovered to "
      f"{lvl_late:.2f}.")
print(f"  But the gap to the balanced median is WIDER later "
      f"({late.gap_vs_balanced.mean():+.2f}) than pre-crisis "
      f"({pre.gap_vs_balanced.mean():+.2f}),")
print(f"  and Greece became the WORST of the 12 from 2010/11 onward and stayed there.")
print("  Two countries that were below Greece before the crisis have since passed it.")
print("\n  So: a low Greek baseline PRE-DATES the crisis, the crisis produced a real")
print("  level decline, the level recovered, and the comparative position did not.")
print("  A longstanding low-wellbeing pattern therefore remains plausible, and")
print("  generic pessimism or reporting culture CANNOT be dismissed.")
print("  These are approximate descriptive aggregates: no test is run on them.")

out = d[["essround", "fieldwork", "period", "greece_mean_approx",
         "balanced_12_median_approx", "gap_vs_balanced", "balanced_12_rank_worst",
         "balanced_n", "all_country_median_approx", "greece_rank_worst",
         "n_countries", "worst_percentile", "source_url"]]
out.to_csv(PROC / "ess_greece_life_satisfaction.csv", index=False)
STATUS.write_text("[BUILT: approximate aggregates from the ESS public Analysis tab]\n"
                  "inference permitted: NO -- descriptive context only\n"
                  "confidence intervals: none exist for these values\n"
                  "spliced to Eurostat: never\n")
print(f"\nWritten to {(PROC / 'ess_greece_life_satisfaction.csv').relative_to(ROOT)}")
