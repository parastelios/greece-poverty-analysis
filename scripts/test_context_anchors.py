"""Tests for context-container auditing. Run: python test_context_anchors.py"""
from claim_anchors import (containers, claim_containers, context_containers,
                           context_completeness, REQUIRED_PARTS)

F = []
def check(name, got, want):
    ok = got == want
    F.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:56} got {got} want {want}")

E = {"status": "contextual evidence",
     "permitted": "May affect how households interpret insecurity; available "
                  "evidence does not identify an independent effect.",
     "forbidden": "Presenting trust as an explanation of the residual, or "
                  "implying it was tested and found to matter.",
     "source": "Eurobarometer institutional-trust items"}

FULL = ('<div data-context-id="CTX-2">Institutional trust is contextual evidence. '
        'It may affect how households interpret insecurity, and the available '
        'evidence does not identify an independent effect. It is not presented '
        'as an explanation of the residual and was not tested here. '
        'Source: Eurobarometer institutional-trust items.</div>')

print("extraction")
check("finds its container", len(context_containers(FULL, "CTX-2")), 1)
check("ignores a different id", len(context_containers(FULL, "CTX-3")), 0)
check("claim wrapper still works",
      len(claim_containers('<p data-claim-id="X">y</p>', "X")), 1)
check("one implementation serves both",
      containers('<p data-context-id="A">z</p>', "data-context-id", "A"), [" z "[1:2] and "z"])

print("\\nnested tags do not truncate the container")
nested = ('<div data-context-id="CTX-2">a <div>inner</div> contextual evidence '
          'may affect how households interpret insecurity available evidence '
          'does not identify an independent effect not an explanation of the '
          'residual was not tested Eurobarometer institutional-trust items</div>')
check("nesting handled", context_completeness(context_containers(nested, "CTX-2")[0], E), [])

print("\\ncompleteness: each required part detected independently")
check("complete container passes", context_completeness(context_containers(FULL, "CTX-2")[0], E), [])
no_status = FULL.replace("is contextual evidence", "is interesting")
check("missing status", context_completeness(context_containers(no_status, "CTX-2")[0], E), ["status"])
no_lim = FULL.replace("It is not presented as an explanation of the residual "
                      "and was not tested here. ", "")
check("missing limitation",
      context_completeness(context_containers(no_lim, "CTX-2")[0], E), ["limitation"])
no_cit = FULL.replace("Source: Eurobarometer institutional-trust items.", "")
check("missing citation",
      context_completeness(context_containers(no_cit, "CTX-2")[0], E), ["citation"])
bare = '<div data-context-id="CTX-2">Trust matters a great deal in Greece.</div>'
check("bare mention misses everything",
      sorted(context_completeness(context_containers(bare, "CTX-2")[0], E)),
      ["citation", "limitation", "permitted", "status"])

print("\\nno citation required when the entry has none")
E2 = dict(E); E2["source"] = ""
check("citation skipped when not applicable",
      context_completeness(context_containers(no_cit, "CTX-2")[0], E2), [])

print("\\nPARAPHRASE IS TOLERATED, UNRELATED PROSE IS NOT")
para = ('<div data-context-id="CTX-2">This is contextual evidence. Trust may '
        'affect the way households interpret their own insecurity, though the '
        'evidence available cannot identify an effect that is independent. We '
        'do not present it as an explanation of the residual, and it was never '
        'tested. Eurobarometer institutional-trust items.</div>')
check("paraphrase passes", context_completeness(context_containers(para, "CTX-2")[0], E), [])
junk = ('<div data-context-id="CTX-2">contextual evidence. The weather in '
        'Athens is warm and the food is good.</div>')
check("unrelated prose fails on everything but status",
      sorted(context_completeness(context_containers(junk, "CTX-2")[0], E)),
      ["citation", "limitation", "permitted"])

print("\\nREQUIRED_PARTS is the documented contract")
check("four required parts", list(REQUIRED_PARTS),
      ["status", "permitted", "limitation", "citation"])

bad = [n for n, ok in F if not ok]
print(f"\\n{len(F) - len(bad)}/{len(F)} passed")
if bad:
    raise SystemExit("FAILED: " + ", ".join(bad))
