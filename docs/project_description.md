# Project description

**Status:** current, describing the completed project as published. Distinct
from [`docs/archive/pre-v2-publication/project_description_v3.md`](archive/pre-v2-publication/project_description_v3.md),
the pre-registered protocol this project's tests were fixed against *before*
the results existed — that document is a plan, kept for provenance and still
cited by several pipeline scripts as the source of each construct's testing
conditions. This document describes what the plan produced.

## The Greek Poverty Paradox

On the European Union's official measure of relative income poverty, Greece
ranks seventh of twenty-seven — elevated, not exceptional. On the EU's
measure of subjective financial hardship — households reporting difficulty
making ends meet — Greece ranks first, and has for a decade. The distance
between the two runs to 52.6 percentage points on average over 2015–2024:
roughly one Greek household in five counted as at risk of poverty, roughly
two in three saying they are struggling.

This project exists to find out what that gap is made of. It is organized
around two linked questions, tested against a protocol fixed before any
result was seen ([`project_description_v3.md`](archive/pre-v2-publication/project_description_v3.md)),
with every verdict the output of that fixed procedure rather than a judgement
made after the numbers arrived.

## Main question 1 — Why do the two official measures diverge so dramatically?

**Concise answer.** Partly because the official measures are narrower than
the experience they are used to summarise, and partly because the reported
hardship is not a reporting artefact — it corresponds to concrete material
difficulty, even if that correspondence cannot be independently confirmed
from outside the survey that asks about it. Together these account for a
minority of the 52.6-point gap.

**Is the hardship outcome valid and comparable with Eurostat's official
indicator?** The outcome from 2010 onward is Eurostat's own published
`ilc_sbjp01`, used unmodified. Before 2010 — where Eurostat does not publish
it — the series is this project's own construction from `ilc_mdes09`
components, validated against the official series on 432 overlapping
country-years (318 exact, 114 off by one rounding step, rank correlation
1.00 in every year). The construction is used only for the descriptive
picture; every inferential test runs on the official series alone.

**How exceptional is Greece relative to the other member states?** Not
continuous with the rest of the distribution. Fitting the European
relationship between income poverty and reported hardship through the other
twenty-six countries, Greece sits 47 points above what that relationship
predicts at its own income-poverty rate — a gap larger than the range
spanning the middle of the distribution.

**How much of the divergence does AROPE close, and what does it add beyond
income poverty?** AROPE — income poverty *or* severe material deprivation
*or* very low work intensity — closes about a fifth of the distance (9.8 of
52.6 points), and that contribution is shrinking, from 11.0 points in 2015 to
7.3 in 2024. It is a real part of the answer and a weakening one.

**How did the relative poverty threshold move during the crisis, and what
does an anchored threshold reveal that annual AROP does not?** AROP is 60%
of the *current* national median, so when Greek median income fell by
roughly a third, the threshold fell with it. Holding the threshold fixed at
its 2008 real value instead, measured poverty roughly doubles, from under
20% before the crisis to a peak above 40% in 2014. In cash terms the
threshold has recovered almost entirely (−2.2% by 2025); in purchasing power
it has not (−21.3%). This series is Greece-only and descriptive — it enters
no inferential test.

**Did disadvantage spread across many indicators or stay concentrated in a
few?** It spread. On a fixed basket of sixteen indicators with a valid EU
position in both 2008 and 2024, Greece moved from the worst fifth of the
Union on four of them to eleven. This is a description, not an explanation:
tested as a predictor it is not significant on its own (p = 0.12), and its
coefficient reverses sign once accumulated-history measures are in the same
model.

**Does reported hardship move with concrete affordability failures?** Yes,
within countries as well as across them: arrears, inability to meet an
unexpected expense, inadequate heating and severe deprivation correlate with
reported hardship at 0.63–0.80 within-country, pooled across all 27 states.
Those same four items statistically absorb 71% of Greece's baseline
residual.

**What can same-instrument corroboration establish, and what can it not?**
It establishes that the reported hardship is coherent with concrete
circumstances reported by the same households. It cannot establish that it
is validated from outside the instrument — every item comes from the same
EU-SILC interview as the outcome itself, so a household inclined to answer
the whole battery downbeat would produce correlations of this size without
any item independently confirming another. Falling behind on bills, the item
that looks most like a hard factual anchor, tracks the outcome only weakly
within Greece (0.371) — arrears require having had credit to fall behind on.

**Can generic Greek pessimism or reporting style account for the pattern?
What remains possible after the reporting-style checks?** Not adequately,
though it cannot be excluded either. Greece is worst in Europe on the two
financial questions (hardship, financial expectations) and second-worst on
general life satisfaction — a difference of degree, not of kind, which
argues against pure reporting style but does not rule out a general negative
tendency operating alongside genuine difficulty. A separate survey (the
European Social Survey, kept deliberately apart from the Eurostat series and
entering no test) shows Greece already about 0.8 points below its comparison
group's median before the crisis — a longstanding low-wellbeing pattern
remains plausible and cannot be dismissed by anything tested here.

## Main question 2 — How much do current conditions and accumulated exposure account for?

**Concise answer.** Three present-day constructs and three accumulated ones
each carry information about reported hardship beyond income poverty, on a
cross-country, non-causal, model-dependent basis. Most of the six
present-day constructs that did not clear every gate are unresolved for want
of statistical power, not excluded. The evidence is between-country
throughout; there is no supporting within-Greece dynamic evidence. One
central diagnostic — how much of Greece's residual gets absorbed — reverses
completely depending on a single defensible modelling choice.

**Which present-day conditions remain associated with hardship after AROP
and year effects?** Three of nine pre-registered constructs cleared every
gate (incremental explanatory power, multiplicity correction within its
declared family, and a wild cluster bootstrap far more demanding than a
conventional standard error at 27 clusters): material resources, long-term
unemployment (labour-market exclusion), and wage-adjusted affordability.

**What did each contribute?** Higher material resources predict less
reported hardship (bootstrap p = 0.0055); more long-term unemployment
predicts more (p = 0.0085); worse wage-adjusted affordability predicts more
(p = 0.0005). Each direction was declared before testing. Long-term
unemployment is the most stable of the three under leave-one-country-out
refitting, including with Greece itself dropped.

**Which current candidates were inconclusive, unsupported, blocked or
infeasible?** Six did not clear every gate. Real wages, real household
income, the real poverty threshold and compounded inflation are
**inconclusive under available power** — the design could not have detected
an effect of the size that would matter. Annual food, housing and headline
inflation are **unsupported with adequate power**, at the stated magnitude
only. Proximate material hardship (the same-instrument deprivation items) is
**blocked** — not testable without circularity, since it shares its
instrument with the outcome. Two constructs (share below own GDP peak,
housing-cost overburden) cleared multiplicity correction and then collapsed
under the bootstrap (p = 0.40 and 0.55) — exactly the failure mode the
bootstrap gate exists to catch.

**Does accumulated unemployment, wage non-recovery or housing deterioration
add information beyond the current-level counterpart?** Yes, for all three,
conditional on the matching present-day construct already being in the
model: accumulated excess unemployment (conditional bootstrap p = 0.0025),
duration of wages below 2008 (p = 0.0060, one specific construction only),
and housing-cost deterioration since 2010 (p = 0.0015, borderline — 91 of
1,999 bootstrap replications exceeded the observed statistic). A fourth
result, accumulated wage shortfall, cleared every conditional test but is
capped by a pre-registered rule: an accumulated measure may only qualify or
withdraw support its present-day counterpart already established, never
create support on its own, so it is reported and not counted.

**Do accumulated measures outperform or merely complement current
snapshots?** Neither uniformly — for wage-adjusted affordability the pattern
reverses, with the current measure supported and the accumulated one
inconclusive, which argues against accumulation being a general property of
this outcome and for it being specific to labour, wages and housing.

**Is there supporting within-country or within-Greece dynamic evidence?**
No. Across three related checks on the same panel (a Mundlak
between/within decomposition, and first-difference tests), no within-country
estimate is significant in the adverse direction and no first-difference
test supports one. This is the report's most easily overstated result: the
within tests are too imprecise to establish or rule out a dynamic effect, so
"the design does not support dynamic wording" is a different and weaker
statement than "no dynamic effect exists." Three drafts of the report
crossed that line before the wording was fixed.

**What does the between-country nature of the evidence mean?** Every
supported result in this project is a cross-country association across
twenty-seven countries and roughly a decade. Nothing here identifies a
causal effect, and nothing here describes an individual household — the
ecological-inference gap is real and unresolved by this design.

**How sensitive is Greece's unexplained residual to including same-instrument
deprivation?** Completely. With it in the model, Greece's residual is +6.93,
the third-largest unexplained positive gap in Europe. Remove it, on
identical rows, and the residual is −9.39, the twenty-fifth largest — a
reversal from a stark positive outlier to a stark negative one. Neither
specification is definitive; they may not be averaged or chosen between by
which residual looks more plausible.

**Which planned designs failed, and why must they remain visible?** A
synthetic-control comparison, meant to be the project's centrepiece, failed:
its donor weights collapsed onto a blend of Hungary (0.55) and Bulgaria
(0.45), missing four of six pre-registered conditions, and its divergence
chart appears nowhere in any published document because a compelling picture
built on a counterfactual that thin would persuade readers of something the
evidence cannot support. A multi-domain breadth predictor also failed: added
to the reference model it worsened Greece's residual and reversed sign
conditionally, a reversal left deliberately uninterpreted. Both are recorded
rather than dropped, because a report that shows only its successes
misrepresents how much was tried.

**Which contextual hypotheses were considered but not established?**
Institutional trust, the design of the 2010 adjustment programmes, migration
(tested directly as a predictor, p = 0.4006 — inconclusive, not ruled out),
and the regressivity of Greece's indirect-tax system. Each is recorded in a
separately labelled register with its own vocabulary — "contextual
evidence," "literature-grounded context," and so on — deliberately disjoint
from the evidence tiers above, so a contextual statement can never be
mistaken for a finding.

**How much of the original hardship gap remains unexplained?** Most of it.
Of the 52.6 points, what this project accounts for is a minority. The
remainder is not attributed to anything here, because the analysis could not
establish where it goes.

## Evidence hierarchy

Every tested result carries one of five labels, assigned by a fixed
decision procedure rather than a reading of p-values: **supported**
(cleared every pre-registered gate including the bootstrap); **inconclusive
under available power** (did not clear the gates, and the design could not
have detected an effect of the relevant size — not evidence of absence);
**unsupported with adequate power** (did not clear the gates, and could
have detected an effect of the stated magnitude — the exclusion is specific
to that magnitude); **blocked** (not testable without circularity); and
**infeasible** (the data required does not exist — distinct from a null
result). A separate, deliberately disjoint vocabulary — "contextual
evidence," "descriptive corroboration," "literature-grounded context,"
"future hypothesis," "author interpretation" — covers material discussed
without being established, so it can never be promoted into a finding.

## Central limitations

Every result is a country-year aggregate association; none identifies a
causal effect and none describes an individual household. The number of
clusters (27) is small enough that the wild cluster bootstrap, not a
conventional standard error, decides support. The panel is short enough
(roughly a decade of outcome variation) that within-country dynamic
questions cannot be resolved either way. The most consequential single
modelling decision in the project — whether to admit a same-instrument
deprivation predictor — is not resolvable by the data and moves Greece's
rank from 3rd to 25th of 27.

## What this project does not establish

No causal mechanism, anywhere. No claim that Greece changed over time within
this design — only that countries with more accumulated exposure report
more hardship. No ruling-out of a general negative reporting tendency
alongside genuine hardship. No attribution of any share of the 52.6-point
gap to a specific cause. No household-level mechanism — every finding is
ecological.

## What remains unexplained

A majority of the 52.6-point average gap between reported hardship and
income poverty. The project states this as prominently as its findings,
because the honest version of this project's answer includes a large
residue it could not resolve.

## The documents, and their roles

| Document | Role |
|---|---|
| [`output/v2_report.html`](../output/v2_report.html) | The complete technical source: the eight-stage argument, every frozen claim with its evidence tier and caveats, and the main-path figures. |
| [`output/academic_paper.html`](../output/academic_paper.html) | The same evidence in academic register — hypotheses, estimands, identification limits, a restrained set of central tables and figures. |
| [`output/narrative.html`](../output/narrative.html) | A magazine-style narrative companion telling the same evidence as one continuous story for a general reader. |
| [`output/statistical_appendix.html`](../output/statistical_appendix.html) | Every variable used anywhere in the project, interactive, against all 27 member states, organized around the report's own eight-stage argument — the full audit trail behind every number in the other three documents. |
| [`docs/v2_research_record.md`](v2_research_record.md) | The live research log: every stage, every correction made during review and why. The current source of truth for project *status* — this document describes the completed argument, not the process that produced it. |

## References

- [`data/processed/e_final_claims.csv`](../data/processed/e_final_claims.csv) — the frozen claim set, one row per finding, with its evidence tier, caveats and the documents it is required to appear in.
- [`data/processed/context_register.csv`](../data/processed/context_register.csv) — the register of contextual material discussed but not established.
- [`docs/archive/pre-v2-publication/project_description_v3.md`](archive/pre-v2-publication/project_description_v3.md) — the pre-registered protocol this project's tests were fixed against.
- [`docs/v2_research_record.md`](v2_research_record.md) — every stage of execution, in order, with corrections logged.
