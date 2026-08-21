"""Tests for the P3 branch rule. Run: python test_branch_rule.py"""
from branch_rule import decide, BAR_STRONG, BAR_PARTIAL, EXTREME_RANK

F = []
def check(name, got, want):
    ok = got == want
    F.append((name, ok, got, want))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:52} got {got} want {want}")

print("every branch reachable")
check("branch 1: clears bar, not extreme",      decide(6.9, 8, 27, True),  (1, False))
check("branch 2: mid-range residual",           decide(15.0, 8, 27, True), (2, False))
check("branch 3: residual over 20",             decide(25.0, 1, 27, True), (3, False))
check("branch 3: unstable sign",                decide(5.0, 8, 27, False), (3, False))
check("branch 4: no robust improvement",        decide(5.0, 8, 27, True, improves_baseline=False), (4, False))

print("\nboundary values on the residual")
check("residual 9.9, rank 8  -> 1",             decide(9.9, 8, 27, True),  (1, False))
check("residual 10.0, rank 8 -> 1 (inclusive)", decide(10.0, 8, 27, True), (1, False))
check("residual 10.1, rank 8 -> 2",             decide(10.1, 8, 27, True), (2, False))
check("residual 20.0, rank 8 -> 2 (inclusive)", decide(20.0, 8, 27, True), (2, False))
check("residual 20.1, rank 8 -> 3",             decide(20.1, 8, 27, True), (3, False))

print("\nboundary values on the rank")
check("rank 2 with residual 6.9 -> 2, disagree", decide(6.9, 2, 27, True), (2, True))
check("rank 3 with residual 6.9 -> 2, disagree", decide(6.9, 3, 27, True), (2, True))
check("rank 4 with residual 6.9 -> 1",           decide(6.9, 4, 27, True), (1, False))

print("\nconflicting criteria are flagged, never silently resolved")
check("actual P3 result (6.93, rank 3)",         decide(6.93, 3, 27, True), (2, True))

print("\nno default path can return the strongest conclusion")
import itertools
bad = []
for r in [0.0, 5.0, 9.9, 10.0, 10.1, 15.0, 20.0, 20.1, 30.0, -12.0]:
    for k in range(1, 28):
        for st in (True, False):
            for imp in (True, False):
                b, _ = decide(r, k, 27, st, imp)
                if b == 1 and not (abs(r) <= BAR_STRONG and k > EXTREME_RANK and st and imp):
                    bad.append((r, k, st, imp))
check("exhaustive sweep: branch 1 only when earned", bad, [])

print("\nnegative residuals use magnitude")
check("residual -6.9, rank 8 -> 1",  decide(-6.9, 8, 27, True), (1, False))
check("residual -25.0, rank 8 -> 3", decide(-25.0, 8, 27, True), (3, False))

n_fail = sum(1 for _, ok, _, _ in F if not ok)
print(f"\n{len(F) - n_fail}/{len(F)} passed")
raise SystemExit(1 if n_fail else 0)
