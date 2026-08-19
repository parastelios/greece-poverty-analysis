"""P2a: real wages. Named in the original project brief, never fetched
until now (Methods has explicitly flagged this absence since the
traceability review). Checked for feasibility first, same discipline as
every other P1/P2 item: full 27-country, 2000-2024 coverage on the nominal
series -- genuinely better coverage than several variables already in the
project.

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
"""
import pandas as pd
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
YEARS = range(2000, 2025)
EU = eu_members(2024)
ANCHOR = 2008

nominal = fetch("nama_10_lp_ulc", na_item="D1_SAL_PER", unit="EUR", time=YEARS)
nominal = nominal[nominal.geo.isin(EU)][["geo", "time", "value"]].rename(columns={"value": "nominal_comp_per_employee"})
nominal.to_csv(f"{RAW}/panel_nominal_compensation.csv", index=False)

hicp = fetch("prc_hicp_aind", coicop="CP00", unit="INX_A_AVG", time=YEARS)
hicp = hicp[hicp.geo.isin(EU)][["geo", "time", "value"]].rename(columns={"value": "hicp_index"})
hicp.to_csv(f"{RAW}/panel_hicp_index.csv", index=False)

panel = nominal.merge(hicp, on=["geo", "time"], how="inner")

# deflate to real terms, anchored so each country's own 2008 value = 100
anchor_hicp = panel[panel.time == ANCHOR].set_index("geo")["hicp_index"]
anchor_nominal = panel[panel.time == ANCHOR].set_index("geo")["nominal_comp_per_employee"]
panel["real_wage_idx2008"] = panel.apply(
    lambda r: 100 * (r["nominal_comp_per_employee"] / r["hicp_index"]) /
              (anchor_nominal.get(r["geo"], float("nan")) / anchor_hicp.get(r["geo"], float("nan")))
    if r["geo"] in anchor_hicp.index else None, axis=1)
panel.to_csv(f"{OUT}/real_wages_panel.csv", index=False)

print(f"Coverage: {panel.geo.nunique()} of {len(EU)} EU countries")
print(panel.groupby("geo").time.count().describe())

print("\n=== Greece: nominal compensation/employee, HICP, real wage index (2008=100) ===")
gr = panel[panel.geo == "EL"].sort_values("time")
print(gr.round(1).to_string(index=False))

print(f"\nGreece real wage index, 2024 vs 2008: {gr[gr.time==2024]['real_wage_idx2008'].iloc[0]:.1f} (2008=100)")
peak_row = gr.loc[gr["real_wage_idx2008"].idxmax()]
print(f"Greece real wage peak: {peak_row['real_wage_idx2008']:.1f} in {int(peak_row['time'])}")
trough_row = gr[(gr.time >= peak_row["time"])].loc[gr[(gr.time >= peak_row["time"])]["real_wage_idx2008"].idxmin()]
print(f"Trough after that peak: {trough_row['real_wage_idx2008']:.1f} in {int(trough_row['time'])}")

# cross-country comparison: current (2024) real wage index vs 2008, and vs each country's own peak
last = panel[panel.time == 2024][["geo", "real_wage_idx2008"]].rename(columns={"real_wage_idx2008": "idx2024_vs_2008"})
peaks = panel.loc[panel.groupby("geo")["real_wage_idx2008"].idxmax()][["geo", "real_wage_idx2008", "time"]].rename(
    columns={"real_wage_idx2008": "peak_val", "time": "peak_year"})
comp = last.merge(peaks, on="geo").sort_values("idx2024_vs_2008")
comp["pct_below_2008"] = 100 - comp["idx2024_vs_2008"]
comp.to_csv(f"{OUT}/real_wages_cross_country_2024.csv", index=False)
print("\n=== Real wage index 2024 (2008=100), all 27 EU countries, lowest first ===")
print(comp.round(1).to_string(index=False))

# correlation with subjective poverty (Greece-only, matching Section 4's existing correlation table)
gr_hh = gr[["time", "real_wage_idx2008"]].rename(columns={"time": "year"})
subj = pd.read_csv(f"{OUT}/master_table.csv")[["year", "gr_subjective_poverty"]]
merged = gr_hh.merge(subj, on="year").dropna()
if len(merged) >= 5:
    from scipy.stats import pearsonr
    r0, p0 = pearsonr(merged["real_wage_idx2008"], merged["gr_subjective_poverty"])
    d1 = merged.diff().dropna()
    r1, p1 = pearsonr(d1["real_wage_idx2008"], d1["gr_subjective_poverty"])
    print(f"\n=== Greece: real wage index vs subjective poverty ===")
    print(f"Level correlation: r={r0:.2f}, p={p0:.4f}, n={len(merged)}")
    print(f"First-difference correlation: r={r1:.2f}, p={p1:.4f}, n={len(d1)}")
