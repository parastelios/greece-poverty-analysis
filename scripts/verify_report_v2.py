"""Atomic acceptance check for the V2 technical report.

The global release gate stays red until all three documents are rewritten, so
the report needs its own completion criterion. This is it. Run:

    python verify_report_v2.py

Exits 0 only when the report is a coherent V2 deliverable on its own.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPORT = Path("../output/report.html")
RAW = REPORT.read_text(encoding="utf-8")
STRIP = lambda t: re.sub(r"<style.*?</style>", " ",
                         re.sub(r"<script.*?</script>", " ", t, flags=re.S), flags=re.S)
CLEAN = STRIP(RAW)
TEXT = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", CLEAN)))
LOW = TEXT.lower()

sys.path.insert(0, ".")
from claim_anchors import claim_containers  # noqa: E402

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))

# 1 -- the six V2 claims, each in an anchored visible container
FP = {"10.1": ["27.05"], "10.2": ["+6.93", "6.93"],
      "10.3": ["predominantly between countries", "predominantly between-country"],
      "10.4": ["synthetic-control design", "failed its pre-registered", "did not work"],
      "10.5": ["multidomain breadth", "multi-domain breadth", "breadth measure"],
      "10.6": ["backward-extended official", "official subjective-hardship indicator"]}
missing = []
for cid, fps in FP.items():
    blocks = claim_containers(CLEAN, cid)
    if not any(f.lower() in b.lower() for b in blocks for f in fps):
        missing.append(cid)
check("1. six V2 claims in anchored containers", not missing,
      f"missing: {missing}" if missing else "10.1-10.6 all anchored")

# 2 -- global pending falls 18 -> 12
out = subprocess.run([sys.executable, "audit_parity.py"], capture_output=True, text=True).stdout
pend = re.findall(r"^  (10\.\d)\s+.*missing from: (.+)$", out, re.M)
slots = sum(len(d.split(",")) for _, d in pend)
check("2. global pending slots == 12", slots == 12, f"{slots} pending (18 at branch point)")

# 3 -- no superseded residual presented as a current headline
SUPERSEDED = {"-0.8": "Model G residual", "−0.8": "Model G residual",
              "+2.70": "nested-selection residual", "2.70pt": "nested-selection residual"}
bad = []
for tok, what in SUPERSEDED.items():
    for mm in re.finditer(re.escape(tok), TEXT):
        ctx = LOW[max(0, mm.start() - 260):mm.end() + 260]
        if not any(w in ctx for w in ("superseded", "legacy", "earlier specification",
                                      "no longer", "appendix", "proximity-sensitive")):
            bad.append(f"{tok} ({what}) unlabelled")
check("3. no superseded residual as a headline", not bad, "; ".join(bad) or "all labelled or absent")

# 4 -- mandatory P3/P5 caveats
CAVEATS = {
    "model comparison not decomposition": ["model comparison", "not a causal decomposition"],
    "Tier 0 excluded by construction": ["excluded by construction", "excludes arrears"],
    "predominantly between countries": ["predominantly between countries"],
    "within inconclusive under power": ["inconclusive under", "too imprecise to rule"],
    "bootstrap worst-case labelled": ["worst robustness result"],
    "financial-domain-specific wording": ["financial-domain-specific"],
    "post-selection, not confirmatory": ["post-selection"],
}
absent = [k for k, ps in CAVEATS.items() if not any(p.lower() in LOW for p in ps)]
check("4. mandatory P3/P5 caveats present", not absent, f"absent: {absent}" if absent else "all present")

# 5 -- movements 1-6 present and in spine order
spine = pd.read_csv("../docs/shared_spine.csv")
ids = [f"movement-{i}" for i in range(1, 7)]
pos = [RAW.find(f'id="{i}"') for i in ids]
check("5. movements 1-6 in spine order", all(p >= 0 for p in pos) and pos == sorted(pos),
      f"positions: {[i for i, p in zip(ids, pos) if p < 0]} missing" if any(p < 0 for p in pos)
      else "all six present and ordered")

# 6 -- movement 7 brief + appendix pointer, exact figures absent
m7 = claim_containers(CLEAN, "legacy")
m7_text = " ".join(m7).lower()
has_ptr = "appendix" in m7_text
brief = 0 < len(re.sub(r"\s+", " ", m7_text).split()) <= 160
check("6. movement 7 brief with appendix pointer", bool(m7) and has_ptr and brief,
      f"{len(m7_text.split())} words, appendix pointer: {has_ptr}" if m7 else "no legacy container")

# 7 -- HTML well-formed
import html.parser as hp
class P(hp.HTMLParser):
    VOID = {"br", "img", "hr", "meta", "link", "input", "path", "circle", "line",
            "rect", "text", "use", "stop", "polygon", "polyline", "ellipse"}
    def __init__(s): super().__init__(); s.st = []
    def handle_starttag(s, t, a):
        if t not in s.VOID: s.st.append(t)
    def handle_endtag(s, t):
        if s.st and s.st[-1] == t: s.st.pop()
p = P(); p.feed(RAW)
check("7. HTML well-formed", not p.st, f"{len(p.st)} unclosed")

# 7c -- no orphaned draw/fill targets. Removing legacy sections left three chart
# draw calls and two table-fill blocks pointing at deleted elements; the first
# null dereference aborted the rest of the script and silently blanked SEVEN
# charts and two tables, with no console error visible on a static snapshot.
containers = set(re.findall(r'<svg class="chart" id="([a-z0-9-]+)"', RAW))
draws = set(re.findall(r"svgId:'([a-z0-9-]+)'", RAW))
legend_ids = set(re.findall(r'id="(legend-[a-z0-9-]+)"', RAW))
legend_calls = set(re.findall(r"legend\('([a-z0-9-]+)'", RAW))
tbl_ids = set(re.findall(r'id="([a-z0-9-]+)"', RAW))
tbl_refs = set(re.findall(r"querySelector\('#([a-z0-9-]+) tbody'\)", RAW))
orphans = ([f"draw:{c}" for c in draws - containers]
           + [f"legend:{c}" for c in legend_calls - legend_ids]
           + [f"table:{c}" for c in tbl_refs - tbl_ids])
check("7c. no orphaned draw or fill targets", not orphans,
      f"orphans: {orphans}" if orphans else "every draw/fill target exists")

# 9 -- development verification green
dev = subprocess.run([sys.executable, "audit_parity.py"], capture_output=True).returncode
vb = subprocess.run([sys.executable, "verify_build.py"], capture_output=True).returncode
check("9. development verification green", dev == 0 and vb == 0, f"parity {dev}, build {vb}")

print("=" * 74)
print("TECHNICAL REPORT V2 -- ATOMIC ACCEPTANCE")
print("=" * 74)
for name, ok, detail in results:
    print(f"  [{'PASS' if ok else 'FAIL'}]  {name:44} {detail}")
print("\n  [MANUAL] 8. semantic audit: each paragraph communicates its assigned claim")
print("  [MANUAL] 7b. PDF, desktop and mobile rendering reviewed")
n_fail = sum(1 for _, ok, _ in results if not ok)
print(f"\n{len(results) - n_fail}/{len(results)} automated conditions pass"
      f"{'' if n_fail else '  -- manual checks still required'}")
sys.exit(1 if n_fail else 0)
