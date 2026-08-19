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

- [ ] Real wages
- [ ] Youth unemployment
- [ ] Long-term unemployment
- [ ] Inequality (Gini or S80:S20)
- [ ] Housing tenure, if feasible

## P3 — Integrate into report

Originally planned as one batched step after all of P1a/b/c. User instead
asked to integrate P1a and P1b immediately after their checkpoints (ahead
of P1c), so this happened in two parts rather than one — noted here so the
plan and what actually happened stay in sync.

- [x] Add new sections where they strengthen the story — recovery
      trajectory promoted to lead "Still below its own pre-crisis peak";
      migration added as "The crisis also became an exit route" — **done
      for P1a/P1b**; trust near expectations still pending P1c
- [x] Keep exploratory labels clear and consistent — no new exploratory
      claims introduced by P1a/P1b (both are descriptive, not modeled)
- [ ] Update the scorecard if any new variable entered a model — N/A so far,
      neither P1a nor P1b variables were added to any regression
- [ ] Update executive summary and conclusion — not yet done for P1a/P1b
      findings specifically
- [x] Update Methods and this documentation — done for P1a/P1b (new dataset
      codes, new citations, `data_sources.md`, `publication_strategy.md`)

**Commit**: `p1a-p1b-report-integration` — done for P1a/P1b; P1c and P2
integration still pending a future pass through this checklist

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
