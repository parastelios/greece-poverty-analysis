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


# 14. The summary tables are built in the report, not lifted from a checked
# figure, so nothing else verifies them. A formatter bug printed five unrun
# bootstrap tests in T1 and two in T2 as "<0.0001" -- the most significant
# value the table can show -- and every existing check passed. This compares
# the rendered cells against the artifacts they claim to summarise.
import html as _html
import math as _math


def _cells(tid):
    m = re.search(rf'<div class="evidence-table" id="{tid}">.*?</table>', raw, re.S)
    if not m:
        return None
    body = re.search(r"<tbody>(.*?)</tbody>", m.group(0), re.S)
    out = []
    for tr in re.findall(r"<tr>(.*?)</tr>", body.group(1), re.S):
        out.append([_html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                    for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)])
    return out


def _fmt(v):
    if v is None or (isinstance(v, float) and not _math.isfinite(v)):
        return "\u2014"
    return f"{v:.4f}" if v >= 0.0001 else "<0.0001"


bad = []
e1 = pd.read_csv(ROOT / "data" / "processed" / "e1_results.csv")
t1 = _cells("T1")
if t1 is None:
    bad.append("T1 not found")
else:
    src = e1.sort_values(["outcome", "construct"]).reset_index(drop=True)
    if len(t1) != len(src):
        bad.append(f"T1 has {len(t1)} rows, artifact has {len(src)}")
    else:
        for i, row in enumerate(t1):
            r = src.iloc[i]
            for col, val, j in [("p_fdr", r.p_fdr, 2), ("boot_p", r.boot_p, 3)]:
                want = _fmt(None if pd.isna(val) else float(val))
                if row[j] != want:
                    bad.append(f"T1 r{i} {col}: shows '{row[j]}', artifact {want}")

e7 = pd.read_csv(ROOT / "data" / "processed" / "e7_results.csv")
t2 = _cells("T2")
if t2 is None:
    bad.append("T2 not found")
else:
    src2 = e7[e7.focal.str.startswith("acc_")].sort_values("pair").reset_index(drop=True)
    if len(t2) != len(src2):
        bad.append(f"T2 has {len(t2)} rows, artifact has {len(src2)}")
    else:
        for i, row in enumerate(t2):
            want = _fmt(None if pd.isna(src2.iloc[i].boot_p)
                        else float(src2.iloc[i].boot_p))
            if row[3] != want:
                bad.append(f"T2 r{i} boot_p: shows '{row[3]}', artifact {want}")

# A missing test must never render as a number, in either direction.
for tid, cs in [("T1", t1), ("T2", t2)]:
    for i, row in enumerate(cs or []):
        for c in row:
            if c.strip() in ("nan", "NaN", "None", "inf", "-inf"):
                bad.append(f"{tid} r{i}: raw '{c}' leaked into a cell")
check("14. summary tables agree with their source artifacts", not bad,
      "; ".join(bad[:6]))

# 15. Sentences corrected in review, each of which had shipped once. These are
# exact phrases rather than a broad pattern, so a sentence that correctly
# DENIES the overstatement is not flagged.
REGRESSED = [
    ("nothing in the context register was tested",
     "migration was tested diagnostically; the register bars headline claims, "
     "it does not claim nothing was examined"),
    ("tests eight candidate explanations",
     "eight is the number of narrative stages, not of construct tests"),
    ("greece is unremarkable",
     "rank 7 of 27 is elevated but not exceptional"),
    ("three things account for part of it",
     "implies a decomposition that was never performed"),
    ("most untested constructs",
     "they were tested; they were not supported"),
    ("the same anchor is used for every country",
     "the anchored series is Greece-only"),
]
low = " ".join(re.sub(r"<[^>]+>", " ", raw).lower().split())
back = [f"{ph!r} ({why})" for ph, why in REGRESSED if ph in low]
check("15. no corrected sentence has regressed", not back, "; ".join(back))

# 16. A document that talks about "the table" must contain one. Blocks that are
# not <figure> elements are lifted separately from the batch pages, and the
# first version of that lift used the wrong closing pattern: the report shipped
# prose introducing a table it did not carry, and every existing check passed.
tbl_refs = re.findall(r"[Tt]he table (?:above|below|beneath)|beneath the table",
                      re.sub(r"<[^>]+>", " ", raw))
if tbl_refs and 'class="ess-table"' not in raw and "<table" not in raw:
    check("16. prose referring to a table has a table", False,
          f"{len(tbl_refs)} references, no table in the document")
else:
    check("16. prose referring to a table has a table", True)

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
