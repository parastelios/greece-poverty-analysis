"""Freeze the EA pre-registration: the deprivation-free companion audit.

NO RESULTS IN THIS SCRIPT. It writes the specification and the decision rule,
nothing else. The companion model is not estimated here and must not be
estimated before this file is committed.

Motivation is a documented classification inconsistency, not a result. Frozen P3
excludes the closest Tier-0 indicators but retains severe_mat_soc_deprivation,
which E0 later classified `proximate_same_instrument`, role
`proximate_diagnostic`, construct P1 -- the construct the E pre-registration
reserves as diagnostic-only and never headline.

Freezing P3 protects its specification, numbers and interpretation from post hoc
alteration. It does not oblige us to keep calling it "objective-only" once one
predictor is known to violate the later proximity rule.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"

P3_PREDICTORS = [
    "severe_mat_soc_deprivation", "housing_cost_overburden", "ltu_rate",
    "aic_pps_pc_k", "wage_years_below_2008", "cum_excess_unemployment",
]
REMOVED = "severe_mat_soc_deprivation"

PREREG = {
    "status": "PRE-REGISTERED. No EA result exists at this commit.",
    "stage": "EA",
    "motivated_by": (
        "A classification inconsistency documented in the V2 research record: "
        "P3 retains a predictor E0 classifies proximate_same_instrument, role "
        "proximate_diagnostic, construct P1. Not motivated by any result."
    ),

    "two_roles": {
        "frozen_p3": {
            "role": "audited historical benchmark, unchanged",
            "old_label": "objective-only model",
            "new_label": "frozen P3 mixed-distance model",
            "descriptive_statement": (
                "Excludes the closest Tier-0 indicators but retains official "
                "severe material and social deprivation, drawn from the same "
                "survey system as the outcome."
            ),
            "protected": (
                "Specification, numbers and interpretation are frozen. EA may "
                "change which specification carries the headline and how the "
                "pair must be described. It may not alter any P3 value."
            ),
        },
        "companion": {
            "role": "deprivation-free companion specification",
            "predictors": [p for p in P3_PREDICTORS if p != REMOVED],
            "removed": REMOVED,
            "sample": "identical to frozen P3 (2015-2024, n=269)",
            "fixed_effects": "year, identical to frozen P3",
            "substitutions_permitted": False,
            "further_searching_permitted": False,
            "note": (
                "Exactly one model. Nothing is substituted for the removed "
                "predictor and no alternative companion may be estimated."
            ),
        },
    },

    "comparisons_required": [
        "identical observations, verified by row count and index",
        "Greece residual and rank",
        "accumulated-unemployment coefficient",
        "wild-cluster inference",
        "leave-one-country-out stability",
        "variance inflation factors",
        "within/between decomposition, only if the companion becomes headline",
    ],

    "decision_rule": {
        "implemented_by": "scripts/ea_rule.py, tested by scripts/test_ea_rule.py",
        "prose_is_not_the_rule": (
            "The function is the pre-registration. Prose alone already failed "
            "once on this project: the first P3 run reported the strongest "
            "branch through a default else."
        ),
        "outcomes": {
            "A": (
                "Companion still materially narrows Greece's residual and "
                "passes the existing stability criteria -> it becomes the "
                "cleaner headline specification."
            ),
            "B": (
                "Performance weakens moderately -> report material support "
                "with an explicit range across proximity choices."
            ),
            "C": (
                "Performance weakens sharply, or stability fails -> state that "
                "the frozen P3 result depends materially on an official but "
                "same-instrument deprivation measure."
            ),
        },
        "bands": {
            "measured_as": "companion |residual| minus frozen P3 |residual|, points",
            "A_max_degradation": 3.0,
            "B_max_degradation": 8.0,
            "anchoring": (
                "Expressed against the 20.12-point narrowing accumulation "
                "delivers (27.05 -> 6.93): 3.0 points is ~15% of it, 8.0 "
                "points ~40%. Chosen so 'moderate' and 'sharp' mean something "
                "on this problem rather than in the abstract."
            ),
        },
        "hard_gates_forcing_C": [
            "accumulated-unemployment coefficient not positive",
            "wild-cluster bootstrap does not support the coefficient",
            "coefficient not leave-one-country-out sign-stable",
            "maximum VIF above 10.0",
            "Greece's rank deteriorates (a lower rank number is more under-predicted)",
        ],
        "anti_selection_rule": (
            "Never choose between the two specifications because one produces "
            "the smaller residual. Outcome A is earned by proximity "
            "cleanliness plus stability. A companion residual smaller than "
            "frozen P3's is recorded and never rewarded: dropping a predictor "
            "cannot improve out-of-sample standing for a reason this design "
            "can attribute. BOTH specifications are reported under every "
            "outcome, including A."
        ),
    },

    "no_new_mde": (
        "EA is a comparison of two specifications on identical observations, "
        "not a new significance test, so the E MDE is not re-derived. The "
        "within/between evidence, if the companion becomes headline, inherits "
        "the published power floor of 0.70 SD = 9.29 points and its labelling "
        "rule."
    ),

    "baselines_elsewhere": (
        "E1 and E4 continue to use the neutral baseline AROP + year effects, "
        "NOT P3. P3 returns only at E6, as the frozen combined benchmark "
        "reported alongside the deprivation-free companion."
    ),

    "two_layer_reporting": (
        "AROPE's deprivation component is analytically relevant, but evidence "
        "that deprivation predicts another self-reported hardship measure is "
        "not equivalent to evidence from income, employment, wage or housing "
        "data. The final report shows both layers rather than forcing them "
        "under one 'objective' label."
    ),

    "frozen_protection": (
        "Nothing in EA may alter p5f-frozen, P3, P5 or P3a values."
    ),
}


def main():
    path = OUT / "ea_preregistration.json"
    path.write_text(json.dumps(PREREG, indent=2) + "\n")
    print(f"wrote {path.name}")
    print(f"  companion predictors: {len(PREREG['two_roles']['companion']['predictors'])}")
    print(f"  removed: {REMOVED}")
    print("  NO RESULTS IN THIS COMMIT")


if __name__ == "__main__":
    main()
