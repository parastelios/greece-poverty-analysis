"""Batch 2: stages 3 and 4, five figures.

The heatmap is deliberately small in its default view. A 31x31 matrix contains
everything and communicates almost nothing; the main path carries the outcomes
and the frozen construct representatives, and the full matrix sits behind a
second view and in the appendix.
"""
import json
import math
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

NAMES = {"EL": "Greece", "BG": "Bulgaria", "RO": "Romania", "HU": "Hungary",
         "LU": "Luxembourg", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
         "EE": "Estonia", "ES": "Spain", "PT": "Portugal", "IT": "Italy",
         "FR": "France", "DE": "Germany", "NL": "Netherlands", "BE": "Belgium",
         "AT": "Austria", "IE": "Ireland", "FI": "Finland", "SE": "Sweden",
         "DK": "Denmark", "PL": "Poland", "CZ": "Czechia", "SK": "Slovakia",
         "SI": "Slovenia", "HR": "Croatia", "MT": "Malta"}

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
man = pd.read_csv(PROC / "report_visual_manifest.csv").set_index("id")
panel = pd.read_csv(PROC / "e0_extended_panel.csv")
rec = pd.read_csv(PROC / "e_descriptive_recovery.csv")
e3 = pd.read_csv(PROC / "e3_results.csv")
e1 = pd.read_csv(PROC / "e1_results.csv")
cmap = json.loads((PROC / "construct_map_frozen.json").read_text())


def _assert_json_safe(d, where="payload"):
    """json.dumps happily emits bare NaN and Infinity. Neither is valid JSON,
    so a payload containing one does NOT fail the build -- it fails silently in
    the reader's browser, and the figure quietly shows some other view. An
    empty string read back from a CSV as NaN did exactly that."""
    bad = []

    def walk(v, path):
        if isinstance(v, float) and not math.isfinite(v):
            bad.append(f"{path}={v}")
        elif isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}")
        elif isinstance(v, (list, tuple)):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")

    walk(d, where)
    if bad:
        raise SystemExit(
            "payload contains values JSON cannot represent: " + "; ".join(bad[:5]))


def payload_tag(d, kind="", label=""):
    _assert_json_safe(d)
    body = json.dumps(d).replace("</", "<\\/")
    a = (f' data-kind="{kind}"' if kind else "") + \
        (f' data-label="{label}"' if label else "")
    return f'<script type="application/json"{a}>{body}</script>'


FIGS = {}

# ---- F6 heatmap, small by default ----------------------------------------
OUTCOMES = ["subjective_poverty", "arop", "arope"]
reps = []
for cid, c in cmap["constructs"].items():
    prim = c["primary"]
    for v in (prim if isinstance(prim, list) else [prim]):
        if v in panel.columns and v not in reps:
            reps.append(v)
core = [v for v in OUTCOMES + reps if v in panel.columns]

views6, series6 = [], []
for label, fname in [("Between countries", "e0_corr_between.csv"),
                     ("Within countries", "e0_corr_within.csv"),
                     ("All country-years", "e0_corr_pooled.csv")]:
    m = pd.read_csv(PROC / fname, index_col=0)
    keep = [v for v in core if v in m.index and v in m.columns]
    sub = m.loc[keep, keep]
    s = ce.Series([ce.name(c) for c in keep], dp=3, title=label)
    for r in keep:
        s.add(ce.name(r), [float(sub.loc[r, c]) for c in keep])
    series6.append(s)
    MECH = {("arope", "arop"), ("arop", "arope"),
            ("arope", "severe_mat_soc_deprivation"),
            ("severe_mat_soc_deprivation", "arope")}
    flags = [[1 if (a, b) in MECH else 0 for b in keep] for a in keep]
    views6.append((label, {
        "flags": flags,

        "flagLabel": "partly mechanical",
        "flagExplain": "AROPE CONTAINS this measure, so the correlation is "
                       "partly mechanical and is not an independent relationship.",
        "cols": [ce.name(c) for c in keep],
        # The full matrix, with the diagonal blanked: a variable's correlation
        # with itself is always 1 and is the only genuinely uninformative cell.
        # Showing both halves keeps the conventional shape, so a reader can
        # scan a row or a column without discovering that half is missing.
        "rows": [{"label": ce.name(r),
                  "values": [round(float(sub.loc[r, c]), 3) if i != j else None
                             for j, c in enumerate(keep)]}
                 for i, r in enumerate(keep)],
        "alt": f"Correlations {label.lower()}, outcomes and construct "
               "representatives only; the diagonal is blank because a variable "
               "always correlates perfectly with itself",
    }, "heatmap"))
# The matrices show every pair; the result that MATTERS is what happens to the
# hardship row when the scope changes from between countries to within them.
# That comparison is buried in three separate grids, so it also gets its own
# view, where a sign reversal is a pair of points on opposite sides of zero.
mb = pd.read_csv(PROC / "e0_corr_between.csv", index_col=0)
mw = pd.read_csv(PROC / "e0_corr_within.csv", index_col=0)
# NOT `OUT`: that name is the output directory in this module.
OUTCOME = "subjective_poverty"
hk = [v for v in core if v != OUTCOME and v in mb.index and v in mw.index]
hk.sort(key=lambda v: abs(float(mb.loc[OUTCOME, v]) - float(mw.loc[OUTCOME, v])),
        reverse=True)
f6h = ce.Series(["Between countries", "Within countries", "Change"], dp=3,
                title="Hardship correlations")
rows6h = []
for v in hk:
    b, w = float(mb.loc[OUTCOME, v]), float(mw.loc[OUTCOME, v])
    f6h.add(ce.name(v), [b, w, w - b])
    flip = (b > 0) != (w > 0) and min(abs(b), abs(w)) > 0.05
    rows6h.append({
        "label": ce.name(v), "a": round(w, 3), "b": round(b, 3),
        "tone": "warn" if flip else "text-muted", "strong": flip,
        "right": "sign reverses" if flip else "",
        "detail": (f"between <b>{b:+.3f}</b><br>within <b>{w:+.3f}</b>"
                   f"<br>change {w - b:+.3f}"
                   + ("<br><b>the sign reverses between the two scopes</b>"
                      if flip else ""))})
v6h = {"rows": rows6h, "dp": 3, "legendA": "within countries",
       "legendB": "between countries", "zeroLabel": "no correlation",
       "xLabel": "Correlation with reported hardship",
       "alt": "Each measure's correlation with reported hardship, between "
              "countries against within countries, ordered by how much the "
              "two differ; reversals are marked"}
FIGS["F19"] = dict(
    caption="The real poverty threshold shows the only material sign reversal "
            "when the comparison moves within countries; the rest either hold "
            "their sign or start from a between-country correlation too close "
            "to zero for a reversal to be meaningful",
    kind="dumbbell", payload=v6h, series=f6h, first="Measure")

FIGS["F6"] = dict(
    caption="The same pair can point one way across countries and the other "
            "way within them",
    kind="heatmap", views=views6, view_series=series6, first="Measure",
    extra_caveat=(
        "AROPE contains AROP and material deprivation, so those correlations "
        "are partly mechanical and must not be interpreted as independent "
        "relationships; the affected cells are outlined. This view carries the "
        f"outcomes and the {len(reps)} construct representatives only, "
        "because at full size a matrix contains everything and shows almost "
        "nothing. The complete 35-variable matrix IS available: the "
        "statistical appendix carries it three times, within countries, "
        "between countries and pooled."))

# ---- F7 diverging: share of the 2015 gap closed --------------------------
#
# NOT a dumbbell on a shared axis. The 2015 gaps run from -2,819 PPS for
# material resources to +48.8 percentage points for hardship: percentage
# points, index points and PPS currency cannot share one axis, and the
# smaller-unit series become visually meaningless next to the larger. The
# plotted quantity is therefore DIMENSIONLESS -- the share of each 2015 gap
# closed by 2024 -- with the original values and their units kept in the
# tooltip and the fallback table.
UNIT = {"aic_pps_pc": "PPS per head", "ltu_rate": "percentage points",
        "real_wages_idx": "index points, 2008 = 100",
        "real_income_idx": "index points, 2008 = 100",
        "arop_threshold_real": "index points, 2008 = 100",
        "pct_below_peak": "percentage points", "wadj_a01": "index points, EU = 100",
        "housing_cost_overburden": "percentage points",
        "severe_mat_soc_deprivation": "percentage points",
        "subjective_poverty": "percentage points", "arop": "percentage points",
        "arope": "percentage points", "gap_subj_arop": "percentage points",
        "gap_subj_arope": "percentage points"}
d7 = rec[~rec.trend.str.startswith("not applicable")].copy()
d7 = d7.sort_values("gap_shift_rel", ascending=False)
TONE7 = {"converging": "div-pos", "flat": "div-zero", "diverging": "div-neg"}
# Endpoints for BOTH sides. A gap can narrow because Greece improved or
# because everyone else got worse, and the reader cannot tell which without
# seeing the EU median move too. eu = gr - gap, by construction of the gap.
f7 = ce.Series(["Share of 2015 gap closed", "Greece 2015", "Greece 2024",
                "EU median 2015", "EU median 2024", "Gap 2015", "Gap 2024"],
               dp=2)
rows7 = []
for r in d7.itertuples():
    share = float(r.gap_shift_rel)
    unit = UNIT.get(r.variable, "")
    eu_first = float(r.gr_first) - float(r.gap_first)
    eu_last = float(r.gr_last) - float(r.gap_last)
    f7.add(ce.name(r.variable),
           [share, float(r.gr_first), float(r.gr_last), eu_first, eu_last,
            float(r.gap_first), float(r.gap_last)])
    closed = (f"{share:.0%} of the initial gap closed" if share > 0
              else f"gap widened by {abs(share):.0%} of its 2015 size")
    rows7.append({
        "label": ce.name(r.variable), "value": round(share, 3),
        "tone": TONE7[r.trend], "highlight": False,
        "name": ce.name(r.variable),
        "detail": (f"<b>{closed}</b>"
                   f"<br>Greece {r.gr_first:,.1f} &rarr; {r.gr_last:,.1f}"
                   f"<br>EU median {eu_first:,.1f} &rarr; {eu_last:,.1f}"
                   f"<br>gap {r.gap_first:+,.1f} &rarr; {r.gap_last:+,.1f}"
                   f"<br><span style='opacity:.6'>{unit}</span>")})
FIGS["F7"] = dict(
    caption="Some gaps narrowed, especially long-term unemployment; wage, "
            "resource and affordability gaps widened",
    kind="ladder",
    payload={"rows": rows7, "xLabel": "Share of the 2015 Greece-EU gap closed by 2024 (1.0 = fully closed; above 1.0 = overshot and reversed)", "dp": 2, "unit": "of the 2015 gap",
             "labelAll": True, "reference": 0.0, "referenceLabel": "no change",
             "alt": "Share of each 2015 Greece-EU gap closed by 2024; positive "
                    "means convergence, negative means divergence"},
    series=f7, first="Measure",
    extra_caveat=(
        "A NARROWING GAP DOES NOT MEAN GREECE IMPROVED. A gap can close because "
        "Greece caught up, because the rest of the EU deteriorated, or because "
        "everyone moved in the same direction at different speeds. This chart "
        "measures RELATIVE CONVERGENCE, not national recovery, which is why "
        "both endpoints for Greece and for the EU median are in the tooltip and "
        "the table. \"71% of the gap closed\" and \"conditions improved by 71%\" "
        "are entirely different claims. The plotted quantity is dimensionless "
        "because the underlying gaps are measured in percentage points, index "
        "points and PPS per head and cannot share an axis."))

# ---- F8: the movement itself --------------------------------------------
# One tab per measure. Four panels carrying three lines each would be twelve
# lines on one figure, which is where the earlier versions became unreadable.
# Each tab asks one question: did this concrete difficulty rise and fall with
# what Greek households reported, and was it moving the same way elsewhere?
ITEMS = [("unexpected_expenses", "Unexpected expenses"),
         ("severe_mat_soc_deprivation", "Material deprivation"),
         ("arrears", "Falling behind on bills"),
         ("warm", "Keeping the home warm")]

el = panel[panel.geo == "EL"].dropna(subset=["subjective_poverty"]).sort_values("time")
views8, series8, summary = [], [], []
for col, label in ITEMS:
    sub = el.dropna(subset=[col])
    if len(sub) < 6:
        continue
    r = float(sub.subjective_poverty.corr(sub[col]))
    yy = [int(y) for y in sub.time]
    eu = panel.dropna(subset=[col]).groupby("time")[col].median()
    eu_v = [float(eu.get(y)) if y in eu.index else None for y in yy]
    eu_m = pd.Series([v for v in eu_v if v is not None]).mean()

    # Everything is a distance from its OWN 2015-2024 average, including the
    # European median, or the three lines could not share one axis.
    hz = [round(float(v - sub.subjective_poverty.mean()), 1)
          for v in sub.subjective_poverty]
    iz = [round(float(v - sub[col].mean()), 1) for v in sub[col]]
    ez = [None if v is None else round(float(v - eu_m), 1) for v in eu_v]

    s = ce.Series([str(y) for y in yy], dp=1, title=label)
    s.add("Greece: reported hardship", hz)
    s.add(f"Greece: {label.lower()}", iz)
    s.add(f"EU median: {label.lower()}", ez)
    series8.append(s)
    summary.append(f"{label.lower()} {r:.2f}")
    views8.append((label, {
        "years": yy, "dp": 1, "aspect": 0.44,
        "yMin": -9, "yMax": 9,
        "corner": f"r = {r:.2f}",
        "yLabel": "Percentage-point deviation from each series' "
                  "2015-2024 average",
        "alt": f"Greek reported hardship, Greek {label.lower()} and the EU "
               f"median for {label.lower()}, each as distances from its own "
               f"average. Greek correlation {r:.2f}",
        "series": [
            {"label": "Greece: reported hardship", "tone": "chart-gr",
             "style": "solid", "weight": "strong", "values": hz},
            {"label": f"Greece: {label.lower()}", "tone": "chart-s3",
             "style": "solid", "weight": "strong", "values": iz},
            {"label": f"EU median: {label.lower()}", "tone": "chart-s3",
             "style": "dashed", "weight": "normal", "values": ez}]},
        "panel"))

FIGS["F8"] = dict(
    caption="Three affordability measures closely track hardship in Greece; "
            "falling behind on bills tracks it much less closely",
    kind="panel", views=views8, view_series=series8, first="Year",
    extra_caveat=(
        "Greek correlations with reported hardship: " + " \u00b7 ".join(summary)
        + ". Every line is a distance from its own 2015-2024 average, "
        "including the European median, so three series on different scales "
        "can share one axis: the shapes may be compared, the levels may not. "
        "The scale is the same in all four tabs. European median hardship is "
        "deliberately absent, since the question here is whether the concrete "
        "difficulty moved with Greek reports, not how Greece compares. "
        "Same-survey corroboration: not independent validation, and not "
        "causal evidence."))

# ---- F20: what the model predicts against what Greece reports --------------
# A one-row dumbbell was too little for a figure, and its grammar implied a
# before-and-after process. What changed is the SPECIFICATION. Three points on
# one axis -- two predictions and the observed value -- let a reader see what
# "absorbed" means without translating residuals in their head.
_res = pd.read_csv(PROC / "e3_restatement.csv").iloc[0]
_base_r, _with_r = float(_res.greece_resid_baseline), float(_res.greece_resid_with_p1)
_items = ["arrears", "unexpected_expenses", "warm", "severe_mat_soc_deprivation"]
_obs = float(panel.dropna(subset=["subjective_poverty", "arop"] + _items)
             .query("geo == 'EL'").subjective_poverty.mean())

f20 = ce.Series(["Percent of households"], dp=2)
# "After adding" sounds temporal, and nothing happened in time: the
# specification changed. Both rows are predictions, named as such.
_rows20 = [
    ("Prediction from income poverty and year alone", _obs - _base_r, False),
    ("Prediction including four related survey items", _obs - _with_r, False),
    ("What Greek households actually report", _obs, True),
]
for lbl, val, _ in _rows20:
    f20.add(lbl, [val])

# The report carries these three numbers as a TABLE rather than a chart: three
# points on one axis is a table wearing a chart's clothes. The figure stays in
# the appendix; this artifact is what the report's table is generated from and
# checked against, cell by cell, so the two cannot drift.
pd.DataFrame([{"row": lbl, "percent_of_households": round(val, 1)}
              for lbl, val, _ in _rows20]).to_csv(
    PROC / "e_f20_absorption.csv", index=False)

FIGS["F20"] = dict(
    caption=f"The baseline model expects Greece to report "
            f"{_obs - _base_r:.0f}% hardship; Greek households report "
            f"{_obs:.0f}%",
    kind="ladder",
    payload={"rows": [
        {"label": lbl, "name": lbl, "value": round(v, 1), "highlight": hl,
         # The distance to what Greece reports IS the unaccounted-for part.
         # Drawing it makes the 71% visible instead of a subtraction.
         **({"gapTo": round(_obs, 1),
             "gapLabel": f"{_base_r if i == 0 else _with_r:.2f} points "
                         f"unaccounted for"} if not hl else {})}
        for i, (lbl, v, hl) in enumerate(_rows20)],
             "dp": 1, "unit": "%", "labelAll": True,
             "xLabel": "percent of households reporting difficulty",
             "alt": f"Three values on one scale: the baseline model predicts "
                    f"{_obs - _base_r:.1f}%, adding four related survey items "
                    f"raises the prediction to {_obs - _with_r:.1f}%, and "
                    f"Greek households report {_obs:.1f}%"},
    series=f20, first="Model",
    extra_caveat=(
        f"The distance from a prediction to what Greece reports is the part the "
        f"model does not account for: {_base_r:.2f} points on income poverty and "
        f"year alone, {_with_r:.2f} after the four items enter, so "
        f"{_base_r - _with_r:.2f} points, or {(1 - _with_r / _base_r) * 100:.0f}%, "
        f"is absorbed. These four items are answered by the same "
        f"households in the same interview as the outcome, "
        f"so part of what they take with them is the interview rather than the "
        f"world."))

# ---- F9 coefficient (as prototyped) --------------------------------------
TONE9 = {"supported": "series-3", "inconclusive_under_available_power": "text-muted",
         "unsupported_with_adequate_power": "warn",
         "blocked_by_proximity": "gr", "contradicts_direction": "gr"}
SHORT9 = {"supported": "supported",
          "inconclusive_under_available_power": "inconclusive",
          "unsupported_with_adequate_power": "unsupported",
          "blocked_by_proximity": "blocked"}
d9 = e1.sort_values("std_effect", ascending=False)
f9 = ce.Series(["Effect (SD)", "CI low", "CI high", "p", "p FDR", "Bootstrap p"], dp=3)
rows9 = []
for r in d9.itertuples():
    scale = float(r.std_effect) / abs(float(r.coef)) if r.coef else 0.0
    flip = -1.0 if r.adverse == "lower_is_worse" else 1.0
    est = float(r.coef) * scale * flip
    a, b = float(r.ci_lo) * scale * flip, float(r.ci_hi) * scale * flip
    boot = "not run" if r.boot_p != r.boot_p else f"{r.boot_p:.4f}"
    gate = f"; failed on <b>{r.failed_gate}</b>" if isinstance(r.failed_gate, str) and r.failed_gate else ""
    f9.add(ce.name(r.var), [est, min(a, b), max(a, b), float(r.p_raw),
                            None if r.p_fdr != r.p_fdr else float(r.p_fdr),
                            None if r.boot_p != r.boot_p else float(r.boot_p)])
    rows9.append({"label": ce.name(r.var), "est": round(est, 3),
                  "lo": round(min(a, b), 3), "hi": round(max(a, b), 3),
                  "tone": TONE9.get(r.outcome, "text-muted"),
                  "strong": r.outcome == "supported",
                  "right": SHORT9.get(r.outcome, ""),
                  "detail": (f"<span style='opacity:.6'>{r.var}</span><br>"
                             f"{est:+.2f} SD in the adverse direction<br>"
                             f"cluster-robust 95% CI [{min(a, b):+.2f}, {max(a, b):+.2f}]<br>"
                             f"cluster-robust p {r.p_raw:.4f} &rarr; FDR "
                             f"{'&mdash;' if r.p_fdr != r.p_fdr else f'{r.p_fdr:.4f}'}<br>"
                             f"bootstrap p <b>{boot}</b>{gate}")})
FIGS["F9"] = dict(
    caption="Three current-condition constructs survive the full testing "
            "sequence",
    kind="coefficient",
    payload={"rows": rows9, "xLabel": "Standardised effect (SD of hardship)", "alt": "Standardised effect per construct with its "
             "cluster-robust confidence interval"},
    series=f9, first="Construct",
    extra_caveat=("Bars are CLUSTER-ROBUST 95% confidence intervals, not "
                  "bootstrap intervals: the wild cluster bootstrap determines "
                  "the final support status, and two constructs whose intervals "
                  "exclude zero here still fail it."))

# ---- F10 panel: the three supported, Greece against the EU ----------------
yrs = sorted(panel.time.unique())
gr = panel[panel.geo == "EL"].set_index("time")
med = panel.groupby("time")[["ltu_rate", "aic_pps_pc", "wadj_a01"]].median()
views10, series10 = [], []
# Each tab shows a different quantity in a different unit, so the unit belongs
# on the axis itself rather than in the caption the reader has already scrolled
# past.
UNIT10 = {"ltu_rate": "% of labour force",
          "aic_pps_pc": "PPS per head",
          "wadj_a01": "Index, EU27 = 100"}
for v, dp in [("ltu_rate", 1), ("aic_pps_pc", 0), ("wadj_a01", 1)]:
    s = ce.Series([str(int(y)) for y in yrs], dp=dp, title=ce.name(v))
    s.add("Greece", [float(gr[v].get(y)) for y in yrs])
    s.add("EU median", [float(med[v].get(y)) for y in yrs])
    series10.append(s)
    others10 = []
    for g, s2 in panel.dropna(subset=[v]).groupby("geo"):
        if g == "EL":
            continue
        ss = s2.set_index("time")[v]
        vals = [float(ss.get(y)) if y in ss.index and pd.notna(ss.get(y)) else None
                for y in yrs]
        if sum(x is not None for x in vals) >= 2:
            others10.append({"label": NAMES.get(g, g),
                             "values": [None if x is None else round(x, dp)
                                        for x in vals]})
    views10.append((ce.name(v), {
        "years": [int(y) for y in yrs], "dp": dp, "yLabel": UNIT10[v],
        "context": others10,
        "contextLabel": f"Each other EU country: {ce.name(v).lower()}",
        "alt": f"{ce.name(v)} for Greece against the EU median and every "
               f"other country, in {UNIT10[v]}",
        "series": [{"label": "Greece", "tone": "gr", "style": "solid",
                    "weight": "strong",
                    "values": [round(float(gr[v].get(y)), dp) for y in yrs]},
                   {"label": "EU median", "tone": "eu", "style": "dashed",
                    "weight": "normal",
                    "values": [round(float(med[v].get(y)), dp) for y in yrs]}],
    }, "panel"))
FIGS["F10"] = dict(
    caption="What the three supported constructs look like",
    kind="panel", views=views10, view_series=series10, first="Series")

print(f"batch 2: stages 3-4, {len(FIGS)} figures")
for k, v in FIGS.items():
    nv = len(v.get("views", [])) or 1
    rows = len((v.get("view_series") or [v["series"]])[0].rows)
    print(f"  {k}  {v['kind']:12} {nv} view(s)  {rows} rows")


def build(fid, spec):
    m = man.loc[fid]
    views = spec.get("views")
    if views:
        tags, tables = [], []
        for i, v in enumerate(views):
            tags.append(payload_tag(v[1], v[2] if len(v) > 2 else spec["kind"], v[0]))
            s = spec["view_series"][i]
            s.title = v[0]
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


BASE = ce.base_style((OUT / "build" / "report.html").read_text())
b = {k: build(k, v) for k, v in FIGS.items()}
PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Batch 2 &mdash; stages 3 and 4</title>{BASE}
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
<p class="proto-note"><strong>Batch 2.</strong> Stages 3 and 4, adding the last
two new chart types &mdash; dumbbell and heatmap &mdash; plus the scatter, which
was in the appendix engine but had not been carried across.</p>

<h2>Stage 3 &mdash; Is the reported hardship real?</h2>
<p>Before asking what explains the gap, it is worth asking whether the thing
being explained is real. If Greeks simply describe their circumstances more
darkly, there is no economic puzzle to solve.</p>
{b['F8']}
{b['F20']}
<p>Once each country's own average is removed, reported difficulty co-moves with
unpaid bills, an inability to meet an unexpected expense, inadequate heating and
material deprivation. A reporting style unmoored from circumstance would not
need to track them.</p>
<p class="signpost"><strong>Corroboration, not proof.</strong> All four items and
the outcome come from the same survey, asked of the same households in the same
interview. That makes them evidence of material grounding and disqualifies them
as independent explanations &mdash; which is why they appear nowhere in the
models that follow.</p>
<p>So the hardship is materially grounded. The next question is which
conditions differ between countries, and the descriptive picture already
constrains the answer.</p>
{b['F7']}
<p>Two recoveries ran in opposite directions. The labour market genuinely closed
its distance from Europe; wages and material resources moved further away. The
hardship gap itself did neither &mdash; it is flat.</p>
{b['F6']}
{b['F19']}

<h2>Stage 4 &mdash; Current conditions</h2>
<p>Each construct is tested one at a time against relative income poverty and
year effects, so it has to explain hardship beyond what official poverty and
common shocks already account for.</p>
{b['F9']}
<p>Nothing is called supported on a cluster-robust p-value alone. With 27
clusters and predictors that vary mostly between countries, those standard
errors are too confident: two constructs clear multiple-testing correction and
then collapse under the bootstrap, to 0.40 and 0.55.</p>
{b['F10']}
<script>{ce.JS}</script>
</body></html>
"""
# Build intermediates live in output/build/, not output/ itself:
# output/ holds the canonical publications and nothing else.
_BUILD = OUT / "build"
_BUILD.mkdir(exist_ok=True)
(_BUILD / "batch2.html").write_text(PAGE)
print(f"\nwrote output/build/batch2.html  {len(PAGE):,} chars")
