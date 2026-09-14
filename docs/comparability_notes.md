# Time-series comparability notes

## Subjective poverty ("ability to make ends meet")

- **Definition used in this project**: share of households reporting they make ends
  meet "with difficulty" or "with great difficulty" (Eurostat dataset `ilc_mdes09`,
  categories `DIF` + `GRT`). This matches Eurostat's own "subjective poverty rate"
  headline definition and reproduces the officially reported 2024 EU figure closely
  (this project: EU 17.4% in 2024; Eurostat press release: 17.4%), and the Greece
  figure (this project: 66.7% in 2024 vs. widely reported 66.8%) — the small gap is
  rounding/vintage, not a definitional mismatch.
- **Category definitions have been stable** across the full 2003-2025 window: the
  6-point scale (great difficulty / difficulty / some difficulty / fairly easily /
  easily / very easily) is unchanged in EU-SILC since the survey's inception, so no
  reconstruction was needed — GRT and DIF are the same two categories throughout.
- Earliest Greek EU-SILC data: **2003**. This project's series starts there.
- Caution: in **2003-2004, only 6 countries** had EU-SILC micro-data (early rollout),
  rising to 13 in 2004, 25 by 2005. Greece's EU rank in those two years is computed
  against a tiny country set and is **not comparable** to later, EU27/28-wide
  rankings. Treat 2003-2004 rank as indicative only; the level (48.0%, 45.4%) is
  robust since it doesn't depend on other countries.

## At-risk-of-poverty rate (AROP)

- Dataset `ilc_li02`, threshold = 60% of national median equivalised disposable
  income (`rskpovth=B_60`, `statinfo=MED_EI`). This is the EU-SILC/Europe 2020
  standard definition, unchanged over the period.
- **Income reference period**: for Greece (and most EU-SILC countries using
  calendar-year income), the AROP rate published for survey year *t* is based on
  household income received in calendar year *t-1*. E.g. the "2013" AROP rate
  reflects 2012 income. The subjective "make ends meet" question, by contrast, asks
  about the household's *current* situation at the time of interview (survey year
  *t*). **This project does not shift the AROP series** to align reference years,
  following Eurostat's own convention of labelling both by survey year — but this
  ~1-year lag is exactly why the correlation analysis (Task 8) also reports
  **1-year-lagged** relationships, not just contemporaneous ones.

## EU aggregates

- No single Eurostat geo code covers the full 2003-2025 span with constant
  composition for either indicator. This project uses a **priority fallback**
  (`EU27_2020` → `EU27_2007` → `EU28` → `EU` [changing composition] → euro-area
  codes as last resort), recording which code was used for every year in
  `eu_*_source` / `eu_*_src` columns of the processed tables. Practical effect:
  - AROP: no EU aggregate available for **2003-2004**; 2005-2012 uses the
    variable-composition `EU` code; 2013 onward uses fixed-composition `EU27_2020`.
  - Subjective poverty: no EU aggregate for **2003-2006**; 2007-2009 uses
    `EU27_2007`; 2010 onward uses `EU27_2020`.
  - Because the aggregate's country composition changes across this fallback chain,
    the Greece-EU gap series has a **methodological discontinuity** at those
    transition points, not just an economic one. Read level shifts around
    2005/2007/2013 with that in mind.

## EU membership used for country rankings

Rankings (Task 3/7) restrict the country set to **EU member states only** (not
EFTA/candidate countries reporting to Eurostat, e.g. Norway, Switzerland, Iceland,
Turkey, Serbia, Albania, North Macedonia, Montenegro, Kosovo — all present in the
raw data but excluded from ranking). Membership is applied *as of each survey year*
(`scripts/eu_membership.py`): EU15 pre-2004, EU25 2004-2006, EU27 2007-2012, EU28
2013-2019, EU27 (post-Brexit) 2020 onward. The number of countries actually ranked
each year (`n_countries_*` columns) also depends on data availability, which is
lowest in 2003-2006 (see above).

## Deprivation indicators — a genuine methodology break

- **Legacy severe material deprivation** (`ilc_mddd11`, 9-item list, e.g. cannot
  afford: unexpected expense, one-week holiday, meat/protein every second day,
  arrears, warm home, washing machine, TV, phone, car) is available **2003-2020**
  and was Eurostat's headline indicator through the Europe 2020 strategy period.
- **New severe material and social deprivation rate** (`ilc_mdsd11`, 13-item list
  adding social-participation items) replaces it from **2021 onward** (usable data
  from ~2015, official headline from 2021) as part of the EU 2030 social
  scoreboard. The two series **are not directly comparable** — this project keeps
  them as separate columns (`gr_severe_mat_deprivation_legacy` vs.
  `gr_severe_mat_soc_deprivation_new`) rather than splicing them into one line.
  Both are provided for the overlap years (2015-2020) so the reader can see the
  level difference the redefinition introduces.

## At-risk-of-poverty-or-social-exclusion rate (AROPE) — a genuine methodology break

- Like the deprivation indicators above, AROPE (`ilc_peps01` legacy /
  `ilc_peps01n` revised) has a **methodology break at the 2020/2021
  boundary**, since it partly incorporates the revised material- and
  social-deprivation definitions described above. This project splices the
  legacy series (through 2020) with the revised series (from 2021) at that
  boundary — `21_arope.py` — rather than blending the two vintages into one
  continuous line.
- **AROP is treated as this project's primary poverty measure; AROPE is a
  secondary, motivating benchmark**, not a replacement (the "Core Reframe,"
  agreed 2026-08-20 — see `docs/archive/pre-v2-publication/publication_strategy.md`). This distinction
  matters for reading any AROPE-based figure: AROPE narrows the AROP-based
  subjective-poverty gap (47.6 points) to 39.7 points, but any chart or
  number that mixes pre-2021 and post-2021 AROPE values without noting the
  splice should be read with that break in mind. AROPE's three components
  (income poverty, severe material deprivation, very-low work intensity)
  are a union, not a weighted average, and **their household-level overlap
  is not observable from the aggregate country-year tables this project
  uses** — EU-SILC microdata could support that kind of overlap analysis
  under controlled research access, but that lies outside this project's
  aggregate-only Eurostat API pipeline. This project does not claim to
  reconstruct AROPE from any of its own regression variables as a result;
  see the published reports' own Methods sections for the full framing.

## Labour market series

- `une_rt_a` (unemployment rate, age 15-74) only has disseminated values for
  Greece from **2009 onward** in this vintage of the dataset, despite the dataset's
  stated overall start of 2003 — pre-2009 Greek annual observations at this exact
  age breakdown are not published. Real GDP per capita and HICP inflation, by
  contrast, are available for Greece back to 2000. This asymmetry limits the
  correlation/crisis-sensitivity analysis involving unemployment to 2009-2025 —
  which still covers the full crisis and recovery period, the analytically
  important part, but means the very start of the "pre-crisis" window (2003-2008)
  has no unemployment observation to correlate against.
- **Cumulative-hardship baseline years differ by variable, for this same
  reason.** The cumulative-hardship checkpoint (`38_cumulative_hardship.py`,
  see `docs/data_sources.md`) baselines GDP, real wages, and the AROP
  threshold to **2008**, but headline and long-term unemployment to
  **2009** — confirmed via a direct 27-country coverage check inside the
  script, not assumed, matching the `une_rt_a` gap documented above. Its
  central variable, cumulative excess unemployment, was originally framed
  as a literal permanent, non-decreasing accumulation since that baseline
  year; a rolling-window robustness check (added 2026-08-20 in response to
  external review) found a 10-year trailing window fits at least as well,
  so this project now describes the mechanism as **sustained exposure over
  roughly a decade**, not literal permanent accumulation since one fixed
  year. Full accounting in `docs/archive/pre-v2-publication/publication_strategy.md`.

## Unemployment rate — 2021 EU-wide methodology harmonization (Regulation 2019/1700)

- **What changed, and why.** EU Regulation 2019/1700 (the Integrated European
  Social Statistics framework regulation) mandated a harmonized Labour Force
  Survey methodology across all EU member states from reference year 2021
  onward (revised definitions of employment status and active job search,
  among other changes). This is an EU-wide regulatory requirement, not a
  Greece-specific or politically directed change — every member state's LFS
  series was affected, and ELSTAT implemented it because it was legally
  required to, on the same timeline as every other national statistical
  institute in the EU.
- **Retroactive revision, not a splice.** Rather than leave a methodological
  break at the 2020/2021 boundary, ELSTAT and Eurostat retroactively revised
  the Greek LFS series back through 2009 under the new, harmonized
  definitions, so the published `une_rt_a` series (the one this project
  uses — see "Labour market series" above) is a single continuous,
  harmonized vintage from 2009 onward, not a legacy series spliced onto a
  revised one at 2021. Sources: ELSTAT's own methodological note
  ([statistics.gr](https://www.statistics.gr/documents/20181/f32fb3c5-abf9-6380-5ef0-c3fffeb02e3e))
  and Eurostat's correction-methodology documentation
  ([Statistics Explained cache PDF](https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/94764.pdf)).
- **Direction of the revision.** The harmonized series reports HIGHER
  historical Greek unemployment than the pre-2021 vintage did, not lower —
  confirmed directly against this project's own `data/raw/panel_unemployment_history.csv`
  (`geo=EL`): 2013 = 27.8% (harmonized) vs. 27.5% (pre-revision); 2020 =
  17.6% (harmonized) vs. 16.3% (pre-revision). Both project values match the
  harmonized figures exactly, confirming the pipeline pulls the current,
  corrected `une_rt_a` vintage throughout, not a mix of vintages.
- **Effect on this project's cumulative-unemployment construct.** Card 5 of
  the carousel and `38_cumulative_hardship.py`'s `cum_excess_unemployment`
  sum, for each country, every year's excess unemployment over that
  country's own 2009 level (`UNEMP_BASE_YEAR = 2009`). Because the
  harmonized series runs continuously from 2009 with no vintage change
  partway through, this accumulation carries **no internal discontinuity**
  from the 2021 correction — the 2009 baseline and every subsequent year it
  is compared against are drawn from the same harmonized vintage. See
  `docs/v2_research_record.md`, entry X-06, for the full check that
  established this.

## Pre-EU-SILC data

- The European Community Household Panel (ECHP, pre-2003) was **not** merged into
  any series in this project. ECHP used a different sampling design and a
  differently-worded material-wellbeing question, so its "poverty" figures are not
  methodologically comparable to EU-SILC. 2003 (Greece's first EU-SILC year) is
  therefore the hard start of every series here.

## Revisions

- All data pulled fresh from the Eurostat API dissemination endpoint on the day of
  this analysis; Eurostat revises back data periodically (visible in the API
  response's `updated` timestamp per dataset). No attempt was made to reconstruct
  point-in-time (as first published) values — this is a *current-vintage*
  time series, standard practice for this kind of retrospective analysis.
