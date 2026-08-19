"""What do the countries where AROPE and subjective poverty are almost
identical (Italy, Slovenia, Hungary, France, Belgium, Cyprus, Croatia,
Portugal - |gap| <= 2pp) have in common, as a contrastive lens on Greece
(gap = +39.7pp, by far the largest in the EU)? Uses the latest-year snapshot
plus the predictor set already assembled for the panel models (Model C/E/F),
and the new scarring-stock variable from script 24.
"""
import pandas as pd

OUT = "../data/processed"

snap = pd.read_csv(f"{OUT}/arope_subjective_snapshot_2025.csv")
snap = snap[snap.geo != "EU27_2020"].copy()
snap["group"] = "other"
snap.loc[snap.gap.abs() <= 2, "group"] = "near_zero_gap"
snap.loc[snap.geo == "EL", "group"] = "greece"

near_zero = snap[snap.group == "near_zero_gap"]["geo"].tolist()
print("Near-zero-gap countries (|gap| <= 2pp):", near_zero)

panel_diffs = pd.read_csv(f"{OUT}/panel_with_diffs.csv")
latest = panel_diffs.sort_values("time").groupby("geo").tail(1)

fin_exp = pd.read_csv("../data/raw/panel_financial_expectations.csv")
fin_exp_latest = fin_exp.sort_values("year").groupby("geo").tail(1)[["geo", "fin_expectations"]]

merged = snap.merge(latest, on="geo", how="left").merge(fin_exp_latest, on="geo", how="left")

predictors = ["subjective_poverty_x", "arope", "gap", "arop", "unemployment_rate",
              "severe_mat_soc_deprivation", "housing_cost_overburden", "arrears",
              "unexpected_expenses", "pct_below_peak", "fin_expectations"]
merged = merged.rename(columns={"subjective_poverty_x": "subjective_poverty"})
predictors[0] = "subjective_poverty"

print("\n=== Group means (latest year available per country) ===")
grp = merged.groupby("group")[predictors].mean().round(2)
print(grp.T.to_string())

print("\n=== Per-country detail, near-zero-gap group ===")
cols = ["geo", "gap"] + predictors[3:]
print(merged[merged.group == "near_zero_gap"][cols].sort_values("gap").round(1).to_string(index=False))

print("\n=== Greece for comparison ===")
print(merged[merged.group == "greece"][cols].round(1).to_string(index=False))

merged.to_csv(f"{OUT}/near_zero_gap_comparison.csv", index=False)

print("\n=== Ranks: where does Greece sit vs near-zero-gap group on each predictor? ===")
all_countries = merged.dropna(subset=["pct_below_peak"])
for p in ["arop", "unemployment_rate", "severe_mat_soc_deprivation", "housing_cost_overburden",
          "arrears", "unexpected_expenses", "pct_below_peak", "fin_expectations"]:
    d = merged.dropna(subset=[p]).sort_values(p, ascending=False).reset_index(drop=True)
    d["rank"] = d.index + 1
    gr_rank = d[d.geo == "EL"]["rank"].values
    nz_ranks = d[d.geo.isin(near_zero)][["geo", "rank"]].sort_values("rank")
    print(f"\n{p}: Greece rank {gr_rank[0] if len(gr_rank) else 'NA'}/{len(d)}  |  "
          f"near-zero-gap ranks: {nz_ranks.set_index('geo')['rank'].to_dict()}")
