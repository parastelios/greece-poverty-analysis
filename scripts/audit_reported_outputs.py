"""Scan the project's reported artifacts against the output schema.

Runs inside `make verify`. Anything that reaches a document or a frozen record
must be a clean scalar in its declared domain.
"""
import json
import sys
from pathlib import Path

import pandas as pd

from validate_outputs import scalar, json_safe, OutputError

OUT = Path("../data/processed")

# column -> kind, for the files whose numbers reach documents
SCHEMA = {
    "p3_objective_only.csv":   {"gap": "residual", "rank": "rank", "r2": "r2",
                                "n": "count", "gap_cltu": "residual",
                                "gap_no_accumulation": "residual",
                                "coef_min": "coefficient", "coef_max": "coefficient"},
    "p5_audit.csv":            {"within": "coefficient", "within_p": "p_value",
                                "between": "coefficient", "between_p": "p_value",
                                "fe_coef": "coefficient", "max_loo_pct": "coefficient",
                                "greece_pct": "coefficient", "p_MC_max": "p_value"},
    "p5_bootstrap.csv":        {"seed": "count", "reps": "count",
                                "n_extreme": "count", "p_MC": "p_value"},
    "p5_influence.csv":        {"coef": "coefficient", "pct": "coefficient"},
    "p2_specifications.csv":   {"pre_rmse": "se", "post_gap": "residual",
                                "max_w": "share", "eff_donors": "coefficient"},
    "p0_verdict.csv":          {"median_abs_diff": "se", "share_within_5pp": "share",
                                "min_spearman": "correlation",
                                "greece_trend_corr": "correlation"},
    "persistence_share_battery.csv": {"p_raw": "p_value", "p_fdr_bh": "p_value",
                                      "coef": "coefficient", "r2": "r2", "n": "count"},
    "direction_persistence_battery.csv": {"p_raw": "p_value", "p_fdr_bh": "p_value",
                                          "coef": "coefficient", "r2": "r2", "n": "count"},
    "cumulative_hardship_fdr_correction.csv": {"p_raw": "p_value", "p_fdr_bh": "p_value"},
    "p3a_individual_indicators.csv": {"coef": "coefficient", "p_raw": "p_value",
                                      "p_fdr": "p_value", "greece_resid": "residual",
                                      "rank": "rank"},
    "p3a_results.csv":               {"coef": "coefficient", "p": "p_value",
                                      "greece": "residual", "rank": "rank"},
}
NULLABLE = {("p2_specifications.csv", "post_gap")}

problems, checked = [], 0
for fname, cols in SCHEMA.items():
    path = OUT / fname
    if not path.exists():
        problems.append(f"{fname}: MISSING")
        continue
    df = pd.read_csv(path)
    for col, kind in cols.items():
        if col not in df.columns:
            problems.append(f"{fname}: column {col!r} absent")
            continue
        for i, raw in enumerate(df[col]):        # bracket access, never df.col
            try:
                scalar(raw, kind, f"{fname}:{col}[{i}]",
                       nullable=(fname, col) in NULLABLE)
                checked += 1
            except OutputError as e:
                problems.append(str(e))

# the frozen record must serialize with no custom coercion
frozen = OUT / "p5f_frozen_result.json"
if frozen.exists():
    try:
        json_safe(json.loads(frozen.read_text()), str(frozen))
        checked += 1
    except OutputError as e:
        problems.append(str(e))

print(f"Validated {checked} reported quantities across {len(SCHEMA)} artifacts")
if problems:
    print(f"\n{len(problems)} PROBLEM(S):")
    for p in problems[:25]:
        print(f"  {p}")
    sys.exit(1)
print("OUTPUT SCHEMA OK: every reported quantity is a finite in-domain scalar")
