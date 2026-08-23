"""The Family E decision rule, as a function that can be tested.

Implements the six conditions frozen in data/processed/e_preregistration.json
(`decision_rule_all_must_hold`) plus the pre-registered power labelling: a null
whose effect size sits below available power is INCONCLUSIVE, not unsupported.

  1  direction matches the pre-registration
  2  FDR-adjusted result survives within its declared family
  3  wild-cluster bootstrap supports it
  4  coefficient is leave-one-country-out stable in sign
  5  Greece's EQUAL-SAMPLE absolute residual improves
  6  no proximity or construction-overlap rule is violated

ALL must hold for `supported`. There is deliberately no default branch.

WHY THE FAILURE LABELS ARE NOT ALL "UNSUPPORTED". With MDE = 0.70 residual SD,
this design cannot distinguish "no effect" from "an effect smaller than 0.70
SD". Calling every null unsupported would claim a precision the panel does not
have. So a null is only `unsupported_with_adequate_power` when the confidence
interval EXCLUDES effects of MDE size -- that is, when we could have seen one
and did not. Otherwise it is `inconclusive_under_available_power`.

A wrong-signed result that clears FDR is neither. It contradicts the
pre-registered direction and gets its own label rather than being filed as a
quiet null, which is how contradictory evidence disappears.

Written and tested BEFORE any E1 result was computed. The EA rule was too, and
still failed on a case its author had not imagined -- so the tests here
deliberately include sign reversals, wrong-signed significance, and boundary
values on every gate.
"""

MDE_SD = 0.70          # published floor: 0.70 residual SD = 9.29 points
FDR_ALPHA = 0.05
BOOTSTRAP_ALPHA = 0.05

OUTCOMES = {
    "supported": "all six pre-registered conditions hold",
    "contradicts_direction": "clears FDR with the sign opposite to pre-registration",
    "unsupported_with_adequate_power": "null, and an MDE-sized effect is excluded",
    "inconclusive_under_available_power": "null, but an MDE-sized effect is not excluded",
    "blocked_by_proximity": "violates a proximity or construction-overlap rule",
}


def benjamini_hochberg(pvalues, alpha=FDR_ALPHA):
    """Return (adjusted_pvalues, rejected) in the input order."""
    n = len(pvalues)
    if n == 0:
        return [], []
    order = sorted(range(n), key=lambda i: pvalues[i])
    adj = [0.0] * n
    running = 1.0
    # step-up, enforcing monotonicity from the largest p downward
    for rank, i in reversed(list(enumerate(order, start=1))):
        running = min(running, pvalues[i] * n / rank)
        adj[i] = running
    return adj, [adj[i] <= alpha for i in range(n)]


def direction_ok(coefficient, adverse):
    """Does the coefficient point the way the pre-registration says it must?

    `adverse` is the variable's adverse direction: "higher_is_worse" means more
    of it should predict MORE hardship, so a positive coefficient. Anything
    else raises rather than silently guessing.
    """
    if adverse == "higher_is_worse":
        return coefficient > 0
    if adverse == "lower_is_worse":
        return coefficient < 0
    raise ValueError(f"unknown adverse direction {adverse!r}")


def decide(
    coefficient,
    adverse,
    fdr_rejected,
    bootstrap_p,
    loo_sign_stable,
    greece_residual_improves,
    proximity_violation,
    ci_abs_std_upper,
    mde_sd=MDE_SD,
):
    """Return (outcome, notes).

    ci_abs_std_upper  the larger absolute standardized effect the confidence
                      interval admits, in residual-SD units. Used only to
                      separate the two null labels.
    """
    if adverse not in ("higher_is_worse", "lower_is_worse"):
        raise ValueError(f"unknown adverse direction {adverse!r}")
    if ci_abs_std_upper is not None and ci_abs_std_upper < 0:
        raise ValueError("ci_abs_std_upper must be non-negative")

    notes = []

    # Gate 6 first: a proximity violation disqualifies regardless of fit, and
    # must never be reported as a null (which would imply it was eligible).
    if proximity_violation:
        notes.append("proximity or construction-overlap rule violated")
        return "blocked_by_proximity", notes

    correct_sign = direction_ok(coefficient, adverse)
    if not correct_sign:
        notes.append(f"coefficient {coefficient:+.4f} contradicts "
                     f"pre-registered direction ({adverse})")

    if fdr_rejected and not correct_sign:
        notes.append("clears FDR with the wrong sign: recorded as a "
                     "contradiction, not filed as a null")
        return "contradicts_direction", notes

    if fdr_rejected and correct_sign:
        if bootstrap_p is None:
            notes.append("bootstrap required for anything described as supported")
            return "inconclusive_under_available_power", notes
        if bootstrap_p > BOOTSTRAP_ALPHA:
            notes.append(f"wild-cluster bootstrap p={bootstrap_p:.4f} does not support")
        elif not loo_sign_stable:
            notes.append("coefficient is not leave-one-country-out sign-stable")
        elif not greece_residual_improves:
            notes.append("Greece's equal-sample absolute residual does not improve")
        else:
            notes.append("all six conditions hold")
            return "supported", notes
        # cleared FDR but failed a robustness gate: not supported, and not a
        # null either -- report as inconclusive so the failure stays visible
        notes.append("cleared FDR but failed a robustness gate")
        return "inconclusive_under_available_power", notes

    # Did not clear FDR.
    notes.append("does not survive FDR within its declared family")
    if ci_abs_std_upper is not None and ci_abs_std_upper < mde_sd:
        notes.append(f"interval excludes effects of {mde_sd} SD "
                     f"(largest admitted {ci_abs_std_upper:.2f} SD)")
        return "unsupported_with_adequate_power", notes
    admitted = ("unknown" if ci_abs_std_upper is None
                else f"{ci_abs_std_upper:.2f} SD")
    notes.append(f"interval still admits an effect of {mde_sd} SD "
                 f"(largest admitted {admitted}); power is the binding "
                 "constraint, not evidence of absence")
    return "inconclusive_under_available_power", notes
