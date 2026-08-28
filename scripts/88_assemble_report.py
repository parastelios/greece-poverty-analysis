"""Assemble the final technical report from the eight-stage story.

Figures are NOT rebuilt here. They are lifted verbatim from the four batch
pages, each of which already passed the 65 figure checks, so every checksum,
fallback table, badge and caveat travels with its figure unchanged. What is
authored here is the prose: the stage openers, the interpretation between
figures, the methods expandables and the conclusion.

Composition is bound to two frozen artifacts, and neither may be paraphrased
loosely:
  * e_final_claims.csv   -- canonical wordings and their caveats
  * context_register.csv -- what each contextual entry permits and forbids

Reading path targets: 10,000-12,000 words in the main path, 4,000-6,000 behind
the methods expandables.
"""
import html
import math
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
OUT, PROC = ROOT / "output", ROOT / "data" / "processed"

claims = pd.read_csv(PROC / "e_final_claims.csv").set_index("id")
DISPLAY_CODES = sorted(ce.DISPLAY, key=len, reverse=True)
ctx = pd.read_csv(PROC / "context_register.csv").set_index("id")

# ---- figures come from the batch pages, never rebuilt ----------------------
FIG_SOURCE = {}
for n in (1, 2, 3, 4):
    page = (OUT / "build" / f"batch{n}.html").read_text()
    for m in re.finditer(r'<figure class="figure" id="(F\d+)">.*?</figure>', page, re.S):
        FIG_SOURCE[m.group(1)] = m.group(0)

# Derived from the frozen manifest, never hardcoded: a hardcoded range silently
# stops covering any figure added after it was written.
# The manifest declares WHERE each figure is published. The report places the
# main-path set; the six marked "appendix" are not deleted, they are carried in
# the statistical appendix with their ids, payloads and tables intact, and the
# superset gate checks them there.
_MAN = pd.read_csv(PROC / "report_visual_manifest.csv")
EXPECTED = list(_MAN.loc[_MAN.venue == "report", "id"])
APPENDIX_ONLY = list(_MAN.loc[_MAN.venue == "appendix", "id"])

# Non-figure blocks that also travel from the batch pages. The ESS comparison
# leads with a table rather than a chart, and a table is not a <figure>, so it
# needs lifting explicitly -- the assembler would otherwise carry prose
# referring to a table the document does not contain.
BLOCKS = {}
for _n in (1, 2, 3, 4):
    _page = (OUT / "build" / f"batch{_n}.html").read_text()
    for _m in re.finditer(r'<div class="(ess-table)">.*?</p></div>', _page, re.S):
        BLOCKS[_m.group(1)] = _m.group(0)


def block(key):
    if key not in BLOCKS:
        raise SystemExit(f"block '{key}' not found in any batch page")
    return BLOCKS[key]
missing = [f for f in EXPECTED if f not in FIG_SOURCE]
if missing:
    raise SystemExit(f"figures missing from the batch pages: {missing}")

_used = []


def fig(fid):
    """Place a built figure, numbered in the order the reader meets it.

    The internal id is not a figure number. The report places twenty figures,
    the paper six and the companion five, so a shared number would be wrong in
    two documents out of three. Each numbers its own, in reading order.
    """
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    return FIG_SOURCE[fid].replace(
        "<figcaption>",
        f'<figcaption><span class="fignum">Figure {len(_used)}</span> ', 1)


def fig_with_extra_fallback(fid, extra_html):
    """Place a figure, with extra content inside its OWN "Show the numbers"
    disclosure rather than as a second, separate block after it.

    A figure's native fallback table is required -- it is what a screen
    reader or a printed page sees in place of the chart, and its checksum is
    load-bearing. It is not always the most readable table for a sighted
    reader following the argument, though: F7's fourteen measures share one
    dimensionless axis and lose their own units and the EU-country median to
    do it. Rather than surface a second table in the main reading path (which
    a reader has no reason to expect and would have to notice is related),
    the more readable version goes inside the SAME disclosure, after the
    table the chart requires.
    """
    built = fig(fid)
    marker = "</details>\n</figure>"
    if marker not in built:
        raise SystemExit(f"{fid}: fallback closing tag not found for extra_fallback")
    return built.replace(marker, extra_html + marker, 1)


# Presentation only. The claim set is frozen and is NOT edited here: this
# rewrites how a frozen wording is DISPLAYED, never what it says. Two kinds of
# substitution are allowed, both content-free:
#   * "Material resources (aic_pps_pc)" -> "Material resources". The internal
#     name is a redundant gloss; the reader-facing name already precedes it.
#     The code stays in the tables, the tooltips and the methods panels.
#   * internal specification labels -> the words the report uses for them.
# The canonical text remains in e_final_claims.csv and the research record.
SPEC_WORDS = {
    "the frozen P3 specification": "the reference specification",
    "the frozen model": "the reference model",
    "machine-blocked from every output document":
        "excluded from every document in this project",
}


def reader_text(s):
    s = str(s)
    for code in DISPLAY_CODES:
        s = s.replace(f" ({code})", "")
    for a, b in SPEC_WORDS.items():
        s = s.replace(a, b)
    return s


def _num(v):
    if isinstance(v, float):
        return f"{v:.1f}" if v % 1 else f"{v:.0f}"
    return str(v)


def artifact_table(tid, path, cols, headers, note="", text_cols=()):
    """A results table generated from its artifact, never transcribed.

    Two figures became tables outright: three numbers on one axis is a table
    wearing a chart's clothes, and three indicators on three unrelated scales
    -- a percentage, a net balance and a 0-10 rating -- cannot be compared
    across a shared axis. A third case, T-RECOVERY, sits beside a chart that
    was kept rather than replaced: the dimensionless axis it shares is honest
    for the comparison it makes, but a reader also wants each measure's own
    units and the EU-country median written out, which that axis cannot
    carry. All three are honest only if GENERATED. A hand-typed table is a
    figure's numbers copied once and then left behind to drift. Release
    condition 17 compares every cell rendered here against the CSV it came
    from.

    text_cols names any non-first column that is prose rather than a number
    or a short code -- T-RECOVERY's "plain reading" is a sentence, and every
    other column so far has been short enough that right-aligning it read
    fine. Right-aligning a sentence does not.
    """
    d = pd.read_csv(PROC / path)
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = ""
    for r in d.itertuples():
        cells = ""
        for i, c in enumerate(cols):
            v = getattr(r, c)
            txt = v if isinstance(v, str) else _num(v)
            if i == 0:
                cells += f"<th scope='row'>{html.escape(str(txt))}</th>"
            elif c in text_cols:
                cells += f"<td>{html.escape(str(txt))}</td>"
            else:
                cells += f"<td class='num'>{html.escape(str(txt))}</td>"
        body += f"<tr>{cells}</tr>"
    n = f'<p class="table-note">{note}</p>' if note else ""
    return (f'<div class="table-wrap" data-table-id="{tid}">'
            f'<table class="data"><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table>{n}</div>")


def claim(cid, *, show_caveats=True):
    """Render a frozen claim in its canonical wording, with its caveats.

    The wording is copied from the freeze, never restated, so the report cannot
    drift from what was actually established.

    The identifier and the evidence tier stay in the markup -- the release gate
    and the parity audit both key on data-claim-id, and the tier is kept as a
    title attribute for anyone who wants it. Neither is printed. They are the
    project's bookkeeping, and a reader following the argument does not need a
    catalogue number stamped on every paragraph.
    """
    c = claims.loc[cid]
    cav = ""
    if show_caveats and str(c.caveats) not in ("nan", ""):
        items = "; ".join(html.escape(x.strip())
                          for x in str(c.caveats).split("||"))
        cav = f'<p class="caveats"><strong>Limits.</strong> {items}.</p>'
    return (f'<div class="claim" data-claim-id="{cid}" '
            f'title="{html.escape(str(c.tier))}">'
            f"<p class=\"canonical\">"
            f"{html.escape(reader_text(c.canonical_wording))}</p>{cav}</div>")


def context(cid, prose):
    """One context-register entry, with NEW prose written for this document."""
    e = ctx.loc[cid]
    cite = ""
    if str(e.source_status) != "not applicable":
        url = (f' <a href="{e.source_url}">source</a>'
               if isinstance(e.source_url, str) and e.source_url else "")
        det = f" {e.source_detail}" if isinstance(e.source_detail, str) and e.source_detail else ""
        cite = f'<p class="cite"><strong>Source.</strong> {html.escape(str(e.source))}{det}{url}</p>'
    return (f'<div class="ctx" data-context-id="{cid}">'
            f'<div class="ctx-head">'
            f'<span class="status">{html.escape(str(e.status))}</span></div>'
            f"<h4>{html.escape(str(e.topic))}</h4>{prose}"
            f'<p class="permitted"><strong>What may be concluded.</strong> '
            f"{html.escape(str(e.permitted))}</p>"
            f'<p class="limitation"><strong>Limitation.</strong> '
            f"{html.escape(str(e.forbidden))}</p>{cite}</div>")


def methods(title, body):
    """A methods expandable. Off the main reading path by design."""
    return (f'<details class="methods"><summary>{title}</summary>'
            f'<div class="methods-body">{body}</div></details>')


# ---- evidence tables -------------------------------------------------------
OUTCOME_LABEL = {
    "supported": "Supported",
    "inconclusive_under_available_power": "Inconclusive",
    "unsupported_with_adequate_power": "Unsupported",
    "blocked_by_proximity": "Blocked",
    "blocked_by_mechanical_overlap": "Blocked",
    "contradicts_direction": "Contradicts direction",
    "capped_by_ceiling_cannot_create_support": "Capped by ceiling",
    "failed_incremental_criterion": "Failed incremental test",
}
GATE_LABEL = {
    "bootstrap": "wild cluster bootstrap", "fdr": "multiplicity correction",
    "power": "insufficient power", "incremental": "incremental criterion",
    "direction": "adverse direction", "proximity": "proximity to outcome",
}


def _p(v):
    """Format a p-value, or an em dash where no test was run.

    NaN must be caught BEFORE the comparison. float("nan") converts without
    error and every comparison against it is False, so `v >= 0.0001` sent
    missing values down the "<0.0001" branch -- printing an unrun test as the
    most significant result the table can display. Five rows in T1 and two in
    T2 have no bootstrap result, and one of them was never tested at all
    because it is blocked by proximity to the outcome.
    """
    if v is None:
        return "&mdash;"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "&mdash;"
    if not math.isfinite(v):
        return "&mdash;"
    return f"{v:.4f}" if v >= 0.0001 else "&lt;0.0001"


def table(tid, caption, headers, rows, note=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                   for r in rows)
    n = f'<p class="tnote">{note}</p>' if note else ""
    return (f'<div class="evidence-table" id="{tid}">'
            f'<p class="tcap"><span class="tid">{tid}</span> {caption}</p>'
            f'<div class="tscroll"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>{n}</div>")


def t_current():
    """Every current-level construct, its verdict and the gate that stopped it."""
    d = pd.read_csv(PROC / "e1_results.csv")
    # Construct C3 covers four distinct measures. Printing its name alone gave
    # four rows reading "Loss against own past", which looks like duplication
    # and hides which measure each verdict belongs to.
    dupes = set(d.name[d.name.duplicated(keep=False)])
    rows = []
    for r in d.sort_values(["outcome", "construct"]).itertuples():
        out = OUTCOME_LABEL.get(str(r.outcome), str(r.outcome))
        gate = ("&mdash;" if str(r.failed_gate) == "nan"
                else GATE_LABEL.get(str(r.failed_gate), str(r.failed_gate)))
        cls = "ok" if str(r.outcome) == "supported" else "no"
        label = html.escape(str(r.name))
        if str(r.name) in dupes:
            label += (f' <span class="vsub">{html.escape(ce.name(str(r.var)))}'
                      f"</span>")
        rows.append([label,
                     f"{r.coef:+.4f}", _p(r.p_fdr), _p(r.boot_p),
                     f'<span class="verdict {cls}">{out}</span>', gate])
    return table(
        "T1", "All nine current-level constructs, with the gate that stopped "
        "each one that did not clear.",
        ["Construct", "Coefficient", "FDR p", "Bootstrap p", "Verdict",
         "Stopped at"], rows,
        "Coefficients are on each construct's own scale and are not comparable "
        "across rows. Verdicts are the output of the pre-registered decision "
        "function, not a reading of the p-values.")


def t_accumulated():
    """Accumulated measures against their current-level counterparts."""
    d = pd.read_csv(PROC / "e7_results.csv")
    d = d[d.focal.str.startswith("acc_")]
    rows = []
    for r in d.sort_values("pair").itertuples():
        out = OUTCOME_LABEL.get(str(r.reportable_outcome), str(r.reportable_outcome))
        cls = "ok" if str(r.reportable_outcome) == "supported" else "no"
        ceil = "yes" if bool(r.ceiling_applied) else "&mdash;"
        rows.append([html.escape(ce.name(str(r.focal))),
                     html.escape(ce.name(str(r.controlling_for))),
                     f"{r.coef_joint:+.4f}", _p(r.boot_p),
                     f'<span class="verdict {cls}">{out}</span>', ceil])
    return table(
        "T2", "Each accumulated measure tested with its own current-level "
        "counterpart in the same model.",
        ["Accumulated measure", "Controlling for", "Coefficient",
         "Bootstrap p", "Verdict", "Ceiling applied"], rows,
        "The ceiling column marks where Stage 5 was barred from creating "
        "support that Stage 4 had not established.")


def t_model():
    """The specification comparison, stated as a table rather than asserted."""
    rows = [
        ["Reference specification", "included", "+6.93", "3 of 27",
         "Greece markedly worse than predicted"],
        ["Companion specification", "removed", "&minus;9.39", "25 of 27",
         "Greece markedly better than predicted"],
    ]
    return table(
        "T3", "The same rows, one predictor, two opposite conclusions.",
        ["Specification", "Same-instrument deprivation", "Greek residual",
         "Rank", "Reading"], rows,
        "Neither specification is definitive. The two may not be averaged, and "
        "the choice between them may not be made on residual size.")


def t_summary():
    """What survived, at a glance, in the frozen vocabulary."""
    rows = [
        ['<span class="verdict ok">Supported</span>',
         "Material resources, long-term unemployment and wage-adjusted "
         "affordability predict hardship beyond income poverty",
         "Stage 4, bootstrap 0.0005&ndash;0.0085"],
        ['<span class="verdict ok">Supported</span>',
         "Accumulated unemployment, wage non-recovery and housing "
         "deterioration add cross-country information beyond their "
         "current-level counterparts",
         "Stage 5, conditional bootstrap 0.0015&ndash;0.0060"],
        ['<span class="verdict mid">Descriptive corroboration</span>',
         "Reported hardship co-moves with concrete affordability failure "
         "within countries &mdash; all items from the same EU-SILC interview, "
         "so this is corroboration, not independent validation",
         "Stage 3, within-country r = 0.63&ndash;0.80"],
        ['<span class="verdict no">Inconclusive</span>',
         "Six of nine current-level constructs, and the accumulated "
         "wage-adjusted measure",
         "Stage 4 and Stage 5, power-limited"],
        ['<span class="verdict no">Unsupported</span>',
         "Annual food and housing inflation at 0.70 SD; annual headline "
         "inflation at its detectable conditional magnitude",
         "Stage 4, magnitude-specific"],
        ['<span class="verdict no">No supporting evidence;<br>within effect '
         'inconclusive</span>',
         "Any dynamic reading of the accumulated measures within Greece",
         "Stage 5, no within estimate significant in the adverse direction, "
         "and the within tests cannot establish or rule one out"],
        ['<span class="verdict no">Model-dependent<br>diagnostic</span>',
         "The absorption of Greece's residual by deprivation items",
         "Stage 6, reverses from rank 3 to rank 25"],
        ['<span class="verdict no">Infeasible</span>',
         "Accumulated material resources: the source series begins in 2015 "
         "and no 2008 baseline exists",
         "Stage 5, not a null result"],
        ['<span class="verdict no">Failed</span>',
         "The synthetic-control comparative design",
         "Four of six pre-registered conditions; not shown"],
    ]
    return table(
        "T4", "Everything the analysis established, and everything it did not.",
        ["Status", "What it concerns", "Where and how"], rows,
        "Inconclusive means the design could not have detected an effect of "
        "the relevant size. It is not evidence of absence.")


def t_context():
    """The context register at a glance, in its own disjoint vocabulary."""
    # No identifier column: the register numbering is this project's
    # bookkeeping and tells a reader nothing about the topic.
    rows = []
    for cid, e in ctx.iterrows():
        rows.append([html.escape(str(e.topic)),
                     f'<span class="ctx-status">{html.escape(str(e.status))}</span>',
                     "no" if str(e.may_support_a_claim).strip().lower()
                     in ("false", "no", "0") else "yes"])
    return table(
        "T5", "Material this report discusses without establishing.",
        ["Topic", "What it is", "Can it support a finding?"], rows,
        "Some of these were examined here &mdash; migration was tested on this "
        "panel, and the cross-domain and ESS comparisons are descriptive "
        "analyses done for this report. None of them can carry a finding, and "
        "their statuses come from a deliberately separate vocabulary from the "
        "evidence statuses above so the two cannot be confused.")


STAGES = [
    ("s1", "1", "The puzzle"),
    ("s2", "2", "A broader measure, and a moving line"),
    ("s3", "3", "Is the hardship real?"),
    ("s4", "4", "What current conditions explain"),
    ("s5", "5", "What accumulated history adds"),
    ("s6", "6", "How much depends on the model"),
    ("s7", "7", "What this is not"),
    ("s8", "8", "What the evidence supports"),
]


# ===========================================================================
#  FRONT MATTER
# ===========================================================================
FRONT = f"""
<header class="masthead">
  <p class="kicker">Technical report</p>
  <h1>The Greek Poverty Paradox</h1>
  <p class="standfirst">Greeks report difficulty making ends meet at a rate far
  above what their official poverty rate would predict. This report works
  through the gap in eight stages, testing nine present-day constructs and
  eight accumulated ones against a pre-registered protocol, and reports what
  survived &mdash; including the substantial part that did not.</p>
</header>

<div class="lede">
<p>On the European Union's official measure of relative income poverty, Greek
poverty is elevated but not exceptional. It ranks seventh of twenty-seven. On the European Union's
official measure of subjective financial hardship &mdash; households reporting
difficulty making ends meet &mdash; Greece ranks first, and has done so for
years. The distance between the two runs to
<strong>52.6 percentage points</strong> on average over 2015&ndash;2024.</p>

<p>That distance is the subject of this report. It could mean many things. It
could be a measurement artefact, if the official poverty line is the wrong
ruler. It could be that the broader official measure, AROPE, already covers it.
It could mean Greek households are reporting something real that income
poverty does not capture. It could mean Greeks answer surveys more
pessimistically than other Europeans. Each of these is testable, and each is
tested here.</p>

<p>The answer is layered rather than singular, and the honest version of it
includes a large residue that the analysis could not resolve. That residue is
reported as prominently as the findings.</p>
</div>

<nav class="toc" aria-label="Contents">
  <p class="toc-jump"><a href="#summary">Skip to the findings in one page</a></p>
  <h2>The eight stages</h2>
  <ol>
    <li><a href="#s1">The puzzle</a> &mdash; how far apart the two measures are,
        and whether Greece is merely at one end of a continuum.</li>
    <li><a href="#s2">A broader measure, and a moving line</a> &mdash; what
        AROPE adds, and what happened to the threshold itself.</li>
    <li><a href="#s3">Is the hardship real?</a> &mdash; whether reported
        difficulty tracks concrete affordability failure.</li>
    <li><a href="#s4">What current conditions explain</a> &mdash; nine
        present-day constructs, tested under one pre-registered rule.</li>
    <li><a href="#s5">What accumulated history adds</a> &mdash; whether the
        length of the crisis carries information beyond its present state.</li>
    <li><a href="#s6">How much depends on the model</a> &mdash; the single
        specification choice that moves Greece from third to twenty-fifth.</li>
    <li><a href="#s7">What this is not</a> &mdash; reporting style, trust,
        migration, and the limits of the evidence.</li>
    <li><a href="#s8">What the evidence supports</a> &mdash; the conclusion,
        stated no more strongly than the tests allow.</li>
  </ol>
</nav>

<p class="howto-line">Findings appear as <strong>indented statements with a
coloured rule</strong>, each followed by the limits that qualify it. Both are
fixed &mdash; written down when the analysis finished, reproduced here word
for word &mdash; and the limits matter as much as the findings themselves.</p>

{methods("How to read this document, and the evidence vocabulary", '''
<p>Those statements are fixed: they were written down
when the analysis finished, before this report was drafted, and they are
reproduced here word for word rather than paraphrased. The limits are fixed in
the same way and matter as much as the findings -- several of them exist
because an earlier draft of this report claimed more than the evidence
carried.</p>

<p>Some material is discussed here without having been established here:
institutional trust, migration, the adjustment programmes, tax incidence and the
pre-crisis wellbeing comparison. It appears in <strong>dashed boxes</strong>
that say what may and may not be concluded from it. Parts of it were examined
-- migration was tested on this panel, and the cross-domain and ESS
comparisons are descriptive analyses done for this report -- but none of it
can carry a headline finding, and the boxes exist so that it is never mistaken
for one.</p>

<p>Technical material elsewhere in the report sits behind expandable
<em>methods</em> panels like this one. The main reading path does not depend
on opening them; they are there so that every number can be traced to how it
was produced.</p>

<div class="vocab">
<h3>The evidence vocabulary</h3>
<p>Results are not reported as significant or not significant. A
pre-registered decision rule, implemented as tested code rather than as prose,
assigns each construct one of the following:</p>
<dl>
  <dt>Supported</dt><dd>Cleared every pre-registered gate, including the
    wild cluster bootstrap.</dd>
  <dt>Inconclusive under available power</dt><dd>Did not clear the gates, and
    the design could not have detected an effect of the relevant size. This is
    <strong>not</strong> evidence of absence.</dd>
  <dt>Unsupported with adequate power</dt><dd>Did not clear the gates, and the
    design could have detected an effect of the stated magnitude. The exclusion
    is specific to that magnitude.</dd>
  <dt>Blocked</dt><dd>Not testable without circularity, because the candidate
    shares an instrument with the outcome or overlaps it mechanically.</dd>
  <dt>Infeasible</dt><dd>The data required does not exist. Distinct from a null
    result.</dd>
</dl>
<p>The distinction between the second and third of these does most of the work
in this report, and collapsing them would misrepresent the findings
substantially.</p>
</div>
''')}
"""

SUMMARY = """
<section class="summary" id="summary">
<h2>The findings, in one page</h2>
<p class="sum-lede">Everything below is set out in full over the eight stages
that follow, with the evidence and the limits of each. A reader who stops here
should still come away with an accurate picture.</p>

<div class="sum-gap">
  <p class="sum-num">52.6</p>
  <p class="sum-cap">percentage points between Greece's official
  income-poverty rate and the share of Greek households reporting difficulty
  making ends meet, averaged over 2015&ndash;2024. Greece ranks first of
  twenty-seven on the second measure and seventh on the first, and sits further
  from its nearest neighbour than that neighbour sits from most of Europe.</p>
</div>

<div class="sum-cols">
<div class="sum-col">
<h3>What accounts for part of it</h3>
<ol>
  <li><strong>The official measures are narrower than the experience.</strong>
  The EU's broader measure closes about a fifth of the distance, and its
  contribution is shrinking. The income line itself fell with the Greek
  economy, which a relative measure cannot avoid doing.</li>

  <li><strong>The reported difficulty corresponds to concrete failure.</strong>
  It moves with arrears, unaffordable heating and unexpected expenses, within
  countries as well as across them &mdash; though every one of those items comes
  from the same survey as the question itself.</li>

  <li><strong>Present conditions and accumulated history both carry
  information.</strong> Material resources, long-term unemployment and
  wage-adjusted affordability each predict hardship beyond income poverty; so
  do accumulated unemployment, the years wages have stayed below 2008, and
  housing-cost deterioration, even after their present-day counterparts are
  accounted for.</li>
</ol>
</div>

<div class="sum-col">
<h3>What the evidence does not support</h3>
<ol>
  <li><strong>Nothing here shows what causes what.</strong> Every result is a
  cross-country association across twenty-seven countries.</li>

  <li><strong>Nothing here shows Greece changing over time.</strong> The
  accumulated measures separate countries; the within-country tests are too
  imprecise either to establish a trend or to rule one out.</li>

  <li><strong>Most measures that did not work are unresolved, not
  excluded.</strong> Six of nine present-day measures are inconclusive because
  the study could not have detected an effect of the relevant size.</li>

  <li><strong>One central result reverses.</strong> Admitting a single
  same-survey predictor moves Greece from the third to the twenty-fifth largest
  unexplained gap in Europe, on identical data. Neither version is definitive.</li>
</ol>
</div>
</div>

<p class="sum-rest"><strong>And most of the gap is unexplained.</strong> Of the
52.6 points, what is accounted for above is a minority. The remainder is not
attributed to anything here, because the analysis could not establish where it
goes. A reporting tendency among Greek respondents cannot be excluded either,
and a separate survey reaching back before 2008 suggests Greece started
lower.</p>
</section>
"""


# ===========================================================================
#  STAGE 1 -- The puzzle
# ===========================================================================
S1 = f"""
<section id="s1" class="stage">
<div class="stage-head"><span class="stage-n">Stage 1</span>
<h2>The puzzle</h2></div>
<p class="stage-q">Are the two measures really describing different things, and
is Greece unusual or merely extreme?</p>

<p>The European Union measures poverty in two quite different ways, and both
are official. The first, <em>at-risk-of-poverty</em> (AROP), counts households
below 60% of their own country's median equivalised income. The second asks
households directly whether they have difficulty making ends meet. The first is
a position in a national income distribution; the second is a report about
lived experience. There is no reason they must agree, and across most of Europe
they broadly do.</p>

<p>In Greece they do not.</p>

{fig('F1')}

<p>The two series never converge over the observed period. Reported hardship
begins near 80% and remains above 60% throughout; income poverty moves within a
narrow band around 20%. The distance narrows somewhat after 2016, which matters
and is returned to in Stage 3, but it never closes to anything that could be
called agreement. This is the finding the rest of the report is about.</p>

{claim('V2-1.2')}

<p>It is worth pausing on what a gap of this size means. Roughly one Greek
household in five is counted as at risk of poverty. Roughly two in three report
difficulty making ends meet. These are not two estimates of the same quantity
that happen to differ; they are far enough apart that no plausible measurement
error reconciles them. Either the official rate is missing most of what Greek
households are experiencing, or Greek households are reporting something other
than material difficulty. Both possibilities are taken seriously here, and the
second is tested directly in Stages 3 and 7.</p>

<p>A word on the series itself. Eurostat's subjective-hardship indicator in its
current form does not reach back before 2010, which would truncate the crisis
at exactly the wrong moment. The earlier years shown here come from a
constructed series, validated against the official one where the two overlap.
That construction is ours, not Eurostat's, and it is flagged wherever it
appears.</p>

{claim('V2-1.1')}

{methods("How the pre-2010 series was constructed and checked", '''
<p>From 2010 onward the outcome is Eurostat's official indicator
<em>ilc_sbjp01</em>, used directly and not recomputed. It reports the share of
households declaring difficulty or great difficulty making ends meet. Before
2010 Eurostat does not publish it, so the earlier years are derived from the
official components in <em>ilc_mdes09</em>, aggregated by the same rule that
Eurostat's own series follows.</p>

<p>That aggregation rule was validated on <strong>432 overlapping
country-years</strong> &mdash; every country and year where both exist. Of
those, 318 agree exactly and 114 differ by a single rounding step; none differs
by more than 0.1 percentage points, and the cross-country rank correlation is
1.00 in every year.</p>

<p>Two things this does <em>not</em> establish, and neither is claimed. It does
not mean Eurostat published <em>ilc_sbjp01</em> before 2010; it did not. And it
validates the <strong>aggregation rule only</strong> &mdash; whether the earlier
national survey vintages are comparable across breaks is a separate question
that this overlap cannot answer.</p>

<p>Two disciplines were imposed. First, the constructed values are used only
for the descriptive picture in Stages 1 and 2; <strong>every inferential test
in Stages 4 through 6 runs on the official series alone</strong>, so no
statistical result depends on our construction. Second, the validation was run
before the extension was used anywhere, not afterwards, and its result was
recorded whether or not it was favourable.</p>

<p>The reason for extending at all is that a series beginning in 2010 begins
after the Greek crisis was already underway. It cannot show a pre-crisis
baseline, and a reader looking at it would see a plateau rather than a rise.
The limits of this are real, and Stage 7 returns to a case where no comparable
extension was possible.</p>
''')}

<h3>Is Greece unusual, or just last?</h3>

<p>Ranking first is not by itself remarkable &mdash; some country must rank
first. The question is whether Greece sits at the end of a smooth distribution,
in which case it is the extreme case of an ordinary European pattern, or
whether it is detached from that distribution. The second view of the figure
above answers it: fit the European relationship between income poverty and
reported hardship through the other twenty-six countries, and Greece sits 47
percentage points above what that relationship predicts at its own
income-poverty rate. The gap between Greece and the second-placed country is
larger than the range spanning the middle of the distribution. Whatever
produces this is not a stronger dose of what produces variation elsewhere. The
full ranking is in the statistical appendix.</p>

<p class="signpost"><strong>Where this leaves us.</strong> Two official
measures of the same underlying concept disagree by a wide margin for one
country, and that country is separated from the rest of the distribution rather
than continuous with it. The first thing to check is whether the European
Union's own broader measure &mdash; which was designed precisely because income
poverty alone was recognised as too narrow &mdash; already accounts for it.</p>
</section>
"""


# ===========================================================================
#  STAGE 2 -- AROPE and the moving line
# ===========================================================================
S2 = f"""
<section id="s2" class="stage">
<div class="stage-head"><span class="stage-n">Stage 2</span>
<h2>A broader measure, and a moving line</h2></div>
<p class="stage-q">Does the EU's broader poverty measure close the gap, and did
the yardstick itself move?</p>

<p>The European Union already accepts that income poverty alone is too narrow.
Its headline social indicator is AROPE &mdash; at risk of poverty or social
exclusion &mdash; which counts a household as affected if it falls below the
income line <em>or</em> is severely materially deprived <em>or</em> lives in a
household with very low work intensity. It is a deliberately broader net. If
the puzzle in Stage 1 is simply that AROP is too narrow, AROPE should largely
dissolve it.</p>

{fig('F4')}

<p>The three measures are shown as they are reported, in shares of households,
so the distance between them can be read directly. AROPE sits where its design
implies: above income poverty, because it counts more kinds of disadvantage, and
far below what households themselves report. In 2024 income poverty stands at
19.6% of households, AROPE at 26.9%, and reported difficulty at 66.7%.</p>

<p>So it helps, and it is not enough. Adding deprivation and low work intensity
to income poverty moves Greece about seven points closer to what its households
report, out of a distance of forty-seven. More telling is the direction of
travel: that contribution is <em>shrinking</em>, from eleven points at the start
of the period to seven by the end. As a solution to this puzzle the broader
measure is getting weaker rather than stronger, which is what the second view
plots.</p>

{claim('V2-2.1')}

<p>An aggregate can conceal as much as it reveals, and AROPE is built from
three quite different conditions. Before concluding that the broader measure
merely falls short, it is worth asking which of its parts moved, how each looks
against the rest of Europe, and for whom.</p>

<p>The first three views take one measure each &mdash; income poverty, severe
material deprivation, then AROPE itself &mdash; and show Greece against every
other member state rather than against a single median. The last two split the
Greek population by age and by sex.</p>

{fig('F5')}

<p>The components do not move together, and the age groups do not move
together either. This matters for interpretation: a single headline rate that
combines a falling component with a rising one can look stable while the
population underneath it is being reshaped. It does not close the gap, but it
does explain why the aggregate looks quieter than the experience.</p>

{methods("What AROPE counts, and a coverage trap in the age breakdown", '''
<h4>The three components</h4>
<p>A household is counted in AROPE if any one of three conditions holds.
<strong>At risk of poverty</strong> means equivalised disposable income below
60% of the national median. <strong>Severe material and social
deprivation</strong> means lacking at least seven of thirteen specified items,
covering arrears, capacity to meet unexpected expenses, heating, diet,
consumer durables and minimal social participation. <strong>Very low work
intensity</strong> means working-age adults in the household used 20% or less
of their combined work potential over the reference year.</p>
<p>Because the three are combined with OR rather than added, the headline rate
is not the sum of its parts and cannot be decomposed into them without
double-counting the overlap. The figure in this stage therefore shows the
components separately rather than as a stacked total, and its first view is
labelled for the two components it actually displays rather than implying all
three.</p>

<h4>A coverage trap</h4>
<p>The age-breakdown source does not carry a total row for every indicator. An
earlier version of this figure intersected years across indicators and produced
an empty default view &mdash; a chart that rendered, passed every structural
check, and displayed nothing. The failure was invisible because the checks
verified that the figure was well-formed, not that it contained data.</p>
<p>Every view of every figure is now required to carry at least two positions
on its axis and at least one finite value. A chart can be perfectly well formed
and still show nothing, and that is the kind of defect a reader notices at once
while an automated check misses it entirely unless told to look.</p>

<h4>Low work intensity and the age dimension</h4>
<p>Very low work intensity is defined only over working-age adults, so it
behaves differently across age groups by construction: households composed
entirely of people above working age are excluded from its denominator. Any
comparison of AROPE across age groups is partly a comparison of which
components can apply, and the figure separates the age groups rather than
presenting a single aggregate that would hide this.</p>
''')}

<p>One further question sits behind the aggregate: when AROPE last rose, did
that come from rates worsening inside age groups, or from the groups themselves
changing size? The two can be told apart exactly rather than estimated, and the
decomposition &mdash; charted in the statistical appendix &mdash; is
unambiguous. It came from rates within groups; composition contributed almost
nothing. A rise driven by an ageing population would be a different phenomenon
from a rise driven by conditions deteriorating for people already counted.</p>

<p class="signpost"><strong>Two different checks, not one.</strong> AROPE
broadens the <em>concept</em> of poverty: it counts more kinds of disadvantage.
Anchored poverty changes the <em>yardstick</em>: it holds the income line fixed
in real terms instead of letting it move with the national median. The first
asks whether we are measuring enough things; the second asks whether the ruler
itself moved. They are separate problems, and Greece has both.</p>

<h3>What happened to the line</h3>

<p>Relative income poverty counts people below 60% of the <em>current</em>
national median. This is a deliberate design choice and a defensible one: it
measures relative position, which is what it claims to measure. But it has a
consequence that becomes severe in a large enough downturn. When national
income collapses, the threshold falls with it. A household whose real income
dropped sharply can remain above a line that dropped just as sharply, and will
be recorded as not at risk of poverty throughout.</p>

<p>Greek median income fell by roughly a third over the crisis. The poverty
line, being a fixed fraction of it, fell with it.</p>

{fig('F3')}

<p>The two lines are the same threshold. One is the figure as published, in the
euros of its own year; the other is that figure expressed in what it could buy
in 2008. In cash the line has recovered almost entirely, from a 2010 peak of
&euro;7,178 to &euro;7,020 in 2025, a fall of 2.2%. In purchasing power it has
not: from &euro;6,808 to &euro;5,358, a fall of 21.3%.</p>

<p>A household is counted as poor or not poor against the first line. It lives
against the second.</p>

<p>The second view asks the same question in people rather than euros: how many
fall below a line held fixed at its 2008 real value, against how many fall below
the line as it actually moved. This is not a criticism of AROP, which is doing
exactly what it was designed to do. It is a statement about what AROP cannot
register: a decline affecting the whole distribution at once leaves relative
position largely undisturbed.</p>

{methods("Anchoring, equivalisation, and why the anchor year matters", '''
<p>Anchored poverty holds the income threshold at its real value in a chosen
base year and carries it forward with consumer price inflation, rather than
recomputing it from each year's median. The base year is therefore a
consequential choice, and a badly chosen one can manufacture almost any
result.</p>

<p>We use <strong>2008</strong>, the last year before the Greek downturn, and
we fixed that choice before running the comparison. It was not selected by
looking at which anchor produced the largest divergence.</p>

<p class="caution"><strong>This series is Greece-only.</strong> It compares
Greece against its own 2008 standard of living, and it contains no other
country. It therefore supports no cross-country statement whatever: it cannot
show that Greece's threshold fell further than anyone else's, only that it fell
relative to where Greece itself started.</p>

<p>Incomes throughout are equivalised using the OECD-modified scale, which
weights the first adult at 1.0, additional adults at 0.5 and children under 14
at 0.3. This is Eurostat's own convention and is applied identically to every
country.</p>

<p>One limitation deserves emphasis. Anchored poverty and relative poverty
answer different questions, and neither is the correct one in general. The
relative measure asks whether a household has fallen behind its contemporaries;
the anchored measure asks whether it has fallen behind a fixed standard of
living. In a country where everyone became poorer together, these diverge
sharply &mdash; and that divergence is the point, not a defect. A reader who
wants a single number for Greek poverty will not find one here, and the
recommendation in Stage 8 follows directly from that.</p>

<p>A further caution: the anchored series is descriptive. It enters no
inferential test in this report, and no finding rests on it.</p>
''')}

<h3>One measure, or many?</h3>

<p>A single detached measure invites a single explanation, and the most
deflating one is that the measure is broken. So it is worth asking how much
company that measure keeps. Take indicators of Greek economic and social
conditions &mdash; wages, hours worked, prices, migration, savings,
expectations &mdash; and for each one ask a deliberately crude question: is
this country in the worst fifth of the Union? Then count, twice, on the same
set.</p>

{fig('F21')}

<p>The basket is fixed before the count is taken: every indicator with a valid
EU position in both 2008 and 2024, chosen without reference to whether it
improved or deteriorated. Sixteen qualify. On those same sixteen, Greece moved
from the EU's worst fifth on four in 2008 to eleven in 2024 &mdash; 25.0% to
68.8% &mdash; and because the set is identical at both ends and in every year
between, the rise cannot be an artefact of a growing denominator.</p>

<p>The "Which measures" view separates what changed from what was already true.
Four indicators were in the worst fifth before the crisis and remain there;
seven more entered it over the period; none left. Greece was not uniformly weak
in 2008 and is not uniformly weak now &mdash; five of the sixteen sit outside
the worst fifth at both ends. What happened is that seven further dimensions
joined the four that were already there, and that is what the view shows: where
each indicator moved. Sixteen of the twenty-five now
place Greece at or near the bottom of the Union, and they are not variations on
one theme: pay per hour, hours worked, the real value of the poverty line
itself, household saving, what households expect of the coming year, and the
number of citizens leaving the country all sit in the same place.</p>

<p>This is a description, not an explanation. We tested breadth as a predictor
of reported hardship and it does not survive: on its own it is not significant
(p = 0.12), and once the other accumulated measures are in the same model its
coefficient reverses sign. A quantity whose sign depends on what else is in the
model cannot carry an explanatory reading, so this figure summarises the
condition rather than accounting for it. What it establishes here is narrower and still useful: the
measure that put Greece at the top of Europe is not an isolated instrument
behaving strangely. It sits inside a wide field of measures that moved with
it.</p>

<p class="signpost"><strong>Where this leaves us.</strong> The broader official
measure closes about a fifth of the gap and is closing less over time. The
income line itself moved down with the economy, which the relative measure
cannot register by design. Together these account for part of the distance but
leave most of it standing. The next question is the uncomfortable one: if the
official measures do not capture what Greek households are reporting, is what
they are reporting real?</p>
</section>
"""


# ===========================================================================
#  STAGE 3 -- Is the hardship real?
# ===========================================================================
S3 = f"""
<section id="s3" class="stage">
<div class="stage-head"><span class="stage-n">Stage 3</span>
<h2>Is the hardship real?</h2></div>
<p class="stage-q">Does reported difficulty track concrete affordability
failure, or does it float free of material circumstances?</p>

<p>This is the stage where the report could have ended. If Greek households
report hardship without any corresponding material difficulty, then the puzzle
is about how Greeks answer questions, not about Greek poverty, and the
remaining stages would be measuring an artefact. So it has to be addressed
before anything else is tested &mdash; though, as this stage shows, the
available evidence narrows the question rather than closing it.</p>

<p>The check is whether reported difficulty moves with items that name concrete
events rather than feelings: falling behind on bills, being unable to meet an
unexpected expense, being unable to heat the home adequately, and severe
material deprivation.</p>

<p>These are more specific than a general assessment of making ends meet, but
they are not independent of it. Every one is <em>self-reported by the same
household in the same EU-SILC interview</em>. A household inclined to answer the
whole battery downbeat would move all of them together, so this test can show
that reported hardship is coherent with concrete circumstances &mdash; it cannot
show that it is validated from outside the instrument. That limitation runs
through this entire stage.</p>

{fig('F8')}

<p>The first view is Greece alone, year by year. Each panel draws reported
hardship and one affordability measure as distances from their own averages, so
two series measured on different scales can share an axis. Three of them move
with hardship closely: unexpected expenses at 0.92, deprivation at 0.94,
inadequate heating at 0.87.</p>

<p>Falling behind on bills is the exception, and a sharp one: 0.37. Arrears
require having credit and obligations to fall behind on, so a household that
lost access to credit years ago, or never had it, can be in serious difficulty
without ever registering. The item most often treated as the hard, factual
anchor of financial distress is the one that tracks Greek hardship least
closely.</p>

<p>Each tab also carries the European median for that same measure, so a
reader can see whether the concrete difficulty was moving the same way
elsewhere or only in Greece. And this is not a Greek peculiarity: pooled across
all twenty-seven member states, once each country's own average is removed, the
same relationships hold at 0.63 to 0.80. The binned version of that pooled
comparison, and every observation behind it, are in the statistical
appendix.</p>

{claim('V2-3.1')}

<p>The limits on that finding carry real weight. A household in a difficult
position may answer the whole battery downbeat, and that alone would generate
correlations of this size without any item independently confirming another.
Nor is the pattern uniform: the within-Greece correlation for arrears is much
weaker than the range headline suggests.</p>

<p>The arrears figure deserves particular attention because it is the item
most often treated as the hard, objective anchor of financial distress. Within
Greece it correlates with reported difficulty at 0.371 &mdash; well below the
0.63 floor of the headline range. Arrears depend on having credit and
obligations to fall behind on, so a household that has already lost access to
credit, or that never had it, can be in severe difficulty without registering
arrears at all. A summary that reported only the range would imply a uniformity
that the underlying items do not have.</p>

<p>A stronger version of the same check asks how much of Greece's anomaly these
items can statistically absorb. Three numbers answer it.</p>

{artifact_table('T-ABSORB', 'e_f20_absorption.csv',
                ['row', 'percent_of_households'],
                ['Specification', 'Percent of households'],
                "Greece, on the country-years where all four items and the "
                "outcome are observed. Both predictions are out-of-sample: "
                "the model is fitted without Greece.")}

{claim('V2-3.2')}

<p>The word <em>absorb</em> is doing precise work and is not a synonym for
<em>explain</em>. Once concrete deprivation items are in the model, most of
Greece's unexplained excess is no longer statistically distinguishable. That is
a statement about shared variance, not about mechanism &mdash; and for the
reason given above, part of that shared variance is the interview rather than
the world. Stage 6 shows how much rests on admitting such a predictor at
all.</p>

{methods("Within-country versus pooled correlation, and why the distinction matters", '''
<p>A pooled correlation computed across all country-years conflates two very
different sources of variation: differences <em>between</em> countries, which
are large and persistent, and movements <em>within</em> a country over time,
which are what a claim about Greek households actually requires.</p>

<p>Between-country correlation is easy to generate and weak evidence. Richer
countries have lower deprivation and lower reported hardship on essentially
every measure, so almost any pair of welfare indicators will correlate strongly
across countries without either telling us anything about mechanism.</p>

<p>The within-country figures reported here are computed by demeaning each
series by its own country mean before correlating, so only deviations from each
country's own average contribute. A country that is persistently high on both
measures contributes nothing to a within correlation. This is why the
within-country figures are reported in the claim and the pooled ones are
not.</p>

<p>The heatmap in this stage displays both, side by side, precisely so the
difference is visible rather than asserted. Several relationships that look
strong pooled are considerably weaker within, and one changes sign. Any reader
inclined to take the pooled panel as the finding should look at the within
panel first.</p>

<p><strong>On the absorption figure.</strong> The 71% reduction is the change
in Greece's country residual when the four deprivation items are added to the
baseline specification, on identical rows. It is not an R-squared, not a
variance decomposition, and not a mediation estimate. Mediation analysis would
require an identification strategy this design does not have, and none is
claimed.</p>
''')}

{methods("How the convergence share is computed, and why it is dimensionless", '''
<p>The measures compared here are on incompatible scales: some are percentages
of population, one is a purchasing-power figure in the thousands. An earlier
version of this figure plotted a change of &minus;2,819 purchasing-power
standards on the same axis as a change of +48.8 percentage points, which is not
a comparison at all &mdash; the visual impression was driven entirely by the
choice of units.</p>
<p>The figure now shows, for each measure, the <strong>share of its own 2015
Greece&ndash;EU gap that had closed by 2024</strong>. Each measure is divided by
its own starting gap, so the quantity is dimensionless and the measures are
genuinely comparable: 1.0 means the gap closed entirely, 0 means it did not
move, and a negative value means it widened.</p>
<p>Two limits follow from the construction. A measure whose 2015 gap was
already small will show a large proportional movement for a small absolute one,
so the share should be read alongside the underlying values, which the fallback
table carries. And the share says nothing about which side moved: a gap can
close because Greece improved, because the EU average deteriorated, or both.
Decomposing that would require attributing movement to each side, which this
figure does not do and which the caption states explicitly.</p>
''')}

<h3>Convergence, and what it does and does not mean</h3>

<p>Stage 1 noted that the gap narrows after 2016 without closing. Greece did
not move in one direction across every measure behind it: some crisis-era
conditions improved substantially, while household resources and
affordability either recovered more slowly than the rest of Europe or
deteriorated further. That matters because a falling unemployment rate alone
cannot describe what households actually faced.</p>

{fig_with_extra_fallback('F7',
    '<p class="table-note">Ten of the fourteen measures above, restated with '
    "the EU-country median spelled out in each measure's own unit and a "
    'plain-language reading.</p>'
    + artifact_table('T-RECOVERY', 'e_f7_recovery_table.csv',
        ['measure', 'greece_range', 'eu_median_range', 'distance_range',
         'plain_reading'],
        ['Measure', 'Greece, 2015 → 2024',
         'EU-country median, 2015 → 2024',
         "Greece's distance from median", 'Plain reading'],
        "Distances retain each measure's original unit and are "
        "comparable over time within a row, not across rows.",
        text_cols=['plain_reading']))}

<p>The clearest improvement is long-term unemployment: Greece's rate fell from
16.4% to 5.4%, cutting its distance from the EU-country median from 12.8 to
3.7 percentage points. Housing-cost overburden also fell substantially. Both
are genuine improvements, even though Greece did not fully close either
gap.</p>

<p>The household-resource picture runs the other way. Real wages fell further
below their 2008 level while the EU median rose over the same years. Material
resources grew in Greece, but more slowly than the median, widening the PPS
gap. Wage-adjusted affordability deteriorated sharply. Reported hardship
itself fell, but the EU median fell by almost exactly as much, leaving
Greece's distance from it essentially unchanged.</p>

<p>The pattern is not that Greece failed to recover on every measure.
Labour-market and housing conditions improved substantially, but those gains
were not matched by comparable recovery in wages, resources and purchasing
power. This uneven recovery motivates the next stage's tests of which
conditions remain associated with the hardship gap.</p>

<p class="caution"><strong>Limits.</strong> This comparison is descriptive and
does not identify a mechanism. A narrowing distance can reflect movement in
Greece, movement in the EU-country median, or both; the endpoints show those
movements but do not establish their causes. Distances retain each measure's
original unit and should be compared over time within a row, not across rows.
The appendix retains all fourteen measures, including real household income,
the real poverty threshold and the two derived hardship-gap measures omitted
here for space.</p>

<p>Whether these relationships hold across countries and within them is the
question the correlation structure answers directly. The full matrices &mdash;
within countries, between countries and pooled &mdash; are in the statistical
appendix. The comparison that matters for this stage is narrower: what happens
to each measure's relationship with reported hardship when the scope changes
from between countries to within them.</p>

{fig('F19')}

<p>Most relationships survive the change with their sign intact and their
strength reduced. The real poverty threshold shows the only material reversal:
it correlates weakly and positively across countries and strongly negatively
within them. Real wages technically changes sign too, but its between-country
correlation is +0.01, too close to zero for the reversal to mean anything. A
reversal like that is a fact about the two scopes rather than evidence about
mechanism, and it is the clearest illustration of why the within figures are
the ones reported in the claim above.</p>

<p class="signpost"><strong>Where this leaves us.</strong> The reported
hardship corresponds to concrete affordability failure, so the puzzle is not
simply an artefact of how Greeks answer surveys &mdash; though Stage 7 returns
to the reporting-style question with better evidence than a correlation. What
remains is to identify which conditions predict hardship beyond what income
poverty already captures. That requires moving from description to inference,
and from this point the report follows a pre-registered protocol.</p>
</section>
"""


# ===========================================================================
#  STAGE 4 -- Current conditions
# ===========================================================================
S4 = f"""
<section id="s4" class="stage">
<div class="stage-head"><span class="stage-n">Stage 4</span>
<h2>What current conditions explain</h2></div>
<p class="stage-q">Which present-day conditions predict hardship beyond income
poverty, and which merely could not be resolved?</p>

<p>Nine candidate constructs were specified before any of them was tested:
material resources, labour-market exclusion, wage-adjusted affordability,
housing costs, inflation, migration, and three others. Each was required to
clear the same conditions, in the same order, and those conditions were fixed
before any of them was tested.</p>

<p>The constructs themselves are worth naming, because two of them are
composites whose behaviour is not obvious from their labels. <strong>Material
resources</strong> is actual individual consumption per head in purchasing-power
standards &mdash; what a household in a country can actually buy, rather than
what it nominally earns. <strong>Labour-market exclusion</strong> is the
long-term unemployment rate: people out of work for a year or more, which is a
different quantity from unemployment overall and moves more slowly.
<strong>Wage-adjusted affordability</strong> relates the price level a household
faces to the wages available in its own country, so a country can score badly
either by being expensive or by paying poorly. The remaining six cover housing
costs, several inflation measures, migration and multi-domain breadth.</p>

<p>The gates matter more than the coefficients, so they are worth stating
plainly. Each construct must add explanatory power beyond income poverty and
year effects &mdash; it is not enough to correlate with hardship if AROP
already captures it. It must survive multiplicity correction within its
declared family. And it must survive a wild cluster bootstrap, which is far
more demanding than a conventional standard error when the number of clusters
is small.</p>

{fig('F9')}

<p>Three constructs cleared every gate.</p>

{claim('V2-4.C1')}
{claim('V2-4.C2')}
{claim('V2-4.C4')}

<p class="signpost"><strong>Material resources and material deprivation are
not the same thing, and the difference matters later.</strong> Material
resources is what a country actually consumes per head, adjusted for local
prices, and it comes from national accounts and the purchasing-power
programme &mdash; measured independently of any household survey. Material
deprivation is a survey item: the share of households reporting they cannot
afford a specified list of things, collected in the same EU-SILC interview as
the question about making ends meet.</p>

<p>So one is an outside measure of what money buys, and the other is the same
households answering an adjacent question. That is why material resources can
be a supported predictor here while material deprivation appears in this report
only as corroboration in Stage 3 and as the contested predictor in Stage 6.
Admitting the second into a model is the choice that moves Greece from third to
twenty-fifth; admitting the first is not controversial at all.</p>

<p>Their directions are what one would expect and are worth stating, since a
result that ran the other way would be a reason to distrust the measure rather
than to report it. Higher material resources predict <em>less</em> reported
hardship; more long-term unemployment predicts <em>more</em>; worse
wage-adjusted affordability predicts <em>more</em>. Each direction was declared before testing, and a construct whose coefficient had pointed
the other way would have been recorded as contradicting its declared direction
rather than quietly reinterpreted.</p>

<p>These are cross-country associations. Nothing in this design supports a
causal reading, and the limits attached to each say so. What they establish is
that a country's material resources, its stock of long-term unemployment and
its wage-adjusted affordability each carry information about reported hardship
that the official income-poverty rate does not.</p>

{fig('F10')}

{context('CTX-8', '''
<p>An independently published analysis on the Greece in Figures site reaches a
similar descriptive picture from Eurostat and ELSTAT releases published in
2025 and 2026, without access to this project's panel or its testing
protocol: Greece is not the EU's poorest country on actual consumption per
head, but Greek employees work among the longest hours in the Union for
comparatively low hourly reward, and everyday categories such as food and
information and communication are expensive relative to what that pay buys.
That is the same shape as material resources and wage-adjusted affordability
above, reached by a different route and a different, more recent, vintage of
data.</p>
<p>The article's central numbers reproduce against the primary releases they
draw on, with two exceptions worth flagging on their own terms rather than
folded into this project's findings: a stock of registered vehicles is
presented as evidence of new-car purchases, which it cannot support, and a
rise in resident trip-taking is generalised to "all Greeks travelled," which
the underlying survey does not say. Three of its comparisons sit close to but
not exactly on this project's own numbers &mdash; an AIC rank, an
annual-hours measure against this report's weekly-hours one, and an overall
price-level index &mdash; and each gap traces to a different year vintage or
a different aggregate, not to a disagreement about the underlying facts.</p>
''')}

<h3>The six that did not, and why that is not a null result</h3>

<p>Six of the nine did not clear the gates. It would be convenient to describe
these as ruled out. That would be wrong for most of them, and the distinction
is the most important methodological point in this report.</p>

{claim('V2-4.X')}

<p>A test that fails to detect an effect tells us something only if it could
have detected one. With twenty-seven countries and roughly a decade of
observations, the design has limited power, and for most of the six constructs
the smallest effect it could reliably detect is larger than any effect worth
caring about. Those constructs are <em>inconclusive under available power</em>:
the study is silent about them, not negative.</p>

<p>A small number are genuinely different. Where the design had adequate power
and still found nothing, the exclusion is real &mdash; but it holds at a stated
size, not in general. The inflation measures are the clearest case: annual food
and housing inflation can be excluded at the magnitude this design could detect,
which is not the same as showing that inflation does not matter to Greek
households.</p>

{claim('L-4')}

{t_current()}

<p>Two constructs illustrate why the bootstrap gate was worth imposing. Both
cleared multiplicity correction comfortably and then collapsed under the
bootstrap, with p-values of 0.40 and 0.55. Had the protocol stopped at the
conventional step, both would have been reported as findings.</p>

{methods("The decision rule, the bootstrap, multiplicity, and minimum detectable effects", '''
<h4>How a verdict is reached</h4>
<p>Each construct is passed through the same conditions in the same order, and
the first condition it fails is the one recorded against it in the table above.
The verdict is the output of that procedure rather than a reading of the
numbers, which is what makes "inconclusive" and "unsupported" separable at
all: they are different exit points, not different degrees of the same
judgement.</p>

<h4>The wild cluster bootstrap</h4>
<p>Standard errors clustered on twenty-seven countries are unreliable:
cluster-robust inference is asymptotic in the <em>number of clusters</em>, and
twenty-seven is not large. The wild cluster bootstrap addresses this by
resampling cluster-level weights rather than observations.</p>
<p>The implementation imposes the null &mdash; the restricted, rather than
unrestricted, variant. This is not a detail. An earlier version resampled from
the unrestricted residuals and produced a p-value of 0.82 for a coefficient
with a t-statistic of 9.69, which is not a marginal disagreement but a symptom
of a misspecified bootstrap. Under the null-imposed version the same
coefficient behaves as its t-statistic implies. Every bootstrap p-value in this
report uses 1,999 replications with the null imposed.</p>

<h4>Multiplicity</h4>
<p>Testing nine constructs invites false positives. Benjamini-Hochberg
false-discovery-rate control is applied <strong>within each declared family</strong>,
where the families were declared before testing. Applying FDR across all tests
regardless of family would be more conservative but would also be incoherent,
since the families ask different questions. The families were fixed before
testing; reassigning them afterwards would invalidate the correction.</p>

<h4>Minimum detectable effects</h4>
<p>For every construct that did not clear the gates, the minimum detectable
effect was computed <em>by simulation</em> rather than by formula: the observed
panel structure is retained, an effect of known size is injected, and the
proportion of simulated datasets in which the protocol recovers it is recorded.
The MDE is the smallest injected effect recovered at least 80% of the time.</p>
<p>This is what licenses the distinction between inconclusive and unsupported.
A construct is only ever described as unsupported when its MDE is smaller than
an effect size that would matter substantively, and the report states the
magnitude at which the exclusion holds. For Stage 5 the MDEs are computed
pair-specifically and conditionally, because the relevant question there is
whether an accumulated measure adds anything <em>given</em> its current-level
counterpart, which is a different and harder test.</p>

<h4>Leaving one country out</h4>
<p>Twenty-seven countries is few enough that a single one can carry a result.
Every construct is therefore refitted twenty-seven times, each time with one
country removed, and the range of coefficients across those refits is recorded
alongside the headline estimate.</p>
<p>The three supported constructs are stable under this: long-term unemployment
ranges from 3.20 to 4.83 against a headline of 4.34, wage-adjusted affordability
from 0.25 to 0.33 against 0.31, and material resources holds its sign and
magnitude throughout. None of them depends on any single country, and in
particular none depends on Greece &mdash; which matters, because Greece is the
case the report is about and a result driven by it would be circular.</p>
<p>Housing pressure behaves differently. Its refits run from &minus;0.10 to
1.27, so dropping one country flips the sign. That instability is one of the
reasons it does not clear the gates, and it is a more informative fact about
that construct than its p-value.</p>

<h4>What the specification controls</h4>
<p>All models include the country's AROP rate and year fixed effects. Year
effects absorb Europe-wide shocks &mdash; the financial crisis, the pandemic,
the 2022 energy shock &mdash; that would otherwise be attributed to whichever
construct happens to move at the same time. Controlling for AROP is what makes
this a test of incremental information: a construct that merely proxies income
poverty cannot clear the first gate.</p>
''')}

<p class="signpost"><strong>Where this leaves us.</strong> Three present-day
conditions carry information beyond income poverty; six are mostly unresolved
rather than excluded. But every one of these measures describes Greece
<em>now</em>. A country that has been in difficulty for a decade may differ
from one with identical current conditions and no such history. That is the
next question, and it is the one where overstatement is easiest.</p>
</section>
"""


# ===========================================================================
#  STAGE 5 -- Accumulated history
# ===========================================================================
S5 = f"""
<section id="s5" class="stage">
<div class="stage-head"><span class="stage-n">Stage 5</span>
<h2>What accumulated history adds</h2></div>
<p class="stage-q">Does the length of a country's difficulty carry information
beyond its present state?</p>

<p>Two countries can look identical today and have arrived there by different
routes. One has had 8% long-term unemployment for a year; the other has had it
for twelve. The intuition that these are not the same situation is strong, and
it is the intuition behind every account of the Greek crisis that emphasises
its duration rather than its depth at any single moment.</p>

<p>Intuition is not evidence, and this stage is where an appealing story is
easiest to overstate. What follows is stated narrowly on purpose. Three
readings of the results were caught and corrected during review, each of them a
version of the same error: treating a cross-country association as though it
described a process unfolding within Greece over time.</p>

<h3>Building the accumulated measures</h3>

<p>For each construct supported in Stage 4, a matching accumulated measure was
built: the total excess exposure a country has absorbed since a fixed baseline,
rather than its level today. Excess unemployment accumulates the amount by
which a country's rate exceeded its own pre-crisis norm, summed over years.
Wage non-recovery counts the consecutive years real wages have remained below
their 2008 level. Housing deterioration accumulates the worsening in housing
cost burden since 2010.</p>

{fig('F11')}

<p>Greece has absorbed a large accumulated exposure on these measures. On one
of the three it is not the highest &mdash; Hungary has a longer run of wage
non-recovery &mdash; and the figure shows the full ranking rather than Greece
alone, so that this is visible rather than buried.</p>

<h3>The test that matters</h3>

<p>Showing that Greece accumulated a lot is description, not inference. The
question is whether an accumulated measure predicts hardship <em>once its own
current-level counterpart is already in the model</em>. If today's
unemployment rate is controlled for, does the history of unemployment still add
anything? That is a demanding test, because the two are strongly correlated by
construction.</p>

{fig('F12')}

<p>Three accumulated measures cleared it.</p>

{claim('V2-5.C2')}
{claim('V2-5.C3')}
{claim('V2-5.C6')}

<p>The third is borderline, and is labelled as such: 91 of 1,999 bootstrap
replications exceeded the observed statistic. It
is reported at the strength the test gives it and no more. The second is
supported only under one specific construction &mdash; the current uninterrupted
run measured against a fixed 2008 base. Alternative constructions of the same
idea point the same way but do not meet the pre-registered criteria, and they
are not counted as corroboration.</p>

{t_accumulated()}

<p>The pattern is not uniform across constructs, which is itself informative.</p>

{claim('V2-5.X')}

<p>For wage-adjusted affordability the relationship runs the other way: the
present-day measure survives conditioning while the accumulated one does not
resolve. If accumulation were a general property of this outcome, this reversal
should not appear. It suggests the accumulated measures are picking up
something specific to labour markets, wages and housing rather than a
universal history effect.</p>

<h3>The limit that must not be crossed</h3>

<p>Everything above is a statement about differences <em>between countries</em>.
It is tempting, and wrong, to convert it into a statement about change
<em>within</em> Greece over time.</p>

{fig('F13')}

{claim('V2-5.Y')}

<p class="caution"><strong>This is the report's most easily overstated
result.</strong> No within-country estimate reaches significance in the adverse
direction, and no first-difference test supports a dynamic reading. But
imprecise estimates are not proof of absence: the within-country tests have
considerably less power than the between-country ones, because they discard all
the cross-sectional variation. The correct statement is that this design does
not support dynamic wording &mdash; not that the dynamic effect has been shown
to be absent. Three separate drafts of this report crossed that line before it
was caught.</p>

<p>One construct could not be tested at all, and is reported rather than
quietly dropped.</p>

{claim('V2-5.Z')}

<p>Moving the baseline to 2015 would have made it testable and would also have
made it a different measure, one that could not register the crisis it was
built to capture. The baseline was left where it was.</p>

<p>One further result is reported here without being counted. The accumulated
wage-shortfall measure passed every conditional test it faced &mdash; but the
present-day measure it was paired with had not been supported in the previous
stage, and a rule fixed in advance prevents this stage from promoting anything
its predecessor did not establish. Reported, and not a finding.</p>

{claim('L-3')}

<p>The rule costs something here: on the face of the numbers this measure looks
as convincing as the three that are counted. The reason for keeping the rule
anyway is that conditional tests run after seeing which measures succeeded are
selected tests, and a rule that can be set aside when its result is inconvenient
is not a rule.</p>

{methods("Accumulation, conditioning, the Mundlak decomposition, and the E7 ceiling", '''
<h4>How accumulation is computed</h4>
<p>Each accumulated series is a cumulative sum of annual excess over a fixed
baseline. The property that matters is that no accumulated value at year
<em>t</em> may use information from any year after <em>t</em> &mdash; otherwise
a measure of history would quietly contain the future. This is checked by
rebuilding each series from truncated inputs: if any value changes when later
years are withheld, the construction leaks.</p>
<p>One construction error was caught this way. The wage-adjusted excess measure
was written to subtract 100 from an index, but the underlying source held
absolute euro values near 32,000 rather than an EU27=100 index, so the excess
was zero in every country and year. The series was silently degenerate and every
downstream test on it was meaningless. It is now indexed explicitly, with an
assertion that fails loudly if the source scale changes again.</p>

<h4>What conditioning means here</h4>
<p>The conditional test places the accumulated measure and its current-level
counterpart in the same specification, alongside AROP and year effects, and
asks whether the accumulated coefficient survives. Because the two are
correlated by construction, this test is conservative: shared variance is
attributed to neither, so an accumulated measure can only clear it by carrying
information the current level does not.</p>
<p>Minimum detectable effects in this stage are computed pair-specifically and
conditionally &mdash; the MDE for accumulated unemployment given current
unemployment, not in isolation. An unconditional MDE would understate how
demanding this test is and would make the inconclusive results look like
stronger nulls than they are.</p>

<h4>The between/within decomposition</h4>
<p>The dynamic question is addressed with a Mundlak specification, which enters
both each country's mean of a predictor and its deviation from that mean. The
coefficient on the country mean is the between-country association; the
coefficient on the deviation is the within-country one. Reporting only the
pooled estimate would blend the two and allow a between-country result to be
read as a within-country process.</p>
<p>The within estimates in this report are imprecise. That is a property of the
data &mdash; roughly a decade of annual observations per country, with slow-moving
series &mdash; and not a finding. The figure shows both estimates with their
intervals so that the imprecision is visible.</p>

<h4>The E7 ceiling</h4>
<p>This stage may only qualify or withdraw support that Stage 4 established. It
may never create support. The reason is that these conditional tests are run
after seeing which measures succeeded, which makes them selected tests: a
measure that reaches this stage has already passed a filter, so letting the
stage promote it would turn a selected result into a finding.</p>
<p>The limit binds in exactly one case, the accumulated wage-shortfall measure,
which cleared every conditional test while its present-day counterpart had not
been supported. It is reported in Stage 5 and it is not counted.</p>
''')}

<p class="signpost"><strong>Where this leaves us.</strong> Accumulated
exposure on labour, wages and housing carries cross-country information beyond
present conditions. No dynamic claim about Greece over time is supported. The
next stage asks how much of all this survives a change in one modelling
decision &mdash; and the answer is uncomfortable.</p>
</section>
"""


# ===========================================================================
#  STAGE 6 -- Model dependence
# ===========================================================================
S6 = f"""
<section id="s6" class="stage">
<div class="stage-head"><span class="stage-n">Stage 6</span>
<h2>How much depends on the model</h2></div>
<p class="stage-q">Would a defensible alternative specification have produced a
different answer?</p>

<p>Most empirical reports include a robustness section demonstrating that the
findings hold up. This one includes a robustness section demonstrating that one
of them does not, and that fact is a result rather than an embarrassment.</p>

<p>Recall from Stage 3 that four deprivation items absorbed most of Greece's
excess residual, and that they share their instrument with the outcome. Whether
to admit such a predictor is a real methodological choice, and the data cannot
settle it.</p>

<p>The case for admitting it: severe material deprivation is a substantively
meaningful measure of hardship, it is officially published, and excluding
variables because they are measured well is not a principle anyone actually
holds. The case against: when predictor and outcome come from the same
respondents answering adjacent questions in one sitting, part of any
relationship between them reflects shared measurement rather than shared
substance, and a model that leans on it will attribute to explanation what is
really instrument.</p>

<p>Both positions are defensible. So we ran both.</p>

{fig('F14')}

{claim('V2-6.1')}

{t_model()}

<p>Greece moves from third-highest unexplained hardship in Europe to
twenty-fifth &mdash; from a marked positive anomaly to a marked negative one
&mdash; on identical rows, with one predictor added or removed. This is not a
small sensitivity. It is a reversal.</p>

<p class="caution"><strong>Neither specification is definitive, and they may
not be reconciled.</strong> The two results may not be averaged, and the choice
between them may not be made by looking at which produces a more plausible
residual. Selecting a specification on the size of its residual is exactly the
practice that makes robustness checks meaningless. What the report can say is
that conclusions about how much of Greece's anomaly is absorbed depend
materially on a modelling decision that the data cannot adjudicate, and any
reader should treat absorption results with that in mind.</p>

<p>This is why Stage 3's absorption result is framed as a diagnostic rather
than an explanation, and why the conclusion in Stage 8 does not rest on it. A
finding that reverses under a defensible alternative is not a finding to build
on.</p>

<h3>Two analyses that were planned and failed</h3>

<p>The report would look stronger without this section, which is the reason it
is here. Both of the analyses below were specified in advance, both were meant
to carry weight, and neither worked.</p>

<p>The first was a synthetic control, and it was intended as the centrepiece:
build a weighted combination of other countries that tracks pre-crisis Greece,
then read the divergence after 2008 as the crisis effect. The construction
failed. The donor weights collapsed onto two countries, so the synthetic Greece
was a blend of Hungary and Bulgaria rather than a credible counterfactual, and
the design missed four of its six pre-registered conditions.</p>

{claim('L-1')}

<p>Its divergence chart would be the most arresting image in this report. It is
not shown anywhere, and that is deliberate: a striking picture built on a
counterfactual this thin would persuade readers of something the analysis
cannot support. Being compelling is not the same as being right, and the first
is more dangerous when the second is absent.</p>

<p>The second was a measure of how many domains of disadvantage a country shows
at once. Adding it to the reference model made Greece's residual worse rather than
better, and its sign flipped once other measures were controlled. That
reversal is left uninterpreted here. An unexplained sign flip in a specification
that has already failed is exactly the kind of loose end that invites a story to
be built around it, and the story would be untestable.</p>

{claim('L-2')}

{methods("The two specifications, and how their residuals are compared", '''
<h4>The reference specification</h4>
<p>The reference specification regresses reported hardship on income poverty,
the supported present-day measures, severe material deprivation and year fixed
effects, and extracts each country's residual. It was fixed before the final
results were produced. The companion specification is identical except that the
same-instrument deprivation predictor is removed.</p>
<p>Both are run on <strong>identical rows</strong>. A common way to
manufacture an apparent robustness failure, or to conceal one, is to let the
estimation sample shift when a variable with different coverage enters or
leaves. The row set is fixed to the intersection before either model runs, and
this is asserted in code rather than checked by eye.</p>

<h4>How the residuals are extracted</h4>
<p>A country residual is the average, across that country's years, of the
difference between its observed hardship rate and the rate the model predicts.
A positive residual means a country reports more hardship than its
characteristics predict; a negative one means less. Ranks are taken across all
twenty-seven countries within each specification separately, so a rank change
reflects Greece's movement relative to the same comparison set rather than a
change in who is being compared.</p>
<p>Residuals are averaged over years rather than taken from a single year,
because a single-year residual is sensitive to which year is chosen and would
make the comparison in this stage look more or less dramatic depending on an
arbitrary decision. Year fixed effects are already in both models, so the
averaging is over deviations that have had Europe-wide shocks removed.</p>

<h4>Why residual size may not select a specification</h4>
<p>Both models produce a Greek residual, and it would be easy, and entirely
circular, to prefer whichever one better matched a prior expectation about
Greece. Choosing between them on the size of the residual is therefore ruled
out. That is why this report presents both and settles on neither.</p>

<h4>Why the failed design's chart is absent</h4>
<p>A synthetic control whose donor pool collapses onto two countries does not
describe a counterfactual Greece, so the gap between the real and synthetic
series measures the failure of the construction rather than the effect of the
crisis. Plotting it would give a precise-looking magnitude to a quantity that
has no defensible interpretation.</p>
''')}

<p class="signpost"><strong>Where this leaves us.</strong> The empirical
sequence is complete. Before drawing conclusions, one alternative explanation
needs addressing directly &mdash; that Greeks simply report everything more
negatively &mdash; along with the contextual factors this project did not test
and must not pretend it did.</p>
</section>
"""


# ===========================================================================
#  STAGE 7 -- What this is not
# ===========================================================================
S7 = f"""
<section id="s7" class="stage">
<div class="stage-head"><span class="stage-n">Stage 7</span>
<h2>What this is not</h2></div>
<p class="stage-q">Is this a reporting artefact, and what else might matter
that this project did not test?</p>

<p>The most economical explanation of everything so far is that Greeks answer
survey questions more negatively than other Europeans. If that were true, the
gap in Stage 1 would be a property of the respondents rather than of their
circumstances, and much of what follows would be measuring national
temperament.</p>

<p>Stage 3 partly addressed this: reported difficulty tracks concrete
affordability failure. But that evidence came entirely from within one survey
instrument, so it cannot settle the question by itself. A better test compares
Greek responses across <em>different domains</em>. A general negative reporting
tendency should depress everything roughly equally. A domain-specific pattern
&mdash; extreme on financial questions, less extreme elsewhere &mdash; points
toward circumstances rather than temperament.</p>

{artifact_table('T-DOMAIN', 'e_f15_domains.csv',
                ['indicator', 'unit', 'greece', 'eu_median',
                 'greece_position_worst_first', 'countries'],
                ['Indicator', 'Unit', 'Greece', 'EU median',
                 "Greece's position, worst first", 'Countries'],
                "2024. A percentage, a net balance and a 0-10 rating do not "
                "share a scale, so level and position are given rather than "
                "plotted together. The distributions themselves are charted "
                "in the statistical appendix.")}

<p>The level and the position answer the question together. On the two money
questions Greece is not merely last: it sits clear of the cluster, at 66.7%
reporting difficulty against a European median of 17.1%, and at &minus;43.2 on
expectations against a median of &minus;1.8. On life satisfaction Greece is
inside the pack, at 6.7 against a median of 7.3, and second from the worst
end.</p>

{claim('V2-7.1')}

<p>So the pattern is domain-specific and the difference is one of degree, not
of kind. That is not the profile of a country whose financial reports are
extreme while its general outlook is ordinary, and an earlier draft of this
report described it that way in error.</p>

<p>Two things must be held apart here, and conflating them is easy. Greek life
satisfaction <em>rose</em> over the observed period, from 6.2 to 6.9. Greece's
<em>rank</em> nonetheless worsened, because other countries improved faster. A
worsening rank on a rising series is not falling satisfaction, and reading it
as such would invert the finding.</p>

{context('CTX-1', '''
<p>The cross-domain comparison is descriptive corroboration for the
domain-specificity reading, not a test of it. Greece's financial indicators sit
at the extreme of the European distribution while its general-wellbeing
indicator sits close to it, and that difference in degree is what the figure
above shows.</p>
<p>It does not rule out a broader negative reporting tendency operating
alongside genuine financial difficulty. Both could be true at once, and this
design cannot separate them.</p>
''')}

<h3>A separately labelled descriptive extension</h3>

<p>The Eurostat series used everywhere else in this report begins in 2013, at
the crisis trough, so it cannot say whether Greece was already unusual before
2008. The European Social Survey can. What follows is kept deliberately apart
from everything above: a different instrument, shown on its own, never joined
to the EU-SILC series and never modelled.</p>

<p>It also carries a weaker warrant than the rest of the report, and the
difference matters. The respondent-level files are behind a login. What is used
here comes from the ESS portal's public analysis view, which displays weighted
response distributions by country; country means were reconstructed by
multiplying each displayed percentage by its score and summing. The portal
rounds those percentages, so the means are approximate at that precision. There
are no standard errors and no confidence intervals, and nothing inferential is
built on them.</p>

<p>Six observations across two decades, with a ten-year hole in the middle, do
not make a line. They make a short table, which can carry the gap as a stated
fact rather than as a break in a chart.</p>

{block('ess-table')}

<p>Three things happen in sequence, and separating them is the point. Greece was
<em>already</em> about 0.8 points below the median of these twelve countries
before the crisis, at third or fourth worst. Its level then fell to 5.64 by
2010/11. And by 2023/24 it had recovered to 6.42, close to where it
started.</p>

<p>Its comparative position did not recover with it. The gap to the median is
wider now than before the crisis, and Greece has been the worst of the twelve
since 2010/11 &mdash; the two countries that were below it before the crisis
have since passed it. Part of that is the median rising; part is being
overtaken.</p>

<p class="caution"><strong>What this does to the reporting-style
question.</strong> A low Greek baseline pre-dates the crisis, so the position
cannot be attributed to the crisis alone, and a longstanding low-wellbeing
pattern remains plausible. Generic pessimism or reporting culture cannot be
dismissed on this evidence &mdash; and cannot be established by it either. It
sharpens the caveat already attached to the claim above rather than replacing
it.</p>

{context('CTX-7', '''
<p>Across six ESS rounds, holding the same twelve countries fixed, Greece sat
roughly 0.8 points below the median before the crisis, fell to 5.64 by 2010/11,
and recovered its level to approximately its pre-crisis value by 2023/24 while
its comparative position did not recover.</p>
<p>The all-country ranks in the source data are deliberately not used for
comparison here. The full ESS country set varies from twenty-two to thirty
between rounds, so an all-country rank moves when the country set moves, and a
change in it would be partly composition rather than substance.</p>
''')}

<h3>Health: a second post-freeze extension</h3>

<p>Health is the other obvious candidate a reader will ask about, and it was
examined after the claim set was frozen. Like the survey extension above, it is
kept apart from everything in Stages 1 to 6, and for the same reason: it could
not have changed a headline claim whatever it returned.</p>

<p>The finding worth carrying forward is descriptive and it is stark. On unmet
medical care &mdash; the share who needed care and did not get it because of
cost, waiting time or distance &mdash; Greece was second-worst in the Union in
2016, 2019 and 2022, and worst of twenty-seven in 2024, at 12.1% against a
median member state of 1.9%. That is a health-system fact of the same order as
anything in Stage 1, and it belongs in any account of what hardship means in
practice for a Greek household.</p>

<p>What health does <em>not</em> do is explain the gap. Four measures were
tested against the same baseline used elsewhere &mdash; unmet care, self-rated
health, long-standing illness, and activity limitation &mdash; and none
survives. Three of the four carry the wrong sign: across countries, worse
reported health goes with <em>less</em> reported hardship, which is not a
finding but a warning. Separating the comparison shows why. All three
health-status measures reverse sign between countries and within them, so the
pooled coefficient describes neither comparison; within a country, years of
worse reported health are years of more reported hardship, the expected
direction. National composition and reporting conventions dominate the pooled
association. Unmet care is the exception that makes the point: it measures
access rather than health, it is positive in both comparisons, and it is also
the one measure whose leave-one-country-out refits change sign.</p>

<p>So health enters this report as context and as a research direction, not as
a predictor. The natural next step is not more EU-SILC: it is
age-standardised rates and independent sources &mdash; out-of-pocket and
catastrophic health spending, medicine access, avoidable mortality &mdash;
which could test whether the survey signal matches administrative evidence
instead of restating the same instrument. The full analysis, its eight
artifacts and three figures are in the statistical appendix and in
<code>docs/health_preliminary_analysis.md</code>.</p>

<h3>What this project did not test</h3>

<p>Several factors are prominent in accounts of the Greek crisis and are absent
from the analysis above. Omitting them silently would be misleading; discussing
them as though they were findings would be worse. They are recorded here in a
separate register, with an explicitly different vocabulary, and each entry
states what it permits and what it forbids.</p>

<p>The boundary is not that none of it was examined &mdash; migration was tested
diagnostically on this panel, and the cross-domain comparison and the ESS
extension are both descriptive analyses carried out here. The boundary is that
<strong>none of it may support a headline claim</strong>. These entries carry
their own status vocabulary, deliberately disjoint from the evidence statuses
used in Stages 1 to 6, so that a contextual statement can never be promoted
into a finding.</p>

{t_context()}

{context('CTX-2', '''
<p>Institutional trust is low in Greece by OECD measurement, and there is a
plausible route by which it could matter: households that do not expect
effective support may experience the same material circumstances as more
threatening, and report accordingly. The pattern within Greece is uneven, which
matters for that reading: the institutions a household would actually turn to
for support are not the ones Greeks trust most.</p>
<p>This project ran no test on trust. What the OECD's own country note for
Greece reports &mdash; charted in the statistical appendix under contextual
evidence &mdash; is more
interesting than a single comparison: Greek trust is not uniformly low. Greeks
report more trust in the police and the courts than in any elected or political
institution, and political parties sit at the bottom at 17%. Central government,
at 32% against an OECD average of 39%, sits in the middle of a wide internal
range rather than at the bottom of it.</p>
''')}

{context('CTX-3', '''
<p>The adjustment programmes of 2010 onward reshaped Greek incomes, employment
protection, pensions and public services simultaneously and over a compressed
period. They are the historical setting for every accumulated measure in Stage
5.</p>
<p>This project estimates no policy effect. The accumulated measures record
what a country absorbed; they do not attribute any of it to a specific
programme, measure or decision, and the design contains nothing that would
license such an attribution.</p>
''')}

{context('CTX-4', '''
<p>Emigration of working-age Greeks during the crisis is well documented, and
it interacts with the labour-market measures in Stage 4 in both directions: it
is plausibly a consequence of prolonged labour-market damage, and plausibly a
contributor to the composition of who remains.</p>
<p>Migration was tested on this panel as an aggregate predictor in Stage 4 and
found nothing (p=0.4006). That result speaks to aggregate prediction only. It
does not establish that migration is irrelevant, and it does not speak to
either causal direction.</p>
''')}

{fig('F16')}

{context('CTX-5', '''
<p>Published incidence research establishes that the Greek indirect tax system
became markedly more regressive across the crisis, shifting burden toward
lower-income households. If a household's disposable position worsened through
taxation in ways that income-based poverty measures capture poorly, that would
be one route to a gap of the kind this report documents.</p>
<p>This is a hypothesis for future work and nothing more. The cited literature
concerns tax incidence, not subjective hardship; this project tested nothing on
tax; and no quantitative link between tax burden and the hardship gap is
asserted or implied.</p>
''')}

{methods("How the cross-domain comparison works, and what it cannot settle", '''
<h4>The comparison</h4>
<p>Three Eurostat indicators are compared for Greece against the other EU
member states: reported financial hardship, financial expectations, and general
life satisfaction. The first two are financial; the third is not. If a country
scores at the extreme of the distribution on all three by a similar margin,
that is consistent with a general reporting tendency. If it is extreme on the
financial pair and less so on the general one, that is consistent with domain
specificity.</p>
<p>Greece is worst in Europe on the financial pair and second-worst on life
satisfaction by 2024. The difference is a difference of degree, and the report
describes it that way.</p>

<h4>Rank and level are different quantities</h4>
<p>The figure shows rank trajectories because the question is comparative,
and rank is treacherous on its own for the reason already noted above (a
score can improve while its rank still worsens). The figure carries the
underlying values alongside the ranks for that reason, and the axis is
labelled so that the worst position is unambiguous.</p>

<h4>What this cannot settle</h4>
<p>Separating genuine financial difficulty from genuine difficulty
<em>plus</em> a general negative tendency requires either a pre-crisis
baseline, which this series does not have, or an external anchor on Greek
response style, which this project does not have. The claim is worded to
leave both possibilities open.</p>

<h4>How the ESS figures were reconstructed</h4>
<p>The respondent-level ESS files require an account. The portal's public
analysis view does not, and it publishes, for each country and round, the
weighted percentage of respondents choosing each point on the 0&ndash;10 life
satisfaction scale. A country mean is recovered from that by multiplying each
percentage by its score and summing.</p>
<p>The portal rounds the percentages it displays, so the recovered means are
approximate at that precision. More importantly, a distribution published as
percentages carries no information about sampling variability: there is no way
to attach a standard error or an interval to a mean recovered this way, and no
test is run on them anywhere in this report.</p>
<p>The twelve-country balanced set exists because the full ESS country set
ranges from twenty-two to thirty across the six Greek rounds. A rank computed
against a changing set moves when the set moves, so an all-country rank
trajectory would confound Greece's position with who happened to participate.
Holding the same twelve countries fixed removes that, at the cost of comparing
Greece against a smaller and richer group than the EU average used elsewhere
&mdash; which is one more reason the two series are never placed on the same
axis.</p>

<h4>Why trust was not tested</h4>
<p>Institutional trust is measured by the OECD on a different instrument, a
different sample and a different periodicity from the Eurostat panel used
throughout this report. There is no defensible way to merge them at
country-year level for the period analysed, and constructing one would
manufacture the comparability it needs. Trust therefore appears as registered
context, and the figure reports only the two values read directly from the
primary OECD release.</p>
''')}

<p class="signpost"><strong>Where this leaves us.</strong> The gap is not
adequately explained as a reporting artefact, though a general negative
tendency cannot be excluded. Several plausible contributing factors were not
tested and are recorded as untested. What remains is to state the conclusion at
the strength the evidence actually supports.</p>
</section>
"""


# ===========================================================================
#  STAGE 8 -- Conclusion
# ===========================================================================
S8 = f"""
<section id="s8" class="stage">
<div class="stage-head"><span class="stage-n">Stage 8</span>
<h2>What the evidence supports</h2></div>
<p class="stage-q">Stated no more strongly than the tests allow.</p>

{t_summary()}

<p>Greek households report financial difficulty at a rate far above what the
official relative-poverty rate predicts, and the distance is large, persistent
and not a feature of a smooth European distribution. Three bodies of evidence
make part of it more intelligible. None of them decomposes the gap, and no
share of it is attributed to any of them.</p>

<p><strong>The official measures are narrower than the experience.</strong>
The broader AROPE measure closes about a fifth of the distance and its
contribution is shrinking. The relative income line moved down with the Greek
economy, which is what a relative measure is designed to do and which leaves it
unable to register a decline affecting everyone at once. Together these are a
real part of the answer and a minority of it.</p>

<p><strong>What households report corresponds to concrete failure.</strong>
Reported difficulty co-moves with arrears, inability to meet unexpected
expenses, inadequate heating and severe deprivation, within countries as well
as across them. This is corroboration from inside one survey instrument rather
than independent validation, and it is not uniform across items.</p>

<p><strong>Present conditions and accumulated exposure both carry
information.</strong> Material resources, long-term unemployment and
wage-adjusted affordability each predict hardship beyond income poverty.
Accumulated unemployment, the duration of wage non-recovery and housing-cost
deterioration each retain a cross-country association after their present-day
counterparts are controlled.</p>

<h3>What the evidence does not support</h3>

<p>These limits are part of the conclusion, not qualifications appended to it.</p>

<ul class="limits">
<li><strong>No causal claim is made anywhere.</strong> Every supported result is
a cross-country association in a panel of twenty-seven countries. Nothing in
this design identifies a causal effect.</li>
<li><strong>There is no supporting dynamic evidence, and the within-country
effect is inconclusive.</strong> The accumulated measures differentiate
countries; no within-country estimate supports a process unfolding within
Greece, and the within tests are too imprecise to establish or rule one out.
Those are two different statements and neither is "no effect".</li>
<li><strong>Most non-supported tested constructs are unresolved, not
excluded.</strong> Six of nine current-level constructs are inconclusive under
available power. Only a small number are excluded, and only at specific
magnitudes.</li>
<li><strong>A central absorption result reverses under a defensible alternative
model.</strong> Greece moves from third to twenty-fifth on unexplained hardship
depending on whether a same-instrument predictor is admitted. Neither
specification is definitive.</li>
<li><strong>A broader negative reporting tendency is not ruled out.</strong> The
domain pattern suggests specificity; Greece is nonetheless close to worst in
Europe on general life satisfaction. The EU-SILC series carries no pre-crisis
observation. The separate ESS extension does reach back before 2008, and shows
a Greek deficit that pre-dates the crisis &mdash; which makes a longstanding
pattern more plausible, not less.</li>
<li><strong>Most of the gap remains unexplained.</strong> Of the 52.6-point
average distance, the measurement account addresses a minority. The rest is
not attributed here.</li>
</ul>

<h3>What follows for measurement</h3>

{context('CTX-6', '''
<p>The analysis shows repeatedly that no single official indicator captures
what Greek households report. AROP misses concept and yardstick alike; AROPE
adds breadth but a shrinking share of it; anchored poverty registers what the
relative line cannot; and accumulated labour and housing exposure carries
information none of the current-level measures hold.</p>
<p>A dashboard that reports these together would represent the situation better
than any one of them alone. That is a recommendation about how poverty is
reported, and it follows from what the analysis showed the single measures
miss.</p>
''')}

<h3>What would change this conclusion</h3>

<p>Stating what would overturn a finding is more useful than asserting
confidence in it. Four things would.</p>

<p>Independent corroboration from outside EU-SILC &mdash; administrative
arrears data, utility disconnection records, or a separate survey instrument
&mdash; would settle whether Stage 3's co-movement reflects shared substance or
shared instrument, which is the question Stage 6 shows the current design
cannot resolve. A longer or wider panel would convert several inconclusive
results into genuine findings or genuine nulls; most of the six unresolved
constructs are unresolved for want of power, not because the data speak against
them. Household-level rather than country-level analysis would permit the
within-country tests that this design cannot support, and would allow the
dynamic question in Stage 5 to be asked properly. And respondent-level ESS
access would put the pre-crisis wellbeing comparison on a firmer footing than
the extension in Stage 7 can manage: that extension already indicates a Greek
deficit predating the crisis, but it rests on approximate means reconstructed
from published distributions, with no standard errors and no way to test
anything.</p>

<p>Each of these is a route to a stronger answer than this report can give. It
is worth saying plainly that this report's central finding is a well-documented
gap with a partial account of its composition, and that the honest description
of the remainder is that it is unexplained.</p>
</section>
"""


# ===========================================================================
#  BACK MATTER
# ===========================================================================
BACK = f"""
<section id="back" class="stage backmatter">
<div class="stage-head"><span class="stage-n">Back matter</span>
<h2>Protocol, data and reproduction</h2></div>

<p>This section records how the analysis was governed. It is not on the main
reading path, but every claim above depends on it being true.</p>

<h3>How the analysis was constrained</h3>

<p>Each construct in this report was specified, and the conditions it had to
meet were written as executable code, before it was tested. Those conditions
decide the outcomes reported in Stages 4 and 5; none of the verdicts is a
judgement made after seeing the numbers.</p>

<p>The conditions are code rather than prose because prose admits
interpretation exactly when interpretation is most tempting. A rule that runs
cannot be reread more favourably once an inconvenient result arrives.</p>

<p>Where a result in this report was corrected during review, the correction
and its reason are logged in the research record, which is generated from the
same registers as this document.</p>

<h3>Data</h3>

<p>All quantitative inputs are Eurostat, principally EU-SILC, at country-year
level for the EU27 over 2015&ndash;2024, with the constructed pre-2010
extension described in Stage 1 used for description only. The institutional
trust figures come from the OECD's 2024 trust survey and were read from the
primary release. Migration figures are national-level Greek data.</p>

<p>The literature cited in Stage 7 was verified against primary sources rather
than secondary summaries: each reference was checked at its publisher or
repository of record.</p>

{methods("Sources, coverage, and how missing data is handled", '''
<h4>What the panel contains</h4>
<p>The estimation panel is country-year, covering the EU27 across
2015&ndash;2024, drawn from Eurostat. The outcome and the deprivation items come
from EU-SILC; the labour-market measures from the Labour Force Survey; prices
and wages from the harmonised price and national accounts series; and
purchasing-power figures from the PPP programme. The accumulated measures in
Stage 5 reach back to 2008 or 2010 for their baselines, so their inputs extend
earlier than the estimation window even though the outcome does not.</p>

<h4>The EU comparison</h4>
<p>Where a figure shows "the EU median" it is the median across the member
states present in that year, recomputed per year rather than fixed to a base
year's membership, and Greece is included in it. An excluded-Greece median would
widen every gap shown here by construction, which would flatter the argument;
the difference is small but it runs in the direction that favours the report's
own case, so the conservative choice is the one taken.</p>

<h4>Missing values</h4>
<p>Nothing is imputed. Where a country-year lacks a value the observation is
dropped from the model that needs it, which is why the row counts differ between
specifications &mdash; and why Stage 6's two models are explicitly run on the
intersection of their rows rather than on whatever each could manage alone.
Series with structural breaks flagged by Eurostat are used as published; this
project does not attempt its own break adjustment, and cross-vintage
comparability before 2010 is a limitation noted in Stage 1 rather than a
problem solved here.</p>

<h4>Two coverage gaps that shaped the analysis</h4>
<p>The purchasing-power consumption series begins in 2015, which is why the
accumulated version of material resources could not be built at all rather than
being built badly from a later baseline. And the wellbeing module begins in
2013, which is why the pre-crisis question in Stage 7 needed an entirely
separate survey to address at all.</p>
''')}

<h3>Scope, and what this design can carry</h3>

<p>The unit of analysis is the country-year, and the panel holds twenty-seven
countries over roughly a decade. Three consequences follow and none of them are
incidental.</p>

<p>First, every result is an aggregate association. Nothing here describes an
individual Greek household, and an aggregate relationship need not hold at the
household level &mdash; the ecological inference problem is real and this design
does not escape it. A finding that accumulated unemployment predicts national
hardship rates does not establish that individuals who experienced unemployment
report more hardship.</p>

<p>Second, the number of clusters is small. Twenty-seven is enough for
descriptive comparison and marginal for inference, which is why the bootstrap
gate exists and why so many constructs land as inconclusive. A larger panel
would not merely tighten the estimates; it would convert a substantial part of
this report from silence into evidence.</p>

<p>Third, the period is short relative to the process being studied. The
accumulated measures reach back to 2008 or 2010, but the outcome series
supports roughly a decade of variation, and within-country identification draws
only on that. This is the direct cause of the imprecision in Stage 5, and it is
why the dynamic question is left open rather than answered.</p>

<h3>Provenance</h3>

<p>Every claim, decision, correction and deviation in this project is recorded
in the research record, along with which script produced each number and from
which artifact. This report states its results; the record shows how each one
was arrived at, and what was changed along the way.</p>

{methods("What is checked before this report is published", '''
<p>Every figure is checked mechanically before publication, and the checks that
matter to a reader are these.</p>
<p>The numbers in each chart and the numbers in its table are compared by a
checksum recomputed from the rendered table, so a chart cannot drift from the
figures beneath it. Every view must contain real data &mdash; at least two
positions on its axis and one finite value &mdash; because a chart that renders
correctly while displaying nothing will otherwise pass unnoticed, as one did.
No internal variable name may appear in a reader-facing label. Every figure must
carry its question, its evidence status, a keyboard-reachable chart and a table
fallback, and wide content must scroll inside its own container rather than
pushing the page sideways.</p>
<p>Results that were registered as not reportable &mdash; principally the failed
synthetic control's divergence chart &mdash; are checked for by name in every
generated document, so they cannot reappear by accident. An optional input that
is unavailable writes an explicit marker recording that it was skipped, so a
stage that did not run can never be mistaken for one that ran and found
nothing.</p>
''')}

<h3>Reproduction</h3>

<p>Every number in this report is produced from the published Eurostat, OECD
and ESS sources by code, and the whole sequence can be rerun from those sources
without manual steps. Which script produced each number, from which input, and
under which decision, is recorded in the research record.</p>
</section>
"""


# ===========================================================================
#  PAGE
# ===========================================================================
BASE = ce.base_style((OUT / "build" / "report.html").read_text())

REPORT_CSS = """
body{max-width:54rem;margin:0 auto;padding:0 1.2rem 6rem;
  font:1.02rem/1.72 ui-serif,Georgia,'Times New Roman',serif}
.masthead{padding:3.4rem 0 1.6rem;border-bottom:2px solid var(--text-primary);
  margin-bottom:2rem}
.kicker{font:600 .72rem/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.14em;
  text-transform:uppercase;color:var(--text-secondary);margin:0 0 1rem}
.masthead h1{font-size:clamp(2.1rem,6vw,3.1rem);line-height:1.08;margin:0 0 1rem;
  letter-spacing:-.02em;text-wrap:balance}
.standfirst{font-size:1.16rem;line-height:1.6;color:var(--text-secondary);
  max-width:40rem;margin:0}
.lede p:first-of-type{font-size:1.08rem}
.toc{background:var(--surface-2);border-radius:8px;padding:1.4rem 1.6rem;
  margin:2.6rem 0;font:.95rem/1.6 ui-sans-serif,system-ui,sans-serif}
.toc-jump{margin:0 0 .9rem;font:600 .95rem/1.4 ui-sans-serif,system-ui,sans-serif}
.toc h2{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;
  margin:0 0 .9rem;color:var(--text-secondary)}
.toc ol{margin:0;padding-left:1.3rem}
.toc li{margin:.45rem 0;color:var(--text-secondary)}
.toc a{font-weight:600;color:var(--text-primary)}
.howto{border:1px solid var(--border);border-radius:8px;padding:1.5rem 1.7rem;
  margin:2.4rem 0 1rem;font-size:.97rem}
.howto h2{font-size:1.1rem;margin:0 0 .8rem}
.vocab{margin-top:1.4rem;padding-top:1.2rem;border-top:1px solid var(--border)}
.vocab h3{font-size:.95rem;margin:0 0 .7rem}
.vocab dl{margin:0;font-size:.93rem}
.vocab dt{font-weight:700;margin-top:.7rem}
.vocab dd{margin:.15rem 0 0;color:var(--text-secondary)}
.summary{margin:2.6rem 0 0;padding:1.8rem 0 0;border-top:2px solid var(--text-primary)}
.summary h2{font-size:clamp(1.4rem,3.4vw,1.85rem);margin:0 0 .6rem;
  letter-spacing:-.015em}
.sum-lede{font:.95rem/1.6 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);max-width:38rem;margin:0 0 1.6rem}
.sum-gap{display:flex;gap:1.2rem;align-items:baseline;flex-wrap:wrap;
  background:var(--surface-2);border-radius:8px;padding:1.2rem 1.4rem;
  margin:0 0 1.6rem}
.sum-num{font:700 clamp(2.4rem,7vw,3.4rem)/1 ui-sans-serif,system-ui,sans-serif;
  color:var(--series-gr);margin:0;flex:none;font-variant-numeric:tabular-nums}
.sum-cap{font:.92rem/1.55 ui-sans-serif,system-ui,sans-serif;margin:0;
  flex:1 1 18rem;color:var(--text-secondary)}
.sum-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(17rem,1fr));
  gap:1.4rem 2rem}
.sum-col h3{font:600 .76rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 .8rem}
.sum-col ol{margin:0;padding-left:1.2rem;
  font:.94rem/1.6 ui-sans-serif,system-ui,sans-serif}
.sum-col li{margin:0 0 .8rem}
.sum-col li strong{color:var(--text-primary)}
.sum-rest{margin:1.5rem 0 0;padding:.9rem 1.1rem;border-left:3px solid var(--div-neg);
  background:var(--surface-2);border-radius:0 5px 5px 0;
  font:.95rem/1.6 ui-sans-serif,system-ui,sans-serif}
.stage{margin:4.5rem 0 0;scroll-margin-top:1rem}
.stage-head{display:flex;align-items:baseline;gap:.9rem;flex-wrap:wrap;
  border-top:2px solid var(--text-primary);padding-top:1rem;margin-bottom:.4rem}
.stage-n{font:700 .72rem/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.12em;
  text-transform:uppercase;color:var(--text-secondary)}
.stage-head h2{font-size:clamp(1.5rem,3.6vw,2.05rem);margin:0;letter-spacing:-.015em;
  text-wrap:balance}
.stage-q{font:italic 1.06rem/1.55 ui-serif,Georgia,serif;color:var(--text-secondary);
  margin:.2rem 0 1.6rem;max-width:38rem}
.stage h3{font-size:1.22rem;margin:2.6rem 0 .7rem;letter-spacing:-.01em}
.claim{border-left:3px solid var(--series-gr);padding:.15rem 0 .15rem 1.1rem;
  margin:1.5rem 0}
.canonical{margin:0;font-size:1.06rem;line-height:1.62}
.caveats{margin:.5rem 0 0;font:.9rem/1.6 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary)}
.caveats strong{color:var(--text-secondary);font-weight:700}
.ctx{border:1px dashed var(--border);border-radius:6px;padding:1.1rem 1.3rem;
  margin:1.8rem 0;background:transparent}
.ctx-head{display:flex;gap:.7rem;align-items:center;margin-bottom:.3rem}
.ctx .cid{font:700 .74rem ui-monospace,SFMono-Regular,Menlo,monospace}
.ctx .status{font:.7rem ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
  letter-spacing:.08em;color:var(--text-secondary)}
.ctx h4{margin:.2rem 0 .6rem;font-size:1.02rem}
.ctx p{font-size:.95rem}
.ctx .permitted,.ctx .limitation,.ctx .cite{font:.88rem/1.55 ui-sans-serif,
  system-ui,sans-serif;margin:.6rem 0 0}
.ctx .limitation{color:var(--text-secondary)}
.ctx .cite{color:var(--text-secondary);font-size:.82rem;padding-top:.5rem;
  border-top:1px solid var(--border)}
.skipped{border:1px solid var(--border);border-radius:6px;padding:1.1rem 1.3rem;
  margin:1.8rem 0;background:var(--surface-2)}
.skipped-head{display:flex;gap:.7rem;align-items:center;
  font:.72rem ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
  letter-spacing:.09em;color:var(--text-secondary)}
.skipped .tag{font-weight:700;border:1px solid var(--text-secondary);
  border-radius:3px;padding:.12em .45em;letter-spacing:.06em}
.skipped h4{margin:.6rem 0 .5rem;font-size:1.02rem}
.skipped p{font-size:.95rem}
.signpost{border-left:3px solid var(--series-3);padding:.8rem 1.1rem;
  background:var(--surface-2);border-radius:0 5px 5px 0;margin:2rem 0 0;
  font-size:.97rem}
.caution{border-left:3px solid var(--div-neg);padding:.8rem 1.1rem;
  background:var(--surface-2);border-radius:0 5px 5px 0;margin:1.6rem 0;
  font-size:.97rem}
.limits{padding-left:1.2rem}
.limits li{margin:.6rem 0}
details.methods{margin:1.8rem 0;border:1px solid var(--border);border-radius:6px;
  background:var(--surface-2)}
details.methods>summary{cursor:pointer;padding:.85rem 1.1rem;
  font:600 .92rem ui-sans-serif,system-ui,sans-serif;list-style:none;
  display:flex;align-items:center;gap:.6rem}
details.methods>summary::-webkit-details-marker{display:none}
details.methods>summary::before{content:"+";font-weight:700;
  color:var(--text-secondary);font-size:1.1em;line-height:1}
details.methods[open]>summary::before{content:"\\2212"}
details.methods>summary:hover{color:var(--series-gr)}
details.methods>summary:focus-visible{outline:2px solid var(--series-gr);
  outline-offset:-2px}
.methods-body{padding:0 1.3rem 1.1rem;font:.94rem/1.65 ui-sans-serif,system-ui,
  sans-serif;border-top:1px solid var(--border)}
.methods-body h4{font-size:.95rem;margin:1.2rem 0 .4rem}
.methods-body code{font:.88em ui-monospace,SFMono-Regular,Menlo,monospace;
  background:var(--surface-1);padding:.1em .35em;border-radius:3px}
/* The two figures replaced by generated tables (T-ABSORB, T-DOMAIN) reuse
   this file's own artifact_table() helper, which emits <div class="table-wrap">
   <table class="data">...</table></div> -- a different markup pattern from
   the T1/T2 evidence tables below, and one that was never given CSS. It
   rendered as bare unstyled browser-default rows: no borders, no header
   emphasis, numeric columns not visually separated from the label column.
   Styled here in the same visual language as .evidence-table so a reader
   cannot tell which mechanism produced which table. */
.table-wrap{margin:1.4rem 0;overflow-x:auto;border:1px solid var(--border);
  border-radius:6px}
.table-wrap table.data{border-collapse:collapse;width:100%;min-width:26rem;
  font:.87rem/1.45 ui-sans-serif,system-ui,sans-serif}
/* The row label is marked up as <th scope="row">, which is the more correct
   choice for a screen reader -- it associates the label with its row the way
   scope="col" does for a column. But a bare `th` selector cannot tell a row
   header from the column header row, and gave every row label the same
   heavy background as the header: every row looked like a second header.
   Scoped to thead specifically for the header treatment; row headers get
   their own, lighter rule. */
.table-wrap table.data thead th{text-align:left;font-weight:700;font-size:.76rem;
  letter-spacing:.05em;text-transform:uppercase;color:var(--text-secondary);
  padding:.6rem .8rem;border-bottom:1px solid var(--border);
  background:var(--surface-2);white-space:nowrap}
.table-wrap table.data td,.table-wrap table.data tbody th{
  padding:.55rem .8rem;border-bottom:1px solid var(--border);vertical-align:top}
.table-wrap table.data tbody th{text-align:left;font-weight:600;
  color:var(--text-primary)}
.table-wrap table.data td.num{font-variant-numeric:tabular-nums;text-align:right}
.table-wrap table.data tbody tr:last-child td,
.table-wrap table.data tbody tr:last-child th{border-bottom:none}
.table-wrap .table-note{font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin:.6rem .1rem 0}

.evidence-table{margin:2rem 0}
.tcap{font:600 .9rem/1.5 ui-sans-serif,system-ui,sans-serif;margin:0 0 .6rem;
  display:flex;gap:.6rem;align-items:baseline}
.tid{font:700 .74rem ui-monospace,SFMono-Regular,Menlo,monospace;
  color:var(--text-secondary);flex:none}
.tscroll{overflow-x:auto;border:1px solid var(--border);border-radius:6px}
.evidence-table table{border-collapse:collapse;width:100%;min-width:34rem;
  font:.87rem/1.45 ui-sans-serif,system-ui,sans-serif}
.evidence-table th{text-align:left;font-weight:700;font-size:.76rem;
  letter-spacing:.05em;text-transform:uppercase;color:var(--text-secondary);
  padding:.6rem .8rem;border-bottom:1px solid var(--border);
  background:var(--surface-2);white-space:nowrap}
.evidence-table td{padding:.55rem .8rem;border-bottom:1px solid var(--border);
  vertical-align:top}
.evidence-table tbody tr:last-child td{border-bottom:none}
.evidence-table td:nth-child(n+3){font-variant-numeric:tabular-nums}
.verdict{font-weight:700;white-space:nowrap}
.verdict.ok{color:var(--div-pos)}
.verdict.no{color:var(--text-secondary)}
.verdict.mid{color:var(--ink-ok)}
.ctx-status{font-size:.82rem;color:var(--text-secondary)}
.vsub{display:block;font-size:.82em;color:var(--text-secondary)}
.tnote{font:.82rem/1.5 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin:.5rem 0 0;max-width:44rem}
.backmatter{border-top:2px solid var(--text-primary);margin-top:5rem}
@media print{
  .toc,details.methods{break-inside:avoid}
  details.methods[open]>.methods-body{display:block}
  .stage{break-before:page}
}
@media (max-width:38rem){
  body{font-size:.98rem}
  .stage-head{gap:.5rem}
}
"""

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Greek Poverty Paradox</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu)}}
{REPORT_CSS}</style></head><body>
{FRONT}{SUMMARY}{S1}{S2}{S3}{S4}{S5}{S6}{S7}{S8}{BACK}
<script>{ce.JS}</script>
</body></html>
"""

# ---- checks before writing -------------------------------------------------
unplaced = [f for f in EXPECTED if f not in _used]
if unplaced:
    raise SystemExit(f"figures built but never placed: {unplaced}")
_stray = [f for f in APPENDIX_ONLY if f in _used]
if _stray:
    raise SystemExit(
        f"appendix-only figures placed in the report: {_stray}")

for cid in ctx.index:
    if f'data-context-id="{cid}"' not in PAGE:
        raise SystemExit(f"context entry {cid} never placed")

# The placement columns hold WHERE a claim must appear, not whether. Every
# claim marked "body" must be present in this document's body.
required = [i for i in claims.index
            if str(claims.loc[i, "report"]).strip().lower() == "body"]
if not required:
    raise SystemExit("no claims required in the report -- the check is vacuous")
absent = [i for i in required if f'data-claim-id="{i}"' not in PAGE]
if absent:
    raise SystemExit(f"claims required in the report but absent: {absent}")

(OUT / "v2_report.html").write_text(PAGE)
print(f"wrote output/v2_report.html  {len(PAGE):,} chars")
print(f"  figures {len(_used)}  claims {len(required)}  context {len(ctx)}")
