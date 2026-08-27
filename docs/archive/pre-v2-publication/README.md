# Pre-V2 publication documents — archived, not current

Six documents that tracked the project's status, plan and research reasoning
before and during the V2 rewrite, moved here so `docs/` isn't left with
several files answering "what is this project's current state?" differently.
None of these is current. **`docs/v2_research_record.md` is the one live
record** — it's what every other current document, and every script comment
in `scripts/`, cites for status and protocol going forward.

| File | What it was |
|---|---|
| `project_description.md` | The original V1 project brief. |
| `project_description_v2.md` | A revision of the brief, mid-project. |
| `project_description_v3.md` | The brief V2 was actually built against — still cited by several V2 pipeline scripts (`51_p0_outcome_reconciliation.py` and others) for the pre-registered protocol sections it defines. Superseded as a *status* document, not as a *protocol* citation: those references are correct and current, and point here deliberately. |
| `current_state.md` | A concise V1/early-V2 status snapshot, last updated 2026-08-20. |
| `todo_plan.md` | A release-readiness checklist from 2026-08-20, before the V2 rewrite most of this project's recent history consists of. |
| `publication_strategy.md` | The chronological research/decision log through the V2 rewrite. Explicitly marked **closed** in `docs/v2_research_record.md`'s own status table, which replaced it as the live notebook — kept here in full because it's cited throughout the codebase (`46_appendix_data.py`, `48_direction_persistence.py`, `50_persistence_share.py`, `79_context_register.py`, and others) as the record of *why* specific pre-registration and methodology decisions were made, which `v2_research_record.md` doesn't restate. |

Nothing here was deleted or rewritten — these are exactly what they were
before the move, only relocated. Any script comment or doc citing one of
these by its old `docs/<name>.md` path was updated to
`docs/archive/pre-v2-publication/<name>.md` in the same commit that moved it.
