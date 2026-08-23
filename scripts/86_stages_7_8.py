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


# ---- F15: rank trajectories ----------------------------------------------
# "Rank 1" means opposite things across these indicators unless the direction is
# stated: worst on hardship, worst on expectations, but BEST on satisfaction if
# ranked naively. Every series is oriented so 1 = WORST, and the axis is
# inverted so worse is higher.
yrs = [int(y) for y in cross.year] if "year" in cross else [int(y) for y in cross.time]

# Hardship and financial expectations are at rank 1 in EVERY available year, so
# they draw as one line on top of another and the reader sees a series go
# missing. They are combined into a single labelled series, with the fallback
# table keeping them apart.
same = all(a == 1 and b == 1 for a, b in
           zip(cross.gr_subj_poverty_rank_worst, cross.gr_fin_expectations_rank_worst))
assert same, "the two series are no longer identical; separate them again"

f15 = ce.Series(["Hardship rank", "Expectations rank", "Life satisfaction rank",
                 "Hardship %", "Expectations index", "Life satisfaction (0-10)"],
                dp=1)
for i, y in enumerate(yrs):
    r = cross.iloc[i]
    f15.add(str(y), [float(r.gr_subj_poverty_rank_worst),
                     float(r.gr_fin_expectations_rank_worst),
                     float(r.gr_life_sat_rank_worst),
                     float(r.gr_subj_poverty_value),
                     float(r.gr_fin_expectations_value),
                     float(r.gr_life_sat_value)])

# Ranks hide the size of the differences, so the values ride along in the tooltip.
extra = [f"hardship {r.gr_subj_poverty_value:.1f}% &middot; expectations "
         f"{r.gr_fin_expectations_value:.1f} &middot; life satisfaction "
         f"{r.gr_life_sat_value:.1f}/10" for r in cross.itertuples()]

FIGS = {"F15": dict(
    caption="Greece is worst in the EU on hardship and on financial "
            "expectations in every available year, but not on life satisfaction",
    kind="panel",
    payload={"years": yrs, "dp": 0, "invertY": True,
             "yLabel": "EU rank, 1 = worst",
             "extraRows": extra,
             "alt": "Greece's EU rank on three indicators, 1 is worst; hardship "
                    "and financial expectations coincide at rank 1 throughout",
             "series": [
                 {"label": "Hardship and financial expectations: both rank 1",
                  "tone": "gr", "style": "solid", "weight": "strong",
                  "values": [int(v) for v in cross.gr_subj_poverty_rank_worst]},
                 {"label": "Life satisfaction", "tone": "series-3",
                  "style": "solid", "weight": "normal",
                  "values": [int(v) for v in cross.gr_life_sat_rank_worst]}]},
    series=f15, first="Year",
    extra_caveat=(
        "Rank 1 is the EU's worst position. Greece ranks first on hardship and "
        "financial expectations in every available year, but 2nd-6th on life "
        "satisfaction. This weakens generic pessimism without excluding "
        "financially specific reporting differences. The vertical axis shows "
        "only the worst seven ranks, so movement within that band looks larger "
        "than it is against all 27; 2019 and 2020 are not available."))}


# ---- F16: the crisis as an exit route, and its reversal -------------------
mig = pd.read_csv(PROC / "migration_nationals_panel.csv")
gm = mig[mig.geo == "EL"].sort_values("time")
myrs = [int(y) for y in gm.time]
f16 = ce.Series([str(y) for y in myrs], dp=0, title="Departures and returns")
f16.add("Departures", [float(v) for v in gm.emigration_nationals])
f16.add("Returns", [float(v) for v in gm.immigration_nationals])
v16a = {"years": myrs, "dp": 0,
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
v16c = {"rows": rows16c, "dp": 2,
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
                   "detail": "trust in central government, 2023<br>"
                             "<span style='opacity:.6'>OECD Trust Survey, "
                             "fieldwork October-November 2023</span>"})
FIGS["F17"] = dict(
    caption="Institutional trust in Greece is below the OECD average",
    kind="ladder",
    payload={"rows": rows17, "dp": 1, "unit": "%", "labelAll": True,
             "alt": "Trust in central government, Greece against the OECD "
                    "average, 2023"},
    series=f17, first="Entity")


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
BASE = re.search(r"<style.*?</style>", (OUT / "report.html").read_text(), re.S).group(0)
F15 = build("F15", FIGS["F15"])
F16 = build("F16", FIGS["F16"])
F17 = build("F17", FIGS["F17"])

# Connected discussion, not six equal cards: each entry is introduced by prose
# that says why it appears here and how it relates to the one before.
# Order: the figure that TESTS reporting style is followed immediately by the
# entry that interprets it. Previously reporting style was introduced, cut
# across by four other topics, and then introduced again.
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
(OUT / "batch4.html").write_text(PAGE)
print(f"wrote output/batch4.html  {len(PAGE):,} chars")
