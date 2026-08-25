"""Assemble the narrative companion.

The earlier companion's voice and chapter structure are kept: direct, concrete,
no jargon, one idea per chapter. Its evidence is not. Most chapters were
written against an earlier analysis and carry numbers from models that no
longer exist -- one presents a "proof table" showing Greece's gap falling from
11.6 to 3.9 and its rank moving from 1st to 6th, quantities the final analysis
does not contain, and describes long-term unemployment as "the mechanism that
best explains" Greek hardship, which the final analysis does not support.

So the chapters are rewritten against the evidence as it finally stood, in the
register the companion established. Where an explanation in the earlier text is
still accurate and well put -- the account of why a relative poverty line falls
with the economy, or why duration is a different question from rate -- it is
carried forward.

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
    page = (OUT / f"batch{n}.html").read_text()
    for m in re.finditer(r'<figure class="figure" id="(F\d+)">.*?</figure>', page, re.S):
        FIG_SOURCE[m.group(1)] = m.group(0)

# A general reader needs fewer charts than the technical report carries, and
# each has to earn its place in the story rather than complete the record.
# Selected by purpose, not by id: several ids changed meaning during the figure
# work, so reuse by id was unsafe. Five, deliberately fewer than the report:
#   F1  the paradox
#   F3  the threshold that moved
#   F5  breadth, across measures and across groups
#   F11 the historical scars
#   F15 the strongest contextual figure -- where Greece sits on three indicators
NARRATIVE_FIGS = ["F1", "F3", "F5", "F11", "F15"]

# Non-figure blocks that travel from the batch pages. The pre-crisis comparison
# is six rows with a decade missing from the middle, which is a table.
BLOCKS = {}
for _n in (1, 2, 3, 4):
    _page = (OUT / f"batch{_n}.html").read_text()
    for _m in re.finditer(r'<div class="(ess-table)">.*?</p></div>', _page, re.S):
        BLOCKS[_m.group(1)] = _m.group(0)


def block(key):
    if key not in BLOCKS:
        raise SystemExit(f"block '{key}' not found in any batch page")
    return BLOCKS[key]
# The selection is FROZEN. Figure ids changed meaning during the figure work --
# what an id pointed at was not stable -- so this list records a decision about
# what this document argues, and any change to it has to be a decision too.
_FROZEN = ['F1', 'F3', 'F5', 'F11', 'F15']
if PAPER_FIGS != _FROZEN if "PAPER_FIGS" in dir() else NARRATIVE_FIGS != _FROZEN:
    raise SystemExit(
        "the narrative figure selection changed; update _FROZEN deliberately")

_used = []


def fig(fid):
    """Place a built figure, numbered in the order the reader meets it."""
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    n = len(_used)
    return FIG_SOURCE[fid].replace(
        "<figcaption>", f'<figcaption><span class="fignum">Figure {n}</span> ', 1)


def finding(cid):
    """The established wording, quietly set apart, with its limits."""
    c = claims.loc[cid]
    cav = ""
    if str(c.caveats) not in ("nan", ""):
        items = "; ".join(html.escape(x.strip()) for x in str(c.caveats).split("||"))
        cav = f'<p class="limits"><em>The limits of this.</em> {items}.</p>'
    return (f'<div class="finding" data-claim-id="{cid}">'
            f"<p>{html.escape(reader_text(c.canonical_wording))}</p>{cav}</div>")


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


def chapter(key, title, body):
    """Number derives from position, never passed in.

    Chapters refer to each other by KEY, not by number. Writing "Chapter 4"
    into prose breaks the moment a chapter is inserted ahead of it, which is
    exactly what happened when the generational chapter was added. Prose uses
    the token {ch:key} and the numbers are resolved once, after the sequence
    is final. Chapter bodies are f-strings, so the token is WRITTEN as
    {{ch:key}} and arrives here single-braced -- which is the form matched
    below. An earlier version matched the double-braced form, found nothing,
    and reported success while leaving every reference unresolved.
    """
    n = len(CH) + 1
    CH_KEYS[key] = n
    return (f'<section class="ch" id="ch{n}">'
            f'<p class="chnum">Chapter {n}</p><h2>{title}</h2>{body}</section>')


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


# ===========================================================================
#  CHAPTERS 1-4
# ===========================================================================
CH = []

CH.append(chapter("paradox", "Two official numbers that don't agree", f"""
<p>Europe measures poverty in two ways, and both are official.</p>

<p>The first counts households whose income falls below 60% of what a typical
household in their country earns. It is a number about position: are you far
behind your neighbours? The second is a question put directly to households:
are you having difficulty making ends meet? It is a number about experience.</p>

<p>In most of Europe the two roughly agree. In Greece they are 52.6 percentage
points apart, and have been for a decade.</p>

<p>Put plainly: roughly one Greek household in five is officially counted as at
risk of poverty. Roughly two in three say they are struggling to get by. Those
are not two attempts to measure the same thing that landed slightly apart. They
are far enough apart that no ordinary measurement error closes them.</p>

{fig('F1')}

{finding('V2-1.2')}

<p>Greece also ranks first in the European Union on the question about
struggling, and seventh on the income measure. That combination is what makes
this a puzzle rather than a ranking. And Greece is not simply the last country
in a long queue: the distance between Greece and the next country is wider than
the distance covering most of the rest of Europe. Whatever is happening here is
not a stronger dose of what happens elsewhere.</p>

<p>This report is an attempt to find out what that gap is made of. The honest
summary of the answer, given at the start so that nothing later reads as a
reveal: we can account for part of it, we can rule some explanations out, and
most of it remains unexplained.</p>
"""))

CH.append(chapter("ruler", "A ruler that shrank", f"""
<p>The official poverty line isn't fixed. It moves with the very economy it is
supposed to be measuring.</p>

<p>Here is the quiet flaw at the centre of the EU's standard poverty measure:
it is not an income level. It is a percentage &mdash; 60% of whatever the
national median income happens to be, <em>that year</em>. In an ordinary
economy, where incomes drift up slowly and roughly together, that is a
reasonable way to define being poor relative to your neighbours.</p>

<p>Greece's economy, from 2010, was not ordinary. Incomes across the whole
country fell together, hard and fast. And when the median falls, the poverty
line falls with it. A household earning exactly what it earned five years
earlier could find itself reclassified from poor to not poor &mdash; not
because anything in its life had improved, but because the ruler measuring it
had shrunk to match the collapse around it.</p>

<p>So the official income-poverty rate barely moved through the worst years.
Not because Greek households weren't getting poorer &mdash; they were,
dramatically &mdash; but because the yardstick was falling with them, always
re-centring on a poorer and poorer normal.</p>

<p>What happens if you refuse to let the ruler move? Hold the line where it
stood in 2008, adjust it only for inflation, and measured poverty roughly
doubles: from under 20% before the crisis to a peak above 40% in 2014.</p>

{fig('F3')}

<p>A word on where these numbers come from, since this chapter reaches back
further than the rest. From 2010 onward the figures are Eurostat's own,
published and used as they are. For the years before that Eurostat does not
publish this measure, so the earlier values are built from its own components
using a rule we checked against the official series everywhere the two overlap
&mdash; 432 country-years, agreeing almost exactly. Those earlier years are
used for the picture only. Nothing later in this report is tested on them.</p>

{finding('V2-1.1')}

<p>Two cautions, because this chart is easy to over-read. This is a measure of
Greece against its own past, and it contains no other country: it cannot tell
you that Greece's line fell further than anyone else's. And the fixed line is
not the <em>correct</em> line. The relative measure is doing exactly what it
was designed to do &mdash; measuring position &mdash; and the fixed measure
answers a different question about living standards. When a whole country falls
together, those two questions come apart, and that separation is the point.</p>
"""))

CH.append(chapter("wider_net", "The wider net", f"""
<p>Europe already knows income alone is too narrow. Its headline measure of
social exclusion casts a wider net: it counts you if your income is low, or if
you can't afford a list of ordinary things, or if the adults in your household
are barely working. If the puzzle in Chapter {{ch:paradox}} is just that the income measure
is too narrow, the wider one should mostly dissolve it.</p>

{finding('V2-2.1')}

<p>It helps, and it isn't enough. The wider net picks up under a quarter of the
distance. More telling is the direction of travel: its contribution is getting
<em>smaller</em>, from eleven points at the start of the period to seven by the
end. As an explanation of this puzzle it is weakening, not strengthening.</p>

<p>There is also something hidden inside that headline number. It is built from
three separate conditions joined by <em>or</em>: your income is low, or you
can't afford a list of ordinary things, or the adults around you are barely
working. Because they're joined by <em>or</em> and not added up, the headline
can't be taken apart into neat slices &mdash; a household counted for two
reasons is still one household.</p>

<p>What that hides is that the three don't move together. One of them can be
falling while another rises, and the combined rate sits calmly in the middle
looking like nothing much is happening. Nor do they apply equally to everyone:
the work-intensity condition is defined over working-age adults, so a household
of pensioners can't trigger it at all. Comparing the headline across age groups
is therefore partly comparing which conditions were even eligible to fire.</p>

<p>This is a recurring shape in the whole investigation. The averages are calm.
What's underneath them isn't.</p>
"""))

CH.append(chapter("generations", "The average hid a reversal", f"""
<p>National averages are averages of people, and people are not
interchangeable.</p>

<p>Underneath a Greek headline rate that moved gently, the age groups did not
move together at all. The pattern that emerges when you split them apart is the
kind of thing an average is very good at concealing: some groups improving
while others did not, and the combined figure sitting placidly between
them.</p>

{fig('F5')}

<p>This matters for the question this report is asking. A country where
hardship has become concentrated in particular groups can look, on the
headline, exactly like a country where it eased for everybody a little. The
household answering the survey question is not answering about the national
average. It is answering about itself.</p>

<p>It also complicates the recovery story from the previous chapters. Aggregate
improvement in unemployment and consumption is real. Whether it reached the
same people who absorbed the worst of the crisis is a different question, and
the age split is the closest this data comes to an answer: not evenly.</p>

<p>We stop short of the stronger version of that claim. Showing that groups
moved differently is not the same as showing which group's experience drives
the national answer to the survey question, and this study cannot do the
second.</p>
"""))

CH.append(chapter("real", "Is any of it real?", f"""
<p>This is the chapter where the whole thing could have collapsed.</p>

<p>If Greek households say they are struggling while nothing in their material
circumstances corresponds to it, then this is a story about how people answer
questions, not about poverty, and everything after this point measures a
phantom. So it has to be dealt with before anything else.</p>

<p>The test is whether the reported difficulty moves together with things that
name events rather than feelings: falling behind on bills, being unable to
handle an unexpected expense, being unable to heat the home, going without
several basic things at once.</p>

{finding('V2-3.1')}

<p>They move together, and they do so <em>within</em> countries, which is the
harder test &mdash; it can't be satisfied by rich countries simply differing
from poor ones.</p>

<p>Now the honest part, and it matters more than the result. Every one of those
items comes from the same survey, asked of the same household, in the same
sitting, as the question about making ends meet. A household in a grim mood
about its finances will answer the whole set grimly, and that alone would
produce numbers like these. This is one instrument agreeing with itself. It is
real evidence and it is not independent confirmation, and the difference
between those two things runs through the rest of this report.</p>

<p>It isn't even uniform. Falling behind on bills &mdash; the item you would
expect to be the hardest, most factual anchor &mdash; tracks the reported
difficulty far more weakly within Greece than the others do. Arrears require
having credit and bills to fall behind on. A household that lost access to
credit years ago, or never had it, can be in serious trouble without ever
registering.</p>

{finding('V2-3.2')}

<p>That word &mdash; absorb &mdash; is doing careful work, and it is not a
synonym for explain. Put those deprivation items into the model and most of
Greece's unexplained excess stops being statistically visible. That tells you
the two things share a great deal of information. It does not tell you one
causes the other, because both are measured by the same survey of the same
households on the same day. Chapter {{ch:flip}} shows how much rides on that.</p>
"""))


# ===========================================================================
#  CHAPTERS 5-9
# ===========================================================================
CH.append(chapter("money", "What money actually buys", f"""
<p>Income is not the same as what a household can get for it. Two countries can
report similar wages and offer very different lives, depending on what things
cost.</p>

<p>The measure that captures this counts what people in a country actually
consume, adjusted for what things cost there &mdash; not what they nominally
earn. It is the closest thing in official statistics to asking what a household
can actually get.</p>

<p>On that measure Greece has risen substantially over the decade, from roughly
14,800 to 21,300 in the units used for these comparisons. That is a real
improvement and it is worth saying clearly, because a report about hardship can
give the impression that nothing improved. A great deal improved.</p>

<p>And the measure still predicts reported hardship after income poverty has
been accounted for &mdash; meaning it carries information the official poverty
rate does not.</p>

{finding('V2-4.C1')}

<p>Read that carefully: it says the measure carries information the official
poverty rate does not. It does not say that raising it would lower hardship by
a calculable amount. Nothing in this study can establish that. What it
establishes is that a country's real consuming power tells you something about
how its households answer the question, over and above where they sit in their
own income distribution.</p>
"""))

CH.append(chapter("jobless", "When joblessness stops being a spell", f"""
<p>The headline unemployment rate tells you how many people are out of work
this month. It tells you nothing about whether those are the same people as
last year.</p>

<p>That distinction is not a technicality. A labour market where people lose
jobs and find new ones within months is a different place from one where the
same people have been out of work for years, even if both report the same
percentage. The first is churn. The second is a condition.</p>

<p>Long-term unemployment &mdash; out of work for twelve months or more &mdash;
measures the second thing, and Greece's figure was extraordinary. In 2015 it
stood at 16.4% of the labour force. At the worst of it, roughly three out of
every four unemployed Greeks had been out of work for over a year. Not between
jobs. Out.</p>

<p>By 2024 it had fallen to 5.4%. That is substantial, real progress, and it is
still among the highest in Europe &mdash; most of the EU sits under 2%.</p>

<p>The reason this matters for a question about making ends meet is that time
does something specific to a household. Savings go first, then whatever could
be sold, then the goodwill of relatives, then the ability to absorb any
surprise at all. A month of unemployment is an inconvenience for most
households. Two years is a different category of event, and the household that
comes out the other side is not the household that went in.</p>

{finding('V2-4.C2')}

<p>This is the clearest of the present-day results, and it survives every check
applied to it, including being re-estimated twenty-seven times with a different
country left out each time. Dropping Greece itself does not overturn it &mdash;
which matters, because a finding that only held because of the country the
report is about would be worthless.</p>
"""))

CH.append(chapter("paycheck", "A paycheck that never came back", f"""
<p>Of everything measured here, this is the series that has not recovered.</p>

<p>Greek real wages stood at about 77% of their 2008 level in 2015. In 2024
they stood at about 68%. Not recovering slowly &mdash; not recovering. Greek
wages have now been below their pre-crisis level for fifteen consecutive years,
longer than any country in the EU except Hungary.</p>

<p>What matters for households is not the wage alone but the wage against what
things cost, and that combination also predicts reported hardship beyond income
poverty.</p>

{finding('V2-4.C4')}

<p>A country can score badly here two ways: by being expensive, or by paying
poorly. Greece does both at once, and the household experiencing it does not
much care which half is responsible.</p>

<p>It is worth sitting with what fifteen years means. A worker who started a
job in 2008 at the going rate has spent an entire career &mdash; the whole of
their thirties, say &mdash; without the pay level they began with ever
returning. Not a bad year. Not a bad stretch. The entire span in which most
people expect their earnings to rise.</p>

<p>Set this beside Chapter {{ch:jobless}} and you have the shape of the Greek recovery. The
unemployment rate came back. The paycheck did not. A household looking at a
labour market that has genuinely improved is also looking at a wage that has
been below where it started for a decade and a half.</p>
"""))

CH.append(chapter("unsettled", "The things we couldn't settle", f"""
<p>Nine present-day measures were tested. Three worked. This chapter is about
the other six, and it is more important than it sounds.</p>

<p>The tempting thing to write is that the six were ruled out. For most of
them, that would be false.</p>

{finding('V2-4.X')}

<p>A test that finds nothing tells you something only if it was capable of
finding something. With twenty-seven countries and about a decade of data, this
study can detect large effects and not small ones. For most of the six, the
smallest effect it could reliably have caught is bigger than any effect worth
caring about. So the study is <em>silent</em> about them. Not negative &mdash;
silent. Reporting that as "no evidence of an effect" would be one of the
easiest and most common ways to mislead with a true sentence.</p>

<p>A few are genuinely different, and for those the exclusion is real &mdash;
though it holds at a stated size rather than in general.</p>

{finding('L-4')}

<p>Inflation is the clearest case. Two inflation measures can be ruled out at
the size this study could detect. That is not the same as showing that rising
prices don't matter to Greek households, and it should not be read that
way.</p>

<p>One more thing belongs here, because it shows why the checks were worth
having. Two measures passed the standard statistical test comfortably and then
failed a stricter one designed for studies with few countries. Had the protocol
stopped at the usual step, this report would contain two more findings than it
does.</p>
"""))

CH.append(chapter("duration", "How long it went on", f"""
<p>Two countries can look identical today and have arrived by different roads.
One has had high long-term unemployment for a year. The other has had it for
twelve. The intuition that these are not the same situation is strong, and it
is the intuition behind almost every account of the Greek crisis.</p>

<p>Intuition isn't evidence, and this is the chapter where an appealing story
is easiest to oversell. Three drafts of this report oversold it before the
wording below was settled.</p>

<p>For each measure that worked in the earlier chapters, we built a matching
one that counts not the level today but the total burden a country has absorbed
since before the crisis: how much excess unemployment it accumulated, how many
consecutive years its wages stayed below 2008, how much its housing costs
deteriorated.</p>

{fig('F11')}

<p>Greece has absorbed a great deal on these measures. On one of the three it
is not the highest &mdash; Hungary has a longer run of depressed wages &mdash;
and the chart shows every country rather than Greece alone, so that this is
visible rather than buried.</p>

<p>Showing that Greece accumulated a lot is description. The real test is
harder: does the history predict hardship <em>after</em> you already know the
present-day situation? If you know today's unemployment rate, does the past
decade of it still add anything?</p>

<p>For three measures, it does.</p>

{finding('V2-5.C2')}
{finding('V2-5.C3')}
{finding('V2-5.C6')}

<p>The third of those is borderline and is labelled so rather than rounded up.
The second holds only for one specific way of counting, and other reasonable
ways of counting the same idea point the same direction without meeting the
standard &mdash; they are not counted as support.</p>

<p>And the pattern is not universal, which is itself informative.</p>

{finding('V2-5.X')}

<p>For the cost-of-living measure it runs the other way: today's number
survives and the accumulated one doesn't resolve. If history mattered as a
general rule, that reversal shouldn't happen. It suggests these results are
specific to work, wages and housing rather than reflecting some broad law that
the past always counts.</p>

<p>One measure couldn't be tested at all, and is reported rather than quietly
dropped.</p>

{finding('V2-5.Z')}

<p>The data for it simply starts too late. Moving the starting line to make it
testable would have turned it into a measure of something else &mdash; one that
couldn't see the crisis it was built to see. The starting line stayed where it
was.</p>

{finding('L-3')}

<p>And one result passed every test in this chapter without being counted,
because the measure it was paired with hadn't been supported in the earlier
round, and a rule set in advance stops this stage from promoting anything its
predecessor didn't establish. On the face of the numbers it looks as convincing
as the three that count. The rule held anyway, which is the only condition
under which having rules means anything.</p>
"""))


# ===========================================================================
#  CHAPTERS 10-16
# ===========================================================================
CH.append(chapter("between_within", "Between countries, not inside one", f"""
<p>Everything in the last chapter is a statement about how countries differ
from each other. It is very tempting, and it is wrong, to turn it into a
statement about how Greece changed over time.</p>

{finding('V2-5.Y')}

<p>Here is the distinction, because it is the single easiest thing in this
report to get wrong. "Countries that accumulated more hardship report more
difficulty" is a claim about a group photograph. "As Greece accumulated more
hardship, Greek households reported more difficulty" is a claim about a film.
This study took the photograph. It did not shoot the film.</p>

<p>We tested for the film anyway, three separate ways, and found nothing that
supports it. And here the caution runs in the other direction: finding nothing
is not the same as showing there is nothing. Those tests throw away all the
comparison between countries and rely only on movement within each one, which
leaves far less to work with. They are too imprecise to settle the question
either way.</p>

<p>So: the honest sentence is that this design cannot support a claim about
Greece changing over time. Not that Greece didn't change.</p>

<p>This is an unsatisfying place to leave a chapter and it is where the
evidence stops. The reason to say it this precisely, rather than letting the
group photograph quietly stand in for the film, is that the film is the version
everybody wants &mdash; it is the version that sounds like an explanation. It
is also the version this study did not produce.</p>
"""))

CH.append(chapter("flip", "The result that flips", f"""
<p>Most reports include a section showing their findings hold up. This one
includes a section showing that one of them doesn't, and that is a result
rather than an embarrassment.</p>

<p>Remember from Chapter {{ch:real}} that the deprivation items &mdash; can't pay bills,
can't heat the home &mdash; absorbed most of Greece's unexplained excess. And
remember that those items come from the same survey as the thing being
explained.</p>

<p>Whether to let a measure like that into the model is a real choice with a
real case on both sides. For: it is a meaningful, officially published measure
of hardship, and refusing to use variables because they are well measured is
not a principle anyone actually holds. Against: when the question and the
answer come from the same person in the same interview, some of the agreement
between them is the interview rather than the world.</p>

<p>Both positions are defensible. So we ran both.</p>

{finding('V2-6.1')}

<p>Greece moves from the third-worst country in Europe on unexplained hardship
to the twenty-fifth &mdash; from a stark positive outlier to a stark negative
one &mdash; on exactly the same rows of data, with one variable added or
removed. Third to twenty-fifth, out of twenty-seven, from a single judgement
call.</p>

<p>That is not a wobble. It is a reversal, and there is no honest way to pick
between the two. We can't average them. We can't choose the one that looks more
plausible, because choosing the model that gives the answer you expected is how
this kind of check gets rendered meaningless. What can be said is this: how
much of Greece's anomaly gets absorbed depends on a judgement call the data
cannot settle, and any conclusion resting on that absorption inherits the
uncertainty.</p>

<p>Which is why the conclusion of this report does not rest on it.</p>
"""))

CH.append(chapter("what_it_wasnt", "What it wasn't", f"""
<p>Two analyses were planned in advance, meant to carry real weight, and
neither worked. They are here because a report that shows only its successes
gives a false impression of how much was tried.</p>

<p>The first was the one that would have made the best chart in this report.
The idea is elegant: build an artificial Greece out of a weighted blend of
other countries, one that tracks the real Greece closely before 2008, then
watch the two diverge afterwards. The gap between them is the crisis.</p>

<p>It failed. The blend collapsed onto essentially two countries &mdash;
Hungary and Bulgaria &mdash; which is not a stand-in for Greece, and the design
missed four of the six conditions set for it in advance.</p>

{finding('L-1')}

<p>The chart it would have produced is not in this report, and that is
deliberate. A dramatic picture resting on a counterfactual that thin would
convince people of something the evidence cannot support. Being convincing and
being right are different properties, and the first is most dangerous when the
second is missing.</p>

<p>The second was a measure of how many different kinds of disadvantage a
country shows at once. Adding it made Greece's position worse rather than
better, and its direction flipped once other things were held constant. That
flip is left unexplained here on purpose: inventing a story for a strange result
in an analysis that has already failed is exactly how failed analyses come back
from the dead.</p>

{finding('L-2')}
"""))

CH.append(chapter("how_greeks_talk", "Is this just how Greeks talk?", f"""
<p>There is a simpler explanation for everything so far, and it deserves to be
taken seriously rather than waved away: maybe Greeks are just gloomier
answerers.</p>

<p>Chapter {{ch:real}} got partway to an answer &mdash; the reported difficulty does
track real material trouble &mdash; but all of that evidence came from inside
one survey, so it can't settle this on its own.</p>

<p>A better test looks across <em>different</em> subjects. A general tendency
to answer darkly should drag everything down about equally. A pattern that is
extreme on money and milder elsewhere points at circumstances instead.</p>

{fig('F15')}

{finding('V2-7.1')}

<p>Each row places every EU country on one indicator, with Greece marked. The
pattern is specific to money, but it is a difference of degree, not of
kind. Greece is worst in Europe on the financial questions and close to worst
on general life satisfaction. That is not the profile of a country that is
desperate about money and otherwise content, and an earlier version of this
report described it that way and was wrong.</p>

<p>One more thing has to be held apart here, because getting it backwards
inverts the finding. Greek life satisfaction <em>rose</em> over this period,
from 6.2 to 6.9. Greece's <em>rank</em> got worse anyway, because other
countries improved faster. A falling rank on a rising number is not a country
getting unhappier.</p>

{context('CTX-1', '''
<p>Greece's money questions sit at the far edge of the European range while its
general-wellbeing question sits closer to it. That difference of degree is what
the comparison shows, and it is description rather than a test.</p>''')}
"""))

CH.append(chapter("before", "Before the crisis", f"""
<p>There is a hole in the middle of the last chapter. The European survey used
throughout this report only starts asking about life satisfaction in 2013
&mdash; at the bottom of the Greek crisis. So it cannot tell you whether Greece
was already unusual <em>before</em> 2008, which is exactly what you would want
to know.</p>

<p>A different survey can, and what follows is kept deliberately separate: a
different instrument, shown on its own, never joined to the other series.</p>

{block('ess-table')}

<p>Three things happen in order. Greece was <em>already</em> about 0.8 points
below the middle of this group before the crisis. Its level then fell sharply,
to 5.64 by 2010/11. And by 2023/24 it had climbed back to 6.42, roughly where
it started.</p>

<p>Its position, though, did not climb back. The gap to the middle of the group
is wider now than before the crisis, and Greece has been the lowest of these
twelve countries since 2010/11 &mdash; the two countries that used to sit below
it have both passed it.</p>

<p>This cuts against a tidy conclusion, which is why it is here. A low Greek
starting point pre-dates the crisis, so the crisis cannot be the whole story,
and a long-standing pattern of lower reported wellbeing remains entirely
plausible. Gloominess as a national trait can't be dismissed on this evidence.
It also can't be established by it.</p>

{context('CTX-7', '''
<p>Across six rounds of a separate European survey, holding the same twelve
countries fixed each time, Greece's level fell and then recovered while its
position relative to the others did not.</p>
<p>This is descriptive corroboration and not a test: it shows a pattern that
sits alongside the previous chapter without confirming or refuting it.</p>''')}

<p>A caution about where these numbers come from: they are reconstructed from
percentages the survey publishes publicly, not from the underlying responses,
which sit behind a login. They are approximate, they carry no margin of error,
and nothing is tested on them. There is also a decade with no Greek survey
round at all, right through the deepest part of the adjustment.</p>
"""))

CH.append(chapter("untested", "What we didn't test", f"""
<p>Several things that come up in every conversation about the Greek crisis are
not established in this report. Leaving them out silently would be misleading.
Discussing them as though they were findings would be worse.</p>

<p>Some of them were looked at. Migration was tested here directly. The
cross-country comparison in Chapter {{ch:how_greeks_talk}} and the survey in
Chapter {{ch:before}} are both
analyses done for this report. What none of them can do is carry a conclusion,
and each one below says what it permits and what it doesn't.</p>

{context('CTX-2', '''
<p>Trust in institutions is low in Greece, and there is a plausible route by
which it could matter: a household that doesn't expect help to arrive may
experience the same circumstances as more frightening. Nothing here tested
that.</p>''')}

{context('CTX-3', '''
<p>The bailout programmes from 2010 reshaped incomes, job protections, pensions
and public services at once and in a hurry. They are the backdrop to every
accumulated measure in Chapter {{ch:duration}}.</p>''')}

{context('CTX-4', '''
<p>Large numbers of working-age Greeks left during the crisis, and some have
returned. This cuts both ways: plausibly a consequence of a broken labour
market, and plausibly part of why the people who stayed look the way they
do.</p>''')}

{context('CTX-5', '''
<p>Published research establishes that Greece's system of indirect taxes became
markedly harder on lower-income households across the crisis. If a household's
position worsened through tax in a way income-based poverty measures capture
badly, that would be one route to the kind of gap this report describes.</p>''')}
"""))

CH.append(chapter("landing", "Landing", f"""
<p>Greek households report struggling at a rate far above what the official
poverty figure predicts, and they have done so consistently for a decade. Three
bodies of evidence make part of that distance easier to understand.</p>

<p>The official measures are narrower than the experience they get used to
summarise. The wider net closes about a fifth of the gap and is closing less
each year, and the income line itself fell along with the Greek economy, which
a relative measure cannot help doing.</p>

<p>What households report corresponds to real material trouble &mdash; bills,
heating, unexpected expenses &mdash; though that agreement comes from inside a
single survey rather than from an independent source.</p>

<p>And both the present and the past carry information: what a country can
actually afford, how much long-term unemployment it carries, how its wages
stand against its prices, together with the accumulated weight of unemployment,
of wages that never recovered, and of housing costs that worsened.</p>

<p>What the evidence does not support is just as much part of the answer.
Nothing here shows what causes what. Nothing here shows Greece changing over
time; that question was asked and the answer was too imprecise to settle. Most
of the measures that didn't work are unresolved rather than ruled out. One
central result flips depending on a judgement call the data can't settle. And a
general tendency to answer darkly cannot be excluded &mdash; the survey
reaching back before the crisis suggests Greece started lower.</p>

<p>And most of the gap is still unexplained. Of the 52.6 points, what is
accounted for here is a minority. The rest is not attributed to anything,
because we could not establish where it goes.</p>

{context('CTX-6', '''
<p>What runs through all of this is that no single official number captures
what Greek households are reporting. Each one misses something different, and
the ones that catch what the others miss are not the headline.</p>''')}

<p>That is a recommendation about how poverty gets reported, and it follows
from what the single measures were seen to miss. It is not itself a finding,
and it is the last thing in this report rather than the first for that
reason.</p>
"""))


# ===========================================================================
#  PAGE
# ===========================================================================
BASE = ce.base_style((OUT / "report.html").read_text())

NARR_CSS = """
body{max-width:40rem;margin:0 auto;padding:0 1.3rem 6rem;
  font:1.09rem/1.78 ui-serif,Georgia,'Times New Roman',serif}
.masthead{padding:3.6rem 0 1.4rem;margin-bottom:1rem}
.masthead h1{font-size:clamp(2rem,6vw,2.9rem);line-height:1.1;margin:0 0 1rem;
  letter-spacing:-.02em;text-wrap:balance}
.standfirst{font-size:1.14rem;line-height:1.6;color:var(--text-secondary);margin:0}
.ch{margin:4rem 0 0}
.chnum{font:600 .7rem/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.14em;
  text-transform:uppercase;color:var(--text-secondary);margin:0 0 .5rem}
.ch h2{font-size:clamp(1.5rem,4vw,1.95rem);margin:0 0 1.2rem;
  letter-spacing:-.015em;text-wrap:balance}
.ch p{margin:0 0 1.05rem}
.finding{border-left:3px solid var(--series-gr);padding:.1rem 0 .1rem 1.1rem;
  margin:1.6rem 0}
.finding p{margin:0 0 .5rem;font-size:1.06rem}
.limits{font:.92rem/1.65 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin:0}
.ctx{border:1px dashed var(--border);border-radius:6px;padding:1rem 1.2rem;
  margin:1.8rem 0}
.ctx-status{font:600 .68rem/1 ui-sans-serif,system-ui,sans-serif;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text-secondary);
  margin:0 0 .45rem}
.ctx h4{margin:0 0 .55rem;font-size:1.02rem}
.ctx p{font-size:.98rem;margin:0 0 .7rem}
.ctx .permitted,.ctx .limitation,.ctx .src{
  font:.9rem/1.6 ui-sans-serif,system-ui,sans-serif;margin:.5rem 0 0}
.ctx .limitation{color:var(--text-secondary)}
.ctx .src{color:var(--text-secondary);font-size:.82rem;padding-top:.5rem;
  border-top:1px solid var(--border)}
@media (max-width:34rem){body{font-size:1.04rem}}
"""

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Greek Poverty Paradox &mdash; a companion</title>{BASE}
<style>{ce.CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu)}}
{NARR_CSS}</style></head><body>
<header class="masthead">
<h1>The Greek Poverty Paradox</h1>
<p class="standfirst">Two official numbers say very different things about how
Greek households are doing. This is an attempt to find out which is closer to
the truth, and how much of the difference between them anyone can actually
account for.</p>
</header>
{resolve_refs(''.join(CH))}
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
print(f"  chapters {len(CH)}  claims {len(required)}  context {len(ctx)}  figures {len(_used)}")
