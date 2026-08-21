"""Euro-changeover normalisation for national-currency (NAC) Eurostat series.

Eurostat's NAC series are in whatever currency the country used at the time, so
any country that adopted the euro mid-series has an undeflatable break in it.
Indexing such a series to a base year on the other side of that break produces
nonsense: Slovenia's real AROP threshold reads 22,445 in 2006 (tolar values
against a 2008 euro base) and Slovakia's reads 3.5 from 2009 (euro values
against a 2008 koruna base).

The fix is the irrevocable fixed conversion rate each country entered at. These
are immutable historical constants, not estimates.

Not every affected country actually shows the break -- Eurostat has already
back-converted some series (Estonia's is in euro throughout) -- so the break is
detected before it is corrected rather than assumed.
"""

# EUR = X units of the former national currency, on the official adoption date.
EURO_ADOPTION = {
    "SI": (2007, 239.640),    # tolar
    "CY": (2008, 0.585274),   # Cypriot pound
    "MT": (2008, 0.429300),   # Maltese lira
    "SK": (2009, 30.12600),   # koruna
    "EE": (2011, 15.64660),   # kroon
    "LV": (2014, 0.702804),   # lats
    "LT": (2015, 3.452800),   # litas
    "HR": (2023, 7.534500),   # kuna
}


def normalise_nac_to_euro(df, geo_col="geo", time_col="time", value_col=None,
                          verbose=True):
    """Convert pre-adoption values to euro for countries whose series breaks.

    Detects the break by comparing the last pre-adoption value with the first
    post-adoption one, then asking whether that ratio sits closer to the official
    conversion rate or to 1 (on a log scale, since the rate can be either side of
    1). A naive "ratio > rate/2" test is wrong for the currencies that were worth
    MORE than a euro -- the Cypriot pound, Maltese lira and Latvian lats -- and
    would convert series that Eurostat has already back-converted.
    Returns a copy; the input is not modified.
    """
    import math
    out = df.copy()
    for geo, (year, rate) in EURO_ADOPTION.items():
        sub = out[out[geo_col] == geo]
        pre = sub[sub[time_col] == year - 1][value_col]
        post = sub[sub[time_col] == year][value_col]
        if pre.empty or post.empty or not post.iloc[0]:
            continue
        ratio = pre.iloc[0] / post.iloc[0]
        if ratio <= 0:
            continue
        # Closer to the conversion rate than to 1 => a genuine currency break.
        near_rate = abs(math.log(ratio / rate))
        near_one = abs(math.log(ratio))
        if near_rate < near_one:
            mask = (out[geo_col] == geo) & (out[time_col] < year)
            out[value_col] = out[value_col].astype(float)
            out.loc[mask, value_col] = out.loc[mask, value_col] / rate
            if verbose:
                print(f"    {geo}: currency break at {year} (observed ratio {ratio:.1f} vs "
                      f"official {rate}) -- {int(mask.sum())} pre-adoption years converted to euro")
        elif verbose:
            print(f"    {geo}: no break at {year} (ratio {ratio:.2f}) -- already in euro, left alone")
    return out
