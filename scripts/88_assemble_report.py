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
ctx = pd.read_csv(PROC / "context_register.csv").set_index("id")

# ---- figures come from the batch pages, never rebuilt ----------------------
FIG_SOURCE = {}
for n in (1, 2, 3, 4):
    page = (OUT / f"batch{n}.html").read_text()
    for m in re.finditer(r'<figure class="figure" id="(F\d+)">.*?</figure>', page, re.S):
        FIG_SOURCE[m.group(1)] = m.group(0)

# Derived from the frozen manifest, never hardcoded: a hardcoded range silently
# stops covering any figure added after it was written.
EXPECTED = list(pd.read_csv(PROC / "report_visual_manifest.csv")["id"])
missing = [f for f in EXPECTED if f not in FIG_SOURCE]
if missing:
    raise SystemExit(f"figures missing from the batch pages: {missing}")

_used = []


def fig(fid):
    """Place a built figure. Each may be placed exactly once."""
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    return FIG_SOURCE[fid]


def claim(cid, *, show_caveats=True):
    """Render a frozen claim in its canonical wording, with its caveats.

    The wording is copied from the freeze, never restated, so the report cannot
    drift from what was actually established.
    """
    c = claims.loc[cid]
    cav = ""
    if show_caveats and str(c.caveats) not in ("nan", ""):
        items = "".join(f"<li>{html.escape(x.strip())}</li>"
                        for x in str(c.caveats).split("||"))
        cav = f'<ul class="caveats">{items}</ul>'
    return (f'<div class="claim" data-claim-id="{cid}">'
            f'<div class="claim-head"><span class="cid">{cid}</span>'
            f'<span class="tier">{html.escape(str(c.tier))}</span></div>'
            f"<p class=\"canonical\">{html.escape(str(c.canonical_wording))}</p>{cav}</div>")


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
            f'<div class="ctx-head"><span class="cid">{cid}</span>'
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
        ["Frozen specification (P3)", "included", "+6.93", "3 of 27",
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
         "Four of six pre-registered gates; non-reportable"],
    ]
    return table(
        "T4", "Everything the analysis established, and everything it did not.",
        ["Status", "What it concerns", "Where and how"], rows,
        "Inconclusive means the design could not have detected an effect of "
        "the relevant size. It is not evidence of absence.")


def t_context():
    """The context register at a glance, in its own disjoint vocabulary."""
    rows = []
    for cid, e in ctx.iterrows():
        rows.append([f'<span class="tid">{cid}</span>',
                     html.escape(str(e.topic)),
                     f'<span class="ctx-status">{html.escape(str(e.status))}</span>',
                     "no" if str(e.may_support_a_claim).strip().lower()
                     in ("false", "no", "0") else "yes"])
    return table(
        "T5", "The context register: material discussed but not tested here.",
        ["ID", "Topic", "Status", "May support a claim"], rows,
        "These statuses belong to a deliberately separate vocabulary from the "
        "evidence statuses above, so that contextual material can never be "
        "read as an empirical result.")


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

<div class="howto">
<h2>How to read this document</h2>
<p>Every numbered claim in this report is drawn from a <strong>frozen claim
set</strong>, committed to version control before any of this report was
composed. The freeze followed the last analytical stage rather than preceding
it, and one claim &mdash; V2-7.1, on life satisfaction &mdash; was narrowed
after review when its original wording was found to overstate Greece's
position. Every change to the set is recorded in the research record. Claims appear in their canonical wording, in bordered
blocks marked with an identifier such as <span class="inline-cid">V2-4.C2</span>,
together with the caveats that were frozen alongside them. The caveats are not
decoration: several of them exist because an earlier draft of this report
overstated the finding and was corrected.</p>

<p>Contextual material &mdash; institutional trust, migration, the adjustment
programmes, tax incidence, the pre-crisis wellbeing baseline &mdash; is kept in
a separate <strong>context register</strong> with its own vocabulary, and is
visually distinct from empirical findings. Some of it was examined here:
migration was tested diagnostically, and the cross-domain and ESS comparisons
are descriptive analyses carried out for this report. What the register enforces
is that <strong>none of it may establish a headline analytical claim</strong>.
Each entry states explicitly what it permits and forbids.</p>

<p>Technical material sits behind expandable <em>methods</em> panels. The main
reading path does not depend on opening them; they are there so that every
number can be traced to how it was produced.</p>

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
</div>
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
whether it is detached from that distribution, in which case something
different is happening.</p>

{fig('F2')}

<p>Greece is detached. The gap between Greece and the second-placed country is
larger than the range spanning the middle of the distribution. On a measure
where most of Europe is packed within a few points, Greece sits well clear of
the pack. Whatever produces this is not simply a stronger dose of what produces
variation elsewhere.</p>

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

<p>It helps, and it is not enough. AROPE moves Greece meaningfully closer to
what Greek households report, but it recovers well under a quarter of the
distance. More telling is the direction of travel: AROPE's contribution is
<em>shrinking</em>. The broader measure was adding eleven points at the start
of the period and is adding seven by the end, so as a solution to this puzzle
it is getting weaker rather than stronger.</p>

{claim('V2-2.1')}

<p>An aggregate can conceal as much as it reveals, and AROPE is an aggregate of
three quite different components. Before concluding that the broader measure
merely falls short, it is worth asking which of its parts moved and for
whom.</p>

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
<p>The verification harness now requires every view of every figure to carry at
least two x-values and at least one finite number. This is the kind of defect
that a reader would notice immediately and an automated check will miss unless
it is told to look, and it is recorded here because it was caught in review
rather than by the build.</p>

<h4>Low work intensity and the age dimension</h4>
<p>Very low work intensity is defined only over working-age adults, so it
behaves differently across age groups by construction: households composed
entirely of people above working age are excluded from its denominator. Any
comparison of AROPE across age groups is partly a comparison of which
components can apply, and the figure separates the age groups rather than
presenting a single aggregate that would hide this.</p>
''')}

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

<p>Anchoring the threshold to its pre-crisis real value tells a different
story from the relative measure, and the difference between the two lines is a
direct measure of how much the ruler moved. This is not a criticism of AROP,
which is doing exactly what it was designed to do. It is a statement about what
AROP cannot register: a decline that affects the whole distribution at once
leaves relative position largely undisturbed.</p>

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
inferential test in this report, and no claim in the frozen set rests on
it.</p>
''')}

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

<p>Reported difficulty and concrete affordability failure move together, and
they do so within countries as well as across them &mdash; which is the harder
test, because it cannot be satisfied by rich countries simply differing from
poor ones. It remains corroboration from inside a single instrument.</p>

{claim('V2-3.1')}

<p>The caveats on that claim carry real weight and should not be read past.
Every one of those items, and the outcome itself, comes from the same survey
instrument: EU-SILC. A household in a difficult financial position may answer
the whole battery of questions in a consistently downbeat way, and that alone
would generate correlations of this size without any of the items being
independent confirmation of the others. This is corroboration from within one
instrument, not validation from outside it. Nor is the pattern uniform: the
within-Greece correlation for arrears is much weaker than the range headline
suggests.</p>

<p>The arrears figure deserves particular attention because it is the item
most often treated as the hard, objective anchor of financial distress. Within
Greece it correlates with reported difficulty at 0.371 &mdash; well below the
0.63 floor of the headline range. Arrears depend on having credit and
obligations to fall behind on, so a household that has already lost access to
credit, or that never had it, can be in severe difficulty without registering
arrears at all. A summary that reported only the range would imply a uniformity
that the underlying items do not have.</p>

<p>A stronger version of the same check asks how much of Greece's anomaly these
items can statistically absorb.</p>

{claim('V2-3.2')}

<p>The word <em>absorb</em> is doing precise work and is not a synonym for
<em>explain</em>. What this shows is that once concrete deprivation items are
in the model, most of Greece's unexplained excess is no longer statistically
distinguishable. That is a diagnostic about shared variance. It does not
establish that deprivation causes reported hardship, because both are measured
by the same survey of the same households at the same moment. Stage 6 shows how
much rests on this single modelling decision.</p>

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

<p>Stage 1 noted that the gap narrows after 2016 without closing. That
narrowing is worth examining directly, because a narrowing gap is easy to read
as recovery and that reading is not automatically correct.</p>

{fig('F7')}

<p>The measures did not converge uniformly: some closed a substantial share of
their 2015 distance to the EU, others closed little, and the spread across
measures is wide. A single summary statement about Greek convergence would
misrepresent this.</p>

<p class="caution"><strong>A narrowing gap does not establish Greek
improvement.</strong> The distance between Greece and the EU average can shrink
because Greece improved, because the EU average deteriorated, or because both
moved in the same direction at different speeds. This figure shows the share of
each gap that closed; it does not decompose that closure into the two
countries' contributions, and it should not be read as evidence of Greek
recovery on its own.</p>

<p>Whether these relationships hold across countries and within them is the
question the correlation structure answers directly.</p>

{fig('F6')}

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
clear the same set of gates, in the same order, defined in code and committed
to version control before the analysis ran.</p>

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

<p>Their directions are what one would expect and are worth stating, since a
result that ran the other way would be a reason to distrust the measure rather
than to report it. Higher material resources predict <em>less</em> reported
hardship; more long-term unemployment predicts <em>more</em>; worse
wage-adjusted affordability predicts <em>more</em>. Each direction was declared
in the registry before testing, and a construct whose coefficient had pointed
the other way would have been recorded as contradicting its declared direction
rather than quietly reinterpreted.</p>

<p>These are cross-country associations. Nothing in this design supports a
causal reading, and the frozen caveat on each says so. What they establish is
that a country's material resources, its stock of long-term unemployment and
its wage-adjusted affordability each carry information about reported hardship
that the official income-poverty rate does not.</p>

{fig('F10')}

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
and still found nothing, the exclusion is real &mdash; but it is specific to a
magnitude, not general.</p>

{claim('L-4')}

{t_current()}

<p>Two constructs illustrate why the bootstrap gate was worth imposing. Both
cleared multiplicity correction comfortably and then collapsed under the
bootstrap, with p-values of 0.40 and 0.55. Had the protocol stopped at the
conventional step, both would have been reported as findings.</p>

{methods("The decision rule, the bootstrap, multiplicity, and minimum detectable effects", '''
<h4>Why the rule is code, not prose</h4>
<p>In earlier iterations of this project the decision rule was written as
prose and applied by hand. It failed repeatedly &mdash; not through bad faith,
but because prose admits interpretation at exactly the moments when
interpretation is most tempting. The rule is now a tested Python function,
<code>decide()</code>, with sixty-four unit tests covering its branches
including the ones no observed result reaches. It returns an outcome, the notes
supporting it, and the specific gate that stopped a construct. Every result in
this stage is that function's output, not a judgement made after seeing the
numbers.</p>

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
since the families ask different questions. The family assignments are frozen
in the registry and cannot be changed after the fact without invalidating the
correction.</p>

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

<p>The third of these is borderline and is labelled as such in its frozen
caveat: 91 of 1,999 bootstrap replications exceeded the observed statistic. It
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
built to capture. The baseline was left where it was and the construct is
recorded as infeasible.</p>

{claim('L-3')}

{methods("Accumulation, conditioning, the Mundlak decomposition, and the E7 ceiling", '''
<h4>How accumulation is computed</h4>
<p>Each accumulated series is a cumulative sum of annual excess over a fixed
baseline, computed by pre-registered transforms in <code>accumulate.py</code>
with twenty-seven unit tests. The critical property, tested directly, is that no
accumulated value at year <em>t</em> may use information from any year after
<em>t</em>. The test rebuilds each series from truncated inputs and compares:
if a value changes when future years are removed, the transform leaks and the
test fails.</p>
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
<p>A pre-registered ceiling governs this stage: E7 may only qualify or withdraw
support that Stage 4 established. It may never create support. This exists
because conditional tests run after seeing which constructs succeeded are
post-selection, and allowing them to promote a construct would launder a
selected result into a finding.</p>
<p>The ceiling bound in exactly one case. The accumulated wage-shortfall
measure cleared every conditional gate, but its current-level counterpart was
not supported in Stage 4, so the ceiling caps it. It is reported and it is not
a finding. When the ceiling existed only as prose in the protocol it failed to
bind and the result was briefly written up as a finding; it is now enforced in
code.</p>
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

<p>Recall from Stage 3 that four deprivation items statistically absorbed most
of Greece's excess residual. Those items come from the same survey as the
outcome. Whether to admit a same-instrument predictor into the model is a real
methodological choice with arguments on both sides, and it cannot be settled by
the data.</p>

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

<h3>What else was tried and did not work</h3>

<p>Two further specifications were pre-registered and both failed. They are
recorded here rather than omitted, because a report that shows only the
analyses that worked gives a false impression of how much was attempted.</p>

{claim('L-1')}
{claim('L-2')}

<p>The synthetic-control design was intended to be a centrepiece: construct a
weighted combination of other countries resembling pre-crisis Greece, and read
the divergence after 2008 as the crisis effect. It failed four of six
pre-registered gates. The donor weights collapsed onto two countries, which
means the synthetic Greece was not a credible counterfactual. Its divergence
figure would be the most striking image in this report, and it is machine-blocked
from every output document precisely because it is striking and
uninterpretable.</p>

<p>The multi-domain breadth measure failed a different way: adding it to the
frozen model made Greece's residual worse and reversed its sign under
conditioning. The reversal is left uninterpreted. Post-hoc explanations of sign
reversals in failed specifications are how failed specifications get revived,
and the pre-registration does not permit it.</p>

{methods("Specification choices, what was frozen, and the blocking mechanism", '''
<h4>The frozen specification</h4>
<p>The P3 specification &mdash; the reference model for residual comparisons
&mdash; regresses subjective hardship on AROP, the supported current-level
constructs, severe material deprivation and year fixed effects, with country
residuals extracted for comparison. It was frozen and committed before the
final results were produced, and it has not been altered since. The companion
specification is identical except that the same-instrument deprivation
predictor is removed.</p>
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
<p>Both models produce a Greek residual. It would be easy, and entirely
circular, to prefer whichever residual better matched a prior expectation about
Greece. The protocol therefore forbids selection on residual size, and the
frozen claim records that prohibition rather than leaving it to the reader's
good faith.</p>

<h4>How a non-reportable result is enforced</h4>
<p>The synthetic-control divergence figure is not merely omitted. It is
registered as non-reportable, and the document harness checks every generated
output for it: if it were reintroduced, the build fails rather than producing a
document containing it. The same mechanism enforces the claim-anchoring checks
described in the back matter.</p>
<p>This may look excessive for a project with a single author and a reviewer.
It exists because the failed synthetic control produced the most rhetorically
attractive image in the entire analysis, and rhetorical attractiveness is
exactly the pressure that pre-registration is meant to resist.</p>
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

{fig('F15')}

{claim('V2-7.1')}

<p>The pattern is domain-specific but the difference is one of degree, not
kind. Greece is worst in Europe on the financial indicators and close to worst
on general life satisfaction. That is not the profile of a country whose
financial reports are extreme while its general outlook is ordinary, and an
earlier draft of this report described it that way in error.</p>

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

{fig('F18')}

<p>Three things happen in sequence, and separating them is the whole point of
showing levels rather than ranks alone. Greece was <em>already</em> about
0.8 points below the median of these twelve countries before the crisis, at
third or fourth worst. Its level then fell to 5.64 by 2010/11. And by 2023/24
it had recovered to 6.42, close to where it started.</p>

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
it: the distinction between the financial indicators and the general one is one
of degree, not a contrast between financial hardship and general
contentment.</p>

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
threatening, and report accordingly.</p>
<p>This project ran no test on trust. The figure below reports only the two
values read directly from the OECD source; a per-institution breakdown
circulated in secondary coverage could not be verified against the primary
release and is therefore not shown.</p>
''')}

{fig('F17')}

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
<p>The figure shows rank trajectories because the question is comparative. Rank
is treacherous on its own: a country whose score improves can still fall in the
ranking if others improve faster, which is exactly what happened to Greece on
life satisfaction &mdash; the Greek series rose from 6.2 to 6.9 while its rank
worsened. The figure therefore carries the underlying values alongside the
ranks, and the axis is labelled so that the worst position is unambiguous.</p>

<h4>What this cannot settle</h4>
<p>A domain-specific pattern is consistent with genuine financial difficulty,
and it is also consistent with genuine financial difficulty <em>plus</em> a
general negative tendency. Separating those requires either a pre-crisis
baseline, which this series does not have, or an external anchor on Greek
response style, which this project does not have. The claim is worded to leave
both possibilities open.</p>

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

{methods("How each sentence of this conclusion maps to a frozen claim", '''
<p>The conclusion above introduces no new results. Each of its statements
corresponds to a claim in the frozen set, and the mapping is given here so that
any reader can check the conclusion against what was actually established
rather than against how it is phrased.</p>
<ul>
<li>The size and persistence of the gap, and Greece's rank on each measure:
<strong>V2-1.2</strong>, with the provenance of the extended series in
<strong>V2-1.1</strong>.</li>
<li>AROPE's partial and shrinking contribution: <strong>V2-2.1</strong>.</li>
<li>Correspondence between reported difficulty and concrete failure:
<strong>V2-3.1</strong>, with the absorption diagnostic in
<strong>V2-3.2</strong> and its model dependence in
<strong>V2-6.1</strong>.</li>
<li>The three supported current-level constructs:
<strong>V2-4.C1</strong>, <strong>V2-4.C2</strong> and
<strong>V2-4.C4</strong>; the unresolved remainder in <strong>V2-4.X</strong>
and the magnitude-specific exclusions in <strong>L-4</strong>.</li>
<li>The three supported accumulated measures: <strong>V2-5.C2</strong>,
<strong>V2-5.C3</strong> and <strong>V2-5.C6</strong>; the reversal in
<strong>V2-5.X</strong>; the prohibition on dynamic wording in
<strong>V2-5.Y</strong>; the untestable construct in
<strong>V2-5.Z</strong>; the capped result in <strong>L-3</strong>.</li>
<li>The reporting-style question: <strong>V2-7.1</strong>, whose caveats carry
the second-worst life-satisfaction position and the rising Greek level.</li>
<li>The failed designs: <strong>L-1</strong> and <strong>L-2</strong>.</li>
</ul>
<p>The measurement recommendation is <strong>CTX-6</strong> and is registered
as author interpretation rather than as a finding. It follows from what the
analysis showed the single measures miss; it is not itself a result.</p>
''')}

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

<h3>Pre-registration</h3>

<p>Each analytical stage was committed to version control <strong>with zero
results</strong> before it was run. The commit history shows, for every stage,
a specification-only commit preceding the commit that adds output. This is
checkable rather than asserted: the repository is the record.</p>

<p>The decision rules are executable code with unit tests, not prose. This
followed from repeated failure of the prose version. On three separate
occasions a rule that read unambiguously in the protocol document failed to
bind when results arrived &mdash; not through bad faith, but because prose
admits interpretation precisely when interpretation is most tempting. Rules
that live in <code>e_rule.py</code>, <code>registry.py</code> and
<code>accumulate.py</code> carry 64, 12 and 27 tests respectively and cannot be
reinterpreted after seeing an outcome.</p>

<p>Two protocol deviations occurred and both are recorded in the research
record with their reasons. Neither was a change made after seeing a result it
would affect.</p>

{methods("Corrections made during review, and what they changed", '''
<p>Thirty-three corrections are logged in the research record. Most were
routine. Several changed a stated finding, and those are summarised here
because a report that mentions only its successes misrepresents how it was
produced.</p>
<ul>
<li><strong>Adverse-direction inversion.</strong> A translation between two
vocabularies silently mapped every variable to the same direction, flagging four
correct results as contradictions. Caught by inspection, fixed by passing the
registry vocabulary through directly, and prevented from recurring by
validating vocabularies at module load.</li>
<li><strong>A degenerate constructed series.</strong> The wage-adjusted excess
measure was built from a source holding absolute euros where an index was
assumed, producing zeros throughout. Every test on it had been meaningless. Now
indexed explicitly with a failing assertion on the source scale.</li>
<li><strong>A robustness rule that returned the wrong verdict.</strong> The
companion-model rule compared absolute residuals across a sign change, treating
a movement from +2.46 to a larger negative value as degradation. The
implementation was corrected to match the frozen wording rather than the
wording being loosened to match the implementation.</li>
<li><strong>A ceiling that did not bind.</strong> The Stage 5 ceiling existed
only in prose, and a construct that its own prior stage had not supported was
briefly written up as a finding. The ceiling is now enforced in code.</li>
<li><strong>A verification check that could not fail.</strong> The figure
checksum test compared two stored values both written by the same builder, so a
tampered figure passed. It now recomputes the checksum from the rendered table
content, and the negative test fails as it should.</li>
<li><strong>A figure whose default view was empty.</strong> Every structural
check passed on a figure whose first tab displayed nothing, because the checks
verified structure and not data. A data gate was added requiring every view to
carry at least two x-values and one finite number.</li>
<li><strong>Three separate overstatements of the between/within
result</strong>, each treating imprecise within-country estimates as evidence
of absence. The third prompted a claim-specific guard in the verification
harness.</li>
<li><strong>A factually false headline.</strong> A figure caption claimed
Greece led Europe on all three accumulated measures; Hungary leads on wage
non-recovery. Corrected, and the figure now shows the full ranking.</li>
<li><strong>A misread rank.</strong> Greece's life-satisfaction position was
described as middling when it is second-worst in the EU. The affected claim was
narrowed and its caveats extended.</li>
</ul>
<p>The pattern worth noting is that most of these were caught by a reviewer
rather than by the harness, and each one that was caught by a person produced a
new automated check so that it could not recur silently.</p>
''')}

<h3>Data</h3>

<p>All quantitative inputs are Eurostat, principally EU-SILC, at country-year
level for the EU27 over 2015&ndash;2024, with the constructed pre-2010
extension described in Stage 1 used for description only. The institutional
trust figures come from the OECD's 2024 trust survey and were read from the
primary release. Migration figures are national-level Greek data.</p>

<p>The literature cited in the context register was verified against primary
sources rather than secondary summaries: each reference in Stage 7 was checked
at its publisher or repository of record.</p>

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

<h3>Registers</h3>

<p>Four registers govern the documents in this project and are maintained in
the research record: results (49 entries), decisions (64), corrections (33) and
protocol deviations (2). The frozen claim set contains 21 claims; the context
register contains 6 entries with a deliberately disjoint vocabulary, so that a
contextual statement can never be mistaken for an empirical one.</p>

{methods("The verification harness", '''
<p>Documents in this project are generated, not written by hand, and are
checked mechanically before they are published.</p>
<h4>Claim anchoring</h4>
<p>Every claim in the frozen set must appear in each document that is required
to carry it, inside a container tagged with its identifier. Matching is by
distinctive-word overlap against the canonical wording, so a container that
merely cites an identifier without stating the claim does not pass. The
harness reports how many of the required claim-document pairs are present and
fails the build below the threshold.</p>
<h4>Context anchoring</h4>
<p>The same mechanism applies to context entries, with an additional
constraint: a document that discusses a registered topic without an anchored
container is flagged. This prevents contextual material from drifting into the
main argument unlabelled.</p>
<h4>Figure checks</h4>
<p>Thirteen checks run against every figure: that no internal variable name
appears in a reader-facing label, that the value checksum recomputed from the
rendered fallback table matches the one the chart carries, that every view
holds at least two x-values and one finite number, that the view count and
chart type match the frozen visual manifest, that each figure carries a badge,
a question and a keyboard-reachable chart, that no figure uses a bare pixel
width, and that pinned-width content scrolls within its own container. All 65
checks pass across the four figure batches.</p>
<h4>Blocked outputs</h4>
<p>Results registered as non-reportable &mdash; principally the failed
synthetic-control divergence figure &mdash; are checked for by identifier in
every generated document. Their reappearance fails the build.</p>
<h4>Skipped inputs</h4>
<p>An optional input that is unavailable writes an explicit status marker
recording that it was skipped and why. A stage whose optional input is missing
must not be able to read as a completed one merely because the pipeline exited
cleanly. The ESS extension in Stage 7 is the current instance.</p>
''')}

<h3>Reproduction</h3>

<p>The full sequence runs from the repository root with <code>make all</code>,
followed by <code>make verify</code>, which runs the unit tests, the figure
checks and the document harness. Figures in this report are lifted verbatim
from batch pages that passed their checks independently, so the checksums shown
in each figure's fallback table are the ones computed at build time.</p>

<p>Detailed provenance for every number &mdash; which script produced it, from
which artifact, under which decision &mdash; is in the research record, which
is generated alongside this report from the same registers.</p>
</section>
"""


# ===========================================================================
#  PAGE
# ===========================================================================
BASE = re.search(r"<style.*?</style>", (OUT / "report.html").read_text(), re.S).group(0)

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
.inline-cid{font:600 .85em ui-monospace,SFMono-Regular,Menlo,monospace;
  background:var(--surface-2);padding:.1em .4em;border-radius:3px}
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
.claim{border:1px solid var(--border);border-left:4px solid var(--series-gr);
  border-radius:0 6px 6px 0;padding:1rem 1.2rem;margin:1.6rem 0;
  background:var(--surface-2)}
.claim-head{display:flex;gap:.7rem;align-items:center;margin-bottom:.5rem}
.claim .cid{font:700 .74rem ui-monospace,SFMono-Regular,Menlo,monospace;
  letter-spacing:.04em}
.claim .tier{font:.7rem ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
  letter-spacing:.08em;color:var(--text-secondary)}
.canonical{margin:0;font-size:1.01rem;line-height:1.6}
.caveats{margin:.7rem 0 0;padding-left:1.1rem;font:.89rem/1.55 ui-sans-serif,
  system-ui,sans-serif;color:var(--text-secondary)}
.caveats li{margin:.25rem 0}
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
.verdict.mid{color:var(--series-3)}
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
{FRONT}{S1}{S2}{S3}{S4}{S5}{S6}{S7}{S8}{BACK}
{ce.build_stamp()}
<script>{ce.JS}</script>
</body></html>
"""

# ---- checks before writing -------------------------------------------------
unplaced = [f for f in EXPECTED if f not in _used]
if unplaced:
    raise SystemExit(f"figures built but never placed: {unplaced}")

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
