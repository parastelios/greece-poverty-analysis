"""Assemble the academic paper.

The empirical sections are rebuilt around the final evidence. The institutional
background, the literature review and the reference list are carried over from
the earlier draft, which remains accurate: nothing in the later analysis
changed what the published literature says or what Greece's crisis consisted
of.

What did change is the argument those sections lead into. The earlier draft
concluded that Greece's residual was "ultimately explained by accumulated,
rather than current-year, labour-market exposure". That does not survive: the
accumulated measures carry cross-country information, no within-country dynamic
was demonstrated, present conditions were not ruled out, and for wage-adjusted
affordability the relationship runs the other way. Sections 4 through 9 are
written against the evidence as it finally stood.

Claims and context entries are anchored in the markup for the acceptance
checks. No identifier, tier, register or internal variable name appears in the
text: this is a paper, not a project record.
"""
import html
import math
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
OUT, PROC = ROOT / "output", ROOT / "data" / "processed"
FRAG = Path(__file__).resolve().parent / "paper_sections"

claims = pd.read_csv(PROC / "e_final_claims.csv").set_index("id")
ctx = pd.read_csv(PROC / "context_register.csv").set_index("id")
DISPLAY_CODES = sorted(ce.DISPLAY, key=len, reverse=True)

SPEC_WORDS = {
    "the frozen P3 specification": "the reference specification",
    "the frozen model": "the reference model",
    "machine-blocked from every output document":
        "withheld from every document in this project",
}


def reader_text(s):
    """Presentation only: the claim set is never edited here."""
    s = str(s)
    for code in DISPLAY_CODES:
        s = s.replace(f" ({code})", "")
    for a, b in SPEC_WORDS.items():
        s = s.replace(a, b)
    return s


# ---- figures: lifted from the checked batch pages, never rebuilt -----------
FIG_SOURCE = {}
for n in (1, 2, 3, 4):
    page = (OUT / "build" / f"batch{n}.html").read_text()
    for m in re.finditer(r'<figure class="figure" id="(F\d+)">.*?</figure>', page, re.S):
        FIG_SOURCE[m.group(1)] = m.group(0)

# A paper carries the figures its argument needs, not the full evidence base.
# The rest stays in the technical report and the statistical appendix.
# One figure per argument the paper has to make:
#   F1  the central paradox
#   F3  the moving threshold, which Section 5.4 rests on
#   F21 breadth of deterioration: how many measures place Greece in the worst
#       fifth of the Union, and which ones
#   F5  what the AROPE aggregate conceals -- components and age groups. This
#       slot previously carried the "breadth" label, which was wrong: F5
#       decomposes ONE measure, it does not count how many measures moved.
#   F9  the current-condition results
#   F12 historical exposure, conditional on present conditions
#   F13 the between/within limitation
#   F14 model dependence
PAPER_FIGS = ["F1", "F21", "F5", "F3", "F9", "F12", "F13", "F14"]
# The selection is FROZEN. Figure ids changed meaning during the figure work --
# what an id pointed at was not stable -- so this list records a decision about
# what this document argues, and any change to it has to be a decision too.
_FROZEN = ['F1', 'F21', 'F5', 'F3', 'F9', 'F12', 'F13', 'F14']
if PAPER_FIGS != _FROZEN if "PAPER_FIGS" in dir() else NARRATIVE_FIGS != _FROZEN:
    raise SystemExit(
        "the paper figure selection changed; update _FROZEN deliberately")

_used = []


# Figures whose views must all be visible at once here rather than sitting
# behind tabs. A tab bar is a row of dead buttons on paper and in PDF, where
# only the first view survives, and these figures need both halves together:
#   F3  the fixed-versus-moving threshold AND the nominal-versus-real threshold
#       are two different questions. The first shows that ordinary AROP misses
#       people whose income fell because the line fell with it; the second
#       shows why -- the line recovered in euros and is still about a fifth
#       lower in what it buys. Neither carries the argument alone.
STACKED = {"F3"}


def fig(fid, number):
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    src = FIG_SOURCE[fid]
    # Academic numbering: the reader sees "Figure 3", not the project's own id.
    src = src.replace(
        "<figcaption>",
        f'<figcaption><span class="fignum">Figure {number}</span> ', 1)
    if fid in STACKED:
        n = src.count('type="application/json"')
        if n < 2:
            raise SystemExit(
                f"{fid} is marked STACKED but carries {n} view(s); either it "
                "lost a view or the marking is stale")
        src = src.replace('data-chart=', 'data-views="stacked" data-chart=', 1)
    return src


def claim(cid):
    """A finding in its established wording, with its limits. No identifier."""
    c = claims.loc[cid]
    cav = ""
    if str(c.caveats) not in ("nan", ""):
        items = "; ".join(html.escape(x.strip()) for x in str(c.caveats).split("||"))
        cav = f'<p class="limits"><em>Limits.</em> {items}.</p>'
    return (f'<div class="finding" data-claim-id="{cid}">'
            f"<p>{html.escape(reader_text(c.canonical_wording))}</p>{cav}</div>")


def context(cid, prose):
    """A competing explanation or contextual factor, with its standing."""
    e = ctx.loc[cid]
    cite = ""
    if str(e.source_status) != "not applicable":
        url = (f' <a href="{e.source_url}">link</a>'
               if isinstance(e.source_url, str) and e.source_url else "")
        det = f" {e.source_detail}" if isinstance(e.source_detail, str) and e.source_detail else ""
        cite = (f'<p class="src">{html.escape(str(e.source))}{det}{url}</p>')
    return (f'<div class="ctx" data-context-id="{cid}">'
            f'<p class="ctx-status">{html.escape(str(e.status))}</p>'
            f"<h4>{html.escape(str(e.topic))}</h4>{prose}"
            f'<p class="permitted"><em>What may be concluded.</em> '
            f"{html.escape(str(e.permitted))}</p>"
            f'<p class="limitation"><em>Limitation.</em> '
            f"{html.escape(str(e.forbidden))}</p>{cite}</div>")


def frag(slug):
    return (FRAG / f"{slug}.html").read_text()


def literature():
    """The preserved review, with two repairs.

    The extract is kept faithful on disk; the repairs happen here so the reason
    for each is visible.

      * Its final subsection, "Contribution of this paper", asserts that
        duration matters "under full nested validation". That is the conclusion
        the later analysis withdrew, and it cannot stand. The contribution is
        stated in the introduction instead, against the evidence as it finally
        stood.
      * It refers the reader to a section number from the earlier draft's
        structure, which no longer exists.
    """
    s = frag("literature")
    i = s.find("<h3")
    while i != -1:
        head = s[i:s.find("</h3>", i)]
        if "Contribution of this paper" in head:
            nxt = s.find("<h3", i + 4)
            s = s[:i] + (s[nxt:] if nxt != -1 else "")
            break
        i = s.find("<h3", i + 4)
    # Every cross-reference in the extract points at the earlier draft's
    # numbering. Remap the ones that still have a target and drop the rest
    # rather than leave a reader chasing a section that no longer exists.
    for old, new in [("&sect;5.3", "Section 5.4"), ("§5.3", "Section 5.4"),
                     ("&sect;6.7", "Section 6.1"), ("§6.7", "Section 6.1"),
                     ("&sect;6.2", "Section 6.2"), ("§6.2", "Section 6.2"),
                     ("&sect;8", "Section 8"), ("§8", "Section 8")]:
        s = s.replace(old, new)
    s = s.replace("Part II's central empirical puzzle",
                  "The central empirical puzzle of this paper")
    return s


def references():
    """The reference list, with the earlier draft's trailing note removed.

    That note described the old section structure, cited section numbers that
    no longer exist, and recorded a data-vintage detail now covered by Section
    10. The reference entries themselves are unchanged.
    """
    s = frag("references")
    i = s.find("This working paper is a preprint")
    if i == -1:
        raise SystemExit("references: trailing note not found -- check the extract")
    # Trim back to the end of the element containing the note.
    start = s.rfind("<", 0, i)
    tag = re.match(r"<(\w+)", s[start:])
    end = s.find(f"</{tag.group(1)}>", i)
    return s[:start] + (s[end + len(tag.group(1)) + 3:] if end != -1 else "")


def background():
    """The preserved background, with its one cross-reference remapped."""
    s = frag("background")
    return (s.replace("&sect;7.3", "Section 7.3").replace("§7.3", "Section 7.3")
             .replace("proceed directly to &sect;3", "proceed directly to Section 3")
             .replace("proceed directly to §3", "proceed directly to Section 3"))


def results_table():
    """Every present-day construct, its verdict and where it stopped."""
    d = pd.read_csv(PROC / "e1_results.csv")
    OUT_LBL = {"supported": "Supported",
               "inconclusive_under_available_power": "Inconclusive",
               "unsupported_with_adequate_power": "Unsupported",
               "blocked_by_proximity": "Not testable"}
    GATE = {"bootstrap": "wild cluster bootstrap", "fdr": "multiplicity",
            "power": "insufficient power", "proximity": "proximity to outcome",
            "direction": "adverse direction", "incremental": "incremental test"}
    dupes = set(d.name[d.name.duplicated(keep=False)])
    rows = []
    for r in d.sort_values(["outcome", "construct"]).itertuples():
        nm = html.escape(str(r.name))
        if str(r.name) in dupes:
            nm += f" &mdash; {html.escape(ce.name(str(r.var)))}"
        p_b = ("&mdash;" if r.boot_p != r.boot_p
               else (f"{r.boot_p:.4f}" if r.boot_p >= 0.0001 else "&lt;0.0001"))
        gate = ("&mdash;" if str(r.failed_gate) == "nan"
                else GATE.get(str(r.failed_gate), str(r.failed_gate)))
        rows.append(f"<tr><td>{nm}</td><td class='n'>{r.coef:+.4f}</td>"
                    f"<td class='n'>{p_b}</td>"
                    f"<td>{OUT_LBL.get(str(r.outcome), str(r.outcome))}</td>"
                    f"<td>{gate}</td></tr>")
    return ("<table class='res'><caption><b>Table 1.</b> Present-day "
            "constructs: coefficient, bootstrap <em>p</em>, verdict, and the "
            "condition that stopped each construct that did not clear. "
            "Coefficients are on each construct's own scale and are not "
            "comparable across rows.</caption>"
            "<thead><tr><th>Construct</th><th class='n'>Coef.</th>"
            "<th class='n'>Bootstrap <em>p</em></th><th>Verdict</th>"
            "<th>Stopped at</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")



# ===========================================================================
#  FRONT MATTER AND INTRODUCTION
# ===========================================================================
FRONT = """
<header class="titleblock">
<h1>Subjective Poverty and the Limits of Relative-Income Measurement:
Evidence from Greece, 2015&ndash;2024</h1>
<p class="byline">Working paper</p>
</header>

<div class="abstract">
<h2 class="abs">Abstract</h2>
<p>Greek households report difficulty making ends meet at a rate roughly
53 percentage points above the country's official at-risk-of-poverty rate, a
divergence sustained over a decade and far larger than in any other member
state. We ask what that gap is composed of. Using a country-year panel of the
EU27 over 2015&ndash;2024 and a pre-specified testing protocol, we establish
three things. First, the divergence is not an artefact of the broader official
measure: at-risk-of-poverty-or-social-exclusion closes about a fifth of it, and
its contribution is declining. Second, reported difficulty co-moves with
concrete affordability failure within countries, though all such items are
drawn from the same survey instrument as the outcome and therefore corroborate
rather than validate it. Third, material resources, long-term unemployment and
wage-adjusted affordability each predict reported hardship beyond income
poverty, and accumulated exposure on labour, wages and housing retains
cross-country predictive information after present-day conditions are
controlled. We find no evidence supporting a within-country dynamic reading,
and the within-country estimates are too imprecise to exclude one. A single
specification choice &mdash; whether to admit a same-instrument deprivation
predictor &mdash; moves Greece from the third to the twenty-fifth largest
unexplained residual in the sample, and we report both specifications without
selecting between them. Most of the gap remains unexplained.</p>
<p class="kw"><strong>Keywords:</strong> subjective poverty; material
deprivation; relative income thresholds; anchored poverty; Greece; EU-SILC</p>
</div>

<section id="s1">
<h2>1. Introduction</h2>

<p>The European Union measures poverty in two ways that are both official and
rarely compared. The at-risk-of-poverty rate (AROP) counts households below
60% of their own country's median equivalised disposable income. A separate
EU-SILC item asks households directly whether they have difficulty making ends
meet. The first is a position in a national income distribution; the second is
a report about lived circumstances. There is no reason the two must coincide,
and across most of Europe they diverge modestly and stably.</p>

<p>Greece is the exception. Over 2015&ndash;2024 the average distance between
the two measures is 52.6 percentage points. Greece ranks first of twenty-seven
member states on reported hardship while ranking seventh on AROP, and the
distance between Greece and the next-ranked country on the subjective measure
exceeds the range spanning most of the remaining distribution. This is not the
tail of a continuum; it is a separation.</p>

<p>This paper asks what that separation consists of. The question admits
several answers that are not mutually exclusive, and the contribution here is
to test them under one pre-specified protocol rather than to advocate for any
of them. The candidate accounts are: that the official measure is too narrow,
and a broader one would close the gap; that the relative income threshold
itself moved during the Greek collapse, so that AROP could not register a
decline affecting the whole distribution; that households are reporting real
material difficulty that income-based measures do not capture; that present-day
economic conditions carry information beyond income poverty; that the
<em>duration</em> of adverse conditions carries information beyond their
present level; and that Greek respondents answer subjective questions more
negatively than others.</p>

<p>Our answer is layered and incomplete, and we state the incompleteness as a
result rather than as a caveat. The measurement accounts &mdash; a broader
concept of poverty, and a threshold that fell with the economy &mdash; are real
and account for a minority of the distance. The reported hardship corresponds
to concrete affordability failure, though the evidence for this comes from
within a single instrument. Three present-day conditions and three accumulated
ones carry predictive information beyond income poverty. A reporting tendency
cannot be excluded. And after all of this, most of the 52.6-point gap is not
attributed.</p>

<p>The contribution is threefold. First, we decompose a specific and unusually
large measurement divergence rather than documenting it, testing each available
account under a protocol fixed before the results were seen. Second, we
distinguish throughout between constructs the design excluded and constructs it
could not resolve, and we compute the minimum detectable effect for each
negative result so that the distinction is quantitative rather than rhetorical;
this matters because the majority of our negative results fall into the second
category and would be misreported as nulls under conventional practice. Third,
we report the model dependence of a central result at full strength rather than
selecting the specification that supports the argument, and we report two
pre-specified designs that failed.</p>

<p>The corresponding limitation should also be stated at the outset. This is a
country-level analysis of twenty-seven countries over a decade. It cannot
identify causal effects, cannot speak to individual households, and has limited
power against effects of moderate size. Readers seeking a decomposition of the
Greek gap into attributable shares will not find one here; what we offer is a
bounded account of which candidate explanations survive testing, and an
explicit statement of how much remains unexplained after they do.</p>

<p>Three features of the design deserve statement at the outset, because they
determine how the results should be read.</p>

<p><em>The protocol was fixed before testing.</em> Nine present-day constructs
and eight accumulated ones were specified in advance, together with the
conditions each had to satisfy and the order in which those conditions applied.
Verdicts are the output of that procedure rather than a reading of the
resulting coefficients. This matters most for the negative results: it is what
allows a distinction between constructs the design could not resolve and
constructs it could have detected and did not.</p>

<p><em>Inference is cross-country.</em> The unit of analysis is the
country-year. Nothing in this design identifies a causal effect, and nothing
here describes an individual household. We use "predicts" throughout in its
statistical sense and avoid causal language even where a causal reading would
be natural.</p>

<p><em>One result is model-dependent, and we report it as such.</em> Whether to
admit a same-instrument deprivation predictor is a defensible choice either
way, and the two choices place Greece at opposite ends of the residual
distribution on identical rows. We present both and select neither, because
selecting on the size of a residual is the practice that makes robustness
checks uninformative.</p>

<p>The paper proceeds as follows. Section 2 describes the Greek institutional
and macroeconomic setting. Section 3 reviews the relevant literature on
relative thresholds, subjective measures and the Greek crisis. Section 4 sets
out the data and the testing protocol. Section 5 establishes the paradox and
examines the two measurement accounts. Section 6 reports what predicts
reported hardship, and what does not. Section 7 discusses competing
explanations that this design cannot adjudicate. Section 8 states the
limitations. Section 9 concludes.</p>
</section>
"""


# ===========================================================================
#  4. DATA AND METHODS
# ===========================================================================
S4 = f"""
<section id="s4">
<h2>4. Data and methods</h2>

<h3>4.1 Panel and sources</h3>

<p>The estimation panel is country-year, covering the EU27 over
2015&ndash;2024. The outcome is the share of households reporting difficulty or
great difficulty making ends meet. From 2010 onward this is Eurostat's
published series, used directly. Earlier years, used for description only, are
derived from the official components of the corresponding earlier release under
an aggregation rule validated on 432 overlapping country-years, of which 318
agree exactly and 114 differ by a single rounding step; none differs by more
than 0.1 percentage points, and the cross-country rank correlation is 1.00 in
every year. The validation establishes the aggregation rule only. It does not
establish comparability across earlier national survey vintages, and no
inferential result in this paper uses the extended years.</p>

<p>Income poverty, at-risk-of-poverty-or-social-exclusion, severe material and
social deprivation, arrears, capacity to meet unexpected expenses and heating
adequacy come from EU-SILC. Long-term unemployment comes from the Labour Force
Survey. Prices and wages come from the harmonised price index and national
accounts. Actual individual consumption per head in purchasing power standards
comes from the purchasing-power parity programme. Incomes are equivalised using
the OECD-modified scale throughout. Nothing is imputed: where a country-year
lacks a value the observation is dropped from the specification requiring it.</p>

{claim('V2-1.1')}

<h3>4.2 Constructs</h3>

<p>Nine present-day constructs were specified before testing: material
resources, labour-market exclusion, loss against a country's own past (four
measures), wage-adjusted affordability, inflation exposure, housing pressure,
and proximate material hardship. For each construct supported at the
present-day stage, a matching accumulated measure was constructed: the total
excess exposure absorbed since a fixed baseline rather than the level today.
Accumulated series are cumulative sums of annual excess over a baseline of 2008
or 2010 depending on data availability, and are constructed so that no value at
year <em>t</em> uses information from any year after <em>t</em>.</p>

<h3>4.3 Testing protocol</h3>

<p>Every construct was required to satisfy the same conditions in the same
order. It must add explanatory power beyond AROP and year fixed effects; it
must survive false-discovery-rate correction within its declared family; its
coefficient must lie in the declared adverse direction; it must not be
mechanically or instrumentally too proximate to the outcome to be tested
without circularity; and it must survive a wild cluster bootstrap.</p>

<p>Year fixed effects absorb Europe-wide shocks &mdash; the sovereign debt
crisis, the pandemic, the 2022 energy shock &mdash; that would otherwise be
attributed to whichever construct moved concurrently. Conditioning on AROP is
what makes each test one of incremental information: a construct that merely
proxies income poverty cannot satisfy the first condition.</p>

<p>Standard errors clustered on twenty-seven countries are unreliable, since
cluster-robust inference is asymptotic in the number of clusters. We therefore
use a wild cluster bootstrap with the null imposed, 1,999 replications. The
restricted variant is not optional here: an unrestricted implementation
returned <em>p</em> = 0.82 for a coefficient with a <em>t</em>-statistic of
9.69, which is a symptom of misspecification rather than a marginal
disagreement. Multiplicity is controlled by the Benjamini-Hochberg procedure
within families declared before testing; applying it across families
regardless would be more conservative but incoherent, since the families
address different questions.</p>

<h3>4.4 Estimating equations</h3>

<p>For a construct <em>x</em>, country <em>i</em> and year <em>t</em>, the
present-day test estimates</p>

<p class="eq">H<sub>it</sub> = &alpha; + &beta;&thinsp;x<sub>it</sub> +
&gamma;&thinsp;AROP<sub>it</sub> + &delta;<sub>t</sub> +
&epsilon;<sub>it</sub></p>

<p>where H is the share of households reporting difficulty making ends meet
and &delta;<sub>t</sub> are year fixed effects. The hypothesis concerns
&beta;, and the conditioning on AROP is what makes it a test of incremental
information rather than of association with poverty in general.</p>

<p>The conditional test in Section 6.3 adds the accumulated counterpart
<em>a</em> alongside the present-day measure,</p>

<p class="eq">H<sub>it</sub> = &alpha; + &beta;<sub>1</sub>&thinsp;a<sub>it</sub>
+ &beta;<sub>2</sub>&thinsp;x<sub>it</sub> + &gamma;&thinsp;AROP<sub>it</sub> +
&delta;<sub>t</sub> + &epsilon;<sub>it</sub></p>

<p>and asks whether &beta;<sub>1</sub> survives. The between/within
decomposition in Section 6.4 replaces <em>a</em> with a country mean and a
deviation from it, following Mundlak, so that the cross-sectional and
longitudinal components of the same variable carry separate coefficients. The
coefficient on the country mean is the between-country association; the
coefficient on the deviation is the within-country one. Reporting only a pooled
estimate would blend them and permit a between-country result to be read as a
within-country process.</p>

<p>All specifications cluster on country. Where two specifications are
compared, as in Section 6.5, they are estimated on the intersection of their
non-missing rows, so that a change in coefficient cannot reflect a change in
sample.</p>

<h3>4.5 Power, and the meaning of a negative result</h3>

<p>A test that fails to detect an effect is informative only if it could have
detected one. For every construct that did not satisfy the conditions, the
minimum detectable effect was computed by simulation rather than by formula:
the observed panel structure is retained, an effect of known size is injected,
and the proportion of simulated samples in which the protocol recovers it is
recorded. The minimum detectable effect is the smallest injected effect
recovered in at least 80% of samples.</p>

<p>This licenses a distinction we maintain throughout. A construct is
<em>inconclusive</em> where the design could not have detected an effect of the
relevant magnitude, and <em>unsupported</em> only where it could have and did
not &mdash; in which case the exclusion is stated at the magnitude that holds.
Collapsing these two would misrepresent the majority of our negative results.
For the conditional tests in Section 6.3 the minimum detectable effect is
computed pair-specifically and conditionally, since the relevant question there
is whether an accumulated measure adds information <em>given</em> its
present-day counterpart.</p>

<h3>4.6 Sensitivity to single countries</h3>

<p>Each construct is additionally refitted twenty-seven times with one country
removed in turn, and the range of coefficients across those refits is recorded.
This guards against a result carried by a single country &mdash; including, and
especially, by Greece, since a finding driven by the case the paper is about
would be circular.</p>
</section>
"""


# ===========================================================================
#  5. RESULTS I -- the paradox and the measurement accounts
# ===========================================================================
S5 = f"""
<section id="s5">
<h2>5. Results I: the paradox and the measurement accounts</h2>

<h3>5.1 The divergence</h3>

<p>Figure 1 shows the two series for Greece. They do not converge over the
observed period: reported hardship begins near 80% and remains above 60%
throughout, while income poverty moves within a narrow band around 20%. The
distance narrows somewhat after 2016, which we return to in Section 5.6, but
never approaches agreement.</p>

{fig('F1', 1)}

{claim('V2-1.2')}

<p>Ranking first is not by itself informative, since some country must. The
relevant question is whether Greece lies at the end of a smooth distribution,
in which case it is the extreme case of an ordinary pattern, or is separated
from it. The distance between Greece and the second-ranked country on reported
hardship exceeds the range spanning the middle of the distribution: whatever
produces the Greek position is not a larger dose of what produces variation
elsewhere.</p>

<h3>5.2 One measure, or a field of measures?</h3>

<p>A single detached indicator invites the explanation that the indicator is
faulty. That explanation is weaker if the indicator has company. We therefore
take twenty-five indicators of Greek economic and social conditions &mdash;
wages, hours worked, prices, unemployment, migration, household debt, saving,
and expectations &mdash; and for each one record whether the country falls in
the worst quintile of the Union in a given year. The outcome and every model
covariate are excluded from the count, so the measure cannot restate the
quantity the paper sets out to explain. Years reporting fewer than ten
indicators are dropped.</p>

{fig('F21', 2)}

<p>Greece was in the worst quintile on roughly a quarter of these indicators
before the crisis and is in the worst quintile on approximately two thirds of
them now. Sixteen of the twenty-five now place the country at or near the
bottom of the distribution, and they are not restatements of a single quantity:
hourly compensation, hours worked, the real value of the poverty threshold
itself, the household saving rate, expectations for the coming year, and net
migration of nationals all sit together.</p>

<p>This measure is descriptive and is treated as such throughout. It was
entered as a candidate predictor of reported hardship in the exploratory Family
D analysis and did not survive: alone it is not significant
(<em>b</em>&nbsp;=&nbsp;5.94, <em>p</em>&nbsp;=&nbsp;0.12), and when the other
accumulated measures enter the same specification its coefficient reverses sign
(<em>b</em>&nbsp;=&nbsp;&minus;2.17). A quantity whose sign depends on the rest
of the model cannot support an explanatory reading. It is not among the six
constructs of Section 6.2, which were pre-registered; this test was exploratory
throughout and could not have strengthened the evidentiary tier whatever it
returned. Its role here is to establish that the divergence in
Section 5.1 sits inside a broad deterioration rather than standing alone, which
is a claim about the setting and not about mechanism. The second panel plots
each indicator by <em>position</em> in the European distribution rather than by
value, because the twenty-five share no common unit; 0 is the most favourable
position in the Union on that indicator and 100 the least, in whichever
direction the indicator runs.</p>

<h3>5.3 Does the broader official measure close it?</h3>

<p>The European Union already treats income poverty alone as too narrow. Its
headline social indicator, at-risk-of-poverty-or-social-exclusion (AROPE),
counts a household as affected if it falls below the income line, is severely
materially deprived, or lives in a household with very low work intensity. If
the divergence is simply a matter of AROP being too narrow, AROPE should
largely dissolve it.</p>

{claim('V2-2.1')}

<p>It does not. AROPE recovers under a quarter of the distance, and the
direction of travel is against the measurement account: its contribution falls
from 11.0 points in 2015 to 7.3 in 2024. As a resolution of this puzzle the
broader measure is weakening rather than strengthening.</p>

<h3>5.4 What the aggregate conceals</h3>

<p>AROPE is a union of three conditions rather than a sum, so the headline rate
cannot be decomposed into its components without double-counting the overlap.
Examining the components separately is nonetheless informative about why the
aggregate moves less than the experience it summarises. Over the observed
period the components do not move together, and neither do the age groups
within them. A headline rate combining a falling component with a rising one
can remain stable while the composition beneath it changes substantially.</p>

<p>One component behaves differently by construction. Very low work intensity
is defined over working-age adults, so households composed entirely of people
above working age are excluded from its denominator; any comparison of AROPE
across age groups is therefore partly a comparison of which components can
apply. We report the components separately for this reason rather than
presenting an age-disaggregated aggregate that would obscure it.</p>

{fig('F5', 3)}

<p>Two features of the disaggregation bear on the argument. Greece is at or
near the top of the European distribution on income poverty, severe material
deprivation and the combined measure alike, so the position is not an artefact
of one component. And the burden is not evenly distributed: the age groups
diverge, and women sit above men throughout, with the difference widening after
2022.</p>

<h3>5.5 The moving threshold</h3>

<p>The second measurement account concerns the ruler rather than the concept.
AROP counts households below 60% of the <em>current</em> national median. This
is a deliberate design choice and a defensible one, but it has a consequence
that becomes severe in a large enough contraction: when national income falls,
the threshold falls with it, and a household whose real income dropped sharply
can remain above a line that dropped as sharply.</p>

<p>Greek median equivalised income fell by roughly a third over the crisis. The
poverty line, being a fixed fraction of it, fell in step. Figure 3 compares the
relative threshold with one anchored to its 2008 real value.</p>

{fig('F3', 4)}

<p>The anchor year was fixed before the comparison was run and was not selected
by inspecting which choice produced the largest divergence. We note two
limitations. The anchored series in this paper is constructed for Greece alone
and therefore supports no cross-country statement: it shows that the Greek
threshold fell relative to Greece's own pre-crisis standard, not that it fell
further than any other country's. And anchored and relative poverty answer
different questions, neither of which is the correct one in general. Where a
whole distribution declines together, they diverge sharply, and that divergence
is the substantive point rather than a defect.</p>

<p>Our reconstruction is coarser than the household-level anchored series
computed by Andriopoulou, Kanavitsa and Tsakloglou, and we use their
income-year-2013 figure as an external benchmark rather than as a replication
target.</p>

<h3>5.6 Convergence, and what it does not show</h3>

<p>The narrowing after 2016 invites a recovery reading, and that reading does
not follow. A gap between a country and the EU average can close because the
country improved, because the average deteriorated, or because both moved in
the same direction at different speeds. Decomposing the closure into those
contributions would require attributing movement to each side, which we do not
do. The measures also did not converge uniformly: some closed a substantial
share of their 2015 distance and others closed little, so a single summary
statement about Greek convergence would misrepresent the pattern.</p>

<h3>5.7 Does the reported hardship correspond to anything?</h3>

<p>If Greek households report hardship without corresponding material
difficulty, the object of study is response behaviour rather than poverty, and
the remaining analysis measures an artefact. We therefore test whether reported
difficulty co-moves with items naming concrete events: arrears, inability to
meet an unexpected expense, inability to heat the home adequately, and severe
material and social deprivation.</p>

{claim('V2-3.1')}

<p>We report the within-country correlations because between-country
correlation is weak evidence here: richer countries score better on essentially
every welfare indicator, so almost any pair correlates across countries without
either telling us about mechanism. The within figures are computed after
demeaning each series by its country mean, so a country persistently high on
both contributes nothing.</p>

<p>The limitation is structural and we place it in the text rather than in a
footnote. Every one of these items, and the outcome, is self-reported by the
same household in the same interview. A household answering the whole battery
downbeat would generate correlations of this size without any item
independently confirming another. This is corroboration from within one
instrument, not external validation, and the pattern is not uniform: arrears
within Greece correlates at 0.371, well below the range headline.</p>

<p>A stronger version of the same test asks how much of Greece's excess these
items statistically absorb.</p>

{claim('V2-3.2')}

<p>The word absorb is doing precise work. Once concrete deprivation items enter
the model, most of Greece's unexplained excess is no longer statistically
distinguishable. That is a statement about shared variance, not about
mechanism, and Section 6.4 shows how much rests on the decision to admit such
a predictor at all.</p>
</section>
"""


# ===========================================================================
#  6. RESULTS II -- what predicts reported hardship
# ===========================================================================
S6 = f"""
<section id="s6">
<h2>6. Results II: what predicts reported hardship</h2>

<h3>6.1 Present-day conditions</h3>

<p>Three of the nine present-day constructs satisfied every condition.</p>

{claim('V2-4.C1')}
{claim('V2-4.C2')}
{claim('V2-4.C4')}

<p>The directions are as expected and were declared before testing: greater
material resources predict less reported hardship, more long-term unemployment
predicts more, and worse wage-adjusted affordability predicts more. A construct
whose coefficient had pointed the other way would have been recorded as
contradicting its declared direction rather than reinterpreted.</p>

<p>Figure 4 shows all nine as standardised effects, which is what makes them
comparable: the constructs are measured in percentages, purchasing power
standards and index points, and raw coefficients could not share an axis.</p>

{fig('F9', 5)}

{results_table()}

<p>Leave-one-out refits confirm that the three supported constructs do not
depend on any single country. Long-term unemployment ranges from 3.20 to 4.83
across the twenty-seven refits against a headline of 4.34, and wage-adjusted
affordability from 0.25 to 0.33 against 0.31. Housing pressure, which does not
clear the conditions, ranges from &minus;0.10 to 1.27 and therefore changes
sign when one country is dropped.</p>

<h3>6.2 The six that did not, and what that does and does not mean</h3>

<p>Six constructs did not satisfy the conditions. Describing these as ruled out
would misstate most of them.</p>

{claim('V2-4.X')}

<p>With twenty-seven countries and roughly a decade of observations the design
has limited power, and for most of the six the smallest reliably detectable
effect exceeds any magnitude of substantive interest. Those constructs are
inconclusive: the study is silent about them rather than negative. Where the
design did have adequate power, the exclusion is real but magnitude-specific.</p>

{claim('L-4')}

<p>Two constructs illustrate why the bootstrap condition was imposed. Both
cleared multiplicity correction comfortably and then collapsed under the
bootstrap, at <em>p</em> = 0.40 and 0.55. A protocol stopping at the
conventional step would have reported both as findings.</p>

<h3>6.3 Accumulated exposure</h3>

<p>Two countries can present identical current conditions and have reached them
by different routes. Whether that history carries information is tested by
placing each accumulated measure in the same specification as its own
present-day counterpart and asking whether it survives. Because the two are
correlated by construction, the test is conservative: shared variance is
attributed to neither.</p>

{fig('F12', 6)}

{claim('V2-5.C2')}
{claim('V2-5.C3')}
{claim('V2-5.C6')}

<p>The third is borderline, with 91 of 1,999 bootstrap replications exceeding
the observed statistic, and is reported at that strength. The second holds only
under one construction &mdash; the current uninterrupted run against a fixed
2008 base &mdash; and alternative constructions of the same idea point the same
way without meeting the criteria; they are not counted as corroboration.</p>

<p>The pattern is not uniform, which is itself informative.</p>

{claim('V2-5.X')}

<p>For wage-adjusted affordability the relationship reverses: the present-day
measure survives conditioning while the accumulated one does not resolve. Were
accumulation a general property of this outcome, that reversal should not
appear. It suggests the accumulated results are specific to labour markets,
wages and housing rather than reflecting a general history effect &mdash; and
it is the clearest reason to resist a summary in which history supersedes
present conditions.</p>

<p>One construct could not be tested at all, and we report it rather than
omitting it.</p>

{claim('V2-5.Z')}

{claim('L-3')}

<h3>6.4 The limit of the accumulated results</h3>

<p>The results in Section 6.3 are statements about differences between
countries. Converting them into statements about change within Greece over time
is not supported, and Figure 7 shows why.</p>

{fig('F13', 7)}

{claim('V2-5.Y')}

<p>We are explicit about what this does not establish. The within-country
estimates are imprecise, and imprecision is not evidence of absence: these
tests discard all cross-sectional variation and have considerably less power
than the between-country ones. The correct statement is that this design does
not support dynamic wording, not that a within-country relationship has been
shown to be absent.</p>

<h3>6.5 Model dependence</h3>

<p>Whether to admit a same-instrument deprivation predictor is a genuine
methodological choice. In favour: severe material deprivation is a
substantively meaningful, officially published measure, and excluding variables
because they are well measured is not a principle anyone holds. Against: when
predictor and outcome come from the same respondents answering adjacent
questions, part of any relationship reflects shared measurement rather than
shared substance. We ran both.</p>

{fig('F14', 8)}

{claim('V2-6.1')}

<p>Greece moves from the third to the twenty-fifth largest unexplained residual
&mdash; from a marked positive anomaly to a marked negative one &mdash; on
identical rows, with one predictor added or removed. This is a reversal rather
than a sensitivity, and we neither average the two nor select between them.
Selecting a specification on the size of its residual is precisely the practice
that renders robustness checks uninformative. What can be said is that
conclusions about how much of Greece's anomaly is absorbed depend materially on
a choice the data cannot adjudicate.</p>

<h3>6.6 Two pre-specified designs that failed</h3>

<p>Two further analyses were specified in advance and did not work. We report
them because a paper presenting only its successful analyses misrepresents the
evidence base.</p>

{claim('L-1')}

<p>The synthetic-control design was intended to carry substantial weight:
construct a weighted combination of donor countries tracking pre-crisis Greece,
and read post-2008 divergence as the crisis effect. On the only substantively
defensible pre-period, 2003&ndash;2008, only six countries have complete
coverage and the fit is poor, with donor weights collapsing onto two countries.
Restricting the match to 2007&ndash;2008 produces a near-exact pre-period fit
on two observations against roughly twenty-five free donor weights, which is
not evidence of fit. We report the diagnostics and not the divergence estimate,
which has no defensible interpretation.</p>

{claim('L-2')}

<p>The multi-domain breadth measure failed differently: adding it to the
reference model worsened Greece's residual and reversed its sign under
conditioning. We leave the reversal uninterpreted. Post-hoc explanation of sign
reversals in failed specifications is the mechanism by which failed
specifications return.</p>
<h3>6.7 Robustness</h3>

<p>Four checks bear on the results above and we summarise them together. The
wild cluster bootstrap with the null imposed is the binding condition for two
constructs that clear multiplicity correction, which is the reason it is
applied rather than conventional cluster-robust inference. Leave-one-out
refits establish that no supported result depends on a single country. The
between/within decomposition establishes that the accumulated results are
cross-sectional, and we report the imprecision of the within estimates rather
than treating them as nulls. And the two specifications in Section 6.5
establish the boundary of what the absorption result can bear.</p>

<p>Two checks that a reader might expect are absent, and their absence is
deliberate. We do not report a specification chosen for producing the most
favourable Greek residual, because that choice is available in both directions
and is uninformative. And we do not report the synthetic-control divergence,
because a construction whose donor pool collapses onto two countries yields a
quantity with no defensible interpretation, however precise it appears.</p>
</section>
"""


# ===========================================================================
#  7-9. DISCUSSION, LIMITATIONS, CONCLUSION
# ===========================================================================
S7 = f"""
<section id="s7">
<h2>7. Discussion</h2>

<h3>7.1 Is this a reporting artefact?</h3>

<p>The most economical account of everything above is that Greek respondents
answer subjective questions more negatively than others. Section 5.6 addresses
this partly, but from within a single instrument. A better test compares Greek
responses across <em>domains</em>: a general negative tendency should depress
all of them roughly equally, whereas a pattern concentrated in financial items
points toward circumstances.</p>

{claim('V2-7.1')}

<p>The pattern is domain-specific, but the difference is one of degree rather
than kind, and an earlier version of this analysis described it too favourably.
Greece is worst in Europe on the financial indicators and close to worst on
general life satisfaction. Two quantities must also be held apart: Greek life
satisfaction <em>rose</em> over the observed period, from 6.2 to 6.9, while
Greece's <em>rank</em> worsened because other countries improved faster. A
worsening rank on a rising series is not falling satisfaction.</p>

{context('CTX-1', '''
<p>The cross-domain comparison is descriptive corroboration for the
domain-specificity reading rather than a test of it. Greece's financial
indicators sit at the extreme of the European distribution while its
general-wellbeing indicator sits close to it, and that difference in degree is
what the comparison shows.</p>''')}

<p>Two features of this test limit what it can deliver. A domain-specific
pattern is consistent with genuine financial difficulty, and equally consistent
with genuine financial difficulty accompanied by a general negative tendency;
separating those would require either a pre-crisis baseline on the same
instrument or an external anchor on Greek response style, and we have neither.
And the comparison is between ranks in a European distribution, which move when
other countries move: the Greek life-satisfaction rank worsened over a period
in which the Greek level rose, because other countries improved faster. We
therefore report levels alongside ranks throughout and treat the two as
distinct quantities.</p>

<h3>7.2 A pre-crisis baseline</h3>

<p>The Eurostat wellbeing series begins in 2013, at the trough of the Greek
crisis, and therefore cannot establish whether Greece was already unusual
before 2008. We address this with a separate instrument, reported separately
and never joined to the EU-SILC series.</p>

<p>Using publicly published weighted response distributions from the European
Social Survey for six rounds in which Greece participated, and holding fixed
the twelve countries present in all six, Greece sat approximately 0.8 points
below the median <em>before</em> the crisis, fell to 5.64 by 2010/11, and
recovered its level to approximately its pre-crisis value by 2023/24. Its
comparative position did not recover: the gap to the median is wider than
before the crisis, and Greece has ranked lowest of the twelve since 2010/11.</p>

<p>These means are reconstructed from displayed percentages and are approximate
at that precision; no standard error can be attached to them and no test is run
on them. The all-country ranks are not compared across rounds, since the ESS
country set varies from twenty-two to thirty and a rank against a changing set
would confound Greece's position with participation. The implication for
Section 7.1 is direct: a low Greek baseline pre-dates the crisis, so the
position cannot be attributed to the crisis alone, and a longstanding
low-wellbeing pattern remains plausible without being established.</p>

{context('CTX-7', '''
<p>Across six rounds, holding the same twelve countries fixed, the Greek level
fell and then recovered while the comparative position did not.</p>''')}

<h3>7.3 Factors this design cannot adjudicate</h3>

<p>Several factors prominent in accounts of the Greek crisis are not
established here. Some were examined: migration was tested on this panel and
the cross-domain and ESS comparisons are descriptive analyses conducted for
this paper. None of them can carry a headline finding, and we set out what each
permits.</p>

{context('CTX-2', '''
<p>Institutional trust is low in Greece by OECD measurement, and a route by
which it could matter is available: households not expecting effective support
may experience identical material circumstances as more threatening. Trust is
measured on a different instrument, sample and periodicity from the panel used
here, and no defensible country-year merge exists for this period.</p>''')}

{context('CTX-3', '''
<p>The adjustment programmes from 2010 reshaped incomes, employment protection,
pensions and public services simultaneously and over a compressed period. They
are the historical setting for every accumulated measure in Section 6.3.</p>''')}

{context('CTX-4', '''
<p>Emigration of working-age Greeks during the crisis is well documented and
interacts with the labour-market measures in both directions: plausibly a
consequence of prolonged labour-market damage, and plausibly a contributor to
the composition of who remains.</p>''')}

{context('CTX-5', '''
<p>Published incidence research establishes that the Greek indirect tax system
became markedly more regressive across the crisis. If household disposable
positions worsened through taxation in ways income-based poverty measures
capture poorly, that would be one route to a gap of the kind documented
here.</p>''')}

<h3>7.4 Implications for measurement</h3>

{context('CTX-6', '''
<p>The analysis shows repeatedly that no single official indicator captures
what Greek households report. AROP misses both concept and yardstick; AROPE
adds breadth but a declining share of it; anchored poverty registers what the
relative line cannot; and accumulated labour and housing exposure carries
information none of the present-day measures hold.</p>''')}
</section>

<section id="s8">
<h2>8. Limitations</h2>

<p>These are properties of the design rather than qualifications appended to
it, and several of them bound the results more tightly than the results
themselves.</p>

<p><em>Aggregate inference.</em> The unit of analysis is the country-year.
Every result is an aggregate association, and an aggregate relationship need
not hold at household level. That accumulated unemployment predicts national
hardship rates does not establish that individuals who experienced unemployment
report more hardship.</p>

<p><em>No causal identification.</em> Nothing in this design identifies a
causal effect. We report associations conditional on AROP and year effects, and
the direction of any underlying mechanism is not established.</p>

<p><em>Cluster count.</em> Twenty-seven clusters is marginal for inference,
which is why the bootstrap condition exists and why so many constructs land as
inconclusive. A larger panel would convert a substantial part of this paper
from silence into evidence.</p>

<p><em>Short outcome window.</em> The accumulated measures reach back to 2008
or 2010, but the outcome supports roughly a decade of variation, and
within-country identification draws only on that. This is the direct cause of
the imprecision in Section 6.4.</p>

<p><em>Shared instrument.</em> The corroboration in Section 5.6 comes from
items collected in the same interview as the outcome, and Section 6.5 shows
that admitting such a predictor moves Greece's residual across the full range
of the sample.</p>

<p><em>Unexplained remainder.</em> Of the 52.6-point average distance, the
accounts established here address a minority. We do not attribute the rest.</p>

<p><em>External validity.</em> Greece is studied here because it is the extreme
case, and that is also the principal constraint on generalisation. The
inferential results are estimated across twenty-seven countries and are not
Greece-specific &mdash; the leave-one-out refits confirm that dropping Greece
does not overturn them &mdash; but the question the paper asks is prompted by a
divergence that only Greece exhibits at this magnitude. Whether the same
accounts would decompose a smaller divergence elsewhere is untested. We would
expect the measurement components to travel, since they follow from how the
indicators are constructed rather than from Greek particulars, and would expect
the accumulated-exposure results to travel only to countries that experienced a
contraction of comparable duration. Neither expectation is established here.</p>

<p>Two further limitations concern the outcome itself. The item asks about
difficulty making ends meet without specifying a reference period or a
standard, so the quantity respondents report is not fixed by the instrument;
this is a general property of subjective items and is the reason Section 7.1
treats the reporting question directly rather than assuming it away. And the
outcome is a household-level assessment aggregated to a national share, so a
country with a small number of households in extreme difficulty and a country
with widespread moderate difficulty can return the same figure. The measures
tested here are not able to distinguish those cases, and no result in this
paper should be read as bearing on the depth of hardship as opposed to its
incidence.</p>
</section>

<section id="s9">
<h2>9. Conclusion</h2>

<p>Greek households report financial difficulty far above what the official
relative-poverty rate predicts, persistently and by a margin that separates
Greece from the European distribution rather than placing it at one end of it.
Three bodies of evidence make part of that distance more intelligible.</p>

<p>The official measures are narrower than the experience they are taken to
summarise. The broader AROPE measure closes about a fifth of the distance and
its contribution is declining, and the relative income line fell with the Greek
economy, which a relative measure cannot register by design. What households
report corresponds to concrete affordability failure, within countries as well
as across them, though this is corroboration from inside one survey instrument
rather than independent validation. And both present conditions and accumulated
exposure carry predictive information beyond income poverty: material
resources, long-term unemployment and wage-adjusted affordability at the
present-day stage, and accumulated unemployment, the duration of wage
non-recovery and housing-cost deterioration conditional on their own
present-day counterparts.</p>

<p>What the evidence does not support is equally part of the result. No causal
claim is made anywhere. No within-country dynamic reading is supported, and the
within-country tests are too imprecise to exclude one. Most constructs that did
not clear the conditions are unresolved rather than excluded. A central
absorption result reverses under a defensible alternative specification. A
broader negative reporting tendency is not ruled out, and the ESS comparison
indicates a Greek deficit that pre-dates the crisis. And most of the gap
remains unexplained.</p>

<p>Four developments would change these conclusions. Corroboration from outside
EU-SILC &mdash; administrative arrears, utility disconnection records, or an
independent survey &mdash; would settle whether the co-movement in Section 5.6
reflects shared substance or shared instrument, which Section 6.5 shows this
design cannot resolve. A longer or wider panel would convert most of the
inconclusive results into findings or genuine nulls. Household-level analysis
would permit the within-country tests this design cannot support. And
respondent-level access to a pre-crisis wellbeing instrument would place
Section 7.2 on a footing that admits inference.</p>

<p>The measurement implication follows from what the single indicators miss
rather than from any test reported here, and we state it as an interpretation:
a poverty dashboard combining the relative rate, its real threshold, anchored
poverty, deprivation, and accumulated labour and housing exposure would
represent a prolonged contraction better than any one of them alone.</p>
</section>
"""


# Sections 2 and 3 are carried over from the earlier draft, which remains
# accurate. Both were short for their role in the argument: the background did
# not establish the DURATION of the Greek adjustment, which is what motivates
# the accumulated measures, and the literature review did not cover subjective
# measurement or scarring. The additions below sit after the preserved text.
S2_EXTRA = """
<h3>2.1 A contraction measured in years as well as depth</h3>

<p>The depth of the Greek contraction is widely reported; its duration is the
feature that motivates the measures in Section 6.3. Unemployment did not
return below 20% until 2019, eleven years after the peak of the cycle, and
long-term unemployment &mdash; those out of work for a year or more &mdash;
stood at 16.4% of the labour force as late as 2015 and did not fall below 10%
until 2021. For a substantial cohort, joblessness was not an episode between
jobs but a condition lasting the better part of a decade.</p>

<p>Recovery in the aggregate has been real and rapid. Unemployment fell from
25.0% in 2015 to 10.1% in 2024, and long-term unemployment from 16.4% to 5.4%
over the same period. Actual individual consumption per head rose from
approximately 14,800 to 21,300 purchasing power standards. On the headline
labour and consumption series, Greece in 2024 is a substantially different
country from Greece in 2015.</p>

<h3>2.2 What has not returned</h3>

<p>Two series behave differently, and they are the ones this paper's
accumulated measures track. Real wages stood at roughly 77% of their 2008 level
in 2015 and at 68% in 2024: they did not recover across the observed period,
and by this measure Greek wages have now been below their pre-crisis level for
longer than in any other member state except Hungary. Housing cost overburden
&mdash; the share of the population spending more than 40% of disposable income
on housing &mdash; fell from 45.5% in 2015 to 28.9% in 2024, an improvement from a
level that remained several times the EU median throughout: 5.2 times it in
2015 and 4.3 times it in 2024.</p>

<p>This divergence between the labour aggregates and the wage and housing
series is the substantive reason a paper about Greek hardship cannot rely on
present-day conditions alone. A household observing an unemployment rate of
10.1% in 2024 is also observing a wage that has not recovered in sixteen
years.</p>

<h3>2.3 Composition</h3>

<p>The population itself changed over the period. Net emigration of Greek
nationals through the crisis years was substantial and has partially reversed
since; the aggregate series used here cannot separate a country whose
circumstances improved from a country whose composition changed, and Section
7.3 records this as an unresolved interaction rather than a controlled
factor.</p>
"""

S3_EXTRA = """
<h3>3.5 The case against cross-national subjective comparison</h3>

<p>The objection to the measure used here is established and deserves stating
in its strongest form. Subjective assessments are sensitive to reference
groups, to adaptation over time, and to national conventions of response; on
that view a cross-country comparison of subjective items measures response
culture as much as circumstance, in a way that comparison of income percentiles
does not. If the objection holds in full, the divergence documented in Section
5.1 is a fact about Greek respondents rather than about Greek households.</p>

<p>We do not assume the objection away. Section 5.6 tests whether reported
difficulty tracks concrete affordability failure, and Section 7.1 tests whether
the Greek pattern is concentrated in financial domains or general across them.
Both narrow the objection without eliminating it, and Section 7.2 shows that
part of the Greek position pre-dates the crisis, which is consistent with a
longstanding component that this design cannot separate from circumstance.</p>

<h3>3.6 Duration, scarring and hysteresis</h3>

<p>The proposition that the length of an adverse spell matters beyond its
depth is well developed in the labour literature, where long unemployment
spells are associated with persistent effects on subsequent earnings and
employment that are not explained by the depth of the initial shock. The
mechanism most often proposed &mdash; depletion of savings, erosion of skills
and networks, and the exhaustion of household coping capacity &mdash; implies
that two households facing identical current conditions may differ according to
how long those conditions have obtained.</p>

<p>This paper tests the aggregate analogue of that proposition and finds it
partially supported: accumulated exposure on labour, wages and housing retains
cross-country predictive information after present conditions are controlled.
We emphasise in Section 6.4 that this is not the household-level scarring
result the literature describes, and that the design cannot deliver one.</p>

<h3>3.7 Anchored thresholds and cumulative exposure as measurement choices</h3>

<p>Anchoring a poverty threshold to a base year's real value is a long-standing
device for separating changes in relative position from changes in living
standards, and its properties are well understood: it answers a different
question from the relative measure rather than a better version of the same
one. The choice of base year is consequential and is the principal degree of
freedom the method offers, which is why we fix it in advance and report that we
did.</p>

<p>Cumulative exposure measures are less standardised. Constructing one
requires three decisions &mdash; the baseline against which excess is measured,
whether excess accumulates continuously or resets, and whether the quantity of
interest is a stock of accumulated deficit or a duration &mdash; and the
literature offers no settled convention for any of them. We specify each in
advance and, where a construct admits more than one defensible construction, we
report the one specified and note that alternatives point the same way without
counting them as corroboration. This is a weaker position than a standardised
measure would allow, and we regard the absence of such a convention as a
limitation of the area rather than of this paper.</p>

<h3>3.8 The Greek case in comparative perspective</h3>

<p>Greece's position on subjective hardship is frequently noted and rarely
decomposed. The literature on the Greek crisis has concentrated, reasonably, on
its fiscal and macroeconomic dimensions and on distributional consequences
measured with income-based instruments. The contribution attempted here is
narrower and complementary: to ask what the persistent gap between the two
official measures is composed of, and to report how much of it remains
unaccounted for after the available accounts are tested.</p>
"""


# ===========================================================================
#  PAGE
# ===========================================================================
BASE = ce.base_style((OUT / "build" / "report.html").read_text())

PAPER_CSS = """
body{max-width:46rem;margin:0 auto;padding:0 1.3rem 6rem;
  font:1.0rem/1.7 ui-serif,Georgia,'Times New Roman',serif}
.titleblock{padding:3rem 0 1.2rem;border-bottom:1px solid var(--border);
  margin-bottom:1.6rem}
.titleblock h1{font-size:clamp(1.6rem,4vw,2.2rem);line-height:1.22;margin:0 0 .7rem;
  letter-spacing:-.01em;text-wrap:balance}
.byline{font:.85rem ui-sans-serif,system-ui,sans-serif;color:var(--text-secondary);
  margin:0}
.abstract{background:var(--surface-2);border-radius:6px;padding:1.2rem 1.4rem;
  margin:0 0 2.4rem;font-size:.95rem}
.abstract h2.abs{font:600 .74rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.12em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 .7rem;border:0;padding:0}
.abstract p{margin:0 0 .7rem}
.kw{font-size:.87rem;color:var(--text-secondary);margin:0}
section{margin:2.6rem 0 0}
h2{font-size:1.32rem;margin:2.6rem 0 .8rem;letter-spacing:-.01em;
  padding-top:.9rem;border-top:1px solid var(--border)}
h3{font-size:1.06rem;margin:1.8rem 0 .5rem}
h4{font-size:.98rem;margin:1.2rem 0 .4rem}
p{margin:0 0 .9rem}
.finding{border-left:3px solid var(--series-gr);padding:.1rem 0 .1rem 1rem;
  margin:1.3rem 0}
.finding p{margin:0 0 .4rem;font-size:1.02rem}
.limits{font:.87rem/1.6 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin:0}
.ctx{border:1px dashed var(--border);border-radius:5px;padding:.9rem 1.1rem;
  margin:1.4rem 0}
.ctx-status{font:600 .68rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 .45rem}
.ctx h4{margin:0 0 .5rem;font-size:.98rem}
.ctx p{font-size:.93rem}
.ctx .permitted,.ctx .limitation,.ctx .src{
  font:.85rem/1.55 ui-sans-serif,system-ui,sans-serif;margin:.5rem 0 0}
.ctx .limitation{color:var(--text-secondary)}
.ctx .src{color:var(--text-secondary);font-size:.8rem;padding-top:.4rem;
  border-top:1px solid var(--border)}
.eq{text-align:center;margin:1rem 0;font-size:1.02rem;font-style:italic}
table.res{border-collapse:collapse;width:100%;margin:1.4rem 0;
  font:.85rem/1.45 ui-sans-serif,system-ui,sans-serif;
  font-variant-numeric:tabular-nums;display:block;overflow-x:auto}
table.res caption{caption-side:top;text-align:left;font-size:.85rem;
  color:var(--text-secondary);margin-bottom:.5rem;line-height:1.5}
table.res th{text-align:left;font-weight:700;font-size:.75rem;
  text-transform:uppercase;letter-spacing:.05em;color:var(--text-secondary);
  padding:.5rem .7rem;border-bottom:1px solid var(--text-secondary)}
table.res td{padding:.45rem .7rem;border-bottom:1px solid var(--border)}
table.res .n{text-align:right;white-space:nowrap}
.figure figcaption{font-size:.9rem}
ol.refs,.refs li{font-size:.88rem;line-height:1.55}
@media print{h2{break-after:avoid}.figure{break-inside:avoid}}
@media (max-width:34rem){body{font-size:.97rem}}
"""

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Subjective Poverty and the Limits of Relative-Income Measurement</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu)}}
{PAPER_CSS}</style></head><body>
{FRONT}
{background()}{S2_EXTRA}
{literature()}{S3_EXTRA}
{S4}{S5}{S6}{S7}
<section id="s10">
<h2>10. Data and reproducibility</h2>

<p>All quantitative inputs are published series. The outcome, income poverty,
at-risk-of-poverty-or-social-exclusion, deprivation and housing series come
from Eurostat's EU-SILC collection; long-term unemployment from the Labour
Force Survey; prices and wages from the harmonised price index and national
accounts; and consumption per head from the purchasing power parity programme.
Institutional trust figures in Section 7.3 come from the OECD's 2024 survey on
drivers of trust in public institutions and were read from the primary release.
The comparison in Section 7.2 uses publicly published weighted response
distributions from the European Social Survey portal; respondent-level ESS
files are not used, and no result in this paper depends on them.</p>

<p>The analysis runs end to end from these published sources by code, without
manual steps. Every figure in this paper carries the numbers behind it in an
expandable table beneath the chart, so each chart can be checked against its
own data without recourse to the source files. A technical report and a
statistical appendix accompany this paper and carry the full evidence base,
including the constructs and specifications not reported here.</p>

<p>Analysis and drafting were assisted by a large language model under author
direction. All specifications, decision rules and conclusions were fixed by the
authors, and every quantitative statement in this paper is generated from the
source data rather than transcribed.</p>
</section>

{references()}
<script>{ce.JS}</script>
</body></html>
"""

# ---- checks ---------------------------------------------------------------
missing_f = [f for f in PAPER_FIGS if f not in _used]
if missing_f:
    raise SystemExit(f"paper figures selected but not placed: {missing_f}")

required = [i for i in claims.index
            if str(claims.loc[i, "paper"]).strip().lower() == "body"]
if not required:
    raise SystemExit("no claims required in the paper -- the check is vacuous")
absent = [i for i in required if f'data-claim-id="{i}"' not in PAGE]
if absent:
    raise SystemExit(f"claims required in the paper but absent: {absent}")

for cid in ctx.index:
    if f'data-context-id="{cid}"' not in PAGE:
        raise SystemExit(f"context entry {cid} never placed")

# No identifier, register vocabulary or internal name may reach the reader.
visible = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", PAGE, flags=re.S))
visible = html.unescape(visible)
BANNED = ["V2-", "CTX-", "L-1", "L-2", "L-3", "L-4", "frozen claim",
          "aic_pps_pc", "ltu_rate", "wadj_a01", "data-claim-id"]
leaked = [b for b in BANNED if b in visible]
if leaked:
    raise SystemExit(f"internal vocabulary visible in the paper: {leaked}")

(OUT / "academic_paper.html").write_text(PAGE)
print(f"wrote output/academic_paper.html  {len(PAGE):,} chars")
print(f"  claims {len(required)}  context {len(ctx)}  figures {len(_used)}")
