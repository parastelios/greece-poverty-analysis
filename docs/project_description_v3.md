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
4. **Match multiple pre-crisis outcome years and objective predictors**, not
   the outcome gap alone. The current implementation matches on the gap itself,
   which is what allows a two-point window to fit perfectly.
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

## 7. Power, by design type

The binding constraint is 27 units. It belongs in the first paragraph of the
methods, not in a late robustness section. The calculation differs by design:

- **Panel model and the 27-country change model:** simulation-based minimum
  detectable effect using the actual cluster structure, not a textbook formula.
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
| **P5** | **Inference and robustness.** Wild-cluster, influence, alternative outcomes, reporting baseline, dependence | v2 §8.5, unchanged |
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
