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
}


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
.gridline{stroke:var(--border);stroke-width:1}
.axis-label{fill:var(--text-muted);font:11px ui-sans-serif,system-ui,sans-serif}
.line-faint{fill:none;stroke:var(--text-muted);stroke-width:1;opacity:.28}
.line-eu{fill:none;stroke:var(--eu);stroke-width:2.2;stroke-dasharray:5 3}
.line-gr{fill:none;stroke:var(--gr);stroke-width:2.8}
.zero-line{stroke:var(--text-muted);stroke-width:1.4}
.cursor-line{stroke:var(--text-secondary);stroke-width:1;stroke-dasharray:3 3}
.tip{position:absolute;pointer-events:none;background:var(--surface-2);
border:1px solid var(--border);border-radius:5px;padding:.45rem .6rem;
font:.76rem/1.45 ui-sans-serif,system-ui,sans-serif;color:var(--text-primary);
box-shadow:0 3px 12px rgba(0,0,0,.14);max-width:15rem;z-index:5;opacity:0;
transition:opacity .1s}
.tip.on{opacity:1}
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
  function widthFor(host){ const w=host.clientWidth||640; return Math.max(320,Math.min(920,w)); }

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
    const padL=46,padR=Math.min(W*0.34,Math.max(52,longest*6.2+14)),padT=12,padB=28;
    const pw=W-padL-padR, ph=H-padT-padB, yrs=d.years;
    const xs=y=>padL+(yrs.length<2?pw/2:(y-yrs[0])/(yrs[yrs.length-1]-yrs[0])*pw);
    let lo=Infinity,hi=-Infinity;
    d.series.forEach(s=>s.values.forEach(v=>{if(v!=null){lo=Math.min(lo,v);hi=Math.max(hi,v);}}));
    if(!isFinite(lo)){lo=0;hi=1;}
    const pad=(hi-lo)*0.10||1; hi+=pad; lo=(lo<0)?lo-pad:Math.max(0,lo-pad);
    const ys=v=>padT+ph-(v-lo)/(hi-lo)*ph;
    const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
      'aria-label':d.alt||d.caption||'chart'});
    for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4,y=ys(v);
      svg.appendChild(el('line',{x1:padL,x2:W-padR,y1:y,y2:y,class:'gridline'}));
      const t=el('text',{x:padL-6,y:y+3.5,'text-anchor':'end',class:'axis-label'});
      t.textContent=fmt(v,d.dp);svg.appendChild(t);}
    const step=Math.max(1,Math.ceil(yrs.length/(W<480?4:8)));
    yrs.forEach((y,i)=>{if(i%step&&i!==yrs.length-1)return;
      const t=el('text',{x:xs(y),y:H-padB+16,'text-anchor':'middle',class:'axis-label'});
      t.textContent=y;svg.appendChild(t);});
    const cur=el('line',{class:'cursor-line',y1:padT,y2:padT+ph,x1:-9,x2:-9});
    svg.appendChild(cur);
    const ends=[];
    d.series.forEach(s=>{let p='',pen=false;
      s.values.forEach((v,i)=>{if(v==null){pen=false;return;}
        p+=(pen?' L ':' M ')+xs(yrs[i])+','+ys(v);pen=true;});
      if(p)svg.appendChild(el('path',{d:p,class:s.cls||'line-faint'}));
      const li=(()=>{for(let i=s.values.length-1;i>=0;i--)if(s.values[i]!=null)return i;return -1;})();
      if(li>=0&&s.label)ends.push({y:ys(s.values[li]),x:xs(yrs[li])+6,s:s});
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
          stroke:`var(--${e.s.tone||'text-muted'})`,'stroke-width':1,opacity:.5}));
      const t=el('text',{x:e.x+4,y:e.y,class:'axis-label',
        style:`fill:var(--${e.s.tone||'text-muted'});font-weight:700`});
      t.textContent=e.s.label;svg.appendChild(t);});
    host.insertBefore(svg,host.firstChild);
    const tp=tip(host);
    let idx=-1;
    const show=i=>{ if(i<0||i>=yrs.length)return; idx=i;
      cur.setAttribute('x1',xs(yrs[i]));cur.setAttribute('x2',xs(yrs[i]));
      const rows=d.series.filter(s=>s.label).map(s=>`${s.label}: <b>${fmt(s.values[i],d.dp)}</b>`).join('<br>');
      tp.innerHTML=`<strong>${yrs[i]}</strong><br>${rows}`;tp.classList.add('on');
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
    const padL=W<480?110:190, padR=W<480?54:96, padT=26, padB=30;
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
      const tone=r.tone||'text-muted';
      svg.appendChild(el('line',{x1:xs(r.lo),x2:xs(r.hi),y1:y,y2:y,
        stroke:`var(--${tone})`,'stroke-width':2,opacity:.55}));
      const c=el('circle',{cx:xs(r.est),cy:y,r:W<480?4.5:5.5,fill:`var(--${tone})`});
      svg.appendChild(c);marks.push({y:y,r:r});
      const lbl=el('text',{x:padL-10,y:y+4,'text-anchor':'end',class:'axis-label',
        style:r.strong?'font-weight:700':''});
      lbl.textContent=r.label;svg.appendChild(lbl);
      const vt=el('text',{x:W-padR+8,y:y+4,class:'axis-label',
        style:`fill:var(--${tone});font-weight:600`});
      vt.textContent=r.right||'';svg.appendChild(vt);
    });
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

  const KINDS={panel:panel,coefficient:coefficient};

  function mount(){
    document.querySelectorAll('[data-chart]').forEach(host=>{
      if(host.dataset.drawn)return;
      const payload=host.querySelector('script[type="application/json"]');
      if(!payload)return;
      const d=JSON.parse(payload.textContent);
      const fn=KINDS[host.dataset.chart];
      if(!fn)return;
      host.querySelectorAll('svg').forEach(s=>s.remove());
      fn(host,d);
      host.dataset.drawn='1';
    });
  }
  function redraw(){document.querySelectorAll('[data-chart]').forEach(h=>h.dataset.drawn='');mount();}
  document.addEventListener('DOMContentLoaded',mount);
  if(document.readyState!=='loading')mount();
  let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(redraw,180);});
})();
"""


def figure(fid, caption, question, badge, host_kind, payload, fallback_html,
           caveat="", appendix_link=""):
    """One figure: chart, badge, caveat, and an accessible table fallback.

    The fallback is always in the DOM, so screen readers and print both reach
    the numbers whether or not the chart draws.
    """
    cav = (f'<p class="fig-caveat"><strong>Read with this.</strong> '
           f'{html.escape(caveat)}</p>' if caveat else "")
    link = (f' <a href="{appendix_link}">Full evidence in the appendix</a>.'
            if appendix_link else "")
    data = html.escape(json.dumps(payload), quote=False).replace("</", "<\\/")
    return f"""<figure class="figure" id="{fid}">
<figcaption>{caption}</figcaption>
<div class="fig-meta"><span class="badge">{html.escape(badge)}</span>
<span class="fig-q">{html.escape(question)}</span></div>
<div class="chart-live" data-chart="{host_kind}" tabindex="0"
     aria-describedby="{fid}-fb">
<script type="application/json">{data}</script>
</div>{cav}
<details class="fallback" id="{fid}-fb"><summary>Show the numbers{link}</summary>
{fallback_html}</details>
</figure>"""
