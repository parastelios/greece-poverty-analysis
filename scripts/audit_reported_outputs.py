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
    "e0_coverage.csv":               {"n_obs": "count", "pct": "share",
                                      "countries": "count", "years": "count"},
    "e0_redundancy.csv":             {"pooled": "correlation", "between": "correlation",
                                      "within": "correlation"},
    "e_mde.csv":                     {"effect_sd_per_sd": "coefficient",
                                      "effect_points_per_sd": "coefficient",
                                      "power": "share"},
    "ea_results.csv":                {"p3_residual": "residual",
                                      "p3_rank": "rank",
                                      "p3_r2": "r2",
                                      "companion_residual": "residual",
                                      "companion_rank": "rank",
                                      "companion_r2": "r2",
                                      "degradation": "coefficient",
                                      "companion_residual_no_accumulation": "residual",
                                      "cum_coef_p3": "coefficient",
                                      "cum_coef_companion": "coefficient",
                                      "cum_se_companion": "coefficient",
                                      "bootstrap_t": "coefficient",
                                      "bootstrap_p": "p_value",
                                      "loo_coef_min": "coefficient",
                                      "loo_coef_max": "coefficient",
                                      "max_vif": "coefficient",
                                      "n": "count"},
    "e1_results.csv":                {"coef": "coefficient", "se": "se",
                                      "p_raw": "p_value", "p_fdr": "p_value",
                                      "ci_lo": "coefficient", "ci_hi": "coefficient",
                                      "std_effect": "coefficient",
                                      "ci_abs_std_upper": "coefficient",
                                      "r2_base": "r2", "r2_full": "r2",
                                      "greece_resid_base": "residual",
                                      "greece_resid_full": "residual",
                                      "n": "count", "countries": "count"},
    "e1_secondary.csv":              {"coef": "coefficient", "se": "se",
                                      "p_raw": "p_value", "p_fdr": "p_value",
                                      "n": "count"},
    "e2_pooled_posthoc.csv":         {"p_raw": "p_value", "p_fdr": "p_value",
                                      "p_fdr_pooled": "p_value"},
    "e2_results.csv":                {"coef": "coefficient", "se": "se",
                                      "p_raw": "p_value", "p_fdr": "p_value",
                                      "boot_p": "p_value",
                                      "std_effect": "coefficient",
                                      "ci_abs_std_upper": "coefficient",
                                      "n": "count"},
}
NULLABLE = {("p2_specifications.csv", "post_gap"),
            # P1 is excluded from BH family 1 by pre-registration, so it
            # legitimately has no adjusted p-value. A number here would be
            # the bug -- it would mean a diagnostic-only construct had been
            # corrected alongside the eligible ones.
            ("e1_results.csv", "p_fdr"),
            ("e1_secondary.csv", "p_fdr"),
            # Proximity-blocked members get no adjusted p and no bootstrap:
            # they are excluded from their family before testing.
            ("e2_results.csv", "p_fdr"),
            ("e2_results.csv", "boot_p")}

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
