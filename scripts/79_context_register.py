"""Stage 7: the context register.

A SEPARATE ARTIFACT FROM THE CLAIM FREEZE, AND DELIBERATELY SO. The 22 frozen
claims are what the analysis established. This register holds what the
discussion may say ABOUT that analysis without estimating anything new.

The hazard it exists to prevent is an informal second model: a discussion in
which trust, taxation, crisis policy and migration are lined up next to the
statistical findings until they read as competing estimates. They are not
estimates. Nothing here was tested, and after the FINAL freeze nothing here CAN
be tested without opening a new pre-registered project.

So the two registers use DIFFERENT status vocabularies, and no entry here is
headline-eligible as an empirical finding. A context entry may never be cited as
support for an analytical claim.
"""
import json
import sys
from pathlib import Path

import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
claims = pd.read_csv(PROC / "e_final_claims.csv")

ANCHOR = (
    "The statistical analysis identifies where Greece's hardship aligns with "
    "material conditions and accumulated history. It does not identify which "
    "institutions or policies produced that history. Crisis policy, taxation, "
    "trust and migration therefore belong in the interpretation as plausible "
    "context, not as estimated explanations.")

# Deliberately disjoint from the claim register's vocabulary.
STATUSES = {
    "descriptive corroboration": "tested in this project; a frozen claim exists",
    "contextual evidence": "evidence exists, but not identified here",
    "literature-grounded context": "external literature; not estimated here",
    "contextual consequence": "consistent with the findings; not an explanation of them",
    "future hypothesis": "requires data this project does not have",
    "author interpretation": "the authors' reading, not an empirical result",
}

ENTRIES = [
    {
        "id": "CTX-1", "topic": "Financial expectations and life satisfaction",
        "status": "descriptive corroboration",
        "permitted": "Generic pessimism is insufficient; financially specific "
                     "reporting differences remain possible.",
        "forbidden": "Concluding that reporting style plays no part, or that a "
                     "financial-domain difference has been ruled out.",
        # The one context topic that IS a tested claim. It POINTS at the frozen
        # claim rather than restating it, so there is a single source.
        "relates_to_claim": "V2-7.1",
        "evidence": "reporting_style_cross_indicator.csv",
        "detect": "generic pessimism|reporting style|reporting culture",
        "source": "reporting_style_cross_indicator.csv, this project",
        "source_status": "verified", "review_date": "2026-08-23",
    },
    {
        "id": "CTX-2", "topic": "Institutional trust",
        "status": "contextual evidence",
        "permitted": "May affect how households interpret insecurity; available "
                     "evidence does not identify an independent effect.",
        "forbidden": "Presenting trust as an explanation of the residual, or "
                     "implying it was tested and found to matter.",
        "relates_to_claim": "", "evidence": "external literature",
        "detect": "institutional trust|trust in institutions|trust in the state",
        # FLAGGED: no verified citation is held. Naming what is required is
        # honest; inventing a reference is not, and this project has already
        # been bitten by unverifiable citations.
        "source": "REQUIRED: a trust series with Greek coverage over the "
                  "window -- Eurobarometer institutional-trust items or the "
                  "OECD Trust Survey -- cited to the primary release, not to "
                  "a secondary summary",
        "source_status": "REQUIRED-PENDING", "review_date": "2026-08-23",
    },
    {
        "id": "CTX-3", "topic": "Crisis and adjustment policies",
        "status": "literature-grounded context",
        "permitted": "Help explain the historical setting; this project does "
                     "not estimate their causal contribution.",
        "forbidden": "Attributing any share of the accumulated exposure to a "
                     "specific programme or measure.",
        "relates_to_claim": "", "evidence": "external literature",
        "detect": "adjustment programme|adjustment program|austerity|bailout|memorandum",
        "source": "REQUIRED: the adjustment-programme literature already "
                  "verified in publication_strategy.md, incl. Andriopoulou, "
                  "Kanavitsa & Tsakloglou (LSE GreeSE 149, 2020)",
        "source_status": "REQUIRED-PENDING", "review_date": "2026-08-23",
    },
    {
        "id": "CTX-4", "topic": "Migration",
        "status": "contextual consequence",
        "permitted": "Consistent with prolonged scarring; not supported as an "
                     "independent explanation of the gap.",
        "forbidden": "Reading it as a driver. E3 tested it and found nothing "
                     "(p=0.4006), and its causal position is ambiguous by "
                     "construction.",
        "relates_to_claim": "", "evidence": "e3_results.csv (null), external literature",
        "detect": "net migration|emigration|brain drain",
        "source": "e3_results.csv for the null; REQUIRED for the contextual "
                  "reading: a Greek emigration source covering 2008 onward",
        "source_status": "REQUIRED-PENDING", "review_date": "2026-08-23",
    },
    {
        "id": "CTX-5", "topic": "Tax burden and unequal treatment",
        "status": "future hypothesis",
        "permitted": "A plausible distributional channel requiring dedicated "
                     "tax-incidence data; not tested here.",
        "forbidden": "Any quantitative statement. This project holds no "
                     "tax-incidence data and none may be added post-freeze.",
        "relates_to_claim": "", "evidence": "none in this project",
        "detect": "tax burden|tax incidence|tax system|taxation",
        # FLAGGED: the weakest-sourced entry. It is a future hypothesis and
        # must not appear at all until a citation exists.
        "source": "REQUIRED: tax-incidence microdata or a published Greek "
                  "incidence study. NONE is held by this project, and the "
                  "entry may not be written up without one",
        "source_status": "REQUIRED-PENDING", "review_date": "2026-08-23",
    },
    {
        "id": "CTX-6", "topic": "Policy implications",
        "status": "author interpretation",
        "permitted": "Poverty dashboards should combine AROP, its real "
                     "threshold, anchored poverty, AROPE/deprivation and "
                     "accumulated labour and housing indicators.",
        "forbidden": "Presenting this as a finding. It follows from what the "
                     "analysis showed AROP alone misses; it is not itself a "
                     "result.",
        "relates_to_claim": "", "evidence": "authors' reading of V2-1.2, V2-2.1, V2-5.*",
        "detect": "policy implication|dashboard should|we recommend|should combine",
        "source": "not applicable -- authors' interpretation of V2-1.2, V2-2.1 and V2-5.*",
        "source_status": "not applicable", "review_date": "2026-08-23",
    },
]

PLACEMENT = {
    "report": "full contextual discussion with evidence-status labels",
    "paper": "concise competing-explanations and policy-implications section",
    "narrative": "one readable chapter connecting the findings to lived "
                 "institutional context",
    "appendix": "sources, exact indicators, coverage limitations and null tests",
}

df = pd.DataFrame(ENTRIES)
df["headline_eligible"] = False          # never, for any entry
df["may_support_a_claim"] = False        # never, for any entry
for c, v in PLACEMENT.items():
    df["placement_" + c] = v

# ---- guards --------------------------------------------------------------
if df.detect.isna().any() or (df.detect == "").any():
    raise SystemExit("every context entry needs explicit detection phrases: a "
                     "key derived from the topic collapses to generic words "
                     "like 'crisis' or 'policy' and matches everything")
for col in ("source", "source_status", "review_date"):
    if df[col].isna().any() or (df[col].astype(str).str.strip() == "").any():
        raise SystemExit(f"every context entry needs {col}")
if set(df.source_status) - {"verified", "REQUIRED-PENDING", "not applicable"}:
    raise SystemExit(f"unknown source_status: {sorted(set(df.source_status))}")
bad = set(df.status) - set(STATUSES)
if bad:
    raise SystemExit(f"unknown context status: {sorted(bad)}")
if df.headline_eligible.any() or df.may_support_a_claim.any():
    raise SystemExit("a context entry was marked headline-eligible or supporting")
overlap = set(df.status) & set(claims.status)
if overlap:
    raise SystemExit(f"context and claim vocabularies overlap: {sorted(overlap)}")
linked = df[df.relates_to_claim != ""].relates_to_claim
missing = set(linked) - set(claims.id)
if missing:
    raise SystemExit(f"relates_to_claim points at unknown claims: {sorted(missing)}")

bar = "=" * 96
print(bar); print("STAGE 7: CONTEXT REGISTER"); print(bar)
print("  Separate from the claim freeze. Nothing here was tested, nothing here")
print("  is headline-eligible, and no entry may support an analytical claim.\n")
print(f"  ANCHOR\n  {ANCHOR}\n")
for r in df.itertuples():
    print(f"  {r.id}  {r.topic}")
    print(f"        status     {r.status}  ({STATUSES[r.status]})")
    print(f"        permitted  {r.permitted}")
    print(f"        FORBIDDEN  {r.forbidden}")
    if r.relates_to_claim:
        print(f"        points at  {r.relates_to_claim} (single source; not restated)")
    print()

print(bar); print("PLACEMENT"); print(bar)
for c, v in PLACEMENT.items():
    print(f"  {c:10} {v}")

print(f"\n{bar}\nGUARDS PASSED\n{bar}")
print(f"  {len(df)} entries, 0 headline-eligible, 0 able to support a claim")
pend = df[df.source_status == "REQUIRED-PENDING"]
print(f"  sources: {int((df.source_status == 'verified').sum())} verified, "
      f"{len(pend)} REQUIRED-PENDING, "
      f"{int((df.source_status == 'not applicable').sum())} not applicable")
for r in pend.itertuples():
    print(f"    PENDING  {r.id}  {r.topic}")
print("  A REQUIRED-PENDING entry may NOT be written up until its citation")
print("  exists and is verified against the primary release.")
print(f"  status vocabularies are disjoint from the claim register's")
print(f"  the {len(linked)} cross-reference(s) resolve to real frozen claims")
print("  the analytical freeze is untouched: no claim added, removed or reworded")

df.to_csv(PROC / "context_register.csv", index=False)
(PROC / "context_anchor.json").write_text(json.dumps(
    {"anchor": ANCHOR, "statuses": STATUSES, "placement": PLACEMENT,
     "rule": "A context entry may never be cited as support for an analytical "
             "claim, and may never appear without its evidence-status label."},
    indent=2) + "\n")
print(f"\nWritten to {PROC}/context_register.csv, context_anchor.json")
