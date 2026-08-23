"""EDA: the descriptive groundwork. Step 1 of the approved E testing order.

NO MODELS, NO TESTS, NO P-VALUES. Levels, trajectories and ranks only, plus a
pointer to the three correlation views E0 already produced. Descriptive
corroboration tier throughout -- nothing here can support or refute anything.

The stage needs no pre-registration precisely because it makes no inferential
claim. What it must not do is let a descriptive pattern become the reason a
later test is run, so the construct map was frozen (2103b3d) and the E tests
pre-registered (a747e7a) BEFORE this stage runs, not after.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

panel = pd.read_csv(PROC / "e0_extended_panel.csv")
cmap = json.loads((PROC / "construct_map_frozen.json").read_text())
GR = "EL"

OUTCOMES = ["subjective_poverty", "arop", "arope", "gap_subj_arop", "gap_subj_arope"]
PRIMARIES = []
for cid, c in cmap["constructs"].items():
    prim = c["primary"]
    for v in (prim if isinstance(prim, list) else [prim]):
        PRIMARIES.append((cid, c["name"], v))

# Adverse direction, so a rank of 1 always means "worst in Europe".
reg = pd.read_csv(PROC / "e0_variable_registry.csv").set_index("name")
ADVERSE = reg["adverse_direction"].to_dict()
ADVERSE.update({v: "higher_is_worse" for v in OUTCOMES})
assert set(ADVERSE.values()) <= {"higher_is_worse", "lower_is_worse", "ambiguous"}, \
    f"unexpected adverse_direction values: {set(ADVERSE.values())}"

bar = "=" * 74
print(bar); print("EDA: DESCRIPTIVE GROUNDWORK (no models, no tests)"); print(bar)

# --------------------------------------------------------------------------
# 1. The paradox, and whether AROPE bridges it
# --------------------------------------------------------------------------
print("\n1. THE GAP, AND WHETHER AROPE CLOSES IT\n")
rows = []
for yr in sorted(panel.time.unique()):
    d = panel[panel.time == yr]
    g = d[d.geo == GR]
    if g.empty:
        continue
    g = g.iloc[0]
    rec = {"time": int(yr)}
    for v in ["subjective_poverty", "arop", "arope"]:
        rec[f"gr_{v}"] = g[v]
        rec[f"eu_{v}"] = d[v].median()
    rec["gap_vs_arop"] = g["subjective_poverty"] - g["arop"]
    rec["gap_vs_arope"] = g["subjective_poverty"] - g["arope"]
    rows.append(rec)
paradox = pd.DataFrame(rows)
print(f"  {'year':>5}  {'subj':>6} {'AROP':>6} {'AROPE':>6}   "
      f"{'subj-AROP':>9} {'subj-AROPE':>10}   {'AROPE closes':>12}")
for r in paradox.itertuples():
    closed = r.gap_vs_arop - r.gap_vs_arope
    print(f"  {r.time:>5}  {r.gr_subjective_poverty:6.1f} {r.gr_arop:6.1f} "
          f"{r.gr_arope:6.1f}   {r.gap_vs_arop:9.1f} {r.gap_vs_arope:10.1f}   "
          f"{closed:11.1f}pp")
m = paradox.gap_vs_arop.mean()
ma = paradox.gap_vs_arope.mean()
print(f"\n  Mean gap against AROP  : {m:.1f} points")
print(f"  Mean gap against AROPE : {ma:.1f} points")
print(f"  AROPE closes on average: {m - ma:.1f} points "
      f"({(m - ma) / m:.0%} of the AROP gap), leaving {ma:.1f} unexplained")

# --------------------------------------------------------------------------
# 2. Where Greece ranks, per construct primary
# --------------------------------------------------------------------------
print(f"\n{bar}\n2. WHERE GREECE RANKS (1 = worst in the EU27)\n")
rank_rows = []
for cid, cname, v in [("--", "outcome", o) for o in OUTCOMES] + PRIMARIES:
    if v not in panel.columns:
        print(f"  {v:26} NOT IN PANEL")
        continue
    # rank 1 must always mean WORST. For lower_is_worse variables that is the
    # SMALLEST value, so the rank runs ascending. An earlier version compared
    # against "low", a value this column never holds, so every variable ranked
    # descending and Greece's worst-in-Europe real wages showed as rank 27.
    asc = ADVERSE[v] == "lower_is_worse"
    for yr in sorted(panel.time.unique()):
        d = panel[(panel.time == yr)].dropna(subset=[v])
        if GR not in set(d.geo) or len(d) < 20:
            continue
        d = d.assign(rk=d[v].rank(ascending=asc, method="min"))
        g = d[d.geo == GR].iloc[0]
        rank_rows.append({"construct": cid, "variable": v, "time": int(yr),
                          "gr_value": g[v], "gr_rank": int(g.rk),
                          "n_countries": len(d), "eu_median": d[v].median()})
ranks = pd.DataFrame(rank_rows)
latest = ranks[ranks.time == ranks.time.max()]
print(f"  {'construct':>9}  {'variable':28} {'Greece':>8} {'EU med':>8} {'rank':>8}")
for r in latest.itertuples():
    print(f"  {r.construct:>9}  {r.variable:28} {r.gr_value:8.1f} "
          f"{r.eu_median:8.1f} {r.gr_rank:5d}/{r.n_countries}")

# --------------------------------------------------------------------------
# 3. Recovery: what came back, and what did not
# --------------------------------------------------------------------------
FLAT_BAND = 0.10   # |change| under 10% of the original gap counts as flat
first, last = int(panel.time.min()), int(panel.time.max())

print(f"\n{bar}\n3. RECOVERY SINCE THE PANEL START ({first} -> {last})\n")
print(f"  Movement classified against the size of the {first} gap. "
      f"Under {FLAT_BAND:.0%} = flat.\n")
rec_rows = []
for cid, cname, v in PRIMARIES + [("--", "outcome", o) for o in OUTCOMES]:
    if v not in panel.columns:
        continue
    a = ranks[(ranks.variable == v) & (ranks.time == first)]
    b = ranks[(ranks.variable == v) & (ranks.time == last)]
    if a.empty or b.empty:
        continue
    a, b = a.iloc[0], b.iloc[0]
    gr_change = b.gr_value - a.gr_value
    gap_a, gap_b = a.gr_value - a.eu_median, b.gr_value - b.eu_median
    # A binary "did the gap shrink" flag scored a 0.1-point move over nine
    # years as convergence. Movement is classified against the size of the
    # original gap instead, with a flat band, so "converging" means something.
    shift = abs(gap_a) - abs(gap_b)
    rel = shift / abs(gap_a) if abs(gap_a) > 1e-9 else 0.0
    if abs(rel) < FLAT_BAND:
        trend = "flat"
    else:
        trend = "converging" if shift > 0 else "diverging"
    # HICP is an annual inflation RATE. Comparing 2015's rate with 2024's is not
    # a recovery comparison, and labelling it one would be a category error of
    # exactly the kind E0 was built to prevent.
    if v.startswith("hicp"):
        trend = "not applicable (annual rate, not a level)"
    rec_rows.append({"construct": cid, "variable": v,
                     "gr_first": a.gr_value, "gr_last": b.gr_value,
                     "gr_change": gr_change,
                     "gap_first": gap_a, "gap_last": gap_b,
                     "gap_shift": shift, "gap_shift_rel": rel, "trend": trend,
                     "rank_first": a.gr_rank, "rank_last": b.gr_rank})
recovery = pd.DataFrame(rec_rows)
print(f"  {'variable':28} {'gap ' + str(first):>10} {'gap ' + str(last):>10}"
      f" {'shift':>8}  {'rank':>12}  trend")
for r in recovery.itertuples():
    print(f"  {r.variable:28} {r.gap_first:10.1f} {r.gap_last:10.1f}"
          f" {r.gap_shift_rel:+7.0%}  {r.rank_first:4d} -> {r.rank_last:<4d}  "
          f"{r.trend}")

for label in ["converging", "flat", "diverging"]:
    vs = recovery[recovery.trend == label].variable.tolist()
    print(f"\n  {label.upper()} ({len(vs)}): {', '.join(vs) if vs else '-'}")

# --------------------------------------------------------------------------
paradox.to_csv(PROC / "e_descriptives.csv", index=False)
ranks.to_csv(PROC / "e_descriptive_ranks.csv", index=False)
recovery.to_csv(PROC / "e_descriptive_recovery.csv", index=False)
print(f"\n{bar}")
print("Written: e_descriptives.csv, e_descriptive_ranks.csv, "
      "e_descriptive_recovery.csv")
print("Correlation views already exist: e0_corr_{pooled,between,within}.csv")
print("\nDESCRIPTIVE ONLY. Nothing here supports or refutes any hypothesis.")
