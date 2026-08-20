"""Acquisition step for raw inputs that previously had NO producing script.

An external clean-room review found that a set of files in data/raw/ were read
by numbered scripts but produced by none -- they had been fetched in ad hoc
terminal sessions during development, which broke full from-scratch
reproducibility. This script closes that gap: every formerly-orphaned raw
input is fetched here, from the documented Eurostat dataset and filters, in
the exact column shape its readers expect.

Modes:
  python 00_fetch_missing_raw.py            # CHECK mode: fetch into a temp dir,
                                            # compare against the archived
                                            # snapshot, report agreement, write
                                            # nothing into data/raw/
  python 00_fetch_missing_raw.py --write    # write/overwrite data/raw/ (a real
                                            # re-acquisition -- note this moves
                                            # the data vintage to today)

Notes:
  - Eurostat revises published figures, so CHECK mode reports an agreement
    rate rather than demanding byte equality.
  - gr_financial_expectations_annual.csv is deliberately NOT fetched: it is
    read by no script (a leftover from an early exploration) and is kept in
    the snapshot only as a historical artifact.
"""
import sys
import tempfile
from pathlib import Path

import pandas as pd
from eurostat import fetch

RAW = Path("../data/raw")
SUMMARY = []
WRITE = "--write" in sys.argv
DEST = RAW if WRITE else Path(tempfile.mkdtemp(prefix="fetch_check_"))
print(f"Mode: {'WRITE (updating data/raw/)' if WRITE else f'CHECK (temp dir: {DEST})'}\n")


def out(df, name, rename=None, sort_cols=None):
    if rename:
        df = df.rename(columns=rename)
    keep = [c for c in df.columns if c in (sort_cols or df.columns)]
    df = df[keep] if sort_cols else df
    df.to_csv(DEST / f"{name}.csv", index=False)
    print(f"fetched {name}: {len(df)} rows")
    return df


def compare(name, key_cols, value_col):
    """CHECK mode: value-agreement between fresh fetch and archived snapshot."""
    if WRITE:
        return
    old_p, new_p = RAW / f"{name}.csv", DEST / f"{name}.csv"
    if not old_p.exists():
        print(f"  [no archived copy to compare: {name}]")
        return
    old = pd.read_csv(old_p)
    new = pd.read_csv(new_p)
    m = old.merge(new, on=key_cols, suffixes=("_old", "_new"))
    if m.empty:
        print(f"  [WARN {name}: no overlapping keys between archived and fresh]")
        return
    diff = (m[f"{value_col}_old"] - m[f"{value_col}_new"]).abs()
    exact = (diff == 0).mean()
    within = (diff < 0.05).mean()
    verdict = ("EXACT" if exact == 1.0
               else "within-tolerance" if within == 1.0
               else "DIFFERS")
    print(f"  [{verdict}] {len(m)} overlapping rows: {exact:.1%} byte-identical, "
          f"{within:.1%} within 0.05 (max abs diff {diff.max():.4f}); "
          f"archived-only rows: {len(old) - len(m)}, fresh-only: {len(new) - len(m)}")
    SUMMARY.append((name, verdict, exact, within, diff.max()))


YEARS_FULL = range(2000, 2026)
YEARS_PANEL = range(2015, 2025)

# --- anchored-poverty inputs (Greece only): rates and thresholds at 4 cutoffs ----
r = fetch("ilc_li02", geo=["EL"], time=range(2003, 2026), age=["TOTAL"], sex=["T"],
          unit=["PC"], statinfo=["MED_EI"], rskpovth=["B_40", "B_50", "B_60", "B_70"])
out(r[["time", "rskpovth", "value"]].rename(columns={"value": "rate_pct"}), "anchor_rates")
compare("anchor_rates", ["time", "rskpovth"], "rate_pct")

t = fetch("ilc_li01", geo=["EL"], time=range(2003, 2026), hhcomp=["A1"], unit=["EUR"],
          statinfo=["MED_EI"], rskpovth=["B_40", "B_50", "B_60", "B_70"])
out(t[["time", "rskpovth", "value"]].rename(columns={"value": "threshold_eur"}), "anchor_thresholds")
compare("anchor_thresholds", ["time", "rskpovth"], "threshold_eur")

# --- AROPE, legacy and revised, all reporting countries ------------------------
for code, name, col in [("ilc_peps01", "arope_legacy_all_countries", "arope_legacy"),
                         ("ilc_peps01n", "arope_new_all_countries", "arope_new")]:
    d = fetch(code, time=YEARS_FULL, age=["TOTAL"], sex=["T"], unit=["PC"])
    cols = ["geo", "geo_label", "time", "value"] if "geo_label" in d.columns else ["geo", "time", "value"]
    out(d[cols].rename(columns={"value": col}), name)
    compare(name, ["geo", "time"], col)

# --- cross-country panels, 2015-2024, all reporting countries ------------------
PANELS = [
    ("panel_aic_pps", "nama_10_pc", dict(na_item=["P41"], unit=["CP_PPS_EU27_2020_HAB"]), "aic_pps_pc"),
    # NOTE: the only series that does not reproduce exactly. The archived snapshot
    # stored it rounded to the nearest 100 PPS while the current API returns one
    # decimal; 96.9% of rows match after rounding fresh values to 100, and the
    # remaining ~3% are genuine Eurostat revisions. It feeds only the alternative
    # M3_swap_to_GDP_PPS specification in 11_panel_extended.py -- every headline
    # model uses aic_pps_pc_k (actual individual consumption) instead -- so this
    # difference does not touch any published result.
    ("panel_gdp_pps", "nama_10_pc", dict(na_item=["B1GQ"], unit=["CP_PPS_EU27_2020_HAB"]), "gdp_pps_pc"),
    ("panel_arrears", "ilc_mdes05", dict(hhcomp=["TOTAL"], rskpovth=["TOTAL"], unit=["PC"]), "arrears"),
    ("panel_housing_overburden", "ilc_lvho07a", dict(rskpovth=["TOTAL"], age=["TOTAL"], sex=["T"], unit=["PC"]), "housing_cost_overburden"),
    ("panel_unexpected_expenses", "ilc_mdes04", dict(hhcomp=["TOTAL"], rskpovth=["TOTAL"], unit=["PC"]), "unexpected_expenses"),
    ("panel_arop_before_transfers", "ilc_li09", dict(age=["TOTAL"], sex=["T"], unit=["PC"],
      statinfo=["MED_EI"], rskpovth=["B_60"]), "arop_before_transfers"),
    ("panel_debt_to_income", "tec00104", dict(), "debt_to_income"),
    ("panel_saving_rate", "tec00131", dict(), "saving_rate"),
]
for name, code, filters, col in PANELS:
    d = fetch(code, time=YEARS_PANEL, **filters)
    out(d[["geo", "time", "value"]].rename(columns={"value": col}), name)
    compare(name, ["geo", "time"], col)

# --- unemployment full history (2003-2025), all reporting countries ------------
d = fetch("une_rt_a", time=range(2003, 2026), age=["Y15-74"], sex=["T"], unit=["PC_ACT"])
out(d[["geo", "time", "value"]].rename(columns={"value": "unemployment_rate"}),
    "panel_unemployment_history_2008_2024")
compare("panel_unemployment_history_2008_2024", ["geo", "time"], "unemployment_rate")

# --- financial expectations: monthly consumer-survey balance -> annual mean ----
d = fetch("ei_bsco_m", indic=["BS-FS-NY"], s_adj=["NSA"], unit=["BAL"])
d["year"] = d["time"].astype(str).str.slice(0, 4).astype(int)
ann = (d.groupby(["geo", "year"], as_index=False)["value"].mean()
        .rename(columns={"value": "fin_expectations"}))
ann = ann[(ann.year >= 2015) & (ann.year <= 2024)]
out(ann, "panel_financial_expectations")
compare("panel_financial_expectations", ["geo", "year"], "fin_expectations")

# --- real wage index (derived): compensation per employee, HICP-deflated, 2008=100
comp = fetch("nama_10_lp_ulc", time=YEARS_FULL, na_item=["D1_SAL_PER"], unit=["EUR"])
comp = comp[["geo", "time", "value"]].rename(columns={"value": "comp_eur"})
hicp = fetch("prc_hicp_aind", time=YEARS_FULL, coicop=["CP00"], unit=["INX_A_AVG"])
hicp = hicp[["geo", "time", "value"]].rename(columns={"value": "hicp"})
w = comp.merge(hicp, on=["geo", "time"], how="inner")
base = w[w.time == 2008][["geo", "comp_eur", "hicp"]].rename(
    columns={"comp_eur": "_c08", "hicp": "_h08"})
w = w.merge(base, on="geo", how="inner")
w["real_wage_idx2008"] = 100 * (w.comp_eur / (w.hicp / w._h08)) / w._c08
out(w[["geo", "time", "real_wage_idx2008"]], "real_wage_idx2008")
compare("real_wage_idx2008", ["geo", "time"], "real_wage_idx2008")

if not WRITE and SUMMARY:
    n_exact = sum(1 for _, v, _, _, _ in SUMMARY if v == "EXACT")
    n_within = sum(1 for _, v, _, _, _ in SUMMARY if v == "within-tolerance")
    n_diff = sum(1 for _, v, _, _, _ in SUMMARY if v == "DIFFERS")
    print(f"\n{'=' * 66}")
    print(f"SUMMARY of {len(SUMMARY)} re-acquired files vs the archived snapshot:")
    print(f"  {n_exact} byte-identical on every overlapping row")
    print(f"  {n_within} within 0.05 on every row but not byte-identical")
    print(f"  {n_diff} with at least one row differing by more than 0.05")
    for name, verdict, exact, within, mx in SUMMARY:
        if verdict != "EXACT":
            print(f"    - {name}: {verdict} ({exact:.1%} identical, {within:.1%} within 0.05, max diff {mx:.4f})")

print("\nDone." + ("" if WRITE else " (CHECK mode: data/raw/ untouched)"))
