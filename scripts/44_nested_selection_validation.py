"""Nested selection validation for the cumulative-hardship screening.

External review point: leave-one-country-out validation in 38_cumulative_hardship.py
tests coefficient stability for the ALREADY-SELECTED variable, and the
selection-leakage check reruns the screening once with Greece excluded -- but
candidate selection itself had not been repeated independently inside every
held-out fold. This script closes that gap: for each of the 27 leave-one-out
folds, the complete 18-candidate screening (8 cumulative + 10 duration
candidates, each added one at a time to the Model C-LTU baseline) is rerun on
the panel with that fold's country dropped ENTIRELY (never seen during
screening), and the fold's winning candidate is recorded.

Selection criterion inside each fold: the added candidate's own coefficient
p-value, the same criterion the original screening used. The headline outputs:
  - how many folds select cum_excess_unemployment first,
  - how many select wage_years_below_2008 first,
  - whether any fold selects anything outside that top-2 set,
  - the per-fold p-values for both leading candidates.

Inputs: cumulative_hardship_candidate_panel.csv, written by
38_cumulative_hardship.py from the exact panel its own screening used.
"""
import pandas as pd
import statsmodels.formula.api as smf

OUT = "../data/processed"

panel = pd.read_csv(f"{OUT}/cumulative_hardship_candidate_panel.csv")

vars_c_ltu = ["ltu_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
              "housing_cost_overburden", "arrears", "unexpected_expenses"]

CUM_CANDIDATES = [
    "cum_gdp_shortfall_2008base", "pct_below_peak", "cum_gdp_shortfall_ownpeak",
    "cum_wage_shortfall_2008base", "cum_wage_shortfall_ownpeak",
    "cum_excess_unemployment", "cum_excess_ltu", "cum_threshold_shortfall",
]
DUR_CANDIDATES = [c for c in panel.columns if c.startswith(("gdp_", "wage_"))
                  and c not in CUM_CANDIDATES
                  and c not in ("gdp_pps_pc", "gdp_pps_pc_k")]  # base panel columns, not screening candidates
ALL_CANDIDATES = CUM_CANDIDATES + DUR_CANDIDATES
assert len(ALL_CANDIDATES) == 18, f"expected 18 candidates, found {len(ALL_CANDIDATES)}: {ALL_CANDIDATES}"

# Folds run only over countries that actually contribute rows to the screening.
# The raw panel also carries a UK geo, but the UK has no usable rows (missing
# ltu_rate and aic_pps_pc_k throughout), so a "UK held out" fold would train on
# data identical to the full screening -- a redundant no-op, excluded here.
usable = panel.dropna(subset=vars_c_ltu + ["subjective_poverty"])
countries = sorted(usable.geo.unique())
print(f"Panel: {panel.shape[0]} rows, {len(countries)} countries, "
      f"{len(ALL_CANDIDATES)} candidates x {len(countries)} folds "
      f"= {len(ALL_CANDIDATES) * len(countries)} screening regressions")

fold_rows = []
detail_rows = []
for held_out in countries:
    train_panel = panel[panel.geo != held_out]
    fold_results = []
    for var in ALL_CANDIDATES:
        d = train_panel.dropna(subset=vars_c_ltu + [var, "subjective_poverty"]).copy()
        if d.geo.nunique() < 10:
            continue
        formula = "subjective_poverty ~ " + " + ".join(vars_c_ltu + [var]) + " + C(time)"
        m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
        fold_results.append({"fold": held_out, "variable": var,
                             "coef": float(m.params[var]), "p": float(m.pvalues[var])})
    fr = pd.DataFrame(fold_results).sort_values("p").reset_index(drop=True)
    fr["rank"] = fr.index + 1
    detail_rows.append(fr)
    top = fr.iloc[0]
    ceu = fr[fr.variable == "cum_excess_unemployment"].iloc[0]
    wyb = fr[fr.variable == "wage_years_below_2008"].iloc[0]
    fold_rows.append({
        "fold_held_out": held_out,
        "selected_first": top["variable"], "selected_p": top["p"],
        "cum_excess_unemployment_rank": int(ceu["rank"]), "cum_excess_unemployment_p": ceu["p"],
        "wage_years_below_2008_rank": int(wyb["rank"]), "wage_years_below_2008_p": wyb["p"],
    })

folds_df = pd.DataFrame(fold_rows)
folds_df.to_csv(f"{OUT}/nested_selection_validation_folds.csv", index=False)
pd.concat(detail_rows).to_csv(f"{OUT}/nested_selection_validation_detail.csv", index=False)

pd.set_option("display.width", 220)
print("\n=== Per-fold winners: which candidate the screening selects when each country "
      "is excluded from screening entirely ===")
print(folds_df.to_string(index=False))

win_counts = folds_df.selected_first.value_counts()
print("\n=== Summary ===")
print("Winner counts across the 27 folds:")
print(win_counts.to_string())
top2 = {"cum_excess_unemployment", "wage_years_below_2008"}
outside = folds_df[~folds_df.selected_first.isin(top2)]
print(f"\nFolds selecting a candidate OUTSIDE the top-2 set: {len(outside)}"
      + (f"\n{outside[['fold_held_out', 'selected_first']].to_string(index=False)}" if len(outside) else ""))
both_top2 = ((folds_df.cum_excess_unemployment_rank <= 2) & (folds_df.wage_years_below_2008_rank <= 2)).sum()
print(f"Folds where the same two candidates occupy ranks 1-2: {both_top2} of {len(folds_df)}")
print(f"cum_excess_unemployment: worst rank {folds_df.cum_excess_unemployment_rank.max()}, "
      f"worst p {folds_df.cum_excess_unemployment_p.max():.5f}")
print(f"wage_years_below_2008: worst rank {folds_df.wage_years_below_2008_rank.max()}, "
      f"worst p {folds_df.wage_years_below_2008_p.max():.5f}")

print("\nOutputs written:")
for f in ["nested_selection_validation_folds.csv", "nested_selection_validation_detail.csv"]:
    print(f"  {OUT}/{f}")
