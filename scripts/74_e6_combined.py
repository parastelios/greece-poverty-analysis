"""E6: the frozen combined model.

THIS STAGE FITS NOTHING NEW. The pre-registration fixes the combined model as
the frozen P3 specification and does NOT reopen it. The fifteen pairwise family
combinations are not tested. E6 reports what already exists and states what may
not be said about it.

TWO SPECIFICATIONS, TWO INTERPRETATIONS, NOT MERGED.

  Frozen P3      the pre-committed historical result. It includes
                 same-instrument deprivation, so it cannot be described as
                 purely objective or fully distant from the outcome.
  EA companion   removes that proximity concern. The residual changes
                 materially. It is a STRICTER DIAGNOSTIC, not a replacement
                 selected because its result is preferable.

Neither is the definitive model, and they are not combined into one preferred
estimate. THEIR DISAGREEMENT IS THE RESULT: how much of Greece's gap is absorbed
depends materially on whether same-instrument deprivation is admitted.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import load as load_registry, block_reason

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
frozen = json.loads((PROC / "p5f_frozen_result.json").read_text())
ea = pd.read_csv(PROC / "ea_results.csv").iloc[0]
e1 = pd.read_csv(PROC / "e1_results.csv").set_index("var")
e4 = pd.read_csv(PROC / "e4_results.csv").set_index("var")
reg = load_registry()

P3_PREDICTORS = [
    ("severe_mat_soc_deprivation", "P1", "current"),
    ("housing_cost_overburden", "C6", "current"),
    ("ltu_rate", "C2", "current"),
    ("aic_pps_pc_k", "C1", "current"),
    ("wage_years_below_2008", "C3", "accumulated (duration)"),
    ("cum_excess_unemployment", "C2", "accumulated"),
]
# E-stage equivalents, where the E variable is a rename of the P3 one
E_EQUIVALENT = {
    "aic_pps_pc_k": "aic_pps_pc",
    "wage_years_below_2008": "dur_real_wages_below",
    "cum_excess_unemployment": "acc_cum_excess_unemployment",
}

bar = "=" * 96
print(bar); print("E6: THE FROZEN COMBINED MODEL"); print(bar)
print("  NOTHING IS FITTED HERE. The combined model is the frozen P3")
print("  specification and is not reopened. The fifteen pairwise family")
print("  combinations are NOT tested.\n")

print(f"{bar}\nTWO SPECIFICATIONS, REPORTED SIDE BY SIDE\n{bar}\n")
p3 = frozen["p3"]
print(f"  {'':34} {'Frozen P3':>14} {'EA companion':>14}")
print(f"  {'predictors':34} {6:>14} {5:>14}")
print(f"  {'additional P1 predictor beyond AROP':34} {'YES':>14} {'no':>14}")
print("  (both specifications retain AROP, itself an EU-SILC measure)")
print(f"  {'Greece residual':34} {p3['greece_oos_residual']:>+14.2f} "
      f"{ea.companion_residual:>+14.2f}")
print(f"  {'Greece rank':34} {str(p3['rank']):>14} "
      f"{str(int(ea.companion_rank)) + '/27':>14}")
print(f"  {'R2':34} {p3['r2']:>14.3f} {ea.companion_r2:>14.3f}")
print(f"  {'n':34} {p3['n']:>14} {int(ea.n):>14}")
print(f"\n  Both fitted on IDENTICAL rows (n={int(ea.n)}).")

print(f"\n{bar}\nTHE DISAGREEMENT IS THE RESULT\n{bar}\n")
print(f"  Frozen P3 UNDER-predicts Greek hardship by {p3['greece_oos_residual']:.2f} points.")
print(f"  The companion OVER-predicts it by {abs(ea.companion_residual):.2f}.")
print(f"  Greece moves from rank {p3['rank']} to rank {int(ea.companion_rank)}/27 --")
print("  from third-most under-predicted to third-most OVER-predicted.")
print(f"  R2 falls {p3['r2']:.3f} -> {ea.companion_r2:.3f}.\n")
print("  CONCLUSIONS ABOUT HOW MUCH OF GREECE'S GAP IS ABSORBED DEPEND")
print("  MATERIALLY ON WHETHER SAME-INSTRUMENT DEPRIVATION IS ADMITTED.")
print("  Neither specification is the definitive model. They are not merged")
print("  into a single preferred estimate, and neither is selected because its")
print("  result is preferable.")

print(f"\n{bar}\nWHAT E1-E5 SAY ABOUT EACH FROZEN-P3 PREDICTOR\n{bar}\n")
print(f"  {'predictor':28} {'con':>4} {'kind':22} E-stage verdict")
rows = []
for v, cid, kind in P3_PREDICTORS:
    ev = E_EQUIVALENT.get(v, v)
    verdict, src = "not tested in E", ""
    if ev in e1.index:
        verdict, src = e1.loc[ev, "outcome"], "E1"
    if ev in e4.index:
        verdict, src = e4.loc[ev, "outcome"], "E4"
    note = ""
    if v in E_EQUIVALENT:
        note = f" (E variable: {ev})"
    if block_reason(reg, v) if v in reg.index else None:
        note += "  BLOCKED"
    print(f"  {v:28} {cid:>4} {kind:22} {verdict} [{src}]{note}")
    rows.append({"p3_predictor": v, "construct": cid, "kind": kind,
                 "e_variable": ev, "e_stage": src, "e_verdict": verdict})

n_sup = sum(1 for r in rows if r["e_verdict"] == "supported")
n_blocked = sum(1 for r in rows if r["e_verdict"] == "blocked_by_proximity")
n_other = len(rows) - n_sup - n_blocked
print(f"\n  Of {len(rows)} frozen-P3 predictors: {n_sup} supported in the E stages, "
      f"{n_other} inconclusive, {n_blocked} proximity-blocked.")
print("  NOTE: P3 uses housing at its CURRENT level, which E1 found inconclusive.")
print("  It is the ACCUMULATED housing measure that E4 supported, and that is a")
print("  different variable from the one frozen P3 contains.")
print("\n  IMPORTANT: this is NOT independent corroboration of P3. Every E test")
print("  used the same panel, the same outcome and the same countries. The")
print("  cross-walk shows the frozen specification is CONSISTENT with the")
print("  pre-registered framework, not that it was replicated.")
print(f"\n  wage_years_below_2008 and E4's dur_real_wages_below are the SAME")
print("  SERIES (identical to floating point). The C3 duration measure E4")
print("  supported was already inside the frozen specification.")

print(f"\n{bar}\nPROHIBITED REINTERPRETATIONS\n{bar}\n")
PROHIBITED = [
    "Calling frozen P3 'objective-only'. It retains severe material and social "
    "deprivation, an EU-SILC item from the same instrument as the outcome.",
    "Calling the EA companion a replacement or a corrected model. EA returned "
    "Outcome C: the frozen result depends materially on that predictor.",
    "Merging the two into one preferred estimate, or averaging their residuals.",
    "Choosing between them on residual size. EA's anti-selection rule forbids "
    "it, and both are reported under every outcome.",
    "Describing accumulated exposure dynamically. P5 and E4 both find the "
    "evidence predominantly between-country, with no first-difference support.",
    "Treating E1-E5 as replication of P3 (same panel, outcome and countries), "
    "or as evidence that its predictors contribute independently when entered "
    "jointly -- they were tested separately, not conditionally on each other.",
    "Reopening the fifteen pairwise family combinations. The pre-registration "
    "fixes the combined model and does not reopen it.",
]
for i, s in enumerate(PROHIBITED, 1):
    print(f"  {i}. {s}")

print(f"\n{bar}\nNOT REOPENED\n{bar}\n")
print("  The fifteen pairwise combinations of the six constructs are NOT tested.")
print("  The pre-registration fixes the combined model as frozen P3. Searching")
print("  combinations after seeing which constructs succeeded would be the")
print("  exploratory screening this design replaced.")
print(f"\n  Nothing in E6 alters p5f-frozen. Frozen P3 values are read from")
print("  p5f_frozen_result.json, not recomputed.")

pd.DataFrame(rows).to_csv(PROC / "e6_crosswalk.csv", index=False)
pd.DataFrame([{
    "p3_residual": p3["greece_oos_residual"], "p3_rank": 3, "p3_r2": p3["r2"],
    "companion_residual": float(ea.companion_residual),
    "companion_rank": int(ea.companion_rank),
    "companion_r2": float(ea.companion_r2),
    "n": int(ea.n), "ea_outcome": ea.outcome,
    "specifications_merged": False, "definitive_model_named": False,
}]).to_csv(PROC / "e6_results.csv", index=False)
print(f"\nWritten to {PROC}/e6_results.csv, e6_crosswalk.csv")
