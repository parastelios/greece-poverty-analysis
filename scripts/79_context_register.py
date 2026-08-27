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
        # Follows V2-7.1's narrowing: Greece is second-WORST on life
        # satisfaction by 2024, not middling.
        "permitted": "The financial indicators are more extreme than the "
                     "general-wellbeing one, which suggests domain "
                     "specificity. A broader negative reporting tendency is "
                     "NOT ruled out.",
        "forbidden": "Describing Greece as ordinary or middling on life "
                     "satisfaction: it is second-worst in the EU by 2024. And "
                     "reading a worsening RANK as falling satisfaction, when "
                     "the Greek level rose over the period.",
        # The one context topic that IS a tested claim. It POINTS at the frozen
        # claim rather than restating it, so there is a single source.
        "relates_to_claim": "V2-7.1",
        "evidence": "reporting_style_cross_indicator.csv",
        "detect": "generic pessimism|reporting style|reporting culture",
        "source": "reporting_style_cross_indicator.csv, this project",
        "source_url": "", "source_detail": "Greece ranks 1st of 27 on hardship "
                        "and financial expectations, 2nd-6th on life satisfaction.",
        "source_status": "verified", "review_date": "2026-08-23",
        "verified_how": "this project's own artifact",
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
        "source": "OECD (2024), OECD Survey on Drivers of Trust in Public "
                  "Institutions - 2024 Results, Country Notes: Greece. OECD "
                  "Publishing, Paris.",
        "source_url": "https://www.oecd.org/en/publications/oecd-survey-on-drivers-of-trust-in-public-institutions-2024-results-country-notes_a8004759-en/greece_56edc018-en.html",
        "source_detail": "Fieldwork October-November 2023, 30 OECD countries. "
                         "32% of Greek respondents report high or moderately "
                         "high trust in central government against an OECD "
                         "average of 39%.",
        "source_status": "verified", "review_date": "2026-08-23",
        "verified_how": "primary PDF read directly, pages 1-2",
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
        "source": "Andriopoulou, E., Kanavitsa, E. & Tsakloglou, P. (2020), "
                  "Decomposing Poverty in Hard Times: Greece 2007-2016. LSE "
                  "GreeSE Paper No. 149.",
        "source_url": "https://www.lse.ac.uk/Hellenic-Observatory/Publications/GreeSE-Papers",
        "source_detail": "EU-SILC microdata, ELSTAT waves 2008-2017. Anchored "
                         "FGT0 on a 2007 base reaches 48% at the 2013 peak.",
        "source_status": "verified", "review_date": "2026-08-23",
        "verified_how": "read in full; recorded in docs/archive/pre-v2-publication/publication_strategy.md",
    },
    {
        "id": "CTX-4", "topic": "Migration",
        "status": "contextual consequence",
        # BIDIRECTIONAL. Migration is both a plausible consequence of prolonged
        # labour-market damage and a possible contributor to it. What the
        # project can say is only that it is unsupported as an independent
        # aggregate predictor on this panel.
        "permitted": "A plausible consequence of prolonged labour-market damage "
                     "and a possible contributor to it. It is UNSUPPORTED as an "
                     "independent aggregate predictor here.",
        "forbidden": "Reading it as a driver, or as ruled out. E3 tested it on "
                     "this panel and found nothing (p=0.4006), which speaks to "
                     "aggregate prediction and not to either causal direction.",
        "relates_to_claim": "", "evidence": "e3_results.csv (null), external literature",
        "detect": "net migration|emigration|brain drain",
        "source": "Lazaretou, S. (2016), The Greek brain drain: the new "
                  "pattern of Greek emigration during the recent crisis. "
                  "Economic Bulletin, Bank of Greece, issue 43, pp. 31-53.",
        "source_url": "https://www.bankofgreece.gr/BogEkdoseis/econbull201607.pdf",
        "source_detail": "427,000 residents aged 15-64 left permanently "
                         "2008-2013; ~223,000 of them aged 25-39. The E3 null "
                         "(p=0.4006) is this project's own evidence.",
        "source_status": "verified", "review_date": "2026-08-23",
        "verified_how": "RePEc record confirmed: bog:econbl:y:2016:i:43:p:31",
    },
    {
        "id": "CTX-5", "topic": "Tax burden and unequal treatment",
        "status": "future hypothesis",
        "permitted": "Published incidence evidence establishes that Greece's "
                     "indirect tax system became markedly more regressive over "
                     "the crisis. Whether that channel contributes to the "
                     "hardship gap is a plausible hypothesis and is NOT tested "
                     "here.",
        "forbidden": "Any quantitative statement linking tax burden to the "
                     "hardship gap. The literature is about incidence, not "
                     "about this outcome, and this project tested nothing on "
                     "tax.",
        "relates_to_claim": "", "evidence": "none in this project",
        "detect": "tax burden|tax incidence|tax system|taxation",
        # KEPT, not dropped: an adequate published incidence study exists.
        # What remains untested is the LINK from tax burden to the hardship
        # gap, which is why the status stays "future hypothesis".
        "source": "Kaplanoglou, G. (2015), Who Pays Indirect Taxes in Greece? "
                  "From EU Entry to the Fiscal Crisis. Public Finance Review "
                  "43(4), 529-556.",
        "source_url": "https://doi.org/10.1177/1091142113517925",
        "source_detail": "Microsimulation on Household Expenditure Survey data, "
                         "1988-2011. The 2011 indirect tax system is the most "
                         "regressive of the period, with the sharpest effects "
                         "on families with children and the unemployed.",
        "source_status": "verified", "review_date": "2026-08-23",
        "verified_how": "DOI resolved to the publisher record; author, title, "
                        "volume, issue, pages and year confirmed",
    },
    {
        "id": "CTX-6", "topic": "Policy implications",
        "status": "author interpretation",
        "permitted": "POLICY RECOMMENDATION, NOT AN EMPIRICAL CONCLUSION: "
                     "poverty dashboards should combine AROP, its real "
                     "threshold, anchored poverty, AROPE/deprivation and "
                     "accumulated labour and housing indicators.",
        "forbidden": "Presenting this as a finding. It follows from what the "
                     "analysis showed AROP alone misses; it is not itself a "
                     "result.",
        "relates_to_claim": "", "evidence": "authors' reading of V2-1.2, V2-2.1, V2-5.*",
        "detect": "policy implication|dashboard should|we recommend|should combine",
        "source": "not applicable -- authors' interpretation of V2-1.2, V2-2.1 and V2-5.*",
        "source_url": "", "source_detail": "",
        "source_status": "not applicable", "review_date": "2026-08-23",
        "verified_how": "not applicable",
    },
    {
        # Added after the ESS aggregates were obtained from the portal's public
        # Analysis tab. It is descriptive context, not a tested result: the
        # means are approximate reconstructions with no confidence intervals,
        # and no test was run on them.
        "id": "CTX-7", "topic": "Pre-crisis wellbeing baseline (ESS)",
        "status": "descriptive corroboration",
        "permitted": "On a balanced set of 12 countries observed in every Greek "
                     "ESS round, Greece already sat about 0.8 points below the "
                     "median before the crisis, fell to 5.64 by 2010/11, and "
                     "recovered its LEVEL to roughly the pre-crisis value by "
                     "2023/24. Its comparative position did not recover: the "
                     "gap to the balanced median is wider than before the "
                     "crisis, and Greece has been worst of the 12 since "
                     "2010/11. A longstanding low-wellbeing pattern therefore "
                     "remains plausible and generic pessimism or reporting "
                     "culture CANNOT be dismissed.",
        "forbidden": "Splicing ESS to the Eurostat EU-SILC series, or reading "
                     "the two as one trajectory. Attaching any confidence "
                     "interval, standard error or significance test to these "
                     "means, which are approximate reconstructions from "
                     "displayed weighted percentages. Comparing ALL-COUNTRY "
                     "ranks across rounds, since the country set varies from "
                     "22 to 30. Treating the decade after 2010/11 as observed.",
        "relates_to_claim": "V2-7.1",
        "evidence": "ESS Data Portal public Analysis tab, stflife, six Greek rounds",
        # Deliberately ESS-specific. An earlier version matched the bare phrase
        # "pre-crisis baseline", which the narrative uses about the social
        # safety net and which has nothing to do with this entry.
        "detect": "European Social Survey|ESS round|stflife|"
                  "balanced 12 countries|same 12 countries|same twelve countries",
        "source": "European Social Survey Data Portal, public Analysis tab for "
                  "stflife (life satisfaction, 0-10), rounds 1, 2, 4, 5, 10 and 11.",
        "source_url": "https://ess.sikt.no/en/",
        "source_detail": "Weighted distributions with the post-stratification "
                         "weight; country means reconstructed by the authors.",
        "source_status": "verified",
        "review_date": "2026-08-23",
        "verified_how": "per-round analysis URLs recorded in "
                        "data/raw/ess/ess_life_satisfaction_round_summary.csv; "
                        "stated percentiles recomputed from stated ranks and "
                        "country counts, all six agree",
    },
    {
        # An independently published piece reaching a similar descriptive
        # picture by a different route: no access to this project's panel, no
        # bootstrap, no FDR, no within/between split, no model comparison. It
        # corroborates the SHAPE of V2-4.C1/V2-4.C4, not the inference behind
        # them, and its own numbers are a different (2025/2026) vintage from
        # this project's frozen 2015-2024 panel.
        "id": "CTX-8", "topic": "Independent descriptive corroboration (Greece in Figures)",
        "status": "descriptive corroboration",
        "permitted": "The independent picture -- Greece not last on actual "
                     "consumption, long hours for comparatively low hourly "
                     "reward, high relative prices in food and information/"
                     "communication -- is consistent with and external "
                     "corroboration for this project's own material-resources "
                     "and wage-adjusted-affordability findings. Its central "
                     "descriptive numbers reproduce against the primary "
                     "Eurostat and ELSTAT releases they draw on.",
        "forbidden": "Treating the article's own comparisons, or its "
                     "constructed AIC-per-hour ratio, as inferential evidence: "
                     "it applies no bootstrap, no FDR correction, no "
                     "within/between decomposition and no model comparison, "
                     "and it does not test whether these factors account for "
                     "reported hardship. Merging its 2025/2026-vintage figures "
                     "into this project's frozen 2015-2024 panel. Repeating "
                     "its car-ownership sentence, which cites a vehicle-STOCK "
                     "figure as evidence of new purchases, or its 'all Greeks "
                     "travelled' generalisation, which the underlying ELSTAT "
                     "survey does not support. Reading its AIC rank, hours "
                     "rank or price-level figure as contradicting this "
                     "project's own numbers without first noting the "
                     "different vintage or aggregate behind each.",
        "relates_to_claim": "V2-4.C4",
        "evidence": "external analysis; not evaluated by this project's "
                    "statistical protocol",
        "detect": "Greece in Figures|greeceinfigures|niothoun toso ptokhoi|"
                  "AIC per hour worked",
        "source": "Greece in Figures, \"Γιατί οι "
                  "Έλληνες νιώθουν "
                  "τόσο φτωχοί\" "
                  "[Why Greeks feel so poor].",
        "source_url": "https://www.greeceinfigures.com/analyses/giati-oi-ellenes-niothoun-toso-phtokhoi/",
        "source_detail": "Constructs an AIC-per-hour ratio from aggregate "
                         "actual individual consumption and aggregate annual "
                         "hours worked; cites 2025-vintage Eurostat AIC and "
                         "price-level releases and a 2026 ELSTAT resident "
                         "travel bulletin.",
        "source_status": "verified",
        "review_date": "2026-08-26",
        "verified_how": "the article's headline figures (AIC per capita rank, "
                        "annual hours worked, the constructed AIC-per-hour "
                        "figure, overall and category price-level indices, "
                        "resident trip counts) were checked one by one "
                        "against the primary Eurostat AIC 2025 release, the "
                        "Eurostat 2025 price-level release, the Eurostat "
                        "working-week comparison and the ELSTAT resident "
                        "travel survey; all reproduce. Two claims in the "
                        "article do not hold up: its car-purchase sentence "
                        "cites a vehicle-stock number, and its travel "
                        "sentence over-generalises to all residents.",
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
for col in ("source", "source_status", "review_date", "verified_how"):
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
if len(pend):
    print("  A REQUIRED-PENDING entry may NOT be written up until its citation")
    print("  exists and is verified against the primary release.")
else:
    print("  All citable entries are verified against their primary release.")
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
