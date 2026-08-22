"""The EA proximity-audit decision rule, as a function that can be tested.

Motivated by a documented classification inconsistency, not by a result. Frozen
P3 excludes the closest Tier-0 indicators but retains severe_mat_soc_deprivation,
which E0 later classified `proximate_same_instrument`, role
`proximate_diagnostic`, construct P1 -- the construct the E pre-registration
reserves as diagnostic-only and never headline.

EA compares frozen P3 against ONE pre-specified companion: the same sample, the
same year effects, the same five remaining predictors, with
severe_mat_soc_deprivation removed. No substitutions. No further searching.

Nothing here alters p5f-frozen. Frozen P3's numbers and interpretation stand as
an audited historical result; what EA can change is which specification carries
the headline, and how the pair must be described.

The three outcomes, from the pre-registered rule:

  A  companion still materially narrows the residual and passes stability
     -> the companion becomes the cleaner headline specification
  B  performance weakens moderately
     -> report material support with an explicit range across proximity choices
  C  performance weakens sharply, or stability fails
     -> state that the frozen P3 result depends materially on an official but
        same-instrument deprivation measure

THE ANTI-SELECTION RULE. Outcome A is earned by proximity cleanliness plus
stability, never by producing the smaller residual. A companion residual SMALLER
than frozen P3's does not upgrade anything and is not evidence the companion is
better: dropping a predictor cannot improve out-of-sample standing for a reason
this design can attribute. Both specifications are reported in every outcome.

As with branch_rule, there is deliberately NO default branch, and no path
returns A except the one satisfying every one of its conditions.
"""

# Frozen P3 anchors. Read from p5f_frozen_result.json by the caller; repeated
# here as constants so the thresholds below are legible next to what they mean.
P3_RESIDUAL = 6.93          # frozen Greece out-of-sample residual, points
P3_RANK = 3                 # frozen rank, 1 = most under-predicted
P3_NARROWING = 20.12        # 27.05 -> 6.93, the narrowing accumulation delivers

# Degradation bands, in points of Greece residual relative to frozen P3.
# Anchored to the narrowing accumulation actually delivers, so that "moderate"
# and "sharp" mean something on this problem rather than in the abstract:
#   3.0 points ~= 15% of the 20.12-point narrowing  (>=85% retained)
#   8.0 points ~= 40% of the 20.12-point narrowing  (>=60% retained)
BAND_A_MAX_DEGRADATION = 3.0
BAND_B_MAX_DEGRADATION = 8.0

# A predictor's variance inflation above this is treated as a stability failure.
VIF_CEILING = 10.0

OUTCOMES = {
    "A": "companion is the cleaner headline specification",
    "B": "material support, reported as a range across proximity choices",
    "C": "frozen P3 depends materially on a same-instrument deprivation measure",
}


def decide(
    companion_residual,
    companion_rank,
    n_countries,
    cum_coef_positive,
    bootstrap_supports,
    loo_sign_stable,
    max_vif,
    p3_residual=P3_RESIDUAL,
    p3_rank=P3_RANK,
):
    """Return (outcome, degradation, notes).

    outcome     one of "A", "B", "C"
    degradation companion residual minus frozen P3 residual, in points.
                Positive means the companion is worse. Negative means smaller,
                which by the anti-selection rule is NOT an upgrade.
    notes       list of strings recording every condition that fired
    """
    if not isinstance(companion_rank, int):
        raise TypeError(f"rank must be int, got {type(companion_rank).__name__}")
    if companion_rank < 1 or companion_rank > n_countries:
        raise ValueError(f"rank {companion_rank} outside 1..{n_countries}")
    if max_vif is not None and max_vif < 1.0:
        raise ValueError(f"VIF {max_vif} below 1.0 is not possible")

    notes = []
    degradation = abs(companion_residual) - abs(p3_residual)

    # Stability gates. Any failure forces C regardless of the residual, which is
    # the point: a specification that narrows the residual while flipping sign
    # under leave-one-out is not a cleaner headline, it is a less stable one.
    stability_failed = False
    if not cum_coef_positive:
        notes.append("accumulated-unemployment coefficient is not positive")
        stability_failed = True
    if not bootstrap_supports:
        notes.append("wild-cluster bootstrap does not support the coefficient")
        stability_failed = True
    if not loo_sign_stable:
        notes.append("coefficient is not leave-one-country-out sign-stable")
        stability_failed = True
    if max_vif is not None and max_vif > VIF_CEILING:
        notes.append(f"max VIF {max_vif:.1f} exceeds ceiling {VIF_CEILING}")
        stability_failed = True

    if stability_failed:
        notes.append("stability failure forces outcome C")
        return "C", degradation, notes

    # Rank may not deteriorate. Lower rank number = more under-predicted = worse.
    if companion_rank < p3_rank:
        notes.append(
            f"rank deteriorates from {p3_rank} to {companion_rank} "
            "(lower is more under-predicted)"
        )
        return "C", degradation, notes

    if degradation < 0:
        # Smaller residual than frozen P3. Recorded, never rewarded.
        notes.append(
            f"companion residual is {abs(degradation):.2f} points SMALLER than "
            "frozen P3; per the anti-selection rule this is not an upgrade and "
            "both specifications are still reported"
        )

    if degradation <= BAND_A_MAX_DEGRADATION:
        notes.append(
            f"degradation {degradation:+.2f} within band A "
            f"(<= {BAND_A_MAX_DEGRADATION} points)"
        )
        return "A", degradation, notes

    if degradation <= BAND_B_MAX_DEGRADATION:
        notes.append(
            f"degradation {degradation:+.2f} within band B "
            f"(<= {BAND_B_MAX_DEGRADATION} points); report the range "
            f"[{abs(p3_residual):.2f}, {abs(companion_residual):.2f}]"
        )
        return "B", degradation, notes

    notes.append(
        f"degradation {degradation:+.2f} exceeds {BAND_B_MAX_DEGRADATION} points"
    )
    return "C", degradation, notes


def retained_narrowing(companion_residual, no_accumulation_residual):
    """Share of the accumulation narrowing the companion retains, 0-1.

    Reported alongside the outcome so the bands can be read in proportional
    terms as well as in points. Not itself a decision input.
    """
    span = abs(no_accumulation_residual) - abs(companion_residual)
    if abs(no_accumulation_residual) <= 0:
        raise ValueError("no-accumulation residual must be non-zero")
    return span / abs(no_accumulation_residual)
