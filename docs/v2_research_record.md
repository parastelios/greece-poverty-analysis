# V2 Research Record

## How to read this

This is the living record of the V2 analysis. It documents what was planned,
what was run, what was found, and what decision followed at each stage.

Every stage below opens with **In plain words** — a short, non-technical
account of what the step was for and what came out of it. If you read nothing
else, read those. Everything after that heading is the formal record.

Every stage ends with **Where the detail lives** — the script that produced it,
the files it wrote, and the commit that froze it.

Some stages also carry **Notes from review** — why a decision went the way it
did, what was argued against, and what was caught by review rather than by the
code. These exist because the reasoning is the first thing to evaporate. Six
months from now the numbers will still be in the CSVs; the argument that
produced them will not be anywhere else.

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
| Last completed stage | EA |
| Branch | `p6-rewrite` |
| HEAD | `ad37d6a` Expand E0 into a step-by-step account with per-step results and file pointers |
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
- Freezing a result protects its numbers and interpretation. It does not
  protect an inaccurate label, and it does not forbid a pre-registered audit of
  what the result depends on.
- Evidence that deprivation predicts hardship is **not** equivalent to evidence
  from income, employment, wage or housing data. Both are analytically
  relevant; both are reported as separate layers, never forced under one
  "objective" label.
- E1 and E4 use the neutral baseline `AROP + year effects`. P3 returns only at
  E6, as the frozen combined benchmark reported alongside the deprivation-free
  companion.

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
| EA | How much of the P3 result depends on a same-instrument predictor? | complete | `ea_preregistration.json` | — | [EA](#ea--deprivation-free-companion-audit) |
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

### Notes from review

The tolerances were declared before the comparison ran, which mattered more than
it looked at the time: the agreement turned out to be near-perfect, and a
tolerance set *afterwards* would have been unfalsifiable no matter what number
it contained.

The renaming was not cosmetic. Calling it "our constructed series" understated
what it is and invited a reviewer to ask why we had not simply used the official
indicator. Calling it "the official indicator" would have overstated the pre-2010
segment, which has no official counterpart. The compound name is the only one
that survives both objections.

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

### Notes from review

An earlier draft reported this design as evidence, citing a near-exact
pre-crisis fit. That fit existed only on a degenerate two-point window
(2007–2008). On the honest 2003–2008 window the RMSE is 25.3 — a failure. The
error reached three published documents before review caught it.

A separate error travelled with it: `p=0.037` was attributed to synthetic-control
placebo inference when it comes from the TWFE country-placebo test.

The machine-enforced ban exists because of how that first error propagated. A
figure that is merely *documented* as unreportable gets copied into a summary
by someone reading quickly. One that fails the build does not.

### Where the detail lives

`scripts/52_p2_comparative_design.py` ·
`data/processed/p2_specifications.csv`, `p2_donor_weights.csv`,
`p2_placebo_distribution.csv` ·
`docs/publication_strategy.md` § "P2 FAILS its pre-registered gates"

---

## P3 — How much of Greece's gap do objective conditions explain?

> **Label corrected 2026-08-22.** This is the **frozen P3 mixed-distance
> model**, not an objective-only model: it excludes the closest Tier-0
> indicators but retains official severe material and social deprivation, drawn
> from the same survey system as the outcome. The numbers, specification and
> interpretation below are frozen and unchanged. What changed is the label and
> the addition of a pre-registered audit — see [EA](#ea--deprivation-free-companion-audit).

### In plain words

We predicted each country's hardship level from objective conditions,
deliberately excluding the measures closest to the outcome — arrears, being
unable to meet an unexpected expense, financial expectations. Greece's actual
hardship sits far above what those conditions predict: **27 points above**, the
worst gap in Europe. Then we added one variable — how much cumulative excess
unemployment the country has absorbed since the crisis — and the gap fell to
**7 points**.

So adding accumulated unemployment substantially narrows Greece's cross-country
prediction residual. It does not eliminate it. **Greece remains among the three
most under-predicted countries in Europe**, which is what kept this at Branch 2
rather than Branch 1.

One caveat on the label, and it is not only a caveat. Of P3's six predictors,
`severe_mat_soc_deprivation` is classified by E0 as `proximate_same_instrument`
— it comes from the same survey system as the outcome and belongs to construct
P1, the diagnostic-only construct. So this model excludes the *closest*
proximate measures but is not free of same-instrument hardship indicators.

Freezing P3 protects its numbers from being changed after the fact. It does not
oblige us to keep calling it "objective-only" once one predictor is known to
break the proximity rule we adopted later. So the model keeps its numbers and
gets an accurate name — the **frozen P3 mixed-distance model** — and the
question of how much the result depends on that one predictor is settled by a
pre-registered audit rather than by wording. See [EA](#ea--deprivation-free-companion-audit).

### Question

With the Tier-0 proximate indicators excluded, how large is Greece's residual,
and does accumulated exposure narrow it?

### Specification

Six predictors plus year fixed effects, all fixed in advance:

| Predictor | E0 proximity class |
|---|---|
| `severe_mat_soc_deprivation` | **`proximate_same_instrument`** (construct P1) |
| `housing_cost_overburden` | `objective` |
| `ltu_rate` | `objective` |
| `aic_pps_pc_k` | `objective` |
| `wage_years_below_2008` | derived accumulation |
| `cum_excess_unemployment` | derived accumulation |

Excluded by construction (Tier 0): arrears, inability to meet an unexpected
expense, financial expectations.

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

### Notes from review

The branch rule is the origin of a policy now applied to every decision rule in
the project. The pre-commitment was correct and written down in advance; the
implementation had an if/else chain whose final `else` returned the strongest
available conclusion. Nothing in the prose was wrong. The code simply did not
implement it, and the first run published the wrong branch.

Since then a decision rule is a tested function or it is not a rule.
`branch_rule` (17 tests), `mundlak_rule` (23), `ea_rule` (47). The EA run proved
the policy was not paranoia: that rule failed too, on a case its author had not
imagined.

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
stating carefully — and carefully means resisting the stronger sentence that
keeps suggesting itself.

The accumulated-unemployment result works by comparing *countries to each
other*: countries that absorbed more accumulated unemployment have higher
hardship. That signal is strong and statistically solid.

The second half is where the wording has to stay disciplined. **We found no
supporting within-country evidence, and the estimate is too imprecise to
establish or rule out such a relationship.** It is flat and inconclusive, not
demonstrated to be absent.

Two things this specifically does not say. It does not say the relationship
fails *inside Greece*: the within coefficient pools year-to-year variation
across all 27 countries, so it is not a Greece-specific time series, and we
never estimated one. And it does not say there is no dynamic relationship —
only that this analysis does not demonstrate one.

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

![The effect is between countries, not within them](figures/between_within.svg)

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

### Notes from review

This is the stage that most changed what the project is allowed to claim, and
the wording rules are strict because the tempting sentence is so close to the
defensible one.

"As exposure accumulated, hardship rose" is banned outright. It describes a
within-country dynamic the analysis does not support, and it is what most
readers will assume the between-country result means unless told otherwise.

The `p=0.058` equality test caused a specific argument. It fails to reject
equality of the within and between coefficients — and it is *not* evidence they
are equal. The point estimates remain −0.076 and +0.332. A rule was locked
requiring both facts to be stated together, because quoting the p-value alone
implies a conclusion the test cannot deliver.

The bootstrap was also wrong on the first attempt: unrestricted residuals gave
p=0.82 against t=9.69. Nonsense loud enough to notice — which is the only reason
it was caught, and an argument for reporting test statistics alongside p-values.

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

**Failed the incremental criterion, and reversed sign conditionally.** This is
a result about the specification, not a power-based null: breadth measurably
worsened the model it was added to. No MDE was computed for this family, so it
must not be recorded as *unsupported with adequate power*. The universe was
frozen in `p3a_frozen_universe.json` before testing.

### Notes from review

The sign reversal was left uninterpreted deliberately, and that was a choice
made against real temptation. A conditional coefficient of −2.17 on a breadth
measure invites a story about compensating adjustment or habituation. Any such
story would have been constructed after seeing the sign, on a variable that had
just failed its pre-registered test.

Freezing the universe first is what made the null publishable. Without it, a
failed breadth measure would simply have been dropped and never mentioned —
which is how null results disappear.

### Where the detail lives

`scripts/55a_p3a_freeze_universe.py`, `scripts/55b_p3a_family_d.py` ·
`data/processed/p3a_frozen_universe.json`, `p3a_results.csv`,
`p3a_individual_indicators.csv` ·
`docs/publication_strategy.md` § "P3a result"

---

## E0 — Data and construct map

### In plain words

E0 was a data preparation and quality-control stage. **No new models were run
and no search for significant results took place.** Five things happened.

**1. Put the data in one place.** We combined the existing model data with
additional variables from the statistical appendix. The result covers 27 EU
countries from 2015 to 2024.

**2. Checked whether the data are complete.** We recorded how many countries and
years are available for every variable. Most have complete coverage; a few have
clearly documented gaps.

**3. Described what every variable actually measures.** For each one we recorded
its source and unit; whether higher or lower values indicate hardship; whether
it is objective, self-reported or contextual; whether it overlaps with another
variable; and whether and how it can be accumulated over time.

**4. Separated variables that look similar but measure different things.**
Inflation is not the price level. Migration is not unemployment. Inequality is
not deprivation. Working hours alone do not necessarily indicate hardship. And
arrears and unexpected expenses sit very close to the subjective-hardship
question itself.

**5. Compared relationships in three different ways** — across all
country-years, between countries' average positions, and within countries as
conditions changed over time. Some relationships that look strong across
countries turn weak or reverse direction within them. Pooled correlations alone
would have produced misleading variable groups.

That work supported six defensible questions:

- Do material resources matter?
- Does labour-market exclusion matter?
- Does falling behind one's own past matter?
- Does wage-adjusted affordability matter?
- Does accumulated inflation matter?
- Does housing pressure matter?

A seventh group — proximate hardship indicators such as arrears — is kept
visible but **cannot be used as the headline explanation**, because it is too
close to the outcome being explained.

So E0's result is not a statistical conclusion. It is a documented map of the
available evidence, plus rules preventing incompatible, duplicated or circular
variables from being mixed in the next stage.

### Notes from review

The first proposed grouping was rejected, and the reasons are worth keeping.

*Families were being fitted, not theorised.* `net_migration` and `s80s20` had
been assigned to whichever family they correlated with best — immediately after
stating that correlation should validate theory groupings, not define them. Both
are now contextual or standalone retests.

*"Coherence" was an undefined number.* A ratio of within-family to
between-family mean |r|, presented as if it were interpretable on its own.

*HICP was a category error.* The three HICP series are inflation *rates*, and
they had been pooled as country "price levels". The correlation evidence then
settled the matter independently: near-zero pooled against `wadj_a01`, and
sign-reversing between the views.

*Four variables were wrongly ruled out.* `real_wages_idx`, `real_income_idx`,
`arop_threshold_real` and `pct_below_peak` were marked "already indexed" and so
ineligible for accumulation — when the project had already built accumulations
from all four, one of which (`wage_years_below_2008`) was an FDR survivor.

The binary eligible/ineligible field was the root cause of that last error, and
it was replaced with the six-way taxonomy rather than corrected in place.

> Two errors were caught in review and corrected. The correlation tables
> originally left out the outcome itself, which made the intended exploration
> impossible. And four variables were wrongly marked ineligible for
> accumulation when the project had already built accumulations from all four —
> one of them a surviving result from an earlier stage.

---

### Step 1 — The combined dataset

One table: **27 EU countries · 2015–2024 · 270 country-year rows · 68 columns**,
carrying hardship, AROP, AROPE and the candidate variables together. Seventeen
series were merged in from the statistical appendix.

`data/processed/e0_extended_panel.csv`

### Step 2 — Coverage results

Coverage is generally strong: **24 of 31 variables are complete at 270/270**,
all 27 countries in every year. The seven exceptions are all documented:

| Variable | n_obs | Countries | What is missing |
|---|---:|---:|---|
| `arop_threshold_real` | 260 | 26 | **Croatia** entirely — its threshold series begins too late to index to 2008 |
| `arrears` | 268 | 27 | Luxembourg 2018, 2019 |
| `saving_rate` | 268 | 27 | Bulgaria 2023, 2024 |
| `debt_to_income` | 268 | 27 | Bulgaria 2023, 2024 |
| `real_income_idx` | 268 | 27 | Bulgaria 2023, 2024 |
| `net_migration` | 269 | 27 | Portugal 2024 |
| `housing_cost_overburden` | 269 | 27 | France 2021 |

Revised AROPE covers all 27 countries in every year, verified, with no splice
required.

Most comparisons can therefore use the full panel. Anything involving the real
AROP threshold runs on a smaller sample or as a clearly labelled sensitivity
check — and because the gap is one whole country rather than scattered
country-years, that sample is 26 countries, not 27.

![Coverage gaps, located](figures/coverage.svg)

`data/processed/e0_coverage.csv` — columns mean:

| Column | Meaning |
|---|---|
| `n_obs` | available country-years |
| `pct` | percentage coverage |
| `countries` | countries represented |
| `min_year_reporters` | smallest number of countries available in any one year |
| `years` | years with observations |

### Step 3 — Variable-classification results

Each of the **31 variables** is documented by: meaning and unit; Eurostat
source; expected adverse direction; whether it is a level, flow or derived
measure; whether it is objective, proximate, contextual or mechanically
related; how it could be accumulated; and whether it is a primary measure,
sensitivity, contextual item or retest.

| Variable | Classification |
|---|---|
| `aic_pps_pc` | primary resources measure (C1) |
| `ltu_rate` | primary current labour measure (C2) |
| `wadj_a01` | wage-adjusted affordability (C4) |
| `hicp` | **inflation, not a price-level measure** (C5) |
| `arrears`, `unexpected_expenses` | proximate, same survey framework as hardship (P1) |
| `net_migration` | contextual — **not** unemployment |
| `s80s20` | inequality retest — **not** deprivation |
| `debt_to_income`, `saving_rate` | ambiguous-direction context |
| `work_effort_squeeze` | overlaps strongly with hours and hourly compensation |

`cum_excess_unemployment` is the primary *historical* labour measure, but it is
**not** one of the 31 registry rows — it is a derived accumulation carried in
from the earlier P3 work, and it appears in the frozen construct map as C2's
accumulated representative rather than in the E0 registry.

Roles assigned across the 31:

| Role | Count |
|---|---:|
| Primary representative | 9 |
| Sensitivity variant | 9 |
| Proximate diagnostic | 4 |
| Contextual descriptive | 3 |
| Mechanical comparator | 3 |
| Standalone retest | 2 |
| Standalone retest of known null | 1 |

`data/processed/e0_variable_registry.csv`

Related technical detail:

| File | Holds |
|---|---|
| `e0_provenance.json` | sources and versions |
| `e0_lineage.csv` | shared construction inputs |
| `e0_nonindependence_flags.csv` | definitional and construction overlaps — **35 flags** across four types |

### Step 4 — Correlation results

The three views showed that relationships depend on which question is being
asked.

| Pair | Pooled | Between | Within | Reading |
|---|---:|---:|---:|---|
| `aic_pps_pc` – `consumption_pc` | 0.899 | 0.972 | 0.831 | resources measures are highly redundant |
| `aic_pps_pc` – `hourly_comp` | 0.903 | 0.915 | 0.932 | |
| `ltu_rate` – `unemployment_rate` | 0.914 | 0.897 | 0.961 | labour measures are highly redundant |
| `ltu_rate` – `employment_rate` | −0.769 | −0.759 | −0.802 | |
| `wadj_a01` – `work_effort_squeeze` | **0.963** | 0.968 | 0.924 | two versions of one structural position — may never enter a model together |
| `wadj_a01` – `hicp` | 0.058 | **0.480** | **−0.285** | **sign reverses** — inflation and affordability are not one construct |
| `wadj_a01` – `hicp_food` | 0.087 | 0.637 | −0.253 | sign reverses |
| `wadj_a01` – `hicp_housing` | 0.011 | 0.222 | −0.130 | sign reverses |

The three HICP pairs are the reason C5 was separated from C4 on evidence rather
than preference: near-zero pooled, moderately positive between countries,
negative within them.

![Why pooled correlations alone would have misled us](figures/sign_reversal.svg)

| File | Holds |
|---|---|
| `e0_corr_pooled.csv` | across all country-years |
| `e0_corr_between.csv` | between countries' average positions |
| `e0_corr_within.csv` | within countries over time |
| `e0_redundancy.csv` | primary–sensitivity redundancy, all three views, with `sign_flips` |

All three correlation views carry five comparator columns: `subjective_poverty`,
`arop`, `arope`, `gap_subj_arop`, `gap_subj_arope`.

### Step 5 — The frozen construct map

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

C6 uses 2010 rather than 2008 because coverage only reaches 27 reporters from
2010.

`data/processed/construct_map_frozen.json`

### Construction and non-independence findings

A six-way accumulation taxonomy replaced the earlier binary
eligible/ineligible field: `direct_excess`, `fixed_base_shortfall`,
`duration_below_base`, `compounded_change`, `ambiguous_direction`,
`not_applicable`.

**35 non-independence flags** across four types: `arithmetic_coupling`,
`definitional_overlap`, `component_overlap`, `construction_overlap`.

### What E0 does not establish

Nothing empirical about the outcome. E0 is construction and classification
only. The data are mostly complete, but many candidate variables overlap, some
have ambiguous meanings, and pooled correlations alone would have produced
misleading families. What E0 buys is that the next stage can test clearly
separated hypotheses instead of searching across a loosely assembled variable
list.

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

![Power curve with the published MDE marked](figures/mde_power.svg)

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

## EA — Deprivation-free companion audit

### In plain words

P3's headline model contains one predictor that, by the rules we adopted later,
should not be in a headline model: severe material and social deprivation comes
from the same survey system as the outcome we are trying to explain. Using it to
predict hardship is closer to explaining a thing with itself than the other five
predictors are.

We are not going to fix this by choosing better words. We run **one** extra
model — same countries, same years, same year effects, the same five remaining
predictors, with that one variable removed — and see what happens to the result.
Nothing gets substituted in its place, and we do not go looking for a better
companion if the first one disappoints. That is the whole point of writing this
down beforehand.

Three things can happen, and all three were decided before the model was run. If
the result largely survives, the cleaner model becomes the headline. If it
weakens moderately, we report a range instead of a single number and say openly
that it depends on how strictly you define distance from the outcome. If it
collapses, we say plainly that the P3 result depends materially on a
same-instrument deprivation measure.

The rule that matters most is the one preventing us from cheating: **we may
never pick between the two models just because one produces the smaller
residual.** Both get reported whatever happens.

### Question

How much of the frozen P3 result depends on `severe_mat_soc_deprivation`, a
predictor E0 classifies `proximate_same_instrument`?

### Two roles

| | Frozen P3 | Companion |
|---|---|---|
| Status | audited historical benchmark, unchanged | new, pre-specified |
| Label | frozen P3 **mixed-distance** model | deprivation-free companion |
| Predictors | 6 | 5 |
| `severe_mat_soc_deprivation` | retained | **removed** |
| Sample | 2015-2024, n = 269 | identical |
| Year effects | yes | identical |
| Substitutions | -- | **none permitted** |

### Comparisons required

Identical observations (verified by row count and index) - Greece residual and
rank - accumulated-unemployment coefficient - wild-cluster inference -
leave-one-country-out stability - VIFs - within/between decomposition **only if**
the companion becomes headline.

### Decision rule

Implemented as `scripts/ea_rule.py`, tested by `scripts/test_ea_rule.py`
(37 tests). The function is the pre-registration; the prose below describes it.

> Prose alone already failed once here. The first P3 run reported the strongest
> branch because an if/else chain ended in a default `else`.

| Outcome | Condition | Consequence |
|---|---|---|
| **A** | degradation <= 3.0 points, rank does not deteriorate, all stability gates pass | companion becomes the cleaner headline specification |
| **B** | degradation <= 8.0 points | material support, reported as an explicit **range** across proximity choices |
| **C** | degradation > 8.0 points, rank deteriorates, or any stability gate fails | frozen P3 depends materially on an official but same-instrument deprivation measure |

Degradation is the companion's absolute residual minus frozen P3's 6.93.
Thresholds are anchored to the 20.12-point narrowing accumulation delivers
(27.05 -> 6.93): 3.0 points is about 15% of it, 8.0 points about 40%.

**Hard gates, any one forcing C:** coefficient not positive - bootstrap does not
support - not LOO sign-stable - max VIF > 10.0 - Greece's rank deteriorates.

**The anti-selection rule.** Outcome A is earned by proximity cleanliness plus
stability, never by producing the smaller residual. A companion residual
*smaller* than frozen P3's is recorded and never rewarded -- dropping a predictor
cannot improve out-of-sample standing for a reason this design can attribute.
Both specifications are reported under every outcome, including A.

### Notes from review

EA exists because of a label, and the argument that produced it is worth
recording precisely.

Review found that P3 — described throughout as the "objective-only" model —
contains `severe_mat_soc_deprivation`, which E0 later classified
`proximate_same_instrument`, construct P1: the construct the E pre-registration
reserves as diagnostic-only and never headline. P3 excludes the *closest*
proximate measures, but is not free of same-instrument ones.

The first proposed fix was wording: relabel and move on. That was rejected, and
correctly. The reasoning: freezing a result protects its specification, numbers
and interpretation from post-hoc alteration — it does not oblige anyone to keep
using an inaccurate label, and it does not forbid a pre-registered audit of what
the result depends on. Two roles, not one correction.

The anti-selection rule was written before the run for an obvious reason: with
two specifications on the table, whichever produced the smaller residual would
have been extremely easy to prefer for stated reasons that were not the real
ones.

The 3.0 and 8.0 point bands are the one number chosen without external anchor.
They are pinned to the 20.12-point narrowing accumulation delivers (≈15% and
≈40%), so "moderate" and "sharp" mean something on this problem — but a
different anchoring would have given different bands, and that should be
remembered if EA is ever cited as a precedent.

### Minimum detectable effect

No new MDE. EA compares two specifications on identical observations rather than
running a new significance test. If the companion becomes headline, its
within/between evidence inherits the published floor of 0.70 SD = 9.29 points
and its labelling rule.

### Results

Frozen P3 reproduced exactly on this run: residual +6.93, rank 3/27, R² 0.907,
n = 269. Nothing frozen changed.

| | Frozen P3 | Companion |
|---|---:|---:|
| Predictors | 6 | 5 |
| n | 269 | 269 (identical rows) |
| R² | 0.907 | **0.821** |
| Greece residual | **+6.93** | **−9.39** |
| Greece rank | 3 of 27 | 25 of 27 |
| `cum_excess_unemployment` | +0.2808 (se 0.0290) | +0.2271 (se 0.0459) |
| Wild-cluster bootstrap p | 0.0005 | 0.0285 |
| LOO coefficient range | — | +0.1655 to +0.2490, sign-stable |
| Max VIF | — | 4.82 |

Equal-sample rule: `severe_mat_soc_deprivation` had no additional missing values,
so re-deriving complete cases would have given the same 269 rows. The constraint
bound nothing here — but it was verified before estimation, not after.

**Greece's residual reverses sign.** Frozen P3 under-predicts Greek hardship by
6.93 points. The companion *over*-predicts it by 9.39. Rank 25 of 27 is third
from the opposite end of the ladder: Greece did not leave the extreme group, it
crossed to the other tail.

![Greece's residual reverses when deprivation is removed](figures/ea_reversal.svg)

![Where every country sits, in both specifications](figures/residual_ladders.svg)

Removing deprivation also destroys the narrowing story. In frozen P3,
accumulation moves Greece +27.05 → +6.93. In the companion the same comparison
is +9.52 → −9.39: not a narrowing, a crossing.

![What adding accumulated unemployment does, in each model](figures/narrowing.svg)

### The decision rule failed, and had to be corrected

**The rule as pre-registered returned Outcome A.** That verdict was wrong, and
the reason matters more than the result.

`decide()` compared *absolute* residuals: |−9.39| − |6.93| = +2.46 points, inside
band A's 3.0-point threshold. And its rank gate was one-tailed — it checked only
whether Greece became *more* under-predicted, so rank 3 → 25 registered as an
improvement.

Both are implementation defects, not disagreements with the pre-registration.
The pre-registered prose for Outcome A reads "companion still materially
narrows Greece's residual." A residual crossing zero does not narrow under any
reading of that sentence. The function diverged from the condition it was
written to implement — the same class of failure as the P3 `branch_rule` default
`else`, which also returned the strongest conclusion on a case its author had
not anticipated.

Two corrections, both regression-tested:

- **Sign reversal is not narrowing.** A residual crossing zero returns C unless
  it lands within 3.0 points of zero, in which case it genuinely did narrow.
- **Extremeness is two-tailed.** Tail position is `min(rank, n − rank + 1)`, so
  rank 3 and rank 25 of 27 both score 3. Greece's tail position is *unchanged*.

`test_ea_rule.py` grew from 37 to 47 tests; the observed case (−9.39 at rank 25)
is now a named regression test.

### Notes from review

Two things about this correction need to be defensible, not just stated.

**Why this is fixing an implementation, not moving a goalpost.** The
pre-registered prose for Outcome A reads *"companion still materially narrows
Greece's residual."* A residual crossing zero does not narrow under any reading
of that sentence. So the function and the frozen prose disagreed, and the prose
is the pre-registration. The prose was not touched.

**What would make this illegitimate.** If the prose had been ambiguous — if it
had said "improves" or "performs comparably" — then choosing an interpretation
after seeing −9.39 would be exactly the post-hoc rule-fitting the whole protocol
exists to prevent. The fix survives only because "narrows" is unambiguous about
direction.

The reversal tolerance (3.0 points) *was* chosen while looking at the result. It
does not change this verdict — any tolerance below 9.39 yields C — but it was
not set blind, and it should be treated as provisional if EA is reused.

Worth noting what the defect was not: not a coding slip. Both defects come from
the same unexamined assumption — that the residual would stay positive and only
shrink. Every test written before the run shared that assumption, which is why
47 tests passed while the rule was wrong.

### Decision

**Outcome C — the frozen P3 result depends materially on an official but
same-instrument deprivation measure.**

Both specifications are reported, per the anti-selection rule.

### Interpretation

`severe_mat_soc_deprivation` was carrying the fit. Without it, R² falls from
0.907 to 0.821, and the remaining predictors — long-term unemployment, income,
wage history, accumulated unemployment — predict Greece should report
*substantially more* hardship than it does.

That is a finding about the evidence layers, not a repair of P3. Greece's
hardship tracks its deprivation closely; conditional on labour-market and income
data alone it is over-predicted. The two layers do not tell the same story, which
is precisely why they may not sit under one "objective" label.

### What this does not establish

That the companion is the better model — it is not, and Outcome C means it does
not take the headline. That deprivation "causes" the fit. And nothing about
`p5f-frozen`, which is unchanged and was re-verified on this run.

The accumulated-unemployment coefficient survives in the companion (+0.2271,
bootstrap p = 0.0285, LOO sign-stable), so the accumulation result is not itself
an artefact of deprivation. What depends on deprivation is Greece's *position*
relative to prediction, not the coefficient.

### What this does not establish

Nothing about `p5f-frozen`, which EA may not alter. And a clean companion result
would not make the model "objective" in the strict sense -- it would make it
free of *same-instrument* predictors, which is a narrower claim.

### Where the detail lives

`scripts/63_ea_preregistration.py`, `scripts/ea_rule.py`,
`scripts/test_ea_rule.py` -
`data/processed/ea_preregistration.json`

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
| D-09 | 2026-08-22 | EA | P3 relabelled *frozen P3 mixed-distance model*; numbers unchanged | `severe_mat_soc_deprivation` is `proximate_same_instrument`, construct P1 | Keeping the "objective-only" label; re-estimating frozen P3 | `frozen` | D-03 label only | — |
| D-10 | 2026-08-22 | EA | One deprivation-free companion pre-registered; no substitutions, no further searching | Documented classification inconsistency, not a result | Searching for a better companion; leaving it to wording | `pre-registered` | — | — |
| D-11 | 2026-08-22 | EA | Selection between the two specifications may never be made on residual size | A smaller residual from dropping a predictor is not attributable improvement | Choosing whichever model looks better | `frozen` | — | — |
| D-12 | 2026-08-22 | EA | E1 and E4 use the neutral baseline `AROP + year effects`, not P3 | P3 carries a P1 predictor and must not seed the construct tests | Using P3 as the E-stage baseline | `frozen` | — | — |
| D-13 | 2026-08-22 | EA | Outcome C: frozen P3 depends materially on a same-instrument deprivation measure | Greece's residual reverses, +6.93 → −9.39; R² 0.907 → 0.821 | Outcome A, which the defective rule returned | `frozen` | — | — |
| D-14 | 2026-08-22 | EA | `ea_rule` corrected: sign reversal is not narrowing; extremeness is two-tailed | Function diverged from the pre-registered prose it implements | Publishing Outcome A; changing the pre-registered prose instead | `frozen` | — | — |

Allowed statuses: `proposed`, `pre-registered`, `frozen`, `superseded`,
`withdrawn`, `infeasible`.

## Results Register

| ID | Stage | Outcome | Construct or predictor | Estimand | Sample | Estimate | Raw p | FDR p | Wild-bootstrap | LOO | MDE assessment | Interpretation | Status | Output |
|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| R-01 | P3 | hardship level | objective conditions, no accumulation | cross-country residual | n=269 | +27.05 (rank 1/27) | — | — | — | — | — | Greece is the largest outlier in Europe | `supported` | `p3_objective_only.csv` |
| R-02 | P3 | hardship level | `cum_excess_unemployment` | cross-country residual | n=269 | +6.93 (rank 3/27) | — | — | p=0.0005 primary | max 12.7% | above MDE | accumulated history narrows most of the gap | `supported` | `p3_objective_only.csv` |
| R-03 | P5 | hardship level | `cum_excess_unemployment` | between-country | n=269 | +0.3323 | <0.0001 | — | worst p=0.0070 | Greece −0.8% | above MDE | between-country scarring marker | `supported` | `p5_audit.csv` |
| R-04 | P5 | hardship level | `cum_excess_unemployment` | within-country | n=269 | −0.0755 | 0.692 | — | — | — | below MDE | no dynamic evidence | `inconclusive_under_available_power` | `p5_audit.csv` |
| R-06 | EA | hardship level | companion, `severe_mat_soc_deprivation` removed | cross-country residual | n=269, identical rows | residual −9.39 (rank 25/27); R² 0.821 | — | — | p=0.0285 for `cum_excess_unemployment` | sign-stable, +0.1655 to +0.2490 | no new MDE; comparison on identical observations | residual reverses sign; frozen P3 depends materially on a same-instrument measure | `outcome_C` | `ea_results.csv` |
| R-05 | P3a | hardship level | accumulated breadth (Family D) | cross-country residual | n=269 | residual 10.39 (rank 1/27); coefficient −2.17 | — | — | — | — | no MDE computed for this family | failed the incremental criterion and reversed sign conditionally; reversal left uninterpreted | `failed_incremental_criterion` | `p3a_results.csv` |

Allowed statuses: `supported`, `unsupported_with_adequate_power`,
`inconclusive_under_available_power`, `failed_incremental_criterion`,
`descriptive_only`, `infeasible`, `superseded`.

`outcome_C` is EA's pre-registered verdict label, not a generic status.

`unsupported_with_adequate_power` requires a published MDE showing the test
could have detected an effect of the relevant size. Without one, use
`inconclusive_under_available_power`. `failed_incremental_criterion` is for a
predictor that measurably *worsened* the specification it was added to — a
result about the model, not about statistical power.

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
| C-08 | 2026-08-22 | EA rule returned Outcome A on the live run | Compared absolute residuals across a sign flip (+2.46, inside band A) and gated rank one-tailed, so rank 3 → 25 read as improvement | Sign reversal returns C unless within 3.0 points of zero; tail position `min(rank, n−rank+1)`; 10 new regression tests | `ea_rule.py`, `test_ea_rule.py` | — |
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
| EA | `ea_preregistration.json` | FROZEN deprivation-free companion spec and decision rule | present |
| EA | `ea_results.csv` | Outcome C: residual reverses +6.93 -> -9.39 | present |
| EA | `ea_companion_residuals.csv` | Companion residual ladder, 27 countries | present |
<!-- AUTO:END artifact-index -->
