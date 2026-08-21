"""P6 step 5 prerequisite: the shared cross-document spine.

A structured map, not prose. Every document is written FROM this; none of them
is the source. Drafting the technical report first and letting the others
inherit from it is how a shared spine silently becomes one document's outline.

Emits docs/shared_spine.csv and docs/shared_spine.md.
"""
import csv
import sys

sys.path.insert(0, ".")
import pandas as pd

FULL, SUMMARY, BRIEF, NONE = "full", "summary", "brief", "-"

# movement, section purpose, claim ids, canonical number, canonical wording,
# tier, mandatory caveat, required visual, (report, paper, narrative, appendix)
SPINE = [
 (1, "The puzzle",
  "Establish the divergence between reported hardship and official income poverty, "
  "then immediately introduce AROPE as the official system's own bridge.",
  "1.1 1.2 1.3 1.4 3.1 3.2 3.3 10.6",
  "67.2% vs EU 17.6%; AROP 19.6%, 4th of 27; AROPE gap 39.7pt",
  "Greek reported hardship is the EU's highest while AROP is elevated but ordinary; "
  "AROPE narrows the gap and does not close it.",
  "confirmatory / descriptive",
  "AROPE is a bridge, not a competing headline. The outcome is Eurostat's official "
  "indicator (ilc_sbjp01 from 2010, validated backward extension before).",
  "AROP vs subjective scatter; AROPE panel",
  (FULL, FULL, FULL, FULL)),

 (2, "The ruler moved",
  "Explain why the annual relative rate understates a national collapse, and give "
  "the anchored reconstruction.",
  "2.1 2.2 2.3 2.4 2.5",
  "threshold 100 -> 65 (2008=100); anchored ~20% -> ~41%",
  "The poverty line fell with the median, so AROP stayed calm while the living "
  "standard it represents deteriorated.",
  "confirmatory",
  "The anchored series is an approximation validated at MAE 1.22pt against the "
  "official 2019-anchored product; microdata finds a LARGER effect, not a smaller one.",
  "real threshold vs real income, 2008=100",
  (FULL, FULL, FULL, FULL)),

 (3, "How broad the deterioration was",
  "Show that the collapse was wide, not confined to one indicator, in real units "
  "the reader can hold.",
  "1.9 7.1 7.2 7.3 7.4 7.5 7.6 7.7 7.8",
  "21% pre-crisis -> 58% from 2012, 68% in 2024, 1st of 27",
  "Greece moved from the EU's worst fifth on a fifth of measured indicators to "
  "roughly two-thirds, and has not moved back.",
  "descriptive corroboration",
  "DESCRIPTIVE ONLY. Tested as a predictor and null (FDR 0.287). Never written as "
  "a driver; audit_parity's FORBIDDEN rules fail the build on causal phrasing.",
  "breadth series; 25-indicator position ladder",
  (FULL, SUMMARY, FULL, FULL)),

 (4, "The objective-only model",
  "The central quantitative result, in a specification containing nothing that "
  "restates the outcome.",
  "10.1 10.2 4.1 4.3 5.1 5.3 6.2 6.3 6.6",
  "+27.05 -> +6.93pt; rank 1 -> 3 of 27",
  "Adding accumulated unemployment exposure to the objective-only specification "
  "reduces Greece's leave-out residual from approximately 27 to 7 points. Greece "
  "nevertheless remains the third most under-predicted country.",
  "post-selection robustness (not independent confirmation)",
  "A MODEL COMPARISON, not a causal decomposition. Arrears, unexpected-expense "
  "capacity and financial expectations are excluded by construction. The legacy "
  "residuals 11.6, 3.9, -0.8 and +2.70 are superseded and must not be quoted as "
  "headlines.",
  "objective-only model ladder",
  (FULL, FULL, SUMMARY, FULL)),

 (5, "What the result is not",
  "The between-country qualification, the unresolved remainder, and both failed "
  "designs.",
  "10.3 10.4 10.5 6.5 6.7 6.8 8.1 4.4",
  "between +0.332 p<0.0001; within -0.076 p=0.692",
  "The association is supported predominantly between countries. The panel does "
  "not establish a within-country dynamic effect, and its within estimate is too "
  "imprecise to rule one out.",
  "post-selection robustness / core nulls",
  "Never write 'as exposure accumulated, hardship increased'. Use 'between-country "
  "scarring marker', not 'mechanism'. Synthetic control failed and no effect from "
  "it is interpreted. Family D is descriptive only.",
  "Mundlak within/between; failed-design summary",
  (FULL, FULL, BRIEF, FULL)),

 (6, "Discussion",
  "Material grounding without claiming full resolution or causality, and the "
  "reporting-culture question at its actual strength.",
  "8.2 8.3 8.4 8.5 8.6 8.7 9.1 9.2 9.3 9.4",
  "widening +19.8pt vs median -8.8pt; placebo 1st of 27, p=0.037",
  "A time-invariant reporting premium cannot explain a crisis-timed widening, but "
  "a crisis-induced change in response behaviour is not excluded.",
  "confirmatory / limitation",
  "p=0.037 is a permutation statistic under exchangeability, not randomization "
  "inference. Domain specificity rules out a GENERIC response-style account, not a "
  "fiscally specific one. All results associational and aggregate.",
  "event study; placebo distribution",
  (FULL, FULL, SUMMARY, SUMMARY)),

 (7, "Legacy specifications (appendix only)",
  "The superseded residuals, kept visible so the record is complete and so a "
  "reader meeting them in V1 can see why they were retired.",
  "4.2 5.2 6.1 6.4",
  "11.6 / 3.9 / -0.8 / +2.70",
  "Earlier specifications that included predictors proximate to the outcome, or "
  "that reported a nested-selection figure. Superseded by claim 10.2 and retained "
  "only as legacy, proximity-sensitive results.",
  "legacy / superseded",
  "MUST NOT be quoted as headline estimates. Each is labelled superseded with a "
  "pointer to 10.2. Appendix only -- absent from all three reader-facing documents.",
  "legacy ladder table",
  (NONE, NONE, NONE, FULL)),
]

rows = []
for mv, name, purpose, ids, number, wording, tier, caveat, visual, levels in SPINE:
    rows.append(dict(movement=mv, section=name, purpose=purpose,
                     claim_ids=ids, canonical_number=number,
                     canonical_wording=wording, tier=tier,
                     mandatory_caveat=caveat, required_visual=visual,
                     report=levels[0], paper=levels[1],
                     narrative=levels[2], appendix=levels[3]))
df = pd.DataFrame(rows)
df.to_csv("../docs/shared_spine.csv", index=False)

# cross-check: every claim in the matrix must appear in exactly one movement
cm = pd.read_csv("../docs/claim_matrix.csv", dtype=str)
spine_ids = [i for r in rows for i in r["claim_ids"].split()]
dupes = [i for i in set(spine_ids) if spine_ids.count(i) > 1]
missing = sorted(set(cm["id"]) - set(spine_ids))
extra = sorted(set(spine_ids) - set(cm["id"]))
print(f"{len(SPINE)} movements, {len(spine_ids)} claim placements")
print(f"  claims in the matrix but not placed: {missing or 'none'}")
print(f"  placed but not in the matrix       : {extra or 'none'}")
print(f"  placed in more than one movement   : {dupes or 'none'}")

with open("../docs/shared_spine.md", "w") as f:
    f.write("# Shared spine\n\nEvery document is written FROM this map. None of "
            "them is the source.\n\nDetail levels: `full` / `summary` / `brief` / "
            "`-` (absent).\n\n")
    for r in rows:
        f.write(f"## Movement {r['movement']} — {r['section']}\n\n"
                f"**Purpose.** {r['purpose']}\n\n"
                f"**Claims.** {r['claim_ids']}\n\n"
                f"**Canonical number.** {r['canonical_number']}\n\n"
                f"**Canonical wording.** {r['canonical_wording']}\n\n"
                f"**Tier.** {r['tier']}\n\n"
                f"**Mandatory caveat.** {r['mandatory_caveat']}\n\n"
                f"**Required visual.** {r['required_visual']}\n\n"
                f"| report | paper | narrative | appendix |\n|---|---|---|---|\n"
                f"| {r['report']} | {r['paper']} | {r['narrative']} | {r['appendix']} |\n\n---\n\n")
print("\nWritten to docs/shared_spine.csv and docs/shared_spine.md")
if missing or extra or dupes:
    sys.exit(1)
