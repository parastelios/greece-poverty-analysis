"""P5 interpretation rules, committed before P5 was run.

TERMINOLOGY: the comparison of the within and between coefficients is a
WITHIN-BETWEEN EQUALITY TEST -- a linear hypothesis on the Mundlak coefficients
with country-clustered errors. It is deliberately not called a Hausman test,
which would require a covariance structure this does not implement. And failing
to reject equality is not evidence of equality.

Same discipline as branch_rule.py, for the same reason: the P3 branch bug showed
that a rule written only in prose can be defeated by its implementation.

WHAT P5 CAN AND CANNOT DO
-------------------------
Country-FE and Mundlak models cannot reproduce the leave-Greece-out residual --
country fixed effects absorb exactly the Greek intercept that prediction needs.
They therefore CANNOT independently assign a P3 branch. They audit the
INTERPRETATION of the accumulation coefficient. Branch 2 remains the headline
classification from the frozen objective-only prediction model unless P5 reveals
enough instability to downgrade it, which is a separate decision recorded in
`downgrade_warranted()`.

MUNDLAK OUTCOMES
----------------
A  within and between both supported : accumulated exposure distinguishes
   countries AND tracks deterioration within countries
B  between only : a cross-country scarring marker; do NOT claim that additional
   exposure raises hardship within a country
C  within only : accumulating exposure tracks internal change, but Greece's
   cross-country position requires another explanation
D  neither, or unstable : downgrade the P3 accumulation claim
"""
ALPHA = 0.05

OUTCOMES = {
    "A": ("within and between both supported: accumulated exposure distinguishes "
          "countries and tracks deterioration within them"),
    "B": ("between only: a cross-country scarring marker; do not claim that "
          "additional exposure raises hardship within a country"),
    "C": ("within only: accumulating exposure tracks internal change, but Greece's "
          "cross-country position requires another explanation"),
    "D": "neither supported, or unstable: downgrade the P3 accumulation claim",
}


def _supported(coef, p):
    return coef > 0 and p < ALPHA


def classify(within_coef, within_p, between_coef, between_p, stable=True):
    """Return (outcome_key, explanation). Instability forces D regardless."""
    if not stable:
        return "D", OUTCOMES["D"]
    w = _supported(within_coef, within_p)
    b = _supported(between_coef, between_p)
    if w and b:
        return "A", OUTCOMES["A"]
    if b and not w:
        return "B", OUTCOMES["B"]
    if w and not b:
        return "C", OUTCOMES["C"]
    return "D", OUTCOMES["D"]


# ---------------------------------------------------------------- instability ----
# Predefined. Any ONE of these makes the coefficient unstable.
MAX_LOO_CHANGE_PCT = 50.0
MAX_GREECE_CHANGE_PCT = 50.0
MIN_LEVERAGE_COUNTRIES = 3       # crisis countries holding most of the leverage


def instability_flags(sign_reversed, max_loo_change_pct, greece_change_pct,
                      bootstrap_consistent, leverage_concentrated):
    """Return the list of triggered instability criteria (empty means stable)."""
    f = []
    if sign_reversed:
        f.append("sign reversal in a leave-one-country-out fold")
    if max_loo_change_pct > MAX_LOO_CHANGE_PCT:
        f.append(f"a single omitted country moves the estimate by "
                 f"{max_loo_change_pct:.0f}% (bar {MAX_LOO_CHANGE_PCT:.0f}%)")
    if abs(greece_change_pct) > MAX_GREECE_CHANGE_PCT:
        f.append(f"Greece alone moves the estimate by {greece_change_pct:+.0f}% "
                 f"-- Greece drives the coefficient")
    if not bootstrap_consistent:
        f.append("conclusion depends on one bootstrap weight distribution or seed")
    if leverage_concentrated:
        f.append(f"leverage concentrated in fewer than {MIN_LEVERAGE_COUNTRIES} "
                 f"crisis countries")
    return f


def downgrade_warranted(flags):
    """P5 may downgrade P3's branch only on demonstrated instability, never on
    a Mundlak outcome alone. B or C narrow the CLAIM; they do not move the branch."""
    return len(flags) > 0
