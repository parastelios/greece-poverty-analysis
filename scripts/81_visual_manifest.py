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
      artifact="e0_extended_panel.csv, anchored_poverty.csv, "
               "analysis_dataset.csv",
      series="VIEW A: anchored against current-year poverty rates. "
             "VIEW B: Greek income poverty against every other country. "
             "VIEW C: the threshold itself, cash against 2008 purchasing power",
      interaction="switch between the three views; hover reads the rates or "
                  "the two threshold values, and names any faint country line",
      fallback="year x anchored and current-year rates; year x Greek and EU "
               "median income poverty; year x threshold in cash and in 2008 "
               "purchasing power",
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
               "arope_by_sex.csv, e0_extended_panel.csv",
      series="VIEW A: income poverty, Greece against every other country. "
             "VIEW B: severe material deprivation, likewise. "
             "VIEW C: AROPE, likewise. "
             "VIEW D: AROPE by age group with the 65+ series emphasised. "
             "VIEW E: AROPE by sex, whole population",
      interaction="switch measure/age/sex; hover reads the rate for the group "
                  "and year, and names any faint country line",
      fallback="component x year; age group x year; sex x year; and "
               "the shift-share contributions",
      caveat="These are changes in group-level rates, not evidence about the "
             "same individuals over time. The 2024-2025 national increase was "
             "driven primarily by within-group changes, especially "
             "deterioration among people aged 65+, rather than population "
             "ageing. AROPE components are a UNION and may not be summed.",
      status_label="descriptive"),
 dict(id="F6", stage=3, chart_type="heatmap",
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
 dict(id="F7", stage=3, chart_type="ladder",
      question="Which measures converged toward the EU and which diverged?",
      artifact="e_descriptive_recovery.csv",
      # CHANGED from dumbbell to a diverging ladder: the 2015 gaps run from
      # -2,819 PPS to +48.8 percentage points, and percentage points, index
      # points and PPS currency cannot share one axis. The plotted quantity is
      # the dimensionless share of each gap closed; the original values and
      # units live in the tooltip and the table.
      series="share of each 2015 Greece-EU gap closed by 2024, as diverging "
             "bars from a no-change line",
      interaction="hover reads both endpoints and the shift; converging, flat "
                  "and diverging coloured separately",
      fallback="variable, gap 2015, gap 2024, shift, trend",
      caveat="", status_label="descriptive"),
 dict(id="F8", stage=3, chart_type="scatter",
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
 dict(id="F9", stage=4, chart_type="coefficient",
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
 dict(id="F11", stage=5, chart_type="ladder",
      question="How much accumulated unemployment has each country absorbed, "
               "and where does Greece sit?",
      artifact="e4_accumulated_panel.csv",
      # CHANGED from panel to ladder: the question is where Greece sits among
      # 27 countries, which a ranked comparison answers and a time series does
      # not. Three views, one per supported accumulated measure.
      series="each supported accumulated measure, all 27 countries ranked, "
             "with Greece and the EU median marked",
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
      # Kept short: the figure's own caveat carries the rank convention, the
      # axis zoom and the missing years.
      caveat="",
      status_label="descriptive corroboration"),
 dict(id="F16", stage=7, chart_type="panel",
      question="Did the crisis also become an exit route, and has that reversed?",
      artifact="migration_nationals_panel.csv",
      series="departures and returns of Greek nationals 2008-2024, switchable "
             "to the net flow around a zero line and to an EU comparison",
      interaction="hover reads departures, returns and the net flow for the "
                  "year; the zero line marks the turn from net exit to net return",
      fallback="year x departures, returns, net flow, rate per 1,000",
      caveat="CONTEXTUAL CONSEQUENCE AND POSSIBLE CONTRIBUTOR, not an "
             "independently supported predictor. Net migration was tested "
             "directly at the diagnostic stage and returned nothing "
             "(p = 0.4006), which speaks to aggregate prediction and to "
             "neither causal direction.",
      status_label="contextual consequence"),
 dict(id="F17", stage=7, chart_type="ladder",
      question="How does Greek institutional trust compare with the OECD?",
      artifact="oecd_trust_2023.csv",
      series="Greek trust across nine institutions in 2023, with the OECD "
             "average for central government marked",
      interaction="hover reads the share and the survey window",
      fallback="entity, share reporting high or moderately high trust",
      # Kept short on the face of the figure. The provenance detail -- which
      # summary figures were never verified, and what obtaining the OECD
      # country table would allow -- is in the research record.
      caveat="A 2023 snapshot, not a trend. The OECD Trust Survey has run in "
             "2021, 2023 and 2025, so a short series exists, but this project "
             "holds only the 2023 wave. Contextual and not modelled.",
      status_label="contextual evidence"),
 dict(id="F18", stage=2, chart_type="dumbbell",
      question="What drove the most recent rise in AROPE: rates within age "
               "groups, or the changing size of those groups?",
      artifact="age_breakdown_shiftshare_decomposition.csv",
      series="within-group and compositional contribution per age group, "
             "in percentage points",
      interaction="hover reads both contributions and the underlying rates",
      fallback="age group, within-group contribution, composition contribution",
      caveat="These are exact decomposition terms, not estimates: they carry "
             "no uncertainty and no interval is drawn. Within-group means the "
             "rate changed inside an age group; composition means the size of "
             "the group changed.",
      status_label="descriptive"),
 dict(id="F19", stage=3, chart_type="dumbbell",
      question="Which relationships with reported hardship change when the "
               "comparison moves from between countries to within them?",
      artifact="e0_corr_between.csv, e0_corr_within.csv",
      series="each measure's correlation with reported hardship, between "
             "against within, ordered by how much the two differ",
      interaction="hover reads both correlations and the change",
      fallback="measure, between-country correlation, within-country "
               "correlation, change",
      caveat="Correlations identify duplication and sign reversals. They do "
             "NOT select variables, and a reversal is a fact about the two "
             "scopes rather than evidence about mechanism.",
      status_label="descriptive"),
]

# NARRATIVE OWNERSHIP. Every visual belongs to a claim or a context entry, and
# sits either on the main reading path or behind an expandable. A figure owned
# by nothing is a figure nobody has to justify.
OWNER = {
    "F1": ("V2-1.2", "main"),
    "F2": ("V2-1.2", "main"),
    "F3": ("V2-2.1", "main"),
    "F4": ("V2-2.1", "main"),
    "F5": ("V2-2.1", "expandable"),
    "F6": ("V2-3.2", "expandable"),
    "F7": ("V2-4.X", "main"),
    "F8": ("V2-3.1", "main"),
    "F9": ("V2-4.C2", "main"),
    "F10": ("V2-4.C1", "expandable"),
    "F11": ("V2-5.C2", "main"),
    "F12": ("V2-5.C2", "main"),
    "F13": ("V2-5.Y", "main"),
    "F14": ("V2-6.1", "main"),
    "F15": ("CTX-1", "main"),
    "F16": ("CTX-4", "expandable"),
    "F17": ("CTX-2", "main"),
    "F18": ("V2-2.1", "expandable"),
    "F19": ("V2-3.1", "expandable"),
}
seen_ids = [e["id"] for e in M]
if len(set(seen_ids)) != len(seen_ids):
    dupes = sorted({i for i in seen_ids if seen_ids.count(i) > 1})
    raise SystemExit(f"duplicate figure ids: {dupes}")
for i, e in enumerate(M, start=1):
    owner, path = OWNER[e["id"]]
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
# Raised from 15 to 17 for the two contextual figures. Contextual status should
# restrict INTERPRETATION, not prevent visualisation, and forcing migration and
# trust into an existing chart would have made one figure carry two unrelated
# topics.
# Raised again from 17 to 18 for the ESS pre-crisis extension, which answers a
# question no existing figure can: the Eurostat series starts in 2013 and has no
# pre-crisis baseline. It is a separate instrument and cannot share an axis with
# anything already here.
# Raised to 20: the shift-share decomposition and the hardship-correlation
# comparison were tabs inside figures that answered a different question.
# A tab implies an alternative view of one question; these are second
# questions and are now their own figures.
print(f"  figures          {len(df)}   (target 12-20)")
if not 12 <= len(df) <= 20:
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
