"""Parity audit: does each document carry every claim the matrix requires of it?

Reads docs/claim_matrix.csv and searches each document for a distinctive
fingerprint of each claim. Reports claims that are REQUIRED in a document's body
but cannot be found anywhere in it -- the drift this whole alignment exists to
prevent.

Fingerprints are deliberately loose (a number or a distinctive phrase) because
the three documents say the same thing in three registers. A miss here means
"check this by hand", not necessarily "this is broken".
"""
import re, html, sys
from pathlib import Path
import pandas as pd

DOCS = {"report": "../output/report.html",
        "paper": "../output/academic_paper_draft.html",
        "narrative": "../output/narrative_companion.html"}

# distinctive fingerprints per claim id: any ONE match counts as present
FP = {
 "1.1": ["67.2", "two out of three", "highest share anywhere"],
 "1.2": ["4th-highest", "4th of 27"],
 "1.3": ["47.6", "14.9"],
 "1.4": ["48% of Greek households", "48%", "2003"],
 "2.1": ["65 in 2016", "100 (2008) to a low of 65", "from 100", "shrank"],
 "2.2": ["20.1%", "21.2%", "barely moved"],
 "2.3": ["roughly doubling", "roughly doubles", "41%", "40.6"],
 "2.4": ["1.2 points", "1.22", "r=0.89", "0.89"],
 "2.5": ["48%", "Andriopoulou"],
 "3.1": ["39.7"],
 "3.2": ["reconstruct", "overlap at the household level"],
 "3.3": ["spliced", "methodology break", "2020/2021"],
 "4.1": ["25.6"],
 "4.2": ["35.5", "11.6"],
 "4.3": ["close to the outcome", "conceptually close", "close to the thing being explained"],
 "4.4": ["debt", "transfer"],
 "5.1": ["0.93", "r=0.93"],
 "5.2": ["3.9", "6th of 27", "6th / 27"],
 "5.3": ["p&lt;0.001", "p<0.001", "27 leave-one"],
 "6.1": ["&minus;0.8", "-0.8", "−0.8"],
 "6.2": ["0.0024"],
 "6.3": ["25 of 27"],
 "1.9": ["58%", "worst quintile", "worst fifth"],
 "6.4": ["+2.70", "2.70", "2.7", "19th of 27"],
 "6.5": ["secretly optimistic", "secretly more optimistic", "not that Greek households"],
 "6.6": ["sustained", "10-year", "decade"],
 "6.7": ["individual", "aggregate", "ecological"],
 "6.8": ["0.291"],
 "7.1": ["11.2%"],
 "7.2": ["31.8%"],
 "7.3": ["wage-adjusted", "price pressure"],
 "7.4": ["25.7%"],
 "7.5": ["290,281"],
 "7.6": ["65+", "generational"],
 "7.7": ["59.5", "17th of 27"],
 "7.8": ["39.8", "14.2", "230.5"],
 "8.1": ["inequality"],
 "8.2": ["2003", "before the crisis", "pre-crisis"],
 "8.3": ["19.8", "50.2", "widening"],
 "8.4": ["0.037", "placebo"],
 "8.5": ["2007", "pre-trend", "pre-existing"],
 "8.6": ["3.76", "life satisfaction", "three times"],
 "8.7": ["7%", "trust"],
 "9.1": ["not read alone", "not on its own", "read alone", "alongside"],
 "9.2": ["associational"],
 "9.3": ["archived", "reproduce"],
 "9.4": ["pre-specified", "four tier", "four tiers", "pre-registered"],
}

def text_of(p):
    s = Path(p).read_text(encoding="utf-8")
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)

m = pd.read_csv("../docs/claim_matrix.csv", dtype=str)  # ids like "1.1" must stay strings
texts = {k: text_of(v) for k, v in DOCS.items()}
raws = {k: Path(v).read_text(encoding="utf-8") for k, v in DOCS.items()}

problems = []
for _, r in m.iterrows():
    fps = FP.get(r.id, [])
    for doc in DOCS:
        need = r[doc]
        if need == "--":
            continue
        found = any(f.lower() in texts[doc].lower() or f.lower() in raws[doc].lower() for f in fps)
        if not found:
            problems.append((r.id, r.element, r.claim[:58], doc, need))

FORBIDDEN = {
    # P2's synthetic control failed its pre-registered gates: the synthetic unit
    # had half Greece's income and three times its deprivation. The estimated
    # +27-point post-period divergence is NOT reportable -- not as a headline,
    # not hedged, not "suggestive". Quoting it with caveats is still quoting it.
    "p2-synthetic-effect-reported": [
        "synthetic greece diverges by 27",
        "27-point divergence from synthetic",
        "synthetic control shows greece",
        "compared with its synthetic counterpart, greece",
        "diverged by roughly 27 points from",
    ],
    # The breadth-of-disadvantage composite is descriptive corroboration and was
    # tested as a predictor and found null. If any document ever restates it as a
    # driver, explanation or cause, that is the regression this rule catches.
    "breadth-stated-as-cause": [
        "breadth of disadvantage explains",
        "because greece is in the worst quintile on",
        "the worst-quintile share drives",
        "the breadth measure predicts",
        "explained by the share of indicators",
    ],
    "only-precrisis-gdp": [
        "only eu country below its own pre-crisis",
        "only eu country that never rejoins",
        "only one that never rejoins the pack",
    ],
    "stale-reproduction": [
        "end-to-end re-acquisition pipeline remains incomplete",
        "end-to-end re-acquisition from a clean checkout is still being completed",
        "automated re-fetching of every raw input is not yet complete",
    ],
    "salaried-hours-overclaim": [
        "salaried workers who work the eu's longest hours",
        "salaried workers &mdash; who work the eu's longest hours",
    ],
}
for doc, raw in raws.items():
    low = raw.lower()
    for rule, phrases in FORBIDDEN.items():
        for phrase in phrases:
            if phrase in low:
                problems.append(("forbid", rule, phrase, doc, "remove"))

# ---------------------------------------------------------------- supersession ----
# Every V1 claim must receive an explicit V2 disposition. This is the rule that
# makes keeping both releases safe rather than confusing: a V1 claim can be
# carried forward, retested, reworded, superseded, retracted or marked V1-only,
# but it cannot silently disappear from the record.
#
# Deliberately NOT enforced here: presence in all three reader-facing documents.
# Some claims are properly appendix-only -- a technical diagnostic does not
# belong in the narrative -- and the per-document requirement above already
# handles that through its "--" marker.
# NaN is truthy in Python, so `value or ""` leaves a NaN in place and str() turns
# it into the non-empty string "nan". Every emptiness test below goes through
# this helper instead.
def _missing(v):
    return v is None or (isinstance(v, float) and pd.isna(v)) or not str(v).strip() or str(v).strip().lower() == "nan"

DISPOSITIONS = {"retained", "retested", "reworded", "superseded",
                "retracted", "v1_only", "undecided"}
NEEDS_REASON = {"superseded", "retracted", "reworded"}
NEEDS_REPLACEMENT = {"superseded", "retracted"}

sup = []
if "v2_disposition" in m.columns:
    for _, r in m.iterrows():
        d = "" if _missing(r.get("v2_disposition")) else str(r.get("v2_disposition")).strip()
        cid = r["id"]
        if d not in DISPOSITIONS:
            sup.append((cid, f"disposition '{d}' is not one of {sorted(DISPOSITIONS)}"))
            continue
        if d in NEEDS_REASON and _missing(r.get("decision_reason")):
            sup.append((cid, f"'{d}' requires a decision_reason"))
        if d in NEEDS_REPLACEMENT and _missing(r.get("replacement_claim_id")):
            sup.append((cid, f"'{d}' requires a replacement_claim_id (use 'none' if deliberate)"))
        if d == "superseded" and _missing(r.get("superseded_by")):
            sup.append((cid, "'superseded' requires superseded_by"))

undecided = sum(1 for _, r in m.iterrows()
                if not _missing(r.get("v2_disposition"))
                and str(r.get("v2_disposition")).strip() == "undecided")
if undecided:
    print(f"SUPERSESSION: {undecided} of {len(m)} claims still 'undecided' "
          f"— expected until V2 gates settle; not a failure.\n")
if sup:
    print(f"SUPERSESSION PROBLEMS ({len(sup)}):")
    for cid, msg in sup:
        print(f"  {cid:5} {msg}")
    print()

print(f"Audited {len(m)} claims x 3 documents\n")
if problems:
    print(f"{len(problems)} claim/document pairs need a manual check:\n")
    print(f"{'id':5} {'doc':10} {'req':5} {'element':20} claim")
    for cid, el, claim, doc, need in problems:
        print(f"{cid:5} {doc:10} {need:5} {el:20} {claim}")
else:
    print("PARITY OK: every claim required in a document was found in it.")

print(f"\n{'=' * 70}")
print(f"{len(m) * 3 - sum(1 for _, r in m.iterrows() for d in DOCS if r[d] == '--') - len(problems)}"
      f" of {len(m) * 3 - sum(1 for _, r in m.iterrows() for d in DOCS if r[d] == '--')} required claim/document pairs present")
sys.exit(1 if (problems or sup) else 0)
