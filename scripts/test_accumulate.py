"""Tests for the pre-registered accumulation transforms. Run: python test_accumulate.py"""
import numpy as np
import pandas as pd
from accumulate import (cumulative_shortfall_from_index, cumulative_excess_over_own_base,
                        cumulative_excess_over_fixed, cumulative_sum,
                        compounded_growth, consecutive_years_below,
                        rebuild_and_compare)

F = []
def check(name, got, want):
    ok = got == want
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:58} got {got} want {want}")

def frame(geo, years, vals):
    return pd.DataFrame({"geo": geo, "time": years, "v": vals})

def vals(df, col):
    return [round(float(x), 6) for x in df[col]]

print("cumulative_shortfall_from_index: sum of max(0, 100 - x)")
d = frame("A", [2008, 2009, 2010], [100.0, 90.0, 80.0])
check("no shortfall in the base year",
      vals(cumulative_shortfall_from_index(d, "v", 2008, "c"), "c"), [0.0, 10.0, 30.0])
d2 = frame("A", [2008, 2009, 2010], [100.0, 110.0, 90.0])
check("years ABOVE the base contribute zero, never negative",
      vals(cumulative_shortfall_from_index(d2, "v", 2008, "c"), "c"), [0.0, 0.0, 10.0])
d3 = frame("A", [2006, 2007, 2008, 2009], [50.0, 50.0, 100.0, 90.0])
check("years before the base are excluded",
      vals(cumulative_shortfall_from_index(d3, "v", 2008, "c"), "c"), [0.0, 10.0])

print("\ncumulative_excess_over_own_base: sum of max(0, x - x_base)")
d = frame("A", [2010, 2011, 2012], [20.0, 25.0, 30.0])
check("excess accumulates from the country's own base",
      vals(cumulative_excess_over_own_base(d, "v", 2010, "c"), "c"), [0.0, 5.0, 15.0])
d = frame("A", [2010, 2011, 2012], [20.0, 15.0, 30.0])
check("years BELOW the base contribute zero",
      vals(cumulative_excess_over_own_base(d, "v", 2010, "c"), "c"), [0.0, 0.0, 10.0])

print("\nA MISSING BASELINE YIELDS NaN, NEVER ZERO")
d = pd.concat([frame("A", [2010, 2011], [20.0, 25.0]),
               frame("B", [2011, 2012], [40.0, 50.0])])   # B has no 2010
got = cumulative_excess_over_own_base(d, "v", 2010, "c")
check("country with a baseline is computed",
      vals(got[got.geo == "A"], "c"), [0.0, 5.0])
check("country WITHOUT a baseline is NaN, not 0",
      all(np.isnan(x) for x in got[got.geo == "B"]["c"]), True)

print("\ncumulative_excess_over_fixed: benchmark, not own base")
d = frame("A", [2008, 2009], [120.0, 90.0])
check("excess over 100 floors at zero",
      vals(cumulative_excess_over_fixed(d, "v", 2008, "c"), "c"), [20.0, 20.0])
check("a country never above the benchmark accumulates nothing",
      vals(cumulative_excess_over_fixed(frame("A", [2008, 2009], [80.0, 90.0]),
                                        "v", 2008, "c"), "c"), [0.0, 0.0])

print("\ncumulative_sum: for series already non-negative")
check("plain running sum",
      vals(cumulative_sum(frame("A", [2008, 2009], [3.0, 4.0]), "v", 2008, "c"), "c"),
      [3.0, 7.0])
try:
    cumulative_sum(frame("A", [2008], [-1.0]), "v", 2008, "c")
    check("rejects negative values", "no error", "ValueError")
except ValueError:
    check("rejects negative values", "ValueError", "ValueError")

print("\ncompounded_growth: COMPOUNDED, not summed")
d = frame("A", [2008, 2009, 2010], [10.0, 10.0, 10.0])
check("10% three times compounds to 33.1%, not 30%",
      vals(compounded_growth(d, "v", 2008, "c"), "c"), [10.0, 21.0, 33.1])
d = frame("A", [2008, 2009], [10.0, -10.0])
check("deflation reduces the compounded total",
      vals(compounded_growth(d, "v", 2008, "c"), "c"), [10.0, -1.0])

print("\nconsecutive_years_below: a RUN that RESETS, not a total")
d = frame("A", [2008, 2009, 2010, 2011], [90.0, 90.0, 110.0, 90.0])
check("run resets after a year at or above threshold",
      vals(consecutive_years_below(d, "v", 2008, "c"), "c"), [1.0, 2.0, 0.0, 1.0])
check("a total would have given 3 at the end -- it does not",
      vals(consecutive_years_below(d, "v", 2008, "c"), "c")[-1], 1.0)
d = frame("A", [2008, 2009, 2010], [90.0, 80.0, 70.0])
check("an unbroken run counts up",
      vals(consecutive_years_below(d, "v", 2008, "c"), "c"), [1.0, 2.0, 3.0])
check("exactly at the threshold is NOT below",
      vals(consecutive_years_below(frame("A", [2008], [100.0]), "v", 2008, "c"), "c"),
      [0.0])

print("\nunsorted input must not change the answer")
d = frame("A", [2010, 2008, 2009], [80.0, 100.0, 90.0])
check("shortfall is order-independent",
      vals(cumulative_shortfall_from_index(d, "v", 2008, "c"), "c"), [0.0, 10.0, 30.0])
check("run length is order-independent",
      vals(consecutive_years_below(d, "v", 2008, "c"), "c"), [0.0, 1.0, 2.0])

print("\nduplicate country-years are rejected, not silently double-counted")
d = pd.DataFrame({"geo": ["A", "A"], "time": [2008, 2008], "v": [1.0, 2.0]})
for fn in [cumulative_shortfall_from_index, cumulative_excess_over_own_base,
           compounded_growth]:
    try:
        fn(d, "v", 2008, "c")
        check(f"{fn.__name__} rejects duplicates", "no error", "ValueError")
    except ValueError:
        check(f"{fn.__name__} rejects duplicates", "ValueError", "ValueError")

print("\nNO FUTURE INFORMATION: truncating later years cannot change earlier ones")
rng = np.random.default_rng(7)
panel = pd.concat([
    frame(g, list(range(2008, 2025)),
          list(100 + rng.normal(0, 15, 17)))
    for g in ["A", "B", "C"]])
for fn in [cumulative_shortfall_from_index, cumulative_excess_over_own_base,
           cumulative_excess_over_fixed, compounded_growth,
           consecutive_years_below]:
    bad = rebuild_and_compare(fn, panel, "v", 2008, "c")
    check(f"{fn.__name__} is a running quantity", bad, [])

bad_names = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad_names)}/{len(F)} passed")
if bad_names:
    raise SystemExit("FAILED: " + ", ".join(bad_names))
