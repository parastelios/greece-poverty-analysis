"""Thin client for the Eurostat SDMX-JSON dissemination API."""
import itertools
import json
import time
import urllib.parse

import pandas as pd
import requests

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def fetch(dataset: str, retries: int = 3, **params) -> pd.DataFrame:
    """Fetch a Eurostat dataset and return a tidy long-format DataFrame.

    params: SDMX dimension filters, e.g. geo=["EL", "EU27_2020"], time=range(2003, 2026)
    List/tuple values are repeated as multiple query params (OR filter), per Eurostat API.
    """
    query = []
    for k, v in params.items():
        if isinstance(v, (list, tuple, range)):
            for item in v:
                query.append((k, str(item)))
        else:
            query.append((k, str(v)))
    query.append(("format", "JSON"))
    query.append(("lang", "en"))
    url = f"{BASE}/{dataset}?" + urllib.parse.urlencode(query)

    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    else:
        raise RuntimeError(f"Failed to fetch {dataset}: {last_err}\nURL: {url}")

    if "error" in data:
        raise RuntimeError(f"Eurostat API error for {dataset}: {data['error']}\nURL: {url}")

    dim_ids = data["id"]
    sizes = data["size"]
    dims = data["dimension"]

    # index -> category code, in dimension order, for each dim
    cat_lists = []
    for dim_id in dim_ids:
        idx_map = dims[dim_id]["category"]["index"]
        # idx_map: code -> position; invert to position -> code
        pos_to_code = {v: k for k, v in idx_map.items()}
        cat_lists.append([pos_to_code[i] for i in range(len(pos_to_code))])

    labels = {}
    for dim_id in dim_ids:
        labels[dim_id] = dims[dim_id]["category"].get("label", {})

    values = data.get("value", {})

    # Build multipliers for row-major flat index (matches Eurostat's ordering)
    n = len(dim_ids)
    multipliers = [1] * n
    for i in range(n - 2, -1, -1):
        multipliers[i] = multipliers[i + 1] * sizes[i + 1]

    records = []
    for flat_str, val in values.items():
        flat = int(flat_str)
        rem = flat
        combo = {}
        for i, dim_id in enumerate(dim_ids):
            pos = rem // multipliers[i]
            rem = rem % multipliers[i]
            code = cat_lists[i][pos]
            combo[dim_id] = code
        combo["value"] = val
        records.append(combo)

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df

    # attach human labels for geo and time if present
    if "geo" in df.columns:
        df["geo_label"] = df["geo"].map(labels.get("geo", {}))
    if "time" in df.columns and df["time"].str.match(r"^\d+$").all():
        df["time"] = df["time"].astype(int)

    return df


if __name__ == "__main__":
    df = fetch(
        "ilc_li02",
        sex="T", age="TOTAL", unit="PC", statinfo="MED_EI", rskpovth="B_60",
        geo=["EL", "EU27_2020"], time=range(2020, 2024),
    )
    print(df)
