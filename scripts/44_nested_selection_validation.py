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
p-value, the same criterion the original screening used. Because 18 candidates
are screened per fold, those p-values are corrected within each fold
(Benjamini-Hochberg) as well as reported raw -- selection uses the raw ranking
(as the original screening did), and the corrected value records whether the
fold's winner would still clear a multiplicity-adjusted bar in isolation.

Two distinct things are measured, and they should not be conflated:

  (A) SELECTION STABILITY -- which candidate each fold picks when its country
      is absent from screening entirely. Establishes that the choice of
      variable is not an artifact of any one country's data.

  (B) NESTED PREDICTIVE PERFORMANCE -- the fold's OWN selected candidate is
      then fitted on the 26 training countries and used to predict the
      held-out country, which was involved in neither selection nor fitting.
      This is the genuine nested cross-validation quantity: it measures how
      well the whole select-then-fit procedure generalizes, not how well one
      pre-chosen variable does.

(B) is the stricter claim and is what licenses language about out-of-sample
predictive validity; (A) alone only licenses claims about stability.

Inputs: cumulative_hardship_candidate_panel.csv, written by
38_cumulative_hardship.py from the exact panel its own screening used.
"""
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

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
    rej, p_adj, _, _ = multipletests(fr["p"].values, alpha=0.05, method="fdr_bh")
    fr["p_fdr_within_fold"] = p_adj
    fr["survives_fdr_within_fold"] = rej
    detail_rows.append(fr)
    top = fr.iloc[0]

    # --- (B) nested prediction: fit THIS fold's own winner on the 26 training
    # countries, predict the held-out country. Selection and fitting both
    # exclude the held-out country entirely.
    win = top["variable"]
    dv = panel.dropna(subset=vars_c_ltu + [win, "subjective_poverty"])
    tr, te = dv[dv.geo != held_out], dv[dv.geo == held_out]
    nested_resid = nested_abs = None
    if len(te) and tr.geo.nunique() >= 10:
        f = "subjective_poverty ~ " + " + ".join(vars_c_ltu + [win]) + " + C(time)"
        mm = smf.ols(f, data=tr).fit(cov_type="cluster", cov_kwds={"groups": tr["geo"]})
        r = te["subjective_poverty"] - mm.predict(te)
        nested_resid, nested_abs = float(r.mean()), float(r.abs().mean())
    ceu = fr[fr.variable == "cum_excess_unemployment"].iloc[0]
    wyb = fr[fr.variable == "wage_years_below_2008"].iloc[0]
    fold_rows.append({
        "fold_held_out": held_out,
        "selected_first": top["variable"], "selected_p": top["p"],
        "cum_excess_unemployment_rank": int(ceu["rank"]), "cum_excess_unemployment_p": ceu["p"],
        "wage_years_below_2008_rank": int(wyb["rank"]), "wage_years_below_2008_p": wyb["p"],
        "selected_p_fdr_within_fold": top["p_fdr_within_fold"],
        "selected_survives_fdr_within_fold": bool(top["survives_fdr_within_fold"]),
        "nested_mean_residual": nested_resid, "nested_mean_abs_residual": nested_abs,
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
      f"worst raw p {folds_df.cum_excess_unemployment_p.max():.5f}")
print(f"wage_years_below_2008: worst rank {folds_df.wage_years_below_2008_rank.max()}, "
      f"worst raw p {folds_df.wage_years_below_2008_p.max():.5f}")
n_fdr = int(folds_df.selected_survives_fdr_within_fold.sum())
print(f"Folds whose selected winner also survives within-fold FDR correction "
      f"across the 18 candidates: {n_fdr} of {len(folds_df)}")

print("\n=== (B) Nested predictive performance ===")
print("Each fold's OWN selected candidate, fitted on 26 training countries, predicting "
      "the held-out 27th (excluded from both selection and fitting):")
nres = folds_df.dropna(subset=["nested_mean_residual"])
print(f"  folds scored: {len(nres)}")
print(f"  mean absolute residual across held-out countries: {nres.nested_mean_abs_residual.mean():.2f} pts")
print(f"  median: {nres.nested_mean_abs_residual.median():.2f} pts | "
      f"worst: {nres.nested_mean_abs_residual.max():.2f} ({nres.loc[nres.nested_mean_abs_residual.idxmax(), 'fold_held_out']})")
el = nres[nres.fold_held_out == "EL"]
if len(el):
    r = el.iloc[0]
    print(f"  GREECE held out: selected '{r.selected_first}', nested mean residual "
          f"{r.nested_mean_residual:+.2f} pts (abs {r.nested_mean_abs_residual:.2f})")
    worse = (nres.nested_mean_abs_residual > r.nested_mean_abs_residual).sum()
    print(f"  {worse} of the other {len(nres) - 1} countries are predicted WORSE than Greece "
          f"under their own fold's selected model")

print("\nOutputs written:")
for f in ["nested_selection_validation_folds.csv", "nested_selection_validation_detail.csv"]:
    print(f"  {OUT}/{f}")
