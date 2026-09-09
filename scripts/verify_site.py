"""The landing pages (site/index.html, site/el.html) sit outside the
claim/parity system that keeps the four canonical documents in sync, and
that is exactly how index.html went stale once already: the headline gap,
the year, the ranks and the one-line finding all drifted from what the
analysis currently says, while every other document was checked on every
build. This gate closes that gap in coverage, for both languages. For each
landing page it checks two things:

  * every number the page states matches the current canonical data
    (data/processed/e_descriptives.csv for the latest year, and the frozen
    V2-1.2 claim for the period average), formatted the way that language
    formats it -- so a rewrite of the finding cannot silently leave a stale
    figure behind, and a future data refresh cannot silently leave a
    landing page behind either;
  * every internal link on the page points to a file the deploy workflow
    will actually publish -- read from pages.yml's own copy list, not a
    second hardcoded list that could drift from the first.

It also checks something broader than the two landing pages: every
filename pages.yml renames at deploy time (report.html for v2_report.html,
for instance) must not still be referenced by its pre-rename name anywhere
in the canonical documents themselves -- the appendix was once renamed to
appendix.html for a shorter URL while every figure in every document still
linked to it internally as statistical_appendix.html#F1, and none of that
showed up until a reader hit the 404 on a phone.

This does not replace editorial judgement about what a page should say. It
only catches numbers and links that stop matching their source.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"

F = []


def check(name, ok, detail=""):
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f"\n         {detail}" if detail and not ok else ""))


# ---------------------------------------------------------------------------
#  Canonical numbers, computed once, shared by every landing page's check.
# ---------------------------------------------------------------------------
desc = pd.read_csv(ROOT / "data" / "processed" / "e_descriptives.csv")
latest = desc.loc[desc["time"].idxmax()]
year = int(latest["time"])

ranks = pd.read_csv(ROOT / "data" / "processed" / "e_descriptive_ranks.csv")


def rank_of(variable):
    row = ranks[(ranks["variable"] == variable) & (ranks["time"] == year)]
    if row.empty:
        raise SystemExit(f"no rank row for {variable} in {year}")
    return int(row.iloc[0]["gr_rank"])


subj_rank, arop_rank = rank_of("subjective_poverty"), rank_of("arop")

claims = pd.read_csv(ROOT / "data" / "processed" / "e_final_claims.csv").set_index("id")
gap_wording = claims.loc["V2-1.2", "canonical_wording"]
gap_match = re.search(r"(\d+\.\d+) points", gap_wording)
if not gap_match:
    raise SystemExit(f"could not read the average gap out of V2-1.2: {gap_wording!r}")
avg_gap_en = gap_match.group(1)

if not PAGES_WORKFLOW.exists():
    raise SystemExit(f"missing {PAGES_WORKFLOW}")
workflow = PAGES_WORKFLOW.read_text(encoding="utf-8")
published = set(re.findall(r"_site/([\w.-]+\.html)", workflow))
if not published:
    raise SystemExit(f"no 'cp ... _site/*.html' lines found in {PAGES_WORKFLOW}")

# Carousel card image and alt text come from two different places -- the
# image from scripts/render2.py's own render, the alt text hand-authored in
# this HTML -- and that split is exactly how alt text once went stale: a
# card's visible content changed (a lede line added, a closing card
# rewritten) without its alt text following. titles.json is written by the
# same render step that draws the cards, so checking every alt against it
# catches that drift at its source instead of trusting the two copies to
# stay in sync.
import json as _json
TITLES_PATH = ROOT / "site" / "assets" / "carousel" / "titles.json"
if not TITLES_PATH.exists():
    raise SystemExit(f"missing {TITLES_PATH}")
CAROUSEL_TITLES = _json.loads(TITLES_PATH.read_text(encoding="utf-8"))


def el_decimal(text):
    """1.234 -> 1,234, the only decimal convention the Greek page uses."""
    return text.replace(".", ",")


# ---------------------------------------------------------------------------
#  One landing page's checks, parameterised by language so the same
#  canonical numbers are checked in each language's own formatting.
# ---------------------------------------------------------------------------
def check_page(path, lang):
    if not path.exists():
        raise SystemExit(f"missing {path}")
    page = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)

    pct = (lambda v: f"{v:.1f}%") if lang == "en" else (lambda v: el_decimal(f"{v:.1f}%"))

    def _ordinal_en(n):
        if n == 1:
            return "highest of 27"
        suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix} highest of 27"

    rank_text = (_ordinal_en if lang == "en" else (lambda n: f"{n}η θέση"))
    avg_gap = avg_gap_en if lang == "en" else el_decimal(avg_gap_en)
    unexplained_word = "unexplained" if lang == "en" else "ανεξήγητο"

    expected = {
        "subjective poverty rate": pct(latest["gr_subjective_poverty"]),
        "AROP rate": pct(latest["gr_arop"]),
        "EU subjective-poverty median": pct(latest["eu_subjective_poverty"]),
        "EU AROP median": pct(latest["eu_arop"]),
    }
    for label, text in expected.items():
        check(f"[{lang}] states the current {label} ({year}: {text})",
              text in page, f"{text!r} not found in {rel}")

    check(f"[{lang}] states the current subjective-poverty rank ({subj_rank})",
          rank_text(subj_rank) in page,
          f"{rank_text(subj_rank)!r} not found in {rel}")
    check(f"[{lang}] states the current AROP rank ({arop_rank})",
          rank_text(arop_rank) in page,
          f"{rank_text(arop_rank)!r} not found in {rel}")

    check(f"[{lang}] states the current average gap ({avg_gap}, per V2-1.2)",
          avg_gap in page, f"{avg_gap!r} not found in {rel}")

    # The old English page's "Most of the rest is duration" / "stops being a
    # cross-country outlier" framing overclaimed a settled explanation. The
    # current, hedged finding is that most of the gap remains unexplained;
    # every landing page must say so, not the opposite.
    check(f'[{lang}] says the gap remains largely unexplained, not "explained"',
          unexplained_word in page.lower()
          and "cross-country outlier" not in page.lower())

    links = sorted(set(re.findall(r'href="([\w.-]+\.html)"', page)))
    missing_links = [l for l in links if l not in published]
    check(f"[{lang}] every internal link will be published",
          not missing_links,
          f"linked but not in pages.yml's copy list: {missing_links}")

    # Local <img src="assets/...">/og:image references have no equivalent to
    # pages.yml's html copy list to check against -- verify_site.py checked
    # the .html links, so it checks these the same way: the referenced file
    # must actually exist under site/, or the image silently 404s once
    # deployed (the same class of bug the appendix rename caught).
    local_imgs = sorted(set(re.findall(r'(?:src|content)="(?:https://parastelios\.github\.io/'
                                        r'greece-poverty-analysis/)?(assets/[\w./-]+)"', page)))
    missing_imgs = [i for i in local_imgs if not (ROOT / "site" / i).exists()]
    check(f"[{lang}] every referenced local image exists under site/",
          not missing_imgs, f"referenced but missing: {missing_imgs}")

    titles = CAROUSEL_TITLES[lang]
    stale_alts = []
    for m in re.finditer(r'src="assets/carousel/(el|en)-(\d+)\.png"[^>]*alt="([^"]*)"', page):
        card_lang, n, alt = m.group(1), int(m.group(2)), m.group(3)
        if card_lang != lang:
            continue
        if n < 1 or n > len(titles):
            stale_alts.append(f"card {n}: no such title (only {len(titles)} cards)")
            continue
        if titles[n - 1] not in alt:
            stale_alts.append(f"card {n}: alt does not contain current title {titles[n - 1]!r}")
    check(f"[{lang}] every carousel alt text matches its card's current title",
          not stale_alts, "; ".join(stale_alts))


# ---------------------------------------------------------------------------
#  Cross-document links: every hardcoded output/*.html -> output/*.html
#  reference (the "Show the numbers" links every figure carries to the
#  statistical appendix, for instance) has to survive whatever renaming
#  pages.yml does at deploy time. This is the actual bug this check exists
#  for: the appendix was deployed as appendix.html for a shorter URL, but
#  every document links to it internally as statistical_appendix.html#F1,
#  a name baked into dozens of cross-references across four generated
#  documents -- and none of that showed up in the two checks above, which
#  only look at the landing pages. Catch it generally: for every rename
#  pages.yml performs (source name != deployed name), no canonical
#  document may still reference the source name.
# ---------------------------------------------------------------------------
renames = [(m.group(1), m.group(2))
           for m in re.finditer(r"cp\s+output/(\S+\.html)\s+_site/(\S+\.html)", workflow)
           if m.group(1) != m.group(2)]
canonical_docs = sorted((ROOT / "output").glob("*.html"))
for old_name, new_name in renames:
    offenders = []
    for doc in canonical_docs:
        text = doc.read_text(encoding="utf-8")
        if f'"{old_name}#' in text or f'"{old_name}"' in text:
            offenders.append(doc.relative_to(ROOT).as_posix())
    check(f'no canonical document still links to "{old_name}" '
          f'(deployed as "{new_name}")',
          not offenders, f"found in: {offenders}")

check_page(ROOT / "site" / "index.html", "en")
check_page(ROOT / "site" / "el.html", "el")

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} landing-page checks pass")
if bad:
    raise SystemExit("LANDING PAGE CHECKS FAILED: " + "; ".join(sorted(set(bad))))
