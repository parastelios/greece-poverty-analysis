"""Batch 3: stages 5 and 6.

Stage 5 leads with accumulated exposure and ENDS with the between/within
figure, so the strongest-looking result is immediately bounded by the
limitation that governs it.
"""
import json
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
man = pd.read_csv(PROC / "report_visual_manifest.csv").set_index("id")
acc = pd.read_csv(PROC / "e4_accumulated_panel.csv")
e4 = pd.read_csv(PROC / "e4_results.csv")
e7 = pd.read_csv(PROC / "e7_results.csv")
dyn = pd.read_csv(PROC / "e7_dynamic.csv")
p3r = pd.read_csv(PROC / "p3_residuals.csv")
ear = pd.read_csv(PROC / "ea_companion_residuals.csv")
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

# ---- F11: the three supported accumulated measures, all countries ---------
# Units differ between these measures and must be stated: summing an annual
# excess over years gives percentage-point-YEARS, while a duration count gives
# years. Presenting them without units invites the reader to compare 137.5 with
# 15 as if they were the same quantity.
ACC_UNIT = {"acc_cum_excess_unemployment": "percentage-point-years above 2009",
            "acc_housing_excess": "percentage-point-years above 2010",
            "dur_real_wages_below": "consecutive years below the 2008 level"}
views11, series11 = [], []
for v in ["acc_cum_excess_unemployment", "dur_real_wages_below", "acc_housing_excess"]:
    d = acc.dropna(subset=[v])
    latest = d[d.time == d.time.max()][["geo", v]].sort_values(v, ascending=False)
    med = float(latest[v].median())
    unit = ACC_UNIT[v]
    s = ce.Series([f"{ce.name(v)} ({unit})"], dp=1, title=ce.name(v))
    rows = []
    for i, r in enumerate(latest.itertuples(), start=1):
        val = float(getattr(r, v))
        s.add(NAMES.get(r.geo, r.geo), [val])
        rows.append({"label": NAMES.get(r.geo, r.geo), "name": NAMES.get(r.geo, r.geo),
                     "value": round(val, 1), "highlight": r.geo == "EL",
                     "detail": f"rank {i} of {len(latest)}<br>"
                               f"<span style='opacity:.6'>{unit}</span>"})
    series11.append(s)
    views11.append((ce.name(v), {
        "rows": rows, "dp": 1, "reference": round(med, 1),
        "referenceLabel": "EU median", "unit": unit,
        "alt": f"{ce.name(v)} for all 27 countries, latest year, in {unit}"},
        "ladder"))
FIGS["F11"] = dict(
    caption="Greece ranks first on accumulated unemployment and housing "
            "deterioration, and second on wage non-recovery",
    kind="ladder", views=views11, view_series=series11, first="Country",
    extra_caveat=("The three measures are in different units and may not be "
                  "compared with each other: accumulated unemployment and "
                  "housing deterioration are percentage-point-years, wage "
                  "non-recovery is a count of consecutive years."))

# ---- F12: the conditional coefficients ------------------------------------
TONE = {"supported": "series-3",
        "inconclusive_under_available_power": "text-muted",
        "unsupported_with_adequate_power": "warn",
        "capped_by_ceiling_cannot_create_support": "series-5",
        "contradicts_direction": "gr"}
SHORT = {"supported": "adds information",
         "inconclusive_under_available_power": "inconclusive",
         "unsupported_with_adequate_power": "unsupported",
         "capped_by_ceiling_cannot_create_support": "capped by rule",
         "contradicts_direction": "wrong direction"}
d12 = e7.copy()
d12["is_acc"] = d12.focal.str.startswith(("acc_", "dur_"))
d12 = d12.sort_values(["pair", "is_acc"], ascending=[True, False])
f12 = ce.Series(["Coefficient", "p FDR", "Bootstrap p", "Focal VIF",
                 "Conditional MDE (SD)"], dp=4)
rows12 = []
for r in d12.itertuples():
    lbl = f"{ce.name(r.focal)} | {ce.name(r.controlling_for)}"
    f12.add(lbl, [float(r.coef_joint),
                  None if r.p_fdr != r.p_fdr else float(r.p_fdr),
                  None if r.boot_p != r.boot_p else float(r.boot_p),
                  float(r.focal_vif),
                  None if r.conditional_mde_sd != r.conditional_mde_sd
                  else float(r.conditional_mde_sd)])
    boot = "not run" if r.boot_p != r.boot_p else f"{r.boot_p:.4f}"
    rows12.append({
        "label": lbl, "est": round(float(r.coef_joint), 4),
        "lo": round(float(r.ci_lo), 4), "hi": round(float(r.ci_hi), 4),
        "tone": TONE.get(r.reportable_outcome, "text-muted"),
        "strong": r.reportable_outcome == "supported",
        "right": SHORT.get(r.reportable_outcome, ""),
        "detail": (f"<span style='opacity:.6'>{r.focal} | {r.controlling_for}</span>"
                   f"<br>{r.coef_joint:+.4f} with its counterpart controlled"
                   f"<br>cluster-robust 95% CI [{r.ci_lo:+.4f}, {r.ci_hi:+.4f}]"
                   f"<br>bootstrap p <b>{boot}</b>"
                   f"<br>focal VIF {r.focal_vif:.2f}"
                   f"<br>this pair's detectable effect: "
                   f"{'—' if r.conditional_mde_sd != r.conditional_mde_sd else f'{r.conditional_mde_sd:.2f} SD'}")})
FIGS["F12"] = dict(
    caption="Accumulated history provides additional conditional cross-country "
            "information in three of eight pairs",
    kind="coefficient",
    payload={"rows": rows12, "alt": "The sixteen conditional coefficients, each "
             "tested with its counterpart in the same model"},
    series=f12, first="Test",
    extra_caveat=("Each coefficient is tested against ITS OWN pair-specific "
                  "detectable effect, not a single study-wide threshold: "
                  "conditional power depends on how much independent variation "
                  "survives once the counterpart is controlled. Bars are "
                  "cluster-robust intervals; the bootstrap decides support."))

# ---- F13: between against within, the limitation --------------------------
f13 = ce.Series(["Between", "Between p", "Within", "Within p",
                 "First difference", "First difference p"], dp=4)
rows13 = []
PAIRNAME = {r.pair: ce.name(r.focal) for r in e7.itertuples()
            if str(r.focal).startswith(("acc_", "dur_"))}
for r in dyn.itertuples():
    nm = PAIRNAME.get(r.pair, r.pair)
    f13.add(nm, [float(r.acc_between), float(r.acc_between_p),
                 float(r.acc_within), float(r.acc_within_p),
                 float(r.fd_acc), float(r.fd_acc_p)])
    rows13.append({
        "label": nm, "a": round(float(r.acc_within), 4),
        "b": round(float(r.acc_between), 4),
        "tone": "series-3" if r.acc_between_p < 0.05 else "text-muted",
        "strong": bool(r.acc_between_p < 0.05),
        "right": "no dynamic support",
        "detail": (f"between <b>{r.acc_between:+.4f}</b> (p {r.acc_between_p:.4f})"
                   f"<br>within {r.acc_within:+.4f} (p {r.acc_within_p:.4f})"
                   f"<br>first difference {r.fd_acc:+.4f} (p {r.fd_acc_p:.4f})")})
FIGS["F13"] = dict(
    caption="The supported historical associations are predominantly between "
            "countries; the within-country estimates provide no supporting "
            "dynamic evidence",
    kind="dumbbell",
    payload={"rows": rows13, "dp": 3, "legendA": "within countries",
             "legendB": "between countries", "zeroLabel": "no effect",
             "alt": "Between-country against within-country estimates for every "
                    "accumulated measure"},
    series=f13, first="Accumulated measure",
    # Wording matches the canonical elements the build now requires, so the
    # guard and the text cannot drift apart.
    extra_caveat=("This does NOT establish that no within-country relationship "
                  "exists: the within estimates are too imprecise to establish "
                  "or rule out such a relationship. The frozen result records "
                  "them as inconclusive, not absent."))

# ---- F14: model dependence -----------------------------------------------
a = p3r.set_index("geo").resid
b = ear.set_index("geo").resid
common = [g for g in a.index if g in b.index]
common.sort(key=lambda g: a[g], reverse=True)
f14 = ce.Series(["Frozen specification", "Deprivation-free companion", "Change"],
                dp=2)
rows14 = []
for g in common:
    f14.add(NAMES.get(g, g), [float(a[g]), float(b[g]), float(b[g] - a[g])])
    rows14.append({"label": NAMES.get(g, g), "a": round(float(a[g]), 2),
                   "b": round(float(b[g]), 2),
                   "tone": "gr" if g == "EL" else "text-muted",
                   "strong": g == "EL",
                   "right": "Greece" if g == "EL" else "",
                   "detail": (f"frozen {a[g]:+.2f} &rarr; companion {b[g]:+.2f}"
                              f"<br>{'crosses zero' if a[g] * b[g] < 0 else 'same side of zero'}")})
FIGS["F14"] = dict(
    caption="Removing the same-instrument deprivation measure moves Greece "
            "from under-predicted to over-predicted",
    kind="dumbbell",
    payload={"rows": rows14, "dp": 2, "legendA": "frozen specification",
             "legendB": "deprivation-free companion", "zeroLabel": "predicted exactly",
             "alt": "Country residuals under both specifications, on identical rows"},
    series=f14, first="Country")

print(f"batch 3: stages 5-6, {len(FIGS)} figures")
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
<title>Batch 3 &mdash; stages 5 and 6</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu);--ok:#2f855a;--warn:#b7791f}}
body{{max-width:52rem;margin:0 auto;padding:2rem 1.2rem 5rem}}
h2{{margin:2.8rem 0 .6rem}}
.signpost{{border-left:3px solid var(--series-3);padding:.7rem 1rem;
background:var(--surface-2);border-radius:0 5px 5px 0;margin:1.6rem 0}}
.bound{{border-left:3px solid var(--gr)}}
.proto-note{{border:1px dashed var(--border);border-radius:6px;padding:.9rem 1.1rem;
margin-bottom:2rem;font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;
color:var(--text-secondary)}}
</style></head><body>
<p class="proto-note"><strong>Batch 3.</strong> Stages 5 and 6. Stage 5 leads
with accumulated exposure and ends with the between/within figure, so the
strongest-looking result is bounded by its central limitation before the reader
carries it anywhere.</p>

<h2>Stage 5 &mdash; Accumulated history</h2>
<p>Stage 4 found that present conditions explain part of the gap. But something
recovered without hardship following it down, which is what makes accumulated
history worth testing: not what a country looks like now, but how much damage it
has absorbed and for how long.</p>
{b['F11']}
<p>Greece ranks first of 27 on accumulated unemployment and on housing
deterioration since 2010, and second behind Hungary on years of wage
non-recovery. That is the strongest-looking result in the report, and the next
two figures establish exactly how far it can be taken.</p>
<p>The first question is whether accumulated history adds anything once today's
conditions are in the same model. Separate models cannot answer that; comparing
two p-values from two regressions is not a test.</p>
{b['F12']}
<p>Three pairs answer yes: accumulated unemployment beyond current long-term
unemployment, wage duration beyond the current wage level, and housing
deterioration beyond current overburden. One runs the other way &mdash; for
wage-adjusted affordability it is the present-day measure that survives.</p>
<p class="signpost bound"><strong>And here is the boundary.</strong> Everything
above compares countries with different histories. It does not show that
hardship rose <em>inside</em> Greece as damage accumulated &mdash; a different
claim, and one this evidence does not support.</p>
{b['F13']}
<p>No within-country estimate is significant in the adverse direction and no
first-difference test supports one, so there is no dynamic evidence here. That
is not the same as showing there is none: the within estimates are too imprecise
to establish or rule out such a relationship. Countries carrying more historical
exposure report more hardship, and that is a marker rather than a demonstrated
process.</p>

<h2>Stage 6 &mdash; Which model?</h2>
<p>A reader is entitled to ask how much of Greece's gap the full model accounts
for. There is no single answer, and that is the finding rather than a gap in
it.</p>
{b['F14']}
<p>The two specifications differ by one predictor, run on identical rows, and
produce residuals of opposite sign. Greece travels from third-most
under-predicted to third-most over-predicted. Neither is the definitive model,
they are not merged or averaged, and neither is chosen because its residual
looks better.</p>
<script>{ce.JS}</script>
</body></html>
"""
(OUT / "batch3.html").write_text(PAGE)
print(f"\nwrote output/batch3.html  {len(PAGE):,} chars")
