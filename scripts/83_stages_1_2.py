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
        ("Greece: reported hardship", gr.subjective_poverty, "gr", "solid", "strong"),
        ("Greece: income poverty", gr.arop, "eu", "solid", "strong"),
        ("EU median: reported hardship", med.subjective_poverty, "gr", "dashed", "light"),
        ("EU median: income poverty", med.arop, "eu", "dashed", "light")]:
    f1.add(lbl, [float(src.get(y)) for y in yrs], tone=tone, style=style, weight=weight)
FIGS["F1"] = dict(
    caption="Reported hardship and income poverty remain far apart, despite "
            "some narrowing",
    kind="panel", series=f1,
    payload={"years": [int(y) for y in yrs], "dp": 1,
             "alt": "Greek reported hardship against income poverty, 2015 to 2024",
             "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                         "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                        for l, vs, m in f1.rows]},
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
    caption="Greece is not at the end of a continuum &mdash; it is separated "
            "from it",
    kind="ladder", series=f2,
    payload={"rows": rows2, "dp": 1, "unit": "%",
             "reference": round(float(allc.subjective_poverty.median()), 1),
             "referenceLabel": "EU median",
             "alt": "All 27 EU countries ranked on reported hardship"},
    first="Country")

# ---- F3 two views --------------------------------------------------------
f3 = ce.Series([str(int(y)) for y in yrs], dp=1)
f3.add("Greece: real poverty threshold", [float(gr.arop_threshold_real.get(y)) for y in yrs],
       tone="gr", style="solid", weight="strong")
f3.add("EU median: real poverty threshold",
       [float(med.arop_threshold_real.get(y)) for y in yrs],
       tone="eu", style="dashed", weight="normal")
v3a = {"years": [int(y) for y in yrs], "dp": 1,
       "alt": "Real poverty threshold indexed to each country's own 2008 level",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                  for l, vs, m in f3.rows]}
anch = pd.read_csv(PROC / "anchored_poverty.csv")
anch = anch.dropna(subset=["anchored_poverty_rate", "actual_arop_rate"])
ay = [int(y) for y in anch.year]
f3b = ce.Series([str(y) for y in ay], dp=1)
f3b.add("Greece: anchored poverty", [float(v) for v in anch.anchored_poverty_rate],
        tone="gr", style="solid", weight="strong")
f3b.add("Greece: income poverty", [float(v) for v in anch.actual_arop_rate],
        tone="eu", style="solid", weight="normal")
v3b = {"years": ay, "dp": 1,
       "alt": "Greek anchored poverty against the floating income-poverty rate",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                  for l, vs, m in f3b.rows]}
FIGS["F3"] = dict(
    caption="The line moved: a falling threshold, and what a fixed one shows "
            "instead", kind="panel", series=f3, extra_series=[("Anchored", f3b)],
    payload=v3a, views=[("Real threshold, 2008 = 100", v3a),
                        ("Anchored vs floating poverty", v3b)],
    view_series=[f3, f3b],
    first="Series")

# ---- F4 the bridge -------------------------------------------------------
f4 = ce.Series([str(int(y)) for y in desc.time], dp=1)
f4.add("Gap against income poverty", [float(v) for v in desc.gap_vs_arop],
       tone="gr", style="solid", weight="strong")
f4.add("Gap against AROPE", [float(v) for v in desc.gap_vs_arope],
       tone="eu", style="solid", weight="strong")
FIGS["F4"] = dict(
    caption="AROPE narrows the puzzle by about a fifth, and its contribution "
            "is shrinking",
    kind="panel", series=f4,
    payload={"years": [int(y) for y in desc.time], "dp": 1,
             "alt": "Greek hardship gap against AROP and against AROPE",
             "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                         "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                        for l, vs, m in f4.rows]},
    first="Series")

# ---- F5 four views -------------------------------------------------------
comp = {}
for f, col, lbl in [("age_breakdown_arop.csv", "arop_rate", "Income poverty"),
                    ("age_breakdown_deprivation.csv", "deprivation_rate", "Material deprivation"),
                    ("age_breakdown_low_work_intensity.csv", "low_work_intensity_rate",
                     "Low work intensity")]:
    d = pd.read_csv(PROC / f)
    d = d[(d.geo == "EL") & (d.age == "TOTAL")] if "age" in d else d[d.geo == "EL"]
    comp[lbl] = d.set_index("time")[col]
cy = sorted(set.intersection(*[set(s.index) for s in comp.values()]))
f5 = ce.Series([str(int(y)) for y in cy], dp=1)
tones = ["gr", "eu", "series-3"]
for (lbl, s), tone in zip(comp.items(), tones):
    f5.add(lbl, [float(s.get(y)) for y in cy], tone=tone, style="solid", weight="normal")
v5a = {"years": [int(y) for y in cy], "dp": 1,
       "alt": "The three AROPE components for Greece",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"], "values": [round(v, 1) for v in vs]}
                  for l, vs, m in f5.rows]}
age = pd.read_csv(PROC / "age_breakdown_arope.csv")
age = age[age.geo == "EL"]
AGEL = {"Y_LT18": "Under 18", "Y18-24": "18&ndash;24", "Y25-49": "25&ndash;49",
        "Y50-64": "50&ndash;64", "Y_GE65": "65 and over", "TOTAL": "All ages"}
ay2 = sorted(age.time.unique())
f5b = ce.Series([str(int(y)) for y in ay2], dp=1)
for g, tone, w in [("TOTAL", "text-muted", "light"), ("Y_LT18", "series-4", "normal"),
                   ("Y18-24", "series-5", "normal"), ("Y25-49", "series-3", "normal"),
                   ("Y50-64", "eu", "normal"), ("Y_GE65", "gr", "strong")]:
    s = age[age.age == g].set_index("time").arope_rate
    if s.empty:
        continue
    f5b.add(AGEL[g], [float(s.get(y)) if y in s.index else None for y in ay2],
            tone=tone, style="solid", weight=w)
v5b = {"years": [int(y) for y in ay2], "dp": 1,
       "alt": "Greek AROPE by age group, with 65 and over emphasised",
       "series": [{"label": l, "tone": m["tone"], "style": m["style"],
                   "weight": m["weight"],
                   "values": [None if v is None else round(v, 1) for v in vs]}
                  for l, vs, m in f5b.rows]}
ss = pd.read_csv(PROC / "age_breakdown_shiftshare_decomposition.csv")
f5c = ce.Series(["Within-group (pp)", "Composition (pp)"], dp=3)
rows5c = []
for r in ss.itertuples():
    f5c.add(AGEL.get(r.age, r.age).replace("&ndash;", "-"),
            [float(r.within_group_contribution_pp), float(r.composition_contribution_pp)])
    rows5c.append({"label": AGEL.get(r.age, r.age).replace("&ndash;", "-"),
                   "est": round(float(r.within_group_contribution_pp), 3),
                   "lo": min(0.0, round(float(r.within_group_contribution_pp), 3)),
                   "hi": max(0.0, round(float(r.within_group_contribution_pp), 3)),
                   "tone": "gr" if r.within_group_contribution_pp > 0.2 else "text-muted",
                   "strong": r.within_group_contribution_pp > 0.2,
                   "right": f"{r.composition_contribution_pp:+.3f} comp.",
                   "detail": (f"within-group <b>{r.within_group_contribution_pp:+.3f} pp</b>"
                              f"<br>composition {r.composition_contribution_pp:+.3f} pp"
                              f"<br>rate {r.arope_rate_2024:.1f} &rarr; {r.arope_rate_2025:.1f}")})
v5c = {"rows": rows5c, "alt": "Shift-share: within-group against compositional "
       "contribution to the 2024-2025 change"}
FIGS["F5"] = dict(
    caption="What sits behind AROPE, and which groups moved",
    kind="panel", series=f5,
    payload=v5a,
    views=[("Components", v5a), ("By age", v5b), ("Shift-share", v5c, "coefficient")],
    view_series=[f5, f5b, f5c],
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
    shell = ce.figure(fid, spec["caption"], m.question, m.status_label,
                      spec["kind"], {}, body, caveat=m.caveat,
                      appendix_link="statistical_appendix.html", checksum=stamp)
    return shell.replace(payload_tag({}), payload_html)


print(f"batch 1: stages 1-2, {len(FIGS)} figures")
for k, v in FIGS.items():
    nv = len(v.get("views", [])) or 1
    print(f"  {k}  {v['kind']:12} {nv} view(s)  {len(v['series'].rows)} rows  "
          f"checksum {v['series'].checksum()}")

# --------------------------------------------------------------------- page
import re as _re
BASE = _re.search(r"<style.*?</style>", (OUT / "report.html").read_text(), _re.S).group(0)
built = {k: build(k, v) for k, v in FIGS.items()}

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Batch 1 &mdash; stages 1 and 2</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu);--ok:#2f855a;--warn:#b7791f}}
body{{max-width:52rem;margin:0 auto;padding:2rem 1.2rem 5rem}}
h2{{margin:2.8rem 0 .6rem}}
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
<p>Relative income poverty counts people below 60% of the <em>current</em>
national median. When national income collapses the threshold falls with it, so
a household can stay above a shrinking line while becoming materially worse off.
That is not a defect of AROP &mdash; it measures relative position, and does so
correctly &mdash; but it cannot register a fall that affects everyone at once.</p>
{built['F3']}
<p>So the EU's broader measure is the natural next step. AROPE adds material
deprivation and low work intensity to income poverty, and it does move Greece
closer to its reported hardship.</p>
{built['F4']}
<p>It closes about a fifth of the distance and its contribution is shrinking,
from 11.0 points in 2015 to 7.3 in 2024. Underneath, the three components and
the age groups did not move together.</p>
{built['F5']}
<script>{ce.JS}</script>
</body></html>
"""
(OUT / "batch1.html").write_text(PAGE)
print(f"\nwrote output/batch1.html  {len(PAGE):,} chars")
