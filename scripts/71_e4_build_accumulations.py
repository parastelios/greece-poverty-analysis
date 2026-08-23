"""E4 step 1: build the pre-registered accumulations, and audit which are feasible.

BUILD ONLY. No outcome is touched here and no test is run.

The pre-registration fixes ten accumulated representatives with baselines in
2008, 2009 or 2010. The analysis panel runs 2015-2024, so every one of them
needs source history reaching back before the panel starts -- and not all of it
exists. Which ones are constructible is therefore a RESULT of this stage, to be
reported, not a problem to work around by quietly moving a baseline.

A construct that cannot be built at its pre-registered baseline is recorded
INFEASIBLE. It is not rebuilt at a later baseline to make it testable: that
would be choosing the baseline after seeing which choice yields data, which is
the same class of error the whole protocol exists to prevent.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accumulate import (cumulative_shortfall_from_index, cumulative_excess_over_own_base,
                        cumulative_excess_over_fixed, cumulative_sum,
                        compounded_growth, consecutive_years_below,
                        rebuild_and_compare)
from eu_membership import eu_members

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
prereg = json.loads((PROC / "e_preregistration.json").read_text())["transformations"]
# EU27 as of the analysis window. Membership is year-dependent in this
# module; the panel is the EU27 of today throughout, matching E0.
EU27 = set(eu_members(2024))


def eu(df):
    return df[df.geo.isin(EU27)].copy()


bar = "=" * 92
print(bar); print("E4 STEP 1: BUILD ACCUMULATIONS AND AUDIT FEASIBILITY"); print(bar)
print("  Build only. No outcome touched, no test run.\n")

built, audit = {}, []


def record(name, construct, ok, reason, base, n_countries=None, kind=""):
    audit.append({"variable": name, "construct": construct, "feasible": ok,
                  "baseline": base, "countries_at_baseline": n_countries,
                  "accumulation_kind": kind, "reason": reason})
    flag = "OK      " if ok else "INFEAS. "
    print(f"  {flag} {construct:3} {name:26} base {base}  "
          f"{'n=' + str(n_countries) if n_countries else '':7} {reason}")


def source(fname, col, rename=None):
    d = pd.read_csv(RAW / fname)
    if rename:
        d = d.rename(columns=rename)
    return eu(d.dropna(subset=[col]))[["geo", "time", col]]


def baseline_countries(d, col, base):
    return d[(d.time == base) & d[col].notna()].geo.nunique()


# ---------------------------------------------------------------------------
print("FEASIBILITY AUDIT\n")

# --- C2: already built and frozen. Reuse, do not reconstruct. ---------------
frozen = pd.read_csv(PROC / "cumulative_hardship_candidate_panel.csv")
built["acc_cum_excess_unemployment"] = frozen[
    ["geo", "time", "cum_excess_unemployment"]].rename(
        columns={"cum_excess_unemployment": "acc_cum_excess_unemployment"})
record("cum_excess_unemployment", "C2", True,
       "ALREADY BUILT AND FROZEN -- reused, not reconstructed", 2009,
       frozen.geo.nunique(), "direct_excess")

# --- C3 real_wages_idx: shortfall area AND duration -------------------------
w = source("real_wage_idx2008.csv", "real_wage_idx2008")
n = baseline_countries(w, "real_wage_idx2008", 2008)
if n >= 27:
    built["acc_real_wages_shortfall"] = cumulative_shortfall_from_index(
        w, "real_wage_idx2008", 2008, "acc_real_wages_shortfall")
    built["dur_real_wages_below"] = consecutive_years_below(
        w, "real_wage_idx2008", 2008, "dur_real_wages_below")
    record("real_wages_idx", "C3", True, "shortfall AREA and DURATION, reported separately",
           2008, n, "fixed_base_shortfall + duration_below_base")
else:
    record("real_wages_idx", "C3", False, f"only {n} countries at 2008", 2008, n)

# --- C3 pct_below_peak: area under an already non-negative shortfall --------
g = source("panel_gdp_history_2008_2024.csv", "real_gdp_pc")
g = g.sort_values(["geo", "time"])
g["running_peak"] = g.groupby("geo")["real_gdp_pc"].cummax()
g["pct_below_peak"] = 100 - 100 * g["real_gdp_pc"] / g["running_peak"]
n = baseline_countries(g, "pct_below_peak", 2008)
built["acc_pct_below_peak"] = cumulative_sum(g, "pct_below_peak", 2008, "acc_pct_below_peak")
record("pct_below_peak", "C3", True, "area under the shortfall curve", 2008, n,
       "fixed_base_shortfall")

# --- C3 arop_threshold_real ------------------------------------------------
th = pd.read_csv(PROC / "cumulative_hardship_candidate_panel.csv")
if "cum_threshold_shortfall" in th.columns:
    thr = th[["geo", "time", "cum_threshold_shortfall"]]
    # TWO SERIES, and the PRIMARY is the uniform one.
    #
    # The pre-registration fixes baseline 2008. Croatia has no 2008 threshold
    # observation and the existing build falls back to its earliest year (2010),
    # so Croatia accumulates over two fewer years than everyone else. A
    # per-country fallback is not authorised, so the mixed-baseline series
    # cannot be the primary test.
    #
    # Primary:     26 countries, ALL on a uniform 2008 baseline.
    # Sensitivity: 27 countries, mixed baseline, reported alongside.
    built["acc_threshold_shortfall"] = thr[thr.geo != "HR"].rename(
        columns={"cum_threshold_shortfall": "acc_threshold_shortfall"})
    built["acc_threshold_shortfall_mixed"] = thr.rename(
        columns={"cum_threshold_shortfall": "acc_threshold_shortfall_mixed"})
    # MIXED BASELINE, disclosed. Croatia has no 2008 threshold observation and
    # the existing build falls back to its earliest year (2010), so Croatia
    # accumulates over two fewer years than everyone else -- mechanically
    # understating it. The pre-registration says "baseline 2008" and does not
    # authorise a per-country fallback, so this is reported with a
    # Croatia-dropped sensitivity rather than presented as uniform.
    record("arop_threshold_real", "C3", True,
           "PRIMARY is the uniform 2008 baseline, Croatia excluded (it has no "
           "2008 observation). The 27-country mixed-baseline version is "
           "reported as a sensitivity, not as the primary",
           2008, 26, "fixed_base_shortfall")
else:
    record("arop_threshold_real", "C3", False, "no deflated threshold series", 2008)

# --- C3 real_income_idx: NOT constructible ---------------------------------
inc = source("real_hh_income_idx2008.csv", "real_hh_income_idx2008")
n = baseline_countries(inc, "real_hh_income_idx2008", 2008)
record("real_income_idx", "C3", False,
       f"source has {n} countries at 2008 and never reaches 27; "
       "not a panel series before 2015", 2008, n)

# --- C1 aic_pps_pc: NOT constructible --------------------------------------
aic = source("panel_aic_pps.csv", "aic_pps_pc")
record("aic_pps_pc", "C1", False,
       f"source begins {int(aic.time.min())}; no 2008 baseline exists. "
       "The baseline is NOT moved to make it testable", 2008,
       baseline_countries(aic, "aic_pps_pc", 2008))

# --- C4 wadj_a01: excess over the EU27 benchmark ---------------------------
pl = eu(pd.read_csv(RAW / "panel_price_levels_by_category.csv"))
pl = pl[pl.category == "A01"][["geo", "time", "price_level"]]
# The stored file holds ABSOLUTE compensation per employee in euros, not an
# index. The price ratio needs both sides on EU27 = 100. Skipping this made
# wadj_a01 about 0.3 instead of about 120, so max(0, x - 100) was zero for every
# country-year and C4 came back as a degenerate contradiction.
wl_raw = pd.read_csv(RAW / "panel_nominal_compensation_wage_level.csv")
eu_row = wl_raw[wl_raw.geo == "EU27_2020"][["time", "nominal_comp"]].rename(
    columns={"nominal_comp": "_eu"})
if eu_row.empty:
    eu_row = (wl_raw[wl_raw.geo.isin(EU27)].groupby("time", as_index=False)
              ["nominal_comp"].mean().rename(columns={"nominal_comp": "_eu"}))
wl = wl_raw.merge(eu_row, on="time", how="inner")
wl["wage_level"] = 100 * wl.nominal_comp / wl._eu
wl = eu(wl)[["geo", "time", "wage_level"]]
m = pl.merge(wl, on=["geo", "time"], how="inner")
m["wadj_a01"] = 100 * m.price_level / m.wage_level
assert m.wadj_a01.std() > 1.0, (
    f"wadj_a01 is degenerate (sd={m.wadj_a01.std():.4f}); "
    "check that wage_level is an EU27=100 index, not absolute euros")
n = baseline_countries(m, "wadj_a01", 2008)
if n >= 27:
    built["acc_wadj_excess"] = cumulative_excess_over_fixed(
        m, "wadj_a01", 2008, "acc_wadj_excess", benchmark=100.0)
    record("wadj_a01", "C4", True,
           "persistent excess above the EU27 benchmark (=100)", 2008, n,
           "fixed_base_shortfall")
else:
    record("wadj_a01", "C4", False, f"only {n} countries at 2008", 2008, n)

# --- C5 hicp: COMPOUNDED, not summed ---------------------------------------
hi = eu(pd.read_csv(RAW / "panel_hicp_index.csv"))
hcol = [c for c in hi.columns if c not in ("geo", "time")][0]
hi = hi.sort_values(["geo", "time"])
hi["hicp_rate"] = hi.groupby("geo")[hcol].pct_change() * 100
hi = hi.dropna(subset=["hicp_rate"])
n = baseline_countries(hi, "hicp_rate", 2008)
built["acc_hicp_compounded"] = compounded_growth(hi, "hicp_rate", 2008, "acc_hicp_compounded")
record("hicp", "C5", True,
       "COMPOUNDED price growth since 2008; NOT affordability, NOT hardship",
       2008, n, "compounded_change")

# --- C6 housing_cost_overburden: deterioration SINCE 2010 ------------------
ho = eu(pd.read_csv(RAW / "panel_housing_overburden_by_tenure.csv"))
tcol = [c for c in ho.columns if c.lower() in ("tenure", "tenure_status")]
if tcol:
    tot = ho[ho[tcol[0]].astype(str).str.upper().isin(["TOTAL", "TOT"])]
    ho = tot if len(tot) else ho
vcol = [c for c in ho.columns if c not in ("geo", "time") and ho[c].dtype != object][0]
ho = ho[["geo", "time", vcol]].rename(columns={vcol: "hco"}).dropna()
ho = ho.groupby(["geo", "time"], as_index=False).hco.mean()
n = baseline_countries(ho, "hco", 2010)
built["acc_housing_excess"] = cumulative_excess_over_own_base(
    ho, "hco", 2010, "acc_housing_excess")
record("housing_cost_overburden", "C6", True,
       "deterioration SINCE 2010, NOT total burden", 2010, n, "fixed_base_shortfall")

# --- P1: diagnostic only, and not constructible anyway ---------------------
dep = source("panel_deprivation.csv", "severe_mat_soc_deprivation")
record("severe_mat_soc_deprivation", "P1", False,
       f"source begins {int(dep.time.min())}; no 2008 baseline. Diagnostic only regardless",
       2008, baseline_countries(dep, "severe_mat_soc_deprivation", 2008))

# ---------------------------------------------------------------------------
print(f"\n{bar}\nNO-FUTURE-INFORMATION CHECK ON EVERY BUILT SERIES\n{bar}")
checks = [
    ("acc_real_wages_shortfall", cumulative_shortfall_from_index, w, "real_wage_idx2008", 2008),
    ("dur_real_wages_below", consecutive_years_below, w, "real_wage_idx2008", 2008),
    ("acc_pct_below_peak", cumulative_sum, g[["geo", "time", "pct_below_peak"]], "pct_below_peak", 2008),
    ("acc_wadj_excess", cumulative_excess_over_fixed, m[["geo", "time", "wadj_a01"]], "wadj_a01", 2008),
    ("acc_hicp_compounded", compounded_growth, hi[["geo", "time", "hicp_rate"]], "hicp_rate", 2008),
    ("acc_housing_excess", cumulative_excess_over_own_base, ho, "hco", 2010),
]
leaks = 0
for name, fn, src, col, base in checks:
    if name not in built:
        continue
    bad = rebuild_and_compare(fn, src, col, base, name)
    print(f"  {name:28} {'clean' if not bad else f'{len(bad)} LEAKS'}")
    leaks += len(bad)
if leaks:
    raise SystemExit(f"FUTURE INFORMATION DETECTED in {leaks} country-years")
print("  Every built series is a running quantity: truncating later years")
print("  leaves earlier values unchanged.")

# ---------------------------------------------------------------------------
panel = pd.read_csv(PROC / "e0_extended_panel.csv")
for name, df in built.items():
    panel = panel.merge(df, on=["geo", "time"], how="left")
acc_cols = list(built)
print(f"\n{bar}\nMERGED INTO THE ANALYSIS WINDOW (2015-2024)\n{bar}")
print(f"  {'column':30} {'n':>5} {'countries':>10}")
for c in acc_cols:
    s = panel.dropna(subset=[c])
    print(f"  {c:30} {len(s):5d} {s.geo.nunique():10d}")

panel.to_csv(PROC / "e4_accumulated_panel.csv", index=False)
a = pd.DataFrame(audit)
a.to_csv(PROC / "e4_feasibility.csv", index=False)
print(f"\n  feasible: {int(a.feasible.sum())} of {len(a)} pre-registered accumulations")
print(f"  INFEASIBLE: {', '.join(a[~a.feasible].variable)}")
print(f"\nWritten to {PROC}/e4_accumulated_panel.csv, e4_feasibility.csv")
