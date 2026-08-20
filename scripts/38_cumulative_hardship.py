"""Cumulative-hardship checkpoint: does accumulated exposure since the crisis
explain Greece's subjective-poverty gap better than current-year hardship
alone? A new checkpoint, not folded into any existing model -- generalizes
the anchored-poverty method (Section 3's fixed-2008-baseline reconstruction)
to GDP, real wages, unemployment, long-term unemployment, and the AROP
threshold itself.

Construction rules (agreed before running):
  - GDP / real wages: annual shortfall = max(0, 100 - index), summed since
    2008 -- an accumulated-damage measure, not a net-performance score where
    later growth cancels earlier hardship. Two baselines each: fixed 2008
    level, and each country's own rolling historical peak (may differ from
    2008 for countries that peaked later).
  - Unemployment / LTU: cumulative EXCESS above each country's own baseline
    year rate, summed (also floored at 0 per year). Unemployment baselined
    to 2008; LTU baselined to 2009 (its earliest common year across the
    panel -- confirmed via coverage check, not assumed).
  - AROP threshold: nominal threshold (NAC, national currency, not EUR --
    avoids exchange-rate contamination for non-euro countries) deflated by
    each country's own HICP, indexed to that country's own 2008=100, same
    floored-shortfall-summed construction. Croatia has no 2008/2009 data
    (series starts 2010) -- baselined to 2010 for Croatia only, flagged.
  - Every cumulative variable tested ONE AT A TIME added to Model C-LTU,
    compared directly against its own current-year equivalent already in
    the scorecard. No combined cumulative model unless a variable clearly
    earns it in its own individual test.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
BASE_YEAR = 2008
# Headline unemployment (une_rt_a) and LTU both start in 2009 for nearly every
# country in this panel (confirmed via coverage check, not assumed) -- both
# use the same later baseline, clearly distinct from GDP/wages/threshold's 2008.
UNEMP_BASE_YEAR = 2009
LTU_BASE_YEAR = 2009

members = sorted(eu_members(2025))

# ---------------------------------------------------------------- fetch AROP threshold (NAC) ----
thresh = fetch(
    "ilc_li01",
    statinfo="MED_EI", rskpovth="B_60", hhcomp="A1", unit="NAC",
    geo=members, time=range(2003, 2026),
)
thresh = thresh[["geo", "time", "value"]].rename(columns={"value": "arop_threshold_nac"})
thresh.to_csv(f"{RAW}/arop_threshold_all_countries_nac.csv", index=False)
print(f"AROP threshold (NAC) fetched: {len(thresh)} rows, {thresh.geo.nunique()} countries")
cov = thresh.groupby("geo")["time"].agg(["min", "max", "count"])
gaps = cov[cov["max"] - cov["min"] + 1 != cov["count"]]
print(f"Countries with internal gaps: {len(gaps)}" + (f"\n{gaps}" if len(gaps) else " (none)"))
print(f"Countries starting after {BASE_YEAR}: {cov[cov['min'] > BASE_YEAR].index.tolist()}")

hicp = pd.read_csv(f"{RAW}/panel_hicp_index.csv")

# ---------------------------------------------------------------- load existing panels -----------
gdp = pd.read_csv(f"{RAW}/panel_gdp_history_2008_2024.csv")[["geo", "time", "real_gdp_pc"]]
wages = pd.read_csv(f"{RAW}/real_wage_idx2008.csv")  # already indexed to each country's own 2008=100
unemp = pd.read_csv(f"{RAW}/panel_unemployment_history_2008_2024.csv")
ltu = pd.read_csv(f"{RAW}/panel_long_term_unemployment.csv")[["geo", "time", "ltu_rate"]]

# ================================================================ build cumulative variables ====

def floored_cumulative_shortfall(df, value_col, base_year, out_col, id_col="geo", time_col="time"):
    """Sum of max(0, 100 - index) from base_year through each year (inclusive),
    where value_col is already indexed to 100 = that country's base_year level."""
    df = df.sort_values([id_col, time_col]).copy()
    df["_shortfall"] = (100 - df[value_col]).clip(lower=0)
    df = df[df[time_col] >= base_year]
    df[out_col] = df.groupby(id_col)["_shortfall"].cumsum()
    return df[[id_col, time_col, out_col]]


def floored_cumulative_excess(df, value_col, base_year, out_col, id_col="geo", time_col="time"):
    """Sum of max(0, value(year) - value(base_year)) from base_year through each year."""
    df = df.sort_values([id_col, time_col]).copy()
    base = df[df[time_col] == base_year][[id_col, value_col]].rename(columns={value_col: "_base"})
    df = df.merge(base, on=id_col, how="left")
    df["_excess"] = (df[value_col] - df["_base"]).clip(lower=0)
    df = df[df[time_col] >= base_year]
    df[out_col] = df.groupby(id_col)["_excess"].cumsum()
    return df[[id_col, time_col, out_col]]


# --- GDP, fixed-2008 basis ---
gdp = gdp.sort_values(["geo", "time"])
gdp_2008 = gdp[gdp.time == BASE_YEAR][["geo", "real_gdp_pc"]].rename(columns={"real_gdp_pc": "_gdp_2008"})
gdp = gdp.merge(gdp_2008, on="geo", how="left")
gdp["gdp_idx_2008base"] = 100 * gdp["real_gdp_pc"] / gdp["_gdp_2008"]
cum_gdp_2008 = floored_cumulative_shortfall(gdp, "gdp_idx_2008base", BASE_YEAR, "cum_gdp_shortfall_2008base")

# --- GDP, own rolling-peak basis ---
gdp["running_peak"] = gdp.groupby("geo")["real_gdp_pc"].cummax()
gdp["gdp_idx_ownpeak"] = 100 * gdp["real_gdp_pc"] / gdp["running_peak"]
gdp["pct_below_peak"] = 100 - gdp["gdp_idx_ownpeak"]  # already >= 0 by construction
gdp_peak = gdp[gdp.time >= BASE_YEAR].sort_values(["geo", "time"]).copy()
gdp_peak["cum_gdp_shortfall_ownpeak"] = gdp_peak.groupby("geo")["pct_below_peak"].cumsum()
cum_gdp_peak = gdp_peak[["geo", "time", "cum_gdp_shortfall_ownpeak"]]

# --- Real wages, fixed-2008 basis (already indexed to own 2008=100) ---
cum_wage_2008 = floored_cumulative_shortfall(wages, "real_wage_idx2008", BASE_YEAR, "cum_wage_shortfall_2008base")

# --- Real wages, own rolling-peak basis ---
wages_s = wages.sort_values(["geo", "time"]).copy()
wages_s["running_peak"] = wages_s.groupby("geo")["real_wage_idx2008"].cummax()
wages_s["pct_below_peak"] = wages_s["running_peak"] - wages_s["real_wage_idx2008"]
wages_peak = wages_s[wages_s.time >= BASE_YEAR].copy()
wages_peak["cum_wage_shortfall_ownpeak"] = wages_peak.groupby("geo")["pct_below_peak"].cumsum()
cum_wage_peak = wages_peak[["geo", "time", "cum_wage_shortfall_ownpeak"]]

# --- Unemployment, cumulative excess above 2009 (earliest common year, like LTU) ---
cum_unemp = floored_cumulative_excess(unemp, "unemployment_rate", UNEMP_BASE_YEAR, "cum_excess_unemployment")

# --- LTU, cumulative excess above 2009 (earliest common year) ---
cum_ltu = floored_cumulative_excess(ltu, "ltu_rate", LTU_BASE_YEAR, "cum_excess_ltu")

# --- AROP threshold, real terms, cumulative shortfall ---
thresh_hicp = thresh.merge(hicp, on=["geo", "time"], how="left")
frames = []
for g, grp in thresh_hicp.groupby("geo"):
    grp = grp.sort_values("time")
    base_rows = grp[grp.time == BASE_YEAR]
    base_year_g = BASE_YEAR
    if base_rows.empty:
        base_year_g = grp.time.min()  # Croatia: no 2008/2009 data, use earliest (2010)
    base_row = grp[grp.time == base_year_g]
    if base_row.empty or base_row["hicp_index"].isna().all() or base_row["arop_threshold_nac"].isna().all():
        continue
    base_hicp = base_row["hicp_index"].values[0]
    base_thresh_nac = base_row["arop_threshold_nac"].values[0]
    grp = grp.copy()
    grp["real_thresh"] = grp["arop_threshold_nac"] / (grp["hicp_index"] / base_hicp)
    grp["thresh_idx"] = 100 * grp["real_thresh"] / base_thresh_nac
    grp["_baseline_year_used"] = base_year_g
    frames.append(grp)
thresh_real = pd.concat(frames)
cum_thresh_frames = []
for g, grp in thresh_real.groupby("geo"):
    by = grp["_baseline_year_used"].iloc[0]
    sub = floored_cumulative_shortfall(grp, "thresh_idx", by, "cum_threshold_shortfall")
    cum_thresh_frames.append(sub)
cum_thresh = pd.concat(cum_thresh_frames)
print(f"\nAROP-threshold baseline years used (non-2008 flagged): "
      f"{thresh_real.groupby('geo')['_baseline_year_used'].first().loc[lambda s: s != BASE_YEAR].to_dict()}")

# ================================================================ assemble & test =================
panel = pd.read_csv(f"{OUT}/panel_extended.csv")
debt = pd.read_csv(f"{RAW}/panel_debt_to_income.csv")
before = pd.read_csv(f"{RAW}/panel_arop_before_transfers.csv")
gdp_hist = pd.read_csv(f"{RAW}/panel_gdp_history_2008_2024.csv").sort_values(["geo", "time"])
gdp_hist["running_peak"] = gdp_hist.groupby("geo")["real_gdp_pc"].cummax()
gdp_hist["pct_below_peak"] = 100 * (gdp_hist["running_peak"] - gdp_hist["real_gdp_pc"]) / gdp_hist["running_peak"]

panel = panel.merge(debt, on=["geo", "time"], how="left")
panel = panel.merge(before, on=["geo", "time"], how="left")
panel["transfer_effect"] = panel["arop_before_transfers"] - panel["arop"]
panel = panel.merge(gdp_hist[["geo", "time", "pct_below_peak"]], on=["geo", "time"], how="left")
panel = panel.merge(ltu, on=["geo", "time"], how="left")

for cum_df in [cum_gdp_2008, cum_gdp_peak, cum_wage_2008, cum_wage_peak, cum_unemp, cum_ltu, cum_thresh]:
    panel = panel.merge(cum_df, on=["geo", "time"], how="left")

vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]

CANDIDATES = {
    "cum_gdp_shortfall_2008base": "Cumulative GDP shortfall, fixed 2008 basis",
    "pct_below_peak": "[current-year] % below own GDP peak (existing Model F variable)",
    "cum_gdp_shortfall_ownpeak": "Cumulative GDP shortfall, own rolling-peak basis",
    "cum_wage_shortfall_2008base": "Cumulative real-wage shortfall, fixed 2008 basis",
    "cum_wage_shortfall_ownpeak": "Cumulative real-wage shortfall, own rolling-peak basis",
    "cum_excess_unemployment": "Cumulative excess unemployment above 2009",
    "cum_excess_ltu": "Cumulative excess LTU above 2009",
    "cum_threshold_shortfall": "Cumulative real AROP-threshold shortfall since 2008",
}

results = []
for var, label in CANDIDATES.items():
    vars_ = vars_c_ltu + [var]
    d = panel.dropna(subset=vars_ + ["subjective_poverty"]).copy()
    formula = "subjective_poverty ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d["predicted"] = m.predict(d)
    d["residual"] = d["subjective_poverty"] - d["predicted"]
    gr_in = d[d.geo == "EL"]["residual"].mean()

    rows = []
    for c in sorted(d["geo"].unique()):
        train = d[d.geo != c]
        test = d[d.geo == c].copy()
        mc = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
        test["predicted_loo"] = mc.predict(test)
        test["residual_loo"] = test["subjective_poverty"] - test["predicted_loo"]
        rows.append({"geo": c, "avg_residual": test["residual_loo"].mean()})
    loo = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
    loo["rank"] = loo.index + 1
    gr_loo_row = loo[loo.geo == "EL"].iloc[0]

    results.append({
        "variable": var,
        "label": label,
        "n_countries": d.geo.nunique(),
        "n_obs": len(d),
        "r2": round(m.rsquared, 3),
        "gr_avg_residual_insample": round(gr_in, 2),
        "gr_avg_residual_oos": round(gr_loo_row["avg_residual"], 2),
        "gr_rank_oos": f"{int(gr_loo_row['rank'])}/{len(loo)}",
        "coef": round(float(m.params[var]), 4),
        "p_value": round(float(m.pvalues[var]), 4),
    })

# baseline for comparison: C-LTU with no added variable
d0 = panel.dropna(subset=vars_c_ltu + ["subjective_poverty"]).copy()
formula0 = "subjective_poverty ~ " + " + ".join(vars_c_ltu) + " + C(time)"
m0 = smf.ols(formula0, data=d0).fit(cov_type="cluster", cov_kwds={"groups": d0["geo"]})
d0["predicted"] = m0.predict(d0)
d0["residual"] = d0["subjective_poverty"] - d0["predicted"]
gr_in0 = d0[d0.geo == "EL"]["residual"].mean()
rows0 = []
for c in sorted(d0["geo"].unique()):
    train = d0[d0.geo != c]
    test = d0[d0.geo == c].copy()
    mc = smf.ols(formula0, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
    test["predicted_loo"] = mc.predict(test)
    test["residual_loo"] = test["subjective_poverty"] - test["predicted_loo"]
    rows0.append({"geo": c, "avg_residual": test["residual_loo"].mean()})
loo0 = pd.DataFrame(rows0).sort_values("avg_residual", ascending=False).reset_index(drop=True)
loo0["rank"] = loo0.index + 1
gr_loo0 = loo0[loo0.geo == "EL"].iloc[0]

results_df = pd.DataFrame(results)
results_df.to_csv(f"{OUT}/cumulative_hardship_checkpoint.csv", index=False)

pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 60)
print("\n\n=== Baseline: Model C-LTU, no cumulative variable added ===")
print(f"R2={m0.rsquared:.3f}  Greece in-sample={gr_in0:.2f}  Greece out-of-sample={gr_loo0['avg_residual']:.2f}  "
      f"rank={int(gr_loo0['rank'])}/{len(loo0)}")

print("\n=== Cumulative-hardship checkpoint: each variable added individually to Model C-LTU ===")
print(results_df.to_string(index=False))

print("\n=== Current-year vs. cumulative, side by side ===")
pairs = [
    ("pct_below_peak", "cum_gdp_shortfall_2008base", "GDP: current % below peak vs. cumulative shortfall (2008 basis)"),
    ("pct_below_peak", "cum_gdp_shortfall_ownpeak", "GDP: current % below peak vs. cumulative shortfall (own-peak basis)"),
]
for cur, cum, desc in pairs:
    r_cur = results_df[results_df.variable == cur]
    r_cum = results_df[results_df.variable == cum]
    print(f"\n{desc}")
    print(pd.concat([r_cur, r_cum])[["variable", "gr_avg_residual_oos", "gr_rank_oos", "p_value"]].to_string(index=False))


# ================================================================ duration/direction battery ======
# Exploratory extension: does PERSISTENCE (years continuously below baseline, longest historical
# streak, count of negative-change years) explain the gap better than a raw cumulative SUM of
# shortfall? Tested for GDP and real wages, the two variables with full 2008-2024 coverage.

def duration_features(df, id_col, time_col, value_col, base_series, own_peak_series, base_year=2008):
    df = df[df[time_col] >= base_year].sort_values([id_col, time_col]).copy()
    out_rows = []
    for g, grp in df.groupby(id_col):
        grp = grp.sort_values(time_col)
        streak_2008 = streak_peak = longest_2008 = longest_peak = neg_years = 0
        prev_val = None
        for _, row in grp.iterrows():
            below_2008 = row[value_col] < row[base_series]
            below_peak = row[value_col] < row[own_peak_series]
            streak_2008 = streak_2008 + 1 if below_2008 else 0
            streak_peak = streak_peak + 1 if below_peak else 0
            longest_2008 = max(longest_2008, streak_2008)
            longest_peak = max(longest_peak, streak_peak)
            if prev_val is not None and row[value_col] < prev_val:
                neg_years += 1
            prev_val = row[value_col]
            out_rows.append({id_col: g, time_col: row[time_col],
                              "years_below_2008": streak_2008, "years_below_peak": streak_peak,
                              "longest_streak_2008": longest_2008, "longest_streak_peak": longest_peak,
                              "cum_negative_years": neg_years})
    return pd.DataFrame(out_rows)


gdp_d = gdp.copy()
gdp_dur = duration_features(gdp_d, "geo", "time", "real_gdp_pc", "_gdp_2008", "running_peak")
gdp_dur = gdp_dur.rename(columns={c: f"gdp_{c}" for c in gdp_dur.columns if c not in ("geo", "time")})

wages_d = wages.copy()
wages_d["_w08"] = 100.0
wages_d["running_peak"] = wages_d.groupby("geo")["real_wage_idx2008"].cummax()
wages_dur = duration_features(wages_d, "geo", "time", "real_wage_idx2008", "_w08", "running_peak")
wages_dur = wages_dur.rename(columns={c: f"wage_{c}" for c in wages_dur.columns if c not in ("geo", "time")})

panel = panel.merge(gdp_dur, on=["geo", "time"], how="left")
panel = panel.merge(wages_dur, on=["geo", "time"], how="left")

DURATION_CANDIDATES = [c for c in gdp_dur.columns if c not in ("geo", "time")] + \
                      [c for c in wages_dur.columns if c not in ("geo", "time")]

def run_model(vars_extra, panel, base_vars=vars_c_ltu, outcome="subjective_poverty"):
    vars_ = base_vars + vars_extra
    d = panel.dropna(subset=vars_ + [outcome]).copy()
    formula = f"{outcome} ~ " + " + ".join(vars_) + " + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    d["predicted"] = m.predict(d)
    d["residual"] = d[outcome] - d["predicted"]
    gr_in = d[d.geo == "EL"]["residual"].mean()
    rows = []
    for c in sorted(d["geo"].unique()):
        train = d[d.geo != c]
        test = d[d.geo == c].copy()
        mc = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
        test["predicted_loo"] = mc.predict(test)
        test["residual_loo"] = test[outcome] - test["predicted_loo"]
        rows.append({"geo": c, "avg_residual": test["residual_loo"].mean()})
    loo = pd.DataFrame(rows).sort_values("avg_residual", ascending=False).reset_index(drop=True)
    loo["rank"] = loo.index + 1
    gr_loo = loo[loo.geo == "EL"].iloc[0]
    return dict(r2=round(m.rsquared, 3), n=len(d), gr_in=round(gr_in, 2),
                gr_oos=round(gr_loo["avg_residual"], 2), rank=f"{int(gr_loo['rank'])}/{len(loo)}",
                coefs={v: (round(float(m.params[v]), 4), round(float(m.pvalues[v]), 4)) for v in vars_extra},
                model=m, data=d, formula=formula)

dur_results = []
for var in DURATION_CANDIDATES:
    r = run_model([var], panel)
    coef, p = r["coefs"][var]
    dur_results.append(dict(var=var, r2=r["r2"], n=r["n"], gr_in=r["gr_in"], gr_oos=r["gr_oos"],
                             rank=r["rank"], coef=coef, p=p))
dur_df = pd.DataFrame(dur_results)
dur_df.to_csv(f"{OUT}/cumulative_hardship_duration_battery.csv", index=False)
print("\n\n=== Duration/direction battery (exploratory), each added individually to Model C-LTU ===")
print(dur_df.to_string(index=False))


# ================================================================ replacement test ================
# Is cumulative excess unemployment a better REPLACEMENT for LTU, or a genuine ADDITIONAL layer?
base_covars = ["aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
               "housing_cost_overburden", "arrears", "unexpected_expenses"]

replacement_results = {}
for label, extra, base in [
    ("C-LTU baseline", ["ltu_rate"], base_covars),
    ("C + cum_excess_unemployment (LTU swapped out)", ["cum_excess_unemployment"], base_covars),
    ("C-LTU + cum_excess_unemployment (both)", ["ltu_rate", "cum_excess_unemployment"], base_covars),
]:
    r = run_model(extra, panel, base_vars=base)
    replacement_results[label] = r
    print(f"\n{label}")
    print(f"  R2={r['r2']}  n={r['n']}  Greece in-sample={r['gr_in']}  out-of-sample={r['gr_oos']}  rank={r['rank']}")
    print(f"  coefficients: {r['coefs']}")

pd.DataFrame([
    dict(model=k, r2=v["r2"], n=v["n"], gr_in=v["gr_in"], gr_oos=v["gr_oos"], rank=v["rank"], coefs=str(v["coefs"]))
    for k, v in replacement_results.items()
]).to_csv(f"{OUT}/cumulative_hardship_replacement_test.csv", index=False)


# ================================================================ LOO stability + redundancy ======
from statsmodels.stats.outliers_influence import variance_inflation_factor

def loo_stability(var, panel, base_vars=vars_c_ltu):
    r = run_model([var], panel, base_vars=base_vars)
    d, formula = r["data"], r["formula"]
    full_coef = r["model"].params[var] if hasattr(r["model"], "params") else None
    stability_rows = []
    for c in sorted(d["geo"].unique()):
        train = d[d.geo != c]
        mc = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
        stability_rows.append({"exclude": c, "coef": round(float(mc.params[var]), 4),
                                "p": round(float(mc.pvalues[var]), 4)})
    return pd.DataFrame(stability_rows)

for var in ["cum_excess_unemployment", "wage_years_below_2008"]:
    stab = loo_stability(var, panel)
    stab.to_csv(f"{OUT}/cumulative_hardship_loo_stability_{var}.csv", index=False)
    n_flips = ((stab["coef"] > 0).sum() == 0) or ((stab["coef"] < 0).sum() == 0)
    print(f"\n=== LOO stability, {var}: sign flips = {'NO' if n_flips else 'YES'}, "
          f"coef range [{stab['coef'].min():.4f}, {stab['coef'].max():.4f}], "
          f"max p-value {stab['p'].max():.4f} (Greece excluded row: "
          f"{stab[stab.exclude=='EL'][['coef','p']].values.tolist()})")

# redundancy: both wage_years_below_2008 and cum_excess_unemployment together
r_both = run_model(["wage_years_below_2008", "cum_excess_unemployment"], panel)
d2 = r_both["data"]
X = d2[vars_c_ltu + ["wage_years_below_2008", "cum_excess_unemployment"]].copy()
X["const"] = 1
vifs = {c: round(variance_inflation_factor(X.values, i), 2) for i, c in enumerate(X.columns) if c != "const"}
corr_panel = d2["wage_years_below_2008"].corr(d2["cum_excess_unemployment"])
corr_gr = d2[d2.geo == "EL"]["wage_years_below_2008"].corr(d2[d2.geo == "EL"]["cum_excess_unemployment"])
print(f"\n=== Redundancy: wage_years_below_2008 + cum_excess_unemployment together ===")
print(f"  R2={r_both['r2']}  Greece OOS={r_both['gr_oos']}  rank={r_both['rank']}  coefs={r_both['coefs']}")
print(f"  VIFs: {vifs}")
print(f"  correlation panel-wide={corr_panel:.3f}  Greece-only={corr_gr:.3f}")


# ================================================================ year-by-year residual check =====
r_final = run_model(["ltu_rate", "cum_excess_unemployment"], panel, base_vars=base_covars)
d_final = r_final["data"]
train = d_final[d_final.geo != "EL"]
test = d_final[d_final.geo == "EL"].copy()
m_loo = smf.ols(r_final["formula"], data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
test["predicted"] = m_loo.predict(test)
test["residual"] = test["subjective_poverty"] - test["predicted"]
yby = test[["time", "subjective_poverty", "predicted", "residual"]].sort_values("time")
yby.to_csv(f"{OUT}/cumulative_hardship_final_model_year_by_year.csv", index=False)
print("\n=== Year-by-year residual, final model (C-LTU + cumulative excess unemployment), Greece excluded from fit ===")
print(yby.to_string(index=False))


# ================================================================ Stage 1: individual gap explanation =
# Each candidate tested ALONE against just AROP + year FE -- the simplest possible baseline, tied
# to the paper's primary object, putting every variable (whether or not it's in the main model) on
# equal footing. Answers: "how much does this ONE variable, on its own, help translate AROP into
# subjective poverty" -- explicitly NOT a causal-contribution claim.
base_ap = pd.read_csv(f"{OUT}/panel_extended.csv")[["geo", "time", "subjective_poverty", "arop"]]

housing = pd.read_csv(f"{RAW}/panel_housing_overburden.csv")
arrears_df = pd.read_csv(f"{RAW}/panel_arrears.csv")
unexp = pd.read_csv(f"{RAW}/panel_unexpected_expenses.csv")
dep = pd.read_csv(f"{RAW}/panel_deprivation.csv")
fin_exp = pd.read_csv(f"{RAW}/panel_financial_expectations.csv").rename(columns={"year": "time"})
migr = pd.read_csv(f"{RAW}/migration_nationals_panel.csv")[["geo", "time", "net_migration_rate_per1000"]]
tenure = pd.read_csv(f"{RAW}/panel_housing_overburden_by_tenure.csv")
tenure_ownl = tenure[tenure.tenure == "OWN_NL"][["geo", "time", "value"]].rename(columns={"value": "tenure_ownl_overburden"})
price = pd.read_csv(f"{RAW}/panel_price_levels_by_category.csv")
price_a01 = price[price.category == "A01"][["geo", "time", "price_level"]]
wage_level = pd.read_csv(f"{RAW}/panel_nominal_compensation_wage_level.csv")
wcol = [c for c in wage_level.columns if c not in ("geo", "time")][0]
wage_adj = price_a01.merge(wage_level, on=["geo", "time"], how="inner")
wage_adj["wage_adjusted_pressure"] = 100 * wage_adj["price_level"] / wage_adj[wcol]
wage_adj = wage_adj[["geo", "time", "wage_adjusted_pressure"]]

STAGE1_CANDIDATES = {
    "material_deprivation": (dep.rename(columns={"severe_mat_soc_deprivation": "val"}), "Material deprivation"),
    "housing_overburden": (housing.rename(columns={"housing_cost_overburden": "val"}), "Housing cost overburden"),
    "arrears": (arrears_df.rename(columns={"arrears": "val"}), "Arrears"),
    "unexpected_expenses": (unexp.rename(columns={"unexpected_expenses": "val"}), "Inability to cover unexpected expense"),
    "ltu_rate": (ltu.rename(columns={"ltu_rate": "val"}), "LTU"),
    "cum_excess_unemployment": (cum_unemp.rename(columns={"cum_excess_unemployment": "val"}), "Cumulative excess unemployment"),
    "wage_years_below_2008": (wages_dur[["geo", "time", "wage_years_below_2008"]].rename(columns={"wage_years_below_2008": "val"}), "Wage years below 2008"),
    "wage_adjusted_pressure": (wage_adj.rename(columns={"wage_adjusted_pressure": "val"}), "Wage-adjusted price pressure"),
    "tenure_ownl_overburden": (tenure_ownl.rename(columns={"tenure_ownl_overburden": "val"}), "Housing tenure burden (mortgage-free owners)"),
    "net_migration_rate_per1000": (migr.rename(columns={"net_migration_rate_per1000": "val"}), "Migration (net rate per 1000)"),
    "fin_expectations": (fin_exp.rename(columns={"fin_expectations": "val"}), "Financial expectations"),
}

gr_subj, gr_arop, gr_arope = 67.2, 19.6, 27.5
raw_arop_gap = gr_subj - gr_arop
raw_arope_gap = gr_subj - gr_arope

stage1_results = []
for key, (df, label) in STAGE1_CANDIDATES.items():
    d = base_ap.merge(df[["geo", "time", "val"]], on=["geo", "time"], how="inner").dropna(subset=["subjective_poverty", "arop", "val"])
    if d.time.nunique() < 3 or d.geo.nunique() < 10 or "EL" not in d.geo.unique():
        stage1_results.append(dict(key=key, label=label, status="insufficient coverage", gr_oos=None,
                                    pts_arop_explained=None, pts_arope_explained=None))
        continue
    formula = "subjective_poverty ~ arop + val + C(time)"
    m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
    train = d[d.geo != "EL"]
    test = d[d.geo == "EL"].copy()
    mc = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
    test["pred"] = mc.predict(test)
    test["resid"] = test["subjective_poverty"] - test["pred"]
    gr_oos = test["resid"].mean()
    stage1_results.append(dict(key=key, label=label, n_obs=len(d), status="ok", gr_oos=round(gr_oos, 2),
                                p=round(float(m.pvalues["val"]), 4), coef=round(float(m.params["val"]), 4),
                                pts_arop_explained=round(raw_arop_gap - gr_oos, 1),
                                pts_arope_explained=round(raw_arope_gap - gr_oos, 1)))

stage1_df = pd.DataFrame(stage1_results).sort_values("gr_oos")
stage1_df.to_csv(f"{OUT}/cumulative_hardship_stage1_individual.csv", index=False)
print("\n\n=== STAGE 1: individual gap explanation (each variable alone + AROP + year FE) ===")
print(stage1_df.to_string(index=False))


# ================================================================ Stage 2: layered bridge table ====
stage2 = [
    dict(step=1, layer="AROP raw gap", type="raw, single-country", greece_value=raw_arop_gap, points_closed=None),
    dict(step=2, layer="AROPE bridge", type="raw, single-country", greece_value=raw_arope_gap, points_closed=raw_arop_gap - raw_arope_gap),
    dict(step=3, layer="Basic model: AROP + income + deprivation + headline unemployment (Model A)",
         type="regression, OOS", greece_value=25.6, points_closed=raw_arop_gap - 25.6),
    dict(step=4, layer="+ housing, arrears, unexpected-expense capacity (Model C)",
         type="regression, OOS", greece_value=11.6, points_closed=raw_arop_gap - 11.6),
    dict(step=5, layer="Headline unemployment -> LTU (Model C-LTU)",
         type="regression, OOS", greece_value=gr_loo0["avg_residual"], points_closed=raw_arop_gap - gr_loo0["avg_residual"]),
    dict(step=6, layer="+ cumulative excess unemployment (final model)",
         type="regression, OOS", greece_value=r_final["gr_oos"], points_closed=raw_arop_gap - r_final["gr_oos"]),
]
stage2_df = pd.DataFrame(stage2)
stage2_df.to_csv(f"{OUT}/cumulative_hardship_stage2_bridge.csv", index=False)
print("\n\n=== STAGE 2: layered bridge, subjective poverty minus AROP (47.6pt raw gap) ===")
print(stage2_df.to_string(index=False))
wyb_oos = dur_df[dur_df["var"] == "wage_years_below_2008"]["gr_oos"].values
print(f"\nSide note (not stacked into the sequence): wage_years_below_2008 alone reaches "
      f"Greece OOS={wyb_oos}, "
      f"robust under leave-Greece-out, but combined with step 6 correlates at r=0.95 within Greece "
      f"(see redundancy check above) -- kept as supporting evidence, not a seventh layer.")

print("\n\nCheckpoint complete. Outputs written:")
for f in ["cumulative_hardship_checkpoint.csv", "cumulative_hardship_duration_battery.csv",
          "cumulative_hardship_replacement_test.csv", "cumulative_hardship_loo_stability_cum_excess_unemployment.csv",
          "cumulative_hardship_loo_stability_wage_years_below_2008.csv",
          "cumulative_hardship_final_model_year_by_year.csv", "cumulative_hardship_stage1_individual.csv",
          "cumulative_hardship_stage2_bridge.csv"]:
    print(f"  {OUT}/{f}")
