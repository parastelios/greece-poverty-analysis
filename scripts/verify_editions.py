"""The English and Greek narratives must say the same thing.

The Greek edition is NOT generated from the English one. It is built from its
own source file, with its own prose, by 92_build_narrative_el.py. That is a
deliberate choice -- a translated sentence and an authored Greek sentence are
different things, and the authored one reads better -- but it has an obvious
failure mode, and this project has already produced it once:

    An overclaim in the closing paragraph was corrected in the Greek edition
    and left standing in the English one. For several commits the two
    documents asserted different conclusions about the same analysis, and
    nothing in the build noticed.

Structural drift is the same hazard in a quieter form: a figure moved in one
edition and not the other, a finding box dropped, a claim placed in a
different section. Prose cannot be diffed across languages. Structure and
numbers can, so those are checked here:

  * the two editions place the same anchors in the same order;
  * every claim and context box carries the same numbers in both;
  * the charts carry identical DATA, whatever language their labels are in.

What this CANNOT check is meaning. A Greek paragraph that quietly softens a
conclusion still passes, as long as it carries the same numbers in the same
place. That is what editorial review is for. This gate exists so that the
mechanical half of the problem stops recurring.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "output" / "narrative.html"
EL = ROOT / "output" / "narrative_el.html"

F = []


def check(name, ok, detail=""):
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f"\n         {detail}" if detail and not ok else ""))


# ---------------------------------------------------------------------------
#  Readers
# ---------------------------------------------------------------------------
def anchors(doc):
    """The document's skeleton, in reading order.

    Deliberately excludes prose: the point is to compare what the two editions
    are made of and in what sequence, which survives translation, rather than
    the words, which must not.
    """
    out = []
    pattern = (r'<h2>|<figure class="figure" id="(\w+)"|data-claim-id="([^"]*)"'
               r'|data-context-id="([^"]+)"|<details class="disclosure">|<blockquote>')
    for m in re.finditer(pattern, doc):
        if m.group(1):
            out.append("figure:" + m.group(1))
        elif m.group(2):
            out.append("claim:" + " ".join(sorted(m.group(2).split())))
        elif m.group(3):
            out.append("context:" + m.group(3))
        elif m.group(0).startswith("<h2"):
            out.append("section")
        elif m.group(0).startswith("<details"):
            out.append("disclosure")
        else:
            out.append("pull-quote")
    return out


def statistics(text):
    """The statistics a box states, separator-insensitive.

    Greek writes 52,6 and 14.800 where English writes 52.6 and 14,800. Dropping
    both separators normalises the two conventions without having to guess
    which separator meant what, and that guess is where a comparison like this
    would otherwise go wrong.

    Restricted to numbers with a fractional part, which is what a headline
    statistic looks like. Bare integers are not comparable across the two
    editions and would make this gate cry wolf: English spells out "first of
    27" where Greek writes «1η από 27», and a year or a page number in a
    citation carries no claim at all.

    Entities are unescaped first. Without that, `&#x27;` -- the apostrophe in
    "Eurostat's" -- reads as the number 27.
    """
    plain = html.unescape(text)
    return sorted(re.sub(r"[.,]", "", n)
                  for n in re.findall(r"\d+[.,]\d+", plain))


def boxes(doc, attr):
    """Every claim or context box, keyed by its id, as plain text."""
    found = {}
    for m in re.finditer(rf'<div class="[^"]*" {attr}="([^"]+)">(.*?)</div>',
                         doc, re.S):
        text = re.sub(r"<[^>]+>", " ", m.group(2))
        for key in m.group(1).split():
            found.setdefault(key, "")
            found[key] += " " + text
    return found


def payload_shape(doc):
    """Chart payloads with every string blanked out.

    What survives is the data and the structure. The Greek build translates
    labels and reformats displayed numbers; it must never touch a value, a
    series order or a key. Blanking the strings is what lets the two be
    compared at all, and what is left is precisely the part that has to match.
    """
    def blank(node):
        if isinstance(node, dict):
            return {k: blank(v) for k, v in node.items()}
        if isinstance(node, list):
            return [blank(v) for v in node]
        return "" if isinstance(node, str) else node

    shapes = []
    for fig in re.finditer(r'<figure class="figure" id="(\w+)">(.*?)</figure>',
                           doc, re.S):
        for pay in re.finditer(
                r'<script type="application/json"[^>]*>(.*?)</script>',
                fig.group(2), re.S):
            data = json.loads(pay.group(1).replace("<\\/", "</"))
            shapes.append((fig.group(1), json.dumps(blank(data), sort_keys=True)))
    return shapes


# ---------------------------------------------------------------------------
#  Checks
# ---------------------------------------------------------------------------
missing = [p.name for p in (EN, EL) if not p.exists()]
check("both editions are built", not missing, f"missing: {missing}")
if missing:
    # Nothing below can run, and a silent skip is how the divergence this file
    # exists to prevent came back the first time.
    raise SystemExit("EDITION CHECKS FAILED: build both narratives first")

en, el = EN.read_text(encoding="utf-8"), EL.read_text(encoding="utf-8")

a_en, a_el = anchors(en), anchors(el)
first_diff = next((f"position {i}: EN={x!r} EL={y!r}"
                   for i, (x, y) in enumerate(zip(a_en, a_el)) if x != y),
                  f"lengths {len(a_en)} vs {len(a_el)}")
check("both editions place the same anchors in the same order",
      a_en == a_el, first_diff)

for kind, attr in (("claim", "data-claim-id"), ("context", "data-context-id")):
    b_en, b_el = boxes(en, attr), boxes(el, attr)
    check(f"both editions carry the same {kind} boxes",
          set(b_en) == set(b_el),
          f"EN-only {sorted(set(b_en) - set(b_el))}, "
          f"EL-only {sorted(set(b_el) - set(b_en))}")
    drift = [k for k in sorted(set(b_en) & set(b_el))
             if statistics(b_en[k]) != statistics(b_el[k])]
    check(f"every {kind} box states the same statistics in both editions",
          not drift,
          "; ".join(f"{k}: EN={statistics(b_en[k])} EL={statistics(b_el[k])}"
                    for k in drift[:3]))

s_en, s_el = payload_shape(en), payload_shape(el)
check("both editions draw the same charts from the same data",
      s_en == s_el,
      next((f"{x[0]} differs" for x, y in zip(s_en, s_el) if x != y),
           f"{len(s_en)} payloads vs {len(s_el)}"))

bad = [n for n, ok in F if not ok]
print(f"\n{len(F) - len(bad)}/{len(F)} edition checks pass")
if bad:
    raise SystemExit("EDITION CHECKS FAILED: " + "; ".join(sorted(set(bad))))
