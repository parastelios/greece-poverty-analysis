# Current project state

Updated 2026-08-20. This is the concise live status; `publication_strategy.md`
remains the chronological research log.

## Shared argument

All three outputs use the same evidence spine:

1. AROP is the primary puzzle: elevated, but not exceptional, while subjective
   hardship is the EU's highest.
2. AROP's moving national threshold understated Greece's crisis-era loss.
3. AROPE is the official multidimensional bridge; it narrows but does not close
   the gap and cannot be reconstructed from aggregate component rates.
4. Housing and cash-flow strain narrow the out-of-sample residual, though
   housing alone worsens it and proximate indicators overlap with the outcome.
5. Long-term unemployment cuts the residual from 11.6 to 3.9 points.
6. Duration-sensitive exposure measures remove Greece's exceptional outlier
   status. The fixed specification gives -0.8; full nested validation gives
   +2.70 and rank 19/27. The nested result is primary.
7. GDP, wages, prices, housing, migration, age, expectations, and work effort
   provide corroborating context, not equal mechanisms.
8. Inequality is unsupported as an explanation; a stable reporting premium
   cannot explain the crisis-era widening or its financial specificity.
9. AROP should not be read alone during broad macroeconomic collapse.

## Output roles

- `output/report.html`: complete technical evidence record, with Section 11's
  central route explicit and extended method batteries expandable.
- `output/academic_paper_draft.html`: formal argument and full validation.
- `output/narrative_companion.html`: complete general-audience story, with
  technical notes available as a second reading layer.

## Reproducibility and controls

- `make verify`: 41 checks matching published claims to pipeline data.
- `make reproduce`: isolated live re-acquisition, build, and publication-vintage
  comparison. The 2026-08-20 run completed acquisition and all analysis steps,
  then correctly stopped on one live-source revision: fresh Eurostat real-wage
  data produce 18 rather than 17 detrended FDR survivors. The other 40
  headline checks agree. Archived-vintage reproducibility is therefore kept
  distinct from replication against a changing live source.
- Thirteen of fifteen formerly orphaned inputs match byte-for-byte. The two
  documented differences do not alter a headline model.
- `docs/claim_matrix.csv` records canonical wording, importance, window,
  status, caveat, source, and required treatment by output.
- `scripts/audit_parity.py` checks coverage and rejects known false or stale
  formulations.
- FDR correction applies within declared exploratory families. Sequential
  model development remains exploratory or post-selection, not pre-registered.

## Remaining publication work

- Author, affiliation, disclosure decision, target journal, and venue style.
- Publisher-level reference metadata verification.
- Optional new-design extensions: EU-SILC microdata, household balance sheets,
  and explicit spatial-dependence modeling.
