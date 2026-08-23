"""Pre-registered accumulation transforms, as tested functions.

Every formula here is quoted from data/processed/e_preregistration.json and must
not be changed to fit a result. The risks these functions carry are the ones
that do not announce themselves:

  * a baseline year silently missing for some country, making its whole
    accumulation NaN or -- worse -- zero
  * a running sum that sees the future, because a groupby was not sorted
  * a floor applied to the wrong side, turning recovery into damage
  * a DURATION counted as a total rather than as a consecutive run that resets

The last one has already bitten this project once: variables named
"years below" were documented as totals when they are consecutive-run counts.
"""
import numpy as np
import pandas as pd

ID, TIME = "geo", "time"


def _prep(df, value_col):
    d = df.dropna(subset=[value_col]).sort_values([ID, TIME]).copy()
    if d[[ID, TIME]].duplicated().any():
        dup = d[d[[ID, TIME]].duplicated()][[ID, TIME]].head()
        raise ValueError(f"duplicate {ID}/{TIME} rows: {dup.to_dict('records')}")
    return d


def _require_baseline(d, value_col, base_year):
    """Countries with no observation in the baseline year get NO accumulation.

    Returning zero for them would read as 'no damage', which is the opposite of
    'not measurable'.
    """
    have = set(d[d[TIME] == base_year][ID])
    missing = sorted(set(d[ID]) - have)
    return have, missing


def cumulative_shortfall_from_index(df, value_col, base_year, out_col):
    """sum over years >= base of max(0, 100 - x_t), x already indexed base=100."""
    d = _prep(df, value_col)
    d["_s"] = (100 - d[value_col]).clip(lower=0)
    d = d[d[TIME] >= base_year]
    d[out_col] = d.groupby(ID)["_s"].cumsum()
    return d[[ID, TIME, out_col]]


def cumulative_excess_over_own_base(df, value_col, base_year, out_col):
    """sum over years >= base of max(0, x_t - x_base)."""
    d = _prep(df, value_col)
    have, missing = _require_baseline(d, value_col, base_year)
    base = (d[d[TIME] == base_year][[ID, value_col]]
            .rename(columns={value_col: "_b"}))
    d = d.merge(base, on=ID, how="left")
    d["_e"] = (d[value_col] - d["_b"]).clip(lower=0)
    d = d[d[TIME] >= base_year]
    d[out_col] = d.groupby(ID)["_e"].cumsum()
    d.loc[d[ID].isin(missing), out_col] = np.nan
    return d[[ID, TIME, out_col]]


def cumulative_excess_over_fixed(df, value_col, base_year, out_col, benchmark=100.0):
    """sum over years >= base of max(0, x_t - benchmark).

    For measures already expressed against an external benchmark (C4's
    wage-adjusted affordability, where EU27 = 100), so there is no own-country
    base year to align to.
    """
    d = _prep(df, value_col)
    d["_e"] = (d[value_col] - benchmark).clip(lower=0)
    d = d[d[TIME] >= base_year]
    d[out_col] = d.groupby(ID)["_e"].cumsum()
    return d[[ID, TIME, out_col]]


def cumulative_sum(df, value_col, base_year, out_col):
    """sum over years >= base of x_t, for series already non-negative."""
    d = _prep(df, value_col)
    if (d[d[TIME] >= base_year][value_col] < 0).any():
        raise ValueError(f"{value_col} has negative values; it is not a shortfall")
    d = d[d[TIME] >= base_year]
    d[out_col] = d.groupby(ID)[value_col].cumsum()
    return d[[ID, TIME, out_col]]


def compounded_growth(df, value_col, base_year, out_col):
    """prod over years base..t of (1 + r_s/100) - 1, r in percent.

    COMPOUNDED, NOT SUMMED. This is cumulative PRICE GROWTH -- not
    affordability, and not hardship. Returned in percent.
    """
    d = _prep(df, value_col)
    d = d[d[TIME] >= base_year]
    d["_f"] = 1 + d[value_col] / 100.0
    d[out_col] = (d.groupby(ID)["_f"].cumprod() - 1) * 100
    return d[[ID, TIME, out_col]]


def consecutive_years_below(df, value_col, base_year, out_col, threshold=100.0):
    """Length of the CURRENT unbroken run of years with x_t < threshold.

    Resets to zero the moment a year is not below. This is NOT a running total
    of years spent below, and describing it as one is a documented past error
    in this project.
    """
    d = _prep(df, value_col)
    d = d[d[TIME] >= base_year]
    out = []
    for g, grp in d.groupby(ID, sort=True):
        grp = grp.sort_values(TIME)
        run, runs = 0, []
        for below in (grp[value_col] < threshold):
            run = run + 1 if below else 0
            runs.append(run)
        out.append(pd.DataFrame({ID: g, TIME: grp[TIME].values, out_col: runs}))
    return pd.concat(out, ignore_index=True)


def rebuild_and_compare(fn, source, value_col, base_year, out_col, atol=1e-9):
    """Rebuild on truncated data and compare, for every country and year.

    Returns a list of (geo, year, full_value, truncated_value) disagreements.
    """
    full = fn(source, value_col, base_year, out_col).set_index([ID, TIME])[out_col]
    bad = []
    for g, grp in source.dropna(subset=[value_col]).groupby(ID):
        years = sorted(y for y in grp[TIME].unique() if y >= base_year)
        for t in years:
            trunc = source[(source[ID] == g) & (source[TIME] <= t)]
            got = fn(trunc, value_col, base_year, out_col)
            row = got[got[TIME] == t]
            if row.empty or (g, t) not in full.index:
                continue
            a, b = float(full.loc[(g, t)]), float(row[out_col].iloc[0])
            if not (np.isnan(a) and np.isnan(b)) and abs(a - b) > atol:
                bad.append((g, t, a, b))
    return bad
