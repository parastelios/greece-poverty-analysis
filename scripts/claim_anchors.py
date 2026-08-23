"""Shared anchor extraction for claims and context entries.

Lives in its own module because audit_parity.py is a script with no __main__
guard: importing the function from there ran the entire audit and exited.
"""
import html
import re


def containers(raw, attr, cid):
    """Text inside every element carrying <attr>="<cid>".

    A document-wide fingerprint search can be satisfied by unrelated prose or by
    chart data that happens to contain the number -- both already happened here.
    Anchored content is therefore checked against its container's text only.

    One implementation serves data-claim-id and data-context-id: the nesting
    logic is the fiddly part and should not exist twice.
    """
    out = []
    for mm in re.finditer(
            r'<(\w+)[^>]*\b' + re.escape(attr) + r'\s*=\s*["\']([^"\']+)["\'][^>]*>',
            raw):
        tag, ids = mm.group(1), mm.group(2)
        if cid not in [x.strip() for x in ids.split()]:
            continue
        i, depth, close = mm.end(), 1, len(raw)
        pat = re.compile(r"</?" + tag + r"\b", re.I)
        while depth:
            nxt = pat.search(raw, i)
            if not nxt:
                break
            depth += -1 if nxt.group(0).startswith("</") else 1
            # Cut at the START of the matching close tag, not its end: cutting
            # at the end left a trailing "</p" fragment in the extracted text,
            # which the tag-stripping regex cannot remove because it has no ">".
            close = nxt.start() if depth == 0 else close
            i = nxt.end()
        inner = raw[mm.end():min(close, i)]
        out.append(html.unescape(re.sub(r"<[^>]+>", " ", inner)))
    return out


def claim_containers(raw, cid):
    """Text inside every element carrying data-claim-id="<cid>"."""
    return containers(raw, "data-claim-id", cid)


def context_containers(raw, cid):
    """Text inside every element carrying data-context-id="<cid>"."""
    return containers(raw, "data-context-id", cid)


REQUIRED_PARTS = ("status", "permitted", "limitation", "citation")


def context_completeness(container_text, entry):
    """Which required parts are missing from one context container.

    A context entry is only auditable if its container carries, together:
      status       the evidence-status label
      permitted    the permitted interpretation
      limitation   the limitation or forbidden interpretation
      citation     the supporting source, where one applies

    Checking these as separate document-wide keywords was the previous design
    and could be satisfied by four unrelated sentences in four places.
    """
    low = " ".join(container_text.lower().split())
    missing = []
    if str(entry["status"]).lower() not in low:
        missing.append("status")
    if not _overlaps(low, entry["permitted"]):
        missing.append("permitted")
    if not _overlaps(low, entry["forbidden"]):
        missing.append("limitation")
    src = str(entry.get("source") or "")
    if src and src.lower() not in ("", "nan", "not applicable"):
        if not _overlaps(low, src, need=2):
            missing.append("citation")
    return missing


def _overlaps(haystack, needle, need=4):
    """Do at least `need` distinctive words of `needle` appear in `haystack`?

    Exact-string matching would force the prose to quote the register verbatim,
    which is not how a discussion section reads. Distinctive-word overlap
    tolerates paraphrase while still failing on an unrelated sentence.
    """
    stop = {"the", "a", "an", "and", "or", "not", "is", "are", "it", "its",
            "of", "to", "in", "as", "that", "this", "be", "may", "any", "for",
            "with", "on", "by", "from", "here", "does", "do", "no"}
    words = [w for w in re.findall(r"[a-z][a-z-]{3,}", str(needle).lower())
             if w not in stop]
    if not words:
        return True
    hits = sum(1 for w in set(words) if w in haystack)
    return hits >= min(need, len(set(words)))
