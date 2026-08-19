"""Multiple-testing discipline: apply Benjamini-Hochberg FDR correction within
each family of exploratory tests run across this project, and record which
results survive. This doesn't touch the confirmatory tests (the panel
regressions' own coefficients, e.g. Model E/F's added-variable p-values,
which were each the single planned test for a specific hypothesis) -- it's
for the multi-variable sweeps where many correlations were computed together
and a reader could otherwise mistake "significant at p<0.05" for "one of
several dozen comparisons that would produce ~1-2 false positives by chance
alone."
"""
import pandas as pd
from statsmodels.stats.multitest import multipletests

OUT = "../data/processed"

print("=== Family 1: correlation table (Section 4 / Methods), contemporaneous, n=17 ===")
d1 = pd.read_csv(f"{OUT}/correlations.csv")
rej, padj, _, _ = multipletests(d1["p_contemporaneous"], alpha=0.05, method="fdr_bh")
d1["p_adj_fdr"] = padj
d1["survives_fdr"] = rej
print(d1[["variable", "p_contemporaneous", "p_adj_fdr", "survives_fdr"]].round(4).to_string(index=False))
d1.to_csv(f"{OUT}/fdr_correlations.csv", index=False)

print("\n=== Family 2: sensitivity-vs-gap test (Section 11), n=9 ===")
d2 = pd.read_csv(f"{OUT}/sensitivity_vs_gap.csv")
rej, padj, _, _ = multipletests(d2["p_with_greece"], alpha=0.05, method="fdr_bh")
d2["p_adj_fdr"] = padj
d2["survives_fdr"] = rej
print(d2[["predictor", "p_with_greece", "p_adj_fdr", "survives_fdr"]].round(4).to_string(index=False))
d2.to_csv(f"{OUT}/fdr_sensitivity_vs_gap.csv", index=False)

print("\n=== Family 3: second-difference / acceleration test, n=5 ===")
d3 = pd.DataFrame([
    {"variable": "arop", "p": 0.0767},
    {"variable": "unemployment_rate", "p": 0.9828},
    {"variable": "real_gdp_pc", "p": 0.1034},
    {"variable": "severe_mat_soc_deprivation", "p": 0.0010},
    {"variable": "arrears", "p": 0.3272},
])
rej, padj, _, _ = multipletests(d3["p"], alpha=0.05, method="fdr_bh")
d3["p_adj_fdr"] = padj
d3["survives_fdr"] = rej
print(d3.round(4).to_string(index=False))
d3.to_csv(f"{OUT}/fdr_acceleration.csv", index=False)
