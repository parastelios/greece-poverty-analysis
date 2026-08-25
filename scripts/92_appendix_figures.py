"""Detailed figures that belong in the appendix rather than the report.

Three kinds of thing land here. Views the report simplified away, because the
simplification was right for a reader following an argument and wrong for one
checking it: the raw affordability observations behind the binned European
view, and the hardship-against-income-poverty scatter for every year rather
than the latest. And the full correlation matrix, which at 35 variables shows
almost nothing to a reader and is exactly what someone auditing variable
selection wants.

These are built the same way as the report's figures, through the shared
engine, so the appendix can carry them beside the report's own without a second
rendering path.
"""
import json
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
panel = pd.read_csv(PROC / "e0_extended_panel.csv")

NAMES = {"EL": "Greece", "BG": "Bulgaria", "RO": "Romania", "HU": "Hungary",
         "LU": "Luxembourg", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
         "EE": "Estonia", "ES": "Spain", "PT": "Portugal", "IT": "Italy",
         "FR": "France", "DE": "Germany", "NL": "Netherlands", "BE": "Belgium",
         "AT": "Austria", "IE": "Ireland", "FI": "Finland", "SE": "Sweden",
         "DK": "Denmark", "PL": "Poland", "CZ": "Czechia", "SK": "Slovakia",
         "SI": "Slovenia", "HR": "Croatia", "MT": "Malta"}
ITEMS = [("unexpected_expenses", "Cannot meet an unexpected expense"),
         ("severe_mat_soc_deprivation", "Material deprivation"),
         ("arrears", "Arrears on bills"),
         ("warm", "Cannot keep the home warm")]

FIGS = {}

# ---- A1: every observation behind the binned European view ----------------
panels_raw, fA1 = [], ce.Series(["Country-years", "Pooled correlation"], dp=3)
for col, label in ITEMS:
    d = panel.dropna(subset=[col, "subjective_poverty"]).copy()
    for c in [col, "subjective_poverty"]:
        d[c + "_w"] = d[c] - d.groupby("geo")[c].transform("mean")
    r = float(d["subjective_poverty_w"].corr(d[col + "_w"]))
    sx = d[col + "_w"].std()
    sy = d["subjective_poverty_w"].std()
    fA1.add(label, [float(len(d)), r])
    panels_raw.append({
        "label": label, "r": round(r, 3), "xLabel": "",
        "points": [{"x": round(float(a) / sx, 2), "y": round(float(b) / sy, 2),
                    "highlight": g == "EL"}
                   for g, a, b in zip(d.geo, d[col + "_w"],
                                      d["subjective_poverty_w"])]})

FIGS["A1"] = dict(
    caption="Every country-year behind the binned European view",
    kind="multiples",
    payload={"panels": panels_raw,
             "xMin": -4, "xMax": 4, "yMin": -4, "yMax": 4,
             "xTicks": [-2, 0, 2], "yTicks": [-2, 0, 2],
             "yLabel": "Reported hardship, standard deviations from the "
                       "country's own average",
             "alt": "The raw country-year observations the report's binned "
                    "view summarises, with Greek observations marked"},
    series=fA1, first="Measure",
    extra_caveat=(
        "These are the observations the report's second view bins. Both axes "
        "are in standard deviations from each country's own average. Greek "
        "observations are marked. At this density the cloud shows spread "
        "rather than shape, which is why the report bins it."))

# ---- A4: the European relationship, binned --------------------------------
# This was a second view of the report's Figure 7. It needs standard
# deviations, demeaned observations, bins and a pooled correlation explained
# before it can be read, which is appendix work rather than report work.
panels_eu, fA4 = [], ce.Series(["Bins", "Country-years", "Pooled correlation"], dp=3)
for col, label in ITEMS:
    d = panel.dropna(subset=[col, "subjective_poverty"]).copy()
    for c in [col, "subjective_poverty"]:
        d[c + "_w"] = d[c] - d.groupby("geo")[c].transform("mean")
    r = float(d["subjective_poverty_w"].corr(d[col + "_w"]))
    d[col + "_z"] = d[col + "_w"] / d[col + "_w"].std()
    d["hard_z"] = d["subjective_poverty_w"] / d["subjective_poverty_w"].std()
    d["_bin"] = pd.qcut(d[col + "_z"], 9, labels=False, duplicates="drop")
    b = d.groupby("_bin").agg(x=(col + "_z", "mean"),
                              y=("hard_z", "mean")).reset_index()
    sxx = ((b.x - b.x.mean()) ** 2).sum()
    b1 = (((b.x - b.x.mean()) * (b.y - b.y.mean())).sum() / sxx) if sxx else 0.0
    fA4.add(label, [float(len(b)), float(len(d)), r])
    panels_eu.append({
        "label": label, "r": round(r, 3), "xLabel": "",
        "points": [{"x": round(float(x), 2), "y": round(float(y), 2)}
                   for x, y in zip(b.x, b.y)],
        "fit": {"b1": round(b1, 4),
                "b0": round(float(b.y.mean() - b1 * b.x.mean()), 4)}})

FIGS["A4"] = dict(
    caption="The European relationship, as binned country-year averages",
    kind="multiples",
    payload={"panels": panels_eu,
             "xMin": -2.2, "xMax": 2.2, "yMin": -2.2, "yMax": 2.2,
             "xTicks": [-1, 0, 1], "yTicks": [-1, 0, 1],
             "yLabel": "Reported hardship, standard deviations from the "
                       "country's own average",
             "alt": "Nine binned averages per measure, each grouping "
                    "country-years where the measure sat similarly above or "
                    "below that country's normal level"},
    series=fA4, first="Measure",
    extra_caveat=(
        "Both axes are in standard deviations from each country's own average, "
        "so one step means the same thing in all four panels. The line is "
        "fitted through the nine plotted bins while the correlation in each "
        "title is computed from all country-years: they are not the same "
        "calculation."))

# ---- A2: the cross-section, every year ------------------------------------
both = panel.dropna(subset=["subjective_poverty", "arop"])
years = [int(y) for y in sorted(both.time.unique())
         if both[both.time == y].geo.nunique() >= 25]
frames = []
for y in years:
    s = both[both.time == y]
    frames.append({"label": str(y), "points": [
        {"x": round(float(r.arop), 1), "y": round(float(r.subjective_poverty), 1),
         "label": NAMES.get(r.geo, r.geo), "highlight": r.geo == "EL"}
        for r in s.itertuples()]})

fA2 = ce.Series(["Greece: income poverty", "Greece: reported hardship",
                 "Median country: income poverty",
                 "Median country: reported hardship"], dp=1)
for y in years:
    s = both[both.time == y]
    g = s[s.geo == "EL"].iloc[0]
    fA2.add(str(y), [float(g.arop), float(g.subjective_poverty),
                     float(s.arop.median()), float(s.subjective_poverty.median())])

FIGS["A2"] = dict(
    caption="Where every country stood, year by year",
    kind="scatter",
    payload={"frames": frames, "dp": 1, "aspect": 0.52,
             "xLabel": "Income poverty, percent of people",
             "yLabel": "Reported hardship, percent of households",
             "fitExcludesHighlight": True,
             "fitLabel": "Peer relationship, Greece excluded",
             "points": frames[-1]["points"],
             "alt": "Every EU country placed by income poverty and reported "
                    "hardship, with a selector for each year from "
                    f"{years[0]} to {years[-1]}"},
    series=fA2, first="Year",
    extra_caveat=(
        "The report carries the latest year only. The axes here are fixed "
        "across every year, so switching year moves the countries and not the "
        "scale. The fitted line excludes Greece in each year."))

# ---- A3: the full correlation matrix --------------------------------------
for label, fname in [("Within countries", "e0_corr_within.csv"),
                     ("Between countries", "e0_corr_between.csv"),
                     ("All country-years", "e0_corr_pooled.csv")]:
    m = pd.read_csv(PROC / fname, index_col=0)
    keep = list(m.index)
    s = ce.Series([ce.name(c) for c in keep], dp=3, title=label)
    for r in keep:
        s.add(ce.name(r), [float(m.loc[r, c]) for c in keep])
    FIGS[f"A3{label[0]}"] = dict(
        caption=f"The full {len(keep)}-variable correlation matrix, {label.lower()}",
        kind="heatmap",
        payload={"cols": [ce.name(c) for c in keep],
                 "rows": [{"label": ce.name(r),
                           "values": [round(float(m.loc[r, c]), 3) if i != j else None
                                      for j, c in enumerate(keep)]}
                          for i, r in enumerate(keep)],
                 "flags": [[0] * len(keep) for _ in keep],
                 "flagLabel": "", "flagExplain": "",
                 "alt": f"All {len(keep)} variables correlated {label.lower()}, "
                        "diagonal blank"},
        series=s, first="Variable",
        extra_caveat=(
            "The report shows ten construct representatives because at this "
            "size a matrix contains everything and shows almost nothing. It is "
            "here for anyone checking which variables duplicate which."))


def payload_tag(d, kind="", label=""):
    body = json.dumps(d).replace("</", "<\\/")
    a = (f' data-kind="{kind}"' if kind else "") + \
        (f' data-label="{label}"' if label else "")
    return f'<script type="application/json"{a}>{body}</script>'


def build(fid, spec):
    body = spec["series"].fallback_table(spec.get("first", ""))
    shell = ce.figure(fid, spec["caption"], spec.get("question", ""),
                      "appendix", spec["kind"], {}, body,
                      caveat=spec.get("extra_caveat", ""),
                      checksum=spec["series"].checksum())
    return shell.replace(payload_tag({}), payload_tag(spec["payload"]))


CARDS = "\n".join(build(k, v) for k, v in FIGS.items())
(OUT / "_appendix_figures.html").write_text(
    f"<!doctype html><html><head><meta charset='utf-8'><style>{ce.CSS}</style>"
    f"</head><body>{CARDS}<script>{ce.JS}</script></body></html>")
print(f"built {len(FIGS)} appendix figures: {', '.join(FIGS)}")
