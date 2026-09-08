"""site/index.html is outside the claim/parity system that keeps the four
canonical documents in sync, and that is exactly how it went stale: the
headline gap, the year, the ranks and the one-line finding all drifted from
what the analysis currently says, while every other document was checked on
every build. This gate closes that gap in coverage. It checks two things:

  * every number the landing page states matches the current canonical data
    (data/processed/e_descriptives.csv for the latest year, and the frozen
    V2-1.2 claim for the period average) -- so a rewrite of the finding
    cannot silently leave a stale figure behind, and a future data refresh
    cannot silently leave the landing page behind either;
  * every internal link on the landing page points to a file the deploy
    workflow will actually publish -- read from pages.yml's own copy list,
    not a second hardcoded list that could drift from the first.

This does not replace editorial judgement about what the page should say.
It only catches numbers and links that stop matching their source.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "index.html"
PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"

F = []


def check(name, ok, detail=""):
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f"\n         {detail}" if detail and not ok else ""))


if not SITE.exists():
    raise SystemExit(f"missing {SITE}")
page = SITE.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
#  Numbers: the landing page's stat tiles and headline gap against the
#  current canonical descriptives and the frozen V2-1.2 claim.
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


expected = {
    "subjective poverty rate": (f"{latest['gr_subjective_poverty']:.1f}%",
                                 latest["gr_subjective_poverty"]),
    "AROP rate": (f"{latest['gr_arop']:.1f}%", latest["gr_arop"]),
    "EU subjective-poverty median": (f"{latest['eu_subjective_poverty']:.1f}%",
                                      latest["eu_subjective_poverty"]),
    "EU AROP median": (f"{latest['eu_arop']:.1f}%", latest["eu_arop"]),
}
for label, (text, _) in expected.items():
    check(f"landing page states the current {label} ({year}: {text})",
          text in page, f"{text!r} not found in {SITE.relative_to(ROOT)}")

subj_rank, arop_rank = rank_of("subjective_poverty"), rank_of("arop")
check(f"landing page states the current subjective-poverty rank ({subj_rank})",
      f"rank {subj_rank}" in page.lower(), f"'rank {subj_rank}' not found")
check(f"landing page states the current AROP rank ({arop_rank})",
      f"rank {arop_rank}" in page.lower(), f"'rank {arop_rank}' not found")

claims = pd.read_csv(ROOT / "data" / "processed" / "e_final_claims.csv").set_index("id")
gap_wording = claims.loc["V2-1.2", "canonical_wording"]
gap_match = re.search(r"(\d+\.\d+) points", gap_wording)
if not gap_match:
    raise SystemExit(f"could not read the average gap out of V2-1.2: {gap_wording!r}")
avg_gap = gap_match.group(1)
check(f"landing page states the current average gap ({avg_gap} points, per V2-1.2)",
      avg_gap in page, f"{avg_gap!r} not found in {SITE.relative_to(ROOT)}")

# The old "Most of the rest is duration" / "stops being a cross-country
# outlier" framing overclaimed a settled explanation. The current, hedged
# finding is that most of the gap remains unexplained; the landing page
# must say so, not the opposite.
check('landing page says the gap remains largely unexplained, not "explained"',
      "unexplained" in page.lower() and "cross-country outlier" not in page.lower())

# ---------------------------------------------------------------------------
#  Links: every internal .html link on the landing page must resolve to a
#  file the deploy workflow actually publishes, per pages.yml's own copy
#  list -- read from there, not duplicated here, so the two cannot drift.
# ---------------------------------------------------------------------------
if not PAGES_WORKFLOW.exists():
    raise SystemExit(f"missing {PAGES_WORKFLOW}")
workflow = PAGES_WORKFLOW.read_text(encoding="utf-8")
published = set(re.findall(r"_site/([\w.-]+\.html)", workflow))
if not published:
    raise SystemExit(f"no 'cp ... _site/*.html' lines found in {PAGES_WORKFLOW}")

links = sorted(set(re.findall(r'href="([\w.-]+\.html)"', page)))
missing_links = [l for l in links if l not in published]
check("every internal link on the landing page will be published",
      not missing_links,
      f"linked but not in pages.yml's copy list: {missing_links}")

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} landing-page checks pass")
if bad:
    raise SystemExit("LANDING PAGE CHECKS FAILED: " + "; ".join(sorted(set(bad))))
