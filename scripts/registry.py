"""Validated access to the E0 variable registry.

Exists because of a specific failure. E1 read `adverse_direction` and compared
it against "high"/"low" -- values that column has never held. Every variable
silently became lower_is_worse, and four correct results were published as
direction contradictions. The decision rule was tested and correct; the
translation feeding it was not, and no test touched it.

So the vocabularies are asserted HERE, once, at load time. A typo now fails the
build instead of quietly reclassifying every variable in the study.
"""
from pathlib import Path

import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

ADVERSE = {"higher_is_worse", "lower_is_worse", "ambiguous"}
PROXIMITY = {"objective", "proximate_same_instrument", "mechanical_with_arop",
             "contextual", "comparator_baseline"}
ROLES = {"primary_representative", "sensitivity_variant", "proximate_diagnostic",
         "contextual_descriptive", "mechanical_comparator", "standalone_retest",
         "standalone_retest_of_known_null"}
CONSTRUCTION = {"direct_excess", "fixed_base_shortfall", "duration_below_base",
                "compounded_change", "ambiguous_direction", "not_applicable"}

VOCABULARIES = {"adverse_direction": ADVERSE, "proximity_class": PROXIMITY,
                "role": ROLES, "construction": CONSTRUCTION}

# Any predictor in these classes is disqualified from a headline claim.
BLOCKING_PROXIMITY = {"proximate_same_instrument", "mechanical_with_arop"}


def load():
    """Return the registry indexed by name, with every vocabulary checked."""
    reg = pd.read_csv(PROC / "e0_variable_registry.csv").set_index("name")
    problems = []
    for col, allowed in VOCABULARIES.items():
        if col not in reg.columns:
            problems.append(f"registry has no column {col!r}")
            continue
        seen = set(reg[col].dropna().unique())
        unknown = seen - allowed
        if unknown:
            problems.append(
                f"{col}: unknown value(s) {sorted(unknown)}; "
                f"allowed {sorted(allowed)}")
    if reg.index.duplicated().any():
        problems.append(f"duplicate names: "
                        f"{sorted(reg.index[reg.index.duplicated()])}")
    if problems:
        raise SystemExit("REGISTRY VOCABULARY\n  " + "\n  ".join(problems))
    return reg


def adverse_direction(reg, name):
    """The pre-registration's own vocabulary, passed through, never translated."""
    v = reg.loc[name, "adverse_direction"]
    if v not in ADVERSE:
        raise ValueError(f"{name}: adverse_direction {v!r} not in {sorted(ADVERSE)}")
    return v


def blocks_headline(reg, name):
    return reg.loc[name, "proximity_class"] in BLOCKING_PROXIMITY
