# Project Description Version 2

## The Greek Poverty Paradox

### Measurement, material hardship, prolonged exposure, and reported financial strain

**Document status:** Updated analytical and publication protocol based on the completed first phase of the project. This document records established findings, remaining hypotheses, required data, validation standards, and the intended publication story. It is not a retroactive preregistration: completed exploratory work is identified as such, and all new confirmatory checks are separated from it.

---

## 1. Project Goal

The project investigates why Greece reports exceptionally high difficulty making ends meet even when the country's standard official poverty indicators do not always appear equally exceptional.

The central question is:

> Why is reported financial strain in Greece so much higher than AROP, and how much of that gap can be accounted for by poverty measurement, current material conditions, and the accumulated effects of a long economic crisis?

The project has two linked outputs:

1. A scientifically defensible academic analysis of the measurement puzzle and its possible explanations.
2. A clear data-journalism account that lets readers understand the same evidence as a coherent social and economic story.

The intended conclusion is not that Greeks are simply pessimistic, nor that AROP is wrong. The project tests whether Greece's reported hardship becomes intelligible once the poverty line itself, broader material hardship, labor-market duration, and crisis history are considered together.

---

## 2. Core Argument

The project is organized around six linked claims.

### 2.1 AROP creates the initial puzzle

AROP is the main official benchmark in the paper because it measures the share of people below 60% of the current national median equivalised disposable income. Greece is elevated on AROP, but not as uniquely extreme as it is on reported difficulty making ends meet.

This creates the primary gap to explain:

> subjective financial strain minus AROP.

### 2.2 The AROP threshold moved during the crisis

AROP is a relative measure. When median income falls across the country, its poverty threshold also falls. During a broad macroeconomic collapse, an annual AROP rate can therefore remain comparatively stable even while the real living standard represented by the threshold deteriorates substantially.

The project does not argue that AROP is defective. It argues that AROP answers one question well - who is poor relative to the current national median - but is insufficient on its own for another question - how far living standards have deteriorated relative to the pre-crisis period.

### 2.3 AROPE is the official bridge, not a competing headline

AROPE broadens the official poverty concept by adding severe material and social deprivation and very low work intensity. It is introduced immediately after AROP as the official system's own recognition that income poverty alone is too narrow.

AROPE narrows Greece's subjective-hardship gap, but does not close it. Its role in the project is therefore:

> AROP states the measurement problem; AROPE motivates the multidimensional analysis that follows.

The project does not reconstruct AROPE from aggregate components. AROPE is a union measure, and its component overlaps cannot be observed without household-level EU-SILC microdata.

### 2.4 Current hardship dimensions explain much of the gap

Income, deprivation, unemployment, housing-cost pressure, arrears, and inability to meet an unexpected expense account for substantially more of Greece's reported hardship than AROP alone.

However, individual variables do not all help uniformly. Housing-cost overburden alone can make Greece appear more anomalous, while combinations of material-strain indicators explain much more. Arrears and unexpected-expense capacity are powerful but conceptually close to the outcome, so they are treated as proximate hardship indicators rather than deep causal mechanisms.

### 2.5 Duration and accumulated exposure are central

Current-year conditions do not capture how long households and labor markets have been under pressure. Long-term unemployment is more informative than headline unemployment, and cumulative excess unemployment since the pre-crisis baseline provides additional information beyond current conditions.

The accumulated-exposure result is the project's strongest new statistical finding, but its magnitude is reported conservatively after nested selection validation rather than through the most favorable post-selection model.

### 2.6 The cultural explanation is incomplete

Greece already reported high financial strain before the main crisis, so a stable reporting or cultural component cannot be dismissed. But that baseline does not explain the subsequent widening of the subjective-AROP gap, its changing residual over time, or Greece's much more extreme ranking on financial indicators than on general life satisfaction.

The appropriate conclusion is:

> Reporting style may influence Greece's baseline, but it does not adequately explain the crisis-era movement or the financial specificity of the result.

---

## 3. Conceptual Framework

The analysis separates four layers that are often conflated.

### Layer 1: Measurement

- AROP and its moving national threshold
- Real value of the AROP threshold
- Anchored or fixed-threshold poverty
- AROPE and material-deprivation measures

### Layer 2: Current material conditions

- Disposable income
- Current unemployment and long-term unemployment
- Severe material and social deprivation
- Housing-cost overburden
- Arrears
- Inability to meet unexpected expenses
- Prices relative to wages

### Layer 3: Duration and economic history

- Years below the 2008 real-wage level
- Cumulative excess unemployment
- GDP and wage shortfall histories
- Persistence, streaks, rolling averages, and decayed exposure
- Migration and incomplete recovery as contextual scars

### Layer 4: Reporting heterogeneity and interpretation

- Pre-crisis country differences in reporting financial strain
- Financial expectations versus general life satisfaction
- Trust and institutional context where comparable data permit
- Survey wording, response styles, and cross-cultural comparability

These layers are analytically distinct. Measurement explains why official rates may understate the depth of a collapse; current conditions describe present hardship; duration tests whether past exposure still matters; and reporting heterogeneity tests whether some remaining difference reflects how respondents use subjective scales.

---

## 4. Main Research Questions

### RQ1. What exactly is the apparent Greek poverty paradox?

How large is the gap between reported difficulty making ends meet and AROP? How does Greece rank on each measure, and how stable is the gap over time?

### RQ2. How much of the puzzle is created by the moving AROP threshold?

Did the real poverty threshold fall during the crisis? What does an anchored 2008 threshold show that the annual relative measure does not?

### RQ3. How far does AROPE bridge the gap?

Does the broader official indicator move closer to reported hardship? What remains unexplained after deprivation and low work intensity are acknowledged?

### RQ4. Which current material conditions account for the remaining gap?

How much do income, deprivation, unemployment, housing costs, arrears, and financial buffers contribute alone and in disciplined combinations?

### RQ5. Does duration explain more than current-year conditions?

Do long-term unemployment, cumulative excess unemployment, wage-loss duration, or other history-sensitive measures explain Greece better than current snapshots?

### RQ6. Could the result mainly reflect Greek reporting culture?

Was Greece already unusually high before the crisis? Is the post-crisis widening larger than in other countries? Does the same extremity appear in non-financial subjective outcomes?

### RQ7. Did recovery reach all households and generations?

How do wages, prices, housing burden, age, household type, migration, and labor-market status complicate the aggregate recovery narrative?

### RQ8. Do the findings generalize beyond the estimation sample?

Do the main specifications survive leave-one-country-out, nested selection, blocked time validation, alternative outcome definitions, and stricter inference?

---

## 5. Outcomes, Units, and Analytical Windows

### 5.1 Primary outcome

The primary subjective-hardship outcome is the share reporting difficulty or great difficulty making ends meet from Eurostat EU-SILC (`ilc_mdes09`, categories `DIF + GRT`).

This choice must be stated consistently in every document and chart. It is not a diagnosis of poverty and should not be called an official poverty rate.

### 5.2 Alternative outcome definitions to validate

The next validation round should test whether the central result depends on the selected subjective-outcome threshold:

- `GRT` only: great difficulty making ends meet
- `DIF + GRT`: primary binary definition
- An ordered or severity-weighted score using all response categories, where aggregate construction is defensible
- Eurostat's published population-weighted subjective-poverty series (`ilc_sbjp01`) for its available period

Conclusions should distinguish findings that survive all definitions from those specific to the primary outcome.

### 5.3 Units of analysis

- Primary panel: EU member-state by year
- Greece time series: descriptive and within-country robustness
- Out-of-sample country evaluation: leave Greece out of model fitting
- Cross-country validation: leave one country out and nested selection
- Future extension: household-level EU-SILC microdata

### 5.4 Time windows

- Long descriptive series: use the maximum definitionally comparable period for each variable
- Primary panel model window: 2015-2024, held constant across model comparisons
- 2025 data: descriptive update only unless all required model variables are complete and comparable
- Pre/post cultural check: pre-crisis 2003-2008 versus post-crisis periods, with definitions documented

No table should mix a 2025 raw gap with a model residual estimated on 2015-2024 without a prominent warning. The model ladder is a narrative sequence, not a formal additive decomposition.

---

## 6. Data Requirements

### 6.1 Poverty and subjective hardship

| Concept | Preferred source | Required fields |
|---|---|---|
| Difficulty making ends meet | Eurostat `ilc_mdes09` | country, year, response category, population share |
| Official subjective-poverty indicator | Eurostat `ilc_sbjp01` | country, year, unit, population group |
| AROP rate | Eurostat `ilc_li02` | post-transfer rate, total population, median-based statistic |
| AROP threshold | Eurostat `ilc_li01` | nominal threshold, household type, national currency/euro |
| AROPE | Eurostat `ilc_peps01` / revised series | country, year, age, sex where available |
| Severe deprivation | Eurostat deprivation series | current and legacy definitions, break metadata |
| Anchored poverty | Derived from threshold and HICP; microdata preferred | fixed baseline and real threshold |

### 6.2 Labor market

- Headline unemployment rate
- Long-term unemployment rate
- Youth unemployment
- Employment status and in-work poverty
- Actual weekly hours worked
- Full-time, employee, and self-employed hours
- Compensation per employee and hourly compensation in PPS
- Cumulative excess unemployment relative to the earliest common reliable baseline

### 6.3 Income, wages, and output

- Real household income per capita
- Nominal and real compensation per employee
- PPS income per capita
- Real GDP per capita
- Distance from 2008 level and from own historical peak
- Household saving rate
- Household debt-to-income where coverage is sufficient
- Welfare-transfer effectiveness, defined transparently as AROP before minus after transfers

### 6.4 Prices and living costs

- HICP overall and essential categories
- Cross-country price-level indices
- Food and beverages
- Housing and utilities
- Transport
- Communications
- Wage-adjusted price-pressure indicators

Raw price comparisons must not be interpreted as affordability without a wage or income denominator.

### 6.5 Housing and household strain

- Housing-cost overburden
- Arrears on mortgage, rent, utilities, or hire purchase
- Inability to meet an unexpected expense
- Tenure distribution
- Housing-cost overburden by tenure
- Household type and age where cross-tabs exist

`Arrears` must always be defined in the glossary and at first substantive use.

### 6.6 Demography, migration, and institutions

- Emigration and return migration of own nationals
- Age and skill profile where comparable data exist
- AROPE and AROP by age and household type
- Trust in political institutions, state, and EU where repeated comparable series exist
- Financial expectations and life satisfaction

Migration and trust remain contextual unless they pass the same data-coverage and model-validation standards as central predictors.

### 6.7 Metadata requirements

Every analytical variable must record:

- Eurostat dataset code
- exact filters and units
- seasonal adjustment
- age and population scope
- source versus income year convention
- definition breaks
- earliest and latest reliable year
- country coverage by year
- EU comparator basis: population-weighted EU aggregate or unweighted member-state mean
- archived raw-file checksum or equivalent provenance record

---

## 7. Hypotheses and Analysis Plan

## H1. A falling relative threshold hid part of the crisis deterioration

**Hypothesis:** Greece's annual AROP rate understates the deterioration in absolute living standards because the real AROP threshold fell with national median income.

**Analysis:**

1. Plot AROP and the real AROP threshold over time.
2. Index the threshold to 2008 in real terms.
3. Estimate anchored poverty using the fixed 2008 threshold.
4. Compare annual AROP, anchored poverty, AROPE, and subjective hardship.
5. Compare Greece with crisis-hit and non-crisis EU countries where comparable threshold data exist.

**Robustness:** alternative HICP base, household type, baseline year, and exclusion of years surrounding definition breaks.

**Current status:** Supported descriptively. Exact person-level reconstruction remains a microdata task.

**Publication role:** Core measurement finding.

---

## H2. AROPE narrows but does not close the subjective-hardship gap

**Hypothesis:** AROPE is closer to subjective hardship than AROP because it adds deprivation and work intensity, but Greece remains unusually high relative to AROPE.

**Analysis:**

1. Present AROP first and AROPE immediately afterward.
2. Compare Greece's raw subjective-minus-AROP and subjective-minus-AROPE gaps on the same year and population basis.
3. Show the two benchmarks in the same visual sequence, with AROPE visually secondary.
4. Use the remaining AROPE gap to motivate the decomposed multivariable analysis.

**Limitation:** Published marginal component rates cannot reconstruct AROPE's union because household overlaps are unknown.

**Current status:** Supported.

**Publication role:** Official bridge between Parts I and II.

---

## H3. Current material conditions explain more than AROP alone

**Hypothesis:** Income, deprivation, labor-market conditions, housing pressure, arrears, and financial buffers collectively reduce Greece's out-of-sample residual.

**Analysis:**

- Model A: AROP plus basic economic conditions
- Model B: housing-focused extension
- Model C: decomposed multidimensional hardship
- Stage 1: each candidate tested against a common AROP-plus-year-effects baseline
- Stage 2: a theoretically ordered model sequence

**Required reporting:**

- In-sample fit
- Greece leave-out residual
- Greece rank among all countries
- coefficient uncertainty
- coverage and sample size
- conceptual proximity to the outcome

**Interpretive rule:** Arrears and unexpected-expense capacity may be excellent concurrent markers of hardship, but should not be described as deep causal explanations.

**Current status:** Supported as association. Individual additions are heterogeneous; the combination matters.

**Publication role:** Core multidimensional finding.

---

## H4. Long-term unemployment is more informative than headline unemployment

**Hypothesis:** The duration of unemployment captures the Greek labor-market scar more directly than the current headline unemployment rate.

**Analysis:**

1. Compare headline unemployment and LTU in otherwise matched specifications.
2. Test replacement and additive versions.
3. Diagnose multicollinearity and coefficient stability.
4. Run leave-one-country-out stability tests.
5. Plot actual Greece and EU LTU levels so the model variable remains interpretable.

**Decision rule:** Prefer LTU only if it improves out-of-sample performance, remains stable, and avoids the unstable coefficient pattern produced by including highly collinear labor-market measures together.

**Current status:** Supported. LTU is the preferred current labor-market specification.

**Publication role:** Core current-condition finding.

---

## H5. Accumulated labor-market exposure explains information missed by current snapshots

**Hypothesis:** Cumulative excess unemployment since the common pre-crisis baseline captures prolonged exposure that is not contained in current LTU or current unemployment alone.

**Primary construction:**

> cumulative excess unemployment = sum of each year's unemployment rate above the country's 2009 baseline, floored at zero where specified.

**Analysis:**

1. Compare current-year, duration, cumulative, rolling, and decayed versions.
2. Test each candidate one at a time against Model C-LTU.
3. Apply FDR correction across the candidate family.
4. Repeat variable selection inside every leave-one-country-out fold.
5. Report the conservative nested-selection Greece estimate as the headline result.
6. Plot the full 27-country distribution, EU median, IQR, and Greece trajectory.

**Existing result:** The cumulative/duration family is robust, with cumulative excess unemployment selected in most nested folds. The conservative nested result leaves Greece modestly above prediction rather than producing the more favorable negative residual from the post-selection richest model.

**Interpretive rule:** The family is better identified than a uniquely privileged formula. Do not describe the post-selection negative residual as proof that Greeks are optimistic.

**Current status:** Strong robust support, subject to the remaining out-of-time and alternative-outcome checks.

**Publication role:** Central new statistical result.

---

## H6. The central result survives a strict objective-only specification

**Hypothesis:** LTU and accumulated labor-market exposure remain informative when predictors conceptually close to the subjective outcome are excluded.

**Why this is necessary:** The current strongest models include arrears and inability to meet unexpected expenses. These are valid hardship measures but overlap conceptually with difficulty making ends meet.

**Planned analysis:**

1. Predefine an objective-only predictor set before fitting:
   - AROP
   - real income or wages
   - LTU
   - housing-cost overburden
   - cumulative excess unemployment
   - year effects
2. Exclude arrears, unexpected-expense capacity, financial expectations, and all directly subjective predictors.
3. Compare residual, rank, fit, and stability with Model C-LTU and the nested cumulative specification.
4. Repeat leave-one-country-out and nested validation.

**Decision rule:** If cumulative exposure remains stable, the claim can be framed as structural. If it weakens sharply, the report must state that much of the explanatory power comes from proximate hardship indicators.

**Current status:** Highest-priority uncompleted validation.

**Publication role:** Publication gate.

---

## H7. A stable Greek reporting premium cannot explain the post-crisis change

**Hypothesis:** Greece may have a high pre-crisis baseline in reported hardship, but the crisis created an additional widening not explained by a stable country-specific reporting style.

**Analysis already completed:**

- Pre-crisis cross-country rank
- Pre/post change in the subjective-minus-AROP gap
- Country and year fixed-effects interaction design
- Residual trend under current-condition models
- Comparison with financial expectations and general life satisfaction
- Country-placebo/randomization checks where appropriate

**Additional planned check:** Include a pre-crisis reporting-baseline measure in a prediction model and test whether cumulative exposure still contributes.

**Interpretive rule:** Reject a culture-only explanation, not all cultural or reporting effects.

**Current status:** Culture-only account not supported; partial baseline heterogeneity remains plausible.

**Publication role:** Robustness and interpretation section, placed after material evidence.

---

## H8. The main finding generalizes over time, not only across countries

**Hypothesis:** A model trained on earlier years should retain useful predictive performance in later years.

**Planned analysis:**

1. Expanding-window validation where feasible.
2. Blocked train/test splits, for example training through 2019 and testing 2020-2024.
3. Pandemic sensitivity excluding 2020-2021.
4. Compare current-condition and accumulated-exposure models using the same folds.
5. Report prediction intervals and year-specific residuals.

**Constraint:** The panel is short and candidate coverage differs. This test should remain simple and pre-specified.

**Current status:** Not yet completed.

**Publication role:** Publication gate for predictive language.

---

## H9. Results do not depend on one subjective-outcome cutoff

**Hypothesis:** The main findings remain directionally consistent under alternative definitions of reported financial strain.

**Planned analysis:**

1. Refit the fixed model using `GRT` only.
2. Refit using the primary `DIF + GRT` outcome.
3. Construct and test an all-category severity score if weighting can be justified without household microdata.
4. Compare with the official Eurostat subjective-poverty series for its available years.
5. Apply the same country and time validation to each outcome.

**Decision rule:** Claims surviving all reasonable definitions can be presented as robust. Divergent results must be tied to the specific severity threshold.

**Current status:** Not yet completed.

**Publication role:** Publication gate.

---

## H10. Recovery was incomplete and uneven across dimensions and groups

**Hypothesis:** Aggregate recovery indicators conceal persistent losses in wages, labor-market history, affordability, housing security, and some demographic groups.

**Analysis:**

- GDP relative to the 2008 level and own peak
- Real wages relative to 2008
- Wage-adjusted price pressure
- Housing burden by tenure
- Migration and return migration
- AROPE/AROP by age, sex, and household type
- Shift-share decomposition of recent national changes
- Work effort versus hourly compensation

**Interpretive rule:** These are not all independent scorecard predictors. Many provide descriptive depth, distributional context, or external corroboration.

**Current status:** Strong descriptive evidence; model status varies by indicator.

**Publication role:** Human consequences and recovery section.

---

## H11. Plausible alternative explanations should be reported even when unsupported

Candidates include:

- Income inequality
- Youth unemployment after LTU is included
- Cumulative GDP shortfall
- Cumulative AROP-threshold loss
- Welfare-transfer effectiveness
- Household debt
- Saving rate
- Work-effort squeeze
- Migration
- Trust
- Broad indicator-count or persistence composites

**Analysis standard:** Each candidate receives a feasibility check, descriptive result, appropriate correlation/model test, multiple-testing status where part of a family, and a clear evidentiary label.

**Current status:** Several are null, redundant, contextual, or limited by coverage. These outcomes are informative and should not be hidden.

**Publication role:** Compact ruled-out/checked section and full appendix.

---

## 8. Statistical Design

### 8.1 Descriptive analysis

- Plot actual levels, not only standardized model inputs.
- Show Greece, EU aggregate or median, and the full country distribution where useful.
- Label the EU comparator basis.
- Mark model windows and definition breaks.
- Show levels and cumulative constructions separately.

### 8.2 Panel models

- Country-year panel
- Year fixed effects in the primary cross-country specifications
- Country-clustered standard errors as the baseline
- Consistent samples for model-to-model comparisons
- Greece excluded when producing the principal Greece prediction

### 8.3 Validation

- Leave-Greece-out prediction
- Leave-one-country-out coefficient and rank stability
- Nested candidate selection within each fold
- Blocked or expanding-window validation
- Pandemic and influential-country sensitivity
- Alternative outcome definitions

### 8.4 Multiple testing

Benjamini-Hochberg FDR correction is applied within clearly defined test families, including:

- Correlation-screen columns
- Cumulative/duration candidate families
- Work-effort candidate families
- Sensitivity and acceleration families where multiple hypotheses are tested

No claim should imply that FDR correction across one family corrects the entire exploratory history of the project. Sequential model development remains exploratory unless independently validated.

### 8.5 Small-sample and influence checks still required

- Wild-cluster bootstrap or another small-cluster robustness method
- Leave-one-country-out influence diagnostics
- DFBETAs or equivalent coefficient influence measures
- Residual and leverage inspection
- Bounded-outcome sensitivity, such as fractional response or transformed-outcome checks where feasible
- Serial and cross-sectional dependence diagnostics

These checks should focus on the fixed final specifications, not reopen candidate screening.

### 8.6 Residual interpretation

A Greece residual is an out-of-sample difference between reported and model-predicted hardship under a specific specification. It is not a causal effect and not a literal count of percentage points mechanically explained by each variable.

The gap ladder is a communication device. Raw AROP/AROPE differences and regression residuals have different estimands and must be labeled as such.

---

## 9. Fixed Final Validation Round

Before publication, the project should complete the following checks in this order.

### P0. Objective-only model

Test whether LTU and cumulative exposure survive without proximate subjective-hardship variables.

### P1. Out-of-time validation

Use blocked or expanding-window splits and a pandemic sensitivity test.

### P2. Alternative subjective outcomes

Test great difficulty only, the primary binary outcome, and at least one broader severity representation.

### P3. Baseline-adjusted reporting model

Control for pre-crisis reporting levels or estimate changes relative to each country's baseline, then reassess accumulated exposure.

### P4. Inference and influence audit

Run small-cluster, leverage, influence, bounded-outcome, and dependence checks on the fixed final models.

### Stopping rule

After P0-P4, do not add further candidate variables unless a reviewer identifies a specific omitted-variable concern supported by a clear theory and comparable data. The next step should be manuscript consolidation, not continued variable hunting.

---

## 10. Household-Microdata Extension

The aggregate panel cannot answer several important questions. A future EU-SILC microdata phase should examine:

1. Exact anchored poverty at household level.
2. Overlap among AROP, deprivation, and low work intensity, allowing literal AROPE reconstruction.
3. Ordered models of making-ends-meet responses.
4. Household unemployment histories and duration.
5. Wealth, liquid savings, debt service, and housing costs.
6. Age, sex, household type, tenure, and labor-status interactions.
7. Measurement invariance and country-specific response thresholds.
8. Repeated cross-sections or longitudinal components where access permits.
9. Distributional effects hidden by national averages.

This would move the project from country-level association toward household-level mechanisms. It would not automatically establish causality, but it would substantially reduce ecological-inference and overlap limitations.

---

## 11. Evidence Hierarchy

Every result should carry one of six labels.

### Core finding

Central to the argument, supported by direct analysis and the main validation battery.

### Robust support

Survives defined robustness checks but is secondary to the core argument.

### Descriptive context

Important for interpreting lived conditions, but not an independently identified model contribution.

### Exploratory lead

Plausible and tested, but limited by sample size, model dependence, measurement, or incomplete validation.

### Tested and unsupported

A plausible hypothesis that did not receive adequate empirical support in the current data.

### Checked but infeasible

A relevant question that cannot be tested credibly with available comparable data.

This hierarchy must remain consistent across the technical report, academic paper, narrative companion, presentation, statistical appendix, and project documentation.

---

## 12. Publication Story

All public documents should contain approximately the same evidence, but use different levels of technical detail. Their shared spine should be:

### Opening: the puzzle

Greeks report exceptional difficulty making ends meet, while AROP appears elevated but less exceptional.

### Part I: the ruler moved

AROP is relative to the current national median. During Greece's collapse, the real threshold fell. The indicator remained useful for relative poverty but incomplete as a standalone crisis measure.

### The official bridge

AROPE acknowledges that poverty is multidimensional. It moves closer to what households report but still leaves a large gap.

### Part II: test the missing dimensions

Instead of reconstructing AROPE, test income, deprivation, work, housing, arrears, and financial buffers separately. Show that single-variable stories often fail and combinations matter.

### The central test: duration

Current unemployment is not enough. Long-term unemployment matters more, and accumulated labor-market exposure carries additional information about how long the crisis remained embedded in households and institutions.

### The stricter result

Nested validation produces a smaller and more conservative improvement than the richest post-selection model. Lead with the conservative result.

### Human consequences

Connect the model to actual levels: wages, prices, housing burden, inability to meet expenses, migration, long working hours with low hourly compensation, and unequal recovery by age and household type.

### Discussion

The remaining Greek difference is not well described as a mystery of national mood. The evidence supports a combination of moving measurement, multidimensional current hardship, and prolonged exposure, while leaving room for baseline reporting differences and unobserved household factors.

### General recommendation

In macroeconomic crises, AROP should not be published or interpreted alone. It should be accompanied by:

- the real poverty threshold
- an anchored poverty measure
- AROPE and deprivation
- current material-strain indicators
- duration or cumulative-exposure indicators where justified

---

## 13. Document Roles

### Technical report

The complete evidence record. It should include all central results, actual levels, model ladders, caveats, null findings, and collapsible technical detail, ordered around the shared story.

### Academic paper

The defensible research argument. It should prioritize hypotheses, estimands, identification limits, robustness, literature, and a restrained set of central tables and figures. Large batteries belong in an appendix.

### Narrative companion

The same substantive findings written as a long-form data-journalism story. Methods notes preserve credibility, but the reader encounters people, time, and consequences before model mechanics.

### Statistical appendix

The complete visual and numerical audit trail: actual levels, distributions, cumulative measures, candidate screens, residuals, influence, collinearity, validation, and glossary.

### Presentation and podcast

Short-form versions of the same hierarchy. They must not introduce stronger claims than the written research.

---

## 14. Required Outputs

### Data and reproducibility

- Raw-data fetch scripts with exact filters
- Archived input snapshot and provenance record
- Processed country-year panels
- One-command offline verification
- One-command clean re-acquisition and rebuild
- Claim matrix linking published numbers to generated outputs

### Analysis outputs

- Primary and alternative outcome panels
- AROP/AROPE/anchored comparisons
- Current-condition model table
- LTU replacement battery
- Cumulative/duration family and FDR table
- Nested validation outputs
- Objective-only model battery
- Time-validation outputs
- Baseline-reporting adjustment
- Influence and inference diagnostics
- Actual-level and full-distribution chart pack

### Publication outputs

- Technical report
- Academic working paper
- Narrative companion
- Statistical appendix
- Slide deck
- Two-person debate/podcast outline
- Updated methodology and data documentation

---

## 15. Limitations

### 15.1 Addressable in the current project

- AROP/AROPE narrative confusion
- Inconsistent outcome naming
- Incomplete visibility of actual variable levels
- Cumulative-measure construction choices
- Multiple-testing documentation
- Model-specification dependence
- Short-window disclosure
- Proximate-outcome predictor labeling
- Reporting-culture baseline adjustment
- Out-of-time validation
- Alternative outcome definitions
- Influence and small-cluster diagnostics

### 15.2 Partly addressable

- Household balance sheets, through aggregate proxies only
- Subjective response-style differences, through baseline and cross-indicator checks
- Greek crisis specificity, through comparative cases
- Migration and trust, through bounded contextual analysis
- Policy interpretation, through literature triangulation rather than causal attribution

### 15.3 Structural without new data

- Ecological inference from country-year aggregates
- Literal AROPE reconstruction from marginal rates
- Household-level overlap among hardship dimensions
- Individual unemployment histories
- Wealth and liquid-asset depletion
- Measurement invariance across languages and cultures
- Strong causal identification
- Full separation of age, household, tenure, and labor-status interactions

These limitations should appear in the abstract or executive limits note, the Methods section, and the final Discussion - not only in an appendix.

---

## 16. Final Publication Standard

The project will be ready for external publication when:

1. P0-P4 are complete and reproducible.
2. The conservative nested result remains the headline estimate.
3. All three principal documents share the same evidence and hierarchy.
4. Actual levels accompany model variables central to the story.
5. Null and infeasible analyses are documented.
6. The statistical appendix contains the full audit trail.
7. Causal language has been removed unless supported by a causal design.
8. Every headline number is linked to a verified pipeline output.

The defensible final claim is:

> Greece's exceptional reported financial strain is not adequately explained by AROP alone or by a stable national pessimism premium. A falling relative poverty threshold, multidimensional current hardship, long-term unemployment, and prolonged labor-market exposure together make the Greek result substantially less anomalous. The evidence is associational and aggregate, but it supports reading Greece's subjective hardship as materially grounded rather than dismissing it as mood.

