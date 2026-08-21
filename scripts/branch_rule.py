"""The P3 conclusion-branch rule, as a function that can be tested.

Prose pre-registration was not enough. The first P3 run reported "STRONG
OBJECTIVE SUPPORT" while Greece sat at rank 3, because an if/else chain ended in
a default `else` that returned the strongest conclusion. The pre-commitment was
correct; the implementation defeated it.

The rule, from docs/project_description_v3.md §5:

  1  residual <= 10 AND Greece leaves the extreme-outlier group
  2  residual 10-20 with stable improvement
  3  residual > 20, or unstable cumulative coefficient
  4  no robust improvement

There is deliberately NO default branch, and no path returns branch 1 except the
one that satisfies both of its conditions.
"""
EXTREME_RANK = 3      # "the extreme-outlier group"
BAR_STRONG = 10.0
BAR_PARTIAL = 20.0

BRANCHES = {
    1: "STRONG OBJECTIVE SUPPORT",
    2: "material history explains a meaningful share, not the full difference",
    3: "accumulated exposure is CONDITIONAL support; paradox NOT resolved",
    4: "no robust improvement; lead with measurement and descriptive scarring",
}


def decide(residual, rank, n_countries, sign_stable, improves_baseline=True):
    """Return (branch_number, criteria_disagree). Conservative on disagreement."""
    if not isinstance(rank, int) or rank < 1 or rank > n_countries:
        raise ValueError(f"rank {rank} outside 1..{n_countries}")
    if not improves_baseline:
        return 4, False
    if not sign_stable or abs(residual) > BAR_PARTIAL:
        return 3, False
    extreme = rank <= EXTREME_RANK
    clears_bar = abs(residual) <= BAR_STRONG
    if clears_bar and not extreme:
        return 1, False
    if clears_bar and extreme:
        # Both conditions are required for branch 1. Residual passes, rank does
        # not: take the more conservative branch and report the disagreement.
        return 2, True
    return 2, False
