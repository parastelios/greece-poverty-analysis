"""Work-effort squeeze checkpoint.

Question: does Greece combine unusually long working time with unusually low
hourly reward, and does that combination help explain subjective poverty?

This is a checkpoint only. It fetches fresh Eurostat data, writes standalone
processed tables and preview figures, and does not modify any published report.

Design:
  1. Verify the headline LFS hours comparison and decompose it by work-time and
     employment status. The headline combines full- and part-time workers and
     refers to actual hours in the main job, so it is not treated as a pure
     measure of individual effort.
  2. Use national-accounts compensation per hour worked (not annual salary
     divided by unrelated survey hours) for the matched hourly-reward measure.
     PPS levels support cross-country purchasing-power comparisons; HICP-
     deflated EUR levels support within-country change since 2008.
  3. Test employed-only subjective poverty, AROP and AROPE directly.
  4. Add each candidate one at a time to Model C-LTU, apply BH-FDR across the
     pre-specified candidate family, and run leave-one-country-out validation.
  5. Separately test the employed-only outcome against employed AROP + year FE.

Important interpretation limits:
  - Compensation per hour is gross employer compensation, not take-home pay.
  - LFS actual weekly hours cover the main job and mix full-/part-time workers.
  - The work-effort squeeze is descriptive: high hours do not cause poverty.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "data" / "processed" / ".matplotlib"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import pearsonr
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

from eurostat import fetch
from eu_membership import eu_members


RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
FIG = OUT / "work_effort_figures"
YEARS = list(range(2003, 2026))
MEMBERS = sorted(eu_members(2025))

RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)


def save_raw(df, name):
    df.to_csv(RAW / name, index=False)
    return df


def bh_adjust(df, p_col="p_value_raw"):
    out = df.copy()
    mask = out[p_col].notna()
    out["p_fdr_bh"] = np.nan
    out["fdr_significant_05"] = False
    if mask.any():
        reject, adjusted, _, _ = multipletests(out.loc[mask, p_col], method="fdr_bh")
        out.loc[mask, "p_fdr_bh"] = adjusted
        out.loc[mask, "fdr_significant_05"] = reject
    return out


def country_loo(formula, data, outcome, candidate):
    rows = []
    for geo in sorted(data.geo.unique()):
        train = data[data.geo != geo]
        test = data[data.geo == geo].copy()
        model = smf.ols(formula, data=train).fit(
            cov_type="cluster", cov_kwds={"groups": train.geo}
        )
        test["prediction_loo"] = model.predict(test)
        test["residual_loo"] = test[outcome] - test["prediction_loo"]
        rows.append({
            "geo": geo,
            "avg_residual_loo": test.residual_loo.mean(),
            "candidate_coef": model.params.get(candidate, np.nan),
            "candidate_p": model.pvalues.get(candidate, np.nan),
        })
    loo = pd.DataFrame(rows).sort_values("avg_residual_loo", ascending=False).reset_index(drop=True)
    loo["rank"] = loo.index + 1
    return loo


def add_eu_index(df, value_col, out_col):
    eu = df[df.geo == "EU27_2020"][["time", value_col]].rename(columns={value_col: "_eu"})
    out = df.merge(eu, on="time", how="left")
    out[out_col] = 100 * out[value_col] / out["_eu"]
    return out.drop(columns="_eu")


# ---------------------------------------------------------------- fresh official data pulls
lfs = save_raw(
    fetch(
        "lfsa_ewhan2", geo=MEMBERS + ["EU27_2020"], time=range(2008, 2026),
        nace_r2=["TOTAL"], age=["Y20-64"], sex=["T"], unit=["HR"],
        wstatus=["EMP", "SAL", "SELF"], worktime=["TOTAL", "FT", "PT"],
    ),
    "work_effort_lfs_hours_fresh.csv",
)

lp = save_raw(
    fetch(
        "nama_10_lp_ulc", geo=MEMBERS + ["EU27_2020"], time=range(2000, 2025),
        na_item=["D1_SAL_HW", "HW_EMP", "RLPR_HW", "NLPR_HW"],
    ),
    "work_effort_labour_productivity_fresh.csv",
)

na_emp = save_raw(
    fetch(
        "nama_10_a10_e", geo=MEMBERS + ["EU27_2020"], time=range(2000, 2025),
        nace_r2=["TOTAL"], na_item=["SAL_DC"], unit=["THS_HW", "THS_PER"],
    ),
    "work_effort_employee_hours_fresh.csv",
)

subj_work = save_raw(
    fetch(
        "ilc_sbjp03", geo=MEMBERS + ["EU27_2020"], time=YEARS,
        wstatus=["EMP", "SAL", "NSAL", "POP"], unit=["PC"],
    ),
    "work_effort_subjective_poverty_status_fresh.csv",
)

arop_work = save_raw(
    fetch(
        "ilc_iw01", geo=MEMBERS + ["EU27_2020"], time=YEARS,
        wstatus=["EMP", "SAL", "NSAL"], sex=["T"], age=["Y_GE18"], unit=["PC"],
    ),
    "work_effort_inwork_arop_fresh.csv",
)

arope_work = save_raw(
    fetch(
        "ilc_peps02n", geo=MEMBERS + ["EU27_2020"], time=range(2015, 2026),
        wstatus=["EMP", "SAL", "NSAL"], sex=["T"], age=["Y_GE18"], unit=["PC"],
    ),
    "work_effort_employed_arope_fresh.csv",
)

hicp = save_raw(
    fetch(
        "prc_hicp_aind", geo=MEMBERS + ["EU27_2020"], time=range(2000, 2025),
        coicop=["CP00"], unit=["INX_A_AVG"],
    ),
    "work_effort_hicp_fresh.csv",
)


# ---------------------------------------------------------------- construct working-time series
hours = lfs[["geo", "time", "wstatus", "worktime", "value"]].rename(columns={"value": "weekly_actual_hours"})
hours.to_csv(OUT / "work_effort_hours_by_status.csv", index=False)

headline_hours = hours[(hours.wstatus == "EMP") & (hours.worktime == "TOTAL")][
    ["geo", "time", "weekly_actual_hours"]
]
headline_hours = add_eu_index(headline_hours, "weekly_actual_hours", "weekly_hours_eu100")

ft_hours = hours[(hours.wstatus == "EMP") & (hours.worktime == "FT")][
    ["geo", "time", "weekly_actual_hours"]
].rename(columns={"weekly_actual_hours": "full_time_weekly_hours"})
self_hours = hours[(hours.wstatus == "SELF") & (hours.worktime == "TOTAL")][
    ["geo", "time", "weekly_actual_hours"]
].rename(columns={"weekly_actual_hours": "self_employed_weekly_hours"})
employee_lfs_hours = hours[(hours.wstatus == "SAL") & (hours.worktime == "TOTAL")][
    ["geo", "time", "weekly_actual_hours"]
].rename(columns={"weekly_actual_hours": "employee_weekly_hours"})
employee_lfs_hours = add_eu_index(employee_lfs_hours, "employee_weekly_hours", "employee_weekly_hours_eu100")

annual = na_emp.pivot_table(index=["geo", "time"], columns="unit", values="value").reset_index()
annual["annual_hours_per_employee"] = annual["THS_HW"] / annual["THS_PER"]
annual = add_eu_index(annual, "annual_hours_per_employee", "annual_employee_hours_eu100")


# ---------------------------------------------------------------- hourly compensation measures
comp_eur = lp[(lp.na_item == "D1_SAL_HW") & (lp.unit == "EUR")][
    ["geo", "time", "value"]
].rename(columns={"value": "hourly_compensation_eur"})
comp_nac = lp[(lp.na_item == "D1_SAL_HW") & (lp.unit == "NAC")][
    ["geo", "time", "value"]
].rename(columns={"value": "hourly_compensation_nac"})
comp_pps = lp[(lp.na_item == "D1_SAL_HW") & (lp.unit == "PPS_EU27_2020")][
    ["geo", "time", "value"]
].rename(columns={"value": "hourly_compensation_pps"})
comp_pps = add_eu_index(comp_pps, "hourly_compensation_pps", "hourly_comp_pps_eu100")

hicp_s = hicp[["geo", "time", "value"]].rename(columns={"value": "hicp"})
comp = comp_eur.merge(comp_nac, on=["geo", "time"], how="outer").merge(
    comp_pps, on=["geo", "time"], how="outer"
).merge(hicp_s, on=["geo", "time"], how="left")
base = comp[comp.time == 2008][["geo", "hourly_compensation_nac", "hicp"]].rename(
    columns={"hourly_compensation_nac": "_comp_2008", "hicp": "_hicp_2008"}
)
comp = comp.merge(base, on="geo", how="left")
comp["real_hourly_comp_idx2008"] = 100 * (
    comp.hourly_compensation_nac / (comp.hicp / comp._hicp_2008)
) / comp._comp_2008
comp = comp.drop(columns=["_comp_2008", "_hicp_2008"])

comp = comp.sort_values(["geo", "time"])
comp["real_hourly_shortfall"] = (100 - comp.real_hourly_comp_idx2008).clip(lower=0)
comp.loc[comp.time < 2008, "real_hourly_shortfall"] = 0
comp["cum_real_hourly_shortfall"] = comp.groupby("geo").real_hourly_shortfall.cumsum()
comp["_below_2008"] = ((comp.time >= 2008) & (comp.real_hourly_comp_idx2008 < 100)).astype(int)
comp["years_hourly_pay_below_2008"] = comp.groupby("geo")._below_2008.cumsum()
comp = comp.drop(columns="_below_2008")

effort = headline_hours.merge(comp, on=["geo", "time"], how="inner").merge(
    employee_lfs_hours, on=["geo", "time"], how="left"
).merge(
    annual[["geo", "time", "annual_hours_per_employee", "annual_employee_hours_eu100"]],
    on=["geo", "time"], how="left",
)
effort["work_effort_squeeze"] = 100 * effort.weekly_hours_eu100 / effort.hourly_comp_pps_eu100
effort["employee_lfs_effort_squeeze"] = 100 * effort.employee_weekly_hours_eu100 / effort.hourly_comp_pps_eu100
effort["matched_employee_effort_squeeze"] = 100 * effort.annual_employee_hours_eu100 / effort.hourly_comp_pps_eu100
effort["low_hourly_reward_eu"] = 100 - effort.hourly_comp_pps_eu100
effort.to_csv(OUT / "work_effort_panel.csv", index=False)


# ---------------------------------------------------------------- employed-only hardship panel
subj_emp = subj_work[subj_work.wstatus == "EMP"][["geo", "time", "value"]].rename(
    columns={"value": "subjective_poverty_employed"}
)
subj_pop = subj_work[subj_work.wstatus == "POP"][["geo", "time", "value"]].rename(
    columns={"value": "subjective_poverty_population_status_table"}
)
arop_emp = arop_work[arop_work.wstatus == "EMP"][["geo", "time", "value"]].rename(
    columns={"value": "arop_employed"}
)
arope_emp = arope_work[arope_work.wstatus == "EMP"][["geo", "time", "value"]].rename(
    columns={"value": "arope_employed"}
)
employed = subj_emp.merge(arop_emp, on=["geo", "time"], how="outer").merge(
    arope_emp, on=["geo", "time"], how="outer"
).merge(subj_pop, on=["geo", "time"], how="left").merge(
    effort, on=["geo", "time"], how="left"
)
employed["employed_subjective_minus_arop"] = employed.subjective_poverty_employed - employed.arop_employed
employed["employed_subjective_minus_arope"] = employed.subjective_poverty_employed - employed.arope_employed
employed = employed[employed.geo.isin(MEMBERS + ["EU27_2020"])].copy()
employed.to_csv(OUT / "work_effort_employed_hardship_panel.csv", index=False)


# ---------------------------------------------------------------- descriptive latest-year table
latest_common = int(min(headline_hours.time.max(), comp.dropna(subset=["hourly_compensation_pps"]).time.max()))
snapshot = effort[effort.time == latest_common].merge(ft_hours, on=["geo", "time"], how="left").merge(
    self_hours, on=["geo", "time"], how="left"
)
member_mask = snapshot.geo.isin(MEMBERS)
for col, asc in [
    ("weekly_actual_hours", False),
    ("hourly_compensation_pps", True),
    ("work_effort_squeeze", False),
    ("matched_employee_effort_squeeze", False),
]:
    snapshot[f"rank_{col}"] = pd.Series(pd.NA, index=snapshot.index, dtype="Int64")
    snapshot.loc[member_mask, f"rank_{col}"] = snapshot.loc[member_mask, col].rank(
        method="min", ascending=asc
    ).astype("Int64")
snapshot.to_csv(OUT / "work_effort_cross_country_latest.csv", index=False)

hardship_latest_year = int(employed.dropna(subset=["subjective_poverty_employed"]).time.max())
hardship_latest = employed[employed.time == hardship_latest_year].copy()
hardship_member_mask = hardship_latest.geo.isin(MEMBERS)
for col in ["subjective_poverty_employed", "arop_employed", "arope_employed"]:
    hardship_latest[f"rank_{col}_worst"] = pd.Series(pd.NA, index=hardship_latest.index, dtype="Int64")
    hardship_latest.loc[hardship_member_mask, f"rank_{col}_worst"] = hardship_latest.loc[
        hardship_member_mask, col
    ].rank(method="min", ascending=False).astype("Int64")
hardship_latest.to_csv(OUT / "work_effort_employed_hardship_latest.csv", index=False)

# Detailed status table (all employed, salaried, self-employed), keeping the subjective,
# AROP and AROPE concepts side by side. This exposes whether the finding is driven only by
# Greece's comparatively large self-employed population.
status_latest = subj_work[
    (subj_work.time == hardship_latest_year) & subj_work.wstatus.isin(["EMP", "SAL", "NSAL"])
][["geo", "wstatus", "value"]].rename(columns={"value": "subjective_poverty"})
status_latest = status_latest.merge(
    arop_work[(arop_work.time == hardship_latest_year) & arop_work.wstatus.isin(["EMP", "SAL", "NSAL"])][
        ["geo", "wstatus", "value"]
    ].rename(columns={"value": "arop"}), on=["geo", "wstatus"], how="left",
).merge(
    arope_work[(arope_work.time == hardship_latest_year) & arope_work.wstatus.isin(["EMP", "SAL", "NSAL"])][
        ["geo", "wstatus", "value"]
    ].rename(columns={"value": "arope"}), on=["geo", "wstatus"], how="left",
)
status_latest["time"] = hardship_latest_year
for status in ["EMP", "SAL", "NSAL"]:
    mask = (status_latest.wstatus == status) & status_latest.geo.isin(MEMBERS)
    for measure in ["subjective_poverty", "arop", "arope"]:
        rank_col = f"{measure}_rank_worst"
        status_latest.loc[mask, rank_col] = status_latest.loc[mask, measure].rank(
            method="min", ascending=False
        )
status_latest.to_csv(OUT / "work_effort_status_latest.csv", index=False)


# ---------------------------------------------------------------- Greece time-series correlations
gr = employed[employed.geo == "EL"].sort_values("time")
corr_candidates = [
    "weekly_actual_hours", "annual_hours_per_employee", "hourly_compensation_pps",
    "real_hourly_comp_idx2008", "work_effort_squeeze", "employee_lfs_effort_squeeze",
    "matched_employee_effort_squeeze", "cum_real_hourly_shortfall",
    "years_hourly_pay_below_2008",
]
corr_rows = []
for var in corr_candidates:
    d = gr[["time", "subjective_poverty_employed", var]].dropna().sort_values("time")
    if len(d) < 5:
        continue
    r_level, p_level = pearsonr(d[var], d.subjective_poverty_employed)
    dd = d[["subjective_poverty_employed", var]].diff().dropna()
    if len(dd) >= 4 and dd[var].nunique() > 1 and dd.subjective_poverty_employed.nunique() > 1:
        r_diff, p_diff = pearsonr(dd[var], dd.subjective_poverty_employed)
    else:
        r_diff, p_diff = np.nan, np.nan
    corr_rows.append({
        "variable": var, "n_level": len(d), "r_level": r_level, "p_level": p_level,
        "n_first_diff": len(dd), "r_first_diff": r_diff, "p_first_diff": p_diff,
    })
pd.DataFrame(corr_rows).to_csv(OUT / "work_effort_greece_correlations.csv", index=False)


# ---------------------------------------------------------------- total-population Model C-LTU battery
panel = pd.read_csv(OUT / "panel_extended.csv")
ltu = pd.read_csv(RAW / "panel_long_term_unemployment.csv")[["geo", "time", "ltu_rate"]]
panel = panel.merge(ltu, on=["geo", "time"], how="left")
panel = panel.merge(effort, on=["geo", "time"], how="left")

base_vars = [
    "ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
    "housing_cost_overburden", "arrears", "unexpected_expenses",
]
candidates = {
    "weekly_actual_hours": "LFS actual weekly hours, all employed",
    "annual_hours_per_employee": "National-accounts annual hours per employee",
    "hourly_compensation_pps": "Hourly compensation, purchasing-power standard",
    "real_hourly_comp_idx2008": "Real hourly compensation, own 2008=100",
    "work_effort_squeeze": "Work-effort squeeze: relative hours / relative PPS hourly compensation",
    "employee_lfs_effort_squeeze": "Employee-only LFS hours / relative PPS hourly compensation",
    "matched_employee_effort_squeeze": "Matched national-accounts employee hours / PPS hourly compensation",
    "cum_real_hourly_shortfall": "Cumulative real hourly-compensation shortfall since 2008",
    "years_hourly_pay_below_2008": "Years hourly compensation remained below own 2008 level",
}

model_rows = []
loo_files = {}
for var, label in candidates.items():
    cols = base_vars + [var, "subjective_poverty", "geo", "time"]
    d = panel[cols].dropna().copy()
    formula = "subjective_poverty ~ " + " + ".join(base_vars + [var]) + " + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d.geo})
    loo = country_loo(formula, d, "subjective_poverty", var)
    loo_files[var] = loo
    el = loo[loo.geo == "EL"].iloc[0]
    model_rows.append({
        "variable": var, "label": label, "n_obs": len(d), "n_countries": d.geo.nunique(),
        "r2": model.rsquared, "coef": model.params[var], "se": model.bse[var],
        "p_value_raw": model.pvalues[var], "greece_oos_residual": el.avg_residual_loo,
        "greece_oos_rank": int(el["rank"]),
    })

models = bh_adjust(pd.DataFrame(model_rows)).sort_values("p_fdr_bh")
models.to_csv(OUT / "work_effort_model_battery.csv", index=False)

for var, loo in loo_files.items():
    if bool(models.set_index("variable").loc[var, "fdr_significant_05"]):
        loo.to_csv(OUT / f"work_effort_loo_{var}.csv", index=False)


# ---------------------------------------------------------------- employed-only model battery
emp_candidates = list(candidates)
emp_rows = []
for var in emp_candidates:
    d = employed[employed.geo.isin(MEMBERS)][
        ["geo", "time", "subjective_poverty_employed", "arop_employed", var]
    ].dropna().copy()
    if d.geo.nunique() < 10 or len(d) < 50:
        continue
    formula = f"subjective_poverty_employed ~ arop_employed + {var} + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d.geo})
    loo = country_loo(formula, d, "subjective_poverty_employed", var)
    el = loo[loo.geo == "EL"].iloc[0]
    emp_rows.append({
        "variable": var, "n_obs": len(d), "n_countries": d.geo.nunique(), "r2": model.rsquared,
        "coef": model.params[var], "se": model.bse[var], "p_value_raw": model.pvalues[var],
        "greece_oos_residual": el.avg_residual_loo, "greece_oos_rank": int(el["rank"]),
    })
emp_models = bh_adjust(pd.DataFrame(emp_rows)).sort_values("p_fdr_bh")
emp_models.to_csv(OUT / "work_effort_employed_model_battery.csv", index=False)


# ---------------------------------------------------------------- standalone AROP bridge battery
# Put each work candidate on the same simple footing as the project's Stage 1 bridge:
# subjective poverty ~ AROP + candidate + year FE, excluding Greece for its OOS residual.
stage1_rows = []
for var, label in candidates.items():
    d = panel[["geo", "time", "subjective_poverty", "arop", var]].dropna().copy()
    formula = f"subjective_poverty ~ arop + {var} + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d.geo})
    loo = country_loo(formula, d, "subjective_poverty", var)
    el = loo[loo.geo == "EL"].iloc[0]
    stage1_rows.append({
        "variable": var, "label": label, "n_obs": len(d), "n_countries": d.geo.nunique(),
        "r2": model.rsquared, "coef": model.params[var], "p_value_raw": model.pvalues[var],
        "greece_oos_residual": el.avg_residual_loo, "greece_oos_rank": int(el["rank"]),
        # 52.6 = Greece's average raw subjective-minus-AROP gap over the same 2015-2024
        # window as this panel's OOS residuals -- NOT the single-year 2025 gap (47.6),
        # so the "points closed" comparison shares one window with the residual it's
        # compared against (same convention as 38_cumulative_hardship.py's ladder).
        "points_of_arop_gap_closed": 52.6 - el.avg_residual_loo,
    })
stage1 = bh_adjust(pd.DataFrame(stage1_rows)).sort_values("p_fdr_bh")
stage1.to_csv(OUT / "work_effort_stage1_arop_bridge.csv", index=False)


# ---------------------------------------------------------------- interaction and collinearity check
# Standardise the two interpretable components and test whether their interaction adds
# anything beyond the main effects. Positive z_low_pay means lower hourly compensation.
ix = panel.dropna(subset=base_vars + ["subjective_poverty", "weekly_actual_hours", "hourly_compensation_pps"]).copy()
ix["z_hours"] = (ix.weekly_actual_hours - ix.weekly_actual_hours.mean()) / ix.weekly_actual_hours.std()
ix["z_low_pay"] = -(ix.hourly_compensation_pps - ix.hourly_compensation_pps.mean()) / ix.hourly_compensation_pps.std()
ix["hours_x_low_pay"] = ix.z_hours * ix.z_low_pay
ix_formula = "subjective_poverty ~ " + " + ".join(base_vars + ["z_hours", "z_low_pay", "hours_x_low_pay"]) + " + C(time)"
ix_model = smf.ols(ix_formula, data=ix).fit(cov_type="cluster", cov_kwds={"groups": ix.geo})

vif_x = ix[base_vars + ["z_hours", "z_low_pay", "hours_x_low_pay"]].dropna()
vif_design = smf.add_constant(vif_x, has_constant="add") if hasattr(smf, "add_constant") else None
# statsmodels.formula.api does not expose add_constant in every release.
if vif_design is None:
    import statsmodels.api as sm
    vif_design = sm.add_constant(vif_x, has_constant="add")
vif = pd.DataFrame({
    "variable": vif_design.columns,
    "vif": [variance_inflation_factor(vif_design.values, i) for i in range(vif_design.shape[1])],
})
pd.DataFrame([{
    "n_obs": len(ix), "n_countries": ix.geo.nunique(), "r2": ix_model.rsquared,
    "interaction_coef": ix_model.params["hours_x_low_pay"],
    "interaction_p": ix_model.pvalues["hours_x_low_pay"],
    "hours_coef": ix_model.params["z_hours"], "hours_p": ix_model.pvalues["z_hours"],
    "low_pay_coef": ix_model.params["z_low_pay"], "low_pay_p": ix_model.pvalues["z_low_pay"],
}]).to_csv(OUT / "work_effort_interaction_test.csv", index=False)
vif.to_csv(OUT / "work_effort_interaction_vif.csv", index=False)


# ---------------------------------------------------------------- incremental test on final cumulative model
# Recreate the agreed cumulative excess-unemployment variable from the fresh/full history,
# then ask whether the work-effort squeeze adds anything after the checkpoint's strongest
# existing mechanism. This is intentionally separate from the pre-specified FDR family.
unemp = pd.read_csv(RAW / "panel_unemployment_history_2008_2024.csv")[
    ["geo", "time", "unemployment_rate"]
].sort_values(["geo", "time"])
u0 = unemp[unemp.time == 2009][["geo", "unemployment_rate"]].rename(
    columns={"unemployment_rate": "_u2009"}
)
unemp = unemp.merge(u0, on="geo", how="left")
unemp["excess_unemployment"] = (unemp.unemployment_rate - unemp._u2009).clip(lower=0)
unemp["cum_excess_unemployment"] = unemp.groupby("geo").excess_unemployment.cumsum()
panel = panel.merge(unemp[["geo", "time", "cum_excess_unemployment"]], on=["geo", "time"], how="left")

final_rows = []
for label, extras in [
    ("C-LTU", []),
    ("C-LTU + work-effort squeeze", ["work_effort_squeeze"]),
    ("C-LTU + matched employee effort squeeze", ["matched_employee_effort_squeeze"]),
    ("C-LTU + cumulative real hourly-pay shortfall", ["cum_real_hourly_shortfall"]),
    ("C-LTU + years hourly pay below 2008", ["years_hourly_pay_below_2008"]),
    ("C-LTU + cumulative excess unemployment", ["cum_excess_unemployment"]),
    ("C-LTU + cumulative excess unemployment + work-effort squeeze",
     ["cum_excess_unemployment", "work_effort_squeeze"]),
    ("C-LTU + cumulative excess unemployment + matched employee effort squeeze",
     ["cum_excess_unemployment", "matched_employee_effort_squeeze"]),
    ("C-LTU + cumulative excess unemployment + cumulative real hourly-pay shortfall",
     ["cum_excess_unemployment", "cum_real_hourly_shortfall"]),
    ("C-LTU + cumulative excess unemployment + years hourly pay below 2008",
     ["cum_excess_unemployment", "years_hourly_pay_below_2008"]),
]:
    vars_ = base_vars + extras
    d = panel.dropna(subset=vars_ + ["subjective_poverty"]).copy()
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    model = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d.geo})
    loo = country_loo(formula, d, "subjective_poverty", extras[-1] if extras else "ltu_rate")
    el = loo[loo.geo == "EL"].iloc[0]
    final_rows.append({
        "model": label, "n_obs": len(d), "n_countries": d.geo.nunique(), "r2": model.rsquared,
        "greece_oos_residual": el.avg_residual_loo, "greece_oos_rank": int(el["rank"]),
        "headline_squeeze_coef": model.params.get("work_effort_squeeze", np.nan),
        "headline_squeeze_p": model.pvalues.get("work_effort_squeeze", np.nan),
        "matched_squeeze_coef": model.params.get("matched_employee_effort_squeeze", np.nan),
        "matched_squeeze_p": model.pvalues.get("matched_employee_effort_squeeze", np.nan),
        "cum_unemployment_coef": model.params.get("cum_excess_unemployment", np.nan),
        "cum_unemployment_p": model.pvalues.get("cum_excess_unemployment", np.nan),
        "cum_hourly_pay_shortfall_coef": model.params.get("cum_real_hourly_shortfall", np.nan),
        "cum_hourly_pay_shortfall_p": model.pvalues.get("cum_real_hourly_shortfall", np.nan),
        "hourly_pay_duration_coef": model.params.get("years_hourly_pay_below_2008", np.nan),
        "hourly_pay_duration_p": model.pvalues.get("years_hourly_pay_below_2008", np.nan),
    })
final_models = pd.DataFrame(final_rows)
final_models.to_csv(OUT / "work_effort_final_model_increment.csv", index=False)


# ---------------------------------------------------------------- source-of-identification checks
# The main model intentionally omits country FE so it can identify country outliers. These
# checks ask whether the squeeze also tracks change within countries or is mainly a stable
# cross-country marker. The latter can be informative descriptively but is weaker as a
# dynamic mechanism for Greece.
robust_rows = []
for var in [
    "work_effort_squeeze", "matched_employee_effort_squeeze",
    "cum_real_hourly_shortfall", "years_hourly_pay_below_2008",
]:
    d = panel.dropna(subset=base_vars + ["subjective_poverty", var]).sort_values(["geo", "time"]).copy()
    fe_formula = "subjective_poverty ~ " + " + ".join(base_vars + [var]) + " + C(geo) + C(time)"
    fe = smf.ols(fe_formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d.geo})
    diff_cols = ["subjective_poverty", var] + base_vars
    dd = d[["geo", "time"] + diff_cols].copy()
    dd[diff_cols] = dd.groupby("geo")[diff_cols].diff()
    dd = dd.dropna(subset=diff_cols)
    diff_formula = "subjective_poverty ~ " + " + ".join(base_vars + [var]) + " + C(time)"
    dm = smf.ols(diff_formula, data=dd).fit(cov_type="cluster", cov_kwds={"groups": dd.geo})
    robust_rows.append({
        "variable": var, "country_fe_coef": fe.params[var], "country_fe_p": fe.pvalues[var],
        "first_diff_coef": dm.params[var], "first_diff_p": dm.pvalues[var],
        "n_fe": len(d), "n_diff": len(dd),
    })
robust = pd.DataFrame(robust_rows)
robust.to_csv(OUT / "work_effort_within_change_robustness.csv", index=False)

# Full LOO stability for the richest model, saved even if the result is an overshoot.
rich_vars = base_vars + ["cum_excess_unemployment", "work_effort_squeeze"]
rich_d = panel.dropna(subset=rich_vars + ["subjective_poverty"]).copy()
rich_formula = "subjective_poverty ~ " + " + ".join(rich_vars) + " + C(time)"
rich_loo = country_loo(rich_formula, rich_d, "subjective_poverty", "work_effort_squeeze")
rich_loo.to_csv(OUT / "work_effort_rich_model_loo.csv", index=False)

# Stage-1 stability for accumulated hourly-pay loss, whose simple AROP bridge is strong even
# though its incremental C-LTU p-value narrowly misses the family-wise FDR threshold.
pay_stage1_d = panel[[
    "geo", "time", "subjective_poverty", "arop", "cum_real_hourly_shortfall"
]].dropna().copy()
pay_stage1_formula = "subjective_poverty ~ arop + cum_real_hourly_shortfall + C(time)"
pay_stage1_loo = country_loo(
    pay_stage1_formula, pay_stage1_d, "subjective_poverty", "cum_real_hourly_shortfall"
)
pay_stage1_loo.to_csv(OUT / "work_effort_cumulative_hourly_pay_stage1_loo.csv", index=False)


# ---------------------------------------------------------------- preview figures
plt.rcParams.update({"font.size": 10, "axes.titlesize": 14, "axes.labelsize": 11})
country_snapshot = snapshot[snapshot.geo.isin(MEMBERS)].copy()

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(country_snapshot.hourly_compensation_pps, country_snapshot.weekly_actual_hours,
           color="#9aa0a6", alpha=.75, s=38)
for _, row in country_snapshot.iterrows():
    if row.geo in {"EL", "BG", "PL", "NL", "DE", "DK"}:
        color = "#176b5b" if row.geo == "EL" else "#555555"
        ax.annotate(row.geo, (row.hourly_compensation_pps, row.weekly_actual_hours),
                    xytext=(4, 4), textcoords="offset points", color=color, weight="bold" if row.geo == "EL" else "normal")
el = country_snapshot[country_snapshot.geo == "EL"]
ax.scatter(el.hourly_compensation_pps, el.weekly_actual_hours, color="#176b5b", s=95, zorder=5)
ax.axhline(country_snapshot.weekly_actual_hours.mean(), color="#cccccc", lw=1)
ax.axvline(country_snapshot.hourly_compensation_pps.mean(), color="#cccccc", lw=1)
ax.set(title=f"Long hours, low hourly reward ({latest_common})",
       xlabel="Compensation per hour worked (PPS)", ylabel="Actual weekly hours, main job")
fig.tight_layout()
fig.savefig(FIG / "hours_vs_hourly_compensation.png", dpi=180)
plt.close(fig)

rank = country_snapshot.sort_values("work_effort_squeeze", ascending=True)
fig, ax = plt.subplots(figsize=(9, 8))
colors = ["#176b5b" if g == "EL" else "#b6bbb9" for g in rank.geo]
ax.barh(rank.geo, rank.work_effort_squeeze, color=colors)
ax.axvline(100, color="#555", lw=1, linestyle="--")
ax.set(title=f"Work-effort squeeze ({latest_common})", xlabel="EU=100; higher = more hours relative to PPS hourly compensation")
fig.tight_layout()
fig.savefig(FIG / "work_effort_squeeze_ranking.png", dpi=180)
plt.close(fig)

traj = comp[(comp.geo.isin(MEMBERS)) & (comp.time >= 2008)].dropna(subset=["real_hourly_comp_idx2008"])
fig, ax = plt.subplots(figsize=(10, 6))
for geo, g in traj.groupby("geo"):
    ax.plot(g.time, g.real_hourly_comp_idx2008, color="#c8ccca", lw=.8, alpha=.7)
g = traj[traj.geo == "EL"]
ax.plot(g.time, g.real_hourly_comp_idx2008, color="#176b5b", lw=2.8, label="Greece")
ax.axhline(100, color="#555", lw=1, linestyle="--")
ax.set(title="Real hourly compensation since 2008", xlabel="Year", ylabel="Each country: 2008=100")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "real_hourly_compensation_trajectory.png", dpi=180)
plt.close(fig)

hard = hardship_latest[hardship_latest.geo.isin(MEMBERS)].dropna(subset=["subjective_poverty_employed"])
hard = hard.sort_values("subjective_poverty_employed", ascending=True)
fig, ax = plt.subplots(figsize=(9, 8))
colors = ["#176b5b" if g == "EL" else "#b6bbb9" for g in hard.geo]
ax.barh(hard.geo, hard.subjective_poverty_employed, color=colors)
ax.set(title=f"Subjective poverty among employed people ({hardship_latest_year})",
       xlabel="Share reporting difficulty or great difficulty making ends meet (%)")
fig.tight_layout()
fig.savefig(FIG / "employed_subjective_poverty_ranking.png", dpi=180)
plt.close(fig)

gap_plot = status_latest[(status_latest.wstatus == "SAL") & status_latest.geo.isin(["EL", "EU27_2020"])].copy()
plot_long = gap_plot.melt(
    id_vars=["geo"], value_vars=["arop", "arope", "subjective_poverty"],
    var_name="measure", value_name="rate",
)
measure_labels = {"arop": "AROP", "arope": "AROPE", "subjective_poverty": "Subjective poverty"}
fig, ax = plt.subplots(figsize=(9, 5.5))
x = np.arange(3)
width = .35
for offset, (geo, color) in enumerate([("EL", "#176b5b"), ("EU27_2020", "#b6bbb9")]):
    vals = [
        plot_long[(plot_long.geo == geo) & (plot_long.measure == m)].rate.iloc[0]
        for m in ["arop", "arope", "subjective_poverty"]
    ]
    bars = ax.bar(x + (offset - .5) * width, vals, width, label="Greece" if geo == "EL" else "EU27", color=color)
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=9)
ax.set_xticks(x, [measure_labels[m] for m in ["arop", "arope", "subjective_poverty"]])
ax.set_ylabel("Share of salaried workers (%)")
ax.set_title(f"Employment does not close Greece's lived-hardship gap ({hardship_latest_year})")
ax.legend(frameon=False)
ax.set_ylim(0, max(plot_long.rate) * 1.15)
fig.tight_layout()
fig.savefig(FIG / "salaried_arop_arope_subjective_gap.png", dpi=180)
plt.close(fig)


# ---------------------------------------------------------------- console checkpoint summary
print("\n=== Latest comparable work-effort snapshot ===")
print(snapshot[snapshot.geo.isin(["EL", "EU27_2020"])][[
    "geo", "time", "weekly_actual_hours", "full_time_weekly_hours", "employee_weekly_hours",
    "self_employed_weekly_hours", "annual_hours_per_employee", "hourly_compensation_eur",
    "hourly_compensation_pps", "hourly_comp_pps_eu100", "work_effort_squeeze",
]].to_string(index=False))

print("\n=== Greece ranks, latest comparable year ===")
print(snapshot[snapshot.geo == "EL"][[
    "rank_weekly_actual_hours", "rank_hourly_compensation_pps", "rank_work_effort_squeeze",
    "rank_matched_employee_effort_squeeze",
]].to_string(index=False))

print("\n=== Employed-only hardship, Greece vs EU ===")
print(hardship_latest[hardship_latest.geo.isin(["EL", "EU27_2020"])][[
    "geo", "time", "subjective_poverty_employed", "arop_employed", "arope_employed",
    "employed_subjective_minus_arop", "employed_subjective_minus_arope",
]].to_string(index=False))
print("\n=== Greece ranks by working-status population (competition rank, 1=highest) ===")
print(status_latest[status_latest.geo == "EL"][[
    "wstatus", "subjective_poverty", "subjective_poverty_rank_worst",
    "arop", "arop_rank_worst", "arope", "arope_rank_worst",
]].to_string(index=False))

print("\n=== Model C-LTU candidate battery, BH-FDR corrected ===")
print(models.to_string(index=False))
print("\n=== Employed subjective-poverty battery, AROP + candidate + year FE ===")
print(emp_models.to_string(index=False))
print("\n=== Standalone AROP bridge battery ===")
print(stage1.to_string(index=False))
print("\n=== Hours x low-hourly-pay interaction ===")
print(pd.DataFrame([{
    "interaction_coef": ix_model.params["hours_x_low_pay"],
    "interaction_p": ix_model.pvalues["hours_x_low_pay"],
    "max_predictor_vif": vif.loc[vif.variable != "const", "vif"].max(),
}]).to_string(index=False))
print("\n=== Incremental test against cumulative-unemployment model ===")
print(final_models.to_string(index=False))
print("\n=== Within-country and first-difference robustness ===")
print(robust.to_string(index=False))

print("\nCheckpoint complete. Published reports were not modified.")
print(f"Processed outputs: {OUT}")
print(f"Preview figures: {FIG}")
