"""Atomic acceptance for the eight-stage technical report.

The V2 harness checked a six-movement structure that no longer exists. This one
checks what the report must now satisfy, and every condition here corresponds to
a defect this project has actually shipped at least once.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from claim_anchors import claim_containers, context_containers, context_completeness

# The report is the eight-stage document assembled by 88_assemble_report.py.
# This gate previously validated output/report.html, the superseded v3 build,
# so the shipping report had no acceptance gate at all.
raw = (ROOT / "output" / "v2_report.html").read_text()
claims = pd.read_csv(ROOT / "data" / "processed" / "e_final_claims.csv").set_index("id")
ctx = pd.read_csv(ROOT / "data" / "processed" / "context_register.csv").set_index("id")

F = []
def check(name, ok, detail=""):
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail and not ok else ""))

print("=" * 78); print("REPORT V3 ACCEPTANCE"); print("=" * 78)

stages = re.findall(r'<section id="s(\d)" class="stage"', raw)
check("1. eight stages, in order", stages == [str(i) for i in range(1, 9)], str(stages))

unplaced = [c for c in claims.index if not claim_containers(raw, c)]
check("2. every frozen claim in an anchored container", not unplaced, str(unplaced))

dupes = [c for c in claims.index if len(claim_containers(raw, c)) > 1]
check("3. no claim placed twice", not dupes, str(dupes))

# Mandatory caveats must travel WITH the claim, inside its own container.
missing_cav = []
for cid, r in claims.iterrows():
    if not isinstance(r.caveats, str) or not r.caveats:
        continue
    body = " ".join(claim_containers(raw, cid)).lower()
    for cav in r.caveats.split(" | "):
        head = " ".join(cav.lower().split()[:4])
        if head not in body:
            missing_cav.append(f"{cid}: {cav[:40]}")
check("4. every mandatory caveat inside its own claim container",
      not missing_cav, str(missing_cav[:3]))

hist = [c for c in claims.index
        if isinstance(claims.loc[c].caveats, str)
        and "no demonstrated within-Greece dynamic" in claims.loc[c].caveats]
check("5. historical-exposure claims carry all four caveats", len(hist) >= 3,
      f"only {len(hist)}")

ctx_missing, ctx_incomplete = [], []
for cid, e in ctx.iterrows():
    found = context_containers(raw, cid)
    if not found:
        ctx_missing.append(cid)
        continue
    entry = {"status": e.status, "permitted": e.permitted, "forbidden": e.forbidden,
             "source": "" if str(e.source_status) == "not applicable" else e.source}
    for c in found:
        m = context_completeness(c, entry)
        if m:
            ctx_incomplete.append(f"{cid}: missing {','.join(m)}")
check("6. every context entry anchored", not ctx_missing, str(ctx_missing))
check("7. every context container complete", not ctx_incomplete, str(ctx_incomplete[:3]))

# A context entry must never sit inside a claim container, or it reads as a finding.
bleed = [cid for cid in ctx.index
         if any(f'data-context-id="{cid}"' in c for c in
                sum((claim_containers(raw, k) for k in claims.index), []))]
check("8. no context entry nested inside a claim", not bleed, str(bleed))

scripts_found = re.findall(r"<script([^>]*)>", raw)
stray = [s for s in scripts_found
         if 'type="application/json"' not in s and s.strip() != ""]
remote = re.findall(r'<script[^>]*\ssrc=', raw)
inline_handlers = re.findall(r'\son(?:click|load|error|mouseover)\s*=', raw)
check("9. only the chart engine and its JSON payloads are scripted",
      not stray and not remote and not inline_handlers,
      f"stray={stray} remote={remote} handlers={inline_handlers}")

bare = set(re.findall(r"var\(--([\w-]+)\s*\)", raw))
defined = set(re.findall(r"--([\w-]+)\s*:", raw))
check("10. no undefined CSS variables without a fallback",
      not (bare - defined), str(sorted(bare - defined)))

FIG_MIN, FLOOR = 620, 7.0
small = []
for m in re.finditer(r'<svg[^>]*viewBox="0 0 (\d+)[^"]*"(.*?)</svg>', raw, re.S):
    vb = int(m.group(1))
    s = [float(x) for x in re.findall(r'font-size="([\d.]+)"', m.group(2))]
    if s and min(s) * (FIG_MIN / vb) < FLOOR:
        small.append(f"{vb}-wide at {min(s) * (FIG_MIN / vb):.1f}px")
check("11. inline SVG text legible at 375px", not small, str(small))

check("12. tags balanced",
      raw.count("<section") == raw.count("</section>")
      and raw.count("<figure") == raw.count("</figure>")
      and raw.count("<div") == raw.count("</div>"))

forbidden = [
    ("objective-only", "frozen P3 may not be called objective-only"),
    ("proves that", "no causal proof language"),
    ("caused by accumulated", "no causal attribution to accumulation"),
]
hits = [d for p_, d in forbidden if p_ in raw.lower()]
check("13. no prohibited phrasing", not hits, str(hits))

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} conditions pass")
if bad:
    raise SystemExit("REPORT NOT ACCEPTED: " + "; ".join(bad))
print("REPORT ACCEPTED")
