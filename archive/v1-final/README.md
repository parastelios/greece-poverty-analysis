# V1 final — frozen archive

Snapshot of the four published outputs as at tag `v1-final`, taken before
P0 (outcome reconciliation) begins.

## Why the appendix is archived here too

The appendix has **one pipeline and one builder**, updated in place —
`scripts/46_appendix_data.py` and `scripts/47_build_appendix.py`. The builder
is never forked; the session that maintained two builders over one dataset
showed why.

But the *rendered* appendix must be versioned even though the builder is not.
The three V1 reports point the reader at "the statistical appendix". Once the
canonical appendix at `output/statistical_appendix.html` advances to V2 models
and revised claims, those pointers would resolve to content the V1 reports were
never written against. **The appendix in this directory is the one the V1
reports refer to.** The canonical appendix becomes the V2 appendix when V2 is
published.

## What this archive is, and is not

- **Evidence: preserved.** The measurement finding, the screening record
  (families A, B and C with their FDR tables), every null, the failed
  synthetic-control design, and the descriptive work all carry forward.
- **Framing: superseded.** V1's headline was Greece's out-of-sample residual in
  a cross-country model. `docs/project_description_v3.md` replaces that
  estimand. See its §2 for why.
- **Not a competing live version.** When V2 is released, V2 is the sole primary
  public interpretation and this remains a clearly superseded archive.

## Not included

**Family D** (accumulated multi-domain deterioration) is *not* part of the V1
screening record. It was developed after inspecting V1 results, its
construction and outputs were never formally added to the V1 pipeline, and it
was never frozen with a validated output. It is registered in
`docs/project_description_v3.md` §6a as a declared exploratory candidate for
V2, and it enters as one — not as a completed V1 family.

## Verification at freeze

`verify_build` 41/41 · `audit_parity` 140/140 · git tag `v1-final`
