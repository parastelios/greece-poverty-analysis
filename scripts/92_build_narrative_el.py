"""Assemble the Greek edition of the narrative companion.

A hybrid translation, not a parallel build: every figure is lifted from the
exact same batch pages the English narrative (91_build_narrative.py) uses,
byte-for-byte, so the charts themselves -- axes, legends, tab labels, data
tables -- stay in English. Only the surrounding text (captions, section
prose, findings, context boxes, the two summary tables, the table of
contents, the masthead) is Greek. That split was a deliberate choice, not a
limitation discovered along the way: rebuilding every chart with Greek
labelling would mean a second chart-rendering pipeline, not a translation.

Findings and context here are hand-translated from the frozen English wording
in e_final_claims.csv / context_register.csv, not machine-generated from it --
the frozen wording is English by construction (it is the acceptance-checked
canonical text for the OTHER three documents), so a Greek reading of it has to
be authored, the same way the earlier compact finding boxes in the English
narrative are authored rather than templated. The data-claim-id and
data-context-id attributes are kept identical to the English document, so the
same ids can be cross-checked against the same registries.
"""
import hashlib
import html
import json
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce
import el_figure_strings as ELF

ROOT = Path(__file__).resolve().parents[1]
OUT, PROC = ROOT / "output", ROOT / "data" / "processed"

claims = pd.read_csv(PROC / "e_final_claims.csv").set_index("id")
ctx = pd.read_csv(PROC / "context_register.csv").set_index("id")

FIG_SOURCE = {}
for n in (1, 2, 3, 4):
    page = (OUT / "build" / f"batch{n}.html").read_text()
    for m in re.finditer(r'<figure class="figure" id="(F\d+)">.*?</figure>', page, re.S):
        FIG_SOURCE[m.group(1)] = m.group(0)

# Same eight-plus-two figure selection as the English narrative -- F1, F3,
# F5, F8, F21, F7, F10, F11, F13A (a lifted view of F13), F14. Kept in one
# place and checked below so the Greek edition can never silently drift from
# what the English edition actually argues.
_FROZEN = ["F1", "F3", "F5", "F8", "F21", "F7", "F10", "F11", "F13A", "F14"]

_used = []


def fig(fid, caption=None):
    """Place a built figure. Numbering is resolved later, left to right, by
    resolve_fig_nums() -- identical mechanism to the English narrative.

    CAPTION replaces the figure's caption IN THIS DOCUMENT ONLY, in Greek.
    Everything else inside the figure -- axes, legend, tab labels, the
    fallback data table -- is the untouched English chart, per the "hybrid"
    brief: charts stay in English, the prose around them does not.
    """
    if fid in _used:
        raise SystemExit(f"{fid} placed twice")
    _used.append(fid)
    html_ = FIG_SOURCE[fid]
    if caption is not None:
        html_ = re.sub(r"<figcaption>.*?</figcaption>",
                        f"<figcaption>{caption}</figcaption>", html_, count=1, flags=re.S)
    html_ = html_.replace(
        "<figcaption>", f'<figcaption><span class="fignum">Γράφημα {{fig:{fid}}}</span> ', 1)
    html_ = re.sub(
        r'(<p class="fig-caveat">.*?</p>)',
        r'<details class="fig-methods"><summary>Μέθοδος και περιορισμοί</summary>\1</details>',
        html_, count=1, flags=re.S)
    return localize_figure(fid, html_)


def subfig(fid, parent_fid, view_index, caption, question):
    """One view of a multi-view report figure, lifted as its own figure --
    same mechanism as the English narrative's subfig(), Greek caption/question."""
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
    chart_type = chart_types[view_index]
    # The shell is written in Greek here; the payload and the table are lifted
    # from the English parent figure, so the whole thing still goes through the
    # localizer below.
    shell = (f'<figure class="figure" id="{fid}">'
             f'<figcaption><span class="fignum">Γράφημα {{fig:{fid}}}</span> {caption}</figcaption>'
             f'<div class="fig-meta"><span class="badge">προσχεδιασμένη επιβεβαιωτική ανάλυση</span>'
             f'<span class="fig-q">{question}</span></div>'
             f'<div class="chart-live" data-chart="{chart_type}" tabindex="0" '
             f'data-checksum="{checksum}" aria-describedby="{fid}-fb">'
             f'<script type="application/json">{payload}</script></div>'
             f'<details class="fallback" id="{fid}-fb"><summary>Δείτε τους αριθμούς '
             f'<a href="statistical_appendix.html#{parent_fid}">Αυτό το γράφημα στο παράρτημα</a>, '
             f'με τη λεπτομέρεια που παραλείπει η αναφορά (στα αγγλικά).</summary>{table}</details>'
             f'</figure>')
    return localize_figure(fid, shell)


def finding_el(cid, wording_el, caveats_el=None,
                lead="Τι δείχνουν τα στοιχεία.",
                caveat_lead="Τι δεν μπορούμε να συμπεράνουμε."):
    """A hand-translated reading of claims.loc[cid].canonical_wording. The
    English wording is frozen and acceptance-checked against the other three
    documents; this is an authored Greek rendering of the same claim, not a
    template pulling the CSV text, which is English by construction."""
    if cid not in claims.index:
        raise SystemExit(f"finding_el: unknown claim id {cid}")
    cav = (f'<p class="limits"><em>{caveat_lead}</em> '
           f"{caveats_el}</p>" if caveats_el else "")
    return (f'<div class="finding" data-claim-id="{cid}">'
            f'<p><em>{lead}</em> {wording_el}</p>{cav}</div>')


def gr_num(text):
    """English number formatting to Greek: decimal comma, thousands full stop.

    The source CSVs are written for the English documents, so a cell arrives
    as "16.4% -> 5.4%" or "14,770 -> 21,310 PPS". Swapping the two separators
    has to happen in one pass through a placeholder, or the comma inserted for
    the decimal point is immediately re-read as a thousands separator.
    """
    return (str(text).replace(",", "\x00").replace(".", ",")
            .replace("\x00", ".").replace("PPS", "ΜΑΔ"))


# ---------------------------------------------------------------------------
#  FIGURE LOCALIZATION
#
#  The figures are lifted from the English batch pages, so everything a reader
#  sees inside them arrives in English: tab names, axes, legends, series and
#  country names, the fallback table, the accessibility description and the
#  methods note. This translates the presentation layer and NOTHING else. Data
#  values, series order, figure ids, claim anchors and the chart tone names
#  (chart-gr and friends, which the JS reads as CSS class fragments) are left
#  exactly as they are.
#
#  Every reader-facing string is looked up in el_figure_strings. A miss is
#  collected and fails the build at the end, so a renamed English label cannot
#  reach a Greek reader untranslated.
# ---------------------------------------------------------------------------
_fig_missing = set()
# Anything that is only digits and punctuation is not a translation problem,
# it is a number: send it through the Greek formatter instead of the lookup.
_NUMERIC_ONLY = re.compile(r"^[\d\s.,%+\-–—:=/()]*$")


_GREEK = re.compile(r"[Α-Ωα-ωΆ-Ώά-ώΐΰ]")


def _tr(s, where):
    t = s.strip()
    if not t or t in ELF.KEEP_AS_IS:
        return s
    # subfig() writes its own shell in Greek; those strings are already done.
    if _GREEK.search(t):
        return s
    if _NUMERIC_ONLY.match(t):
        return gr_num(s)
    if t in ELF.STRINGS:
        return s.replace(t, ELF.STRINGS[t], 1)
    _fig_missing.add(f"{where}  |  {t[:100]}")
    return s


# Keys whose values are rendering instructions, not text: CSS tone fragments,
# line weights, dash styles, chart kinds. Translating any of them would stop
# the chart drawing rather than change a word.
_NOT_TEXT = {"tone", "toneA", "toneB", "weight", "style", "kind", "colour",
             "color", "dash", "class", "id", "href", "series-tone", "place"}


def _gr_numbers_in_text(s):
    """Greek separators, applied only between digits.

    Blunt replacement is unsafe here: tooltip HTML carries things like
    style='opacity:.6', where swapping the dot breaks the attribute.
    """
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "\x00", s)
    s = re.sub(r"(?<=\d)\.(?=\d)", ",", s)
    return s.replace("\x00", ".")


def _tr_detail(text, where):
    """Tooltip text, translated as parts: chart_engine composes these from a
    template, so the sentences are patterns with numbers in them."""
    out = text
    for pat, rep in ELF.DETAIL_RULES:
        out = re.sub(pat, rep, out)
    stripped = out.strip()
    if stripped in ELF.STRINGS:
        out = out.replace(stripped, ELF.STRINGS[stripped], 1)
    out = _gr_numbers_in_text(out)
    # &rarr; and friends are entities, not words the reader sees in Latin.
    probe = re.sub(r"&\w+;", " ", out)
    leftover = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", probe)
                if w not in ELF.DETAIL_ALLOWED]
    if leftover:
        _fig_missing.add(f"{where}  |  {stripped[:100]}")
    return out


def _localize_html_text(frag, where):
    """Translate the text nodes of a small HTML fragment, leaving tags alone."""
    parts = re.split(r"(<[^>]+>)", frag)
    return "".join(p if p.startswith("<") else _tr_detail(p, where)
                   for p in parts)


def _localize_payload(node, fid, key=""):
    """Walk the whole payload. Every string is either translated, recognised
    as a number, protected as a rendering instruction, or reported missing --
    so a field nobody thought about cannot quietly stay English."""
    if isinstance(node, dict):
        return {k: (v if k in _NOT_TEXT else _localize_payload(v, fid, k))
                for k, v in node.items()}
    if isinstance(node, list):
        return [_localize_payload(v, fid, key) for v in node]
    if not isinstance(node, str) or not node.strip():
        return node
    if key in ("detail", "legendExtra"):
        return _localize_html_text(node, f"{fid}.{key}")
    if key == "corner":
        return gr_num(node)
    return _tr(node, f"{fid}.{key}")


def _table_checksum(cols, rows):
    """chart_engine.Series.checksum(), recomputed from rendered table text.

    Verified against the untranslated tables before anything is translated
    (see the assertion in _localize_tables), so this is a reproduction of the
    original hash rather than a new convention invented here.
    """
    blob = json.dumps({"cols": cols, "rows": rows}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _cells(fragment, tag):
    return re.findall(rf"<{tag}(?=[\s>])[^>]*>(.*?)</{tag}>", fragment, re.S)


def _read_table(tbl):
    head = re.search(r"<thead>.*?<tr>(.*?)</tr>.*?</thead>", tbl, re.S).group(1)
    cols = [html.unescape(re.sub("<[^>]+>", "", c)) for c in _cells(head, "th")]
    body = re.search(r"<tbody>(.*?)</tbody>", tbl, re.S).group(1)
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        cs = [html.unescape(re.sub("<[^>]+>", "", c)) for c in _cells(tr, "td")]
        rows.append(["" if c == "—" else c for c in cs])
    return cols, rows


def _localize_tables(fid, fig_html):
    """Translate every fallback table, then recompute its checksum.

    The checksum covers the column headers, the row labels and the formatted
    values, so translating a label or a decimal separator legitimately changes
    it. Recomputing keeps the guarantee it exists for -- that the chart and its
    table came from the same data -- instead of leaving a stale hash that
    silently no longer matches. The old value is then swapped for the new one
    across the whole figure, which updates the chart host too, since host and
    table carry the same string.
    """
    swaps = {}
    for m in re.finditer(r'<table data-checksum="([^"]+)"[^>]*>.*?</table>',
                         fig_html, re.S):
        tbl, stored = m.group(0), m.group(1)
        cols, rows = _read_table(tbl)
        if _table_checksum(cols[1:], rows) != stored:
            raise SystemExit(
                f"{fid}: cannot reproduce the original table checksum, so it "
                "cannot honestly be recomputed after translation")
        new_tbl = re.sub(r"(<caption>)(.*?)(</caption>)",
                          lambda x: x.group(1) + _tr(html.unescape(x.group(2)),
                                                     f"{fid}.caption") + x.group(3),
                          tbl, flags=re.S)
        new_tbl = re.sub(r"(<th(?=[\s>])[^>]*>)(.*?)(</th>)",
                          lambda x: x.group(1) + _tr(html.unescape(x.group(2)),
                                                     f"{fid}.header") + x.group(3),
                          new_tbl, flags=re.S)
        new_tbl = re.sub(r"(<td[^>]*>)(.*?)(</td>)",
                          lambda x: x.group(1) + _tr(html.unescape(x.group(2)),
                                                     f"{fid}.cell") + x.group(3),
                          new_tbl, flags=re.S)
        new_cols, new_rows = _read_table(new_tbl)
        swaps[stored] = _table_checksum(new_cols[1:], new_rows)
        fig_html = fig_html.replace(tbl, new_tbl)
    for old, new in swaps.items():
        fig_html = fig_html.replace(old, new)
    return fig_html


def localize_figure(fid, fig_html):
    # tab names, carried on the payload script tag
    fig_html = re.sub(
        r'data-label="([^"]*)"',
        lambda m: f'data-label="{html.escape(_tr(html.unescape(m.group(1)), f"{fid}.tab"))}"',
        fig_html)
    # chart payloads
    def _payload(m):
        d = json.loads(m.group(2).replace("<\\/", "</"))
        data = json.dumps(_localize_payload(d, fid), ensure_ascii=False).replace("</", "<\\/")
        return f"{m.group(1)}{data}</script>"
    fig_html = re.sub(r'(<script type="application/json"[^>]*>)(.*?)</script>',
                       _payload, fig_html, flags=re.S)
    # the lede sentence a few figures print above their fallback table
    fig_html = re.sub(
        r'(<p class="fig-lede">)(.*?)(</p>)',
        lambda m: m.group(1) + _localize_html_text(m.group(2), f"{fid}.lede") + m.group(3),
        fig_html, flags=re.S)
    # the question and the evidence-tier badge
    fig_html = re.sub(
        r'(<span class="fig-q">)(.*?)(</span>)',
        lambda m: m.group(1) + _tr(html.unescape(m.group(2)), f"{fid}.question") + m.group(3),
        fig_html, flags=re.S)
    fig_html = re.sub(
        r'(<span class="badge">)(.*?)(</span>)',
        lambda m: m.group(1) + _tr(html.unescape(m.group(2)), f"{fid}.badge") + m.group(3),
        fig_html, flags=re.S)
    # the methods note, replaced wholesale rather than phrase by phrase
    if fid in ELF.CAVEATS:
        fig_html = re.sub(
            r'<p class="fig-caveat">.*?</p>',
            '<p class="fig-caveat"><strong>Διαβάστε το μαζί με αυτό.</strong> '
            + ELF.CAVEATS[fid] + "</p>",
            fig_html, count=1, flags=re.S)
    # the fallback disclosure's own wording
    fig_html = fig_html.replace(
        "<summary>Show the numbers", "<summary>Δείτε τους αριθμούς")
    fig_html = fig_html.replace(
        "This figure in the appendix</a>, with the detail the report leaves out.",
        "Αυτό το γράφημα στο παράρτημα</a>, με τη λεπτομέρεια που παραλείπει η "
        "αναφορά (στα αγγλικά).")
    return _localize_tables(fid, fig_html)


def recovery_table_el():
    """Greek reading of F7's convergence-share chart -- same six rows, same
    source CSV (e_f7_recovery_table.csv), numeric ranges carried over
    unchanged; only the row labels, headers and plain-language reading are
    translated."""
    d = pd.read_csv(PROC / "e_f7_recovery_table.csv").set_index("measure")
    rows_el = [
        ("Long-term unemployment", "Μακροχρόνια ανεργία",
         "Μεγάλη βελτίωση· η Ελλάδα παρέμεινε πάνω από τη διάμεση τιμή"),
        ("Share below own GDP peak", "Απόσταση από τη δική της κορύφωση ΑΕΠ",
         "Σημαντική αλλά ελλιπής ανάκαμψη"),
        ("Housing-cost overburden", "Υπερβολική επιβάρυνση από το κόστος στέγασης",
         "Βελτιώθηκε, αλλά το εναπομείναν μειονέκτημα ήταν μεγάλο"),
        ("Real wages, 2008 = 100", "Πραγματικοί μισθοί, 2008 = 100",
         "Η Ελλάδα έμεινε ακόμα πιο πίσω"),
        ("Material resources", "Πραγματική κατανάλωση",
         "Η κατανάλωση αυξήθηκε στην Ελλάδα, αλλά πιο αργά από τη διάμεση τιμή"),
        ("Wage-adjusted affordability", "Αγοραστική πίεση (τιμές σε σχέση με τις αμοιβές)",
         "Η αγοραστική πίεση επιδεινώθηκε απότομα σε σχέση με την Ευρώπη"),
    ]
    rows = "".join(
        f"<tr><td>{label_el}</td><td class='num'>{gr_num(d.loc[m, 'greece_range'])}</td>"
        f"<td class='num'>{gr_num(d.loc[m, 'eu_median_range'])}</td>"
        f"<td>{reading_el}</td></tr>"
        for m, label_el, reading_el in rows_el)
    return (f'<div class="mini-table" id="recovery-table"><table><thead><tr>'
            f"<th>Δείκτης</th><th>Ελλάδα, 2015&rarr;2024</th>"
            f"<th>Διάμεση τιμή ΕΕ, 2015&rarr;2024</th><th>Τι συνέβη στην πραγματικότητα</th>"
            f"</tr></thead><tbody>{rows}</tbody></table></div>")


def domain_table_el():
    """Greek reading of the three-domain comparison (e_f15_domains.csv) --
    same table T-DOMAIN in the technical report reads, translated labels."""
    d = pd.read_csv(PROC / "e_f15_domains.csv")
    LABEL_EL = {
        "Reported hardship": "Δηλωμένη δυσκολία",
        "Financial expectations": "Οικονομικές προσδοκίες",
        "Life satisfaction": "Ικανοποίηση από τη ζωή",
    }
    rows = ""
    for r in d.itertuples():
        gr = f"{r.greece:+.1f}" if r.indicator == "Financial expectations" else f"{r.greece:g}{'%' if r.unit == '%' else ''}"
        eu = f"{r.eu_median:+.1f}" if r.indicator == "Financial expectations" else f"{r.eu_median:g}{'%' if r.unit == '%' else ''}"
        ord_ = {1: "1η", 2: "2η", 3: "3η"}.get(r.greece_position_worst_first,
                                                 f"{r.greece_position_worst_first}η")
        rows += (f"<tr><td>{LABEL_EL[r.indicator]}</td><td class='num'>{gr_num(gr)}</td>"
                 f"<td class='num'>{gr_num(eu)}</td>"
                 f"<td class='num'>{ord_} από {r.countries}, με πρώτη τη χειρότερη</td></tr>")
    return (f'<div class="mini-table"><table><thead><tr>'
            f"<th>Δείκτης</th><th>Ελλάδα</th><th>Διάμεση τιμή ΕΕ</th>"
            f"<th>Θέση της Ελλάδας</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")


def context_el(cid, status_el, topic_el, prose_el, permitted_el, forbidden_el,
                source_el, source_url=None, expand=False, collapse=False):
    """Hand-translated reading of a context_register.csv row. The registry
    entry (status/topic/permitted/forbidden/source) is authored in English
    for the other three documents; this authors the same entry's content in
    Greek rather than templating the English text, and keeps the same
    data-context-id so the id can be cross-checked against the registry.
    `collapse` tucks the whole entry -- topic, prose and the permitted/
    limitation/citation trailer -- behind a <summary> naming the status and
    topic, for entries (external corroborating sources) that are worth
    linking to but would otherwise crowd the reading flow. The outer <div
    data-context-id> stays put either way: verify_editions.py's box-parity
    check matches that exact `<div class="X" attr="Y">...</div>` shape."""
    if cid not in ctx.index:
        raise SystemExit(f"context_el: unknown context id {cid}")
    cite = f'<p class="src">{source_el}</p>' if source_el else ""
    body = (f'<p class="permitted"><em>Τι δείχνουν τα στοιχεία.</em> '
            f"{permitted_el}</p>"
            f'<p class="limitation"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> '
            f"{forbidden_el}</p>{cite}")
    if expand:
        body = f'<details class="ctx-detail"><summary>Πλήρης σημείωση</summary>{body}</details>'
    if collapse:
        return (f'<div class="ctx ctx-collapse" data-context-id="{cid}">'
                f'<details><summary><span class="ctx-status">{status_el}</span>'
                f'<span class="ctx-summary-topic">{topic_el}</span></summary>'
                f"{prose_el}{body}</details></div>")
    return (f'<div class="ctx" data-context-id="{cid}">'
            f'<p class="ctx-status">{status_el}</p>'
            f"<h4>{topic_el}</h4>{prose_el}{body}</div>")


CH_KEYS = {}
CH_BY_KEY = {}


def chapter(key, title, body):
    n = len(CH) + 1
    CH_KEYS[key] = n
    rendered = f'<section class="ch" id="ch{n}"><h2>{title}</h2>{body}</section>'
    CH_BY_KEY[key] = rendered
    return rendered


def resolve_refs(doc):
    unknown = set(re.findall(r"\{ch:([a-z_]+)\}", doc)) - set(CH_KEYS)
    if unknown:
        raise SystemExit(f"reference to unknown chapter(s): {sorted(unknown)}")
    for k, n in CH_KEYS.items():
        doc = doc.replace("{ch:" + k + "}", str(n))
    left = re.findall(r"\{ch:[a-z_]*\}", doc)
    if left:
        raise SystemExit(f"unresolved chapter references: {sorted(set(left))}")
    return doc


def resolve_fig_nums(doc):
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
#  ΕΠΤΑ ΕΝΟΤΗΤΕΣ
# ===========================================================================
CH = []

# ---- 1. Ο Δείκτης Φτώχειας Λέει Ένα Πράγμα. Τα Νοικοκυριά Λένε Άλλο. -------
CH.append(chapter("paradox", "Πραγματική δυσκολία ή ελληνική απαισιοδοξία;", f"""
<p>Υπάρχει μια παράξενη ασυμμετρία στη δημόσια συζήτηση για την ελληνική
οικονομία. Όταν πέφτει η ανεργία ή αυξάνεται το ΑΕΠ, οι δείκτες
παρουσιάζονται ως ισχυρές αποδείξεις ανάκαμψης. Όταν όμως δύο στα τρία
νοικοκυριά δηλώνουν ότι δυσκολεύονται να τα βγάλουν πέρα, η συζήτηση συχνά
μετατοπίζεται από τους οικονομικούς δείκτες στις ίδιες τις επιλογές των
νοικοκυριών: στον καφέ, στο έτοιμο φαγητό, στα ταξίδια, στην «υπερβολή» ή
στην υποτιθέμενη ελληνική απαισιοδοξία. Είναι όμως δικαιολογημένη αυτή η
μετατόπιση;</p>

<p>Ο επίσημος <em>δείκτης εισοδηματικής φτώχειας</em> δείχνει πράγματι μια
Ελλάδα σε δυσμενή θέση, αλλά όχι μια ακραία ευρωπαϊκή περίπτωση. Οι
απαντήσεις των νοικοκυριών δίνουν πολύ διαφορετική εικόνα: η <em>δυσκολία να
τα βγάλουν πέρα</em> είναι τόσο εκτεταμένη ώστε η Ελλάδα να ξεχωρίζει καθαρά
από τις περισσότερες χώρες της ΕΕ.</p>

<p>Για να καταλάβουμε αυτή την απόκλιση, πρέπει πρώτα να δούμε τι μετρά
καθένας από τους δύο δείκτες. Και οι δύο προέρχονται από την <em>EU-SILC</em>
(<em>European Union Statistics on Income and Living Conditions</em>), την
ευρωπαϊκή έρευνα για το εισόδημα και τις συνθήκες διαβίωσης των
νοικοκυριών. Η έρευνα πραγματοποιείται κάθε χρόνο σε όλες τις χώρες της ΕΕ,
με κοινή μεθοδολογία ώστε τα αποτελέσματα να είναι συγκρίσιμα. Στην Ελλάδα
διεξάγεται από την ΕΛΣΤΑΤ.</p>

<p>Ο επίσημος δείκτης εισοδηματικής φτώχειας ονομάζεται «κίνδυνος
φτώχειας» ή <em>AROP</em> (<em>At Risk of Poverty</em>). Δεν εξετάζει άμεσα
αν ένα εισόδημα αρκεί για τις καθημερινές ανάγκες. Μετρά πόσο χαμηλά
βρίσκεται σε σχέση με τα εισοδήματα της υπόλοιπης χώρας. Ένα άτομο
θεωρείται ότι βρίσκεται σε κίνδυνο φτώχειας όταν το ισοδύναμο διαθέσιμο
εισόδημα του νοικοκυριού του είναι χαμηλότερο από το 60% του διάμεσου
εθνικού εισοδήματος. «Διάμεσο» είναι το εισόδημα που χωρίζει τον πληθυσμό
στα δύο: οι μισοί βρίσκονται πάνω από αυτό και οι άλλοι μισοί κάτω.</p>

<p>Ένα απλό, υποθετικό παράδειγμα βοηθά. Αν το διάμεσο ισοδύναμο εισόδημα
ήταν 1.000 ευρώ τον μήνα, το όριο του <em>AROP</em> θα ήταν 600 ευρώ. Για
μεγαλύτερα νοικοκυριά το ποσό προσαρμόζεται ανάλογα με το μέγεθος και τη
σύνθεσή τους. Επειδή όμως το διάμεσο εισόδημα υπολογίζεται ξανά κάθε χρόνο,
μετακινείται και το όριο φτώχειας: αν πέσουν συνολικά τα εισοδήματα μιας
χώρας, μπορεί να πέσει μαζί τους και ο πήχης.</p>

<p>Η <em>δηλωμένη οικονομική δυσκολία</em> μετρά κάτι διαφορετικό και πιο
άμεσο. Στην ίδια έρευνα, τα νοικοκυριά ερωτώνται πόσο εύκολα μπορούν να τα
βγάλουν πέρα. Όσα απαντούν «με δυσκολία» ή «με μεγάλη δυσκολία»
καταγράφονται εδώ ως <em>νοικοκυριά που αντιμετωπίζουν οικονομική
δυσκολία</em>. Ο <em>AROP</em>, επομένως, μετρά τη θέση του εισοδήματος σε
σχέση με την υπόλοιπη χώρα. Η δηλωμένη οικονομική δυσκολία καταγράφει αν οι
ίδιοι οι πόροι του νοικοκυριού επαρκούν για την καθημερινότητά του.</p>

<p>Οι δύο δείκτες δεν θα έπρεπε να ταυτίζονται, αλλά θα περιμέναμε να
συνδέονται: όσο αυξάνεται η εισοδηματική φτώχεια, τόσο περισσότερα
νοικοκυριά θα έπρεπε γενικά να δυσκολεύονται να τα βγάλουν πέρα. Στην
Ελλάδα, όμως, η απόσταση μεταξύ τους είναι ασυνήθιστα μεγάλη, και η δημόσια
συζήτηση έχει συχνά ήδη απαντήσει: η ανάκαμψη είναι πραγματική, άρα η
επιμονή των νοικοκυριών είναι θέμα διάθεσης και όχι στοιχείων. Το βασικό
ερώτημα αυτού του κειμένου είναι αν αυτή η απόρριψη στέκει: έχει η δηλωμένη
δυσκολία υλική βάση που ο <em>AROP</em> δεν καταγράφει, ή πρόκειται, σε
σημαντικό βαθμό, για έναν πιο απαισιόδοξο τρόπο απάντησης;</p>

{fig('F1', caption="Η Ελλάδα δηλώνει πολύ περισσότερη δυσκολία από όση προβλέπει η εισοδηματική φτώχεια")}

<p>Η πρώτη καρτέλα του <a class="fig-jump" href="#F1" data-view="0">Γραφήματος
{{fig:F1}}</a> τοποθετεί τους δύο δείκτες δίπλα δίπλα και δείχνει καθαρά το
παράδοξο. Από το 2015, το ποσοστό των ελληνικών νοικοκυριών που δηλώνουν
οικονομική δυσκολία δεν έχει πέσει ποτέ κάτω από τα δύο τρίτα: ξεκινά κοντά
στο 78% και υποχωρεί μόνο σταδιακά. Την ίδια δεκαετία, ο δείκτης
εισοδηματικής φτώχειας κινείται κοντά στο ένα πέμπτο, με μικρές μόνο
μεταβολές. Οι αντίστοιχες ευρωπαϊκές τιμές παραμένουν αισθητά χαμηλότερες σε
όλη την περίοδο. Η διάμεση τιμή της ΕΕ εδώ είναι η τιμή της μεσαίας χώρας
και όχι ένας πληθυσμιακά σταθμισμένος ευρωπαϊκός μέσος όρος.</p>

<p>Δεν πρόκειται, επομένως, για μια κακή χρονιά. Πρόκειται για ένα επίμονο
μοτίβο μιας ολόκληρης δεκαετίας.</p>

<p>Στη <a class="fig-jump" href="#F1" data-view="1">δεύτερη καρτέλα</a>,
«Πού βρίσκονταν οι χώρες το 2024», το ελληνικό χάσμα γίνεται ευρωπαϊκή
εξαίρεση. Κάθε γκρι κουκκίδα αντιστοιχεί σε μία χώρα της ΕΕ. Στον οριζόντιο
άξονα βρίσκεται η εισοδηματική φτώχεια και στον κάθετο η οικονομική
δυσκολία. Η διακεκομμένη γραμμή αποτυπώνει τη σχέση που παρατηρείται στις
υπόλοιπες 26 χώρες.</p>

<p>Η Ελλάδα βρίσκεται πολύ πάνω από αυτήν. Με το επίπεδο εισοδηματικής
φτώχειας που έχει, το ευρωπαϊκό μοτίβο θα αντιστοιχούσε σε περίπου 20% των
νοικοκυριών να δηλώνουν δυσκολία. Στην πραγματικότητα δηλώνει περίπου 67%.
Η απόσταση των 47 ποσοστιαίων μονάδων είναι το χάσμα που προσπαθεί να
κατανοήσει αυτή η ανάλυση.</p>

{finding_el('V2-1.2', "Η οικονομική δυσκολία στην Ελλάδα βρίσκεται κατά μέσο "
            "όρο 52,6 ποσοστιαίες μονάδες πάνω από τη σχετική εισοδηματική "
            "φτώχεια. Η Ελλάδα κατατάσσεται 1η από τις 27 χώρες ως προς τη "
            "δυσκολία, αλλά 7η ως προς τον δείκτη AROP.")}

<details class="fig-methods"><summary>Γιατί το γράφημα ξεκινά από το 2015</summary>
<p class="fig-caveat">Όχι επειδή λείπουν παλαιότερα δεδομένα, αλλά επειδή
από εκεί και μετά το ελληνικό χάσμα αποτυπώνεται καθαρότερα. Ο δείκτης έχει
ανασυγκροτηθεί και για χρόνια πριν από το 2010, ενώ η ανασύνθεση ελέγχθηκε
έναντι των επίσημα δημοσιευμένων δεδομένων της Eurostat στα σημεία όπου οι
δύο επικαλύπτονται. Κανένα από τα βασικά συμπεράσματα που ακολουθούν,
ωστόσο, δεν εξαρτάται από αυτή την ανασυγκρότηση.</p></details>

{finding_el('V2-1.1', "Ο δείκτης δυσκολίας είναι ο επίσημος δείκτης της "
            "Eurostat, ο οποίος επεκτάθηκε αναδρομικά πριν το 2010 με "
            "ανακατασκευασμένες εκτιμήσεις που επαληθεύτηκαν σε σχέση με "
            "αυτόν σε 432 επικαλυπτόμενα έτη-χώρες.",
            "Η προέλευση των στοιχείων πριν το 2010 είναι δική μας "
            "κατασκευή, όχι της Eurostat.",
            lead="Από πού προέρχεται ο δείκτης.",
            caveat_lead="Τι πρέπει να προσέξουμε.")}

<p>Οι δύο αριθμοί δεν είναι αντίπαλες απόψεις. Προέρχονται από το ίδιο
ευρωπαϊκό σύστημα και από έρευνες στα ίδια νοικοκυριά, αλλά απαντούν σε
διαφορετικά ερωτήματα. Ο πρώτος συγκρίνει το εισόδημα ενός νοικοκυριού με το
εισόδημα των υπόλοιπων νοικοκυριών της χώρας. Ο δεύτερος καταγράφει πώς
αξιολογεί το ίδιο το νοικοκυριό την ικανότητά του να καλύψει τον
προϋπολογισμό του. Στο μεγαλύτερο μέρος της Ευρώπης, οι δύο δείκτες
κινούνται μαζί. Στην Ελλάδα παραμένουν συστηματικά πολύ μακριά ο ένας από
τον άλλον.</p>

<p>Κι όμως, όταν εμφανίζεται ένα τέτοιο χάσμα, οι δύο αριθμοί συνήθως δεν
αντιμετωπίζονται με την ίδια εμπιστοσύνη. Η εισοδηματική φτώχεια μοιάζει πιο
«αντικειμενική»: εισόδημα, όρια, κατατάξεις. Η οικονομική δυσκολία μοιάζει
πιο ασαφής, επειδή βασίζεται στο πώς το ίδιο το νοικοκυριό περιγράφει την
κατάστασή του.</p>

<p>Είναι όμως δικαιολογημένη αυτή η διάκριση; Ή μήπως οι απαντήσεις των
νοικοκυριών καταγράφουν κάτι υλικό που η εισοδηματική φτώχεια, από μόνη
της, δεν βλέπει;</p>
"""))

# ---- 2. Χαμήλωσε ο πήχης, όχι η φτώχεια -----------------------------------
CH.append(chapter("ruler", "Χαμήλωσε ο πήχης, όχι η φτώχεια", f"""
<p>Η πρώτη απάντηση κρύβεται στο ίδιο το εργαλείο της μέτρησης. Το επίσημο
όριο φτώχειας δεν είναι σταθερό. Κινείται μαζί με την οικονομία που
υποτίθεται ότι μετρά.</p>

<p>Ο βασικός δείκτης της ΕΕ, ο κίνδυνος φτώχειας (<em>AROP</em>), στηρίζεται
σε ένα όριο που δεν είναι σταθερό σε χρήμα. Το όριο αυτό ορίζεται στο 60%
του διάμεσου εθνικού εισοδήματος κάθε χρονιάς, και ο ίδιος ο δείκτης
<em>AROP</em> είναι το ποσοστό των ατόμων που βρίσκονται κάτω από αυτό. Σε
μια οικονομία που κινείται ομαλά, αυτό είναι λογικό. Δείχνει ποιος μένει
πίσω σε σχέση με τους υπόλοιπους.</p>

<p>Η Ελλάδα μετά το 2010 δεν ήταν μια τέτοια οικονομία. Τα εισοδήματα
υποχώρησαν μαζικά και μαζί τους υποχώρησε και το όριο φτώχειας. Έτσι, ένα
νοικοκυριό μπορούσε στατιστικά να βγει από τη φτώχεια χωρίς να κερδίζει
ούτε ένα ευρώ περισσότερο. <strong>Δεν είχε βελτιωθεί η ζωή του. Είχε
χαμηλώσει ο πήχης.</strong></p>

{fig('F3', caption="Το όριο φτώχειας έμοιαζε σταθερό. Η αξία του όχι.")}

<p>Η πρώτη καρτέλα του Γραφήματος {{fig:F3}} (<a class="fig-jump" href="#F3"
data-view="0">Ποιοι είναι κάτω από σταθερό όριο</a>) δείχνει το
πρόβλημα καθαρά. Ο επίσημος δείκτης σχεδόν δεν κινείται, γιατί το όριο
πέφτει μαζί με το εισόδημα. Αν όμως κρατήσουμε σταθερό, σε πραγματικές
τιμές, το όριο του 2008 (<em>φτώχεια με σταθερό όριο</em>), η φτώχεια σχεδόν διπλασιάζεται και ξεπερνά το 40%
το 2014. Η δεύτερη καρτέλα (<a class="fig-jump" href="#F3"
data-view="1">Πόσο αξίζει το ίδιο το όριο</a>) δείχνει τον μηχανισμό: το
όριο έμοιαζε σταθερό σε ευρώ, αλλά αυτό που αγόραζε κατέρρευσε και δεν έχει
επανέλθει.</p>

{context_el('CTX-3B', "επιπλέον στοιχεία από άλλη πηγή",
    "Φτώχεια με σταθερό όριο του 2008 σε πραγματικές τιμές, επιβεβαιωμένη "
    "από ανεξάρτητα μικροδεδομένα",
    '''<p>Ανεξάρτητα μικροδεδομένα δείχνουν προς την ίδια κατεύθυνση.
    Ξεχωριστή μελέτη, βασισμένη σε ελληνικά μικροδεδομένα νοικοκυριών,
    εκτιμά ότι το 48% του πληθυσμού ήταν φτωχό όταν εφαρμόστηκε όριο
    αγκυρωμένο πριν από την κρίση, για το ίδιο έτος εισοδήματος για το
    οποίο η δική μας ανασύνθεση δίνει 40,6%.</p>''',
    "Ανεξάρτητη ανάλυση μικροδεδομένων επιβεβαιώνει τη βασική κατεύθυνση: "
    "ένα σταθερό όριο προ κρίσης αποκαλύπτει πολύ μεγαλύτερη φτώχεια κατά "
    "την περίοδο της κρίσης από όση δείχνει ο εκάστοτε σύγχρονος AROP.",
    "Η σύγκριση 48% έναντι 40,6% δεν αποτελεί άμεσο τεστ επικύρωσης ούτε "
    "εκτίμηση σφάλματος. Οι δύο προσεγγίσεις διαφέρουν ως προς τα "
    "δεδομένα, το έτος αναφοράς, την αναπροσαρμογή τιμών και τη χρονική "
    "περίοδο παραγωγής των στοιχείων.",
    "Andriopoulou, E., Kanavitsa, E. &amp; Tsakloglou, P. (2020), "
    "Decomposing Poverty in Hard Times: Greece 2007-2016. LSE GreeSE Paper "
    'No. 149. <a href="https://www.lse.ac.uk/Hellenic-Observatory/'
    'Publications/GreeSE-Papers">πηγή</a>',
    collapse=True)}

<p>Αυτό δεν σημαίνει ότι το σταθερό όριο είναι το «σωστό» και ο <em>AROP</em>
το «λάθος». Οι δύο δείκτες απαντούν σε διαφορετικά ερωτήματα. Ο επίσημος
<em>AROP</em> δείχνει ποιος βρίσκεται χαμηλά σε σχέση με τη σημερινή
κατανομή εισοδήματος, ενώ το σταθερό όριο δείχνει πόσοι εξακολουθούν να
ζουν κάτω από ένα επίπεδο που πριν από την κρίση θεωρούνταν όριο φτώχειας.
Γι' αυτό, αν το ερώτημα είναι αν η κοινωνία έχει πράγματι ανακτήσει το
βιοτικό επίπεδο που έχασε στην κρίση, το σταθερό όριο είναι πιο κατάλληλο
μέτρο. Ο <em>AROP</em> μπορεί να παραμένει σχετικά σταθερός ακόμη και όταν
μεγάλο μέρος της κοινωνίας έχει γίνει φτωχότερο σε πραγματικούς όρους,
επειδή το ίδιο το όριο μετακινείται μαζί με τα εισοδήματα. Αυτή είναι και
η πολιτική σημασία της διάκρισης: η σταθερότητα ενός δείκτη σχετικής
φτώχειας δεν σημαίνει απαραίτητα ότι έχει αποκατασταθεί το επίπεδο ζωής
πριν από την κρίση. Η δική μας εκτίμηση με σταθερό όριο χρησιμοποιείται
ακριβώς για αυτή τη σύγκριση της Ελλάδας με το δικό της παρελθόν και όχι
με άλλες χώρες.</p>

<p>Υπάρχει όμως και ένα δεύτερο ερώτημα: μήπως ο <em>AROP</em> αφήνει έξω
σημαντικές πλευρές της σημερινής οικονομικής δυσκολίας επειδή βασίζεται
μόνο στο εισόδημα; Ο ευρύτερος ευρωπαϊκός δείκτης <em>AROPE</em>, κίνδυνος
φτώχειας ή κοινωνικού αποκλεισμού, επιχειρεί να καλύψει ακριβώς αυτό το
κενό. Καταγράφει όποιον πληροί τουλάχιστον μία από τρεις συνθήκες:
εισοδηματική φτώχεια, σοβαρή υλική και κοινωνική στέρηση ή <em>πολύ χαμηλή
ένταση εργασίας</em>. Αν λοιπόν το χάσμα οφειλόταν κυρίως στο ότι ο
<em>AROP</em> μετρά τη φτώχεια πολύ στενά, ο <em>AROPE</em> θα έπρεπε να
μειώνει αισθητά την απόσταση ανάμεσα στο ποσοστό των ανθρώπων που
θεωρούνται φτωχοί και στο πολύ υψηλότερο ποσοστό των νοικοκυριών που
δηλώνουν ότι δυσκολεύονται να τα βγάλουν πέρα.</p>

<p>Το μειώνει, αλλά μόνο εν μέρει. Από τις 52,6 ποσοστιαίες μονάδες της
μέσης απόστασης ανάμεσα στην εισοδηματική φτώχεια και τη δηλωμένη
οικονομική δυσκολία, ο <em>AROPE</em> κλείνει μόλις 9,8, λιγότερο από το
ένα πέμπτο.</p>

{finding_el('V2-2.1', "Η μετάβαση από τον AROP στον AROPE κλείνει κατά μέσο "
            "όρο 9,8 από τις 52,6 μονάδες του χάσματος, δηλαδή περίπου το "
            "19%, αφήνοντας 42,8 μονάδες. Η συνεισφορά αυτή μειώνεται από "
            "11,0 μονάδες το 2015 σε 7,3 το 2024.")}

{fig('F5', caption="Πού βρίσκεται ο AROPE, από τι αποτελείται και ποιος τον επωμίζεται")}

<p>Το Γράφημα {{fig:F5}} δείχνει και τις δύο πλευρές της εικόνας. Στην πρώτη
καρτέλα (<a class="fig-jump" href="#F5" data-view="0">Βασικοί δείκτες</a>),
ο <em>AROPE</em> βρίσκεται ανάμεσα στην εισοδηματική φτώχεια και την
οικονομική δυσκολία, αλλά πολύ πιο κοντά στην πρώτη.</p>

<p>Οι υπόλοιπες καρτέλες δείχνουν γιατί ένας εθνικός αριθμός δεν αρκεί. Η
Ελλάδα βρίσκεται πάνω από τη διάμεση χώρα της ΕΕ και στα δύο συστατικά για
τα οποία υπάρχουν συγκρίσιμα εθνικά δεδομένα: την εισοδηματική φτώχεια και
την υλική στέρηση. Οι ηλικιωμένοι ακολουθούν διαφορετική πορεία από τους
νεότερους. Οι γυναίκες βρίσκονται σταθερά πάνω από τους άνδρες.</p>

<p>Το βασικό σημείο δεν είναι κάθε επιμέρους διαφορά. Είναι ότι ένας
εθνικός μέσος όρος συμπιέζει πολύ διαφορετικές εμπειρίες σε μία μόνο
γραμμή. Οι επίσημοι δείκτες δεν είναι λανθασμένοι. Κάνουν ακριβώς τη
δουλειά για την οποία σχεδιάστηκαν: μετρούν σχετική εισοδηματική θέση,
διευρυμένο κίνδυνο κοινωνικού αποκλεισμού και εθνικούς μέσους όρους.</p>

<p>Το νοικοκυριό που απαντά αν «τα βγάζει πέρα», όμως, μιλά για κάτι πιο
άμεσο: πόσο κοστίζει η καθημερινότητά του σε σχέση με τα χρήματα που
διαθέτει.</p>
"""))

# ---- 3. Δεν είναι απλώς μια αίσθηση ---------------------------------------
CH.append(chapter("footprint", "Δεν είναι απλώς μια αίσθηση", f"""
<p>Αν τα ελληνικά νοικοκυριά απαντούν απλώς σε ένα υποκειμενικό ερώτημα πιο
απαισιόδοξα από όλους τους άλλους, τότε η ιστορία αφορά περισσότερο τον
τρόπο με τον οποίο οι άνθρωποι μιλούν για τη ζωή τους παρά την οικονομική
τους κατάσταση. Σε αυτή την περίπτωση, όσα ακολουθούν δεν θα περιέγραφαν την
οικονομία αλλά την ηχώ μιας συλλογικής διάθεσης.</p>

<p>Αυτό πρέπει να εξεταστεί πρώτο και σοβαρά, όχι να απορριφθεί εκ
προοιμίου.</p>

<p>Το κρίσιμο ερώτημα δεν είναι αν η απάντηση ενός μεμονωμένου νοικοκυριού
είναι από μόνη της αξιόπιστη. Είναι αν το εθνικό ποσοστό <em>οικονομικής
δυσκολίας</em> κινείται, χρόνο με τον χρόνο, μαζί με εθνικούς δείκτες που
περιγράφουν συγκεκριμένα γεγονότα και όχι διαθέσεις: <em>καθυστερήσεις στην
πληρωμή λογαριασμών</em>, <em>αδυναμία κάλυψης ενός απρόοπτου εξόδου</em>,
<em>ανεπαρκή θέρμανση του σπιτιού</em> και <em>υλική στέρηση</em> από πολλά
βασικά αγαθά ταυτόχρονα.</p>

<p>Ένα ασαφές ερώτημα μπορεί πράγματι να επηρεαστεί από μια γενικευμένη
αρνητική διάθεση. Είναι όμως δυσκολότερο να αποδοθεί αποκλειστικά στη
διάθεση όταν επί σειρά ετών κινείται μαζί με πολλούς διαφορετικούς,
συγκεκριμένους δείκτες οικονομικής πίεσης.</p>

{fig('F8', caption="Κινούνταν μαζί η δηλωμένη δυσκολία και τα συγκεκριμένα οικονομικά προβλήματα;")}

<p>Τρεις από τις τέσσερις καρτέλες του Γραφήματος {{fig:F8}} δείχνουν το ίδιο
μοτίβο: όταν περισσότερα ελληνικά νοικοκυριά δηλώνουν ότι δυσκολεύονται να
τα βγάλουν πέρα, αυξάνονται συνήθως και πολύ συγκεκριμένες οικονομικές
δυσκολίες. Περισσότερα νοικοκυριά αδυνατούν να καλύψουν <a class="fig-jump"
href="#F8" data-view="0">μια έκτακτη δαπάνη</a>, να <a class="fig-jump"
href="#F8" data-view="2">θερμάνουν επαρκώς το σπίτι τους</a> ή να
εξασφαλίσουν <a class="fig-jump" href="#F8" data-view="1">αρκετά βασικά
αγαθά και ανάγκες</a>.</p>

<p>Το 2015, για παράδειγμα, και οι τέσσερις δείκτες βρίσκονταν πάνω από τον
μέσο όρο τους για τη δεκαετία. Μέχρι το 2024 είχαν πέσει όλοι κάτω από
αυτόν. Δεν κινούνται απόλυτα μαζί κάθε χρόνο, αλλά η γενική τους πορεία
είναι σαφώς παράλληλη. Η συσχέτιση, δηλαδή ο αριθμός που συνοψίζει πόσο
στενά κινούνται δύο δείκτες μαζί, είναι πολύ υψηλή και στις τρεις
περιπτώσεις: από 0,87 έως 0,94, σε μια κλίμακα όπου το 1 θα σήμαινε
απόλυτα παράλληλη κίνηση.</p>

<p>Το ίδιο μοτίβο εμφανίζεται και όταν επαναλαμβάνουμε τον έλεγχο σε
ολόκληρη την ΕΕ. Εδώ δεν συγκρίνουμε απλώς την Ελλάδα με πλουσιότερες ή
φτωχότερες χώρες. Εξετάζουμε κάθε χώρα ξεχωριστά και ρωτάμε: στις χρονιές
που αυξάνεται η δηλωμένη οικονομική δυσκολία μέσα σε αυτή τη χώρα,
αυξάνονται και οι συγκεκριμένες υλικές δυσκολίες; Στις περισσότερες
περιπτώσεις η απάντηση είναι ναι. Οι αντίστοιχες συσχετίσεις κυμαίνονται
από 0,63 έως 0,80.</p>

<p>Αυτό δεν αποδεικνύει ότι ο ένας δείκτης προκαλεί τον άλλον. Δείχνει όμως
ότι η δηλωμένη οικονομική δυσκολία δεν κινείται μόνη της: ακολουθεί μια
ευρύτερη και συγκεκριμένη μεταβολή στις υλικές συνθήκες των
νοικοκυριών.</p>

{finding_el('V2-3.1', "Η οικονομική δυσκολία συμμεταβάλλεται με τις καθυστερήσεις "
            "πληρωμών, την αδυναμία κάλυψης ενός απρόοπτου εξόδου, την "
            "ανεπαρκή θέρμανση και τη σοβαρή υλική στέρηση. Οι ενδοχωρικές "
            "συσχετίσεις σε επίπεδο ΕΕ κυμαίνονται από 0,63 έως 0,80.",
            "Πρόκειται για επιβεβαίωση από το ίδιο εργαλείο μέτρησης και "
            "όχι για ανεξάρτητη επικύρωση. Όλα τα στοιχεία προέρχονται από "
            "το EU-SILC. Επιπλέον, η σχέση δεν είναι ομοιόμορφη: στην "
            "Ελλάδα η συσχέτιση με τις καθυστερήσεις πληρωμών είναι μόλις "
            "0,371.")}

<p>Η τέταρτη καρτέλα (<a class="fig-jump" href="#F8" data-view="3">Καθυστερήσεις
σε λογαριασμούς</a>) διαφέρει και αξίζει να
σταθούμε στο γιατί. Οι καθυστερήσεις είναι ίσως το πιο χειροπιαστό από τα
τέσσερα στοιχεία, κι όμως ακολουθούν πολύ λιγότερο στενά τις μεταβολές της
συνολικής οικονομικής δυσκολίας. Μια εύλογη εξήγηση είναι ότι, για να
εμφανιστεί μια καθυστέρηση πληρωμής, πρέπει πρώτα να υπάρχει μια υποχρέωση
που μπορεί να μείνει απλήρωτη. Ένα νοικοκυριό που έχασε την πρόσβαση σε
πίστωση χρόνια πριν ή που δεν είχε ποτέ τέτοια πρόσβαση μπορεί να βρίσκεται
σε πραγματική οικονομική δυσκολία χωρίς αυτή να καταγράφεται ως ληξιπρόθεσμος
λογαριασμός. Πρόκειται, ωστόσο, για πιθανή ερμηνεία και όχι για μηχανισμό
που ελέγχθηκε άμεσα από την ανάλυση.</p>

<p>Ο πρώτος έλεγχος μας οδηγεί μέχρι εδώ: η δηλωμένη οικονομική δυσκολία
συμβαδίζει στενά με συγκεκριμένες υλικές στερήσεις. Δεν μπορεί όμως να
αποτελέσει ανεξάρτητη επιβεβαίωση, επειδή όλοι αυτοί οι δείκτες
προέρχονται από την ίδια έρευνα και μπορεί να επηρεάζονται από έναν κοινό
τρόπο απάντησης.</p>

<p>Χρειάζεται επομένως ένας δεύτερος, ευρύτερος έλεγχος. Αν η δηλωμένη
οικονομική δυσκολία ήταν απλώς μια ιδιομορφία της ερώτησης για το αν τα
νοικοκυριά «τα βγάζουν πέρα», θα περιμέναμε να παραμένει απομονωμένη από
την υπόλοιπη εικόνα της ελληνικής οικονομίας. Δεν παραμένει. Η ίδια
επιδείνωση εμφανίζεται σε ένα ευρύτερο σύνολο δεικτών για την εργασία,
τους μισθούς, τις τιμές, την πραγματική κατανάλωση και τις προσδοκίες των
νοικοκυριών, πολλοί από τους οποίους προέρχονται από διαφορετικές
στατιστικές σειρές.</p>

{fig('F21', caption="Το ελληνικό μειονέκτημα απλώθηκε σε ολόκληρο το φάσμα των δεικτών")}

<p>Ας πάρουμε <em>δεκαέξι διαφορετικούς δείκτες</em> της ελληνικής οικονομικής και
κοινωνικής πραγματικότητας (<a class="fig-jump" href="#F21">Γράφημα
{{fig:F21}}</a>): μισθούς, ώρες εργασίας, τιμές, δυνατότητα θέρμανσης του
σπιτιού, προσδοκίες των νοικοκυριών για τον επόμενο χρόνο, εισοδηματική
ανισότητα και άλλα συναφή μεγέθη. Στην ανάλυση κρατήθηκαν μόνο δείκτες για
τους οποίους υπάρχει συγκρίσιμη ευρωπαϊκή μέτρηση τόσο το 2008 όσο και το
2024. Περισσότερες λεπτομέρειες για την επιλογή τους δίνονται στις
«Μεθόδους και περιορισμούς» κάτω από το Γράφημα {{fig:F21}}.</p>

<p>Η πρώτη καρτέλα (<a class="fig-jump" href="#F21" data-view="0">Ποιοι
δείκτες</a>) συγκρίνει τη θέση της Ελλάδας σε κάθε δείκτη το 2008 και το
2024, δείχνοντας αν στο μεταξύ η χώρα πέρασε στο χειρότερο πέμπτο της ΕΕ,
δηλαδή περίπου στις έξι δυσμενέστερες θέσεις, ή αν βρισκόταν ήδη εκεί. Οι
δείκτες δεν κινήθηκαν όλοι με τον ίδιο τρόπο. Η συνολική εικόνα, όμως,
είναι ότι το ελληνικό μειονέκτημα εξαπλώθηκε σε περισσότερους τομείς, αντί
να περιορίζεται σε λίγα μεμονωμένα προβλήματα.</p>

<p>Η δεύτερη καρτέλα (<a class="fig-jump" href="#F21" data-view="1">Πόσοι
δείκτες</a>) συμπυκνώνει αυτή την εξάπλωση σε μία γραμμή. Πριν από την κρίση, η Ελλάδα βρισκόταν στο χειρότερο πέμπτο της ΕΕ
σε τέσσερις από τους δεκαέξι δείκτες, στο ένα τέταρτο του συνόλου (25%). Το
2024 βρίσκεται εκεί σε έντεκα από τους δεκαέξι, περίπου στα δύο τρίτα
(περίπου 69%). Την ίδια περίοδο, η αντίστοιχη τιμή για τη διάμεση χώρα της
ΕΕ μεταβάλλεται ελάχιστα. Η εξάπλωση αυτή, επομένως, δεν φαίνεται να
αποτελεί μια γενική ευρωπαϊκή τάση.</p>

<p>Έχει σημασία επίσης ότι οι περισσότεροι από αυτούς τους δείκτες δεν
προέρχονται από την ίδια συνέντευξη με την ερώτηση για την οικονομική
δυσκολία. Το ευρύτερο ελληνικό μειονέκτημα, επομένως, δεν εμφανίζεται μόνο
στις απαντήσεις των νοικοκυριών για το αν μπορούν να τα βγάλουν πέρα, αλλά
και σε ανεξάρτητα μετρημένες πλευρές της οικονομικής πραγματικότητας.</p>

<p>Υπάρχει, τέλος, ένα ακόμη αποτέλεσμα που χρειάζεται προσοχή. Όταν
προσθέσουμε σε ένα στατιστικό μοντέλο τους δείκτες στέρησης που συνδέονται
πιο στενά με την εμπειρία της οικονομικής δυσκολίας, μεγάλο μέρος της
ελληνικής διαφοράς ανάμεσα στην εισοδηματική φτώχεια και τη δηλωμένη
δυσκολία παύει να μένει ανεξήγητο. Αυτό είναι σημαντικό, γιατί δείχνει ότι
οι συγκεκριμένες μορφές στέρησης συνδέονται στενά με όσα δηλώνουν τα
νοικοκυριά. Ταυτόχρονα, όμως, επαναφέρει ακόμη εντονότερα το πρόβλημα του
κοινού εργαλείου μέτρησης: αρκετοί από αυτούς τους δείκτες προέρχονται από
την ίδια έρευνα με την οικονομική δυσκολία. Γι' αυτό το αποτέλεσμα αποτελεί
ισχυρή ένδειξη, αλλά δεν μπορεί να χρησιμοποιηθεί ως ανεξάρτητη εξήγηση, ένα
ζήτημα στο οποίο θα επιστρέψουμε αργότερα.</p>

{finding_el('V2-3.2', "Οι τέσσερις δείκτες στέρησης, η αδυναμία κάλυψης "
            "ενός απρόοπτου εξόδου, η υλική στέρηση, η αδυναμία επαρκούς "
            "θέρμανσης του σπιτιού και οι καθυστερήσεις σε λογαριασμούς, "
            "απορροφούν στατιστικά το 71% του βασικού ανεξήγητου "
            "υπολοίπου της Ελλάδας, μειώνοντάς το από +46,92 σε +13,74 "
            "ποσοστιαίες μονάδες.",
            "Η στατιστική απορρόφηση δεν αποδεικνύει ότι οι συγκεκριμένες "
            "στερήσεις προκαλούν ή εξηγούν αιτιωδώς την οικονομική "
            "δυσκολία. Επειδή οι δείκτες προέρχονται από το ίδιο εργαλείο "
            "μέτρησης, μέρος της κοινής τους μεταβολής μπορεί να "
            "οφείλεται στον κοινό τρόπο μέτρησης και όχι σε κοινή αιτία. "
            "Το αποτέλεσμα έχει επομένως διαγνωστική αξία, όχι "
            "αποδεικτική.")}

<p>Επομένως, οι απαντήσεις των νοικοκυριών συνδέονται πολύ στενά με υλικές
συνθήκες για να απορριφθούν απλώς ως «διάθεση». Ταυτόχρονα, αρκετές από τις
ισχυρότερες επιβεβαιώσεις προέρχονται από το ίδιο εργαλείο μέτρησης και δεν
μπορούν να θεωρηθούν ανεξάρτητη απόδειξη. Και τα δύο ισχύουν ταυτόχρονα.
Αυτό αρκεί για να περάσουμε στο επόμενο ερώτημα: αν η δυσκολία είναι
πραγματική, γιατί ο <em>AROP</em> την καταγράφει τόσο λίγο;</p>
"""))

# ---- 4. Οι δουλειές ανέκαμψαν. Τα νοικοκυριά όχι. ----------------------
CH.append(chapter("recovery", "Η απασχόληση ανέκαμψε. Τα νοικοκυριά όχι.", f"""
<p>Το ισχυρότερο επιχείρημα υπέρ της ελληνικής ανάκαμψης είναι η αγορά
εργασίας. Η ανεργία υποχώρησε από τα ακραία επίπεδα της κρίσης σε κάτω από
9%, ενώ μειώθηκε σημαντικά και η <em>μακροχρόνια ανεργία</em>. Αυτό είναι πραγματική
πρόοδος. Ένα νοικοκυριό, όμως, δεν ζει με το ποσοστό ανεργίας. Ζει με τον
μισθό που μπαίνει στο σπίτι, τις τιμές που πληρώνει, το κόστος στέγασης και
το ποσό που απομένει στο τέλος του μήνα. Με αυτά τα κριτήρια, η ανάκαμψη
φαίνεται πολύ λιγότερο ολοκληρωμένη.</p>

<p>Ας ξεκινήσουμε από εκεί που υπήρξε ξεκάθαρη βελτίωση. Η μακροχρόνια
ανεργία, η έλλειψη εργασίας για δώδεκα μήνες ή περισσότερο, βρισκόταν στο
16,4% του εργατικού δυναμικού το 2015. Μέχρι το 2024 είχε υποχωρήσει στο
5,4%. Πρόκειται για σημαντική πρόοδο. Λιγότεροι άνθρωποι έμειναν για χρόνια
εκτός αγοράς εργασίας, ακριβώς το είδος παρατεταμένης απουσίας που μπορεί
να αναγκάσει ένα νοικοκυριό να εξαντλήσει αποταμιεύσεις, να ρευστοποιήσει
περιουσιακά στοιχεία ή να στηριχθεί περισσότερο σε συγγενείς. Η ανάλυση δεν
παρακολουθεί άμεσα αυτές τις αντιδράσεις, αλλά η μείωση της μακροχρόνιας
ανεργίας παραμένει ουσιαστική.</p>

<p>Η απασχόληση, ωστόσο, ανέκαμψε πολύ περισσότερο από τους μισθούς. Το
2015 οι <em>πραγματικοί μισθοί</em> βρίσκονταν περίπου στο 77% του επιπέδου του
2008. Το 2024 βρίσκονταν περίπου στο 68%. Δεν ανακάμπτουν αργά. Δεν έχουν
ανακάμψει. Οι ελληνικοί πραγματικοί μισθοί παραμένουν κάτω από το επίπεδο
του 2008 για δεκαπέντε συνεχόμενα χρόνια, περισσότερο από κάθε άλλη χώρα
της ΕΕ εκτός από την Ουγγαρία.</p>

<p>Ταυτόχρονα το κατά κεφαλήν προϊόν δίνει μια ενδιάμεση εικόνα: η
απόσταση από το επίπεδο του 2008 έχει μειωθεί περίπου κατά το μισό, αλλά
δεν έχει κλείσει.</p>

<p>Τέλος, υπάρχει και ένα μέγεθος που βελτιώθηκε αισθητά και πρέπει να
αναφερθεί καθαρά, ώστε η εικόνα να μην γίνει μονόπλευρη. Ο όγκος της
<em>πραγματικής ατομικής κατανάλωσης</em>, τα αγαθά και οι υπηρεσίες που πράγματι
καταναλώνουν τα νοικοκυριά, μετρημένα σε κοινή μονάδα αγοραστικής δύναμης,
αυξήθηκε από περίπου 14.800 σε 21.300 μονάδες. Η Ελλάδα λοιπόν κατανάλωνε
περισσότερο. Την ίδια περίοδο, όμως, η διάμεση χώρα της ΕΕ βελτιώθηκε
ακόμη γρηγορότερα. Έτσι η ελληνική κατανάλωση αυξήθηκε, αλλά η σχετική
απόσταση από την Ευρώπη μεγάλωσε.</p>

{fig('F7', caption="Κάποια χάσματα έκλεισαν. Άλλα διευρύνθηκαν.")}

<p>Το Γράφημα {{fig:F7}} συνοψίζει την εικόνα. Τα χάσματα που αφορούν την
απασχόληση και τη στέγαση στένεψαν σημαντικά. Το χάσμα του κατά κεφαλήν
προϊόντος μειώθηκε περίπου στο μισό. Αντίθετα, τα χάσματα στους μισθούς,
στην πραγματική κατανάλωση και στην αγοραστική δύναμη είτε έκλεισαν ελάχιστα
είτε διευρύνθηκαν. Επειδή δεκατέσσερις διαφορετικοί δείκτες δεν μπορούν να
τοποθετηθούν στον ίδιο άξονα με τις φυσικές τους μονάδες, <a
class="fig-jump" href="#recovery-table">ο συνοδευτικός πίνακας</a>
παρουσιάζει τις ίδιες μεταβολές στις μονάδες κάθε δείκτη. Η πραγματική κατανάλωση
μετριέται σε μονάδες αγοραστικής δύναμης (ΜΑΔ): μια κοινή τεχνητή
μονάδα, όχι ευρώ, που επιτρέπει να συγκρίνεται ο όγκος της πραγματικής
κατανάλωσης ανάμεσα σε χώρες με διαφορετικό επίπεδο τιμών.</p>

{recovery_table_el()}

<p class="table-legend">Ο πίνακας παρουσιάζει την ίδια σύγκριση στις
φυσικές μονάδες κάθε δείκτη: ποσοστά για την ανεργία, το προϊόν και το
κόστος στέγασης· μονάδες αγοραστικής δύναμης (ΜΑΔ) για τους υλικούς
πόρους· μονάδες δείκτη για τους μισθούς και την αγοραστική πίεση. Κρατά
επίσης ορατή τη βασική προειδοποίηση: ένας ελληνικός δείκτης μπορεί να
βελτιώνεται χωρίς να κλείνει το χάσμα από την Ευρώπη. Η πραγματική κατανάλωση
αυξήθηκε σημαντικά στην Ελλάδα, αλλά έμεινε ακόμη πιο πίσω επειδή η
διάμεση χώρα της ΕΕ βελτιώθηκε ταχύτερα. Το γράφημα δεν εξηγεί γιατί ένα
χάσμα στένεψε ή διευρύνθηκε. Δείχνει μόνο πού ήταν ισχυρότερη η ανάκαμψη:
στην απασχόληση πολύ περισσότερο από ό,τι στους μισθούς, στους υλικούς
πόρους και στην αγοραστική δύναμη.</p>

{fig('F10', caption="Η ανάκαμψη φαίνεται πιο αδύναμη από τη σκοπιά του νοικοκυριού")}

<p>Ο ίδιος διαχωρισμός φαίνεται και στα σημερινά επίπεδα. Στο Γράφημα
{{fig:F10}}, η μακροχρόνια ανεργία, η πραγματική κατανάλωση και η <em>αγοραστική
πίεση</em> τοποθετούν την Ελλάδα στη δυσμενή πλευρά της διάμεσης χώρας της ΕΕ. Είναι
επίσης οι τρεις τρέχουσες συνθήκες που προσθέτουν στατιστικά πληροφορία
πέρα από τον επίσημο δείκτη εισοδηματικής φτώχειας. Το συμπέρασμα, όμως,
είναι απλούστερο από το μοντέλο: <strong><em>η ανάκαμψη που βιώνουν τα
νοικοκυριά είναι ασθενέστερη από την ανάκαμψη που αποτυπώνουν οι μεγάλοι
μακροοικονομικοί δείκτες.</em></strong></p>

<p>Μια χώρα μπορεί να βρίσκεται υπό αγοραστική πίεση επειδή είναι ακριβή ή
επειδή πληρώνει χαμηλούς μισθούς. Στην Ελλάδα τα δύο προβλήματα
συνυπάρχουν. Για τον οικογενειακό προϋπολογισμό, η διάκριση έχει μικρή
σημασία.</p>

<div class="finding compact" data-claim-id="V2-4.C2 V2-4.C1 V2-4.C4">
<p><em>Τι δείχνουν τα στοιχεία.</em> Η μακροχρόνια ανεργία, οι υλικοί
πόροι και η αγοραστική πίεση προβλέπουν καθεμία την οικονομική δυσκολία
πέρα από την εισοδηματική φτώχεια και τις επιδράσεις του έτους.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> Πρόκειται για
συσχετίσεις μεταξύ χωρών και όχι για αιτιώδεις αποδείξεις. Η αγοραστική
πίεση δεν πρέπει να συγχέεται με την ένταση και πίεση στην εργασία.
Πρόκειται για διαφορετικούς δείκτες: ο πρώτος αφορά τη σχέση τιμών και
οικονομικών πόρων του νοικοκυριού, ενώ ο δεύτερος τις απαιτήσεις της ίδιας
της εργασίας, όπως ο γρήγορος ρυθμός και οι στενές προθεσμίες. Διαφορετική
έννοια είναι επίσης η «πολύ χαμηλή ένταση εργασίας» του <em>AROPE</em>, η
οποία μετρά πόσο από τον δυνητικό χρόνο εργασίας αξιοποίησαν συνολικά τα
μέλη ενός νοικοκυριού.</p>
</div>

{context_el('CTX-8', "επιπλέον στοιχεία από άλλη πηγή",
    "Μια ανεξάρτητη ανάλυση (Greece in Figures)",
    '''<p>Μια πρόσφατη ανάλυση του Greece in Figures καταλήγει σε παρόμοια
    εικόνα από διαφορετική διαδρομή, χωρίς να χρησιμοποιεί τα μοντέλα της
    παρούσας ανάλυσης. Η Ελλάδα δεν βρίσκεται τελευταία στην Ευρώπη ως
    προς την πραγματική κατανάλωση, αλλά συνδυάζει πολλές ώρες εργασίας,
    χαμηλή ωριαία αμοιβή και υψηλές καθημερινές τιμές.</p>''',
    "Η εικόνα συμφωνεί με τα ευρήματα για την πραγματική κατανάλωση και την "
    "αγοραστική πίεση και προέρχεται από ανεξάρτητη ανάλυση. Οι βασικοί "
    "αριθμοί του άρθρου επιβεβαιώνονται από τις πρωτογενείς δημοσιεύσεις "
    "της Eurostat και της ΕΛΣΤΑΤ στις οποίες βασίζεται.",
    "Το άρθρο περιγράφει, δεν ελέγχει. Δεν κάνει κανέναν από τους "
    "στατιστικούς ελέγχους αυτής της ανάλυσης, δεν ξεχωρίζει τις "
    "συγκρίσεις μεταξύ χωρών από τη σύγκριση κάθε χώρας με τον εαυτό της, "
    "και πουθενά δεν εξετάζει αν αυτοί οι παράγοντες εξηγούν την οικονομική "
    "δυσκολία. Ούτε ο δικός του δείκτης κατανάλωσης ανά ώρα εργασίας "
    "αποτελεί απόδειξη: είναι ένας λόγος δύο μεγεθών, όχι έλεγχος. "
    "Τα στοιχεία του είναι επίσης νεότερα, από το 2025 και το 2026, ενώ η "
    "ανάλυση εδώ σταματά το 2024, οπότε τα δύο δεν συνδυάζονται στο ίδιο "
    "σύνολο δεδομένων. "
    "Δύο σημεία του άρθρου δεν στέκουν και δεν επαναλαμβάνονται εδώ: για "
    "την ιδιοκτησία αυτοκινήτων επικαλείται τον συνολικό αριθμό οχημάτων "
    "που κυκλοφορούν, ο οποίος δεν δείχνει νέες αγορές, και το «όλοι οι "
    "Έλληνες ταξίδεψαν» δεν προκύπτει από την έρευνα της ΕΛΣΤΑΤ στην οποία "
    "στηρίζεται. "
    "Τέλος, όπου η κατάταξη της Ελλάδας στο άρθρο διαφέρει από τη δική μας, "
    "η διαφορά είναι συνήθως θέμα περιόδου ή διαφορετικού μεγέθους, όχι "
    "αντίφαση.",
    "Greece in Figures, «Γιατί οι Έλληνες νιώθουν τόσο φτωχοί». "
    '<a href="https://www.greeceinfigures.com/analyses/'
    'giati-oi-ellenes-niothoun-toso-phtokhoi/">πηγή</a>',
    collapse=True)}

<p>Με απλά λόγια: η αγορά εργασίας βελτιώθηκε, αλλά ο προϋπολογισμός του
νοικοκυριού δεν ανέκαμψε μαζί της.</p>

<blockquote>Η ανεργία επανήλθε. Ο μισθός όχι.</blockquote>
"""))

# ---- 5. Μια Δεκαετία Ζημιάς Ακόμα Μετράει ----------------------------------
CH.append(chapter("duration", "Το συσσωρευμένο βάρος της κρίσης", f"""
<p>Η διάκριση ανάμεσα στην ανάκαμψη της απασχόλησης και την πιο αδύναμη
ανάκαμψη των νοικοκυριών αφορά κυρίως το πού βρισκόμαστε σήμερα. Για ένα
νοικοκυριό, όμως, δεν έχει σημασία μόνο το σημερινό επίπεδο. Έχει σημασία
και το πόσο διήρκεσε η πίεση. Ένας χρόνος ανεργίας δεν είναι το ίδιο με
δέκα. Μια προσωρινή μείωση μισθού δεν είναι το ίδιο με δεκαπέντε χρόνια
χαμηλότερων πραγματικών αποδοχών. Και μια σύντομη επιβάρυνση στο κόστος
στέγασης δεν είναι το ίδιο με μια πίεση που επιμένει επί χρόνια.</p>

<p>Εδώ χρειάζεται όμως προσοχή. Το γεγονός ότι μια χώρα έχει περάσει
περισσότερα χρόνια υπό πίεση δεν σημαίνει από μόνο του ότι αυτό το
συσσωρευμένο παρελθόν εξηγεί τη σημερινή οικονομική δυσκολία. Μπορεί απλώς
οι χώρες που είχαν τη δυσκολότερη πορεία να εξακολουθούν να έχουν και τις
χειρότερες συνθήκες σήμερα. Γι' αυτό η ανάλυση δεν αρκείται στο να μετρήσει
πόση πίεση συσσωρεύτηκε· εξετάζει στη συνέχεια αν αυτό το παρελθόν
εξακολουθεί να προσθέτει πληροφορία αφού ληφθεί υπόψη η σημερινή
κατάσταση.</p>

<p>Για τον σκοπό αυτό κατασκευάζονται τρεις δείκτες συσσωρευμένου βάρους:
η <em>συσσωρευμένη ανεργία</em>, πόση επιπλέον ανεργία πέρασε κάθε χώρα από την αρχή της κρίσης, η <em>διάρκεια μισθολογικής μη ανάκαμψης</em>, πόσα
συνεχόμενα χρόνια οι πραγματικοί μισθοί της παρέμειναν κάτω από το επίπεδο
του 2008, και η <em>σωρευτική επιδείνωση του κόστους στέγασης</em>, πόσο επίμονα επιδεινώθηκε το κόστος στέγασης. Ο τελευταίος
δείκτης συνδυάζει το μέγεθος και τη διάρκεια της επιδείνωσης: μια χώρα που
βρίσκεται πέντε ποσοστιαίες μονάδες πάνω από το επίπεδο του 2010 επί δέκα
χρόνια συσσωρεύει διπλάσιο βάρος από μία που βρίσκεται πέντε μονάδες πάνω
επί πέντε χρόνια.</p>

{fig('F11', caption="Η Ελλάδα είχε ένα από τα μεγαλύτερα συσσωρευμένα βάρη της Ευρώπης")}

<p>Το Γράφημα {{fig:F11}} αποτυπώνει τον ισολογισμό της κρίσης. Η Ελλάδα
έχει το μεγαλύτερο συσσωρευμένο βάρος ανεργίας στην ΕΕ και τη μεγαλύτερη
επιδείνωση του κόστους στέγασης από το 2010· και στους δύο δείκτες
κατατάσσεται πρώτη μεταξύ των 27 χωρών. Πολύ ψηλά βρίσκεται και στη
διάρκεια της μισθολογικής μη ανάκαμψης: οι πραγματικοί μισθοί της
παραμένουν κάτω από το επίπεδο του 2008 για δεκαπέντε συνεχόμενα χρόνια,
μόλις ένα λιγότερο από την Ουγγαρία.</p>

<p>Άλλο όμως να έχει μια χώρα βαρύ παρελθόν και άλλο να γνωρίζουμε ότι
αυτό το παρελθόν εξακολουθεί να σχετίζεται με τη σημερινή δυσκολία αφού
ληφθούν υπόψη οι σημερινές συνθήκες. Εδώ βρίσκεται το δύσκολο ερώτημα:
<em>αν γνωρίζουμε τη σημερινή κατάσταση μιας χώρας, μας λέει κάτι επιπλέον
η δεκαετία που προηγήθηκε;</em></p>

<p>Για τρεις δείκτες, η απάντηση είναι ναι. Οι χώρες με μεγαλύτερη
συσσωρευμένη ανεργία, περισσότερα χρόνια πραγματικών μισθών κάτω από το
επίπεδο του 2008 και μεγαλύτερη σωρευτική επιδείνωση του κόστους στέγασης
δηλώνουν μεγαλύτερη οικονομική δυσκολία ακόμη και όταν λαμβάνονται υπόψη ο
σημερινός δείκτης φτώχειας και οι τρέχουσες συνθήκες.</p>

<div class="finding compact" data-claim-id="V2-5.C2 V2-5.C3 V2-5.C6">
<p><em>Τι δείχνουν τα στοιχεία.</em> Η συσσωρευμένη επιπλέον ανεργία, η
διάρκεια των πραγματικών μισθών κάτω από το επίπεδο του 2008 και η
σωρευτική επιδείνωση του κόστους στέγασης προσθέτουν, καθεμία χωριστά,
πληροφορία για την οικονομική δυσκολία πέρα από τη σημερινή κατάσταση.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> Πρόκειται για
σχέσεις μεταξύ χωρών και όχι για απόδειξη ότι το συσσωρευμένο παρελθόν
προκαλεί τη σημερινή δυσκολία μέσα στην Ελλάδα.</p>
</div>

<p>Τα αποτελέσματα δεν είναι εξίσου ισχυρά και για τους τρεις δείκτες.
Στους μισθούς, το εύρημα εξαρτάται από τον συγκεκριμένο τρόπο με τον οποίο
μετριούνται τα συνεχόμενα χρόνια κάτω από το επίπεδο του 2008: άλλοι
εύλογοι ορισμοί κινούνται προς την ίδια κατεύθυνση, αλλά δεν περνούν το
προκαθορισμένο όριο. Η στέγαση δίνει επίσης το πιο ασταθές αποτέλεσμα από
τα τρία.</p>

<p>Το μοτίβο πάντως δεν είναι καθολικό, και αυτό από μόνο του λέει κάτι.
Στην <em>αγοραστική πίεση</em> τα πράγματα αντιστρέφονται: τη διαφορά την κάνει ο
σημερινός αριθμός, ενώ η σωρευτική εκδοχή δεν δίνει σαφές αποτέλεσμα. Ο
<em>συσσωρευμένος πληθωρισμός</em> εξετάστηκε επίσης, αλλά τα διαθέσιμα δεδομένα
δεν επιτρέπουν ασφαλές συμπέρασμα. Αυτό δείχνει ότι η διάρκεια φαίνεται να
έχει ιδιαίτερη σημασία σε ορισμένους τομείς, την ανεργία, τους μισθούς και
τη στέγαση, και όχι ότι κάθε οικονομικό πρόβλημα του παρελθόντος αφήνει
αυτομάτως ανεξάρτητο αποτύπωμα στο σήμερα.</p>

<div class="finding compact" data-claim-id="V2-5.X">
<p><em>Τι δείχνουν τα στοιχεία.</em> Στην αγοραστική πίεση, ο τρέχων
δείκτης παραμένει ισχυρός μετά τον έλεγχο, ενώ ο σωρευτικός δείκτης
παραμένει χωρίς σαφές συμπέρασμα.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> «Χωρίς σαφές
συμπέρασμα» δεν σημαίνει «χωρίς επίδραση»· σημαίνει ότι τα διαθέσιμα
στοιχεία δεν επαρκούν για ασφαλή κρίση.</p>
</div>

<p>Υπάρχουν επίσης δύο περιπτώσεις όπου ο σωρευτικός έλεγχος δεν μπορεί να
χρησιμοποιηθεί. Η πρώτη αφορά την πραγματική κατανάλωση: τα διαθέσιμα δεδομένα
ξεκινούν μόλις το 2015, άρα δεν υπάρχει σημείο αναφοράς πριν από την
κρίση. Θα μπορούσαμε να ξεκινήσουμε τη μέτρηση από το 2015, αλλά τότε ο
δείκτης δεν θα περιλάμβανε την ίδια την κρίση που θέλουμε να μετρήσουμε.
Για τον λόγο αυτό δεν κατασκευάστηκε.</p>

{finding_el('V2-5.Z', "Η συσσωρευμένη πραγματική κατανάλωση δεν μπόρεσε καν "
            "να ελεγχθεί: τα διαθέσιμα δεδομένα ξεκινούν το 2015 και δεν "
            "υπάρχει σημείο αναφοράς για το 2008. Το σημείο αναφοράς δεν "
            "μετακινήθηκε προκειμένου να καταστεί ελέγξιμο.",
            "Πρόκειται για ανέφικτο έλεγχο, όχι για μηδενικό αποτέλεσμα.",
            lead="Τι δεν μπόρεσε να ελεγχθεί.")}

<p>Η δεύτερη περίπτωση αφορά έναν συγγενικό δείκτη συσσωρευμένου
μισθολογικού ελλείμματος. Παρότι ο σωρευτικός δείκτης πέρασε τα ενδιάμεσα
στατιστικά κριτήρια, ο αντίστοιχος τρέχων δείκτης πάνω στον οποίο
στηρίζεται δεν είχε τεκμηριωθεί επαρκώς στον προηγούμενο έλεγχο. Με βάση τον
προκαθορισμένο κανόνα της ανάλυσης, το αποτέλεσμα αναφέρεται αλλά δεν
θεωρείται εύρημα.</p>

{finding_el('L-3', "Ο συντελεστής του συσσωρευμένου μισθολογικού "
            "ελλείμματος πέρασε κάθε ενδιάμεσο κριτήριο, αλλά δεν τον "
            "υποστήριξε το προηγούμενο βήμα της ανάλυσης, οπότε ένας "
            "προκαθορισμένος κανόνας τον περιορίζει. Αναφέρεται, αλλά δεν "
            "αποτελεί εύρημα.",
            "Ένα ισχυρότερο αποτέλεσμα σε μεταγενέστερο έλεγχο δεν μπορεί "
            "να διορθώσει εκ των υστέρων ένα αδύναμο θεμέλιο.",
            lead="Τι βρέθηκε, και γιατί δεν μετράει.")}

<p>Αυτά αρκούν για να πούμε ότι η κρίση άφησε ένα μετρήσιμο σωρευτικό
αποτύπωμα. Δεν αρκούν για να πούμε πώς ακριβώς αυτό το αποτύπωμα
μεταφράστηκε σε οικονομική δυσκολία μέσα στην ίδια την Ελλάδα χρόνο με τον
χρόνο.</p>

<p>Συνολικά, η διάρκεια φαίνεται να αποτελεί μέρος της εικόνας, όχι
ολόκληρη την εικόνα. Οι χώρες με περισσότερη συσσωρευμένη ανεργία,
περισσότερα χρόνια μη ανάκαμψης των μισθών και μεγαλύτερη επιδείνωση της
στέγασης δηλώνουν μεγαλύτερη δυσκολία ακόμη και αφού ληφθούν υπόψη οι
σημερινές συνθήκες. Αυτό παραμένει, ωστόσο, σχέση μεταξύ χωρών και όχι
αποδεδειγμένη αιτιώδης διαδρομή μέσα στην Ελλάδα.</p>
"""))

# ---- 6. Εκεί Όπου Σταματούν τα Στοιχεία ------------------------------------
CH.append(chapter("limits", "Τι μένει ακόμη ανοιχτό", f"""
<p>Μέχρι εδώ, τα στοιχεία δίνουν μια αρκετά καθαρή εικόνα για αρκετά από
τα βασικά ερωτήματα. Η μεγάλη απόσταση ανάμεσα στη δηλωμένη οικονομική
δυσκολία και την εισοδηματική φτώχεια στην Ελλάδα συνδέεται στενά με
συγκεκριμένες υλικές στερήσεις. Παράλληλα, εμφανίζεται σε μια χώρα όπου η
ανάκαμψη της απασχόλησης δεν συνοδεύτηκε από αντίστοιχη ανάκαμψη στους
μισθούς, στην πραγματική κατανάλωση και στην αγοραστική δύναμη. Βρήκαμε επίσης
ενδείξεις ότι, σε ορισμένους τομείς, δεν έχει σημασία μόνο η σημερινή
κατάσταση αλλά και το βάρος που συσσωρεύτηκε στη διάρκεια της κρίσης.</p>

<p>Αυτή η εικόνα, όμως, δεν απαντά σε όλα. Υπάρχουν δύο ερωτήματα για τα
οποία τα διαθέσιμα δεδομένα δίνουν πιο περιορισμένη απάντηση. Πρώτον, οι
σχέσεις που βρήκαμε για το συσσωρευμένο βάρος εμφανίζονται καθαρά όταν
συγκρίνουμε χώρες μεταξύ τους. Για να δείξουμε όμως αν η ίδια σχέση
εξελίχθηκε μέσα στην Ελλάδα χρόνο με τον χρόνο, χρειάζονται περισσότερες
ετήσιες παρατηρήσεις και μεγαλύτερη μεταβολή μέσα στην ίδια τη χώρα. Με
περίπου μία δεκαετία δεδομένων, οι σχετικές εκτιμήσεις παραμένουν πολύ
αβέβαιες.</p>

<p>Δεύτερον, ενώ μεγάλο μέρος της επιπλέον οικονομικής δυσκολίας που
δηλώνουν τα ελληνικά νοικοκυριά μπορεί να εξηγηθεί στατιστικά από δείκτες
στέρησης, οι δείκτες αυτοί, όμως, προέρχονται από την ίδια έρευνα με τη
δηλωμένη οικονομική δυσκολία. Αυτό κάνει το αποτέλεσμα λιγότερο
ανεξάρτητο. Υπάρχουν επίσης παράγοντες για τους οποίους τα διαθέσιμα
στοιχεία δεν επαρκούν ακόμη ώστε να δώσουν καθαρή εικόνα.</p>

<p>Πάμε να τα δούμε ένα ένα.</p>

<h3>Τι μπορούμε να πούμε για τη μεταβολή μέσα στην ίδια τη χώρα;</h3>

<p>Η προηγούμενη ενότητα έδειξε ότι οι χώρες που έχουν συσσωρεύσει
μεγαλύτερο βάρος ανεργίας, μισθολογικής μη ανάκαμψης και στεγαστικής
πίεσης τείνουν να δηλώνουν μεγαλύτερη οικονομική δυσκολία ακόμη και αφού
ληφθούν υπόψη οι σημερινές συνθήκες. Αυτό είναι ουσιαστικό εύρημα, αλλά
αφορά κυρίως διαφορές μεταξύ χωρών.</p>

<p>Ένα διαφορετικό ερώτημα είναι αν μπορούμε να δούμε την ίδια σχέση να
εξελίσσεται μέσα στην ίδια χώρα: αν, δηλαδή, η οικονομική δυσκολία στην
Ελλάδα αυξανόταν ή υποχωρούσε καθώς συσσωρευόταν ή μειωνόταν το βάρος της
κρίσης. Η ανάλυση εξέτασε και αυτή την εκδοχή, αλλά οι περίπου δέκα
ετήσιες παρατηρήσεις ανά χώρα δεν δίνουν αρκετή ακρίβεια για σαφές
συμπέρασμα.</p>

<div class="finding compact" data-claim-id="V2-5.Y">
<p><em>Τι δείχνουν τα στοιχεία.</em> Σε τρεις συγγενείς ελέγχους, οι
ενδοχωρικές εκτιμήσεις δεν τεκμηρίωσαν καθαρά την αναμενόμενη σχέση.
Επομένως, τα διαθέσιμα δεδομένα δεν αρκούν για να δείξουν αν η οικονομική
δυσκολία μέσα στην Ελλάδα μεταβαλλόταν καθώς συσσωρευόταν το βάρος της
κρίσης.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> Η απουσία
καθαρού ενδοχωρικού αποτελέσματος δεν αναιρεί τις σχέσεις μεταξύ χωρών που
παρουσιάστηκαν προηγουμένως. Απαντά σε διαφορετικό και απαιτητικότερο
ερώτημα. Οι τρεις έλεγχοι είναι επίσης συγγενείς και βασίζονται στα ίδια
δεδομένα, όχι σε τρεις ανεξάρτητες πηγές.</p>
</div>

{subfig('F13A', 'F13', 0,
        "Οι ισχυρότερες ενδείξεις προέρχονται από τις διαφορές μεταξύ χωρών",
        "Βλέπουμε το συσσωρευμένο βάρος μόνο όταν συγκρίνουμε χώρες ή και όταν παρακολουθούμε την ίδια χώρα στον χρόνο;")}

<p>Το Γράφημα {{fig:F13A}} κάνει αυτή τη διάκριση ορατή. Όταν συγκρίνουμε
τις χώρες μεταξύ τους, όσες κουβαλούν μεγαλύτερο συσσωρευμένο βάρος τείνουν
να δηλώνουν και μεγαλύτερη οικονομική δυσκολία. Όταν όμως προσπαθούμε να
παρακολουθήσουμε την ίδια σχέση μέσα σε κάθε χώρα στον χρόνο, οι εκτιμήσεις
γίνονται πολύ πιο αβέβαιες. Άρα γνωρίζουμε αρκετά για το πώς διαφέρουν οι
χώρες μεταξύ τους, αλλά λιγότερα για το πώς εξελίχθηκε ο συγκεκριμένος
μηχανισμός μέσα στην Ελλάδα.</p>

<h3>Πόσο εξαρτάται η εξήγηση από το τι βάζουμε στο μοντέλο;</h3>

<p>Το δεύτερο ανοιχτό ζήτημα αφορά τους <em>δείκτες στέρησης</em> <a
href="#ch{{ch:footprint}}">που είδαμε νωρίτερα</a>, όπως η αδυναμία
κάλυψης ενός απρόοπτου εξόδου, η ανεπαρκής θέρμανση και οι καθυστερήσεις
πληρωμών. Αυτοί οι δείκτες συνδέονται πολύ στενά με τη δηλωμένη οικονομική
δυσκολία και, όταν προστεθούν στο μοντέλο μαζί με την εισοδηματική
φτώχεια, απορροφούν μεγάλο μέρος της ελληνικής υπέρβασης.</p>

<p>Το αποτέλεσμα είναι σημαντικό, αλλά έχει μια βασική ιδιαιτερότητα: οι
δείκτες στέρησης και η οικονομική δυσκολία προέρχονται από την ίδια
έρευνα. Έτσι προκύπτουν δύο εξίσου εύλογες αναλυτικές επιλογές. Αν τους
συμπεριλάβουμε, αξιοποιούμε πληροφορία που βρίσκεται πολύ κοντά στην
καθημερινή οικονομική εμπειρία των νοικοκυριών. Αν τους αποκλείσουμε,
αποφεύγουμε να εξηγούμε μια απάντηση με άλλες απαντήσεις που συλλέχθηκαν
μέσα από το ίδιο εργαλείο μέτρησης. Η ανάλυση εξέτασε και τις δύο εκδοχές,
και η θέση της Ελλάδας αλλάζει δραστικά.</p>

<div class="finding compact" data-claim-id="V2-6.1">
<p><em>Τι δείχνουν τα στοιχεία.</em> Ανάλογα με το αν συμπεριλαμβάνονται
οι δείκτες στέρησης από το ίδιο εργαλείο μέτρησης, το <em>ανεξήγητο
υπόλοιπο</em> της Ελλάδας αλλάζει από θετικό σε αρνητικό και η θέση της μετακινείται
από 3η σε 25η μεταξύ των 27 χωρών.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> Καμία από τις
δύο εκδοχές δεν μπορεί να θεωρηθεί οριστική. Η διαφορά μεταξύ τους δεν
λύνεται παίρνοντας τον μέσο όρο ή επιλέγοντας εκείνη που παράγει το πιο
εύλογο αποτέλεσμα.</p>
</div>

{fig('F14', caption="Μία επιλογή στο μοντέλο αντιστρέφει ολόκληρη την εικόνα")}

<p>Το Γράφημα {{fig:F14}} δείχνει πόσο μεγάλη είναι αυτή η διαφορά. Με τα
ίδια δεδομένα, αλλά διαφορετική απόφαση για τη συμπερίληψη των δεικτών
στέρησης, η Ελλάδα μετακινείται από την τρίτη υψηλότερη στην εικοστή
πέμπτη θέση ως προς το ανεξήγητο υπόλοιπο. Αυτό δεν ακυρώνει τα προηγούμενα
ευρήματα για τη σχέση της οικονομικής δυσκολίας με τη στέρηση. Δείχνει ότι
δεν μπορούμε ακόμη να προσδιορίσουμε με ασφάλεια πόσο από την ελληνική
υπέρβαση πρέπει να θεωρήσουμε πραγματικά «ανεξήγητο» αφού λάβουμε υπόψη
αυτές τις στενά συγγενείς μετρήσεις.</p>

<p>Γι' αυτό κανένα βασικό συμπέρασμα της ανάλυσης δεν εξαρτάται από την
επιλογή ανάμεσα στις δύο εκδοχές.</p>

<details class="disclosure"><summary>Οι δείκτες που έμειναν αναπάντητοι, και οι σχεδιασμοί που δεν δούλεψαν</summary>

<p>Υπάρχουν και ερωτήματα για τα οποία τα διαθέσιμα δεδομένα απλώς δεν
επιτρέπουν ακόμη καθαρή απάντηση. Από τους εννέα τρέχοντες δείκτες που
εξετάστηκαν, τρεις έδωσαν αρκετά σταθερά αποτελέσματα ώστε να
χρησιμοποιηθούν στην κύρια ανάλυση. Για έξι, η στατιστική ισχύς δεν ήταν
αρκετή για σαφή κρίση. Αυτό δεν σημαίνει ότι οι συγκεκριμένοι παράγοντες
δεν έχουν σημασία· σημαίνει ότι με 27 χώρες και περίπου μία δεκαετία
δεδομένων μπορούμε να ανιχνεύσουμε αξιόπιστα μόνο σχετικά μεγάλες
επιδράσεις.</p>

<div class="finding compact" data-claim-id="V2-4.X L-4">
<p><em>Τι δείχνουν τα στοιχεία.</em> Έξι από τους εννέα τρέχοντες δείκτες
παραμένουν χωρίς σαφές συμπέρασμα. Για τον ετήσιο πληθωρισμό τροφίμων και
στέγασης, καθώς και για τον γενικό ετήσιο πληθωρισμό, τα δεδομένα
επιτρέπουν πιο συγκεκριμένους αποκλεισμούς στο μέγεθος επίδρασης που
μπορούσε να ανιχνεύσει η ανάλυση. Ο συσσωρευμένος πληθωρισμός από το 2008
παραμένει χωρίς σαφή απάντηση.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> «Χωρίς σαφές
συμπέρασμα» δεν σημαίνει «χωρίς επίδραση». Οι αποκλεισμοί αφορούν
συγκεκριμένα μεγέθη επίδρασης και όχι την πλήρη απουσία οποιασδήποτε
σχέσης.</p>
</div>

<p>Δύο ακόμη προσεγγίσεις εξετάστηκαν αλλά δεν χρησιμοποιούνται στα τελικά
συμπεράσματα. Η πρώτη ήταν μια «συνθετική Ελλάδα»: μια κατασκευασμένη
χώρα σύγκρισης που θα ακολουθούσε όσο το δυνατόν καλύτερα την Ελλάδα πριν
από την κρίση, ώστε η μεταγενέστερη απόκλιση να μπορεί να εξεταστεί ως
πιθανή επίδρασή της. Στην πράξη, όμως, η συνθετική σύγκριση στηρίχθηκε
σχεδόν εξ ολοκλήρου σε δύο χώρες και δεν πληρούσε τέσσερα από τα έξι
κριτήρια που είχαν καθοριστεί εκ των προτέρων. Για τον λόγο αυτό δεν
χρησιμοποιείται ως τεκμήριο.</p>

<p>Η δεύτερη προσέγγιση ήταν να χρησιμοποιηθεί η εξάπλωση των δεκαέξι
δεικτών <a href="#ch{{ch:footprint}}">του Γραφήματος 3</a> όχι μόνο ως
περιγραφή αλλά και ως προβλεπτικός παράγοντας της οικονομικής δυσκολίας.
Ως περιγραφικό μέτρο παραμένει χρήσιμη: δείχνει πόσο ευρύτερο έγινε το
ελληνικό μειονέκτημα. Ως προβλεπτικός δείκτης, όμως, δεν έδωσε αρκετά
σταθερό αποτέλεσμα ώστε να στηρίξει πρόσθετο συμπέρασμα.</p>

<div class="finding compact" data-claim-id="L-1 L-2">
<p><em>Τι δείχνουν τα στοιχεία.</em> Η συνθετική σύγκριση δεν πληρούσε
τέσσερα από τα έξι προκαθορισμένα κριτήρια και δεν χρησιμοποιείται. Η
εξάπλωση των δεκαέξι δεικτών παραμένει περιγραφικό εύρημα, αλλά δεν
τεκμηριώθηκε ως ανεξάρτητος προβλεπτικός παράγοντας της οικονομικής
δυσκολίας.</p>
<p class="limits"><em>Τι δεν μπορούμε να συμπεράνουμε.</em> Τα
αποτελέσματα αυτά δεν αναιρούν όσα έδειξαν οι υπόλοιπες αναλύσεις. Απλώς
δεν προσθέτουν την επιπλέον απάντηση για την οποία σχεδιάστηκαν.</p>
</div>

</details>

<p>Μέχρι εδώ φτάνει η ποσοτική ανάλυση. Έχει απαντήσει ένα σημαντικό
μέρος του αρχικού ερωτήματος, αλλά όχι κάθε πιθανό μηχανισμό πίσω από την
ελληνική ιδιαιτερότητα. Παράγοντες όπως η εμπιστοσύνη στους θεσμούς, οι
πολιτικές προσαρμογής, η μετανάστευση, η φορολογία, η υγεία και ο τρόπος
με τον οποίο οι άνθρωποι απαντούν σε υποκειμενικές ερωτήσεις μπορεί επίσης
να αποτελούν μέρος της εικόνας. Ορισμένοι εξετάζονται στη συνέχεια με τα
διαθέσιμα στοιχεία· για άλλους μπορούμε μόνο να περιγράψουμε τι γνωρίζουμε
και τι παραμένει ανοιχτό.</p>

<p>Αυτό δεν αφήνει την προηγούμενη εικόνα μετέωρη. Αντίθετα, αφήνει ένα
τελευταίο επίπεδο ερωτημάτων: παράγοντες που μπορεί να συμπληρώνουν την
εικόνα, αλλά δεν μετρήθηκαν αρκετά καλά ή δεν μπορούν να ελεγχθούν με τον
ίδιο τρόπο.</p>
"""))

# ---- 7. Τι Εξακολουθούν να Μη Δείχνουν οι Αριθμοί --------------------------
CH.append(chapter("leftover", "Τι δεν μας λένε ακόμη οι αριθμοί", f"""
<p>Υπάρχει μια απλούστερη εξήγηση που πρέπει να ληφθεί σοβαρά υπόψη: ίσως
οι Έλληνες τείνουν γενικότερα να απαντούν πιο απαισιόδοξα.</p>

<p>Τα στοιχεία που εξετάστηκαν μέχρι εδώ δεν μπορούν να αποκλείσουν πλήρως
αυτή την πιθανότητα. Η ισχυρότερη επιβεβαίωση της δηλωμένης <em>οικονομικής
δυσκολίας</em>, οι συγκεκριμένοι <em>δείκτες στέρησης</em>, προέρχεται από την ίδια
έρευνα. Τα ανεξάρτητα στοιχεία που χρησιμοποιήθηκαν αλλού, όπως οι μισθοί,
η απασχόληση, η πραγματική κατανάλωση ή το ευρύτερο καλάθι δεικτών, δεν έχουν αυτό
το πρόβλημα, αλλά δεν σχεδιάστηκαν για να ελέγξουν άμεσα το ύφος με το
οποίο απαντούν οι Έλληνες.</p>

<h3>Οικονομικές προσδοκίες και ικανοποίηση από τη ζωή</h3>

<div class="ctx-inline" data-context-id="CTX-1">

<p>Ένας καλύτερος έλεγχος είναι να κοιτάξουμε διαφορετικά είδη
υποκειμενικών ερωτήσεων, αντλώντας από ξεχωριστή σύγκριση ύφους απάντησης
που κατασκευάστηκε για αυτό το έργο (reporting_style_cross_indicator.csv).
Αν υπήρχε μια γενικευμένη τάση αρνητικής απάντησης, θα περιμέναμε η
Ελλάδα να εμφανίζεται περίπου εξίσου ακραία σε πολλά διαφορετικά πεδία. Αν
αντίθετα η απόκλιση είναι πολύ εντονότερη στις οικονομικές ερωτήσεις και
ηπιότερη αλλού, αυτό θα ήταν περισσότερο συμβατό με πραγματική οικονομική
πίεση. Πρόκειται εδώ για περιγραφικό στοιχείο, όχι έλεγχο, και ο πίνακας
παρακάτω κάνει αυτή τη σύγκριση απευθείας.</p>

{domain_table_el()}

<p>Η Ελλάδα βρίσκεται σταθερά στις τελευταίες θέσεις της Ευρώπης ως προς
την <em>ικανοποίηση από τη ζωή</em> και στην τελευταία θέση ως προς την
οικονομική δυσκολία και τις <em>οικονομικές προσδοκίες</em>. Το γεγονός ότι οι
οικονομικοί δείκτες είναι ακόμη πιο ακραίοι υποδηλώνει κάποια εξειδίκευση
ως προς το πεδίο, χωρίς να αποκλείει μια ευρύτερη τάση αρνητικής
αναφοράς.</p>

{finding_el('V2-7.1', "Η Ελλάδα βρίσκεται σταθερά ανάμεσα στις χειρότερες "
            "χώρες της Ευρώπης στην ικανοποίηση από τη ζωή και σταθερά η "
            "χειρότερη στην οικονομική δυσκολία και τις προσδοκίες. Η "
            "μεγαλύτερη ακρότητα των οικονομικών δεικτών υποδηλώνει "
            "εξειδίκευση ως προς το πεδίο, αλλά δεν αποκλείει μια ευρύτερη "
            "τάση αρνητικής αναφοράς.",
            "Η Ελλάδα δεν είναι «μέτρια» ως προς την ικανοποίηση από τη "
            "ζωή: μέχρι το 2024 βρίσκεται στη δεύτερη χειρότερη θέση στην "
            "ΕΕ. Παράλληλα, η ίδια η ικανοποίηση από τη ζωή ΑΥΞΗΘΗΚΕ την "
            "περίοδο που εξετάζεται, από 6,2 σε 6,9. Αυτό που χειροτέρεψε "
            "είναι η κατάταξη, επειδή άλλες χώρες βελτιώθηκαν γρηγορότερα. "
            "Τα διαθέσιμα συγκρίσιμα δεδομένα για την ικανοποίηση από τη "
            "ζωή ξεκινούν το 2013, όταν η κρίση βρισκόταν ήδη σε εξέλιξη, "
            "επομένως δεν υπάρχει αντίστοιχο σημείο αναφοράς πριν από την "
            "κρίση.",
            caveat_lead="Τι πρέπει να προσέξουμε.")}

<p>Αυτό το τελευταίο σημείο είναι σημαντικό. Η ικανοποίηση από τη ζωή στην
Ελλάδα αυξήθηκε. Η σχετική θέση της χώρας, όμως, χειροτέρεψε επειδή άλλες
χώρες βελτιώθηκαν περισσότερο. Μια χειρότερη κατάταξη δεν είναι το ίδιο
πράγμα με ένα χειρότερο επίπεδο.</p>

</div>

<h3>Επίπεδο ευημερίας πριν την κρίση</h3>

<p>Ένας ακόμη έλεγχος φτάνει πιο πίσω από την έναρξη των δεδομένων της
Eurostat. Μια διαφορετική ευρωπαϊκή έρευνα δείχνει ότι η Ελλάδα βρισκόταν
ήδη περίπου 0,8 μονάδες κάτω από την ομάδα σύγκρισής της πριν από την
κρίση, υποχώρησε περισσότερο κατά τη διάρκειά της και μέχρι τη δεκαετία
του 2020 είχε ανακτήσει περίπου το αρχικό της επίπεδο, όχι όμως και τη
σχετική της θέση.</p>

<p>Ένα μακροχρόνιο μοτίβο χαμηλότερης δηλωμένης ευημερίας είναι επομένως
εύλογο. Δεν μπορεί όμως να τεκμηριωθεί ως εξήγηση του σημερινού οικονομικού
χάσματος.</p>

{context_el('CTX-7', "επιπλέον στοιχεία από άλλη πηγή",
    "Επίπεδο ευημερίας πριν την κρίση (ESS)",
    '''<p>Σε έξι γύρους μιας ξεχωριστής ευρωπαϊκής έρευνας, κρατώντας
    σταθερές τις ίδιες δώδεκα χώρες κάθε φορά, το επίπεδο της Ελλάδας
    έπεσε και μετά ανέκαμψε, ενώ η θέση της σε σχέση με τις άλλες όχι.
    Πρόκειται για περιγραφική επιβεβαίωση, όχι για τεστ.</p>''',
    "Σε αυτό το ισορροπημένο σύνολο 12 χωρών, η Ελλάδα βρισκόταν ήδη "
    "περίπου 0,8 μονάδες κάτω από τη διάμεσο πριν από την κρίση, "
    "υποχώρησε στο 5,64 το 2010/11 και μέχρι το 2023/24 είχε επιστρέψει "
    "περίπου στο προ κρίσης ΕΠΙΠΕΔΟ της. Η σχετική της θέση, όμως, δεν "
    "ανέκαμψε: το χάσμα από τη διάμεσο είναι μεγαλύτερο από πριν την "
    "κρίση και η Ελλάδα παραμένει τελευταία από τις 12 χώρες από το "
    "2010/11 και μετά. Μια μακροχρόνια τάση χαμηλότερης δηλωμένης "
    "ευημερίας είναι επομένως εύλογη και η γενικότερη απαισιοδοξία ή "
    "«κουλτούρα αναφοράς» ΔΕΝ μπορεί να αποκλειστεί.",
    "Τα δεδομένα ESS δεν μπορούν να ενωθούν με τα δεδομένα EU-SILC σαν να "
    "αποτελούσαν ενιαία χρονοσειρά. Οι μέσοι όροι είναι κατά προσέγγιση "
    "ανακατασκευές από δημοσιευμένα σταθμισμένα ποσοστά και δεν "
    "υποστηρίζουν διαστήματα εμπιστοσύνης, τυπικά σφάλματα ή ελέγχους "
    "σημαντικότητας. Οι κατατάξεις όλων των χωρών επίσης δεν μπορούν να "
    "συγκριθούν άμεσα μεταξύ γύρων, επειδή ο αριθμός συμμετεχουσών χωρών "
    "μεταβάλλεται από 22 έως 30. Η δεκαετία μετά το 2010/11 δεν "
    "παρατηρείται συνεχώς.",
    'European Social Survey Data Portal. <a href="https://ess.sikt.no/en/">πηγή</a>',
    collapse=True)}

<h3>Υγεία</h3>

<p>Η υγεία έχει διαφορετική θέση από τους παράγοντες που ακολουθούν,
επειδή εξετάστηκε άμεσα. Η Ελλάδα έχει ένα από τα υψηλότερα ποσοστά
<em>ανικανοποίητων ιατρικών αναγκών</em> στην ΕΕ, μέχρι το 2024 το
υψηλότερο στην Ένωση και πολλαπλάσιο της τυπικής χώρας-μέλους. Αυτό
αποτελεί από μόνο του σοβαρό στοιχείο για την ποιότητα ζωής στην
Ελλάδα.</p>

<p>Τέσσερις διαφορετικοί δείκτες υγείας ελέγχθηκαν πάνω στην ίδια βάση που
χρησιμοποιήθηκε και για τους υπόλοιπους παράγοντες. Κανένας δεν πέρασε τον
προκαθορισμένο κανόνα ώστε να θεωρηθεί εξήγηση του χάσματος οικονομικής
δυσκολίας.</p>

<p>Τρεις δείκτες, η <em>αυτοαναφερόμενη υγεία</em>, οι <em>μακροχρόνιες
παθήσεις</em> και οι <em>περιορισμοί δραστηριότητας</em>, εμφανίζουν
μάλιστα ένα παράδοξο πρόσημο στις συγκρίσεις μεταξύ χωρών: χώρες με
χειρότερη δηλωμένη υγεία εμφανίζουν λιγότερη δηλωμένη οικονομική δυσκολία.
Όταν όμως συγκρίνουμε κάθε χώρα με το δικό της παρελθόν, η σχέση
αντιστρέφεται προς την αναμενόμενη κατεύθυνση: χρόνια με χειρότερη υγεία
συνδέονται με περισσότερη δυσκολία.</p>

<p>Ο τέταρτος δείκτης, οι ανικανοποίητες ιατρικές ανάγκες, έχει την
αναμενόμενη κατεύθυνση και στις δύο προσεγγίσεις, αλλά το αποτέλεσμα
μεταβάλλεται σημαντικά όταν αφαιρεθεί οποιαδήποτε μεμονωμένη χώρα. Για τον
λόγο αυτό δεν περνά ούτε αυτός τον κανόνα.</p>

<p>Η δύσκολη κατάσταση της υγείας στην Ελλάδα παραμένει πραγματική. Δεν
μετατρέπεται όμως, με αυτά τα δεδομένα, σε τεκμηριωμένη εξήγηση του
συγκεκριμένου χάσματος.</p>

<h3>Μετανάστευση</h3>

<p>Μεγάλος αριθμός Ελλήνων σε ηλικία εργασίας έφυγε από τη χώρα κατά τη
διάρκεια της κρίσης και ένα μέρος τους έχει επιστρέψει. Η μετανάστευση
μπορεί εύλογα να ιδωθεί και ως συνέπεια μιας βαθιά τραυματισμένης αγοράς
εργασίας και ως παράγοντας που αλλάζει τη σύνθεση όσων παραμένουν στη
χώρα. Σε αντίθεση με τους περισσότερους παράγοντες που ακολουθούν, αυτή
ελέγχθηκε άμεσα, ως συγκεντρωτικός προβλεπτικός παράγοντας της οικονομικής
δυσκολίας μεταξύ χωρών.</p>

{context_el('CTX-4', "πιθανή συνέπεια, όχι εξήγηση", "Μετανάστευση",
    '''<p>Όταν η μετανάστευση εξετάστηκε ως συγκεντρωτικός προβλεπτικός
    παράγοντας της οικονομικής δυσκολίας μεταξύ χωρών, δεν προέκυψε σαφής
    στατιστική σχέση.</p>''',
    "Δεν προέκυψε σαφής στατιστική σχέση (p = 0,4006). Με απλά λόγια, με "
    "τα διαθέσιμα δεδομένα δεν μπορούμε να πούμε ότι οι χώρες με "
    "μεγαλύτερη μετανάστευση εμφανίζουν συστηματικά μεγαλύτερη ή "
    "μικρότερη οικονομική δυσκολία.",
    "Το αποτέλεσμα αυτό δεν αποδεικνύει ότι η μετανάστευση δεν έχει "
    "σημασία. Ο συγκεκριμένος έλεγχος εξετάζει μόνο αν υπάρχει μια "
    "συνολική σχέση σε επίπεδο χώρας. Δεν μπορεί να ξεχωρίσει "
    "διαφορετικούς μηχανισμούς: για παράδειγμα, αν η οικονομική δυσκολία "
    "ωθεί ανθρώπους να μεταναστεύσουν, αν η μετανάστευση αλλάζει τη "
    "σύνθεση του πληθυσμού που παραμένει, ή αν οι δύο διαδικασίες "
    "επηρεάζονται από άλλους κοινούς παράγοντες. Επομένως, η μετανάστευση "
    "δεν τεκμηριώνεται εδώ ως ανεξάρτητη εξήγηση, αλλά ούτε και "
    "αποκλείεται ως μέρος της ευρύτερης ιστορίας.",
    "Lazaretou, S. (2016), The Greek brain drain: the new pattern of "
    "Greek emigration during the recent crisis. Economic Bulletin, Bank "
    'of Greece, issue 43, pp. 31-53. <a href="https://www.bankofgreece.gr/'
    'BogEkdoseis/econbull201607.pdf">πηγή</a>')}

<p>Άλλοι παράγοντες εμφανίζονται σχεδόν σε κάθε αφήγηση της ελληνικής
κρίσης, αλλά δεν τεκμηριώθηκαν από αυτή την ανάλυση. Η σιωπηλή παράλειψή
τους θα ήταν παραπλανητική. Η παρουσίασή τους ως ευρημάτων θα ήταν ακόμη
χειρότερη. Καταγράφονται επομένως μόνο ως πιθανοί μηχανισμοί ή ιστορικό
πλαίσιο.</p>

<details class="disclosure"><summary>Άλλοι πιθανοί παράγοντες</summary>

{context_el('CTX-2', "συμπληρωματικό στοιχείο", "Εμπιστοσύνη στους θεσμούς",
    '''<p>Η εμπιστοσύνη στους θεσμούς είναι χαμηλή στην Ελλάδα και υπάρχει
    ένας εύλογος μηχανισμός μέσω του οποίου θα μπορούσε να σχετίζεται με
    την οικονομική ανασφάλεια: ένα νοικοκυριό που δεν πιστεύει ότι θα
    λάβει βοήθεια όταν τη χρειαστεί μπορεί να βιώνει την ίδια οικονομική
    κατάσταση ως πιο επισφαλή. Η παρούσα ανάλυση δεν διαθέτει έλεγχο
    αυτής της υπόθεσης.</p>''',
    "Η εμπιστοσύνη θα μπορούσε εύλογα να επηρεάζει τον τρόπο με τον οποίο "
    "τα νοικοκυριά βιώνουν την ανασφάλεια. Τα διαθέσιμα στοιχεία δεν "
    "τεκμηριώνουν ανεξάρτητη επίδραση.",
    "Η εμπιστοσύνη δεν μπορεί να παρουσιαστεί ως εξήγηση του ανεξήγητου "
    "υπολοίπου ούτε να υπονοηθεί ότι εξετάστηκε και βρέθηκε σημαντική.",
    'OECD (2024), OECD Survey on Drivers of Trust in Public Institutions '
    '2024 Results, Country Notes: Greece. '
    '<a href="https://www.oecd.org/en/publications/'
    'oecd-survey-on-drivers-of-trust-in-public-institutions-2024-results-'
    'country-notes_a8004759-en/greece_56edc018-en.html">πηγή</a>')}

{context_el('CTX-3', "ιστορικό πλαίσιο από τη βιβλιογραφία",
    "Η κρίση και οι πολιτικές προσαρμογής",
    '''<p>Τα προγράμματα προσαρμογής μετά το 2010 αναδιαμόρφωσαν μέσα σε
    μικρό χρονικό διάστημα εισοδήματα, συντάξεις, εργασιακές σχέσεις και
    δημόσιες υπηρεσίες. Αποτελούν το ιστορικό υπόβαθρο σχεδόν όλων των
    σωρευτικών δεικτών που παρουσιάστηκαν νωρίτερα.</p>''',
    "Αποτελούν κρίσιμο ιστορικό πλαίσιο.",
    "Η παρούσα ανάλυση δεν εκτιμά την αιτιώδη συνεισφορά συγκεκριμένων "
    "προγραμμάτων ή μέτρων και δεν μπορεί να αποδώσει συγκεκριμένο "
    "ποσοστό του σωρευτικού βάρους σε κάποια από αυτά.",
    "Andriopoulou, E., Kanavitsa, E. &amp; Tsakloglou, P. (2020), "
    "Decomposing Poverty in Hard Times: Greece 2007-2016. LSE GreeSE "
    'Paper No. 149. <a href="https://www.lse.ac.uk/Hellenic-Observatory/'
    'Publications/GreeSE-Papers">πηγή</a>')}

{context_el('CTX-5', "υπόθεση προς διερεύνηση", "Φορολογικό βάρος και άνιση μεταχείριση",
    '''<p>Δημοσιευμένη έρευνα δείχνει ότι το σύστημα έμμεσης φορολογίας
    στην Ελλάδα έγινε σημαντικά πιο επαχθές για τα νοικοκυριά χαμηλότερου
    εισοδήματος κατά τη διάρκεια της κρίσης. Αν ένα νοικοκυριό
    επιβαρύνθηκε μέσω της φορολογίας με τρόπο που οι δείκτες φτώχειας
    βασισμένοι αποκλειστικά στο εισόδημα καταγράφουν ατελώς, αυτό θα
    μπορούσε να αποτελεί έναν ακόμη μηχανισμό πίσω από το χάσμα που
    περιγράφεται εδώ.</p>''',
    "Η δημοσιευμένη βιβλιογραφία τεκμηριώνει ότι οι έμμεσοι φόροι έγιναν "
    "περισσότερο επιβαρυντικοί για τα χαμηλότερα εισοδήματα κατά τη "
    "διάρκεια της κρίσης.",
    "Η παρούσα ανάλυση δεν εξέτασε τη φορολογία και επομένως δεν μπορεί "
    "να αποδώσει κανένα μέρος του χάσματος οικονομικής δυσκολίας σε "
    "αυτήν. Η βιβλιογραφία αφορά το φορολογικό βάρος, όχι τον "
    "συγκεκριμένο δείκτη αποτελέσματος.",
    "Kaplanoglou, G. (2015), Who Pays Indirect Taxes in Greece? From EU "
    "Entry to the Fiscal Crisis. Public Finance Review 43(4), 529-556. "
    '<a href="https://doi.org/10.1177/1091142113517925">πηγή</a>')}

{context_el('CTX-9', "συμπληρωματικό στοιχείο", "Συγκέντρωση πλούτου από το 2019",
    '''<p>Ανεξάρτητα στοιχεία της ΕΚΤ δείχνουν ότι από την αύξηση κατά 224,8
    δισ. ευρώ στον καθαρό πλούτο των ελληνικών νοικοκυριών μεταξύ των
    μέσων του 2019 και των αρχών του 2026, περίπου το 72,6% κατευθύνθηκε
    στο πλουσιότερο πέμπτο των νοικοκυριών. Το κάτω μισό έλαβε περίπου το
    9,2% της αύξησης, ενώ το μερίδιό του στον συνολικό πλούτο μειώθηκε
    ελαφρά. Αυτό προσφέρει έναν εύλογο τρόπο να συνυπάρχουν δύο
    φαινομενικά αντικρουόμενες εικόνες: η συνολική οικονομική ανάκαμψη
    και η επίμονη οικονομική δυσκολία μεγάλου μέρους των νοικοκυριών. Η
    αύξηση ενός εθνικού συνόλου πλούτου δεν σημαίνει ότι τα οφέλη
    κατανέμονται ομοιόμορφα.</p>''',
    "Οι πειραματικές μετρήσεις κατανομής πλούτου της ΕΚΤ δείχνουν ότι ο "
    "καθαρός πλούτος των ελληνικών νοικοκυριών αυξήθηκε κατά περίπου "
    "224,8 δισ. ευρώ ή 32,2% μεταξύ των μέσων του 2019 και των αρχών του "
    "2026. Περίπου το 72,6% αυτής της αύξησης κατευθύνθηκε στο "
    "πλουσιότερο πέμπτο, ενώ το κάτω μισό έλαβε περίπου το 9,2%. Το "
    "μερίδιο του κάτω μισού στον συνολικό πλούτο μειώθηκε ελαφρά, από "
    "περίπου 9,5% σε 9,4%. Πρόκειται για έναν εύλογο μηχανισμό μέσω του "
    "οποίου η αύξηση του συνολικού πλούτου μπορεί να συνυπάρχει με "
    "επίμονη οικονομική πίεση σε μεγάλο μέρος του πληθυσμού.",
    "Η κατανομή πλούτου δεν εξετάστηκε στα μοντέλα οικονομικής δυσκολίας "
    "αυτής της ανάλυσης και βρίσκεται εν μέρει έξω από το χρονικό "
    "παράθυρο 2015-2024. Δεν αποτελεί επομένως τεκμηριωμένη εξήγηση του "
    "χάσματος των 52,6 μονάδων. Επιπλέον, η αύξηση του καθαρού πλούτου "
    "δεν ισοδυναμεί με αύξηση του διαθέσιμου εισοδήματος ή της "
    "ικανότητας πληρωμής λογαριασμών: μεγάλο μέρος των μεταβολών "
    "προέρχεται από ανατιμήσεις ακινήτων και χρηματοοικονομικών "
    "περιουσιακών στοιχείων. Τέλος, η ίδια η ΕΚΤ χαρακτηρίζει τους "
    "συγκεκριμένους λογαριασμούς πειραματικούς.",
    "European Central Bank, Distributional Wealth Accounts (DWA), Greece, "
    'household sector (S14), 2019 Q2&ndash;2026 Q1. <a href="'
    'https://data.ecb.europa.eu/data/datasets/DWA">πηγή</a>')}


</details>
"""))

# ---- 8. Τι σημαίνουν όλα αυτά ----------------------------------------------
CH.append(chapter("conclusion", "Τι σημαίνουν όλα αυτά", f"""
<div class="ctx-inline" data-context-id="CTX-6">

<p>Τα ελληνικά νοικοκυριά δηλώνουν οικονομική δυσκολία σε ποσοστό πολύ
υψηλότερο από όσο θα περίμενε κανείς με βάση τον επίσημο δείκτη
εισοδηματικής φτώχειας, και αυτή η απόσταση επιμένει εδώ και μία δεκαετία.
Αυτό που διατρέχει όλο το κείμενο είναι ότι κανένας μεμονωμένος επίσημος
αριθμός δεν συλλαμβάνει από μόνος του αυτό που δηλώνουν τα ελληνικά
νοικοκυριά: ο καθένας χάνει κάτι διαφορετικό, και ο δείκτης που πιάνει
ό,τι χάνουν οι άλλοι δεν είναι ο κεντρικός τίτλος. Ένα μέρος της απόστασης
μπορούμε πλέον να το κατανοήσουμε καλύτερα.</p>

<p>Ο <em>AROP</em> μετρά κάτι στενότερο από την οικονομική εμπειρία που
συχνά καλείται να συνοψίσει. Επειδή το όριο φτώχειας μετακινείται μαζί με
το εθνικό εισόδημα, μπορεί να παραμένει σχετικά σταθερός ακόμη και όταν το
βιοτικό επίπεδο έχει υποχωρήσει σημαντικά. Ο <em>AROPE</em> διευρύνει την
εικόνα, αλλά καλύπτει μόνο ένα μέρος του χάσματος. Παράλληλα, η δηλωμένη
οικονομική δυσκολία κινείται μαζί με συγκεκριμένες υλικές στερήσεις, ενώ η
κατάσταση στην εργασία, στην πραγματική κατανάλωση και στην αγοραστική δύναμη
προσθέτει πληροφορία που ο AROP από μόνος του δεν καταγράφει. Η Ελλάδα
κουβαλά επίσης ένα από τα μεγαλύτερα συσσωρευμένα βάρη της Ευρώπης: πρώτη
θέση στις 27 χώρες σε συσσωρευμένη ανεργία και σε επιδείνωση του κόστους
στέγασης, δεύτερη σε συνεχόμενα χρόνια με μισθούς κάτω από το επίπεδο του
2008. Η σημερινή κατάσταση από μόνη της δεν αρκεί για να εξηγήσει τη
δυσκολία· μετράει και το τι πέρασε η κοινωνία στον δρόμο ως εδώ.</p>

<p>Αυτό που ανέκαμψε, επομένως, είναι στενότερο από όσο υπονοεί συχνά η
λέξη «ανάκαμψη». Η απασχόληση βελτιώθηκε ουσιαστικά και η πίεση στη
στέγαση υποχώρησε από τα ακραία επίπεδά της. Το κατά κεφαλήν ΑΕΠ, όμως,
δεν επέστρεψε στο επίπεδο του 2008, οι πραγματικοί μισθοί παρέμειναν πολύ
χαμηλότερα και σε κρίσιμα μέτρα υλικών πόρων και αγοραστικής δύναμης η
Ελλάδα εξακολουθεί να υστερεί σημαντικά από τη διάμεση χώρα της ΕΕ.</p>

<p>Δεν μπορούμε να αποκλείσουμε πλήρως έναν γενικότερα πιο απαισιόδοξο τρόπο
απάντησης. Μπορούμε όμως να αποκλείσουμε την εύκολη εκδοχή του
επιχειρήματος: ότι η δηλωμένη οικονομική δυσκολία δεν έχει υλικό υπόβαθρο.
Οι απαντήσεις των νοικοκυριών συμβαδίζουν με συγκεκριμένες υλικές στερήσεις
και εντάσσονται σε ένα ευρύτερο μοτίβο οικονομικού μειονεκτήματος. Αυτό δεν
σημαίνει ότι
έχουμε εξηγήσει πλήρως το χάσμα των 52,6 ποσοστιαίων μονάδων. Κανένας από
τους ανεξάρτητα μετρημένους μηχανισμούς που εξετάστηκαν δεν μπορεί, μόνος
του και με σταθερό τρόπο, να εξηγήσει ολόκληρο το μέγεθός του. Παραμένουν
παράγοντες και διαδρομές για τους οποίους τα διαθέσιμα δεδομένα δεν δίνουν
ακόμη πλήρη εικόνα.</p>

<p>Ο <em>AROP</em>, λοιπόν, δεν είναι λάθος. Μετρά
ακριβώς αυτό για το οποίο σχεδιάστηκε: ποιος βρίσκεται κάτω από ένα όριο
που ορίζεται σε σχέση με το σημερινό διάμεσο εθνικό εισόδημα. Αυτό όμως
είναι διαφορετικό από το ερώτημα αν τα ελληνικά νοικοκυριά έχουν ανακτήσει
το βιοτικό επίπεδο και την οικονομική ασφάλεια που έχασαν στη διάρκεια
της κρίσης. Για αυτό το δεύτερο ερώτημα, ο AROP από μόνος του δεν
αρκεί.</p>

<p>Ίσως, λοιπόν, το πρόβλημα δεν είναι ότι τα ελληνικά νοικοκυριά δεν
αναγνώρισαν την ανάκαμψη. Είναι ότι η εικόνα της ανάκαμψης που κυριαρχεί
στον δημόσιο λόγο στηρίζεται κυρίως σε δείκτες που δεν αποτυπώνονται στην
καθημερινή οικονομική εμπειρία των νοικοκυριών, όπως στους μισθούς, στην
αγοραστική δύναμη και, τελικά, στην οικονομική τους ασφάλεια. Αυτή η
τελική σύνθεση είναι ερμηνεία των συγγραφέων και όχι νέο εμπειρικό
αποτέλεσμα: προκύπτει άμεσα από όσα έδειξε η ανάλυση ότι χάνει ο AROP από
μόνος του, όχι από κάποιον επιπλέον έλεγχο.</p>

</div>
"""))


# ===========================================================================
#  ΣΕΛΙΔΑ
# ===========================================================================
BASE = ce.base_style((OUT / "build" / "report.html").read_text())

SECTION_ORDER = ["paradox", "footprint", "ruler", "recovery", "duration",
                  "limits", "leftover", "conclusion"]
if sorted(SECTION_ORDER) != sorted(CH_KEYS):
    raise SystemExit(
        "section order does not match the sections actually defined -- "
        f"missing {sorted(set(CH_KEYS) - set(SECTION_ORDER))}, "
        f"unknown {sorted(set(SECTION_ORDER) - set(CH_KEYS))}")

TOC_GLOSS = {
    "paradox": ("Πραγματική δυσκολία ή ελληνική απαισιοδοξία;",
                "Το παράδοξο: δύο επίσημοι δείκτες, ένα χάσμα που αυτό το "
                "κείμενο προσπαθεί να εξηγήσει."),
    "footprint": ("Δεν είναι απλώς μια αίσθηση",
                  "Εξετάζοντας αν η δηλωμένη οικονομική δυσκολία είναι "
                  "διάθεση, ή κάτι πραγματικό."),
    "ruler": ("Χαμήλωσε ο πήχης, όχι η φτώχεια",
              "Γιατί ο επίσημος δείκτης φτώχειας μετά βίας κατέγραψε την "
              "κρίση."),
    "recovery": ("Η απασχόληση ανέκαμψε. Τα νοικοκυριά όχι.",
                 "Τι ανέκαμψε, και τι όχι."),
    "duration": ("Το συσσωρευμένο βάρος της κρίσης",
                 "Αν η διάρκεια της κρίσης έχει ακόμα σημασία σήμερα."),
    "limits": ("Τι μένει ακόμη ανοιχτό",
               "Δύο ερωτήματα στα οποία τα διαθέσιμα δεδομένα δίνουν πιο "
               "περιορισμένη απάντηση."),
    "leftover": ("Τι δεν μας λένε ακόμη οι αριθμοί",
                 "Ποιοι παράγοντες ελέγχθηκαν, και ποιοι όχι."),
    "conclusion": ("Τι σημαίνουν όλα αυτά",
                   "Πώς κλείνει η ιστορία."),
}
if set(TOC_GLOSS) != set(SECTION_ORDER):
    raise SystemExit(
        "the table of contents doesn't match SECTION_ORDER -- "
        f"missing {sorted(set(SECTION_ORDER) - set(TOC_GLOSS))}, "
        f"unknown {sorted(set(TOC_GLOSS) - set(SECTION_ORDER))}")
TOC = ('<nav class="narr-toc" aria-label="Σε αυτό το κείμενο">'
       '<p class="narr-toc-label">Σε αυτό το κείμενο</p><ol>' +
       "".join(f'<li><a href="#ch{{ch:{k}}}">'
               f'<span class="narr-toc-title">{TOC_GLOSS[k][0]}</span>'
               f'<span class="narr-toc-gloss">{TOC_GLOSS[k][1]}</span></a></li>'
               for k in SECTION_ORDER) +
       "</ol></nav>")

BODY = TOC + "".join(CH_BY_KEY[k] for k in SECTION_ORDER)

# ---- headline font, bundled (identical to the English narrative) ----------
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
.fig-jump{{border-bottom:1px dotted var(--series-gr)}}
blockquote{{margin:2.2rem -.1rem;padding:0;border:none;
  font-family:'Fraunces Bundled',Georgia,'Times New Roman',serif;
  font-style:italic;font-weight:500;font-size:1.4rem;line-height:1.36;
  color:var(--text-primary);letter-spacing:-.005em;text-wrap:balance}}
blockquote::before,blockquote::after{{color:var(--series-eu);font-style:normal}}
blockquote::before{{content:"\\00AB"}}
blockquote::after{{content:"\\00BB"}}
.finding{{border-left:3px solid var(--series-gr);padding:.1rem 0 .1rem 1.1rem;
  margin:1.6rem 0}}
.finding p{{margin:0 0 .5rem;font-size:1.06rem}}
.limits{{font:.92rem/1.65 ui-sans-serif,system-ui,sans-serif;
  color:var(--text-secondary);margin:0}}
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
.ctx-collapse{{padding:.7rem 1.2rem}}
.ctx-collapse summary{{cursor:pointer;list-style:none;display:flex;
  flex-wrap:wrap;align-items:baseline;gap:.5rem;padding:.3rem 0}}
.ctx-collapse summary::-webkit-details-marker{{display:none}}
.ctx-collapse summary::before{{content:"+";color:var(--text-secondary);
  font-weight:700;width:1em}}
.ctx-collapse details[open] summary::before{{content:"−"}}
.ctx-collapse .ctx-status{{margin:0}}
.ctx-collapse .ctx-summary-topic{{font-size:.92rem;color:var(--text-primary)}}
.ctx-collapse details>p,.ctx-collapse details>div{{margin-top:.6rem}}
.fig-meta .badge{{display:none}}
.fig-methods{{margin:0 1.1rem 1rem}}
.fig-methods summary{{cursor:pointer;font:600 .78rem/1 ui-sans-serif,
  system-ui,sans-serif;letter-spacing:.04em;color:var(--text-secondary);
  padding:.2rem 0}}
.fig-methods[open] summary{{margin-bottom:.4rem}}
.fig-methods .fig-caveat{{margin:0;font-size:.86rem}}
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
details.disclosure{{border:1px solid var(--border);border-radius:6px;
  margin:1.8rem 0;padding:0 1.1rem}}
details.disclosure summary{{cursor:pointer;font:600 .84rem/1
  ui-sans-serif,system-ui,sans-serif;letter-spacing:.02em;padding:1rem 0}}
details.disclosure[open] summary{{border-bottom:1px solid var(--border)}}
details.disclosure .ctx:last-child{{margin-bottom:1.2rem}}
@media (max-width:34rem){{body{{font-size:1.04rem}}}}
"""

# ---- chart numbers, in Greek ---------------------------------------------
# chart_engine formats every number the charts draw in one place: fmt() for
# axis ticks and tooltips, and two toFixed(3) calls for correlation readouts.
# The shared module stays untouched, since the other three documents are in
# English; this rewrites only the copy of the script embedded in THIS page.
_JS_EL = ce.JS
_JS_SWAPS = [
    ("v.toLocaleString(undefined,{maximumFractionDigits:0})",
     "v.toLocaleString('el-GR',{maximumFractionDigits:0})"),
    ("v.toFixed(d==null?1:d)", "v.toFixed(d==null?1:d).replace('.',',')"),
    ("m.v.toFixed(3)", "m.v.toFixed(3).replace('.',',')"),
]
for _a, _b in _JS_SWAPS:
    if _a not in _JS_EL:
        raise SystemExit(
            "chart_engine's number formatting changed shape; the Greek "
            f"locale patch no longer applies to: {_a}")
    _JS_EL = _JS_EL.replace(_a, _b)

# ---- glossary: bold + hover definition on each term's first mention ------
EL_GLOSS = {
    "AROP": "Ο επίσημος δείκτης εισοδηματικής φτώχειας της ΕΕ: ποσοστό ατόμων με "
        "εισόδημα κάτω από το 60% του διάμεσου εθνικού εισοδήματος.",
    "AROPE": "Ευρύτερος δείκτης της ΕΕ: όποιος πληροί έστω μία από τρεις "
        "συνθήκες — AROP, σοβαρή υλική στέρηση, ή πολύ χαμηλή ένταση εργασίας "
        "στο νοικοκυριό.",
    "EU-SILC": "Η ετήσια πανευρωπαϊκή έρευνα της Eurostat για το εισόδημα και "
        "τις συνθήκες διαβίωσης, πηγή σχεδόν όλων των στοιχείων αυτής της "
        "ανάλυσης.",
    "δείκτης εισοδηματικής φτώχειας": "Ο ίδιος δείκτης με τον AROP, όπως "
        "εξηγείται αμέσως παρακάτω στο κείμενο.",
    "δηλωμένη οικονομική δυσκολία": "Το ποσοστό νοικοκυριών που δηλώνουν στην "
        "EU-SILC ότι τα βγάζουν πέρα «με δυσκολία» ή «με μεγάλη δυσκολία».",
    "φτώχεια με σταθερό όριο": "Η φτώχεια όπως θα μετριόταν αν το όριο έμενε "
        "σταθερό στην πραγματική του αξία του 2008, αντί να προσαρμόζεται "
        "κάθε χρόνο στο τρέχον εισόδημα.",
    "καθυστερήσεις στην πληρωμή λογαριασμών": "Ποσοστό νοικοκυριών που δεν "
        "κατάφεραν να πληρώσουν εγκαίρως λογαριασμό, ενοίκιο ή δόση δανείου "
        "τους τελευταίους 12 μήνες.",
    "αδυναμία κάλυψης ενός απρόοπτου εξόδου": "Ποσοστό νοικοκυριών που δεν θα "
        "μπορούσαν να καλύψουν ένα απρόβλεπτο έξοδο ίσο με το εθνικό όριο "
        "φτώχειας από δικούς τους πόρους.",
    "ανεπαρκή θέρμανση του σπιτιού": "Ποσοστό νοικοκυριών που δηλώνουν ότι δεν "
        "μπορούν να διατηρήσουν το σπίτι τους επαρκώς ζεστό.",
    "υλική στέρηση": "Ποσοστό νοικοκυριών που δεν μπορούν να αντεπεξέλθουν "
        "οικονομικά σε αρκετά από ένα σύνολο βασικών αγαθών και αναγκών.",
    "πραγματικοί μισθοί": "Οι μισθοί προσαρμοσμένοι για τον πληθωρισμό, ώστε να "
        "δείχνουν πραγματική αγοραστική δύναμη και όχι μόνο ονομαστική αύξηση.",
    "πραγματικής ατομικής κατανάλωσης": "Η αξία των αγαθών και υπηρεσιών που "
        "πράγματι καταναλώνουν τα νοικοκυριά, προσαρμοσμένη για τις διαφορές "
        "τιμών ανάμεσα στις χώρες.",
    "συσσωρευμένη ανεργία": "Πόση επιπλέον ανεργία, πάνω από το επίπεδο πριν "
        "την κρίση, συσσωρεύτηκε σε μια χώρα χρόνο με τον χρόνο από το 2009.",
    "διάρκεια μισθολογικής μη ανάκαμψης": "Πόσα συνεχόμενα χρόνια οι "
        "πραγματικοί μισθοί μιας χώρας παρέμειναν κάτω από το επίπεδο του "
        "2008.",
    "σωρευτική επιδείνωση του κόστους στέγασης": "Πόσο επίμονα και για πόσο "
        "καιρό επιδεινώθηκε η επιβάρυνση από το κόστος στέγασης, αθροιστικά "
        "στον χρόνο.",
    "αγοραστική πίεση": "Πόσο έχουν ανέβει οι τιμές σε σχέση με τους μισθούς, "
        "δηλαδή πόση αγοραστική δύναμη έχασαν στην πράξη τα νοικοκυριά.",
    "συσσωρευμένος πληθωρισμός": "Ο πληθωρισμός αθροισμένος έτος με έτος από "
        "ένα σημείο αναφοράς, αντί να μετριέται μόνο ετησίως.",
    "δείκτες στέρησης": "Οι επιμέρους δείκτες υλικής στέρησης — "
        "καθυστερήσεις, απρόοπτα έξοδα, θέρμανση — που μαζί συνθέτουν την "
        "εικόνα της οικονομικής πίεσης.",
    "ικανοποίηση από τη ζωή": "Η αυτοαναφερόμενη γενική ικανοποίηση των "
        "ανθρώπων από τη ζωή τους, σε κλίμακα 0 έως 10, όπως καταγράφεται "
        "στην EU-SILC.",
    "οικονομικές προσδοκίες": "Το πόσο αισιόδοξα ή απαισιόδοξα βλέπουν τα "
        "νοικοκυριά την οικονομική τους κατάσταση για τον επόμενο χρόνο.",
    "ανικανοποίητων ιατρικών αναγκών": "Ποσοστό ατόμων που δήλωσαν ότι "
        "χρειάζονταν ιατρική εξέταση ή θεραπεία αλλά δεν την έλαβαν, συνήθως "
        "λόγω κόστους ή αναμονής.",
    "αυτοαναφερόμενη υγεία": "Το πώς αξιολογεί το ίδιο το άτομο τη γενική του "
        "κατάσταση υγείας, από πολύ καλή έως πολύ κακή.",
    "μακροχρόνιες παθήσεις": "Ποσοστό ατόμων που δηλώνουν ότι πάσχουν από "
        "χρόνιο πρόβλημα υγείας διάρκειας τουλάχιστον έξι μηνών.",
    "περιορισμοί δραστηριότητας": "Ποσοστό ατόμων που δηλώνουν περιορισμό στις "
        "καθημερινές τους δραστηριότητες λόγω προβλήματος υγείας.",
    "μακροχρόνια ανεργία": "Ποσοστό του εργατικού δυναμικού που βρίσκεται "
        "άνεργο για 12 μήνες ή περισσότερο.",
}

_main = ce.apply_glossary(resolve_fig_nums(resolve_refs(BODY)), EL_GLOSS)

_TITLE_EL = "Αν η Ελλάδα ανέκαμψε, γιατί τόσα νοικοκυριά εξακολουθούν να δυσκολεύονται;"

PAGE = f"""<!doctype html><html lang="el"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_TITLE_EL}</title>{BASE}
<style>{ce.CSS}
{ce.TERM_CSS}
:root{{--gr:var(--series-gr);--eu:var(--series-eu)}}
{NARR_CSS}</style></head><body>
<header class="masthead">
<p class="rubric">Το ελληνικό παράδοξο της φτώχειας</p>
<h1>{_TITLE_EL}</h1>
<p class="standfirst">Η αγορά εργασίας της Ελλάδας ανέκαμψε ταχύτερα από τα
νοικοκυριά της. Η απόσταση ανάμεσα στην εισοδηματική φτώχεια και τη δηλωμένη
δυσκολία δείχνει τι αφήνουν έξω οι τίτλοι της ανάκαμψης: ένα μετακινούμενο
όριο φτώχειας, τραυματισμένους μισθούς, πίεση στην αγοραστική δύναμη και τη
μακρά σκιά της κρίσης.</p>
<div class="stat-pair">
  <div class="stat stat--official">
    <span class="n">1 στα 5</span>
    <p class="pct">19,6%</p>
    <p class="l"><b>Άτομα</b> σε κίνδυνο φτώχειας, ο επίσημος δείκτης</p>
  </div>
  <div class="stat stat--lived">
    <span class="n">2 στα 3</span>
    <p class="pct">66,7%</p>
    <p class="l"><b>Νοικοκυριά</b> που δυσκολεύονται να τα βγάλουν πέρα</p>
  </div>
</div>
<p class="table-legend">Αυτή είναι η ελληνική έκδοση του κειμένου. Τα
δεδομένα, οι υπολογισμοί και τα ευρήματα είναι τα ίδια με την <a
href="narrative.html">αγγλική έκδοση</a>· το στατιστικό παράρτημα, στο οποίο
παραπέμπουν τα γραφήματα, παραμένει στα αγγλικά.</p>
</header>
{_main}
<script>{_JS_EL}</script>
<script>
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

# ---- checks -----------------------------------------------------------------
missing_f = [f for f in _FROZEN if f not in _used]
if missing_f:
    raise SystemExit(f"narrative figures selected but not placed: {missing_f}")
extra_f = [f for f in _used if f not in _FROZEN]
if extra_f:
    raise SystemExit(f"figures placed but not in the frozen selection: {extra_f}")

required = [i for i in claims.index
            if str(claims.loc[i, "narrative"]).strip().lower() == "body"]
if not required:
    raise SystemExit("no claims required in the narrative -- the check is vacuous")
_placed_ids = {tok for m in re.finditer(r'data-claim-id="([^"]*)"', PAGE)
               for tok in m.group(1).split()}
absent = [i for i in required if i not in _placed_ids]
if absent:
    raise SystemExit(f"claims required in the narrative but absent: {absent}")

# A substring check only proves the id string appears somewhere on the
# page -- an empty tag carrying just the attribute would pass it. What the
# register actually requires is a container whose own text carries the
# status label, the permitted interpretation, the limitation and the
# citation together. audit_parity.py --release only reads narrative.html
# (the register is English by construction), so this build has no
# language-matched completeness signal of its own to run -- but every
# container still has to be real, not empty, so a hollow one is rejected
# here on the same principle: found but with no text at all is exactly
# what a zero-content marker would produce.
from claim_anchors import context_containers
for cid in ctx.index:
    found = context_containers(PAGE, cid)
    if not found:
        raise SystemExit(f"context entry {cid} never placed")
    if not any(re.sub(r"\s+", "", c) for c in found):
        raise SystemExit(f"context entry {cid} container is empty")

# A typed figure number defeats resolve_fig_nums() the same way a typed
# "Figure N" would in the English narrative -- checked here against the
# Greek word instead.
_src = Path(__file__).read_text()
_src_prose = re.sub(r"^.*?_FROZEN = ", "", _src, count=1, flags=re.S)
_src_prose = "\n".join(l for l in _src_prose.splitlines()
                       if not l.lstrip().startswith("#"))
_typed = [" ".join(m.group(0).split())
          for m in re.finditer(r".{0,40}\bΓράφημα \d+\b.{0,25}", _src_prose)
          if "{fig:" not in m.group(0) and "fignum" not in m.group(0)]
if _typed:
    raise SystemExit(
        "figure numbers typed into prose instead of {fig:FID} tokens: "
        + "; ".join(_typed[:3]))

stripped = re.sub(r"<script.*?</script>", " ", PAGE, flags=re.S)
visible = html.unescape(re.sub(r"<[^>]+>", " ", stripped))
BANNED = ["V2-", "CTX-", "L-1", "L-2", "L-3", "L-4", "frozen claim", "aic_pps_pc",
          "ltu_rate", "wadj_a01", "data-claim-id"]
leaked = [b for b in BANNED if b in visible]
if leaked:
    raise SystemExit(f"internal vocabulary visible in the narrative: {leaked}")

# The findings/context boxes are allowed their own precise statistics
# (matching the English narrative's rule); the surrounding Greek prose is
# checked for leaked English statistical jargon, the same words the English
# self-check bans in its own prose.
prose = re.sub(r"<figure class=\"figure\".*?</figure>", " ", stripped, flags=re.S)
prose = re.sub(r'<div class="(?:finding|ctx)(?:\s[^"]*)?".*?</div>', " ", prose, flags=re.S)
prose = html.unescape(re.sub(r"<[^>]+>", " ", prose))
JARGON = ["bootstrap", "p-value", "coefficient", "specification", "estimator",
          "fixed effects", "statistically significant", "confidence interval",
          "regression", "multiplicity", "residual"]
found = [j for j in JARGON if j in prose.lower()]
if found:
    raise SystemExit(f"jargon in the companion's own prose: {found}")

# An untranslated reader-facing string in a figure is a missing translation,
# not a default. The localizer collects them all rather than stopping at the
# first, so one build reports the whole list.
if _fig_missing:
    raise SystemExit(
        "untranslated figure strings (add them to el_figure_strings.py):\n  "
        + "\n  ".join(sorted(_fig_missing)))

# ---- the Greek editorial standard, enforced -------------------------------
# Reader-visible text only. `visible` above strips <script> but not <style>,
# which is harmless for the id checks and fatal for the decimal one: a CSS
# rgba(11,11,11,0.10) is not a number a reader ever sees.
readable = re.sub(r"<style.*?</style>", " ", stripped, flags=re.S)
readable = html.unescape(re.sub(r"<[^>]+>", " ", readable))
# docs/greek_editorial_standard.md is the agreed style for this edition. The
# rules below are the ones a machine can check, so they fail the build rather
# than waiting for a reviewer to catch them again. Everything else in that
# document is enforced by the read-aloud pass.

# Internal governance vocabulary, in either language. The English narrative
# bans the claim ids; this edition also has to ban the stage and candidate
# labels, which a literal translation happily carried into reader-facing text.
GOVERNANCE = ["παγωμέν", "στάδι", "πάνελ", "(C1)", "(C5)", " E3 ", " E7 ",
              "FDR", "bootstrap"]
gov = [g for g in GOVERNANCE if g in readable]
if gov:
    raise SystemExit(f"project-governance vocabulary visible in Greek: {gov}")

# Translationese the review flagged: each of these read as English wearing
# Greek words, and each has an agreed replacement in the standard.
CALQUES = ["συγκινείται", "μέσο-υπολογ", "στασιμοποιήθηκαν", "άγκιστρο",
           "κουβαλά πληροφορία", "κουβαλούν πληροφορία", "δείχνει προς",
           "επέζησε", "αρκετά σκληρά", "ως προφανές όχι", "ταμπλό",
           "διάμεσος τιμή", "φτώχεια εισοδήματος", "προσαρμοσμένη στους μισθούς"]
calq = [c for c in CALQUES if c in readable]
if calq:
    raise SystemExit(f"banned translationese in the Greek edition: {calq}")

# Greek decimal convention. A decimal point between digits in visible text is
# English formatting that survived a copy from the source CSVs. Thousands
# separators are full stops, so only digit.digit with one or two decimals is
# the giveaway; four-digit groups (14.770) are legitimate.
# Now that the figures are localized too, this covers the whole page rather
# than the article's prose alone: a decimal point in a chart label or a
# fallback table is as wrong as one in a paragraph.
readable_prose = re.sub(r"<style.*?</style>", " ", stripped, flags=re.S)
readable_prose = html.unescape(re.sub(r"<[^>]+>", " ", readable_prose))
# An abbreviation has to be introduced before it is used. This caught a real
# regression: a copy-editing pass shortened the AROPE sentence and removed the
# only place the acronym was ever expanded.
#
# Scoped to the reading path rather than the whole page. A figure's axis or
# fallback table names a measure in two words because that is all a label has
# room for, and F21's basket legitimately lists AROPE as one of its sixteen
# indicators before the prose gets to it. What has to be defined first is the
# term the reader meets in a sentence.
_reading_path = re.sub(r"<figure class=\"figure\".*?</figure>", " ", stripped, flags=re.S)
_reading_path = re.sub(r"<style.*?</style>", " ", _reading_path, flags=re.S)
_reading_path = html.unescape(re.sub(r"<[^>]+>", " ", _reading_path))
_reading_path = " ".join(_reading_path.split())   # the source is hard-wrapped
DEFINED_FIRST = [("AROP", "κίνδυνος φτώχειας"),
                 ("AROPE", "κοινωνικού αποκλεισμού"),
                 ("ΜΑΔ", "μονάδες αγοραστικής δύναμης")]
for _abbr, _expansion in DEFINED_FIRST:
    _first = re.search(rf"\b{_abbr}\b", _reading_path)
    # The gloss may come just before the acronym or, more usually, in
    # parentheses straight after it: «ο AROPE (κίνδυνος φτώχειας ή κοινωνικού
    # αποκλεισμού)». Both introduce the term; what fails is a first use with
    # no gloss anywhere near it.
    _where = _reading_path.find(_expansion)
    if _first and not (0 <= _where <= _first.start() + 90):
        raise SystemExit(
            f"{_abbr} is used before it is explained; the reader meets it "
            f"with no definition (expected '{_expansion}' earlier)")

en_decimals = re.findall(r"\d+\.\d{1,2}(?!\d)", readable_prose)
if en_decimals:
    raise SystemExit(
        f"English decimal points in visible Greek text: {en_decimals[:8]}")

# Also prose-scoped, and for two reasons: chart_engine renders an empty
# fallback-table cell as &mdash; and its tooltip script uses one for a null,
# so the lifted English figures and the shared chart engine both legitimately
# contain em dashes. readable_prose has scripts, styles and figures already
# removed and its entities unescaped, so the bare character is the test.
if "—" in readable_prose:
    raise SystemExit("em dash in the Greek edition; the standard forbids it")

# Sentence case for headings: after the first word, a heading should not read
# as English Title Case. Two or more capitalised words after the first is the
# signature of a translated headline.
for _h in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", PAGE, re.S):
    _words = [w for w in html.unescape(re.sub(r"<[^>]+>", " ", _h)).split()[1:]
              if len(w) > 3]
    _caps = [w for w in _words if w[0].isupper() and not w.isupper()]
    # Sentence-initial capitals after a full stop are legitimate, so allow one
    # per sentence boundary in the heading.
    if len(_caps) > _h.count(".") + 1:
        raise SystemExit(f"heading looks Title Cased, not sentence case: {_h}")

(OUT / "narrative_el.html").write_text(PAGE)
print(f"wrote output/narrative_el.html  {len(PAGE):,} chars")
