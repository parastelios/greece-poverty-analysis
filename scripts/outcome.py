"""The project's outcome series: the backward-extended official
subjective-hardship indicator.

P0 (scripts/51_p0_outcome_reconciliation.py) established that Eurostat's
ilc_sbjp01 IS the DIF + GRT aggregation of ilc_mdes09: across 432 overlapping
country-years, 318 agree exactly, 114 differ by one rounding step, none by more
than 0.1 pp, with cross-country Spearman 1.00 in every year.

Rule 2 of docs/archive/pre-v2-publication/project_description_v3.md §4a.1 follows from that: where Eurostat
publishes the indicator, use Eurostat's figure rather than recomputing it.

    2010 onward  ->  ilc_sbjp01 directly (official)
    before 2010  ->  ilc_mdes09 DIF + GRT (validated backward extension)

Two things this module deliberately does NOT claim:

  - That Eurostat published ilc_sbjp01 before 2010. It does not. The pre-2010
    values are derived from official components using a rule validated against
    the later official series (rule 4).
  - That the pre-2010 vintages are free of national survey breaks. The overlap
    validates the AGGREGATION RULE only; earlier-vintage comparability is a
    separate question this cannot answer (rule 3).

V1 is frozen and does not use this module. It is for V2 work only.
"""
import pandas as pd

from eurostat import fetch
from eu_membership import eu_members

SPLICE_YEAR = 2010


def official_hardship(years=range(2003, 2026), members_only=True):
    """Return geo/time/value for the backward-extended official indicator,
    plus a `source` column naming which series each row came from."""
    members = sorted(eu_members(2025))

    off = fetch("ilc_sbjp01", time=years, age=["TOTAL"], sex=["T"], unit=["PC"])
    off = off[["geo", "time", "value"]].copy()
    off = off[off.time >= SPLICE_YEAR]
    off["source"] = "ilc_sbjp01 (official)"

    ext = fetch("ilc_mdes09", time=years, hhcomp=["TOTAL"], rskpovth=["TOTAL"],
                unit=["PC"], lev_diff=["DIF", "GRT"])
    ext = ext.groupby(["geo", "time"], as_index=False)["value"].sum()
    ext = ext[ext.time < SPLICE_YEAR]
    ext["source"] = "ilc_mdes09 DIF+GRT (validated backward extension)"

    d = pd.concat([ext, off], ignore_index=True)
    if members_only:
        d = d[d.geo.isin(members)]
    return d.sort_values(["geo", "time"]).reset_index(drop=True)


def hardship_gap(years=range(2003, 2026)):
    """Secondary outcome (§4a): hardship minus AROP. Reported as a distinct
    result, never as a substitute for the level."""
    h = official_hardship(years)
    arop = fetch("ilc_li02", time=years, age=["TOTAL"], sex=["T"], unit=["PC"],
                 statinfo=["MED_EI"], rskpovth=["B_60"])[["geo", "time", "value"]]
    arop = arop.rename(columns={"value": "arop"})
    d = h.merge(arop, on=["geo", "time"], how="inner")
    d["gap"] = d["value"] - d["arop"]
    return d


if __name__ == "__main__":
    d = official_hardship()
    print(f"{len(d)} country-years, {d.geo.nunique()} countries, "
          f"{int(d.time.min())}-{int(d.time.max())}")
    print(d.source.value_counts().to_string())
    print(f"\nsplice check around {SPLICE_YEAR}, Greece:")
    g = d[(d.geo == "EL") & d.time.between(SPLICE_YEAR - 3, SPLICE_YEAR + 2)]
    print(g.to_string(index=False))
    pre = d[d.time < SPLICE_YEAR].geo.nunique()
    print(f"\npre-2010 country coverage: {pre} | 2003-2009 years available: "
          f"{sorted(d[d.time < SPLICE_YEAR].time.unique())}")
