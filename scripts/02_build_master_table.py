"""Build the core annual Greece-EU master table: levels, EU aggregate, rankings, gaps."""
import pandas as pd
from eu_membership import eu_members, composition_label

RAW = "../data/raw"
OUT = "../data/processed"

arop = pd.read_csv(f"{RAW}/arop_all_countries.csv")
sub = pd.read_csv(f"{RAW}/subjective_poverty_all_countries.csv")

# Official Eurostat EU-scope aggregates, in preference order (most current/comparable first,
# falling back to widen year coverage). EA (euro area) codes are intentionally excluded --
# different geographic scope than "EU".
EU_AGG_PRIORITY = ["EU27_2020", "EU27_2007", "EU28", "EU", "EU15"]


def eu_aggregate_series(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    rows = []
    for year in sorted(df["time"].unique()):
        year_df = df[df["time"] == year]
        for code in EU_AGG_PRIORITY:
            match = year_df[year_df["geo"] == code]
            if len(match) and pd.notna(match.iloc[0][value_col]):
                rows.append({"time": year, f"eu_{value_col}": match.iloc[0][value_col], f"eu_{value_col}_source": code})
                break
        else:
            rows.append({"time": year, f"eu_{value_col}": None, f"eu_{value_col}_source": None})
    return pd.DataFrame(rows)


def rank_greece(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Rank Greece among EU member states each year, 1 = highest poverty rate."""
    rows = []
    for year in sorted(df["time"].unique()):
        members = set(eu_members(int(year)))
        year_df = df[(df["time"] == year) & (df["geo"].isin(members)) & df[value_col].notna()]
        if not len(year_df):
            rows.append({"time": year, f"gr_{value_col}_rank": None, f"n_countries_{value_col}": 0})
            continue
        ranked = year_df.sort_values(value_col, ascending=False).reset_index(drop=True)
        ranked["rank"] = ranked.index + 1
        gr_row = ranked[ranked["geo"] == "EL"]
        gr_rank = int(gr_row["rank"].iloc[0]) if len(gr_row) else None
        rows.append({
            "time": year,
            f"gr_{value_col}_rank": gr_rank,
            f"n_countries_{value_col}": len(ranked),
        })
    return pd.DataFrame(rows)


# ---- AROP ----
eu_arop = eu_aggregate_series(arop, "arop")
rank_arop = rank_greece(arop, "arop")
gr_arop = arop[arop.geo == "EL"][["time", "arop"]].rename(columns={"arop": "gr_arop"})

# ---- Subjective poverty ----
eu_sub = eu_aggregate_series(sub, "subjective_poverty")
rank_sub = rank_greece(sub, "subjective_poverty")
gr_sub = sub[sub.geo == "EL"][["time", "subjective_poverty", "great_difficulty", "difficulty"]].rename(
    columns={"subjective_poverty": "gr_subjective_poverty"}
)

# ---- Merge into master table ----
master = gr_arop.merge(eu_arop, on="time").merge(rank_arop, on="time")
master = master.merge(gr_sub, on="time", how="outer").merge(eu_sub, on="time", how="outer").merge(rank_sub, on="time", how="outer")
master = master.sort_values("time").reset_index(drop=True)

master["gr_eu_arop_gap"] = master["gr_arop"] - master["eu_arop"]
master["gr_eu_subjective_gap"] = master["gr_subjective_poverty"] - master["eu_subjective_poverty"]
master["eu_composition"] = master["time"].apply(lambda y: composition_label(int(y)))

cols = [
    "time", "gr_arop", "eu_arop", "eu_arop_source", "gr_arop_rank", "n_countries_arop",
    "gr_subjective_poverty", "gr_great_difficulty" if False else "great_difficulty", "difficulty",
    "eu_subjective_poverty", "eu_subjective_poverty_source", "gr_subjective_poverty_rank", "n_countries_subjective_poverty",
    "gr_eu_arop_gap", "gr_eu_subjective_gap", "eu_composition",
]
master = master[[c for c in cols if c in master.columns]]
master = master.rename(columns={
    "time": "year",
    "gr_subjective_poverty_rank": "gr_subj_rank",
    "n_countries_subjective_poverty": "n_countries_subj",
})

master.to_csv(f"{OUT}/master_table.csv", index=False)
pd.set_option("display.width", 200)
print(master.to_string(index=False))
