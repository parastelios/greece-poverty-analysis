"""Leave-one-country-out for EVERY country (not just Greece), on Model C, to
give Greece's out-of-sample gap a distribution to be judged against rather than
standing alone as a single number. If leaving any random country out produces
swings of a similar size, Greece's gap is less remarkable; if Greece's gap is
far outside the range produced by leaving other countries out, that's a
stronger claim than the single leave-Greece-out number by itself."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

RAW = "../data/raw"
OUT = "../data/processed"

panel = pd.read_csv(f"{OUT}/panel_extended.csv")
vars_c = ["unemployment_rate", "aic_pps_pc_k", "severe_mat_soc_deprivation", "arop",
          "housing_cost_overburden", "arrears", "unexpected_expenses"]
d = panel.dropna(subset=vars_c + ["subjective_poverty"])
formula = "subjective_poverty ~ " + " + ".join(vars_c) + " + C(time)"

countries = sorted(d["geo"].unique())
rows = []
for c in countries:
    train = d[d.geo != c]
    test = d[d.geo == c].copy()
    model = smf.ols(formula, data=train).fit(cov_type="cluster", cov_kwds={"groups": train["geo"]})
    test["predicted"] = model.predict(test)
    test["residual"] = test["subjective_poverty"] - test["predicted"]
    rows.append({
        "geo": c,
        "avg_residual": test["residual"].mean(),
        "min_residual": test["residual"].min(),
        "max_residual": test["residual"].max(),
        "n_years": len(test),
    })

result = pd.DataFrame(rows).sort_values("avg_residual", ascending=False)
result.to_csv(f"{OUT}/leave_one_out_all_countries.csv", index=False)
pd.set_option("display.width", 160)
print(result.round(1).to_string(index=False))

others = result[result.geo != "EL"]["avg_residual"]
gr = result[result.geo == "EL"]["avg_residual"].iloc[0]
print(f"\nGreece leave-out avg residual: {gr:.1f}")
print(f"Other 26 countries' leave-out avg residual: mean={others.mean():.1f}, sd={others.std():.1f}, "
      f"min={others.min():.1f}, max={others.max():.1f}")
print(f"Greece's z-score vs the other 26: {(gr - others.mean()) / others.std():.2f}")
n_more_extreme = (others.abs() >= abs(gr)).sum()
print(f"Countries with |avg residual| >= Greece's: {n_more_extreme} of 26")
