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

## Narrative companion published to output/, Chapter 9 rewrite, academic paper drafted (2026-08-19)

Three separate pieces of follow-on work, logged together since they happened
in one continuous stretch.

**Narrative companion moved into the project.** `narrative_companion.html`
had only existed in scratchpad and as a standalone Artifact; copied into
`output/narrative_companion.html` per user request and added to the README's
project-structure listing. The stray file `output/The Greek Poverty
Paradox.html` (an accidental Claude-artifact-shell save, untracked, not
project content) was found alongside it and deleted.

**Chapter 9 rewrite.** The user's own critique: "pessimism is not reporting
things are already hard but that they are hard already for a long time and
because of that there is no hope to see things becoming better," combined
with political trust. Chapter 9 ("Why pessimism isn't the story") was
redundant with Chapter 11's landing and rested on a weaker mechanism than the
report's own Section 11 findings actually support. Rewrote around a
duration&rarr;extrapolation&rarr;hopelessness argument, explicitly tying
Chapter 9 back to Chapter 7's sixteen-year scarring thesis (which the
original version never referenced) and integrating the institutional-trust
finding as a second, parallel timeline rather than a footnote. Added an
explicit method-note caveat that the trust/income timelines are a documented
parallel, not a tested joint mechanism.

**A second independent review** (7 line-referenced findings on
`narrative_companion.html`: stale data-vintage date, an AROP/AROPE
conflation in the opening hook, an overclaimed "cannot make ends meet"
phrasing, a wrong chapter cross-reference, an unscoped "hardest country to
predict" claim, a colophon overclaiming Eurostat-only sourcing, two phrases
needing softer absolute language) &mdash; every claim verified against the
file directly before any fix, consistent with this project's standing
discipline. All seven fixed. Separately, the "today" date used throughout
much of this session (2026-08-21) was caught as wrong by the user against the
narrative companion's own vintage field; verified correct via the
`panel_regression_summary.txt` generation timestamp (`Wed, 19 Aug 2026`) and
fixed in the two functionally meaningful vintage claims (narrative companion,
README) &mdash; historical dated changelog headers throughout this file were
deliberately left alone as internal timestamps, not user-facing claims.

**Academic working paper drafted.** The user asked for a structure/plan for
an academic working-paper draft, then, on a substantive critique that this
report never examined *why* Greek government policy since the crisis largely
failed to translate into visible household-level improvement, asked
specifically to fold that question into the paper's Discussion section
("Option 3, fold it into the academic paper's Discussion"). Researched
Greece's three EU/IMF/ESM adjustment programs (2010, 2012, 2015) from two
primary sources read in full (via `WebSearch` + `Read`'s PDF extraction,
after `WebFetch` failed on both PDFs' raw binary content &mdash; worth noting
as a recurring tool limitation, not specific to this project):
Pagoulatos (2018), *Greece after the Bailouts: Assessment of a Qualified
Failure* (LSE Hellenic Observatory GreeSE Paper No. 130), an independent
academic assessment; and European Stability Mechanism (2020), *Lessons from
Financial Assistance to Greece*, the lending institution's own commissioned,
independent evaluation. Deliberately sought a source that would argue the
programs' case, not just the critical one, before writing anything &mdash;
consistent with the explicit commitment made to the user not to write toward
the user's own stated hypothesis ("almost everything failed") as a
predetermined conclusion. The two sources converge on a similar qualified
verdict from opposite institutional positions (financial-stability and
structural-reform objectives substantially met; growth and social objectives
not, for reasons both sources attribute partly to program design &mdash;
front-loaded austerity built on a since-revised fiscal-multiplier assumption,
delayed debt relief, and labor-market liberalization without a matching
safety net), which is used in the paper's Discussion section as a source of
confidence that the qualified-failure framing isn't simply one critic's
reading. The Discussion section connects this record to the paper's own
empirical findings &mdash; the "flexicurity without security" gap as a
plausible institutional explanation for why long-term unemployment
specifically outpredicts headline unemployment (Section 11's central
result), and front-loading/the multiplier error as consistent with the
unusually deep and prolonged GDP scarring &mdash; explicitly hedged
throughout as interpretation, not a causal claim tested by this paper's own
regressions.

Drafted as `output/academic_paper_draft.html`: full IMRaD-style academic
paper (abstract, JEL codes, formal literature review, data/methods,
Results I &amp; II reformatted from the technical report into academic
register with in-text citations, the new Discussion section above,
limitations, conclusion, data/code/AI-disclosure statement, full APA
reference list). Four structural decisions were made by default rather than
asked, and are flagged as open items directly in the draft's own text for
the user to confirm or override: single combined paper rather than split
(matches the existing report's own Part I/II structure); APA citation style
(previously suggested, not objected to); AI-assistance disclosure included
(previously recommended); author name and affiliation left as explicit
placeholders. Published as a separate Artifact
(https://claude.ai/code/artifact/2fede66a-f98a-4365-bb89-7634c8661208,
title "Greek Poverty Working Paper", favicon &#127468;&#127479;). Tag-balance
verified via regex count before publishing; dark-mode rendering verified via
computed-style JS check after the Browser pane's screenshot tool proved
unreliable on this file (returned blank captures at depth while the
underlying DOM/CSS were confirmed correct) &mdash; noted here in case it
recurs on a future large single-page artifact.

## Charts added to both companion pieces; academic paper review response (2026-08-19)

The user pointed out, correctly, that neither `narrative_companion.html` nor
`academic_paper_draft.html` had any charts &mdash; both were text/table-only,
unlike `report.html`. Fixed by generating self-contained inline SVGs (a
Python script computing coordinates directly from `output/report_data.json`,
no chart library, colors set via `var(--token)` so each chart inherits its
document's own light/dark theme automatically):

- **Academic paper** (5 numbered figures, inserted at their first relevant
  reference): Fig. 1 AROPE-vs-subjective dumbbell, all 27 countries + EU
  average (&sect;5.1); Fig. 2 real poverty threshold vs. real household
  income, 2005&ndash;2024 (&sect;5.2); Fig. 3 out-of-sample gap by model, bar
  chart of Table 1 (&sect;6.4); Fig. 4 long-term unemployment rate, all EU
  countries (&sect;6.5); Fig. 5 real GDP per capita indexed to own peak, all
  EU countries (&sect;6.6).
- **Narrative companion** (3 charts, placed more sparingly to match its
  lighter pacing): the AROPE/subjective dumbbell using a curated ~9-country
  subset, right after the opening pull-stat; the GDP-recovery chart in
  Chapter 3; the long-term-unemployment chart in Chapter 7.

One data-accuracy catch during generation: the EU aggregate's row in
`arope_snapshot` carries Eurostat's raw label ("European Union - 27
countries (from 2020)"), relabeled to "EU average" for the chart legend
before use &mdash; the underlying value wasn't touched, just the display
label.

**Independent review of the academic paper, second round.** While the charts
were still being added, the user shared a detailed review of the pre-chart
draft and, on its central point ("Section 7 makes it lose some of its
earlier power... tone it down and report as a dimension in the discussion"),
agreed directly rather than just relaying the reviewer's view. Every finding
was checked against the actual file (and, for the two most technical ones,
against `docs/data_sources.md` and the relevant script) before any fix, per
this project's standing discipline of never taking a review's claims at
face value:

- **Confirmed, fixed:** methods text cited "(Table 3)" for a table actually
  labeled "Table 1" &mdash; a stale internal numbering artifact, not a
  missing-rows problem (the table already had all seven models A&ndash;F +
  C-LTU).
- **Confirmed, fixed:** abstract claimed AROP "ranked only 4th&ndash;10th,"
  contradicted by this project's own established fact that Greece's AROP
  rank has touched 1st since 2007; fixed to "ranged between 1st and 10th...
  4th-highest in the most recent year" in both the abstract and
  introduction, removing the confusing "never worse than 1st" phrasing.
- **Confirmed, fixed &mdash; the sharpest catch:** the methods section
  described `tepsr_wc310` as the deflator for the poverty threshold. Checked
  against `docs/data_sources.md` and `scripts/05_threshold_hypothesis.py`
  directly: `tepsr_wc310` is actually *real household disposable income,
  already indexed to 2008* &mdash; a comparison series, not a deflator. The
  real deflator is Greek HICP (`prc_hicp_aind`), confirmed by the script's
  own comment. Fixed to attribute each series correctly.
- **Confirmed, fixed:** the Andriopoulou et al. comparison labeled this
  project's own figure "income year 2014," but `report.html` itself uses
  "survey-year 2014" &mdash; a real convention mismatch introduced when
  converting to academic prose; fixed, and the surrounding claim softened to
  note the survey-year/income-year alignment hasn't been independently
  verified against Andriopoulou et al.'s exact convention.
- **Confirmed, fixed:** institutional-trust figures (OECD 2026 country
  profile, Eurobarometer series) were cited in-text but the OECD reference
  was missing from the paper's own reference list &mdash; added, matching
  `report.html`'s existing citation.
- **Confirmed, fixed:** the "no series is hand-entered / not drawn from a
  non-public source" reproducibility claim (both the &sect;4 opening and the
  &sect;10 data-availability statement) was scoped too broadly &mdash; it
  didn't account for the OECD/Eurobarometer trust context or the two
  bailout-program secondary sources. Fixed with the same pattern already
  used to fix this exact issue in the narrative companion's colophon earlier
  this session: scope the strong claim to the core Eurostat panel, name the
  literature/institutional sources explicitly as a separate category.
- **Agreed and acted on, not just "fixed":** Section 7 was restructured from
  five subsections (&sect;7.1&ndash;7.5, ~1700 words, three full paragraphs
  connecting program design to the paper's own findings, one of them a
  "two independent, mutually reinforcing reasons" claim about trust and
  scarring together that read stronger than the evidence supports) down to
  two subsections (~700 words): &sect;7.1 interprets the paper's own &sect;5/&sect;6
  results directly (new content &mdash; the old Section 7 jumped straight to
  bailout history with no discussion of the paper's own core results first,
  which was itself part of why it read as scope creep); &sect;7.2 condenses
  the programs table and the credited/criticized record into shorter prose,
  keeps only the two connections with the clearest evidentiary basis
  (front-loading/scarring; flexicurity-gap/long-term-unemployment), and
  drops the trust-and-scarring "two independent reasons" paragraph entirely.
  The Conclusion and abstract were rewritten to match &mdash; leading with
  the paper's own tested findings, mentioning the policy-history connection
  once, briefly, clearly hedged. TOC and cross-references to the old
  `#s7-3`/`#s7-4`/`#s7-5` anchors updated throughout.

Both files' tag balance verified via regex count before republishing; both
republished to their existing Artifact URLs (not new ones).

## Third review round: FDR scope, remaining academic-paper issues, GDP-trajectory
## bug found in report.html itself, narrative chart expansion (2026-08-19)

Same discipline as the previous two rounds: every claim checked against the
actual file (and, for the multiple-testing point, against
`scripts/27_multiple_testing.py` directly) before any fix.

**Multiple-testing scope, raised separately from the numbered review.** The
Methods text described FDR correction as applying "most notably" to the
9-predictor sensitivity-vs-gap test, without naming the other two families.
Checked `scripts/27_multiple_testing.py` directly: the project actually runs
FDR correction on **three** separate families &mdash; the contemporaneous
correlation screen (17 variables, `fdr_correlations.csv`), the sensitivity-
vs-gap test (9 predictors, `fdr_sensitivity_vs_gap.csv`, the only one of the
three reproduced in the academic paper itself), and a second-difference/
acceleration check (5 variables, `fdr_acceleration.csv`) &mdash; explicitly
*not* the confirmatory panel-regression coefficients, per the script's own
docstring. Fixed to name all three families and state plainly that no single
correction spans the whole project, since the families answer different
questions.

**Five further, independently-checked issues in `academic_paper_draft.html`:**
- Figure 2's caption still said the threshold was "deflated by
  `tepsr_wc310`" &mdash; the exact mistake already fixed in the body text
  (&sect;4) two rounds ago, missed in the figure caption when the figure was
  added afterward. Fixed to match the corrected body text.
- The abstract said a 6&ndash;20pp out-of-sample gap "persists under every
  specification," then two sentences later said C-LTU cuts it to 3.9 &mdash;
  a direct self-contradiction. Fixed to scope the claim to "every
  specification that uses headline unemployment," matching the (already
  correct) wording already used in the Results section itself.
- Section 7 was still introduced, in both the Introduction and the Literature
  Review's "contribution" paragraph, as something done for the first time /
  not previously attempted &mdash; novelty framing left over from before the
  Section 7 demotion two rounds ago, inconsistent with treating it as
  interpretive context. Both passages rewritten to state plainly that
  Sections 5&ndash;6 are the paper's contribution and Section 7 makes no
  claim of novelty.
- Section headings rendered as "1.Introduction" with no space in the
  underlying text content (only CSS margin provided visual separation) &mdash;
  cosmetically fine on screen, but would collapse on copy-paste or any
  text-extraction tool. Fixed by adding a literal space after the number in
  all 11 headings.

**A real bug in `report.html` itself, not just the derived documents.** The
GDP-recovery finding (Section 11) said Greece's decline "ran from its 2008
peak all the way to a trough in 2020" and "took twelve years just to stop
falling" &mdash; wording that implies continuous decline. Checked the actual
series (`recovery_trajectory` in `report_data.json`, Greece/EL column): the
index fell from 100 (2008) to a first trough of 73.76 in **2013**, recovered
to 80.35 by **2019**, then the COVID-19 pandemic pushed it to a new marginal
low of 73.11 in **2020** &mdash; barely below the 2013 trough, but via an
unrelated second shock landing on a partially-recovered economy, not twelve
years of uninterrupted falling. The underlying data and the "11.2% below
peak in 2024" headline number were never wrong; only the shape description
was. This is the first review round in this project's history to catch a
factual bug in `report.html`'s own prose rather than in a document derived
from it &mdash; worth noting since two prior independent-review rounds and
this project's own P4 release-readiness review all read past it. Fixed at
the root (`report.html`), then propagated the same correction to the two
derived documents (`academic_paper_draft.html` &sect;7.2,
`narrative_companion.html` Chapter 3) rather than patching each
independently. Also fixed on the same pass: "all-time high" (too absolute
for a 2008&ndash;2024 observation window) &mdash; changed to "2008 peak" in
the narrative's table header, matching the more careful "own historical
peak" language already used elsewhere.

**Two more narrative-companion wording fixes**, both confirmed against the
file before changing: the Chapter 9 trust passage ("two independent,
sixteen-year timelines... two separate, reinforcing reasons") stated more
than an untested, context-only variable supports &mdash; softened to
describe it as a documented parallel, not a claim about reasons a household
actually has. The colophon's "the full technical report behind every figure
cited here" was corrected to "the modeled and Eurostat-based figures," since
the institutional-trust figures are explicitly not part of that pipeline
(the very next sentence already said so &mdash; the fix makes the first
clause consistent with it rather than contradicting it).

**Narrative companion: two more charts.** The user felt three charts felt
thin against the academic paper's five and asked for more. Added a real-
wages trajectory chart (Chapter 4, capped at 160 matching `report.html`'s
own convention, since a few Eastern European countries grow far past that
line) and a net-migration bar chart (Chapter 8, diverging around zero,
rust for net-outflow years and green for the two recent net-inflow years) &mdash;
now five charts total, generated the same way as the first three (inline
SVG, colors via `var(--token)`, data pulled directly from
`report_data.json`).

All three files' tag balance re-verified via regex count; all three
republished to their existing Artifact URLs. The user also shared a
higher-level observation mid-round: that the three outputs now cover the
same material but don't yet share one explicit hierarchy of central vs.
supporting vs. contextual findings, and suggested treating the narrative
companion as the "story spine" the other two should align to.

## Cross-document alignment pass: a story hierarchy layered on the badge system (2026-08-20)

Followed up on the hierarchy observation above. Explicit design decision,
made by the user after two rounds of back-and-forth: **keep the existing
evidence-quality badge system (Core finding / Descriptive check /
Exploratory lead) completely untouched**, and add a *separate*, orthogonal
axis &mdash; a six-stage story hierarchy (measurement problem &rarr; residual
outlier &rarr; material scarring &rarr; duration mechanism &rarr; social/
demographic scars &rarr; ruled-out explanations) &mdash; expressed through
ordering, framing, transitions, and summaries, not new badges or a
relabeling of existing ones. Rationale, in the user's own words: the badges
answer "how strong is this finding," the story spine answers "why am I
being told this and how does it move the argument" &mdash; conflating them
risks making supporting-but-strong evidence read as weak. One new visible
phrase was authorized: <b>Evidence role:</b>, used sparingly in method notes
to name a finding's narrative role without touching its evidentiary label.

This was explicitly scoped as an editorial pass, not new analysis &mdash;
no new variables, no new charts, no changed numbers. Work by document:

**`report.html`** (needed the most work, per the user's own read &mdash;
"still feels like accumulated evidence"): added a one-line statement of the
whole argument's shape at the top of the executive summary (the same
sentence the user supplied: "Greece's poverty paradox is partly a
measurement problem and partly a scarring problem..."), naming the six
stages explicitly; added a previously-missing executive-summary paragraph
for the social/demographic-scars stage (migration + trust had findings in
Section 11 but no executive-summary mention at all &mdash; a real gap, not
just an ordering issue); gave the ruled-out-inequality finding a bolded
"Ruled out:" lead-in inside its existing paragraph, rather than a new
paragraph; regrouped Section 11's own lede into the three sub-groups it
implicitly always had (material scarring / duration / social scars) with a
one-sentence description of each; added six "Evidence role:" phrases to the
method-note boxes for real wages, wage-adjusted pricing, housing tenure,
migration/youth-unemployment, pessimism/trust, and the ruled-out inequality
finding.

**`narrative_companion.html`** (needed the least, since the user identified
it as already having "the best spine" &mdash; its chapter order already
matches the six-stage hierarchy almost exactly): added one roadmap
paragraph right after the opening hook, before Chapter 1, naming the shape
of the whole piece in narrative voice and mapping chapter ranges to stages.
Chapter-level transitions (Ch. 2&rarr;3, Ch. 6&rarr;7, Ch. 9&rarr;10) were
checked and left alone &mdash; each chapter's own lede sentence already
does the pivoting work cleanly, and the Landing (Ch. 11) already crystallizes
the argument better in its own prose than the clinical one-line summary
would; adding the explicit sentence there would have flattened it, so it
was left untouched.

**`academic_paper_draft.html`**: added a roadmap paragraph to the
Introduction naming the six stages with section cross-references; added a
new paragraph to &sect;4.3 (evidentiary hedging convention) explicitly
distinguishing evidentiary status from argument stage, stating a finding
can be central to the argument while resting on descriptive evidence; split
&sect;6.6's single undifferentiated paragraph (GDP/wages/prices/housing
mixed with migration/trust) into two bolded sub-paragraphs, "Material
scarring" and "Social and demographic scars," matching the same split now
named in report.html's Section 11 lede.

All three files' tag balance re-verified via regex count; all three
republished to their existing Artifact URLs. Committed and pushed to
`origin/main` (commit `2032f97` for the academic-paper/chart/GDP-bug round;
this alignment round follows in a separate commit).

## Cumulative-hardship checkpoint (2026-08-20)

New checkpoint, `scripts/38_cumulative_hardship.py`, run to completion end to
end (not just interactively) before this entry was written. Motivated by a
methodological question raised while discussing the AROP/AROPE restructuring:
does *accumulated* exposure to hardship since the crisis explain Greece's
subjective-poverty gap better than *current-year* hardship alone? Framed
explicitly as a generalization of the anchored-poverty method already in the
report (Section 3's fixed-2008-baseline reconstruction), applied
systematically to GDP, real wages, unemployment, long-term unemployment, and
the AROP threshold itself, rather than a new idea bolted on.

### Data and construction

- **AROP threshold, cross-country**: fetched fresh (`ilc_li01`, national
  currency (NAC), not EUR -- avoids exchange-rate contamination for non-euro
  countries), deflated by each country's own HICP. Coverage checked before
  building anything on top of it (the explicit gate agreed before running):
  clean for all 27 countries, only Croatia lacks 2008/2009 data (series
  starts 2010, used as Croatia's own baseline, flagged in the script's
  output).
- **Headline unemployment, full history**: the existing `panel_unemployment.csv`
  only covers 2015-2024 (matches the model's own window); a longer-history
  version was fetched fresh and confirmed to start in **2009**, not 2008, for
  nearly every country (`panel_unemployment_history_2008_2024.csv`) -- an
  assumption that would have been wrong if not checked directly. Unemployment
  and LTU cumulative-excess measures both baselined to 2009 as a result.
- **Construction rules** (agreed before running, per the discipline
  established for every other checkpoint in this project): GDP and real-wage
  cumulative shortfalls use `max(0, 100 - index)` per year, summed -- an
  accumulated-*damage* measure, not a net-performance score where later
  growth cancels earlier hardship. Two baselines each (fixed 2008, own
  rolling peak). Unemployment/LTU use cumulative *excess* above each
  country's own baseline-year rate, also floored at 0 per year.

### Main results

**Stage 1 (individual, each variable alone + AROP + year FE, clustered by
country)** -- deliberately the simplest possible baseline, so every
candidate (whether or not it's already inside the main model) is tested on
equal footing. Answers "how much does this one variable, alone, help
translate AROP into subjective poverty" -- explicitly not a causal-
contribution claim. Full results:
`data/processed/cumulative_hardship_stage1_individual.csv`.

| Variable | Greece OOS (alone) | Points of 47.6pt AROP gap | Note |
|---|---:|---:|---|
| Arrears | 0.05 | 47.5 | Conceptually close to the outcome -- not trusted as a mechanism |
| Cumulative excess unemployment | 9.58 | 38.0 | Strongest clean standalone structural variable |
| LTU | 21.84 | 25.8 | Real, but modest alone -- most of its power comes from combination |
| Financial expectations | 25.79 | 21.8 | Outcome-adjacent by design, caveated throughout the report already |
| Housing tenure burden | 36.07 | 11.5 | |
| Unexpected-expense capacity | 38.28 | 9.3 | Also conceptually close to the outcome |
| Wage years below 2008 | 38.68 | 8.9 | |
| Wage-adjusted price pressure | 39.31 | 8.3 | |
| Material deprivation | 40.00 | 7.6 | |
| Migration | 46.92 | 0.7 | Not significant alone (p=0.40) -- contextual, not explanatory |
| **Housing cost overburden** | **51.53** | **-3.9** | **Makes Greece look *more* anomalous alone -- confirms independently why Section 9's nested design (housing alone worsens the out-of-sample prediction) was the right call, not an artifact of that one section |

**Stage 2 (layered, sequential)** -- the combined story, `data/processed/cumulative_hardship_stage2_bridge.csv`:

| Step | Layer | Greece value | Points closed (of 47.6) |
|---|---|---:|---:|
| 1 | AROP raw gap | 47.6 | -- |
| 2 | AROPE bridge | 39.7 | 7.9 |
| 3 | Basic model (Model A) | 25.6 | 22.0 |
| 4 | + housing, arrears, expense capacity (Model C) | 11.6 | 36.0 |
| 5 | Headline unemployment -> LTU (Model C-LTU) | 3.9 | 43.7 |
| 6 | + cumulative excess unemployment (final model) | **-0.8** | 48.4 |

Step 6's negative value is a residual sign flip, not "102% explained": the
model, once cumulative excess unemployment is added to C-LTU, mildly
*overpredicts* Greece's subjective poverty rather than leaving a positive
unexplained gap.

**Robustness, run before treating step 6 as a real finding, not after:**
- *Replacement test*: cumulative excess unemployment is not a better version
  of LTU. Replacing LTU with it performs worse (R²=0.911, Greece OOS=4.26)
  than the C-LTU baseline (R²=0.914, OOS=3.86). Combined, both stay
  significant with no collinearity destabilization (R²=0.930, OOS=-0.82).
  It's a genuine additional layer, not a substitute.
- *Leave-one-country-out stability*: coefficient positive and significant in
  all 27 refits (range 0.134-0.197), including the refit that excludes
  Greece itself (coef=0.164, p=0.0064).
- *Year-by-year check*: the negative average residual is not driven by one
  anomalous year -- small and mostly negative-to-near-zero across
  2015-2024 (range -3.25 to +1.01), with exactly one exception (2021,
  +4.40, plausibly the pandemic-disruption year).
  Full table: `data/processed/cumulative_hardship_final_model_year_by_year.csv`.

**Exploratory extension: duration/direction, not just cumulative level.**
Tested separately (`data/processed/cumulative_hardship_duration_battery.csv`):
does *persistence* (years continuously below baseline, longest historical
streak, count of negative-change years) explain the gap better than a raw
cumulative sum? Only one variable clears significance:
**`wage_years_below_2008`** (years continuously below own 2008 real-wage
level), p=0.0045, robust under its own leave-one-country-out check
(positive and significant in all 27 refits, including excluding Greece:
coef=0.31, p=0.0036). Every GDP-based duration/direction variant is
non-significant (p=0.74-0.89) -- duration matters for wages specifically,
not GDP, consistent with the project's existing "GDP is an abstraction, the
payslip is what households feel" framing (narrative companion, Chapter 4).
Combined with cumulative excess unemployment: both individually significant
(R²=0.931, OOS=-1.08), but the within-Greece correlation between them is
0.95 (panel-wide only 0.54) -- the "two independent channels" claim is
well-supported as a cross-country statistical result, weaker as a claim
about what's separably happening inside Greece's own trajectory. Kept as
**robust supporting evidence, not a seventh layer in the main sequence.**

### Central finding, stated plainly

The gap does not close because of one current-year hardship variable. It
closes when current hardship is combined with duration and accumulated
labor-market exposure. **Cumulative excess unemployment since 2009** is the
central new mechanism: strong alone (Stage 1), strong in combination
(Stage 2), stable under leave-one-out, and not explainable by definitional
overlap with the outcome (unlike arrears).

**On the negative residual specifically:** this does not show that Greeks
are optimistic. It shows that the "Greek pessimism premium" interpretation
no longer survives once accumulated labor-market exposure is included, in
this specific (richest-tested) model. Worth featuring as a discussion
point, with one explicit condition attached: it is a property of the
richest tested specification (C-LTU + cumulative excess unemployment), not
the paper's baseline finding, and the write-up should say so rather than
letting the negative sign read as the report's default characterization of
Greece.

### Evidentiary status, stated separately for every variable touched

Kept deliberately distinct from the *argument-stage* hierarchy (measurement
/ residual / scarring / duration / social scars / ruled-out) established in
the prior alignment-pass round -- this is about statistical/methodological
trust, that round was about narrative role:

- **Ruled out**: income inequality (pre-existing finding, unaffected by
  this checkpoint).
- **Tested, came back null**: cumulative real AROP-threshold shortfall
  (p=0.645, despite being the checkpoint's most narratively-anticipated
  candidate going in); GDP-based cumulative and duration/direction variants
  (all non-significant, p=0.13-0.89).
- **Contextual scarring evidence, not a modeled cause**: migration
  (not significant alone, p=0.40, and never entered as a covariate);
  institutional trust (never modeled at all, per the project's own
  pre-existing decision -- Eurostat's trust series is too thin to support a
  trend variable).
- **Robust supporting evidence, not a scorecard-changing layer**:
  `wage_years_below_2008`.
- **Central new cumulative mechanism**: `cum_excess_unemployment`.

### Limitations -- addressed through checkpoint design vs. structural

**Addressed directly by this checkpoint's own design:**
- *Model-specification risk*: Stage 1 prevents overclaiming any single
  factor's contribution (several look strong combined but weak or even
  counterproductive alone -- housing overburden is the clearest case).
  Stage 2 shows the combination is not arbitrary stacking: each layer was
  chosen for a stated reason and tested against the prior layer, not
  assembled post hoc to hit a target number.

**Reduced through framing, applied consistently across this entry and the
docs to follow:**
- AROP/AROPE hierarchy: AROP is the paper's main object; AROPE is the
  bridge, not a co-equal headline measure (decision finalized earlier this
  round, restated here since this checkpoint's results are built on it).
- Cumulative-measure choices are documented explicitly (baselines, flooring
  rule, robustness checks), not left implicit.
- Arrears and unexpected-expense capacity are labeled conceptually close to
  the outcome everywhere they appear, including in this checkpoint's own
  Stage 1 table -- not just in the original report.
- Short-coverage variables (wage-adjusted pressure's 3-year category-level
  window, though the "overall consumption" series used here has full
  2000-2024 coverage and was checked before use) carry coverage notes.
- Migration and trust are kept explicitly separate from model-tested
  findings throughout, never silently upgraded to covariate status.
- AROP's crisis-context misuse becomes a stated discussion contribution
  (planned for the Discussion section), not a hidden assumption.

**Structural, not reducible by better framing -- stated once here rather
than re-litigated in every document:**
- This project uses aggregate country-level Eurostat data throughout, not
  EU-SILC household microdata.
- AROPE cannot be literally reconstructed from its components; the overlap
  between income-poverty, severe deprivation, and low-work-intensity is
  unobserved without microdata (stated explicitly in the AROP/AROPE
  restructuring plan, applies equally here).
- Every result in this checkpoint, like every regression result elsewhere
  in the project, is associational, not causal.
- Household balance sheets, savings depletion, informal support, and wealth
  buffers remain only partially observed (savings rate was tested
  elsewhere in the project and added no independent power once financial
  expectations was already in the model).
- Subjective poverty is self-reported and may still reflect norms or
  expectations not captured by any variable tested here or previously.
- Greece's crisis is a distinctive case; the AROP-in-crisis-contexts
  warning (the discussion contribution) generalizes more readily than any
  individual substantive Greek finding does.

### Next step

Per the agreed order: the three output documents are not touched by this
entry. The AROP/AROPE restructuring (Core Reframe: AROP primary, AROPE
bridge, Part II reframed as decomposing AROPE's intuition rather than
reconstructing it, discussion critique of AROP-alone-in-crisis-contexts)
proceeds next, now informed by this checkpoint's actual results rather than
being written before they were known -- avoiding exactly the
retrofitted-caveats problem the checkpoint-first ordering was chosen to
prevent.

## AROP/AROPE restructuring across all three outputs (2026-08-20)

All three published documents (`output/report.html`, `output/narrative_companion.html`,
`output/academic_paper_draft.html`) were rewritten around the agreed 7-point
spine, using the checkpoint above as the authoritative source for every
number and framing decision. No new analysis was run in this pass -- this
was purely a rewrite of prose, charts, and tables around results already
locked and committed.

**Spine applied consistently to all three:**
1. AROP puzzle (47.6pt gap, Greece 4th on AROP vs. 1st on subjective, next
   largest gap Bulgaria at 14.9pt) -- now the primary chart/finding in every
   document, always shown first.
2. Shrinking ruler (AROP's moving threshold) -- unchanged content, reordered
   to follow directly from the AROP puzzle.
3. AROPE bridge (39.7pt gap, narrows but does not close) -- repositioned as
   secondary, immediately after AROP, framed as the EU's own acknowledgment
   that income poverty is too narrow, never as a replacement primary measure.
4. Part II reframed explicitly as "decomposing AROPE's intuition," stated
   plainly as not a reconstruction of AROPE (component overlaps unobserved
   without EU-SILC microdata) in all three documents.
5. Gap-closing ladder: raw AROP (47.6) -> AROPE (39.7) -> Model A (25.6) ->
   Model C (11.6) -> Model C-LTU (3.9) -> + cumulative excess unemployment
   (-0.8), consistent across report.html's new ladder table, the narrative
   companion's Chapter 8 proof table, and the academic paper's new Table 2.
6. Main new mechanism -- cumulative excess unemployment since 2009 -- added
   as a new section/chapter in all three: report.html gets a new "gap-closing
   ladder" subsection plus updated scorecard (Model G); the narrative
   companion gets a new Chapter 8 ("The debt that never gets paid down"),
   renumbering all subsequent chapters (8->12 total, up from 11) and every
   cross-reference; the academic paper gets a new &sect;6.6 with its own
   Table 2, renumbering &sect;6.6-6.7 to &sect;6.7-6.8 and &sect;7.1-7.2 to
   &sect;7.2-7.3, with a new &sect;7.1 stating the AROP-in-crisis-contexts
   methodological caution.
7. Discussion: the AROP-in-crisis-contexts caution (relative-income measures
   can understate deterioration for years during a prolonged collapse; safest
   read alongside a fixed-standard threshold, a broader measure, and a
   cumulative-exposure measure) added to all three -- report.html's
   literature section, the narrative companion's Landing chapter, and the
   academic paper's new &sect;7.1 -- plus the negative-residual interpretation
   sentence (agreed exact framing: "does not survive," never "more than
   100% explained") repeated verbatim in all three.

**Mechanical work specific to each document:**
- `report.html`: new `DATA.arop_snapshot`, `cum_stage1`, `cum_stage2`,
  `cum_year_by_year` keys already exported in a prior session (script
  `37_arop_snapshot.py`, `09_export_report_data.py`); this pass added a new
  primary AROP dumbbell chart (reusing the existing `dumbbellChart()` JS
  function), a new gap-closing-ladder table and year-by-year residual line
  chart populated from `DATA.cum_stage2`/`DATA.cum_year_by_year`, a Model G
  row in the existing scorecard table, and new Methods `<dl>` entries for
  the cumulative-excess-unemployment construction and a structural-limitations
  list. Verified in-browser: new charts/tables render with real injected
  data (Greece AROP=19.6, subjective=67.2, gap=47.6; ladder table 6 rows
  matching checkpoint numbers exactly).
- `narrative_companion.html`: the opening hand-coded SVG dumbbell chart
  (9 representative countries) was recomputed from AROP data using the
  same x-axis scale formula as the original AROPE version, verified against
  the axis tick endpoints. New Chapter 8 added with its own proof table and
  method notes; all subsequent chapters (former 8-11) renumbered to 9-12,
  including every in-text cross-reference and the masthead chapter count
  (11->12). Landing chapter and colophon rewritten to reflect the closed
  residual and the crisis-context caution.
- `academic_paper_draft.html`: Figure 1's full 27-country-plus-EU-average
  SVG dumbbell chart was regenerated programmatically from
  `arop_subjective_snapshot_2025.csv` using the same coordinate formula as
  the original (verified against axis endpoints: x(4%)=100, x(72%)=654),
  rather than hand-edited, given the number of precise coordinates involved.
  New &sect;6.6 added with its own Table 2 (gap-closing ladder); a pre-existing
  table also numbered "Table 2" (financial-assistance programs) was
  renumbered to Table 3 to avoid a duplicate caption. Abstract, Introduction,
  Discussion, Limitations, and Conclusion rewritten; every stale
  cross-section reference from the renumbering (&sect;6.6/&sect;7.1/&sect;7.2
  used in their old sense) was found via full-file grep and corrected.

**Verification before republish:** tag-balance checks (div/section/svg/table/
tr and, for the academic paper, dl/dt/dd/ul/li) run on all three files;
each file reloaded in-browser with console-error checks; new chart elements
counted and cross-checked against expected row/country counts (report.html:
56 circles for 28-row AROP snapshot; narrative companion: AROP chart renders
with correct Greece/Bulgaria/Italy/etc. coordinates; academic paper: 58
circles for the 29-row-including-legend Figure 1). All three republished to
their existing Artifact URLs (same URLs as prior sessions, favicon
unchanged: 🇬🇷).

## Literature-review response: FDR correction for the cumulative family,
## level-of-analysis caveat, and new citations (2026-08-20, later same day)

An external literature review of the restructured spine (user-supplied,
citation-heavy) confirmed the Core Reframe is well aligned with published
research, flagged one genuinely new distinctive contribution (no existing
EU study found using this specific country-level cumulative-excess-
unemployment construction to explain the subjective-poverty gap), and
raised four concrete, actionable points. All four were addressed before
republishing again.

**1. Multiple-testing correction for the cumulative/duration family.**
The review noted this was still outstanding: several cumulative, baseline,
and duration constructions were screened in script `38_cumulative_hardship.py`
before `cum_excess_unemployment` was selected, and that screening family
had not yet been checked against false-discovery-rate correction the way
every other exploratory family in this project has been. Ran
Benjamini-Hochberg correction (`statsmodels.stats.multitest.multipletests`,
matching the project's existing convention) across all 18 candidates from
that screening (the original 8-variable cumulative battery + the 10-variable
duration/direction battery; the replacement test and the final combined
model are confirmatory follow-ups on the already-selected winner, not part
of the exploratory family, per this project's existing confirmatory/
exploratory distinction).
  - `cum_excess_unemployment`: raw p=0.0001 -> FDR-adjusted p=0.0018.
    Survives comfortably.
  - `wage_years_below_2008`: raw p=0.0045 -> FDR-adjusted p=0.0405. Survives,
    but narrowly -- confirming the reviewer's own prediction that this one
    "may be more sensitive."
  - All other 16 candidates: FDR-adjusted p >= 0.25. None survives.
  Result saved to `data/processed/cumulative_hardship_fdr_correction.csv`.
  This is exactly the outcome the checkpoint's own framing already assumed
  (central mechanism vs. narrowly-supporting evidence) -- the correction
  confirms rather than overturns the existing evidentiary hierarchy, but it
  is now demonstrated rather than asserted.

**2. AROPE's 2020/2021 methodology break.** The review flagged that any
chart spanning the boundary needs explicit disclosure. Checked: `report.html`
already discloses this (both in a chart note and in Methods, matching the
splice convention already used in `21_arope.py`). `academic_paper_draft.html`
and `narrative_companion.html` did not have an equivalent disclosure --
added one to the academic paper's §4 data description; checked the
narrative companion's specific AROPE figures (2008 and 2014 only) and
confirmed neither crosses the 2021 boundary, so no correction was needed
there, only the general point that the mechanism is well-established (see
below).

**3. Individual-level vs. aggregate-level evidence for the cumulative-exposure
mechanism.** The review correctly distinguished the (well-established)
individual-unemployment-scarring literature from this project's own
country-level aggregate variable, and warned against implying the two are
the same kind of evidence. Added an explicit level-of-analysis caveat to
all three documents: the individual-level literature (Lucas et al., 2004;
Mousteri et al., 2018; Clark & Lepinteur, 2019) tracks personal unemployment
histories and personal outcomes; this project's `cum_excess_unemployment`
variable is a country-year aggregate, and its correlation with Greece's
aggregate subjective-poverty rate is not direct evidence that the specific
Greek households behind that rate personally experienced sustained
joblessness. Framed as an ecological-inference limitation the project's
aggregate Eurostat data cannot close, added to the academic paper's
Limitations (§8) explicitly.

**4. Framing the shrinking-ruler result as well-established, not novel; and
using the EU's own persistent-poverty/poverty-dynamics work as a bridge for
the cumulative-exposure contribution.** Both of these were mostly already
correctly hedged (the academic paper's §3.1/§3.5 already say the mechanism
"is well established, including for Greece specifically" and that the
paper's contribution is the combination, not the mechanism itself) but were
strengthened with two additional, directly-on-point citations: Leventi &
Matsaganis (2016, OECD working paper using EUROMOD) independently confirm
Greece's relative poverty rate barely moved 2009-2014 despite collapsing
absolute living standards; OECD (2018) reaches the same conclusion in its
Greece country survey. Separately, added the EU's own persistent-AROP
indicator and a 2026 European Commission poverty-dynamics study
(Directorate-General for Employment, Social Affairs and Inclusion, 2026)
as an explicit bridge: the cumulative-excess-unemployment variable extends,
one level up, a dynamic-poverty logic the EU already applies to individual
households (poor this year AND in 2 of the past 3), plus Lin (2016, IMF)
as macro-level (not individual-level) corroboration of the same
accumulation logic via labor-market hysteresis.

**New citations added** (all fetched and verified via WebSearch, not
guessed): Bárcena-Martín, Pérez-Moreno & Rodríguez-Díaz (2020); Clark &
Lepinteur (2019); Directorate-General for Employment, Social Affairs and
Inclusion (2026); Leventi & Matsaganis (2016); Lin (2016); Lucas, Clark,
Georgellis & Diener (2004); Mousteri, Daly & Delaney (2018); OECD (2018);
Zieleńska & Wnuk (2024) -- the latter two also used to strengthen the
existing "AROPE cannot be reconstructed, union construction hides
component overlap" argument in both the academic paper and report.html.
Several other sources the reviewer named (a Springer AROPE-critique
article, a ScienceDirect multidimensional-poverty article, an IMF
hysteresis paper, two individual-scarring papers) were paywalled on first
attempt; all were successfully identified and verified via WebSearch
against independent secondary sources (abstracts, IDEAS/RePEc, institutional
pages) rather than added from the reviewer's own descriptive labels
unverified -- consistent with this project's standing discipline of never
citing a source without confirming it independently.

Not added: the reviewer's suggested news-media citations (Reuters, Guardian,
EU Commission country report, OECD 2024) were deliberately not added to the
academic paper's literature review, since the reviewer's own guidance was
that these "should illustrate the public puzzle, not serve as proof of the
models" -- a role better suited to the report and narrative companion's
existing external-corroboration sections (Greece in Figures, diaNEOsis,
Greekonomics.gr) than to a working paper's formal §3. Left as a possible
future addition if the author wants a "press coverage" aside, not treated
as a gap in this pass.

All three documents re-verified (tag balance, in-browser console-error
checks) and republished to their existing Artifact URLs after these
changes.

## Second-round methodological review: selection leakage, permanence
## assumption, and reproducibility fixes (2026-08-20, same day, third pass)

A second, more technical external review of the literature-response round
above found three P1 (blocking) issues and two P2 (wording) issues before
the round should be committed. All three P1 issues required new analysis,
not just documentation edits, and were run in full before any document text
was changed. The reviewer's own framing turned out to be correct on all
three points; none was a false alarm.

**Fix 1: FDR correction is now computed inside `38_cumulative_hardship.py`
itself, from full-precision p-values, and declared as a script output.**
Previously `cumulative_hardship_fdr_correction.csv` was generated by an ad
hoc one-off analysis outside the script, using the checkpoint CSV's
4-decimal-rounded `p_value` column as input rather than the underlying
full-precision p-value. Fixed at the root: both candidate-battery loops
now also store `p_value_raw` / `p_raw` (unrounded, straight from the fitted
model's `.pvalues`), and a new section runs
`statsmodels.stats.multitest.multipletests` on those 18 full-precision
values directly inside the script, writing
`cumulative_hardship_fdr_correction.csv` as one of its declared outputs.
Re-running confirmed the reviewer's own prediction ("the substantive
conclusion will almost certainly remain unchanged") — the corrected numbers
are close to, but not identical to, the ad hoc round's rounded-input
numbers:
  - `cum_excess_unemployment`: raw p=0.000132 &rarr; FDR-adjusted p=**0.00238**
    (previously reported, from rounded input, as 0.0018). Still survives
    comfortably.
  - `wage_years_below_2008`: raw p=0.004533 &rarr; FDR-adjusted p=**0.0408**
    (previously reported as 0.0405). Still survives, still narrowly.
  - All other 16 candidates: unchanged conclusion, none survives
    (adjusted p&ge;0.25).
  All three documents' FDR numbers updated to the newly-correct values.

**Fix 2: selection-leakage check — and this one changed the honest story,
not just the numbers.** The reviewer's core point: `cum_excess_unemployment`
was picked as "the preferred candidate" using the full 27-country panel,
Greece included, so language like "the final model was built without ever
seeing Greek data" (narrative companion) overstates what leave-one-country-out
actually demonstrates — LOO re-estimates *coefficients* without Greece for
an *already-chosen* variable; it says nothing about whether Greece's own
data point influenced *which* variable got chosen in the first place. Ran
the reviewer's own "at minimum" check: reran the complete 18-candidate
screening (both battery loops) with Greece dropped from the panel entirely
— not evaluated out-of-sample, excluded from model-fitting altogether — and
compared p-values with vs. without Greece in the screening data.
  **Result: `wage_years_below_2008` (p=0.0036 without Greece) edges out
  `cum_excess_unemployment` (p=0.0064 without Greece) once Greece is fully
  excluded from candidate selection.** Both remain highly significant
  either way, and both are the same two candidates that survive FDR
  correction with Greece included — the *ranking between the top two*
  changes, not which two are worth taking seriously. Saved as
  `cumulative_hardship_selection_excl_greece.csv`. This is a genuine,
  reportable limitation, not a technicality to bury: it means the
  "cum_excess_unemployment is unambiguously THE central mechanism, with
  wage-duration merely supporting" framing was too strong. Documents
  revised throughout to present cumulative excess unemployment and
  wage-years-below-2008 as **two closely related, mutually reinforcing
  measures of sustained hardship** (they correlate at r=0.95 within
  Greece's own time series specifically), with cumulative excess
  unemployment retained as the headline construction because it has the
  cleanest direct interpretation (a labor-market variable, not one step
  removed via wages) and is the stronger FDR survivor with Greece included
  in the panel — the way variable selection is actually and legitimately
  done in this project (Greece's data is a real part of the historical
  record, not an artificial contaminant) — while being explicit that the
  two are not independently, unambiguously ranked once Greece is held out
  of the selection step itself. "Built without ever seeing Greek data" and
  equivalent phrasing corrected throughout to distinguish LOO coefficient
  re-estimation (true, tested, stable) from candidate-selection independence
  (not true, now tested, and closer than the original framing implied).
  Note on scope: this is the "at minimum" fix the reviewer named, not the
  stronger (and substantially more expensive) fix of repeating the full
  18-candidate selection separately inside each of the 27 LOO training
  folds — flagged as a further, not-yet-done robustness step if this paper
  moves toward submission.

**Fix 3: permanent-accumulation assumption tested against rolling-window and
decayed alternatives.** `cum_excess_unemployment` is a floored, strictly
non-decreasing running sum — on its own it cannot distinguish "genuine
undiminished accumulated scarring" from simply encoding "how many years
since the crisis began" (a trend/time proxy that would also always
increase). Built and tested five alternative constructions from the same
underlying per-year excess-unemployment series, all of which CAN fall over
time unlike the permanent sum: trailing 3-, 5-, and 10-year rolling sums,
and two exponentially-decayed running sums (20%/year and 10%/year decay).
Each tested the same way as every other candidate (added individually to
Model C-LTU, R&sup2;, Greece in-sample and out-of-sample residual,
coefficient, p-value). Saved as `cumulative_hardship_rolling_decay_battery.csv`.
  Results, sorted by how well each closes Greece's gap:
  - **10-year rolling window**: R&sup2;=0.932, Greece OOS=&minus;0.47,
    p=0.000023 — the *strongest* of all six by both R&sup2; and p-value,
    and closer to a perfect out-of-sample fit than the permanent sum.
  - Permanent sum (the preferred variable): R&sup2;=0.930, OOS=&minus;0.82,
    p=0.000132.
  - 10%/year decay: R&sup2;=0.934, OOS=&minus;1.90, p=0.000056 — strong fit,
    but overshoots (more negative residual) more than the permanent sum.
  - 20%/year decay: R&sup2;=0.931, OOS=&minus;1.78, p=0.000297 — same
    pattern, slightly weaker.
  - 5-year rolling window: R&sup2;=0.922, OOS=0.98, p=0.0418 — borderline,
    clearly weaker.
  - 3-year rolling window: R&sup2;=0.917, OOS=0.93, p=0.293 — **not
    significant**. A short window loses the effect entirely.
  **Honest reading**: this is good news for the underlying mechanism and
  bad news for the specific "permanent, never-fading, must-accumulate-since-
  exactly-2009" framing. A 3&ndash;5-year window is too short to capture
  the effect — this rules out "it's just a short recent bad patch." But a
  10-year rolling window (which literally forgets anything older than a
  decade) fits *at least as well as*, and by some metrics better than, the
  permanent since-2009 sum. That means the finding is better described as
  **sustained excess unemployment over roughly the past decade**, not as
  literal permanent, undiminished accumulation since the exact crisis start
  year. This is a more defensible claim than the one it replaces — it's now
  supported by multiple related constructions converging on the same
  conclusion, not resting on one specific, somewhat arbitrary choice
  (summing forever from a fixed 2009 baseline). "Permanent"/"never fades"/
  similar absolutist language removed from all three documents; replaced
  with "sustained over roughly a decade" framing, with the rolling-window
  finding cited as supporting evidence.

**Fix 4 [P2, wording]: AROPE citation overstatement corrected.**
Bárcena-Martín, Pérez-Moreno &amp; Rodríguez-Díaz (2020)'s published
abstract supports claims about poverty *depth*, *concurrence of dimensions*,
and *different multidimensional profiles hidden behind similar AROPE
rates* — it does not make a claim specifically about *duration*. "Duration"
removed from the attribution to this source in `report.html` and
`academic_paper_draft.html`; the severity/concurrence/hidden-profile claims,
which the abstract does support, are kept. Separately, "Eurostat does not
publish how AROPE's three components overlap at the household level" was
narrowed to "the published aggregate tables used here do not reveal
household-level overlap" — EU-SILC microdata can support overlap analysis
under controlled research access, so the stronger absolute claim
("Eurostat does not publish [ever, anywhere]") overstated what is actually
a data-access limitation of this project's aggregate-only pipeline, not a
limitation of Eurostat's data holdings in general.

**Fix 5 [P2, wording]: chronology fix in the narrative companion.** "That's
exactly why this chapter treats cumulative excess unemployment as the
headline result..." (Chapter 8 method note) reversed the actual order of
events — the evidentiary hierarchy (central mechanism vs. supporting
evidence) was set from magnitude, LOO stability, and the replacement test,
*before* the FDR correction was run late in this session. Corrected to
"This confirms the chapter's treatment of cumulative excess unemployment as
the headline result..." — the FDR check is confirmatory of an
already-made editorial decision, not the basis for it.

No files were changed before this analysis was run and reported in full;
the reviewer's own note ("No files were changed during this review") is
accurate and is why this fix-then-report sequence was possible without
reverting anything.

## Age-breakdown checkpoint (2026-08-20, fourth pass): does the aggregate
## AROPE recovery conceal a generational redistribution?

Triggered by an external review of a Greece in Figures article
(`greeceinfigures.com/ftoxeia-kai-koinonikos-apokleismos`) making several
specific age-group AROPE/AROP/deprivation claims. Per this project's
standing discipline, none of the article's figures were trusted or
integrated before independent verification against the live Eurostat API
(`ilc_peps01n` for AROPE, `ilc_li02` for AROP, `ilc_mdsd11` for severe
material & social deprivation, `ilc_lvhl11` for very-low-work-intensity;
new script `39_age_breakdown_arope.py`). This is a checkpoint only — none
of the three published documents were touched in this pass, per the
reviewer's own explicit staging ("before integrating this, we should...").

**Verification against the article's specific claims — all confirmed
against live Eurostat data, to the decimal:**
- Overall Greek AROPE: 26.9% (2024) → 27.5% (2025). Confirmed.
- Young adults (18–24): 43.6% (2015, article said "about 44%") → 33.2%
  (2025). Confirmed as improvement from an exceptionally bad starting
  point, not deterioration.
- Children (<18): 27.9% (2024) → 29.6% (2025). Confirmed exactly.
- 65+ AROPE: 27.7% (2025). Confirmed exactly (not the article's 27.8%).
- 65+ AROP: 18.8% (2024) → 20.9% (2025). Confirmed exactly.
- 65+ deprivation: 12.8% (2024) → 14.1% (2025). Confirmed exactly.
- Child AROP: 22.4% (2024) → 22.8% (2025). Confirmed exactly.
- Child deprivation: 13.9% (2024) → 15.9% (2025). Confirmed exactly.
- Overall deprivation: 14.0% (2024) → 14.9% (2025). Confirmed exactly.
- EU27 65+ AROPE 2025: 18.8% (lowest of any EU age group). Confirmed
  exactly. EU27 18–24 AROPE 2025: 26.3% (highest). Confirmed exactly.
- Greece's 65+ AROPE (27.7%) vs. EU27's (18.8%): a 8.9-point gap. The
  article's "about nine points" is confirmed.

**Three of the article's own claims were checked and found inaccurate —
the reviewer's suspicion was correct on all three:**
1. **Age-label error.** The article's "860,000" figure is the AROPE
   persons-count for `Y_GE60` (860.0 thousand, confirmed), not `Y_GE65`
   (666.0 thousand) — the article mislabels a 60+ figure as 65+.
2. **EU ranking error.** The article's heading says Greece ranks 3rd in
   the EU on AROPE; the live 2025 data (all 27 member states) puts Greece
   2nd, behind Bulgaria (29.0%) and ahead of Romania (27.4%) — matching
   Eurostat's own news release, not the article's heading.
3. **The "roughly eight percentage points since 2015" claim for 65+ AROPE
   undersells it.** The actual Eurostat figure is 17.5% (2015) → 27.7%
   (2025) = +10.2 points, not ~8. Full year-by-year trajectory pulled and
   confirmed monotonic-ish with an acceleration in the last two years
   (23.9% in 2023, 24.9% in 2024, 27.7% in 2025).

**New finding, not in the article at all: a shift-share decomposition
shows the elderly increase is not a contributing factor among several —
it is single-handedly responsible for more than the entire national
change.** Using each age group's population share (backed out from the
AROPE persons-in-thousands and rate columns Eurostat publishes alongside
each other, not assumed) and applying a standard two-term shift-share
decomposition (within-group rate change vs. between-group population-
composition shift) to the 2024→2025 national change:
  - **Within-group (rate) effect: +0.598pp** — dominates the total change.
  - **Between-group (demographic composition/aging) effect: +0.018pp** —
    negligible. This directly answers the reviewer's step 5 ("separate
    demographic aging from increased individual risk"): the population is
    not meaningfully aging into a higher-risk bracket year over year; the
    risk itself is rising within the 65+ group specifically.
  - Per-group contribution to the +0.622pp reconstructed total: Y_LT18
    +0.283pp, Y18-24 −0.088pp, Y25-49 −0.094pp, Y50-64 −0.154pp, **Y_GE65
    +0.651pp**. Every working-age group's rate *improved* (negative
    contribution); the elderly group's own rate increase is larger than
    the entire net national change, meaning it is offsetting real
    improvement everywhere else, not just adding to it.
  Full table: `data/processed/age_breakdown_shiftshare_decomposition.csv`.

**Structural note on very-low-work-intensity**: confirmed directly (not
assumed) that Eurostat's `ilc_lvhl11` has no age breakdown at all above
59 — the indicator is structurally defined only for the population aged
0–59 (a household work-attachment concept). This independently confirms
the reviewer's own point: the 65+ AROPE increase cannot mechanically
involve the work-intensity component at all, since that component isn't
defined for this age group. The 65+ increase must come from AROP, severe
deprivation, or their (unobservable, per the AROPE-decomposition
limitation already documented above) overlap — both of which did in fact
rise for this group (AROP +2.1pp, deprivation +1.3pp, 2024→2025).

**Not yet done, from the reviewer's own 6-step checklist**: household
type, tenure, and sex robustness checks for the elderly jump (step 6) were
only partially touched — a real gender gap is visible in the raw data
(65+ AROPE 2025: women 30.9%, men 23.6%, a 7.3-point gap, not yet
decomposed further) but a full household-type/tenure-controlled check was
not run. Flagged as a further step, not yet integrated into any narrative
claim.

**Disposition**: this is a strong, verified, decision-ready checkpoint —
every one of the article's checkable claims either confirmed to the
decimal or specifically corrected, plus a genuinely new decomposition
result the article didn't attempt. Per the explicit staging instruction,
no integration into `report.html`, `narrative_companion.html`, or
`academic_paper_draft.html` has been done yet — awaiting agreement on
scope and placement (a candidate working title, "Recovery did not reach
every generation," was proposed alongside the checkpoint request).

### Bounded household-type follow-up (same day, before integration)

Extended `39_age_breakdown_arope.py` with a tightly-scoped household-type
check, per explicit instruction to clarify *who* among older people is
most exposed without delaying the section further. Six items requested;
all six checked directly against Eurostat, three came back as genuine
findings and three came back as "this cross-tab doesn't exist, reported
honestly rather than inferred."

**Confirmed findings:**
- **65+ AROPE by sex, over time** (native age x sex dimension, not
  inferred): Greek women 65+ rose from 18.7% (2015) to 30.9% (2025),
  +12.2pp. Greek men 65+ rose from 15.9% to 23.6%, +7.7pp. The gender gap
  within Greece's own elderly population widened from 2.8pp (2015) to
  7.3pp (2025). At EU27 level over the same period, women 65+ actually
  *fell* slightly (20.6% -> 21.2%, roughly flat) and men stayed flat
  (14.7% -> 15.8%) — Greece's elderly women are diverging sharply from
  the EU pattern, not simply worse off in the same direction.
- **Single 65+ households vs. 65+ couples** (`ilc_peps03n`/`ilc_li03`,
  `hhcomp=A1_GE65` / `A2_GE1_GE65`, a genuine Eurostat household-
  composition dimension): Greek single-elderly AROPE rose from 23.0%
  (2015) to **38.7%** (2025), +15.7pp — the single largest generational
  finding in this whole checkpoint. Greek 65+-couple AROPE rose from
  18.2% to 26.2%, +8.0pp — real, but roughly half the single-elderly
  increase. AROP-only tells the same story (single 65+: 20.2% -> 30.7%,
  +10.5pp; couples: 10.9% -> 17.8%, +6.9pp). Cross-country context: Greek
  single-elderly households started *below* the EU27 average in 2015
  (23.0% vs. 26.9%) and are now *above* it (38.7% vs. 30.0%) — a genuine
  reversal, not just a persistently bad starting position getting worse
  in parallel with the rest of the EU.

**Checked and found NOT to exist as genuine Eurostat statistics — not
inferred, reported as absent:**
- **Sex within single-elderly households.** `ilc_peps03n`/`ilc_li03` have
  no `sex` dimension at all. `F1`/`M1` in the same tables are single-
  person households of *any* age, not age-restricted — combining them
  with `A1_GE65` would infer a cross-tab Eurostat doesn't publish, exactly
  what the explicit instruction warned against. Not done.
- **Age/household-type x tenure, as an outcome rate.** `ilc_lvho07c`
  (housing-cost overburden by tenure) has no age or household-composition
  dimension at all. `ilc_lvho02` does cross household composition with
  tenure, but inspection of its actual values shows it is a population-
  *distribution* table (what share of each household type lives in each
  tenure category, summing toward 100), not an overburden-*rate* table —
  using it to claim "single elderly owners face X% housing-cost
  overburden" would not be a real Eurostat statistic. Tenure is excluded
  from the household finding as a result, exactly as anticipated by the
  original conditional instruction ("tenure only if Eurostat provides a
  genuine age-by-tenure cross-tab").
- **Formal sampling uncertainty.** Checked the raw SDMX-JSON `status`
  field (where Eurostat would carry reliability/break flags) on every
  query in this script directly — empty on all of them. No standard error
  or confidence interval is exposed by the dissemination API for these
  cells. The qualitative caution instead: Greece's single-65+ population
  is real but modest (273 thousand people in 2025, per the AROPE
  persons-in-thousands column already fetched), so year-over-year
  single-year movements for this and smaller subgroups carry more normal
  EU-SILC sampling variance than the national headline rate; the
  decade-long trend is the load-bearing claim, the single-year 2024->2025
  jump is corroborating, not independently definitive.

**Revised story, per instruction, replacing the earlier draft framing**:
Greece's aggregate AROPE increase in 2025 was not caused by population
aging (shift-share composition effect: +0.018pp, negligible) and was not
shared evenly across generations. Every working-age group's own rate
improved. Children saw a real, recent reversal. Among people 65+ — whose
own deterioration is large enough on its own to outweigh the working-age
improvement — the burden is concentrated specifically among women and
people living alone, with single-elderly households showing the single
largest movement of any group or subgroup checked in this entire
checkpoint (+15.7pp since 2015) and a reversal from below- to above-EU-
average over the same span.

**Title changed** per explicit instruction, from the earlier working title
("Recovery did not reach every generation" — rejected because the
shift-share result shows several groups *did* improve) to **"The national
average hid a generational reversal"** (alternate offered: "Recovery
reached generations unevenly").

**Integration scope agreed, not yet built**: a supporting section in all
three documents (age-trajectory chart; a 2024->2025 shift-share figure; a
compact elderly AROP/deprivation/AROPE table; a short household-profile
paragraph; a methods caveat covering the AROPE union limitation, survey
uncertainty, and the structural absence of low-work-intensity measurement
for 65+). Kept separate from the main country-year regression by design —
this is a within-Greece distributional result, not another candidate
explanation for the cross-country residual — but positioned to strengthen
the AROPE-bridge framing and the Discussion.

### Integration built (same day)

All five requested components built into all three documents.
`09_export_report_data.py` extended to load the six new `age_breakdown_*`
CSVs and export five new bundle keys
(`age_arope_trajectory_gr`, `age_shiftshare_2024_2025`,
`age_elderly_table`, `age_65plus_by_sex`, `age_household_arope`);
`inject_data.py` re-run to embed the refreshed JSON into `report.html`.

- **`report.html`**: new subsection "The national average hid a
  generational reversal" in Section 11 (the "scars beneath the gap"
  section), placed after the migration subsection. A 5-series JS line
  chart (age-group AROPE trajectories, 2015-2025, using the existing
  `lineChart()` engine); a `barChart()` shift-share figure (each age
  group's own contribution to the 2024-to-2025 national change); a
  JS-populated compact table (65+ AROP/deprivation/AROPE/national-AROPE,
  five years); a household-profile finding box (sex and household-type
  breakdown, with EU comparison); a full Methods aside covering
  construction, the three checked-and-absent cross-tabs, and the
  qualitative uncertainty caveat. Verified in-browser: 5 chart paths, 10
  bar-chart rects (5 bars + 5 hit targets), 5 populated table rows
  matching the source CSVs exactly (2015 row: 13.7/7.1/17.5/32.4; 2025
  row: 20.9/14.1/27.7/27.5).
- **`narrative_companion.html`**: new Chapter 10, same title, inserted
  between the migration chapter (now 9) and the pessimism chapter (now
  11) — all subsequent chapters renumbered (13 chapters total, up from
  12), masthead count and every cross-reference updated. Uses the
  document's existing `.pull` big-number callout and `.proof` table
  patterns (three tables: age-group 2015-vs-2025, the shift-share
  breakdown, and the who's-most-exposed household table) rather than new
  hand-plotted SVG charts, consistent with this document's established
  mix of prose/pull-quote/proof-table and reserving hand-drawn charts for
  its most central visual moments.
- **`academic_paper_draft.html`**: new §6.8 "A generational reversal
  behind the aggregate AROPE bridge," inserted before the
  candidate-explanations-ruled-out subsection (renumbered to §6.9).
  Includes a genuine SVG line chart (Figure 6, programmatically generated
  from the same source data to guarantee coordinate accuracy, matching
  this document's existing chart visual style exactly) and a data table
  (Table 4). Two new Limitations bullets added to §8 covering the
  descriptive/non-causal status of the finding and the three
  checked-and-absent sub-breakdowns.

All three re-verified (tag balance; in-browser console-error and
chart-element checks) and republished to their existing Artifact URLs.

### Follow-up: why 2015 and not further back (same day)

User asked directly why the age-breakdown checkpoint starts in 2015 rather
than matching the rest of the project's 2003 start. This had not actually
been verified before being used as the range for all four series (AROPE,
AROP, deprivation, low-work-intensity) — checked properly rather than
just explained after the fact:

- **AROP-by-age** (`ilc_li02`): no legacy/revised break at all, confirmed
  by checking there is no "new" AROP series to splice against. Full
  history available back to 1995.
- **AROPE-by-age** (`ilc_peps01n`) and **deprivation-by-age**
  (`ilc_mdsd11`): carry the same legacy/revised break as the rest of this
  project's AROPE series, but the revised, age-broken-down version is
  only disseminated from 2015 onward. Checked whether splicing legacy
  (`ilc_peps01`/`ilc_mddd11`, back to 2003) with revised data would be
  safe, the same way the project already splices the whole-population
  series — it isn't: the 2015-2020 overlap shows an age-specific gap of
  up to 7.3 points (18-24) and 5.4 points (65+), well past the ~1-3-point
  gap already tolerated for the whole-population splice, and larger than
  several of this checkpoint's own headline findings. Not spliced, per
  direct instruction, and the check is now a permanent, reproducible part
  of `39_age_breakdown_arope.py` (`age_breakdown_legacy_revised_overlap_check.csv`).

**Resolution, per explicit instruction**: AROP-by-age extended to 2003
(`YEARS_AROP = range(2003, 2026)`, fetched separately from the other three
series, which stay 2015-2025). This surfaced a genuinely useful piece of
context: Greek 65+ AROP was 29.4% in 2003, fell to a low of 11.6% in 2018,
then rose for seven consecutive years to 20.9% in 2025 — still below its
2003 level. The current elderly deterioration is a substantial partial
reversal of an earlier, larger improvement, not unprecedented territory.
Added as one explanatory paragraph in each document's Methods/method-note
section (not a new chart, and not pulled into the main 2015-2025
comparison), using close to the user's own supplied framing verbatim.
`09_export_report_data.py` and `inject_data.py` re-run (bundle keys
unaffected in shape, since `age_elderly_table` already filtered to
specific years present in the data). All three re-verified and
republished.

## Reporting-style / cultural-premium robustness checkpoint (2026-08-20,
## fifth pass) — new script `40_reporting_style_robustness.py`

Anticipates the obvious reviewer critique directly rather than waiting for
it: if Greece already reported the EU's highest subjective poverty before
the crisis even began, maybe part of the gap is a stable reporting-style
or cultural effect rather than something material conditions explain. Six
tests run, matching the reviewer's own list exactly. Checkpoint only — no
document changes made yet.

**1. Pre-crisis level (2003-2008).** Greece averaged 50.6% subjective
poverty, 2nd-highest of 26 EU countries with coverage (behind Bulgaria,
68.6%). **A stable baseline component cannot be ruled out** — this is
conceded directly, not argued away.

**2. Raw gap widening, pre-crisis vs. current.** Greece's subjective-
minus-AROP gap: 30.4pt (2003-2008) &rarr; 50.2pt (2019-2024), **+19.8pt**.
Ranked against all 25 other EU countries with coverage in both windows,
Greece's widening is **the largest of any country, by a wide margin** —
median widening among the other 25 was actually **&minus;8.8pt** (most
countries' gaps *shrank* over the same span, not grew). A pure stable-
premium story predicts a roughly constant gap over time; this is close to
the opposite pattern.

**3. Formal difference-in-differences.** Two-way fixed-effects panel
(country FE absorbs each country's own pre-existing baseline; year FE
absorbs common EU-wide shocks), with a Greece x post-2009 interaction
term, clustered by country: **coefficient +22.3 points, p&lt;0.0001**.
Greece's own incremental shift after 2009, net of its own baseline and
common EU-wide year effects, is large and highly significant. Noted
explicitly as a limitation: with a single treated country against 26
controls, country-clustered SEs are this project's standard convention
but a real limitation of this specific design (not a fully rigorous
synthetic-control or permutation-inference test).

**4. Out-of-sample residual stability, current-conditions-only model
(Model C-LTU, no cumulative-exposure term).** Mean residual 3.9pt, but
**standard deviation 6.3pt** (larger than the mean) and a **linear trend
of +1.8pt/year**. A stable premium would show a small, flat residual
across years; instead the residual starts negative (model overpredicts
Greece in 2015-2016), crosses zero around 2018, and grows to +11 to +14pt
by 2021 and 2024 — the same trending pattern the cumulative-hardship
checkpoint (above) already explained with accumulated labor-market
exposure, not a constant offset.

**5. Cross-indicator comparison — the most novel and diagnostic test.**
If Greece's extremity were a generic response-style effect, it should
show up equally on ALL self-reported wellbeing measures, not just
financial ones. Checked against Eurostat's overall life-satisfaction
series (`ilc_pw01`, 2018 and 2021-2024, the years with EU-wide coverage)
alongside subjective poverty and financial expectations (already in this
project's pipeline):
  - **Subjective poverty ("can't make ends meet")**: Greece ranks **1st
    of 27, every single year** (2018, 2021-2024).
  - **Financial expectations** (pessimism about the household's own
    finances next year): Greece ranks **1st of 27, every single year**.
  - **General life satisfaction**: Greece ranks 4th, 6th, 3rd, 3rd, 2nd
    worst across the same years — bad, but **not always the extreme, and
    never as extreme as its financial-hardship ranks**.
  Greece is not uniformly the most negative self-reporter in the EU on
  everything — it is specifically and consistently the most negative on
  financial/material self-assessment. That pattern is hard to reconcile
  with a generic cultural-pessimism explanation and easier to reconcile
  with something tied to actual financial circumstances specifically.

**6. Institutional trust.** Not re-tested — Eurostat's holdings remain a
single year (2013), already documented elsewhere in this project as
insufficient for any panel or before/after comparison.

**Conclusion, closely matching the framing proposed alongside the request
(not just adopted uncritically — each piece checked against the actual
numbers above before accepting it)**: Greece did enter the crisis with
unusually high reported difficulty (test 1), so a stable reporting
component cannot be fully ruled out for the *baseline* level. But the
crisis-era *increase* was itself the largest widening of any EU country
(tests 2-3), the model residual is unstable and trending rather than flat
(test 4), and the extremity is specific to financial self-assessment
rather than general wellbeing (test 5) — three independent pieces of
evidence, not one, all pointing the same direction. Culture may set part
of Greece's baseline; it does not explain the crisis-era movement, and
the fact that accumulated labor-market exposure independently closes most
of the residual (the cumulative-hardship checkpoint, above) is additional,
separate evidence against a purely cultural reading of the *current* gap.

**Disposition (superseded by the second-pass battery below)**: strong,
decision-ready checkpoint, not yet integrated into any of the three
published documents. Natural placement, per the original framing: a
robustness/context subsection (e.g. "Is Greece always high because
Greeks report hardship differently?"), positioned after the main
cross-country residual/scorecard material as an anticipated-critique
response, not as a new primary finding.

---

### Reporting-style checkpoint, second pass: full robustness battery + literature review (2026-08-20)

Requested explicitly before integration: a balanced-coverage audit, a full
DiD robustness battery (event study, alternative treatment dates,
country-placebo/randomization inference, leave-one-control-out, a
periphery comparator, synthetic control), standardized (not just ranked)
cross-indicator deviations, residual-trend specification sensitivity, and
a four-strand literature review. Implemented in `scripts/41_reporting_style_robustness_v2.py`
(Parts 1-2) and `scripts/42_reporting_style_robustness_v3.py` (Parts 3-4).
Every item below was run, not assumed.

#### Part 1 — Balanced-coverage audit for "2nd of 26, 2003-2008"

The first-pass ranking used an **unbalanced** panel (countries with
however many years of 2003-2008 data they happened to have). Audited
directly: EU-SILC's true "gentlemen's agreement" launch group — the only
six countries with full 2003-2008 (6-year) coverage — is **AT, DK, LU,
BE, EL, IE**. This is confirmed independently by Eurostat's own EU-SILC
metadata (see literature section below), not just inferred from the data.

  - **Full-coverage-only, n=6 (2003-2008)**: Greece ranks **1st of 6**
    (50.6%, vs. Ireland 23.9%, Belgium 17.7%, Austria 11.3%, Denmark 7.6%,
    Luxembourg 6.6%).
  - **2005-2008 balanced, n=25**: Greece ranks **2nd of 25** (52.6%,
    behind Bulgaria 68.6%).
  - **2007-2008 balanced, n=26 (near-complete EU coverage)**: Greece
    ranks **2nd of 26** (53.5%, behind Bulgaria 65.9%).

All three balanced windows **confirm rather than undermine** the original
claim — Greece was already at or near the top of the EU distribution
before the crisis regardless of which properly-balanced panel is used.
The "2nd of 26" framing understates it slightly: on the one panel with
genuinely complete 2003-2008 coverage, Greece was 1st, not 2nd.

#### Part 2 — Difference-in-differences robustness battery

All built on a 2007-2025 panel (27 countries, 19 years, n=510 — chosen
because Part 1 established this is the first window with near-universal
coverage).

- **Event study** (Greece's year-specific deviation from its own 2008
  baseline, country + year FE): flat and non-significant pre-2009
  (2007 coefficient &minus;0.96, p=0.17 — no pre-existing differential
  trend), then rises sharply and monotonically from 2009 onward, crossing
  significance by 2011 (p&lt;0.01) and plateauing at 24-29pt from 2015
  onward. A textbook clean pre-trend/post-break pattern.
- **Alternative treatment dates** (2009/2010/2011): coefficient stable
  across all three (20.3, 21.0, 22.3 points), all p&lt;1e-70 — the result
  does not depend on the exact year chosen.
- **Country-placebo / randomization inference**: every one of the 27 EU
  countries treated in turn as if it were "Greece," same model. Greece's
  true coefficient (+20.3) is the **largest of all 27**, rank 1 of 27 —
  **empirical p-value = 0.037**. This randomization-inference p-value is
  the one to trust; the naive cluster-robust p-value (~1e-77) is not
  credible with a single treated cluster and is reported only for
  completeness.
- **Leave-one-control-country-out**: dropping each of the 26 control
  countries in turn, the Greece x post-2009 coefficient stays in a tight
  range [19.9, 20.6], all p&lt;0.05 — not driven by any single comparator.
- **Periphery-only comparator** (Greece vs. Italy, Spain, Portugal,
  Cyprus, Malta): coefficient +24.5 (p&lt;0.0001) — if anything larger
  than against the full EU panel, so restricting to Greece's closest
  structural peers does not weaken the result.
- **Synthetic control**: first attempt (donor pool = the 5 countries with
  full 2003-2008 **and** full post-period coverage: AT/BE/DK/IE/LU)
  **failed outright** — RMSE 25.32pt, optimizer collapsed to ~100%
  Ireland, because none of these wealthy comparators resemble Greece's
  high pre-crisis level. Reported as a failed/null result, not hidden,
  and root-caused to donor-pool composition, not an optimizer bug.
  **Corrected version**, matching on 2007-2008 instead (per Part 1's own
  finding that this is the first near-universal-coverage window, opening
  the donor pool to 25 countries): RMSE&asymp;0.00 pre-period fit, with
  sensible weights on higher-hardship Southern/Eastern European
  comparators (Bulgaria 35.8%, Portugal 25.4%, Cyprus 21.4%, Hungary
  9.9%, Latvia 5.4%, Slovakia 2.1%). Post-2009, actual and synthetic
  Greece diverge from ~2.3pt (2009) to 30-40pt by 2015-2025 (mean
  post-period gap 24.75pt) — an independent, non-regression-based
  confirmation of the DiD result. Both attempts are now reproducible
  directly from `scripts/41_reporting_style_robustness_v2.py` (the
  corrected version was initially run ad hoc and has since been folded
  into the script itself, per this project's standing discipline that
  every result must be reproducible from a numbered script).

#### Part 3 — Standardized cross-indicator deviations

The first-pass check compared EU *ranks* across subjective poverty,
financial expectations, and life satisfaction. Requested: standardized
(z-score) magnitudes, not just ranks, sign-harmonized so all three point
the same direction (positive = worse than the EU average). For the years
common to all three series (2018, 2021-2024):

  - Subjective poverty: average |z| = **3.76**
  - Financial expectations: average |z| = **3.20**
  - Life satisfaction: average |z| = **1.17**

Greece's deviation on the two financial/material indicators is roughly
**3x larger in standard-deviation terms** than its deviation on general
life satisfaction — the same "financial-domain-specific, not generic
pessimism" conclusion as the rank-based test, now quantified rather than
just ordinal. If this were a generic response-style effect, all three
z-scores should be comparably large; they are not.

#### Part 4 — Residual-trend specification sensitivity

Requested: confirm the +1.8pt/year residual trend (test 4 in the
first-pass checkpoint, Model C-LTU) isn't an artifact of that specific
model choice, and confirm the residuals are genuinely leave-Greece-out
predictions each year rather than per-year refits.

**Methodology, stated explicitly** (matching the user's request): one
model is fit on the other 26 countries' pooled panel only — Greece is
excluded from estimation entirely — and that single fitted model is used
to predict Greece's value in every year shown. This is a genuine
out-of-sample prediction throughout: not a fresh per-year refit, and a
specification that never sees Greece's own data at any point.

  | Model | Predictors | Mean residual | Std. dev | Trend (pt/yr) |
  |---|---|---|---|---|
  | A (basic) | unemployment, income, deprivation, AROP | 25.6 | 5.9 | **+1.86** |
  | C (+housing/arrears/unexpected) | + housing cost overburden, arrears, unexpected expenses | 11.6 | 4.2 | **+0.80** |
  | C-LTU (long-term unemployment) | as C, LTU rate replacing headline unemployment | 3.9 | 6.3 | **+1.82** |

All three specifications show a **positive, non-trivial, non-flat**
trend — the "not a stable premium" finding survives specification
changes. The exact magnitude varies (Model C's smaller +0.80pt/yr trend
is plausibly because its housing/arrears variables already absorb part
of the crisis-era arc; swapping in long-term unemployment for headline
unemployment removes that absorption and re-exposes a trend similar to
the basic model). Reported honestly rather than cherry-picking the
strongest spec: the finding is robust in direction and significance, less
so in exact magnitude.

#### Literature review (four strands, as requested)

**Strand 1 — subjective-poverty / financial-strain measurement.**
Eurostat, *"Living conditions in Europe — subjective poverty statistics"*
(Statistics Explained, data extraction Oct 2025) and the companion
*Glossary: Subjective poverty*: subjective poverty is derived from the
EU-SILC "ability to make ends meet" variable (6 categories; "with great
difficulty" / "with difficulty" = subjectively poor) — a genuinely
distinct construct from income-based AROP, not a redundant proxy. Useful,
directly citable, out-of-project confirmation: in the latest published
EU-wide figures, **Greece's subjective poverty rate is 66.8% against an
AROP rate of 19.6% — a 47.2-point gap, the largest such gap of any EU
country** in Eurostat's own headline statistics. That is an independent
replication of this project's central Part I finding from an entirely
separate, official, most-recent-year source. European Commission, DG
Employment/Social Affairs, *"Beyond Income Poverty: Subjective Poverty
and Indebtedness"* (2024, using 2020 EU-SILC data): frames subjective
poverty as capturing perceived income adequacy for necessary expenses,
distinct from and complementary to income poverty, alongside related
measures (over-indebtedness, housing/food/transport/loan burden).

**Strand 2 — cross-country response-style / anchoring-vignette
literature.** The specific unipd.it repository page could not be
accessed directly (403 Forbidden); its likely author, Omar Paccagnella
(University of Padua, Dept. of Statistical Sciences), works on exactly
this literature. The representative peer-reviewed result, found and
verified independently: Angelini, Cavapozzi, Corazzini & Paccagnella
(2014), *"Do Danes and Italians Rate Life Satisfaction in the Same Way?
Using Vignettes to Correct for Individual-Specific Scale Biases,"*
*Oxford Bulletin of Economics and Statistics*. Finding: response-scale
differences explain much of the raw cross-country variation in reported
life satisfaction, and vignette-corrected country rankings differ from
raw rankings — i.e., this general concern (some of cross-country
variation in self-reports is response style, not substance) is real and
documented, which is exactly why this robustness section is worth
running. A closely related finding worth flagging explicitly, because it
cuts **against** a "Greek cultural pessimism inflates the numbers"
reading: vignette-corrected studies of childhood hardship exposure find
that lived hardship causes people to **adopt lower subjective standards**
(adaptation) — naive, non-vignette-corrected associations between
hardship and self-reported distress are biased **toward finding a
muted, not inflated, response**. If this adaptation mechanism applies,
it would work against Greece's high and rising subjective-poverty
numbers being a reporting-style artifact — adaptation would, if
anything, cause under-reporting of accumulated hardship over time, not
over-reporting.

**Strand 3 — pre-crisis Greek conditions.** Katsikas, Karakitsios,
Filinis & Petralias (2015), *"Social Profile Report on Poverty, Social
Exclusion and Inequality Before and After the Crisis in Greece,"*
Crisis Observatory / ELIAMEP (FRAGMEX research programme). Covers
1995-2008 as baseline and 2009-2013 as crisis impact. Findings: poverty
(especially *anchored* poverty) rose sharply after 2009; the contribution
of unemployed-headed households to aggregate poverty rose sharply while
pensioner-headed households' contribution fell (the elderly were
relatively protected). This independently confirms genuine material
deterioration post-2008, not just a reporting shift, and documents that
Greece's pre-crisis (1995-2008) poverty profile was already comparatively
elevated within the EU — consistent with this project's own pre-crisis
finding. Zambarloukou (2015), *"Greece After the Crisis: Still a South
European Welfare Model?"* *European Societies*, 17(5), 653-673: frames
Greece's welfare state as a structurally distinct "South European" model
(thin universal safety net, heavy reliance on family/informal support)
both before and after the crisis, arguing the crisis triggered radical
reform but not a full model change. Supports reading Greece's elevated
baseline as rooted in genuine structural/institutional features of its
welfare state, not a survey-response quirk.

**Strand 4 — crisis movement vs. persistent baseline.** The specific
document requested, SWD(2013) 38, turned out on direct retrieval to be a
general EU-wide document — *"Evidence on Demographic and Social Trends:
Social Policies' Contribution to Inclusion, Employment and the Economy"*
(accompanying the Social Investment Package Communication) — not a
Greece-specific crisis assessment. Reported honestly rather than
force-fitted: it does not appear to contain Greece-specific crisis
analysis, and the ELIAMEP and Zambarloukou sources above (Strand 3)
already cover this strand directly with Greece-specific pre/post-2008
data, so no substitute document was pursued further.

**EU-SILC metadata caution, checked directly** (`ec.europa.eu/eurostat/cache/metadata/en/ilc_sieusilc.htm`,
as specifically flagged): confirms, independently of this project's own
data-driven coverage audit, that "the EU-SILC project was launched in
2003 based on a 'gentlemen's agreement' in six Member States (Belgium,
Denmark, Greece, Ireland, Luxembourg and Austria) and Norway" — an exact
match to Part 1's own empirically-derived full-coverage-six. The metadata
also documents a real caveat worth carrying forward: *"there were
disruptions in series between 2001 and 2005"* during the transition from
the preceding ECHP survey to EU-SILC, and several other EU-15 countries
(Germany, Netherlands, UK) plus nine of the ten 2004 accession countries
did not join until 2005 (with a retrospective-2004-data condition). This
is exactly why Part 1's three-window balanced-panel approach — rather
than trusting the unbalanced 2003-2008 average at face value — was the
right check to run.

#### Final synthesized conclusion (per the user's twice-refined wording, adopted verbatim)

> Greece entered the crisis with an unusually high reported level of
> financial difficulty, so a persistent country-specific reporting
> component cannot be excluded. But a stable reporting tendency cannot
> explain the subsequent deterioration and persistence by itself. The
> appropriate question is not whether Greeks are culturally pessimistic,
> but how much of the baseline and later movement remains after
> comparable material conditions and accumulated exposure are
> considered.

Every individual test in this battery is consistent with that wording:
the baseline concession (Part 1) is real and not argued away; every
crisis-era test (Part 2's six independent checks, Part 3, Part 4) points
the same direction and survives every robustness variant tried; and the
literature review supports a structural/institutional reading of the
baseline (Strand 3) over a cultural-pessimism one, while flagging that
the general response-style concern this section exists to address
(Strand 2) is real in the literature but, if anything, cuts against
rather than for a reporting-artifact explanation of Greece's specific
pattern.

**Disposition**: coverage audit, full DiD battery, standardized
cross-indicator comparison, residual-trend specification sensitivity,
and the four-strand literature review are now all complete and logged.
This is now a fully decision-ready checkpoint. Per the user's explicit
instruction, integration into the three published documents
(`report.html`, `narrative_companion.html`, `academic_paper_draft.html`)
— positioned after the cumulative-hardship section as a "Could this
still be reporting culture?" robustness challenge — awaits explicit
go-ahead before proceeding.

**Integration complete (2026-08-20)**: approved by the user ("yes
integrate") and applied to all three published documents, each in its
own voice, in the position specified &mdash; after the cumulative-hardship
material, as a robustness/context section rather than a new headline
finding.

  - **`report.html`**: new section `id="reporting-culture"`, "Could this
    still be reporting culture?", inserted after the Answer-to-Question-2
    box and before the Literature section; added an unnumbered TOC entry.
    Four subsections mirror the checkpoint's six tests (pre-crisis level,
    DiD/event-study/placebo/synthetic-control battery, cross-indicator
    comparison, literature), each with a `finding` box and a closing
    `method-aside` pointing to scripts 40&ndash;42.
  - **`narrative_companion.html`**: new Chapter 13, "Is this just how
    Greeks talk?", inserted between "What wasn't it" (Ch. 12) and
    "Landing" (renumbered Ch. 13&rarr;14); the table-of-contents preview
    paragraph and Landing's own chapter number were both updated to stay
    consistent. Prose-only, matching the chapter's existing narrative
    voice, with one closing method note.
  - **`academic_paper_draft.html`**: new &sect;6.10, "Reporting
    heterogeneity: a robustness check against cultural-premium
    explanations," inserted after the RQ2 answer callout, before &sect;7
    (Discussion); the &sect;1 "seven stages" roadmap paragraph was
    updated to name it. Six new references added to &sect;references in
    alphabetical order (Angelini et al. 2014; Cameron &amp; Miller 2015,
    cited for the cluster-robust-inference caveat already present in the
    checkpoint's own methodology; two Eurostat citations for the EU-SILC
    metadata and the independent subjective-poverty replication figure;
    Katsikas et al. 2015; Zambarloukou 2015). Closes with a "Robustness
    verdict" callout using the user's twice-refined conclusion wording,
    explicitly scoped as a robustness check that would only be elevated
    to a primary finding if the baseline reporting component proved
    substantial and stable &mdash; which this evidence does not indicate.

All three renders verified directly in-browser (DOM inspection: correct
heading text, table row counts, finding-box counts, TOC/roadmap links,
reference-list entries; zero console errors on any of the three pages).
A pre-existing, unrelated cross-reference bug was noticed in passing
during this pass (academic paper &sect;1 cites "&sect;6.8, income
inequality" where it should read "&sect;6.9") and flagged as a separate
background task rather than folded into this change. Note: this bug was
later superseded and fixed directly (see 2026-08-20 work-effort-squeeze
entry below), since the correct target number changed to &sect;6.10 once
a new subsection was inserted before it.

---

### Work-effort-squeeze checkpoint: user-built, reviewed, corrected, and integrated (2026-08-20)

Prompted by a posted chart showing Greece working the most hours in the
EU (2025) alongside falling real income &mdash; the user's own hypothesis:
does working the most while earning the least per hour also feed the
subjective-poverty gap? The user built and ran the checkpoint
independently (`scripts/43_work_effort_squeeze.py`), then shared full
results for review.

**Review process**: every headline number in the user's write-up was
independently re-derived from the checkpoint's own output CSVs rather
than taken on trust &mdash; hours/pay levels and ranks, the FDR-corrected
model battery, the AROP-bridge gap-closing figures, the within-country
robustness (country-FE and first-difference nulls), the LOO stability
range, and the redundancy-with-cumulative-unemployment check. All
reproduced exactly. One real inconsistency was found and subsequently
fixed by the user: the "employed AROP ranking only sixth" / "AROPE
second" claims in the original write-up were computed from the broader
`EMP` (all employed, including self-employed) population, not the `SAL`
(salaried-only) population the accompanying table displayed &mdash; salaried
AROP rank is actually 17th of 27, not 6th. This strengthens rather than
weakens the finding: salaried Greeks look completely ordinary on official
income poverty and still rank 1st on subjective poverty. A second,
minor correction from the user during review: employed-population AROPE
is tied 2nd (Greece and Romania both 16.0%, behind Bulgaria's 16.3%),
not 3rd &mdash; a rank-without-tie-handling artifact in the reviewer's own
quick check, confirmed via `rank(method="min")`.

**Key results** (salaried workers, 2025 unless noted): AROP 5.7% (Greece)
vs. 6.5% (EU27), rank 17th of 27 &mdash; unremarkable. AROPE 12.5% vs. 9.2%,
rank 3rd. Subjective poverty 59.5% vs. 13.6%, rank 1st of 27 by the
widest margin in the EU. Hours (2024): 39.8/week all employed (highest in
EU, EU27 36.0), 41.1 full-time (highest, EU27 38.8), 1,900 annual hours
per employee (4th-highest, EU27 1,547), salaried-only weekly hours still
7th-highest (ruling out self-employment composition as the sole driver).
Hourly compensation, PPS-adjusted: 14.2, lowest in the EU (EU27 29.6).
Composite "work-effort squeeze" index (relative hours &divide; relative PPS
hourly pay, EU=100): 230.5, highest in the EU. Real hourly compensation
remains 27.8% below its 2008 level. Added to Model C-LTU, FDR-corrected
across a pre-specified 9-candidate family: coefficient 0.078, raw
p=0.00048, FDR-adjusted p=0.0030; Greece's out-of-sample residual moves
from +3.9 (rank 6/27) to &minus;3.5 (rank 21/27); stable and significant
across all 27 leave-one-country-out refits. Alone next to AROP, it closes
8.8 of the raw 47.6-point gap. A matched national-accounts employee-hours
version also survives FDR correction (p=0.0063). An unreported-in-the-
original-writeup hours&times;low-pay interaction term is independently
significant (coefficient 1.52, p=0.024) but was excluded from the
pre-specified FDR family and carries a maximum VIF of 9.05 &mdash; kept as
exploratory corroboration only, never as a headline result.

**Critical limitation, surfaced by the user and independently confirmed**:
the squeeze fails every within-country dynamic test &mdash; country fixed
effects (p=0.34), first differences (p=0.73), and Greece's own
2010&ndash;2024 time-series correlation with subjective poverty (r=&minus;0.03,
p=0.92). This is genuine, FDR-corrected, cross-country structural
evidence &mdash; a stable fact about where Greece sits relative to the rest
of the EU &mdash; not a dynamic mechanism explaining year-to-year movement
the way long-term or cumulative excess unemployment do. Agreed
disposition: integrate as supporting evidence, explicitly excluded from
the scorecard, framed as "who Greece is structurally, not what changed
year to year."

**Integration, applied to all three published documents**, each keeping
the agreed salaried-only framing and structural/dynamic distinction:

  - **`report.html`**: new h4 subsection "Working the most hours, earning
    the least per hour" within Section 11, after the financial-pessimism
    subsection and before the closing eight-country comparison. Two
    tables (salaried AROP/AROPE/subjective comparison; hours vs. hourly
    compensation for a handful of representative countries) replace what
    would otherwise have been an unwired chart placeholder &mdash; this
    report's charts are driven by an embedded JS data blob that a
    checkpoint script's CSVs don't automatically populate, so a
    `data-table` card was used instead, consistent with how several
    other Section 11 findings already present.
  - **`narrative_companion.html`**: new Chapter 12, "Working the most,
    earning the least," inserted between "Hardship extrapolated" (Ch.
    11) and "What wasn't it" (renumbered Ch. 12&rarr;13); "Is this just
    how Greeks talk?" and "Landing" renumbered to Ch. 14 and 15. The
    roadmap paragraph and all internal chapter cross-references were
    checked and updated; none pointed past the insertion point
    incorrectly.
  - **`academic_paper_draft.html`**: new &sect;6.9, "Hourly work effort
    and reward: a structural mechanism that isolates the puzzle from
    unemployment," inserted after &sect;6.8 and before the
    candidates-ruled-out section (renumbered &sect;6.9&rarr;6.10) and the
    reporting-heterogeneity robustness section (renumbered
    &sect;6.10&rarr;6.11). A discussion point was added to &sect;7.2 tying
    the salaried-only result into the paper's broader argument (two
    distinct, population-specific expressions of the same underlying
    claim, not one unified mechanism). A new &sect;8 limitations bullet
    states the cross-sectional-only caveat explicitly. The &sect;1
    roadmap paragraph was updated to name &sect;6.9 and to fix, in the
    same edit, the pre-existing stale "&sect;6.8, income inequality"
    cross-reference &mdash; now correctly pointing to &sect;6.10, the
    number it needed to become once this insertion shifted the
    candidates-ruled-out section.
    **Concurrency note**: a background task requesting the old,
    now-incorrect fix ("&sect;6.8"&rarr;"&sect;6.9") had already been
    started by the user in a separate session before this insertion was
    planned; it could not be withdrawn once started. Its target fix is
    superseded by the correct one applied here. If that separate session
    completes and writes a conflicting edit to the same file, the two
    should be reconciled by re-checking &sect;1's roadmap sentence points
    to &sect;6.10, not &sect;6.9.

All three documents verified directly in-browser (DOM inspection: table
row counts, chapter/subsection sequencing with no gaps or duplicates,
correct cross-reference numbers, zero console errors on any page).

**Post-integration review, two fixes (2026-08-20)**: the user checked all
three published documents directly and confirmed the concurrency risk
above did not materialize &mdash; the academic roadmap correctly reads
&sect;6.9 (work effort), &sect;6.10 (inequality), &sect;6.11 (reporting
style). Two further issues found and fixed:

1. **Overstated claim, academic paper &sect;1 roadmap.** "a structural,
   cross-country-only mechanism that isolates the puzzle from
   unemployment status entirely" overstated the &sect;6.9 evidence as a
   demonstrated causal mechanism, when it is cross-country structural
   evidence that the puzzle persists among salaried workers, not proof
   that unemployment is irrelevant. Reworded to the user's own
   suggestion: "supporting cross-country evidence that the puzzle
   persists even among salaried workers (&sect;6.9, hourly work effort
   and reward)."
2. **Pre-existing, unrelated numerical-language contradiction**, found
   by the user in the age-breakdown material: the EU27 65+ comparison
   line described EU women's AROPE (20.6%&rarr;21.2%, actually +0.6pp) as
   having "fell slightly" and EU men's (14.7%&rarr;15.8%, actually
   +1.1pp) as having "stayed flat" &mdash; both numbers show a rise, not a
   fall or flat line. This sentence had been present since the original
   age-breakdown checkpoint, predating the work-effort-squeeze
   integration, and existed identically in all three published
   documents (`report.html`, `academic_paper_draft.html`,
   `narrative_companion.html`). Fixed in all three to state both groups
   "rose only modestly by comparison" with the correct numbers, keeping
   the underlying point intact &mdash; Greece's elderly women are
   diverging sharply from the EU pattern, since Greece's own rise
   (+12.2pp) dwarfs the EU's (+0.6pp), not because the EU trend runs in
   the opposite direction.

Confirmed no remaining instances of the incorrect wording in any of the
three files after the fix.

---

### Chart UX: nearest-line hover labels on multi-country line charts (2026-08-20)

Requested: in charts showing many countries' lines at once, hovering
should identify which line is which, not just show Greece's value.

`report.html`'s shared `lineChart()` JS function (used by every line chart
in the document) already drew all ~27 EU countries' lines on three charts
&mdash; GDP-recovery-vs-peak, real wages, long-term unemployment &mdash;
but the tooltip was hardcoded to show only Greece (`tooltipSeries:
[{key:'EL', ...}]`), leaving the other 26 gray background lines
unlabeled on hover.

**Fix**: each line's `<path>` now carries a `data-key` attribute. On
mousemove within a chart, the function computes the mouse's vertical
position in chart coordinates and finds whichever "extra" (not-already-
always-shown) series is closest to it at that year; if within 16px, that
country's code and value are appended to the tooltip and its line is
highlighted (bold, switched to the theme's ink color) so it's visually
traceable against the gray background, with everything reset cleanly on
mouseleave. Charts where every series is already always shown in the
tooltip (e.g. the AROPE-by-age-group chart, 5 series) are unaffected,
since there's nothing "extra" to detect.

Verified directly in-browser via simulated `mouseenter`/`mousemove`
events at several cursor positions on all three affected charts: correct
country codes returned when the cursor is actually near a line (e.g.
Slovenia on the recovery chart, Slovakia on the wages chart), no false
match when it isn't, and clean reset on `mouseleave`. Zero console
errors.

**Scope note**: `narrative_companion.html` and `academic_paper_draft.html`
have no JS interactivity at all &mdash; their charts are static,
pre-rendered SVG paths with no `<script>`, tooltip elements, or event
listeners. This fix applies to `report.html` only, the sole document
with an interactive chart engine; adding hover behavior to the other two
would mean building chart interactivity from scratch, a separate and
substantially larger task, not attempted here.

---

### Multiple-testing audit and remediation: Section 4's live correlation table (2026-08-20)

Prompted by the user's audit question ("did we adjust for multiple testing
everywhere needed?"). Full audit findings, then the user's own independent
re-derivation (which caught a deeper issue than the one first reported),
then the fix actually applied.

**Audit finding**: every other multi-candidate battery in the project was
already correctly FDR-corrected &mdash; cumulative-hardship (script 38,
18-candidate family), work-effort-squeeze (script 43, two 9-candidate
families), Section 11's swing-sensitivity test (9 predictors, script 27).
Age-breakdown (script 39) is purely descriptive, no correction needed.
Reporting-style robustness (scripts 40-42) is mostly single planned tests
or already uses an appropriate method (randomization inference for the
country-placebo test, which doesn't need FDR on top since it produces one
honest p-value from a reference distribution, not many separate claims).

**The gap**: Section 4's live correlation table (raw / year-over-year /
trend-removed columns, the one readers actually see) had never had FDR
correction applied to its year-over-year or trend-removed columns. A
dedicated correction script (27) existed, but it corrected a *different*,
earlier, orphaned correlation table (`correlations.csv`, 21 variables,
contemporaneous + one-year lag, from script 06) that is exported into
`report_data.json` but never rendered anywhere in the live document. The
Methods appendix's "16 of 21 survive correction" claim described that
orphaned analysis, not the table's actual significance flags.

**User's independent re-derivation went further**: reproduced the 18-row
result exactly (15/18 YoY survive, 16/18 detrended survive, real wages
flips from raw p=0.0489 to FDR-adjusted p&asymp;0.0518), but also caught that
`10_robustness_correlations.py`'s own `predictors` dict already declared
19 variables (including AROPE), while the checked-in CSV and displayed
table were stale at 18 rows &mdash; the script had been edited to add AROPE
at some point but never rerun. With AROPE correctly included: 16/19 survive
YoY, 17/19 survive detrended, real wages narrows further to adjusted
p&asymp;0.0516. Correct instruction: fix the pipeline/output staleness
first, do not patch around it by re-deriving a knowingly-incomplete
18-variable table.

**Remediation applied**:

1. **`scripts/10_robustness_correlations.py`** rewritten to compute
   BH-FDR correction directly inside itself, separately for each of the
   three displayed families (level, first-difference, detrended), from
   full-precision p-values before any rounding for display. Added a
   warning print for any predictor declared but missing from the
   analysis dataset, so this specific staleness class can't recur
   silently. Rerun: **19 of 19** declared predictors now found and
   tested (confirms the dict/data mismatch is resolved, not just
   patched around). Verified results match the user's independent
   re-derivation exactly: level 17/19 survive (AROP and income
   inequality don't), year-over-year 16/19 survive (severe material &amp;
   social deprivation's newer measure, real wages, and headline HICP
   inflation don't), detrended 17/19 survive (severe material & social
   deprivation's newer measure and real wages don't; HICP is a genuine
   mixed case &mdash; fails YoY, survives detrended, reported as such
   rather than smoothed over). Real wages, detrended: raw p=0.0489,
   FDR-adjusted p=0.0516 &mdash; confirmed to the fourth decimal against
   the user's own figure.
2. **`scripts/09_export_report_data.py`** updated to pass the new
   `p_firstdiff_fdr`, `survives_fdr_firstdiff`, `p_detrended_fdr`,
   `survives_fdr_detrended` columns through into the exported bundle.
3. **`report.html`**'s inline `DATA` blob (previously hand-pasted, not
   auto-synced with `report_data.json`) resynced programmatically: load
   the regenerated JSON, dump it compact (matching the existing
   single-line embedded format exactly), and replace the `const DATA =
   {...};` statement via a precise regex substitution rather than a
   manual paste, given its size (~60KB). Verified via DOM inspection
   that `DATA.robustness` now has all 19 rows with the new FDR fields
   correctly populated, including AROPE.
4. **`report.html`**'s table-rendering JS changed from raw `p < 0.05`
   checks to `survives_fdr_firstdiff` / `survives_fdr_detrended` booleans
   for the "(n.s.)" flags. Verified in-browser via DOM inspection: 19
   rows render, exactly 3 rows carry an "(n.s.)" flag (severe
   material &amp; social deprivation-new, real wages, HICP inflation),
   5 flagged cells total, matching the corrected data exactly.
5. **`report.html`** narrative paragraph following the table rewritten:
   states the corrected 16/19 and 17/19 survival counts, names AROPE's
   strong survival on both tests now that it's included for the first
   time, names all three variables that fail at least one test (not
   just one, as the stale text implied), and flags HICP's mixed result
   honestly. The table's own "n.s." legend note rewritten to define it
   as "does not survive FDR correction," not raw p&ge;0.05.
6. **`report.html`** Section 11's real-wages method-aside sentence
   fixed: "borderline but crosses the conventional 5% threshold" &rarr;
   "borderline before correction, and does not survive FDR correction
   ... adjusted p=0.052."
7. **`report.html`** Methods appendix rewritten to correctly describe
   the current 19-variable, three-family, in-script correction as the
   one governing the live table, with the old 21-variable
   contemporaneous+lag1 screen explicitly relabeled as an earlier,
   superseded, separately-kept exploratory record &mdash; not cited as
   governing any live claim.
8. **`academic_paper_draft.html`**'s equivalent FDR-family paragraph
   (&sect;4.3) rewritten the same way: correct 19-variable/three-family
   description as current, old 21-variable screen explicitly marked
   superseded. `narrative_companion.html` was checked and does not
   contain this content at all, so needed no fix.
9. **Event-study multiple testing (point 8 of the user's plan),
   resolved by inspection rather than by adding a test**: the reporting-
   style DiD panel (script 41) runs from 2007, with 2008 as the omitted
   base year, so there is exactly **one** pre-treatment coefficient
   (2007) in the design &mdash; already the single number reported
   everywhere this is discussed (coefficient &minus;0.96, p=0.17). A
   joint pre-trend F-test requires at least two pre-period coefficients
   to test jointly and doesn't apply here; there is nothing to correct.
   Checked separately: all three published documents already describe
   the ~17 post-treatment year-by-year coefficients only as an aggregate
   pattern ("no sign of the gap already widening before 2009," "rises
   sharply and monotonically post-2009") and never present any
   individual year's coefficient as its own significance claim, so no
   live-document change was needed on this point either.

All fixes verified directly in-browser: `report.html`'s table shows the
correct 19 rows and n.s. flags via DOM inspection; both `report.html` and
`academic_paper_draft.html` load with zero console errors after the
edits; the previously-added nearest-line chart-hover feature (see prior
entry) re-verified still working correctly after the `DATA` blob resync.

---

### Full dual-lens review pass: academic reviewer + reporter (2026-08-20)

Requested by the user: a complete pass over all documentation, planning,
analysis, results, and the three published documents, read once as a
critical academic reviewer (is everything included, correct, and valid)
and once as a reporter publishing this research (is the story concrete,
readable, and catchy). Method: full end-to-end reads of all three
documents' extracted text, README, todo_plan, data_sources,
comparability_notes; numeric spot-checks of contested figures against
the pipeline CSVs directly. **Findings reported to the user; no fixes
applied in this pass** — fix list below is the review's output.

**What holds up (stated first because it's most of the picture)**: every
load-bearing number cross-checks across the three documents and against
the pipeline outputs (headline gaps, scorecard rows, DiD battery, FDR
counts, work-effort figures, age breakdown, salaried table); the
methodological discipline (OOS validation everywhere, per-family FDR,
selection-leakage check, permanence testing, evidentiary labels, honest
nulls) is genuinely strong and consistently applied; the story spine is
coherent and parallel across all three documents.

**Factual errors found (P1)**:
1. `narrative_companion.html` Ch. 12 claims Greece's weekly hours are
   "still highest ... restricted to ... salaried employees only" —
   false: salaried-only hours rank 7th of 27 (Romania highest, 39.0 vs
   Greece 38.0). Report and academic versions state 7th correctly; the
   narrative alone overclaims.
2. Same paragraph: "Greece's own eighteen-year history" — the
   work-effort/subjective series for Greece is 15 years (2010–2024,
   n=15, verified in `work_effort_employed_hardship_panel.csv`).
3. Cross-document inconsistency: academic §2 says unemployment "peaked
   at 27.5%" (Pagoulatos's figure); report §4 and the project's own
   `analysis_dataset.csv` say 27.8% (2013, ages 15–74). Align or
   attribute explicitly.
4. `report.html` has two stale "Section 12" cross-references: the
   executive summary's "Full limitation structure in Section 12"
   (limitations live in Methods) and the Methods line "distinctive in
   scale and duration (Section 12)" (that discussion is in Section 11).
   The literature section's "Answer to Question 2, Section 12" reference
   is correct and needs no change.
5. Academic paper: two tables are both numbered "Table 4" (§6.8 elderly
   and §6.9 salaried — the latter introduced in the work-effort
   integration without checking the existing sequence), and Table 3
   (§7.3) appears after both. Renumber document-order: the §6.9 table
   and everything after shift.

**Stale counts / internal consistency (P2)**:
6. Narrative header badge "13 chapters" → now 15.
7. Narrative Ch. 14: "spent twelve chapters explaining" → thirteen.
8. Narrative Landing: "in eight separate and independently-checked
   ways" — fragile count (arguably nine with Ch. 12); update or remove
   the numeral.
9. Academic §1: "moves through seven stages" — the list that follows now
   has nine items (work-effort and reporting-heterogeneity were appended
   without updating the count).
10. Academic §4.3: "the six-stage argument structure set out in §1" —
    contradicts §1's own (already-wrong) "seven".
11. Report Section 11 intro: "tests seven candidates directly ... in
    three groups" — now eight tested candidates; the work-effort squeeze
    is absent from the intro's taxonomy.
12. Academic §6.9 heading still reads "a structural mechanism that
    isolates the puzzle from unemployment" — the same overstatement the
    user's earlier review fixed in the §1 roadmap wording; the heading
    (and the section's first sentence, "entirely apart from unemployment
    status") kept it.

**Stale scaffolding (P2)**:
13. README run-order table stops at script 39 — scripts 40–43 missing.
14. Data-vintage claims ("2026-08-19") in README, all three documents'
    colophons/badges, and academic §10 are no longer strictly true: the
    work-effort data (script 43) was pulled 2026-08-20.
15. `docs/todo_plan.md` predates scripts 40–43 and still says "Commit:
    pending user confirmation" (commit d673e11 was pushed today);
    `docs/data_sources.md` has no entries for scripts 40–43's datasets
    (lfsa_ewhan2, nama_10_lp_ulc/D1_SAL_HW, ilc_sbjp03, ilc_iw01,
    ilc_peps02n, ilc_pw01, sts_rb_q-adjacent none needed).
16. Academic §3.5 (Contribution) is stale: still names long-term
    unemployment as "the single variable that most changes Greece's
    standing" without mentioning cumulative excess unemployment — the
    paper's own self-declared central new result — or §6.9/§6.11.
17. Academic abstract omits both §6.9 (salaried-worker persistence) and
    §6.11 (reporting-heterogeneity robustness) — the two things a
    referee/reader most wants signposted.
18. Academic §4 data-sources paragraph omits §6.9's datasets.

**Methodological soft spots (acknowledge, not necessarily fix)**:
19. The DiD pre-trend evidence rests on a single pre-treatment
    coefficient (2007; 2008 is the omitted base) — the academic paper
    states this precisely; report.html's looser "there's no sign of the
    gap already widening before 2009" reads stronger than one
    coefficient strictly supports. One qualifying clause would fix it.
20. Academic Table 1 stops at Model F (Model G appears only in Table 2
    and §6.6 text) while report.html's scorecard shows all eight — a
    referee may ask for G as a Table 1 row.
21. References: Zambarloukou alphabetized after the Želinský entries.
22. Two different "wages below 2008" figures (31.8% per-employee, 27.8%
    per-hour) plus a nominal 13.1% figure appear near each other in
    Section 11 / Ch. 4–12 with no bridging sentence — correct but
    reader-confusing; one cross-reference clause each would resolve it.

**Reporter-lens findings**:
- The two newest and most quotable findings never reach the front doors:
  report.html's executive summary has no mention of the salaried-worker
  result (ordinary 17th on AROP, 1st at 59.5% on subjective — arguably
  the single most striking fact in the project) nor of the "could this
  still be reporting culture?" test; the narrative's Landing sequence
  enumerates the scars but skips Ch. 12's "even a job doesn't fix it."
  One sentence in each place would carry the strongest hook to the
  readers most likely to stop there.
- report.html Section 11 has grown to nine h4 subsections; a one-line
  mini-map at the section top would help navigation.
- Otherwise the story is in good shape: chapter titles are strong, the
  honest-nulls style is distinctive, and the spine reads the same way in
  all three registers.

**Suggested fix order**: P1 items 1–5 first (factual/numbering);
then P2 consistency counts (6–12) and scaffolding (13–18); then the
optional soft-spot and reporter items (19–22 and the exec-summary/
landing hooks) as one final polish pass.

---

### Round 4: P0 validity/reproducibility + P1 corrections (2026-08-20)

Executing a combined external review verdict ("strong quantitative core and
coherent central story, but not yet publication-ready"), in the reviewer's own
priority order. P2 editorial rewrite deliberately held for user confirmation.

#### P0.1 — Reproducibility (the highest-priority technical issue)

A clean-room test established what the earlier review could not: numbers match
the *stored* pipeline outputs, but the project could not acquire every required
dataset from scratch. Audited directly rather than assumed: 15 files in
`data/raw/` were read by numbered scripts and produced by none — fetched ad hoc
during development.

**Built**: `scripts/00_fetch_missing_raw.py`, which re-fetches all fifteen from
documented datasets/filters. CHECK mode (default) fetches to a temp dir and
reports agreement against the archive without touching `data/raw/`; `--write`
performs a real re-acquisition. **Result: 14 of 15 reproduce exactly.**
`real_wage_idx2008` agrees on 99.6% of rows (rounding) with wider country
coverage; `panel_gdp_pps` is the one genuine exception (archive stored it
rounded to the nearest 100 PPS, API now returns one decimal, ~3% of rows since
revised) and feeds only the alternative `M3_swap_to_GDP_PPS` specification in
script 11, never a headline model.

Writing the acquisition script surfaced three previously-undocumented filter
choices that the missing step had been hiding, each pinned down by diffing a
fresh fetch against the archive: `statinfo=MED_EI` on both `ilc_li02` and
`ilc_li09` (without it the fetch returns both mean- and median-based rows,
silently doubling the table), and `s_adj=NSA` rather than `SA` on `ei_bsco_m`
(NSA reproduces the archive at 100%, SA at 96.6%).

**Also built**: `scripts/verify_build.py` — 36 checks of published headline
numbers against pipeline outputs (headline gaps, every ladder step, scorecard
residuals *and* ranks, FDR survivor counts, nested-selection results,
work-effort figures, placebo inference), exiting non-zero on mismatch. And a
`Makefile`: `make verify` (fast, offline, the default), `make fetch`,
`make build`, `make all`. All 36 checks currently pass.

**Claim reworded** in the report's Methods, its data appendix, the paper's §10,
and the README, from "every series fetched live" to: *all results reproduce
from the archived source-data snapshot; full automated re-acquisition is
scripted and verified per-file but not yet demonstrated end to end from a clean
checkout.*

#### P0.2 — Gap ladder now one estimand-window

The ladder mixed 2025 raw AROP/AROPE gaps (steps 1–2) with 2015–2024 average
out-of-sample residuals (steps 3–6), then reported differences as "points
explained" — implying a common decomposition across rows that used different
estimands *and* different periods. Fixed at the source in
`38_cumulative_hardship.py`: raw gaps are now computed on the same 2015–2024
window as the residuals (**AROP 52.6, AROPE 41.5**, replacing 47.6/39.7).
Points-closed recomputed against 52.6 throughout, in the stage-1 and stage-2
tables, the work-effort AROP bridge (script 43), and all three documents. The
remaining raw-gap-vs-residual estimand difference is now stated explicitly in
every caption, with the table labeled a *sequence*, not an additive
decomposition. The single-year 2025 figures (47.6/39.7) remain the headline
numbers elsewhere and are unchanged — they are simply no longer mixed into this
table.

#### P0.3 — Nested selection validation (script 44)

Prior checks tested coefficient stability for an *already-selected* variable and
re-ran selection once with Greece excluded. Now the complete 18-candidate
screening is repeated independently inside all 27 leave-one-country-out folds
(486 screening regressions), each fold's country dropped from screening
entirely. `38_cumulative_hardship.py` now exports
`cumulative_hardship_candidate_panel.csv` so script 44 reuses the exact
screening inputs rather than rebuilding them.

**Result**: cumulative excess unemployment selected first in **25 of 27 folds**;
significant in **every** fold (worst-case p=0.0064). The two exceptions both
land on near-neighbour duration/exposure constructions: the Greece-excluded fold
picks the wage-duration measure (the already-documented sensitivity), and the
Finland-excluded fold picks a GDP-duration measure with cumulative excess
unemployment still ranked 3rd. Selection is stable; the family is not.

#### P0.4 — Evidence labels and causal language

Added an explicit four-tier taxonomy to the report's Methods and the paper's
§4.3 — *pre-planned confirmatory* / *exploratory screening* / *post-selection
robustness* / *descriptive corroboration* — stating directly that FDR
correction controls false discoveries within a family but **does not convert
sequentially developed specifications into pre-specified tests**, and that the
later scorecard rows (C-LTU, Model G) therefore rest on out-of-sample, placebo,
and nested-selection validation rather than in-sample p-values.

Causal language softened where it exceeded an aggregate observational panel:
§6.5/§6.6 headings changed from "the sharpest mechanism"/"the mechanism that
closes the residual" to "the sharpest current-conditions marker"/"the addition
that closes the residual"; "precise labor-market mechanisms" → "specific
labor-market measures with a clear interpretation"; "This isolates the puzzle
from unemployment entirely" → "This shows the puzzle persists among people who
are working"; §1's "mechanisms that most fully account for" → "strongest and
most stable explanatory markers … associational markers whose robustness is
established through out-of-sample, placebo, and nested-selection validation,
not causally identified mechanisms."

#### P1 — Factual and structural corrections

One genuine factual error: the narrative's Chapter 12 claimed Greek salaried-only
weekly hours were "still highest" in the EU — the true rank is **7th of 27**
(Romania highest). Rewritten to say the self-employed contribute to the record
without being the whole story. Also: "eighteen-year history" → fifteen (the
series is 2010–2024, n=15); unemployment peak now stated as 27.8% on this
project's own Eurostat series with Pagoulatos's 27.5% explicitly attributed to a
different vintage; two stale "Section 12" cross-references retargeted (Methods
and Section 11 — the two remaining "Section 12" references are correct, since
Section 12 *is* "Answer to Question 2"); the paper's duplicate **Table 4**
resolved by renumbering to document order (elderly → Table 3, salaried → Table
4, programs → Table 5); chapter/stage counts corrected (13→15 chapters,
"twelve"→"thirteen chapters", "seven stages"→nine, "six-stage"→nine, "seven
candidates"→eight — the report's own "traces seven stages" was checked and is
correct as written); §6.9's heading overstatement removed; Zambarloukou
re-alphabetized before the Želinský entries; abstract and §3.5 Contribution
refreshed to name cumulative excess unemployment as the central result and to
signpost §6.9 and §6.11; §4 data list extended with §6.9's six datasets;
README run-order table extended with scripts 00 and 40–44 plus `verify_build`;
`docs/data_sources.md` given full entries for scripts 00 and 40–44;
`docs/todo_plan.md` updated (commit status corrected — `d673e11` was pushed —
plus rounds 3 and 4); vintage dates now disclose the 2026-08-20 work-effort pull
alongside the 2026-08-19 core.

Reporter-lens hooks added as *illustrations of the central argument, not new
pillars*: the salaried-worker fact and the reporting-culture test now appear in
the report's executive summary, and "hardship that even holding a job doesn't
resolve" was added to the narrative's landing sequence.

#### Verification

All three documents re-checked in-browser after every pass: ladder rows render
the corrected common-window values, the correlation table still renders 19 rows,
the paper's captions now read Table 1–5 in order, the narrative shows 15
chapters with every corrected string present, and all three load with zero
console errors. `make verify` passes all 36 checks.

**Not done, held for user confirmation**: the P2 editorial rewrite
(consolidating the corroborating band, moving batteries/screens/notes into
appendices, a Section 11 navigation guide, disambiguating the three nearby wage
figures, mobile presentation, final cross-document audit).

---

### Round 5 (P0.5): closing the reproducibility and inference gaps properly (2026-08-20)

A second external pass confirmed Round 4 closed most of the earlier review but
found five P0 items still open and six stale statements still standing. All
addressed; the findings below include one that changes a headline number.

**1. The build order had a real dependency bug — and it was the same one this
project already hit.** `04_merge_all.py` rebuilds `analysis_dataset.csv` from
scratch; `05` and `21` write derived columns back into it; and
`10_robustness_correlations.py` *reads* AROPE, which only `21` supplies. Plain
numeric order runs `10` before `21`, so the Makefile written in Round 4 would
have silently regenerated the **18-variable** correlation table whose staleness
Round 3 had just fixed. Verified empirically: after `04` alone, `gr_arope` is
absent; after hoisting `05` and `21`, script 10 reports "19 of 19 declared
predictors found". The Makefile now defines an explicit dependency-ordered
sequence with the write-back scripts hoisted, and documents why filename order
is unsafe.

**2. `make all` did not re-acquire anything** — it called `fetch` (CHECK mode,
writes nothing) and then built from the archive. Added `make reproduce`: exports
the committed tree into a temp directory via `git archive`, runs `fetch-write`
there for real, builds, and verifies, leaving the working copy untouched. That
is the target that answers "does this rebuild from nothing?"

**3. "14 of 15 reproduce exactly" was imprecise.** The check used a 0.05
tolerance. Measured properly, it is **13 byte-identical, 2 differing**:
`real_wage_idx2008` (58.1% identical, 99.6% within 0.05, max 0.168 — a derived
HICP-deflated index) and `panel_gdp_pps` (archive rounded to the nearest 100
PPS; ~3% since revised; feeds only an alternative specification). The fetch
script now reports EXACT / within-tolerance / DIFFERS per file with a summary,
and the README states the corrected figures with a per-file table.

**4. Script 44 measured selection stability, not nested prediction — and
extending it changed a headline number.** It now measures both, kept explicitly
distinct: (A) which candidate each fold selects, and (B) that fold's *own*
selected candidate fitted on 26 training countries and used to predict the
held-out 27th. Per-fold p-values are additionally FDR-corrected within each
fold across all 18 candidates (26 of 27 winners survive).

The nested result is materially more conservative than the fixed-specification
figure, and is now reported as the primary one wherever the claim concerns the
whole procedure: **Greece's nested residual is +2.70 points (mean absolute error
4.51), ranking 19th of 27 — eight EU countries are predicted less accurately
than Greece by their own fold's model.** The Greece fold selects the
wage-duration measure rather than cumulative excess unemployment, which is
precisely the already-documented sensitivity, now priced in rather than noted
beside. The &minus;0.8 residual of Model G remains correct for what it is (a
fixed specification whose variable was chosen with Greece in the screening
panel) and both are reported, with the difference between them explained: +2.70
additionally pays the cost of the selection step. The mid-pack ranking is the
stronger form of the claim, since it no longer depends on which member of the
duration/exposure family a fold happens to pick.

**5. Six stale statements removed**: README's "All data is fetched live", its
"7-point spine" heading over a nine-point list, and its salaried-workers/longest-hours
conflation; the same conflation in the academic abstract and the report's
executive summary (salaried employees rank 7th of 27 on hours — it is all
employed and full-time workers who rank 1st); the report's "none of the eight
fully closes the gap" (one does); and the academic Methods' description of
added-variable coefficients as "single planned" and "pre-specified" tests, now
corrected to state plainly that specifications were developed sequentially and
are therefore not pre-registered.

#### Alignment infrastructure: the canonical claim matrix

Built `docs/claim_matrix.csv` (via `scripts/build_claim_matrix.py`): **46
canonical claims across the nine agreed backbone elements**, each with its exact
number, population/window, evidentiary status, statistical caveat, source file,
and required treatment per document (body / note / appendix / omit). Status
distribution: 21 core, 9 limitations, 8 descriptive, 5 post-selection, 2 core
nulls, 1 exploratory screening.

Built `scripts/audit_parity.py` to check each document against it. First run
(after fixing a bug where pandas parsed the `"1.1"`-style ids as floats) found
**two genuine gaps, both in the narrative companion**: the close-to-outcome
caveat on arrears and unexpected-expense capacity, and the point that FDR
correction does not make sequential specifications pre-registered. Both were
real omissions that repeated prose review had not caught — which is the argument
for the matrix. Both added in the narrative's own register; the auditor's
fingerprints were broadened to accept register differences rather than forcing
the narrative into academic vocabulary. **Parity is now 137 of 137.**

`make verify` now runs 41 checks (up from 36), including the nested-CV residual,
Greece's prediction-error rank, and the within-fold FDR count.

### Round 5: cross-document editorial alignment and release audit (2026-08-20)

Completed the P2 editorial restructuring across all three outputs. The shared
argument is now explicit: AROP puzzle, AROPE bridge, shrinking ruler, decomposed
hardship, duration-sensitive labor-market evidence, material and social
corroboration, reporting-culture challenge, and a bounded conclusion. The
technical report retains the full record but adds a Section 11 navigation map
and collapsible methodological detail; the narrative companion keeps the same
evidence in an editorial sequence with method notes hidden on first reading;
the academic paper foregrounds the estimand, nested validation, contribution,
and limitations.

Corrected three cross-document hierarchy risks during the pass: the fixed
post-selection Model G residual (&minus;0.8) is no longer presented as the primary
validation result, which is the fully nested +2.70 residual and rank 19 of 27;
Greece is described as having the EU's deepest and longest unresolved GDP
shortfall rather than being the only country below a prior peak; and the real
wage comparison now acknowledges Hungary and Italy's remaining shortfalls.

Added `canonical_wording` and `importance` fields to the claim matrix and
expanded `audit_parity.py` with forbidden stale-claim checks. Added
`docs/current_state.md` as the short, current handoff document. Final release
requires the numerical, parity, browser, mobile-overflow, and console checks
listed there; their results are recorded in the commit closing this round.

### Round 6: clean-room replication and academic appendix (2026-08-20)

Executed the isolated `make reproduce` path with the pinned project
environment. Acquisition and all 44 analysis scripts completed. The final
publication-vintage comparison passed 40 of 41 checks and stopped on one live
Eurostat revision: the refreshed real-wage series changes the detrended
correlation from r=&minus;0.425 (FDR p=0.0516, archived vintage) to r=&minus;0.474
(FDR p=0.0236, live vintage), increasing detrended FDR survivors from 17 to
18. No other headline check changed. Documentation now distinguishes exact
archived-vintage reproducibility from replication against a revisable live
source. The Makefile automatically prefers `.venv` and propagates that
interpreter into its isolated copy.

Moved the academic paper's full cumulative-hardship screening and validation
record from the main results flow to Appendix A. Section 6.6 retains the
estimand, the common-window ladder, the fixed result, the primary nested result,
the decade-duration interpretation, and the ecological limitation. Appendix A
retains the replacement test, 18-candidate FDR battery, Greece-exclusion and
27-fold nested selection details, rolling/decay battery, and individual-level
literature bridge. Browser validation confirms one Table 2, a working appendix
TOC link, no console errors, and no horizontal overflow at 390px.
