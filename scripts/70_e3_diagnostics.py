"""E3: diagnostic and contextual checks.

Step 5 of the approved testing order, plus the contextual and legacy record.

E3 IS NOT A HYPOTHESIS-TESTING FAMILY, AND DELIBERATELY SO. The frozen
pre-registration declares three BH families -- current primaries, accumulated
primaries, secondary outcome -- and none of them covers contextual or legacy
variables. Inventing a fourth family here would repeat exactly the unregistered
grouping recorded as PD-01.

So nothing in this stage is FDR-corrected, and NOTHING HERE CAN BECOME A
FINDING. Raw p-values are shown because suppressing them would be worse, but
they are diagnostic quantities, not tests. Where a variable has no
pre-registered direction, no directional claim is made at all.

Sections:
  A  proximate diagnostic (P1): how much apparent explanation is restatement,
     and separately, what the same items validate
  B  inequality retest (s80s20) -- a RETEST of the known null at claim 8.1
  C  migration context
  D  ambiguous-direction context: saving, debt, hours -- descriptive only
  E  work-effort squeeze retest, with its C4 overlap stated
  F  transfer-policy comparators -- mechanically tied to AROP, blocked
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import load as load_registry, BLOCKING_PROXIMITY

OUT = Path(__file__).resolve().parents[1] / "data" / "processed"
GR = "EL"
BASE = "subjective_poverty ~ arop + C(time)"

panel = pd.read_csv(OUT / "e0_extended_panel.csv")
reg = load_registry()
cmap = json.loads((OUT / "construct_map_frozen.json").read_text())
P1_ITEMS = ([cmap["constructs"]["P1"]["primary"]]
            + [s for s in cmap["constructs"]["P1"]["sensitivities"]
               if s in panel.columns])


def fit(f, d):
    return smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})


def greece_residual(f, d):
    tr, te = d[d.geo != GR], d[d.geo == GR]
    m = smf.ols(f, data=tr).fit()
    return float((te["subjective_poverty"] - m.predict(te)).mean())


rows = []
bar = "=" * 92
print(bar); print("E3: DIAGNOSTIC AND CONTEXTUAL CHECKS"); print(bar)
print("  NOT a hypothesis-testing family. No FDR. Nothing here can become a")
print("  finding. Raw p-values are diagnostic quantities, not tests.\n")

# ---------------------------------------------------------------------------
# A. Proximate diagnostic
# ---------------------------------------------------------------------------
print(f"{bar}\nA. PROXIMATE DIAGNOSTIC (P1) — two separate questions\n{bar}")
d = panel.dropna(subset=P1_ITEMS + ["subjective_poverty", "arop"])
r_base = greece_residual(BASE, d)
f_all = f"{BASE} + " + " + ".join(P1_ITEMS)
r_p1 = greece_residual(f_all, d)
m_base, m_all = fit(BASE, d), fit(f_all, d)
print(f"\n  A1. HOW MUCH APPARENT EXPLANATION IS RESTATEMENT")
print(f"      n = {len(d)}, {d.geo.nunique()} countries")
print(f"      Greece residual, baseline                 : {r_base:+7.2f}")
print(f"      Greece residual, all four P1 items added  : {r_p1:+7.2f}")
print(f"      absorbed by same-instrument items         : {r_base - r_p1:+7.2f} "
      f"({(r_base - r_p1) / r_base:.0%} of the baseline residual)")
print(f"      R2 {m_base.rsquared:.3f} -> {m_all.rsquared:.3f}")
print("      This is the quantity P1 exists to produce. It is NOT an explanation.")

# The validation question is a different one, and needs a different statistic:
# does reported difficulty move WITH concrete affordability failure, or is it a
# reporting style that floats free of them?
print(f"\n  A2. VALIDATION: does reported difficulty track concrete failure?")
print(f"      Within-country correlation (country means removed), and Greece alone.\n")
print(f"      {'item':26} {'within-country r':>17} {'Greece over time r':>20} {'GR mean':>9}")
dem = panel.copy()
for c in ["subjective_poverty"] + P1_ITEMS:
    dem[c + "_w"] = dem[c] - dem.groupby("geo")[c].transform("mean")
gr = panel[panel.geo == GR]
for v in P1_ITEMS:
    sub = dem.dropna(subset=["subjective_poverty_w", v + "_w"])
    r_within = sub["subjective_poverty_w"].corr(sub[v + "_w"])
    g = gr.dropna(subset=["subjective_poverty", v])
    r_gr = g["subjective_poverty"].corr(g[v])
    print(f"      {v:26} {r_within:17.3f} {r_gr:20.3f} {g[v].mean():9.1f}")
    rows.append({"section": "A2 validation", "var": v, "stat": "within_country_r",
                 "value": r_within, "greece_timeseries_r": r_gr,
                 "eligible_for_finding": False})
print("\n      A reporting style unmoored from circumstance would not track these.")

# ---------------------------------------------------------------------------
# B-F. contextual and legacy, one at a time
# ---------------------------------------------------------------------------
CHECKS = [
    ("B. INEQUALITY RETEST", ["s80s20"],
     "RETEST of the known null at claim 8.1. Never a fresh candidate."),
    ("C. MIGRATION CONTEXT", ["net_migration"],
     "Causal position ambiguous: both a response to and a contributor to "
     "labour-market damage."),
    ("D. AMBIGUOUS-DIRECTION CONTEXT", ["saving_rate", "debt_to_income", "working_hours"],
     "NO pre-registered direction. High saving may be prudence or demand "
     "collapse. Reported descriptively; no directional claim is made."),
    ("E. WORK-EFFORT SQUEEZE RETEST", ["work_effort_squeeze"],
     "r = 0.963 with wadj_a01 in all three views. Run ALONE here; it may never "
     "enter a specification with C4's primary, and its result cannot be read "
     "as independent of C4."),
    ("F. TRANSFER-POLICY COMPARATORS", ["arop_before_transfers", "transfer_effect"],
     "Mechanically tied to AROP, which is in the baseline. Blocked."),
]

for title, vs, note in CHECKS:
    print(f"\n{bar}\n{title}\n{bar}")
    print(f"  {note}\n")
    print(f"  {'variable':24} {'direction':16} {'coef':>10} {'se':>8} "
          f"{'p_raw':>8} {'n':>5}  status")
    for v in vs:
        if v not in panel.columns:
            print(f"  {v:24} NOT IN PANEL")
            continue
        adv = reg.loc[v, "adverse_direction"]
        prox = reg.loc[v, "proximity_class"]
        dd = panel.dropna(subset=[v, "subjective_poverty", "arop"])
        m = fit(f"{BASE} + {v}", dd)
        blocked = prox in BLOCKING_PROXIMITY
        if blocked:
            status = "BLOCKED (mechanical with AROP)"
        elif adv == "ambiguous":
            status = "descriptive only, no directional claim"
        else:
            status = "diagnostic, not FDR-corrected, cannot become a finding"
        print(f"  {v:24} {adv:16} {m.params[v]:+10.4f} {m.bse[v]:8.4f} "
              f"{m.pvalues[v]:8.4f} {len(dd):5d}  {status}")
        rows.append({"section": title.split(".")[0], "var": v,
                     "stat": "coef_on_baseline", "value": float(m.params[v]),
                     "se": float(m.bse[v]), "p_raw": float(m.pvalues[v]),
                     "adverse_direction": adv, "proximity_class": prox,
                     "n": len(dd), "blocked": blocked,
                     "eligible_for_finding": False, "note": note})

print(f"\n{bar}\nSUMMARY\n{bar}")
print(f"  Checks run: {sum(len(v) for _, v, _ in CHECKS)} contextual/legacy "
      f"variables + {len(P1_ITEMS)} proximate items")
print("  Eligible to become findings: 0, by construction.")
print("  FDR corrections applied: none. E3 declares no family.")

pd.DataFrame(rows).to_csv(OUT / "e3_results.csv", index=False)
pd.DataFrame([{"greece_resid_baseline": r_base, "greece_resid_with_p1": r_p1,
               "absorbed": r_base - r_p1,
               "absorbed_share": (r_base - r_p1) / r_base,
               "r2_baseline": m_base.rsquared, "r2_with_p1": m_all.rsquared,
               "n": len(d)}]).to_csv(OUT / "e3_restatement.csv", index=False)
print(f"\nWritten to {OUT}/e3_results.csv, e3_restatement.csv")
