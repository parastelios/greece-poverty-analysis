"""Batch 4: stages 7 and 8. The last.

Stage 7's context entries form a connected discussion, not six equal cards.
Stage 8 SYNTHESISES ONLY: no new estimate, no new interpretation, and the
evidence ladder is a table because it summarises status rather than showing a
distribution.
"""
import json
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
man = pd.read_csv(PROC / "report_visual_manifest.csv").set_index("id")
ctx = pd.read_csv(PROC / "context_register.csv").set_index("id")
claims = pd.read_csv(PROC / "e_final_claims.csv").set_index("id")
cross = pd.read_csv(PROC / "reporting_style_cross_indicator.csv")
NAMES = {"EL": "Greece", "BG": "Bulgaria", "RO": "Romania", "HU": "Hungary",
         "LU": "Luxembourg", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
         "EE": "Estonia", "ES": "Spain", "PT": "Portugal", "IT": "Italy",
         "FR": "France", "DE": "Germany", "NL": "Netherlands", "BE": "Belgium",
         "AT": "Austria", "IE": "Ireland", "FI": "Finland", "SE": "Sweden",
         "DK": "Denmark", "PL": "Poland", "CZ": "Czechia", "SK": "Slovakia",
         "SI": "Slovenia", "HR": "Croatia", "MT": "Malta"}



def payload_tag(d, kind="", label=""):
    body = json.dumps(d).replace("</", "<\\/")
    a = (f' data-kind="{kind}"' if kind else "") + \
        (f' data-label="{label}"' if label else "")
    return f'<script type="application/json"{a}>{body}</script>'


FIGS = {}

# ---- F15: where Greece sits on each indicator ----------------------------
# This was a rank trajectory, and ranks were the wrong instrument. A rank hides
# how large the differences are, needs its own axis inverted to stay readable,
# moves when OTHER countries move, and put two of the three series permanently
# on top of each other at rank 1. Showing the actual distribution answers the
# question the stage asks -- is Greece extreme on money and ordinary elsewhere?
# -- without any of that.
LATEST = 2024
_pan = pd.read_csv(PROC / "e0_extended_panel.csv")
_hard = _pan[(_pan.time == LATEST)].dropna(subset=["subjective_poverty"])
_sat = pd.read_csv(PROC / "reporting_style_life_satisfaction.csv")
_sat = _sat[_sat.time == LATEST].dropna(subset=["life_satisfaction"])
_exp = pd.read_csv(PROC / "near_zero_gap_comparison.csv")
_exp = _exp[_exp.time == LATEST].dropna(subset=["fin_expectations"])

CNAME = {"EL": "Greece", "BG": "Bulgaria", "RO": "Romania", "HU": "Hungary",
         "LU": "Luxembourg", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
         "EE": "Estonia", "ES": "Spain", "PT": "Portugal", "IT": "Italy",
         "FR": "France", "DE": "Germany", "NL": "Netherlands", "BE": "Belgium",
         "AT": "Austria", "IE": "Ireland", "FI": "Finland", "SE": "Sweden",
         "DK": "Denmark", "PL": "Poland", "CZ": "Czechia", "SK": "Slovakia",
         "SI": "Slovenia", "HR": "Croatia", "MT": "Malta"}


def _points(df, col):
    return [{"name": CNAME.get(r.geo, r.geo), "value": round(float(getattr(r, col)), 2),
             "highlight": r.geo == "EL"} for r in df.itertuples()]


strips15 = [
    {"label": "Reported hardship", "unit": "%", "dp": 1, "worseIs": "high",
     "points": _points(_hard, "subjective_poverty")},
    {"label": "Financial expectations", "unit": "", "dp": 1, "worseIs": "low",
     "points": _points(_exp, "fin_expectations")},
    {"label": "Life satisfaction", "unit": "", "dp": 1, "worseIs": "low",
     "points": _points(_sat, "life_satisfaction")},
]

f15 = ce.Series(["Greece", "EU median", "Countries", "Greece's position"], dp=2)
for s in strips15:
    vs = sorted(p["value"] for p in s["points"])
    g = next(p["value"] for p in s["points"] if p["highlight"])
    med = vs[len(vs) // 2] if len(vs) % 2 else (vs[len(vs)//2 - 1] + vs[len(vs)//2]) / 2
    pos = (sorted(vs).index(g) + 1) if s["worseIs"] == "low" else (
        len(vs) - sorted(vs).index(g))
    f15.add(s["label"], [g, round(med, 2), float(len(vs)), float(pos)])

FIGS["F15"] = dict(
    caption="Greece is the worst in Europe on both money questions, and among "
            "the worst on general life satisfaction",
    kind="strip",
    payload={"strips": strips15,
             "alt": "Every EU country as a dot on each of three indicators for "
                    "2024, with Greece marked. Greece is at the worst end of "
                    "reported hardship and financial expectations, and near it "
                    "on life satisfaction",
             "xLabel": "each indicator on its own scale"},
    series=f15, first="Indicator",
    extra_caveat=(
        "Each strip has its OWN scale, because the three indicators are in "
        "different units; positions may be compared within a strip and not "
        "between them. The last column of the table is Greece's position "
        "counting from the worst end. Greek life satisfaction ROSE over the "
        "observed period, from 6.2 to 6.9: the position shown here worsened "
        "because other countries improved faster, which is not the same as "
        "Greece becoming less satisfied."))

# ---- F16: the crisis as an exit route, and its reversal -------------------
mig = pd.read_csv(PROC / "migration_nationals_panel.csv")
gm = mig[mig.geo == "EL"].sort_values("time")
myrs = [int(y) for y in gm.time]
f16 = ce.Series([str(y) for y in myrs], dp=0, title="Departures and returns")
f16.add("Departures", [float(v) for v in gm.emigration_nationals])
f16.add("Returns", [float(v) for v in gm.immigration_nationals])
v16a = {"years": myrs, "dp": 0, "yLabel": "People",
        "alt": "Greek nationals leaving and returning, 2008 to 2024",
        "series": [{"label": "Departures", "tone": "gr", "style": "solid",
                    "weight": "strong",
                    "values": [int(v) for v in gm.emigration_nationals]},
                   {"label": "Returns", "tone": "series-3", "style": "solid",
                    "weight": "normal",
                    "values": [int(v) for v in gm.immigration_nationals]}]}
f16b = ce.Series([str(y) for y in myrs], dp=0, title="Net flow")
f16b.add("Net outflow of nationals", [float(v) for v in gm.net_migration_nationals])
v16b = {"years": myrs, "dp": 0,
        "zeroBand": True, "zeroLabel": "balance: equal numbers leaving and returning",
        "yLabel": "Net outflow of nationals",
        "alt": "Net outflow of Greek nationals; above the line is net exit, "
               "below it is net return",
        "series": [{"label": "Net outflow", "tone": "gr", "style": "solid",
                    "weight": "strong",
                    "values": [int(v) for v in gm.net_migration_nationals]}],
        "extraRows": [("net EXIT" if v > 0 else "net RETURN") +
                      f" of {abs(int(v)):,}" for v in gm.net_migration_nationals]}
# CUMULATIVE 2008-2024, not the latest year. Ranking on 2024 alone put Greece
# near the BOTTOM, because 2024 was a year of net return -- which repeats the
# reversal the timeline already shows and hides the historical cost.
cum = pd.read_csv(PROC / "migration_cumulative_comparison.csv")
cum = cum.sort_values("cum_net_pct_of_pop", ascending=False).reset_index(drop=True)
f16c = ce.Series(["Cumulative net departures", "% of average population",
                  "Years covered"], dp=2, title="EU comparison, cumulative")
rows16c = []
for i, r in enumerate(cum.itertuples(), start=1):
    nm = NAMES.get(r.geo, r.geo)
    f16c.add(nm, [float(r.total_net_migration), float(r.cum_net_pct_of_pop),
                  float(r.n_years)])
    rows16c.append({"label": nm, "name": nm,
                    "value": round(float(r.cum_net_pct_of_pop), 2),
                    "highlight": r.geo == "EL",
                    "detail": (f"{int(r.total_net_migration):,} cumulative net "
                               f"departures<br>{r.cum_net_pct_of_pop:.2f}% of "
                               f"average population<br>rank {i} of {len(cum)}, "
                               f"{int(r.n_years)} years")})
v16c = {"rows": rows16c, "xLabel": "% of average population, cumulative 2008-2024", "dp": 2,
        "alt": "Cumulative net departures of nationals 2008-2024 as a share of "
               "average population, 25 countries with sufficient coverage"}
FIGS["F16"] = dict(
    caption="The crisis also became an exit route &mdash; and since 2023 that "
            "has reversed",
    kind="panel",
    views=[("Departures and returns", v16a), ("Net flow", v16b),
           ("EU comparison, cumulative", v16c, "ladder")],
    view_series=[f16, f16b, f16c], first="Series",
    extra_caveat=("Net outflow peaked at 44,502 in 2012. Across 2008-2024 the "
                  "cumulative net loss is 290,281 people, 2.69% of average "
                  "population and the fifth highest of the 25 countries with "
                  "sufficient coverage. By 2023 the flow had turned: more Greek "
                  "nationals returned than left, and in 2024 the net return was "
                  "19,852. The accumulated loss is now beginning to reverse; it "
                  "has not been undone."))

# ---- F17: the trust snapshot ---------------------------------------------
tr = pd.read_csv(PROC / "oecd_trust_2023.csv")
f17 = ce.Series(["Share reporting high or moderately high trust (%)"], dp=1)
rows17 = []
for r in tr.itertuples():
    f17.add(r.entity, [float(r.share_high_or_moderate_trust)])
    rows17.append({"label": r.entity, "name": r.entity,
                   "value": float(r.share_high_or_moderate_trust),
                   "highlight": bool(r.highlight),
                   "detail": f"{r.entity}: <b>{r.share_high_or_moderate_trust:.0f}%</b>"
                             " report high or moderately high trust"
                             "<br><span style='opacity:.6'>OECD Trust Survey, "
                             "Greece, fieldwork October-November 2023</span>"})
FIGS["F17"] = dict(
    caption="Greeks trust the police and the courts far more than they trust "
            "the central government, parliament or political parties",
    kind="ladder",
    payload={"rows": rows17,
             "xLabel": "% reporting high or moderately high trust",
             "dp": 1, "unit": "%", "labelAll": True,
             "reference": 39.0,
             "referenceLabel": "OECD average, central government",
             "alt": "Greek trust across nine institutions in 2023, from other "
                    "people at 54% down to political parties at 17%, with "
                    "central government at 32% against an OECD average of 39%"},
    series=f17, first="Institution")


# ---- F18: the ESS pre-crisis baseline -------------------------------------
# A SEPARATELY LABELLED DESCRIPTIVE EXTENSION. ESS is a different instrument
# from EU-SILC and is never joined to it. The means are approximate
# reconstructions from the portal's public weighted distributions, so no
# interval is drawn and no test is reported. Levels lead, because a rank on its
# own inverts the reading: Greece's level recovered while its rank did not.
ess = pd.read_csv(PROC / "ess_greece_life_satisfaction.csv").sort_values("essround")
elab = [str(x) for x in ess.fieldwork]

# Numeric years, not evenly spaced categories: the x-scale is linear, so the
# decade with no Greek round renders as real horizontal distance instead of
# being collapsed into one more equal step.
# An empty slot at 2016 does two things: the renderer lifts the pen on a null,
# so the line BREAKS instead of drawing a trajectory through a decade nobody
# observed, and the break sits at the right place on a linear year axis.
eyrs = [2003, 2005, 2009, 2011, 2016, 2021, 2024]
GAP = 4                       # index of the unobserved slot


def gapped(vals):
    """Insert the unobserved slot so the drawn line breaks across it."""
    v = list(vals)
    return v[:GAP] + [None] + v[GAP:]

f18a = ce.Series(elab, dp=2, title="Level")
f18a.add("Greece", [float(v) for v in ess.greece_mean_approx])
f18a.add("Median of the same 12 countries",
         [float(v) for v in ess.balanced_12_median_approx])
f18a.add("Greece's gap to that median", [float(v) for v in ess.gap_vs_balanced])

f18b = ce.Series(elab, dp=0, title="Rank among the same 12")
f18b.add("Greece's rank, 1 = worst",
         [float(v) for v in ess.balanced_12_rank_worst])

v18a = {"years": eyrs, "dp": 2, "yLabel": "Life satisfaction, 0-10 (approx.)",
        "hiddenTicks": [2016],
        "alt": "Greek life satisfaction against the median of the same twelve "
               "countries across six ESS rounds; Greece is below the median in "
               "every round, falls to 5.64 in 2010/11 and recovers to 6.42; "
               "the line is broken between 2010/11 and 2020-22, where no Greek "
               "round was run",
        "series": [
            {"label": "Greece", "tone": "gr", "style": "solid",
             "weight": "strong",
             "values": gapped(float(v) for v in ess.greece_mean_approx)},
            {"label": "Median of the same 12 countries", "tone": "series-3",
             "style": "dashed", "weight": "normal",
             "values": gapped(float(v)
                              for v in ess.balanced_12_median_approx)}]}

v18b = {"years": eyrs, "dp": 0, "invertY": True, "hiddenTicks": [2016],
        "yLabel": "Rank among the same 12, 1 = worst",
        "alt": "Greece's rank among the same twelve countries, worst first; "
               "third or fourth before the crisis, worst from 2010/11 onward; "
               "the line is broken across the unobserved decade",
        "series": [
            {"label": "Greece's rank among the same 12", "tone": "gr",
             "style": "solid", "weight": "strong",
             "values": gapped(int(v) for v in ess.balanced_12_rank_worst)}]}

ess_table = (
    '<div class="ess-table"><table><caption>Greek life satisfaction across six '
    'ESS rounds, against the median of the same twelve countries in every '
    'round. Means are approximate reconstructions from published weighted '
    'percentages: no interval can be attached to them and nothing is tested on '
    'them.</caption><thead><tr><th>Period</th><th>Fieldwork</th>'
    '<th class="n">Greece</th><th class="n">Median of the 12</th>'
    '<th class="n">Gap</th><th class="n">Rank of 12</th></tr></thead><tbody>'
    + "".join(
        f'<tr{" class=gap-row" if i and int(r.essround) - prev > 2 else ""}>'
        f"<td>{r.period}</td><td>{r.fieldwork}</td>"
        f'<td class="n">{r.greece_mean_approx:.2f}</td>'
        f'<td class="n">{r.balanced_12_median_approx:.2f}</td>'
        f'<td class="n">{r.gap_vs_balanced:+.2f}</td>'
        f'<td class="n">{int(r.balanced_12_rank_worst)}'
        f'{" (worst)" if r.balanced_12_rank_worst == 1 else ""}</td></tr>'
        for i, (r, prev) in enumerate(
            zip(ess.itertuples(),
                [0] + [int(x) for x in ess.essround[:-1]])))
    + "</tbody></table><p class='tnote'>No Greek round falls between 2010/11 "
      "and 2020-22, so the decade covering the depth of the adjustment and the "
      "recovery is unobserved.</p></div>")

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
        spec = dict(spec, series=spec["view_series"][0])
    else:
        payload_html = payload_tag(spec["payload"])
        body = spec["series"].fallback_table(spec.get("first", ""))
    cav = m.caveat
    if spec.get("extra_caveat"):
        cav = ("" if cav != cav else str(cav) + " ") + spec["extra_caveat"]
    shell = ce.figure(fid, spec["caption"], m.question, m.status_label,
                      spec["kind"], {}, body, caveat=cav,
                      appendix_link="statistical_appendix.html",
                      checksum=spec["series"].checksum())
    return shell.replace(payload_tag({}), payload_html)


# ---- context entries, as a connected discussion ---------------------------
def ctx_block(cid, prose):
    """One context entry: status, permitted reading, limitation, source.

    Written as NEW prose for this document. Wrapping existing text in a
    container would satisfy the extractor and defeat the register.
    """
    e = ctx.loc[cid]
    cite = ""
    if str(e.source_status) != "not applicable":
        url = (f' <a href="{e.source_url}">source</a>'
               if isinstance(e.source_url, str) and e.source_url else "")
        det = f" {e.source_detail}" if isinstance(e.source_detail, str) and e.source_detail else ""
        cite = f'<p class="cite"><strong>Source.</strong> {e.source}{det}{url}</p>'
    return (f'<div class="ctx" data-context-id="{cid}">'
            f'<div class="ctx-head"><span class="cid">{cid}</span>'
            f'<span class="status">{e.status}</span></div>'
            f"<h4>{e.topic}</h4>{prose}"
            f'<p class="permitted"><strong>What may be concluded.</strong> {e.permitted}</p>'
            f'<p class="limitation"><strong>Limitation.</strong> {e.forbidden}</p>{cite}</div>')


# ---- the evidence table ---------------------------------------------------
BUCKET = {"supported": "Supported", "retained": "Supported",
          "inconclusive_under_available_power": "Inconclusive",
          "unsupported_with_adequate_power": "Unsupported",
          "blocked_by_proximity": "Blocked", "superseded": "Failed or superseded",
          "descriptive_only": "Descriptive"}
ROWS = [
    ("Supported", "Material resources, long-term unemployment and "
     "wage-adjusted affordability predict hardship beyond income poverty",
     "E1, bootstrap 0.0005&ndash;0.0085"),
    ("Supported", "Accumulated unemployment, wage non-recovery and housing "
     "deterioration predict hardship, and add conditional cross-country "
     "information beyond their current-level counterparts",
     "E4 and E7"),
    ("Inconclusive", "Six current-level constructs, the C3 depth measures, and "
     "compounded inflation", "below the detectable effect for their tests"),
    ("Inconclusive", "Whether any within-country dynamic exists",
     "estimates too imprecise to establish or rule out"),
    ("Unsupported", "Annual food and housing inflation at 0.70 SD; annual "
     "headline inflation at its conditional magnitude", "E2 and E7"),
    ("Blocked", "Arrears, unexpected expenses, heating and material deprivation "
     "as EXPLANATIONS", "same survey instrument as the outcome"),
    ("Descriptive", "Those same four items track reported hardship strongly "
     "within the same survey, at within-country correlations of 0.63 to 0.80, "
     "and absorb 71% of the baseline residual",
     "same-instrument corroboration, not independent validation"),
    ("Blocked", "The transfer-policy comparators",
     "algebraic functions of income poverty"),
    ("Failed or superseded", "The synthetic-control comparative design; "
     "multi-domain breadth; the accumulated wage-shortfall coefficient",
     "failed gates, failed the incremental criterion, capped by rule"),
    ("Contextual", "Institutional trust, crisis policy, migration, taxation",
     "literature-grounded, not estimated here"),
]
ev = ce.Series(["Finding", "Basis"], dp=0)
for bucket, finding, basis in ROWS:
    ev.rows.append((bucket, [finding, basis], {}))
EV_TABLE = ('<div class="tw"><table><caption>What the sequence establishes, by '
            'evidence status. Nothing in this table is new: every row points at '
            'a result reached earlier.</caption>'
            '<thead><tr><th>Status</th><th>Finding</th><th>Basis</th></tr></thead>'
            '<tbody>' + "".join(
                f'<tr><td><strong>{b}</strong></td><td>{f}</td><td>{s}</td></tr>'
                for b, f, s in ROWS) + "</tbody></table></div>")

print(f"batch 4: {len(FIGS)} figure, {len(ctx)} context entries, "
      f"{len(ROWS)} evidence rows")


# ---- the page -------------------------------------------------------------
BASE = ce.base_style((OUT / "build" / "report.html").read_text())
F15 = build("F15", FIGS["F15"])
F16 = build("F16", FIGS["F16"])
F17 = build("F17", FIGS["F17"])

# Connected discussion, not six equal cards: each entry is introduced by prose
# that says why it appears here and how it relates to the one before.
# Order: the figure that TESTS reporting style is followed immediately by the
# entry that interprets it. Previously reporting style was introduced, cut
# across by four other topics, and then introduced again.
ESS_LEAD = """
<h3>A separately labelled descriptive extension</h3>
<p>The Eurostat series used everywhere else in this report begins in 2013, at
the crisis trough, so it cannot say whether Greece was already unusual before
2008. The European Social Survey can, and the following figure is kept
deliberately apart from everything above: a different instrument, shown on its
own, never joined to the EU-SILC series and never modelled.</p>
<p>It also carries a weaker warrant than the rest of the report. The underlying
respondent files are behind a login; what is used here comes from the ESS
portal's public analysis view, which displays weighted response distributions
by country. Country means were reconstructed by multiplying each displayed
percentage by its score and summing. That reconstruction is approximate at the
precision the portal shows, it produces no confidence intervals, and nothing
inferential is built on it.</p>
"""

ESS_CTX = """
<p>Across six ESS rounds, holding the same twelve countries fixed in every
round, Greece sat roughly 0.8 points below the median <em>before</em> the
crisis, at third or fourth worst of the twelve. Its level then fell to 5.64 by
2010/11 and recovered to 6.42 by 2023/24 &mdash; approximately its pre-crisis
value.</p>
<p>Its comparative position did not recover. The gap to the median is wider
now than before the crisis, and Greece has been the worst of the twelve since
2010/11: the two countries that were below it before the crisis have since
passed it. A rise in the median accounts for part of this and being overtaken
accounts for the rest.</p>
<p>The bearing on the reporting-style question is direct. A low Greek baseline
pre-dates the crisis, so the low position cannot be attributed to the crisis
alone, and a longstanding low-wellbeing pattern remains plausible. Generic
pessimism or reporting culture cannot be dismissed &mdash; nor, on this
evidence, established.</p>
"""

DISC = {
 "CTX-1": "<p>That is the one contextual topic this project tested, and the "
          "figure above is the test. It weakens the reading-style alternative "
          "without eliminating it, which is the right place to begin "
          "everything that follows.</p>",
 "CTX-2": "<p>If reporting style is not the whole answer, the next candidate is "
          "the one that would change the reading most if it were true. Two "
          "households in identical circumstances may describe their security "
          "differently depending on whether they expect institutions to help. "
          "Greek trust in central government sits below the OECD average, and "
          "no variable in any model above measures it.</p>",
 "CTX-3": "<p>Trust does not arise from nothing, which leads to the period "
          "itself. The historical exposure measured in Stage 5 was produced by "
          "something: a decade of fiscal consolidation whose distributional "
          "effects are documented in work using EU-SILC microdata.</p>",
 "CTX-5": "<p>One channel within that period is worth naming because it is "
          "specific and testable, just not here. Consolidation leaned heavily "
          "on indirect taxation, and published incidence work finds the burden "
          "became markedly more regressive.</p>",
 "CTX-4": "<p>The same decade had another outlet, and it runs in both "
          "directions at once.</p>",
 "CTX-6": "<p>Which leaves what a reader should take from all of this for "
          "measurement rather than for policy.</p>",
}

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Batch 4 &mdash; stages 7 and 8</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu);--ok:#2f855a;--warn:#b7791f}}
body{{max-width:52rem;margin:0 auto;padding:2rem 1.2rem 5rem}}
h2{{margin:2.8rem 0 .6rem}}
.ctx{{border:1px solid var(--border);border-radius:6px;padding:1rem 1.2rem;
margin:1.2rem 0;background:var(--surface-1)}}
.ctx-head{{display:flex;gap:.7rem;align-items:baseline;margin-bottom:.3rem}}
.ctx-head .cid{{font:600 .7rem/1 ui-monospace,Menlo,monospace;
color:var(--text-muted);letter-spacing:.05em}}
.status{{font-size:.68rem;text-transform:uppercase;letter-spacing:.06em;
font-weight:700;color:var(--series-5)}}
.ctx h4{{margin:.2rem 0 .6rem;font-size:1rem}}
.ctx .permitted,.ctx .limitation,.ctx .cite{{font-size:.85rem;margin:.5rem 0 0}}
.ctx .limitation{{color:var(--text-secondary)}}
.ctx .cite{{color:var(--text-muted);word-break:break-word}}
.tw{{overflow-x:auto;margin:1.4rem 0;border:1px solid var(--border);
border-radius:6px;background:var(--surface-1)}}
.tw table{{border-collapse:collapse;width:100%;
font:.84rem/1.45 ui-sans-serif,system-ui,sans-serif}}
.tw caption{{caption-side:top;text-align:left;padding:.8rem 1rem .4rem;
font-size:.8rem;color:var(--text-muted)}}
.tw th{{text-align:left;padding:.55rem .8rem;
border-bottom:1.5px solid var(--border);font-size:.72rem;
text-transform:uppercase;letter-spacing:.04em;color:var(--text-secondary)}}
.tw td{{padding:.55rem .8rem;border-bottom:1px solid var(--border);
vertical-align:top}}
{ce.STAMP_CSS}
.proto-note{{border:1px dashed var(--border);border-radius:6px;padding:.9rem 1.1rem;
margin-bottom:2rem;font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;
color:var(--text-secondary)}}
</style></head><body>
<p class="proto-note"><strong>Batch 4.</strong> Stages 7 and 8, the last. The
context entries form one discussion rather than six equal cards, and Stage 8
synthesises only &mdash; no new estimate, no new interpretation.</p>

<h2>Stage 7 &mdash; What else might matter</h2>
<p>Everything so far has been about what can be measured on this panel. The
analysis identifies where Greek hardship aligns with material conditions and
accumulated history. It does not identify which institutions or policies
produced that history, and the honest thing is to say so and then say what is
plausible anyway &mdash; labelled as what it is.</p>
{F15}
{DISC['CTX-1']}{ctx_block('CTX-1', '')}
{ESS_LEAD}
{ess_table}
{ctx_block('CTX-7', ESS_CTX)}
{DISC['CTX-2']}{ctx_block('CTX-2', '')}
{F17}
{DISC['CTX-3']}{ctx_block('CTX-3', '')}
{DISC['CTX-5']}{ctx_block('CTX-5', '')}
{DISC['CTX-4']}{ctx_block('CTX-4', '')}
{F16}
{DISC['CTX-6']}{ctx_block('CTX-6', '')}

<h2>Stage 8 &mdash; Conclusion</h2>
<p>Greece's hardship gap cannot be explained by generic pessimism alone,
although a financial-domain-specific reporting difference cannot be excluded. It
aligns with concrete affordability failures, and with a long history of
unemployment, wage non-recovery and housing deterioration.</p>
<p>Relative income poverty understates crisis-era deterioration when read alone.
AROPE narrows the puzzle and does not close it. Concrete affordability failures
move closely with reported hardship within the same EU-SILC survey, which
corroborates the measure but does not independently validate it. And accumulated
unemployment, wage non-recovery and housing deterioration provide additional
conditional cross-country information beyond current snapshots.</p>
<p>The evidence remains <strong>cross-country rather than causal</strong>, and
the share of Greece's gap that appears accounted for depends materially on
whether closely related deprivation measures are admitted.</p>
{EV_TABLE}
<p>Nothing in that table is new. Every row points at a result reached in an
earlier stage, and this section introduces no estimate and no interpretation
that was not already established and bounded where it was produced.</p>
{ce.build_stamp()}
<script>{ce.JS}</script>
</body></html>
"""
# Build intermediates live in output/build/, not output/ itself:
# output/ holds the canonical publications and nothing else.
_BUILD = OUT / "build"
_BUILD.mkdir(exist_ok=True)
(_BUILD / "batch4.html").write_text(PAGE)
print(f"wrote output/build/batch4.html  {len(PAGE):,} chars")
