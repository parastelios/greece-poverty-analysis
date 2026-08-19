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
