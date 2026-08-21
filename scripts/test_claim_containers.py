"""Tests for data-claim-id container extraction in audit_parity.

The gate certified unwritten claims twice: once because a chart-data blob
contained the number, once because an unrelated methods phrase matched a
fingerprint fragment. Container anchoring is the fix, so it is tested rather
than trusted.
"""
import re, html, sys

from claim_anchors import claim_containers

CASES = [
    ("matches inside its container",
     '<p data-claim-id="10.2">falls from 27.05 to +6.93 points</p>', "10.2", "+6.93", True),
    ("identical text OUTSIDE any container does not count",
     '<p>the gap falls to +6.93 points</p>', "10.2", "+6.93", False),
    ("a container for a different claim does not count",
     '<p data-claim-id="10.1">+6.93 appears here wrongly</p>', "10.2", "+6.93", False),
    ("nested same-tag elements are handled",
     '<div data-claim-id="10.3"><div>predominantly between countries</div> t</div>',
     "10.3", "predominantly between countries", True),
    ("no bleed past the closing tag",
     '<p data-claim-id="10.4">design failed</p><p>+6.93 out here</p>', "10.4", "+6.93", False),
    ("a container may own several claims",
     '<div data-claim-id="10.1 10.2">27.05 and +6.93</div>', "10.2", "+6.93", True),
    ("inner markup is stripped before matching",
     '<p data-claim-id="10.6">the <b>backward-extended official</b> series</p>',
     "10.6", "backward-extended official", True),
    ("single quotes on the attribute",
     "<p data-claim-id='10.2'>+6.93</p>", "10.2", "+6.93", True),
    ("absent claim id yields no blocks",
     '<p data-claim-id="10.2">+6.93</p>', "10.9", "+6.93", False),
]
fails = 0
for name, raw, cid, fp, want in CASES:
    got = any(fp.lower() in b.lower() for b in claim_containers(raw, cid))
    good = got == want
    fails += not good
    print(f"  [{'PASS' if good else 'FAIL'}] {name:50} {got} (want {want})")
print(f"\n{len(CASES)-fails}/{len(CASES)} passed")
sys.exit(1 if fails else 0)
