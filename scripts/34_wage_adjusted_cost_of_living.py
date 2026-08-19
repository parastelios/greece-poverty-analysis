"""P2e: wage-adjusted cost-of-living pressure. Not "are Greek prices high"
in isolation, but "how far does a Greek paycheck stretch on essentials
compared with the rest of the EU" -- price level (Eurostat's comparative
price level indices, EU27=100) set against wage level (nominal
compensation per employee, same EU27=100 benchmarking), category by
category.

Checkpoint script: computes and prints/saves results only. Does not touch
the report.
"""
import pandas as pd
from eurostat import fetch
from eu_membership import eu_members

RAW = "../data/raw"
OUT = "../data/processed"
EU = eu_members(2024)

CATEGORIES = {
    "A01": "Overall household consumption",
    "A0101": "Food & non-alcoholic beverages",
    "A0104": "Housing, water, electricity, gas & fuels",
    "A0107": "Transport",
    "A0111": "Restaurants & accommodation",
    "A0108": "Information & communication",
}

# --- 1. Feasibility: coverage by category ---
print("=== Feasibility: 27-country coverage by category, prc_ppp_ind_1 (PLI_EU27_2020) ===")
price_frames = {}
for cat, label in CATEGORIES.items():
    df = fetch("prc_ppp_ind_1", indic_ppp="PLI_EU27_2020", ppp_cat18=cat, time=range(2000, 2025))
    df_eu = df[df.geo.isin(EU)][["geo", "time", "value"]].rename(columns={"value": "price_level"})
    df_eu["category"] = cat
    price_frames[cat] = df_eu
    years = sorted(df_eu.time.unique())
    print(f"  {cat} ({label}): {df_eu.geo.nunique()} countries, years {years[0]}-{years[-1]} "
          f"({len(years)} distinct years)")

all_prices = pd.concat(price_frames.values(), ignore_index=True)
all_prices.to_csv(f"{RAW}/panel_price_levels_by_category.csv", index=False)

# --- 2. Descriptive cross-country: latest year, price level ---
print("\n=== Greece price level vs EU average (=100), latest available year per category ===")
for cat, label in CATEGORIES.items():
    d = price_frames[cat]
    latest_year = d.time.max()
    gr_val = d[(d.geo == "EL") & (d.time == latest_year)]["price_level"]
    if len(gr_val):
        rank = d[d.time == latest_year].sort_values("price_level", ascending=False).reset_index(drop=True)
        gr_rank = rank[rank.geo == "EL"].index[0] + 1
        print(f"  {label} ({latest_year}): Greece = {gr_val.iloc[0]:.1f}, rank {gr_rank} of {len(rank)} (1=most expensive)")

# --- Wage level vs EU average, same benchmarking ---
print("\n=== Wage level vs EU average (=100), nominal compensation per employee ===")
nom = fetch("nama_10_lp_ulc", na_item="D1_SAL_PER", unit="EUR", time=range(2000, 2025))
nom_eu = nom[nom.geo.isin(EU + ["EU27_2020"])][["geo", "time", "value"]].rename(columns={"value": "nominal_comp"})
nom_eu.to_csv(f"{RAW}/panel_nominal_compensation_wage_level.csv", index=False)

eu_avg = nom_eu[nom_eu.geo == "EU27_2020"].set_index("time")["nominal_comp"]
wage_level = nom_eu[nom_eu.geo != "EU27_2020"].copy()
wage_level["wage_level_vs_eu"] = wage_level.apply(
    lambda r: 100 * r["nominal_comp"] / eu_avg.get(r["time"], float("nan")), axis=1)
wage_level.to_csv(f"{OUT}/wage_level_vs_eu.csv", index=False)

latest_wage_year = wage_level.time.max()
gr_wage = wage_level[(wage_level.geo == "EL") & (wage_level.time == latest_wage_year)]
wage_rank = wage_level[wage_level.time == latest_wage_year].sort_values("wage_level_vs_eu").reset_index(drop=True)
gr_wage_rank = wage_rank[wage_rank.geo == "EL"].index[0] + 1
print(f"  Greece wage level ({latest_wage_year}): {gr_wage['wage_level_vs_eu'].iloc[0]:.1f} (EU=100), "
      f"rank {gr_wage_rank} of {len(wage_rank)} (1=lowest)")

# --- 3. Wage-adjusted price pressure: price_level / wage_level * 100 ---
print("\n=== Wage-adjusted price pressure (price level / wage level x 100), latest year, Greece ===")
print("(>100 = this category costs proportionally MORE of a Greek paycheck than of an EU-average paycheck)")
combined_rows = []
for cat, label in CATEGORIES.items():
    d = price_frames[cat]
    latest_year = d.time.max()
    merged = d[d.time == latest_year].merge(
        wage_level[wage_level.time == latest_wage_year][["geo", "wage_level_vs_eu"]], on="geo", how="inner")
    merged["wage_adjusted_pressure"] = 100 * merged["price_level"] / merged["wage_level_vs_eu"]
    merged["category"] = cat
    combined_rows.append(merged)
    gr = merged[merged.geo == "EL"]
    if len(gr):
        rank = merged.sort_values("wage_adjusted_pressure", ascending=False).reset_index(drop=True)
        gr_rank = rank[rank.geo == "EL"].index[0] + 1
        print(f"  {label}: price {gr['price_level'].iloc[0]:.1f} / wage {gr['wage_level_vs_eu'].iloc[0]:.1f} "
              f"= pressure {gr['wage_adjusted_pressure'].iloc[0]:.1f}  (rank {gr_rank} of {len(rank)}, 1=highest pressure)")

combined = pd.concat(combined_rows, ignore_index=True)
combined.to_csv(f"{OUT}/wage_adjusted_price_pressure.csv", index=False)

print("\n=== Full ranking, food category, wage-adjusted pressure (highest first) ===")
food = combined[combined.category == "A0101"].sort_values("wage_adjusted_pressure", ascending=False)
print(food[["geo", "price_level", "wage_level_vs_eu", "wage_adjusted_pressure"]].round(1).to_string(index=False))

# --- 4. Time-series angle: Greece only, prices vs wages since 2008 ---
print("\n=== Greece time series: overall price level (EU=100) vs real wage index (2008=100) ===")
overall = price_frames["A01"]
gr_overall = overall[overall.geo == "EL"].sort_values("time")
print(gr_overall[["time", "price_level"]].round(1).to_string(index=False))

real_wages = pd.read_csv(f"{OUT}/real_wages_panel.csv")
gr_rw = real_wages[real_wages.geo == "EL"][["time", "real_wage_idx2008"]]
print("\nReal wage index (2008=100), same years:")
print(gr_rw[gr_rw.time.isin(gr_overall.time)].round(1).to_string(index=False))

# HICP category inflation, Greece, already-fetched series
print("\n=== HICP category inflation check (existing project data, Greece) ===")
try:
    hicp_food = pd.read_csv(f"{RAW}/hicp_food_rate.csv") if __import__("os").path.exists(f"{RAW}/hicp_food_rate.csv") else None
    print("(existing HICP series available in data/raw/ from earlier project rounds; see 03_fetch_supplementary.py)")
except Exception as e:
    print("Note:", e)
