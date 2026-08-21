"""Render the interactive statistical appendix from appendix_series_core.json.

Every chart draws all 27 EU member states as faint lines, with Greece and the
EU comparator highlighted. Hovering reads out the year, Greece's value, the EU
value, and the value of whichever country's line the cursor is nearest -- which
is the point of the appendix: the reports use these variables, but a reader
could not previously look up what any of them actually was.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
DEST = ROOT / "output" / "statistical_appendix.html"

blob = json.load(open(OUT / "appendix_series_core.json"))


# ---------------------------------------------------------------------------
# Section order follows the reports' own argument, not the data's categories:
# the puzzle, why the official ruler understates it, the labour-market
# explanation (level -> duration -> accumulation), what that history did to
# household finances, the alternatives tested, and finally the diagnostics.
# Each entry is (kind, key) where kind is series | panel | scatter.
# ---------------------------------------------------------------------------
SECTIONS = [
    dict(id="puzzle", num="1", title="The puzzle",
         blurb="Greece's official income-poverty rate is elevated but ordinary; the share of "
               "households saying they cannot make ends meet is the highest in the Union. These "
               "are the two measures whose divergence the whole project exists to explain.",
         items=[("series", "subjective_poverty"), ("series", "arop"), ("series", "arope"),
                ("scatter", "arop_vs_subjective"), ("scatter", "arope_vs_subjective"),
                ("panel", "arope_by_age"),
                ("sub", "How wide the disadvantage is \u2014 descriptive, not a model input"),
                ("series", "breadth_worst_quintile"),
                ("panel", "breadth_indicator_ladder")]),

    dict(id="ruler", num="2", title="Why the official ruler understates the crisis",
         blurb="AROP's threshold is 60% of each year's national median, so when incomes collapse "
               "together the line falls with them. Holding it fixed at its 2008 real value instead "
               "tells a very different story.",
         items=[("series", "arop_threshold_real"), ("panel", "anchored_poverty"),
                ("series", "s80s20")]),

    dict(id="labour", num="3", title="The labour market: level, duration, accumulation",
         blurb="The report's central explanation moves through three steps. How much unemployment "
               "there is; how long it lasts; and how much a country has accumulated over the years "
               "since the crisis. Each step explains more of Greece's gap than the last.",
         items=[("sub", "How much unemployment, and how long it lasts"),
                ("series", "unemployment"), ("series", "ltu"), ("series", "youth_unemployment"),
                ("series", "employment_rate"),
                ("scatter", "ltu_vs_subjective"),
                ("sub", "Accumulated over time, not just this year"),
                ("series", "cum_excess_unemployment"), ("series", "cum_excess_ltu"),
                ("scatter", "cumulative_vs_subjective")]),

    dict(id="income", num="4", title="Income, output and what never came back",
         blurb="What the economy produces, what households receive, and how far both remain below "
               "their own pre-crisis peaks.",
         items=[("sub", "Output, and how far below its own peak"),
                ("series", "real_gdp_pc"), ("series", "pct_below_peak"),
                ("sub", "What households actually receive and spend"),
                ("series", "income_pps"), ("series", "real_income_idx"),
                ("series", "consumption_pc"), ("scatter", "income_vs_subjective")]),

    dict(id="work", num="5", title="Work effort: hours against reward",
         blurb="Greece works the longest week in the Union at the lowest hourly compensation. The "
               "paradox survives even among people who have jobs.",
         items=[("series", "working_hours"), ("series", "hourly_comp"),
                ("scatter", "hours_vs_pay"),
                ("series", "real_wages_idx"), ("series", "work_effort_squeeze"),
                ("series", "min_wage")]),

    dict(id="prices", num="6", title="Prices, and what they cost a local paycheck",
         blurb="Greece is not an expensive country by raw price level. Measured against Greek "
               "wages, it becomes one. The overall comparison comes first; the category detail "
               "(published for 2022 onward only) follows.",
         items=[("sub", "The overall picture"),
                ("panel", "prices_raw_vs_adjusted"),
                ("series", "price_a01"), ("series", "wadj_a01"),
                ("series", "price_avg_categories"),
                ("scatter", "prices_vs_pay"),
                ("sub", "Inflation"),
                ("series", "hicp"), ("series", "hicp_food"), ("series", "hicp_housing"),
                ("sub", "Category detail \u2014 published for 2022 onward only. Each category "
                        "appears twice: the raw price level, then the same prices divided by the "
                        "country's own wage level."),
                ("series", "price_a0101"), ("series", "wadj_a0101"),
                ("series", "price_a0104"), ("series", "wadj_a0104"),
                ("series", "price_a0107"), ("series", "wadj_a0107"),
                ("series", "price_a0108"), ("series", "wadj_a0108"),
                ("series", "price_a0111"), ("series", "wadj_a0111")]),

    dict(id="strain", num="7", title="Household financial strain",
         blurb="The cash-flow and housing pressures that close much of Greece's gap in-sample. "
               "Two of these -- arrears and the inability to meet an unexpected expense -- are "
               "themselves close to the outcome being explained, and are treated cautiously in "
               "the reports for that reason.",
         items=[("sub", "Material deprivation"),
                ("series", "deprivation_new"), ("series", "deprivation_legacy"),
                ("sub", "Housing"),
                ("series", "housing_overburden"), ("panel", "housing_by_tenure"),
                ("sub", "Cash-flow strain \u2014 the two measures closest to the outcome itself"),
                ("series", "arrears"), ("series", "unexpected"), ("series", "warm"),
                ("scatter", "housing_vs_arrears"),
                ("sub", "Saving and debt \u2014 the counter-narrative pair"),
                ("series", "saving_rate"), ("series", "debt_to_income"),
                ("scatter", "debt_vs_saving")]),

    dict(id="expectations", num="8", title="Expectations, wellbeing and who left",
         blurb="Self-reported expectations are the most heavily caveated evidence in the project. "
               "Life satisfaction matters here as a check: if Greek answers were simply gloomier "
               "across the board, Greece would be as extreme on this as on financial hardship. "
               "It is not.",
         items=[("series", "fin_expectations"), ("series", "life_satisfaction"),
                ("scatter", "lifesat_vs_subjective"),
                ("series", "net_migration"), ("series", "transfer_effect")]),

    dict(id="diagnostics", num="9", title="Model diagnostics",
         blurb="How the models actually performed. The in-sample figure is always the more "
               "flattering one, which is why the reports lead with out-of-sample and nested "
               "validation instead.",
         items=[("panel", "gap_ladder"), ("panel", "model_scorecard_bars"),
                ("panel", "model_actual_vs_predicted"),
                ("panel", "partial_cumulative_unemployment"),
                ("panel", "residual_dumbbell"),
                ("panel", "predictor_correlation"),
                ("panel", "all_candidate_correlation")]),

    dict(id="candidates", num="10", title="The full candidate family (mostly nulls)",
         blurb="Eighteen cumulative and duration constructions were screened together before "
               "cumulative excess unemployment was selected. Only two survived correction. The "
               "rest are shown here in full, because a screening family reported only by its "
               "winner is not a screening family.",
         items=[("panel", "candidate_fdr"), ("panel", "selection_frequency")]),
         # remaining candidate series are appended programmatically below
]

HEAD = """<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Statistical Appendix — The Greek Poverty Paradox</title>
<style>
:root{
  color-scheme: light;
  --page:#f9f9f7; --surface-1:#fcfcfb; --surface-2:#f3f2ee;
  --text-primary:#0b0b0b; --text-secondary:#52514e; --text-muted:#898781;
  --gridline:#e1e0d9; --border:rgba(11,11,11,0.10);
  --gr:#2a78d6; --eu:#eb6834; --faint:#b8b7b0; --hi:#1baf7a;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --page:#111110; --surface-1:#191918; --surface-2:#222221;
    --text-primary:#ffffff; --text-secondary:#c3c2b7; --text-muted:#898781;
    --gridline:#2c2c2a; --border:rgba(255,255,255,0.12);
    --gr:#3987e5; --eu:#f07a49; --faint:#4a4a47; --hi:#2ecc8f;
  }
}
:root[data-theme="dark"]{
  --page:#111110; --surface-1:#191918; --surface-2:#222221;
  --text-primary:#ffffff; --text-secondary:#c3c2b7; --text-muted:#898781;
  --gridline:#2c2c2a; --border:rgba(255,255,255,0.12);
  --gr:#3987e5; --eu:#f07a49; --faint:#4a4a47; --hi:#2ecc8f;
}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--text-primary);
  font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.6;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:44px 22px 90px}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
  color:var(--text-muted);margin:0 0 12px}
h1{font-size:38px;line-height:1.12;letter-spacing:-.02em;margin:0 0 16px;text-wrap:balance}
.dek{font-size:16.5px;color:var(--text-secondary);max-width:70ch;margin:0 0 10px}
.howto{background:var(--surface-2);border-radius:10px;padding:16px 18px;margin:22px 0 8px;
  font-size:13.5px;color:var(--text-secondary);max-width:78ch}
.howto b{color:var(--text-primary)}
nav.toc{background:var(--surface-1);border:1px solid var(--border);border-radius:10px;
  padding:16px 18px;margin:22px 0 34px}
nav.toc a{display:inline-block;margin:3px 14px 3px 0;font-size:13.5px;color:var(--gr);
  text-decoration:none}
nav.toc a:hover{text-decoration:underline}
h2.group{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--text-muted);margin:52px 0 4px;padding-top:12px;border-top:1px solid var(--gridline)}
p.group-blurb{font-size:13.5px;color:var(--text-secondary);margin:0 0 20px;max-width:74ch}
/* ---- glossary ---- */
.gloss-wrap{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;
  padding:18px 20px 6px}
.gloss-search{width:100%;box-sizing:border-box;padding:9px 12px;margin-bottom:6px;
  font:inherit;font-size:13.5px;color:var(--text-primary);background:var(--surface-2);
  border:1px solid var(--border);border-radius:8px}
.gloss-search:focus{outline:2px solid var(--gr);outline-offset:1px}
h3.gloss-group{font-size:12px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--text-secondary);margin:22px 0 8px;padding-bottom:6px;
  border-bottom:1px solid var(--border)}
dl.gloss{margin:0}
.gloss-row{display:grid;grid-template-columns:150px 1fr;gap:10px 18px;
  padding:9px 0;border-bottom:1px solid var(--border)}
.gloss-row:last-child{border-bottom:none}
.gloss-row dt{font-weight:650;color:var(--gr);font-size:13.5px;
  font-variant-numeric:tabular-nums;word-break:break-word}
.gloss-row dd{margin:0;font-size:13.5px;line-height:1.55;color:var(--text-secondary)}
.gloss-full{display:block;color:var(--text-primary);font-weight:550}
.gloss-def{display:block;margin-top:3px}
.gloss-row[hidden]{display:none}
.gloss-none{padding:14px 0;color:var(--text-secondary);font-size:13.5px}
@media(max-width:640px){.gloss-row{grid-template-columns:1fr;gap:2px}}
.chart-card{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;
  padding:18px 20px 12px;margin:0 0 20px}
.chart-title{font-size:15.5px;font-weight:650;margin:0 0 3px;letter-spacing:-.01em}
.secnum{display:inline-block;min-width:26px;color:var(--gr);font-weight:800}
.subhead{font-size:12.5px;font-weight:700;letter-spacing:.03em;color:var(--text-secondary);
  margin:26px 0 12px;padding-bottom:5px;border-bottom:1px solid var(--gridline);max-width:74ch}
.tag{display:inline-block;font-size:10px;font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;color:var(--hi);border:1px solid var(--hi);border-radius:4px;
  padding:1px 6px;margin-right:8px;vertical-align:2px}
.scatter-card{border-left:3px solid var(--hi)}
.candidate-detail{margin:0 0 12px;border:1px solid var(--border);border-radius:10px;
  background:var(--surface-1)}
.candidate-detail summary{cursor:pointer;padding:11px 14px;font-size:13px;font-weight:650;
  color:var(--text-secondary);list-style-position:inside}
.candidate-detail[open] summary{border-bottom:1px solid var(--border);color:var(--text-primary)}
.candidate-detail .chart-card{border:0;border-radius:0;margin:0;background:transparent}
nav.toc a b{color:var(--gr);margin-right:5px}
.chart-unit{font-size:12px;color:var(--text-muted);margin:0 0 2px}
.chart-note{font-size:12.5px;color:var(--text-secondary);margin:6px 0 0;max-width:80ch}
.chart-basis{font-size:11.5px;color:var(--text-muted);margin:4px 0 0}
.chart-wrap{position:relative;margin-top:10px}
svg.chart{width:100%;height:auto;display:block;overflow:visible}
.gridline{stroke:var(--gridline);stroke-width:1}
.axis-label{font-size:10.5px;fill:var(--text-muted)}
.line-faint{fill:none;stroke:var(--faint);stroke-width:1;opacity:.55}
.line-gr{fill:none;stroke:var(--gr);stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round}
.line-eu{fill:none;stroke:var(--eu);stroke-width:2;stroke-dasharray:6 4;stroke-linejoin:round}
.crosshair{stroke:var(--text-muted);stroke-width:1;stroke-dasharray:3 3;opacity:0}
.hover-dot{opacity:0;pointer-events:none}
.hit{fill:transparent;cursor:crosshair}
.tip{position:absolute;pointer-events:none;opacity:0;transform:translate(-50%,0);
  background:var(--surface-1);border:1px solid var(--border);border-radius:8px;
  padding:9px 11px;font-size:12.5px;line-height:1.5;white-space:nowrap;z-index:5;
  box-shadow:0 4px 16px rgba(0,0,0,.13)}
.tip .y{font-weight:700;margin-bottom:4px}
.tip .r{display:flex;gap:7px;align-items:center}
.tip .sw{width:9px;height:9px;border-radius:2px;flex:none}
.tip .v{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:600}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--text-secondary);
  margin-top:8px}
.legend span{display:flex;align-items:center;gap:6px}
.legend i{width:16px;height:0;border-top-width:2.5px;border-top-style:solid;display:inline-block}
table.mini{border-collapse:collapse;width:100%;font-size:12.5px;margin-top:10px}
table.mini th,table.mini td{padding:6px 9px;border-bottom:1px solid var(--gridline);text-align:right}
table.mini th:first-child,table.mini td:first-child{text-align:left}
table.mini th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--text-muted);font-weight:600}
table.mini td.gr{color:var(--gr);font-weight:650}
.scroll{overflow-x:auto}
footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--gridline);
  font-size:12.5px;color:var(--text-muted);max-width:80ch}
@media(max-width:760px){
  .wrap{padding:28px 14px 70px} h1{font-size:29px}
  .chart-card{padding:14px 12px 10px}
}
</style>"""


JS = """
<script>
const DATA = __DATA__;
const NAMES = __NAMES__;
const EL = 'EL';

function fmt(v, unit){
  if (v === null || v === undefined) return '--';
  const a = Math.abs(v);
  if (a >= 10000) return v.toLocaleString(undefined,{maximumFractionDigits:0});
  if (a >= 100) return v.toFixed(1);
  return v.toFixed(a < 10 ? 2 : 1);
}
function cssv(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

function drawSeries(host, key, s){
  const W = 860, H = 300, padL = 52, padR = 96, padT = 14, padB = 30;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const years = s.years;
  const xs = y => padL + (years.length === 1 ? plotW/2
              : (y - years[0]) / (years[years.length-1] - years[0]) * plotW);

  let lo = Infinity, hi = -Infinity;
  const all = Object.values(s.countries).concat([s.eu]);
  all.forEach(a => a.forEach(v => { if (v !== null) { if (v < lo) lo = v; if (v > hi) hi = v; }}));
  if (!isFinite(lo)) { lo = 0; hi = 1; }
  // Don't pad below zero for quantities that cannot be negative -- an axis
  // reading -1.8 on an unemployment rate is simply wrong.
  const padY = (hi - lo) * 0.08 || 1;
  const canBeNegative = lo < 0;
  lo = canBeNegative ? lo - padY : Math.max(0, lo - padY);
  hi += padY;
  const ys = v => padT + plotH - (v - lo) / (hi - lo) * plotH;

  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.setAttribute('class', 'chart');
  const el = (t, a) => { const e = document.createElementNS(ns, t);
    for (const k in a) e.setAttribute(k, a[k]); return e; };

  // y gridlines
  for (let i = 0; i <= 4; i++){
    const v = lo + (hi - lo) * i / 4, y = ys(v);
    svg.appendChild(el('line', {x1: padL, x2: W - padR, y1: y, y2: y, class: 'gridline'}));
    const t = el('text', {x: padL - 7, y: y + 3.5, 'text-anchor': 'end', class: 'axis-label'});
    t.textContent = fmt(v, s.unit); svg.appendChild(t);
  }
  // x labels
  const step = Math.max(1, Math.ceil(years.length / 8));
  years.forEach((y, i) => { if (i % step && i !== years.length - 1) return;
    const t = el('text', {x: xs(y), y: H - padB + 16, 'text-anchor': 'middle', class: 'axis-label'});
    t.textContent = y; svg.appendChild(t); });

  const path = (vals, cls) => {
    let d = '', pen = false;
    vals.forEach((v, i) => { if (v === null) { pen = false; return; }
      d += (pen ? ' L ' : ' M ') + xs(years[i]) + ',' + ys(v); pen = true; });
    return d ? el('path', {d: d, class: cls}) : null;
  };

  const codes = Object.keys(s.countries).filter(c => c !== EL);
  codes.forEach(c => { const p = path(s.countries[c], 'line-faint');
    if (p) { p.setAttribute('data-c', c); svg.appendChild(p); } });
  const pe = path(s.eu, 'line-eu'); if (pe) svg.appendChild(pe);
  const pg = path(s.countries[EL] || [], 'line-gr'); if (pg) svg.appendChild(pg);

  // end labels for Greece and EU
  const lastIdx = a => { for (let i = a.length - 1; i >= 0; i--) if (a[i] !== null) return i; return -1; };
  [[s.countries[EL], 'gr', 'Greece'], [s.eu, 'eu', 'EU']].forEach(([arr, col, nm]) => {
    if (!arr) return; const i = lastIdx(arr); if (i < 0) return;
    const t = el('text', {x: xs(years[i]) + 6, y: ys(arr[i]) + 4,
      class: 'axis-label', style: `fill:var(--${col});font-weight:700;font-size:11.5px`});
    t.textContent = nm + ' ' + fmt(arr[i], s.unit); svg.appendChild(t);
  });

  const cross = el('line', {class: 'crosshair', y1: padT, y2: padT + plotH});
  svg.appendChild(cross);
  const dotG = el('circle', {r: 4.5, fill: cssv('--gr'), class: 'hover-dot'});
  const dotE = el('circle', {r: 4, fill: cssv('--eu'), class: 'hover-dot'});
  const dotN = el('circle', {r: 4, fill: cssv('--hi'), class: 'hover-dot'});
  [dotG, dotE, dotN].forEach(d => svg.appendChild(d));

  const tip = document.createElement('div'); tip.className = 'tip';
  const wrap = document.createElement('div'); wrap.className = 'chart-wrap';
  wrap.appendChild(svg); wrap.appendChild(tip); host.appendChild(wrap);

  let hlPath = null;
  // The highlight is applied as inline styles, so clearing has to remove those
  // -- resetting the class alone left every line the cursor had passed stuck in
  // the highlight colour.
  const clearHl = () => {
    if (hlPath){ hlPath.style.stroke=''; hlPath.style.strokeWidth=''; hlPath.style.opacity='';
      hlPath.setAttribute('class','line-faint'); hlPath = null; }
  };

  const hit = el('rect', {x: padL, y: padT, width: plotW, height: plotH, class: 'hit'});
  svg.appendChild(hit);

  function move(ev){
    const r = svg.getBoundingClientRect();
    const mx = (ev.clientX - r.left) / r.width * W;
    const my = (ev.clientY - r.top) / r.height * H;
    let bi = 0, bd = Infinity;
    years.forEach((y, i) => { const d = Math.abs(xs(y) - mx); if (d < bd){ bd = d; bi = i; } });
    const yr = years[bi], X = xs(yr);
    cross.setAttribute('x1', X); cross.setAttribute('x2', X); cross.setAttribute('opacity', 1);

    const gv = (s.countries[EL] || [])[bi], ev2 = s.eu[bi];
    if (gv !== null && gv !== undefined){ dotG.setAttribute('cx',X); dotG.setAttribute('cy',ys(gv)); dotG.setAttribute('opacity',1);} else dotG.setAttribute('opacity',0);
    if (ev2 !== null && ev2 !== undefined){ dotE.setAttribute('cx',X); dotE.setAttribute('cy',ys(ev2)); dotE.setAttribute('opacity',1);} else dotE.setAttribute('opacity',0);

    // nearest other country to the cursor
    let nc = null, nd = Infinity, nv = null;
    codes.forEach(c => { const v = s.countries[c][bi]; if (v === null || v === undefined) return;
      const d = Math.abs(ys(v) - my); if (d < nd){ nd = d; nc = c; nv = v; } });
    clearHl();
    if (nc && nd < 22){
      const p = svg.querySelector(`path[data-c="${nc}"]`);
      if (p){ p.style.stroke = cssv('--hi');
        p.style.strokeWidth = '2.2'; p.style.opacity = '1'; hlPath = p; }
      dotN.setAttribute('cx',X); dotN.setAttribute('cy',ys(nv)); dotN.setAttribute('opacity',1);
    } else { dotN.setAttribute('opacity',0); nc = null; }

    let h = `<div class="y">${yr}</div>`;
    h += `<div class="r"><span class="sw" style="background:var(--gr)"></span>Greece<span class="v">${fmt(gv,s.unit)}</span></div>`;
    h += `<div class="r"><span class="sw" style="background:var(--eu)"></span>EU<span class="v">${fmt(ev2,s.unit)}</span></div>`;
    if (nc) h += `<div class="r"><span class="sw" style="background:var(--hi)"></span>${NAMES[nc]||nc}<span class="v">${fmt(nv,s.unit)}</span></div>`;
    tip.innerHTML = h;
    tip.style.left = (X / W * 100) + '%';
    tip.style.top = '4px';
    tip.style.opacity = 1;
  }
  hit.addEventListener('mousemove', move);
  hit.addEventListener('mouseleave', () => {
    cross.setAttribute('opacity',0); tip.style.opacity = 0;
    [dotG,dotE,dotN].forEach(d=>d.setAttribute('opacity',0));
    clearHl();
  });
}
</script>
"""


JS_PANELS = """
<script>
const PANELS = __PANELS__;
const PAL = ['#2a78d6','#eb6834','#1baf7a','#eda100','#4a3aa7','#d03b3b',
             '#0f8b8d','#a0522d','#6a5acd','#c2185b'];

function drawPanel(host, key, p){
  if (p.kind === 'bars') return drawBars(host, key, p);
  if (p.kind === 'ladder') return drawLadder(host, p);
  if (p.kind === 'position_ladder') return drawPositionLadder(host, p);
  if (p.kind === 'candidate') return drawCandidate(host, p);
  if (p.kind === 'selection') return drawSelection(host, p);
  if (p.kind === 'partial') return drawPartial(host, p);
  if (p.kind === 'dumbbell') return drawDumbbell(host, p);
  if (p.kind === 'heatmap') return drawHeatmap(host, p);
  if (p.kind === 'heatmap_big') return drawHeatmapBig(host, p);
  const W=860,H=320,padL=52,padR=250,padT=14,padB=30;
  const plotW=W-padL-padR, plotH=H-padT-padB, years=p.years;
  const xs=y=>padL+(years.length===1?plotW/2:(y-years[0])/(years[years.length-1]-years[0])*plotW);
  let lo=Infinity,hi=-Infinity;
  p.lines.forEach(l=>l.values.forEach(v=>{if(v!==null){if(v<lo)lo=v;if(v>hi)hi=v;}}));
  if(!isFinite(lo)){lo=0;hi=1;}
  const pd=(hi-lo)*0.08||1;
  lo = lo < 0 ? lo - pd : Math.max(0, lo - pd);
  hi += pd;
  const ys=v=>padT+plotH-(v-lo)/(hi-lo)*plotH;
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`); svg.setAttribute('class','chart');
  const el=(t,a)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};
  for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4,y=ys(v);
    svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:y,y2:y,class:'gridline'}));
    const t=el('text',{x:padL-7,y:y+3.5,'text-anchor':'end',class:'axis-label'});
    t.textContent=fmt(v,p.unit); svg.appendChild(t);}
  const step=Math.max(1,Math.ceil(years.length/8));
  years.forEach((y,i)=>{if(i%step&&i!==years.length-1)return;
    const t=el('text',{x:xs(y),y:H-padB+16,'text-anchor':'middle',class:'axis-label'});
    t.textContent=y; svg.appendChild(t);});
  const groups=[...new Set(p.lines.map(l=>l.group))];
  p.lines.forEach(l=>{
    const col=PAL[groups.indexOf(l.group)%PAL.length];
    let d='',pen=false;
    l.values.forEach((v,i)=>{if(v===null){pen=false;return;}
      d+=(pen?' L ':' M ')+xs(years[i])+','+ys(v); pen=true;});
    if(!d)return;
    const path=el('path',{d:d,fill:'none',stroke:col,
      'stroke-width':l.highlight?2.6:1.8,'stroke-linejoin':'round',
      'stroke-dasharray':l.style==='dashed'?'6 4':(l.style==='dotted'?'2 3':'none'),
      opacity:l.highlight?1:.85});
    path.dataset.group=l.group; path.dataset.baseOpacity=l.highlight?1:.85;
    svg.appendChild(path);
  });
  // legend to the right
  let ly=padT+4;
  p.lines.forEach(l=>{
    const col=PAL[groups.indexOf(l.group)%PAL.length];
    svg.appendChild(el('line',{x1:W-padR+12,x2:W-padR+34,y1:ly,y2:ly,stroke:col,
      'stroke-width':l.highlight?2.6:1.8,
      'stroke-dasharray':l.style==='dashed'?'6 4':(l.style==='dotted'?'2 3':'none')}));
    const t=el('text',{x:W-padR+40,y:ly+3.5,class:'axis-label',
      style:l.highlight?'font-weight:700':''});
    t.textContent=l.name; svg.appendChild(t); ly+=17;
  });
  const cross=el('line',{class:'crosshair',y1:padT,y2:padT+plotH}); svg.appendChild(cross);
  const tip=document.createElement('div'); tip.className='tip';
  const wrap=document.createElement('div'); wrap.className='chart-wrap';
  wrap.appendChild(svg); wrap.appendChild(tip); host.appendChild(wrap);
  const hit=el('rect',{x:padL,y:padT,width:plotW,height:plotH,class:'hit'}); svg.appendChild(hit);
  // When a panel pairs several lines per group (each age band or tenure drawn
  // for Greece and for the EU), listing all ten in the tooltip buries the two
  // the cursor is actually on. In that case show only the nearest group and dim
  // the rest. Panels where every line is its own group keep the full readout.
  const groupHover = p.lines.length > groups.length;
  const dim=g=>svg.querySelectorAll('path[data-group]').forEach(pa=>{
    pa.style.opacity = (g===null||pa.dataset.group===g) ? pa.dataset.baseOpacity : .12;});
  hit.addEventListener('mousemove',ev=>{
    const r=svg.getBoundingClientRect(); const mx=(ev.clientX-r.left)/r.width*W;
    const my=(ev.clientY-r.top)/r.height*H;
    let bi=0,bd=Infinity;
    years.forEach((y,i)=>{const d=Math.abs(xs(y)-mx);if(d<bd){bd=d;bi=i;}});
    const X=xs(years[bi]);
    cross.setAttribute('x1',X);cross.setAttribute('x2',X);cross.setAttribute('opacity',1);
    let shown=p.lines, hg=null;
    if(groupHover){
      let nd=Infinity;
      p.lines.forEach(l=>{const v=l.values[bi]; if(v===null||v===undefined)return;
        const d=Math.abs(ys(v)-my); if(d<nd){nd=d; hg=l.group;}});
      if(hg!==null) shown=p.lines.filter(l=>l.group===hg);
      dim(hg);
    }
    let h=`<div class="y">${years[bi]}${hg?' &middot; '+hg:''}</div>`;
    shown.forEach(l=>{const col=PAL[groups.indexOf(l.group)%PAL.length];
      h+=`<div class="r"><span class="sw" style="background:${col}"></span>${l.name}<span class="v">${fmt(l.values[bi],p.unit)}</span></div>`;});
    tip.innerHTML=h; tip.style.left=(X/W*100)+'%'; tip.style.top='4px'; tip.style.opacity=1;
  });
  hit.addEventListener('mouseleave',()=>{cross.setAttribute('opacity',0);tip.style.opacity=0;
    if(groupHover) dim(null);});
}

function drawBars(host,key,p){
  const rows=p.rows, W=860, rowH=30, H=rows.length*rowH+46, padL=290, padR=70;
  const plotW=W-padL-padR;
  const vals=rows.flatMap(r=>[r.oos,r.insample]).filter(v=>v!==null);
  const lo=Math.min(0,...vals), hi=Math.max(...vals);
  const xs=v=>padL+(v-lo)/(hi-lo)*plotW;
  const {svg,el,hover,rowHit,row}=panelSvg(host,W,H);
  svg.appendChild(el('line',{x1:xs(0),x2:xs(0),y1:10,y2:H-36,class:'gridline'}));
  rows.forEach((r,i)=>{
    const y=16+i*rowH;
    hover(rowHit(y-2,rowH),()=>`<div class="y">${r.pretty||r.label||r.model}</div>`
      +row('out-of-sample gap',r.oos.toFixed(1)+' pp')
      +(r.insample===null||r.insample===undefined?'':row('in-sample gap',r.insample.toFixed(1)+' pp'))
      +(r.r2===null||r.r2===undefined?'':row('R&sup2;',r.r2)));
    const t=el('text',{x:padL-10,y:y+13,'text-anchor':'end',class:'axis-label',
      style:'font-size:11.5px'});
    t.textContent=r.pretty||r.model; svg.appendChild(t);
    const x0=xs(Math.min(0,r.oos)), w=Math.abs(xs(r.oos)-xs(0));
    svg.appendChild(el('rect',{x:x0,y:y+3,width:Math.max(w,1),height:11,
      fill:'var(--gr)',rx:2,opacity:.9}));
    if(r.insample!==null){
      const xi0=xs(Math.min(0,r.insample)), wi=Math.abs(xs(r.insample)-xs(0));
      svg.appendChild(el('rect',{x:xi0,y:y+16,width:Math.max(wi,1),height:8,
        fill:'none',stroke:'var(--eu)','stroke-width':1.4,'stroke-dasharray':'3 2',rx:2}));
    }
    // Put the value at the bar's outer end, but never let a negative bar's label
    // run back into the model-name column.
    let vx=xs(r.oos)+(r.oos>=0?6:-6), anchor=r.oos>=0?'start':'end';
    if(vx<padL+4){ vx=xs(Math.max(r.oos,0))+6; anchor='start'; }
    const v=el('text',{x:vx,y:y+13,class:'axis-label',
      'text-anchor':anchor,style:'font-weight:650;fill:var(--gr)'});
    v.textContent=r.oos.toFixed(1); svg.appendChild(v);
  });
  const lab=el('text',{x:xs(0),y:H-14,'text-anchor':'middle',class:'axis-label'});
  lab.textContent="Greece's average residual, percentage points (0 = predicted exactly)";
  svg.appendChild(lab);
}

function panelSvg(host,W,H){
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`); svg.setAttribute('class','chart');
  // The diagnostics used to append the bare svg, which left them with nowhere to
  // put a tooltip -- every one of them was inert. They now get the same wrap+tip
  // the line charts use, plus hover() to bind a target to its readout.
  const wrap=document.createElement('div'); wrap.className='chart-wrap';
  const tip=document.createElement('div'); tip.className='tip';
  wrap.appendChild(svg); wrap.appendChild(tip); host.appendChild(wrap);
  const el=(t,a={})=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};
  const hover=(node,html)=>{
    node.style.cursor='crosshair';
    node.addEventListener('mousemove',ev=>{
      const rc=svg.getBoundingClientRect();
      tip.innerHTML=typeof html==='function'?html():html;
      tip.style.left=Math.min(72,Math.max(4,(ev.clientX-rc.left)/rc.width*100))+'%';
      tip.style.top=Math.max(2,(ev.clientY-rc.top)/rc.height*100-8)+'%';
      tip.style.opacity=1;
    });
    node.addEventListener('mouseleave',()=>{tip.style.opacity=0;});
  };
  // full-width invisible band for row-per-record charts
  const rowHit=(y,h)=>{const r=el('rect',{x:0,y:y,width:W,height:h,fill:'transparent',class:'hit'});
    svg.appendChild(r); return r;};
  const row=(n,v)=>`<div class="r">${n}<span class="v">${v}</span></div>`;
  return {svg,el,tip,hover,rowHit,row};
}

function drawLadder(host,p){
  const rows=p.rows,W=860,rowH=37,H=rows.length*rowH+52,padL=315,padR=70;
  const {svg,el,hover,rowHit,row}=panelSvg(host,W,H), vals=rows.map(r=>+r.greece_value);
  const lo=Math.min(-2,...vals),hi=Math.max(...vals),X=v=>padL+(v-lo)/(hi-lo)*(W-padL-padR);
  svg.appendChild(el('line',{x1:X(0),x2:X(0),y1:12,y2:H-35,class:'gridline'}));
  rows.forEach((r,i)=>{const v=+r.greece_value,y=12+i*rowH;
    hover(rowHit(y-rowH/2,rowH),()=>`<div class="y">${r.layer}</div>`
      +row('step',r.step)
      +row('evidence type',r.type)
      +row("Greece's value",(+r.greece_value).toFixed(2)+' pp')
      +(r.points_closed===null||r.points_closed===undefined?''
        :row('closed so far',(+r.points_closed).toFixed(2)+' pp')));
    const label=el('text',{x:padL-10,y:y+15,'text-anchor':'end',class:'axis-label',style:'font-size:11.5px'});
    label.textContent=r.step_label||r.layer||r.step;svg.appendChild(label);
    const x0=X(Math.min(0,v)),w=Math.abs(X(v)-X(0));
    svg.appendChild(el('rect',{x:x0,y:y+3,width:Math.max(1,w),height:17,rx:3,
      fill:v<0?'var(--hi)':'var(--gr)',opacity:.9}));
    const t=el('text',{x:X(v)+(v>=0?7:-7),y:y+16,'text-anchor':v>=0?'start':'end',
      class:'axis-label',style:'font-weight:700'});t.textContent=v.toFixed(1);svg.appendChild(t);
  });
  const axis=el('text',{x:padL+(W-padL-padR)/2,y:H-12,'text-anchor':'middle',class:'axis-label'});
  axis.textContent='Greece gap or out-of-sample residual (percentage points)';svg.appendChild(axis);
}

function drawPositionLadder(host,p){
  const rows=p.rows,rowH=27,padL=326,padR=54,padT=34,padB=34,spanW=62;
  const W=860,H=rows.length*rowH+padT+padB,plotW=W-padL-padR,X=v=>padL+v/100*plotW;
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.setAttribute('class','chart');
  const el=(t,a)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};

  svg.appendChild(el('rect',{x:X(80),y:padT-8,width:X(100)-X(80),height:H-padT-padB+14,
    fill:cssv('--gr'),opacity:.10}));
  const band=el('text',{x:X(90),y:padT-14,'text-anchor':'middle',class:'axis-label'});
  band.textContent="EU's worst fifth";svg.appendChild(band);
  [0,25,50,75,100].forEach(v=>{
    svg.appendChild(el('line',{x1:X(v),x2:X(v),y1:padT-8,y2:H-padB+6,
      stroke:cssv('--gridline'),'stroke-width':1}));
    const t=el('text',{x:X(v),y:H-padB+20,'text-anchor':'middle',class:'axis-label'});
    t.textContent=v;svg.appendChild(t);
  });
  const axis=el('text',{x:padL+plotW/2,y:H-8,'text-anchor':'middle',class:'axis-label'});
  axis.textContent='Position in the EU distribution — 0 = best, 100 = worst';svg.appendChild(axis);

  const tip=document.createElement('div');tip.className='tip';
  const wrap=document.createElement('div');wrap.className='chart-wrap';
  rows.forEach((r,i)=>{
    const y=padT+i*rowH+rowH/2,worse=r.pct_last>=r.pct_first;
    const col=worse?cssv('--eu'):cssv('--hi');
    const hit=el('rect',{x:0,y:y-rowH/2,width:W,height:rowH,fill:'transparent',class:'hit'});
    svg.appendChild(hit);
    const lab=el('text',{x:padL-spanW-10,y:y+4,'text-anchor':'end',class:'axis-label'});
    const maxch=Math.floor((padL-spanW-10)/5.4);
    lab.textContent=r.label.length>maxch?r.label.slice(0,maxch-1)+'…':r.label;svg.appendChild(lab);
    const span=el('text',{x:padL-10,y:y+4,'text-anchor':'end',class:'axis-label',opacity:.62});
    span.textContent=`${r.year_first}–${r.year_last}`;svg.appendChild(span);
    svg.appendChild(el('line',{x1:X(r.pct_first),x2:X(r.pct_last),y1:y,y2:y,
      stroke:col,'stroke-width':2.4,opacity:.55,'stroke-linecap':'round'}));
    if(r.eu_pct!==null&&r.eu_pct!==undefined){
      const d=6,ex=X(r.eu_pct);
      svg.appendChild(el('path',{d:`M ${ex} ${y-d} L ${ex+d} ${y} L ${ex} ${y+d} L ${ex-d} ${y} Z`,
        fill:cssv('--page'),stroke:cssv('--text-muted'),'stroke-width':1.6}));
    }
    svg.appendChild(el('circle',{cx:X(r.pct_first),cy:y,r:5,fill:cssv('--page'),stroke:col,'stroke-width':2}));
    svg.appendChild(el('circle',{cx:X(r.pct_last),cy:y,r:5.5,fill:col}));
    const fmtv=v=>v===null||v===undefined?'—':(Math.abs(v)>=1000?v.toLocaleString():v);
    hit.addEventListener('mousemove',ev=>{
      const rc=svg.getBoundingClientRect();
      tip.innerHTML=`<div class="y">${r.label}</div>`
        +`<div class="r">${r.year_first}<span class="v">${fmtv(r.val_first)} ${r.unit}</span></div>`
        +`<div class="r">${r.year_last}<span class="v">${fmtv(r.val_last)} ${r.unit}</span></div>`
        +`<div class="r">EU ${r.year_last}<span class="v">${fmtv(r.eu_last)} ${r.unit}</span></div>`
        +`<div class="r" style="opacity:.7">Greece position<span class="v">`
        +`${Math.round(r.pct_first)} → ${Math.round(r.pct_last)}</span></div>`;
      tip.style.left=Math.min(78,Math.max(12,(ev.clientX-rc.left)/rc.width*100))+'%';
      tip.style.top=(y/H*100)+'%';tip.style.opacity=1;
    });
    hit.addEventListener('mouseleave',()=>{tip.style.opacity=0;});
  });
  const ly=padT-14;
  [[padL+8,'earliest','open'],[padL+86,'latest','solid'],[padL+150,'EU','diamond']].forEach(([x,label,kind])=>{
    if(kind==='diamond'){const d=6;svg.appendChild(el('path',{d:`M ${x} ${ly-10} L ${x+d} ${ly-4} L ${x} ${ly+2} L ${x-d} ${ly-4} Z`,fill:cssv('--page'),stroke:cssv('--text-muted'),'stroke-width':1.6}));}
    else svg.appendChild(el('circle',{cx:x,cy:ly-4,r:5,fill:kind==='open'?cssv('--page'):cssv('--text-muted'),stroke:cssv('--text-muted'),'stroke-width':kind==='open'?2:0}));
    const t=el('text',{x:x+10,y:ly,class:'axis-label'});t.textContent=label;svg.appendChild(t);
  });
  wrap.appendChild(svg);wrap.appendChild(tip);host.appendChild(wrap);
}

function drawCandidate(host,p){
  const rows=[...p.rows].sort((a,b)=>a.p_fdr_bh-b.p_fdr_bh),W=860,rowH=25,H=rows.length*rowH+58,padL=285,padR=55;
  const {svg,el,hover,rowHit,row}=panelSvg(host,W,H),max=Math.max(2.2,...rows.map(r=>-Math.log10(Math.max(r.p_fdr_bh,1e-8))));
  const X=v=>padL+v/max*(W-padL-padR),cut=-Math.log10(.05);
  svg.appendChild(el('line',{x1:X(cut),x2:X(cut),y1:8,y2:H-36,stroke:'var(--eu)',
    'stroke-width':1.3,'stroke-dasharray':'5 4'}));
  rows.forEach((r,i)=>{const y=12+i*rowH,x=-Math.log10(Math.max(r.p_fdr_bh,1e-8));
    hover(rowHit(y-4,rowH),()=>`<div class="y">${r.pretty||r.variable}</div>`
      +row('raw p',r.p_raw<1e-4?r.p_raw.toExponential(2):r.p_raw.toFixed(4))
      +row('BH-adjusted q',r.p_fdr_bh.toFixed(4))
      +row('survives FDR 5%',r.significant_after_fdr?'yes':'no')
      +row('coefficient',r.coef)
      +row("Greece's OOS gap",r.gr_oos));
    const lab=el('text',{x:padL-9,y:y+10,'text-anchor':'end',class:'axis-label',style:'font-size:10.5px'});
    lab.textContent=r.pretty||r.variable;svg.appendChild(lab);
    svg.appendChild(el('line',{x1:padL,x2:X(x),y1:y+6,y2:y+6,stroke:'var(--gridline)','stroke-width':2}));
    svg.appendChild(el('circle',{cx:X(x),cy:y+6,r:5,fill:r.p_fdr_bh<=.05?'var(--gr)':'var(--faint)'}));
    const q=el('text',{x:X(x)+8,y:y+10,class:'axis-label',style:'font-size:10px'});
    q.textContent='q='+r.p_fdr_bh.toFixed(r.p_fdr_bh<.01?4:3);svg.appendChild(q);
  });
  const a=el('text',{x:padL+(W-padL-padR)/2,y:H-12,'text-anchor':'middle',class:'axis-label'});
  a.textContent='Stronger evidence  →  −log10(BH-adjusted p-value)';svg.appendChild(a);
}

function drawSelection(host,p){
  const rows=p.rows,W=860,H=rows.length*42+48,padL=330,padR=70;
  const {svg,el,hover,rowHit,row}=panelSvg(host,W,H),X=v=>padL+v/27*(W-padL-padR);
  rows.forEach((r,i)=>{const y=14+i*42;
    hover(rowHit(y,40),()=>`<div class="y">${r.pretty||r.variable}</div>`
      +row('selected first in',`${r.count} of 27 folds`)
      +row('share of folds',`${(r.count/27*100).toFixed(0)}%`));
    const lab=el('text',{x:padL-10,y:y+15,'text-anchor':'end',class:'axis-label'});
    lab.textContent=r.pretty||r.variable;svg.appendChild(lab);
    svg.appendChild(el('rect',{x:padL,y:y+3,width:X(r.count)-padL,height:18,rx:3,fill:'var(--gr)'}));
    const t=el('text',{x:X(r.count)+8,y:y+17,class:'axis-label',style:'font-weight:700'});
    t.textContent=r.count+' of 27 folds';svg.appendChild(t);
  });
}

function drawPartial(host,p){
  const W=860,H=430,L=65,R=25,T=20,B=55,{svg,el,hover,row}=panelSvg(host,W,H),pts=p.points;
  let xs=pts.map(d=>d.x_resid),ys=pts.map(d=>d.y_resid),xl=Math.min(...xs),xh=Math.max(...xs),yl=Math.min(...ys),yh=Math.max(...ys);
  const px=(xh-xl)*.08||1,py=(yh-yl)*.08||1;xl-=px;xh+=px;yl-=py;yh+=py;
  const X=v=>L+(v-xl)/(xh-xl)*(W-L-R),Y=v=>T+(yh-v)/(yh-yl)*(H-T-B);
  svg.appendChild(el('line',{x1:X(0),x2:X(0),y1:T,y2:H-B,class:'gridline'}));
  svg.appendChild(el('line',{x1:L,x2:W-R,y1:Y(0),y2:Y(0),class:'gridline'}));
  svg.appendChild(el('line',{x1:X(xl),x2:X(xh),y1:Y(p.coef*xl),y2:Y(p.coef*xh),
    stroke:'var(--hi)','stroke-width':2}));
  pts.forEach(d=>{const gr=d.geo==='EL';
    const c=el('circle',{cx:X(d.x_resid),cy:Y(d.y_resid),r:gr?6:3.5,
      fill:gr?'var(--gr)':'var(--faint)',opacity:gr?1:.55});
    svg.appendChild(c);
    hover(c,()=>`<div class="y">${NAMES[d.geo]||d.geo} ${d.time}</div>`
      +row('accumulated unemployment',d.x_resid.toFixed(2))
      +row('subjective poverty',d.y_resid.toFixed(2))
      +`<div class="r" style="opacity:.7">both residualised on the C-LTU controls</div>`);});
  const title=el('text',{x:W-R,y:T+12,'text-anchor':'end',class:'axis-label',style:'font-weight:700'});
  title.textContent=`coefficient ${p.coef.toFixed(3)} · p ${p.p.toFixed(4)}`;svg.appendChild(title);
  const xlab=el('text',{x:L+(W-L-R)/2,y:H-12,'text-anchor':'middle',class:'axis-label'});
  xlab.textContent='Accumulated unemployment after removing C-LTU controls';svg.appendChild(xlab);
}

function drawDumbbell(host,p){
  const rows=[...p.rows].sort((a,b)=>b.nested-b.nested),W=860,rowH=22,H=rows.length*rowH+50,L=95,R=55;
  const {svg,el,hover,rowHit,row}=panelSvg(host,W,H),vals=rows.flatMap(r=>[r.baseline,r.nested]),lo=Math.min(-5,...vals),hi=Math.max(15,...vals);
  const X=v=>L+(v-lo)/(hi-lo)*(W-L-R);
  svg.appendChild(el('line',{x1:X(0),x2:X(0),y1:8,y2:H-34,stroke:'var(--hi)','stroke-dasharray':'4 4'}));
  rows.forEach((r,i)=>{const y=12+i*rowH,gr=r.geo==='EL';
    hover(rowHit(y-rowH/2,rowH),()=>`<div class="y">${NAMES[r.geo]||r.geo}</div>`
      +row('C-LTU residual',r.baseline.toFixed(2)+' pp')
      +row('nested selection',r.nested.toFixed(2)+' pp')
      +row('change',(r.nested-r.baseline>=0?'+':'')+(r.nested-r.baseline).toFixed(2)+' pp'));
    const lab=el('text',{x:L-8,y:y+4,'text-anchor':'end',class:'axis-label',style:gr?'font-weight:700;fill:var(--gr)':'font-size:10px'});
    lab.textContent=gr?'Greece':r.geo;svg.appendChild(lab);
    svg.appendChild(el('line',{x1:X(r.baseline),x2:X(r.nested),y1:y,y2:y,stroke:gr?'var(--gr)':'var(--gridline)','stroke-width':gr?2.5:1.5}));
    svg.appendChild(el('circle',{cx:X(r.baseline),cy:y,r:4,fill:'var(--eu)'}));
    svg.appendChild(el('circle',{cx:X(r.nested),cy:y,r:4.5,fill:gr?'var(--gr)':'var(--hi)'}));
  });
  const a=el('text',{x:L+(W-L-R)/2,y:H-10,'text-anchor':'middle',class:'axis-label'});
  a.textContent='Country out-of-sample residual (pp): orange C-LTU → green nested selection';svg.appendChild(a);
}

function drawHeatmapBig(host,p){
  const labels=p.labels,n=labels.length;
  // 37 variables in 860px: cells land near 17px, too small for printed numbers,
  // so this one is colour + hover only. Family dividers carry the structure.
  const L=232,T=150,R=14,B=14,cell=Math.min(30,(860-L-R)/n);
  const W=860,H=T+n*cell+B;
  const {svg,el,hover,row}=panelSvg(host,W,H);
  labels.forEach((lab,i)=>{
    const cx=L+i*cell+cell/2;
    const tx=el('text',{x:cx,y:T-6,'text-anchor':'start',class:'axis-label',
      transform:`rotate(-55 ${cx} ${T-6})`,style:'font-size:8.5px'});
    tx.textContent=lab.length>26?lab.slice(0,25)+'…':lab; svg.appendChild(tx);
    const ty=el('text',{x:L-6,y:T+i*cell+cell*0.68,'text-anchor':'end',class:'axis-label',
      style:'font-size:8.5px'});
    ty.textContent=lab.length>34?lab.slice(0,33)+'…':lab; svg.appendChild(ty);
  });
  p.values.forEach((rowVals,i)=>rowVals.forEach((v,j)=>{
    const a=Math.abs(v);
    const col = i===j ? 'var(--gridline)'
              : (v>=0?`rgba(42,120,214,${0.10+0.80*a})`:`rgba(235,104,52,${0.10+0.80*a})`);
    const c=el('rect',{x:L+j*cell,y:T+i*cell,width:cell-0.5,height:cell-0.5,fill:col});
    svg.appendChild(c);
    if(i!==j) hover(c,()=>`<div class="y">${labels[i]}<br>&times; ${labels[j]}</div>`
      +row('correlation',v.toFixed(3))
      +row('shared variance',(v*v*100).toFixed(0)+'%')
      +row('direction',v>=0?'same direction':'opposite direction'));
  }));
  // family dividers + block labels
  (p.bounds||[]).forEach(b=>{
    const x=L+b*cell, y=T+b*cell;
    svg.appendChild(el('line',{x1:x,x2:x,y1:T,y2:T+n*cell,stroke:'var(--text-primary)','stroke-width':1.1,opacity:.55}));
    svg.appendChild(el('line',{x1:L,x2:L+n*cell,y1:y,y2:y,stroke:'var(--text-primary)','stroke-width':1.1,opacity:.55}));
  });
  (p.blocks||[]).forEach(b=>{
    const y=T+(b.start+b.n/2)*cell;
    const t=el('text',{x:12,y:y,class:'axis-label',
      style:'font-size:9px;font-weight:700;fill:var(--text-secondary)'});
    t.textContent=b.name.split(' - ')[0]; svg.appendChild(t);
  });
}

function drawHeatmap(host,p){
  const labels=p.labels,n=labels.length,W=860,H=620,L=190,T=95,cell=Math.min(52,(W-L-30)/n),{svg,el,hover,row}=panelSvg(host,W,H);
  labels.forEach((lab,i)=>{const tx=el('text',{x:L+i*cell+cell/2,y:T-8,'text-anchor':'start',class:'axis-label',
    transform:`rotate(-45 ${L+i*cell+cell/2} ${T-8})`,style:'font-size:10px'});tx.textContent=lab;svg.appendChild(tx);
    const ty=el('text',{x:L-8,y:T+i*cell+cell*.65,'text-anchor':'end',class:'axis-label',style:'font-size:10px'});ty.textContent=lab;svg.appendChild(ty);});
  // NB: name this rowVals, not row -- panelSvg's row() helper is in scope here
  p.values.forEach((rowVals,i)=>rowVals.forEach((v,j)=>{const a=Math.abs(v),col=v>=0?`rgba(42,120,214,${.12+.78*a})`:`rgba(235,104,52,${.12+.78*a})`;
    const cr=el('rect',{x:L+j*cell,y:T+i*cell,width:cell-1,height:cell-1,fill:col});
    svg.appendChild(cr);
    hover(cr,()=>`<div class="y">${labels[i]} &times; ${labels[j]}</div>`
      +row('correlation',v.toFixed(3))
      +row('shared variance',(v*v*100).toFixed(0)+'%')
      +(i===j?'<div class="r" style="opacity:.7">a variable with itself</div>':''));
    const t=el('text',{x:L+j*cell+cell/2,y:T+i*cell+cell*.62,'text-anchor':'middle',class:'axis-label',style:'font-size:9px;fill:var(--text-primary)'});
    t.textContent=v.toFixed(2);svg.appendChild(t);}));
}
</script>
"""


JS_SCATTER = """
<script>
const SCATTERS = __SCATTERS__;

function drawScatter(host, key, sc){
  const W=860,H=430,padL=62,padR=26,padT=18,padB=52;
  const plotW=W-padL-padR, plotH=H-padT-padB;
  const xs_=sc.points.map(p=>p.x), ys_=sc.points.map(p=>p.y);
  let xlo=Math.min(...xs_), xhi=Math.max(...xs_);
  let ylo=Math.min(...ys_), yhi=Math.max(...ys_);
  if(sc.eu_x!==null){xlo=Math.min(xlo,sc.eu_x);xhi=Math.max(xhi,sc.eu_x);}
  if(sc.eu_y!==null){ylo=Math.min(ylo,sc.eu_y);yhi=Math.max(yhi,sc.eu_y);}
  const px=(xhi-xlo)*0.10||1, py=(yhi-ylo)*0.10||1;
  xlo=xlo<0?xlo-px:Math.max(0,xlo-px); xhi+=px;
  ylo=ylo<0?ylo-py:Math.max(0,ylo-py); yhi+=py;
  const X=v=>padL+(v-xlo)/(xhi-xlo)*plotW;
  const Y=v=>padT+plotH-(v-ylo)/(yhi-ylo)*plotH;

  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`); svg.setAttribute('class','chart');
  const el=(t,a)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};

  for(let i=0;i<=4;i++){
    const v=ylo+(yhi-ylo)*i/4, y=Y(v);
    svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:y,y2:y,class:'gridline'}));
    const t=el('text',{x:padL-8,y:y+3.5,'text-anchor':'end',class:'axis-label'});
    t.textContent=fmt(v,sc.y_unit); svg.appendChild(t);
    const v2=xlo+(xhi-xlo)*i/4, x=X(v2);
    const t2=el('text',{x:x,y:H-padB+16,'text-anchor':'middle',class:'axis-label'});
    t2.textContent=fmt(v2,sc.x_unit); svg.appendChild(t2);
  }
  // EU reference lines split the plot into quadrants relative to the EU value
  if(sc.eu_x!==null){
    svg.appendChild(el('line',{x1:X(sc.eu_x),x2:X(sc.eu_x),y1:padT,y2:padT+plotH,
      stroke:'var(--eu)','stroke-width':1,'stroke-dasharray':'5 4',opacity:.65}));}
  if(sc.eu_y!==null){
    svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:Y(sc.eu_y),y2:Y(sc.eu_y),
      stroke:'var(--eu)','stroke-width':1,'stroke-dasharray':'5 4',opacity:.65}));}

  // Fit the descriptive cross-country line on the 26 peers, leaving Greece
  // out so the line shows what the comparison countries alone would predict.
  const peers=sc.points.filter(p=>p.geo!=='EL');
  if(peers.length>2){
    const mx=peers.reduce((s,p)=>s+p.x,0)/peers.length;
    const my=peers.reduce((s,p)=>s+p.y,0)/peers.length;
    const den=peers.reduce((s,p)=>s+(p.x-mx)*(p.x-mx),0);
    const slope=den?peers.reduce((s,p)=>s+(p.x-mx)*(p.y-my),0)/den:0;
    const intercept=my-slope*mx;
    svg.appendChild(el('line',{x1:X(xlo),x2:X(xhi),y1:Y(intercept+slope*xlo),
      y2:Y(intercept+slope*xhi),stroke:'var(--hi)','stroke-width':1.6,
      'stroke-dasharray':'7 4',opacity:.8}));
  }

  sc.points.forEach(p=>{
    const isGR=p.geo==='EL';
    const c=el('circle',{cx:X(p.x),cy:Y(p.y),r:isGR?7:4.5,
      fill:isGR?'var(--gr)':'var(--faint)',
      stroke:isGR?'var(--gr)':'none','stroke-width':isGR?2:0,
      opacity:isGR?1:.8,'data-geo':p.geo,style:'cursor:pointer'});
    svg.appendChild(c);
    const lab=el('text',{x:X(p.x)+(isGR?10:6),y:Y(p.y)-(isGR?8:5),class:'axis-label',
      style:isGR?'fill:var(--gr);font-weight:700;font-size:12px':'font-size:9.5px'});
    lab.textContent=isGR?'Greece':p.geo; svg.appendChild(lab);
  });
  if(sc.eu_x!==null&&sc.eu_y!==null){
    svg.appendChild(el('path',{d:`M ${X(sc.eu_x)-6},${Y(sc.eu_y)} L ${X(sc.eu_x)},${Y(sc.eu_y)-6} `+
      `L ${X(sc.eu_x)+6},${Y(sc.eu_y)} L ${X(sc.eu_x)},${Y(sc.eu_y)+6} Z`,
      fill:'var(--eu)',stroke:'none'}));
    const t=el('text',{x:X(sc.eu_x)+10,y:Y(sc.eu_y)+14,class:'axis-label',
      style:'fill:var(--eu);font-weight:650'}); t.textContent='EU'; svg.appendChild(t);
  }
  // axis titles
  const xt=el('text',{x:padL+plotW/2,y:H-10,'text-anchor':'middle',class:'axis-label',
    style:'font-size:11.5px'});
  xt.textContent=sc.x_label+' ('+sc.x_unit+') \u2192'; svg.appendChild(xt);
  const yt=el('text',{x:14,y:padT+plotH/2,'text-anchor':'middle',class:'axis-label',
    style:'font-size:11.5px',transform:`rotate(-90 14 ${padT+plotH/2})`});
  yt.textContent=sc.y_label+' ('+sc.y_unit+') \u2192'; svg.appendChild(yt);
  if(sc.r!==null){
    const rt=el('text',{x:W-padR-4,y:padT+12,'text-anchor':'end',class:'axis-label',
      style:'font-size:11.5px;font-weight:650'});
    rt.textContent='r = '+sc.r.toFixed(2)+'  ·  '+sc.points.length+' countries  ·  '+sc.year;
    svg.appendChild(rt);
  }

  const tip=document.createElement('div'); tip.className='tip';
  const wrap=document.createElement('div'); wrap.className='chart-wrap';
  wrap.appendChild(svg); wrap.appendChild(tip); host.appendChild(wrap);

  svg.querySelectorAll('circle[data-geo]').forEach(c=>{
    c.addEventListener('mouseenter',()=>{
      const g=c.getAttribute('data-geo');
      const p=sc.points.find(q=>q.geo===g);
      const gr=sc.points.find(q=>q.geo==='EL');
      let h=`<div class="y">${NAMES[g]||g}</div>`;
      h+=`<div class="r">${sc.x_label}<span class="v">${fmt(p.x,sc.x_unit)}</span></div>`;
      h+=`<div class="r">${sc.y_label}<span class="v">${fmt(p.y,sc.y_unit)}</span></div>`;
      if(g!=='EL'&&gr){
        h+=`<div class="r" style="margin-top:5px;padding-top:5px;border-top:1px solid var(--gridline)">`+
           `<span class="sw" style="background:var(--gr)"></span>Greece<span class="v">`+
           `${fmt(gr.x,sc.x_unit)} / ${fmt(gr.y,sc.y_unit)}</span></div>`;
      }
      tip.innerHTML=h;
      tip.style.left=(X(p.x)/W*100)+'%';
      tip.style.top=Math.max(0,(Y(p.y)/H*100))+'%';
      tip.style.opacity=1;
      c.setAttribute('r',g==='EL'?8:6.5);
    });
    c.addEventListener('mouseleave',()=>{
      tip.style.opacity=0;
      c.setAttribute('r',c.getAttribute('data-geo')==='EL'?7:4.5);
    });
  });
}
</script>
"""


COUNTRY_NAMES = {
 "AT":"Austria","BE":"Belgium","BG":"Bulgaria","CY":"Cyprus","CZ":"Czechia","DE":"Germany",
 "DK":"Denmark","EE":"Estonia","EL":"Greece","ES":"Spain","FI":"Finland","FR":"France",
 "HR":"Croatia","HU":"Hungary","IE":"Ireland","IT":"Italy","LT":"Lithuania","LU":"Luxembourg",
 "LV":"Latvia","MT":"Malta","NL":"Netherlands","PL":"Poland","PT":"Portugal","RO":"Romania",
 "SE":"Sweden","SI":"Slovenia","SK":"Slovakia","UK":"United Kingdom","NO":"Norway",
 "CH":"Switzerland","IS":"Iceland","TR":"Türkiye","RS":"Serbia","ME":"Montenegro",
 "MK":"North Macedonia","AL":"Albania","BA":"Bosnia and Herzegovina","XK":"Kosovo",
 "EU27_2020":"EU27","EA19":"Euro area 19","EA20":"Euro area 20","EU28":"EU28","EU":"EU",
}

series, panels = blob["series"], blob["panels"]
scatters = blob.get("scatters", {})

# ---------------------------------------------------------------------------
# V2 enrichments. These use already-produced checkpoint outputs; no model is
# reselected and no published result is changed. The original appendix remains
# available as statistical_appendix.html for direct comparison.
# ---------------------------------------------------------------------------
series["income_pps"]["label"] = "Actual individual consumption (PPS per capita)"
if "income_vs_subjective" in scatters:
    scatters["income_vs_subjective"]["title"] = \
        "Actual individual consumption against reported hardship"
    scatters["income_vs_subjective"]["x_label"] = \
        "Actual individual consumption (PPS per capita)"
    scatters["income_vs_subjective"]["note"] = (
        "Countries with higher actual individual consumption generally report less hardship. "
        "This is a consumption-based welfare measure, not household income; Greece reports far "
        "more hardship than its consumption level alone would predict.")


def cross_section_scatter(xkey, ykey, title, note):
    """Build a latest-common-year scatter from two appendix series."""
    sx, sy = series[xkey], series[ykey]
    common = sorted(set(sx["years"]) & set(sy["years"]), reverse=True)
    for year in common:
        ix, iy = sx["years"].index(year), sy["years"].index(year)
        points = []
        for geo in sorted(set(sx["countries"]) & set(sy["countries"])):
            xv, yv = sx["countries"][geo][ix], sy["countries"][geo][iy]
            if xv is not None and yv is not None:
                points.append({"geo": geo, "x": xv, "y": yv})
        if len(points) >= 20:
            eu_x, eu_y = sx["eu"][ix], sy["eu"][iy]
            r = float(np.corrcoef([p["x"] for p in points], [p["y"] for p in points])[0, 1])
            return dict(title=title, note=note, year=year,
                        x_label=sx["label"], y_label=sy["label"],
                        x_unit=sx["unit"], y_unit=sy["unit"],
                        eu_x=eu_x, eu_y=eu_y,
                        eu_basis_x=sx["eu_basis"], eu_basis_y=sy["eu_basis"],
                        r=r, points=points)
    raise ValueError(f"No common cross-section for {xkey} and {ykey}")


scatters["arope_vs_subjective"] = cross_section_scatter(
    "arope", "subjective_poverty",
    "AROPE against reported hardship",
    "The official broader measure moves closer to reported hardship than AROP does, but Greece "
    "still sits far above countries with a similar AROPE rate. This is the bridge from Part I to "
    "the decomposed hardship models in Part II.")

# The gap ladder is deliberately labelled a sequence: its first two rows are
# raw gaps and its later rows are out-of-sample model residuals.
ladder = pd.read_csv(OUT / "cumulative_hardship_stage2_bridge.csv")
panels["gap_ladder"] = dict(
    label="From the raw AROP gap to the final residual",
    group="Model diagnostics", unit="percentage points", kind="ladder",
    note="A narrative sequence, not a formal decomposition: raw single-country gaps are followed "
         "by cross-country out-of-sample residuals on the common 2015-2024 window.",
    eu_basis="", rows=ladder.to_dict("records"))

# Add the two final estimates omitted from the original scorecard.
score = panels["model_scorecard_bars"]["rows"]
if not any(r.get("model") == "G_fixed" for r in score):
    score.extend([
        dict(model="G_fixed", label="Fixed Model G: C-LTU + cumulative excess unemployment",
             pretty="Fixed Model G: + accumulated unemployment", oos=-0.82,
             insample=-0.06, r2=0.930),
        dict(model="G_nested", label="Nested-selection validation (selection repeated in each fold)",
             pretty="Nested validation: selection inside every fold", oos=2.70,
             insample=None, r2=None),
    ])

# Added-variable plot: residualise both the outcome and cumulative exposure on
# the full C-LTU control set and year fixed effects. This shows the conditional
# association used by Model G rather than another raw cross-country snapshot.
panel_df = pd.read_csv(OUT / "cumulative_hardship_candidate_panel.csv")
controls = ["aic_pps_pc_k", "severe_mat_soc_deprivation", "arop", "ltu_rate",
            "housing_cost_overburden", "arrears", "unexpected_expenses"]
cols = ["geo", "time", "subjective_poverty", "cum_excess_unemployment"] + controls
partial_df = panel_df[cols].dropna().copy()
rhs = " + ".join(controls) + " + C(time)"
partial_df["x_resid"] = smf.ols("cum_excess_unemployment ~ " + rhs,
                                data=partial_df).fit().resid
partial_df["y_resid"] = smf.ols("subjective_poverty ~ " + rhs,
                                data=partial_df).fit().resid
full = smf.ols("subjective_poverty ~ cum_excess_unemployment + " + rhs,
               data=partial_df).fit(cov_type="cluster", cov_kwds={"groups": partial_df["geo"]})
panels["partial_cumulative_unemployment"] = dict(
    label="Conditional contribution of accumulated unemployment",
    group="Model diagnostics", unit="residualised percentage points", kind="partial",
    note="Added-variable plot after removing AROP, consumption, deprivation, LTU, housing, "
         "arrears, unexpected-expense capacity and year effects from both axes. Grey dots are "
         "country-years; blue dots are Greece. Association, not a household-level causal effect.",
    eu_basis="", coef=float(full.params["cum_excess_unemployment"]),
    p=float(full.pvalues["cum_excess_unemployment"]),
    points=partial_df[["geo", "time", "x_resid", "y_resid"]].to_dict("records"))

# Country-level out-of-sample residuals before and after nested selection.
base_resid = pd.read_csv(OUT / "scorecard_loo_C_LTU_swap.csv").rename(
    columns={"avg_residual": "baseline"})[["geo", "baseline"]]
nested_resid = pd.read_csv(OUT / "nested_selection_validation_folds.csv").rename(
    columns={"fold_held_out": "geo", "nested_mean_residual": "nested"})[["geo", "nested"]]
dumb = base_resid.merge(nested_resid, on="geo")
panels["residual_dumbbell"] = dict(
    label="Where each country moves after nested validation",
    group="Model diagnostics", unit="average out-of-sample residual, percentage points",
    kind="dumbbell",
    note="Each line joins the C-LTU residual to the residual from a model whose candidate selection "
         "was repeated inside that country's held-out fold. Zero means predicted exactly.",
    eu_basis="", rows=dumb.to_dict("records"))

# Correlation heatmap for the final model's predictors, so overlap among the
# hardship measures is visible rather than left only to VIF prose.
corr_vars = ["arop", "aic_pps_pc_k", "severe_mat_soc_deprivation", "ltu_rate",
             "housing_cost_overburden", "arrears", "unexpected_expenses",
             "cum_excess_unemployment"]
corr_labels = ["AROP", "AIC (PPS)", "Deprivation", "LTU", "Housing",
               "Arrears", "Unexpected expense", "Accum. unemployment"]
corr = panel_df[corr_vars].corr()
panels["predictor_correlation"] = dict(
    label="How the final predictors overlap",
    group="Model diagnostics", unit="Pearson correlation, country-year panel", kind="heatmap",
    note="High correlation does not make two variables identical, but it warns against reading "
         "their coefficients as isolated causal contributions.", eu_basis="",
    labels=corr_labels, values=corr.values.round(3).tolist())

# The heatmap above is scoped to the final model, which answers "does this
# specification have a collinearity problem". It does not answer the other
# question the screening raises: how much do the 29 screened candidates
# duplicate each other? Families B and C were dismissed largely on redundancy
# (one candidate correlated 0.948 with an already-tested null), and that
# argument should be visible rather than asserted in prose. All three families
# plus the model's own covariates and the outcome go in one matrix, blocked by
# family so the redundancy shows up as structure.
FAMILY_BLOCKS = [
    ("Outcome", ["subjective_poverty"]),
    ("Model C-LTU covariates",
     ["arop", "aic_pps_pc_k", "severe_mat_soc_deprivation", "ltu_rate",
      "housing_cost_overburden", "arrears", "unexpected_expenses"]),
    ("Family A - accumulation & duration (18 screened)", None),   # filled from the FDR file
    ("Family B - direction & standing (5)", None),
    ("Family C - persistence share (6)", None),
]
try:
    allp = pd.read_csv(OUT / "persistence_share_panel.csv")
    famA = pd.read_csv(OUT / "cumulative_hardship_fdr_correction.csv").variable.tolist()
    famB = pd.read_csv(OUT / "direction_persistence_battery.csv").variable.tolist()
    famC = pd.read_csv(OUT / "persistence_share_battery.csv").variable.tolist()
    blocks = [(FAMILY_BLOCKS[0][0], FAMILY_BLOCKS[0][1]),
              (FAMILY_BLOCKS[1][0], FAMILY_BLOCKS[1][1]),
              (FAMILY_BLOCKS[2][0], famA),
              (FAMILY_BLOCKS[3][0], famB),
              (FAMILY_BLOCKS[4][0], famC)]
    order, bounds, blabels = [], [], []
    for name, vs in blocks:
        vs = [v for v in vs if v in allp.columns]
        if not vs:
            continue
        blabels.append(dict(name=name, start=len(order), n=len(vs)))
        order += vs
        bounds.append(len(order))
    pretty = {"subjective_poverty": "SUBJECTIVE POVERTY (outcome)", "arop": "AROP",
              "aic_pps_pc_k": "AIC (PPS)", "severe_mat_soc_deprivation": "Deprivation",
              "ltu_rate": "LTU", "housing_cost_overburden": "Housing",
              "arrears": "Arrears", "unexpected_expenses": "Unexpected expense"}
    labels = [pretty.get(v, v.replace("_", " ")) for v in order]
    cm = allp[order].corr()
    panels["all_candidate_correlation"] = dict(
        label="Every screened candidate against every other",
        group="Model diagnostics", unit="Pearson correlation, country-year panel",
        kind="heatmap_big",
        note=f"All {len(order)} variables the project tested anywhere: the outcome, the seven "
             "Model C-LTU covariates, and the three screening families, blocked by family with "
             "dividing lines. Cells are too small to print numbers at this size, so hover any "
             "cell for the pair, its correlation and the variance they share. The redundancy "
             "that closed families B and C is OFF the diagonal blocks, not inside them: family "
             "B is internally diverse (mean |r| 0.19), but its members pair almost one-to-one "
             "with family C and with family A's wage measures \u2014 years-worst-quintile-wage "
             "against share-worst-real-wage is 0.964, against cumulative wage shortfall 0.948. "
             "Those bright cells spanning the family dividers are the picture of three families "
             "measuring one thing three ways. Read it as description of overlap, not as evidence "
             "about any variable's effect \u2014 correlation among predictors says nothing about "
             "which of them explains the outcome.",
        eu_basis="", labels=labels, values=cm.values.round(3).tolist(),
        blocks=blabels, bounds=bounds[:-1])
    print(f"  all_candidate_correlation          {len(order)} variables, "
          f"{len(blabels)} family blocks")
except Exception as e:
    print(f"  [WARN] all_candidate_correlation: {e}")

# FDR family and nested-selection stability.
fdr = pd.read_csv(OUT / "cumulative_hardship_fdr_correction.csv")
check = pd.read_csv(OUT / "cumulative_hardship_checkpoint.csv").rename(
    columns={"variable": "variable", "coef": "coef_checkpoint", "gr_avg_residual_oos": "gr_oos_checkpoint"})
dur = pd.read_csv(OUT / "cumulative_hardship_duration_battery.csv").rename(
    columns={"var": "variable", "coef": "coef_duration", "gr_oos": "gr_oos_duration"})
fdr = fdr.merge(check[["variable", "coef_checkpoint", "gr_oos_checkpoint"]],
                on="variable", how="left")
fdr = fdr.merge(dur[["variable", "coef_duration", "gr_oos_duration"]],
                on="variable", how="left")
fdr["coef"] = fdr["coef_checkpoint"].fillna(fdr["coef_duration"])
fdr["gr_oos"] = fdr["gr_oos_checkpoint"].fillna(fdr["gr_oos_duration"])
fdr["pretty"] = fdr["label"].str.replace("_", " ", regex=False)
panels["candidate_fdr"] = dict(
    label="All 18 screened cumulative and duration candidates",
    group="Candidate family", unit="Benjamini-Hochberg adjusted p-value", kind="candidate",
    note="The vertical line marks q = 0.05. Only cumulative excess unemployment and years of "
         "real wages below 2008 survive family-wide correction.", eu_basis="",
    rows=fdr[["variable", "pretty", "p_raw", "p_fdr_bh", "significant_after_fdr",
              "coef", "gr_oos"]].to_dict("records"))

folds = pd.read_csv(OUT / "nested_selection_validation_folds.csv")
counts = folds["selected_first"].value_counts().rename_axis("variable").reset_index(name="count")
counts["pretty"] = counts["variable"].str.replace("_", " ", regex=False)
panels["selection_frequency"] = dict(
    label="Which candidate wins when selection is repeated inside each fold?",
    group="Candidate family", unit="held-out-country folds, out of 27", kind="selection",
    note="Cumulative excess unemployment ranks first in 25 of 27 folds. Greece and Finland select "
         "near-neighbour duration measures instead, supporting the family rather than one uniquely "
         "privileged construction.", eu_basis="", rows=counts.to_dict("records"))


def latest_table(s):
    """Small Greece/EU table under each chart so values are readable without hovering."""
    yrs = s["years"]
    gr = s["countries"].get("EL", [])
    marks = [i for i in range(len(yrs)) if gr and gr[i] is not None]
    if not marks:
        return ""
    pick, seen = [], set()
    for target in (yrs[marks[0]], 2010, 2015, 2020, yrs[marks[-1]]):
        cand = [i for i in marks if yrs[i] == target]
        if cand and yrs[cand[0]] not in seen:
            pick.append(cand[0]); seen.add(yrs[cand[0]])
    if len(pick) < 2:
        pick = marks[:: max(1, len(marks) // 4)][:5]

    def f(v):
        if v is None:
            return "--"
        a = abs(v)
        return f"{v:,.0f}" if a >= 10000 else (f"{v:.1f}" if a >= 100 else f"{v:.2f}")
    head = "".join(f"<th>{yrs[i]}</th>" for i in pick)
    rg = "".join(f'<td class="gr">{f(gr[i])}</td>' for i in pick)
    re_ = "".join(f"<td>{f(s['eu'][i])}</td>" for i in pick)
    return (f'<div class="scroll"><table class="mini"><thead><tr><th></th>{head}</tr></thead>'
            f'<tbody><tr><td>Greece</td>{rg}</tr><tr><td>EU</td>{re_}</tr></tbody></table></div>')


# Anything not explicitly placed lands in the candidate-family section, so a
# newly added series can never disappear from the appendix unnoticed.
placed = {k for sec in SECTIONS for kind, k in sec["items"] if kind == "series"}
leftover = [k for k in series if k not in placed]
for sec in SECTIONS:
    if sec["id"] == "candidates":
        cum_like = sorted([k for k in leftover if "shortfall" in k or "threshold" in k],
                          key=lambda x: series[x]["label"])
        dur_like = sorted([k for k in leftover if k not in cum_like],
                          key=lambda x: series[x]["label"])
        sec["items"] += ([("sub", "Cumulative shortfall constructions")]
                        + [("series", k) for k in cum_like]
                        + [("sub", "Duration and direction constructions")]
                        + [("series", k) for k in dur_like])
placed_p = {k for sec in SECTIONS for kind, k in sec["items"] if kind == "panel"}
placed_x = {k for sec in SECTIONS for kind, k in sec["items"] if kind == "scatter"}
missing = ([f"panel:{k}" for k in panels if k not in placed_p]
           + [f"scatter:{k}" for k in scatters if k not in placed_x])
if missing:
    print("WARNING: not placed in any section ->", missing)

n_items = sum(1 for sec in SECTIONS for kind, _ in sec["items"] if kind != "sub")
print(f"placing {n_items} charts across {len(SECTIONS)} sections "
      f"({len(leftover)} auto-routed to the candidate family)")


def series_card(k):
    sv = series[k]
    n = len(sv["countries"])
    complete_year = next((year for i, year in enumerate(sv["years"])
                          if sum(vals[i] is not None for vals in sv["countries"].values()) == n),
                         None)
    coverage = (f"Complete {n}-country coverage from {complete_year}." if complete_year
                else f"Coverage varies by year; up to {n} countries report.")
    return (
        f'<div class="chart-card"><p class="chart-title">{sv["label"]}</p>'
        f'<p class="chart-unit">{sv["unit"]} &middot; up to {n} EU member states &middot; '
        f'{sv["years"][0]}&ndash;{sv["years"][-1]}</p>'
        f'<div id="s_{k}"></div>'
        f'<div class="legend"><span><i style="border-color:var(--gr)"></i>Greece</span>'
        f'<span><i style="border-color:var(--eu);border-top-style:dashed"></i>EU</span>'
        f'<span><i style="border-color:var(--faint)"></i>other EU member states</span>'
        f'<span><i style="border-color:var(--hi)"></i>nearest country to cursor</span></div>'
        + latest_table(sv)
        + (f'<p class="chart-note">{sv["note"]}</p>' if sv.get("note") else "")
        + f'<p class="chart-basis">{coverage} EU comparator: {sv["eu_basis"]}</p></div>')


def panel_card(k):
    pv = panels[k]
    return (f'<div class="chart-card"><p class="chart-title">{pv["label"]}</p>'
            f'<p class="chart-unit">{pv["unit"]}</p><div id="p_{k}"></div>'
            + (f'<p class="chart-note">{pv["note"]}</p>' if pv.get("note") else "")
            + (f'<p class="chart-basis">EU comparator: {pv["eu_basis"]}</p>'
               if pv.get("eu_basis") else "") + "</div>")


def scatter_card(k):
    sx = scatters[k]
    return (f'<div class="chart-card scatter-card"><p class="chart-title">'
            f'<span class="tag">relationship</span>{sx["title"]}</p>'
            f'<p class="chart-unit">{sx["year"]} &middot; {len(sx["points"])} member states '
            f'&middot; r = {sx["r"]:+.2f}</p>'
            f'<div id="x_{k}"></div>'
            f'<p class="chart-note">{sx["note"]}</p>'
            f'<p class="chart-basis">EU marker: {sx["eu_basis_x"]} (x), '
            f'{sx["eu_basis_y"]} (y). Cross-country correlation for the year shown &mdash; a '
            f'different quantity from the within-Greece correlations quoted in the reports. '
            f'The green dashed line is fitted to the 26 peers, excluding Greece.</p>'
            "</div>")


def sub_head(text):
    return f'<p class="subhead">{text}</p>'


GLOSSARY = [
 ("Poverty and living-conditions measures", [
  ("AROP", "At Risk Of Poverty",
   "Below 60% of the national median equivalised disposable income. A relative measure: "
   "the line moves with the country's own median, which is why it can fall while living "
   "standards fall. Eurostat's headline income-poverty indicator."),
  ("AROPE", "At Risk Of Poverty or social Exclusion",
   "A person counted if they meet <em>any</em> of three conditions: AROP, severe material "
   "and social deprivation, or living in a very low work intensity household. A union, not "
   "an average, so it is always at least as large as AROP."),
  ("EU-SILC", "European Union Statistics on Income and Living Conditions",
   "The annual household survey behind almost every poverty figure here. Income data refer "
   "to the year before the survey; deprivation and subjective questions to the survey year."),
  ("SMSD", "Severe Material and Social Deprivation",
   "Lacking at least 7 of 13 items a household cannot afford. Replaced the legacy 9-item "
   "severe material deprivation measure in 2021; both appear in the appendix, spliced."),
  ("S80/S20", "Income quintile share ratio",
   "Total income of the richest 20% divided by that of the poorest 20%. The project's "
   "inequality measure, tested and ruled out as an explanation."),
  ("Anchored poverty", "&mdash;",
   "The poverty line held fixed at an earlier year's real value instead of moving with the "
   "current median. Section 3's fixed-2008-baseline reconstruction."),
  ("Equivalised income", "&mdash;",
   "Household income adjusted for household size and composition, so a couple is not "
   "counted as twice as well off as a single person."),
  ("Arrears", "Household payment arrears",
   "A household reports that, because of financial difficulty, it could not pay on time "
   "during the previous 12 months one or more scheduled housing, utility or instalment/loan "
   "payments. It measures missed payments, not total debt, and does not necessarily mean a "
   "formal legal default."),
 ]),
 ("Statistics and method", [
  ("FDR", "False Discovery Rate",
   "When many variables are screened at once, some will look significant by chance. FDR "
   "control caps the expected share of false positives among the findings declared "
   "significant &mdash; here at 5%. It is why a variable can have a raw p of 0.005 and an "
   "adjusted p of 0.041: the penalty for having asked 18 questions rather than one."),
  ("BH", "Benjamini&ndash;Hochberg",
   "The specific procedure used to control the FDR. Ranks the p-values and rescales each by "
   "the family size divided by its rank. Adding candidates to a family raises every "
   "adjusted p-value in it."),
  ("p-value", "&mdash;",
   "The probability of seeing an association at least this strong if there were really no "
   "relationship. Small means surprising-under-no-effect; it is not the probability that "
   "the finding is true, and it says nothing about effect size."),
  ("R&sup2;", "Coefficient of determination",
   "Share of the variation in the outcome the model accounts for, 0 to 1. In-sample R&sup2; "
   "always rises when a variable is added, which is why this project also reports "
   "out-of-sample performance."),
  ("LOO", "Leave-One-Out cross-validation",
   "The model is refit on 26 countries and used to predict the 27th, country by country. "
   "The Greek out-of-sample gap is what a model that has never seen Greece gets wrong "
   "about Greece &mdash; a far harder test than in-sample fit."),
  ("OOS", "Out-Of-Sample",
   "Any figure computed on data the model was not fitted to. The project's headline "
   "residual is an out-of-sample quantity."),
  ("RMSE", "Root Mean Squared Error",
   "Typical size of a prediction error, in the outcome's own units."),
  ("VIF", "Variance Inflation Factor",
   "How much a predictor's variance is inflated by correlation with the other predictors. "
   "Above about 10 is conventionally treated as disqualifying collinearity."),
  ("r", "Pearson correlation coefficient",
   "Strength and direction of a straight-line association, &minus;1 to +1. Cross-country "
   "correlations in the appendix are a different quantity from the within-Greece "
   "correlations quoted in the reports."),
  ("pp", "percentage points",
   "The arithmetic difference between two percentages. A move from 10% to 13% is 3 "
   "percentage points, not 3 percent."),
  ("pp-years", "accumulated percentage-point-years",
   "The unit of the cumulative-exposure variables: a rate held one percentage point above "
   "baseline for one year contributes 1. Ten years at 10pp above baseline gives 100."),
  ("s.e.", "standard error",
   "The estimated sampling variability of a coefficient. Roughly, the coefficient plus or "
   "minus two standard errors is a 95% interval."),
  ("n", "sample size",
   "Here almost always the number of countries (27) or country-years in a panel."),
  ("FE", "Fixed effects",
   "Controls for stable differences between countries or shocks common to a given year. "
   "Country fixed effects ask whether changes within a country move with the outcome."),
  ("CI", "Confidence interval",
   "A range expressing estimation uncertainty. Under repeated comparable samples, a 95% "
   "confidence-interval procedure would contain the true parameter about 95% of the time."),
  ("SDMX-JSON", "Statistical Data and Metadata eXchange, JSON format",
   "The machine-readable format used to retrieve Eurostat data and its dimension labels."),
 ]),
 ("Economic and price concepts", [
  ("GDP", "Gross Domestic Product", "Total value of goods and services produced."),
  ("AIC", "Actual Individual Consumption",
   "What households actually consume, including services provided by government such as "
   "health and education. Eurostat recommends it over GDP for welfare comparisons, and the "
   "cross-country models use it as a living-standards variable. Here AIC never means the "
   "Akaike information criterion."),
  ("PPS", "Purchasing Power Standard",
   "An artificial currency that equalises purchasing power across countries: one PPS buys "
   "the same basket everywhere. Removes price-level differences from income and pay "
   "comparisons."),
  ("PLI", "Price Level Index",
   "A country's price level relative to the EU27 average, which is set to 100."),
  ("HICP", "Harmonised Index of Consumer Prices",
   "The EU's comparable consumer-price index, used here to deflate nominal series into "
   "real terms using each country's own inflation."),
  ("COICOP", "Classification Of Individual Consumption by Purpose",
   "The standard category scheme behind the price charts (food, housing and energy, "
   "transport, communications, restaurants)."),
  ("NAC", "National Currency",
   "Values in whatever currency the country used at the time &mdash; not converted to euro. "
   "For countries that adopted the euro mid-series this creates a level break, corrected "
   "in this project by <code>scripts/currency.py</code>."),
  ("LTU", "Long-Term Unemployment",
   "Unemployed for 12 months or more, as a share of the active population. The strongest "
   "single correlate of Greek subjective poverty in this project."),
  ("LFS", "Labour Force Survey",
   "The EU survey behind the employment, unemployment and working-hours series."),
  ("JEL", "Journal of Economic Literature classification",
   "Subject codes on the working paper's title page, used by economics journals for "
   "indexing."),
 ]),
 ("Institutions and sources", [
  ("OECD", "Organisation for Economic Co-operation and Development", ""),
  ("IMF", "International Monetary Fund", ""),
  ("ESM", "European Stability Mechanism",
   "Lender in Greece's third assistance programme (2015&ndash;2018)."),
  ("EFSF", "European Financial Stability Facility",
   "Lender in the second programme (2012&ndash;2015)."),
  ("GLF", "Greek Loan Facility",
   "Pooled bilateral loans in the first programme (2010&ndash;2012)."),
  ("PSI", "Private Sector Involvement",
   "The 2012 restructuring of privately held Greek debt."),
  ("ELSTAT", "Hellenic Statistical Authority", "Greece's national statistical office."),
  ("ELIAMEP", "Hellenic Foundation for European and Foreign Policy",
   "Athens policy institute; host of the Crisis Observatory."),
  ("IOBE", "Foundation for Economic and Industrial Research",
   "Athens economic research institute."),
  ("EKT", "National Documentation Centre",
   "Greek research and documentation body; source of the graduate-emigration figures."),
  ("EUROMOD", "&mdash;",
   "The EU-wide tax and benefit microsimulation model."),
  ("diaNEOsis", "&mdash;",
   "Greek research and policy organisation; source of the national survey used as "
   "corroborating evidence."),
 ]),
 ("Geography and country codes", [
  ("EL", "Greece",
   "Eurostat uses EL, not GR. Both refer to Greece; EL is the code throughout this project."),
  ("EU27 / EU27_2020", "European Union, 27 members after the UK's withdrawal",
   "Eurostat's official aggregate: population-weighted, so large countries count more. "
   "Distinct from an unweighted mean of the 27 member states, which is what the appendix "
   "draws when no official aggregate is published."),
  ("EU15, EU-28", "Earlier EU compositions",
   "The Union before the 2004 enlargement, and before the UK left. Appear only where a "
   "cited source used them."),
  ("EA19 / EA20 / EA21", "Euro area",
   "Countries using the euro. Excluded from this appendix, which shows member states only."),
  ("EFTA", "European Free Trade Association",
   "Iceland, Liechtenstein, Norway, Switzerland. Not EU members and not included here."),
 ]),
 ("Eurostat dimension codes seen in the Methods", [
  ("B_60", "60% of median threshold", "The cut-off defining AROP. B_40, B_50 and B_70 are the alternative cut-offs used in the anchored-poverty reconstruction."),
  ("MED_EI", "Median equivalised income", "The statistic the threshold is computed from."),
  ("SAL", "Salaried employees", "Employees only, excluding the self-employed &mdash; the population used in the work-effort section."),
  ("EMP", "Employed persons", "All employed, including the self-employed."),
  ("DIF / GRT", "With difficulty / with great difficulty",
   "The two response categories summed to form the subjective-poverty measure."),
  ("NAT", "Nationals", "The reporting country's own citizens, used for the migration series."),
  ("PC_ACT", "Percent of active population", "The denominator for unemployment rates."),
  ("Y15-74, Y15-24, Y20-64", "Age bands", "Working-age, youth, and the employment-rate band."),
  ("Y_LT18 / Y_GE65", "Under 18 / 65 and over", "Eurostat's standard EU-SILC age breakdown."),
  ("SA / NSA", "Seasonally adjusted / not seasonally adjusted",
   "Whether regular within-year seasonal movements have been removed. The project records the "
   "choice explicitly because mixing the two changes time-series comparisons."),
  ("INX_A_AVG", "Annual-average index", "An index expressed as the average level for the year."),
  ("PLI_EU27_2020", "Price-level index, EU27=100",
   "A value above 100 means prices are above the EU27 average; below 100 means they are lower."),
  ("BS-FS-NY", "Cannot make ends meet",
   "Eurostat's code for the financial-strain outcome used as subjective poverty."),
  ("COMPLET", "Completed duration",
   "Eurostat duration code used for completed unemployment spells."),
  ("MIGTRT", "Migration treatment/status",
   "A Eurostat migration dimension used to distinguish relevant movement categories."),
  ("DN", "Downward/negative direction",
   "Direction code used in selected business and expectations series."),
 ]),
]

# ---------------------------------------------------------------------------
# The variable dictionary is generated, not hand-written: every name that
# appears in a model, a screening family or a chart is pulled from the same
# files the analysis runs on, so a renamed or dropped variable cannot leave a
# stale definition sitting in the glossary.
VAR_GLOSS = {
    "subjective_poverty": ("The outcome. Share of households reporting difficulty or great "
        "difficulty making ends meet (EU-SILC ilc_mdes09, DIF + GRT)."),
    "arop": ("At-risk-of-poverty rate: share below 60% of the national median equivalised "
        "income. A Model C-LTU covariate."),
    "aic_pps_pc_k": ("Actual individual consumption per capita in PPS, thousands. The income "
        "term in every cross-country model."),
    "severe_mat_soc_deprivation": ("Severe material and social deprivation: lacking at least 7 "
        "of 13 affordability items."),
    "ltu_rate": ("Long-term unemployment: unemployed 12 months or more, share of the active "
        "population. The strongest single correlate in the project."),
    "housing_cost_overburden": ("Share of people whose housing costs exceed 40% of disposable "
        "income."),
    "arrears": ("Share in arrears on mortgage, rent, utilities or hire-purchase."),
    "unexpected_expenses": ("Share unable to meet an unexpected required expense from own "
        "resources."),
    "cum_excess_unemployment": ("THE HEADLINE MECHANISM. Unemployment above each country's own "
        "2009 rate, floored at zero and summed year over year since 2009, in accumulated "
        "percentage-point-years. Survives FDR at q=0.002; Greece 138 against an EU median of 6."),
    "cum_excess_ltu": ("The same accumulation applied to long-term unemployment. Null."),
    "wage_years_below_2008": ("SECOND FDR SURVIVOR. Consecutive years real wages have been "
        "below their own 2008 level \u2014 a current run that resets on recovery, not a total. "
        "Greece 15 years. Survives FDR at q=0.041."),
    "cum_threshold_shortfall": ("Accumulated shortfall of the real AROP threshold against its "
        "own 2008 level. The most narratively anticipated candidate; null (p=0.291)."),
    "pct_below_peak": ("How far current GDP per capita sits below the country's own historical "
        "peak. A stock measure of scarring. Null."),
    "share_worst_composite": ("Share of independent indicators placing the country in the EU's "
        "worst quintile that year. Descriptive only \u2014 tested and null (FDR 0.287)."),
    "years_worst_quintile_wage": ("Cumulative years in the EU's bottom quintile on real wages "
        "indexed to own 2008. The family-B near-miss; redundant with the wage family "
        "(r=+0.948) and rejected."),
}
VAR_PREFIX = [
    ("cum_gdp_shortfall", "Accumulated GDP shortfall against a baseline, summed since 2008."),
    ("cum_wage_shortfall", "Accumulated real-wage shortfall against a baseline, summed since 2008."),
    ("gdp_years_below", "Consecutive years GDP has been below a baseline (current run, resets on recovery)."),
    ("wage_years_below", "Consecutive years real wages have been below a baseline (current run, resets on recovery)."),
    ("gdp_longest_streak", "Longest unbroken run of years GDP was below a baseline (running maximum, never falls)."),
    ("wage_longest_streak", "Longest unbroken run of years wages were below a baseline (running maximum, never falls)."),
    ("gdp_cum_negative", "Count of years GDP fell year on year, at any level."),
    ("wage_cum_negative", "Count of years real wages fell year on year, at any level."),
    ("slope5_", "Five-year trailing OLS slope of the series \u2014 its rate of change. Family B."),
    ("years_worst_quintile", "Cumulative years spent in the EU's worst quintile. Family B."),
    ("share_worst", "Share of observed years since 2008 in the EU's worst quintile, 0 to 1. Family C."),
]


def variable_glossary():
    """Build the variable entries from the panel and the three battery files."""
    import pandas as _pd
    try:
        allp = _pd.read_csv(OUT / "persistence_share_panel.csv")
        famA = _pd.read_csv(OUT / "cumulative_hardship_fdr_correction.csv")
        famB = _pd.read_csv(OUT / "direction_persistence_battery.csv").variable.tolist()
        famC = _pd.read_csv(OUT / "persistence_share_battery.csv").variable.tolist()
    except Exception as e:
        print(f"  [WARN] variable glossary: {e}")
        return []
    survivors = set(famA[famA.significant_after_fdr].variable)
    covars = ["subjective_poverty", "arop", "aic_pps_pc_k", "severe_mat_soc_deprivation",
              "ltu_rate", "housing_cost_overburden", "arrears", "unexpected_expenses"]
    groups = [("Model variables \u2014 the outcome and the Model C-LTU covariates", covars),
              ("Screened candidates, family A \u2014 accumulation and duration (18)",
               famA.variable.tolist()),
              ("Screened candidates, family B \u2014 direction and relative standing (5)", famB),
              ("Screened candidates, family C \u2014 persistence share (6)", famC)]
    out = []
    for title, names in groups:
        entries = []
        for v in names:
            if v not in allp.columns and v not in covars:
                continue
            desc = VAR_GLOSS.get(v)
            if desc is None:
                desc = next((d for pre, d in VAR_PREFIX if v.startswith(pre)), "")
                if "2008" in v and "own" not in desc:
                    desc += " Baseline: the country's own 2008 level."
                elif "peak" in v:
                    desc += " Baseline: the country's own rolling historical peak."
            tag = ""
            if v in survivors:
                tag = " <b>Survives FDR correction.</b>"
            elif v in set(famA.variable) | set(famB) | set(famC):
                tag = " Tested and null."
            entries.append((v, "", (desc + tag).strip()))
        if entries:
            out.append((title, entries))
    return out


GLOSSARY += variable_glossary()



def glossary_html():
    """A reader who meets 'FDR' 33 times without ever seeing it expanded cannot
    look it up. This section is the lookup: every abbreviation the four
    documents use, what it stands for, and -- where expanding it is not enough
    to make it usable -- what it actually means."""
    out = ['<div class="gloss-wrap">',
           '<input id="glossq" class="gloss-search" type="search" '
           'placeholder="Filter \u2014 type an abbreviation or a word" '
           'aria-label="Filter glossary">']
    for group, entries in GLOSSARY:
        out.append(f'<h3 class="gloss-group">{group}</h3><dl class="gloss">')
        for abbr, full, gloss in entries:
            out.append(
                f'<div class="gloss-row"><dt>{abbr}</dt><dd>'
                + (f'<span class="gloss-full">{full}</span>' if full and full != "&mdash;" else '')
                + (f'<span class="gloss-def">{gloss}</span>' if gloss else '')
                + '</dd></div>')
        out.append('</dl>')
    out.append('</div>')
    return "".join(out)


def safe_json(value):
    """Serialize embedded chart data as strict JSON, converting NaN/Inf to null."""
    def clean(item):
        if isinstance(item, dict):
            return {key: clean(val) for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [clean(val) for val in item]
        if isinstance(item, (float, np.floating)) and not np.isfinite(item):
            return None
        if isinstance(item, np.generic):
            return item.item()
        return item
    return json.dumps(clean(value), allow_nan=False)


RENDER = {"series": series_card, "panel": panel_card, "scatter": scatter_card,
          "sub": sub_head}

body, toc = [], []
for sec in SECTIONS:
    if not sec["items"]:
        continue
    toc.append(f'<a href="#{sec["id"]}"><b>{sec["num"]}</b> {sec["title"]}</a>')
    body.append(f'<h2 class="group" id="{sec["id"]}">'
                f'<span class="secnum">{sec["num"]}</span>{sec["title"]}</h2>')
    body.append(f'<p class="group-blurb">{sec["blurb"]}</p>')
    for kind, k in sec["items"]:
        rendered = RENDER[kind](k)
        if sec["id"] == "candidates" and kind == "series":
            rendered = (f'<details class="candidate-detail"><summary>View candidate trajectory: '
                        f'{series[k]["label"]}</summary>{rendered}</details>')
        body.append(rendered)

toc.append('<a href="#glossary"><b>&#167;</b> Abbreviations</a>')
body.append('<h2 class="group" id="glossary"><span class="secnum">&#167;</span>'
            'Abbreviations and terms</h2>')
body.append('<p class="group-blurb">Technical measures, methods and data codes used across the '
            'project, collected in one searchable place. Where expanding a term is not enough '
            'to make it usable, a plain-language explanation is included.</p>')
body.append(glossary_html())

html = f"""{HEAD}
<div class="wrap">
<p class="eyebrow">Statistical appendix &middot; EU-SILC / Eurostat</p>
<h1>Every variable, in its own units</h1>
<p class="dek">The three reports use these variables as model inputs, coefficients and residuals.
This appendix shows what each one actually <em>is</em>: the real value, every year, for Greece,
for the EU comparator, and for each of the other 26 member states. The country set is the
27 current EU members &mdash; the same panel the models are estimated on. Eurostat publishes many of
these series for candidate and EFTA countries as well, and for the euro-area aggregates; those are
excluded here so that what you see is the country set the analysis actually used.</p>
<div class="howto"><b>How this is organised.</b> The ten sections follow the reports' own
argument rather than the data's categories: the puzzle first, then why the official measure
understates it, then the labour-market explanation in three steps (how much unemployment, how long
it lasts, how much has accumulated), then what that history did to household finances, the
alternatives tested, and finally the model diagnostics and the full family of screened candidates.
Charts marked <span class="tag">relationship</span> are cross-country scatters placed in the section
whose claim they illustrate. Version 2 adds the final fixed and nested model results, the complete
multiple-testing screen, conditional diagnostics and country-level residual comparisons; detailed
candidate trajectories are collapsed by default so the central evidence remains readable.
<br><br><b>How to read the charts.</b> Each line chart draws every EU member state as a faint grey
line, with <b style="color:var(--gr)">Greece</b> in blue and the <b style="color:var(--eu)">EU
comparator</b> as an orange dashed line. Hover anywhere to read the year, Greece's value, the EU
value, and the value of whichever country's line your cursor is nearest &mdash; that line lights up
in green. The small table under each chart gives the same figures at fixed years, so the numbers are
readable without a mouse. On scatters, the dashed orange lines mark the EU value on each axis, so
the plot divides into quadrants relative to the EU.
<br><br><b>Two cautions.</b> The EU line is Eurostat's own population-weighted EU27 aggregate where
one is published, and an unweighted mean of member states where it is not; the difference is stated
under every chart, and the two are not interchangeable. And a country line stopping early means that
country stopped reporting, not that its value fell to zero.</div>
<nav class="toc">{"".join(toc)}</nav>
{"".join(body)}
<footer>
Built by <code>scripts/46_appendix_data.py</code> and <code>scripts/47_build_appendix.py</code>
from the same Eurostat pipeline as the main reports. {len(series)} series, {len(panels)} panels and {len(scatters)} scatter relationships.
Eurostat revises published figures over time, so a later pull will not reproduce these numbers
exactly. Every result in the main reports is associational and drawn from country-level aggregates,
not household microdata &mdash; see the technical report's Methods for the full limitations.
</footer>
</div>
{JS.replace("__DATA__", safe_json(series)).replace("__NAMES__", safe_json(COUNTRY_NAMES))}
{JS_PANELS.replace("__PANELS__", safe_json(panels))}
{JS_SCATTER.replace("__SCATTERS__", safe_json(scatters))}
<script>
// Glossary filter: matches abbreviation, expansion and explanation, and hides a
// group heading when nothing under it survives the filter.
(() => {{
  const q = document.getElementById('glossq');
  if (!q) return;
  const rows = [...document.querySelectorAll('.gloss-row')];
  const heads = [...document.querySelectorAll('h3.gloss-group')];
  const none = document.createElement('p');
  none.className = 'gloss-none'; none.hidden = true;
  none.textContent = 'No abbreviation matches that.';
  q.after(none);
  q.addEventListener('input', () => {{
    const t = q.value.trim().toLowerCase();
    rows.forEach(r => {{ r.hidden = t && !r.textContent.toLowerCase().includes(t); }});
    heads.forEach(h => {{
      const dl = h.nextElementSibling;
      h.hidden = dl && ![...dl.querySelectorAll('.gloss-row')].some(r => !r.hidden);
    }});
    none.hidden = rows.some(r => !r.hidden);
  }});
}})();
</script>
<script>
Object.entries(DATA).forEach(([k, s]) => {{
  const host = document.getElementById('s_' + k);
  if (host) try {{ drawSeries(host, k, s); }} catch (e) {{ console.error('series', k, e); }}
}});
Object.entries(PANELS).forEach(([k, p]) => {{
  const host = document.getElementById('p_' + k);
  if (host) try {{ drawPanel(host, k, p); }} catch (e) {{ console.error('panel', k, e); }}
}});
Object.entries(SCATTERS).forEach(([k, sc]) => {{
  const host = document.getElementById('x_' + k);
  if (host) try {{ drawScatter(host, k, sc); }} catch (e) {{ console.error('scatter', k, e); }}
}});
</script>
"""
DEST.write_text(html, encoding="utf-8")
print(f"{DEST}  ({len(html)/1024:.0f} KB)  {len(series)} series, {len(panels)} panels, {len(scatters)} scatters")
