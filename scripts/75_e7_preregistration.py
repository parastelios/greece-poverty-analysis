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

    # AMENDMENT 1: every pair named explicitly, before any result is visible.
    # "The pre-registered primaries and their counterparts" was not explicit
    # enough: it left open whether wage duration -- a SUPPORTED E4 result --
    # was in or out, which could have been settled after seeing the numbers.
    "pairs": [
        {"id": "P1_ltu", "construct": "C2",
         "current": "ltu_rate", "accumulated": "acc_cum_excess_unemployment",
         "sample": "27 countries"},
        {"id": "P2_wage_area", "construct": "C3",
         "current": "real_wages_idx", "accumulated": "acc_real_wages_shortfall",
         "sample": "27 countries"},
        {"id": "P3_wage_duration", "construct": "C3",
         "current": "real_wages_idx", "accumulated": "dur_real_wages_below",
         "sample": "27 countries",
         "note": "the SUPPORTED E4 duration result; explicitly included"},
        {"id": "P4_gdp", "construct": "C3",
         "current": "pct_below_peak", "accumulated": "acc_pct_below_peak",
         "sample": "27 countries"},
        {"id": "P5_threshold", "construct": "C3",
         "current": "arop_threshold_real", "accumulated": "acc_threshold_shortfall",
         "sample": "26 countries, UNIFORM 2008 baseline (Croatia excluded)"},
        {"id": "P6_wadj", "construct": "C4",
         "current": "wadj_a01", "accumulated": "acc_wadj_excess",
         "sample": "27 countries"},
        {"id": "P7_hicp", "construct": "C5",
         "current": "hicp", "accumulated": "acc_hicp_compounded",
         "sample": "27 countries"},
        {"id": "P8_housing", "construct": "C6",
         "current": "housing_cost_overburden", "accumulated": "acc_housing_excess",
         "sample": "27 countries"},
    ],
    "pairs_note": ("Eight pairs, frozen. C1 has no feasible accumulated form "
                   "(E4 feasibility audit) and is therefore absent. No pair may "
                   "be added or dropped after results are visible."),

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
        "thresholds": {"focal_vif": 10.0, "abs_correlation": 0.90},
        "vif_definition": (
            "VIF of the TWO FOCAL PREDICTORS ONLY -- <current> and "
            "<accumulated> -- computed in the joint design. NOT the maximum "
            "over the year dummies, which are collinear by construction and "
            "would trip the rule on every pair."),
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
        # AMENDMENT 3: the published 0.70 SD MDE does NOT transfer. Power for a
        # conditional coefficient depends on the correlation between the two
        # focal predictors: the more collinear the pair, the less independent
        # variation is left and the larger the detectable effect becomes.
        "failure_labels": (
            "Labels come from e_rule, but the threshold does NOT. A "
            "PAIR-SPECIFIC CONDITIONAL MDE is computed for every pair BEFORE "
            "any outcome model is fitted, by the same simulation method as the "
            "published family MDE. A failed conditional test may be called "
            "UNSUPPORTED WITH ADEQUATE POWER only against its own pair's "
            "conditional MDE. Where no conditional MDE is available, every "
            "failure is INCONCLUSIVE and no adequate-power claim may be made."),
    },

    # AMENDMENT 4: executable formulas. Without them E7 could reuse E4's
    # SEPARATE-model decomposition, which would not establish a CONDITIONAL
    # dynamic result.
    "restrictions_retained": [
        "Mundlak, CONDITIONAL: subjective_poverty ~ arop + C(time) + <current> "
        "+ acc_between + acc_within, where acc_between is the country mean of "
        "<accumulated> and acc_within its deviation from that mean. The "
        "current measure is CONTROLLED, which is what makes it conditional.",
        "First differences, CONDITIONAL: d_hardship ~ d_current + d_accumulated "
        "+ d_arop + C(time). E4's separate-model first differences do NOT "
        "satisfy this requirement.",
        "FIRST DIFFERENCES required before any dynamic wording. E4 found none "
        "supported; nothing in E7 may relax that.",
        "Current and accumulated are DIFFERENT ESTIMANDS. A pair where the "
        "accumulated measure survives conditionally does not show that history "
        "matters more than standing.",
    ],

    # AMENDMENT 2: the conditional coefficients ARE a new multiplicity family.
    # Saying "E7 cannot create findings" does not solve this, because
    # "accumulation adds information beyond current conditions" is itself a new
    # incremental claim, and the earlier corrections do not cover coefficients
    # from joint models that did not exist when they were computed.
    "multiplicity": {
        "family": ("BH FAMILY 4: all E7 conditional coefficients, both "
                   "directions, across all eight pairs. One conservative "
                   "family, corrected together."),
        "size": 16,
        "why_a_new_family": (
            "The joint-model coefficients did not exist when BH families 1 and "
            "2 were computed, and 'adds information beyond current conditions' "
            "is a new incremental claim rather than a restatement of E1 or E4."),
        "ceiling": (
            "E7 may still only QUALIFY or WITHDRAW. A conditional coefficient "
            "cannot create support for a construct that E1 and E4 did not "
            "already support -- the BH family governs what E7 may call "
            "conditionally supported among results that already stood."),
    },

    "frozen_protection": (
        "Nothing in E7 may alter p5f-frozen, P3, P5, P3a, or any E1-E6 result."),
}


def main():
    path = PROC / "e7_preregistration.json"
    path.write_text(json.dumps(PREREG, indent=2) + "\n")
    print(f"wrote {path.name}")
    print(f"  pairs frozen: {len(PREREG['pairs'])}")
    for pr in PREREG["pairs"]:
        print(f"    {pr['id']:18} {pr['construct']:3} {pr['current']:24} "
              f"<-> {pr['accumulated']:28} {pr['sample']}")
    print(f"  models per pair: {len(PREREG['models']) - 1}")
    print(f"  BH family 4: {PREREG['multiplicity']['size']} conditional coefficients")
    print(f"  conditional tests: both directions, neither privileged")
    print(f"  multicollinearity: VIF>10 or |r|>0.90 -> UNINTERPRETABLE, not null")
    print("  NO RESULTS IN THIS COMMIT")


if __name__ == "__main__":
    main()
