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
# output/ holds the canonical publications; output/build/ holds the batch pages
# the assemblers lift figures from. The prototype (build/prototype.html) is the
# original two-figure preview, superseded by the batch pages: it carries its own
# copies of two figures that have since been redesigned, so checking it against
# the current manifest measures a scaffold rather than a deliverable.
#
# output/report.html was the v1 publication. It is preserved at tag v1-final and
# is no longer written to output/, so the guard below simply skips it.
_BUILD = ROOT / "output" / "build"
TARGETS = [p for p in [_BUILD / "batch1.html",
                       _BUILD / "batch2.html",
                       _BUILD / "batch3.html",
                       _BUILD / "batch4.html",
                       ROOT / "output" / "v2_report.html",
                       _BUILD / "report.html"] if p.exists()]

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
        # Two sentences are the same statement if one opens with the other,
        # not only if their first eight words match. "Absorption is not
        # explanation." and "Absorption is not explanation: these four items..."
        # slipped through a fixed-length prefix comparison.
        norm = [re.sub(r"[^a-z0-9 ]", "", s).strip() for s in sents]
        for x in range(len(norm)):
            for y in range(x + 1, len(norm)):
                a2, b2 = norm[x], norm[y]
                if not a2 or not b2:
                    continue
                short, long_ = (a2, b2) if len(a2) <= len(b2) else (b2, a2)
                if len(short.split()) >= 3 and long_.startswith(short):
                    dupes.append(f"{fid}: caveat repeats \"{short[:52]}...\"")
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

# ---------------------------------------------------------------------------
# GATE: NO POSITIONAL FIGURE REFERENCES.
#
# Prose that says "the figure below" or "Figure 7" is correct until the next
# reshuffle and then silently wrong: figures are numbered AT PLACEMENT, so
# moving one renumbers everything after it and no existing check can see the
# break. Claims and context are anchored by container and survive; sentences
# pointing at a position do not. Reference figures by what they show.
# ---------------------------------------------------------------------------
# Positional PHRASES are banned everywhere: they name a position, and a
# position is not a fact about the figure.
#
# A numbered reference is different. In the report and the narrative it is
# banned too, because neither builds one deliberately. The paper needs them --
# academic convention -- and builds them from {fig:Fxx} tokens resolved against
# its own placement map, with 90_build_paper.py refusing to build if a number
# was typed instead. So numbers are checked at their source, not here, where a
# typed number and a resolved one are the same characters.
_POSITIONAL = [
    r"\bthe (?:figure|chart|plot|panel) (?:below|above)\b",
    r"\bthe (?:next|previous|preceding|following) (?:figure|chart)\b",
    r"\b(?:as )?(?:shown|seen) (?:below|above)\b",
]
_NUMBERED = r"\b(?:figure|fig\.)\s+\d+\b"


def positional_hits(text, patterns=None):
    """Prose-only: the figure's own caption legitimately carries its number."""
    body = re.sub(r'<figcaption.*?</figcaption>', " ", text, flags=re.S)
    body = re.sub(r'<script.*?</script>', " ", body, flags=re.S)
    body = re.sub(r'<style.*?</style>', " ", body, flags=re.S)
    body = re.sub(r'<table.*?</table>', " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    body = htmlmod.unescape(body)
    hits = []
    for pat in (patterns or _POSITIONAL):
        for m in re.finditer(pat, body, re.I):
            s = max(0, m.start() - 45)
            hits.append(" ".join(body[s:m.end() + 25].split()))
    return hits


# ---------------------------------------------------------------------------
# GATE: CLAIMS ABOUT THE APPENDIX MUST BE TRUE OF THE APPENDIX.
#
# A caveat saying "the full matrix is not shown anywhere" was true when written
# and false once the appendix gained figures. That has now happened three
# times. Two rules:
#
#   1. Negative-existence claims are banned outright. "Not shown anywhere" is a
#      statement about every other document in the project and cannot be kept
#      true by anyone editing one of them.
#   2. A positive claim that the appendix carries something is checked against
#      the appendix's actual text.
# ---------------------------------------------------------------------------
_NEGATIVE_EXISTENCE = [
    r"not shown anywhere", r"shown nowhere", r"appears nowhere",
    r"is not shown in (?:the )?(?:appendix|report)",
    r"nowhere in (?:the )?(?:appendix|report)",
    r"not (?:available|reproduced) anywhere",
]


def appendix_claims(report_text, appendix_text):
    """Return (banned, unsupported) claims made about the appendix."""
    cavs = re.findall(r'<p class="fig-caveat">(.*?)</p>', report_text, re.S)
    cavs = [htmlmod.unescape(re.sub(r"<[^>]+>", " ", c)) for c in cavs]
    banned, unsupported = [], []
    app = htmlmod.unescape(re.sub(r"<[^>]+>", " ", appendix_text)).lower()
    for c in cavs:
        flat = " ".join(c.split())
        for pat in _NEGATIVE_EXISTENCE:
            if re.search(pat, flat, re.I):
                banned.append(flat[:110])
        # A sentence naming the appendix asserts something about it. Check the
        # distinctive tokens in that sentence -- the ones a reader would use to
        # find the thing -- actually occur there.
        for sent in re.split(r"(?<=[.;]) ", flat):
            if "appendix" not in sent.lower():
                continue
            toks = set(re.findall(r"\b\d+-variable\b|\b\d+ tables?\b|"
                                  r"\b\d+ figures?\b", sent.lower()))
            missing = [tk for tk in toks if tk not in app]
            if missing:
                unsupported.append(f"{sent[:90]} -> {missing}")
    return banned, unsupported


# ---------------------------------------------------------------------------
# THE APPENDIX MUST BE A SUPERSET. Every figure the report carries has to
# appear in the appendix with the SAME payload, so a reader sent there to check
# a number finds the same object rather than a similar one. Hashed, not counted.
# ---------------------------------------------------------------------------
_rep = ROOT / "output" / "v2_report.html"
_app = ROOT / "output" / "statistical_appendix.html"
if _rep.exists() and _app.exists():
    def _fig_hashes(text):
        out = {}
        for m in re.finditer(
                r'<figure class="figure" id="([A-Z]\d+[A-Z]?)">(.*?)</figure>',
                text, re.S):
            pls = re.findall(
                r'<script type="application/json"[^>]*>(.*?)</script>',
                m.group(2), re.S)
            out[m.group(1)] = hashlib.sha256("".join(pls).encode()).hexdigest()[:12]
        return out

    # The two cross-document gates run over the published documents, so they
    # see what a reader sees rather than what a builder intended.
    _rt, _at = _rep.read_text(), _app.read_text()
    _pos = []
    for _doc in ("v2_report.html", "academic_paper.html", "narrative.html"):
        _f = ROOT / "output" / _doc
        if _f.exists():
            _pos += [f"{_doc}: {h}" for h in positional_hits(_f.read_text())]
            if _doc != "academic_paper.html":
                _pos += [f"{_doc}: {h}"
                         for h in positional_hits(_f.read_text(), [_NUMBERED])]
    check("no positional figure references in prose",
          not _pos, "; ".join(sorted(set(_pos))[:4]))

    _banned, _unsup = appendix_claims(_rt, _at)
    check("no caveat makes a negative-existence claim about other documents",
          not _banned, "; ".join(_banned[:3]))
    check("claims a caveat makes about the appendix hold in the appendix",
          not _unsup, "; ".join(_unsup[:3]))

    # ---- NEAR-DUPLICATION, not just byte-duplication --------------------
    #
    # The payload-hash check catches two views that are literally the same
    # object. It cannot catch two figures that show the same lines with one
    # added, or ask the same question of the same data -- which is an
    # editorial problem regardless of whether the bytes differ. Merging the
    # AROPE component tabs into one view put Greek income poverty and AROPE on
    # a chart beside the figure that already plots exactly those two.
    _STOP = {"what", "does", "with", "that", "this", "from", "much", "have",
             "into", "than", "when", "which", "were", "been", "they", "them",
             "their", "each", "every", "same", "more", "most", "other",
             "greek", "greece", "country", "countries"}

    def _shown(fig_html):
        """Series labels a reader actually sees, and the figure's question."""
        labels = set()
        for pl in re.findall(
                r'<script type="application/json"[^>]*>(.*?)</script>',
                fig_html, re.S):
            try:
                d = json.loads(pl)
            except Exception:
                continue
            for s in d.get("series", []) or []:
                if s.get("label"):
                    labels.add(re.sub(r"^.*?:\s*", "", s["label"]).strip().lower())
            for r in d.get("rows", []) or []:
                if r.get("label"):
                    labels.add(r["label"].strip().lower())
        # The question is a <span>, not a <p>. Matching the wrong tag made
        # this check unable to fire at all -- it passed on every document
        # because the question was always empty.
        q = re.search(r'<span class="fig-q">(.*?)</span>', fig_html, re.S)
        return labels, " ".join(
            htmlmod.unescape(re.sub(r"<[^>]+>", " ", q.group(1))).split()
        ).lower() if q else ""

    # A check that cannot fire is documentation, not enforcement. Prove the
    # question is actually being read before trusting the result.
    _probe = {k: _shown(v)[1] for k, v in
              list(re.finditer(r'<figure class="figure" id="([A-Z]\d+)">.*?</figure>',
                               _rt, re.S).__class__ and
              {m.group(1): m.group(0) for m in re.finditer(
                  r'<figure class="figure" id="([A-Z]\d+)">.*?</figure>',
                  _rt, re.S)}.items())}
    if not any(_probe.values()):
        raise SystemExit(
            "near-duplication check read no figure questions: its selector is "
            "wrong and the check cannot fail")

    _figs = {m.group(1): m.group(0) for m in re.finditer(
        r'<figure class="figure" id="([A-Z]\d+)">.*?</figure>', _rt, re.S)}
    _near = []
    _ids = sorted(_figs)
    for _i, _x in enumerate(_ids):
        lx, qx = _shown(_figs[_x])
        for _y in _ids[_i + 1:]:
            ly, qy = _shown(_figs[_y])
            if not lx or not ly:
                continue
            _shared = lx & ly
            # Shared series ALONE is not restatement, and a first version of
            # this check said it was: it flagged the accumulated-exposure
            # ladder against the model-dependence chart because both label
            # rows with country names, and the conditional figure against the
            # between/within one because both name the same measures. They do,
            # and they ask different things of them.
            #
            # Restatement is the same QUESTION asked of the same series. The
            # question is the figure's own one-line statement of what it
            # answers, so comparing content words in it is comparing intent.
            _overlap = len(_shared) / min(len(lx), len(ly))
            _wx = set(re.findall(r"[a-z]{4,}", qx)) - _STOP
            _wy = set(re.findall(r"[a-z]{4,}", qy)) - _STOP
            _qsim = (len(_wx & _wy) / min(len(_wx), len(_wy))) if _wx and _wy else 0
            if _overlap >= 0.8 and _qsim >= 0.6:
                _near.append(
                    f"{_x}/{_y}: {int(_overlap*100)}% of displayed series "
                    f"shared and questions {int(_qsim*100)}% alike "
                    f"({sorted(_shared)[:3]})")
    check("no report figure restates another's series and question",
          not _near, "; ".join(_near[:3]))

    # ---- THE APPENDIX AS A NAVIGABLE DOCUMENT ---------------------------
    #
    # Ninety-odd charts behind collapsible groups is only an improvement if
    # every one of them is still reachable, still counted, and still printed.
    # Four things can silently break that, so four checks.

    # 1. DUPLICATE IDS. Two elements sharing an id makes getElementById return
    #    the first, so a deep link lands on the wrong chart -- or on the right
    #    chart in the wrong group, which the reveal logic then fails to open.
    _all_ids = re.findall(r'\sid="([^"]+)"', _at)
    _dupe_ids = sorted({i for i in _all_ids if _all_ids.count(i) > 1})
    check("appendix element ids are unique",
          not _dupe_ids, ", ".join(_dupe_ids[:6]))

    # 2. UNRESOLVED DEEP LINKS. Every in-page link must resolve to an id that
    #    exists. A link into the atlas that points at a renamed anchor now
    #    fails twice over: it does not scroll, and it does not open the group.
    _ids = set(_all_ids)
    _links = {h for h in re.findall(r'href="#([^"]+)"', _at) if h}
    _dead = sorted(h for h in _links if h not in _ids)
    check("every in-page link resolves to an element that exists",
          not _dead, ", ".join(_dead[:6]))

    # 3. THE ATLAS IS STILL WHOLE. Regrouping ten sections into eight domains
    #    is the kind of edit that loses a chart between two lists without any
    #    error. The anchors are counted directly off the page.
    _atlas = (len(re.findall(r'\sid="s_[a-z0-9_]+"', _at))
              + len(re.findall(r'\sid="p_[a-z0-9_]+"', _at))
              + len(re.findall(r'\sid="x_[a-z0-9_]+"', _at)))
    check("the variable atlas still carries all 89 charts",
          _atlas == 89, f"found {_atlas}")

    # 4. PRINT VISIBILITY. A closed <details> prints as missing content, not as
    #    a closed block, so the appendix would lose most of the atlas on paper.
    #    Two independent mechanisms have to be present: a CSS rule that shows
    #    the content, and a beforeprint handler that opens the elements.
    _print_css = re.search(r"@media print\{(.*?)\}\s*\.howto", _at, re.S)
    _has_css = bool(_print_css) and "details{display:block}" in \
        re.sub(r"\s+", "", _print_css.group(1))
    _has_js = "beforeprint" in _at and "d.open=true" in re.sub(r"\s+", "", _at)
    check("the atlas is expanded for print, by CSS and by script",
          _has_css and _has_js,
          f"css={_has_css} js={_has_js}")

    # 5. EVERY ATLAS CHART SITS IN A GROUP THAT CAN BE OPENED. An anchor that
    #    is inside no <details> is fine; one inside a <details> the reveal
    #    logic never sees is not. The logic walks ancestors, so the only
    #    failure mode is an anchor outside the domain wrappers entirely, which
    #    would mean a chart lost from the grouping.
    _grouped = 0
    for _m in re.finditer(
            r'<details class="atlas-domain"[^>]*>(.*?)(?=<details class="atlas-domain"|</div>\s*<h2|\Z)',
            _at, re.S):
        _grouped += (len(re.findall(r'\sid="s_[a-z0-9_]+"', _m.group(1)))
                     + len(re.findall(r'\sid="p_[a-z0-9_]+"', _m.group(1)))
                     + len(re.findall(r'\sid="x_[a-z0-9_]+"', _m.group(1))))
    check("every atlas chart sits inside a collapsible domain",
          _grouped == _atlas, f"{_grouped} of {_atlas} grouped")

    # 6. NO STALE REPORT NUMBERS. A figure moved out of the report must not
    #    still announce itself as "Figure 7": that number belongs to whatever
    #    now occupies the seventh position there.
    _numbered = re.findall(r'<span class="fignum">([^<]*)</span>', _at)
    check("no appendix figure displays a report figure number",
          not _numbered, ", ".join(_numbered[:5]))

    # ---- THE FIXED BASKET IS STILL THE BASKET THE RULE SELECTS ----------
    #
    # The breadth figure rests on a membership rule fixed before any result was
    # looked at: every indicator with a valid EU position in both 2008 and
    # 2024, chosen without reference to direction. A stored basket is only
    # worth anything if the rule still produces it, so the rule is re-run here
    # against the series and the two memberships compared. A silent change of
    # membership would move the headline without moving anything visible.
    import pandas as _pd
    _bk = ROOT / "data" / "processed" / "breadth_fixed_basket.csv"
    _core = ROOT / "data" / "processed" / "appendix_series_core.json"
    if _bk.exists() and _core.exists():
        _src = (ROOT / "scripts" / "46_appendix_data.py").read_text()
        _wh = eval("{" + _src.split("WORSE_HIGH = {")[1].split("}")[0] + "}")
        _circ = eval("{" + _src.split("CIRCULAR = {")[1].split("}")[0] + "}")
        _minr = int(_src.split("MIN_REPORTERS = ")[1].split("\n")[0])
        _wq = float(_src.split("WORST_Q = ")[1].split("\n")[0])
        _ser = json.loads(_core.read_text())["series"]

        def _pos(k, yr):
            v = _ser[k]
            if yr not in v["years"]:
                return None
            i = v["years"].index(yr)
            vals = {c: sv[i] for c, sv in v["countries"].items()
                    if sv[i] is not None}
            if len(vals) < _minr or "EL" not in vals:
                return None
            s = _pd.Series(vals) if _wh[k] else -_pd.Series(vals)
            return 100 * float(s.rank(pct=True)["EL"])

        _want = sorted(k for k in _wh if k not in _circ and k in _ser
                       and _pos(k, 2008) is not None and _pos(k, 2024) is not None)
        _have = sorted(_pd.read_csv(_bk)["key"])
        check("the fixed basket is exactly what its selection rule derives",
              _want == _have,
              f"rule gives {len(_want)}, stored has {len(_have)}; "
              f"differences {sorted(set(_want) ^ set(_have))[:4]}")

        # And the headline the report prints must be the basket's own count.
        _b = _pd.read_csv(_bk)
        _line = 100 * (1 - _wq)
        _n8 = int((_b.pct_2008 >= _line).sum())
        _n24 = int((_b.pct_2024 >= _line).sum())
        # The caption is generated and prints digits; the prose is written and
        # spells the numbers. Both must agree with the basket.
        _WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                  "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                  "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
                  "fifteen": 15, "sixteen": 16, "seventeen": 17}

        def _num(s):
            s = s.strip().lower()
            return int(s) if s.isdigit() else _WORDS.get(s)

        _claims = re.findall(
            r"worst fifth on ([\w]+) in 2008 to ([\w]+) in 2024", _rt)
        _bad_h = [c for c in _claims
                  if _num(c[0]) != _n8 or _num(c[1]) != _n24]
        check("every breadth headline in the report matches the stored basket",
              bool(_claims) and not _bad_h,
              f"basket says {_n8} -> {_n24}; report says {_bad_h or _claims}")

    _r, _a = _fig_hashes(_rt), _fig_hashes(_at)
    _gap = [k for k in _r if k not in _a]
    _diff = [k for k in _r if k in _a and _r[k] != _a[k]]
    print(f"\nappendix superset: {len(_r)} report figures, {len(_a)} in appendix")
    check("every report figure appears in the appendix", not _gap, str(_gap))
    check("appendix figures carry the report's exact payloads", not _diff, str(_diff))

    # -----------------------------------------------------------------------
    # THE APPENDIX'S EIGHT-STAGE STRUCTURE. Added when the appendix was
    # regrouped from six flat "kind of evidence" categories -- assembled
    # separately from the variable atlas and, until a structural bug was
    # fixed in the same change, appended after the page's own footer -- into
    # eight sections following the report's own stage order, each holding a
    # stage's report figures, shed views, descriptive and diagnostic detail,
    # context and underlying variables together. These checks hold that
    # structure in place; each was negative-tested by breaking the condition
    # it checks and confirming the check fails before the break was reverted.
    _stage_secs = re.findall(r'<section id="stage-(\d)" class="appx-stage">(.*?)</section>\s*(?=<section|<h2 class="group")',
                              _at, re.S)
    _stage_nums = [int(n) for n, _ in _stage_secs]
    check("appendix stage sections occur in report order",
          _stage_nums == sorted(_stage_nums) and _stage_nums == list(range(1, len(_stage_nums) + 1)),
          str(_stage_nums))

    _all_fig_ids = re.findall(r'<figure class="figure" id="([A-Z]\d+[A-Z]?)">', _at)
    _fig_stage_count = {}
    for _n, _body in _stage_secs:
        for _fid in re.findall(r'<figure class="figure" id="([A-Z]\d+[A-Z]?)">', _body):
            _fig_stage_count[_fid] = _fig_stage_count.get(_fid, 0) + 1
    _unassigned = [f for f in _all_fig_ids if _fig_stage_count.get(f, 0) == 0]
    _multi = [f for f, c in _fig_stage_count.items() if c > 1]
    check("every appendix figure is assigned to exactly one stage section",
          not _unassigned and not _multi,
          f"unassigned: {_unassigned}; in more than one stage: {_multi}")

    _order_bad = []
    for _n, _body in _stage_secs:
        _feat = _body.find('class="featured-group"')
        _atlas = _body.find('class="atlas-domain"')
        if _feat != -1 and _atlas != -1 and _feat > _atlas:
            _order_bad.append(_n)
    check("featured evidence appears before the variable atlas, within every stage",
          not _order_bad, f"stages with atlas before featured content: {_order_bad}")

    _i_stage8 = _at.find('<section id="stage-8"')
    _i_source = _at.find('id="source-notes"')
    _i_glossary = _at.find('id="glossary"')
    _i_footer = _at.find("<footer>")
    _i_footer_end = _at.find("</footer>")
    check("source and coverage notes follow the eighth stage",
          -1 < _i_stage8 < _i_source, f"{_i_stage8}, {_i_source}")
    check("the glossary follows source and coverage notes, as the final substantive section",
          -1 < _i_source < _i_glossary, f"{_i_source}, {_i_glossary}")
    check("the footer is the final visible element",
          -1 < _i_glossary < _i_footer, f"{_i_glossary}, {_i_footer}")
    _figs_after_footer = re.findall(r'<figure class="figure" id="([A-Z]\d+[A-Z]?)">',
                                     _at[_i_footer_end:]) if _i_footer_end != -1 else []
    check("no figure is emitted after the footer",
          not _figs_after_footer, str(_figs_after_footer))

    _atlas_details = re.findall(r'<details class="atlas-domain" id="(atlas-s\d)"([^>]*)>', _at)
    _open_by_default = [aid for aid, attrs in _atlas_details if " open" in attrs]
    check("every atlas group starts closed, so a deep link has something to open",
          bool(_atlas_details) and not _open_by_default, str(_open_by_default))
    check("the deep-link reveal script is present for every closed atlas group",
          "function reveal(hash)" in _at and "DOMContentLoaded" in _at)

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} figure checks pass")
if bad:
    raise SystemExit("FIGURE CHECKS FAILED: " + "; ".join(sorted(set(bad))))
