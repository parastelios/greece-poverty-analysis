"""Between- and within-country SDs for the accumulated measures.

F13 shows Mundlak between and within coefficients. Those coefficients are on
each measure's own scale -- percentage-point-years, years, index points -- so
plotting the raw values on one axis invites a comparison that is not valid: a
larger bar can simply mean a larger unit.

Standardising fixes that, but only if each component is scaled by ITS OWN
variation. The between coefficient multiplies country MEANS and the within
coefficient multiplies DEVIATIONS from those means, and the two have different
spreads. Dividing both by a single pooled SD would preserve exactly the
distortion it was meant to remove.

This computes nothing inferential. It reads the same panel E7 used, takes the
SD of the country means and the SD of the within-country deviations for each
focal measure, and writes them out. No model is fitted and no frozen number is
touched.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

panel = pd.read_csv(PROC / "e4_accumulated_panel.csv")
prereg = json.loads((PROC / "e7_preregistration.json").read_text())
PAIRS = prereg["pairs"]
e7 = pd.read_csv(PROC / "e7_results.csv")

rows = []
for pr in PAIRS:
    cur, acc, pid = pr["current"], pr["accumulated"], pr["id"]
    d = panel.dropna(subset=[cur, acc, "subjective_poverty", "arop"]).copy()
    cmean = d.groupby("geo")[acc].transform("mean")
    # ddof=0 on the country means matches how the Mundlak term is constructed:
    # every observation carries its country's mean, so the spread that the
    # between coefficient actually multiplies is the observation-level one.
    sd_between = float(cmean.std(ddof=0))
    sd_within = float((d[acc] - cmean).std(ddof=0))
    # resid_sd is the outcome scale E7 already recorded for this pair.
    sub = e7[(e7.pair == pid) & (e7.focal == acc)]
    resid_sd = float(sub.resid_sd.iloc[0]) if len(sub) else float("nan")
    rows.append({"pair": pid, "focal": acc, "sd_between": round(sd_between, 6),
                 "sd_within": round(sd_within, 6), "resid_sd": round(resid_sd, 6),
                 "n": len(d)})

out = pd.DataFrame(rows)
assert (out.sd_between > 0).all() and (out.sd_within > 0).all(), \
    "a zero SD would make the standardisation undefined"
assert out.resid_sd.notna().all(), "missing outcome scale for a pair"

bar = "=" * 78
print(bar); print("BETWEEN AND WITHIN SCALES (descriptive only, no model fitted)"); print(bar)
print(f"  {'pair':18} {'sd between':>11} {'sd within':>10} {'ratio':>7} {'resid sd':>9}")
for r in out.itertuples():
    print(f"  {r.pair:18} {r.sd_between:11.3f} {r.sd_within:10.3f} "
          f"{r.sd_between / r.sd_within:7.2f} {r.resid_sd:9.3f}")
print("\n  The ratio is why one pooled SD will not do: between-country spread")
print("  exceeds within-country spread by a wide and uneven margin.")

out.to_csv(PROC / "e7_between_within_scales.csv", index=False)
print(f"\nWritten to {(PROC / 'e7_between_within_scales.csv').relative_to(ROOT)}")
