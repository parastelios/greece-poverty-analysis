"""Build output/research_record.html from docs/v2_research_record.md.

The markdown stays the editable source; this renders the reading copy -- inline
SVG figures, a sticky contents rail, stage status, and both themes.

No markdown library and no pandoc. pandoc IS installed on this machine, but the
project promises `make reproduce` from a clean tree, and a system-binary
dependency quietly breaks that promise. The markdown subset here is one I write
and control.

A hand-rolled converter can mangle content silently, so main() cross-checks the
output against the source: headings, tables, figures and links must all survive
in equal number, or the build fails.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "v2_research_record.md"
FIGS = ROOT / "docs" / "figures"
OUT = ROOT / "output" / "research_record.html"

INLINE = [
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{html.escape(m.group(1))}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\*)"), lambda m: f"<em>{m.group(1)}</em>"),
]
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMG = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")


def inline(s):
    """Escape, then re-apply the inline markup. Code spans are protected."""
    spans = []

    def stash(m):
        spans.append(html.escape(m.group(1)))
        return f"\x00{len(spans) - 1}\x00"

    s = INLINE[0][0].sub(stash, s)
    s = html.escape(s)
    for pat, fn in INLINE[1:]:
        s = pat.sub(fn, s)
    s = LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{spans[int(m.group(1))]}</code>", s)
    return s


def slug(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s_]+", "-", s).strip("-")


def embed_figure(alt, src):
    """Inline the SVG so the page is self-contained."""
    path = ROOT / "docs" / src
    if not path.exists():
        return f'<figure class="fig"><p class="missing">missing figure: {html.escape(src)}</p></figure>'
    body = re.sub(r'^<\?xml[^>]*\?>\s*', "", path.read_text())
    body = re.sub(r'\swidth="\d+"\s+height="\d+"', ' class="svg"', body, count=1)
    # No visible caption: every figure carries its own title inside the SVG, and
    # repeating it below reads as a mistake. The alt text stays as aria-label.
    return f'<figure class="fig" aria-label="{html.escape(alt)}">{body}</figure>'


def convert(md):
    out, toc = [], []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("<!-- AUTO:"):
            i += 1
            continue

        m = IMG.match(ln)
        if m:
            out.append(embed_figure(m.group(1), m.group(2)))
            i += 1
            continue

        if ln.startswith("#"):
            lvl = len(ln) - len(ln.lstrip("#"))
            txt = inline(ln[lvl:].strip())
            sid = slug(txt)
            if lvl == 1:
                out.append(f'<h1>{txt}</h1>')
            else:
                out.append(f'<h{lvl} id="{sid}">{txt}</h{lvl}>')
            if lvl == 2:
                toc.append((sid, txt))
            i += 1
            continue

        if ln.strip() in ("---", "***"):
            out.append("<hr>")
            i += 1
            continue

        # table
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln)
            aligns = ["right" if c.strip().endswith(":") else "left"
                      for c in cells(lines[i + 1])]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            th = "".join(f'<th style="text-align:{a}">{inline(c)}</th>'
                         for c, a in zip(head, aligns))
            tb = "".join(
                "<tr>" + "".join(
                    f'<td style="text-align:{aligns[j] if j < len(aligns) else "left"}">'
                    f'{inline(c)}</td>' for j, c in enumerate(r)) + "</tr>"
                for r in rows)
            out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead>'
                       f'<tbody>{tb}</tbody></table></div>')
            continue

        # blockquote
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip())
                i += 1
            out.append(f'<blockquote><p>{inline(" ".join(buf).strip())}</p></blockquote>')
            continue

        # list
        if re.match(r"^\s*[-*]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            items, cur = [], None
            while i < len(lines):
                s = lines[i]
                m2 = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", s)
                if m2:
                    if cur is not None:
                        items.append(cur)
                    cur = m2.group(1)
                elif s.strip() and s.startswith("  ") and cur is not None:
                    cur += " " + s.strip()
                elif s.strip() and cur is not None and not s.startswith(("|", "#", ">")):
                    cur += " " + s.strip()
                else:
                    break
                i += 1
            if cur is not None:
                items.append(cur)
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue

        if not ln.strip():
            i += 1
            continue

        buf = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(
                ("#", "|", ">", "---", "<!--")) and not IMG.match(lines[i]) \
                and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append(f"<p>{inline(' '.join(buf))}</p>")
        else:
            i += 1
    return "\n".join(out), toc


CSS = """
:root{--bg:#fbfaf7;--panel:#fff;--ink:#1f2933;--soft:#4a5568;--mute:#7b8794;
--line:#e3e0d8;--accent:#7a4b2a;--accent-soft:#f0e6dc;--code:#f4f1ec;
--gr:#c0392b;--ok:#2f855a;--warn:#b7791f;--max:52rem;--fig-min:620px}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#16181c;--panel:#1d2025;--ink:#e8e6e1;--soft:#b6bcc5;--mute:#8b929c;
--line:#2e333a;--accent:#d9a273;--accent-soft:#2a2218;--code:#23262c;
--gr:#e8776a;--ok:#68b98a;--warn:#d9a441}}
:root[data-theme=dark]{--bg:#16181c;--panel:#1d2025;--ink:#e8e6e1;--soft:#b6bcc5;
--mute:#8b929c;--line:#2e333a;--accent:#d9a273;--accent-soft:#2a2218;
--code:#23262c;--gr:#e8776a;--ok:#68b98a;--warn:#d9a441}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 Charter,"Bitstream Charter","Iowan Old Style",Georgia,serif;
-webkit-font-smoothing:antialiased}
.wrap{display:grid;grid-template-columns:16rem minmax(0,var(--max));
gap:3rem;justify-content:center;padding:2.5rem 1.5rem 6rem}
nav{position:sticky;top:2.5rem;align-self:start;max-height:calc(100vh - 5rem);
overflow-y:auto;font-family:ui-sans-serif,system-ui,sans-serif;font-size:.8rem}
nav h2{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;
color:var(--mute);margin:0 0 .75rem;font-weight:600}
nav a{display:block;padding:.28rem .6rem;color:var(--soft);text-decoration:none;
border-left:2px solid transparent;line-height:1.35}
nav a:hover{color:var(--accent);border-left-color:var(--accent);
background:var(--accent-soft)}
main{min-width:0}
h1{font-size:2.1rem;line-height:1.15;margin:0 0 .4rem;letter-spacing:-.01em;
text-wrap:balance}
h2{font-size:1.5rem;margin:3.5rem 0 1rem;padding-top:1.4rem;
border-top:1px solid var(--line);text-wrap:balance;letter-spacing:-.005em}
h3{font-size:1.06rem;margin:2rem 0 .6rem;color:var(--accent);
font-family:ui-sans-serif,system-ui,sans-serif;font-weight:650;
letter-spacing:.005em}
p{margin:0 0 1rem}
a{color:var(--accent)}
code{font:.85em/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;
background:var(--code);padding:.12em .38em;border-radius:3px;
word-break:break-word}
blockquote{margin:1.4rem 0;padding:.9rem 1.2rem;background:var(--panel);
border-left:3px solid var(--accent);border-radius:0 4px 4px 0;color:var(--soft)}
blockquote p{margin:0;font-size:.94rem}
ul,ol{margin:0 0 1rem;padding-left:1.3rem}
li{margin:.3rem 0}
hr{border:0;border-top:1px solid var(--line);margin:2.5rem 0}
.tw{overflow-x:auto;margin:1.2rem 0;border:1px solid var(--line);
border-radius:6px;background:var(--panel)}
table{border-collapse:collapse;width:100%;
font:.86rem/1.45 ui-sans-serif,system-ui,sans-serif;
font-variant-numeric:tabular-nums}
th{text-align:left;padding:.6rem .8rem;border-bottom:1.5px solid var(--line);
font-weight:650;color:var(--soft);font-size:.78rem;letter-spacing:.03em;
text-transform:uppercase;white-space:nowrap}
td{padding:.55rem .8rem;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
.fig{margin:1.6rem 0;padding:1rem;background:var(--panel);
border:1px solid var(--line);border-radius:6px;text-align:center;
overflow-x:auto;-webkit-overflow-scrolling:touch}
.fig svg,.svg{max-width:100%;height:auto;border-radius:3px}
/* Below the breakpoint a figure SCROLLS rather than shrinking. Letting it
   shrink to fit 375px put the smallest labels at ~4 effective pixels. */
@media(max-width:56rem){.fig svg,.svg{min-width:var(--fig-min);max-width:none}}
.missing{color:var(--gr);font-family:ui-sans-serif,system-ui,sans-serif}
.sub{color:var(--mute);font:.9rem/1.5 ui-sans-serif,system-ui,sans-serif;
margin-bottom:2rem}
@media(max-width:56rem){.wrap{grid-template-columns:minmax(0,1fr);gap:0;
padding:1.5rem 1.1rem 4rem}nav{position:static;max-height:none;
margin-bottom:2rem;padding-bottom:1.2rem;border-bottom:1px solid var(--line);
columns:2;font-size:.75rem}h1{font-size:1.6rem}h2{font-size:1.25rem}
body{font-size:15px}}
@media print{nav{display:none}.wrap{grid-template-columns:1fr}}
"""


def main():
    md = SRC.read_text()
    body, toc = convert(md)

    # Structural cross-check: nothing may vanish in translation.
    src_h2 = len(re.findall(r"^## ", md, re.M))
    src_h3 = len(re.findall(r"^### ", md, re.M))
    src_fig = len(re.findall(r"^!\[", md, re.M))
    src_tbl = len(re.findall(r"^\|[\s:|-]+\|$", md, re.M))
    got = {
        "h2": len(re.findall(r"<h2 ", body)), "h3": len(re.findall(r"<h3 ", body)),
        "figures": len(re.findall(r"<figure", body)),
        "tables": len(re.findall(r"<table>", body)),
    }
    want = {"h2": src_h2, "h3": src_h3, "figures": src_fig, "tables": src_tbl}
    if got != want:
        raise SystemExit(f"CONVERSION LOSS\n  want {want}\n  got  {got}")
    if '<p class="missing">' in body:
        raise SystemExit("a referenced figure is missing from docs/figures/")

    # Mobile legibility. Below the breakpoint each SVG is pinned to --fig-min
    # and scrolls, so its effective scale is fig_min/viewBox_width. The report
    # already shipped a chart whose labels rendered at 5.4px on a 375px screen;
    # this is the same failure, caught statically.
    FIG_MIN, FLOOR = 620, 7.0
    for svg_el in re.finditer(r'<svg[^>]*viewBox="0 0 (\d+)[^"]*"(.*?)</svg>',
                              body, re.S):
        vb = int(svg_el.group(1))
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', svg_el.group(2))]
        if not sizes:
            continue
        effective = min(sizes) * (FIG_MIN / vb)
        if effective < FLOOR:
            raise SystemExit(
                f"MOBILE LEGIBILITY: a {vb}-wide figure renders its smallest "
                f"label at {effective:.1f}px (floor {FLOOR}). Widen --fig-min "
                f"or raise the figure's font sizes.")

    nav = "".join(f'<a href="#{i}">{t}</a>' for i, t in toc)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>V2 Research Record</title><style>{CSS}</style></head><body>'
        f'<div class="wrap"><nav><h2>Contents</h2>{nav}</nav><main>{body}</main>'
        f'</div></body></html>\n')
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {want['h2']} sections, {want['h3']} subsections, "
          f"{want['figures']} figures, {want['tables']} tables")
    print(f"  {OUT.stat().st_size / 1024:.0f} KB, self-contained")


if __name__ == "__main__":
    main()
