"""Render the three published HTML reports to print-ready PDFs.

Uses headless Chrome, which is required rather than incidental: report.html
draws every chart from an embedded JSON blob at runtime, and both report.html
and narrative.html move their method blocks into <details> elements
with JavaScript. A non-JS renderer (weasyprint, wkhtmltopdf) would produce
PDFs with blank charts and, worse, silently drop the collapsed method notes.

Before printing, each document is copied to a temp file with a print layer
injected that:
  - forces the light palette (the documents are theme-aware; a reader printing
    in dark mode would otherwise get dark pages),
  - opens every <details> block, since "click to expand" is meaningless on
    paper and the content would otherwise be missing entirely,
  - adds page-break rules so cards, tables, findings and figures are not split
    across pages,
  - hides interactive-only furniture (hover tooltips).

Usage:  python make_pdfs.py            -> writes output/pdf/*.pdf
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"

# The three publication documents, all generated from the same claim set.
# report.html, narrative_companion.html and academic_paper_draft.html are the
# superseded builds and are not exported.
DOCS = [
    ("v2_report.html", "Greek-Poverty-Paradox-technical-report.pdf"),
    ("narrative.html", "Greek-Poverty-Paradox-narrative.pdf"),
    ("academic_paper.html", "Greek-Poverty-Paradox-working-paper.pdf"),
]

# Injected into <head>, i.e. BEFORE the documents' own scripts. This matters:
# report.html's chart code reads getComputedStyle(--series-*) at draw time and
# bakes the result into each SVG stroke. Injecting these tokens at the end of
# <body> (the obvious place) leaves the charts drawn in whatever palette was
# active earlier -- in headless Chrome, the dark one -- which then gets painted
# onto a forced-white page. That happens to be legible, but only by accident.
HEAD_LAYER = """
<style id="pdf-colour-layer">
  /* Force the light palette: these documents are theme-aware, and a dark
     rendering would waste ink and read poorly on paper. */
  :root, :root:not([data-theme="light"]) {
    color-scheme: light !important;
    --page:#ffffff !important; --surface-1:#ffffff !important; --surface-2:#f4f3ef !important;
    --text-primary:#0b0b0b !important; --text-secondary:#3f3e3b !important;
    --text-muted:#6b6963 !important; --gridline:#e1e0d9 !important;
    --border:rgba(11,11,11,0.14) !important;
    --paper:#ffffff !important; --ink:#0b0b0b !important; --ink-mute:#3f3e3b !important;
    --bg:#ffffff !important; --rule:#e1e0d9 !important; --code-bg:#f4f3ef !important;
  }
  html, body { background:#ffffff !important; }
  /* Deliberate mid-grey for the "every other EU country" chart lines: the
     light-theme --gridline is too faint to print, the dark-theme value too
     heavy against the highlighted Greece line. */
  :root, :root:not([data-theme="light"]) { --gridline:#b0afa8 !important; }
</style>
"""

BODY_LAYER = """
<style id="pdf-print-layer">
  @page { size: A4; margin: 16mm 14mm 18mm; }

  /* Keep atomic blocks whole. Long method prose is deliberately NOT in this
     list: those blocks can exceed a full page, and forcing them whole leaves
     their heading stranded on an otherwise-blank sheet. They flow instead,
     with the summary pinned to the start of its own content (rule below). */
  .card, .finding, .answer-box,
  .stat-tile, .tile, table, figure, .chart-wrap, .proof, .checked-item,
  .table-wrap, blockquote, .callout, .story-map
    { break-inside: avoid; page-break-inside: avoid; }
  details.method-details > summary
    { break-after: avoid; page-break-after: avoid; }
  h1,h2,h3,h4,.chapter-title,.sec-title { break-after: avoid; page-break-after: avoid; }
  .chapter { break-before: page; page-break-before: page; }
  section { break-before: auto; }

  /* Interactive-only furniture. */
  .tooltip { display:none !important; }
  /* Decorative chapter dividers: on screen they separate chapters, but in print
     each chapter already starts on a fresh page, so they add nothing and can be
     pushed onto a page of their own -- producing otherwise-blank sheets. */
  svg.crack { display:none !important; }
  details.method-details > summary { list-style:none; font-weight:700; }
  details.method-details > summary::-webkit-details-marker { display:none; }

  /* Long identifiers in method notes must wrap rather than overflow. */
  code { overflow-wrap:anywhere; word-break:break-word; }
  table { width:100% !important; min-width:0 !important; font-size:11px !important; }
  .table-scroll, .mini-scroll { overflow:visible !important; }
  a { color: inherit; text-decoration: none; }
</style>
<script>
  // Expand everything: a collapsed <details> prints as missing content, not as
  // a closed block. Runs after the documents' own scripts have created them.
  window.addEventListener('load', function () {
    document.querySelectorAll('details').forEach(function (d) { d.open = true; });
  });
</script>
"""


def main():
    if not Path(CHROME).exists():
        sys.exit(f"Chrome not found at {CHROME}")
    OUT.mkdir(parents=True, exist_ok=True)
    tmpdir = Path(tempfile.mkdtemp(prefix="pdf_build_"))
    made = []

    for src_name, pdf_name in DOCS:
        src = ROOT / "output" / src_name
        html = src.read_text(encoding="utf-8")
        # Colour tokens first, before any chart script can read them.
        if "<title>" in html:
            html = html.replace("<title>", HEAD_LAYER + "\n<title>", 1)
        else:
            html = HEAD_LAYER + html
        # Layout/expansion last, after the documents' own scripts have run.
        if "</body>" in html:
            html = html.replace("</body>", BODY_LAYER + "\n</body>", 1)
        else:
            html += BODY_LAYER
        staged = tmpdir / src_name
        staged.write_text(html, encoding="utf-8")

        dest = OUT / pdf_name
        cmd = [
            CHROME, "--headless", "--disable-gpu", "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=20000",
            "--no-pdf-header-footer",
            f"--print-to-pdf={dest}",
            staged.as_uri(),
        ]
        print(f"rendering {src_name} -> {pdf_name}")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if not dest.exists() or dest.stat().st_size == 0:
            print(r.stderr[-800:])
            sys.exit(f"FAILED to render {src_name}")
        made.append((pdf_name, dest.stat().st_size))

    shutil.rmtree(tmpdir, ignore_errors=True)
    print("\nWritten to output/pdf/:")
    for name, size in made:
        print(f"  {name:48} {size/1_048_576:5.2f} MB")


if __name__ == "__main__":
    main()
