"""Automated checks for every figure the shared engine renders.

Four failure modes, each of which this project has already produced at least
once, and each of which becomes fifteen times more expensive once the full set
is built.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [p for p in [ROOT / "output" / "prototype.html",
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

    # 1. READER-FACING LABELS. A code name in a title, caption or visible label
    #    is a defect; it may appear only inside a tooltip payload's detail field.
    leaked = []
    for b in blocks:
        visible = re.sub(r'<script type="application/json">.*?</script>', "", b, flags=re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        for code in ce.DISPLAY:
            if re.search(rf"\b{re.escape(code)}\b", visible):
                leaked.append(f"{code} visible in a figure")
    check("reader-facing labels: no code names in visible text",
          not leaked, "; ".join(sorted(set(leaked))[:5]))

    # 2. CHART/TABLE AGREEMENT. The fallback must carry the same number of
    #    entries as the chart, or the two tell different stories.
    mism = []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        pj = re.search(r'<script type="application/json">(.*?)</script>', b, re.S)
        if not pj:
            continue
        d = json.loads(pj.group(1))
        n_chart = len(d.get("rows", [])) or len(d.get("years", []))
        n_rows = len(re.findall(r"<tr>", b.split("</summary>", 1)[-1])) - 0
        n_body = len(re.findall(r"<tr><td", b))
        if n_chart and n_body and n_chart != n_body:
            mism.append(f"{fid}: chart {n_chart} vs table {n_body}")
    check("chart and table fallback agree on row count", not mism, "; ".join(mism))

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
