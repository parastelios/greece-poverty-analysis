"""Thin client for the Eurostat SDMX-JSON dissemination API."""
import itertools
import json
import os
import time
import urllib.parse

import pandas as pd
import requests

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# 25 scripts across this pipeline call fetch() unconditionally, with no
# cache -- every one of them contacts the live API on every run. That is
# exactly what let `make build` silently move the data vintage on 2026-09-10
# (see the Makefile's own top-of-file warning). This is the guard that
# incident argued for: fetch() refuses by default, so running one of those
# 25 scripts directly -- the natural thing to do while testing an unrelated
# change -- fails immediately and loudly, before any file is touched,
# instead of quietly refreshing dozens of data/raw/ and data/processed/
# files. The Makefile's fetch/fetch-write/build targets, the only places
# a live refresh is actually intended, set the env var themselves.
_ALLOW = os.environ.get("GREECE_POVERTY_ALLOW_FETCH") == "1"


def fetch(dataset: str, retries: int = 3, **params) -> pd.DataFrame:
    """Fetch a Eurostat dataset and return a tidy long-format DataFrame.

    params: SDMX dimension filters, e.g. geo=["EL", "EU27_2020"], time=range(2003, 2026)
    List/tuple values are repeated as multiple query params (OR filter), per Eurostat API.
    """
    if not _ALLOW:
        raise RuntimeError(
            f"refusing to fetch {dataset}: this contacts the live Eurostat "
            "API and would move the data vintage. Run via `make fetch`, "
            "`make fetch-write` or `make build` (which set "
            "GREECE_POVERTY_ALLOW_FETCH=1), or set that variable yourself "
            "if you specifically intend a live refresh.")
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
