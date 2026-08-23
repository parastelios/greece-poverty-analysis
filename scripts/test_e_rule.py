"""Tests for the Family E decision rule. Run: python test_e_rule.py"""
from e_rule import (decide, direction_ok, benjamini_hochberg, MDE_SD,
                    FDR_ALPHA, OUTCOMES)

F = []
def check(name, got, want):
    ok = got == want
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:58} got {got} want {want}")

def gate(**kw):
    base = dict(coefficient=1.0, adverse="higher_is_worse", fdr_rejected=True,
                bootstrap_p=0.01, loo_sign_stable=True,
                greece_residual_improves=True, proximity_violation=False,
                ci_abs_std_upper=0.9)
    base.update(kw)
    return decide(**base)[2]

def out(**kw):
    base = dict(coefficient=1.0, adverse="higher_is_worse", fdr_rejected=True,
                bootstrap_p=0.01, loo_sign_stable=True,
                greece_residual_improves=True, proximity_violation=False,
                ci_abs_std_upper=0.9)
    base.update(kw)
    return decide(**base)[0]

print("all six conditions hold")
check("clean pass -> supported", out(), "supported")
check("lower_is_worse with negative coef", out(coefficient=-1.0,
      adverse="lower_is_worse"), "supported")

print("\neach gate independently blocks 'supported'")
check("bootstrap fails",       out(bootstrap_p=0.06), "inconclusive_under_available_power")
check("LOO sign flips",        out(loo_sign_stable=False), "inconclusive_under_available_power")
check("Greece residual worse", out(greece_residual_improves=False), "inconclusive_under_available_power")
check("no bootstrap run",      out(bootstrap_p=None), "inconclusive_under_available_power")
check("proximity violation",   out(proximity_violation=True), "blocked_by_proximity")

print("\nproximity is checked FIRST and is not reportable as a null")
check("proximity beats a clean pass", out(proximity_violation=True), "blocked_by_proximity")
check("proximity beats a null",  out(proximity_violation=True, fdr_rejected=False,
      ci_abs_std_upper=0.1), "blocked_by_proximity")
check("proximity beats wrong sign", out(proximity_violation=True,
      coefficient=-1.0), "blocked_by_proximity")

print("\nWRONG SIGN is a contradiction, never a quiet null")
check("wrong sign + FDR -> contradiction", out(coefficient=-1.0), "contradicts_direction")
check("wrong sign, lower_is_worse",        out(coefficient=1.0,
      adverse="lower_is_worse"), "contradicts_direction")
check("wrong sign without FDR is just a null",
      out(coefficient=-1.0, fdr_rejected=False, ci_abs_std_upper=0.9),
      "inconclusive_under_available_power")
check("wrong sign + FDR beats every robustness gate",
      out(coefficient=-1.0, bootstrap_p=0.9, loo_sign_stable=False,
          greece_residual_improves=False), "contradicts_direction")
_, notes, _ = decide(coefficient=-1.0, adverse="higher_is_worse", fdr_rejected=True,
                  bootstrap_p=0.01, loo_sign_stable=True,
                  greece_residual_improves=True, proximity_violation=False,
                  ci_abs_std_upper=0.9)
check("contradiction is explained in the notes",
      any("contradict" in n for n in notes), True)

print("\nthe two NULL labels turn on whether an MDE-sized effect is excluded")
n = dict(fdr_rejected=False)
check(f"interval admits {MDE_SD} SD -> inconclusive",
      out(ci_abs_std_upper=0.71, **n), "inconclusive_under_available_power")
check(f"interval excludes {MDE_SD} SD -> unsupported",
      out(ci_abs_std_upper=0.69, **n), "unsupported_with_adequate_power")
check("exactly at the MDE -> inconclusive (not excluded)",
      out(ci_abs_std_upper=0.70, **n), "inconclusive_under_available_power")
check("wide interval -> inconclusive", out(ci_abs_std_upper=3.0, **n),
      "inconclusive_under_available_power")
check("tiny interval -> unsupported",  out(ci_abs_std_upper=0.05, **n),
      "unsupported_with_adequate_power")
check("unknown interval -> inconclusive, never unsupported",
      out(ci_abs_std_upper=None, **n), "inconclusive_under_available_power")

print("\ndirection_ok")
check("higher_is_worse, positive", direction_ok(0.5, "higher_is_worse"), True)
check("higher_is_worse, negative", direction_ok(-0.5, "higher_is_worse"), False)
check("lower_is_worse, negative",  direction_ok(-0.5, "lower_is_worse"), True)
check("zero is not the adverse direction", direction_ok(0.0, "higher_is_worse"), False)
for bad in ["higher", "", None, "worse"]:
    try:
        direction_ok(1.0, bad)
        check(f"rejects adverse={bad!r}", "no error", "ValueError")
    except ValueError:
        check(f"rejects adverse={bad!r}", "ValueError", "ValueError")

print("\ninput validation")
try:
    decide(1.0, "higher_is_worse", False, 0.01, True, True, False, -0.5)
    check("rejects negative CI bound", "no error", "ValueError")
except ValueError:
    check("rejects negative CI bound", "ValueError", "ValueError")

print("\nBenjamini-Hochberg")
adj, rej = benjamini_hochberg([0.001, 0.02, 0.30, 0.70])
check("smallest p survives", rej[0], True)
check("largest p does not",  rej[3], False)
check("adjusted p are monotone in the original order",
      all(adj[i] <= adj[j] for i, j in [(0, 1), (1, 2), (2, 3)]), True)
check("adjusted >= raw", all(a >= p for a, p in zip(adj, [0.001, 0.02, 0.30, 0.70])), True)
adj2, rej2 = benjamini_hochberg([0.04, 0.04, 0.04, 0.04])
check("four equal p at .04 all survive", all(rej2), True)
adj3, rej3 = benjamini_hochberg([0.04])
check("single test: adjusted equals raw", round(adj3[0], 6), 0.04)
check("empty input", benjamini_hochberg([]), ([], []))
adj4, rej4 = benjamini_hochberg([0.06, 0.99])
check("nothing survives when all p are large", any(rej4), False)
check("BH is order-independent",
      benjamini_hochberg([0.30, 0.001, 0.70, 0.02])[1],
      [False, True, False, True])

print("\nevery documented outcome is reachable")
seen = {out(), out(coefficient=-1.0), out(proximity_violation=True),
        out(fdr_rejected=False, ci_abs_std_upper=0.1),
        out(fdr_rejected=False, ci_abs_std_upper=3.0)}
check("all 5 outcomes reachable", seen == set(OUTCOMES), True)

print("\nTHE SENSITIVITY RULE: a sensitivity never creates a finding")
from e_rule import sensitivity_disposition as sd, SENSITIVITY_DISPOSITIONS
check("supported primary + supported sensitivity",
      sd("supported", "supported"), "confirms_primary")
check("supported primary + inconclusive sensitivity",
      sd("supported", "inconclusive_under_available_power"), "qualifies_primary")
check("supported primary + contradicting sensitivity",
      sd("supported", "contradicts_direction"), "qualifies_primary")

# The case the rule exists for: primary failed, sensitivity looks great.
for primary in ["inconclusive_under_available_power",
                "unsupported_with_adequate_power", "contradicts_direction",
                "blocked_by_proximity"]:
    check(f"{primary[:28]:28} + SUPPORTED sensitivity -> cannot_promote",
          sd(primary, "supported"), "cannot_promote")

check("blocked sensitivity is blocked even under a supported primary",
      sd("supported", "blocked_by_proximity"), "blocked_by_proximity")
check("blocked sensitivity under a failed primary",
      sd("inconclusive_under_available_power", "blocked_by_proximity"),
      "blocked_by_proximity")
check("every disposition reachable",
      {sd("supported", "supported"), sd("supported", "contradicts_direction"),
       sd("contradicts_direction", "supported"),
       sd("supported", "blocked_by_proximity")} == set(SENSITIVITY_DISPOSITIONS),
      True)
for bad_in in [("nonsense", "supported"), ("supported", "nonsense")]:
    try:
        sd(*bad_in)
        check(f"rejects {bad_in}", "no error", "ValueError")
    except ValueError:
        check(f"rejects {bad_in}", "ValueError", "ValueError")

print("\nFAILED GATE: the outcome alone does not say WHY")
from e_rule import FAILED_GATES
check("clean pass has no failed gate",  gate(), "")
check("bootstrap gate",                 gate(bootstrap_p=0.06), "bootstrap")
check("LOO gate",                       gate(loo_sign_stable=False), "loo_stability")
check("Greece-residual gate",           gate(greece_residual_improves=False), "greece_residual")
check("proximity gate",                 gate(proximity_violation=True), "proximity")
check("direction gate",                 gate(coefficient=-1.0), "direction")
check("power gate",                     gate(fdr_rejected=False, ci_abs_std_upper=3.0), "power")
check("fdr gate when MDE excluded",     gate(fdr_rejected=False, ci_abs_std_upper=0.1), "fdr")
check("missing bootstrap counts as the bootstrap gate",
      gate(bootstrap_p=None), "bootstrap")
check("every gate name is documented",
      all(g in FAILED_GATES for g in
          ["", "bootstrap", "loo_stability", "greece_residual", "proximity",
           "direction", "fdr", "power"]), True)

# The case that motivated the field: identical outcome, opposite situations.
near = decide(coefficient=1.0, adverse="higher_is_worse", fdr_rejected=True,
              bootstrap_p=0.002, loo_sign_stable=True,
              greece_residual_improves=False, proximity_violation=False,
              ci_abs_std_upper=0.9)
far = decide(coefficient=1.0, adverse="higher_is_worse", fdr_rejected=False,
             bootstrap_p=None, loo_sign_stable=False,
             greece_residual_improves=False, proximity_violation=False,
             ci_abs_std_upper=3.0)
check("both are the same pre-registered outcome", near[0] == far[0], True)
check("but the gates differ", (near[2], far[2]), ("greece_residual", "power"))

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} passed")
if bad:
    raise SystemExit("FAILED: " + ", ".join(bad))
