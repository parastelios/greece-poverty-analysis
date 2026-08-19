# Project Description

This is the original project brief in full, kept verbatim for reference. It's
treated as a **north-star spec, not an immediate mandate** — the current
report is Version 1, built around the two research questions actually posed
in `output/report.html`. Several items named below (migration/brain drain,
trust in institutions, real wages, housing tenure, spatial robustness) are
intentionally out of scope for V1 and tracked as future work; see
`publication_strategy.md` for what's been done and the project's task list
for what's planned next.

---

# Project Description: Poverty in Greece — Measured Poverty, Subjective Hardship, and the Greek Poverty Paradox

## Project Goal

This project investigates why Greek households report exceptionally high difficulty making ends meet, even though Greece's standard relative-income poverty rate is elevated but not uniquely extreme by EU standards.

The central question is:

**To what extent does Greece's unusually high subjective poverty reflect measurable, long-term deterioration in living standards, financial security, and expectations, rather than merely differences in mood, perception, or pessimism?**

The project starts from official data and avoids assuming either that subjective poverty is misleading or that it automatically reflects objective impoverishment. The aim is to understand what different poverty measures capture, why they diverge, and whether Greeks have measurable reasons to feel poorer and more financially insecure than the standard AROP rate suggests.

The project should produce both:

1. A rigorous analytical backbone suitable for an academic-style working paper.
2. A readable long-form report suitable for serious data journalism: credible, careful, evidence-based, but structured as a clear story rather than only a sequence of data outputs.

## Background

Eurostat publishes a subjective poverty indicator based on EU-SILC survey responses to the question of how easily households are able to make ends meet, given their total household income.

Households reporting that they make ends meet:

- "with difficulty"
- or "with great difficulty"

are classified here as experiencing subjective poverty.

This differs from the standard at-risk-of-poverty rate, or **AROP**, which is a relative-income measure. A person is considered at risk of poverty when their equivalised disposable income is below 60% of the national median.

This distinction matters because a country can experience broad deterioration in living standards while its relative poverty rate changes only moderately. If incomes fall across much of the distribution, the national median also falls, so the poverty threshold falls too. The official poverty "ruler" shrinks at the same time as household income.

Greece is a particularly important case because:

- subjective poverty is far above the EU average;
- Greece has ranked first in the EU for subjective poverty for more than a decade;
- AROP is high but not uniquely extreme;
- Greek real incomes and living standards fell sharply during the debt crisis;
- Greece appears not to have fully recovered its pre-crisis living standard;
- households also face high housing costs, arrears, low savings, and pessimistic expectations.

The project therefore asks whether the Greek poverty paradox is partly a measurement problem, partly a real material-hardship problem, and partly a longer-term scarring and expectations problem.

## Main Research Questions

The project should answer the following questions:

1. How has subjective poverty in Greece evolved from the earliest comparable EU-SILC data to the latest available year?

2. How has Greece's AROP rate evolved over the same period?

3. How do subjective poverty and AROP compare with EU averages each year?

4. What has been Greece's EU ranking each year for:
   - AROP;
   - subjective poverty;
   - AROPE, where relevant?

5. Did subjective poverty increase during periods of measurable economic deterioration, especially during the sovereign-debt crisis?

6. Did subjective poverty decline during recovery, or did it remain persistently elevated?

7. Does subjective poverty move together with economic variables such as:
   - real household disposable income;
   - real GDP per capita;
   - real wages, if available;
   - unemployment;
   - long-term or youth unemployment;
   - employment;
   - purchasing power;
   - material and social deprivation;
   - severe material deprivation;
   - housing-cost overburden;
   - arrears;
   - inability to face unexpected expenses;
   - inflation;
   - household consumption;
   - household saving rate?

8. How strong are the statistical relationships between subjective poverty and these variables?

9. Does AROP understate broad deterioration in living standards because it is based on a moving national median threshold?

10. What happens if poverty is measured against a fixed pre-crisis benchmark instead of a moving relative threshold?

11. Does AROPE, the broader poverty-or-social-exclusion indicator, track subjective poverty better than AROP?

12. Is Greece still an outlier after accounting for income, unemployment, material hardship, housing pressure, and cash-flow strain?

13. How much of Greece's subjective-poverty gap is explained by each additional group of variables?

14. Does Greece remain an outlier in out-of-sample tests, where the model is trained only on other EU countries?

15. Is Greece's current hardship better understood as a persistent level effect or as a normal reaction to year-to-year economic changes?

16. How does Greece's recovery path compare with other EU countries after the crisis?

17. How many years has Greece remained below its own pre-crisis peak, and how unusual is that compared with the rest of the EU?

18. Do emigration, brain drain, and the non-return of skilled workers help explain longer-term scarring, pessimism, or weakened expectations?

19. Do trust in national institutions, trust in the state, or trust in the EU help explain part of the remaining subjective-poverty gap?

20. What remains unexplained after all measurable economic, social, and institutional variables are considered?

## Core Dataset

Create a cleaned annual dataset covering approximately 2003 or 2004 to the latest available year, subject to Eurostat data availability and comparability.

The core Greece–EU table should include:

| Variable | Description |
|---|---|
| Year | EU-SILC survey year |
| Greece AROP | At-risk-of-poverty rate in Greece |
| EU AROP | Official Eurostat EU aggregate AROP |
| Greece AROP rank | Greece's rank among EU countries, highest poverty = rank 1 |
| Countries in AROP ranking | Number of countries with available observations |
| Greece subjective poverty | Share reporting difficulty or great difficulty making ends meet |
| EU subjective poverty | Corresponding official or reconstructed EU aggregate |
| Greece subjective rank | Greece's rank among available EU countries |
| Countries in subjective ranking | Number of countries with available observations |
| Greece AROPE | At risk of poverty or social exclusion |
| EU AROPE | EU aggregate AROPE |
| Greece AROPE rank | Greece's rank among EU countries |
| Greece–EU AROP gap | Difference in percentage points |
| Greece–EU subjective poverty gap | Difference in percentage points |
| Greece–EU AROPE gap | Difference in percentage points |

The EU aggregate should use official Eurostat population-weighted EU aggregates where available, not simple averages of national percentages.

Country rankings should use EU membership as of each survey year and explicitly record the number of countries included, because EU membership and data availability change over time.

## Additional Economic and Social Variables

The expanded dataset should include, where possible:

- real household disposable income;
- real GDP per capita;
- real wages or compensation measures;
- unemployment rate;
- youth unemployment;
- long-term unemployment;
- employment rate;
- purchasing-power-adjusted income;
- household consumption;
- minimum wage;
- HICP inflation;
- food inflation;
- housing and energy inflation;
- housing-cost overburden;
- arrears;
- inability to face unexpected expenses;
- inability to keep home warm;
- severe material deprivation;
- severe material and social deprivation;
- AROPE;
- household saving rate;
- household debt-to-income;
- poverty-reducing effect of social transfers;
- financial expectations;
- trust in national government or parliament;
- trust in the EU;
- net migration;
- emigration by age and education or skill level;
- return migration where available.

Not every variable needs to become part of the main model. Variables should be classified as:

- core explanatory variables;
- robustness checks;
- exploratory extensions;
- unavailable or unsuitable, with explanation.

## Time-Series Comparability

Special attention must be paid to methodological consistency.

The analysis should verify and document:

- the earliest comparable year for Greek EU-SILC data;
- whether "ability to make ends meet" categories are stable over time;
- whether older subjective-poverty observations need reconstruction from "difficulty" + "great difficulty";
- whether subjective-poverty series are household-weighted or population-weighted;
- changes in EU composition over time;
- changes in Eurostat aggregate codes;
- breaks in deprivation indicators;
- revisions to Eurostat datasets;
- whether AROP survey-year values refer to income from the previous calendar year;
- whether pre-EU-SILC data, such as ECHP, are comparable enough to include;
- whether AROPE definitions changed over time;
- which findings depend on approximated or reconstructed measures.

The report should clearly distinguish between:

- official Eurostat measures;
- project-reconstructed measures;
- approximated measures;
- exploratory indicators.

## Main Analysis Plan

### 1. Descriptive Time-Series Analysis

Plot Greece and the EU average for:

- subjective poverty;
- AROP;
- AROPE;
- selected hardship indicators.

Identify major periods:

- pre-crisis baseline;
- sovereign-debt crisis;
- post-crisis recovery;
- COVID period;
- inflation and cost-of-living period;
- latest available year.

The analysis should show whether subjective poverty responds visibly to economic shocks, and whether it remains elevated even after partial recovery.

### 2. Greece–EU Divergence

Calculate annual Greece-minus-EU gaps for:

- AROP;
- subjective poverty;
- AROPE;
- selected hardship indicators.

This should show whether Greece's subjective-poverty gap is persistent, widening, narrowing, or structurally different from the AROP gap.

### 3. Ranking Analysis

Track Greece's annual EU ranking for:

- AROP;
- subjective poverty;
- AROPE;
- key hardship indicators such as housing overburden, arrears, and inability to face unexpected expenses.

The report should clearly distinguish between:

- "Greece has one of the highest relative poverty rates in Europe"
- and
- "Greece has by far the highest subjective poverty rate in Europe."

That distinction is central.

### 4. Moving-Threshold Analysis

Test whether AROP understates deterioration because its threshold moves with national median income.

The analysis should:

- extract the AROP threshold in euros;
- deflate it to constant prices;
- compare the real poverty threshold with real income;
- show how the poverty line itself fell during the crisis;
- explain why AROP can remain stable even while households become poorer.

### 5. Anchored Poverty

Construct an approximate fixed-benchmark poverty measure anchored to a pre-crisis living standard, preferably 2008.

This should test what happens if the poverty line is adjusted for inflation but not allowed to fall with national median income.

The approximation should be validated where possible, for example by:

- comparing with Eurostat's official 2019-anchored poverty series;
- comparing with published microdata-based crisis-year estimates;
- documenting uncertainty in crisis years where extrapolation is largest.

### 6. Correlation and Robustness Tests

Calculate relationships between subjective poverty and economic variables using:

- level correlations;
- one-year lags where economically justified;
- first differences;
- detrended series;
- Spearman correlations;
- lead/lag scans on first differences.

Variables should include:

- AROP;
- AROPE;
- anchored poverty;
- real income;
- GDP per capita;
- unemployment;
- employment;
- deprivation;
- housing costs;
- arrears;
- unexpected expenses;
- inflation;
- consumption;
- wages if available.

Correlation should not be interpreted as causation.

Because many tests are run, the project should include multiple-testing discipline:

- distinguish confirmatory tests from exploratory tests;
- apply false-discovery-rate correction or adjusted p-values where appropriate;
- avoid building major claims on isolated significant findings;
- state how many related comparisons were run;
- label weaker exploratory results clearly.

### 7. Cross-Country Panel Analysis

Build a panel of EU countries to test whether countries with worse economic conditions also report higher subjective poverty.

Core predictors should include:

- unemployment;
- purchasing-power-adjusted income;
- material hardship;
- AROP;
- housing cost overburden;
- arrears;
- inability to face unexpected expenses.

The analysis should estimate whether Greece's subjective poverty is higher than expected after accounting for these conditions.

### 8. Nested Model Scorecard

Create a clear summary table showing how much of Greece's subjective-poverty gap remains after each group of variables is added.

The scorecard should include:

| Model | Variables Added | Greece Residual | Residual Reduction | Greece Rank | R² | Sample | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|

Model layers should include:

1. Basic economic conditions: unemployment, income, material hardship, AROP.
2. Housing pressure.
3. Cash-flow strain: arrears and inability to cover unexpected expenses.
4. Debt and transfer effectiveness.
5. Scarring stock: distance below own pre-crisis or historical peak.
6. Financial expectations and saving rate.
7. Trust or institutional confidence, if data are suitable.
8. Migration or brain-drain indicators, if data are suitable.

The table should show both in-sample and out-of-sample results where possible.

### 9. Leave-Greece-Out and Leave-One-Out Tests

Run out-of-sample tests:

- train models on all EU countries except Greece;
- predict Greece;
- calculate Greece's residual;
- repeat for every EU country to see whether Greece's residual is unusually large.

This should be done for all major nested model specifications, including any model that appears in the summary scorecard.

### 10. Recovery and Scarring Analysis

The project should compare deterioration and recovery patterns, not only current levels.

Key tests should include:

- peak-to-trough decline;
- current distance below historical peak;
- years below pre-crisis peak;
- years from trough to recovery;
- countries not yet recovered;
- Greece compared with EU trajectories indexed to 2008 or to each country's own peak.

This section should answer:

**Did Greece merely suffer a severe downturn, or did it uniquely fail to recover its previous living standard?**

This is central to defending the Greek perspective: persistent subjective hardship is more credible if Greece remains materially below where it once was while much of Europe moved forward.

### 11. Year-to-Year Dynamics

Test whether Greece's subjective poverty moves with annual economic changes in the same way other countries' subjective poverty does.

For each country, calculate the relationship between year-over-year changes in subjective poverty and year-over-year changes in:

- AROP;
- GDP;
- income;
- unemployment;
- deprivation;
- housing costs;
- arrears;
- unexpected expenses.

This should distinguish between:

- a normal reaction to yearly economic news;
- and a persistent elevated level consistent with scarring, insecurity, or expectations.

### 12. Near-Zero-Gap Country Comparison

Identify EU countries where AROPE and subjective poverty are close to each other.

Compare those countries with Greece on:

- unemployment;
- deprivation;
- housing cost overburden;
- arrears;
- unexpected expenses;
- distance below peak;
- savings;
- financial expectations;
- trust indicators if available.

This section should help explain why some countries feel almost exactly as poor as they measure, while Greece feels much poorer than standard indicators imply.

### 13. Emigration and Brain Drain

Explore whether crisis-era emigration helps explain long-term scarring and pessimism.

The analysis should investigate:

- net migration from Greece during crisis and recovery years;
- cumulative net population loss;
- age profile of emigrants;
- education or skill profile where available;
- return migration;
- comparison with other EU countries;
- whether emigration is associated with pessimism, expectations, or subjective poverty residuals.

This should be framed carefully as a structural scarring channel, not as a simple direct cause of subjective poverty.

Possible interpretation:

A society can feel poorer not only because current incomes are low, but because part of its working-age and skilled population left, family networks were disrupted, and expectations about the country's future weakened.

### 14. Trust and Institutional Confidence

Investigate whether trust in the state, trust in national government, trust in parliament, or trust in the EU helps explain Greece's remaining subjective-poverty gap.

This should be exploratory unless the data are strong and comparable.

Possible sources include:

- Eurobarometer;
- Eurostat governance or SDG indicators;
- OECD trust data;
- World Governance Indicators;
- European Social Survey, if suitable.

The report should distinguish between:

- material hardship;
- expectations about the future;
- and institutional confidence.

Trust should not be used to imply Greeks are irrationally pessimistic. Instead, it may help explain why similar economic conditions produce different levels of insecurity across countries.

## Storytelling and Report Structure

The final report should read as a serious long-form data-journalism article or newspaper-style evidence report.

It should be credible and scientifically careful, but easier to read than a technical paper.

The report should use a clear story arc:

1. **The paradox**
   Greece has very high subjective poverty but only moderately extreme AROP.

2. **The moving ruler**
   AROP's threshold fell with Greek incomes, hiding part of the deterioration.

3. **The fixed benchmark**
   Anchored poverty shows the crisis much more clearly.

4. **The reality check**
   Subjective poverty tracks real hardship, not random mood.

5. **The outlier test**
   Greece remains unusually high even compared with countries facing similar conditions.

6. **The layers of explanation**
   Housing, arrears, unexpected expenses, scarring, and expectations each explain part of the gap.

7. **The incomplete recovery**
   Greece has not fully regained its pre-crisis living standard.

8. **The stacked-pressure argument**
   Other countries may score badly on one dimension, but Greece combines many pressures at once.

9. **The Greek perspective**
   Greek pessimism is not merely cultural or emotional; it is rooted in measurable, long-lasting hardship.

10. **What remains open**
   Trust, migration, brain drain, housing tenure, informal income, savings depletion, and household composition may explain more, but require further testing.

The report should include:

- a stronger executive summary;
- a short "nut graf" after the hero;
- section recaps;
- "story so far" bridge paragraphs;
- callout statistics;
- a model scorecard;
- clearer links to original research questions;
- literature references woven into the relevant sections;
- a final Discussion and Conclusion section rather than a detached literature appendix.

## Literature and External Comparison

The report should compare its findings with relevant academic literature and serious public-facing work.

Literature should not appear only at the end. Key references should be placed near the findings they support.

Examples:

- anchored poverty and the moving-threshold problem near the AROP/anchored-poverty section;
- subjective poverty literature near the measurement section;
- scarring research near the recovery and below-peak section;
- housing-tenure literature near the housing section;
- trust or institutional literature near the expectations/trust section;
- data-journalism or news comparisons near the discussion of public interpretation.

The final section should become a Discussion and Conclusion that explains:

- what the report confirms;
- what it adds;
- what remains unresolved;
- how its findings compare with prior work;
- what should be tested next.

## Expected Outputs

The project should produce:

- a cleaned annual Greece–EU master table;
- a full merged analysis dataset;
- raw Eurostat data files;
- reproducible scripts;
- a model scorecard;
- Greece and EU trend charts;
- Greece–EU gap charts;
- ranking charts;
- anchored-poverty chart;
- AROPE vs subjective-poverty comparison;
- recovery trajectory chart;
- outlier residual charts;
- leave-one-out robustness tables;
- multiple-testing documentation;
- methodology notes;
- literature/discussion section;
- a readable long-form HTML report;
- an academic-style analytical memo or paper skeleton.

## Documentation Requirements

The project documentation should include:

- setup instructions;
- package versions;
- script run order;
- data sources and dataset codes;
- fetch date and data vintage;
- explanation of generated files;
- notes on comparability and breaks;
- current publication strategy;
- superseded decisions or corrections clearly marked;
- mapping from original research questions to report sections;
- limitations and future work.

## Final Research Question

The final report should be able to answer:

**When Greek households report exceptionally high difficulty making ends meet, are they simply expressing pessimism, or are they responding to measurable, long-lasting deterioration in living standards, financial security, recovery prospects, and trust in the future?**

The expected answer should be nuanced:

- Greece's subjective poverty is strongly supported by real economic deterioration.
- AROP misses part of that deterioration because its threshold moves with national median income.
- Housing costs, arrears, cash-flow strain, and material hardship explain much of the gap.
- Greece's incomplete recovery and pessimistic expectations explain additional parts.
- Greeks have measurable reasons to feel poorer and more insecure than the standard poverty rate alone suggests.
- But a residual remains, and future work should test trust, migration, brain drain, housing tenure, informal income, household composition, and microdata-based mechanisms.

The aim is not to declare one poverty measure correct and another wrong. The aim is to understand what each measure captures, why they diverge, and what Greece's unusually high subjective poverty reveals about the country's long crisis, incomplete recovery, and uncertain future.
