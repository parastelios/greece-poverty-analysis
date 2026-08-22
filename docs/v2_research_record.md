# V2 Research Record

## How to read this

This is the living record of the V2 analysis. It documents what was planned,
what was run, what was found, and what decision followed at each stage.

Every stage below opens with **In plain words** — a short, non-technical
account of what the step was for and what came out of it. If you read nothing
else, read those. Everything after that heading is the formal record.

Every stage ends with **Where the detail lives** — the script that produced it,
the files it wrote, and the commit that froze it.

The technical report, academic paper, and narrative companion are not updated
stage by stage. They are revised only after the analytical sequence is complete
and the claims have been frozen.

**Sources of truth.** This document does not restate them, it points at them:

| Thing | Lives in | Maintained by |
|---|---|---|
| The 53 published claims and their disposition | `docs/claim_matrix.csv` | `scripts/build_claim_matrix.py`, audited by `audit_parity.py` |
| Full dated decision log with reasoning | `docs/publication_strategy.md` | hand-written, append-only |
| The protocol V2 follows | `docs/project_description_v3.md` | hand-written |
| Frozen P3/P5/P3a values and wording rules | `data/processed/p5f_frozen_result.json` | frozen, never edited |
| Frozen construct map | `data/processed/construct_map_frozen.json` | frozen, never edited |
| Frozen E pre-registration | `data/processed/e_preregistration.json` | frozen, never edited |

## Document Control

<!-- AUTO:BEGIN document-control -->
| Field | Value |
|---|---|
| Current stage | EDA |
| Last completed stage | PRE |
| Branch | `p6-rewrite` |
| HEAD | `476e177` Publish E minimum detectable effects; two simulation bugs found and fixed |
| Uncommitted changes | yes |
| Last refreshed | 2026-08-22 |
| Frozen V1 reference | `v1-final` |
| Frozen V2 analytical reference | `p5f-frozen` |
<!-- AUTO:END document-control -->

## Ground Rules

- Pre-registration is committed before the corresponding test is run.
- Results are committed separately from their pre-registration.
- Exploratory analyses remain exploratory.
- Superseded decisions and claims are retained and linked to replacements.
- Null, inconclusive, infeasible, and unsupported results remain visible.
- Current and accumulated measures are different estimands.
- Raw gaps and regression residuals are not a formal decomposition.
- Proximate hardship indicators cannot become the headline explanation.
- No Family E result may alter P3, P5, or `p5f-frozen`.

## Stage Index

<!-- AUTO:BEGIN stage-index -->
| Stage | Question | Status | Pre-registration | Result | Entry |
|---|---|---|---|---|---|
| P0 | Is our outcome measure the real thing? | complete | — | — | [P0](#p0--is-our-outcome-measure-the-real-thing) |
| P2 | Can we build a synthetic comparison country? | complete | — | — | [P2](#p2--can-we-build-a-synthetic-comparison-country) |
| P3 | How much of Greece's gap do objective conditions explain? | complete | — | — | [P3](#p3--how-much-of-greeces-gap-do-objective-conditions-explain) |
| P5 | Is that a real relationship, or a difference between countries? | complete | — | `p5f-frozen` | [P5](#p5--is-that-a-real-relationship-or-a-difference-between-countries) |
| P3a | Does breadth of disadvantage add anything? | complete | `p3a_frozen_universe.json` | — | [P3a](#p3a--does-breadth-of-disadvantage-add-anything) |
| E0 | What data and constructs are suitable for testing? | complete | — | `2103b3d` | [E0](#e0--data-and-construct-map) |
| PRE | What exact tests and decision rules are fixed before analysis? | complete | `a747e7a` | `476e177` | [PRE](#pre--pre-registration-and-power) |
| EDA | What do the candidate variables actually look like? | **next** | — | — | [EDA](#eda--descriptive-groundwork) |
| E1 | Which current-level constructs are associated with hardship? | pending | `a747e7a` | — | [E1](#e1--current-level-constructs) |
| E2 | Do sensitivity variants change the current-level conclusions? | pending | `a747e7a` | — | [E2](#e2--current-level-sensitivities) |
| E3 | What do the diagnostic and contextual checks show? | pending | `a747e7a` | — | [E3](#e3--diagnostic-and-contextual-checks) |
| E4 | Which accumulated constructs are associated with hardship? | pending | `a747e7a` | — | [E4](#e4--accumulated-exposure) |
| E5 | Do accumulated-measure sensitivities change those conclusions? | pending | `a747e7a` | — | [E5](#e5--accumulation-sensitivities) |
| E6 | Does the frozen combined model remain appropriate? | pending | `a747e7a` | — | [E6](#e6--frozen-combined-model) |
| E7 | Do accumulated measures add information beyond current snapshots? | pending | `a747e7a` | — | [E7](#e7--current-versus-accumulated-comparison) |
| FINAL | What survives into the final reports? | pending | — | — | [FINAL](#final--claim-freeze-and-publication) |
<!-- AUTO:END stage-index -->

## Standard Stage Template

Every analytical stage uses these headings, in this order:

### In plain words
### Question
### Pre-registered specification
### Data and sample
### Minimum detectable effect
### Results
### Robustness and validation
### Interpretation
### What this does not establish
### Decision
### Open issues
### Where the detail lives

---

# Part I — Completed stages

## P0 — Is our outcome measure the real thing?

### In plain words

Before testing anything, we had to know whether the hardship series we built
ourselves was actually the official European statistic, or something we had
invented that merely resembled it. It turned out to be the official one. Where
both exist, they agree almost perfectly — the typical difference is zero, and
no country-year differs by more than a tenth of a percentage point. So the
series was renamed to say what it is: the official indicator, extended
backwards in time before the official version begins.

### Question

Is the constructed `DIF+GRT` series the same quantity as Eurostat `ilc_sbjp01`?

### Results

| Check | Tolerance set before running | Result |
|---|---|---|
| Median absolute difference | ≤ 0.5 pp | **0.0 pp** |
| Share of country-years within 5 pp | ≥ 0.95 | **1.00** |
| Minimum cross-sectional Spearman rank correlation | ≥ 0.90 | **0.999** |
| Greece trend correlation | ≥ 0.90 | **0.99999** |

432 overlapping country-years; 318 exact matches; none differing by more than
0.1 pp.

### Decision

**Passed.** The outcome is renamed the *backward-extended official subjective-
hardship indicator*. Four wording rules were locked: terminology; that the
splice occurs at 2010; that validation covers only the overlap period; and
that pre-2010 provenance is ours, not Eurostat's.

### What this does not establish

Nothing about the pre-2010 segment, which has no official counterpart to be
validated against.

### Where the detail lives

`scripts/51_p0_outcome_reconciliation.py`, `scripts/outcome.py` ·
`data/processed/p0_outcome_reconciliation.csv`, `p0_verdict.csv` ·
`docs/publication_strategy.md` § "P0 complete"

---

## P2 — Can we build a synthetic comparison country?

### In plain words

The idea was to construct an artificial "Greece" out of a weighted blend of
other European countries that matched Greece before the crisis, then see how
far the real Greece diverged from it afterwards. This failed, and we recorded
the failure instead of quietly dropping it. The blend collapsed onto essentially
two countries — Hungary and Bulgaria — which between them have about half
Greece's income and three times its deprivation rate. A comparison built on
that is not a comparison. The large post-crisis divergence the method produced
is therefore **not reportable as a result**, and a rule in the audit script
forbids it appearing in any document.

### Question

Is a synthetic-control comparative design viable on this panel?

### Pre-registered specification

Primary pre-period 2005–2008 (2009 excluded as a transition year), six gates
fixed before running.

### Results

| Specification | Pre-period RMSE | Max donor weight | Effective donors |
|---|---|---|---|
| 2005–2008, unpenalised | 0.91 | 0.55 | 1.98 |
| 2005–2008, regularised (λ=0.5) | 0.91 | 0.55 | 1.98 |
| 2005–2009 | 0.93 | 0.49 | 2.22 |

Donor weights: Hungary 0.552, Bulgaria 0.448, everything else ≈ 0.

**Failed 4 of 6 gates**: donor concentration, covariate imbalance on income,
covariate imbalance on deprivation, and effective donor count.

### Decision

**Rejected as infeasible.** The +27 pp divergence figure is marked
non-reportable via `FORBIDDEN` rules in `audit_parity.py`, which fails the
build if it appears in any output document.

### Where the detail lives

`scripts/52_p2_comparative_design.py` ·
`data/processed/p2_specifications.csv`, `p2_donor_weights.csv`,
`p2_placebo_distribution.csv` ·
`docs/publication_strategy.md` § "P2 FAILS its pre-registered gates"

---

## P3 — How much of Greece's gap do objective conditions explain?

### In plain words

We predicted each country's hardship level from objective conditions only —
deliberately excluding measures that are really just hardship restated (arrears,
being unable to meet an unexpected expense). Greece's actual hardship sits far
above what those conditions predict: **27 points above**, the worst gap in
Europe. Then we added one variable — how much cumulative excess unemployment
the country has absorbed since the crisis — and the gap fell to **7 points**.
So accumulated history explains a large share of the puzzle, but not all of it.
Greece is still an outlier, just no longer an extreme one.

### Question

With proximate hardship indicators excluded, how large is Greece's residual,
and does accumulated exposure narrow it?

### Results

| Specification | Greece residual | Rank |
|---|---|---|
| Objective conditions, no accumulation | **+27.05** | 1 of 27 |
| Plus `cum_excess_unemployment` | **+6.93** | 3 of 27 |
| Plus Tier-0 proximate indicators (diagnostic only) | +3.81 | — |

Model fit R² = 0.907, n = 269.

### Decision

**Branch 2 of 4** — *material history explains a meaningful share, not the full
difference.* Chosen by `scripts/branch_rule.py`, a tested function (17 tests),
not by judgement: the residual clears the ≤10 bar, but the rank stays inside
the extreme-outlier group (≤3), which rules out Branch 1.

> This branch rule exists because an earlier hand-written version defaulted to
> the strongest conclusion and reported "strong objective support" while Greece
> sat at rank 3. Prose pre-registration did not prevent that; a tested function
> does.

### Evidentiary tier

**Post-selection robustness, not independent confirmation.**
`cum_excess_unemployment` was discovered on this same panel during family-A
screening. It has not been validated out of sample.

### Where the detail lives

`scripts/53_p3_objective_only.py`, `scripts/branch_rule.py`,
`scripts/test_branch_rule.py` ·
`data/processed/p3_objective_only.csv`, `p3_residuals.csv` ·
`docs/publication_strategy.md` § "P3 result: BRANCH 2"

---

## P5 — Is that a real relationship, or a difference between countries?

### In plain words

This is the most important limitation in the whole project, so it is worth
stating carefully. The accumulated-unemployment result works by comparing
*countries to each other* — countries that absorbed more accumulated
unemployment have higher hardship. It does **not** work within a country over
time: inside Greece, years with more accumulated exposure are not years with
more hardship. The between-country signal is strong and statistically solid;
the within-country signal is flat and, given how little power we have, simply
inconclusive.

That means we may describe this as a *scarring marker that distinguishes
countries*. We may **never** write "as exposure accumulated, hardship rose."
That sentence is not supported.

### Results

| Component | Estimate | p |
|---|---|---|
| Between-country | **+0.3323** | < 0.0001 |
| Within-country | **−0.0755** | 0.692 |
| Test of within = between | — | 0.058 |
| Country fixed effects | −0.0385 | — |
| First differences | −0.0034 | — |
| Country-specific trends | +0.0490 | — |

Mundlak outcome **B — between-country scarring marker**.

### Robustness and validation

Wild cluster bootstrap, null-imposed: **p = 0.0005** in the primary
specification (the 1/2,000 resolution floor). Worst result across Rademacher,
Webb and Mammen weights × three seeds: **p = 0.0070**.

Leave-one-country-out: max change 12.7%; dropping Greece changes it by −0.8%.
No instability flags.

> The first bootstrap implementation used unrestricted residuals and returned
> p = 0.82 against t = 9.69 — obvious nonsense. Fixed by refitting under the
> null and resampling those residuals.

### What this does not establish

That annual increases in accumulated exposure caused, or even tracked, annual
increases in hardship within Greece. The p = 0.058 equality test **fails to
reject** equality; it is not evidence the two are equal, and the point estimates
remain materially different (−0.076 against +0.332).

### Decision

**Frozen** at tag `p5f-frozen`. Eight wording rules locked in
`p5f_frozen_result.json`. Classification performed by `scripts/mundlak_rule.py`
(23 tests), not by judgement.

### Where the detail lives

`scripts/54_p5_inference_audit.py`, `scripts/mundlak_rule.py`,
`scripts/test_mundlak_rule.py` ·
`data/processed/p5_audit.csv`, `p5_bootstrap.csv`, `p5_influence.csv`,
`p5f_frozen_result.json` ·
`docs/publication_strategy.md` § "P5 result: OUTCOME B"

---

## P3a — Does breadth of disadvantage add anything?

### In plain words

We tested whether counting how many *different kinds* of hardship a country
accumulates adds predictive value beyond what we already had. It does not — it
actively makes things worse. Adding it pushed Greece's gap from 7 points back up
to 10, and Greece from rank 3 back to rank 1. The variable also flipped sign in
a way we could not interpret, so we left it uninterpreted rather than
constructing a story around it. Recorded as a null.

### Results

| Specification | Greece residual | Rank | n |
|---|---|---|---|
| Frozen P3 | 6.93 | 3 of 27 | 269 |
| P3 + accumulated breadth | **10.39** | **1 of 27** | 269 |

Breadth coefficient −2.17, a stable conditional sign reversal, **left
uninterpreted** by decision.

Common-sample verification confirms 269 rows in both specifications, so the
comparison is clean.

### Decision

**Null / rejected** as an incremental predictor. The universe was frozen in
`p3a_frozen_universe.json` before testing.

### Where the detail lives

`scripts/55a_p3a_freeze_universe.py`, `scripts/55b_p3a_family_d.py` ·
`data/processed/p3a_frozen_universe.json`, `p3a_results.csv`,
`p3a_individual_indicators.csv` ·
`docs/publication_strategy.md` § "P3a result"

---

## E0 — Data and construct map

### In plain words

Family E reopens the search for explanatory variables, this time properly. E0
is the groundwork: assemble every candidate variable in one panel, write down
what each one actually measures, check which ones are secretly the same
variable wearing different clothes, and group them into a small number of
*constructs* defined by theory rather than by which grouping happened to fit
best.

Two errors were caught in review and corrected. First, the correlation tables
originally left out the outcome itself, which made the intended exploration
impossible. Second, four variables were wrongly marked as ineligible for
accumulation when the project had already successfully built accumulations from
all four — one of which was a surviving result from an earlier stage.

### Work completed

Extended panel: **27 countries × 2015–2024 = 270 rows, 68 columns**, merging 17
series from the statistical appendix, plus AROPE (`ilc_peps01n`, verified at 27
reporters in every year).

Variable registry: **31 variables**, each carrying label, unit, source, domain,
adverse direction, stock/flow status, construction type, proximity class, role
and construct assignment.

Three correlation views — pooled, between-country, within-country — each
carrying five comparator columns: `subjective_poverty`, `arop`, `arope`,
`gap_subj_arop`, `gap_subj_arope`.

### Roles assigned

| Role | Count |
|---|---|
| Primary representative | 9 |
| Sensitivity variant | 9 |
| Proximate diagnostic | 4 |
| Contextual descriptive | 3 |
| Mechanical comparator | 3 |
| Standalone retest | 2 |
| Standalone retest of known null | 1 |

### Construction and non-independence findings

Six-way accumulation taxonomy replaced the earlier binary eligible/ineligible
field: `direct_excess`, `fixed_base_shortfall`, `duration_below_base`,
`compounded_change`, `ambiguous_direction`, `not_applicable`.

**35 non-independence flags** raised across four types (`arithmetic_coupling`,
`definitional_overlap`, `component_overlap`, `construction_overlap`).

Key redundancy finding: `wadj_a01` and `work_effort_squeeze` correlate at
**r = 0.963 in all three views** — they may never enter a model together.

### Construct-map decisions

Six objective constructs plus one diagnostic:

| ID | Construct | Primary representative |
|---|---|---|
| C1 | Material resources | `aic_pps_pc` |
| C2 | Labour-market exclusion | `ltu_rate` (current) / `cum_excess_unemployment` (accumulated) |
| C3 | Loss against own past | four individual primaries, **no composite** |
| C4 | Wage-adjusted affordability | `wadj_a01` |
| C5 | Inflation exposure | `hicp` |
| C6 | Housing pressure | `housing_cost_overburden`, base year **2010** |
| P1 | Proximate material hardship | `severe_mat_soc_deprivation` — **diagnostic only, never headline** |

C5 was separated from C4 on evidence, not preference: inflation rates correlate
near zero with wage-adjusted affordability and reverse sign between the pooled
and between views.

C6 uses 2010 rather than 2008 because coverage only reaches 27 reporters from
2010.

### What E0 does not establish

Nothing empirical about the outcome. E0 is construction and classification only.

### Where the detail lives

`scripts/57_e0_extended_panel.py`, `scripts/58_e0_extension.py`,
`scripts/59_freeze_construct_map.py` ·
`data/processed/e0_extended_panel.csv`, `e0_variable_registry.csv`,
`e0_coverage.csv`, `e0_corr_{pooled,between,within}.csv`,
`e0_nonindependence_flags.csv`, `e0_redundancy.csv`, `e0_lineage.csv`,
`e0_provenance.json`, `construct_map_frozen.json` ·
commits `9223306`, `e791e01`, `2103b3d`

---

## PRE — Pre-registration and power

### In plain words

Everything about how Family E will be tested was written down and committed to
git **before any result existed** — the exact model, the exact transformations,
what counts as success, and how much of a signal we could realistically detect.

That last part is the uncomfortable one. The power calculation says we can only
reliably detect effects of about **9.3 points**, which is very large. Most of
what we are about to test will probably come back looking like nothing — but
"we found nothing" and "there is nothing" are different statements. Anything
below that threshold gets labelled **inconclusive under available power**, not
*unsupported*.

The reason the threshold is so high is visible in the numbers: almost all the
usable variation is between countries (SD 12.87) rather than within them
(SD 4.01). That is the same fact P5 found, arrived at from a different direction.

### Questions and outcomes

| | Formula |
|---|---|
| **Primary** | `subjective_poverty ~ arop + C(time) + <construct>` |
| **Secondary** | `(subjective_poverty - arop) ~ C(time) + <construct>` |

AROP is not re-added on the right-hand side of the secondary formula — it is
already inside the outcome by subtraction.

**A secondary result cannot override a primary null.** It may qualify or
illustrate a primary finding; it may never create one.

### Transformations and baselines

Exact formula, direction, baseline and floor fixed for all 11 primaries. All
accumulations verified as **running sums with no backward leakage of future
information**.

Two wording distinctions carried in from review:

- **Housing accumulation** measures deterioration *since the 2010 baseline*, not
  total burden. A country already overburdened in 2010 receives no credit for
  that level.
- **Compounded HICP** measures cumulative *price growth*, not affordability and
  not hardship. Affordability is C4's separate question.

### Multiple-testing families

Three declared BH families: current primaries, accumulated primaries, secondary
outcome. Correction does **not** span the earlier exploratory families A–D.

Sensitivity variants cannot become discoveries when the primary fails.

### Minimum detectable effects

| Effect (SD per SD) | Effect (points per SD) | Power |
|---:|---:|---:|
| 0.1 | 1.33 | 0.117 |
| 0.2 | 2.65 | 0.233 |
| 0.3 | 3.98 | 0.390 |
| 0.4 | 5.31 | 0.535 |
| 0.5 | 6.64 | 0.672 |
| 0.6 | 7.96 | 0.797 |
| **0.7** | **9.29** | **0.895** |
| 0.8 | 10.62 | 0.970 |
| 0.9 | 11.95 | 0.988 |
| 1.0 | 13.27 | 0.995 |

**MDE at 80% power ≈ 0.70 residual SD = 9.29 points.**

Residual SD 13.27 · between-country SD **12.87** · within-country SD **4.01**.

> Two bugs were found and fixed in this simulation before publication. Noise
> drawn by permuting residuals within country preserved each country's mean and
> so correlated with the regressor — a planted +5.31 came back as −2.35, wrong
> in sign and magnitude. And detection counted any p < 0.05 as a hit regardless
> of coefficient sign. Both would have published nonsense.

### Decision criteria

All six must hold:

1. Direction matches the pre-registration
2. FDR-adjusted result survives within its declared family
3. Wild-cluster bootstrap supports it
4. Coefficient is leave-one-country-out stable in sign
5. Greece's **equal-sample** absolute residual improves
6. No proximity or construction-overlap rule is violated

### Frozen-model safeguards

The combined model is the frozen P3 specification. The 15 pairwise family
combinations are **not** reopened. Nothing in E may alter `p5f-frozen`.

### Where the detail lives

`scripts/60_e_preregistration.py`, `scripts/61_e_mde.py` ·
`data/processed/e_preregistration.json`, `e_mde.csv` ·
commits `a747e7a` (pre-registration, no results), `476e177` (MDE)

---

# Part II — Pending stages

## EDA — Descriptive groundwork

### In plain words

Before any testing: what do these variables actually look like? Levels,
trajectories over time, where Greece ranks, and how everything correlates in
all three views. No models, no p-values, no claims — this stage exists so the
modelling that follows is read against a picture of the data rather than in the
abstract.

### Question
### Data and sample
### Levels and trajectories
### Ranks
### Correlation views
### What this does not establish

Nothing inferential. Descriptive corroboration tier only.

### Where the detail lives

---

## E1 — Current-level constructs

### In plain words

### Question
### Pre-registered specification
### Data and sample
### Minimum detectable effect
### Results
### Robustness and validation
### Interpretation
### What this does not establish
### Decision
### Where the detail lives

---

## E2 — Current-level sensitivities

### In plain words

### Question
### Pre-registered substitutions
### Equal-sample comparisons
### Results
### Multiple-testing adjustment
### Interpretation
### Decision
### Where the detail lives

---

## E3 — Diagnostic and contextual checks

### In plain words

### Proximate material-hardship family
### Inequality retest
### Migration and demographic context
### Saving and household balance-sheet context
### Work-effort squeeze retest
### Transfer-policy specification
### Results
### Interpretation limits
### Decision
### Where the detail lives

---

## E4 — Accumulated exposure

### In plain words

### Question
### Eligible constructs
### Transformations and baselines
### Data and equal-sample rules
### Minimum detectable effect
### Results
### Multiple-testing adjustment
### Robustness and validation
### Within-between decomposition
### First-difference evidence
### Interpretation
### Decision
### Where the detail lives

---

## E5 — Accumulation sensitivities

### In plain words

### Question
### Pre-registered alternatives
### Equal-sample comparisons
### Results
### Multiple-testing adjustment
### Interpretation
### Decision
### Where the detail lives

---

## E6 — Frozen combined model

### In plain words

### Purpose
### Frozen specification
### Relationship to E1–E5
### Results carried forward
### Prohibited reinterpretations
### Decision
### Where the detail lives

---

## E7 — Current versus accumulated comparison

### In plain words

### Question
### Head-to-head rules
### Equal-sample verification
### Results
### Greece residual and rank
### Leave-one-country-out stability
### Within-between evidence
### First-difference evidence
### Interpretation
### What this does not establish
### Decision
### Where the detail lives

---

## Final — Claim freeze and publication

### In plain words

### Findings retained
### Findings reworded
### Findings superseded
### Null and inconclusive findings
### Failed or infeasible designs
### Headline-eligible claims
### Mandatory caveats
### Report placement
### Final verification
### Freeze commit and tag

---

# Registers

## Decision Register

| ID | Date | Stage | Decision | Evidence and reason | Alternatives rejected | Status | Supersedes | Commit |
|---|---|---|---|---|---|---|---|---|
| D-01 | 2026-08-21 | P0 | Outcome renamed *backward-extended official subjective-hardship indicator* | 432 overlapping country-years, median abs diff 0.0 pp, none >0.1 pp | Treating the series as our own construction | `frozen` | — | — |
| D-02 | 2026-08-21 | P2 | Synthetic-control design rejected as infeasible; divergence figure non-reportable | Failed 4 of 6 pre-registered gates; donors collapse to HU 0.55 + BG 0.45 | Reporting the +27 pp divergence with caveats | `infeasible` | — | — |
| D-03 | 2026-08-21 | P3 | Branch 2 — material history explains a meaningful share, not all | Residual 27.05 → 6.93, but rank stays 3 of 27 | Branch 1 (strong objective support) | `frozen` | — | — |
| D-04 | 2026-08-21 | P5 | Mundlak outcome B — between-country scarring marker | Between +0.332 (p<0.0001), within −0.076 (p=0.692) | Any dynamic within-country wording | `frozen` | D-03 wording | `p5f-frozen` |
| D-05 | 2026-08-21 | P3a | Family D rejected as incremental predictor | Residual worsens 6.93 → 10.39, rank 3 → 1 on the same 269 rows | Interpreting the −2.17 sign reversal | `frozen` | — | — |
| D-06 | 2026-08-22 | E0 | Construct map frozen: six objective constructs plus one diagnostic | Correlation, redundancy and non-independence evidence across three views | Empirically-fitted family groupings | `frozen` | — | `2103b3d` |
| D-07 | 2026-08-22 | PRE | Family E pre-registration frozen | Committed with zero results present | Testing the 15 pairwise family combinations | `frozen` | — | `a747e7a` |
| D-08 | 2026-08-22 | PRE | MDE published at 0.70 SD = 9.29 points before any E result | Simulation on the actual cluster structure | Publishing E results without a power floor | `frozen` | — | `476e177` |

Allowed statuses: `proposed`, `pre-registered`, `frozen`, `superseded`,
`withdrawn`, `infeasible`.

## Results Register

| ID | Stage | Outcome | Construct or predictor | Estimand | Sample | Estimate | Raw p | FDR p | Wild-bootstrap | LOO | MDE assessment | Interpretation | Status | Output |
|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| R-01 | P3 | hardship level | objective conditions, no accumulation | cross-country residual | n=269 | +27.05 (rank 1/27) | — | — | — | — | — | Greece is the largest outlier in Europe | `supported` | `p3_objective_only.csv` |
| R-02 | P3 | hardship level | `cum_excess_unemployment` | cross-country residual | n=269 | +6.93 (rank 3/27) | — | — | p=0.0005 primary | max 12.7% | above MDE | accumulated history narrows most of the gap | `supported` | `p3_objective_only.csv` |
| R-03 | P5 | hardship level | `cum_excess_unemployment` | between-country | n=269 | +0.3323 | <0.0001 | — | worst p=0.0070 | Greece −0.8% | above MDE | between-country scarring marker | `supported` | `p5_audit.csv` |
| R-04 | P5 | hardship level | `cum_excess_unemployment` | within-country | n=269 | −0.0755 | 0.692 | — | — | — | below MDE | no dynamic evidence | `inconclusive_under_available_power` | `p5_audit.csv` |
| R-05 | P3a | hardship level | accumulated breadth (Family D) | cross-country residual | n=269 | residual 10.39 (rank 1/27) | — | — | — | — | — | worsens the frozen model | `unsupported_with_adequate_power` | `p3a_results.csv` |

Allowed statuses: `supported`, `unsupported_with_adequate_power`,
`inconclusive_under_available_power`, `descriptive_only`, `infeasible`,
`superseded`.

## Claim Register

Claims are **not** duplicated here. The single source of truth is
`docs/claim_matrix.csv` — 53 claims with `introduced_in`, `v2_disposition`,
`superseded_by`, `decision_reason` and `replacement_claim_id`, enforced against
the published documents by `scripts/audit_parity.py` on every build.

<!-- AUTO:BEGIN claim-summary -->
Current state of `docs/claim_matrix.csv`: **53 claims**.

| V2 disposition | Claims |
|---|---:|
| retained | 44 |
| superseded | 4 |
| reworded | 3 |
| descriptive_only | 1 |
| future_research | 1 |
<!-- AUTO:END claim-summary -->

## Corrections and Supersessions

| ID | Date | Original statement or decision | Problem | Correction | Affected artifacts | Commit |
|---|---|---|---|---|---|---|
| C-01 | 2026-08-21 | Synthetic control showed a near-exact pre-crisis fit | The fit was on a degenerate two-point window; the honest 2003–2008 window gives RMSE 25.3 | Design recorded as failed; figure made non-reportable | report, narrative, paper, `project_description_v3.md` | — |
| C-02 | 2026-08-21 | `p=0.037` attributed to synthetic-control placebo inference | It comes from the TWFE country-placebo test | Attribution corrected in all four documents | report, narrative, paper, v3 | — |
| C-03 | 2026-08-21 | P3 reported "strong objective support" (Branch 1) | Hand-written if/else defaulted to the strongest branch; Greece was at rank 3 | Extracted to `branch_rule.py` with 17 tests | `53_p3_objective_only.py` | — |
| C-04 | 2026-08-21 | Wild bootstrap returned p=0.82 against t=9.69 | Unrestricted residuals used instead of null-imposed | Refit under the null and resample those residuals | `54_p5_inference_audit.py` | — |
| C-05 | 2026-08-22 | `real_wages_idx`, `real_income_idx`, `arop_threshold_real`, `pct_below_peak` marked accumulation-ineligible | The project had already built successful accumulations from all four, one an FDR survivor | Binary field replaced by a six-way construction taxonomy | `e0_variable_registry.csv` | `e791e01` |
| C-06 | 2026-08-22 | E0 correlation views omitted `subjective_poverty` and AROPE entirely | Made the intended exploration impossible | Five comparator columns added to all three views | `e0_corr_*.csv` | `e791e01` |
| C-07 | 2026-08-22 | MDE simulation reported power 1.00 at 0.66 points and 0.00 at 6.64 | Within-country residual permutation correlated noise with the regressor; detection ignored coefficient sign | Variance-component noise; sign-aware detection | `61_e_mde.py` | `476e177` |

## Artifact Index

<!-- AUTO:BEGIN artifact-index -->
| Stage | Artifact | Purpose | Status |
|---|---|---|---|
| P0 | `p0_outcome_reconciliation.csv` | Official vs constructed series, country-year | present |
| P0 | `p0_verdict.csv` | The four pre-declared tolerance checks | present |
| P2 | `p2_specifications.csv` | Synthetic-control fit across three pre-periods | present |
| P2 | `p2_donor_weights.csv` | Donor weights showing the two-country collapse | present |
| P2 | `p2_placebo_distribution.csv` | Placebo inference distribution | present |
| P3 | `p3_objective_only.csv` | Objective-only model, residuals by specification | present |
| P3 | `p3_residuals.csv` | Per-country residuals and ranks | present |
| P3a | `p3a_frozen_universe.json` | Family D universe, frozen before testing | present |
| P3a | `p3a_results.csv` | Incremental test of accumulated breadth | present |
| P3a | `p3a_individual_indicators.csv` | Per-indicator breadth components | present |
| P5 | `p5_audit.csv` | Mundlak within/between decomposition | present |
| P5 | `p5_bootstrap.csv` | Wild cluster bootstrap across weights and seeds | present |
| P5 | `p5_influence.csv` | Leave-one-country-out stability | present |
| P5 | `p5f_frozen_result.json` | FROZEN P3/P5/P3a values and eight wording rules | present |
| E0 | `e0_extended_panel.csv` | 27 countries x 2015-2024 candidate panel | present |
| E0 | `e0_variable_registry.csv` | 31 variables: units, roles, construction, proximity | present |
| E0 | `e0_coverage.csv` | Reporter counts by variable and year | present |
| E0 | `e0_corr_pooled.csv` | Pooled correlations incl. five outcome comparators | present |
| E0 | `e0_corr_between.csv` | Between-country correlations | present |
| E0 | `e0_corr_within.csv` | Within-country correlations | present |
| E0 | `e0_nonindependence_flags.csv` | 35 flags across four overlap types | present |
| E0 | `e0_redundancy.csv` | Primary-vs-sensitivity redundancy, all three views | present |
| E0 | `e0_lineage.csv` | How each derived variable was constructed | present |
| E0 | `e0_provenance.json` | Source series and vintage | present |
| E0 | `construct_map_frozen.json` | FROZEN six constructs plus one diagnostic | present |
| PRE | `e_preregistration.json` | FROZEN outcomes, transformations, decision rule | present |
| PRE | `e_mde.csv` | Power curve; MDE 0.70 SD = 9.29 points at 80% | present |
<!-- AUTO:END artifact-index -->
