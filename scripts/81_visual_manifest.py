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
      question="How far apart are the three poverty measures for Greece, and "
               "does the distance close over time?",
      artifact="e0_extended_panel.csv",
      series="subjective_poverty, arop, arope for Greece and the EU median",
      interaction="hover reads all three values for the year; EU median shown "
                  "as a reference band",
      fallback="year x measure, Greece and EU median",
      caveat="", status_label="descriptive"),
 dict(id="F2", stage=1, chart_type="ladder",
      question="Is Greece unusual, or at one end of a continuum?",
      artifact="e_descriptive_ranks.csv",
      series="all 27 countries on subjective hardship, latest year",
      interaction="hover names the country and value; Greece highlighted",
      fallback="rank, country, value for all 27",
      caveat="", status_label="descriptive"),
 dict(id="F3", stage=2, chart_type="panel",
      question="What happened to the line Greek poverty is measured against?",
      artifact="e0_extended_panel.csv",
      series="arop_threshold_real for Greece and the EU median, own 2008 = 100",
      interaction="hover reads the index; 100 marked as the pre-crisis level",
      fallback="year x Greece, EU median",
      caveat="", status_label="descriptive"),
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
               "age_breakdown_shiftshare_decomposition.csv",
      series="the three AROPE components, switchable to the age breakdown and "
             "the shift-share decomposition",
      interaction="switch component/age/household; hover reads the rate for the "
                  "group and year; the elderly series is labelled where it "
                  "diverges from the rest",
      fallback="component x year for Greece, and age group x year with the "
               "shift-share split",
      caveat="The components are a UNION and may not be summed. The age result "
             "is a composition finding, not a claim that any group's "
             "experience improved.",
      status_label="descriptive"),
 dict(id="F5", stage=3, chart_type="heatmap",
      question="Do relationships between the candidate variables hold across "
               "countries and within them, or do they change?",
      artifact="e0_corr_pooled.csv, e0_corr_between.csv, e0_corr_within.csv",
      series="the three correlation views, switchable",
      interaction="switch between pooled, between and within; hover reads the "
                  "pair and coefficient; sign reversals marked",
      fallback="the flagged pairs only, with all three views",
      caveat="Correlations identify duplication and sign reversals. They do "
             "NOT select variables, and correlations with the gap outcomes are "
             "partly arithmetic.",
      status_label="descriptive"),
 dict(id="F6", stage=3, chart_type="dumbbell",
      question="Which measures converged toward the EU and which diverged?",
      artifact="e_descriptive_recovery.csv",
      series="gap in 2015 against gap in 2024, per variable",
      interaction="hover reads both endpoints and the shift; converging, flat "
                  "and diverging coloured separately",
      fallback="variable, gap 2015, gap 2024, shift, trend",
      caveat="", status_label="descriptive"),
 dict(id="F7", stage=3, chart_type="ladder",
      question="Does reported difficulty move with concrete affordability "
               "failure, or float free of it?",
      artifact="e3_results.csv",
      series="within-country correlation per proximate item, Greece overlaid",
      interaction="hover reads the within-country and Greece-only correlation",
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
      status_label="pre-planned confirmatory"),
 dict(id="F14", stage=6, chart_type="ladder",
      question="Does the answer depend on which model is chosen?",
      artifact="p3_residuals.csv, ea_companion_residuals.csv",
      series="country residual ladders for both specifications, side by side",
      interaction="hover reads the country's residual in both; Greece "
                  "highlighted in both",
      fallback="Greece's residual and rank in each specification",
      caveat="NEITHER specification is definitive. They may not be merged or "
             "averaged, and selection may not be made on residual size.",
      status_label="post-selection robustness"),
 dict(id="F15", stage=7, chart_type="scatter",
      question="Are Greeks simply gloomier about everything?",
      artifact="reporting_style_cross_indicator.csv",
      series="hardship rank against life-satisfaction rank, by year",
      interaction="hover reads all three indicator ranks for the year",
      fallback="year, hardship rank, financial expectations rank, life "
               "satisfaction rank",
      caveat="Generic pessimism is INSUFFICIENT, not disproved. A "
             "financial-domain-specific reporting difference cannot be excluded.",
      status_label="descriptive corroboration"),
]

for i, e in enumerate(M, start=1):
    e["id"] = f"F{i}"
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
print("  every figure: hover values, Greece and EU reference, evidence-status")
print("  badge, table fallback, and a link to the appendix evidence")

df.to_csv(PROC / "report_visual_manifest.csv", index=False)
print(f"\nWritten to {PROC}/report_visual_manifest.csv")
