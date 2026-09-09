# The Greek Poverty Paradox

Why do roughly two in three Greek households say they struggle to make ends
meet when the official income-poverty rate counts roughly one person in
five?

This repository contains the data, analysis, figures, and published
documents behind an investigation of that gap. It asks whether reported
hardship has a material basis, why official poverty measures capture so
little of it, and how much Greece's current conditions and accumulated
crisis burden help explain.

**Explore the project:** [English](https://parastelios.github.io/greece-poverty-analysis/) | [Ελληνικά](https://parastelios.github.io/greece-poverty-analysis/el.html)

## Start here

Choose the route that matches what you want from the project:

| I want to... | Start with... |
|---|---|
| Get the argument in a few minutes | [Project overview](https://parastelios.github.io/greece-poverty-analysis/) or [Greek overview](https://parastelios.github.io/greece-poverty-analysis/el.html) |
| Read the evidence as a story | [Narrative article](https://parastelios.github.io/greece-poverty-analysis/narrative.html) or [Greek narrative](https://parastelios.github.io/greece-poverty-analysis/narrative_el.html) |
| Inspect the complete analysis and its limitations | [Technical report](https://parastelios.github.io/greece-poverty-analysis/report.html) |
| Read the academic version | [Working paper](https://parastelios.github.io/greece-poverty-analysis/paper.html) |
| Explore every measure and diagnostic | [Statistical appendix](https://parastelios.github.io/greece-poverty-analysis/statistical_appendix.html) |
| Understand the project design and final scope | [`docs/project_description.md`](docs/project_description.md) |
| Audit decisions, corrections, and failed tests | [`docs/v2_research_record.md`](docs/v2_research_record.md) |

PDF versions of the five documents are available in [`output/pdf/`](output/pdf/).

## The question in numbers

For 2024, Eurostat reports:

- **66.7% of Greek households** said they made ends meet with difficulty or
  great difficulty, the highest share in the EU.
- **19.6% of people in Greece** were at risk of income poverty (AROP), the
  seventh-highest rate among the 27 EU member states.
- Across 2015–2024, the average distance between those measures was **52.6
  percentage points**.

The denominators differ deliberately: reported hardship is a household
answer; AROP counts people whose equivalised household income is below 60%
of the current national median.

## What the analysis finds

- Reported hardship moves with concrete problems such as being unable to
  meet an unexpected expense, inadequate heating, and material deprivation.
  A general negative response style cannot be excluded, but the evidence
  does not support dismissing the hardship as pessimism without a material
  basis.
- AROP is a relative measure whose threshold falls when national median
  income falls. A fixed 2008 threshold reveals much more crisis-era
  deterioration. The broader AROPE measure closes only about 19% of the
  average gap.
- Employment improved substantially, but household economic security did
  not improve with it to the same extent. Real wages remained below their
  2008 level, housing pressure stayed high, and purchasing power lagged.
- Three present-day conditions and three accumulated-history measures carry
  information about hardship beyond income poverty. These are cross-country
  associations, not identified causes or household-level effects.
- The factors tested help explain much of the picture, but not the whole
  gap. Most of the 52.6-point distance remains unattributed, and that
  unexplained remainder is not evidence that pessimism accounts for it.

The analysis is intentionally explicit about uncertainty. Results that
failed, reversed under a reasonable modelling choice, could not be tested,
or lacked enough statistical power remain visible rather than being
dropped.

## Verify the published results

The quickest safe check uses the committed data and generated artifacts. It
does not refresh data from Eurostat.

```bash
git clone https://github.com/parastelios/greece-poverty-analysis.git
cd greece-poverty-analysis
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make verify
```

Python 3.11 or later is recommended. No API key is required.

### Useful commands

| Command | What it does |
|---|---|
| `make verify` | Runs the offline tests and checks the published claims, figures, documents, and English/Greek parity against the committed artifacts. |
| `make release-verify` | Runs the stricter publication gate, including the technical-report and website checks. |
| `make fetch` | Contacts the source APIs in comparison mode and reports differences without replacing the archived raw inputs. |
| `make fetch-write` | Refreshes the raw inputs. This changes the data vintage and may change results. |
| `make build` | Runs the full pipeline and document builders. **This contacts live APIs and can rewrite data and outputs as upstream series are revised.** Review the resulting diff carefully. |
| `make reproduce` | Exports the committed tree to a temporary directory, performs a live refresh and complete rebuild there, and leaves the working copy untouched. |

For routine editing, use `make verify`. Use `make reproduce` when you want
to test current live-data reproducibility without changing the publication
snapshot.

## Project structure

```text
site/             English and Greek landing pages and visual assets
scripts/          Analysis, tests, figures, and document builders
data/raw/         Committed source-data snapshot used by the published analysis
data/processed/   Derived tables, figure data, frozen claims, and context register
docs/             Project description, methodology notes, and research record
output/           Generated HTML documents, PDFs, and intermediate build pages
archive/v1-final/ Superseded V1 publication, retained for provenance
```

The numbered scripts are not a reliable build order. The `Makefile` is the
authoritative dependency order because several later-numbered scripts
produce inputs required by earlier-numbered document builders.

## Editing and publication

- Do not hand-edit generated documents in `output/`. Edit their builders in
  `scripts/`, rebuild, and run the verification gates.
- The English and Greek narratives are separately authored but checked for
  equivalent structure, claims, statistics, and contextual material.
- Frozen findings are stored in
  [`data/processed/e_final_claims.csv`](data/processed/e_final_claims.csv).
- Context discussed but not established is stored in
  [`data/processed/context_register.csv`](data/processed/context_register.csv).
- The protocol fixed before the V2 results is preserved in
  [`docs/archive/pre-v2-publication/project_description_v3.md`](docs/archive/pre-v2-publication/project_description_v3.md).
- V1 is retained in [`archive/v1-final/`](archive/v1-final/) for comparison.
  It is superseded and should not be treated as the project's current
  conclusion.

GitHub Pages deploys automatically when relevant changes reach `main`.
Before publishing, the deployment workflow checks the landing pages against
the canonical data and document set.

## Data and reproducibility

The inferential results use the committed data snapshot in `data/raw/` and
`data/processed/`. This prevents published findings from changing silently
when Eurostat revises historical series.

A live rebuild may not reproduce every archived value exactly because
upstream datasets can be revised. That is why the project separates:

- verification against the committed publication snapshot;
- checking for newly available source data;
- deliberately updating the data vintage;
- isolated end-to-end reproduction against the latest available data.

For the full methodology, evidence hierarchy, exclusions, and unresolved
questions, see [`docs/project_description.md`](docs/project_description.md).
For the chronological audit trail, see
[`docs/v2_research_record.md`](docs/v2_research_record.md).
