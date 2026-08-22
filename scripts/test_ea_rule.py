"""Tests for the EA proximity-audit rule. Run: python test_ea_rule.py"""
from ea_rule import (
    decide, retained_narrowing, BAND_A_MAX_DEGRADATION, BAND_B_MAX_DEGRADATION,
    VIF_CEILING, P3_RESIDUAL, P3_RANK,
)

F = []
def check(name, got, want):
    ok = got == want
    F.append((name, ok, got, want))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:56} got {got} want {want}")

def outcome(*a, **k):
    return decide(*a, **k)[0]

# A clean companion: positive coefficient, bootstrap supports, LOO stable, VIF fine.
CLEAN = dict(cum_coef_positive=True, bootstrap_supports=True,
             loo_sign_stable=True, max_vif=4.0)

print("every outcome reachable")
check("A: residual holds, rank holds",      outcome(7.5, 3, 27, **CLEAN), "A")
check("B: moderate weakening",              outcome(12.0, 5, 27, **CLEAN), "B")
check("C: sharp weakening",                 outcome(20.0, 5, 27, **CLEAN), "C")
check("C: stability failure",               outcome(7.0, 3, 27,
      cum_coef_positive=True, bootstrap_supports=False,
      loo_sign_stable=True, max_vif=4.0), "C")

print("\ndegradation bands, measured from frozen P3 6.93")
check(f"degradation {BAND_A_MAX_DEGRADATION} exactly -> A",
      outcome(P3_RESIDUAL + 3.0, 3, 27, **CLEAN), "A")
check("degradation 3.01 -> B",              outcome(P3_RESIDUAL + 3.01, 3, 27, **CLEAN), "B")
check(f"degradation {BAND_B_MAX_DEGRADATION} exactly -> B",
      outcome(P3_RESIDUAL + 8.0, 3, 27, **CLEAN), "B")
check("degradation 8.01 -> C",              outcome(P3_RESIDUAL + 8.01, 3, 27, **CLEAN), "C")

print("\nrank may not deteriorate (lower rank number = more under-predicted)")
check("rank 3 -> 3, unchanged, A",          outcome(7.0, 3, 27, **CLEAN), "A")
check("rank 3 -> 4, improves, A",           outcome(7.0, 4, 27, **CLEAN), "A")
check("rank 3 -> 2, deteriorates, C",       outcome(7.0, 2, 27, **CLEAN), "C")
check("rank 3 -> 1, deteriorates, C",       outcome(7.0, 1, 27, **CLEAN), "C")
check("rank deterioration beats a tiny residual",
      outcome(0.1, 1, 27, **CLEAN), "C")

print("\nTHE ANTI-SELECTION RULE: a smaller residual is never an upgrade")
o, deg, notes = decide(2.0, 3, 27, **CLEAN)
check("smaller residual still only reaches A",  o, "A")
check("degradation is negative",                round(deg, 2), -4.93)
check("the smaller residual is recorded",
      any("SMALLER" in n for n in notes), True)
check("smaller residual cannot rescue a stability failure",
      outcome(0.5, 3, 27, cum_coef_positive=True, bootstrap_supports=True,
              loo_sign_stable=False, max_vif=4.0), "C")
check("smaller residual cannot rescue a rank drop",
      outcome(0.5, 1, 27, **CLEAN), "C")

print("\nstability gates, each one independently forces C")
check("coefficient not positive",           outcome(7.0, 3, 27,
      cum_coef_positive=False, bootstrap_supports=True,
      loo_sign_stable=True, max_vif=4.0), "C")
check("bootstrap does not support",         outcome(7.0, 3, 27,
      cum_coef_positive=True, bootstrap_supports=False,
      loo_sign_stable=True, max_vif=4.0), "C")
check("LOO sign flips",                     outcome(7.0, 3, 27,
      cum_coef_positive=True, bootstrap_supports=True,
      loo_sign_stable=False, max_vif=4.0), "C")
check(f"VIF above {VIF_CEILING}",           outcome(7.0, 3, 27,
      cum_coef_positive=True, bootstrap_supports=True,
      loo_sign_stable=True, max_vif=10.1), "C")
check(f"VIF exactly {VIF_CEILING} passes",  outcome(7.0, 3, 27,
      cum_coef_positive=True, bootstrap_supports=True,
      loo_sign_stable=True, max_vif=10.0), "A")
check("VIF None is skipped, not failed",    outcome(7.0, 3, 27,
      cum_coef_positive=True, bootstrap_supports=True,
      loo_sign_stable=True, max_vif=None), "A")

print("\nno silent default: every stability failure is explained")
for kw in [dict(cum_coef_positive=False), dict(bootstrap_supports=False),
           dict(loo_sign_stable=False), dict(max_vif=99.0)]:
    args = dict(CLEAN); args.update(kw)
    _, _, notes = decide(7.0, 3, 27, **args)
    check(f"note emitted for {list(kw)[0]}",
          any("forces outcome C" in n for n in notes), True)

print("\nSIGN REVERSAL is not narrowing (defect found on the live EA run)")
# The observed case: companion residual -9.39 at rank 25/27. Magnitude
# comparison alone scored this +2.46, inside band A, and the one-tailed rank
# gate read rank 25 as an improvement over rank 3.
check("the observed EA case -> C",           outcome(-9.39, 25, 27, **CLEAN), "C")
o, deg, notes = decide(-9.39, 25, 27, **CLEAN)
check("degradation still reported as +2.46", round(deg, 2), 2.46)
check("reversal is named in the notes",
      any("REVERSES SIGN" in n for n in notes), True)
check("reversal beats a band-A magnitude",   outcome(-7.0, 25, 27, **CLEAN), "C")
check("reversal near zero IS narrowing",     outcome(-2.0, 14, 27, **CLEAN), "A")
check("reversal at the 3.0 tolerance is narrowing",
      outcome(-3.0, 14, 27, **CLEAN), "A")
check("reversal just past tolerance -> C",   outcome(-3.01, 14, 27, **CLEAN), "C")
check("same-sign negatives compare on magnitude",
      decide(-7.5, 3, 27, p3_residual=-6.93, **CLEAN)[0], "A")

print("\nextremeness is TWO-TAILED: both ends of the ladder are extreme")
check("rank 25/27 is tail position 3, same as rank 3",
      outcome(7.5, 25, 27, **CLEAN), "A")
check("rank 26/27 is tail position 2, worse -> C",
      outcome(7.5, 26, 27, **CLEAN), "C")
check("rank 27/27 is tail position 1, worst -> C",
      outcome(7.5, 27, 27, **CLEAN), "C")
check("rank 14/27 is mid-ladder, best -> A",
      outcome(7.5, 14, 27, **CLEAN), "A")

print("\ninput validation")
for bad, exc in [((7.0, 0, 27), ValueError), ((7.0, 28, 27), ValueError),
                 ((7.0, 3.0, 27), TypeError)]:
    try:
        decide(*bad, **CLEAN)
        check(f"rejects {bad[1]!r} as rank", "no error", exc.__name__)
    except exc:
        check(f"rejects {bad[1]!r} as rank", exc.__name__, exc.__name__)
try:
    decide(7.0, 3, 27, cum_coef_positive=True, bootstrap_supports=True,
           loo_sign_stable=True, max_vif=0.5)
    check("rejects VIF below 1.0", "no error", "ValueError")
except ValueError:
    check("rejects VIF below 1.0", "ValueError", "ValueError")

print("\nretained_narrowing is reporting only, not a decision input")
check("6.93 from 27.05 retains 74%",
      round(retained_narrowing(6.93, 27.05), 4), 0.7438)
check("no narrowing retains 0",  round(retained_narrowing(27.05, 27.05), 4), 0.0)
try:
    retained_narrowing(6.93, 0.0)
    check("rejects zero baseline", "no error", "ValueError")
except ValueError:
    check("rejects zero baseline", "ValueError", "ValueError")

bad = [n for n, ok, *_ in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} passed")
if bad:
    raise SystemExit("FAILED: " + ", ".join(bad))
