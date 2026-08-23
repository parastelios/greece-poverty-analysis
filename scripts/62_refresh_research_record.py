"""Refresh the generated blocks of docs/v2_research_record.md.

The record is hand-written prose. Four blocks inside it are derived from the
repository and would silently go stale if typed by hand, so they are
regenerated here between AUTO markers:

    document-control  git state and the frozen references
    stage-index       stage status inferred from artifacts on disk
    claim-summary     counts from docs/claim_matrix.csv, never a copy of it
    artifact-index    every E-stage and P-stage artifact actually present

Everything outside the markers is left untouched.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "v2_research_record.md"
PROC = ROOT / "data" / "processed"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()


# Stage -> (question, artifacts that must exist for the stage to count as done,
#           pre-registration commit, result commit)
STAGES = [
    ("P0", "Is our outcome measure the real thing?",
     ["p0_verdict.csv"], "", ""),
    ("P2", "Can we build a synthetic comparison country?",
     ["p2_specifications.csv"], "", ""),
    ("P3", "How much of Greece's gap do objective conditions explain?",
     ["p3_objective_only.csv"], "", ""),
    ("P5", "Is that a real relationship, or a difference between countries?",
     ["p5f_frozen_result.json"], "", "p5f-frozen"),
    ("P3a", "Does breadth of disadvantage add anything?",
     ["p3a_results.csv"], "p3a_frozen_universe.json", ""),
    ("E0", "What data and constructs are suitable for testing?",
     ["construct_map_frozen.json"], "", "2103b3d"),
    ("PRE", "What exact tests and decision rules are fixed before analysis?",
     ["e_mde.csv"], "a747e7a", "476e177"),
    ("EDA", "What do the candidate variables actually look like?",
     ["e_descriptives.csv"], "", ""),
    ("EA", "How much of the P3 result depends on a same-instrument predictor?",
     ["ea_results.csv"], "ea_preregistration.json", ""),
    ("E1", "Which current-level constructs are associated with hardship?",
     ["e1_results.csv"], "a747e7a", ""),
    ("E2", "Do sensitivity variants change the current-level conclusions?",
     ["e2_results.csv"], "a747e7a", ""),
    ("E3", "What do the diagnostic and contextual checks show?",
     ["e3_results.csv"], "a747e7a", ""),
    ("E4", "Which accumulated constructs are associated with hardship?",
     ["e4_results.csv"], "a747e7a", ""),
    ("E5", "Do accumulated-measure sensitivities change those conclusions?",
     ["e5_results.csv"], "a747e7a", ""),
    ("E6", "Does the frozen combined model remain appropriate?",
     ["e6_results.csv"], "a747e7a", ""),
    ("E7", "Do accumulated measures add information beyond current snapshots?",
     ["e7_results.csv"], "a747e7a", ""),
    ("FINAL", "What survives into the final reports?",
     ["e_final_claims.csv"], "", ""),
]

ANCHORS = {
    "P0": "p0--is-our-outcome-measure-the-real-thing",
    "P2": "p2--can-we-build-a-synthetic-comparison-country",
    "P3": "p3--how-much-of-greeces-gap-do-objective-conditions-explain",
    "P5": "p5--is-that-a-real-relationship-or-a-difference-between-countries",
    "P3a": "p3a--does-breadth-of-disadvantage-add-anything",
    "E0": "e0--data-and-construct-map",
    "PRE": "pre--pre-registration-and-power",
    "EDA": "eda--descriptive-groundwork",
    "EA": "ea--deprivation-free-companion-audit",
    "E1": "e1--current-level-constructs",
    "E2": "e2--current-level-sensitivities",
    "E3": "e3--diagnostic-and-contextual-checks",
    "E4": "e4--accumulated-exposure",
    "E5": "e5--accumulation-sensitivities",
    "E6": "e6--frozen-combined-model",
    "E7": "e7--current-versus-accumulated-comparison",
    "FINAL": "final--claim-freeze-and-publication",
}


def stage_index() -> str:
    rows = [
        "| Stage | Question | Status | Pre-registration | Result | Entry |",
        "|---|---|---|---|---|---|",
    ]
    last_done = None
    current = None
    for sid, question, artifacts, prereg, result in STAGES:
        done = all((PROC / a).exists() for a in artifacts)
        if done:
            status = "complete"
            last_done = sid
        elif current is None:
            status = "**next**"
            current = sid
        else:
            status = "pending"
        pre = f"`{prereg}`" if prereg else "—"
        res = f"`{result}`" if result and done else "—"
        rows.append(
            f"| {sid} | {question} | {status} | {pre} | {res} "
            f"| [{sid}](#{ANCHORS[sid]}) |"
        )
    return "\n".join(rows), last_done, current


def document_control(last_done: str | None, current: str | None) -> str:
    dirty = "yes" if git("status", "--porcelain") else "no"
    rows = [
        "| Field | Value |",
        "|---|---|",
        f"| Current stage | {current or 'none — sequence complete'} |",
        f"| Last completed stage | {last_done or 'none'} |",
        f"| Branch | `{git('rev-parse', '--abbrev-ref', 'HEAD')}` |",
        f"| HEAD | `{git('rev-parse', '--short', 'HEAD')}` "
        f"{git('log', '-1', '--pretty=%s')} |",
        f"| Uncommitted changes | {dirty} |",
        f"| Last refreshed | {date.today().isoformat()} |",
        "| Frozen V1 reference | `v1-final` |",
        "| Frozen V2 analytical reference | `p5f-frozen` |",
    ]
    return "\n".join(rows)


def claim_summary() -> str:
    path = ROOT / "docs" / "claim_matrix.csv"
    if not path.exists():
        return "_`claim_matrix.csv` not found._"
    df = pd.read_csv(path)
    rows = [f"Current state of `docs/claim_matrix.csv`: **{len(df)} claims**.", ""]
    if "v2_disposition" in df.columns:
        counts = df["v2_disposition"].fillna("(unset)").value_counts()
        rows += ["| V2 disposition | Claims |", "|---|---:|"]
        rows += [f"| {k} | {v} |" for k, v in counts.items()]
    return "\n".join(rows)


ARTIFACT_PURPOSE = {
    "p0_outcome_reconciliation.csv": ("P0", "Official vs constructed series, country-year"),
    "p0_verdict.csv": ("P0", "The four pre-declared tolerance checks"),
    "p2_specifications.csv": ("P2", "Synthetic-control fit across three pre-periods"),
    "p2_donor_weights.csv": ("P2", "Donor weights showing the two-country collapse"),
    "p2_placebo_distribution.csv": ("P2", "Placebo inference distribution"),
    "p3_objective_only.csv": ("P3", "Objective-only model, residuals by specification"),
    "p3_residuals.csv": ("P3", "Per-country residuals and ranks"),
    "p3a_frozen_universe.json": ("P3a", "Family D universe, frozen before testing"),
    "p3a_results.csv": ("P3a", "Incremental test of accumulated breadth"),
    "p3a_individual_indicators.csv": ("P3a", "Per-indicator breadth components"),
    "p5_audit.csv": ("P5", "Mundlak within/between decomposition"),
    "p5_bootstrap.csv": ("P5", "Wild cluster bootstrap across weights and seeds"),
    "p5_influence.csv": ("P5", "Leave-one-country-out stability"),
    "p5f_frozen_result.json": ("P5", "FROZEN P3/P5/P3a values and eight wording rules"),
    "e0_extended_panel.csv": ("E0", "27 countries x 2015-2024 candidate panel"),
    "e0_variable_registry.csv": ("E0", "31 variables: units, roles, construction, proximity"),
    "e0_coverage.csv": ("E0", "Reporter counts by variable and year"),
    "e0_corr_pooled.csv": ("E0", "Pooled correlations incl. five outcome comparators"),
    "e0_corr_between.csv": ("E0", "Between-country correlations"),
    "e0_corr_within.csv": ("E0", "Within-country correlations"),
    "e0_nonindependence_flags.csv": ("E0", "35 flags across four overlap types"),
    "e0_redundancy.csv": ("E0", "Primary-vs-sensitivity redundancy, all three views"),
    "e0_lineage.csv": ("E0", "How each derived variable was constructed"),
    "e0_provenance.json": ("E0", "Source series and vintage"),
    "construct_map_frozen.json": ("E0", "FROZEN six constructs plus one diagnostic"),
    "e_preregistration.json": ("PRE", "FROZEN outcomes, transformations, decision rule"),
    "e_mde.csv": ("PRE", "Power curve; MDE 0.70 SD = 9.29 points at 80%"),
    "ea_preregistration.json": ("EA", "FROZEN deprivation-free companion spec and decision rule"),
    "ea_results.csv": ("EA", "Outcome C: residual reverses +6.93 -> -9.39"),
    "e_descriptives.csv": ("EDA", "Greece hardship vs AROP vs AROPE by year"),
    "e_descriptive_ranks.csv": ("EDA", "Greece's rank per variable per year"),
    "e_descriptive_recovery.csv": ("EDA", "Gap movement 2015-2024, trend classified"),
    "e1_results.csv": ("E1", "Nine current primaries: 3 supported, 6 inconclusive"),
    "e1_secondary.csv": ("E1", "Secondary outcome, BH family 3, promotion blocked"),
    "e2_results.csv": ("E2", "Within-construct sensitivities and dispositions"),
    "e2_pooled_posthoc.csv": ("E2", "Post hoc pooled FDR, disclosed under PD-01"),
    "e3_results.csv": ("E3", "Contextual and legacy checks; no family, no FDR"),
    "e3_restatement.csv": ("E3", "P1 absorbs 71% of Greece's baseline residual"),
    "e4_feasibility.csv": ("E4", "7 of 10 accumulations constructible; C1 is not"),
    "e4_accumulated_panel.csv": ("E4", "Panel with the built accumulations merged"),
    "e4_results.csv": ("E4", "BH family 2; 3 supported, all between-country"),
    "e4_current_vs_accumulated.csv": ("E4", "Head-to-head on identical observations"),
    "e4_threshold_sensitivity.csv": ("E4", "Mixed-baseline threshold, outside BH family 2"),
    "ea_companion_residuals.csv": ("EA", "Companion residual ladder, 27 countries"),
}


def artifact_index() -> str:
    rows = ["| Stage | Artifact | Purpose | Status |", "|---|---|---|---|"]
    stage_order = {sid: i for i, (sid, *_) in enumerate(STAGES)}
    ordered = sorted(ARTIFACT_PURPOSE.items(),
                     key=lambda kv: (stage_order.get(kv[1][0], 99), kv[0]))
    for name, (stage, purpose) in ordered:
        path = PROC / name
        rows.append(
            f"| {stage} | `{name}` | {purpose} | "
            f"{'present' if path.exists() else '**MISSING**'} |"
        )
    known = set(ARTIFACT_PURPOSE)
    extra = sorted(
        p.name
        for p in PROC.glob("*")
        if p.name not in known
        and re.match(r"^(p[0-9]|e[0-9]|e_|construct_map)", p.name)
    )
    for name in extra:
        rows.append(f"| ? | `{name}` | **undocumented — add to ARTIFACT_PURPOSE** | present |")
    return "\n".join(rows)


def sort_register_rows(text: str) -> str:
    """Sort the register tables by ID.

    Rows get appended next to whatever anchor was convenient at the time, so
    the Results register had drifted to R-01..R-04, R-15..R-19, R-07..R-14,
    R-06, R-05. Harmless to a machine and actively confusing to the person this
    notebook is written for. Sorting is mechanical and idempotent, so it runs
    on every refresh rather than being fixed once by hand.
    """
    lines = text.split("\n")
    out, i, moved = [], 0, 0
    row = re.compile(r"^\| ([RDC])-(\d+) \|")
    while i < len(lines):
        m = row.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        prefix = m.group(1)
        block = []
        while i < len(lines):
            m2 = row.match(lines[i])
            if not m2 or m2.group(1) != prefix:
                break
            block.append((int(m2.group(2)), lines[i]))
            i += 1
        ordered = [ln for _, ln in sorted(block, key=lambda x: x[0])]
        if ordered != [ln for _, ln in block]:
            moved += 1
        out.extend(ordered)
    if moved:
        print(f"  reordered {moved} register table(s) by ID")
    return "\n".join(out)


def splice(text: str, key: str, body: str) -> str:
    begin, end = f"<!-- AUTO:BEGIN {key} -->", f"<!-- AUTO:END {key} -->"
    pattern = re.compile(
        re.escape(begin) + r".*?" + re.escape(end), re.DOTALL
    )
    if not pattern.search(text):
        raise SystemExit(f"marker block '{key}' not found in {RECORD}")
    return pattern.sub(f"{begin}\n{body}\n{end}", text)


def main() -> None:
    index, last_done, current = stage_index()
    text = RECORD.read_text()
    text = splice(text, "document-control", document_control(last_done, current))
    text = splice(text, "stage-index", index)
    text = splice(text, "claim-summary", claim_summary())
    text = splice(text, "artifact-index", artifact_index())
    text = sort_register_rows(text)
    RECORD.write_text(text)
    print(f"refreshed {RECORD.relative_to(ROOT)}")
    print(f"  last completed stage: {last_done}")
    print(f"  next stage: {current}")


if __name__ == "__main__":
    main()
