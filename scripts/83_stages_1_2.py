"""Batch 1: stages 1 and 2, five figures from the frozen manifest.

Stage 2 carries three of them, which is the point of not enforcing one figure
per section: the moving threshold, the AROPE bridge and what sits behind AROPE
are three different questions.
"""
import json
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
man = pd.read_csv(PROC / "report_visual_manifest.csv").set_index("id")
panel = pd.read_csv(PROC / "e0_extended_panel.csv")
desc = pd.read_csv(PROC / "e_descriptives.csv")
ranks = pd.read_csv(PROC / "e_descriptive_ranks.csv")
NAMES = {"EL": "Greece", "BG": "Bulgaria", "RO": "Romania", "HU": "Hungary",
         "LU": "Luxembourg", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
         "EE": "Estonia", "ES": "Spain", "PT": "Portugal", "IT": "Italy",
         "FR": "France", "DE": "Germany", "NL": "Netherlands", "BE": "Belgium",
         "AT": "Austria", "IE": "Ireland", "FI": "Finland", "SE": "Sweden",
         "DK": "Denmark", "PL": "Poland", "CZ": "Czechia", "SK": "Slovakia",
         "SI": "Slovenia", "HR": "Croatia", "MT": "Malta"}
yrs = sorted(panel.time.unique())
gr = panel[panel.geo == "EL"].set_index("time")
med = panel.groupby("time")[["subjective_poverty", "arop", "arope",
                             "arop_threshold_real"]].median()


def payload_tag(d, kind="", label=""):
    body = json.dumps(d).replace("</", "<\\/")
    a = (f' data-kind="{kind}"' if kind else "") + \
        (f' data-label="{label}"' if label else "")
    return f'<script type="application/json"{a}>{body}</script>'


FIGS = {}

# ---- F1 ------------------------------------------------------------------
f1 = ce.Series([str(int(y)) for y in yrs], dp=1)
for lbl, src, tone, style, weight in [
        # Blue and orange are RESERVED for the Greece/EU comparison on the
        # headline measure. The second measure takes a neutral series colour
        # for both countries, distinguished by dash. Using EU-orange for a
        # Greek series made the palette mean two different things at once.
        ("Greece: reported hardship", gr.subjective_poverty, "gr", "solid", "strong"),
        ("EU median: reported hardship", med.subjective_poverty, "eu", "dashed", "normal"),
        ("Greece: income poverty", gr.arop, "series-3", "solid", "normal"),
        ("EU median: income poverty", med.arop, "series-3", "dashed", "light")]:
    f1.add(lbl, [float(src.get(y)) for y in yrs], tone=tone, style=style, weight=weight)
# Two views answering two questions. The first is the gap over time. The
# second asks whether income poverty accounts for it at all, by placing every
# country on the two measures at once.
ctx1 = []
for g, sub in panel.groupby("geo"):
    if g == "EL":
        continue
    s = sub.set_index("time").subjective_poverty
    vals = [float(s.get(y)) if y in s.index and pd.notna(s.get(y)) else None
            for y in yrs]
    if sum(v is not None for v in vals) >= 2:
        ctx1.append({"label": NAMES.get(g, g), "values": vals})

# Only hardship is drawn for every country. Adding AROP as well would put more
# than fifty background lines on one axis; the country spread of AROP is what
# the second view is for.
f1 = ce.Series([str(int(y)) for y in yrs], dp=1)
f1.add("Greece: reported hardship", [float(gr.subjective_poverty.get(y)) for y in yrs],
       tone="gr", style="solid", weight="strong")
f1.add("EU median: reported hardship", [float(med.subjective_poverty.get(y)) for y in yrs],
       tone="gr", style="dashed", weight="normal")
f1.add("Greece: income poverty", [float(gr.arop.get(y)) for y in yrs],
       tone="series-3", style="solid", weight="strong")
f1.add("EU median: income poverty", [float(med.arop.get(y)) for y in yrs],
       tone="series-3", style="dashed", weight="normal")
v1a = {"years": [int(y) for y in yrs], "dp": 1, "yLabel": "Percent",
       "context": ctx1,
       "contextLabel": "Each other EU country: reported hardship",
       "alt": "Greek reported hardship and income poverty against the EU median "
              "of each, with every other country's hardship faint behind. The "
              "distance between the blue and green Greek lines never closes",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                  for l, vs, m in f1.rows]}

# One year. The temporal story belongs to the first view; a year selector here
# would add controls without changing the conclusion. The year-by-year version
# is kept out of the report.
both = panel.dropna(subset=["subjective_poverty", "arop"])
_lastyr = int(max(y for y in both.time.unique()
                  if both[both.time == y].geo.nunique() >= 25))
_last = both[both.time == _lastyr]
_lel = _last[_last.geo == "EL"].iloc[0]
_medx, _medy = float(_last.arop.median()), float(_last.subjective_poverty.median())

pts1 = [{"x": round(float(r.arop), 1), "y": round(float(r.subjective_poverty), 1),
         "label": (f"Greece: income poverty {r.arop:.1f}%, hardship "
                   f"{r.subjective_poverty:.1f}%" if r.geo == "EL"
                   else NAMES.get(r.geo, r.geo)),
         "highlight": r.geo == "EL"} for r in _last.itertuples()]

f1b = ce.Series(["Income poverty (%)", "Reported hardship (%)"], dp=1)
for r in _last.sort_values("arop").itertuples():
    f1b.add(NAMES.get(r.geo, r.geo), [float(r.arop), float(r.subjective_poverty)])

v1b = {"points": pts1, "dp": 1,
       "xLabel": "Income poverty, percent of people",
       "yLabel": "Reported hardship, percent of households",
       "fitExcludesHighlight": True,
       "fitLabel": "Peer relationship, Greece excluded",
       # Guide lines rather than a synthetic point: a square at the two medians
       # is not a country and needs explaining before it can be read.
       "guides": [{"axis": "x", "value": round(_medx, 1),
                   "label": f"median country: {_medx:.1f}%"},
                  {"axis": "y", "value": round(_medy, 1),
                   "label": f"median country: {_medy:.1f}%"}],
       "frameLabel": str(_lastyr),
       "alt": f"Every EU country in {_lastyr} placed by income poverty and "
              "reported hardship. Greece has an ordinary income-poverty rate "
              "and an extraordinary hardship rate, far above the peer line"}

FIGS["F1"] = dict(
    caption="Greece reports far more hardship than countries with similar "
            "income poverty",
    kind="panel", series=f1, payload=v1a,
    views=[("How Greece's hardship gap developed", v1a),
           (f"Where countries stood in {_lastyr}", v1b, "scatter")],
    view_series=[f1, f1b],
    extra_caveat=(
        "Reported hardship is answered by HOUSEHOLDS and income poverty counts "
        "PEOPLE, so the axis is labelled percent rather than either. In the "
        "second view the fitted line excludes Greece, describing the European "
        "pattern Greece is being judged against rather than one Greece helped "
        "set, and the dashed guides mark the median country on each measure "
        "separately. Both views are country-level and say nothing about any "
        "individual household."),
    first="Series")

# ---- F2 ladder -----------------------------------------------------------
lat = ranks[(ranks.variable == "subjective_poverty") & (ranks.time == ranks.time.max())]
lat = lat.sort_values("gr_value", ascending=False)
f2 = ce.Series(["Reported hardship (%)"], dp=1)
rows2 = []
for r in lat.itertuples():
    pass
allc = panel[panel.time == panel.time.max()][["geo", "subjective_poverty"]]
allc = allc.dropna().sort_values("subjective_poverty", ascending=False)
for r in allc.itertuples():
    f2.add(NAMES.get(r.geo, r.geo), [float(r.subjective_poverty)])
    rows2.append({"label": NAMES.get(r.geo, r.geo), "name": NAMES.get(r.geo, r.geo),
                  "value": round(float(r.subjective_poverty), 1),
                  "highlight": r.geo == "EL"})
FIGS["F2"] = dict(
    caption="In 2024 Greece stands far above the rest of the EU on reported "
            "hardship",
    kind="ladder", series=f2,
    payload={"rows": rows2, "xLabel": "% of households reporting difficulty", "dp": 1, "unit": "%",
             "reference": round(float(allc.subjective_poverty.median()), 1),
             "referenceLabel": "EU median",
             "alt": "All 27 EU countries ranked on reported hardship"},
    first="Country")

# ---- F3 two views --------------------------------------------------------
# The first view showed the real threshold as an index, which is two
# abstractions deep: an index OF a threshold. It asked the reader to decode
# rather than see. Nominal against inflation-adjusted shows the mechanism
# directly -- the two lines separate, and the separation IS the erosion.
ads = pd.read_csv(PROC / "analysis_dataset.csv")
ycol = "year" if "year" in ads.columns else "time"
thr = ads[[ycol, "gr_arop_threshold_nominal_eur",
           "gr_arop_threshold_real_2008eur"]].dropna().sort_values(ycol)
ty = [int(v) for v in thr[ycol]]
f3 = ce.Series([str(y) for y in ty], dp=0)
f3.add("Threshold in cash terms",
       [float(v) for v in thr.gr_arop_threshold_nominal_eur],
       tone="gr", style="solid", weight="strong")
f3.add("Same threshold in 2008 purchasing power",
       [float(v) for v in thr.gr_arop_threshold_real_2008eur],
       tone="series-5", style="dashed", weight="strong")
v3a = {"years": ty, "dp": 0, "yLabel": "Euros per year, single adult",
       "alt": "The Greek poverty threshold in cash terms and in 2008 "
              "purchasing power. The cash line returns close to its peak while "
              "the purchasing-power line stays far below it",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v) for v in vs]}
                  for l, vs, m in f3.rows]}

anch = pd.read_csv(PROC / "anchored_poverty.csv")
anch = anch.dropna(subset=["anchored_poverty_rate", "actual_arop_rate"])
ay = [int(y) for y in anch.year]
f3b = ce.Series([str(y) for y in ay], dp=1)
# Both series are Greek, so neither may take EU-orange. Blue for the fixed
# yardstick, a neutral series colour for the current-year one.
f3b.add("Greece: fixed 2008 threshold", [float(v) for v in anch.anchored_poverty_rate],
        tone="gr", style="solid", weight="strong")
f3b.add("Greece: current-year threshold", [float(v) for v in anch.actual_arop_rate],
        tone="series-3", style="solid", weight="normal")
v3b = {"years": ay, "dp": 1, "yLabel": "% of people",
       "alt": "Greek anchored poverty against the floating income-poverty rate",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                  for l, vs, m in f3b.rows]}

FIGS["F3"] = dict(
    caption="Who counts as poor barely moved; what the poverty line buys fell "
            "by a fifth",
    kind="panel", series=f3b, payload=v3b,
    views=[("Who falls below a fixed line", v3b),
           ("What the line itself is worth", v3a)],
    view_series=[f3b, f3],
    extra_caveat=(
        "The first view counts PEOPLE, the second counts EUROS. In the second, "
        "both lines are the same official threshold: one as published in each "
        "year's own money, the other converted into what it could buy in 2008. "
        "The cash line recovers and the purchasing-power line does not, and "
        "that difference is why the first view's two counts diverge. Both "
        "views are Greece only and support no cross-country statement."),
    first="Series")

# ---- F4 the bridge -------------------------------------------------------
# The first view plots LEVELS, not gaps. Two gap lines asked the reader to hold
# a subtraction in their head, and a gap is a derived quantity: it cannot be
# checked against anything they already know. Three levels in % of households
# show AROPE sitting between reported hardship and income poverty, which is the
# fact the stage turns on. The size of the gap belongs in the sentence beside
# the chart, where it can be stated precisely.
contrib = [float(a) - float(b)
           for a, b in zip(desc.gap_vs_arop, desc.gap_vs_arope)]

f4 = ce.Series([str(int(y)) for y in desc.time], dp=1)
f4.add("Reported hardship", [float(v) for v in desc.gr_subjective_poverty],
       tone="gr", style="solid", weight="strong")
f4.add("AROPE", [float(v) for v in desc.gr_arope],
       tone="series-3", style="solid", weight="normal")
f4.add("Income poverty", [float(v) for v in desc.gr_arop],
       tone="series-5", style="dashed", weight="normal")

f4c = ce.Series([str(int(y)) for y in desc.time], dp=1)
f4c.add("Points closed by AROPE", contrib)
f4c.add("Gap still open after AROPE", [float(v) for v in desc.gap_vs_arope])

v4a = {"years": [int(y) for y in desc.time], "dp": 1,
       "yLabel": "% of households",
       "alt": "Greek reported hardship, AROPE and income poverty as shares of "
              "households; AROPE sits between the other two and closes only "
              "part of the distance",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                  for l, vs, m in f4.rows]}

v4b = {"years": [int(y) for y in desc.time], "dp": 1,
       "yLabel": "Percentage points",
       "alt": "The points AROPE closes, falling from 11.0 in 2015 to 7.3 in "
              "2024, against the gap that remains open",
       "series": [
           {"label": "Points closed by AROPE", "tone": "series-5",
            "style": "solid", "weight": "strong",
            "values": [round(v, 1) for v in contrib]},
           {"label": "Gap still open after AROPE", "tone": "gr",
            "style": "solid", "weight": "normal",
            "values": [round(float(v), 1) for v in desc.gap_vs_arope]}]}

FIGS["F4"] = dict(
    caption="AROPE sits between reported hardship and income poverty, and "
            "closes only about a fifth of the distance",
    kind="panel", series=f4, payload=v4a,
    views=[("The three measures", v4a), ("What AROPE actually closes", v4b)],
    view_series=[f4, f4c],
    extra_caveat=(
        "The first view shows the three measures as they are reported, in "
        "shares of households, so the distance between them can be read "
        "directly. The second plots that distance: the points AROPE closes, "
        "which fall from 11.0 in 2015 to 7.3 in 2024."),
    first="Series")

# ---- F5 four views -------------------------------------------------------
# Low work intensity has NO national row in this source -- only three age
# groups -- so the components view carries the two that do, and says so rather
# than silently dropping one. The empty first view that shipped in the previous
# build came from filtering it for a TOTAL that does not exist.
# One measure per view, each against the whole EU distribution. Two Greek
# component lines on one axis invited comparison between them, which is not the
# question; the question is where Greece sits on each.
def _component_view(col, label, ctx_label, shown=None):
    shown = shown or label.lower()
    sub = panel.dropna(subset=[col])
    cyy = sorted(sub.time.unique())
    gser = sub[sub.geo == "EL"].set_index("time")[col]
    mser = sub.groupby("time")[col].median()
    ser = ce.Series([str(int(y)) for y in cyy], dp=1)
    ser.add(f"Greece: {shown}",
            [float(gser.get(y)) if y in gser.index else None for y in cyy],
            tone="gr", style="solid", weight="strong")
    ser.add(f"EU median: {shown}",
            [float(mser.get(y)) if y in mser.index else None for y in cyy],
            tone="eu", style="dashed", weight="normal")
    others = []
    for g, s2 in sub.groupby("geo"):
        if g == "EL":
            continue
        ss = s2.set_index("time")[col]
        vals = [float(ss.get(y)) if y in ss.index and pd.notna(ss.get(y)) else None
                for y in cyy]
        if sum(v is not None for v in vals) >= 2:
            others.append({"label": NAMES.get(g, g), "values": vals})
    view = {"years": [int(y) for y in cyy], "dp": 1, "yLabel": "% of people",
            "context": others, "contextLabel": ctx_label,
            "alt": f"{label} for Greece against the EU median, with every "
                   f"other country drawn faintly behind",
            "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                        "weight": m["weight"],
                        "values": [None if v is None else round(v, 1) for v in vs]}
                       for l, vs, m in ser.rows]}
    return ser, view


f5, v5a = _component_view("arop", "Income poverty",
                          "Each other EU country: income poverty")
f5m, v5m = _component_view("severe_mat_soc_deprivation", "Material deprivation",
                           "Each other EU country: material deprivation")
f5e, v5e = _component_view("arope", "AROPE",
                           "Each other EU country: AROPE", shown="AROPE")

age_all = pd.read_csv(PROC / "age_breakdown_arope.csv")
age = age_all[age_all.geo == "EL"]
age_eu = age_all[age_all.geo == "EU27_2020"]
# Reader-facing text, not HTML entities: "18&ndash;24" leaked into a chart
# label and a table cell in the previous build.
AGEL = {"Y_LT18": "Under 18", "Y18-24": "18-24", "Y25-49": "25-49",
        "Y25-54": "25-54", "Y50-64": "50-64", "Y_GE65": "65 and over",
        "TOTAL": "All ages"}
ay2 = sorted(age.time.unique())
f5b = ce.Series([str(int(y)) for y in ay2], dp=1)
# Age groups are not a Greece/EU comparison, so neither reserved colour is
# used. Neutral series colours throughout, with 65+ emphasised by weight.
# Each age band is a PAIR: Greece solid, the EU median for the same band
# dashed, in the SAME colour. Drawing every European line in the reserved EU
# orange said only "these are Europe" and left the reader to work out which
# Greek line each belonged to. Colour now encodes the age group and dash
# encodes the country, so a pair reads as one comparison.
AGE_TONE = [("TOTAL", "chart-neutral", "light"), ("Y_LT18", "series-4", "normal"),
            ("Y18-24", "series-5", "normal"), ("Y25-49", "series-3", "normal"),
            ("Y50-64", "eu", "normal"), ("Y_GE65", "gr", "strong")]
for g, tone, w in AGE_TONE:
    s = age[age.age == g].set_index("time").arope_rate
    if s.empty:
        continue
    f5b.add(AGEL[g], [float(s.get(y)) if y in s.index else None for y in ay2],
            tone=tone, style="solid", weight=w)
for g, tone, w in AGE_TONE:
    s = age_eu[age_eu.age == g].set_index("time").arope_rate
    if s.empty:
        continue
    f5b.add(f"EU: {AGEL[g].lower()}",
            [float(s.get(y)) if y in s.index else None for y in ay2],
            tone=tone, style="dashed", weight="light")
v5b = {"years": [int(y) for y in ay2], "dp": 1, "yLabel": "% of age group",
       "alt": "Greek AROPE by age group, each paired with the EU median for "
              "the same band in the same colour: Greece solid, Europe dashed",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"],
                   "values": [None if v is None else round(v, 1) for v in vs]}
                  for l, vs, m in f5b.rows]}
ss = pd.read_csv(PROC / "age_breakdown_shiftshare_decomposition.csv")
f5c = ce.Series(["Within-group (pp)", "Composition (pp)"], dp=3)
rows5c = []
for r in ss.itertuples():
    f5c.add(AGEL.get(r.age, r.age),
            [float(r.within_group_contribution_pp), float(r.composition_contribution_pp)])
    rows5c.append({"label": AGEL.get(r.age, r.age),
                   "a": round(float(r.composition_contribution_pp), 3),
                   "b": round(float(r.within_group_contribution_pp), 3),
                   "tone": "gr" if r.within_group_contribution_pp > 0.2 else "text-muted",
                   "strong": r.within_group_contribution_pp > 0.2,
                   "right": (f"{r.within_group_contribution_pp:+.3f} within, "
                             f"{r.composition_contribution_pp:+.3f} comp."),
                   "detail": (f"within-group <b>{r.within_group_contribution_pp:+.3f} pp</b>"
                              f"<br>composition {r.composition_contribution_pp:+.3f} pp"
                              f"<br>rate {r.arope_rate_2024:.1f} &rarr; {r.arope_rate_2025:.1f}")})
v5c = {"rows": rows5c, "dp": 3, "legendA": "composition",
       "legendB": "within-group", "zeroLabel": "no contribution",
       "xLabel": "Contribution to the 2024-2025 change (percentage points)",
       "alt": "Within-group against compositional contribution to the "
              "2024-2025 change, in percentage points. These are exact "
              "decomposition terms, not estimates: they carry no uncertainty "
              "interval"}
sx = pd.read_csv(PROC / "arope_by_sex.csv")
SEXL = {"T": "All", "F": "Women", "M": "Men"}
sy = sorted(sx.time.unique())
f5d = ce.Series([str(int(y)) for y in sy], dp=1)
# Paired like the age view: colour encodes the group, dash encodes the country.
SEX_TONE = [("T", "chart-neutral", "light"), ("F", "gr", "strong"),
            ("M", "series-5", "normal")]
for g, tone, w in SEX_TONE:
    s = sx[(sx.geo == "EL") & (sx.sex == g)].set_index("time").arope_rate
    if s.empty:
        continue
    f5d.add(SEXL[g], [float(s.get(y)) if y in s.index else None for y in sy],
            tone=tone, style="solid", weight=w)
for g, tone, w in SEX_TONE:
    s = sx[(sx.geo == "EU27_2020") & (sx.sex == g)].set_index("time").arope_rate
    if s.empty:
        continue
    f5d.add(f"EU: {SEXL[g].lower()}",
            [float(s.get(y)) if y in s.index else None for y in sy],
            tone=tone, style="dashed", weight="light")
v5d = {"years": [int(y) for y in sy], "dp": 1, "yLabel": "% of people",
       "alt": "Greek AROPE by sex, each paired with the EU median for the same "
              "sex in the same colour: Greece solid, Europe dashed. Greek women "
              "sit above Greek men throughout, and both far above Europe",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"],
                   "values": [None if v is None else round(v, 1) for v in vs]}
                  for l, vs, m in f5d.rows]}

FIGS["F18"] = dict(
    caption="The most recent rise came from rates within age groups, not from "
            "the changing size of those groups",
    kind="dumbbell", payload=v5c, series=f5c, first="Age group")

FIGS["F5"] = dict(
    caption="What sits behind AROPE, and which groups moved",
    kind="panel", series=f5,
    payload=v5a,
    # 3. Reader-facing tab labels. "Floating poverty" and "shift-share" are
    # methods vocabulary and do not belong in navigation.
    views=[("Income poverty", v5a), ("Material deprivation", v5m),
           ("AROPE", v5e), ("By age", v5b), ("By sex", v5d)],
    view_series=[f5, f5m, f5e, f5b, f5d],
    # Naming the first view "AROPE components" while showing two of three would
    # let a reader take it for a complete decomposition. The absence is stated
    # rather than implied.
    extra_caveat=(
        "Very low work intensity is part of AROPE, but the project does not "
        "hold a comparable national-total series for this view; its available "
        "age coverage uses a different population base, and aggregate "
        "component rates cannot reconstruct the AROPE union in any case. In "
        "the age and sex views, colour marks the group and dash marks the "
        "country: each Greek line is paired with the EU median for the same "
        "group in the same colour."),
    first="Series")


def build(fid, spec):
    """One figure. Every view gets its own payload AND its own table fallback,
    so switching view never leaves the reader without the numbers."""
    m = man.loc[fid]
    views = spec.get("views")
    if views:
        tags, tables = [], []
        for i, v in enumerate(views):
            label, pl = v[0], v[1]
            kind = v[2] if len(v) > 2 else spec["kind"]
            tags.append(payload_tag(pl, kind, label))
            s = spec["view_series"][i]
            s.title = label
            tables.append(s.fallback_table(spec.get("first", ""), view=i))
        payload_html, body = "".join(tags), "".join(tables)
        stamp = spec["view_series"][0].checksum()
    else:
        payload_html = payload_tag(spec["payload"])
        body = spec["series"].fallback_table(spec.get("first", ""))
        stamp = spec["series"].checksum()
    cav = m.caveat
    if spec.get("extra_caveat"):
        cav = ("" if cav != cav else str(cav) + " ") + spec["extra_caveat"]
    shell = ce.figure(fid, spec["caption"], m.question, m.status_label,
                      spec["kind"], {}, body, caveat=cav,
                      appendix_link="statistical_appendix.html", checksum=stamp)
    return shell.replace(payload_tag({}), payload_html)


print(f"batch 1: stages 1-2, {len(FIGS)} figures")
for k, v in FIGS.items():
    nv = len(v.get("views", [])) or 1
    print(f"  {k}  {v['kind']:12} {nv} view(s)  {len(v['series'].rows)} rows  "
          f"checksum {v['series'].checksum()}")

# --------------------------------------------------------------------- page
import re as _re
BASE = ce.base_style((OUT / "report.html").read_text())
built = {k: build(k, v) for k, v in FIGS.items()}

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Batch 1 &mdash; stages 1 and 2</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu);--ok:#2f855a;--warn:#b7791f}}
body{{max-width:52rem;margin:0 auto;padding:2rem 1.2rem 5rem}}
h2{{margin:2.8rem 0 .6rem}}
.signpost{{border-left:3px solid var(--series-3);padding:.7rem 1rem;
background:var(--surface-2);border-radius:0 5px 5px 0;margin:1.6rem 0}}
.proto-note{{border:1px dashed var(--border);border-radius:6px;padding:.9rem 1.1rem;
margin-bottom:2rem;font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;
color:var(--text-secondary)}}
</style></head><body>
<p class="proto-note"><strong>Batch 1.</strong> Stages 1 and 2 from the frozen
manifest &mdash; five figures, including the new <em>ladder</em> type and
multi-view switching. Stage 2 carries three figures because the moving
threshold, the AROPE bridge and what sits behind AROPE are three different
questions.</p>

<h2>Stage 1 &mdash; The paradox</h2>
<p>Greeks report difficulty making ends meet at a rate far above what the
official relative-poverty rate would suggest. Over 2015&ndash;2024 the gap
averages 52.6 points, and Greece ranks first of 27 on reported hardship while
ranking seventh on at-risk-of-poverty. The two measures are not describing the
same thing.</p>
{built['F1']}
<p>The obvious question is whether Greece is merely at one end of a continuum.
It is not: the distance between Greece and the next country is larger than the
distance spanning most of the rest of the distribution.</p>
{built['F2']}

<h2>Stage 2 &mdash; The AROPE bridge</h2>
<p>If reported hardship sits far above income poverty, the natural first move is
a broader official measure. AROPE adds material deprivation and low work
intensity to income poverty, and it does move Greece closer to what its
households report.</p>
{built['F4']}
<p>It closes about a fifth of the distance, and its contribution is shrinking
&mdash; from 11.0 points in 2015 to 7.3 in 2024. So the broader measure helps
and does not resolve the puzzle. The next question is what the aggregate
conceals.</p>
{built['F5']}
{built['F18']}
<p class="signpost"><strong>Two different checks, not one.</strong> AROPE
broadens the <em>concept</em> of poverty: it counts more kinds of disadvantage.
Anchored poverty changes the <em>yardstick</em>: it holds the income line fixed
in real terms instead of letting it move with the national median. The first
asks whether we are measuring enough things; the second asks whether the ruler
itself moved. They are separate problems, and Greece has both.</p>
<p>Relative income poverty counts people below 60% of the <em>current</em>
national median. When national income collapses the threshold falls with it, so
a household can stay above a shrinking line while becoming materially worse off.
That is not a defect of AROP &mdash; it measures relative position, and does so
correctly &mdash; but it cannot register a fall that affects everyone at once.</p>
{built['F3']}
<script>{ce.JS}</script>
</body></html>
"""
(OUT / "batch1.html").write_text(PAGE)
print(f"\nwrote output/batch1.html  {len(PAGE):,} chars")
