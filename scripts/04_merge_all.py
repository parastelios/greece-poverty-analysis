"""Merge core master table with supplementary variables into one analysis-ready dataset."""
import glob
import os

import pandas as pd

RAW = "../data/raw"
OUT = "../data/processed"

EU_AGG_PRIORITY = ["EU27_2020", "EU27_2007", "EU28", "EU", "EA20", "EA19"]

SKIP = {"arop_all_countries", "subjective_poverty_all_countries"}

master = pd.read_csv(f"{OUT}/master_table.csv")

var_files = sorted(glob.glob(f"{RAW}/*.csv"))
source_log = []

for path in var_files:
    name = os.path.splitext(os.path.basename(path))[0]
    if name in SKIP:
        continue
    df = pd.read_csv(path)
    if "geo" not in df.columns:
        # Greece-only files consumed directly by a specific script (e.g. anchor_rates,
        # gr_saving_rate) rather than through this generic cross-country merge.
        print(f"[SKIP] {name}: no 'geo' column, not a generic cross-country file")
        continue
    time_col = "time" if "time" in df.columns else ("year" if "year" in df.columns else None)
    if time_col is None:
        print(f"[SKIP] {name}: no 'time' or 'year' column")
        continue
    if time_col != "time":
        df = df.rename(columns={time_col: "time"})
    if df.duplicated(subset=["geo", "time"]).any():
        # Has an extra dimension (e.g. tenure status, price category) not collapsed to
        # one row per geo/time -- not a generic single-value cross-country file. Merging
        # it here would fan out every row of master via a many-to-many join.
        print(f"[SKIP] {name}: multiple rows per geo/time (extra dimension not filtered) -- "
              f"not a generic single-value cross-country file")
        continue
    value_col = [c for c in df.columns if c not in ("geo", "time", "geo_label")][0]

    gr = df[df.geo == "EL"][["time", value_col]].rename(columns={value_col: f"gr_{name}"})
    master = master.merge(gr, left_on="year", right_on="time", how="left").drop(columns=["time"])

    eu_rows = []
    for year in master["year"]:
        year_df = df[df["time"] == year]
        chosen = None
        for code in EU_AGG_PRIORITY:
            m = year_df[year_df["geo"] == code]
            if len(m) and pd.notna(m.iloc[0][value_col]):
                chosen = (m.iloc[0][value_col], code)
                break
        eu_rows.append(chosen if chosen else (None, None))
    master[f"eu_{name}"] = [r[0] for r in eu_rows]
    src_col = f"eu_{name}_src"
    master[src_col] = [r[1] for r in eu_rows]
    n_gr = master[f"gr_{name}"].notna().sum()
    n_eu = master[f"eu_{name}"].notna().sum()
    source_log.append((name, n_gr, n_eu))

master.to_csv(f"{OUT}/analysis_dataset.csv", index=False)
print(f"Merged dataset: {master.shape[0]} rows x {master.shape[1]} cols")
print(f"Saved to {OUT}/analysis_dataset.csv\n")
print(f"{'variable':40s} {'GR years':>10s} {'EU years':>10s}")
for name, n_gr, n_eu in source_log:
    print(f"{name:40s} {n_gr:10d} {n_eu:10d}")
