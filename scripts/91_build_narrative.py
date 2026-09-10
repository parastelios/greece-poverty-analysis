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
# Construct ids appear parenthetically after the thing they label, where the
# label alone already reads correctly: "Accumulated material resources (C1)".
_CONSTRUCT_ID = re.compile(r" \((?:[A-Z]\d[a-z]?)\)")


def reader_text(s):
    s = str(s)
    for code in DISPLAY_CODES:
        s = s.replace(f" ({code})", "")
    for a, b in SPEC_WORDS.items():
        s = s.replace(a, b)
    return _CONSTRUCT_ID.sub("", s)


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
    # The figure's caveat is the report's own text, written for a reader who
    # can look a stage id up. Here it is rewritten on the way in, exactly as
    # the frozen wording is.
    html_ = re.sub(r'(<p class="fig-caveat">)(.*?)(</p>)',
                    lambda m: m.group(1) + reader_text(m.group(2)) + m.group(3),
                    html_, count=1, flags=re.S)
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
        items = "; ".join(html.escape(reader_text(x.strip()))
                          for x in str(c.caveats).split(" | "))
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


def recovery_table():
    """A plain reading of F7's convergence-share chart, one row per
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
    keep = ["Long-term unemployment", "Share below own GDP peak",
            "Housing-cost overburden", "Real wages, 2008 = 100",
            "Material resources", "Wage-adjusted affordability"]
    rows = "".join(
        f"<tr><td>{m}</td><td class='num'>{d.loc[m, 'greece_range']}</td>"
        f"<td class='num'>{d.loc[m, 'eu_median_range']}</td>"
        f"<td>{d.loc[m, 'plain_reading']}</td></tr>"
        for m in keep)
    return (f'<div class="mini-table" id="recovery-table"><table><thead><tr>'
            f"<th>Measure</th><th>Greece, 2015&rarr;2024</th>"
            f"<th>EU median, 2015&rarr;2024</th><th>What actually happened</th>"
            f"</tr></thead><tbody>{rows}</tbody></table></div>")


def context(cid, prose, expand=False):
    """EXPAND, when true, tucks the permitted/forbidden/citation block into a
    collapsed <details> instead of showing it inline. The anchor and the full
    text are still present -- context_completeness() reads DOM text, not
    visibility -- so this changes what a reader meets by default, not what's
    required to be there. Used where the section's own closing beat needs to
    land right after the topic sentence rather than after a full caveat
    block; everywhere else the full block stays inline, as before.
    """
    e = ctx.loc[cid]
    cite = ""
    if str(e.source_status) != "not applicable":
        url = (f' <a href="{e.source_url}">source</a>'
               if isinstance(e.source_url, str) and e.source_url else "")
        cite = f'<p class="src">{html.escape(str(e.source))}{url}</p>'
    body = (f'<p class="permitted"><em>What this lets us say.</em> '
            f"{html.escape(reader_text(e.permitted))}</p>"
            f'<p class="limitation"><em>What it does not.</em> '
            f"{html.escape(reader_text(e.forbidden))}</p>{cite}")
    if expand:
        body = f'<details class="ctx-detail"><summary>The full caveat</summary>{body}</details>'
    return (f'<div class="ctx" data-context-id="{cid}">'
            f'<p class="ctx-status">{html.escape(str(e.status))}</p>'
            f"<h4>{html.escape(str(e.topic))}</h4>{prose}{body}</div>")


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
CH.append(chapter("paradox", "Real Hardship, or Greek Pessimism?", f"""
<p>There is a strange reversal in the public debate about Greece's economy.
When unemployment falls or GDP grows, the indicators are treated as the final
proof of recovery. But when two in three households say they struggle to make
ends meet, attention shifts away from the indicators and towards household
behaviour: coffee, takeaway food, travel, &ldquo;exaggeration&rdquo;, or
Greek pessimism.</p>

<p>Is that shift justified? By the official income-poverty measure, Greece is
in difficulty but not outside the European range. By what households report,
it is almost in a category of its own, and the public conversation has
often already answered: the recovery is real, so households' persistence
is a matter of mood, not evidence. That is the paradox this piece unfolds:
<em>income poverty</em> and <em>reported hardship</em> are telling two
different stories. The question this piece asks is whether that dismissal
holds: does reported hardship carry a material reality that income poverty
alone cannot see, or is it, to a meaningful degree, a darker way of
answering?</p>

<p>Two measures carry this whole piece, and both come from the same source:
<em>EU-SILC</em> (<em>European Union Statistics on Income and Living
Conditions</em>), the annual EU-wide survey on household income and living
conditions, run to a common methodology in every member state so results
are comparable across countries, and carried out in Greece by ELSTAT.
Income poverty, officially at-risk-of-poverty or <em>AROP</em>, is an income
test: a person counts as poor if the income shared across their household,
adjusted for household size, sits below 60% of the country's median income,
recalculated every year. A simple, hypothetical example helps: if the
median equivalised income were &euro;1,000 a month, the <em>AROP</em> line
would sit at &euro;600. Because the median is recalculated every year, the
line itself moves with it: if a country's incomes fall as a whole, the bar
can fall with them. Reported hardship measures something different and more
direct: in the same survey, households are asked how easily they can make
ends meet, and those who say they manage only &ldquo;with difficulty&rdquo;
or &ldquo;with great difficulty&rdquo; count as struggling.</p>

{fig('F1', caption="Greece Is Far Above the Poverty-Hardship Line")}

<p><a class="fig-jump" href="#F1" data-view="0">Figure {{fig:F1}}'s first
tab</a>, &ldquo;How Greece's hardship gap developed&rdquo;, puts those two
measures side by side and shows why the paradox holds. Since 2015, Greece's
reported hardship has never dropped below
two-thirds of households: it opens near 78% and eases only
gradually. Its income-poverty rate spends the same decade hovering near a
fifth, barely moving at all. Both EU medians sit far beneath Greece's line
for reported hardship, the whole way through. (The EU median is the
middle EU country on that measure, not an EU-wide average.) This isn't a
single bad year showing up once. It's been the shape of an entire decade.</p>

<p>Switch to the <a class="fig-jump" href="#F1" data-view="1">second
tab</a>, &ldquo;Where countries stood in 2024&rdquo;, and the gap turns from a Greek pattern into a European outlier. Each grey
dot is an EU country. The horizontal axis is income poverty; the vertical
is reported hardship. The dotted line is the relationship the other
twenty-six countries actually follow. Greece is the blue point far above
it. At Greece's income-poverty rate, that relationship predicts about 20%
of households struggling to make ends meet. Greece reports about 67%. The
47-percentage-point distance between those two numbers is the gap this
piece tries to understand.</p>

{finding('V2-1.2')}

<details class="fig-methods"><summary>Why the chart starts in 2015</summary>
<p class="fig-caveat">Not because Eurostat's data is that young: it's where
Greece's own hardship gap is clearest. The indicator can be reconstructed
back past 2010 too, and this project checked that reconstruction against
the official series everywhere the two overlap, but nothing later in this
piece relies on it.</p></details>

{finding('V2-1.1')}

<p>The two numbers are not rival opinions. They come from the same European
system, from surveys of the same households, but they ask different kinds
of questions: one about income relative to everyone else, one about
a household's own sense of its budget. In most of Europe, those two answers
move together. In Greece, they have stayed far apart, year after year.</p>

<p>But once a gap like that appears, the two numbers are not usually read
with equal trust. Income poverty feels firmer: a number built from income,
thresholds and ranks. Reported hardship feels softer: not necessarily a
fact about a household's circumstances, but the way that household
describes itself. Is that fair? Or is the hardship signal telling us
something material that income poverty alone cannot see?</p>
"""))

# ---- 2. The Ruler Moved With the Fall (ruler + AROPE + divides) -----------
CH.append(chapter("ruler", "The Ruler Moved With the Fall", f"""
<p>One answer starts with the ruler itself: the official poverty line isn't
fixed. It moves with the very economy it is supposed to be measuring.</p>

<p>The EU's headline poverty measure, at-risk-of-poverty, rests on a line
that isn't fixed in money terms. That line is set at 60% of whatever the
national median income happens to be, <em>that year</em>, and <em>AROP</em> itself is
the share of people whose income falls below it. In an ordinary economy,
where incomes drift up slowly and roughly together, that is a reasonable
way to define being poor relative to your neighbours.</p>

<p>Greece's economy, from 2010, was not ordinary. Incomes fell together,
hard and fast, and when the median falls, the poverty line falls with it. A
household earning exactly what it earned five years earlier could find
itself reclassified from poor to not poor, not because anything in
its life had improved, but because the ruler measuring it had shrunk to
match the collapse around it.</p>

{fig('F3', caption="The Poverty Line Looked Stable. Its Value Did Not.")}

<p>Figure {{fig:F3}}'s first tab (<a class="fig-jump" href="#F3"
data-view="0">Who falls below a fixed line</a>) makes the moving-ruler
problem visible: the official poverty rate barely moves because the line is
allowed to fall with the national median. Hold the 2008 line fixed in real
terms instead, and measured poverty roughly doubles, peaking above 40% in
2014. The second tab (<a class="fig-jump" href="#F3" data-view="1">What the
line itself is worth</a>) shows the mechanism more plainly still: the
threshold may look stable in cash terms, but what it can actually buy
collapsed, and has only partly recovered.</p>

{context('CTX-3B', '''
<p>Independent microdata points the same way. A separate study, using
Greek household microdata, estimates that 48% of the population was poor
under a poverty line anchored before the crisis, for the same income year
this project's own reconstruction puts at 40.6%.</p>''')}

<p>That doesn't make the <em>fixed poverty line</em> the &ldquo;correct&rdquo; one, and
this project's own reconstruction of it says nothing about how Greece
compares to any other country: it measures Greece against its own past,
not against Europe. It asks a different
question: the official rate measures who is far below the middle of
<em>today's</em> Greece; the fixed line asks how many people are below a
pre-crisis standard. When a whole country falls together, those two
questions split apart.</p>

<p>Europe's broader measure, <em>AROPE</em> (at risk of poverty or social
exclusion), tries to widen the lens. It counts anyone who meets at least one
of three conditions &mdash; income poverty, severe material deprivation, or
<em>very low work intensity</em> &mdash; rather than income poverty alone, so it
should close the gap if the problem is only that income poverty is too
narrow. It does close some of it: 9.8 of the 52.6 points, under a fifth.
But it leaves most of the distance untouched, and its contribution shrinks
over the decade.</p>

{finding('V2-2.1')}

{fig('F5', caption="Where AROPE Sits, What It's Made Of, and Who Carries It")}

<p>Figure {{fig:F5}} shows both sides of that result. The first tab
(<a class="fig-jump" href="#F5" data-view="0">Headline measures</a>) places
income poverty, <em>AROPE</em> and reported hardship together: <em>AROPE</em> sits between
them, but much closer to income poverty than to hardship. The other tabs
show why one national number is still too smooth. Greece sits above the EU
median on the two components with a comparable national series,
income poverty and material deprivation; the third, very low work
intensity, has no comparable national series and isn't shown. Older people
move in the opposite direction from everyone younger; women remain above
men throughout. The point isn't any one split on its own. It's that the
national average compresses very different household positions into one
line.</p>

<p>The official measures are not wrong. They are doing exactly what they
were built to do. But they measure position, broadened risk and national
averages. The household answering the hardship question is answering
something narrower and more immediate: what daily life costs against its
own budget. That is where the next part of the story has to go.</p>
"""))

# ---- 3. This Was Not Just a Feeling (real + company) -----------------------
CH.append(chapter("footprint", "This Was Not Just a Feeling", f"""
<p>If Greek households are simply answering a subjective question more
darkly than everyone else, then this is a story about how people talk about
their lives, not about poverty. Everything the rest of this piece does next
would be measuring an echo, not an economy. That has to be settled first,
and settled seriously, not waved off as an obvious no.</p>

<p>The test isn't whether one household's answer feels convincing on its
own. It's whether the national annual rate of that feeling moves together,
year after year, with the national annual rates of things that name actual
events, not moods: <em>falling behind on bills</em>, <em>being unable to cover a surprise
expense</em>, <em>being unable to heat the home properly</em>, and <em>material
deprivation</em>, going without several ordinary things at once. A vague question
can drift with a bad national
mood. A national mood drifting in step with four separate, concrete annual
rates, year after year, is a much harder thing for mood alone to
produce.</p>

{fig('F8', caption="Hardship Moves With Concrete Financial Strain")}

<p><a class="fig-jump" href="#F8">Figure {{fig:F8}}</a>: three of the four
tabs tell the same story, each as a correlation, where close to 1 means
two measures rise and fall together and close to 0 means no strong
straight-line relationship shows up between them. In Greece's own
year-by-year data, <em>reported hardship</em> tracks
an inability to cover a surprise expense almost exactly (<a
class="fig-jump" href="#F8" data-view="0">Unexpected expenses</a>) at 0.92.
It tracks going without several ordinary things at once even more closely
(<a class="fig-jump" href="#F8" data-view="1">Material deprivation</a>), at
0.94. It tracks struggling to keep the home warm at 0.87 (<a
class="fig-jump" href="#F8" data-view="2">Keeping the home warm</a>). When
one line moves, the others move with it, year after year. And this isn't a
Greek peculiarity. Pooled across all twenty-seven EU countries, comparing
each country with itself over time rather than just rich countries with
poor ones, the same relationships hold, at 0.63 to 0.80.</p>

{finding('V2-3.1')}

<p>The fourth tab (<a class="fig-jump" href="#F8" data-view="3">Falling
behind on bills</a>) tells a
different story, and it's worth sitting with why.
Falling behind on bills, the one item that sounds like the hardest,
most factual anchor of the four, tracks reported hardship at only
0.37, by far the weakest of the set. Falling behind requires having had
credit and obligations to fall behind on in the first place. A household
that lost access to credit years ago, or never had any to lose, can be in
real difficulty without that difficulty ever showing up as an unpaid bill.
The weakest link in the evidence has a plausible, ordinary explanation,
not a suspicious one &mdash; though this project did not test that
explanation directly.</p>

<p>None of this is independent proof, and that has to be said plainly
rather than buried. Every one of these items comes from the same survey
as the question about making ends meet, and may share a common way of
answering it. A household in a genuinely grim mood could rate the whole set
grimly, and that alone would produce numbers like these. What's been shown
is that reported hardship is coherent with concrete circumstances. It
hasn't been shown, and can't be shown this way, that it's confirmed by
something entirely outside the survey.</p>

<p>There is a second, different kind of check, and it does not depend on
the same hardship questions. If this one number were an isolated fluke,
one instrument twitching on its own, it should stand apart
from everything else describing Greek life. It doesn't.</p>

{fig('F21', caption="The Problem Spread Across the Dashboard")}

<p>Take <em>sixteen separate measures</em> of Greek life (see
<a class="fig-jump" href="#F21">Figure {{fig:F21}}</a>): wages, hours
worked, prices, keeping the home warm, what households expect of the coming
year, income inequality. They were filtered from a wider set of economic
and social indicators to only those with a valid reading in both 2008 and
2024, so the count couldn't grow just because more things got measured
later, and selected without regard to whether each one improved or
worsened, so there was no room to cherry-pick which sixteen made the
basket. The first tab (<a class="fig-jump" href="#F21"
data-view="0">Which measures</a>) lays out where Greece sat on each one, in
2008 and again in 2024, and whether it crossed into the EU's worst fifth, the
bottom 20% of member states on that measure, or was already
there. The point isn't that every one of them moved identically. It's
that disadvantage spread across the dashboard, not just in one place.</p>

<p>Switch to the second tab (<a class="fig-jump" href="#F21"
data-view="1">How many measures</a>) and that spread turns into a single
line. Before the crisis, Greece sat in the worst fifth of the EU on four of
the sixteen, a quarter. Now it sits there on eleven, two
thirds of the whole set. Plotted alongside it, the EU-country median barely
moves over the same seventeen years. This isn't a general European drift.
Most of these measures don't come from the same interview as the hardship
question, either.</p>

<p>The list is not hand-picked. It includes every indicator in the project
with a valid EU position in both 2008 and 2024, selected before looking at
whether Greece improved or worsened. That is why some obvious
labour-market measures are absent here: their comparable EU series begin
in 2009, one year too late for the fixed 2008 basket. <a
href="statistical_appendix.html#p_breadth_fixed_basket">The appendix
shows</a> the fixed basket and the wider candidate set.</p>

<p>One more thing is worth mentioning here, carefully. Put the closest
hardship items into the same statistical picture as the official poverty
rate, and much of Greece's excess stops standing apart. That matters. But
it also carries the same-survey problem all over again, in a sharper form.
And it returns later in this piece, because it turns out to be
exactly the point where the explanation looks strongest and least
independent.</p>

{finding('V2-3.2')}

<p>So the hardship signal is too materially connected to dismiss as mood.
It is also too close to the same survey instrument to call independently
proven. Both of those are true at once, and the honest version of this
section holds them together rather than picking one. What it does settle is
enough to move forward on: if the difficulty is real, why doesn't the
official poverty rate register it?</p>
"""))

# ---- 4. The Jobs Came Back. The Household Economy Did Not. ----------------
CH.append(chapter("recovery", "The Jobs Came Back. The Household Economy Did Not.", f"""
<p>The strongest case for Greece's recovery is the labour market.
Unemployment fell from its crisis peak to under 9%, and <em>long-term
unemployment</em> fell with it. That is real recovery. But a household does
not live on the unemployment rate. It lives on the wage that arrives, the
prices facing that wage, what it costs to keep a roof over its head, and
what is left when the month runs out. On that test, Greece's recovery
looks much less complete.</p>

<p>Start with the part that clearly improved: long-term unemployment,
meaning worklessness lasting twelve months or more. It stood at 16.4% of
the labour force in 2015. By 2024 it had fallen to 5.4%. That is
substantial progress. It means fewer households spent years outside
work &mdash; the kind of prolonged spell that often forces a household to
run through savings, sell what it can, or lean on relatives, even though
this project did not track those responses directly.</p>

<p>But employment recovered furthest, and it was not the whole household
story. Greek <em>real wages</em> stood at about 77%
of their 2008 level in 2015; by 2024, about 68%. Not recovering slowly.
Not recovering. Greek wages have now been below their pre-crisis
level for fifteen consecutive years, longer than any EU country except
Hungary. Output per person sits between the two stories: the shortfall
against Greece's own 2008 peak roughly halved, but it did not close. <em>Actual
individual consumption</em> &mdash; the volume of goods and services households
actually consume, measured in a common purchasing-power unit that strips out
price-level differences between countries, not literal euros &mdash; did
rise substantially, from roughly 14,800 to 21,300 in that unit. That is
real, and worth saying plainly, because
a piece about hardship can leave the impression that nothing improved. But
the EU median rose faster over the same years, so the distance between
Greece and other EU countries widened even as Greece's own number climbed.</p>

{fig('F7', caption="Some Gaps Closed. Others Widened.")}

<p><a class="fig-jump" href="#F7">Figure {{fig:F7}}</a> shows the shape:
gaps that were mostly about jobs and
housing narrowed considerably; the output gap narrowed too, but only by
about half; gaps that were about wages, resources and what money can buy
narrowed barely at all, or widened. But a chart built to fit
fourteen measures onto one axis has to abstract away units, so <a
class="fig-jump" href="#recovery-table">the table below</a> gives the same
story in the numbers each measure actually reports in, and the plainest
reading of each.</p>

{recovery_table()}

<p class="table-legend">The table gives the same comparison in each
measure's own units: percentages for unemployment, output and housing
costs; a common purchasing-power unit for material resources; index
points for wages and affordability. It also keeps the main caution
visible: an improving Greek number is not always a closing gap. Material
resources rose sharply in Greece but fell further behind, because the EU
median rose faster. And a narrowing gap does not tell us why it narrowed.
It only shows the shape of recovery: employment improved most clearly,
while wages, resources and purchasing power remained much more
damaged.</p>

{fig('F10', caption="Recovery Looks Weaker From the Household Budget")}

<p>That same split appears when we stop looking at gaps and look at
today's levels, in <a class="fig-jump" href="#F10">Figure
{{fig:F10}}</a>. Long-term unemployment, material resources and
<em>wage-adjusted affordability</em>
each place Greece on the wrong side of the European middle. They are also
the three current conditions that carry information beyond the official
poverty rate. But the point here is simpler: <strong><em>some indicators
improved; the household did not recover with them.</em></strong></p>

<p>A country can score badly on affordability two ways: by being expensive,
or by paying poorly. Greece does both at once, and a household experiencing
it does not much care which half is responsible.</p>

<div class="finding compact" data-claim-id="V2-4.C2 V2-4.C1 V2-4.C4">
<p><em>Precise result.</em> Long-term unemployment, material resources and
wage-adjusted affordability each predict reported hardship beyond income
poverty and year effects.</p>
<p class="limits"><em>Limits.</em> Cross-country association, not causal
evidence; wage-adjusted affordability should not be read together with the
work-effort-squeeze measure.</p>
</div>

{context('CTX-8', '''
<p>A newer Greece in Figures analysis reaches a similar descriptive
picture from outside this project's models: Greece is not last in Europe
on actual consumption, but it combines long working hours, low hourly
reward and high everyday prices. That does not test this report's
explanation, and it uses a newer data vintage, but it independently
points to the same household-budget pressure.</p>''', expand=True)}

<p>Put simply: the labour market improved, but the household budget did
not recover with it.</p>

<blockquote>The unemployment rate came back. The paycheck did not.</blockquote>
"""))

# ---- 5. A Decade of Damage Still Counts (duration) -------------------------
CH.append(chapter("duration", "The Accumulated Weight of the Crisis", f"""
<p>The jobs came back. The household economy did not. But even that
distinction still looks mostly at where things stand now. For households,
duration matters: one year of
unemployment is not the same as ten. A wage cut that lasts one year is not
the same as one that lasts fifteen. Housing pressure that spikes and
disappears is not the same as pressure that accumulates.</p>

<p>This is also the point where the story is easiest to overstate.</p>

<p>Instead of asking only how bad a condition is today, this section asks
how much of it a country has carried since the crisis began: <em>accumulated
excess unemployment</em>, how much a country has accumulated since the crisis began;
<em>wage duration below 2008</em>, how many consecutive years its wages stayed
below that level; and <em>housing-cost deterioration</em>, how much its housing
costs have deteriorated since 2010.</p>

{fig('F11', caption="Greece Had Among Europe&rsquo;s Largest Accumulated Burdens")}

<p><a class="fig-jump" href="#F11">Figure {{fig:F11}}</a> is the balance
sheet the crisis left behind. Greece
carries the heaviest accumulated unemployment burden in the EU, and the
worst housing-cost deterioration since 2010; both rank first of 27.
On wage duration it's not the heaviest: Hungary has gone slightly longer,
sixteen consecutive years below its 2008 level to Greece's fifteen. The
chart shows every country, not just Greece, so that one exception is
visible rather than buried.</p>

<p>Carrying a heavy history is one thing. Whether that history still
matters once you already know where a country stands today is a harder
question, and a more important one: if you know this year's unemployment
rate, does the decade behind it tell you anything more?</p>

<p>For three measures, it does. Countries carrying more accumulated
unemployment, more years of wages below 2008, and more housing-cost
deterioration report more hardship, even after today's poverty rate
and current conditions are already accounted for.</p>

<div class="finding compact" data-claim-id="V2-5.C2 V2-5.C3 V2-5.C6">
<p><em>Precise result.</em> Accumulated excess unemployment, wage duration
below 2008, and housing-cost deterioration each still predict reported
hardship once today's poverty rate and current conditions are controlled
for.</p>
<p class="limits"><em>Limits.</em> Cross-country association, not causal
evidence, and not a demonstrated change within Greece over time.</p>
</div>

<p>The wage-duration result holds for one specific way of counting
consecutive years below 2008; other reasonable ways of counting the same
idea point the same direction without quite clearing the bar. The housing
result is the shakiest of the three, and it's presented that way rather
than rounded up to a clean yes.</p>

<p>The pattern is not universal, though, which is itself informative. For
<em>wage-adjusted affordability</em>, it runs the other way: today's number carries
the signal, and the accumulated version of it doesn't resolve.</p>

<div class="finding compact" data-claim-id="V2-5.X">
<p><em>Precise result.</em> For wage-adjusted affordability the pattern
reverses: the current measure survives conditioning while the accumulated
one remains inconclusive.</p>
<p class="limits"><em>Limits.</em> Inconclusive, not unsupported.</p>
</div>

<p><em>Compounded inflation</em> was also tested as an accumulated measure, but the
result remained inconclusive under the available statistical power.</p>

<p>The contrast argues against treating accumulated history as a universal
rule. It suggests these results are specific to work, wages and housing
rather than some broad law that the past always counts for everything.</p>

<p>One more piece of the history simply isn't there to look at. What
households could actually afford, tracked back to before the crisis, can't
be built at all: the source data only starts in 2015, already years
into the recovery. Moving the starting line later, to when the data
actually begins, would have solved the data problem and created a
different one: a measure that could no longer see the crisis it exists to
describe. So it stays out, and is named here rather than quietly
absent.</p>

{finding('V2-5.Z')}

{finding('L-3')}

<p>A related wage measure creates the opposite problem. On the face of the
numbers, <em>accumulated wage shortfall</em> looks convincing. But it cannot be
counted here, because the earlier stage did not establish the current
wage-shortfall measure it depends on. A result can only stand as high as
its foundation. It's named here, not because it counts, but because
pretending it doesn't exist would be its own kind of dishonesty.</p>

<p>That is enough to say the crisis left a measurable mark. It is not yet
enough to say how that mark moved inside Greece year by year.</p>

<p>Put together with the rest of this piece, that leaves duration as a real
part of the picture, not the whole of it: countries carrying more
accumulated unemployment, more years of lost wages and more housing
deterioration report more hardship even once today's conditions are
accounted for, though that is an association across countries and not a
demonstrated cause inside Greece. How much of the story that still leaves
unaccounted for, and where this piece's evidence runs out, is what the next
two sections settle.</p>
"""))

# ---- 6. Where the Evidence Stops (between/within + unsettled + flip
#         + the two failed designs) -----------------------------------------
CH.append(chapter("limits", "What Remains Open", f"""
<p>Up to this point, the evidence gives a fairly clear picture for most of
the central questions. The wide gap between <em>reported hardship</em> and <em>income
poverty</em> in Greece is tied closely to specific material deprivations. It
also shows up in a country where the jobs recovery was not matched by an
equivalent recovery in wages, material resources or purchasing power.
There is also evidence that, in some areas, what matters is not only where
a country stands today but how much weight it accumulated over the course
of the crisis.</p>

<p>That picture, though, doesn't answer everything. Two questions get a
more limited answer from the available data. First, the relationships
found for accumulated burden show up clearly when comparing countries with
each other. Showing whether the same relationship played out inside
Greece, year by year, needs more annual observations and more within-country
change than the data can currently offer: with roughly a decade of data,
the relevant estimates stay too uncertain.</p>

<p>Second, while much of the extra hardship Greek households report can be
explained statistically by deprivation measures, those measures come from
the same survey as reported hardship itself, which makes the result less
independent than it looks. There are also factors the available evidence
simply doesn't yet cover well enough to give a clear picture.</p>

<p>Take them one at a time.</p>

<h3>What Can We Say About Change Within the Country Itself?</h3>

<p>The previous section showed that countries carrying more accumulated
unemployment, wage non-recovery and housing pressure tend to report more
hardship even once today's conditions are taken into account. That is a
substantive finding, but it is mostly a statement about differences
between countries.</p>

<p>A different question is whether the same relationship can be seen
unfolding inside one country: whether hardship in Greece rose or fell as
the crisis burden built up or eased. This project tested that version too,
but roughly ten annual observations per country do not give enough
precision for a clean answer.</p>

<div class="finding compact" data-claim-id="V2-5.Y">
<p><em>Precise result.</em> Across three related tests, no within-country
estimate across the panel clearly supported the expected direction. The
evidence therefore cannot show that hardship rose inside Greece as the
damage accumulated.</p>
<p class="limits"><em>Limits.</em> These are three related checks on the
same data, not three independent confirmations, and they weren't
adjusted for running several checks at once.</p>
</div>

{subfig('F13A', 'F13', 0,
        "The Strongest Evidence Comes From Between-Country Differences",
        "Do we see the accumulated burden only when comparing countries, or also when tracking one country over time?")}

<p><a class="fig-jump" href="#F13A">Figure {{fig:F13A}}</a> makes that
distinction visible. Comparing countries against each other, the ones
carrying more accumulated burden do tend to report more hardship. Trying
to track the same relationship inside each country over time, the
estimates become far less certain. So there is a fair amount known about
how countries differ from one another, and less about how that specific
mechanism played out inside Greece itself.</p>

<h3>How Much Does the Explanation Depend on What Goes Into the Model?</h3>

<p>The second open question concerns the <em>deprivation items</em> <a
href="#ch{{ch:footprint}}">from earlier</a>, things like being unable to
cover an unexpected expense, inadequate heating and payment arrears. These
items track reported hardship very closely, and when added to the model
alongside income poverty, they absorb most of Greece's excess.</p>

<p>That result matters, but it has one key catch: the deprivation items and
reported hardship come from the same survey. That produces two equally
defensible analytical choices. Including them draws on information very
close to households' day-to-day economic experience. Excluding them avoids
explaining one survey answer with other answers collected through the same
instrument. Both versions were built, and Greece's position changes
sharply depending on which one is used.</p>

<div class="finding compact" data-claim-id="V2-6.1">
<p><em>Precise result.</em> Greece's residual reverses from positive to
negative, and its rank from 3rd of 27 to 25th of 27, depending on whether
the same-instrument deprivation predictor is included.</p>
<p class="limits"><em>Limits.</em> Neither specification is definitive;
the two may not be merged or averaged, and selection between them may not
be made on residual size.</p>
</div>

{fig('F14', caption="One Predictor Flips Greece From Third-Worst to Twenty-Fifth")}

<p><a class="fig-jump" href="#F14">Figure {{fig:F14}}</a> shows it: Greece
moves from the third-worst country
in Europe on <em>unexplained hardship</em> to the twenty-fifth, from a stark
positive outlier to a stark negative one, on exactly the same rows of
data, with one measure added or removed. The two results can't be
averaged, and can't be chosen between by which looks more plausible;
doing that is exactly what would make a check like this meaningless.
Which is why nothing later in this piece leans on it.</p>

<details class="disclosure"><summary>The measures that went quiet, and the designs that failed</summary>

<p>Not every present-day measure earned a place in the story so far, and
the reason is statistical power rather than a verdict against them. Nine were tried; three worked. The other six mostly went quiet
rather than failed outright: with twenty-seven countries and a decade of
data, most of them could only have caught an effect bigger than any
effect worth caring about. Silence isn't a verdict. A few can be set
aside for real, at least at the size this design could catch, and they are
all measures of price inflation. The rest simply weren't put under
enough pressure to say either way.</p>

<div class="finding compact" data-claim-id="V2-4.X L-4">
<p><em>Precise result.</em> Six of nine current-level measures are
inconclusive under the available statistical power, not unsupported.
Annual food and housing inflation can be set aside with adequate power,
and annual headline inflation at the magnitude this design could detect;
compounded inflation since 2008 remains inconclusive.</p>
<p class="limits"><em>Limits.</em> Inconclusive is not evidence of
absence; the exclusions that do hold are narrow and specific to the size
this design could detect.</p>
</div>

<p>Two further ideas were meant to carry real weight here, and neither
survived contact with the data. They are named rather than quietly dropped. A synthetic Greece, built to track the real one before 2008 and
read the divergence after as the crisis effect, collapsed into a blend of
essentially two countries and missed four of the six conditions it had
been required to meet before anyone looked at the result. Its chart is
not shown here, because a dramatic picture built on a counterfactual that
thin would persuade readers of something the evidence can't actually
support. And the sixteen-measure spread <a
href="#ch{{ch:footprint}}">from earlier</a> made Greece's position worse,
not better, once it was asked to predict rather than just describe, and
its direction flipped once other measures were held steady, left
deliberately unexplained here, since inventing a story for a strange
result in a design that already failed is how failed ideas come back
from the dead. Both are recorded for what they are: attempts that didn't
work, kept visible rather than erased.</p>

<div class="finding compact" data-claim-id="L-1 L-2">
<p><em>Precise result.</em> The synthetic-control comparison failed four
of six pre-registered gates and is not usable; its own chart is withheld
for that reason. Adding the sixteen-measure spread to the frozen model
worsened Greece's residual and reversed its sign.</p>
<p class="limits"><em>Limits.</em> Both are attempts that did not work,
not findings; the sign reversal in the second is deliberately left
uninterpreted.</p>
</div>

</details>

<p>That is as far as the quantitative analysis goes. It has answered a
substantial part of the original question, but not every possible
mechanism behind Greece's particular pattern. Factors such as trust in
institutions, adjustment policies, migration, taxation, health, and the
way people answer subjective questions may also be part of the picture.
Some of these are examined next with the available evidence; for others,
all that can be done is describe what is known and what remains
open.</p>
"""))

# ---- 7. What the numbers still miss (reporting style + ESS + context
#         register + the close) ---------------------------------------------
CH.append(chapter("leftover", "What the Numbers Still Miss", f"""
<p>There is a simpler explanation for everything above, and it deserves to
be taken seriously rather than waved away: maybe Greeks are just gloomier
answerers. The evidence so far can't fully settle that: the strongest
corroboration for <em>reported hardship</em>, the concrete deprivation items from
earlier, comes from inside the same survey as the hardship question
itself. The external evidence elsewhere in this piece &mdash; wages,
employment, what households can actually buy, the <em>sixteen-measure
spread</em> &mdash; doesn't share that problem, but none of it was built to test
reporting style directly.</p>

<h3>Financial Expectations and Life Satisfaction</h3>

<div class="ctx-inline" data-context-id="CTX-1">

<p>A better test looks across different subjects entirely, drawing on a
separate reporting-style comparison built for this project
(reporting_style_cross_indicator.csv). A general tendency to answer darkly
should drag everything down about equally; a pattern that is extreme on
money and milder elsewhere points at circumstances instead. Read as
descriptive corroboration rather than an independent test, the table below
makes that comparison directly: Greece against the EU on three different
kinds of question, not just the one this piece has leaned on so far.</p>

{domain_table()}

<p>Greece is worst in Europe on the two money questions and close to
worst on general <em>life satisfaction</em>: a difference of degree, not of kind,
which suggests some domain specificity, though a broader negative reporting
tendency is not ruled out.</p>

{finding('V2-7.1')}

<p>One thing about that life-satisfaction number is worth holding onto,
because it's easy to get backwards: it actually <em>rose</em> over the
period. Describing Greece as merely ordinary or middling here would be
wrong: it is second-worst in the EU by 2024. Its rank fell anyway, because
other, faster-improving EU countries pulled further ahead, so reading that
worsening rank as a falling level would be its own mistake. A falling rank
is not the same thing as a falling number.</p>

</div>

<h3>Pre-Crisis Wellbeing Baseline</h3>

<p>One further check reaches back before the Eurostat series begins. A
separate European survey shows Greece already sitting about 0.8 points below
its comparison group before the crisis, falling further during it, and
recovering its level, but not its relative position, by the 2020s. A long-standing pattern of lower reported wellbeing remains plausible
on this evidence. It also cannot be established by it.</p>

{context('CTX-7', '''
<p>Across six rounds of a separate European survey, holding the same twelve
countries fixed each time, Greece's level fell and then recovered while its
position relative to the others did not. This is descriptive corroboration
and not a test.</p>''')}

<h3>Health</h3>

<p>Health is different from the factors that follow: it was tested, not
skipped. Greece has one of the EU's highest rates of unmet medical
need &mdash; worst in the Union by 2024, several times the typical member
state &mdash; and that is a real, troubling fact about Greek life in its
own right.</p>

<p>But four separate health measures, tested against the same baseline
used elsewhere, do not explain the hardship gap: none of them clears the
bar this project sets. Three of them &mdash; <em>self-rated health</em>,
<em>long-standing illness</em> and <em>activity limitation</em> &mdash; carry a puzzling sign at the country
level, where worse reported health goes with <em>less</em> reported
hardship, and that flips once countries are compared with their own past
rather than with each other: within a country, years of worse health are
years of more hardship, the expected direction. The fourth, <em>unmet medical
care</em>, doesn't have that problem &mdash; it points the expected way in both
comparisons &mdash; but its result changes if any single country is
dropped, which is why it doesn't clear the bar either. So the health fact
stands as real, without becoming part of this piece's explanation for the
gap.</p>

<h3>Migration</h3>

<p>Large numbers of working-age Greeks left during the crisis, and some
have returned. This cuts both ways: plausibly a consequence of a broken
labour market, and plausibly part of why the people who stayed look the
way they do. Unlike most of the factors that follow, this one was tested
directly, as an aggregate predictor of hardship across countries.</p>

{context('CTX-4', '''
<p>When migration was tested as an aggregate predictor of hardship across
countries, no clear statistical relationship emerged.</p>''')}

<p>Other factors often appear in accounts of the Greek crisis, and none of
them was established here. Leaving them out silently would be misleading;
treating them as findings would be worse, so they are recorded for what they
are.</p>

<details class="disclosure"><summary>Other possible factors</summary>

{context('CTX-2', '''
<p>Trust in institutions is low in Greece, and there is a plausible route by
which it could matter: a household that doesn't expect help to arrive may
experience the same circumstances as more frightening. This piece has no
check on that either way.</p>''')}

{context('CTX-3', '''
<p>The bailout programmes from 2010 reshaped incomes, job protections,
pensions and public services at once and in a hurry. They are the backdrop
to every accumulated measure described earlier.</p>''')}

{context('CTX-5', '''
<p>Published research establishes that Greece's system of indirect taxes
became markedly harder on lower-income households across the crisis. If a
household's position worsened through tax in a way income-based poverty
measures capture badly, that would be one route to the kind of gap this
report describes.</p>''')}

{context('CTX-9', '''
<p>Independent ECB data show that of the &euro;224.8bn increase in Greek
household net wealth between 2019 and early 2026, about 72.6% went to the
wealthiest fifth of households, while the bottom half accounted for about
9.2% and saw its own share of total wealth slip slightly. A national wealth
total climbing while most of the gain bypasses the bottom half of the
distribution is one plausible way that recovery and persistent hardship
can sit side by side &mdash; this project never tested wealth against its
own hardship measure directly, so it is offered as a plausible mechanism,
not a demonstrated one.</p>''')}

{context('CTX-10', '''
<p>Eurostat data show that in 2023, out-of-pocket payments covered 34.3% of
current health expenditure in Greece &mdash; the third-highest share in the
EU, behind Bulgaria and Latvia, against an EU average of about 14.9%. An
unusually large share of health costs landing directly on the household
budget, rather than being pooled through public or insurance financing, is
one plausible contributor to reported hardship &mdash; this project never
tested health financing against its own hardship measure directly, so it
is offered as a plausible mechanism, not a demonstrated one.</p>''')}

</details>
"""))

# ---- 8. What It Adds Up To (the close) -------------------------------------
CH.append(chapter("conclusion", "What It Adds Up To", f"""
<div class="ctx-inline" data-context-id="CTX-6">

<p>Greek households report struggling at a rate far above what the official
poverty figure predicts, and have done so consistently for a decade. What
runs through the whole of this piece is that no single official number
captures what Greek households are reporting: each one misses something
different, and the measure that catches what the others miss is not the
headline figure. Part of that distance is now easier to understand.</p>

<p><em>AROP</em> measures something narrower than the economic experience it is often
asked to summarise. Because the poverty line moves with national income, it
can stay relatively stable even as living standards fall substantially.
<em>AROPE</em> widens the picture, but covers only part of the gap. Reported hardship,
meanwhile, moves with specific material deprivations, and conditions in
work, material resources and purchasing power add information <em>AROP</em> alone
does not capture. Greece also carries one of Europe's largest accumulated
burdens: first of 27 EU countries on accumulated unemployment and on
housing-cost deterioration, second on consecutive years of wages below
their 2008 level. Today's conditions alone are not enough to explain the
hardship; what the country went through to get here matters too.</p>

<p>Some headline indicators improved. Greek society did not recover with
them. Employment improved substantially, and housing pressure eased from its
most extreme levels. But GDP per person never returned to its 2008 level,
real wages remained far below it, and on the material-resources and
purchasing-power measures that matter most, Greece still lags well behind
the European median.</p>

<p>A generally more negative way of answering cannot be fully ruled out. What
can be ruled out is the easy version of that argument: that reported
hardship has no material basis. It moves with concrete material
difficulties and fits a wider pattern of economic disadvantage. The factors
we were able to test help explain much of the picture, but not the whole of
the 52.6-point gap. The part that remains unexplained by the available
models is not evidence of Greek pessimism. Institutional trust, adjustment
policy, tax burden, wealth distribution, migration and access to healthcare
remain plausible parts of the explanation, but were not established here as
causes.</p>

<p><em>AROP</em> is not wrong: it measures exactly what it was designed to
measure, who falls below a threshold set relative to today&rsquo;s national
median income. That is a different question from whether Greek households
have regained the living standards and economic security they lost during
the crisis. For that second question, <em>AROP</em> on its own is not
enough.</p>

<p>Perhaps, then, the problem is not that Greek households failed to
recognize the recovery. It is that public discourse treated improvements in
certain indicators as proof of recovery, before living standards, purchasing
power and the economic security of society had actually been restored. The
political point that follows is a simple one: we cannot use indicators to
certify recovery, then shift responsibility onto households&rsquo;
psychology and choices when their experience tells a different story. This
closing synthesis is author interpretation rather than a new empirical
result: it follows directly from what the analysis showed AROP alone
misses, not from an additional test that itself produced this finding.</p>

</div>
"""))


# ===========================================================================
#  PAGE
# ===========================================================================
BASE = ce.base_style((OUT / "build" / "report.html").read_text())

# ---- section order ----------------------------------------------------------
# Seven sections, argued in sequence, no grouping layer above them. The old
# five-act structure grouped eighteen chapters; regrouping seven substantial
# sections under acts would just be relabelling the same reset.
SECTION_ORDER = ["paradox", "footprint", "ruler", "recovery", "duration",
                  "limits", "leftover", "conclusion"]
if sorted(SECTION_ORDER) != sorted(CH_KEYS):
    raise SystemExit(
        "section order does not match the sections actually defined -- "
        f"missing {sorted(set(CH_KEYS) - set(SECTION_ORDER))}, "
        f"unknown {sorted(set(SECTION_ORDER) - set(CH_KEYS))}")

# ---- table of contents -------------------------------------------------
# One line per section: title plus a plain-language gloss of the section's
# job, doubling as both a map of the argument's shape and the "in this
# piece" summary a reader gets before committing to several thousand
# words. Keyed against SECTION_ORDER's keys, not the rendered titles, so a
# renamed or reordered section forces this table to be touched too rather
# than silently drifting out of sync with what the piece actually says.
TOC_GLOSS = {
    "paradox": ("Real Hardship, or Greek Pessimism?",
                "The paradox: two official measures, one gap this piece "
                "tries to explain."),
    "footprint": ("This Was Not Just a Feeling",
                  "Testing whether reported hardship is mood, or "
                  "something real."),
    "ruler": ("The Ruler Moved With the Fall",
              "Why the official poverty rate barely registered the "
              "crisis."),
    "recovery": ("The Jobs Came Back. The Household Economy Did Not.",
                 "What recovered, and what didn't."),
    "duration": ("The Accumulated Weight of the Crisis",
                 "Whether the length of the crisis still matters today."),
    "limits": ("What Remains Open",
               "Two questions where the available data give a more "
               "limited answer."),
    "leftover": ("What the Numbers Still Miss",
                 "Factors that were tested, and factors that were not."),
    "conclusion": ("What It Adds Up To",
                   "How the story ends."),
}
if set(TOC_GLOSS) != set(SECTION_ORDER):
    raise SystemExit(
        "the table of contents doesn't match SECTION_ORDER -- "
        f"missing {sorted(set(SECTION_ORDER) - set(TOC_GLOSS))}, "
        f"unknown {sorted(set(TOC_GLOSS) - set(SECTION_ORDER))}")
TOC = ('<nav class="narr-toc" aria-label="In this piece">'
       '<p class="narr-toc-label">In this piece</p><ol>' +
       "".join(f'<li><a href="#ch{{ch:{k}}}">'
               f'<span class="narr-toc-title">{TOC_GLOSS[k][0]}</span>'
               f'<span class="narr-toc-gloss">{TOC_GLOSS[k][1]}</span></a></li>'
               for k in SECTION_ORDER) +
       "</ol></nav>")

BODY = TOC + "".join(CH_BY_KEY[k] for k in SECTION_ORDER)

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
.stat--official .n{{font-size:3.4rem;font-weight:700;color:var(--text-secondary)}}
.stat--lived .n{{font-size:3.4rem;font-weight:700;color:var(--text-primary)}}
.stat .pct{{font:600 .8rem/1 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin-top:.35rem}}
.stat .l{{font:600 .76rem/1.4 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.02em;color:var(--text-secondary);margin:.5rem 0 0;max-width:19ch}}
.stat .l b{{color:var(--text-primary)}}
/* Named narr-toc, not toc: chart_engine's own CSS already defines a .toc
   class (the appendix's navigation), and reusing the name here collided
   with it -- this container inherited display:flex with no width or
   flex-basis from that other rule and collapsed to zero width. */
.narr-toc{{margin:0 0 3rem;padding-top:.4rem}}
.narr-toc-label{{font:600 .74rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 .9rem}}
.narr-toc ol{{list-style:decimal;margin:0;padding-left:1.4rem;
  display:flex;flex-direction:column;gap:.85rem}}
.narr-toc li::marker{{font:600 1rem/1 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary)}}
.narr-toc a{{display:block;text-decoration:none;color:inherit}}
.narr-toc a:hover .narr-toc-title{{color:var(--series-gr)}}
.narr-toc-title{{display:block;font-weight:700;font-size:1.02rem;
  letter-spacing:-.005em;transition:color .15s}}
.narr-toc-gloss{{display:block;font-size:.92rem;line-height:1.4;
  color:var(--text-secondary);margin-top:.15rem}}
.ch{{margin:5rem 0 0}}
.ch h2{{font-family:'Fraunces Bundled',Georgia,'Times New Roman',serif;
  font-weight:700;font-size:clamp(1.6rem,4.2vw,2.1rem);margin:0 0 1.3rem;
  letter-spacing:-.01em;text-wrap:balance}}
.ch p{{margin:0 0 1.05rem}}
.ch a{{color:var(--series-gr);font-variant-numeric:lining-nums}}
/* fig-jump: a prose reference that both scrolls to its figure and (if it
   names one) switches to a specific tab, rather than sitting there as
   dead text next to a chart the reader has to go find. Georgia's BODY
   serif uses old-style figures by default -- digits sized and placed to
   blend with lowercase letters, so "1" sits at x-height with no cap-height
   reach. That reads as merely quirky in a price or a year; right after
   "Figure" it reads as visibly low, since "Figure" ends in a cap-height
   letter and the reader's eye expects the number to match it. The figure's
   OWN caption never has this problem, because it renders in a different,
   sans-serif face. lining-nums (inherited from .ch a above) forces the
   modern, cap-height digit forms for every in-prose link, figure references
   included, without changing how digits render anywhere else in the piece. */
.fig-jump{{border-bottom:1px dotted var(--series-gr)}}
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
details.ctx-detail{{margin:.6rem 0 0}}
details.ctx-detail summary{{cursor:pointer;font:600 .78rem/1
  ui-sans-serif,system-ui,sans-serif;letter-spacing:.04em;
  color:var(--text-secondary);padding:.2rem 0}}
details.ctx-detail[open] summary{{margin-bottom:.4rem}}
details.ctx-detail .permitted{{margin-top:0}}
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
.table-legend{{margin:-1.1rem 0 1.6rem;font-size:.86rem;
  color:var(--text-secondary)}}
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
#
# A typed number is indistinguishable from a resolved one once rendered, so
# the ban on hardcoded figure numbers has to live here, over this file's own
# source -- the same pattern 90_build_paper.py already uses for the same
# reason. Comments and docstrings are not prose a reader sees, so they're
# stripped before the check, same as there.
_src = Path(__file__).read_text()
_src_prose = re.sub(r"^.*?_FROZEN", "", _src, flags=re.S)
_src_prose = "\n".join(l for l in _src_prose.splitlines()
                       if not l.lstrip().startswith("#"))
_typed = [" ".join(m.group(0).split())
          for m in re.finditer(r".{0,40}\bFigure \d+\b.{0,25}", _src_prose)
          if "{fig:" not in m.group(0) and "fignum" not in m.group(0)]
if _typed:
    raise SystemExit(
        "figure numbers typed into prose instead of {fig:FID} tokens: "
        + "; ".join(_typed[:3]))

# ---- glossary: bold + hover definition on each term's first mention ------
EN_GLOSS = {
    "AROP": "The EU's official income-poverty measure: the share of people "
        "with income below 60% of the national median.",
    "AROPE": "The EU's broader measure: anyone meeting at least one of three "
        "conditions -- income poverty, severe material deprivation, or very "
        "low work intensity.",
    "income poverty": "Also called AROP, defined just below.",
    "reported hardship": "The share of households telling the EU-wide survey "
        "they make ends meet ‘with difficulty’ or ‘with great "
        "difficulty’.",
    "fixed poverty line": "Poverty measured against the poverty line's own "
        "2008 real value held constant, instead of a line that moves with "
        "the current median every year.",
    "very low work intensity": "Living in a household where working-age "
        "members worked less than 20% of their combined potential working "
        "time over the past year.",
    "falling behind on bills": "Share of households unable to pay a "
        "scheduled housing, utility or loan payment on time in the past 12 "
        "months.",
    "being unable to cover a surprise expense": "Share of households that "
        "could not cover an unexpected expense equal to the national "
        "poverty line from their own resources.",
    "being unable to heat the home properly": "Share of households "
        "reporting they cannot keep their home adequately warm.",
    "material deprivation": "Share of households unable to afford several "
        "ordinary items or activities at once, out of a fixed EU-wide list.",
    "real wages": "Wages adjusted for inflation, so they reflect actual "
        "purchasing power rather than just a nominal rise.",
    "wage-adjusted affordability": "How far prices have risen relative to "
        "wages -- how much purchasing power households have actually lost.",
    "accumulated excess unemployment": "Unemployment above a country's own "
        "pre-crisis rate, summed year over year since the crisis began.",
    "wage duration below 2008": "How many consecutive years a country's real "
        "wages have stayed below their own 2008 level.",
    "housing-cost deterioration": "How much, and for how long, housing-cost "
        "burden has worsened, accumulated over time since 2010.",
    "Compounded inflation": "Inflation summed year over year from a "
        "reference point, rather than measured only annually.",
    "accumulated wage shortfall": "The cumulative gap between a country's "
        "real wages and their 2008 level, summed year over year.",
    "deprivation items": "The individual material-deprivation indicators -- "
        "arrears, a surprise expense, heating -- that together make up the "
        "hardship picture.",
    "unexplained hardship": "The share of reported hardship a statistical "
        "model cannot account for using the mechanisms this project tested.",
    "life satisfaction": "People's self-reported overall satisfaction with "
        "their life, on a 0-10 scale, as recorded in the EU-wide survey.",
    "long-standing illness": "Share of people reporting a chronic health "
        "problem lasting six months or more.",
    "self-rated health": "How a person rates their own general health, from "
        "very good to very bad.",
    "activity limitation": "Share of people reporting they are limited in "
        "daily activities because of a health problem.",
}

_main = ce.apply_glossary(resolve_fig_nums(resolve_refs(BODY)), EN_GLOSS)

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>If Greece Has Recovered, Why Do So Many Households Still Struggle?</title>{BASE}
<style>{ce.CSS}
{ce.TERM_CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu)}}
{NARR_CSS}</style></head><body>
<header class="masthead">
<p class="rubric">The Greek Poverty Paradox</p>
<h1>If Greece Has Recovered, Why Do So Many Households Still Struggle?</h1>
<p class="standfirst">Greece&rsquo;s labour market recovered faster than its
households. The distance between income poverty and reported hardship shows
what the recovery headlines leave out: a moving poverty line, damaged wages,
pressure on purchasing power and the long shadow of the crisis.</p>
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
<script>
// FIG-JUMP: a prose reference naming a figure and one of its tabs is a
// dead pointer unless clicking it actually takes the reader there. This
// finds the figure by the link's own #id, switches it to the named tab (if
// the link names one, via data-view -- the same viewbar buttons a reader
// would click by hand, so it reuses chart_engine's own state instead of
// duplicating it), then scrolls to it. ce.JS mounts every chart on
// DOMContentLoaded with no lazy loading, so the tab buttons this depends on
// already exist by the time a reader can click anything.
document.addEventListener('click', function (e) {{
  var a = e.target.closest('a.fig-jump');
  if (!a) return;
  var id = a.getAttribute('href').slice(1);
  var target = document.getElementById(id);
  if (!target) return;
  e.preventDefault();
  var view = a.dataset.view;
  if (view !== undefined) {{
    var host = target.querySelector('.chart-live');
    var bar = host && host.previousElementSibling;
    if (bar && bar.classList.contains('viewbar')) {{
      var btn = bar.children[Number(view)];
      if (btn) btn.click();
    }}
  }}
  target.scrollIntoView({{block: 'start', behavior: 'smooth'}});
}});
</script>
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
# A data-claim-id attribute may hold several space-separated ids at once (one
# compact disclosure covering more than one claim), so check membership in
# any attribute's token list rather than requiring an exact one-id match.
_placed_ids = {tok for m in re.finditer(r'data-claim-id="([^"]*)"', PAGE)
               for tok in m.group(1).split()}
absent = [i for i in required if i not in _placed_ids]
if absent:
    raise SystemExit(f"claims required in the narrative but absent: {absent}")

# A substring check only proves the id string appears somewhere on the
# page -- an empty tag carrying just the attribute would pass it. What the
# register actually requires is a container whose own text carries the
# status label, the permitted interpretation, the limitation and the
# citation together, the same test audit_parity.py --release runs at
# release time. Running it here means a hollow container fails the build
# immediately instead of only at release-verify.
from claim_anchors import context_containers, context_completeness
for cid in ctx.index:
    found = context_containers(PAGE, cid)
    if not found:
        raise SystemExit(f"context entry {cid} never placed")
    entry = {"status": ctx.loc[cid, "status"], "permitted": ctx.loc[cid, "permitted"],
             "forbidden": ctx.loc[cid, "forbidden"],
             "source": "" if str(ctx.loc[cid, "source_status"]) == "not applicable"
                       else ctx.loc[cid, "source"]}
    miss = context_completeness(found[0], entry)
    if miss:
        raise SystemExit(f"context entry {cid} container is missing {', '.join(miss)}")

stripped = re.sub(r"<script.*?</script>", " ", PAGE, flags=re.S)
visible = html.unescape(re.sub(r"<[^>]+>", " ", stripped))
BANNED = ["V2-", "CTX-", "L-1", "L-2", "L-3", "L-4", "frozen claim", "aic_pps_pc",
          "ltu_rate", "wadj_a01", "data-claim-id"]
leaked = [b for b in BANNED if b in visible]
if leaked:
    raise SystemExit(f"internal vocabulary visible in the narrative: {leaked}")

# Stage and construct labels (E7, P3a, C1) are how this project names its own
# machinery. They belong in the technical report, and reached readers here
# through three routes at once: claim caveats, context-register fields and a
# figure's own caveat, none of which passed through reader_text().
_stage_codes = sorted(set(re.findall(r"\b(?:E\d|P\d[a-z]?|C\d)\b", visible)))
if _stage_codes:
    raise SystemExit(
        f"internal stage labels visible in the narrative: {_stage_codes}")

# The findings carry their own statistics and those stay as established. The
# companion's OWN prose is what has to stay clear of jargon, so it is checked
# separately, with the finding and context blocks removed first.
# Figures are lifted from the technical report and carry their own labelling,
# which is technical by necessity: an axis has to say what it measures. The
# companion's job is to explain each one in plain words alongside it, which is
# what the surrounding prose does. So figures are excluded here too.
prose = re.sub(r"<figure class=\"figure\".*?</figure>", " ", stripped, flags=re.S)
prose = re.sub(r'<div class="(?:finding|ctx)(?:\s[^"]*)?".*?</div>', " ", prose, flags=re.S)
prose = html.unescape(re.sub(r"<[^>]+>", " ", prose))
JARGON = ["bootstrap", "p-value", "coefficient", "specification", "estimator",
          "fixed effects", "statistically significant", "confidence interval",
          "regression", "multiplicity", "residual"]
found = [j for j in JARGON if j in prose.lower()]
if found:
    raise SystemExit(f"jargon in the companion's own prose: {found}")

(OUT / "narrative.html").write_text(PAGE)
print(f"wrote output/narrative.html  {len(PAGE):,} chars")
