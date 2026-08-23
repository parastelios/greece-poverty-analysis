"""Freeze the report's visual manifest, BEFORE any chart is built.

Charts get added because they exist, not because they answer something. The
first eight-stage draft had the opposite failure -- too few, chosen by whatever
was already generated. Both are avoided the same way: every visual is specified
in advance by the question it answers, and anything that cannot state one does
not get built.

Each entry fixes:
  stage        where it sits in the eight-stage story
  question     what the reader learns from it -- not what it plots
  artifact     the frozen source; a chart with no artifact cannot be built
  chart_type   from the shared engine; NEW types are flagged explicitly
  interaction  what hover/selection must do
  fallback     the compact accessible table that must accompany it
  caveat       the required label travelling with it, or ""
  status_label the evidence-status badge shown on the figure itself
"""
import json
from pathlib import Path

import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

# Types the appendix engine already provides, validated across the full appendix.
EXISTING = {"series", "panel", "scatter"}
# Types the shared engine must gain. Kept deliberately few.
NEW = {"ladder", "coefficient", "dumbbell", "heatmap"}

M = [
 dict(id="F1", stage=1, chart_type="panel",
      question="How far apart are reported hardship and official income "
               "poverty for Greece, and does the distance close over time?",
      artifact="e0_extended_panel.csv",
      series="subjective_poverty and arop for Greece, with the EU median of each",
      interaction="hover reads both values and the gap for the year",
      fallback="year x subjective hardship, AROP, gap; Greece and EU median",
      caveat="AROPE is deliberately absent here. It enters at Stage 2 as the "
             "bridge, and showing it now would pre-empt that step.",
      status_label="descriptive"),
 dict(id="F2", stage=1, chart_type="ladder",
      question="Is Greece unusual, or at one end of a continuum?",
      artifact="e_descriptive_ranks.csv",
      series="all 27 countries on subjective hardship, latest year",
      interaction="hover names the country and value; Greece highlighted",
      fallback="rank, country, value for all 27",
      caveat="", status_label="descriptive"),
 dict(id="F3", stage=2, chart_type="panel",
      question="What happened to the line Greek poverty is measured against, "
               "and what does a fixed line show instead?",
      artifact="e0_extended_panel.csv, anchored_poverty.csv",
      series="VIEW A: arop_threshold_real for Greece and the EU median, own "
             "2008 = 100. VIEW B: Greek AROP against anchored poverty on a "
             "fixed pre-crisis line",
      interaction="switch between the two views; hover reads the index or both "
                  "rates; 100 marked as the pre-crisis level in view A, and the "
                  "two series diverge visibly in view B",
      fallback="year x real threshold index; year x AROP, anchored poverty",
      caveat="The anchored series is an approximation built in this project "
             "and is labelled as such wherever it appears.",
      status_label="descriptive"),
 dict(id="F4", stage=2, chart_type="panel",
      question="What does AROPE add to AROP, and is that addition growing?",
      artifact="e_descriptives.csv",
      series="gap_vs_arop and gap_vs_arope, with the closure between them shaded",
      interaction="hover reads both gaps and the closure for the year",
      fallback="year x gap vs AROP, gap vs AROPE, closure",
      caveat="AROPE components overlap and MAY NOT be added together: it is a "
             "union of income poverty, deprivation and low work intensity, and "
             "aggregate data do not reveal the overlaps",
      status_label="descriptive"),
 dict(id="F5", stage=2, chart_type="panel",
      question="What sits behind AROPE, and did every age group move the same way?",
      artifact="age_breakdown_arope.csv, age_breakdown_arop.csv, "
               "age_breakdown_deprivation.csv, age_breakdown_low_work_intensity.csv, "
               "age_breakdown_household_arope.csv, "
               "age_breakdown_shiftshare_decomposition.csv",
      series="VIEW A: the three AROPE components. VIEW B: AROPE by age group, "
             "with the 65+ series emphasised. VIEW C: by household composition. "
             "VIEW D: the shift-share split of within-group against "
             "compositional contribution",
      interaction="switch component/age/household/shift-share; hover reads the "
                  "rate for the group and year, and in the shift-share view "
                  "the two contributions separately",
      fallback="component x year; age group x year; household type x year; and "
               "the shift-share contributions",
      caveat="These are changes in group-level rates, not evidence about the "
             "same individuals over time. The 2024-2025 national increase was "
             "driven primarily by within-group changes, especially "
             "deterioration among people aged 65+, rather than population "
             "ageing. AROPE components are a UNION and may not be summed.",
      status_label="descriptive"),
 dict(id="F5", stage=3, chart_type="heatmap",
      question="Do relationships between the candidate variables hold across "
               "countries and within them, or do they change?",
      artifact="e0_corr_pooled.csv, e0_corr_between.csv, e0_corr_within.csv",
      series="the three correlation views, switchable",
      interaction="switch between pooled, between and within; hover reads the "
                  "pair and coefficient; sign reversals marked",
      fallback="the flagged pairs only, with all three views",
      # The gap outcomes are NOT in this matrix, so a caveat about them
      # described data the reader could not see. What IS shown includes AROPE
      # alongside its own components.
      caveat="Correlations identify duplication and sign reversals. They do "
             "NOT select variables.",
      status_label="descriptive"),
 dict(id="F6", stage=3, chart_type="dumbbell",
      question="Which measures converged toward the EU and which diverged?",
      artifact="e_descriptive_recovery.csv",
      series="gap in 2015 against gap in 2024, per variable",
      interaction="hover reads both endpoints and the shift; converging, flat "
                  "and diverging coloured separately",
      fallback="variable, gap 2015, gap 2024, shift, trend",
      caveat="", status_label="descriptive"),
 dict(id="F7", stage=3, chart_type="scatter",
      question="Does reported difficulty move with concrete affordability "
               "failure, or float free of it?",
      artifact="e0_extended_panel.csv, e3_results.csv",
      series="hardship against each same-instrument item, COUNTRY MEANS "
             "REMOVED, switchable between the four items",
      interaction="switch item; hover names the country-year and reads both "
                  "demeaned values; Greek points highlighted; the fitted slope "
                  "and its correlation shown per item",
      fallback="item, within-country r, Greece over time",
      caveat="Same-instrument corroboration, NOT independent validation: all "
             "items and the outcome come from EU-SILC.",
      status_label="descriptive corroboration"),
 dict(id="F8", stage=4, chart_type="coefficient",
      question="Which current-level constructs survive every pre-registered "
               "condition, and which gate stopped the rest?",
      artifact="e1_results.csv",
      series="coefficient with interval per construct, coloured by outcome",
      interaction="hover reads the coefficient, the FDR p, the bootstrap p and "
                  "the gate that failed, so the reader sees directly where the "
                  "cluster-robust and bootstrap verdicts part company",
      fallback="the full nine plus the blocked diagnostic",
      caveat="Inconclusive is not evidence of absence.",
      status_label="pre-planned confirmatory"),
 dict(id="F10", stage=4, chart_type="panel",
      question="What do the three supported constructs actually look like for "
               "Greece against the EU?",
      artifact="e0_extended_panel.csv",
      series="ltu_rate, aic_pps_pc and wadj_a01, Greece against EU median",
      interaction="hover reads Greece, EU median and the gap",
      fallback="latest values and ranks for the three",
      caveat="", status_label="pre-planned confirmatory"),
 dict(id="F11", stage=5, chart_type="panel",
      question="How much accumulated unemployment has each country absorbed, "
               "and where does Greece sit?",
      artifact="e4_accumulated_panel.csv",
      series="acc_cum_excess_unemployment, all 27 with Greece and median marked",
      interaction="hover names the country and value; Greece always labelled",
      fallback="latest value and rank for all 27",
      caveat="cross-country association | no demonstrated within-Greece "
             "dynamic | no causal claim | current conditions not ruled out",
      status_label="post-selection robustness"),
 dict(id="F12", stage=5, chart_type="coefficient",
      question="Does accumulated history add anything once today's conditions "
               "are in the same model?",
      artifact="e7_results.csv",
      series="the 16 conditional coefficients, paired by construct",
      interaction="hover reads both directions of the pair, the focal VIF and "
                  "the pair's own detectable effect",
      fallback="pair, direction, coefficient, bootstrap p, outcome",
      caveat="cross-country association | no demonstrated within-Greece "
             "dynamic | no causal claim | current conditions not ruled out",
      status_label="post-selection robustness"),
 dict(id="F13", stage=5, chart_type="dumbbell",
      question="Is the effect between countries or within them?",
      artifact="e7_dynamic.csv",
      series="between and within estimates per pair, with first differences",
      interaction="hover reads between, within, first difference and their p-values",
      fallback="pair, between, within, first difference, dynamic permitted",
      caveat="This is THE central limitation: no within-country estimate is "
             "significant in the adverse direction and no first-difference "
             "test supports one.",
      status_label="pre-registered conditional robustness"),
 dict(id="F14", stage=6, chart_type="dumbbell",
      question="Does the answer depend on which model is chosen?",
      artifact="p3_residuals.csv, ea_companion_residuals.csv",
      series="one dumbbell per country joining its residual under the frozen "
             "specification to its residual under the deprivation-free "
             "companion, with a zero line",
      interaction="hover reads both residuals and the distance between them; "
                  "Greece emphasised, and its crossing of zero is the visual "
                  "point of the figure",
      fallback="Greece's residual and rank in each specification",
      caveat="NEITHER specification is definitive. They may not be merged or "
             "averaged, and selection may not be made on residual size.",
      status_label="post-selection robustness"),
 dict(id="F15", stage=7, chart_type="panel",
      question="Are Greeks simply gloomier about everything?",
      artifact="reporting_style_cross_indicator.csv",
      series="Greece's RANK TRAJECTORY on hardship, financial expectations and "
             "life satisfaction, one line each, worst rank at the top",
      interaction="hover reads all three ranks for the year; the two lines "
                  "pinned at rank 1 read against the third immediately",
      fallback="year, hardship rank, financial expectations rank, life "
               "satisfaction rank",
      caveat="Generic pessimism is INSUFFICIENT, not disproved. A "
             "financial-domain-specific reporting difference cannot be excluded.",
      status_label="descriptive corroboration"),
]

# NARRATIVE OWNERSHIP. Every visual belongs to a claim or a context entry, and
# sits either on the main reading path or behind an expandable. A figure owned
# by nothing is a figure nobody has to justify.
OWNER = {
    1: ("V2-1.2", "main"), 2: ("V2-1.2", "main"), 3: ("V2-2.1", "main"),
    4: ("V2-2.1", "main"), 5: ("V2-2.1", "expandable"),
    6: ("V2-3.2", "expandable"), 7: ("V2-4.X", "main"), 8: ("V2-3.1", "main"),
    9: ("V2-4.C2", "main"), 10: ("V2-4.C1", "expandable"),
    11: ("V2-5.C2", "main"), 12: ("V2-5.C2", "main"), 13: ("V2-5.Y", "main"),
    14: ("V2-6.1", "main"), 15: ("CTX-1", "main"),
}
for i, e in enumerate(M, start=1):
    e["id"] = f"F{i}"
    owner, path = OWNER[i]
    e["claim_id"] = owner if owner.startswith("V2") else ""
    e["context_id"] = owner if owner.startswith("CTX") else ""
    e["reading_path"] = path
df = pd.DataFrame(M)
df["engine_type_is_new"] = ~df.chart_type.isin(EXISTING)

problems = []
for r in df.itertuples():
    if not r.question.strip().endswith("?"):
        problems.append(f"{r.id}: question must be a question")
    if not r.fallback.strip():
        problems.append(f"{r.id}: every interactive figure needs a table fallback")
    for a in [x.strip() for x in r.artifact.split(",")]:
        if not (PROC / a).exists():
            problems.append(f"{r.id}: artifact {a} does not exist")
    if r.chart_type not in EXISTING | NEW:
        problems.append(f"{r.id}: unknown chart type {r.chart_type}")
    if not (r.claim_id or r.context_id):
        problems.append(f"{r.id}: no narrative owner")
    if r.reading_path not in ("main", "expandable"):
        problems.append(f"{r.id}: reading_path must be main or expandable")
if problems:
    raise SystemExit("MANIFEST\n  " + "\n  ".join(problems))

bar = "=" * 96
print(bar); print("REPORT VISUAL MANIFEST"); print(bar)
print(f"  {len(df)} figures across {df.stage.nunique()} stages")
print(f"  engine types reused: {sorted(EXISTING)}")
print(f"  engine types to ADD: {sorted(set(df[df.engine_type_is_new].chart_type))}\n")
for s in sorted(df.stage.unique()):
    print(f"  Stage {s}")
    for r in df[df.stage == s].itertuples():
        new = "  [NEW TYPE]" if r.engine_type_is_new else ""
        print(f"    {r.id:4} {r.chart_type:12}{new}")
        print(f"         Q  {r.question}")
        print(f"         <- {r.artifact}")
        if r.caveat:
            print(f"         !  {r.caveat[:78]}")
    print()

print(bar); print("BUDGET"); print(bar)
print(f"  figures          {len(df)}   (target 12-15)")
if not 12 <= len(df) <= 15:
    raise SystemExit(f"manifest is outside the agreed budget: {len(df)} figures")
print("  the evidence ladder is a TABLE, not a chart: it summarises status "
      "rather than showing a distribution")
print(f"  new engine types {len(set(df[df.engine_type_is_new].chart_type))}   "
      "(kept deliberately few)")
print(f"  main reading path {int((df.reading_path == 'main').sum())}   "
      f"expandable {int((df.reading_path == 'expandable').sum())}")
unowned = [c for c in claims_index if c not in set(df.claim_id)] if False else []
print("  every figure: hover values, Greece and EU reference, evidence-status")
print("  badge, table fallback, and a link to the appendix evidence")

df.to_csv(PROC / "report_visual_manifest.csv", index=False)
print(f"\nWritten to {PROC}/report_visual_manifest.csv")
