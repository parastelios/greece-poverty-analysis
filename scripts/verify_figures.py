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
# output/prototype.html is the original two-figure preview, built before the
# batch pages existed and superseded by them. It carries its own copies of two
# figures that have since been redesigned, so checking it against the current
# manifest measures a scaffold rather than a deliverable.
TARGETS = [p for p in [ROOT / "output" / "batch1.html",
                       ROOT / "output" / "batch2.html",
                       ROOT / "output" / "batch3.html",
                       ROOT / "output" / "batch4.html",
                       ROOT / "output" / "v2_report.html",
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
        visible = re.sub(r'<script type="application/json"[^>]*>.*?</script>', "",
                         b, flags=re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        # Remove the legitimate display names FIRST. Several contain their own
        # code as a substring -- "Cannot keep the home warm" contains `warm`,
        # "Arrears on bills" contains `arrears` -- and the first version of this
        # check reported both as leaks.
        for disp in sorted(ce.DISPLAY.values(), key=len, reverse=True):
            visible = visible.replace(disp, " ").replace(disp.lower(), " ")
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
        # Headers must be unescaped exactly like cells are. They were not, so
        # any column name containing an apostrophe or ampersand hashed
        # differently from the builder's own -- a latent mismatch that only
        # appeared when a header first contained one.
        cols = [htmlmod.unescape(re.sub(r"<[^>]+>", "", c)).strip()
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

    # 2b. EVERY VIEW MUST CONTAIN DATA.
    #
    #     A figure whose default view is blank passed every structural check:
    #     it had a badge, a caption, a fallback table with labels, and a
    #     matching checksum -- and an empty chart. F5's components view shipped
    #     that way because a source had no TOTAL row and the year intersection
    #     collapsed to nothing.
    empty = []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        pls = re.findall(r'<script type="application/json"([^>]*)>(.*?)</script>',
                         b, re.S)
        for attrs, body in pls:
            lbl = (re.search(r'data-label="([^"]*)"', attrs) or [None, fid])[1] \
                if 'data-label' in attrs else fid
            d = json.loads(body.replace("<\\/", "</"))
            xs = (len(d.get("years", [])) or len(d.get("rows", []))
                  or len(d.get("points", []))
                  or sum(len(s.get("points", [])) for s in d.get("strips", []))
                  or sum(len(s.get("points", [])) or len(s.get("x", []))
                         for s in d.get("panels", [])))
            # Each chart type names its numbers differently: series carry
            # "values", coefficient rows carry "est", ladder rows carry
            # "value". Missing one gave a false positive on the ladder.
            vals = [v for s in d.get("series", []) for v in s.get("values", [])
                    if v is not None]
            for r in d.get("rows", []):
                for k in ("est", "value", "a", "b"):
                    if r.get(k) is not None:
                        vals.append(r[k])
                vals.extend([v for v in r.get("values", []) if v is not None])
            vals.extend([pt["y"] for pt in d.get("points", []) if pt.get("y") is not None])
            for s in d.get("strips", []):
                vals.extend([pt["value"] for pt in s.get("points", [])
                             if pt.get("value") is not None])
            for s in d.get("panels", []):
                vals.extend([pt["y"] for pt in s.get("points", [])
                             if pt.get("y") is not None])
                for ln in s.get("series", []):
                    vals.extend([v for v in ln.get("values", []) if v is not None])
            if xs < 2 and not d.get("rows"):
                empty.append(f"{fid}/{lbl}: {xs} x-values")
            elif not vals:
                empty.append(f"{fid}/{lbl}: no finite values")
    check("every view contains at least two x-values and one finite number",
          not empty, "; ".join(empty))

    # A reader should never have to consult a caption or hover a tooltip to
    # learn whether an axis is percent, percentage points, PPS per head, index
    # points, people or years. Correlation matrices are exempt: a correlation
    # is dimensionless, and its axes are variable names rather than a scale.
    unlabelled = []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        for attrs, body in re.findall(
                r'<script type="application/json"([^>]*)>(.*?)</script>', b, re.S):
            d = json.loads(body.replace("<\\/", "</"))
            if not d or "cols" in d or d.get("cells"):
                continue
            lbl = (re.search(r'data-label="([^"]*)"', attrs) or [None, fid])[1] \
                if "data-label" in attrs else fid
            if not (d.get("yLabel") or d.get("xLabel") or d.get("unit")):
                unlabelled.append(f"{fid}/{lbl}")
    check("every view states its units on an axis",
          not unlabelled, "; ".join(unlabelled))

    # Contrast is a property of the tokens, not of any one figure, and it was
    # wrong in BOTH themes: the label colour was a single warm grey shared by
    # light and dark, failing at 3.50:1 on light, and the negative-correlation
    # colour reached only 2.96:1 on dark. Neither is visible by reading the
    # markup, so the ratios are computed here.
    def _lum(hx):
        hx = hx.lstrip("#")
        ch = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        ch = [(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4) for c in ch]
        return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]

    def _ratio(a, b):
        la, lb = _lum(a), _lum(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    def _blocks(css):
        """Every rule that defines chart tokens, tagged by the theme it serves.

        A token is declared three times -- once for light, once under
        prefers-color-scheme, once under the explicit dark attribute -- and any
        ONE of them can be wrong while the others are right. Checking only the
        last value let a bad @media definition through in testing, so every
        block is checked separately.
        """
        out = []
        for m in re.finditer(r"(@media[^{]*\{\s*)?:root([^{]*)\{([^}]*)\}", css):
            body, guard = m.group(3), (m.group(1) or "") + (m.group(2) or "")
            if "--chart-label" not in body and "--div-neg" not in body:
                continue
            dark = "dark" in guard
            out.append((dark, body))
        return out

    bad_contrast = []
    LIGHT_BG, DARK_BG = "#fcfcfb", "#1a1a19"
    # Which tones do these figures actually use? Read them from the payloads and
    # resolve each through the engine's alias map, so a tone that is used but
    # never defined is caught rather than silently rendering black.
    ALIAS = dict(re.findall(r"'([a-z0-9-]+)':'([a-z0-9-]+)'",
                            re.search(r"TONE_ALIAS=\{(.*?)\};", raw, re.S).group(1))
                 ) if re.search(r"TONE_ALIAS=\{(.*?)\};", raw, re.S) else {}
    used = set()
    for m in re.finditer(r'<script type="application/json"[^>]*>(.*?)</script>',
                         raw, re.S):
        try:
            d = json.loads(m.group(1).replace("<\\/", "</"))
        except Exception:
            continue
        for item in (d.get("rows") or []) + (d.get("series") or []):
            if isinstance(item, dict) and item.get("tone"):
                used.add(ALIAS.get(item["tone"], item["tone"]))
    undefined = sorted(u for u in used
                       if not re.search(rf"--{re.escape(u)}\s*:", raw))
    if undefined:
        bad_contrast.append(
            f"tones used but never defined (render as black): {undefined}")
    # token, minimum ratio: label text needs 4.5, data marks need 3.0
    TOKENS = ([("chart-label", 4.5), ("chart-neutral", 3.0)]
              + [(u, 3.0) for u in sorted(used)])
    token_blocks = _blocks(raw)
    if not token_blocks:
        bad_contrast.append("no chart token block found")
    if not any(d for d, _ in token_blocks) or not any(not d for d, _ in token_blocks):
        bad_contrast.append("chart tokens are not defined for both themes")
    for dark, body in token_blocks:
        bg = DARK_BG if dark else LIGHT_BG
        for name, need in TOKENS:
            m = re.search(rf"--{name}\s*:\s*(#[0-9a-fA-F]{{6}})", body)
            if not m:
                continue
            got = _ratio(m.group(1), bg)
            if got < need:
                bad_contrast.append(
                    f"--{name} {m.group(1)} on {'dark' if dark else 'light'}: "
                    f"{got:.2f}:1 (needs {need})")
    check("chart colours meet contrast minimums in both themes",
          not bad_contrast, "; ".join(bad_contrast))

    raw_tone_use = re.findall(r"var\(--\$\{(?:tone|s\.tone|r\.tone)\}\)", raw)
    # An id is a stable identifier, not a position. When the manifest derived
    # ids from order, removing one figure silently re-pointed every id after
    # it, and the companion's pre-crisis chapter ended up showing a shift-share
    # decomposition -- with every check passing, because every id still
    # resolved to something. The manifest must declare ids explicitly.
    man_path = ROOT / "data" / "processed" / "report_visual_manifest.csv"
    src = (ROOT / "scripts" / "81_visual_manifest.py").read_text()
    declared = re.findall(r'dict\(id="(F\d+)"', src)
    if sorted(declared) != sorted(set(declared)):
        dup = sorted({d for d in declared if declared.count(d) > 1})
        check("manifest figure ids are unique and declared", False,
              f"duplicate ids: {dup}")
    elif man_path.exists() and list(pd.read_csv(man_path)["id"]) != declared:
        check("manifest figure ids are unique and declared", False,
              "the published manifest does not match the declared ids")
    else:
        check("manifest figure ids are unique and declared", True)

    # A figure's caveat is assembled from the manifest text plus whatever the
    # builder adds. Three figures have shipped saying the same thing twice,
    # because the builder restated what the manifest already carried. Compare
    # the two halves for a repeated sentence rather than trusting review.
    dupes = []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        cav = re.search(r'<p class="fig-caveat">(.*?)</p>', b, re.S)
        if not cav:
            continue
        txt = htmlmod.unescape(re.sub(r"<[^>]+>", " ", cav.group(1)))
        sents = [s.strip().lower() for s in re.split(r"(?<=[.!?])\s+", txt)
                 if len(s.strip()) > 18]
        # near-duplicate: same opening eight words
        heads = {}
        for s in sents:
            k = " ".join(s.split()[:8]) if len(s.split()) >= 8 else s
            if k in heads:
                dupes.append(f"{fid}: caveat repeats \"{k}...\"")
            heads[k] = True
    check("no figure states the same caveat twice", not dupes, "; ".join(dupes))

    # Two views plotting identical data. This happened twice: a view added to
    # the threshold figure reproduced the income-poverty view of the AROPE
    # breakdown exactly -- same series, same 26 context countries, same values
    # -- and every check passed, because each was individually well formed.
    seen_views, same = {}, []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        for attrs, body in re.findall(
                r'<script type="application/json"([^>]*)>(.*?)</script>', b, re.S):
            try:
                d = json.loads(body.replace("<\\/", "</"))
            except Exception:
                continue
            core = json.dumps({k: d.get(k) for k in
                               ("series", "context", "rows", "strips", "panels")},
                              sort_keys=True)
            if len(core) < 80:
                continue
            key = hashlib.sha256(core.encode()).hexdigest()[:12]
            lbl = (re.search(r'data-label="([^"]*)"', attrs) or [None, ""])[1] \
                if "data-label" in attrs else ""
            here = f"{fid}{'/' + lbl if lbl else ''}"
            if key in seen_views:
                same.append(f"{seen_views[key]} and {here} plot identical data")
            else:
                seen_views[key] = here
    check("no two views plot identical data", not same, "; ".join(same))

    check("no chart colour bypasses the tone alias",
          not raw_tone_use,
          f"{len(raw_tone_use)} direct var(--${{tone}}) uses; route them "
          f"through toneVar() or an undefined tone renders black")

    # 2c. VIEW COUNT MATCHES THE MANIFEST, so scope cannot shrink silently.
    manp = ROOT / "data" / "processed" / "report_visual_manifest.csv"
    if manp.exists():
        man = pd.read_csv(manp).set_index("id")
        wrong = []
        for b in blocks:
            fid = re.search(r'id="([^"]+)"', b).group(1)
            if fid not in man.index:
                continue
            got = len(re.findall(r'data-label="', b)) or 1
            want = str(man.loc[fid].series).upper().count("VIEW ") or 1
            if want > 1 and got != want:
                wrong.append(f"{fid}: {got} views, manifest promises {want}")
        check("view count matches the manifest", not wrong, "; ".join(wrong))

    # 2d. THE BETWEEN/WITHIN CLAIM, GUARDED SPECIFICALLY.
    #
    #     This overstatement has slipped through three times -- P5, E4's first
    #     write-up, and F13 -- because "carried between countries, not within"
    #     reads as a summary of the numbers rather than a claim beyond them.
    #
    #     The guard is claim-specific, not a language regex. A broad pattern
    #     would flag sentences that correctly DENY the overstatement, which this
    #     project's forbidden-phrase sweeps have done repeatedly.
    REQUIRED_IN = {
        "F13": ["predominantly between countries",
                "no supporting dynamic evidence",
                "inconclusive",
                "too imprecise to establish or rule out"],
    }
    missing_req = []
    for b in blocks:
        fid = re.search(r'id="([^"]+)"', b).group(1)
        if fid not in REQUIRED_IN:
            continue
        text = " ".join(re.sub(r"<[^>]+>", " ", b).lower().split())
        for phrase in REQUIRED_IN[fid]:
            if phrase not in text:
                missing_req.append(f"{fid} must contain '{phrase}'")
    check("the between/within figure carries all four canonical elements",
          not missing_req, "; ".join(missing_req))

    # The exact overstatements, banned from captions and ordinary prose. The
    # tooltip payload is excluded, as elsewhere.
    BANNED = ["entirely between countries",
              "carried between countries, not within",
              "no within-country effect",
              "does not work within countries"]
    NEGATORS = ("not ", "never ", "cannot ", "does not ", "do not ", "no claim",
                "would be wrong", "must not", "may not", "rather than")
    prose = re.sub(r'<script type="application/json"[^>]*>.*?</script>', "",
                   raw, flags=re.S)
    prose = " ".join(re.sub(r"<[^>]+>", " ", prose).lower().split())
    hits = []
    for phrase in BANNED:
        for m in re.finditer(re.escape(phrase), prose):
            window = prose[max(0, m.start() - 70):m.start()]
            # A sentence that denies the overstatement is not the overstatement.
            if not any(n in window for n in NEGATORS):
                hits.append(phrase)
    check("no banned between/within overstatement in prose",
          not hits, "; ".join(sorted(set(hits))))

    # 2e. THE FIGURE MUST BE THE ONE THE MANIFEST DESCRIBES.
    #
    #     Inserting two entries ahead of an existing one shifted every id during
    #     renumbering, so the migration figure was built carrying the trust
    #     figure's badge, question and caveat. Nothing caught it: the chart drew,
    #     the checksum matched, the fallback was present. Comparing the rendered
    #     chart type against the manifest's would have.
    if manp.exists():
        mism_kind = []
        for b in blocks:
            fid = re.search(r'id="([^"]+)"', b).group(1)
            if fid not in man.index:
                continue
            host = re.search(r'data-chart="([^"]*)"', b)
            payload_kinds = set(re.findall(r'data-kind="([^"]*)"', b))
            got = payload_kinds or ({host.group(1)} if host else set())
            want = str(man.loc[fid].chart_type)
            if want not in got:
                mism_kind.append(f"{fid}: renders {sorted(got)}, manifest says {want}")
        check("each figure's chart type matches its manifest entry",
              not mism_kind, "; ".join(mism_kind))

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
