# Shared spine

Every document is written FROM this map. None of them is the source.

Detail levels: `full` / `summary` / `brief` / `-` (absent).

## Movement 1 — The puzzle

**Purpose.** Establish the divergence between reported hardship and official income poverty, then immediately introduce AROPE as the official system's own bridge.

**Claims.** 1.1 1.2 1.3 1.4 3.1 3.2 3.3 10.6

**Canonical number.** 67.2% vs EU 17.6%; AROP 19.6%, 4th of 27; AROPE gap 39.7pt

**Canonical wording.** Greek reported hardship is the EU's highest while AROP is elevated but ordinary; AROPE narrows the gap and does not close it.

**Tier.** confirmatory / descriptive

**Mandatory caveat.** AROPE is a bridge, not a competing headline. The outcome is Eurostat's official indicator (ilc_sbjp01 from 2010, validated backward extension before).

**Required visual.** AROP vs subjective scatter; AROPE panel

| report | paper | narrative | appendix |
|---|---|---|---|
| full | full | full | full |

---

## Movement 2 — The ruler moved

**Purpose.** Explain why the annual relative rate understates a national collapse, and give the anchored reconstruction.

**Claims.** 2.1 2.2 2.3 2.4 2.5

**Canonical number.** threshold 100 -> 65 (2008=100); anchored ~20% -> ~41%

**Canonical wording.** The poverty line fell with the median, so AROP stayed calm while the living standard it represents deteriorated.

**Tier.** confirmatory

**Mandatory caveat.** The anchored series is an approximation validated at MAE 1.22pt against the official 2019-anchored product; microdata finds a LARGER effect, not a smaller one.

**Required visual.** real threshold vs real income, 2008=100

| report | paper | narrative | appendix |
|---|---|---|---|
| full | full | full | full |

---

## Movement 3 — How broad the deterioration was

**Purpose.** Show that the collapse was wide, not confined to one indicator, in real units the reader can hold.

**Claims.** 1.9 7.1 7.2 7.3 7.4 7.5 7.6 7.7 7.8

**Canonical number.** 21% pre-crisis -> 58% from 2012, 68% in 2024, 1st of 27

**Canonical wording.** Greece moved from the EU's worst fifth on a fifth of measured indicators to roughly two-thirds, and has not moved back.

**Tier.** descriptive corroboration

**Mandatory caveat.** DESCRIPTIVE ONLY. Tested as a predictor and null (FDR 0.287). Never written as a driver; audit_parity's FORBIDDEN rules fail the build on causal phrasing.

**Required visual.** breadth series; 25-indicator position ladder

| report | paper | narrative | appendix |
|---|---|---|---|
| full | summary | full | full |

---

## Movement 4 — The objective-only model

**Purpose.** The central quantitative result, in a specification containing nothing that restates the outcome.

**Claims.** 10.1 10.2 4.1 4.3 5.1 5.3 6.2 6.3 6.6

**Canonical number.** +27.05 -> +6.93pt; rank 1 -> 3 of 27

**Canonical wording.** Adding accumulated unemployment exposure to the objective-only specification reduces Greece's leave-out residual from approximately 27 to 7 points. Greece nevertheless remains the third most under-predicted country.

**Tier.** post-selection robustness (not independent confirmation)

**Mandatory caveat.** A MODEL COMPARISON, not a causal decomposition. Arrears, unexpected-expense capacity and financial expectations are excluded by construction. The legacy residuals 11.6, 3.9, -0.8 and +2.70 are superseded and must not be quoted as headlines.

**Required visual.** objective-only model ladder

| report | paper | narrative | appendix |
|---|---|---|---|
| full | full | summary | full |

---

## Movement 5 — What the result is not

**Purpose.** The between-country qualification, the unresolved remainder, and both failed designs.

**Claims.** 10.3 10.4 10.5 6.5 6.7 6.8 8.1 4.4

**Canonical number.** between +0.332 p<0.0001; within -0.076 p=0.692

**Canonical wording.** The association is supported predominantly between countries. The panel does not establish a within-country dynamic effect, and its within estimate is too imprecise to rule one out.

**Tier.** post-selection robustness / core nulls

**Mandatory caveat.** Never write 'as exposure accumulated, hardship increased'. Use 'between-country scarring marker', not 'mechanism'. Synthetic control failed and no effect from it is interpreted. Family D is descriptive only.

**Required visual.** Mundlak within/between; failed-design summary

| report | paper | narrative | appendix |
|---|---|---|---|
| full | full | brief | full |

---

## Movement 6 — Discussion

**Purpose.** Material grounding without claiming full resolution or causality, and the reporting-culture question at its actual strength.

**Claims.** 8.2 8.3 8.4 8.5 8.6 8.7 9.1 9.2 9.3 9.4

**Canonical number.** widening +19.8pt vs median -8.8pt; placebo 1st of 27, p=0.037

**Canonical wording.** A time-invariant reporting premium cannot explain a crisis-timed widening, but a crisis-induced change in response behaviour is not excluded.

**Tier.** confirmatory / limitation

**Mandatory caveat.** p=0.037 is a permutation statistic under exchangeability, not randomization inference. Domain specificity rules out a GENERIC response-style account, not a fiscally specific one. All results associational and aggregate.

**Required visual.** event study; placebo distribution

| report | paper | narrative | appendix |
|---|---|---|---|
| full | full | summary | summary |

---

## Movement 7 — Legacy specifications (appendix only)

**Purpose.** The superseded residuals, kept visible so the record is complete and so a reader meeting them in V1 can see why they were retired.

**Claims.** 4.2 5.2 6.1 6.4

**Canonical number.** 11.6 / 3.9 / -0.8 / +2.70

**Canonical wording.** Earlier specifications that included predictors proximate to the outcome, or that reported a nested-selection figure. Superseded by claim 10.2 and retained only as legacy, proximity-sensitive results.

**Tier.** legacy / superseded

**Mandatory caveat.** Exact figures are appendix-only and MUST NOT be quoted as headline estimates. But the report and paper MUST state QUALITATIVELY that proximity-sensitive specifications produced smaller residuals and why they were superseded -- silently omitting them would look selective. Narrative may omit entirely.

**Required visual.** legacy ladder table (appendix); qualitative note (report, paper)

| report | paper | narrative | appendix |
|---|---|---|---|
| brief | brief | - | full |

---

