# Project Description Version 3

## The Greek Poverty Paradox — two estimands, separately identified

**Document status:** A design proposal written with the completed exploratory
project in hand, and revised after review. It is not an edit of v2. Nothing
here has been implemented.

**Correction from the first draft of this document.** That draft proposed
promoting synthetic control to the project's primary design, citing a
"near-exact pre-period fit (RMSE ≈ 0.00)" and a placebo p of 0.037. Both
attributions were wrong, and the error was mine:

- **p = 0.037 is not a synthetic-control result.** It is the permutation rank
  from the two-way fixed-effects country-placebo exercise in
  `scripts/41_reporting_style_robustness_v2.py` — Greece ranks first of 27
  units, and 1/27 = 0.037. It says nothing about synthetic control.
- **The implemented synthetic control does not fit Greece.** On the 2003–2008
  window it fails outright: pre-period RMSE **25.32**, with synthetic Greece at
  2.7–8.1 while actual Greece sits at 27.3–34.4. The post-period "divergence"
  of ~40 points rests on a ~25-point gap that was already there before the
  crisis. Only six countries have complete 2003–2008 coverage.
- **The RMSE ≈ 0.00 figure comes from a 2007–2008 match** — two pre-period
  observations fitted with roughly 25 free donor weights. A near-exact fit
  there is mechanically unsurprising rather than evidential. The published
  paper does disclose the window, but it describes the result as "corroborating
  the regression estimate by an entirely non-regression-based method," which
  claims more than a two-point match can support. **This wording should be
  revisited in the final round regardless of what v3 adopts.**

Synthetic control is therefore treated below as an **unbuilt design with
pre-registered gates it may fail**, not as existing evidence.

---

## 1. What the first project established

Worth stating first, because a redesign that discards the findings would be a
worse project.

- **The measurement mechanism.** Greece's real AROP threshold fell with the
  median during the collapse, so the annual relative rate stayed calm while the
  living standard it represented deteriorated. The cleanest finding in the
  project, and the least model-dependent.
- **Duration beats level.** Long-term unemployment outperforms headline
  unemployment; accumulated exposure since 2009 adds information. Greece 138
  accumulated percentage-point-years against an EU median of 6.
- **Real wages below their own 2008 level for 15 consecutive years**, the
  longest run in the Union.
- **A time-invariant culture-only account is insufficient.** Greece's pre-crisis
  baseline is high, but the widening is not explained by a fixed country
  premium, and the extremity is specific to
  financial questions rather than general life satisfaction. Greece ranks first
  of 27 in the country-placebo; the associated p = 0.037 is a
  permutation statistic under an exchangeability assumption across countries,
  not literal randomization inference \u2014 nothing was randomly assigned.
- **Breadth.** Across 25 indicators excluding the outcome and every covariate,
  the share placing Greece in the EU's worst quintile went from 21% pre-crisis
  to 58% from 2012, 68% in 2024, first of 27.

**What the design cost:** 29 candidates across three families, 2 survivors;
families B and C turned out to be re-expressions of family A (correlations
0.964, 0.950, 0.948 across family dividers); and the headline quantity moved
from 25.6 to −0.8 across the model ladder before settling at 2.7 under nested
validation.

---

## 2. The problem to fix, stated precisely

v1's headline was Greece's out-of-sample residual in a cross-country model.
That quantity moves with the admitted predictor set:

| specification | Greece's out-of-sample gap |
|---|---|
| A: unemployment, income, deprivation, AROP | 25.6 |
| B: A + housing cost overburden | 35.5 |
| C: B + arrears, unexpected-expense capacity | 11.6 |
| C-LTU | 3.9 |
| Fixed Model G: + accumulated unemployment | −0.8 |
| Nested validation | 2.7 |

The first draft of this document said "nothing in the data adjudicates between
these." That was too strong, and the reviewer was right to reject it. Theory,
conceptual proximity to the outcome, out-of-sample prediction and nested
validation all provide evidence, and the project used them. What the data
**cannot** identify is a single uniquely correct conditional residual — the
number that gets quoted as *the* answer.

The fix is not to abandon the panel model. It is to stop asking one design to
answer two questions.

---

## 3. Two estimands, kept separate

### Estimand 1 — comparative divergence

> How did Greek reported hardship diverge, after the crisis, from a credible
> comparative trajectory?

Answered by a comparative-case design (§4). Establishes **timing and
magnitude of the break**.

### Estimand 2 — material association

> How much of Greece's unusual reported strain is associated with materially
> distant, observable conditions?

Answered by one fixed objective-only panel specification (§5). Establishes
**that the divergence is materially grounded**.

**Neither substitutes for the other.** A comparative design can show that
Greece broke away from its counterfactual in 2010; it cannot show the break is
materially grounded merely because wages fell over the same years — that is
coincidence in time, not evidence of association. Conversely the panel model
can establish association while saying nothing about when the divergence began
or whether it is specific to Greece. The first draft of this document collapsed
the two and demoted the panel; that was an overcorrection.

---

## 4. Estimand 1: rebuild the comparative design, and let it fail

Treated as untested. It enters the paper only if it passes every gate below,
all declared before fitting.

**Gates:**

1. **Outcome integrity first (P0).** Reconcile the constructed `DIF + GRT`
   series against Eurostat's official `ilc_sbjp01`. Full pass/fail rule in
   §4a; a design built on a contested outcome is not worth building.
2. **Substantively justified pre-period and treatment date**, chosen for
   coverage and institutional history, not for fit. Declared before any weights
   are computed.
3. **Donor eligibility predefined** before examining fit — including whether
   countries under their own assistance programmes are admissible. Note that
   v1's weights concentrated on Bulgaria, Portugal and Cyprus, two of which were
   themselves in programmes.
4. **Match multiple pre-period outcomes and objective predictors**, rather than
   only two outcome-gap observations. Lagged outcomes are legitimate synthetic-
   control predictors and should not be excluded on principle; the defect in the
   current implementation is that it matches on the gap alone over a two-year
   window, which is what lets a near-exact fit appear without evidential
   content.
5. **Examine donor-weight uniqueness and concentration.** Report the full
   weight vector, not only donors above 1%.
6. **Leave-one-donor-out sensitivity.**
7. **In-space placebos using post/pre RMSPE ratios**, not raw post-period gaps.
8. **Exclude or separately identify placebo units with unacceptable pre-fit**,
   with the threshold declared in advance.
9. **Report the exact permutation denominator and the minimum attainable
   p-value.** With one treated unit and a restricted donor pool, the smallest
   achievable p may well exceed 0.037. That is a property of the design and must
   be stated before running it, not discovered afterwards.
10. **Backdated placebo interventions** at pre-crisis dates.
11. **Augmented synthetic control or synthetic DiD only as pre-specified
    sensitivity**, never as a rescue after the primary fit fails.

**Enforcement checklist, all required before any comparative result is
accepted:**

- Fixed pre-period and donor pool declared before fitting.
- Adequate outcome coverage in **every** pre-period year, not on average.
- Pre-period fit assessed across the **full window**, never two selected years.
  This is the specific failure of the existing implementation.
- No crisis-exposed control quietly treated as an unaffected donor. v1's weights
  concentrated on Bulgaria, Portugal and Cyprus; two were in their own
  programmes.
- **Both** outcomes tested separately: the hardship level (primary) and the
  subjective-minus-AROP gap (secondary). Never interchanged.
- Placebo resolution and the minimum attainable p-value declared in advance.
- Failure reported as failure, with no post-hoc replacement of the design.

### 4.1 P2 pre-registration — declared before fitting

**Committed to version control before the design was run.** The commit that
introduces this section contains no P2 results.

**Windows.**

| | choice |
|---|---|
| Primary pre-period | **2005–2008** — uncontaminated, 25 donors with complete coverage |
| Transition year | **2009** — plotted, excluded from both pre-period fitting and the main post-period estimate |
| Primary post-period | **2010 onward** |
| Predetermined sensitivity | 2005–2009 pre-period, **reported regardless of whether it improves fit** |

**Institutional justification, not fit-based.** Greece was already in recession
through 2009; the October 2009 deficit revision changed expectations before the
formal assistance programme; and including 2009 risks teaching the model part of
the deterioration it exists to estimate. The sovereign-debt crisis and the policy
response become unmistakable from 2010.

**Identification is weak and the safeguards exist because of that.** Four
pre-treatment outcome observations against up to 25 donors is a permissive
environment: better coverage than v1 had does not remove the problem, it makes
the problem tractable enough to be worth guarding. Coverage constraints explain
why v1's two attempts could not work — a six-donor window and a two-observation
window. They do **not** establish that a better-covered design will work.

**Six safeguards, thresholds declared now:**

1. **Constrained weights.** Non-negative, summing to one, as before — plus a
   declared regularisation penalty reported alongside the unpenalised fit.
2. **Pre-fit judged against the placebo distribution**, not Greece's RMSE alone.
   Greece's pre-period RMSE must sit in the better half of the donor placebo
   RMSEs; a good absolute fit that is unremarkable among placebos is not
   evidence.
3. **Covariate balance** on pre-declared predictors as well as the four outcome
   points — AROP, income, unemployment, deprivation, averaged 2005–2008.
4. **Leave-one-donor-out stability**, every donor with non-trivial weight.
5. **No near-perfect fit treated as evidence in itself.** With four points and
   many donors, close fit is attainable by construction; it is a precondition,
   never a result.
6. **Explicit failure conditions**, any one of which fails the design:
   - largest single donor weight > 0.50, or effective number of donors
     (inverse Herfindahl) < 3.0 — excessive concentration;
   - sign flip, or a change in the post-period effect exceeding 50% of its
     magnitude, in any leave-one-donor-out fold;
   - Greece's pre-period RMSE above the median of the placebo RMSEs;
   - post/pre RMSPE ratio not in the top 3 of the placebo distribution.

**Protocol wording, to carry through the documents:**

> The primary design uses 2005–2008 as the uncontaminated pre-crisis period,
> treats 2009 as a transition year, and estimates post-crisis divergence from
> 2010 onward. A 2005–2009 specification is reported as a predetermined
> sensitivity, not selected according to fit.

**Pre-registered failure condition:** if pre-period fit exceeds the declared
threshold, the design fails, is reported as failed, and does not become the
narrative spine. §12 gives the fallback story.

**What this design does and does not remove.** A country reporting premium is
differenced out **only if it is time-invariant**. A crisis-induced change in
response behaviour — people reporting differently *because* of the crisis —
remains possible under any aggregate design and is not resolved here. Say so
in the paper.

---

## 4a. P0: outcome reconciliation, with a stated decision rule

The whole project rests on one constructed series that has never been checked
against Eurostat's own published subjective-poverty indicator. This runs first
and its rule is fixed here.

**Comparative-design outcome, pre-committed.** The existing synthetic control
used `subjective poverty − AROP`; parts of v3's first draft described the
outcome as subjective hardship itself. These are different questions and must
not be interchanged:

- **Primary:** the official/validated subjective-hardship *level*. This is the
  quantity the project is about.
- **Secondary:** the subjective-minus-AROP *gap*. This asks a narrower
  question — how far reported strain runs ahead of the official income measure
  — and is reported as a distinct result, never as a substitute for the primary.

Both are run through every design; where they disagree, that disagreement is
itself reported.

**Reconciliation checks, all four required:**

1. **Definitional equivalence.** Compare population base, household versus
   person weighting, response categories aggregated, and reference period. This
   is a documentation exercise, done before any numbers are compared.
2. **Annual numerical tolerance.** Per country-year absolute difference after
   rounding to the published precision. Declare the tolerance before looking.
3. **Correlation and rank agreement.** Cross-country rank correlation per year,
   and within-Greece time-series correlation across the overlap.
4. **Conclusion sensitivity.** Refit the fixed specification on the official
   series and check whether the central conclusions change.

**Decision rule:**

| Outcome of P0 | Consequence |
|---|---|
| Definitions equivalent, within tolerance, conclusions unchanged | Proceed; report the reconciliation in Methods |
| Definitions equivalent, outside tolerance, conclusions unchanged | Proceed on the official series; report both |
| Definitions equivalent, conclusions change | Official series becomes the primary outcome; all designs rerun on it |
| **Definitions genuinely differ** | **Do not force agreement.** The official series becomes a *separate primary outcome*, reported in parallel throughout, and the constructed series is justified explicitly or dropped |

The last row matters most. If `ilc_sbjp01` measures a different construct, the
right response is two outcomes honestly reported, not a robustness check that
quietly privileges the constructed one.

---

### 4a.1 P0 result and the four rules it locks

**P0 passed on row 1.** Across 432 overlapping country-years (2010–2025), 318
agree exactly, 114 differ by exactly one rounding step, none by more than
0.1 pp. Cross-country Spearman is 1.00 in every year; the within-Greece trend
correlation is 1.000; refitting Model C-LTU on the official series moves the
Greek out-of-sample gap from +3.86 to +3.81 with identical rank and R². Greece
reads 67.2 and ranks 1 of 27 on both. `ilc_sbjp01` **is** the DIF + GRT
aggregation of `ilc_mdes09`, published with age and sex breakdowns instead of
household-composition ones.

Four rules follow and are binding for all V2 work.

**Rule 1 — terminology.** The outcome is the **backward-extended official
subjective-hardship indicator**. The phrase "constructed subjective-poverty
outcome" is retired: it implies an alternative to an official statistic, and
P0 establishes there is no such alternative. This replaces the older language
across V2 documents. V1 is frozen and is not retro-edited.

**Rule 2 — construction.** Use `ilc_sbjp01` **directly from 2010 onward**, and
the validated `DIF + GRT` construction **only before 2010**. Where Eurostat
publishes the indicator, the project uses Eurostat's own figure rather than
recomputing it. The splice point is 2010 and is stated wherever the series
appears.

**Rule 3 — what the validation does and does not cover.** Numerical equivalence
over 2010–2025 validates the **aggregation rule**. It does **not** establish
that every pre-2010 observation is free of national survey breaks. The
aggregation is verified; the earlier vintages' comparability is not, and is a
separate question that the overlap cannot answer.

**Rule 4 — provenance wording.** Never write that Eurostat published
`ilc_sbjp01` before 2010. It does not. Pre-2010 observations are **derived from
official components using a rule validated against the later official series**.
That is a weaker and accurate claim; the stronger one would be false.

**The sentence that should carry through the project:**

> The project uses Eurostat's official subjective-hardship concept. Its pre-2010
> observations are a validated backward extension derived from Eurostat's
> underlying response categories.


---

## 5. Estimand 2: the objective-only model — H6 retained

v2's H6 is **not** made unnecessary by a proximity rule. The distance framework
below decides what may enter; H6 is the test of what happens when it does. Both
are needed.

**Fixed specification, declared before fitting and executable as written:**

```
subjective_hardship ~ severe_mat_soc_deprivation
                    + housing_cost_overburden
                    + ltu_rate
                    + aic_pps_pc               # AIC per capita, PPS -- decided, see below
                    + real_wage_years_below_2008
                    + cum_excess_unemployment
                    + C(time)
```

| Element | Decision |
|---|---|
| Sample period | 2015–2024, the window with complete coverage on all listed predictors |
| Units | EU member-state × year, 27 countries |
| Fixed effects | Year only. **No country fixed effects** — Greece's level is the object of interest and country FE would absorb it |
| Weights | Unweighted. Countries are the units of interest, not a population sample; a population-weighted variant is a declared sensitivity, not the primary |
| Missing data | Complete cases on the full listed set. The resulting n and country count are reported; no imputation |
| Inference | Cluster-robust by country as the point estimate, with **wild cluster bootstrap** as the reported inference given 27 clusters |
| Greece prediction | Leave-Greece-out: coefficients estimated on 26 countries, Greece predicted out of sample |
| **LTU and cumulative exposure together?** | **Yes — both enter simultaneously.** They are separate constructs (current duration vs accumulated history) and v1 tested them jointly without a collinearity failure. Their VIFs and joint stability are reported; if VIF exceeds 10 the joint model is reported alongside single-entry variants rather than silently replaced |

Excluded by construction: arrears, inability to meet an unexpected expense,
financial expectations, and any other Tier 0 predictor.

**Income measure: decided.** `aic_pps_pc` — actual individual consumption per
capita in purchasing power standards.

*Why it represents the intended construct.* The model needs a cross-country
**level** of material living standards. AIC is purchasing-power adjusted, so it
is comparable across countries without an exchange-rate artefact, and it
includes government-provided services such as health and education that
households consume but do not purchase. Eurostat's own guidance recommends it
over GDP for welfare comparison.

*The honest tension.* The survey item asks households about making ends meet
*given total household income*, so a pure household-income measure is
conceptually closer to the question. The available comparable series
(`real_income_idx`, real household disposable income) is an **index against each
country's own 2008**, which measures change from a national base and cannot
serve as a cross-country level. Substituting it would silently change the
construct from "how well off is this country" to "how far has it moved from its
own past". That is a different question, and it is already covered by the
real-wage duration variable.

*Coverage confirmed:* 27 reporters in every year 2015–2024, complete.

*Sensitivity only:* `real_income_idx` (26–27 reporters) and real household
consumption per capita in chain-linked euro, each reported as a declared
sensitivity specification, never as the primary.

**Look-ahead leakage: checked, none present.** `wage_years_below_2008` and
`cum_excess_unemployment` are both running values computed in time order, not a
final duration copied backward. Verified on the panel:

```
wage_years_below_2008   EL: 2015:6  2016:7  ... 2023:14  2024:15
cum_excess_unemployment EL: 2015:76 2016:90 ... 2023:137 2024:138
```

Each row carries only information available through that year, so a model
fitted on the panel is not using the future to predict the past. This check is
recorded here because it is cheap, easy to get wrong when constructing duration
variables, and invisible in a coefficient table.

**Proximity tiers, assigned before fitting:**

- **Tier 0 — proximate or partially overlapping hardship indicators:** arrears,
  unexpected-expense capacity, financial expectations. Not admitted as
  explanatory variables in the fixed specification. They are not the same
  question as making ends meet — being behind on a utility bill is a distinct
  fact — but they overlap enough that treating them as explanations of the
  outcome invites circularity. Reported as *parallel outcomes*: if the same
  crisis history predicts them too, that corroborates; it does not explain.
- **Tier 1 — direct material conditions:** severe material and social
  deprivation, housing-cost overburden. Note that deprivation is itself
  survey-reported and several of its thirteen items are affordability
  judgements, so it is materially proximate too — closer to Tier 0 than its
  "objective" label suggests. State this in the paper rather than relying on
  the tier name.
- **Tier 2 — labour-market and income conditions:** LTU, income, real wages.
- **Tier 3 — history and accumulation:** cumulative excess unemployment, years
  continuously below the 2008 wage level.

**The tier sequence is fixed here, before fitting, and the reported
specification is Tier 1–3 as listed.** The first draft of this document said
"the headline is the most distant tier that still works", which would have
recreated exactly the performance-selected ladder v3 exists to remove. There is
no selection over tiers: the specification is declared, and whatever it returns
is the result.

**Pre-committed conclusion branches.** Written now, before the number exists:

| Objective-only result | Final interpretation |
|---|---|
| Residual ≤ 10 and Greece leaves the extreme-outlier group | Strong objective support |
| Residual 10–20 with stable improvement | Material history explains a meaningful share, not the full difference |
| Residual > 20, or unstable cumulative coefficient | Accumulated exposure becomes conditional support; do **not** claim the paradox is resolved |
| No robust improvement | Lead with measurement and descriptive scarring, not an explanatory model |

**Where the 10 and 20 thresholds come from, and why they are not decisive
alone.** They are anchored to the existing ladder rather than invented: 10
points is roughly the gap Model C reaches *with* the Tier 0 predictors (11.6),
so clearing it without them is a meaningful bar; 20 points sits between Model A
(25.6) and Model C, marking the point at which the objective set has achieved
little beyond the basic specification. Both are conventions, and a residual of
9.9 against 10.1 must not flip a conclusion.

The branch is therefore chosen on **five criteria read together**, declared
here:

1. the out-of-sample residual against the two thresholds above;
2. Greece's **rank** among the 27 — specifically whether it leaves the extreme
   tail, which is more stable than the point estimate;
3. the **prediction interval** around Greece's fitted value, not just the point;
4. **coefficient stability** for `cum_excess_unemployment` across
   leave-one-country-out folds;
5. **improvement relative to the fixed baseline**, and agreement with nested
   validation.

Where the criteria disagree, the more conservative branch is taken and the
disagreement is reported.

This remains the most important gate in the project. Note that the ladder in §2
makes the third or fourth branch the more likely outcome: arrears and
unexpected-expense capacity together move the gap from 35.5 to 11.6, and they
are exactly what this specification removes.

---

## 5a. P4 is withdrawn: its covariates do not exist

The first amendment specified a 2005–2008 → 2015–2018 change design over four
covariates. **It cannot run**, and the project's own coverage record says so.
Reporters per year among the 27 members:

| covariate | 2005 | 2006 | 2007 | 2008 | 2015–2018 |
|---|---|---|---|---|---|
| Long-term unemployment | 2 | 2 | 2 | 2 | 27 |
| Severe material & social deprivation (revised) | 0 | 0 | 0 | 0 | 27 |
| Severe material deprivation (legacy) | 24 | 25 | 26 | 26 | 27 |
| Income (AIC per capita, PPS) | 27 | 27 | 27 | 27 | 27 |
| Real wages, own 2008 = 100 | 27 | 27 | 27 | 27 | 27 |

Two of the four covariates are unavailable in the pre-window: LTU has **two**
reporters, and the revised deprivation series does not begin until 2015. The
legacy deprivation series exists but carries a definitional break at 2021,
so a change computed across it is not a change in one measure.

**P4 is therefore withdrawn as a formal gate.** Specifying a design whose
inputs do not exist would have been the same error as the synthetic control:
a method named in a protocol, run on whatever data could be made to fit, and
then reported as if it had answered the question.

**What replaces it:** nothing new. The time-invariant-premium question is
already answered more credibly by the existing two-way fixed-effects change
analysis and its country-placebo, which use the gap directly and do not require
covariate changes across a window where the covariates are missing.

**What could still be built, outside the gate list:** a change model over a
later window — say 2015–2018 versus 2021–2024 — where all four covariates
exist. That would examine *recovery*, not the crisis break, and must not be
described as a pre-crisis/post-crisis design. It is optional and non-blocking.

**One arithmetic lesson carried forward to P2.** The withdrawn design had a
conclusion rule requiring "top three *and* p < 0.10". With 27 placebo positions
those conflict: rank 1 gives 1/27 = 0.037, rank 2 gives 0.074, rank 3 gives
0.111. "Top three" and "p < 0.10" therefore mean *top two*, stated two ways.
Any permutation-based rule in this project must state **either** a rank
threshold **or** a p threshold, never both, and must be checked against the
attainable grid before it is written down. This applies directly to §4 gate 9.

---

## 5b. P5 additions required by the P3 result

v2 §8.5's list stands. Six additions follow specifically from what P3 returned.

**1. Country fixed-effects coefficient sensitivity.** Country FE do **not**
mechanically absorb `cum_excess_unemployment`: it varies within country over
time. What they do prevent is estimating Greece's own intercept, which is what
the leave-Greece-out prediction needs — so they cannot be used for the headline
residual. They *can* test whether the coefficient survives within-country
variation, and that is a different and worthwhile question.

**2. Within/between (Mundlak) decomposition.** Split the coefficient into its
between-country and within-country parts. This decides whether +0.281 is
essentially a cross-sectional level relationship — countries with more
accumulated exposure report more hardship — or also appears within countries as
exposure accumulates over time. The second is a substantially stronger claim and
the project should not assert it without the decomposition.

**3. Influence diagnostics by country.** DFBETAs and leverage on the fixed P3
specification, reported per country.

**4. Alternative bootstrap weights and seeds.** Rademacher plus at least one
alternative (Mammen or Webb — Webb is the standard recommendation at few
clusters), across multiple seeds, to confirm p = 0.0005 is not an artefact of
one weight scheme or draw.

**5. Full bootstrap reporting.** Repetitions, seed, tail rule (two-sided
absolute-t), and the minimum attainable p-value given the repetition count. With
1999 replications and the +1 correction the floor is 1/2000 = 0.0005 — which is
exactly the reported figure, so it must be stated as "at the resolution floor"
rather than as a precise value.

**6. Reference-implementation check of the restricted bootstrap.** The first
implementation was wrong: it used unrestricted residuals and fitted values, did
not impose the null, and returned p = 0.82 against t = 9.69. The corrected
version must be checked against an established implementation before its numbers
enter any document.

Point 5 deserves emphasis: the reported p = 0.0005 is the smallest value the
procedure can return. It means "no bootstrap draw exceeded the observed t",
not "p equals 0.0005".

---

## 6. Constructs, not variables

v1 screened 29 variables representing far fewer ideas. v3 declares the
constructs and commits to one operationalisation each.

| Construct | Operationalisation | Why this one |
|---|---|---|
| Current material hardship | Severe material and social deprivation | Official, comparable, not a restatement of the outcome |
| Labour-market duration | Long-term unemployment rate | Beat headline unemployment on out-of-sample performance in v1 |
| Accumulated exposure | Cumulative excess unemployment above own 2009 | Survived correction in v1 |
| Loss against own past | **Years continuously below the 2008 real-wage level** | This, not the wage index, is what survived correction in v1 (FDR q = 0.041) |
| Income level | Actual individual consumption per capita, PPS | A purchasing-power-adjusted cross-country level; see §5 for the decision and the household-income tension |

**Five constructs, not four.** The first draft of this document miscounted its
own table.

**Correction to the wage construct.** The first draft listed "real wage index,
own 2008 = 100" as the surviving candidate. That is wrong: the FDR survivor was
`wage_years_below_2008`, the count of *consecutive years* below that level, not
the index itself. The index is a newly chosen descriptive operationalisation
and has never been tested as a predictor. Either use the tested duration
measure — the choice made above — or declare the index as new and untested. Do
not describe it as the survivor.

**Income measure: decided, with the reasoning recorded in §5.** Actual
individual consumption per capita in PPS. The alternative — real household
disposable income — is only published as an index against each country's own
2008 base, which measures a different thing (movement from a national base
rather than a cross-country level) and cannot substitute. It is a declared
sensitivity, not the primary.

**Admission rule for anything not listed.** The first draft proposed a hard
"correlation below 0.8" bar. That is wrong: correlation is not a test of
conceptual redundancy. Two theoretically distinct variables can correlate above
0.8, and two weakly correlated variables can both be products of arbitrary
searching. A candidate is admitted only if it has:

1. a distinct theory,
2. a distinct construct,
3. definition before fitting,
4. adequate coverage and measurement quality,
5. an incremental test run only after the fixed model is estimated, and
6. exploratory status until independently validated.

Measured redundancy against existing constructs is reported as evidence within
that judgement, not as an automatic gate.

---

## 6a. Family D: accumulated multi-domain deterioration (registered, untested)

Registered here before testing. **Exploratory, and it cannot become
confirmatory later** — see the classification note at the end of this section.

**The idea.** Families A–C all measure accumulation on a *single* indicator, or
breadth across indicators at a *point in time*. Neither measures accumulation
across time and domains jointly: how long, and how broadly, a country
deteriorated relative to its own pre-crisis position. That is a distinct
mechanism in the cumulative-disadvantage literature — chronic multi-domain
disadvantage rather than one deep channel — and it is untested here.

**Construction, fixed now.**

1. For each indicator, per country-year, flag whether the country sits in the
   EU's worst quintile that year. Worse-direction declared per indicator, ex
   ante, as in the descriptive composite.
2. Aggregate to a breadth score **weighting domains equally, not indicators**.
   The current descriptive composite weights indicators equally, which lets one
   domain dominate: of its 25 indicators, 11 are Income & output while Housing,
   Prices and Demography have one each — an 11:1 imbalance. Family D computes
   the within-domain share first, then averages across the eight domains.
3. Take the **excess over the country's own 2008–09 breadth baseline**, floored
   at zero, and cumulate. Raw accumulation is not used: it cannot distinguish
   *always at the bottom* from *fell to the bottom*, and ranks Bulgaria and
   Romania above Greece for exactly that reason. The floored-excess form mirrors
   the family-A unemployment construction.

**Variants, declared in advance:**

- **Primary:** objective-only — excludes arrears, unexpected-expense capacity
  and financial expectations, consistent with §5's Tier 0 exclusion.
- **Sensitivity 1:** all-indicator version.
- **Sensitivity 2:** non-labour version (drops the seven labour-market
  indicators), which tests whether the measure is labour-market scarring under
  another name.

**Test sequence, in this order:**

1. **Alone, per indicator.** Accumulated deterioration for every indicator
   separately, tested against **both** outcomes (§4a: the hardship level as
   primary, the subjective-minus-AROP gap as secondary). Correct the whole
   family for multiple testing. Report separately those indicators where Greece
   was *already* in the worst fifth before 2008 and those where it deteriorated
   after — currently 10 and 15 of 25 respectively.
2. **Combined, alone.** Add the composite to a minimal common baseline
   (`AROP + year effects`). Report coefficient, Greece's out-of-sample residual,
   rank, and leave-one-country-out stability.
3. **Combined, in the fixed model.** Add to the pre-specified §5 objective
   specification. Report incremental fit, coefficient stability, VIFs, direct
   comparison against `cum_excess_unemployment`, and whether Greece's residual
   changes materially.
4. **Construction sensitivities.** Worst quintile versus continuous
   standardised distance; alternative pre-crisis baselines; floored excess
   versus net change; balanced-indicator samples; the two variants above.

**Expected redundancy, recorded before testing.** Correlation with
`cum_excess_unemployment` is **+0.83**, and **+0.76** after removing all labour
indicators; with `cum_excess_ltu`, +0.83. It is near-orthogonal to current
conditions (deprivation +0.00, income +0.08). So it is distinct in construction
and co-moving in this sample. **The most likely outcome is that it adds little
conditionally**, exactly as families B and C did at higher correlations. That
expectation is written here so that a null is not later presented as a surprise,
and a small positive is not over-read.

**Decision rules:**

| Outcome | Consequence |
|---|---|
| Survives FDR within family D *and* improves Greece's residual *and* stable under leave-one-out | Exploratory support; requires independent validation before any confirmatory claim |
| Significant but redundant with `cum_excess_unemployment` (VIF high, residual unchanged) | Report as the same finding measured differently, not as an additional channel |
| Null | Report as null; the descriptive result below stands regardless |

**What stands regardless of the model result.** Greece ranks **1st of 27** on
accumulated excess breadth, 10.6× the EU median, with Italy, Spain, Cyprus and
Croatia next — crisis countries, not chronically poor ones. And on 15 of 25
indicators Greece was *not* in the EU's worst fifth before the crisis and is
now. That is descriptive corroboration under the existing taxonomy: evidence
that the crisis produced persistent deterioration across many domains rather
than in unemployment alone. It is reportable even if the variable explains
nothing conditionally, and it must carry the descriptive label if so.

**Classification note, recorded permanently.** The raw accumulated-breadth
measure was built first and ranked Greece third. The excess-over-own-baseline
correction was made **after seeing that result**. The correction has a clear
theoretical basis and copies an existing family-A construction, but it was
still developed after inspecting the data. Family D is therefore exploratory
and stays exploratory: under the standing rule in §8, a discovery first
appearing after family A remains exploratory until it succeeds under a fixed
specification on years, data, or an outcome not used in selection. It must not
be reclassified as confirmatory on the strength of the theory alone.

**Timing.** Not tested until P0 is complete and the fixed P3 model has been
estimated. Family D is an addition to the exploratory record, not a
modification of the pre-specified model.

---

## 7. Power, by design type

The binding constraint is 27 units. It belongs in the first paragraph of the
methods, not in a late robustness section. The calculation differs by design:

- **Panel model (P3):** simulation-based minimum detectable effect using the
  actual cluster structure, not a textbook formula. (The 27-country change
  model referenced in an earlier draft is withdrawn — see §5a — so no MDE is
  required for it.)
- **Comparative-case design:** placebo resolution — the minimum attainable
  p-value given the eligible placebo count — plus detectable post/pre RMSPE
  separation and sensitivity to donor-pool size.

Publish these before any result.

**Three null labels, not one.** v1's "tested and unsupported" conflated
distinct findings:

- **unsupported with adequate sensitivity** — the design could have detected an
  effect of the size that matters, and did not;
- **inconclusive under available power** — it could not;
- **infeasible** — the question cannot be tested credibly with available data.

Several v1 nulls belong in the second category, including direction-of-change
in unemployment at p = 0.065 with the expected sign.

---

## 8. Evidence classification

Keep the existing four-tier procedural taxonomy. Do not migrate to visible new
badges across all documents — that is churn. Instead add three fields as
**columns in the claim matrix**, where the parity auditor can enforce them:

| Field | Values |
|---|---|
| How established | confirmatory / exploratory / post-selection / descriptive |
| Result | supported / unsupported with adequate sensitivity / inconclusive / infeasible |
| Narrative role | primary / supporting / contextual |

These are orthogonal, which is why v2's single six-label list could not work: a
finding can be confirmatory *and* supporting *and* supported.

**Rule for the legacy screening, retained permanently:**

> A discovery first appearing after Family A remains exploratory until it
> succeeds under a fixed specification on years, data, or an outcome not used in
> selection.

v3 stopping future screening does not erase the screening already done.

---

## 9. Microdata: Phase 2, after publication

The first draft of this document proposed submitting a microdata application in
week one and making it a Stage 0 dependency. That is withdrawn.

The revised position:

- Complete and publish the aggregate paper.
- State plainly as unresolved: measurement invariance across countries, literal
  AROPE overlap, household-level anchored poverty.
- Use the publication to seek a recognised institutional collaborator.
- Submit a separate Eurostat proposal for a **predefined extension paper**.

Microdata remains a concrete Phase 2 protocol with the same four priorities as
before — invariance first, since it is the rival hypothesis — but it does not
gate the current project.

---

## 10. Execution order

| Stage | Work | Gate |
|---|---|---|
| **P−1** | **Correct the synthetic-control claims already in the published outputs** | Done: all three documents now report the failed pre-period fit instead of citing it as corroboration |
| **P0** | **Outcome integrity** (§4a, four checks) | §4a decision table; genuinely different definitions make the official series a second primary outcome |
| **P1** | **Descriptive foundation.** AROP threshold, anchored poverty, breadth measure, actual levels | Reportable on its own |
| **P2** | **Comparative trajectory.** Rebuild synthetic control under §4's eleven gates | Allowed to fail; failure is reported |
| **P3** | **Objective-only explanation** (§5; formula fixed, income measure resolved, leakage checked) | §5 branches, on five criteria read together |
| ~~P4~~ | **Withdrawn** (§5a). Required covariates do not exist in the pre-window | — |
| **P3a** | **Family D** (§6a): per-indicator, then combined, then in the fixed model | Exploratory only; §6a decision table |
| **P5** | **Inference and robustness** (§5b) | v2 §8.5 plus the six additions in §5b |
| **P6** | **Publication.** Stop variable discovery; rewrite all outputs around whichever designs survived | — |
| **Phase 2** | Seek Eurostat microdata access | After publication |

Note that P0 precedes everything. The entire project rests on one constructed
outcome series that has never been reconciled against Eurostat's own published
subjective-poverty indicator.

---

## 11. What carries over unchanged

- The four-tier evidence taxonomy.
- The claim matrix, the parity auditor, and the FORBIDDEN rules that fail the
  build when a descriptive finding is restated causally.
- `verify_build`: every published number reproduced from a pipeline output.
- v2 §6.7 metadata requirements — excellent, and would have caught the
  euro-changeover break before it reached a published p-value.
- The statistical appendix as a full audit trail, including nulls.
- The three-document structure with a shared evidence spine.
- v2's stopping rule.

---

## 12. Publication story, both branches

**If the comparative design passes its gates:**

> Greek reported hardship followed its comparative trajectory before the crisis
> and then diverged sharply. The moving AROP threshold concealed part of the
> deterioration. Objective labour-market duration and accumulated exposure
> account for a meaningful portion of the divergence, while proximate
> household-strain indicators describe how that hardship is experienced rather
> than explaining it. A stable reporting premium cannot explain a break that
> begins at the crisis, though a crisis-induced change in response behaviour
> remains unresolved without household microdata.

**If it fails**, it does not become the spine. The paper then leads with:

1. the measurement result — the ruler moved;
2. the breadth of deterioration — 21% to 58% of indicators in the EU's worst
   fifth, first of 27;
3. the fixed objective-only model, reported at whichever §5 branch it lands in;
4. the existing reporting-style robustness battery, including the country
   placebo at rank 1 of 27.

That is a weaker paper than the first branch, but it is publishable and honest,
and every component of it already exists.

---

## 12a. A competing account the design does not exclude: fiscal experience and reported hardship

Registered as a **competing account**, not a channel. It is written here so
that Phase 2 has the prediction in writing before the data arrives.

**The account.** Greece combines relatively heavy taxation of work with limited
family relief and substantial advance-payment obligations on business income,
while banking and shipping operate under exceptional fiscal arrangements created
for other policy reasons. If that asymmetry, together with the externally-set
conditionality of three assistance programmes, changed how Greek households
evaluate and report their circumstances, then part of the outcome is measuring
an institutional judgement rather than a material state.

**Why it is a competing account and not supporting evidence.** The chain ends in
pessimism. The project's central claim is that Greek hardship is materially
grounded rather than a mood, so a mechanism that produces reported hardship via
a changed evaluation of the state **competes with that claim**. Presented as an
additional explanatory channel it would read as reintroducing a psychological
account once the measurable ones were exhausted. It belongs in discussion and
limitations, never in results.

**It is not the account the project already rejected.** Two things are being
kept apart:

- A *time-invariant* reporting premium. Rejected: the widening is crisis-timed,
  and a stable premium cannot produce post-2010 divergence.
- A *crisis-induced change* in response behaviour. **Not rejected**, and §4
  already states that no aggregate design here can difference it out.

This account is the second. It is a specific, motivated version of the open
question, not a new one.

**The existing defence does not exclude it.** The paper's argument against
response-style effects is domain specificity: a *generic* response-style account
predicts uniform extremity across all self-reported wellbeing, and the data show
extremity concentrated in financial measures. "Generic" carries that argument.
A sense of unfair **fiscal** treatment would also be financially specific, so
the domain-specificity evidence rules out general gloom and leaves this account
standing. The discussion must say so rather than let a reader assume otherwise.
Consistent with it: Greece sits in the EU's worst quintile on financial
expectations in all 16 observed years, including pre-crisis, while its
life-satisfaction extremity is milder.

**Evidentiary discipline for the fiscal facts.** Comparable and citable:
tax-to-GDP and tax structure (`gov_10a_taxag`) and the labour tax wedge
(`earn_nt_taxwedge`), both 27 countries 2008–2025, usable as descriptive
comparisons. The sharpest of these is not the headline wedge — single-worker
39.3% against an OECD 35.1% is a 4.2-point gap — but **family relief**: a
one-earner couple with two children faces 37.5% against an OECD 26.2%, fourth
highest, a gap nearly three times larger, and it connects to the project's
existing household-composition and age work.

Not comparable, and therefore case-study background only: the 55% advance
payment on business income (a burden of *timing*, invisible in every standard
tax indicator, and worst when income is unstable), bank deferred-tax credits,
and shipping tonnage taxation. These cannot be country-year predictors and the
causal path from a sectoral tax regime to a household's ability to make ends
meet is too long and too confounded to model.

**Wording that must hold.** Rule asymmetry is documented; **burden** asymmetry
is not, and incidence analysis to establish it is out of scope. The claim is
that Greece taxes work relatively heavily with limited family relief and
front-loaded business obligations, while banking and shipping operate under
exceptional arrangements made for different reasons — not that ordinary Greeks
pay while banks and shipowners do not.

**Testable form, deferred.** If the account is right, **measurement invariance
fails** for the making-ends-meet item: Greek respondents using the response
scale differently after the crisis. That is already priority 1 of the Phase 2
microdata track (§9). This section exists so the prediction is on record
beforehand rather than constructed afterwards to fit whatever the microdata
shows.

**Where it goes in the documents.** Discussion and limitations, beside the
reporting-heterogeneity section. Ervasti, Kouvo and Venetoklis (2019) — already
cited, showing the crisis damaged Greek trust in political and impartial
institutions while leaving interpersonal trust intact — currently does little
work in the paper and would carry real weight here.

---

## 13. Where this proposal is most likely to be wrong

- **The comparative design may fail.** On current evidence that is the more
  likely outcome: the only honest pre-period window available (2003–2008) has
  six countries with complete coverage, and the existing attempt fitted at RMSE
  25.32. P2 may simply not produce a usable counterfactual.
- **H6 may land in the third or fourth branch.** The ladder says arrears and
  unexpected-expense capacity carry most of the explanatory work. If they do,
  the paper's claim narrows substantially — which is the correct outcome, but a
  smaller result than v1 currently implies.
- **P0 may unsettle the outcome variable.** If the constructed series and
  Eurostat's official indicator disagree materially, work built on the
  constructed series needs revisiting. Better to discover that first than last.
