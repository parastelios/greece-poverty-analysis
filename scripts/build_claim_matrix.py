"""Canonical claim matrix: one row per central claim, with its exact number,
population/window, evidentiary status, statistical caveat, source file, and the
required treatment in each of the three documents.

This is the alignment artifact: the three documents must share one evidentiary
backbone and differ only in depth, tone, and placement. Before any rewrite, this
file is the single source of truth for what each document must contain; after a
rewrite, audit_parity.py checks each document against it.

Treatment codes:  body = must appear in the main text
                  note = may live in a method note / footnote
                  appx = may be relegated to an appendix or expandable block
                  --   = may be omitted from this document entirely
"""
import pandas as pd

C = [
 # id, element, claim, number, population/window, status, caveat, source, report, paper, narrative
 ("1.1", "The puzzle", "Greek subjective poverty is the EU's highest, every year since 2011", "67.2% vs EU 17.6%", "Greece, 2025", "core", "self-reported measure", "master_table.csv", "body","body","body"),
 ("1.2", "The puzzle", "AROP is elevated but not exceptional", "19.6%, 4th of 27", "Greece, 2025", "core", "relative-income measure, not a living-standards indicator", "master_table.csv", "body","body","body"),
 ("1.3", "The puzzle", "The AROP gap is >3x the next largest in the EU", "47.6pt vs Bulgaria 14.9pt", "Greece, 2025", "core", "", "arop_subjective_snapshot_2025.csv", "body","body","body"),
 ("1.4", "The puzzle", "The gap predates the crisis", "48% subjective vs 20.7% AROP", "Greece, 2003", "core", "only 6 countries in EU-SILC in 2003", "master_table.csv", "body","body","body"),

 ("2.1", "Shrinking ruler", "The real poverty threshold fell with median income", "100 -> 65 (2008=100)", "Greece, 2008-2016", "core", "", "analysis_dataset.csv", "body","body","body"),
 ("2.2", "Shrinking ruler", "AROP barely moved while the threshold collapsed", "20.1% -> 21.2%", "Greece, 2008-2016", "core", "", "analysis_dataset.csv", "body","body","body"),
 ("2.3", "Shrinking ruler", "Anchored poverty roughly doubled during the crisis", "~20% -> ~41%", "Greece, 2008-2014", "core", "approximation; least reliable in 2012-2014 where effect is largest", "anchored_poverty.csv", "body","body","body"),
 ("2.4", "Shrinking ruler", "Anchored method validated against the official 2019-anchored series", "MAE 1.22pt, r=0.89", "Greece, 2019-2025", "core", "validated years needed no extrapolation; crisis years do", "anchored_validation.csv", "body","note","note"),
 ("2.5", "Shrinking ruler", "Independent microdata finds a LARGER effect than this reconstruction", "48% vs this report's 40.6%", "Greece, income yr 2013", "core", "different anchor year, data source, price index", "Andriopoulou et al. 2019/2020", "body","body","note"),

 ("3.1", "AROPE bridge", "AROPE narrows the gap but does not close it", "39.7pt, still largest in EU", "Greece, 2025", "core", "", "arope_subjective_snapshot_2025.csv", "body","body","body"),
 ("3.2", "AROPE bridge", "AROPE cannot be reconstructed from aggregate data", "component overlap unpublished", "structural", "limitation", "requires EU-SILC microdata", "n/a", "body","body","note"),
 ("3.3", "AROPE bridge", "AROPE has a 2020/2021 methodology break, spliced not blended", "ilc_peps01 -> ilc_peps01n", "2003-2025", "limitation", "", "docs/comparability_notes.md", "note","note","note"),

 ("4.1", "Current hardship", "Basic model leaves Greece the largest EU residual", "25.6pt OOS, 1st of 27", "27 EU, 2015-2024", "core", "", "model_scorecard.csv", "body","body","body"),
 ("4.2", "Current hardship", "Housing + cash-flow strain narrow it, non-monotonically OOS", "25.6 -> 35.5 -> 11.6", "27 EU, 2015-2024", "core", "housing alone makes OOS worse", "scorecard_loo_*.csv", "body","body","body"),
 ("4.3", "Current hardship", "Arrears and unexpected-expense capacity are close to the outcome", "conceptual caveat", "n/a", "limitation", "not independent predictors", "n/a", "body","body","note"),
 ("4.4", "Current hardship", "Debt and welfare transfers add nothing once housing/cash-flow are in", "p n.s.", "27 EU, 2015-2024", "descriptive", "absorbed, not ruled out", "model_scorecard.csv", "body","note","note"),

 ("5.1", "Duration", "LTU tracks Greek subjective poverty better than any other variable", "r=0.93/0.92/0.86", "Greece, 2009-2024", "core", "survives FDR on all three columns", "correlations_robustness.csv", "body","body","body"),
 ("5.2", "Duration", "Swapping headline->LTU cuts the OOS gap by two-thirds", "11.6 -> 3.9, rank 1st -> 6th", "27 EU, 2015-2024", "core", "replacement not addition (VIF 8-9)", "model_scorecard_ltu.csv", "body","body","body"),
 ("5.3", "Duration", "LTU coefficient stable in all 27 LOO refits incl. excluding Greece", "always p<0.001", "27 EU", "post-selection", "", "scorecard_loo_C_LTU_swap.csv", "body","body","note"),

 ("6.1", "Accumulation", "Cumulative excess unemployment closes the residual", "3.9 -> -0.8", "27 EU, 2015-2024", "post-selection", "fixed spec; variable chosen with Greece in panel", "cumulative_hardship_checkpoint.csv", "body","body","body"),
 ("6.2", "Accumulation", "Survives FDR across the 18-candidate screening family", "adj p=0.0024", "18 tests", "exploratory screening", "wage-duration also survives at adj p=0.0408", "cumulative_hardship_fdr_correction.csv", "body","body","note"),
 ("6.3", "Accumulation", "Selection is stable under nested rescreening", "25 of 27 folds", "27 folds", "post-selection", "both exceptions from same duration family", "nested_selection_validation_folds.csv", "body","body","note"),
 ("6.4", "Accumulation", "Under FULL nested CV Greece is mid-pack, not an outlier", "+2.70pt, rank 19 of 27", "27 folds", "post-selection", "the conservative figure; -0.8 excludes selection cost", "nested_selection_validation_folds.csv", "body","body","body"),
 ("6.5", "Accumulation", "Negative residual does NOT mean Greeks are optimistic", "interpretation", "n/a", "limitation", "property of richest spec only", "n/a", "body","body","body"),
 ("6.6", "Accumulation", "Mechanism is ~a decade of sustained exposure, not permanent accumulation", "10-yr window fits >= permanent", "27 EU", "post-selection", "3-5yr windows fail", "cumulative_hardship_rolling_decay_battery.csv", "body","body","note"),
 ("6.7", "Accumulation", "Aggregate variable, individual-level literature: ecological-inference gap", "level-of-analysis caveat", "n/a", "limitation", "", "n/a", "body","body","note"),
 ("6.8", "Accumulation", "AROP-threshold cumulative shortfall tested and NULL", "p=0.291", "27 EU", "core (null)", "the most anticipated candidate", "cumulative_hardship_checkpoint.csv", "body","body","body"),

 ("10.1", "Objective-only model", "Without accumulation the objective-only model leaves Greece the largest EU residual",
  "+27.05pt OOS, 1st of 27", "27 EU, 2015-2024", "core", "no Tier 0 predictors: excludes arrears, unexpected-expense capacity, financial expectations",
  "p3_objective_only.csv", "body","body","body"),
 ("10.2", "Objective-only model", "Accumulated unemployment narrows the objective-only gap; it does not close it",
  "+27.05 -> +6.93pt, rank 3 of 27", "27 EU, 2015-2024", "core", "model comparison, not a causal decomposition; identical 269-row sample both specs",
  "p5f_frozen_result.json", "body","body","body"),
 ("10.3", "Objective-only model", "The association is predominantly between countries, not within them",
  "between +0.332 p<0.0001; within -0.076 p=0.692", "27 EU, 2015-2024", "post-selection",
  "within estimate inconclusive under available power; equality test p=0.058 fails to reject, is not evidence of equality",
  "p5_audit.csv", "body","body","note"),
 ("10.4", "Failed designs", "The comparative/synthetic-control design was pre-registered and failed",
  "pre-RMSE 0.91 vs placebo median 0.78; 4 of 6 gates failed", "20 donors, 2005-2008", "core (null)",
  "synthetic unit had half Greece's income and 3x its deprivation; no post-crisis effect is interpreted",
  "p2_specifications.csv", "body","body","note"),
 ("10.5", "Failed designs", "Multidomain breadth is descriptive only; it fails the incremental test",
  "famD -2.17 p=0.0044; Greece +6.93 -> +10.39", "27 EU, 2015-2024", "core (null)",
  "stable conditional sign reversal, left uninterpreted; identical sample verified",
  "p3a_results.csv", "body","note","note"),
 ("10.6", "Measurement", "The outcome is Eurostat's official subjective-hardship indicator, extended backward",
  "432 country-years, none differing by >0.1pp", "27 EU, 2010-2025", "core",
  "ilc_sbjp01 from 2010; validated DIF+GRT construction before 2010",
  "p0_outcome_reconciliation.csv", "body","body","note"),

 ("1.9", "The puzzle", "Breadth of relative disadvantage: worst-quintile share, descriptive only",
  "21% pre-crisis to 58% from 2012, 68% in 2024, 1st of 27", "27 EU, 25 indicators", "descriptive",
  "tested as a predictor and NULL (FDR 0.287); excluded from every model; outcome and all covariates removed",
  "persistence_share_battery.csv", "body","body","body"),

 ("7.1", "What it looked like", "Greece has the EU's deepest and longest unresolved pre-crisis GDP shortfall", "-11.2%, 16 yrs; EU median recovery 3 yrs", "27 EU, 2008-2024", "core", "Finland remains 2.3% below 2008; Luxembourg is below a recent 2021 peak", "recovery_trajectory.csv", "body","body","body"),
 ("7.2", "What it looked like", "Real wages remain furthest below 2008 of any EU country", "-31.8%", "27 EU, 2024", "descriptive", "level-only; no independent model power", "real_wage_idx2008.csv", "body","body","body"),
 ("7.3", "What it looked like", "Highest wage-adjusted price pressure in the EU, every category", "1st or 2nd of 27", "27 EU, 2024", "descriptive", "3 yrs coverage; no model test possible", "price_pressure.csv", "body","note","body"),
 ("7.4", "What it looked like", "Mortgage-free owners are overburdened at the EU's highest rate", "25.7% vs next 14.0%", "27 EU, 2024", "descriptive", "subcomponent of a variable already in the model", "housing_tenure.csv", "body","note","body"),
 ("7.5", "What it looked like", "Net emigration of 290,281 Greek nationals, now reversing", "2.6% of 2008 pop; 5th of 25", "2008-2024", "descriptive", "not uniquely severe in the EU", "migration_nationals_panel.csv", "body","note","body"),
 ("7.6", "What it looked like", "A generational reversal: 65+ worsened while all working-age improved", "65+ +10.2pt; others -7 to -10pt", "Greece, 2015-2025", "descriptive", "distributional, enters no model; small subgroup variance", "age_breakdown_arope.csv", "body","note","body"),
 ("7.7", "What it looked like", "The paradox persists among salaried workers", "AROP 17th of 27; subjective 1st at 59.5%", "27 EU, 2025", "core", "", "work_effort_status_latest.csv", "body","body","body"),
 ("7.8", "What it looked like", "Longest hours, lowest hourly pay", "39.8h (1st) / 14.2 PPS (lowest); salaried hours 7th", "27 EU, 2024", "descriptive", "cross-sectional only: fails country-FE and first-diff", "work_effort_cross_country_latest.csv", "body","body","body"),

 ("8.1", "Alternatives", "Income inequality does not explain the gap", "6th of 27; adds nothing", "27 EU", "core (null)", "", "income_inequality.csv", "body","body","body"),
 ("8.2", "Alternatives", "Greece was already highest pre-crisis (conceded)", "1st of the 6-country 2003 panel", "2003-2008", "core", "coverage-audited across 3 balanced panels", "reporting_style_v2_balanced_rankings.csv", "body","body","body"),
 ("8.3", "Alternatives", "The crisis-era widening is the largest of any EU country", "+19.8pt vs median -8.8pt", "27 EU", "core", "", "reporting_style_gap_widening.csv", "body","body","body"),
 ("8.4", "Alternatives", "DiD survives placebo/randomization inference", "1st of 27, empirical p=0.037", "27 EU", "core", "single treated unit; RI is the honest p", "reporting_style_v2_country_placebo.csv", "body","body","note"),
 ("8.5", "Alternatives", "Only one pre-treatment year is testable", "2007 coef -0.96, p=0.17", "2007-2025", "limitation", "not an exhaustive pre-trend history", "reporting_style_v2_event_study.csv", "note","body","--"),
 ("8.6", "Alternatives", "Extremity is financial-specific, not generic pessimism", "z 3.76/3.20 vs 1.17 life satisfaction", "27 EU", "core", "", "reporting_style_v3_standardized_deviations.csv", "body","body","body"),
 ("8.7", "Alternatives", "Institutional trust is context, never modeled", "7% in 2012", "Greece", "descriptive", "Eurostat holds one year (2013) only", "OECD 2026 / Eurobarometer", "body","note","body"),

 ("9.1", "Meaning", "AROP should not be read alone during a national collapse", "recommendation", "n/a", "core", "generalizes better than any Greek finding", "n/a", "body","body","body"),
 ("9.2", "Meaning", "All results are associational, from country-level aggregates", "limitation", "n/a", "limitation", "", "n/a", "body","body","body"),
 ("9.3", "Meaning", "Results reproduce from the archive and through an isolated end-to-end re-acquisition", "13 of 15 byte-identical", "n/a", "limitation", "live Eurostat revisions mean a fresh pull is not byte-identical to the archived vintage", "Makefile reproduce / 00_fetch_missing_raw.py", "note","note","note"),
 ("9.4", "Meaning", "FDR does not make sequential specifications pre-specified", "four-tier evidence taxonomy", "n/a", "limitation", "", "n/a", "body","body","note"),
]

cols = ["id","element","claim","number","population_window","status","caveat","source",
        "report","paper","narrative"]
df = pd.DataFrame(C, columns=cols)
importance_by_element = {
    "The puzzle": "spine", "Shrinking ruler": "spine", "AROPE bridge": "spine",
    "Current hardship": "spine", "Duration": "spine", "Accumulation": "spine",
    "What it looked like": "supporting", "Alternatives": "supporting",
    "Meaning": "spine",
}
df.insert(3, "canonical_wording", df["claim"])
df.insert(4, "importance", df["element"].map(importance_by_element))

# ---------------------------------------------------------------- supersession ----
# V1's evidence carries forward; V1's framing does not. These columns force that
# distinction to be made claim by claim rather than left implicit, and the parity
# auditor refuses to pass while any claim's disposition is undecided.
#
#   introduced_in       release the claim first appeared in
#   v2_disposition      what V2 does with it (see DISPOSITIONS)
#   superseded_by       release that supersedes it, if any
#   decision_reason     why -- required for anything other than "undecided"
#   replacement_claim_id  the V2 claim that takes its place, for superseded/retracted
#
# Every claim starts "undecided". Filling these in is a V2 task, done once P0
# and P3 have settled what survives; the auditor's job is to make sure it is not
# skipped.
DISPOSITIONS = ["retained", "reworded", "superseded", "rejected",
                "descriptive_only", "future_research", "retested",
                "v1_only", "undecided"]

# V2 disposition for every V1 claim. Assigned once, here, so the decision is in
# version control rather than in prose. The three residuals that competed as
# headline estimates -- 2.70 (nested), 3.81/3.9 (C-LTU), -0.8 (Model G) -- are
# superseded by the objective-only result and survive only as legacy,
# proximity-sensitive specifications.
DISPOSITION = {
 "1.1":("retained",""), "1.2":("retained",""), "1.3":("retained",""),
 "1.4":("retained",""), "1.9":("descriptive_only",
   "tested as a predictor and null (FDR 0.287); descriptive corroboration only"),
 "2.1":("retained",""), "2.2":("retained",""), "2.3":("retained",""),
 "2.4":("retained",""), "2.5":("retained",""),
 "3.1":("retained",""), "3.2":("retained",""), "3.3":("retained",""),
 "4.1":("retained",""),
 "4.2":("superseded",
   "the 25.6->35.5->11.6 ladder depends on Tier 0 predictors; legacy only"),
 "4.3":("retained","strengthened by P3: the objective-only model excludes these by construction"),
 "4.4":("retained",""),
 "5.1":("retained",""),
 "5.2":("superseded",
   "11.6->3.9 is proximity-sensitive; the objective-only ladder replaces it"),
 "5.3":("reworded",
   "LTU is stable across LOO refits but imprecise under wild-cluster inference (p=0.073)"),
 "6.1":("superseded",
   "3.9->-0.8 replaced by the objective-only 27.05->6.93; -0.8 required Tier 0 predictors"),
 "6.2":("retained",""), "6.3":("retained",""),
 "6.4":("superseded",
   "the +2.70 nested figure no longer competes as a headline; legacy specification"),
 "6.5":("retained",""), "6.6":("retained",""), "6.7":("retained",""),
 "6.8":("retained",""),
 "7.1":("retained",""), "7.2":("retained",""), "7.3":("retained",""),
 "7.4":("retained",""), "7.5":("retained",""), "7.6":("retained",""),
 "7.7":("retained",""), "7.8":("retained",""),
 "8.1":("retained",""), "8.2":("retained",""), "8.3":("retained",""),
 "8.4":("reworded",
   "a country-placebo/permutation reference distribution under exchangeability, "
   "not randomization inference"),
 "8.5":("retained",""),
 "8.6":("reworded",
   "rules out a GENERIC response-style account; does not exclude a fiscally "
   "specific one -- see the competing account in v3 12a"),
 "8.7":("future_research",
   "institutional trust remains context; the fiscal-experience account needs a "
   "separate sourced descriptive checkpoint before entering the discussion"),
 "9.1":("retained",""), "9.2":("retained",""), "9.3":("retained",""),
 "9.4":("retained",""),
}
REPLACEMENT = {"4.2":"10.2","5.2":"10.2","6.1":"10.2","6.4":"10.2"}
df.insert(5, "introduced_in", "v1-final")
df.insert(6, "v2_disposition", df["id"].map(lambda i: DISPOSITION.get(i, ("retained", ""))[0]))
df.insert(7, "superseded_by", df["id"].map(
    lambda i: "v2" if DISPOSITION.get(i, ("", ""))[0] == "superseded" else ""))
df.insert(8, "decision_reason", df["id"].map(lambda i: DISPOSITION.get(i, ("", ""))[1]))
df.insert(9, "replacement_claim_id", df["id"].map(lambda i: REPLACEMENT.get(i, "")))
df.loc[df["id"].str.startswith("10."), ["introduced_in", "v2_disposition"]] = ["v2", "retained"]
df.to_csv("../docs/claim_matrix.csv", index=False)

print(f"{len(df)} canonical claims across {df.element.nunique()} backbone elements\n")
print(df.groupby("element", sort=False).size().to_string())
print("\nBy evidentiary status:")
print(df.status.value_counts().to_string())
print("\nRequired treatment by document:")
print(pd.DataFrame({d: df[d].value_counts() for d in ["report","paper","narrative"]}).fillna(0).astype(int).to_string())
print("\nWritten: docs/claim_matrix.csv")
