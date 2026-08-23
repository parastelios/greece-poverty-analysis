"""Tests for the registry vocabulary guard. Run: python test_registry.py"""
import registry
from registry import load, adverse_direction, blocks_headline, ADVERSE

F = []
def check(name, got, want):
    ok = got == want
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:56} got {got} want {want}")

reg = load()
print("the live registry passes every vocabulary")
check("loads without raising", reg.index.size > 0, True)
check("31 variables", len(reg), 31)

print("\nadverse_direction is passed through, never translated")
check("ltu_rate", adverse_direction(reg, "ltu_rate"), "higher_is_worse")
check("aic_pps_pc", adverse_direction(reg, "aic_pps_pc"), "lower_is_worse")
check("real_wages_idx", adverse_direction(reg, "real_wages_idx"), "lower_is_worse")
check("every value is in the vocabulary",
      set(reg.adverse_direction.dropna()) <= ADVERSE, True)

print("\nthe exact bug that motivated this module")
# E1 compared against "high"/"low". Prove those values are absent, so the
# comparison could only ever have been False for every row.
check("'high' appears nowhere in the column",
      "high" in set(reg.adverse_direction), False)
check("'low' appears nowhere either",
      "low" in set(reg.adverse_direction), False)

print("\nblocking proximity")
check("severe_mat_soc_deprivation blocks",
      blocks_headline(reg, "severe_mat_soc_deprivation"), True)
check("arrears blocks", blocks_headline(reg, "arrears"), True)
check("ltu_rate does not", blocks_headline(reg, "ltu_rate"), False)
check("aic_pps_pc does not", blocks_headline(reg, "aic_pps_pc"), False)

print("\nan unknown vocabulary value fails the load")
import pandas as pd, tempfile, pathlib
orig = registry.PROC
with tempfile.TemporaryDirectory() as tmp:
    d = pathlib.Path(tmp)
    bad = pd.read_csv(orig / "e0_variable_registry.csv")
    bad.loc[0, "adverse_direction"] = "high"          # the original typo
    bad.to_csv(d / "e0_variable_registry.csv", index=False)
    registry.PROC = d
    try:
        load()
        check("rejects adverse_direction='high'", "no error", "SystemExit")
    except SystemExit as e:
        check("rejects adverse_direction='high'", "SystemExit", "SystemExit")
        check("names the offending column", "adverse_direction" in str(e), True)

    bad2 = pd.read_csv(orig / "e0_variable_registry.csv")
    bad2.loc[0, "proximity_class"] = "objectiv"       # plausible typo
    bad2.to_csv(d / "e0_variable_registry.csv", index=False)
    try:
        load()
        check("rejects a proximity_class typo", "no error", "SystemExit")
    except SystemExit:
        check("rejects a proximity_class typo", "SystemExit", "SystemExit")

    bad3 = pd.read_csv(orig / "e0_variable_registry.csv")
    bad3 = pd.concat([bad3, bad3.iloc[[0]]])
    bad3.to_csv(d / "e0_variable_registry.csv", index=False)
    try:
        load()
        check("rejects duplicate names", "no error", "SystemExit")
    except SystemExit as e:
        check("rejects duplicate names", "duplicate" in str(e), True)
registry.PROC = orig

print("\nadverse_direction raises rather than guessing")
try:
    adverse_direction(reg.assign(adverse_direction="nonsense"), "ltu_rate")
    check("rejects an unknown value at point of use", "no error", "ValueError")
except ValueError:
    check("rejects an unknown value at point of use", "ValueError", "ValueError")

bad_names = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad_names)}/{len(F)} passed")
if bad_names:
    raise SystemExit("FAILED: " + ", ".join(bad_names))
