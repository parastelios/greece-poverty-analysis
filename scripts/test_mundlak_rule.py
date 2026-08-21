"""Tests for the P5 interpretation rules. Run: python test_mundlak_rule.py"""
from mundlak_rule import classify, instability_flags, downgrade_warranted, ALPHA

F = []
def check(name, got, want):
    ok = got == want
    F.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:56} {got if ok else f'got {got} want {want}'}")

print("all four Mundlak outcomes reachable")
check("A: both supported",        classify(0.2, 0.01, 0.3, 0.01)[0], "A")
check("B: between only",          classify(0.2, 0.40, 0.3, 0.01)[0], "B")
check("C: within only",           classify(0.2, 0.01, 0.3, 0.40)[0], "C")
check("D: neither",               classify(0.2, 0.40, 0.3, 0.40)[0], "D")
check("D: instability overrides both-supported",
      classify(0.2, 0.01, 0.3, 0.01, stable=False)[0], "D")

print("\nsign matters, not just significance")
check("negative within, sig -> not supported", classify(-0.2, 0.01, 0.3, 0.01)[0], "B")
check("negative between, sig -> not supported", classify(0.2, 0.01, -0.3, 0.01)[0], "C")
check("both negative and sig -> D",            classify(-0.2, 0.01, -0.3, 0.01)[0], "D")

print(f"\nalpha boundary (ALPHA={ALPHA})")
check("p just below alpha  -> supported", classify(0.2, 0.049, 0.3, 0.01)[0], "A")
check("p exactly alpha     -> NOT supported", classify(0.2, 0.05, 0.3, 0.01)[0], "B")
check("p just above alpha  -> NOT supported", classify(0.2, 0.051, 0.3, 0.01)[0], "B")

print("\ninstability criteria, each triggers independently")
base = dict(sign_reversed=False, max_loo_change_pct=10.0, greece_change_pct=5.0,
            bootstrap_consistent=True, leverage_concentrated=False)
check("stable baseline -> no flags", instability_flags(**base), [])
check("sign reversal",        len(instability_flags(**{**base, "sign_reversed": True})), 1)
check("LOO change 51%",       len(instability_flags(**{**base, "max_loo_change_pct": 51.0})), 1)
check("LOO change 50% (bar)", len(instability_flags(**{**base, "max_loo_change_pct": 50.0})), 0)
check("Greece moves it 60%",  len(instability_flags(**{**base, "greece_change_pct": 60.0})), 1)
check("Greece moves it -60%", len(instability_flags(**{**base, "greece_change_pct": -60.0})), 1)
check("bootstrap inconsistent", len(instability_flags(**{**base, "bootstrap_consistent": False})), 1)
check("leverage concentrated", len(instability_flags(**{**base, "leverage_concentrated": True})), 1)
check("multiple flags accumulate",
      len(instability_flags(sign_reversed=True, max_loo_change_pct=99.0,
                            greece_change_pct=80.0, bootstrap_consistent=False,
                            leverage_concentrated=True)), 5)

print("\ndowngrade requires demonstrated instability, never an outcome alone")
check("no flags -> no downgrade",      downgrade_warranted([]), False)
check("any flag -> downgrade",         downgrade_warranted(["x"]), True)
check("outcome B alone cannot downgrade",
      downgrade_warranted(instability_flags(**base)) is False
      and classify(0.2, 0.40, 0.3, 0.01)[0] == "B", True)

n = sum(1 for ok in F if not ok)
print(f"\n{len(F)-n}/{len(F)} passed")
raise SystemExit(1 if n else 0)
