"""Automated verification that the pipeline's outputs match the published claims.

Run after `make build` (or any pipeline rerun) to confirm that every headline
number quoted in the three published documents is still what the pipeline
actually produces. Exits non-zero if any check fails, so it can gate a rebuild.

This is deliberately a check of PUBLISHED CLAIMS against PIPELINE OUTPUTS, not
a unit-test of internal functions: the failure mode it exists to catch is a
document quietly drifting out of sync with the data behind it.
"""
import sys
from pathlib import Path

import pandas as pd

OUT = Path("../data/processed")
failures, checks = [], 0


def check(label, actual, expected, tol=0.05):
    global checks
    checks += 1
    if actual is None:
        failures.append(f"{label}: MISSING (could not compute)")
        print(f"  MISSING  {label}")
        return
    ok = abs(float(actual) - float(expected)) <= tol
    status = "ok      " if ok else "MISMATCH"
    print(f"  {status} {label}: {float(actual):.2f} (published {expected})")
    if not ok:
        failures.append(f"{label}: pipeline {float(actual):.4f} vs published {expected}")


def check_str(label, actual, expected):
    global checks
    checks += 1
    ok = str(actual) == str(expected)
    print(f"  {'ok      ' if ok else 'MISMATCH'} {label}: {actual} (published {expected})")
    if not ok:
        failures.append(f"{label}: pipeline {actual!r} vs published {expected!r}")


print("== Headline gaps (2025 single year) ==")
ad = pd.read_csv(OUT / "analysis_dataset.csv")
g25 = ad[ad.year == 2025].iloc[0]
check("Greece subjective poverty 2025", g25.gr_subjective_poverty, 67.2)
check("Greece AROP 2025", g25.gr_arop, 19.6)
check("AROP gap 2025", g25.gr_subjective_poverty - g25.gr_arop, 47.6)
check("AROPE gap 2025", g25.gr_subjective_poverty - g25.gr_arope, 39.7)

print("\n== Gap-closing ladder (common 2015-2024 window) ==")
w = ad[(ad.year >= 2015) & (ad.year <= 2024)]
check("ladder step 1: raw AROP gap", (w.gr_subjective_poverty - w.gr_arop).mean(), 52.6, tol=0.1)
check("ladder step 2: raw AROPE gap", (w.gr_subjective_poverty - w.gr_arope).mean(), 41.5, tol=0.1)
s2 = pd.read_csv(OUT / "cumulative_hardship_stage2_bridge.csv")
for step, expected in [(3, 25.6), (4, 11.6), (5, 3.9), (6, -0.8)]:
    check(f"ladder step {step}", s2[s2.step == step].greece_value.iloc[0], expected, tol=0.1)

print("\n== Scorecard (out-of-sample residuals) ==")
sc = pd.read_csv(OUT / "model_scorecard_ltu.csv")
for key, label, expected, exp_rank in [("C_baseline", "C", 11.6, "1/27"),
                                        ("C_LTU_swap", "C-LTU", 3.9, "6/27")]:
    row = sc[sc.model == key]
    check(f"Model {label} OOS residual",
          row.gr_avg_residual_oos.iloc[0] if len(row) else None, expected, tol=0.1)
    check_str(f"Model {label} OOS rank", row.gr_rank_oos.iloc[0] if len(row) else None, exp_rank)

print("\n== Correlation table: FDR survivor counts (19 variables) ==")
cr = pd.read_csv(OUT / "correlations_robustness.csv")
check("n variables in correlation table", len(cr), 19, tol=0)
check("FDR survivors, level", cr.survives_fdr_level.sum(), 17, tol=0)
check("FDR survivors, first-difference", cr.survives_fdr_firstdiff.sum(), 16, tol=0)
check("FDR survivors, detrended", cr.survives_fdr_detrended.sum(), 17, tol=0)
ltu = cr[cr.variable.str.contains("Long-term unemployment")].iloc[0]
check("LTU level r", ltu.r_level, 0.93, tol=0.01)
check("LTU first-difference r", ltu.r_firstdiff, 0.92, tol=0.01)
check("LTU detrended r", ltu.r_detrended, 0.86, tol=0.01)

print("\n== Cumulative-hardship FDR + nested selection ==")
fdr = pd.read_csv(OUT / "cumulative_hardship_fdr_correction.csv")
check("candidates in screening family", len(fdr), 18, tol=0)
ceu = fdr[fdr.variable == "cum_excess_unemployment"].iloc[0]
check("cum_excess_unemployment FDR-adjusted p", ceu.p_fdr_bh, 0.0024, tol=0.0005)
check("FDR survivors in family", int(fdr.significant_after_fdr.sum()), 2, tol=0)

nf = pd.read_csv(OUT / "nested_selection_validation_folds.csv")
check("nested-selection folds", len(nf), 27, tol=0)
check("folds selecting cum_excess_unemployment",
      (nf.selected_first == "cum_excess_unemployment").sum(), 25, tol=0)
check("cum_excess_unemployment worst-case raw p across folds",
      nf.cum_excess_unemployment_p.max(), 0.0064, tol=0.0005)
check("folds whose winner survives within-fold FDR",
      int(nf.selected_survives_fdr_within_fold.sum()), 26, tol=0)
check("nested CV: Greece mean residual",
      nf[nf.fold_held_out == "EL"].nested_mean_residual.iloc[0], 2.70, tol=0.05)
check("nested CV: Greece mean absolute error",
      nf[nf.fold_held_out == "EL"].nested_mean_abs_residual.iloc[0], 4.51, tol=0.05)
_rank = nf.nested_mean_abs_residual.rank(method="min")[nf.fold_held_out == "EL"].iloc[0]
check("nested CV: Greece prediction-error rank (of 27)", _rank, 19, tol=0)
check("nested CV: countries predicted worse than Greece", 27 - _rank, 8, tol=0)

print("\n== Work-effort squeeze (salaried workers, 2025) ==")
st = pd.read_csv(OUT / "work_effort_status_latest.csv")
sal = st[(st.wstatus == "SAL") & (st.geo == "EL")].iloc[0]
check("Greece salaried AROP", sal.arop, 5.7)
check("Greece salaried AROPE", sal.arope, 12.5)
check("Greece salaried subjective poverty", sal.subjective_poverty, 59.5)
cc = pd.read_csv(OUT / "work_effort_cross_country_latest.csv")
el = cc[cc.geo == "EL"].iloc[0]
check("Greece weekly hours", el.weekly_actual_hours, 39.8)
check("Greece hourly compensation (PPS)", el.hourly_compensation_pps, 14.2)
check("Greece work-effort squeeze index", el.work_effort_squeeze, 230.5, tol=0.2)
sys.path.insert(0, ".")
from eu_membership import eu_members  # noqa: E402
members = set(eu_members(2025))
sal_hours = cc[cc.geo.isin(members)].dropna(subset=["employee_weekly_hours"]).copy()
sal_hours["rank"] = sal_hours.employee_weekly_hours.rank(ascending=False, method="min")
check("Greece salaried hours EU rank (member states only)",
      sal_hours[sal_hours.geo == "EL"]["rank"].iloc[0], 7, tol=0)

print("\n== Reporting-heterogeneity robustness ==")
pl = pd.read_csv(OUT / "reporting_style_v2_country_placebo.csv")
check("Greece placebo rank (1 = largest of 27)", pl[pl.geo == "EL"]["rank"].iloc[0], 1, tol=0)
check("randomization-inference p-value", 1 / len(pl), 0.037, tol=0.002)

print(f"\n{'=' * 60}")
if failures:
    print(f"FAILED: {len(failures)} of {checks} checks disagree with published values:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print(f"PASSED: all {checks} published headline values reproduce from the pipeline.")
