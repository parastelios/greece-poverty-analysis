"""Assemble the narrative companion.

The earlier companion's voice is kept: direct, concrete, no jargon. Its
structure is not. A magazine reader does not experience eighteen findings as
eighteen findings; they experience a succession of resets. This version is
edited into seven sections that argue in sequence -- the puzzle, the moving
ruler, the material footprint, the uneven recovery, the accumulated past, the
limits of the evidence, and what the piece does not settle -- rather than one
chapter per technical-report result.

Findings and context are anchored in the markup for the acceptance checks. A
general reader sees no identifier, no evidence vocabulary and no variable name.
"""
import html
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
OUT, PROC = ROOT / "output", ROOT / "data" / "processed"

claims = pd.read_csv(PROC / "e_final_claims.csv").set_index("id")
ctx = pd.read_csv(PROC / "context_register.csv").set_index("id")
DISPLAY_CODES = sorted(ce.DISPLAY, key=len, reverse=True)

SPEC_WORDS = {
    "the frozen P3 specification": "the main model",
    "the frozen model": "the main model",
    "machine-blocked from every output document": "kept out of every document",
}


def reader_text(s):
    s = str(s)
    for code in DISPLAY_CODES:
        s = s.replace(f" ({code})", "")
    for a, b in SPEC_WORDS.items():
        s = s.replace(a, b)
    return s


FIG_SOURCE = {}
for n in (1, 2, 3, 4):
    page = (OUT / "build" / f"batch{n}.html").read_text()
    for m in re.finditer(r'<figure class="figure" id="(F\d+)">.*?</figure>', page, re.S):
        FIG_SOURCE[m.group(1)] = m.group(0)

# A general reader needs fewer charts than the technical report carries, and
# each has to earn a new turn in the argument rather than complete the
# record. Eight figures, one per section at minimum, chosen so that no two
# make the same point:
#   F1   the paradox itself                                 -- section 1
#   F3   the threshold that moved                           -- section 2
#   F8   affordability tracking reported hardship            -- section 3
#   F21  breadth: how many separate measures put Greece      -- section 3
#        in Europe's worst fifth
#   F7   which gaps closed and which widened                 -- section 4
#        (replaces the three separate tabs of F10 lifted as
#        F10A/F10B/F10C in the previous version -- three
#        near-identical trend-line beats in a row read as a
#        variable catalogue, not a story gathering force)
#   F11  the historical scars                                -- section 5
#   F13  between countries, not within them, simplified to    -- section 6
#        its first view only (subfig() below) -- the second
#        view (year-on-year first differences) belongs in the
#        appendix, not in a piece already asking a general
#        reader to hold one distinction in mind at a time
#   F14  model dependence, the central limitation             -- section 6
#
# F15 held a slot until it was removed: the report itself demoted it out of
# its own main path (report_visual_manifest.csv: venue "appendix", not
# "report") because three incompatible scales -- a percentage, a net balance,
# a 0-10 rating -- don't share one axis, and replaced it with a generated
# table, T-DOMAIN. domain_table() below gives that chapter the same honest
# table instead of the chart the report itself rejected.
NARRATIVE_FIGS = ["F1", "F3", "F8", "F21", "F7", "F11", "F13A", "F14"]

# Non-figure blocks that travel from the batch pages. The pre-crisis comparison
# is six rows with a decade missing from the middle, which is a table.
BLOCKS = {}
for _n in (1, 2, 3, 4):
    _page = (OUT / "build" / f"batch{_n}.html").read_text()
    for _m in re.finditer(r'<div class="(ess-table)">.*?</p></div>', _page, re.S):
        BLOCKS[_m.group(1)] = _m.group(0)


def block(key):
    if key not in BLOCKS:
        raise SystemExit(f"block '{key}' not found in any batch page")
    return BLOCKS[key]


def domain_table():
    """The three-domain comparison, as a table -- not a chart.

    F15 plotted these three rows on one axis in an earlier version of this
    project and was demoted out of the report's own main path for it: a
    percentage, a net balance and a 0-10 rating share no scale, and the
    report replaced it with T-DOMAIN, a generated table, for exactly that
    reason. This reads the same e_f15_domains.csv T-DOMAIN reads, so the two
    can never disagree, and gives this chapter the honest form of the same
    comparison instead of a chart the report itself rejected.
    """
    d = pd.read_csv(PROC / "e_f15_domains.csv")
    rows = ""
    for r in d.itertuples():
        gr = f"{r.greece:+.1f}" if r.indicator == "Financial expectations" else f"{r.greece:g}{'%' if r.unit == '%' else ''}"
        eu = f"{r.eu_median:+.1f}" if r.indicator == "Financial expectations" else f"{r.eu_median:g}{'%' if r.unit == '%' else ''}"
        ord_ = {1: "1st", 2: "2nd", 3: "3rd"}.get(r.greece_position_worst_first,
                                                    f"{r.greece_position_worst_first}th")
        rows += (f"<tr><td>{r.indicator}</td><td class='num'>{gr}</td>"
                 f"<td class='num'>{eu}</td>"
                 f"<td class='num'>{ord_} of {r.countries}, worst first</td></tr>")
    return (f'<div class="mini-table"><table><thead><tr>'
            f"<th>Measure</th><th>Greece</th><th>EU median</th>"
            f"<th>Greece&rsquo;s position</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")
# The selection is FROZEN. Figure ids changed meaning during the figure work --
# what an id pointed at was not stable -- so this list records a decision about
# what this document argues, and any change to it has to be a decision too.
_FROZEN = ['F1', 'F3', 'F8', 'F21', 'F7', 'F11', 'F13A', 'F14']
if PAPER_FIGS != _FROZEN if "PAPER_FIGS" in dir() else NARRATIVE_FIGS != _FROZEN:
    raise SystemExit(
        "the narrative figure selection changed; update _FROZEN deliberately")

_used = []


def fig(fid, caption=None):
    """Place a built figure. Numbering is NOT assigned here.

    A placeholder token is resolved once by resolve_fig_nums() against the
    FINAL assembled document, left to right -- the order a reader meets it,
    not the order fig() happened to be called while this file was defining
    sections.

    CAPTION, if given, replaces the report's own caption text for this
    figure IN THE NARRATIVE ONLY -- the report's copy (and the appendix's
    superset copy of it) is untouched, since this only rewrites the
    <figcaption> text after lifting the figure, not the source it was
    lifted from. The report's caption states the finding precisely; a
    magazine reader meets the finding in the surrounding prose first and
    needs the caption to pull them toward it, not restate it -- the
    editorial split this project settled on is "section title: narrative
    pull, figure caption: clear finding, question: technical precision",
    and only the caption moves.
    """
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    html_ = FIG_SOURCE[fid]
    if caption is not None:
        html_ = re.sub(r"<figcaption>.*?</figcaption>",
                        f"<figcaption>{caption}</figcaption>", html_, count=1, flags=re.S)
    html_ = html_.replace(
        "<figcaption>", f'<figcaption><span class="fignum">Figure {{fig:{fid}}}</span> ', 1)
    html_ = re.sub(
        r'(<p class="fig-caveat">.*?</p>)',
        r'<details class="fig-methods"><summary>Methods and limits</summary>\1</details>',
        html_, count=1, flags=re.S)
    return html_


def subfig(fid, parent_fid, view_index, caption, question):
    """One view of a multi-view report figure, lifted out as its own
    standalone figure with a fresh caption and question -- not exposed as a
    tab choice.

    Each view's payload and fallback table are already self-contained in the
    built HTML (chart_engine emits one <script> and one checksummed <table
    data-view="N"> per view), so no new chart needs building -- only a new
    figure shell and id, so fid must be unique and (like every real figure
    id) match [A-Z0-9]+ for resolve_fig_nums().
    """
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    src = FIG_SOURCE[parent_fid]
    scripts = re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', src, re.S)
    tables = re.findall(r'<table data-checksum="[^"]*" data-view="\d+">.*?</table>', src, re.S)
    chart_types = re.findall(r'<div class="chart-live" data-chart="([^"]+)"', src)
    if view_index >= len(scripts) or view_index >= len(tables):
        raise SystemExit(f"{parent_fid} has no view {view_index} to lift into {fid}")
    payload, table = scripts[view_index], tables[view_index]
    checksum = re.search(r'data-checksum="([^"]*)"', table).group(1)
    # Each view can be a different chart type (F10's are all "panel" trend
    # lines; F13's first view is a "dumbbell" comparison) -- hardcoding
    # "panel" here silently mounted the wrong renderer for any non-panel
    # source and left the chart area blank with a JS error in the console.
    chart_type = chart_types[view_index]
    return (f'<figure class="figure" id="{fid}">'
            f'<figcaption><span class="fignum">Figure {{fig:{fid}}}</span> {caption}</figcaption>'
            f'<div class="fig-meta"><span class="badge">pre-planned confirmatory</span>'
            f'<span class="fig-q">{question}</span></div>'
            f'<div class="chart-live" data-chart="{chart_type}" tabindex="0" '
            f'data-checksum="{checksum}" aria-describedby="{fid}-fb">'
            f'<script type="application/json">{payload}</script></div>'
            f'<details class="fallback" id="{fid}-fb"><summary>Show the numbers '
            f'<a href="statistical_appendix.html#{parent_fid}">This figure in the appendix</a>, '
            f'with the detail the report leaves out.</summary>{table}</details>'
            f'</figure>')


def finding(cid):
    """The established wording, quietly set apart, with its limits."""
    c = claims.loc[cid]
    cav = ""
    if str(c.caveats) not in ("nan", ""):
        items = "; ".join(html.escape(x.strip()) for x in str(c.caveats).split("||"))
        cav = f'<p class="limits"><em>The limits of this.</em> {items}.</p>'
    return (f'<div class="finding" data-claim-id="{cid}">'
            f"<p>{html.escape(reader_text(c.canonical_wording))}</p>{cav}</div>")


def findings_plain(lead, *cids):
    """A finding (or several, sharing one lead), stated in plain language
    first, with the precise wording and its statistical caveats available on
    demand rather than sitting in the reading path.

    The exact finding still carries its required data-claim-id -- the
    parity check that enforces every claim's presence only checks that the
    id is IN the document, not where, so collapsing it here doesn't weaken
    that requirement. What changes is what a reader meets by default: a
    sentence written for them, not "coef +4.34, wild-cluster bootstrap
    p=0.0085" in the middle of a paragraph they're trying to read for the
    story.
    """
    label = "The precise result" if len(cids) == 1 else "The precise results"
    return (f'<p>{lead}</p>'
            f'<details class="finding-detail"><summary>{label}</summary>'
            + "".join(finding(c) for c in cids) + '</details>')


def section_notes(*cids):
    """One disclosure per SECTION, not per finding: every exact result a
    section's prose draws on, collected once at the end rather than as a
    string of individual pop-ups down the page. This is the successor to
    findings_plain() -- as sections are rewritten, the plain-language
    statement of each finding moves directly into the flowing prose (no
    separate lead sentence bolted in front of a box), and this holds only
    the precise wording and caveats, gathered at the point a section is
    done arguing rather than interrupting it partway through.
    """
    label = "The precise numbers behind this section" if len(cids) > 1 \
        else "The precise number behind this section"
    return (f'<details class="finding-detail"><summary>{label}</summary>'
            + "".join(finding(c) for c in cids) + '</details>')


def recovery_table():
    """A plain reading of Figure 7's convergence-share chart, one row per
    measure, in the units each is actually reported in.

    F7 plots a single dimensionless "share of the 2015 gap closed" so
    fourteen measures on incompatible scales can share one axis -- which is
    exactly the number a reader is most likely to misread, since "0.71"
    reads as a fraction of nothing in particular. This reads the report's
    own e_f7_recovery_table.csv (T-RECOVERY in the technical report) for a
    subset of rows this piece's own story actually uses, so the numbers can
    never drift from the chart above them, and states in words what the
    chart's dimensionless axis cannot: an improving number is not the same
    as a closing gap, and whether Greece moved or the EU median moved is a
    different question from how far apart they ended up.
    """
    d = pd.read_csv(PROC / "e_f7_recovery_table.csv").set_index("measure")
    keep = ["Long-term unemployment", "Housing-cost overburden",
            "Real wages, 2008 = 100", "Material resources",
            "Wage-adjusted affordability"]
    rows = "".join(
        f"<tr><td>{m}</td><td class='num'>{d.loc[m, 'greece_range']}</td>"
        f"<td class='num'>{d.loc[m, 'eu_median_range']}</td>"
        f"<td>{d.loc[m, 'plain_reading']}</td></tr>"
        for m in keep)
    return (f'<div class="mini-table"><table><thead><tr>'
            f"<th>Measure</th><th>Greece, 2015&rarr;2024</th>"
            f"<th>EU median, 2015&rarr;2024</th><th>What actually happened</th>"
            f"</tr></thead><tbody>{rows}</tbody></table></div>")


def context(cid, prose):
    e = ctx.loc[cid]
    cite = ""
    if str(e.source_status) != "not applicable":
        url = (f' <a href="{e.source_url}">source</a>'
               if isinstance(e.source_url, str) and e.source_url else "")
        cite = f'<p class="src">{html.escape(str(e.source))}{url}</p>'
    return (f'<div class="ctx" data-context-id="{cid}">'
            f'<p class="ctx-status">{html.escape(str(e.status))}</p>'
            f"<h4>{html.escape(str(e.topic))}</h4>{prose}"
            f'<p class="permitted"><em>What this lets us say.</em> '
            f"{html.escape(str(e.permitted))}</p>"
            f'<p class="limitation"><em>What it does not.</em> '
            f"{html.escape(str(e.forbidden))}</p>{cite}</div>")


CH_KEYS = {}
CH_BY_KEY = {}


def chapter(key, title, body):
    """Number derives from position, never passed in.

    Sections refer to each other by KEY, not by number: prose uses the token
    {ch:key} and it resolves to the section's anchor id, not a visible
    "Chapter N" label. Section bodies are f-strings, so the token is WRITTEN
    as {{ch:key}} and arrives here single-braced -- which is the form
    matched below.
    """
    n = len(CH) + 1
    CH_KEYS[key] = n
    rendered = f'<section class="ch" id="ch{n}"><h2>{title}</h2>{body}</section>'
    CH_BY_KEY[key] = rendered
    return rendered


def resolve_refs(doc):
    import re as _re
    unknown = set(_re.findall(r"\{ch:([a-z_]+)\}", doc)) - set(CH_KEYS)
    if unknown:
        raise SystemExit(f"reference to unknown chapter(s): {sorted(unknown)}")
    for k, n in CH_KEYS.items():
        doc = doc.replace("{ch:" + k + "}", str(n))
    left = _re.findall(r"\{ch:[a-z_]*\}", doc)
    if left:
        raise SystemExit(f"unresolved chapter references: {sorted(set(left))}")
    return doc


def resolve_fig_nums(doc):
    """Number every {fig:FID} token by where it actually falls in DOC, left
    to right -- the order a reader meets it, not the order fig() happened to
    be called while this file was defining sections."""
    order = []
    for fid in re.findall(r"\{fig:([A-Z0-9]+)\}", doc):
        if fid not in order:
            order.append(fid)
    for i, fid in enumerate(order, start=1):
        doc = doc.replace("{fig:" + fid + "}", str(i))
    left = re.findall(r"\{fig:[A-Z0-9]*\}", doc)
    if left:
        raise SystemExit(f"unresolved figure references: {sorted(set(left))}")
    return doc


# ===========================================================================
#  SEVEN SECTIONS
# ===========================================================================
CH = []

# ---- 1. The Poverty Rate Says One Thing. Households Say Another. ----------
CH.append(chapter("paradox", "The Poverty Rate Says One Thing. Households Say Another.", f"""
<p>Looking at the labour market and some headline economic indicators,
Greece appears to have recovered from the crisis. Unemployment has fallen
sharply. Output has returned. The bailout years are no longer the first
fact most economic summaries reach for.</p>

<p>But the closer we move to households, the less complete that recovery
looks.</p>

<p>By the official income-poverty measure, Greece is in difficulty, but not
exceptional. By what households report, it is close to unmatched. That is
the paradox this piece unfolds: income poverty and reported hardship are
telling two different stories, and the poverty rate becomes misleading when
it is read alone, without context.</p>

{fig('F1', caption="Greece Is Far Above the Poverty-Hardship Line")}

<p>The first tab, &ldquo;How Greece's hardship gap developed,&rdquo;
shows why. Since 2015, Greece's reported hardship has never dropped below
two-thirds of households &mdash; it opens near 78% and eases only
gradually. Its income-poverty rate spends the same decade hovering near a
fifth, barely moving at all. Both EU medians sit far beneath Greece's line
for reported hardship, the whole way through. This isn't a single bad year
showing up once. It's been the shape of an entire decade.</p>

<p>Switch to the second tab, &ldquo;Where countries stood in 2024,&rdquo;
and the gap turns from a Greek pattern into a European outlier. Each grey
dot is an EU country. The horizontal axis is income poverty; the vertical
is reported hardship. The dotted line is the relationship the other
twenty-six countries actually follow. Greece is the blue point far above
it. At Greece's income-poverty rate, that relationship predicts about 20%
of households struggling to make ends meet. Greece reports about 67%. The
47-point distance between those two numbers is the gap this piece tries to
understand.</p>

{finding('V2-1.2')}

<p>The two numbers are not rival opinions. They come from the same European
system, from surveys of the same households, but they ask different
questions. Income poverty asks whether a household sits below 60% of its
country's median income, a measure of relative position. Reported hardship
asks something more direct: can the household make ends meet? In most of
Europe, those two answers move together. In Greece, they have stayed far
apart, year after year.</p>

<p>But once a gap like that appears, the two numbers are not usually read
with equal trust. Income poverty feels firmer: a number built from income,
thresholds and ranks. Reported hardship feels softer: not necessarily a
fact about a household's circumstances, but the way that household
describes itself. Is that fair? Or is the hardship signal telling us
something material that income poverty alone cannot see?</p>
"""))

# ---- 2. The Poverty Line Fell With the Country (ruler + AROPE + divides) ---
CH.append(chapter("ruler", "The Poverty Line Fell With the Country", f"""
<p>The official poverty line isn't fixed. It moves with the very economy it
is supposed to be measuring.</p>

<p>The EU's headline poverty measure, at-risk-of-poverty, is not an income
level. It is a percentage &mdash; 60% of whatever the national median income
happens to be, <em>that year</em>. In an ordinary economy, where incomes
drift up slowly and roughly together, that is a reasonable way to define
being poor relative to your neighbours.</p>

<p>Greece's economy, from 2010, was not ordinary. Incomes fell together,
hard and fast, and when the median falls, the poverty line falls with it. A
household earning exactly what it earned five years earlier could find
itself reclassified from poor to not poor &mdash; not because anything in
its life had improved, but because the ruler measuring it had shrunk to
match the collapse around it.</p>

<p>So the official rate barely moved through the worst years. Hold the line
where it stood in 2008 instead, adjusted only for inflation, and measured
poverty roughly doubles: from under 20% before the crisis to a peak above
40% in 2014.</p>

{fig('F3', caption="The Poverty Line Looked Stable. Its Value Did Not.")}

{findings_plain(
    "That gap between the moving line and the fixed one is not this "
    "piece's own estimate. It is Eurostat's own hardship figure, run "
    "backward past 2010 using a method checked against the official series "
    "everywhere the two overlap.",
    'V2-1.1')}

<p>This is a measure of Greece against its own past, and it contains no
other country: it cannot show that Greece's line fell further than anyone
else's. Nor is the fixed line the &ldquo;correct&rdquo; one &mdash; the
relative measure is doing exactly what it was designed to do, measuring
position. When a whole country falls together, those two questions come
apart, and that separation is the point.</p>

<p>Europe already knows income alone is too narrow, for exactly this reason.
Its broader measure, AROPE, casts a wider net: a household counts if its
income is low, or it can't afford a list of ordinary things, or the adults
in it are barely working. If <a href="#ch{{ch:paradox}}">the puzzle
above</a> were simply that the income measure is too narrow, this wider one
should mostly dissolve it.</p>

{findings_plain(
    "It doesn't. AROPE closes a fifth of the gap, and a shrinking fifth at "
    "that.",
    'V2-2.1')}

<p>It helps, and it isn't enough. The wider net picks up under a quarter of
the distance, and its contribution is shrinking &mdash; from eleven points
at the start of the decade to seven by the end. As an explanation of the
gap, it is weakening rather than strengthening.</p>

<p>Underneath both headline rates sits a further complication: national
averages are averages of people, and Greek age groups did not move together
through the crisis. Some improved while others did not, and the combined
figure sat placidly between them &mdash; which matters, because the
household answering the survey question is not answering about the national
average. It is answering about itself.</p>
"""))

# ---- 3. This Was Not Just a Feeling (real + company) -----------------------
CH.append(chapter("footprint", "This Was Not Just a Feeling", f"""
<p>If Greek households say they are struggling while nothing in their
material circumstances corresponds to it, this is a story about how people
answer questions, not about poverty. So this has to be settled before
anything else: does reported difficulty move together with things that name
events rather than feelings &mdash; falling behind on bills, being unable to
handle an unexpected expense, being unable to heat the home, going without
several basic things at once?</p>

<p>It does, and the honest caveat has to come first, not as a footnote.
Every one of those items comes from the same survey, asked of the same
household, in the same sitting, as the question about making ends meet. A
household in a grim mood about its finances will answer the whole set
grimly, and that alone would produce numbers like these. This is one
instrument agreeing with itself: real evidence, and not independent
confirmation.</p>

{findings_plain(
    "Even holding that caveat firmly in mind, the pattern is strong and it "
    "holds within countries, not just across rich ones and poor ones.",
    'V2-3.1')}

{fig('F8', caption="Hardship Moves With Concrete Financial Strain")}

<p>It isn't even uniform across items. Falling behind on bills &mdash; the
one you'd expect to be the hardest, most factual anchor &mdash; tracks the
reported difficulty far more weakly within Greece than the others do.
Arrears require having credit and bills to fall behind on; a household that
lost access to credit years ago, or never had it, can be in serious trouble
without ever registering.</p>

{findings_plain(
    "Put those concrete items together in the same picture as the official "
    "poverty rate, and most of what makes Greece look unexplained simply "
    "disappears.",
    'V2-3.2')}

<p>That word &mdash; absorb &mdash; is doing careful work, and it is not a
synonym for explain. Put those deprivation items into the picture and most
of Greece's unexplained excess stops standing out. That tells us the two
things share a great deal of information. It does not tell us one causes the
other, because both are measured by the same survey of the same households
on the same day. How much rides on that choice comes back later.</p>

<p>A number this isolated invites a simpler suspicion: that it's broken. So
it is worth asking what company it keeps. Take sixteen separate measures of
Greek life &mdash; wages, hours worked, prices, saving, what households
expect of next year, how many people are leaving &mdash; chosen only
because both a 2008 and a 2024 reading exist for each. Ask a blunt question
of each: is Greece in the worst fifth of Europe on this?</p>

{fig('F21', caption="The Problem Spread Across the Dashboard")}

<p>Before the crisis, four of sixteen did &mdash; about a quarter. Now
eleven do &mdash; about two thirds. They are not sixteen ways of saying the
same thing: pay per hour, hours worked, household saving, the real value of
the poverty line itself, and the number of citizens leaving all sit down
there together. This breadth is description, not explanation &mdash; on its
own it predicts nothing, and a later section returns to why &mdash; but it
settles something modest and real: the measure that put Greece at the top of
Europe is not one strange instrument twitching on its own. It sits inside a
wide field of measures that moved with it.</p>
"""))

# ---- 4. Some Parts Recovered. Others Fell Further Behind ------------------
CH.append(chapter("recovery", "Some Parts Recovered. Others Fell Further Behind", f"""
<p>Greece's recovery is real. It just didn't arrive in every part of a
household's life at the same time, or at the same speed &mdash; and
averages hide that as easily as they hide anything else in this story.</p>

<p>Start with what genuinely improved. Long-term unemployment &mdash; out of
work for twelve months or more, a different and slower-moving thing than the
headline rate &mdash; stood at 16.4% of the labour force in 2015. By 2024 it
had fallen to 5.4%. That is substantial, real progress. Housing-cost
pressure eased too. Time does something specific to a household: savings go
first, then whatever can be sold, then the goodwill of relatives, then the
ability to absorb any surprise at all. A shorter spell of joblessness is a
genuinely different, less corrosive thing than a long one.</p>

<p>Now the part that didn't keep pace. Greek real wages stood at about 77%
of their 2008 level in 2015; by 2024, about 68%. Not recovering slowly
&mdash; not recovering. Greek wages have now been below their pre-crisis
level for fifteen consecutive years, longer than any EU country except
Hungary. What people can actually buy for that money &mdash; consumption
adjusted for local prices &mdash; did rise substantially, from roughly
14,800 to 21,300 in the units used for these comparisons. That is real, and
worth saying plainly, because a piece about hardship can leave the
impression that nothing improved. But the EU median rose faster over the
same years, so the distance between Greece and its neighbours widened even
as Greece's own number climbed.</p>

{fig('F7', caption="The Recovery Was Uneven")}

<p>The shape is consistent: gaps that were mostly about jobs and housing
narrowed considerably; gaps that were about wages, resources and what money
can buy narrowed barely at all, or widened. But a chart built to fit
fourteen measures onto one axis has to abstract away units, so here is the
same story in the numbers each measure actually reports in &mdash; and the
plainest reading of each.</p>

{recovery_table()}

<p>Two things in that table are easy to misread, and both matter. An
improving number is not the same as a closing gap: material resources rose
by nearly half in Greece and still fell further behind, because the EU
median rose faster. And whether a gap narrows because Greece caught up,
because the rest of Europe slowed down, or both, is not something either
version of this comparison can tell you. Convergence is context here, not a
mechanism. It describes what happened, not why.</p>

<p>It isn't only pay, either. In the EU's most recent data, Greece is the
worst country in the Union for people who needed medical care and didn't
get it, because of cost, waiting time or distance &mdash; 12.1% in 2024,
against a European median of 1.9%, and second-worst in three of the
previous four rounds. That is not a statistic this piece can use to explain
the hardship gap; nothing here tests it against the other findings. It is
simply what &ldquo;recovery&rdquo; can coexist with, on the ground, in the
same years the headline numbers were improving.</p>

{findings_plain(
    "Two of the measures behind this uneven picture also do something more "
    "than describe: how much long-term unemployment a country carries, and "
    "how much its households can actually afford, each still predict "
    "reported hardship once the official poverty rate is already accounted "
    "for.",
    'V2-4.C2', 'V2-4.C1')}

<p>A country can score badly on affordability two ways: by being expensive,
or by paying poorly. Greece does both at once, and a household experiencing
it does not much care which half is responsible.</p>

{findings_plain(
    "So does the third: what a Greek wage is actually worth against Greek "
    "prices.",
    'V2-4.C4')}

<blockquote>The unemployment rate came back. The paycheck did not.</blockquote>

{context('CTX-8', '''
<p>An outside analysis (Greece in Figures, working from newer Eurostat and
ELSTAT numbers than the ones used here) lands on the same shape from a
different direction and without running any of the tests in this report:
Greece is not last in the EU on what people actually consume, but Greek
employees put in some of the longest hours in the Union for comparatively
low pay per hour, and everyday things like food cost more than that pay
would suggest. Same picture, different route, no formal test behind it.</p>''')}
"""))

# ---- 5. A Decade of Damage Still Counts (duration) -------------------------
CH.append(chapter("duration", "A Decade of Damage Still Counts", f"""
<p>Two countries can look identical today and have arrived by different
roads. One has had high long-term unemployment for a year. The other has had
it for twelve. The intuition that these are not the same situation is
strong, and it is the intuition behind almost every account of the Greek
crisis.</p>

<p>Intuition isn't evidence, and this is where an appealing story is
easiest to oversell. Three earlier drafts of this piece oversold it, in
fact, before the wording below was settled.</p>

<p>For each present-day measure in the last section, there is a matching
one that counts not the level today but the total weight a country has
carried since before the crisis: how much excess unemployment it
accumulated, how many consecutive years its wages stayed below 2008, how
much its housing costs deteriorated.</p>

{fig('F11', caption="Greece Had Among Europe&rsquo;s Largest Accumulated Burdens")}

<p>Greece carries more of this weight than almost anywhere else in Europe.
On one of the three measures it is not the heaviest &mdash; Hungary has a
longer run of depressed wages &mdash; and the chart shows every country
rather than Greece alone, so that comparison is visible rather than
buried.</p>

<p>Carrying a heavy history is one thing. Whether that history still
matters once you already know where a country stands today is a harder
question, and a more important one: if you know this year's unemployment
rate, does the decade behind it tell you anything more?</p>

<p>For three measures, it does.</p>

{findings_plain(
    "How much excess unemployment a country has absorbed since before the "
    "crisis. How many years its wages have run below their 2008 level, on "
    "one specific way of counting that &mdash; other reasonable ways of "
    "counting the same idea point the same direction without quite "
    "clearing the bar, worth knowing even though they don't change the "
    "answer. And, more tentatively, how much its housing costs have "
    "deteriorated.",
    'V2-5.C2', 'V2-5.C3', 'V2-5.C6')}

<p>The housing result is the shakiest of the three, and it is presented
that way rather than rounded up to a clean yes.</p>

<p>The pattern is not universal, though, which is itself informative.</p>

{findings_plain(
    "For the cost-of-living measure, it runs the other way: today's number "
    "carries the signal, and the accumulated version of it doesn't "
    "resolve.",
    'V2-5.X')}

<p>If history mattered as a general rule, that reversal shouldn't happen.
It suggests these results are specific to work, wages and housing rather
than some broad law that the past always counts for everything.</p>

{findings_plain(
    "One more piece of the history simply isn't there to look at. What "
    "households could actually afford, tracked back to before the crisis, "
    "can't be built at all &mdash; the source data only starts in 2015, "
    "already years into the recovery. Moving the starting line earlier "
    "would have solved the data problem and created a different one: a "
    "measure that could no longer see the crisis it exists to describe. So "
    "it stays out, and is named here rather than quietly absent.",
    'V2-5.Z')}

{finding('L-3')}

<p>Wages are the exception worth naming for the opposite reason. The
accumulated version of the wage story held up under every check put in
front of it &mdash; as convincingly as the three results above. It isn't
counted among them, because the present-day wage measure underneath it was
never established as real in its own right, earlier in this piece. A result
can only stand as high as its foundation, and this one's foundation was
never poured. It's named here, not because it counts, but because
pretending it doesn't exist would be its own kind of dishonesty.</p>
"""))

# ---- 6. Where the Evidence Stops (between/within + unsettled + flip
#         + the two failed designs) -----------------------------------------
CH.append(chapter("limits", "Where the Evidence Stops", f"""
<p>Everything in <a href="#ch{{ch:duration}}">the previous section</a> is a
statement about how countries differ from each other. It is tempting, and
wrong, to turn it into a statement about how Greece changed over time.</p>

{findings_plain(
    "Look for that change happening inside Greece itself, over the years, "
    "and the evidence isn't there to find it &mdash; not because it has "
    "been ruled out, but because this kind of comparison cannot see it "
    "either way.",
    'V2-5.Y')}

{subfig('F13A', 'F13', 0,
        "The Evidence Is Mostly Between Countries",
        "Is the accumulated effect between countries, or within one over time?")}

<p>&ldquo;Countries that accumulated more hardship report more
difficulty&rdquo; is a claim about a group photograph. &ldquo;As Greece
accumulated more hardship, Greek households reported more difficulty&rdquo;
is a claim about a film. This piece has the photograph. It does not have the
film &mdash; not because the film doesn't exist, but because seeing it would
mean giving up the comparison between countries, and what's left on its own
isn't sharp enough to say either way.</p>

<p>Not every present-day measure earned a place in the story so far,
either. Nine were tried; three worked. The other six mostly went quiet
rather than failed outright &mdash; with twenty-seven countries and a
decade of data, most of them could only have caught an effect bigger than
any effect worth caring about. Silence isn't a verdict.</p>

{findings_plain(
    "A couple of them can be set aside for real, at least at the size this "
    "design could catch &mdash; both measures of price inflation among "
    "them. The rest simply weren't put under enough pressure to say either "
    "way.",
    'V2-4.X', 'L-4')}

<p>The biggest complication is a genuine reversal, and it concerns the
deprivation items <a href="#ch{{ch:footprint}}">from earlier</a> &mdash;
can't pay bills, can't heat the home &mdash; which absorbed most of Greece's
unexplained excess. Those items come from the same survey as the thing
they're explaining, and whether to let a measure like that into the picture
is a real, defensible choice either way. So both versions were built.</p>

{findings_plain(
    "Choose differently, and Greece's whole position in Europe flips.",
    'V2-6.1')}

{fig('F14', caption="What the Recovery Story Still Misses")}

<blockquote>That is not a wobble. It is a reversal, and there is no honest
way to pick between the two.</blockquote>

<p>Greece moves from the third-worst country in Europe on unexplained
hardship to the twenty-fifth &mdash; from a stark positive outlier to a
stark negative one &mdash; on exactly the same rows of data, with one
measure added or removed. The two results can't be averaged, and can't be
chosen between by which looks more plausible; doing that is exactly what
would make a check like this meaningless. Which is why nothing later in
this piece leans on it.</p>

<p>Two further ideas were meant to carry real weight here, and neither
survived contact with the data &mdash; worth naming rather than quietly
dropping. A synthetic Greece, built to track the real one before 2008 and
read the divergence after as the crisis effect, collapsed into a blend of
essentially two countries and missed four of the six conditions it had been
required to meet before anyone looked at the result. Its chart is not
shown here, because a dramatic picture built on a counterfactual that thin
would persuade readers of something the evidence can't actually support.
And the sixteen-measure spread <a href="#ch{{ch:footprint}}">from
earlier</a> made Greece's position worse, not better, once it was asked to
predict rather than just describe, and its direction flipped once other
measures were held steady &mdash; left deliberately unexplained here, since
inventing a story for a strange result in a design that already failed is
how failed ideas come back from the dead.</p>

{findings_plain(
    "Both are recorded for what they are: attempts that didn't work, kept "
    "visible rather than erased.",
    'L-1', 'L-2')}
"""))

# ---- 7. What Greece's recovery leaves out (reporting style + ESS + context
#         register + the close) ---------------------------------------------
CH.append(chapter("leftover", "What Greece's Recovery Leaves Out", f"""
<p>There is a simpler explanation for everything above, and it deserves to
be taken seriously rather than waved away: maybe Greeks are just gloomier
answerers. The evidence so far can't settle that on its own &mdash; it all
comes from inside one survey. A better test looks across different subjects
entirely. A general tendency to answer darkly should drag everything down
about equally; a pattern that's extreme on money and milder elsewhere points
at circumstances instead.</p>

{domain_table()}

{findings_plain(
    "Greece is worst in Europe on the two money questions and close to "
    "worst on general life satisfaction &mdash; a difference of degree, "
    "not of kind, which points toward circumstance rather than "
    "temperament, though it doesn't prove it.",
    'V2-7.1')}

<p>One thing about that life-satisfaction number is worth holding onto,
because it's easy to get backwards: it actually <em>rose</em> over the
period. Greece's rank against it fell anyway, because its faster-improving
neighbours pulled further ahead. A falling rank is not the same thing as a
falling number.</p>

{context('CTX-1', '''
<p>Greece's money questions sit at the far edge of the European range while
its general-wellbeing question sits closer to it. That difference of degree
is what the comparison shows, and it is description rather than a
test.</p>''')}

<p>One further check reaches back before the Eurostat series begins. A
separate European survey shows Greece already sitting about 0.8 points below
its comparison group before the crisis, falling further during it, and
recovering its level &mdash; but not its relative position &mdash; by the
2020s. A long-standing pattern of lower reported wellbeing remains plausible
on this evidence. It also cannot be established by it.</p>

{context('CTX-7', '''
<p>Across six rounds of a separate European survey, holding the same twelve
countries fixed each time, Greece's level fell and then recovered while its
position relative to the others did not. This is descriptive corroboration
and not a test.</p>''')}

<p>Several other factors that come up in every account of the Greek crisis
were not established here &mdash; institutional trust, the design of the
adjustment programmes, migration, and the incidence of indirect taxes among
them. Leaving them out silently would be misleading; treating them as
findings would be worse.</p>

<details class="disclosure"><summary>What this piece did not test</summary>

{context('CTX-2', '''
<p>Trust in institutions is low in Greece, and there is a plausible route by
which it could matter: a household that doesn't expect help to arrive may
experience the same circumstances as more frightening. This piece has no
check on that either way.</p>''')}

{context('CTX-3', '''
<p>The bailout programmes from 2010 reshaped incomes, job protections,
pensions and public services at once and in a hurry. They are the backdrop
to every accumulated measure described earlier.</p>''')}

{context('CTX-4', '''
<p>Large numbers of working-age Greeks left during the crisis, and some have
returned. This cuts both ways: plausibly a consequence of a broken labour
market, and plausibly part of why the people who stayed look the way they
do.</p>''')}

{context('CTX-5', '''
<p>Published research establishes that Greece's system of indirect taxes
became markedly harder on lower-income households across the crisis. If a
household's position worsened through tax in a way income-based poverty
measures capture badly, that would be one route to the kind of gap this
report describes.</p>''')}

</details>

<p>Greek households report struggling at a rate far above what the official
poverty figure predicts, and have done so consistently for a decade. Part of
that distance is now easier to understand: official measures are narrower
than the experience they are used to summarise; what households report
corresponds to real material trouble, even if that agreement comes from
inside a single survey; and both the present and the accumulated past carry
information the official rate does not.</p>

<p>What the evidence stops short of is just as much part of the answer.
Nothing here says what causes what. Nothing here shows Greece changing over
time. Most of what didn't work is unresolved, not ruled out. One central
result flips on a judgement call the data cannot settle. And a plainer
explanation &mdash; that Greeks simply answer more darkly &mdash; cannot be
fully excluded. Most of the 52.6-point gap is still unexplained.</p>

{context('CTX-6', '''
<p>What runs through all of this is that no single official number captures
what Greek households are reporting. Each one misses something different,
and the ones that catch what the others miss are not the headline.</p>''')}

<p>Greece's recovery was real. So was the hardship that remained. The
official poverty rate is not wrong; it answers a narrower question than the
one Greek households have been living. A country can recover in its
averages while its households continue to carry the history.</p>
"""))


# ===========================================================================
#  PAGE
# ===========================================================================
BASE = ce.base_style((OUT / "build" / "report.html").read_text())

# ---- section order ----------------------------------------------------------
# Seven sections, argued in sequence, no grouping layer above them. The old
# five-act structure grouped eighteen chapters; regrouping seven substantial
# sections under acts would just be relabelling the same reset.
SECTION_ORDER = ["paradox", "ruler", "footprint", "recovery", "duration",
                  "limits", "leftover"]
if sorted(SECTION_ORDER) != sorted(CH_KEYS):
    raise SystemExit(
        "section order does not match the sections actually defined -- "
        f"missing {sorted(set(CH_KEYS) - set(SECTION_ORDER))}, "
        f"unknown {sorted(set(SECTION_ORDER) - set(CH_KEYS))}")

BODY = "".join(CH_BY_KEY[k] for k in SECTION_ORDER)

# ---- headline font, bundled ------------------------------------------------
# A live Google Fonts fetch would silently fall back to a system serif the
# moment this page is opened offline or rendered to PDF without a network
# connection -- exactly the two ways this project's own documents get used.
# Bundling two static weights (regular headlines, italic pull-quotes) as
# base64 data URIs costs about 55KB and removes that failure mode entirely.
# See scripts/assets/FRAUNCES-LICENSE.txt (SIL OFL 1.1).
import base64 as _b64
_ASSETS = ROOT / "scripts" / "assets"
_fraunces_700 = _b64.b64encode((_ASSETS / "fraunces-700.woff2").read_bytes()).decode()
_fraunces_500i = _b64.b64encode((_ASSETS / "fraunces-500italic.woff2").read_bytes()).decode()

NARR_CSS = f"""
@font-face{{font-family:'Fraunces Bundled';font-style:normal;font-weight:700;
  font-display:swap;
  src:url(data:font/woff2;base64,{_fraunces_700}) format('woff2')}}
@font-face{{font-family:'Fraunces Bundled';font-style:italic;font-weight:500;
  font-display:swap;
  src:url(data:font/woff2;base64,{_fraunces_500i}) format('woff2')}}
/* Two widths, not one. Every figure in this piece is lifted straight from
   the technical report, sized against ITS OWN 54rem container -- squeezed
   into a narrower body, a dense multi-country chart has visibly less room
   to breathe than in the report it came from. Widening body gives figures,
   the hero and the mini-table the room; a per-element cap on running prose
   keeps paragraphs at a normal reading measure rather than stretching them
   the same distance. */
body{{max-width:48rem;margin:0 auto;padding:0 1.3rem 6rem;
  font:1.09rem/1.78 ui-serif,Georgia,'Times New Roman',serif}}
.ch p,.finding p,.limits,.ctx p{{max-width:72ch}}
.masthead{{padding:4rem 0 1.6rem}}
.rubric{{font:600 .74rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.16em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 1.2rem;display:flex;align-items:center;gap:.6rem}}
.rubric::before{{content:"";width:1.3rem;height:1px;background:var(--text-secondary)}}
.masthead h1{{font-family:'Fraunces Bundled',Georgia,'Times New Roman',serif;
  font-weight:700;font-size:clamp(2.1rem,6vw,3.1rem);line-height:1.08;
  margin:0 0 1.2rem;letter-spacing:-.015em;text-wrap:balance}}
.standfirst{{font-size:1.16rem;line-height:1.58;color:var(--text-secondary);
  margin:0;max-width:38ch}}
/* The hero pairing is a deliberate asymmetry, not a dashboard tile pair: the
   official measure sits small and grey, the reported one large and dark,
   because that contrast IS the argument before a reader reaches a word of
   prose. Both labels name their own population explicitly -- people against
   households -- so the pairing cannot be misread as one denominator. */
.stat-pair{{display:flex;align-items:flex-end;gap:1.7rem;flex-wrap:wrap;
  margin:2.6rem 0 1.4rem;padding:1.7rem 0;border-top:1px solid var(--border);
  border-bottom:1px solid var(--border)}}
.stat{{flex:1;min-width:11rem}}
.stat .n{{font-family:'Fraunces Bundled',Georgia,'Times New Roman',serif;
  letter-spacing:-.02em;display:block;line-height:.95}}
.stat--official .n{{font-size:2.5rem;font-weight:700;color:var(--text-secondary)}}
.stat--lived .n{{font-size:4.3rem;font-weight:700;color:var(--text-primary)}}
.stat .pct{{font:600 .8rem/1 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin-top:.35rem}}
.stat .l{{font:600 .76rem/1.4 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.02em;color:var(--text-secondary);margin:.5rem 0 0;max-width:19ch}}
.stat .l b{{color:var(--text-primary)}}
.ch{{margin:5rem 0 0}}
.ch h2{{font-family:'Fraunces Bundled',Georgia,'Times New Roman',serif;
  font-weight:700;font-size:clamp(1.6rem,4.2vw,2.1rem);margin:0 0 1.3rem;
  letter-spacing:-.01em;text-wrap:balance}}
.ch p{{margin:0 0 1.05rem}}
.ch a{{color:var(--series-gr)}}
blockquote{{margin:2.2rem -.1rem;padding:0;border:none;
  font-family:'Fraunces Bundled',Georgia,'Times New Roman',serif;
  font-style:italic;font-weight:500;font-size:1.4rem;line-height:1.36;
  color:var(--text-primary);letter-spacing:-.005em;text-wrap:balance}}
blockquote::before,blockquote::after{{color:var(--series-eu);font-style:normal}}
blockquote::before{{content:"\\201C"}}
blockquote::after{{content:"\\201D"}}
.finding{{border-left:3px solid var(--series-gr);padding:.1rem 0 .1rem 1.1rem;
  margin:1.6rem 0}}
.finding p{{margin:0 0 .5rem;font-size:1.06rem}}
.limits{{font:.92rem/1.65 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin:0}}
/* findings_plain()'s disclosure: the plain-language lead sentence stays in
   the reading path as an ordinary <p>; the precise wording (with its own
   statistics and caveats) sits one click away, styled like .fig-methods
   rather than introducing a third disclosure language on the same page. */
details.finding-detail{{margin:0 0 1.6rem}}
details.finding-detail summary{{cursor:pointer;font:600 .78rem/1
  ui-sans-serif,system-ui,sans-serif;letter-spacing:.04em;
  color:var(--text-secondary);padding:.2rem 0}}
details.finding-detail[open] summary{{margin-bottom:.6rem}}
details.finding-detail .finding{{margin:0 0 .8rem}}
details.finding-detail .finding:last-child{{margin-bottom:0}}
.ctx{{border:1px dashed var(--border);border-radius:6px;padding:1rem 1.2rem;
  margin:1.8rem 0}}
.ctx-status{{font:600 .68rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 .45rem}}
.ctx h4{{margin:0 0 .55rem;font-size:1.02rem}}
.ctx p{{font-size:.98rem;margin:0 0 .7rem}}
.ctx .permitted,.ctx .limitation,.ctx .src{{
  font:.9rem/1.6 ui-sans-serif,system-ui,sans-serif;margin:.5rem 0 0}}
.ctx .limitation{{color:var(--text-secondary)}}
.ctx .src{{color:var(--text-secondary);font-size:.82rem;padding-top:.5rem;
  border-top:1px solid var(--border)}}
/* A figure's technical caveat, expandable rather than open in the reading
   path -- the chart, caption and its own number fallback are unaffected.
   The evidence-tier badge (e.g. "pre-planned confirmatory") is report
   chrome, useful in the audit trail and redundant in a magazine reading
   path that already states what a figure does and doesn't show in prose;
   hidden here rather than in chart_engine.py, which the report and paper
   still rely on unchanged. */
.fig-meta .badge{{display:none}}
.fig-methods{{margin:0 1.1rem 1rem}}
.fig-methods summary{{cursor:pointer;font:600 .78rem/1 ui-sans-serif,
  system-ui,sans-serif;letter-spacing:.04em;color:var(--text-secondary);
  padding:.2rem 0}}
.fig-methods[open] summary{{margin-bottom:.4rem}}
.fig-methods .fig-caveat{{margin:0;font-size:.86rem}}
/* The domain table replaces a chart the report itself rejected (three
   incompatible scales -- a percentage, a net balance, a 0-10 rating -- on
   one axis); styled plainly, in the body serif, rather than borrowing the
   report's own sans-serif data-table language wholesale. */
.mini-table{{margin:1.8rem 0;overflow-x:auto;border:1px solid var(--border);
  border-radius:6px}}
.mini-table table{{border-collapse:collapse;width:100%;min-width:24rem;
  font:.95rem/1.5 ui-serif,Georgia,'Times New Roman',serif}}
.mini-table th{{text-align:left;font:600 .72rem/1 ui-sans-serif,system-ui,
  sans-serif;letter-spacing:.04em;text-transform:uppercase;
  color:var(--text-secondary);padding:.6rem .9rem;
  border-bottom:1px solid var(--border);background:var(--surface-2)}}
.mini-table td{{padding:.55rem .9rem;border-bottom:1px solid var(--border)}}
.mini-table td.num{{font-variant-numeric:tabular-nums;text-align:right}}
.mini-table tr:last-child td{{border-bottom:none}}
/* Grouped context boxes a general reader can skip without losing the
   argument -- the individual boxes inside keep their own dashed border and
   status label, this wrapper just gives them one collapsed entry point. */
details.disclosure{{border:1px solid var(--border);border-radius:6px;
  margin:1.8rem 0;padding:0 1.1rem}}
details.disclosure summary{{cursor:pointer;font:600 .84rem/1
  ui-sans-serif,system-ui,sans-serif;letter-spacing:.02em;padding:1rem 0}}
details.disclosure[open] summary{{border-bottom:1px solid var(--border)}}
details.disclosure .ctx:last-child{{margin-bottom:1.2rem}}
@media (max-width:34rem){{body{{font-size:1.04rem}}}}
"""

# Both token families are resolved against this ONE combined string, in
# final left-to-right document order -- {ch:key} against where each section's
# anchor actually sits, {fig:FID} against where each figure actually appears.
# Resolving them separately per-fragment (opening figure, then body) would
# get the opening figure's own number right by accident and nothing else.
_main = resolve_fig_nums(resolve_refs(BODY))

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>If Greece Has Recovered, Why Do So Many Households Still Struggle?</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu)}}
{NARR_CSS}</style></head><body>
<header class="masthead">
<p class="rubric">The Greek Poverty Paradox</p>
<h1>If Greece Has Recovered, Why Do So Many Households Still Struggle?</h1>
<p class="standfirst">Official income poverty affects roughly one person in
five. Yet about two households in three report difficulty making ends meet.
The distance between them reveals a moving poverty line, an uneven recovery
and the continuing weight of unemployment, wages and housing.</p>
<div class="stat-pair">
  <div class="stat stat--official">
    <span class="n">1 in 5</span>
    <p class="pct">19.6%</p>
    <p class="l"><b>People</b> at risk of poverty &mdash; the official measure</p>
  </div>
  <div class="stat stat--lived">
    <span class="n">2 in 3</span>
    <p class="pct">66.7%</p>
    <p class="l"><b>Households</b> struggling to make ends meet</p>
  </div>
</div>
</header>
{_main}
<script>{ce.JS}</script>
</body></html>
"""

# ---- checks ---------------------------------------------------------------
missing_f = [f for f in NARRATIVE_FIGS if f not in _used]
if missing_f:
    raise SystemExit(f"narrative figures selected but not placed: {missing_f}")

required = [i for i in claims.index
            if str(claims.loc[i, "narrative"]).strip().lower() == "body"]
if not required:
    raise SystemExit("no claims required in the narrative -- the check is vacuous")
absent = [i for i in required if f'data-claim-id="{i}"' not in PAGE]
if absent:
    raise SystemExit(f"claims required in the narrative but absent: {absent}")

for cid in ctx.index:
    if f'data-context-id="{cid}"' not in PAGE:
        raise SystemExit(f"context entry {cid} never placed")

stripped = re.sub(r"<script.*?</script>", " ", PAGE, flags=re.S)
visible = html.unescape(re.sub(r"<[^>]+>", " ", stripped))
BANNED = ["V2-", "CTX-", "L-1", "L-2", "L-3", "L-4", "frozen claim", "aic_pps_pc",
          "ltu_rate", "wadj_a01", "data-claim-id"]
leaked = [b for b in BANNED if b in visible]
if leaked:
    raise SystemExit(f"internal vocabulary visible in the narrative: {leaked}")

# The findings carry their own statistics and those stay as established. The
# companion's OWN prose is what has to stay clear of jargon, so it is checked
# separately, with the finding and context blocks removed first.
# Figures are lifted from the technical report and carry their own labelling,
# which is technical by necessity: an axis has to say what it measures. The
# companion's job is to explain each one in plain words alongside it, which is
# what the surrounding prose does. So figures are excluded here too.
prose = re.sub(r"<figure class=\"figure\".*?</figure>", " ", stripped, flags=re.S)
prose = re.sub(r'<div class="(?:finding|ctx)".*?</div>', " ", prose, flags=re.S)
prose = html.unescape(re.sub(r"<[^>]+>", " ", prose))
JARGON = ["bootstrap", "p-value", "coefficient", "specification", "estimator",
          "fixed effects", "statistically significant", "confidence interval",
          "regression", "multiplicity", "residual"]
found = [j for j in JARGON if j in prose.lower()]
if found:
    raise SystemExit(f"jargon in the companion's own prose: {found}")

(OUT / "narrative.html").write_text(PAGE)
print(f"wrote output/narrative.html  {len(PAGE):,} chars")
