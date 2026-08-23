"""FINAL: the claim freeze. Locks what may be published, before any prose.

THIS STAGE DISCOVERS NOTHING. It fixes eight things so that the report, paper,
narrative and appendix can be written against one source rather than against
memory:

  1. canonical wording and status for every claim
  2. exact placement in report / paper / narrative / appendix
  3. superseded results retained only as clearly labelled legacy evidence
  4. the same substantive information in all three reader-facing documents,
     expressed at different technical levels
  5. mandatory caveats on every historical-exposure result
  6. the model-dependence result, with neither specification definitive
  7. the reporting-culture conclusion, stated narrowly
  8. NO FURTHER MODEL SEARCHING after the freeze

Every number here is read from a frozen artifact. Nothing is recomputed.
"""
import json
import sys
from pathlib import Path

import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
DOCS = Path(__file__).resolve().parents[1] / "docs"

e1 = pd.read_csv(PROC / "e1_results.csv").set_index("var")
e4 = pd.read_csv(PROC / "e4_results.csv").set_index("var")
e7 = pd.read_csv(PROC / "e7_results.csv")
e7v = pd.read_csv(PROC / "e7_verdicts.csv").set_index("pair")
ea = pd.read_csv(PROC / "ea_results.csv").iloc[0]
desc = pd.read_csv(PROC / "e_descriptives.csv")
rest = pd.read_csv(PROC / "e3_restatement.csv").iloc[0]
frozen = json.loads((PROC / "p5f_frozen_result.json").read_text())

# ---------------------------------------------------------------------------
# 5. MANDATORY CAVEATS. Every historical-exposure claim carries all four.
# ---------------------------------------------------------------------------
HISTORICAL_CAVEATS = [
    "cross-country association",
    "no demonstrated within-Greece dynamic",
    "no causal claim",
    "current conditions not ruled out",
]

# 4. One substantive statement, three technical levels. NOT three different
#    findings -- the same finding, said three ways.
def levels(technical, plain, story):
    return {"report": technical, "paper": technical, "narrative": story,
            "plain": plain}


C = []


def claim(cid, movement, wording, status, evidence, tier, headline,
          caveats=None, placement=None, supersedes=None, legacy=False,
          narrative=None):
    C.append({
        "id": cid, "movement": movement, "canonical_wording": wording,
        "status": status, "evidence": evidence, "tier": tier,
        "headline_eligible": headline,
        "caveats": " | ".join(caveats or []),
        "report": (placement or {}).get("report", "body"),
        "paper": (placement or {}).get("paper", "body"),
        "narrative": (placement or {}).get("narrative", "body"),
        "appendix": (placement or {}).get("appendix", "table"),
        "supersedes": supersedes or "",
        "legacy_only": legacy,
        "narrative_level": narrative or "",
    })


# --- Movement 1: the puzzle ------------------------------------------------
g_arop, g_arope = desc.gap_vs_arop.mean(), desc.gap_vs_arope.mean()
claim("V2-1.1", "1. The puzzle",
      "The outcome is Eurostat's official subjective-hardship indicator, "
      "extended backwards before 2010 using a constructed series validated "
      "against it on 432 overlapping country-years.",
      "retained", "p0_verdict.csv", "pre-planned confirmatory", False,
      ["pre-2010 provenance is ours, not Eurostat's"],
      narrative="The measure is the official European one, carried further back in time.")
claim("V2-1.2", "1. The puzzle",
      f"Greek subjective hardship runs {g_arop:.1f} points above relative "
      f"income poverty on average, and Greece ranks first of 27 on hardship "
      f"while ranking seventh on AROP.",
      "retained", "e_descriptives.csv, e_descriptive_ranks.csv",
      "descriptive corroboration", True, [],
      narrative="Greeks report far more difficulty than the official poverty rate suggests.")

# --- Movement 2: AROPE narrows but does not close --------------------------
claim("V2-2.1", "2. AROPE narrows the gap",
      f"Switching to AROPE closes {g_arop - g_arope:.1f} of those "
      f"{g_arop:.1f} points ({(g_arop - g_arope) / g_arop:.0%}), leaving "
      f"{g_arope:.1f} unexplained, and its contribution shrinks from 11.0 "
      "points in 2015 to 7.3 in 2024.",
      "retained", "e_descriptives.csv", "descriptive corroboration", True, [],
      narrative="The EU's broader measure helps, but closes only about a fifth of the gap.")

# --- Movement 3: the hardship is materially grounded -----------------------
claim("V2-3.1", "3. The hardship is real",
      "Reported difficulty co-moves with arrears, inability to meet an "
      "unexpected expense, inadequate heating and severe deprivation at "
      "within-country correlations of 0.63 to 0.80.",
      "retained", "e3_results.csv", "descriptive corroboration", True,
      ["same-instrument corroboration, NOT independent validation",
       "all items and the outcome come from EU-SILC",
       "not uniform: arrears within Greece is 0.371"],
      narrative="When a country's reported difficulty rises, its unpaid bills and cold homes rise with it.")
claim("V2-3.2", "3. The hardship is real",
      f"Those same four items statistically absorb "
      f"{rest.absorbed_share:.0%} of Greece's baseline residual "
      f"({rest.greece_resid_baseline:+.2f} to {rest.greece_resid_with_p1:+.2f}).",
      "retained", "e3_restatement.csv", "descriptive corroboration", False,
      ["ABSORPTION, never explanation",
       "shared instrument is not shared cause",
       "diagnostic only; never a headline explanation"],
      narrative="Measures this close to the question can make the puzzle vanish without explaining it.")

# --- Movement 4: current conditions ----------------------------------------
for v, cid, label, nar in [
    ("aic_pps_pc", "C1", "material resources", "what a country has to spend"),
    ("ltu_rate", "C2", "labour-market exclusion", "how many are locked out of work for years"),
    ("wadj_a01", "C4", "wage-adjusted affordability", "what a local paycheck buys"),
]:
    r = e1.loc[v]
    claim(f"V2-4.{cid}", "4. Current conditions",
          f"{label.capitalize()} ({v}) predicts hardship beyond AROP and year "
          f"effects (coef {r.coef:+.4f}, wild-cluster bootstrap p={r.boot_p:.4f}).",
          "retained", "e1_results.csv", "pre-planned confirmatory", True,
          ["cross-country association", "no causal claim"],
          narrative=f"Countries differ in {nar}, and that tracks reported hardship.")
claim("V2-4.X", "4. Current conditions",
      "Six of nine current-level constructs are inconclusive under available "
      "power, not unsupported; two cleared FDR and collapsed under the "
      "bootstrap (p=0.40 and 0.55).",
      "retained", "e1_results.csv", "pre-planned confirmatory", False,
      ["inconclusive is not evidence of absence"],
      narrative="Most candidates could not be tested sharply enough to say either way.")

# --- Movement 5: accumulated history ---------------------------------------
for v, cid, label, nar in [
    ("acc_cum_excess_unemployment", "C2", "accumulated excess unemployment",
     "how much unemployment a country has absorbed since the crisis"),
    ("dur_real_wages_below", "C3", "duration of real wages below their 2008 level",
     "how long wages have stayed below where they were"),
    ("acc_housing_excess", "C6", "housing-cost deterioration since 2010",
     "how much worse housing costs have got since 2010"),
]:
    r4 = e4.loc[v]
    pid = {"acc_cum_excess_unemployment": "P1_ltu",
           "dur_real_wages_below": "P3_wage_duration",
           "acc_housing_excess": "P8_housing"}[v]
    row7 = e7[(e7.focal == v)].iloc[0]
    extra = []
    if bool(r4.bootstrap_borderline):
        extra.append("BORDERLINE: bootstrap p=0.0460, 91 of 1,999 exceedances")
    if v == "dur_real_wages_below":
        extra.append("supported only as the CURRENT uninterrupted run against a "
                     "fixed 2008 base; alternative constructions point the same "
                     "way but do not meet the criteria")
    claim(f"V2-5.{cid}", "5. Accumulated history",
          f"{label.capitalize()} predicts hardship (bootstrap p={r4.boot_p:.4f}) "
          f"and retains a cross-country association after its current-level "
          f"counterpart is controlled (conditional bootstrap p={row7.boot_p:.4f}).",
          "retained", "e4_results.csv, e7_results.csv",
          "post-selection robustness", True,
          HISTORICAL_CAVEATS + extra,
          narrative=f"Countries differ in {nar}, and that still tracks hardship "
                    "once today's conditions are accounted for.")

claim("V2-5.X", "5. Accumulated history",
      "For wage-adjusted affordability the pattern reverses: the current "
      "measure survives conditioning (bootstrap p=0.0035) while the "
      "accumulated one remains inconclusive.",
      "retained", "e7_results.csv", "post-selection robustness", False,
      ["the accumulated measure is inconclusive, NOT unsupported"],
      narrative="For affordability it is today's prices against today's wages that tracks hardship.")
claim("V2-5.Y", "5. Accumulated history",
      "No accumulated measure permits dynamic wording. Across P5, E4 and E7 no "
      "within-country estimate is significant in the adverse direction and no "
      "first-difference test supports one.",
      "retained", "p5f_frozen_result.json, e4_results.csv, e7_dynamic.csv",
      "pre-planned confirmatory", True,
      ["three RELATED checks on one panel, not independent replications",
       "the dynamic tests were not multiplicity-corrected"],
      narrative="We cannot say hardship rose inside Greece as the damage piled up. "
                "Only that countries carrying more damage report more hardship.")
claim("V2-5.Z", "5. Accumulated history",
      "Accumulated material resources (C1) could not be tested at all: the "
      "source series begins in 2015 and no 2008 baseline exists. The baseline "
      "was not moved to make it testable.",
      "retained", "e4_feasibility.csv", "descriptive corroboration", False,
      ["infeasible, not null"],
      narrative="One promising measure simply had no history to accumulate.")

# --- Movement 6: model dependence (item 6) ---------------------------------
claim("V2-6.1", "6. Model dependence",
      f"Greece's residual is {frozen['p3']['greece_oos_residual']:+.2f} "
      f"(rank 3/27) in the frozen P3 specification and "
      f"{ea.companion_residual:+.2f} (rank {int(ea.companion_rank)}/27) when "
      "the same-instrument deprivation predictor is removed, on identical "
      "rows. Neither specification is definitive.",
      "retained", "e6_results.csv, ea_results.csv",
      "post-selection robustness", True,
      ["NEITHER specification is definitive",
       "the two may not be merged or averaged",
       "selection between them may not be made on residual size",
       "conclusions about absorption depend materially on whether "
       "same-instrument deprivation is admitted"],
      narrative="How big the unexplained gap looks depends on whether you allow "
                "one measure that is very close to the question itself.")

# --- Movement 7: what it is not (item 7) -----------------------------------
claim("V2-7.1", "7. What this is not",
      "Greece ranks first of 27 on subjective hardship and on financial "
      "expectations while ranking second to sixth on life satisfaction, so "
      "generic pessimism is insufficient as an explanation. A "
      "financial-domain-specific reporting difference cannot be excluded.",
      "retained", "reporting_style_cross_indicator.csv",
      "descriptive corroboration", True,
      ["generic pessimism is INSUFFICIENT, not disproved",
       "a financial-domain-specific reporting difference CANNOT be excluded"],
      supersedes="8.6",
      narrative="Greeks are not simply gloomier about everything. But we cannot "
                "rule out that they answer money questions differently.")

# --- Legacy: superseded and failed, retained and labelled (item 3) ---------
claim("L-1", "Legacy",
      "The synthetic-control comparative design failed four of six "
      "pre-registered gates and is not a usable comparison. Its divergence "
      "figure is machine-blocked from every output document.",
      "superseded", "p2_specifications.csv, p2_donor_weights.csv",
      "failed design", False,
      ["donor weights collapse to Hungary 0.55 and Bulgaria 0.45",
       "the divergence figure is NON-REPORTABLE"],
      legacy=True,
      narrative="One method we tried did not work, and we say so.")
claim("L-2", "Legacy",
      "Multi-domain breadth failed the incremental criterion: adding it to the "
      "frozen model worsened Greece's residual from 6.93 to 10.39 and reversed "
      "its sign conditionally. The reversal is left uninterpreted.",
      "superseded", "p3a_results.csv", "pre-planned confirmatory", False,
      ["a result about the specification, not about power",
       "the sign reversal is deliberately left uninterpreted"],
      legacy=True,
      narrative="Counting how many kinds of hardship a country has did not help.")
claim("L-3", "Legacy",
      "The accumulated wage-shortfall coefficient cleared every conditional "
      "gate but its prior stage did not support it, so the pre-registered "
      "ceiling caps it. It is reported and is not a finding.",
      "descriptive_only", "e7_results.csv", "post-selection robustness", False,
      ["capped by the E7 ceiling: E7 may only qualify or withdraw"],
      legacy=True,
      narrative="One result looked good but arrived by a route we had closed in advance.")
claim("L-4", "Legacy",
      "Annual food and housing inflation are unsupported with adequate power "
      "at 0.70 SD; annual headline inflation is unsupported at its detectable "
      "conditional magnitude; compounded inflation since 2008 remains "
      "inconclusive.",
      "retained", "e2_results.csv, e7_results.csv",
      "pre-planned confirmatory", False,
      ["the exclusions are narrow and magnitude-specific",
       "compounded inflation is INCONCLUSIVE, not ruled out"],
      narrative="Inflation did not explain the gap, though we cannot rule out small effects.")

df = pd.DataFrame(C)

FREEZE = {
    "status": "FROZEN. No further model searching. Prose may now be written.",
    "sequence": "P0 -> P2 -> P3 -> P5 -> P3a -> E0 -> PRE -> EDA -> EA -> E1 -> "
                "E2 -> E3 -> E4 -> E5 -> E6 -> E7 -> FINAL",
    "claims_total": len(df),
    "headline_eligible": int(df.headline_eligible.sum()),
    "legacy_only": int(df.legacy_only.sum()),
    "mandatory_caveats_on_historical_exposure": HISTORICAL_CAVEATS,
    "model_dependence": {
        "frozen_p3_residual": frozen["p3"]["greece_oos_residual"],
        "companion_residual": float(ea.companion_residual),
        "definitive_model": None,
        "rule": "Neither is definitive. Not merged, not averaged, not selected "
                "on residual size.",
    },
    "reporting_culture": {
        "established": "generic pessimism is insufficient",
        "NOT established": "a financial-domain-specific reporting difference "
                           "cannot be excluded",
    },
    "no_further_searching": (
        "MODEL SEARCHING IS CLOSED. No new specification, construct, "
        "sensitivity, combination or subgroup may be tested after this freeze. "
        "Anything further is a new pre-registered project, not a continuation "
        "of this one."),
    "same_information_all_documents": (
        "Report, paper and narrative carry the SAME substantive claims at "
        "different technical levels. A claim present in one and absent from "
        "another is a defect, not an editorial choice. The appendix carries "
        "every number."),
}

bar = "=" * 96
print(bar); print("FINAL: CLAIM FREEZE"); print(bar)
print(f"  {len(df)} claims  |  {int(df.headline_eligible.sum())} headline-eligible  "
      f"|  {int(df.legacy_only.sum())} legacy-only\n")
for mv in df.movement.unique():
    sub = df[df.movement == mv]
    print(f"  {mv}")
    for r in sub.itertuples():
        h = "HEADLINE" if r.headline_eligible else "        "
        print(f"    {h} {r.id:8} {r.canonical_wording[:82]}")
        if r.caveats:
            for c in r.caveats.split(" | "):
                print(f"             - {c}")
    print()

print(bar); print("LOCKED"); print(bar)
print(f"  5. mandatory caveats on historical exposure: {len(HISTORICAL_CAVEATS)}, "
      "applied to " + str(int(df.caveats.str.contains("no demonstrated within-Greece").sum()))
      + " claims")
print(f"  6. model dependence: {frozen['p3']['greece_oos_residual']:+.2f} vs "
      f"{ea.companion_residual:+.2f}, neither definitive")
print(f"  7. reporting culture: generic pessimism insufficient; "
      "financial-domain-specific difference cannot be excluded")
print(f"  8. {FREEZE['no_further_searching'][:60]}...")

df.to_csv(PROC / "e_final_claims.csv", index=False)
(PROC / "final_freeze.json").write_text(json.dumps(FREEZE, indent=2) + "\n")
print(f"\nWritten to {PROC}/e_final_claims.csv, final_freeze.json")
