"""Automated checks for every figure the shared engine renders.

Four failure modes, each of which this project has already produced at least
once, and each of which becomes fifteen times more expensive once the full set
is built.
"""
import hashlib
import html as htmlmod
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [p for p in [ROOT / "output" / "prototype.html",
                       ROOT / "output" / "batch1.html",
                       ROOT / "output" / "report.html"] if p.exists()]

F = []
def check(name, ok, detail=""):
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"\n         {detail}" if detail and not ok else ""))


for path in TARGETS:
    raw = path.read_text()
    figs = re.findall(r'<figure class="figure" id="([^"]+)".*?</figure>', raw, re.S)
    blocks = re.findall(r'(<figure class="figure".*?</figure>)', raw, re.S)
    if not blocks:
        continue
    print(f"\n{path.name}: {len(blocks)} figures")

    # 1. READER-FACING PRIMARY LABELS. A code name in a title, caption, axis or
    #    row label is a defect. Technical names are INTENTIONALLY kept in
    #    tooltips, so the payload is excluded from this check by design.
    leaked = []
    for b in blocks:
        visible = re.sub(r'<script type="application/json">.*?</script>', "", b, flags=re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        for code in ce.DISPLAY:
            if re.search(rf"\b{re.escape(code)}\b", visible):
                leaked.append(f"{code} visible in a figure")
    check("no code names in primary labels (tooltips excluded by design)",
          not leaked, "; ".join(sorted(set(leaked))[:5]))

    # 2. CHART/TABLE AGREEMENT AT VALUE LEVEL.
    #
    #    Row-count agreement was false confidence: a chart and its fallback can
    #    carry the same number of rows with different numbers in them and pass.
    #    Both are now derived from one canonical Series, and the checksum of the
    #    exact labels and rounded values is written into both the chart host and
    #    the table. If they were built separately, the two will not match.
    def _hash_table(inner):
        cols = [re.sub(r"<[^>]+>", "", c).strip()
                for c in re.findall(r"<th[^>]*>(.*?)</th>", inner, re.S)][1:]
        rows = []
        for tr in re.findall(r"<tr>(.*?)</tr>", inner, re.S):
            cells = []
            for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S):
                v = htmlmod.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                cells.append("" if v in ("\u2014", "-", "&mdash;") else v)
            if cells:
                rows.append(cells)
        if not rows:
            return None
        blob = json.dumps({"cols": cols, "rows": rows}, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    mism, unchecked = [], []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        host = re.search(r'data-chart="[^"]*"[^>]*data-checksum="([^"]*)"', b)
        tbls = re.findall(r'<table data-checksum="([^"]+)"[^>]*>(.*?)</table>', b, re.S)
        if not host or not host.group(1) or not tbls:
            unchecked.append(fid)
            continue
        # RECOMPUTE from what is rendered. Comparing the two stored attributes
        # proves nothing -- the builder writes the same string into both, so a
        # tampered table still matches. A negative test caught that.
        # Multi-view figures carry one table per view; all are checked.
        for stored, inner in tbls:
            got = _hash_table(inner)
            if got is None:
                unchecked.append(f"{fid} (empty table)")
            elif got != stored:
                mism.append(f"{fid}: table content hashes {got}, attribute says {stored}")
        if host.group(1) not in [s for s, _ in tbls]:
            mism.append(f"{fid}: chart checksum {host.group(1)} matches no table")
    check("chart and table agree by RECOMPUTED value checksum",
          not mism, "; ".join(mism[:4]))
    check("every figure carries a checksum on both sides",
          not unchecked,
          "figures built without a canonical Series: " + ", ".join(unchecked))

    # 3. NO FIXED DOM TARGETS. The old library bound to hardcoded ids and
    #    aborted silently when the structure moved.
    js = "".join(re.findall(r"<script>(.*?)</script>", raw, re.S))
    hard = re.findall(r'getElementById\(["\']([^"\']+)["\']', js)
    check("no getElementById targets", not hard, str(hard))

    # 4. EVERY FIGURE COMPLETE: badge, question, fallback table, focusable host.
    incomplete = []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        for part, pat in [("badge", r'class="badge"'), ("question", r'class="fig-q"'),
                          ("fallback table", r"<table"), ("focusable", r'tabindex="0"'),
                          ("aria-describedby", r"aria-describedby")]:
            if not re.search(pat, b):
                incomplete.append(f"{fid} missing {part}")
    check("every figure has badge, question, fallback and keyboard host",
          not incomplete, "; ".join(incomplete[:5]))

    # 5. MOBILE OVERFLOW. Only a BARE width can overflow: max-width is a
    #    ceiling, and min-width inside an overflow-x container is the
    #    deliberate scroll-instead-of-shrink choice. The first version of this
    #    check flagged all three and was simply wrong.
    bare = re.findall(r"(?<![a-z-])width\s*:\s*(\d{3,})px", raw)
    check("no bare pixel widths that could overflow a phone",
          not [w for w in bare if int(w) > 360], str(bare))
    # and every scrolling container that pins a min-width must actually scroll
    unscrollable = []
    for m in re.finditer(r"([.#][\w-]+)\s*\{[^}]*min-width\s*:\s*(\d{3,})px", raw):
        sel, w = m.group(1), int(m.group(2))
        cls = sel[1:]
        # Only rules that something actually uses. The first version flagged
        # `.data-table`, a dead rule inherited from the previous report's
        # stylesheet with zero matching elements in either document.
        used = re.search(rf'class="[^"]*\b{re.escape(cls)}\b', raw) or \
            re.search(rf'id="{re.escape(cls)}"', raw)
        if not used or w <= 360:
            continue
        if not re.search(re.escape(sel) + r"[^{]*\{[^}]*overflow-x\s*:\s*auto", raw):
            unscrollable.append(f"{sel} pins {w}px and nothing scrolls it")
    check("pinned widths sit inside a scrolling container",
          not unscrollable, "; ".join(unscrollable))

    # 6. PRINT FALLBACK present.
    check("print rules hide the live layer and show the table",
          "@media print" in raw and ".chart-live{display:none}" in raw.replace(" ", ""))

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} figure checks pass")
if bad:
    raise SystemExit("FIGURE CHECKS FAILED: " + "; ".join(sorted(set(bad))))
