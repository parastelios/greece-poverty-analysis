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
- [ ] Net migration, crisis/recovery years
- [ ] Age profile, if comparable
- [ ] Return migration, if comparable
- [ ] Explicitly note anything not clean/comparable rather than forcing it
      (education/skill profile, cross-country comparison were flagged as
      the least likely to be cleanly available)
- [ ] Checkpoint: report findings, recommend placement, decide
      integrate/hold back

**Commit**: `p1b-migration-feasibility`

### P1c — Trust in state/EU
- [ ] Feasibility check: comparable source, years, country coverage, method
      consistency — before any modeling
- [ ] Only proceed to modeling if it clears that bar
- [ ] Checkpoint: report findings, recommend placement, decide
      integrate/hold back

**Commit**: `p1c-trust-feasibility`

## P2 — Labor-market and distribution extensions (lower priority)

- [ ] Real wages
- [ ] Youth unemployment
- [ ] Long-term unemployment
- [ ] Inequality (Gini or S80:S20)
- [ ] Housing tenure, if feasible

## P3 — Integrate into report

Only after the P1 checkpoints (and P2, if pursued) are individually decided.

- [ ] Update the scorecard if any new variable entered a model
- [ ] Add new sections only where they strengthen the story (recovery
      trajectory near scarring; migration as a structural scarring channel;
      trust near expectations, if included)
- [ ] Keep exploratory labels clear and consistent
- [ ] Update executive summary and conclusion
- [ ] Update Methods and this documentation

**Commit**: `report-integration`

## P4 — Final release review

Same five-part structure as the review that produced P0, run again as a
bookend after P1–P3.

- [ ] Claim audit — check every new claim against the underlying CSVs
- [ ] Narrative read-through — as a first-time reader
- [ ] Robustness / multiple-testing check
- [ ] Greek-perspective framing check
- [ ] Cross-reference and formatting pass

**Commit**: `release-review-fixes`
