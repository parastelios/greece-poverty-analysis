"""Shared claim-anchor extraction.

Lives in its own module because audit_parity.py is a script with no __main__
guard: importing the function from there ran the entire audit and exited.
"""
import html
import re


def claim_containers(raw, cid):
    """Text inside every element carrying data-claim-id="<cid>".

    A document-wide fingerprint search can be satisfied by unrelated prose or by
    chart data that happens to contain the number -- both already happened here.
    V2 claims must therefore be anchored in an explicit container, and the
    fingerprint is checked against that container's text only.
    """
    out = []
    for mm in re.finditer(
            r'<(\w+)[^>]*\bdata-claim-id\s*=\s*["\']([^"\']+)["\'][^>]*>', raw):
        tag, ids = mm.group(1), mm.group(2)
        if cid not in [x.strip() for x in ids.split()]:
            continue
        i, depth = mm.end(), 1
        pat = re.compile(r"</?" + tag + r"\b", re.I)
        while depth:
            nxt = pat.search(raw, i)
            if not nxt:
                break
            depth += -1 if nxt.group(0).startswith("</") else 1
            i = nxt.end()
        inner = raw[mm.end():i]
        out.append(html.unescape(re.sub(r"<[^>]+>", " ", inner)))
    return out

