"""Tests for the reported-output validator. Run: python test_validate_outputs.py"""
import math
import numpy as np
import pandas as pd
from validate_outputs import scalar, record, json_safe, OutputError

F = []
def ok(name, fn, want):
    try:
        got = fn(); passed = got == want
    except Exception as e:
        got, passed = f"raised {type(e).__name__}", False
    F.append(passed); print(f"  [{'PASS' if passed else 'FAIL'}] {name:58} {got if passed else f'got {got!r} want {want!r}'}")

def raises(name, fn, must_mention=None):
    try:
        fn(); F.append(False); print(f"  [FAIL] {name:58} did not raise")
    except OutputError as e:
        good = (must_mention is None) or (must_mention.lower() in str(e).lower())
        F.append(good)
        print(f"  [{'PASS' if good else 'FAIL'}] {name:58} {str(e)[:56]}")
    except Exception as e:
        F.append(False); print(f"  [FAIL] {name:58} wrong type {type(e).__name__}")

print("the actual bugs this exists to catch")
row = pd.Series({"coef": 0.28}, name="x")
raises("pandas method object (the .between bug)", lambda: scalar(row.between, "coefficient", "between"), "callable")
raises("DataFrame method (the .pct_change bug)", lambda: scalar(pd.DataFrame().pct_change, "coefficient", "pct_change"), "callable")
raises("NaN not nullable (the truthy-NaN bug)", lambda: scalar(float("nan"), "p_value", "p"), "nan")
raises("numpy array", lambda: scalar(np.array([1.0, 2.0]), "coefficient", "c"), "array")
raises("pandas Series", lambda: scalar(pd.Series([1.0, 2.0]), "coefficient", "c"), None)

print("\ndomain bounds")
ok("p=0.0 valid", lambda: scalar(0.0, "p_value", "p"), 0.0)
ok("p=1.0 valid", lambda: scalar(1.0, "p_value", "p"), 1.0)
raises("p=-0.001 rejected", lambda: scalar(-0.001, "p_value", "p"), "below")
raises("p=1.001 rejected", lambda: scalar(1.001, "p_value", "p"), "above")
raises("r2 above 1", lambda: scalar(1.2, "r2", "r2"), "above")
raises("correlation below -1", lambda: scalar(-1.5, "correlation", "r"), "below")
raises("negative standard error", lambda: scalar(-0.1, "se", "se"), "below")
raises("rank 0", lambda: scalar(0, "rank", "rank"), "below")
raises("negative count", lambda: scalar(-5, "count", "n"), "below")

print("\nintegers")
ok("rank 3 -> int", lambda: scalar(3.0, "rank", "rank"), 3)
ok("count 269 -> int", lambda: scalar(269.0, "count", "n"), 269)
raises("rank 3.5 rejected", lambda: scalar(3.5, "rank", "rank"), "whole number")

print("\nnullability and infinities")
ok("None when nullable", lambda: scalar(None, "coefficient", "c", nullable=True), None)
raises("None when not nullable", lambda: scalar(None, "coefficient", "c"), "not nullable")
ok("NaN when nullable -> None", lambda: scalar(float("nan"), "coefficient", "c", nullable=True), None)
raises("inf always rejected", lambda: scalar(math.inf, "coefficient", "c"), "infinite")
raises("inf rejected even if nullable", lambda: scalar(math.inf, "coefficient", "c", nullable=True), "infinite")

print("\nnumpy scalars are coerced to plain Python, so JSON works with no custom encoder")
ok("np.float64 -> float", lambda: type(scalar(np.float64(0.28), "coefficient", "c")).__name__, "float")
ok("np.int64 -> int", lambda: type(scalar(np.int64(3), "rank", "r")).__name__, "int")
ok("raw np.float64 is NOT json-safe", lambda: (json_safe(float(np.float64(1.0))) == 1.0), True)
# np.float64 SUBCLASSES float and serializes silently; np.int64, np.float32 and
# np.bool_ do not. A codebase that only ever tested float64 would believe numpy
# scalars are safe. They are not, which is why scalar() coerces rather than
# trusting.
ok("np.float64 happens to serialize (it subclasses float)", lambda: json_safe(np.float64(1.0)) == 1.0, True)
raises("json_safe rejects np.int64", lambda: json_safe(np.int64(3)), "serializable")
raises("json_safe rejects np.float32", lambda: json_safe(np.float32(1.0)), "serializable")
raises("json_safe rejects np.bool_", lambda: json_safe(np.bool_(True)), "serializable")
ok("scalar() coerces np.int64 to a serializable int",
   lambda: json_safe(scalar(np.int64(3), "rank", "r")) == 3, True)

print("\nrecord() validates a whole reported row")
ok("valid record", lambda: record(p=("p_value", np.float64(0.0005)), rank=("rank", np.int64(3)),
                                  n=("count", 269), coef=("coefficient", np.float64(0.2808))),
   {"p": 0.0005, "rank": 3, "n": 269, "coef": 0.2808})
raises("record catches a bad field", lambda: record(p=("p_value", 1.5)), "above")
ok("record output is json-safe", lambda: json_safe(record(p=("p_value", np.float64(0.01)))) == {"p": 0.01}, True)

raises("unknown kind", lambda: scalar(1.0, "bananas", "x"), "unknown kind")
raises("string rejected", lambda: scalar("0.28", "coefficient", "c"), "string")

n = sum(1 for p in F if not p)
print(f"\n{len(F)-n}/{len(F)} passed")
raise SystemExit(1 if n else 0)
