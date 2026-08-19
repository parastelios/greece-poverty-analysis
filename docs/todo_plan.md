# Plan: post-scorecard release readiness and next extensions

Agreed plan as of 2026-08-20, after the targeted release-readiness review
found six small, mechanical issues (no large findings were wrong) and before
any further analytical expansion. Checked items are done; update this file
in the same commit as the work it describes, so the checkboxes and the git
history stay in sync. Full reasoning for each completed item lives in
`publication_strategy.md`.

## Step 0 — Version control

- [x] Initialize git in the project directory
- [x] Add `.gitignore` (`.DS_Store`, `__pycache__/`, `.venv/`; data and the
      report itself stay tracked)
- [x] Baseline commit of the current reviewed state (`e3f6e7d`)
- [x] Tag the baseline (`baseline-before-p0-p1`)
- [x] Connect to remote (`git@github.com:parastelios/greece-poverty-analysis`)
      and push `main` + tags

## P0 — Fix current known issues

Small, mechanical fixes surfaced by the release-readiness review. No new
analysis, no claims change — clears the deck before P1.

- [x] Fix wrong AROPE cross-reference ("Section 6" → "Section 3") in the
      near-zero-gap subsection
- [x] Add the missing `q-label` badge to the scorecard section (every other
      numbered section has one; the scorecard doesn't, despite the TOC
      numbering it "10")
- [x] Reconcile the diaNEOsis sample size (report says n=1,348 from the PDF;
      the institution's own portal page says n=1,300 for the apparently same
      survey) — re-checked both: kept 1,348 (what the report's math actually
      used), citation now states the discrepancy explicitly
- [x] Add an evidentiary badge to the swing-sensitivity finding (its
      follow-up gap-relation test is labeled "Exploratory lead"; the primary
      finding itself carries no badge, unlike the near-zero-gap comparison)
- [x] Soften "scarring/pessimism story" — the phrase pairs a hard-data
      finding (scarring) and a caveated subjective one (pessimism) as if
      they're one category
- [x] Add bridge sentences: the scorecard names Models E/F before Section 11
      defines them; Section 11's four subsections have no connective "so
      far" bridges between them

**Commit**: `p0-report-cleanup` — done

## P1 — Highest-value structural extensions (checkpointed, one at a time)

Each item gets its own checkpoint: build it, report findings, decide
placement/inclusion, *then* move to the next. Weak/null/non-comparable
results are a valid outcome to report honestly, not a reason to force
inclusion.

### P1a — Recovery trajectory
- [x] Years below peak, years to recovery, per EU country
- [x] List of countries not yet recovered
- [x] Indexed EU recovery-path chart (Greece vs. faint EU field, each
      country indexed to its own peak)
- [x] Checkpoint: report findings, recommend placement, decide
      integrate/hold back — **decision: strengthens the report, integrate,
      but deferred to the batched P3 integration step rather than done now**

**Commit**: `p1a-recovery-trajectory-analysis` — analysis done, report
integration deferred to P3

### P1b — Migration / brain drain (scoped narrow)
- [x] Net migration, crisis/recovery years
- [x] Age profile, if comparable — not comparable for Greek nationals
      specifically; explicitly not used, attributed instead to OECD/census
      source where cited
- [x] Return migration, if comparable — yes, and this is where the most
      newsworthy finding turned up (net inflow in 2023 and 2024)
- [x] Explicitly note anything not clean/comparable rather than forcing it
      (age profile as above; `demo_gind`'s headline "net migration rate"
      rejected outright as statistically-noise-dominated for Greece)
- [x] Checkpoint: report findings, recommend placement, decide
      integrate/hold back — **decision: integrate, with careful framing**

**Commit**: `p1a-recovery-trajectory-analysis` (P1a analysis) — done

**Commit**: `p1b-migration-feasibility`

### P1c — Trust in state/EU
- [x] Feasibility check: comparable source, years, country coverage, method
      consistency — before any modeling. **Failed**: Eurostat's entire
      institutional-trust holdings are one dataset (`ilc_pw03b`), one year
      (2013) only.
- [x] Only proceed to modeling if it clears that bar — it didn't; not
      modeled
- [x] Checkpoint: report findings, recommend placement, decide
      integrate/hold back — **decision: don't model, do add as
      literature-backed context** (user's own independent research found
      Ervasti et al. 2019 and an OECD 2026 trust profile that together
      support the "structural, not cultural mood" argument)

**Commit**: `p1c-trust-feasibility` (feasibility check) — done; trust
literature integrated directly into the report in the same session
(Section 11, literature section, Methods) rather than deferred to P3

## P2 — Labor-market and distribution extensions (lower priority)

- [x] Real wages — fetched (`30_real_wages.py`), integrated as a major
      Section 11 evidence point + correlation/robustness table row + chart;
      multicollinearity/model-feasibility check done, decided **not** to
      add to the scorecard (no independent explanatory power beyond
      existing predictors). Also fixed two `04_merge_all.py` pipeline bugs
      and a p-value export rounding bug found during verification. See
      `docs/publication_strategy.md`, "P2a: real wages" for the full log.
      Republished.
- [x] Long-term unemployment — fetched (`31_long_term_unemployment.py`),
      became a scorecard-changing finding, not just descriptive evidence.
      Model C-LTU (long-term unemployment replaces headline unemployment)
      cuts Greece's out-of-sample gap from 11.6 to 3.9 points and moves
      Greece from 1st to 6th of 27 — added to the scorecard as the
      preferred labor-market specification, with the additive version kept
      as a robustness check only. Integrated as a new Section 11
      subsection, a reshuffled-outlier table, executive summary and
      Section 12 conclusion updates, and a full Methods writeup covering
      the multicollinearity check, coefficient-stability test, and
      interaction checks against the scarring-stock and
      financial-expectations variables. See `docs/publication_strategy.md`,
      "P2b: long-term unemployment" for the full log. Republished.
- [x] Youth unemployment — fetched (`33_youth_unemployment.py`), checked
      against LTU and migration specifically per user's brief. Strongly
      correlated with subjective poverty on its own (level r=0.71,
      first-diff r=0.79, detrended r=0.81, survives FDR) but redundant with
      long-term unemployment once both are tested together (replacing
      headline unemployment with youth unemployment alone leaves Greece
      1st/worst; added on top of Model C-LTU, its coefficient is not
      significant, p=0.815). **Not added to the scorecard.** Integrated as
      a Section 4 correlation-table row, a Methods checkpoint entry, and a
      short supporting-context note in the migration subsection (youth
      unemployment's 2013 peak fell within a year of the 2012 emigration
      peak) — deliberately no standalone chart/subsection, since that would
      overstate its contribution next to long-term unemployment. See
      `docs/publication_strategy.md`, "P2c: youth unemployment" for the
      full log. Republished.
- [x] Inequality (Gini or S80:S20) — final P2 item, fetched
      (`36_income_inequality.py`). S80/S20 has full 2003–2024 coverage;
      Gini's is shorter (2014–2024). Greece is elevated but not extreme
      (6th of 27). Level correlation with subjective poverty is weak and
      does not survive FDR correction (r=0.15, adjusted p=0.54) — the only
      variable in the table with a non-significant level reading. Adding
      it to Model C-LTU contributes no independent explanatory power.
      **Not added to the scorecard, no dedicated subsection or chart** —
      integrated as a short Methods entry plus one sentence in the Section
      12 conclusion. The useful result is the negative one: Greece's gap
      is not mainly an inequality story. Also caught and fixed a real
      pipeline bug during this round (`04_merge_all.py` choking on three
      multi-row-per-year raw files from earlier P2 rounds) — see
      `docs/publication_strategy.md` for the full fix and the
      confirmation that no previously-published numbers were affected.
      Republished. **This closes out P2.**
- [x] Housing tenure — fetched (`35_housing_tenure.py`), treated as its own
      separate checkpoint per the user's instruction, not combined with
      P2e. Reframed a variable already central to the report
      (`housing_cost_overburden`) by tenure status: Greece's mortgage-free
      owners face a 25.7% overburden rate, the EU's highest by a wide
      margin (next: Sweden 14.0%, typical EU range 1–7%) — homeownership
      does not shield Greek households the way it does almost everywhere
      else in the EU. Renters are still worse off (37.4%), but the
      owner-renter gap is one of the EU's narrowest (Greece ranks 22nd of
      27) because owners are unusually burdened too, not because renters
      are spared — the "small gap" read as the strongest part of the
      finding, not a complication, per explicit user framing. Strongly
      collinear with the existing `housing_cost_overburden` variable
      (r≈0.9) and adds no independent model power once tested — **not
      added to the scorecard**, integrated as descriptive depth only.
      New Section 11 subsection ("Owning your home does not fully protect
      you here") placed between wage-adjusted pricing and long-term
      unemployment, plus a full Methods entry. See
      `docs/publication_strategy.md`, "Housing tenure" for the full log.
      Republished.
- [x] P2e: wage-adjusted cost-of-living pressure — fetched
      (`34_wage_adjusted_cost_of_living.py`), a strong, reader-facing
      finding. On raw price level Greece ranks only 18th-most-expensive of
      27 EU countries on overall consumption — not an expensive country in
      absolute terms. But its wages are so far below the EU average
      (48.3%, 4th-lowest) that once prices are scaled by wage level, the
      ranking reverses completely: Greece has the EU's highest
      wage-adjusted price pressure on overall consumption, and ranks 1st
      or 2nd of 27 in every category tested (food, housing, transport,
      restaurants, communication). Since 2008, Greek nominal wages are
      still 13.1% below their 2008 level while food prices rose 41.6% and
      housing/energy 33.6%. Integrated as a new Section 11 subsection ("A
      smaller paycheck facing ordinary prices"), placed between real wages
      and long-term unemployment; a 2024 price-vs-pressure table; an
      executive-summary paragraph; and a full Methods entry covering the
      real feasibility constraint (category-level price data only has
      full coverage 2022–2024) and why it wasn't tested as a scorecard
      model. See `docs/publication_strategy.md`, "P2e: wage-adjusted
      cost-of-living pressure" for the full log. Republished.

## P3 — Integrate into report

Originally planned as one batched step after all of P1a/b/c. User instead
asked to integrate P1a and P1b immediately after their checkpoints (ahead
of P1c), so this happened in two parts rather than one — noted here so the
plan and what actually happened stay in sync.

- [x] Add new sections where they strengthen the story — recovery
      trajectory promoted to lead "Still below its own pre-crisis peak";
      migration added as "The crisis also became an exit route" (P1a/P1b);
      real wages, wage-adjusted pricing, housing tenure, and long-term
      unemployment all added as their own Section 11 subsections (P2)
- [x] Keep exploratory labels clear and consistent — badge vocabulary
      reviewed and tightened during P4 (see below): "Descriptive check"
      added as a distinct label so confirmatory-model findings (LTU, GDP
      scarring, wage-adjusted pricing, anchored poverty) don't share a
      badge with tested-but-not-scorecard findings (real wages, housing
      tenure, financial expectations)
- [x] Update the scorecard if any new variable entered a model — done:
      Model C-LTU added as the preferred labor-market specification
      (P2b), highlighted in the Section 10 table
- [x] Update executive summary and conclusion — done across P2 (each
      integration round added its own paragraph) and tightened/completed
      during the P4 full review (see below): executive summary reduced
      from 9 to 5 content paragraphs + limits; Section 12 conclusion
      rewritten to cover every Section 11 finding, not just the ones
      integrated earliest
- [x] Update Methods and this documentation — done throughout P2, each
      round's dataset codes and citations added as they landed

**Commit**: `p1a-p1b-report-integration` (P1a/P1b) plus one commit per P2
sub-item; full details in `publication_strategy.md`

## P4 — Final release review

Same five-part structure as the review that produced P0, run again as a
bookend after P1–P3. Scoped explicitly as a release-readiness review, not
a new-ideas review — no new variables added, only consistency work on
what P1/P2 had already produced.

- [x] Claim audit — every headline number in the executive summary,
      scorecard, Section 11, Section 12, and Methods checked against the
      current CSV/JSON outputs. All consistent; no stale numbers found.
- [x] Narrative read-through — found and fixed: Section 11's title no
      longer matched its scope (renamed "Scarring and pessimism" →
      "The scars beneath the gap"); two self-referencing "(Section 11)"
      citations from inside Section 11 itself (→ "above"); a real
      factual contradiction (one passage said 2012 was "Greece's deepest
      economic trough," contradicting the GDP-scarring subsection's own
      2020 trough — corrected to reference the migration peak, which
      2012 actually is, elsewhere in this report); a real-vs-nominal
      wage clarity gap between two adjacent subsections (added a
      one-sentence units note)
- [x] Robustness / multiple-testing check — FDR counts in Methods
      confirmed current (21 variables, 16 survive) as of the P2 close
- [x] Greek-perspective framing check — confirmed intact: measurable
      material reasons (wages, jobs, prices, housing, migration) framed
      ahead of and separately from the more heavily caveated pessimism
      finding, throughout
- [x] Cross-reference and formatting pass — Section 12 conclusion
      rewritten to include wage-adjusted price pressure and housing
      tenure (previously absent entirely) and to drop "housing tenure"
      from its own "still open" speculative list (now tested); "Core
      finding" badge frequency reduced from 7 to 5 actual uses (kept:
      moving-threshold/anchored poverty, LTU ×2, wage-adjusted pricing,
      GDP scarring/recovery trajectory; demoted to new "Descriptive
      check" label: real wages, housing tenure, financial expectations)

**Commit**: `release-review-fixes` — full findings list and fix log in
`publication_strategy.md`, "Full Version 1 release-readiness review"
