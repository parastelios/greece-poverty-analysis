"""Prototype: the shared chart engine, two representative figures, and the
report shell around them.

Two figures deliberately: F1 exercises the REUSED panel type and sets the
standard report chart style; F9 exercises the NEW coefficient type, which has
to carry intervals, status colours, hover detail and the bootstrap information.
If the interaction or the presentation is wrong, it is cheaper to find out here
than after fifteen charts.
"""
import json
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
man = pd.read_csv(PROC / "report_visual_manifest.csv").set_index("id")

panel = pd.read_csv(PROC / "e0_extended_panel.csv")
e1 = pd.read_csv(PROC / "e1_results.csv")

# --------------------------------------------------------------- F1 (panel)
m1 = man.loc["F1"]
yrs = sorted(panel.time.unique())
gr = panel[panel.geo == "EL"].set_index("time")
med = panel.groupby("time")[["subjective_poverty", "arop"]].median()
f1_payload = {
    "years": [int(y) for y in yrs], "dp": 1,
    "alt": "Greek subjective hardship against relative income poverty, "
           "2015 to 2024, with EU medians",
    "series": [
        {"label": "Greece: " + ce.name("subjective_poverty").lower(), "tone": "gr", "cls": "line-gr",
         "values": [round(float(gr.subjective_poverty.get(y)), 1) for y in yrs]},
        {"label": "Greece: income poverty", "tone": "gr", "cls": "line-faint",
         "values": [round(float(gr.arop.get(y)), 1) for y in yrs]},
        {"label": "EU: reported hardship", "tone": "eu", "cls": "line-eu",
         "values": [round(float(med.subjective_poverty.get(y)), 1) for y in yrs]},
        {"label": "EU: income poverty", "tone": "eu", "cls": "line-faint",
         "values": [round(float(med.arop.get(y)), 1) for y in yrs]},
    ],
}
rows = "".join(
    f"<tr><td>{int(y)}</td><td class=num>{gr.subjective_poverty.get(y):.1f}</td>"
    f"<td class=num>{gr.arop.get(y):.1f}</td>"
    f"<td class=num>{gr.subjective_poverty.get(y) - gr.arop.get(y):.1f}</td>"
    f"<td class=num>{med.subjective_poverty.get(y):.1f}</td>"
    f"<td class=num>{med.arop.get(y):.1f}</td></tr>" for y in yrs)
f1_fb = ("<table><caption class='sr'>Greek hardship and AROP by year</caption>"
         "<thead><tr><th>Year</th><th class=num>GR hardship</th>"
         "<th class=num>GR AROP</th><th class=num>Gap</th>"
         "<th class=num>EU hardship</th><th class=num>EU AROP</th></tr></thead>"
         f"<tbody>{rows}</tbody></table>")

F1 = ce.figure("F1", "Reported hardship and income poverty remain far apart, "
               "despite some narrowing",
               m1.question, m1.status_label, "panel", f1_payload, f1_fb,
               caveat=m1.caveat, appendix_link="statistical_appendix.html")

# --------------------------------------------------- F9 (coefficient, NEW)
m9 = man.loc["F9"]
TONE = {"supported": "ok", "inconclusive_under_available_power": "text-muted",
        "unsupported_with_adequate_power": "warn",
        "blocked_by_proximity": "gr", "contradicts_direction": "gr"}
SHORT = {"supported": "supported",
         "inconclusive_under_available_power": "inconclusive",
         "unsupported_with_adequate_power": "unsupported",
         "blocked_by_proximity": "blocked"}
d9 = e1.sort_values("std_effect", ascending=False)
f9_rows = []
for r in d9.itertuples():
    boot = "not run" if r.boot_p != r.boot_p else f"{r.boot_p:.4f}"
    gate = f"; failed on <b>{r.failed_gate}</b>" if isinstance(r.failed_gate, str) and r.failed_gate else ""
    # A REAL interval, not a bar from zero. The first prototype drew
    # [0, largest admitted effect], which looks like a confidence interval and
    # is not one -- and it put a negative tick on an axis where nothing was
    # negative. The standardising scale is recoverable as std_effect/|coef|,
    # and the sign is flipped for lower_is_worse variables so that POSITIVE
    # always means more hardship in the adverse direction.
    scale = float(r.std_effect) / abs(float(r.coef)) if r.coef else 0.0
    flip = -1.0 if r.adverse == "lower_is_worse" else 1.0
    est = float(r.coef) * scale * flip
    a, b = float(r.ci_lo) * scale * flip, float(r.ci_hi) * scale * flip
    f9_rows.append({
        "label": ce.name(r.var), "est": round(est, 3),
        "lo": round(min(a, b), 3), "hi": round(max(a, b), 3),
        "tone": TONE.get(r.outcome, "text-muted"),
        "strong": r.outcome == "supported",
        "right": SHORT.get(r.outcome, ""),
        "detail": (f"<span style='opacity:.6'>{r.var}</span><br>"
                   f"{est:+.2f} SD in the adverse direction<br>"
                   f"cluster-robust 95% CI [{min(a, b):+.2f}, {max(a, b):+.2f}]<br>"
                   f"cluster-robust p {r.p_raw:.4f} &rarr; FDR "
                   f"{'&mdash;' if r.p_fdr != r.p_fdr else f'{r.p_fdr:.4f}'}<br>"
                   f"bootstrap p <b>{boot}</b>{gate}"),
    })
f9_payload = {"rows": f9_rows,
              "alt": "Standardised effect per construct with the interval, "
                     "coloured by pre-registered outcome"}
rows9 = "".join(
    f"<tr><td>{ce.name(r.var)}</td><td class=num>{r.std_effect:.2f}</td>"
    f"<td class=num>{r.p_raw:.4f}</td>"
    f"<td class=num>{'—' if r.p_fdr != r.p_fdr else f'{r.p_fdr:.4f}'}</td>"
    f"<td class=num>{'—' if r.boot_p != r.boot_p else f'{r.boot_p:.4f}'}</td>"
    f"<td>{SHORT.get(r.outcome, r.outcome)}</td></tr>" for r in d9.itertuples())
f9_fb = ("<table><thead><tr><th>Construct</th><th class=num>Effect (SD)</th>"
         "<th class=num>p</th><th class=num>p FDR</th>"
         "<th class=num>Bootstrap p</th><th>Outcome</th></tr></thead>"
         f"<tbody>{rows9}</tbody></table>")

F9 = ce.figure("F9", "Three current-condition constructs survive the full "
               "testing sequence", m9.question, m9.status_label, "coefficient",
               f9_payload, f9_fb,
               caveat="Bars are CLUSTER-ROBUST 95% confidence intervals. They "
                      "are not bootstrap intervals: the wild cluster bootstrap "
                      "determines the final support status, and two constructs "
                      "whose intervals exclude zero here still fail it. "
                      + m9.caveat,
               appendix_link="statistical_appendix.html")

# ------------------------------------------------------------------- shell
report_style = (OUT / "report.html").read_text()
import re
BASE = re.search(r"<style.*?</style>", report_style, re.S).group(0)

SHELL = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prototype &mdash; report chart engine</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr,#c0392b);--eu:var(--series-eu,#3d6fb4);
--ok:#2f855a;--warn:#b7791f}}
body{{max-width:52rem;margin:0 auto;padding:2rem 1.2rem 5rem}}
.proto-note{{border:1px dashed var(--border);border-radius:6px;padding:.9rem 1.1rem;
margin-bottom:2rem;font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;
color:var(--text-secondary)}}
h2{{margin:2.6rem 0 .6rem}}
</style></head><body>
<p class="proto-note"><strong>Prototype.</strong> Two figures from the frozen
manifest, built on the shared engine: one reused panel type and one new
coefficient type. Everything else on this page is the surrounding report shell
&mdash; heading, explanatory paragraph, caption, caveat and expandable evidence
table &mdash; so the visual character can be judged before the other thirteen
are built. Try hovering, tabbing to a chart and using the arrow keys, resizing
to phone width, and printing to PDF.</p>

<h2>Stage 1 &mdash; The paradox</h2>
<p>Greeks report difficulty making ends meet at a rate far above what the
official relative-poverty rate would suggest. Over 2015&ndash;2024 the gap
averages 52.6 points, and Greece ranks first of 27 on reported hardship while
ranking seventh on at-risk-of-poverty. The two measures are not describing the
same thing, and the divergence is not a rounding artefact.</p>
{F1}

<h2>Stage 4 &mdash; Current conditions</h2>
<p>Each construct was tested one at a time against relative income poverty and
year effects, so it has to explain hardship beyond what official poverty and
common shocks already account for. Nothing is called supported on a
cluster-robust p-value alone: with 27 clusters and predictors that vary mostly
between countries, those standard errors are too confident.</p>
{F9}
<p>Hovering a row shows where the two verdicts part company. Share below peak
and housing overburden both clear multiple-testing correction and then collapse
to 0.40 and 0.55 under the bootstrap, which is what decides.</p>

<script>{ce.JS}</script>
</body></html>
"""
(OUT / "prototype.html").write_text(SHELL)
print(f"wrote output/prototype.html  {len(SHELL):,} chars")
print(f"  F1 panel: {len(f1_payload['series'])} series, {len(yrs)} years")
print(f"  F9 coefficient: {len(f9_rows)} rows")
print("  both: badge, question, caveat, table fallback, keyboard, print CSS")
