"""Shared chart engine for the report and any other output that needs it.

Extracted from the appendix renderer rather than rewritten, so the scales,
country highlighting, EU reference and hover behaviour are the ones already
validated across the full appendix. What is new here:

  * NO FIXED DOM IDS. Charts mount on [data-chart] and read their payload from
    an adjacent script tag. The previous report library bound to five hardcoded
    ids and silently aborted when the structure changed.
  * RESPONSIVE VIEWBOX. The appendix draws at a fixed 860 wide, which rendered
    labels at about 4 effective pixels on a 375px screen. Width is chosen per
    breakpoint and the chart redraws on resize.
  * KEYBOARD. Every chart is focusable and arrow keys step through the data,
    announcing values on an aria-live region. Hover alone excludes anyone not
    using a mouse.
  * PRINT. The interactive layer is hidden for print and the table fallback is
    shown, so a PDF carries the evidence rather than an empty box.

Two chart types are implemented here: `panel` (reused) and `coefficient` (new).
The remaining manifest types are added the same way, one function each.
"""
import html
import json

# ---------------------------------------------------------------------------
# READER-FACING NAMES. Code names belong in tooltips and the appendix, never in
# a title, axis or row label. One map, shared by every figure, so a variable
# cannot appear as `wadj_a01` in one chart and by name in another.
# ---------------------------------------------------------------------------
DISPLAY = {
    "subjective_poverty": "Reported hardship",
    "arop": "Income poverty (AROP)",
    "arope": "AROPE",
    "arop_threshold_real": "Real poverty threshold",
    "aic_pps_pc": "Material resources",
    "aic_pps_pc_k": "Material resources",
    "gdp_pps_pc": "GDP per head",
    "real_gdp_pc": "Real GDP per head",
    "consumption_pc": "Consumption per head",
    "hourly_comp": "Hourly compensation",
    "ltu_rate": "Long-term unemployment",
    "unemployment_rate": "Unemployment",
    "youth_unemployment": "Youth unemployment",
    "employment_rate": "Employment rate",
    "real_wages_idx": "Real wages",
    "real_income_idx": "Real household income",
    "pct_below_peak": "Share below own GDP peak",
    "wadj_a01": "Wage-adjusted affordability",
    "work_effort_squeeze": "Work-effort squeeze",
    "hicp": "Inflation",
    "hicp_food": "Food inflation",
    "hicp_housing": "Housing inflation",
    "housing_cost_overburden": "Housing-cost overburden",
    "severe_mat_soc_deprivation": "Material deprivation",
    "arrears": "Arrears on bills",
    "unexpected_expenses": "Cannot meet an unexpected expense",
    "warm": "Cannot keep the home warm",
    "net_migration": "Net migration",
    "s80s20": "Income inequality (S80/S20)",
    "saving_rate": "Household saving rate",
    "debt_to_income": "Household debt to income",
    "working_hours": "Weekly working hours",
    "acc_cum_excess_unemployment": "Accumulated unemployment",
    "cum_excess_unemployment": "Accumulated unemployment",
    "cum_excess_ltu": "Accumulated long-term unemployment",
    "dur_real_wages_below": "Years wages below 2008",
    "wage_years_below_2008": "Years wages below 2008",
    "acc_real_wages_shortfall": "Cumulative wage shortfall",
    "acc_pct_below_peak": "Cumulative GDP shortfall",
    "acc_threshold_shortfall": "Cumulative threshold shortfall",
    "acc_wadj_excess": "Accumulated affordability pressure",
    "acc_hicp_compounded": "Compounded inflation since 2008",
    "acc_housing_excess": "Housing deterioration since 2010",
    "gap_subj_arop": "Hardship gap against income poverty",
    "gap_subj_arope": "Hardship gap against AROPE",
}


def base_style(html_text):
    """The host stylesheet, with stale chart tokens stripped.

    Every builder borrows its base tokens from a document that also carries an
    OLDER copy of this module's chart tokens. Those definitions are overridden
    by the current ones at render time, but they remain in the file, so a
    reader of the CSS -- and any check that reads it -- sees a value that is no
    longer in effect. One of them was the negative-correlation colour at 2.96:1
    on dark, the exact defect this pass exists to remove.

    Stripping them here means the chart tokens have exactly one definition per
    theme, in this module, and the file says what it does.
    """
    import re as _re
    style = _re.search(r"<style.*?</style>", html_text, _re.S).group(0)
    for tok in ("div-neg", "div-pos", "div-zero", "chart-label",
                "chart-neutral", "chart-neutral-edge"):
        style = _re.sub(rf"--{tok}\s*:\s*[^;}}]+;?", "", style)
    return style


def name(code):
    """Reader-facing name, falling back to the code if none is registered."""
    return DISPLAY.get(code, code)

# --------------------------------------------------------------------------- CSS
CSS = """
.figure{margin:1.8rem 0;border:1px solid var(--border);border-radius:8px;
background:var(--surface-1);overflow:hidden}
.figure > figcaption{padding:.9rem 1.1rem .2rem;font:600 .95rem/1.35
ui-sans-serif,system-ui,sans-serif;color:var(--text-primary)}
.fig-meta{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;
padding:0 1.1rem .7rem}
.badge{font:600 .66rem/1 ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
letter-spacing:.06em;padding:.3rem .5rem;border-radius:3px;
background:var(--accent-soft,rgba(61,111,180,.12));color:var(--eu)}
.fig-q{font:.82rem/1.4 ui-sans-serif,system-ui,sans-serif;color:var(--text-secondary)}
.chart-live{padding:.2rem 1.1rem 1rem;position:relative}
.chart-live:focus-visible{outline:2px solid var(--eu);outline-offset:2px}
.chart{width:100%;height:auto;display:block;touch-action:pan-y}
/* Correlation sign is a value scale, not a Greece/EU comparison, so it may
   not borrow those two hues. Magenta/teal is colour-blind safe. */
:root{--div-neg:#a2306f;--div-pos:#127070;--div-zero:#6f6f6f;
--chart-label:#55534e;--chart-neutral:#7a7873;--chart-neutral-edge:#f4f3ef}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--div-neg:#e07ab5;--div-pos:#4fc7c7;--div-zero:#9a9a9a;
--chart-label:#c8c6bf;--chart-neutral:#9a9892;--chart-neutral-edge:#141413}}
:root[data-theme="dark"]{
--div-neg:#e07ab5;--div-pos:#4fc7c7;--div-zero:#9a9a9a;
--chart-label:#c8c6bf;--chart-neutral:#9a9892;--chart-neutral-edge:#141413}
.gridline{stroke:var(--border);stroke-width:1}
.axis-label{fill:var(--chart-label);font:11px ui-sans-serif,system-ui,sans-serif}
.line-faint{fill:none;stroke:var(--chart-neutral);stroke-width:1;opacity:.34}
.line-eu{fill:none;stroke:var(--eu);stroke-width:2.2;stroke-dasharray:5 3}
.line-gr{fill:none;stroke:var(--gr);stroke-width:2.8}
.zero-line{stroke:var(--chart-label);stroke-width:1.4;opacity:.55}
.cursor-line{stroke:var(--text-secondary);stroke-width:1;stroke-dasharray:3 3}
.tip{position:absolute;pointer-events:none;background:var(--surface-2);
border:1px solid var(--border);border-radius:5px;padding:.45rem .6rem;
font:.76rem/1.45 ui-sans-serif,system-ui,sans-serif;color:var(--text-primary);
box-shadow:0 3px 12px rgba(0,0,0,.14);max-width:15rem;z-index:5;opacity:0;
transition:opacity .1s}
.tip.on{opacity:1}
.legend{display:flex;flex-wrap:wrap;gap:.35rem 1rem;padding:.3rem 0 .1rem;
max-width:100%;
font:.76rem/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--text-secondary)}
.viewbar{display:flex;flex-wrap:wrap;gap:.3rem;padding:0 1.1rem .6rem}
.viewbtn{font:600 .74rem/1 ui-sans-serif,system-ui,sans-serif;padding:.35rem .6rem;
border:1px solid var(--border);background:transparent;color:var(--text-secondary);
border-radius:4px;cursor:pointer}
.viewbtn[aria-selected="true"]{background:var(--gr);border-color:var(--gr);color:#fff}
.viewbtn:hover{color:var(--gr)}
.viewbtn[aria-selected="true"]:hover{color:#fff}
.lg-item{display:inline-flex;align-items:center;gap:.4rem;white-space:nowrap;
flex:0 1 auto;min-width:0}
@media(max-width:34rem){.legend{gap:.3rem .7rem;font-size:.72rem}}
.tip b{color:var(--gr)}
.fig-caveat{margin:0;padding:.7rem 1.1rem;border-top:1px solid var(--border);
background:var(--accent-soft,rgba(192,57,43,.05));
font:.78rem/1.5 ui-sans-serif,system-ui,sans-serif;color:var(--text-secondary)}
.fig-caveat strong{color:var(--gr)}
.fallback{border-top:1px solid var(--border)}
.fallback > summary{padding:.6rem 1.1rem;cursor:pointer;
font:.78rem/1 ui-sans-serif,system-ui,sans-serif;color:var(--text-secondary)}
.fallback > summary:hover{color:var(--gr)}
.fallback table{border-collapse:collapse;width:100%;
font:.78rem/1.4 ui-sans-serif,system-ui,sans-serif;font-variant-numeric:tabular-nums}
.fallback th,.fallback td{padding:.4rem .8rem;border-bottom:1px solid var(--border);
text-align:left}
.fallback td.num,.fallback th.num{text-align:right}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
@media print{
  .chart-live{display:none}
  .fallback{border-top:0}
  .fallback > summary{display:none}
  .fallback[open],.fallback{display:block}
  .figure{break-inside:avoid;border-color:#999}
}
"""

# --------------------------------------------------------------------------- JS
JS = r"""
(function(){
  const NS='http://www.w3.org/2000/svg';
  const el=(t,a)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);return e;};
  const cssv=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const fmt=(v,d)=>v==null?'—':(Math.abs(v)>=1000?v.toLocaleString(undefined,{maximumFractionDigits:0}):v.toFixed(d==null?1:d));

  // Width is chosen from the container, not hardcoded. A fixed 860 rendered
  // labels at ~4 effective pixels on a phone.
  // Legacy tone names map onto the chart's own tokens. "text-muted" came from
  // the host document and carries one value for both themes; the chart needs a
  // neutral that adapts, so it is aliased rather than chased through every
  // builder's payload.
  const TONE_ALIAS={'text-muted':'chart-neutral'};
  function toneVar(tone){
    const k=TONE_ALIAS[tone]||tone||'chart-neutral';
    return `var(--${k})`;
  }

  // A medium grey mark loses its edge against either ground. Outlining just the
  // neutral tone keeps it legible without adding a second colour meaning.
  function outlineNeutral(node,tone){
    const k=TONE_ALIAS[tone]||tone||'chart-neutral';
    if(k==='chart-neutral'||k==='div-zero'){
      node.setAttribute('stroke','var(--chart-neutral-edge)');
      node.setAttribute('stroke-width','1');
    }
    return node;
  }

  function widthFor(host){ const w=host.clientWidth||640; return Math.max(320,Math.min(920,w)); }

  // Measure the widest row label as the browser will actually draw it, rather
  // than estimating from character count. A per-character constant is a guess
  // about the font, and the guess was wrong: 5.9px/char underestimated the
  // real ~7.6px/char, so every row label in the conditional figures was
  // clipped on the left. No automated check sees this -- only rendering does.
  // Text measurement for layout. Charts are built into a DETACHED svg and
  // inserted at the end, so getComputedTextLength() on a node inside that tree
  // returns 0 while it is being drawn. Both helpers below therefore measure
  // through a probe attached to the live host, never through the node itself.
  function measurer(host){
    const probe=document.createElementNS('http://www.w3.org/2000/svg','svg');
    probe.setAttribute('style',
      'position:absolute;visibility:hidden;width:0;height:0;overflow:hidden');
    const txt=document.createElementNS('http://www.w3.org/2000/svg','text');
    txt.setAttribute('class','axis-label');
    probe.appendChild(txt); host.appendChild(probe);
    const fn=(s,bold)=>{
      txt.setAttribute('style',bold?'font-weight:700':'');
      txt.textContent=String(s);
      const w=txt.getComputedTextLength();
      // Fall back to an estimate only when the host itself has no layout --
      // a collapsed pane, a closed <details>, an inactive view tab.
      return w>0?w:String(s).length*(bold?7.6:6.0);
    };
    fn.done=()=>{ if(probe.parentNode)probe.parentNode.removeChild(probe); };
    return fn;
  }

  // Size a label gutter to the widest label it must hold, measured bold since
  // emphasised rows draw bold and bold is wider.
  function labelGutter(measure,labels,min,max){
    let widest=0;
    for(const l of labels){widest=Math.max(widest,measure(l,true));}
    return Math.min(max,Math.max(min,Math.ceil(widest)+20));
  }

  // Shorten a label until it fits, keeping the full text as a tooltip. Sizing
  // the gutter is not enough on its own: when the width cap binds, the surplus
  // has to come off the text.
  function fitLabel(node,full,maxW,measure,bold){
    node.textContent=full;
    if(maxW<=0||measure(full,bold)<=maxW){return node;}
    const title=document.createElementNS('http://www.w3.org/2000/svg','title');
    title.textContent=full;
    let lo=0,hi=String(full).length;
    while(lo<hi){
      const mid=Math.ceil((lo+hi)/2);
      if(measure(String(full).slice(0,mid)+'\u2026',bold)<=maxW){lo=mid;}else{hi=mid-1;}
    }
    node.textContent=String(full).slice(0,lo).trimEnd()+'\u2026';
    node.appendChild(title);
    return node;
  }

  function tip(host){
    let t=host.querySelector('.tip');
    if(!t){t=document.createElement('div');t.className='tip';host.appendChild(t);}
    return t;
  }
  function say(host,msg){
    let s=host.querySelector('.sr');
    if(!s){s=document.createElement('div');s.className='sr';s.setAttribute('aria-live','polite');host.appendChild(s);}
    s.textContent=msg;
  }

  /* ---------------------------------------------------------------- panel */
  function panel(host,d){
    const W=widthFor(host), H=Math.round(W*0.42);
    // Right padding is derived from the longest end label, not fixed: a fixed
    // 14% clipped "Greece: hardship" in the first prototype.
    const longest=Math.max(0,...d.series.filter(s=>s.label).map(s=>s.label.length));
    const padL=(d.yLabel?66:46);
    const ms=measurer(host);
    const padR=labelGutter(ms,(d.series||[]).map(s=>s.label||''),52,W*0.34);
    const padT=12,padB=28;
    const pw=W-padL-padR, ph=H-padT-padB, yrs=d.years;
    const xs=y=>padL+(yrs.length<2?pw/2:(y-yrs[0])/(yrs[yrs.length-1]-yrs[0])*pw);
    let lo=Infinity,hi=-Infinity;
    d.series.forEach(s=>s.values.forEach(v=>{if(v!=null){lo=Math.min(lo,v);hi=Math.max(hi,v);}}));
    // The context layer must be inside the scale, or it draws outside the plot
    // and the chart looks broken. It is background, but it is still data.
    if(d.context)d.context.forEach(c=>c.values.forEach(v=>{
      if(v!=null){lo=Math.min(lo,v);hi=Math.max(hi,v);}}));
    if(!isFinite(lo)){lo=0;hi=1;}
    const pad=(hi-lo)*0.10||1; hi+=pad; lo=(lo<0)?lo-pad:Math.max(0,lo-pad);
    // invertY puts the WORSE value higher, which a rank axis needs: rank 1 is
    // the worst position, and drawing it at the bottom would read backwards.
    const ys=v=>d.invertY ? padT+(v-lo)/(hi-lo)*ph
                          : padT+ph-(v-lo)/(hi-lo)*ph;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||d.caption||'chart'});
    for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4,y=ys(v);
      svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:y,y2:y,class:'gridline'}));
      const t=el('text',{x:padL-6,y:y+3.5,'text-anchor':'end',class:'axis-label'});
      t.textContent=fmt(v,d.dp);svg.appendChild(t);}
    const step=Math.max(1,Math.ceil(yrs.length/(W<480?4:8)));
    // hiddenTicks is opt-in per figure. A series may carry an x position that
    // exists only to hold a gap open -- ESS has no round between 2010/11 and
    // 2020-22, and the null slot that breaks the line there must not be
    // labelled, or it reads as an observation that went missing in that one
    // year rather than a decade with no round at all. The position still
    // occupies its true horizontal distance; only its label is suppressed.
    const hide=new Set((d.hiddenTicks||[]).map(Number));
    yrs.forEach((y,i)=>{if(i%step&&i!==yrs.length-1)return;
      if(hide.has(Number(y)))return;
      const t=el('text',{x:xs(y),y:H-padB+16,'text-anchor':'middle',class:'axis-label'});
      t.textContent=y;svg.appendChild(t);});
    // A series that crosses zero needs the zero drawn. Without it the turn from
    // net exit to net return is invisible: the reader sees a falling line and
    // cannot tell where it changes sign. The area between the series and zero
    // is filled by sign, so the two regimes read at a glance.
    if(lo<0&&hi>0){
      const zy=ys(0), s0=d.series[0];
      if(d.zeroBand&&s0){
        const seg=(want)=>{
          let dd='',open=false;
          s0.values.forEach((v,i)=>{
            const inSeg=v!=null&&((want==='pos'&&v>0)||(want==='neg'&&v<0));
            if(inSeg&&!open){dd+=` M ${xs(yrs[i])},${zy} L ${xs(yrs[i])},${ys(v)}`;open=true;}
            else if(inSeg){dd+=` L ${xs(yrs[i])},${ys(v)}`;}
            else if(open){dd+=` L ${xs(yrs[i-1])},${zy} Z`;open=false;}
          });
          if(open)dd+=` L ${xs(yrs[yrs.length-1])},${zy} Z`;
          return dd;
        };
        [['pos','gr'],['neg','series-3']].forEach(([w,tone])=>{
          const dd=seg(w);
          if(dd)svg.appendChild(el('path',{d:dd,fill:toneVar(tone),
            opacity:0.16,stroke:'none'}));
        });
      }
      svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:zy,y2:zy,class:'zero-line'}));
      const zt=el('text',{x:padL+4,y:zy-5,class:'axis-label',style:'font-weight:700'});
      zt.textContent=d.zeroLabel||'0';svg.appendChild(zt);
    }
    if(d.yLabel){const yl=el('text',{x:16,y:padT+ph/2,class:'axis-label',
      'text-anchor':'middle',transform:`rotate(-90 16 ${padT+ph/2})`});
      yl.textContent=d.yLabel;svg.appendChild(yl);}
    const cur=el('line',{class:'cursor-line',y1:padT,y2:padT+ph,x1:-9,x2:-9});
    svg.appendChild(cur);
    // Context layer: all other countries, faint, behind everything. Passing
    // "context" in the payload rather than as extra series keeps them out of
    // the legend, the end labels, the tooltip rows and the table -- they are
    // background for the eye, not part of the argument.
    const ctxHits=[];
    if(d.context&&d.context.length){
      d.context.forEach(c=>{
        let p='',pen=false;
        c.values.forEach((v,i)=>{if(v==null){pen=false;return;}
          p+=(pen?' L ':' M ')+xs(yrs[i])+','+ys(v);pen=true;});
        if(!p)return;
        const el2=el('path',{d:p,fill:'none',stroke:'var(--chart-neutral)',
          'stroke-width':1,opacity:.22,class:'ctx-line'});
        svg.appendChild(el2);
        ctxHits.push({node:el2,name:c.label,values:c.values});
      });
    }
    const DASH={solid:'',dashed:'6 3',dotted:'2 3'};
    const WT={strong:2.8,normal:1.8,light:1.4};
    const ends=[];
    d.series.forEach(s=>{let p='',pen=false;
      s.values.forEach((v,i)=>{if(v==null){pen=false;return;}
        p+=(pen?' L ':' M ')+xs(yrs[i])+','+ys(v);pen=true;});
      // Line and label take their colour from the SAME tone. Previously the
      // stroke came from a CSS class and the label from the tone, so both
      // "income poverty" series drew as identical grey while their labels were
      // blue and orange -- unreadable, and the reader could not tell which line
      // was which.
      if(p)svg.appendChild(el('path',{d:p,fill:'none',
        stroke:toneVar(s.tone),
        'stroke-width':WT[s.weight||'normal'],
        'stroke-dasharray':DASH[s.style||'solid'],
        opacity:s.weight==='light'?0.75:1}));
      const li=(()=>{for(let i=s.values.length-1;i>=0;i--)if(s.values[i]!=null)return i;return -1;})();
      // With a legend present, end-labelling every series just crowds the right
      // margin. Only the emphasised series get an end label; the legend carries
      // the rest.
      const labelled=d.series.filter(x=>x.label).length<=2||s.weight!=='light';
      if(li>=0&&s.label&&labelled)ends.push({y:ys(s.values[li]),x:xs(yrs[li])+6,s:s});
    });
    // End labels collide when series converge -- three of them stacked on one
    // pixel row in the first prototype. Sort by y and push apart by a minimum
    // gap, keeping each label anchored to its own line by a short leader.
    const GAP=W<480?12:13.5;
    ends.sort((a,b)=>a.y-b.y);
    for(let i=1;i<ends.length;i++)
      if(ends[i].y-ends[i-1].y<GAP)ends[i].y=ends[i-1].y+GAP;
    const overflow=ends.length?Math.max(0,ends[ends.length-1].y-(padT+ph)):0;
    if(overflow)ends.forEach(e=>e.y-=overflow);
    ends.forEach(e=>{
      const yl=ys(e.s.values[(()=>{for(let i=e.s.values.length-1;i>=0;i--)
        if(e.s.values[i]!=null)return i;return 0;})()]);
      if(Math.abs(yl-e.y)>2)
        svg.appendChild(el('line',{x1:e.x-3,x2:e.x+2,y1:yl,y2:e.y-3,
          stroke:toneVar(e.s.tone),'stroke-width':1,opacity:.5}));
      const t=el('text',{x:e.x+4,y:e.y,class:'axis-label',
        style:`fill:var(--${e.s.tone||'chart-neutral'});font-weight:700`});
      // The end label starts at the last data point, so the space it has is
      // whatever remains to the right edge -- not the full margin.
      svg.appendChild(t);fitLabel(t,e.s.label,W-(e.x+4)-2,ms,true);});
    ms.done();
    if(typeof ms!=='undefined'&&ms.done)ms.done();
    host.insertBefore(svg,host.firstChild);
    // The legend carries ONLY what the chart did not label directly. A series
    // named at the end of its own line does not need naming again underneath:
    // that is the same key twice, and it makes the reader look away from the
    // data to learn something already written beside it. Where every series is
    // labelled directly, there is no legend at all.
    const ended=new Set(ends.map(e=>e.s));
    const unlabelled=d.series.filter(s=>s.label&&!ended.has(s));
    if(unlabelled.length){
      const lg=document.createElement('div');lg.className='legend';
      unlabelled.forEach(s=>{
        const i=document.createElement('span');i.className='lg-item';
        i.innerHTML=`<svg width="22" height="8" aria-hidden="true"><line x1="0" y1="4" x2="22" y2="4"
          stroke="var(--${s.tone||'chart-neutral'})" stroke-width="${WT[s.weight||'normal']}"
          stroke-dasharray="${DASH[s.style||'solid']}"/></svg>${s.label}`;
        lg.appendChild(i);});
      host.insertBefore(lg,svg.nextSibling);
    }
    // Hovering a faint line names it. Without this the layer is decorative:
    // the reader can see a distribution but cannot ask what any part of it is.
    ctxHits.forEach(h=>{
      h.node.style.pointerEvents='stroke';
      h.node.addEventListener('mouseenter',()=>{
        h.node.setAttribute('opacity','.9');
        h.node.setAttribute('stroke','var(--chart-label)');
        h.node.setAttribute('stroke-width','2');
        const lbl=el('text',{x:padL+6,y:padT+12,class:'axis-label',
          style:'font-weight:700;fill:var(--chart-label)'});
        lbl.textContent=h.name; lbl.setAttribute('data-ctx-name','1');
        svg.appendChild(lbl);
      });
      h.node.addEventListener('mouseleave',()=>{
        h.node.setAttribute('opacity','.22');
        h.node.setAttribute('stroke','var(--chart-neutral)');
        h.node.setAttribute('stroke-width','1');
        svg.querySelectorAll('[data-ctx-name]').forEach(n=>n.remove());
      });
    });
    const tp=tip(host);
    let idx=-1;
    const show=i=>{ if(i<0||i>=yrs.length)return; idx=i;
      cur.setAttribute('x1',xs(yrs[i]));cur.setAttribute('x2',xs(yrs[i]));
      const rows=d.series.filter(s=>s.label).map(s=>`${s.label}: <b>${fmt(s.values[i],d.dp)}</b>`).join('<br>');
      // Extra rows carry quantities the chart does not plot -- ranks hide the
      // size of the differences, so the underlying values travel with them.
      const extra=(d.extraRows&&d.extraRows[i])?`<br><span style="opacity:.65">
        ${d.extraRows[i]}</span>`:'';
      tp.innerHTML=`<strong>${yrs[i]}</strong><br>${rows}${extra}`;tp.classList.add('on');
      const r=svg.getBoundingClientRect(),hr=host.getBoundingClientRect();
      tp.style.left=Math.min(hr.width-tp.offsetWidth-8,(xs(yrs[i])/W)*r.width+8)+'px';
      tp.style.top='8px';
      say(host,`${yrs[i]}. `+d.series.filter(s=>s.label).map(s=>`${s.label} ${fmt(s.values[i],d.dp)}`).join(', '));
    };
    const near=e=>{const r=svg.getBoundingClientRect();
      const x=(e.clientX-r.left)/r.width*W;
      let best=0,bd=1e9;yrs.forEach((y,i)=>{const dd=Math.abs(xs(y)-x);if(dd<bd){bd=dd;best=i;}});
      show(best);};
    svg.addEventListener('mousemove',near);
    svg.addEventListener('mouseleave',()=>{tp.classList.remove('on');cur.setAttribute('x1',-9);cur.setAttribute('x2',-9);});
    host.addEventListener('keydown',e=>{
      if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();
        show(Math.max(0,Math.min(yrs.length-1,(idx<0?yrs.length-1:idx)+(e.key==='ArrowRight'?1:-1))));}
      if(e.key==='Home'){e.preventDefault();show(0);}
      if(e.key==='End'){e.preventDefault();show(yrs.length-1);}
      if(e.key==='Escape'){tp.classList.remove('on');cur.setAttribute('x1',-9);}
    });
  }

  /* ---------------------------------------------- coefficient (new type) */
  function coefficient(host,d){
    const W=widthFor(host), rowH=W<480?34:30;
    // Same fix the ladder already carries: derive the label gutter from the
    // longest label. A fixed 190 clipped every row label in the conditional
    // figure, the worst by 86px, and no automated check could see it.
    const ms=measurer(host);
    const padL=labelGutter(ms,d.rows.map(r=>r.label),W<480?110:150,W*0.42);
    const padR=labelGutter(ms,d.rows.map(r=>r.right||''),W<480?54:96,W*0.26);
    const padT=26, padB=30;
    const H=padT+d.rows.length*rowH+padB, pw=W-padL-padR;
    let lo=Infinity,hi=-Infinity;
    d.rows.forEach(r=>{lo=Math.min(lo,r.lo,r.est);hi=Math.max(hi,r.hi,r.est);});
    const span=(hi-lo)||1; lo-=span*0.08; hi+=span*0.08;
    const xs=v=>padL+(v-lo)/(hi-lo)*pw;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||d.caption||'coefficient plot'});
    [lo,(lo+hi)/2,hi].forEach(v=>{const t=el('text',{x:xs(v),y:H-8,
      'text-anchor':'middle',class:'axis-label'});t.textContent=fmt(v,2);svg.appendChild(t);});
    if(lo<0&&hi>0)svg.appendChild(el('line',{x1:xs(0),x2:xs(0),y1:padT-6,y2:padT+d.rows.length*rowH,class:'zero-line'}));
    const tp=tip(host); let idx=-1;
    const marks=[];
    d.rows.forEach((r,i)=>{
      const y=padT+i*rowH+rowH/2;
      const tone=r.tone||'chart-neutral';
      svg.appendChild(el('line',{x1:xs(r.lo),x2:xs(r.hi),y1:y,y2:y,
        stroke:toneVar(tone),'stroke-width':2,opacity:.55}));
      const c=outlineNeutral(el('circle',{cx:xs(r.est),cy:y,r:W<480?4.5:5.5,fill:toneVar(tone)}),tone);
      svg.appendChild(c);marks.push({y:y,r:r});
      const lbl=el('text',{x:padL-10,y:y+4,'text-anchor':'end',class:'axis-label',
        style:r.strong?'font-weight:700':''});
      svg.appendChild(lbl);fitLabel(lbl,r.label,padL-12,ms,!!r.strong);
      const vt=el('text',{x:W-padR+8,y:y+4,class:'axis-label',
        style:`fill:var(--${tone});font-weight:600`});
      svg.appendChild(vt);fitLabel(vt,r.right||'',padR-12,ms,true);
    });
    if(typeof ms!=='undefined'&&ms.done)ms.done();
    host.insertBefore(svg,host.firstChild);
    const show=i=>{if(i<0||i>=d.rows.length)return;idx=i;const r=d.rows[i];
      tp.innerHTML=`<strong>${r.label}</strong><br>${r.detail}`;tp.classList.add('on');
      const rc=svg.getBoundingClientRect(),hr=host.getBoundingClientRect();
      tp.style.left=Math.min(hr.width-tp.offsetWidth-8,24)+'px';
      tp.style.top=Math.max(4,(marks[i].y/H)*rc.height-tp.offsetHeight-6)+'px';
      say(host,`${r.label}. ${r.detail.replace(/<[^>]+>/g,' ')}`);};
    svg.addEventListener('mousemove',e=>{const rc=svg.getBoundingClientRect();
      const y=(e.clientY-rc.top)/rc.height*H;let best=0,bd=1e9;
      marks.forEach((m,i)=>{const dd=Math.abs(m.y-y);if(dd<bd){bd=dd;best=i;}});show(best);});
    svg.addEventListener('mouseleave',()=>tp.classList.remove('on'));
    host.addEventListener('keydown',e=>{
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();
        show(Math.max(0,Math.min(d.rows.length-1,(idx<0?-1:idx)+(e.key==='ArrowDown'?1:-1))));}
      if(e.key==='Escape')tp.classList.remove('on');});
  }


  /* -------------------------------------------------------- ladder (new) */
  /* All countries on one measure, ranked, with Greece and the EU marked.
     Answers "is Greece unusual, or at one end of a continuum?" -- which a
     Greece-only time series cannot. */
  function ladder(host,d){
    const W=widthFor(host), n=d.rows.length;
    // Left padding derives from the longest label. A fixed 54 clipped
    // "Long-term unemployment" and "Housing-cost overburden" -- the same bug
    // the panel's right margin had.
    const rowH=W<480?15:17;
    const ms=measurer(host);
    const padL=labelGutter(ms,d.rows.map(r=>r.label),W<480?42:54,W*0.42);
    const padR=W<480?46:64, padT=18, padB=26;
    const H=padT+n*rowH+padB, pw=W-padL-padR;
    let lo=Math.min(0,...d.rows.map(r=>r.value)), hi=Math.max(0,...d.rows.map(r=>r.value));
    const sp=(hi-lo)||1; hi+=sp*0.06; if(lo<0)lo-=sp*0.06;
    const xs=v=>padL+(v-lo)/(hi-lo)*pw;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||'ranked comparison of all countries'});
    [lo,(lo+hi)/2,hi].forEach(v=>{
      svg.appendChild(el('line',{x1:xs(v),x2:xs(v),y1:padT-4,y2:padT+n*rowH,class:'gridline'}));
      const t=el('text',{x:xs(v),y:H-8,'text-anchor':'middle',class:'axis-label'});
      t.textContent=fmt(v,d.dp);svg.appendChild(t);});
    if(d.reference!=null){
      svg.appendChild(el('line',{x1:xs(d.reference),x2:xs(d.reference),
        y1:padT-4,y2:padT+n*rowH,class:'zero-line','stroke-dasharray':'4 3'}));
      const rt=el('text',{x:xs(d.reference),y:padT-7,'text-anchor':'middle',
        class:'axis-label',style:'fill:var(--eu);font-weight:700'});
      rt.textContent=d.referenceLabel||'EU median';svg.appendChild(rt);}
    const marks=[];
    d.rows.forEach((r,i)=>{
      const y=padT+i*rowH+rowH/2, hl=!!r.highlight;
      // Bars grow from zero when the scale spans it, so a negative value reads
      // as a bar to the left rather than a short bar from the axis.
      const base=(lo<0)?xs(0):padL;
      const x0=Math.min(base,xs(r.value)), x1=Math.max(base,xs(r.value));
      svg.appendChild(el('rect',{x:x0,y:y-rowH/2+1,width:Math.max(1,x1-x0),
        height:rowH-3,rx:1.5,
        fill:toneVar(hl?'gr':r.tone),opacity:hl?1:.55}));
      const lb=el('text',{x:padL-6,y:y+3.5,'text-anchor':'end',class:'axis-label',
        style:hl?'fill:var(--gr);font-weight:700':''});
      svg.appendChild(lb);fitLabel(lb,r.label,padL-8,ms,!!hl);
      if(hl||i===0||i===n-1||d.labelAll){const vt=el('text',{
        x:xs(r.value)+(r.value<0?-5:5),y:y+3.5,class:'axis-label',
        'text-anchor':r.value<0?'end':'start',
        style:hl?'fill:var(--gr);font-weight:700':''});
        vt.textContent=fmt(r.value,d.dp);svg.appendChild(vt);}
      marks.push({y:y,r:r,i:i});});
    if(typeof ms!=='undefined'&&ms.done)ms.done();
    host.insertBefore(svg,host.firstChild);
    const tp=tip(host);let idx=-1;
    const show=i=>{if(i<0||i>=marks.length)return;idx=i;const r=marks[i].r;
      tp.innerHTML=`<strong>${r.name||r.label}</strong><br>${fmt(r.value,d.dp)}${d.unit?' '+d.unit:''}`
        +(r.detail?'<br>'+r.detail:'')+`<br><span style="opacity:.6">rank ${i+1} of ${marks.length}</span>`;
      tp.classList.add('on');
      const rc=svg.getBoundingClientRect(),hr=host.getBoundingClientRect();
      tp.style.left=Math.min(hr.width-tp.offsetWidth-8,padL/W*rc.width+10)+'px';
      tp.style.top=Math.max(2,Math.min(rc.height-tp.offsetHeight-4,
        (marks[i].y/H)*rc.height-tp.offsetHeight/2))+'px';
      say(host,`${r.name||r.label}, ${fmt(r.value,d.dp)}, rank ${i+1} of ${marks.length}`);};
    svg.addEventListener('mousemove',e=>{const rc=svg.getBoundingClientRect();
      const y=(e.clientY-rc.top)/rc.height*H;let b=0,bd=1e9;
      marks.forEach((m,i)=>{const dd=Math.abs(m.y-y);if(dd<bd){bd=dd;b=i;}});show(b);});
    svg.addEventListener('mouseleave',()=>tp.classList.remove('on'));
    host.addEventListener('keydown',e=>{
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();
        show(Math.max(0,Math.min(marks.length-1,(idx<0?-1:idx)+(e.key==='ArrowDown'?1:-1))));}
      if(e.key==='Home'){e.preventDefault();show(0);}
      if(e.key==='End'){e.preventDefault();show(marks.length-1);}
      if(e.key==='Escape')tp.classList.remove('on');});
  }


  /* ------------------------------------------------------ dumbbell (new) */
  /* Two states joined per row. Reads a change -- a gap in 2015 against 2024,
     or a between estimate against a within one -- as a single object rather
     than two bars the reader has to subtract. */
  function dumbbell(host,d){
    const W=widthFor(host), rowH=W<480?26:24;
    const ms=measurer(host);
    const padL=labelGutter(ms,d.rows.map(r=>r.label),W<480?104:150,W*0.42);
    const padR=labelGutter(ms,d.rows.map(r=>r.right||''),W<480?52:92,W*0.26);
    const padT=26, padB=32;
    const H=padT+d.rows.length*rowH+padB, pw=W-padL-padR;
    let lo=Infinity,hi=-Infinity;
    d.rows.forEach(r=>{lo=Math.min(lo,r.a,r.b);hi=Math.max(hi,r.a,r.b);});
    const sp=(hi-lo)||1; lo-=sp*0.08; hi+=sp*0.08;
    const xs=v=>padL+(v-lo)/(hi-lo)*pw;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||'paired comparison'});
    [lo,(lo+hi)/2,hi].forEach(v=>{
      svg.appendChild(el('line',{x1:xs(v),x2:xs(v),y1:padT-6,y2:padT+d.rows.length*rowH,class:'gridline'}));
      const t=el('text',{x:xs(v),y:H-10,'text-anchor':'middle',class:'axis-label'});
      t.textContent=fmt(v,d.dp);svg.appendChild(t);});
    if(lo<0&&hi>0){svg.appendChild(el('line',{x1:xs(0),x2:xs(0),y1:padT-6,
      y2:padT+d.rows.length*rowH,class:'zero-line'}));
      const zt=el('text',{x:xs(0),y:padT-10,'text-anchor':'middle',class:'axis-label',
        style:'font-weight:700'});zt.textContent=d.zeroLabel||'0';svg.appendChild(zt);}
    const marks=[];
    d.rows.forEach((r,i)=>{
      const y=padT+i*rowH+rowH/2, tone=r.tone||'chart-neutral';
      svg.appendChild(el('line',{x1:xs(r.a),x2:xs(r.b),y1:y,y2:y,
        stroke:toneVar(tone),'stroke-width':2.5,opacity:.45}));
      svg.appendChild(outlineNeutral(el('circle',{cx:xs(r.a),cy:y,r:4,fill:'var(--chart-neutral)'}),'chart-neutral'));
      svg.appendChild(outlineNeutral(el('circle',{cx:xs(r.b),cy:y,r:5.5,fill:toneVar(tone)}),tone));
      const lb=el('text',{x:padL-10,y:y+4,'text-anchor':'end',class:'axis-label',
        style:r.strong?'font-weight:700':''});
      svg.appendChild(lb);fitLabel(lb,r.label,padL-12,ms,!!r.strong);
      if(r.right){const rt=el('text',{x:W-padR+8,y:y+4,class:'axis-label',
        style:`fill:var(--${tone});font-weight:600`});
        svg.appendChild(rt);fitLabel(rt,r.right,padR-12,ms,true);}
      marks.push({y:y,r:r});});
    if(typeof ms!=='undefined'&&ms.done)ms.done();
    host.insertBefore(svg,host.firstChild);
    if(d.legendA||d.legendB){
      const lg=document.createElement('div');lg.className='legend';
      lg.innerHTML=`<span class="lg-item"><svg width="12" height="12" aria-hidden="true">
        <circle cx="6" cy="6" r="4" fill="var(--chart-neutral)" stroke="var(--chart-neutral-edge)" stroke-width="1"/></svg>${d.legendA||'start'}</span>
        <span class="lg-item"><svg width="12" height="12" aria-hidden="true">
        <circle cx="6" cy="6" r="5" fill="var(--gr)"/></svg>${d.legendB||'end'}</span>`;
      host.insertBefore(lg,svg.nextSibling);}
    const tp=tip(host);let idx=-1;
    const show=i=>{if(i<0||i>=marks.length)return;idx=i;const r=marks[i].r;
      tp.innerHTML=`<strong>${r.label}</strong><br>${d.legendA||'start'}: ${fmt(r.a,d.dp)}`
        +`<br>${d.legendB||'end'}: <b>${fmt(r.b,d.dp)}</b>`+(r.detail?'<br>'+r.detail:'');
      tp.classList.add('on');
      const rc=svg.getBoundingClientRect(),hr=host.getBoundingClientRect();
      tp.style.left=Math.min(hr.width-tp.offsetWidth-8,20)+'px';
      tp.style.top=Math.max(2,Math.min(rc.height-tp.offsetHeight-4,
        (marks[i].y/H)*rc.height-tp.offsetHeight-6))+'px';
      say(host,`${r.label}, ${fmt(r.a,d.dp)} to ${fmt(r.b,d.dp)}`);};
    svg.addEventListener('mousemove',e=>{const rc=svg.getBoundingClientRect();
      const y=(e.clientY-rc.top)/rc.height*H;let b=0,bd=1e9;
      marks.forEach((m,i)=>{const dd=Math.abs(m.y-y);if(dd<bd){bd=dd;b=i;}});show(b);});
    svg.addEventListener('mouseleave',()=>tp.classList.remove('on'));
    host.addEventListener('keydown',e=>{
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();
        show(Math.max(0,Math.min(marks.length-1,(idx<0?-1:idx)+(e.key==='ArrowDown'?1:-1))));}
      if(e.key==='Escape')tp.classList.remove('on');});
  }

  /* ------------------------------------------------------- heatmap (new) */
  /* A correlation matrix. Deliberately small by default: a 31x31 grid contains
     everything and communicates almost nothing, so the main view carries the
     outcomes and the frozen construct representatives only. */
  function heatmap(host,d){
    const W=widthFor(host);
    const ms=measurer(host);
    const labW=labelGutter(ms,d.rows.map(r=>r.label),W<480?96:150,W*0.40);
    const cell=Math.max(16,Math.min(34,(W-labW-16)/d.cols.length));
    const top=Math.min(120,labW*0.8);
    const H=top+d.rows.length*cell+10;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||'correlation matrix'});
    d.cols.forEach((c,j)=>{const x=labW+j*cell+cell/2;
      const t=el('text',{x:x,y:top-6,class:'axis-label','text-anchor':'start',
        transform:`rotate(-55 ${x} ${top-6})`});t.textContent=c;svg.appendChild(t);});
    const marks=[];
    d.rows.forEach((r,i)=>{
      const y=top+i*cell;
      const lb=el('text',{x:labW-8,y:y+cell/2+3.5,'text-anchor':'end',class:'axis-label'});
      svg.appendChild(lb);fitLabel(lb,r.label,labW-10,ms,false);
      r.values.forEach((v,j)=>{
        const x=labW+j*cell;
        const mag=v==null?0:Math.min(1,Math.abs(v));
        const tone=v==null?'div-zero':(v<0?'div-neg':'div-pos');
        const rect=el('rect',{x:x+1,y:y+1,width:cell-2,height:cell-2,rx:2,
          fill:toneVar(tone),opacity:v==null?0.10:0.30+mag*0.65});
        svg.appendChild(rect);
        // A mechanical pair is outlined, not dotted: the reader needs to see
        // WHICH cells cannot be read as independent relationships.
        if(d.flags&&d.flags[i]&&d.flags[i][j]){
          svg.appendChild(el('rect',{x:x+1,y:y+1,width:cell-2,height:cell-2,rx:2,
            fill:'none',stroke:'var(--text-primary)','stroke-width':1.6,
            'stroke-dasharray':'2.5 2'}));}
        marks.push({x:x,y:y,i:i,j:j,v:v});});});
    if(typeof ms!=='undefined'&&ms.done)ms.done();
    host.insertBefore(svg,host.firstChild);
    const lg=document.createElement('div');lg.className='legend';
    lg.innerHTML=`<span class="lg-item"><svg width="34" height="10" aria-hidden="true">
      <rect width="11" height="10" fill="var(--div-neg)" opacity=".85"/>
      <rect x="11" width="11" height="10" fill="var(--div-zero)" opacity=".3"/>
      <rect x="22" width="11" height="10" fill="var(--div-pos)" opacity=".85"/></svg>
      negative &rarr; positive</span>`
      +(d.flagLabel?`<span class="lg-item"><svg width="12" height="12" aria-hidden="true">
      <rect x="1" y="1" width="10" height="10" fill="none" stroke="var(--text-primary)"
      stroke-width="1.6" stroke-dasharray="2.5 2"/></svg>${d.flagLabel}</span>`:'');
    host.insertBefore(lg,svg.nextSibling);
    const tp=tip(host);let idx=-1;
    const show=k=>{if(k<0||k>=marks.length)return;idx=k;const m=marks[k];
      const flag=d.flags&&d.flags[m.i]&&d.flags[m.i][m.j];
      tp.innerHTML=`<strong>${d.rows[m.i].label}</strong><br>vs ${d.cols[m.j]}`
        +`<br>r = <b>${m.v==null?'&mdash;':m.v.toFixed(3)}</b>`
        +(flag?`<br><span style="color:var(--text-primary)">${d.flagExplain||d.flagLabel}</span>`:'');
      tp.classList.add('on');
      const rc=svg.getBoundingClientRect(),hr=host.getBoundingClientRect();
      tp.style.left=Math.min(hr.width-tp.offsetWidth-8,
        Math.max(4,(m.x/W)*rc.width-tp.offsetWidth/2))+'px';
      tp.style.top=Math.max(2,(m.y/H)*rc.height-tp.offsetHeight-4)+'px';
      say(host,`${d.rows[m.i].label} versus ${d.cols[m.j]}, r ${m.v==null?'missing':m.v.toFixed(3)}`);};
    svg.addEventListener('mousemove',e=>{const rc=svg.getBoundingClientRect();
      const x=(e.clientX-rc.left)/rc.width*W, y=(e.clientY-rc.top)/rc.height*H;
      let b=-1,bd=1e9;marks.forEach((m,k)=>{
        const dd=Math.abs(m.x+cell/2-x)+Math.abs(m.y+cell/2-y);if(dd<bd){bd=dd;b=k;}});
      if(b>=0)show(b);});
    svg.addEventListener('mouseleave',()=>tp.classList.remove('on'));
    host.addEventListener('keydown',e=>{
      const step={ArrowRight:1,ArrowLeft:-1,ArrowDown:d.cols.length,ArrowUp:-d.cols.length}[e.key];
      if(step){e.preventDefault();show(Math.max(0,Math.min(marks.length-1,(idx<0?0:idx)+step)));}
      if(e.key==='Escape')tp.classList.remove('on');});
  }


  /* ------------------------------------------------------------- scatter */
  /* Country-years as points. Used with country means removed, so the cloud
     shows co-movement WITHIN countries rather than differences between them. */
  function scatter(host,d){
    const W=widthFor(host), H=Math.round(W*0.62);
    const padL=56,padR=18,padT=16,padB=46;
    const pw=W-padL-padR, ph=H-padT-padB;
    const xs_=d.points.map(p=>p.x), ys_=d.points.map(p=>p.y);
    const xlo=Math.min(...xs_),xhi=Math.max(...xs_),ylo=Math.min(...ys_),yhi=Math.max(...ys_);
    const px=(xhi-xlo)*0.06||1, py=(yhi-ylo)*0.06||1;
    const xs=v=>padL+(v-(xlo-px))/((xhi+px)-(xlo-px))*pw;
    const ys=v=>padT+ph-(v-(ylo-py))/((yhi+py)-(ylo-py))*ph;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||'scatter'});
    for(let i=0;i<=4;i++){const v=(ylo-py)+((yhi+py)-(ylo-py))*i/4,y=ys(v);
      svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:y,y2:y,class:'gridline'}));
      const t=el('text',{x:padL-6,y:y+3.5,'text-anchor':'end',class:'axis-label'});
      t.textContent=fmt(v,d.dp);svg.appendChild(t);}
    for(let i=0;i<=4;i++){const v=(xlo-px)+((xhi+px)-(xlo-px))*i/4;
      const t=el('text',{x:xs(v),y:H-padB+16,'text-anchor':'middle',class:'axis-label'});
      t.textContent=fmt(v,d.dp);svg.appendChild(t);}
    if(xlo<0&&xhi>0)svg.appendChild(el('line',{x1:xs(0),x2:xs(0),y1:padT,y2:padT+ph,class:'zero-line'}));
    if(ylo<0&&yhi>0)svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:ys(0),y2:ys(0),class:'zero-line'}));
    // least-squares line, drawn because the figure is about co-movement
    const n=d.points.length,mx=xs_.reduce((a,b)=>a+b,0)/n,my=ys_.reduce((a,b)=>a+b,0)/n;
    let sxy=0,sxx=0;d.points.forEach(p=>{sxy+=(p.x-mx)*(p.y-my);sxx+=(p.x-mx)**2;});
    if(sxx>0){const b1=sxy/sxx,b0=my-b1*mx;
      svg.appendChild(el('line',{x1:xs(xlo-px),y1:ys(b0+b1*(xlo-px)),
        x2:xs(xhi+px),y2:ys(b0+b1*(xhi+px)),stroke:'var(--text-secondary)',
        'stroke-width':1.6,'stroke-dasharray':'5 3',opacity:.8}));}
    const marks=[];
    d.points.forEach(p=>{const c=el('circle',{cx:xs(p.x),cy:ys(p.y),
      r:p.highlight?4.5:2.8,fill:`var(--${p.highlight?'gr':'text-muted'})`,
      opacity:p.highlight?1:.45});svg.appendChild(c);marks.push({x:xs(p.x),y:ys(p.y),p:p});});
    const xt=el('text',{x:padL+pw/2,y:H-10,'text-anchor':'middle',class:'axis-label'});
    xt.textContent=d.xLabel||'';svg.appendChild(xt);
    const yt=el('text',{x:14,y:padT+ph/2,class:'axis-label','text-anchor':'middle',
      transform:`rotate(-90 14 ${padT+ph/2})`});yt.textContent=d.yLabel||'';svg.appendChild(yt);
    if(d.r!=null){const rt=el('text',{x:W-padR-4,y:padT+12,'text-anchor':'end',
      class:'axis-label',style:'font-weight:700'});rt.textContent='r = '+d.r;svg.appendChild(rt);}
    if(typeof ms!=='undefined'&&ms.done)ms.done();
    host.insertBefore(svg,host.firstChild);
    const tp=tip(host);let idx=-1;
    const show=i=>{if(i<0||i>=marks.length)return;idx=i;const p=marks[i].p;
      tp.innerHTML=`<strong>${p.label}</strong><br>${fmt(p.x,d.dp)} , ${fmt(p.y,d.dp)}`;
      tp.classList.add('on');
      const rc=svg.getBoundingClientRect(),hr=host.getBoundingClientRect();
      tp.style.left=Math.min(hr.width-tp.offsetWidth-8,
        Math.max(4,(marks[i].x/W)*rc.width-tp.offsetWidth/2))+'px';
      tp.style.top=Math.max(2,(marks[i].y/H)*rc.height-tp.offsetHeight-8)+'px';
      say(host,`${p.label}, ${fmt(p.x,d.dp)} and ${fmt(p.y,d.dp)}`);};
    svg.addEventListener('mousemove',e=>{const rc=svg.getBoundingClientRect();
      const x=(e.clientX-rc.left)/rc.width*W,y=(e.clientY-rc.top)/rc.height*H;
      let b=-1,bd=1e9;marks.forEach((m,i)=>{const dd=(m.x-x)**2+(m.y-y)**2;
        if(dd<bd){bd=dd;b=i;}});if(b>=0&&bd<900)show(b);else tp.classList.remove('on');});
    svg.addEventListener('mouseleave',()=>tp.classList.remove('on'));
    host.addEventListener('keydown',e=>{
      if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();
        show(Math.max(0,Math.min(marks.length-1,(idx<0?-1:idx)+(e.key==='ArrowRight'?1:-1))));}
      if(e.key==='Escape')tp.classList.remove('on');});
  }

  const KINDS={panel:panel,coefficient:coefficient,ladder:ladder,dumbbell:dumbbell,heatmap:heatmap,scatter:scatter};


  // VIEW SWITCHING. Some questions need more than one look -- the real
  // threshold and the anchored comparison, or AROPE by component, age,
  // household and shift-share. Views live in one figure so the reader does not
  // lose the question while changing the picture.
  function mountViews(host){
    const payloads=[...host.querySelectorAll('script[type="application/json"]')];
    if(payloads.length<2)return false;
    const bar=document.createElement('div');bar.className='viewbar';
    bar.setAttribute('role','tablist');
    const draw=i=>{
      const d=JSON.parse(payloads[i].textContent);
      host.querySelectorAll('svg,.legend,.tip,.sr').forEach(n=>n.remove());
      (KINDS[payloads[i].dataset.kind||host.dataset.chart]||panel)(host,d);
      [...bar.children].forEach((b,j)=>{b.setAttribute('aria-selected',j===i?'true':'false');
        b.tabIndex=j===i?0:-1;});
      // Scope from the FIGURE, not the chart host: the fallback tables live in
      // the <details> sibling, so querying the host matched nothing and every
      // view's table stayed visible at once.
      const fig=host.closest('figure')||document;
      fig.querySelectorAll('table[data-view]').forEach(tb=>{
        tb.hidden = tb.dataset.view !== String(i);});
    };
    payloads.forEach((pl,i)=>{
      const b=document.createElement('button');b.type='button';b.className='viewbtn';
      b.setAttribute('role','tab');b.textContent=pl.dataset.label||('View '+(i+1));
      b.addEventListener('click',()=>draw(i));
      b.addEventListener('keydown',e=>{
        if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();
          const j=(i+(e.key==='ArrowRight'?1:-1)+payloads.length)%payloads.length;
          bar.children[j].focus();draw(j);}});
      bar.appendChild(b);});
    host.parentNode.insertBefore(bar,host);
    draw(0);
    return true;
  }

  function mount(){
    document.querySelectorAll('[data-chart]').forEach(host=>{
      if(host.dataset.drawn)return;
      if(mountViews(host)){host.dataset.drawn='1';return;}
      const payload=host.querySelector('script[type="application/json"]');
      if(!payload)return;
      const d=JSON.parse(payload.textContent);
      const fn=KINDS[host.dataset.chart];
      if(!fn)return;
      // Remove the whole of the previous drawing, not just its canvas. This
      // took out old <svg> only, so every redraw appended another legend -- and
      // because a legend's swatches are themselves <svg>, the stale legend was
      // stripped of its swatches and left behind as a row of bare text.
      host.querySelectorAll(':scope > svg, :scope > .legend').forEach(s=>s.remove());
      fn(host,d);
      host.dataset.drawn='1';
    });
  }
  function redraw(){document.querySelectorAll('.viewbar').forEach(b=>b.remove());
    document.querySelectorAll('[data-chart]').forEach(h=>h.dataset.drawn='');mount();}
  document.addEventListener('DOMContentLoaded',mount);
  if(document.readyState!=='loading')mount();
  let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(redraw,180);});
})();
"""



# ---------------------------------------------------------------------------
# ONE CANONICAL ROW STRUCTURE FEEDS BOTH THE CHART AND THE TABLE.
#
# Row-count agreement is false confidence: a chart and its fallback can carry
# the same number of rows and different numbers in them and still pass. The
# only way to be sure they agree is to stop generating them separately.
#
# A Series is built once. `chart_payload()` and `fallback_table()` both read it,
# and `checksum()` hashes the exact labels and values so the build can prove the
# two were derived from the same thing.
# ---------------------------------------------------------------------------
import hashlib


class Series:
    """Canonical data for one figure: labelled rows of (label, values)."""

    def __init__(self, columns, dp=1, title=""):
        self.columns = list(columns)     # header for the value columns
        self.rows = []                   # (label, [values], meta dict)
        self.dp = dp
        self.title = title

    def add(self, label, values, **meta):
        if len(values) != len(self.columns):
            raise ValueError(
                f"{label}: {len(values)} values against {len(self.columns)} columns")
        self.rows.append((label, list(values), meta))
        return self

    def canonical(self):
        """The exact labels and rounded values both renderers will use."""
        out = []
        for label, vals, _ in self.rows:
            out.append([str(label)] + [
                "" if v is None or v != v else f"{float(v):.{self.dp}f}"
                for v in vals])
        return out

    def checksum(self):
        blob = json.dumps({"cols": self.columns, "rows": self.canonical()},
                          sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    def fallback_table(self, first_header="", numeric=True, view=None):
        head = "".join(f'<th class="num">{html.escape(c)}</th>'
                       if numeric else f"<th>{html.escape(c)}</th>"
                       for c in self.columns)
        body = []
        for row in self.canonical():
            cells = "".join(f'<td class="num">{c or "&mdash;"}</td>'
                            if numeric else f"<td>{c or '&mdash;'}</td>"
                            for c in row[1:])
            body.append(f"<tr><td>{html.escape(row[0])}</td>{cells}</tr>")
        v = f' data-view="{view}"' if view is not None else ""
        cap = (f"<caption>{html.escape(str(self.title))}</caption>"
               if getattr(self, "title", "") else "")
        return (f'<table data-checksum="{self.checksum()}"{v}>{cap}'
                f'<thead><tr><th>{html.escape(first_header)}</th>{head}</tr></thead>'
                f"<tbody>{''.join(body)}</tbody></table>")


def figure(fid, caption, question, badge, host_kind, payload, fallback_html,
           caveat="", appendix_link="", checksum=""):
    """One figure: chart, badge, caveat, and an accessible table fallback.

    The fallback is always in the DOM, so screen readers and print both reach
    the numbers whether or not the chart draws.
    """
    # pandas reads an empty manifest cell as NaN, a float, which html.escape
    # cannot take. Coerce before testing truthiness.
    caveat = "" if caveat is None or caveat != caveat else str(caveat).strip()
    cav = (f'<p class="fig-caveat"><strong>Read with this.</strong> '
           f'{html.escape(caveat)}</p>' if caveat else "")
    link = (f' <a href="{appendix_link}">Full evidence in the appendix</a>.'
            if appendix_link else "")
    # DO NOT html-escape the payload. Script-tag content is raw text, so
    # entities survive JSON.parse as literal characters and the tooltip then
    # displayed "<span style='opacity:.6'>real_wages_idx</span>" verbatim.
    # Escaping "</" is the only thing needed, and it is what prevents the JSON
    # from terminating the script element early.
    data = json.dumps(payload).replace("</", "<\\/")
    return f"""<figure class="figure" id="{fid}">
<figcaption>{caption}</figcaption>
<div class="fig-meta"><span class="badge">{html.escape(badge)}</span>
<span class="fig-q">{html.escape(question)}</span></div>
<div class="chart-live" data-chart="{host_kind}" tabindex="0"
     data-checksum="{checksum}" aria-describedby="{fid}-fb">
<script type="application/json">{data}</script>
</div>{cav}
<details class="fallback" id="{fid}-fb"><summary>Show the numbers{link}</summary>
{fallback_html}</details>
</figure>"""


def build_stamp():
    """Short commit and build time, so a stale preview is visible on its face."""
    import subprocess
    from datetime import datetime
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[1]
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                             capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=root,
                                    capture_output=True, text=True).stdout.strip())
    except Exception:
        sha, dirty = "unknown", False
    when = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (f'<footer class="stamp">Built {when} from commit <code>{sha}</code>'
            f'{" + uncommitted changes" if dirty else ""}. '
            "If this does not match the current commit, the page is stale &mdash; "
            "reopen the file rather than refreshing.</footer>")


STAMP_CSS = """.stamp{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--border);
font:.72rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--text-muted)}
.stamp code{background:var(--surface-2);padding:.1em .35em;border-radius:3px}"""
