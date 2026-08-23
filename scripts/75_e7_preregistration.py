"""Freeze the E7 pre-registration: does accumulation add information beyond
current conditions?

NO RESULTS IN THIS SCRIPT. It writes the design and the decision rule. The
models are not fitted here and must not be fitted before this file is committed.

WHY A PRE-REGISTRATION AT ALL, THIS LATE. E4 already ran current and accumulated
measures in SEPARATE models on equal samples. Separate models cannot answer
whether accumulation adds information BEYOND current conditions -- comparing two
p-values from two models is not a conditional test. Answering the stage's actual
question requires a joint model, and a joint model needs its rules fixed before
it is seen, because there are many defensible ways to read one.
"""
import json
from pathlib import Path

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

PREREG = {
    "status": "PRE-REGISTERED. No E7 result exists at this commit.",
    "stage": "E7",
    "question": ("Does accumulated exposure add information beyond current "
                 "conditions, and vice versa?"),
    "why_not_the_narrower_question": (
        "The narrower question -- how current and accumulated representations "
        "perform in SEPARATE equal-sample models -- was already answered at E4. "
        "Answering it again would not address 'adds information beyond'."),

    "models": [
        "1. current-only:      subjective_poverty ~ arop + C(time) + <current>",
        "2. accumulated-only:  subjective_poverty ~ arop + C(time) + <accumulated>",
        "3. joint:             subjective_poverty ~ arop + C(time) + <current> + <accumulated>",
        "All three on IDENTICAL observations: the intersection of the pair's "
        "complete cases.",
    ],

    "conditional_tests": {
        "accumulated_adds": "coefficient on <accumulated> in the JOINT model",
        "current_adds": "coefficient on <current> in the JOINT model",
        "note": ("Both are reported for every pair. Neither is privileged, and "
                 "a pair where both survive is a legitimate outcome."),
    },

    "reported_for_all_three_models": [
        "coefficient, cluster-robust SE, p",
        "wild cluster bootstrap, null imposed, for anything called supported",
        "leave-one-country-out sign stability",
        "Greece's out-of-sample residual",
        "VIF and the current/accumulated correlation in the joint model",
    ],

    "multicollinearity_rule": {
        "thresholds": {"max_vif": 10.0, "abs_correlation": 0.90},
        "rule": (
            "If the joint model's VIF exceeds 10 or the current/accumulated "
            "correlation exceeds 0.90 in absolute value, the conditional test "
            "is UNINTERPRETABLE and must be reported as such. It is NOT a null. "
            "The two measures cannot be separated on this data, and a "
            "non-significant coefficient under collinearity says nothing about "
            "whether the measure adds information."),
        "why_declared_now": (
            "Current and accumulated forms of one construct can be almost the "
            "same series. Deciding after the fact whether a collinear result "
            "counts as a null would be the choice this rule removes."),
    },

    "decision_rule": {
        "adds_information": [
            "direction matches the pre-registration",
            "survives the wild cluster bootstrap in the JOINT model",
            "leave-one-country-out sign-stable in the JOINT model",
            "Greece's out-of-sample residual improves against the model "
            "WITHOUT it (current-only for the accumulated test, "
            "accumulated-only for the current test)",
            "the multicollinearity rule is not triggered",
        ],
        "all_must_hold": True,
        "forbidden": (
            "SUPERIORITY MAY NOT BE DECIDED BY COMPARING TWO P-VALUES from two "
            "separate models. That comparison is not a test of difference, and "
            "E5 already recorded the same error in another form (C-23)."),
        "failure_labels": (
            "Reuse e_rule's labels. A failure below the published MDE is "
            "INCONCLUSIVE UNDER AVAILABLE POWER, not unsupported."),
    },

    "restrictions_retained": [
        "Between/within decomposition for every accumulated measure.",
        "FIRST DIFFERENCES required before any dynamic wording. E4 found none "
        "supported; nothing in E7 may relax that.",
        "Current and accumulated are DIFFERENT ESTIMANDS. A pair where the "
        "accumulated measure survives conditionally does not show that history "
        "matters more than standing.",
    ],

    "multiplicity": (
        "The pairs are the pre-registered accumulated primaries and their "
        "current counterparts. This is a conditional re-examination of results "
        "already corrected within BH families 1 and 2, NOT a new discovery "
        "family, and NOTHING in E7 may create a finding that E1 or E4 did not "
        "already support. E7 can only qualify or withdraw."),

    "frozen_protection": (
        "Nothing in E7 may alter p5f-frozen, P3, P5, P3a, or any E1-E6 result."),
}


def main():
    path = PROC / "e7_preregistration.json"
    path.write_text(json.dumps(PREREG, indent=2) + "\n")
    print(f"wrote {path.name}")
    print(f"  models per pair: {len(PREREG['models']) - 1}")
    print(f"  conditional tests: both directions, neither privileged")
    print(f"  multicollinearity: VIF>10 or |r|>0.90 -> UNINTERPRETABLE, not null")
    print("  NO RESULTS IN THIS COMMIT")


if __name__ == "__main__":
    main()
