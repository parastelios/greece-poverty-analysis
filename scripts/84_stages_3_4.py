"""Batch 2: stages 3 and 4, five figures.

The heatmap is deliberately small in its default view. A 31x31 matrix contains
everything and communicates almost nothing; the main path carries the outcomes
and the frozen construct representatives, and the full matrix sits behind a
second view and in the appendix.
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
rec = pd.read_csv(PROC / "e_descriptive_recovery.csv")
e3 = pd.read_csv(PROC / "e3_results.csv")
e1 = pd.read_csv(PROC / "e1_results.csv")
cmap = json.loads((PROC / "construct_map_frozen.json").read_text())


def payload_tag(d, kind="", label=""):
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
    views6.append((label, {
        "cols": [ce.name(c) for c in keep],
        "rows": [{"label": ce.name(r),
                  "values": [round(float(sub.loc[r, c]), 3) for c in keep]}
                 for r in keep],
        "alt": f"Correlations {label.lower()}, outcomes and construct "
               "representatives only",
    }, "heatmap"))
FIGS["F6"] = dict(
    caption="The same pair can point one way across countries and the other "
            "way within them",
    kind="heatmap", views=views6, view_series=series6, first="Measure",
    extra_caveat=(
        f"This view carries the outcomes and the {len(reps)} frozen construct "
        "representatives only. The full 31-variable matrix is in the "
        "statistical appendix: at that size it contains everything and shows "
        "almost nothing."))

# ---- F7 dumbbell: converged, flat, diverged -------------------------------
d7 = rec[~rec.trend.str.startswith("not applicable")].copy()
order = {"converging": 0, "flat": 1, "diverging": 2}
d7 = d7.assign(o=d7.trend.map(order)).sort_values(["o", "gap_shift_rel"],
                                                  ascending=[True, False])
TONE7 = {"converging": "series-3", "flat": "text-muted", "diverging": "gr"}
f7 = ce.Series(["Gap 2015", "Gap 2024", "Shift (share of 2015 gap)"], dp=2)
rows7 = []
for r in d7.itertuples():
    f7.add(ce.name(r.variable), [float(r.gap_first), float(r.gap_last),
                                 float(r.gap_shift_rel)])
    rows7.append({"label": ce.name(r.variable), "a": round(float(r.gap_first), 2),
                  "b": round(float(r.gap_last), 2), "tone": TONE7[r.trend],
                  "strong": r.trend != "flat", "right": r.trend,
                  "detail": f"shift {r.gap_shift_rel:+.0%} of the 2015 gap"})
FIGS["F7"] = dict(
    caption="The labour market converged toward Europe; wages and resources "
            "moved further away",
    kind="dumbbell",
    payload={"rows": rows7, "dp": 1, "legendA": "gap in 2015",
             "legendB": "gap in 2024", "zeroLabel": "EU median",
             "alt": "Greece's distance from the EU median in 2015 and 2024"},
    series=f7, first="Measure")

# ---- F8 scatter: same-instrument, country means removed -------------------
ITEMS = ["arrears", "unexpected_expenses", "warm", "severe_mat_soc_deprivation"]
views8, series8 = [], []
for it in ITEMS:
    d = panel.dropna(subset=[it, "subjective_poverty"]).copy()
    for c in [it, "subjective_poverty"]:
        d[c + "_w"] = d[c] - d.groupby("geo")[c].transform("mean")
    r = float(d["subjective_poverty_w"].corr(d[it + "_w"]))
    pts = [{"x": round(float(a), 2), "y": round(float(b), 2),
            "label": f"{g} {int(t)}", "highlight": g == "EL"}
           for g, t, a, b in zip(d.geo, d.time, d[it + "_w"], d["subjective_poverty_w"])]
    s = ce.Series(["Within-country r", "Country-years"], dp=3, title=ce.name(it))
    s.add(ce.name(it), [r, len(d)])
    series8.append(s)
    views8.append((ce.name(it), {
        "points": pts, "r": round(r, 3), "dp": 2,
        "xLabel": ce.name(it) + ", deviation from country mean",
        "yLabel": "Reported hardship, deviation from country mean",
        "alt": f"Reported hardship against {ce.name(it).lower()}, country means removed",
    }, "scatter"))
FIGS["F8"] = dict(
    caption="When a country's reported difficulty moves, its concrete "
            "affordability failures move with it",
    kind="scatter", views=views8, view_series=series8, first="Item")

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
    payload={"rows": rows9, "alt": "Standardised effect per construct with its "
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
for v, dp in [("ltu_rate", 1), ("aic_pps_pc", 0), ("wadj_a01", 1)]:
    s = ce.Series([str(int(y)) for y in yrs], dp=dp, title=ce.name(v))
    s.add("Greece", [float(gr[v].get(y)) for y in yrs])
    s.add("EU median", [float(med[v].get(y)) for y in yrs])
    series10.append(s)
    views10.append((ce.name(v), {
        "years": [int(y) for y in yrs], "dp": dp,
        "alt": f"{ce.name(v)} for Greece against the EU median",
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


BASE = re.search(r"<style.*?</style>", (OUT / "report.html").read_text(), re.S).group(0)
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
(OUT / "batch2.html").write_text(PAGE)
print(f"\nwrote output/batch2.html  {len(PAGE):,} chars")
