# Publication strategy notes

Started 2026-08-18, after a ChatGPT-assisted literature scoping discussion. This
file is the durable record; update it as the picture changes rather than
re-deriving it from scratch each time.

## Verified literature (checked against primary sources, not just ChatGPT's summary)

| Citation | Status | Notes |
|---|---|---|
| Andriopoulou, Kanavitsa & Tsakloglou, "Decomposing Poverty in Hard Times: Greece 2007-2016," LSE GreeSE Paper No. 149 (2020); also IZA DP, Revue d'économie du développement (2019) | **Confirmed, read in full** | Uses actual EU-SILC microdata (ELSTAT SILC 2008-2017 waves, incomes 2007-2016). Anchored FGT0 (headcount, 2007 base, CPI-adjusted) hits **48% at the 2013 peak**, vs. floating/relative FGT0 which rose only from ~20% (2009) to ~23% (2012) as per their Matsaganas & Leventi citation. Modified OECD equivalence scale (1.0 head / 0.3 child<14 / 0.5 other). This is the single most load-bearing paper for our Part I finding and must be cited. |
| Goedemé, Decerf & Van den Bosch, "A new poverty indicator for Europe: the extended headcount ratio," *Journal of European Social Policy* 32(3), 287-301 (2022) | Confirmed via publisher | Proposes the "extended headcount ratio" (EHC) combining relative poverty, poverty intensity, an anchored threshold, and a pan-European perspective into one indicator. Uses Greece as a worked illustration of exactly our Section 2 mechanism (median collapse decoupling AROP from anchored poverty). JESP is a strong topical fit for our paper given this precedent. |
| Želinský, Mysíková & Garner, "Trends in Subjective Income Poverty Rates in the European Union," *European Journal of Development Research* 34(5), 2493-2516 (2022) | Confirmed via publisher/SSRN | **Methodological difference to flag**: uses the Minimum Income Question (MIQ) approach to subjective poverty, not the "ability to make ends meet" item (ilc_mdes09) this project uses. Both are standard in the literature but are not the same construct — don't conflate when writing related work. Finds Greece and Bulgaria exceptionally high; decreasing trend in 16/28 countries over their window. |
| Guagnano, Santarelli & Santini, *Social Indicators Research* 128(2), 881-907 (2016) | Confirmed | Uses 2009 EU-SILC; models subjective poverty via generalized ordered logit against socioeconomic + social-capital variables. Relevant as a modelling-approach precedent, not a Greece-specific paper. |
| Baldini, Gallo & Torricelli, "Past Income Scarcity and Current Perception of Financial Fragility" (CEFIN WP) / "The scars of scarcity in the short run," *Economia Politica* (2020) | Confirmed | EU-SILC longitudinal 2010-2013. Finds a past scarcity spell lowers subjective make-ends-meet assessment up to 2 years later, controlling for current income — effect is subjective, weakens/disappears on more objective financial-health measures. **Directly relevant to the "scarring" hypothesis** flagged as an open question in our Part II. |
| EU-SILC Scientific Use File access process | Confirmed independently | Requires recognized research-entity status (~4 weeks) + research-proposal validation (~8-10 weeks) + national-authority consultation (~4 weeks). Realistic total: 2-3 months minimum, and requires an actual institutional affiliation to apply through. Public/synthetic EU-SILC microdata explicitly cannot be used for publication-quality inference per Eurostat. |

## NOT verified — do not cite without independently pulling the source

- A "2026 *Economics Letters*" paper on a residual-income measure (subtracting fixed costs) aligning with subjective hardship. Could not locate. May be a conflation or a real paper under different framing — check via Scopus/Web of Science directly before citing.
- A "2026 *Social Indicators Research*" paper modelling financial vulnerability as P(expenditure > income). Found two real but non-matching candidates: Guan et al.-style 2021 SIR "Living with Reduced Income" (COVID-era, income-expenditure gap indicator) and Meng & Xiao 2026 SIR (financial vulnerability via ML, COVID focus). Neither matches the description exactly — verify before use.

**General lesson**: the older/more central citations checked out cleanly; the newest ones (used to support the most novel-sounding part of the argument) were the ones that didn't verify. Weight LLM-sourced literature reviews accordingly — verify precisely the citations doing the most rhetorical work, not just a random sample.

## The Andriopoulou cross-check (new finding, 2026-08-18)

Our approximated anchored-poverty series (Section 3 of the report, lognormal fit
to 4 published threshold/rate points, anchored to 2008) gives **39.7%** for 2013.
Andriopoulou et al.'s microdata-based anchored FGT0 (2007 base) gives **48%** for
the same peak year. Gap: ~8 points, much larger than the ~1.2pp average error our
own 2019-anchor validation found.

**Interpretation**: our method understates the anchored-poverty effect specifically
in the high-extrapolation crisis years (2012-2014) — consistent with, and now
giving concrete size to, the caveat already in the report. Directionally
reassuring for the core Part I argument (the true effect is if anything larger
than we show), but means the exact 39.7% figure should not be presented as
precise. This is a much more relevant validation point than the 2019-anchor
check (same mechanism, actual crisis years, peer-reviewed microdata) and should
be folded into the report's methodology section and Section 3 caveat.

**Not yet done**: pulling year-by-year anchored FGT0 from Andriopoulou et al. for
more than just the 2013 peak (their Graph 3 has the full 2007-2016 series,
indexed to 2007=100, but I only read the text description of the peak value —
the underlying chart data isn't in the extracted text). Digitizing or requesting
their full series would let us compare year-by-year rather than at one point.

**Status: DONE.** Folded into the live report on 2026-08-18 — a new "A second,
more relevant check" subsection in Section 3, plus a matching entry in the
Methodology validation subsection. Also added a full "Where this fits in the
research literature" section (before Methods) and a "Related literature — full
citations" block in Methods, in the report's own plain-language register (not
academic-paper style, per user's ask).

## Second literature pass (2026-08-18) — four more verified papers

Went looking specifically for: papers using the exact "ability to make ends
meet" EU-SILC item, a cross-country analog to our own "unexplained residual"
puzzle, housing/tenure determinants of subjective poverty, and statistical
critiques applicable to our cross-country panel models.

| Citation | Relevance |
|---|---|
| Nikolova, M. (2016). Minding the happiness gap: Political institutions and perceived quality of life in transition. *European Journal of Political Economy*, 45, 129-148. | **Best new lead for Part II's open question.** Studies the "happiness gap" between post-communist and Western European countries — a country-level residual that survives controlling for economic conditions, closely analogous to our Greek subjective-poverty residual. Finds institutional quality (rule of law specifically) explains a meaningful further share, on top of macroeconomics. Suggests governance/institutional-quality variables as the next thing to test, distinct from debt-to-income and transfer-effectiveness (already tested, both null). |
| &Zcaron;elinsk&yacute;, T., Ng, J. W. J., & Mysíková, M. (2020). Estimating subjective poverty lines with discrete information. *Economics Letters*, 196. | **Best new lead for Section 3's methodology.** Builds an income threshold directly from the EU-SILC "ability to make ends meet" item — our exact variable — using the Youden index, a more rigorous, peer-reviewed alternative to this project's ad hoc lognormal-probit fit. See ideas list below. |
| Filandri, M., Pasqua, S., & Tucci, V. (2025). Housing tenure and subjective poverty among young European adults: The role of rent regulation. *Journal of European Social Policy*, 35(4), 332-348. | Confirms housing tenure is a validated, EU-SILC-compatible variable for subjective-poverty research (young-adult subsample, not general population — not a direct substitute for our analysis, but real precedent for pursuing the "housing tenure" item already flagged as open in our verdict). |
| Claessens, S., Kyritsis, T., & Atkinson, Q. D. (2023). Cross-national analyses require additional controls to account for the non-independence of nations. *Nature Communications*, 14, 5776. | Methodological critique: cross-country regressions (like our Sections 6-9) usually wrongly treat each country as statistically independent; neighbouring/culturally-linked countries move together in ways plain country-clustered SEs don't fully capture. Recommends Conley (spatial) standard errors or a neighbouring-country-mean control. Applies directly to our panel models — a limitation we share with most published work in this space, not unique to us. |

Also surfaced but not pursued further: "Choosing an optimal material deprivation
indicator threshold" (deprivation-threshold methodology, possibly Guio/Marlier-
adjacent) and "Economic Hardship, Housing Cost Burden and Tenure Status:
Evidence from EU-SILC" (*Journal of Family and Economic Issues*, 2014, older
housing-burden precedent). Lower priority than the four above.

**Status: DONE.** All four folded into the report's new literature section and
methodology citation list on 2026-08-18.

## Third review pass (2026-08-18) — corrections to the literature/Andriopoulou additions

A colleague independently verified the four new papers (all confirmed real and
accurately characterized) but caught real errors in how the additions were
written up. All fixed in the live report:

1. **Year-alignment error in the Andriopoulou comparison.** Andriopoulou et
   al.'s years are *income* years; this project's series are labelled by
   EU-SILC *survey* year, which reflects income from the prior calendar year
   (a distinction the report's own methodology already states elsewhere, just
   wasn't applied here). Correct comparison: their income-year 2013 (48%)
   against this project's survey-year **2014** (40.6%), not survey-year 2013
   (39.7%). Still a ~7-8pp gap, same qualitative conclusion, just the properly
   aligned years.
2. **Overclaimed the direction/cause of that gap.** Originally framed as "our
   method understates" / "the error runs in the reassuring direction" — too
   strong. Microdata vs. four-point aggregate reconstruction, exact price
   index, anchor-year definition, and data vintage all differ simultaneously,
   so the gap can't be attributed cleanly to any one cause including "our
   approximation's bias." Corrected to: independent microdata corroborates the
   same qualitative finding and happens to show an even larger effect — without
   claiming to have identified our own estimator's error.
3. **Youden-index paper (Želinský, Ng & Mysíková 2020) was mischaracterized.**
   Originally described as "a more rigorous version" of this project's
   anchored-poverty construction. It isn't — it estimates a different object
   entirely (the income level that best discriminates subjectively-poor from
   not-poor households in a *given* year) vs. our anchored measure (share below
   a *fixed pre-crisis* threshold). Corrected to describe it as a complementary
   method that could support a genuinely new, distinct future analysis: a
   fourth series alongside AROP/anchored/subjective-rate — an estimated
   "subjective poverty threshold in euros" per year (see idea #1 below, which
   itself needed re-scoping as a result).
4. **Internal contradiction**: the literature section said debt-to-income and
   transfer-effectiveness were "already ruled out" in Section 8, directly
   contradicting Section 8's own carefully-hedged "provided no additional
   explanatory power in this specification" language introduced in the prior
   revision. Fixed to match.
5. **Nikolova and Filandri claims overstated.** Nikolova's happiness-gap paper
   is an analogy (different countries, different outcome variable), not
   evidence about Greece — now explicitly labelled "a future exploratory
   hypothesis," not the obvious next test. Filandri et al.'s housing-tenure
   result is specific to young adults (18-34, 24 countries) — now noted as not
   yet shown to hold for the general Greek population.
6. **Claessens et al. framing corrected.** Their paper doesn't establish Conley
   standard errors as *the* fix — they compare Conley corrections against
   directly modelling geographic/cultural proximity, with mixed results
   depending on the case. Corrected to recommend first checking this project's
   own residuals for spatial structure before choosing how elaborate a
   correction to apply.
7. **Two lingering issues from an earlier round, confirmed still present and
   fixed**: the hero dek still called AROP "unremarkable" (contradicting the
   4th-of-27 stat tile directly below it) — now "elevated but not extreme...
   4th-highest of 27." "National average" was used inconsistently for AROP's
   definition (should be "national median" throughout, as used correctly
   elsewhere) — fixed in the executive summary, Section 1's lede, and the
   Answer to Question 1 box. "The paradox is largely a measurement artifact"
   overclaimed given Part II's own findings — softened to note Part I explains
   a real, sizeable part but not the whole picture.

**New analysis added**: leave-one-country-out (not just leave-Greece-out) run
for all 27 countries on Model C, to give Greece's out-of-sample gap a
distribution to be judged against. Result: Greece's average leave-out residual
(11.6pp) is the largest of all 27 countries — a z-score of ~1.94 against the
other 26's distribution (mean ~0, sd ~6pp) — with only Luxembourg (10.7pp)
close. Script: `scripts/19_leave_one_out_all_countries.py`, output
`data/processed/leave_one_out_all_countries.csv`. Added to Section 9 and the
Answer to Question 2 box.

**Lesson for future rounds**: this is the second time a review caught language
that overclaimed causal attribution or contradicted a hedge introduced
elsewhere in the same document. When adding new content that references
existing findings (e.g. "Section 8 ruled out..."), re-read the section being
referenced rather than reconstructing its claim from memory.

## Fourth review pass (2026-08-18) — the final robustness test, and one self-caught error

Reviewer's assessment: Q1 "essentially finished," Q2 "nearly closed," with one
remaining test requested (the others were judged sufficient, explicitly warning
against further variable-hunting past this point).

**Nested leave-one-country-out A/B/C, for all 27 countries** (not just Model C
as before) — script `scripts/20_nested_leave_one_out.py`. Result was more
interesting than the smooth decline the reviewer hypothesized:

| Model | Greece's out-of-sample gap | Rank | Next-highest |
|---|---|---|---|
| A: structural | +25.6 | 1/27 | Luxembourg +18.5 |
| B: + housing | +35.5 (grows, not shrinks) | 1/27 | Cyprus +19.4 |
| C: + arrears/unexpected | +11.6 | 1/27 | Luxembourg +10.7 |

Housing *alone*, out-of-sample, makes Greece harder to predict, not easier —
the opposite of the in-sample pattern (15.1 → 8.8 → 2.2). Only adding
arrears/unexpected on top of housing brings the out-of-sample gap down. This
mismatch between the clean in-sample decline and the bumpy out-of-sample one is
reported as informative in itself: the in-sample models can partly fit
Greece's own pattern into the housing coefficient, which the out-of-sample
test can't do. Greece is rank 1/27 in *every* specification, in-sample and out
— that finding is robust; "housing and cash-flow explain most of the gap" is
not quite right as a smooth story and is now stated more carefully in the
report (Section 9, Answer to Question 2).

**Self-caught error while writing this up**: first draft claimed Greece's
Model-C out-of-sample gap (11.6) was "more than double" Luxembourg's (10.7) —
arithmetically wrong (barely above it, not double). Caught on re-read before
publishing. Worth remembering: check the arithmetic in any sentence comparing
two numbers, especially when writing quickly after getting an exciting result.

**Other fixes from this pass, all applied**: softened "clearly outside the
range" (superseded by the nested-model writeup itself, which is more precise);
"growing since 2020" → "concentrated in the 2020s" (the leave-Greece-out
residual isn't monotonic — dips in 2022-2023); "supposed to describe the same
thing" → "related but genuinely different things"; Section 8's "shows where
the gap comes from" → "shows how much... can statistically account for" (plus
an explicit reminder that arrears/unexpected-expenses are outcome-adjacent);
fixed a real number error in the first-difference lead/lag write-up (same-year
and prior-year unemployment correlations are 0.859 vs 0.855 — essentially
tied, not "prior year edges ahead" as originally written); softened "eased as
inflation cooled" given subjective poverty ticked up slightly in 2025 rather
than continuing to fall. Q1 and Q2 reworded to the reviewer's more precise
formulations (Q2 now explicitly allows "a residual remains unexplained" as a
valid, complete answer rather than implying the report is unfinished without
a cause).

**Status per the reviewer**: after this pass, empirical scope should freeze.
Explicit instruction: do not add informal-economy, housing-tenure, governance,
or spatial-dependence variables now — those are Paper 2 material, not
robustness checks this report still owes anyone.

## AROPE comparison added (2026-08-18, same day, user follow-up)

User asked whether AROP and AROPE (at-risk-of-poverty-**o**r-social-**e**xclusion,
`ilc_peps01`/`ilc_peps01n`) differ and whether the report's analysis holds for
both. Answer: they're genuinely different indicators — AROPE is the union of
AROP, severe material & social deprivation, and very-low-work-intensity — and
the moving-yardstick mechanism in Section 2 is specific to AROP's construction,
not something that transfers cleanly to AROPE (two of its three components
aren't relative-median-based). User asked to add the comparison anyway.

**Result, script `scripts/21_arope.py`**: AROPE correlates with subjective
poverty far better than plain AROP does, with no approximation required —
r=0.48 (level), 0.74 (first-diff), **0.90 (detrended, matching the anchored-
poverty series)**, vs. AROP's 0.19 / 0.60 / 0.67 on the same three tests. Added
as a fourth line to Section 3's comparison chart, plus a Methodology entry
covering the definition, the same legacy/new (`ilc_peps01`→`ilc_peps01n`)
methodology break already documented for material deprivation, and Greece's
AROPE rank (2nd-7th of 27, elevated like AROP, nowhere near subjective
poverty's 1st-of-27-every-year).

## Reopening Part II: expectations, wealth, and a Greek survey (2026-08-18, same day)

After the outlier-prefilter round (temp employment dropped, healthcare and
co-residence survived), user pushed further: numbers alone probably won't
answer Q2's residual, and something is being missed. Correctly diagnosed:
every variable tested so far (housing, arrears, deprivation, debt-to-income,
transfer-effectiveness) describes material *conditions*. Nothing tested
described *expectations* about the future or *wealth trajectory* (stock, not
flow) — user's own hypothesis: people may not be poor by current income, but
feel poor because they've been losing wealth every year.

**Financial expectations (Model E), script `scripts/23_model_E_expectations_wealth.py`:**
Fetched Eurostat's household financial-expectations survey (`ei_bsco_m`,
indicator `BS-FS-NY`, "financial situation over the next 12 months"). Outlier
pre-check: Greece is the single most pessimistic country in the dataset
(35 countries) at -35.6 (balance statistic), 11 points clear of 2nd place
(Slovenia, -24.5). Added to the panel model in place of the null debt/transfer
variables:
- In-sample: R² 0.892→0.904, coefficient significant (p=0.021), Greece's avg
  residual falls 2.2→1.3.
- **Leave-one-out for all 27 countries: Greece's rank falls from 1st (every
  prior model) to 10th of 27.** This is the first variable tested that
  actually dislodges Greece from the top of the outlier list.

**Critical caveat, must stay in any write-up of this**: "how do you expect
YOUR OWN household's finances to change" is itself a subjective/perceptual
survey question — much closer in kind to "how difficult is it to make ends
meet" than any material variable is. This result is more modest than "we
found the cause": it shows current difficulty and future pessimism are
closely related sentiments that travel together, not that an objective
condition explains the gap. It reframes the residual (from "unexplained
material gap" to "Greece is unusually pessimistic about its own future, in a
way partly separable from current conditions") rather than resolving it. The
sharper open question becomes: why are Greeks so much more pessimistic than
material conditions alone predict — which is arguably a better question than
the one we started with, but not one this aggregate-data approach can answer.

**Household saving rate (wealth-depletion test)**: fetched `tec00131`
(household saving rate). Greece outlier-confirmed: 2nd-lowest of 34 countries
(avg -2.24%, 2015-2024), persistently negative almost every year 2014-2024
except the COVID-distorted 2020-2021. But in Model E, once financial
expectations is included, saving rate's coefficient is ~0 (p=0.997) — no
independent explanatory power. Likely explanation: saving rate correlates
with financial expectations (r=0.23) and arrears (via expectations, r=-0.51
between expectations and arrears) closely enough that it doesn't add
anything once those are in. This doesn't kill the wealth-depletion idea, but
the *aggregate national* saving rate isn't picking up a separable effect —
consistent with the recurring problem that national averages can't see
within-country distribution of who is actually depleting wealth.

**DiaNEOsis survey, found and read (PDF: `ftwxeia2_version_060616_2.pdf`,
University of Macedonia poll for diaNEOsis, April 2016, n=1,348, ±2.7%)** —
independent corroboration from a completely different Greek survey house and
year: 90% said the country was heading in the wrong direction; **74% expected
their own situation to worsen over the next 12 months (7% expected
improvement)**; 81.5% reported difficulty meeting absolutely basic household
needs (even higher than the EU-SILC figure for that year). Two independent
instruments agree on the same extreme pessimism finding.

**Status: written into the report as Section 10, with the caveat kept front
and center** (2026-08-19). The user's next request (below) asked for a
year-by-year-diffs methodology and a near-zero-gap country comparison before
answering the open framing question directly — proceeded to write Model E in
with its full caveat intact, on the judgment that the caveat itself (already
drafted and reviewed above) *is* the safe framing, rather than holding it back
further.

## Year-by-year dynamics, scarring stock, and near-zero-gap comparison (2026-08-19)

User's three-part request: (1) check greekonomics.gr and its GitHub repo for
useful material, (2) design a year-by-year-diffs methodology across all
measures, comparing Greece to the rest of the EU, incorporating "derivatives"
(rate of change / acceleration), (3) investigate why some EU countries (user
named Belgium, Slovenia, Hungary) show subjective poverty almost exactly
matching their official rate, as a contrastive lens on Greece. (1) delegated
to a background research agent (greekonomics.gr navigation was flaky earlier
in this session; `get_page_text` after `navigate` confirmed the report-page
content loads even when `navigate`'s own return string looked like the
homepage). (2) and (3) done directly — new scripts below.

**`scripts/24_year_over_year_dynamics.py`** — three things:
1. **Time-varying scarring stock**: for every country-year 2008–2024, % below
   that country's own running-historical-maximum real GDP/capita
   (`sdg_08_10`). This is the correct operationalization of the user's own
   standing hypothesis ("even if people are not under poverty they think they
   are since every year they lose wealth") — time-varying and entered
   directly into the panel regression, unlike script 12's earlier
   cross-sectional single-number-per-country peak-to-trough check.
   **Result: Greece is uniquely still scarred.** 11.2% below its 2008 peak as
   of 2024 — next-closest is Estonia at 7.1%, then Luxembourg 6.1%; every
   other EU country (18 of 27) is at 0–2.5%, i.e. fully recovered or never
   that far below. A clean, striking, standalone fact independent of any
   regression.
2. **Country-by-country Δpredictor vs. Δsubjective_poverty sensitivity**
   (correlate each country's own year-over-year swings against its own
   year-over-year subjective-poverty swings — different from the existing
   pooled first-diff correlations in scripts 10/18). Notable: Greece's
   Δarop↔Δsubjective_poverty correlation is high (r=+0.71, rank 3/27), but
   its sensitivity to Δunemployment, Δdeprivation, Δhousing, Δarrears,
   Δunexpected_expenses is low or negative (ranks 19–27 of 27 on most). Not
   written into the report — reads as "Greek subjective poverty doesn't swing
   with material hardship the way most of the EU's does; it looks more like a
   sticky/anchored level than a hardship-reactive series," which is
   consistent with the scarring/pessimism story but is its own claim and
   wasn't independently stress-tested before deciding whether to publish it.
   Kept as a research-log note, not report content, for now.
3. **Model F** (Model C + time-varying scarring stock, same panel-regression
   spec as Sections 7–9): R² 0.892→0.896, coefficient 0.43, p=0.045. Greece's
   in-sample avg residual 2.2→1.3. Leave-Greece-out out-of-sample residual:
   11.6 (Model C, Section 9) → 7.1 (Model F). Leave-one-out-all-countries:
   Greece's rank falls from 1st (every model through Section 9) to 4th of 27
   (behind Luxembourg 9.8, Cyprus 7.7, Portugal 7.5). Modest effect size, but
   statistically real, time-varying (not a cross-sectional artifact), and
   matches the already-cited Baldini/Gallo/Torricelli scarring literature —
   written into the report as Section 10 with that grounding stated
   explicitly.
4. **Second differences (acceleration)**: only material deprivation's
   acceleration correlates significantly with subjective poverty's
   acceleration (r=+0.22, p=0.001, n=218); unemployment, GDP, and arrears
   accelerations don't reach significance. Exploratory, not written into the
   report — one significant result out of five tested, plausibly noise, and
   the underlying user idea ("derivatives") is already served better by the
   scarring-stock result (a first-difference-style cumulative-stock variable)
   than by this raw second-difference check.

**`scripts/25_near_zero_gap_countries.py`** — compared Greece against the
eight EU countries where AROPE and subjective poverty are within 2pp of each
other (Italy, France, Portugal, Hungary, Croatia, Cyprus, Belgium, Slovenia;
user specifically named Belgium, Slovenia, Hungary and the analysis
confirmed all three qualify, plus five more). Finding: these eight are *not*
a uniform low-hardship group — individually, several score worse than Greece
on single measures (Hungary's material deprivation 9.3% vs. Greece's 14.0%
looks close, but e.g. Cyprus's arrears at 12.5% actually exceeds several
EU countries). What distinguishes Greece isn't any single hardship dimension
— it's that Greece ranks 1st–3rd of 27 on housing cost overburden, arrears,
distance-below-peak, deprivation, and inability-to-cover-an-unexpected-expense
*simultaneously*, and every one of the eight comparison countries has fully
recovered to its own income peak (0% below) while Greece hasn't (11.2%), and
none approaches Greece's financial-pessimism score. Written into the report
as Section 10's closing subsection. Framed explicitly as descriptive/
correlational (n=8, no regression), not a causal test — consistent with this
project's established discipline.

**Report changes**: new Section 10 ("What's behind the remaining gap:
scarring and pessimism") inserted between Section 9 (leave-Greece-out) and
the Answer 2 box, covering the scarring-stock/Model F result, the Model E
financial-expectations result (with its epistemic caveat kept prominent,
exactly as drafted earlier), the diaNEOsis corroboration, and the near-zero-
gap comparison. Answer 2 box got one bridging sentence pointing to Section
10. Literature section got a new paragraph tying Section 10 to Baldini,
Gallo & Torricelli (2020) and to the diaNEOsis survey, plus diaNEOsis added
to the citations list. Methods section's "variables tested but not central"
note updated to point at Section 10 instead of this log, and a new "Section
10 variables" methods subsection added documenting the scarring-stock and
financial-expectations variable definitions/sources. Tag-balance-checked
before republishing, per established pattern.

**New data files**: `panel_with_diffs.csv` (first/second differences for all
Part II variables plus the scarring stock), `sensitivity_*.csv` (one per
predictor, country-by-country Δ-correlation with rank), `leave_one_out_
modelF.csv`, `near_zero_gap_comparison.csv`.

## Five-point traceability review, addressed (2026-08-18)

A second reviewer (via a different tool) checked the report against the
original project brief specifically for completeness/traceability, not
analysis. All five addressed:
1. Added "Variables tested but not central" methods note (minimum wage,
   inflation, consumption, saving rate, and flagged real wages as never
   fetched at all — genuinely absent, not silently dropped).
2. Added an upfront framing note (right after the hero) explaining the
   deliberate departure from the brief's "objective poverty" label for AROP.
3. Fixed AROPE snapshot chart wording ("every EU country" → "every EU country
   plus the EU average," since the aggregate row is included).
4. Added a "Data appendix" methods entry naming `master_table.csv` and
   `analysis_dataset.csv` explicitly and pointing to the README for the full
   pipeline.
5. Added `README.md` (run order, structure, dependencies) and
   `requirements.txt` to the project root.

**Not yet done**: AROPE wasn't added to the cross-country panel models
(Sections 7-9) as an alternative or additional regressor — it currently only
appears in the Section 3 chart and the correlation table. Given the reviewer's
explicit freeze instruction above, this should wait for a deliberate decision
to reopen the empirical scope, not be added reflexively.

**Follow-up question, worth keeping on record**: user asked whether AROPE
tracking subjective poverty well makes the report's novelty claim weaker.
Answer, reasoned through and now reflected in the report's own text (Section 3
finding box): no — AROPE's good correlation and the anchored-poverty
demonstration are evidence for two *different* mechanisms, not two
confirmations of the same one. AROPE's AROP-poor component still uses the
identical moving 60%-of-median threshold; AROPE performs well mainly because
it *inherits* the severe-material-deprivation component, which this project's
own correlation table already showed tracks subjective poverty closely on its
own. So AROPE corroborates a fairly unsurprising, already-known point (narrow
income measures miss things AROPE's third condition was designed to catch —
which is *why AROPE exists as Eurostat's headline indicator in the first
place*, not a new insight), while the anchored-poverty argument isolates a
specific, cleaner mechanism (the threshold itself moving) using income data
alone. Conclusion: don't shift focus toward AROPE. The report's genuinely
defensible novelty still lives in the combination described earlier in this
file (subjective-poverty angle + robustness layer + Part II residual
decomposition), not in "broader measures beat narrow ones," which is not new.

## Origin story surfaced, and a new opening chart (2026-08-18, same day)

User revealed the actual motivation for this whole project: a chart on
GreeceInFigures.com (Datawrapper, sourced from `ilc_peps01n` + `ilc_sbjp01` —
the same two series this project independently arrived at) showing AROPE vs.
subjective poverty across EU countries for 2025. Cross-checked the numbers in
that image against this project's own pipeline: exact match (Greece 28%/67%,
EU 21%/18%).

Added a new cross-country snapshot chart to the top of Section 1 (a dumbbell
chart, script `scripts/22_arope_snapshot.py`, all 27 EU states + EU aggregate,
2025) reproducing that comparison inside the report itself. Noticed something
the motivating chart shows but this project hadn't stated explicitly: **the
gap flips direction across Europe** — Greece, Bulgaria, Slovakia show
subjective > AROPE; a cluster of mostly Northern/Western states (Germany
-13.8, Luxembourg -11.1, Lithuania -14.5, Sweden -8.5, Netherlands -8.5,
Finland -8.2) show the opposite, AROPE > subjective, by comparable magnitude.
Greece's +39.7pp gap dwarfs every country in either direction (next-largest:
Bulgaria +7.1). This reframes the finding slightly: it's not "Greece
under/over-reports by an unusual amount on a shared spectrum," it's "Greece is
a large, singular exception to a pattern where most countries cluster within
~5 points of agreement." Full snapshot data: `data/processed/arope_subjective_snapshot_2025.csv`.

## My assessment of the overall pitch (Claude, 2026-08-18)

- **Novelty positioning**: agree with ChatGPT — do not sell the moving-threshold
  finding as novel; Andriopoulou et al. already established it for Greece with
  better data. Our defensible contribution is the combination: linking the
  *subjective* measure (not just anchored income poverty) to the mechanism, the
  first-differencing/detrending/within-country-panel robustness layer, and the
  Part II residual decomposition + leave-Greece-out result. The second part is
  the more distinctive piece.
- **Journal fit reasoning** (SIR, JESP as realistic; RIW as a stretch): sound
  given each journal's stated scope, but the specific acceptance-rate numbers
  ChatGPT cited (15%, 9%) are unverified — don't repeat them as confirmed facts.
- **Microdata as "the single biggest upgrade"**: agree in principle, but it's a
  large commitment (institutional affiliation required, 2-3 month minimum
  process, a real step up in statistical complexity) — only worth pursuing if
  there's an actual institutional affiliation available and genuine intent to
  submit, not as a lightweight next step.
- **Overall**: as an HTML report, not close to submittable — needs full academic
  restructuring, a real related-work section engaging the papers above, and the
  novelty reframed away from the moving-threshold observation. As-is, it's
  legitimately useful as a working paper / preprint / policy brief / thesis
  scoping document. The Andriopoulou benchmark above is a cheap, high-value
  addition regardless of which path this takes next.

## Methodological ideas surfaced by the literature, worth applying (2026-08-18)

Ranked by cost vs. value. None of these are done yet.

1. **Youden-index subjective poverty line (from &Zcaron;elinsk&yacute;, Ng & Mysíková 2020) — highest value, moderate cost.**
   Their method derives an income threshold directly from the binary "poor/not
   poor" make-ends-meet responses using the Youden index, applied to EU-SILC
   microdata. We can't replicate it exactly without microdata, but the same
   logic could be approximated from aggregate published tables similarly to how
   Section 3's anchored series was built — and would let us produce an actual
   "subjective poverty threshold in euros" per year, then compare *three*
   threshold trajectories (AROP's relative threshold, our anchored threshold,
   and this subjective threshold) instead of just three poverty *rates*. This
   is probably the single best next analytical addition. (Confirmed correct
   framing in the third review pass below — this entry already treated it as a
   distinct fourth object, not an upgrade to Section 3; the report's prose
   originally got this wrong and has been corrected to match.)
2. **Institutional-quality variable in the Part II regression (from Nikolova
   2016) — high value, low-moderate cost.** Add a governance/rule-of-law
   indicator (e.g. World Bank Worldwide Governance Indicators, or the EU Rule
   of Law Report's country scores) to Model D in place of/alongside
   debt-to-income and transfer-effectiveness (both already tested, both null).
   Directly targets the still-open "what explains the residual" question with
   a concrete, precedented variable rather than speculation.
3. **Spatially-corrected standard errors (from Claessens et al. 2023) —
   moderate value, low-moderate cost.** Rerun the cross-country panel models
   (Sections 6-9) with Conley standard errors or a neighbouring-country-mean
   control, instead of relying only on country-clustered SEs. Wouldn't likely
   change the point estimates, but would make the significance claims more
   defensible against an obvious referee critique.
4. **Housing tenure as a Model D-style addition (from Filandri et al. 2025) —
   moderate value, needs a data source check.** They use tenure status (own
   outright / mortgage / rent / social housing) and rent-regulation variables;
   worth checking whether Eurostat publishes a cross-country tenure-status
   table compatible with our panel before committing to this.

## Ranked next steps, publication track (cost vs. value, as of 2026-08-18)

1. ~~Fold the Andriopoulou comparison into the report~~ — **done**, 2026-08-18.
2. ~~Draft a related-work section~~ — **done**, 2026-08-18 (report-level plain
   language, not academic register, per user's request — a denser academic
   version would still be needed for an actual journal submission).
3. **Moderate**: convert to academic paper structure/register if a specific
   target (working paper series, journal) is chosen.
4. **Large commitment, only if serious about journal submission**: pursue
   EU-SILC Scientific Use File access (needs institutional affiliation) and
   redo the anchored-poverty and cross-country work on exact microdata instead
   of aggregate published tables.

## greekonomics.gr and dianeosis.org research, folded in (2026-08-19)

Two background research agents read greekonomics.gr (+ its GitHub repo) and
four dianeosis.org pages the user pointed at directly. Full agent transcripts
aren't retained here; this is the distilled, verified subset actually written
into the report (literature section, new h4 "External corroboration from
other Greek data-journalism and research"), plus what was deliberately left
out and why.

**Written into the report:**
- **Mantés & Marinakis (2025)**, the Greekonomics.gr report (86pp PDF, code at
  github.com/AMantes/Greekonomics, MIT license, R/tidyverse, dataset codes
  documented and independently reproducible). Their "Bottom-10" comparator
  design (10 EU countries poorer than Greece pre-2008, since overtaken it —
  BG/HU/LV/HR/PL/LT/SK/EE/CZ/RO) is a genuinely different and defensible
  alternative to this project's EU27-pooled approach. Their real-disposable-
  income finding (Greece -18% vs. 2008 in 2023, EU27 +11%, Bottom-10 +38%)
  directly parallels Section 10's own scarring result and was cited as such.
  Housing-overburden (88-90% for Greece's below-median-income households,
  ~3x EU27/Bottom-10) and unmet-medical-need (12% vs ~2.4% EU) findings cited
  with the caveat that their housing figure is poverty-status-specific, not
  directly comparable to Section 8's general-population figure.
- **diaNEOsis housing article** (Nikolaidis, Jan 2026, summarizing an
  IOBE/Vettas study): 35.5% of disposable income on housing (Greece, 2024)
  vs. 19.2% EU average; 42.8% arrears vs. 9.2% EU average. The 42.8% figure
  is an exact match to this project's own Greece arrears rate (Section 8) —
  expected, not coincidental, since both trace to the same Eurostat series,
  but logged as a clean independent sanity check.
- **Matsaganis et al. (2016/2017)**, diaNEOsis's own extreme-poverty study —
  a third poverty definition (absolute "basket of goods" line) distinct from
  both AROP and this project's anchored-poverty approximation, cited as a
  reminder that "poverty line" isn't one settled concept even within Greek
  research specifically.
- Citations added to Methods for all three.

**Found but deliberately NOT written in:**
- diaNEOsis's Crisis Monitor (13 live indicators incl. an AROP series
  identical in definition to Eurostat's) — descriptive dashboard, no
  regression/subjective component, not enough new information to justify a
  report mention beyond what's already cited.
- diaNEOsis's poverty research hub's other entries (2024 regional-poverty
  paper by Karakitsios et al.; 2025 benefits-policy assessment by
  Liargovas) — real but tangential to this report's two specific questions;
  logged here in case a future regional-poverty angle gets pursued.
- Greekonomics.gr's other articles (gender pay gap, property prices,
  tax-revenue mix, brain-drain-reversal rebuttal) — read and verified by the
  agent, genuinely interesting Greek-economy context, but none bear directly
  enough on the subjective-vs-official-poverty question to warrant inclusion
  without diluting the report's focus. Available if a future piece needs
  them (full detail in the agent's original output, not reproduced here).
- The Bottom-10 comparator group itself was **not** adopted as a replacement
  or addition to this project's own EU27-pooled regressions — that would be
  a substantial new analysis (refetching/regrouping the whole panel), not a
  citation, and wasn't asked for. Flagged as a legitimate future-work idea:
  rerunning Part II's models with Bottom-10 as an alternative reference group
  instead of (or alongside) the full EU27 pool.

**Also fixed while in the file**: the TOC had gone stale after Section 10 was
inserted (nav still said "10. Answer to Question 2") — corrected to number
Section 10 correctly and Answer 2 as 11. Added an explicit "Source: Eurostat"
label to the AROPE-vs-subjective-poverty chart foot-note (previously bare
dataset codes) and a corroboration note pointing to Greece in Figures'
matching Greece-vs-EU-average figures for that same chart, worded carefully
to not imply our own 27-country chart was sourced from them — it wasn't;
theirs only covers Greece vs. the EU average, ours is this project's own
27-country pull from the live Eurostat API.

## Diff-sensitivity finally written into the report (2026-08-19)

User pushed back after the previous round's summary claimed the country-by-
country Δ-sensitivity analysis (script 24, section 3) existed but was
deliberately left out — user said "i dont see them in the rwport" and, taken
together with the original ask ("how they relate or not to the gap"), that
was read as: put it in, and actually test the "relate to the gap" half
properly instead of just describing it.

Added script 24's section 6: for each of the 9 predictors, correlate a
country's own Δ-sensitivity (its Section-3 correlation coefficient) against
its Model C leave-one-out residual (Section 9's per-country gap) across all
27 countries — both with and without Greece, specifically to check whether
any relationship found is just "Greece is unusual on two things at once"
rather than a real cross-country pattern. Result: 8 of 9 predictors show no
reliable relationship. **Real GDP per capita is the exception**: r=+0.52,
p=0.006 with Greece included; r=+0.50, p=0.009 with Greece excluded — a
genuine, not Greece-driven, EU-wide pattern (countries whose subjective
poverty is less tied to — or moves opposite to — GDP swings tend to have
bigger unexplained gaps). Arrears looked similar at first (r=-0.46, p=0.016)
but drops to p=0.058 once Greece is excluded — reported as Greece-driven,
not a general pattern, rather than as a finding. Saved to
`data/processed/sensitivity_vs_gap.csv`.

Both this test and the raw Section-3 sensitivity table (Greece's own
Δpredictor-vs-Δsubjective_poverty correlations, ranked against all 27
countries) are now in the report as a new Section 10 subsection, "Does
Greece's subjective poverty move with the economy the way other countries'
does?", inserted between the scarring-stock subsection and the financial-
expectations subsection. Headline pattern written in: Greece tracks its own
AROP changes unusually tightly (rank 3/27) but is unusually *insensitive* to
material-hardship swings — unemployment, housing, deprivation, arrears,
unexpected-expense capacity all rank in the bottom third of the EU, arrears
dead last (27/27, the only negative-signed correlation of any severity).
Framed as consistent with the report's broader "persistent level, not
swing-reactive" scarring/pessimism story, not as a new independent finding.
Explicitly caveated in the report itself: 9-10 observations per country's
own correlation, 9 predictors tested for the gap-relation check — weaker
evidentiary standard than the panel regressions used elsewhere, stated as
such rather than presented at the same confidence level.

## Full project review, then three-item response round (2026-08-19/20)

User asked for a full careful review (analysis rigor + report storytelling),
gave detailed comments (report still too hard to read; Sections "still below
peak," "moves with the economy," and "near-zero-gap" should be anchor
sections, not late subsections; want a summary scorecard; literature section
should connect to the main narrative and become a real discussion/conclusion;
report should more clearly defend that Greeks have real reasons, not just
pessimism — consider trust in state/EU as a variable). Delivered a structured
review (not implemented yet) covering: current-state assessment (11,075
visible words, ~45min read; executive summary predates Section 10/11 entirely
and doesn't mention any of its findings; no single model-comparison table
exists; Model D never had leave-one-out computed), a list of analysis
improvements (recovery-trajectory/shape analysis, not just static
distance-from-peak; real wages; trust-in-EU/state, feasibility unverified;
long-term unemployment; inequality; CI bands; multiple-testing discipline),
storytelling improvements (inverted pyramid, nut-graf, stat callouts,
literature-as-discussion), specific suggestions for the three flagged
sections, and a recommended implementation order.

User responded with a synthesis (agreeing with the three-section framing and
scorecard as top priorities), two additions of their own — multiple-testing
discipline with specific mechanics (FDR correction, confirmatory/exploratory
labels, "survives conceptually and statistically" bar) and emigration/brain-
drain as a structural scarring channel (scoped deliberately narrow: net
migration + age profile + return-migration offset first, not the full
six-part version) — a combined 10-item priority list, and instructions to
start with scorecard + executive-summary rewrite + multiple-testing note.
Also claimed (from an external review) a "duplicated HTML block" — checked
directly (section ids, headings, paragraphs >80 chars, table rows, dd/li
entries, style/script block counts) and found no structural duplication, but
the check surfaced two *real*, different problems worth just as much:

1. The 42.8% arrears "exact match" claim in the diaNEOsis corroboration
   paragraph cited "(Section 8)" — but Section 8 never states that number in
   text; it only appears in Section 10 [now 11]'s near-zero-gap table. Fixed
   to cite the section that actually shows it.
2. "This report's own literature search flagged [unmet medical need] as a
   legitimate outlier candidate" — true internally (publication_strategy.md
   has this) but never actually shown anywhere in the report itself, so the
   self-reference was unverifiable to a reader. Softened to not claim
   internal traceability the report doesn't provide.
3. A near-duplicate sentence: the Answer-to-Q2 box and the literature
   section's Nikolova paragraph both separately stated "household debt and
   transfer-effectiveness added no explanatory power" in near-identical
   language. Trimmed the literature-section copy to a cross-reference instead
   of restating the finding.
4. "Eighteen years after 2008" (Section 11's scarring finding) used the
   current calendar year instead of the data's actual reference year — the
   11.2%-below-peak figure is measured as of 2024 data, sixteen years after
   2008, not eighteen. Fixed.

**Scorecard (script `26_model_scorecard.py`, new section "The scorecard: how
much each layer explains", inserted between Section 9 and the renumbered
Section 11)**: filled the missing Model D leave-one-out (never computed
before — only A/B/C had it, in script 20) and built all six models (A-F)
side by side, in-sample and out-of-sample, on one consistently-built panel.
Confirms A/B/C exactly match the existing nested_loo_summary.csv numbers (a
useful consistency check). New numbers: D's out-of-sample residual is 13.0
(worse than C's 11.6 — debt/transfers hurt out-of-sample despite being null
in-sample too); E's out-of-sample average is 3.6 (previously only the rank,
10/27, was known); F's is 7.1 (rank 4/27, matching what was already
published). Caught mid-build: Model E's *per-year* leave-Greece-out residual
actually goes negative in 2015-2017 (overshoots Greece's difficulty by up to
8.9 points) before swinging positive from 2019 on — a real complication, not
a clean monotonic shrinkage, and different from Model F's residual, which
stays positive and grows smoothly throughout (0.2 to 15.4). This mattered
for the executive-summary rewrite: an early draft claimed a generic "4 to 20"
narrowed range without checking this, caught and corrected before publishing
to avoid exactly the kind of overclaiming error this project has repeatedly
had to walk back. The executive summary now attributes the over-prediction
complication specifically to the financial-pessimism test (Model E), not to
the scarring test (Model F) or generically to "the richer model."

**Multiple-testing discipline (script `27_multiple_testing.py`, new Methods
subsection)**: Benjamini-Hochberg FDR correction applied within three
families of exploratory tests (not across the whole project, which would
conflate unrelated questions): the Section 4 correlation table (17
variables — 13 survive, the 4 that don't are already described as weak in
the text); the Section 11 gap-relation test (9 predictors — real GDP
survives but only just, adjusted p=0.050; arrears, which looked significant
before correction, p=0.070 adjusted, does not survive — confirming the
report's own existing caution about it being Greece-driven); the
acceleration/second-difference check (5 variables, never published in the
main text — only material deprivation survives). Added a labeling
convention — "Core finding," "Descriptive comparison, not a causal test,"
"Exploratory lead, not a core finding" — applied to the scarring finding,
the financial-expectations finding, the near-zero-gap comparison, and the
swing-sensitivity gap-relation test respectively, using the existing
`badge-approx` CSS class rather than inventing new styling.

**Executive summary rewrite**: added a new paragraph ("Why what's left isn't
just pessimism") leading with the three findings the user flagged as the
report's emotional/analytical core — scarring, swing-insensitivity, and the
near-zero-gap contrast — stated explicitly as evidence the residual gap
reflects real conditions, not just pessimism, with financial pessimism
itself named but flagged as the more cautious result. This directly responds
to comment 5. The "what's still unexplained" paragraph was corrected (see
Model E per-year issue above) rather than left with an invented number.

**Not yet done** (remaining items from the 10-item combined list, in the
order agreed): promoting the three sections into full section-level anchors
(currently they're prominent subsections of a renumbered Section 11, not
separate numbered sections — a bigger restructuring deferred on purpose);
recovery-trajectory/shape analysis and chart; emigration/brain-drain
analysis; trust-in-EU/state feasibility check; remaining robustness variables
(real wages, long-term/youth unemployment, inequality, housing tenure);
converting the literature section into a full Discussion/Conclusion with
citations moved inline (the multiple-testing round added one FDR-related
paragraph there but didn't restructure the section itself).

## P0 cleanup (2026-08-20)

Six small fixes from the targeted release-readiness review, all mechanical —
no claims changed, nothing re-analyzed. Full plan and checkboxes in
`docs/todo_plan.md`.

1. **Wrong AROPE cross-reference.** The near-zero-gap subsection cited
   "(AROPE, Section 6)" — Section 6 is Answer to Question 1, which never
   mentions AROPE. AROPE is actually introduced in Section 3. Fixed.
2. **Missing q-label badge.** Every numbered section (1-9, 11) has a small
   numeral badge; the scorecard (Section 10) didn't, despite the TOC
   numbering it "10." Added.
3. **diaNEOsis sample size reconciled, not silently picked.** Re-checked
   both sources directly: the results file is literally named
   `1348q_results-survey_Poverty-DN.xlsx` (n=1,348), while diaNEOsis's own
   summary prose on the page rounds this to "1,300." Kept 1,348 as the
   number actually used in this report's math (it's what the &plusmn;2.7%
   margin was computed from) but the citation and inline mention now both
   state the discrepancy explicitly rather than picking one silently.
4. **Badge added to the swing-sensitivity finding.** Its own follow-up test
   was labeled "Exploratory lead"; the primary finding had no label at all.
   Now tagged "Descriptive comparison, not a causal test," matching the
   near-zero-gap finding's evidentiary status.
5. **"Scarring/pessimism story" softened.** That phrase paired a hard-data
   finding (scarring) and a heavily-caveated subjective one (pessimism) as
   if they were one category. Reworded to distinguish them explicitly and
   point forward to the pessimism subsection's caveat.
6. **Bridge sentences added** in three places: the scorecard's lede now
   tells the reader Models E/F introduce two new variables explained in the
   very next section (they were previously named in the table with zero
   context); the pessimism subsection got an intro paragraph recapping the
   two findings before it (it previously had none, unlike every other
   subsection); the near-zero-gap subsection's opening line now explicitly
   recaps "the three findings above" before pivoting to the contrastive
   framing.

Verified tag balance before republishing, per established practice. Commit:
`p0-report-cleanup`.

## P1a: recovery trajectory (2026-08-20)

Script `28_recovery_trajectory.py`. First draft had a real bug: for
countries whose all-time GDP peak fell in 2024 itself (i.e. still climbing),
the trough-detection trivially set trough=peak=2024, which wiped out every
genuine historical recovery event and produced a nonsensical "0 countries
recovered from a real dip." Caught before reporting anything, fixed by
separating two distinct questions and computing each properly:

1. **Currently below own all-time peak?** — reproduces the already-published
   Section 11 numbers exactly (Greece 11.2%, Estonia 7.1%, Luxembourg 6.1%,
   etc.), used as a consistency check on the new script.
2. **How long to recover from the worst crisis-era drawdown?** — uses
   max-drawdown detection (same method as the older exploratory script 12),
   which correctly finds the crisis trough for a country even if it's since
   climbed to a brand-new peak. Result: 23 of 27 EU countries had a real
   crisis dip (mostly 2009 or 2020) and recovered; median recovery time 3
   years (range 1-7). Only 3 never recovered from their worst dip: Greece
   (26.9% decline, 2020 trough, still not recovered), Luxembourg (a much
   smaller, very recent 6.1% dip — not a comparable case to Greece), and
   Finland (8.5% decline in 2009, never regained its 2008 peak — closest
   approach was 99.2% in 2022 before slipping again). Poland had zero
   drawdown across the whole window.

Also built an indexed-trajectory chart (each country's real GDP/capita
indexed to its own peak = 100, 2008-2024) as a Chart.js preview, shown to
the user directly rather than only described — Greece's line visibly
separates from the EU field around 2011 and never rejoins it.

**Checkpoint decision**: genuinely strengthens the report (the "3-year
median vs. Greece's 16 years and counting" framing is sharper than the
existing static 11.2% number) and the data is internally consistent, so
recommended for integration. User confirmed: hold the actual report
integration for the batched P3 step rather than doing it now, so more P1
items can be checkpointed first without repeatedly touching report.html.
New data: `recovery_trajectory.csv`, `recovery_indexed_trajectories.csv`.

## P1b: migration/brain drain (2026-08-20)

Script `29_migration_brain_drain.py`. Scoped narrow per the agreed plan: net
migration, age profile if comparable, return migration if comparable.

**Rejected first**: Eurostat's headline "net migration rate" (`demo_gind`,
indicator `MIGTRT`) is officially "net migration plus statistical
adjustment" — a residual absorbing census/register revisions, not just real
migration. For Greece it's strongly *positive* every year 2011-2024 (+150k
to +240k), directly contradicting Greece's own falling population and the
well-documented emigration story. Caught by cross-checking against total
population change (`GROW`) and natural change (`NATGROW`) before using it.

**Used instead**: `migr_emi1ctz` / `migr_imm1ctz`, filtered to
`citizen=NAT` (the reporting country's own nationals) and
`agedef=COMPLET`, 2008-2024. All 27 EU countries report into these tables
with near-full coverage — genuinely comparable. Net outflow of Greek
nationals rose from under 6,000/year (2008-2009) to a peak of 44,502 in
2012, stayed elevated through the late 2010s, then declined and **flipped
to a net inflow in 2023 (+9,160 returning) and 2024 (+19,900 returning)** —
first positive years since before the crisis. Cumulative net loss
2008-2024: 290,281 people, 2.6% of Greece's 2008 population.

**Age profile: not usable, reported honestly rather than forced.** Eurostat
only publishes age-band breakdowns for *all* emigrants regardless of
citizenship, not for Greek nationals specifically — using it would conflate
Greek citizens leaving with foreign residents leaving. Per the scoping rule,
not used; any age/education claim in the report is attributed to the
OECD/census source instead (see below), never to this table.

**Cross-country check**: ranked by cumulative net emigration of nationals as
% of population (25 countries, >=15 years coverage), Greece is 5th of 25
(2.7%) — behind Lithuania (8.3%), Croatia (5.9%), Romania (4.3%), Luxembourg
(a different kind of case). Not the most extreme EU case on this dimension.

**Checkpoint decision**: integrate, with careful framing (per user
instructions) — not "worst in the EU," but "large, crisis-linked, sustained
over a decade, with a genuine recent reversal that doesn't erase the
cumulative loss."

## P1a + P1b integration (2026-08-20)

Both integrated together per user's explicit ordering (P1a first, as the
stronger/cleaner result; P1b second, as a secondary structural-scarring
channel), with additional literature verification requested before
integration.

**Chart infrastructure**: extended the existing `lineChart()` JS function
with three small, backward-compatible additions — per-series `showLabel`
(suppress end-label/dot for background series), per-series `opacity`/`width`
(faint background lines), and a chart-level `tooltipSeries` override (so a
27-line chart's hover only shows Greece, not all 27 countries). Extended
`barChart()` with an optional `valFmt` formatter (existing calls unaffected,
default unchanged) — needed because the migration chart's values are
population counts (thousands), not percentages, and `+34225.0` reads badly;
now renders `+34,225`. Caught the formatter wasn't actually wired into the
migration chart's call site on first pass — verified via browser screenshot
before publishing, not assumed from the code alone.

**New report_data.json entries**: `recovery_trajectory` (27 countries x 17
years, indexed to own peak) and `migration_nationals` (Greece's
emigration/immigration/net by year), added via `09_export_report_data.py`.

**Recovery trajectory** now leads "Still below its own pre-crisis peak":
the 3-years-vs-16-years framing, the indexed-trajectory chart (Greece
highlighted, other 26 countries faint), Finland/Luxembourg as honest
complications, and a literature box grounding the "not just pessimism"
argument in Gourinchas/Philippon/Vayanos (2016, VoxEU/CEPR — verified
directly: "one of the worst crises in history... significantly more severe
and protracted" than any comparable trifecta crisis since 1980, 26%
cumulative real income decline 2007-2013) and the ESM's own explainer
(verified directly: cheap euro-era borrowing delayed reform, weak tax
administration, 2009 data-misreporting revelation triggered market-access
loss).

**Migration** added as new subsection "The crisis also became an exit
route" right after, with the chart, the core finding, the cross-country
honesty check, and a careful stock-vs-flow explanation citing the OECD 2026
"Talent Abroad" review (verified directly: 46,000 returned vs 37,000 left
in 2023, "first positive year since the crisis began"; returnees 54% aged
20-39, three-fifths tertiary-educated vs 23% among never-emigrated Greek
residents — explicitly attributed to OECD/census data, not to this
project's own Eurostat flow table) alongside the existing Greekonomics.gr
stock-based "reversal was premature" finding, plus Kathimerini's 3 July 2026
coverage of the same OECD report (verified: 2024 figure of "20,000 more
returned than left" essentially matches this project's own computed figure
of 19,852).

**PDF access saga, worth recording**: the user pointed at Pratsinakis (2022,
"Greece's Emigration During the Crisis Beyond the Brain Drain," in Kousis,
Chatzidaki & Kafetsios eds., *Challenging Mobilities... The Case of
Greece*, IMISCOE/Springer, open access) via a paywalled Springer link first
(inaccessible), then a local PDF in `~/Downloads/` — which failed with
`EPERM` on every tool tried (Read, cp, even plain `cat`/Python `open()`),
a hard macOS Downloads-folder sandbox restriction on this process, not
fixable by switching tools. Told the user directly rather than retry
pointlessly; they moved the file to `docs/978-3-031-11574-5.pdf`, which
resolved it immediately. Full chapter read and used substantively — it's a
better, more directly-on-point source than the Labrianidis & Vogiatzis
(2013) piece for the "brain drain is a real but incomplete frame" argument
(kept both; they're complementary). Concrete additions: only 27% of
post-2010 emigrants in Pratsinakis's own 996-respondent survey said their
decision was "enforced by circumstances" (43% said they'd always wanted to
leave regardless); two in three crisis-era emigrants held a university
degree (Labrianidis & Pratsinakis 2016 survey, cited within); highly
educated Greeks' unemployment rose to ~4x the EU-28 average during the
crisis.

**A genuine three-way shape discrepancy, reported honestly rather than
smoothed over**: this project's own Eurostat extraction shows Greek
national emigration peaking in 2012 then declining fairly steadily. Both
the OECD 2026 review and Pratsinakis (2022) — independently, using
Eurostat data pulled at different times/vintages — describe a 2012 peak
followed by a plateau around 46,000-56,000 through the late 2010s, not a
steady decline. All three agree on the crisis-era surge and the 2012 peak;
they disagree on exactly how fast the outflow eased afterward. Not
resolved (would need re-querying multiple Eurostat table variants) —
stated as an open discrepancy in the report itself rather than picking the
version that reads more cleanly.

**Also fixed in passing**: migration bar-chart value formatting (see chart
infrastructure note above).

Republished after each verification step; tag balance checked before every
publish, per established practice. Commits: `p1a-recovery-trajectory-
analysis` (analysis only), then `p1a-p1b-report-integration` (charts +
prose + citations, both P1a and P1b together).

## P1c: trust in state/EU (2026-08-20)

**Feasibility check, done properly rather than guessed**: searched
Eurostat's actual catalogue (`toc/txt` endpoint) for "trust"/"confidence"
in institutions rather than guessing dataset codes blind. Result: Eurostat's
entire "Trust in institutions and public services" folder (`qol_gov_ins`)
contains exactly one dataset, `ilc_pw03b`, covering exactly one year, 2013.
Confirmed by direct fetch (domains available: `LEG`, `POLC`, `POLIT` — legal
system, police, political system; no EU-institutions-specific domain).
Eurostat's only *ongoing* annual trust series (`ilc_pw03`/`ilc_pw04`, 2013,
2018, then annually 2021-2025) measures interpersonal trust ("trust in
other people"), a different construct — not substituted for institutional
trust.

Pulled the 2013 snapshot anyway for completeness: Greece ranks 4th-lowest
of 28 on political-system trust (2.0/10), behind Portugal (1.7), Slovenia
(1.8), and Spain (1.9) — the bottom five are exactly the crisis-hit
Southern European countries together. Not distinctively worse than
comparable countries on this one data point, and a single year can't show
a trend — **feasibility check failed against the stated bar** (comparable
source, years, coverage, method consistency). Documented in Methods as
checked-and-infeasible, same pattern as real wages and housing tenure.

**User did independent literature research and found the right answer**:
don't model it, but do add it as literature-backed context, since Eurostat
failing as a panel source doesn't mean the broader trust literature has
nothing to say. Verified the two load-bearing sources directly before
writing anything:

- **Ervasti, Kouvo & Venetoklis (2019, *Social Indicators Research*, cited
  190x)** — confirmed via Google's indexed abstract (Springer paywalled
  directly): using ESS data 2002-2011, Greece's crisis sharply damaged
  trust in political/impartial institutions while interpersonal trust held
  steady. Institutional, not general-temperament, damage.
- **OECD (2026), "Survey on Drivers of Trust in Public Institutions 2026
  Results: Greece"** — read directly via browser, not summarized. The
  strongest single source found this round: pre-crisis trust averaged 44%
  (not particularly high — a single 2004 Olympics-year spike above 50% is
  the exception, not the baseline), collapsed to a historical low of 7% in
  2012 (the same year this project's own analysis independently identifies
  as Greece's deepest economic trough — a genuine, unplanned cross-check),
  recovered only to 37% at its best (2015, 2020), never regained the
  pre-2008 average, and has fallen *again* since 2023 (32% to 24%) despite
  strong recent macroeconomic performance — a disconnect the OECD's own
  account calls puzzling. Sourced from Eurobarometer via Tufiș, Ghica &
  Radu (2024), Harvard Dataverse.
- **Economou et al. (2014, *Social Science & Medicine*, cited 76x)** —
  confirmed via indexed abstract (institutional + interpersonal trust
  linked to mental illness during the crisis, nationwide Greek study);
  cited lightly, not load-bearing.

**A real framing correction, caught before publishing**: my first draft led
with "trust collapsed to 7% in 2012" without first establishing the
pre-crisis baseline wasn't itself high — exactly the "Greece was high-trust
then suddenly became low-trust" misreading the user flagged as a risk.
Rewrote using their explicit four-part structure (pre-existing condition →
crisis shock → aftermath → interpretation), leading with "trust was not
particularly high before the crisis" using the OECD source's own words,
*then* the 2012 collapse, *then* the fragile partial recovery. This was a
genuine catch of a claim I'd have gotten subtly wrong otherwise, not just
a style note.

**Where it landed**: a method-aside in Section 11 (full four-part
treatment), a short pointer in the literature section (cross-referencing
Section 11 rather than repeating it), and a Methods entry explaining why it
wasn't modeled — using language close to what the user proposed directly.
Not added as Model G, not charted, not given a badge (it's narrative
context, not a finding this report tests). Three new citations added.

This closes out all of P1 (P1a, P1b, P1c). Tag balance verified before
publishing, per established practice.

## P2a: real wages (2026-08-20/21)

First item under P2 (labor-market/distribution extensions). User's explicit
brief on how to treat it: not minimum-touch — a "major evidence point" in
Section 11, added to the correlation/robustness table with both level and
first-difference readings, a cross-country chart, and a multicollinearity
+ model-feasibility check *before* deciding whether it earns a scorecard
column. Built as `30_real_wages.py`: nominal compensation per employee
(`nama_10_lp_ulc`) deflated by HICP (`prc_hicp_aind`), rebased to each of
27 EU countries' own 2008=100. Full detail of the dataset codes and
construction in `docs/data_sources.md` (P2a addition).

**Headline finding**: by 2024 Greece's real wage index stood at 68.2
(2008=100) — a 31.8% real-terms shortfall, the largest of any EU country
and not close (Hungary next-worst at 74.2, Italy third at 90.6; every other
country had recovered to 2008 level or above). Peak was 2009 (101.7),
trough 2023 (66.4). Correlation with subjective poverty: strong at the
level (r=-0.79, p<0.0001, n=22), weak and not significant on first
differences (r=-0.21, p=0.35) — same pattern the report already flags for
several other variables (a level correlation likely reflecting a shared
crisis-era trend, not tight year-to-year co-movement).

**Multicollinearity + model-feasibility check, done before touching the
scorecard**: real wages correlate only modestly with the existing panel
predictors (PPS income r=-0.12, real GDP r=-0.12, scarring stock r=-0.33) —
not redundant with them. But adding it to Model C barely moves anything:
R² 0.892→0.893, its own coefficient isn't significant (p=0.33), and
Greece's leave-one-out residual gap only inches down (11.6→11.2, rank
unchanged at 1st of 27). Honest null result for the modeling question.
**Decision: not added to the scorecard.** Kept as a strong descriptive
finding about Greece's own paycheck recovery, documented in a new Methods
subsection explaining the reasoning so the "why isn't this a model
variable if the level correlation is r=-0.79" question is answered
directly rather than left implicit.

**Where it landed**: a new Section 11 subsection ("The paycheck didn't
recover either") placed after the recovery-trajectory content and before
migration, with a 27-country line chart (Greece highlighted, other 26
faint) capped at index 160 with a caption explaining why a few
Eastern-European catch-up-growth countries (Bulgaria to 267, Lithuania to
151) run off the top of the frame; a new row in the Section 4
correlation/robustness table; and the Methods subsection described above.

**Two real pipeline bugs found and fixed at the root, not worked around**,
while re-running `04_merge_all.py` to pick up the new
`real_wage_idx2008.csv`: (1) it crashed on pre-existing Greece-only raw
files lacking a `geo` column (`AttributeError`) — fixed with an explicit
skip-and-log check, not a try/except; (2) it crashed on
`panel_financial_expectations.csv`, which uses `year` instead of `time` —
fixed with flexible time-column detection. Both were latent bugs that
predate this round (those raw files existed already; `04` just hadn't been
re-run since). Also re-learned the hard way that `04` rebuilds
`analysis_dataset.csv` from scratch and silently wipes the derived column
`05_threshold_hypothesis.py` writes back in — caught when the AROP
threshold correlation row vanished, fixed by re-running `05` after `04` in
the documented order. Now called out explicitly as a README ordering
caveat so it doesn't get rediscovered the same way next time.

**A genuine display bug caught during final verification, not
introduced by this round but exposed by it**: `09_export_report_data.py`'s
`clean()` helper rounds every float — including p-values — to 2 decimals
before export. The real wages detrended p-value is 0.0489, genuinely below
the 0.05 significance threshold, but 2-decimal rounding turned it into
exactly `0.05`, and the report's JS does a strict `p < 0.05` check for the
"(n.s.)" label — so `0.05 < 0.05` is false and the table incorrectly
flagged a real, if marginal, significant result as not significant. Checked
every other p-value in the robustness table for the same failure mode
(compare rounded-to-2dp threshold crossing against the true value); real
wages' detrended figure was the only one affected. Fixed at the root: added
a separate `clean_p()` that keeps 4 decimals for every exported p-value
(correlations and robustness both), regenerated `report_data.json`,
re-injected, and verified in-browser that the table now matches the prose.
General fix, not real-wages-specific — protects any future variable whose
p-value lands near a rounding-sensitive boundary.

Tag balance and in-browser chart/table rendering verified before
publishing. Republished with label "P2a: real wages integration + p-value
precision fix".

Remaining under P2, not started: youth unemployment, long-term
unemployment, income inequality (Gini/S80:S20), housing tenure. Per the
same checkpoint discipline used throughout, waiting for the user's
go-ahead before starting the next one.

## P2b: long-term unemployment (2026-08-21)

User's explicit sequencing after P2a: long-term unemployment first among
the remaining P2 items, "the most conceptually aligned with scarring,"
before youth unemployment, inequality, and housing tenure. Built as
`31_long_term_unemployment.py`: Eurostat's `une_ltu_a` (unemployed 12
months or more, % of active population), full 27-country coverage,
2009&ndash;2024.

**This one changed the sequence.** Unlike real wages, the checkpoint
analysis came back as a genuine scorecard candidate, not just descriptive
evidence: level correlation r=0.93 (strongest in the whole project,
displacing real household income from 1st place), first-difference r=0.92
(the first variable in this project whose year-to-year changes also track
subjective poverty tightly, not just the shared level), detrended r=0.86.
All three survive FDR correction comfortably.

**Multicollinearity was real and had to be handled carefully.** Long-term
unemployment correlates strongly with headline unemployment (r=0.91 across
the full panel, r=0.998 for Greece's own series alone — mechanically
expected, since by the mid-2010s most of Greece's unemployment *was*
long-term). Two specs tested: adding long-term unemployment *alongside*
headline unemployment improves fit further (R&sup2; 0.919, Greece's gap to
2.3) but destabilizes headline unemployment's own coefficient (flips
negative, loses significance — VIF &asymp;8&ndash;9 for both). *Replacing*
headline unemployment with long-term unemployment instead (Model C-LTU)
avoids that: R&sup2; 0.914, Greece's out-of-sample gap 11.6&rarr;3.9, rank
1st&rarr;6th of 27, with clean coefficients throughout. Confirmed the
swap-model coefficient is not a fluke by refitting 27 times, once per
excluded country: the long-term-unemployment coefficient never changed
sign and was never less significant than p&lt;0.001, including the refit
that excludes Greece itself.

**User's explicit integration brief, after seeing these results**: treat
long-term unemployment as a core model candidate, not descriptive-only.
Use the replacement spec (C-LTU) as preferred, the additive spec as
robustness only. Add a body subsection near scarring/recovery. Reframe the
GDP-scarring subsection as macro context now that long-term unemployment
looks like the sharper household-facing mechanism. Reframe financial
expectations to acknowledge overlap rather than claim independent
explanatory power. Update the executive summary and Section 12 conclusion.
Before finalizing text, run: the full C-LTU scorecard row, the full
27-country leave-one-out ranking (not just Greece's), FDR status for the
correlation, whether C-LTU still behaves well combined with the
scarring-stock and expectations/wealth models, and whether long-term
unemployment reduces the apparent role of financial expectations.

**That follow-up battery** (`32_ltu_model_test.py`) found: (1) adding the
scarring-stock variable on top of Model C-LTU changes nothing (R&sup2;
unchanged, p=0.605) — long-term unemployment appears to subsume most of
what the scarring stock was capturing; (2) adding financial expectations
and saving rate on top of Model C-LTU still improves fit (R&sup2; 0.920)
and pushes Greece's residual to -1.75 (rank 19th) — but financial
expectations' own coefficient weakens from p=0.021 (with headline
unemployment) to p=0.062 (with long-term unemployment), confirming real
overlap. Treated that combined result cautiously in the report (a
directional finding, not a headline number) rather than touting "Greece's
gap basically disappears" — it's the most heavily stacked spec tested, on
a smaller sample (n=265), and overclaiming it risked looking engineered
rather than clean.

**Where it landed**: a new Section 11 subsection ("The crisis left people
unemployed for years, not months") placed right after the GDP-scarring
subsection, with a 27-country chart and a compact before/after table
showing the outlier ranking reshuffle (Cyprus, Luxembourg, Portugal,
Czechia, and Belgium all now rank above Greece under C-LTU); a new
highlighted row in the Section 10 scorecard table; a reframed GDP-scarring
method-aside noting the redundancy once long-term unemployment is
included; a softened financial-expectations core finding acknowledging the
overlap; new paragraphs in the executive summary and the Section 12
"Answer to Question 2" conclusion box; a new Section 4 callout since
long-term unemployment is now the top row in that correlation table too;
and a full Methods subsection covering the multicollinearity check,
coefficient-stability test, and both interaction checks. Also caught and
fixed the Methods "13 of 17 survive FDR correction" line, stale since the
P2a round added real wages without updating this count — now correctly
"15 of 19."

**One real bug caught during chart verification**: the first attempt at
the 27-country long-term-unemployment chart rendered only 2 of 27 lines.
Cause: `09_export_report_data.py`'s new `ltu_trajectory` bundle wasn't
year-floored the way `real_wages_trajectory` is, so its first row (2003)
only had data for France — and the chart's JS derives its list of
countries to draw from the *first* row's keys. Fixed by filtering the
export to `time >= 2009`, the year full 27-country coverage actually
begins (confirmed directly against the raw fetch, not assumed), matching
the precedent already set for real wages. Verified afterward that all 27
lines render.

Tag balance and in-browser chart/table rendering verified before
publishing. Republished with label "P2b: long-term unemployment as central
finding".

Remaining under P2, not started: youth unemployment, income inequality
(Gini/S80:S20), housing tenure. Per the same checkpoint discipline used
throughout, waiting for the user's go-ahead before starting the next one.

## P2b review: Section 11 reorder (2026-08-21)

Before moving to youth unemployment, user asked for a mini-review of the
P2b integration: a claim audit (every LTU number cross-checked against the
underlying data files), a narrative audit, a scorecard audit, and a
Section 11 flow check. Everything passed except the flow check: the
intended story ("the economy did not recover, pay did not recover,
unemployment became long-term, people left, expectations weakened")
requires real wages to come before long-term unemployment, but the actual
subsection order had long-term unemployment first (my own earlier design
choice, reasoning that it should sit immediately next to the GDP
subsection it reframes). Fixed by swapping the two subsections, adding a
short bridge sentence, and correcting a "long-term unemployment, next"
forward-reference in the GDP subsection that assumed the old order.
Verified both charts still render in full after the move. No other issues
found. Republished.

## P2c: youth unemployment (2026-08-21)

User's brief: test youth unemployment specifically against long-term
unemployment and migration, not as a generic hardship variable — the
hypothesis being youth-specific labor-market scarring and exit pressure,
not redundant general hardship. Six-point checkpoint scope: feasibility,
descriptive, correlation (with FDR status), overlap (vs headline
unemployment, LTU, migration, VIF), model tests (swap and add-to-C-LTU),
and an explicit interpretation decision tree (strong+distinct → new
subsection; strong+redundant → Methods/context only; weak → documented and
dropped). Built as `33_youth_unemployment.py`: Eurostat's `une_rt_a`
(ages 15&ndash;24, % of youth *labor force*, not youth population — a
distinct, sometimes-confused Eurostat product), full 27-country coverage,
2009&ndash;2024.

**Result matched the user's own prior expectation almost exactly.**
Descriptively real: Greece peaked at 59.2% in 2013, fell to 22.5% by 2024.
Notably, unlike nearly every other variable in this report, Greece is *not*
currently the EU's worst on this one — Spain overtook it (26.5%), and
Greece ranks only 4th-highest. Correlation with subjective poverty is
genuinely strong (level r=0.71, first-diff r=0.79, detrended r=0.81, all
survive FDR) but clearly weaker than long-term unemployment's r=0.93/0.92/
0.86 at every time scale. Overlap is severe: r=0.99 with both headline
unemployment and long-term unemployment for Greece's own series, r=0.92
and r=0.85 respectively panel-wide.

**Model tests were decisive.** Replacing headline unemployment with youth
unemployment in Model C leaves Greece the largest out-of-sample outlier in
the EU, barely moved from baseline (R&sup2; 0.899 vs 0.892, gap 10.8 vs
11.6, rank unchanged at 1st of 27) — nowhere near long-term unemployment's
swap result (R&sup2; 0.914, gap 3.9, rank 6th). Added on top of Model
C-LTU as a robustness check, it changes almost nothing (R&sup2; unchanged
at 0.914) and its own coefficient is not statistically significant
(p=0.815, VIF 4.7) — once long-term unemployment is already in the model,
youth unemployment adds no further independent explanatory power.
**Not added to the scorecard.**

**One reconciliation caught before reporting back:** the checkpoint
script's own quick detrended-correlation calculation (r=0.93) didn't match
the official pipeline's number (r=0.81) computed via
`10_robustness_correlations.py`. Traced to a real methodological
difference, not a bug: the checkpoint script detrended subjective poverty
using only the 16 years where youth-unemployment data exists, while the
pipeline's `detrend()` function fits subjective poverty's trend line over
its full 23-year series and evaluates it at the overlapping years — the
correct, consistent-with-every-other-variable approach. Used the pipeline
number in the writeup and in the report, not the checkpoint script's.

**Per the user's decision tree, this landed as "strong but redundant with
LTU"** — not a new scorecard model, and deliberately not given its own
Section 11 subsection with a chart (that would overstate its independent
contribution sitting next to long-term unemployment). Instead: (1) added
as a Section 4 correlation/robustness table row using the official
pipeline numbers, confirmed to survive FDR correction (16 of 20 variables
now survive, up from 15 of 19); (2) a full Methods checkpoint entry
("Youth unemployment: checked, strongly correlated, and not a scorecard
model") covering the denominator clarification, correlation, overlap, and
model-test numbers; (3) a short supporting-context note added to the
*existing* migration subsection, using close to the user's own suggested
wording — youth unemployment's 2013 peak fell within a year of the 2012
emigration peak, offered as a descriptive, non-causal push-factor
connection. No new chart, no new subsection.

As the user put it: this is a useful result precisely because it shows the
report's discipline — not every strongly-correlated variable becomes a
headline finding when it's redundant with one already in the model.
Long-term unemployment remains the cleaner structural labor-market scar.

Tag balance and in-browser rendering verified before publishing.
Republished.

Remaining under P2, not started: income inequality (Gini/S80:S20), housing
tenure, and a new item the user proposed mid-session — P2e: wage-adjusted
cost-of-living pressure (Eurostat price-level indices vs. the real-wages
work already done, sequenced after labor-market items and before housing
tenure; see `docs/todo_plan.md` for the full scoping note). Per the same
checkpoint discipline used throughout, waiting for the user's go-ahead
before starting the next one.

## P2e: wage-adjusted cost-of-living pressure (2026-08-21)

User's brief, sent mid-session: not "are Greek supermarket prices high"
but "how expensive are essential goods and services relative to Greek
wages" — price level (Eurostat's comparative price level indices) set
against wage level (nominal compensation per employee, the same series
already fetched for real wages), category by category. Explicit six-point
checkpoint scope: feasibility, descriptive cross-country, the wage-adjusted
basket itself, a time-series angle via HICP categories, an explicit
low-expectation on model role ("I would not expect this to become a
scorecard variable immediately"), and report placement near real wages.

Built as `34_wage_adjusted_cost_of_living.py`: Eurostat's
`prc_ppp_ind_1` (`PLI_EU27_2020`, comparative price levels, EU27=100) for
six categories — overall consumption, food, housing/utilities, transport,
restaurants, information &amp; communication — against a wage benchmark
built from `nama_10_lp_ulc` (Greece's nominal compensation per employee as
a share of the EU27 average).

**Real feasibility constraint, checked and reported honestly rather than
glossed over:** the granular category-level price indices have full
27-country coverage for only three years, 2022&ndash;2024. Only the
broader "overall household consumption" category has a long enough series
(2000&ndash;2024) for any real time-series work. This ruled out a proper
cross-country panel-regression model test for the category detail from
the start &mdash; not enough time variation to support the year-fixed-
effects setup used everywhere else in this report.

**The core finding is a clean reversal, and turned out stronger than
either of us expected going in.** On raw price level, Greece ranks only
18th-most-expensive of 27 EU countries on overall consumption &mdash; not
an expensive country in absolute terms, and in several categories (housing,
transport, restaurants) its raw prices sit well below the EU average.
But Greek wages are so far below the EU average (48.3% of it, 4th-lowest
of 27) that once prices are scaled by wage level, the picture reverses
completely: Greece has the EU's **highest** wage-adjusted price pressure
on overall consumption, and ranks 1st or 2nd of 27 in every individual
category tested &mdash; 2nd on food (behind Bulgaria), 2nd on housing
(behind Czechia), 1st on transport, restaurants, and communication. The
reversal holds even in the categories where Greece's raw prices are
cheapest relative to the EU, which is the whole point: prices don't need
to be high for the squeeze to be severe when wages are this low.

**Time series, the version the user specifically asked for:** since 2008,
Greek nominal wages are still 13.1% below their 2008 level (index 86.9,
2008=100 &mdash; computed directly from the nominal compensation series,
not backed out from the real-wage index), while nominal food prices rose
41.6%, housing/energy 33.6%, and the general HICP 27.5% over the same
span. The paycheck shrank in absolute euro terms while the receipt grew.

**Model role, per the user's own stated low expectation:** confirmed
correct. The one series with enough years to check &mdash; overall
consumption, wage-adjusted &mdash; correlates with subjective poverty at
the level (r=0.696, p=0.0003) but not on year-to-year changes (r=&minus;0.063,
not significant), the same level-only pattern already documented for real
wages, which for real wages translated into zero independent explanatory
power once actually tested against Model C. Given that precedent and the
short category-level time series, no formal cross-country panel test was
run. **Not added to the scorecard.**

**Where it landed, following the user's explicit integration plan almost
verbatim:** a new Section 11 subsection, "A smaller paycheck facing
ordinary prices," placed between real wages and long-term unemployment
(matching where it was checked in the checkpoint, and keeping the
"economy &rarr; pay &rarr; prices &rarr; jobs &rarr; emigration" narrative
arc intact); a 2024 table showing raw price level, EU rank, wage-adjusted
pressure, and wage-adjusted rank side by side for all six categories, so
the reversal (18th on price, 1st on pressure) is directly visible; a
two-sentence executive-summary paragraph, since the user called this "a
headline supporting point in the Greek-perspective argument"; and a full
Methods entry covering the construction, the coverage constraint, what the
measure is and isn't (a harmonized price-level comparison, not a household
budget survey or real receipts), and why it wasn't tested as a scorecard
model.

One title correction, agreed with the user before integrating: the
original working title ("ordinary Greek prices near European levels") was
inaccurate, since Greek prices are frequently *below* the EU average, not
near it. The corrected framing &mdash; prices don't have to be high for
the squeeze to be severe when wages are this low &mdash; is both more
accurate and, per the user, more powerful.

Tag balance and in-browser rendering verified before publishing.
Republished with label "P2e: wage-adjusted cost-of-living pressure".

Remaining under P2, not started: income inequality (Gini/S80:S20) and
housing tenure. Per the user's explicit instruction, housing tenure is to
be treated as its own separate checkpoint (a different question — who is
exposed to housing costs, and how tenure/family structure changes the
burden — likely more complex to interpret than P2e), not combined with any
other item. Waiting for the user's go-ahead before starting the next one.

## Housing tenure (2026-08-21)

Started as its own checkpoint per the user's explicit instruction — a
different question from P2e ("who is exposed to housing costs, and how
does tenure/family structure change the burden"), not combined with it.
Built as `35_housing_tenure.py`: Eurostat's `ilc_lvho07c` (housing cost
overburden by tenure status) and `ilc_lvho02` (tenure distribution), full
27-country coverage, 15&ndash;22 years. Confirmed directly that the
`ilc_lvho07c` "TOTAL" row is the exact same series already powering the
report's `housing_cost_overburden` variable (used throughout Sections
7&ndash;11 and in the cross-country model) &mdash; this is a drill-down of
an already-central variable, not an unrelated new one.

**The headline result, and it's a genuine surprise given the report's
established "renters worse off" prior:** Greece's mortgage-free-owner
overburden rate is 25.7% &mdash; the EU's highest by a wide margin (next:
Sweden, 14.0%; typical EU range 1&ndash;7%). Homeownership, which shields
households from housing-cost pressure almost everywhere else in the EU,
does not do that in Greece. Renters are still worse off in absolute terms
(37.4% overburdened) &mdash; but the owner-renter *gap* is one of the EU's
narrowest (Greece ranks 22nd of 27), because owners are unusually burdened
too, not because renters are spared.

**A genuine judgment call, resolved by the user rather than assumed:**
whether the small owner-renter gap is a complication to the "renters have
it worse" story or the actual headline. Flagged this explicitly as an
open framing question when reporting the checkpoint back. User's answer:
the small gap is the strongest part of the finding, not a complication
&mdash; it's what makes Greece structurally different from the rest of
the EU (tenure normally separates the exposed from the protected; in
Greece it doesn't), and integration proceeded on that basis.

**Multicollinearity check and model test, done before ruling on scorecard
inclusion:** mortgage-free-owner overburden correlates at r=0.91
(panel-wide) and r=0.88 (Greece-only) with the `housing_cost_overburden`
variable already in Model C-LTU &mdash; expected, since it's a
subcomponent of that total by construction. Added on top of Model C-LTU,
R&sup2; barely moves (0.914&rarr;0.917), Greece's out-of-sample gap gets
slightly worse rather than better (3.9&rarr;5.1), and the coefficient
isn't significant (p=0.141). **Not added to the scorecard** &mdash; the
housing-cost channel is already captured; this adds texture to why it's
so severe, not new independent explanatory power. Correlation reported
separately and honestly labeled descriptive, not causal: Greece-only over
time r=0.90 (18 years), cross-country single-year (2024) r=0.66.

**One real data-quality issue caught and handled, not glossed over:** the
renter-specific subseries in Greece's historical data show implausible
year-to-year swings before roughly 2021 (market-rate renter overburden:
23.6% in 2007, 87.5% in 2014) &mdash; almost certainly a small-subsample
artifact in a historically ownership-dominated country, not a real
one-year swing in housing conditions. Handled by relying only on the
stable 2022&ndash;2024 window for the by-tenure comparison, not the full
historical series, and documenting the issue explicitly in Methods rather
than silently using a noisy number.

**Where it landed**, per the user's explicit placement instruction: a new
Section 11 subsection, "Owning your home does not fully protect you
here," placed between the wage-adjusted-pricing subsection and long-term
unemployment (extending the narrative arc: economy &rarr; pay &rarr;
prices &rarr; housing tenure &rarr; jobs &rarr; emigration &rarr;
sentiment) &mdash; a table of the four headline overburden figures, one
sentence on ownership structure (near-EU-average ownership rate but much
lower mortgage penetration, "plausibly consistent with" inherited/
self-built housing rather than asserted as fact), the correlation
figures labeled descriptive, and a full Methods entry. No executive
summary change this round &mdash; the user's integration instructions
didn't call for one, unlike P2e, so none was added.

Tag balance and in-browser rendering verified before publishing.
Republished with label "Housing tenure: ownership doesn't fully protect in
Greece".

Remaining under P2, not started: income inequality (Gini/S80:S20) — the
last item on the original P2 list. Per the same checkpoint discipline used
throughout, waiting for the user's go-ahead before starting.

## Income inequality (2026-08-21) — final P2 item

User's explicit framing going in: expect this to be less central than
LTU, wages/prices, or housing tenure, but worth checking because it tests
whether the average-level measures already in the model are hiding a
worse-off tail. Same five-point checkpoint structure as youth unemployment
and housing tenure: feasibility, descriptive, correlation (with FDR),
model test, interpretation.

Built as `36_income_inequality.py`: Eurostat's `ilc_di11` (S80/S20 income
quintile share ratio, full 27-country coverage 2003&ndash;2024) and
`ilc_di12` (Gini coefficient, age-broken-down series, shorter coverage
2014&ndash;2024 only &mdash; checked directly, not assumed).

**Result matched the user's expectation closely, and turned out to be a
genuinely clean null.** Greece is elevated but not extreme on inequality
&mdash; 6th-highest of 27 EU countries on both measures. Its own S80/S20
has actually *fallen* since 2003 (6.38&rarr;5.27), including a substantial
decline since the 2012 crisis-era peak (6.63) &mdash; the Greek crisis
compressed incomes broadly rather than widening the gap at the top. A
striking cross-country cross-check: Bulgaria has the EU's highest
inequality (6.96) but far *lower* subjective poverty (37.4%) than Greece
(66.7%, only moderately unequal at 5.27) &mdash; inequality level and
subjective poverty are not tracking together across countries. The level
correlation with subjective poverty is weak and does not survive FDR
correction (r=0.15, raw p=0.51, adjusted p=0.54) &mdash; the only variable
in the whole correlation table with a non-significant level reading, a
genuine outlier from this project's usual pattern. Added to Model C-LTU,
it contributes no independent explanatory power (R&sup2; barely moves,
Greece's out-of-sample gap gets worse rather than better, coefficient not
significant, p=0.50).

**Per the user's own interpretation framework, a null result here is
itself the useful finding**: it rules out a plausible alternative
explanation for Greece's subjective-poverty gap. The story this report
has been building &mdash; depressed wages, structural unemployment,
wage-adjusted price pressure, housing costs that reach owners too &mdash;
is about *average*-level hardship being severe for most Greek households,
not about inequality hiding a worse-off minority behind an okay-looking
average.

**Integrated exactly per the user's limited-integration instructions**: a
short entry in the existing "Variables tested but not central to the
story" Methods subsection (no new dedicated h4, unlike LTU/wages/tenure,
since this one doesn't carry the same weight), one sentence appended to
the Section 12 "Answer to Question 2" conclusion box using close to the
user's own suggested wording, and the Section 4 correlation-table row.
Deliberately no chart, no new subsection &mdash; would have diluted the
report's stronger evidence.

**A real pipeline bug found and fixed while getting the FDR number.**
Re-running `04_merge_all.py` (needed to compute inequality's FDR-adjusted
p-value through the standard 04&rarr;05&rarr;06&rarr;10&rarr;27 pipeline)
triggered a cascading many-to-many join blowup: row counts for every
variable exploded into the hundreds. Traced to three raw files created in
earlier P2 rounds &mdash; `panel_housing_overburden_by_tenure.csv`
(P2: housing tenure), `panel_price_levels_by_category.csv` (P2e),
`panel_tenure_distribution.csv` (housing tenure) &mdash; each of which has
multiple rows per country/year (one per tenure or price category, by
design, since they were built for their own dedicated checkpoint scripts,
not the generic merge). None of them had ever been through
`04_merge_all.py` before this round, since none of P2e's or housing
tenure's own integration work needed to re-run the generic merge pipeline
&mdash; this was the first time it ran with all three present. Fixed at
the root, matching this project's established practice of generic fixes
over special cases: added a `geo`/`time` uniqueness check to
`04_merge_all.py` that skips (with a clear log line) any raw file with
more than one row per country/year, rather than adding the three files to
a manual skip list &mdash; this protects against the same failure mode
for any future multi-dimensional raw file, not just these three. Verified
directly afterward that every already-published correlation number (long-
term unemployment r=0.933, real wages r=&minus;0.785, youth unemployment
r=0.711, and every other row) is byte-for-byte unchanged &mdash; the
corruption never touched any previously-published report content, caught
before it could.

Tag balance and in-browser rendering verified before publishing.
Republished with label "P2 final: income inequality checked, not
central".

**This closes out P2.** Per the user's explicit instruction, no further
variables will be added without a fresh decision to do so &mdash; the
next step is a full review of the expanded Version 1 (P3: integrate the
whole P2 sweep into a coherent narrative pass, then P4: final release
review), not more analysis expansion.

## Full Version 1 release-readiness review (2026-08-21)

User's explicit framing: a release-readiness review, not another ideas
review &mdash; "no new variables unless a current claim requires them."
Seven-part scope: full claim/number audit, narrative coherence, executive
summary/conclusion consistency, redundancy check across the six P2
additions, cross-reference/TOC/badge audit, Greek-perspective framing
check, and Methods/documentation consistency.

**Method**: read the entire report end to end (everything from Section 7
onward, since Part I predates this session's changes), cross-checked
every headline number in the executive summary, scorecard, Section 11,
Section 12, and Methods against the current CSV/JSON outputs, and grepped
systematically for cross-reference patterns ("Section 11" self-references,
stale terminology, badge usage counts).

**What passed clean**: every number checked out. Redundancy handling was
already good going in &mdash; GDP-scarring-vs-LTU, housing-tenure-vs-
overburden, expectations-vs-LTU, and youth-unemployment-vs-LTU/migration
all had explicit, consistent "here's the overlap, here's why we didn't
double-count it" language already in place from each round's own
integration work. FDR counts in Methods were current. Citations all
resolved. The Greek-perspective framing goal (measurable material reasons,
pessimism treated more cautiously, no claim that the residual is solved)
read as intact throughout.

**Five must-fix findings, all addressed in one pass**:
1. Section 12 ("Answer to Question 2") never mentioned wage-adjusted price
   pressure or housing tenure at all, despite both being built as
   headline/core findings this session &mdash; a reader who read only the
   conclusion would have missed two of Section 11's strongest results.
   Rewritten (now two paragraphs instead of one very long one) to cover
   every Section 11 finding: LTU, GDP scarring, wage-adjusted pricing,
   housing tenure, migration, financial expectations, and the inequality
   null result, roughly in order of how consequential each one is.
2. Section 12's "still open" speculative list included "housing tenure"
   as an untested candidate explanation &mdash; stale, since housing
   tenure was tested this session (found to be descriptive depth, not
   independently explanatory). Removed from that list.
3. Two self-referencing "(Section 11)" citations found inside Section 11
   itself (in the youth-unemployment/migration method-aside, and the
   trust/pessimism method-aside) &mdash; changed to "above."
4. A genuine factual contradiction: the trust/pessimism method-aside
   claimed 2012 was "the same year this report's own analysis
   independently identifies as Greece's deepest economic trough," but the
   GDP-scarring subsection, earlier in the same section, explicitly
   states the trough was 2020. Traced to what 2012 actually *is* elsewhere
   in the report &mdash; the migration peak (44,502 net departures,
   already called "the depth of the crisis" in the migration subsection)
   &mdash; and corrected the sentence to reference that instead, with an
   explicit note distinguishing it from the later, deeper 2020 GDP trough.
5. Section 11's title ("Scarring and pessimism," both the TOC entry and
   the section's own h3) no longer matched its scope after six rounds of
   P2 additions (real wages, wage-adjusted pricing, housing tenure, and
   long-term unemployment all now live there too, not just GDP scarring
   and financial pessimism). Renamed to "The scars beneath the gap" (the
   user's suggested title), in both the TOC and the section heading.

**One should-fix, addressed**: real wages ("31.8% below 2008 level," real/
inflation-adjusted) and wage-adjusted pricing ("13.1% below 2008 level,"
nominal) sit in adjacent subsections and both describe "wages... below
2008" with different numbers, without an explicit cross-reference &mdash;
risked reading as an unexplained discrepancy even though both are
individually correct. Added a one-sentence units note at the start of the
wage-adjusted-pricing subsection explicitly distinguishing the two: "the
31.8% figure above is real wages... What follows is a different, nominal
comparison."

**Two polish items, both addressed**:
- "Core finding" badge had grown to 7 uses across Section 11 alone,
  diluting its signal. Reduced to 5 actual uses, kept only for the most
  central results: the moving-threshold/anchored-poverty finding in Part I
  (which never had the badge before &mdash; added it, since it's the
  report's foundational result and had none), long-term unemployment
  (both its Section 10 scorecard mention and its Section 11 descriptive
  peak/latest finding), wage-adjusted price pressure, and GDP scarring/
  recovery trajectory. Demoted real wages, housing tenure, and financial
  expectations to a new label, "Descriptive check" &mdash; defined and
  added to the Methods "Labels used in the text" documentation alongside
  the three pre-existing badge types, matching the report's own
  established discipline of documenting every label it uses.
- Executive summary reduced from 9 paragraphs to 5 content paragraphs
  plus the closing limits note, per the user's suggested structure
  (paradox, moving threshold, material reasons, LTU, what remains open).
  Merged the official-rate-mechanism and fixed-benchmark-result paragraphs
  into one; merged the GDP-scarring/wage/price/housing-tenure material
  evidence into a single "material reasons" paragraph; kept long-term
  unemployment as its own paragraph, since it's structurally different
  from the others (the one result that changes the scorecard, not just
  descriptive evidence); folded the inequality null result into the
  closing "what's still unexplained" paragraph.

Tag balance verified after every fix, and the full set re-verified
in-browser (TOC text, section heading, badge counts by type, Section 12
paragraph content) before publishing. Republished with label "Full polish
pass: 8 release-readiness fixes".

This completes P3 and P4. Per the user's own framing, this was
stabilization work, not scope expansion &mdash; the next step, if any, is
the user's call: a final skim, or moving on to something else entirely.

## Independent review, second pass (2026-08-21)

User ran a second, independent review (a fresh read of the report, data,
docs, and git state, files unchanged) and shared seven findings plus a
substantial narrative-structure critique. Verified all seven directly
against the current file state before acting on any of them &mdash; all
seven checked out as genuine:

1. Executive summary said "Greece is the only EU country that still
   hasn't recovered its own pre-crisis living standard," but Section 11
   itself explicitly names Finland and Luxembourg as also below their own
   peaks, landing on the more careful "unresolved by any reasonable
   measure" framing instead. The blunter executive-summary version
   predates this session (present before this session's own P4 tightening
   pass, just carried forward rather than introduced) &mdash; fixed to
   match Section 11's own more precise claim.
2. "Greek real income per capita remains 11.2% below its all-time high"
   (both in the executive summary and Section 11) should say "real GDP
   per capita" &mdash; the chart, its data source (<code>sdg_08_10</code>),
   and the variable's own name elsewhere in the report (the correlation
   table's "Real GDP per capita (EUR)" row) are all GDP, not household
   income, which this report treats as a distinct variable
   (<code>gr_real_hh_income_idx2008</code>) with its own separate
   correlation-table row. Fixed both instances.
3. The scorecard's "Beyond C-LTU, two further additions..." (introducing
   Models E and F) read as if E/F extend C-LTU, when the table shows both
   are built on baseline Model C. Reworded to say explicitly that E/F are
   separate extensions of C, not stacked on the labor-market swap.
4. <code>data_sources.md</code> still said income inequality and housing
   tenure were "not yet fetched," despite both having their own
   fully-integrated sections lower in the same file. Fixed.
5. <code>requirements.txt</code> had no version pins; there was no data-
   vintage or rebuild-date note anywhere in the project. Pinned all five
   dependencies to their exact currently-verified-working versions
   (pandas 2.2.3, numpy 2.2.5, scipy 1.17.1, statsmodels 0.14.6, requests
   2.31.0) and added a "Data vintage" section to the README stating the
   last full pipeline rebuild date (2026-08-21) and flagging that
   Eurostat's own published figures can revise over time, so a later
   re-run won't reproduce these exact numbers byte-for-byte even with
   unchanged code.
6. <code>model_scorecard_ltu.csv</code>'s <code>key_coefficients</code>
   column had raw <code>np.float64(...)</code> reprs baked into the CSV
   text &mdash; traced to <code>32_ltu_model_test.py</code> calling
   Python's built-in <code>round()</code> directly on a numpy float64
   scalar (which returns another numpy float64, not a plain float).
   Fixed by wrapping with <code>float()</code> first; confirmed this was
   the only CSV in the project with the issue (grepped
   <code>data/processed/</code> for the same pattern); reran the script
   and confirmed every other output file it produces is byte-identical to
   before &mdash; purely a formatting fix, no value changed.
7. Section 11's lede still said "Several variables... All three move the
   needle," undercounting the section's actual seven subsections (a
   leftover from before this session's P2 additions). The section title
   itself was renamed during the P4 review, but the lede's own
   enumeration was missed at the time. Rewritten to name all seven
   candidates tested (GDP scarring, real wages, wage-adjusted pricing,
   housing tenure, long-term unemployment, migration, financial
   expectations) and to flag explicitly that not all of them changed the
   model.

**A separate, larger recommendation from the same review**: a full
narrative restructuring of the report &mdash; separating "main text"
(readable, story-driven) from "method boxes" (technical detail, caveats,
robustness), and rewriting Section 11 specifically as the central
narrative chapter around an explicit story spine (economy didn't recover
&rarr; pay didn't recover &rarr; ordinary prices feel expensive &rarr;
housing doesn't protect owners &rarr; unemployment became duration &rarr;
people left &rarr; so pessimism isn't just mood). Assessed as a
substantively different kind of change from the seven fixes above &mdash;
correct in its critique (the report does read as a research memo, method
language does sit inline with the narrative rather than separated out)
but large enough in surface area, and different enough in character from
the stabilization work this session has otherwise done, to warrant an
explicit separate decision rather than folding it into this pass. User
agreed: write it as a separate document, with a full re-review of every
finding and a proposed structure shared before any full narrative draft
is written.

Tag balance and in-browser rendering verified before publishing.
Republished with label "Independent review fixes".

## A real, live bug: the Section 3 AROPE chart was empty (2026-08-21)

A third independent review reran the full pipeline from live Eurostat data,
scripts 01 through 36 in order, then the export/injection step, and
compared the result against the committed state. Verdict: the core
analysis reproduces cleanly &mdash; every headline number checked (subjective
poverty, AROP, AROPE, the C/C-LTU scorecard gap, LTU rate, real wages, GDP
scarring, migration total, wage-adjusted pressure, mortgage-free-owner
overburden, inequality) matched exactly. But it surfaced one real defect:
the committed <code>output/report_data.json</code> had every AROPE trend
value as <code>null</code>, which meant the AROPE line in Section 3's
"four measures of poverty" chart was never actually drawing, even though
the surrounding text discusses AROPE's trajectory and correlation figures
as if the chart shows it.

**Verified directly before acting on the claim, not taken on faith**:
confirmed the committed <code>report_data.json</code> genuinely had
<code>gr_arope</code>/<code>eu_arope</code> null for all 23 years (0 of 23
populated); confirmed the chart (<code>id="chart-anchor"</code>) reads
<code>DATA.trend</code> directly and would render an empty AROPE line as a
result; confirmed the reviewer's other listed diffs (Moldova GDP values,
±1 in <code>panel_regression_summary.txt</code>'s generation timestamp)
were exactly as benign as described, by diffing each file directly rather
than assuming.

**Root cause, traced precisely**: <code>21_arope.py</code> computes a
spliced legacy+new AROPE series and writes it <i>back into</i>
<code>analysis_dataset.csv</code> &mdash; the same write-back pattern
already documented for <code>05_threshold_hypothesis.py</code>
(<code>gr_arop_threshold_real_idx2008</code>), discovered and fixed during
P2a (real wages). <code>04_merge_all.py</code> rebuilds
<code>analysis_dataset.csv</code> from scratch every time it runs, which
silently wipes any write-back column that isn't re-applied afterward.
This session re-ran <code>04</code> multiple times during P2 (real wages,
long-term unemployment, income inequality all triggered reruns for their
own reasons) and, each time, carefully re-ran <code>05</code> afterward per
the documented order &mdash; but never re-ran <code>21</code>, because the
README's own ordering caveat, written when the <code>05</code> issue was
first found, only named <code>05</code> specifically rather than
generalizing to "every write-back script." The <code>21_arope.py</code>
columns were almost certainly wiped during the first such rerun (the P2a
real-wages round) and stayed empty through every subsequent publish since
&mdash; meaning the live, published report's AROPE chart has been broken
for a substantial stretch of this session, caught only by an external full
rerun, not by any of this project's own several review passes.

**Fixed at the root**, not just patched for this one instance: generalized
the README's ordering caveat to name both write-back scripts explicitly
and state the general rule (re-run every write-back script after any
<code>04</code> rerun, for any reason, and verify
<code>analysis_dataset.csv</code>'s expected columns afterward). Regenerated
<code>report_data.json</code> and re-injected into <code>report.html</code>
via the standard <code>09_export_report_data.py</code> /
<code>inject_data.py</code> pair (not just accepted the external rerun's
output directly); verified in-browser that all 4 chart lines now render
with 23 of 23 years populated; republished immediately, given this is a
live-broken chart on the published artifact, not a documentation
inconsistency that can wait for a batched pass.

**A gap in this project's own review discipline, worth naming plainly**:
the P4 release-readiness review and the subsequent independent-review pass
both did claim audits against the live report's <i>text</i>, but neither
one checked whether every chart actually had non-null data behind it &mdash;
a category of bug that text-level claim auditing structurally cannot catch,
since the prose was accurate throughout; only the chart's own data was
empty. Worth remembering for any future review pass: check chart data
population directly (as this fix now does, via a JS in-browser check),
not just the prose describing what the chart shows.

Tag balance and in-browser rendering verified before publishing.
Republished with label "Fix: AROPE chart data was null all session".
