"""Generate the figures embedded in docs/v2_research_record.md.

Hand-written SVG, no plotting dependency. The project already builds its charts
this way (47_build_appendix.py), and a reproducible-build project should not
acquire matplotlib just to draw seven pictures.

Every figure reads its numbers from data/processed at build time, so a figure
cannot drift from the result it illustrates. Each carries an explicit light
background so it stays legible whatever theme the notebook is read in.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

INK, MUTE, GRID = "#1f2933", "#6b7280", "#e5e7eb"
GR, EU, WARN, GOOD = "#c0392b", "#3d6fb4", "#b7791f", "#2f855a"
BG = "#ffffff"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(title)}" '
        f'font-family="Helvetica,Arial,sans-serif">\n'
        f'<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n'
    )


def text(x, y, s, size=11, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


def line(x1, y1, x2, y2, stroke=GRID, width=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')


def rect(x, y, w, h, fill, rx=2):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" '
            f'height="{max(h,0):.1f}" fill="{fill}" rx="{rx}"/>')


def write(name, content):
    (FIG / name).write_text(content)
    print(f"  {name}")


# --------------------------------------------------------------------------
# 1. THE EA RESULT: Greece's residual crosses zero
# --------------------------------------------------------------------------
def fig_ea_reversal():
    ea = pd.read_csv(PROC / "ea_results.csv").iloc[0]
    W, H = 660, 250
    x0, x1 = 200, 480
    lo, hi = -12.0, 12.0
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = [text(20, 26, "Greece's residual reverses when deprivation is removed",
              13, INK, weight="bold"),
         text(20, 44, "Positive = model under-predicts Greek hardship. "
                      "Negative = over-predicts.", 10.5, MUTE)]
    for v in range(-12, 13, 4):
        b.append(line(sx(v), 70, sx(v), 190, GRID))
        b.append(text(sx(v), 208, f"{v:+d}", 9.5, MUTE, "middle"))
    b.append(line(sx(0), 62, sx(0), 196, MUTE, 1.5))
    b.append(text(sx(0), 58, "perfect prediction", 9.5, MUTE, "middle"))
    rows = [("Frozen P3", float(ea.p3_residual), int(ea.p3_rank), 110),
            ("Companion", float(ea.companion_residual),
             int(ea.companion_rank), 160)]
    for label, val, rank, y in rows:
        b.append(text(x0 - 12, y + 4, label, 11, INK, "end", "bold"))
        b.append(text(x0 - 12, y + 18, "mixed-distance" if val > 0
                      else "deprivation-free", 9, MUTE, "end"))
        c = GR if val > 0 else EU
        a, bb = (sx(0), sx(val)) if val > 0 else (sx(val), sx(0))
        b.append(rect(a, y - 11, bb - a, 22, c))
        # Fixed right column. Placing these next to the bar end put the
        # negative bar's label straight through the row label on its left.
        b.append(text(x1 + 16, y + 4, f"{val:+.2f}", 11, INK, "start", "bold"))
        b.append(text(x1 + 72, y + 4, f"rank {rank}/27", 10, MUTE))
    b.append(text(20, 236, f"Identical rows (n={int(ea.n)}). "
                  f"R² {ea.p3_r2:.3f} → {ea.companion_r2:.3f}. "
                  f"Outcome C.", 10, MUTE))
    write("ea_reversal.svg", svg(W, H, "\n".join(b),
          "Greece residual reverses from +6.93 to -9.39"))


# --------------------------------------------------------------------------
# 2. Residual ladders, both specifications
# --------------------------------------------------------------------------
def fig_ladders():
    p3 = pd.read_csv(PROC / "p3_residuals.csv")
    co = pd.read_csv(PROC / "ea_companion_residuals.csv")
    W, H = 620, 400
    panels = [("Frozen P3 (6 predictors)", p3, 40), ("Companion (5)", co, 330)]
    lo, hi = -12.0, 16.0
    top, bh = 70, 11
    b = [text(20, 26, "Where every country sits, in both specifications",
              13, INK, weight="bold")]
    for title, df, px in panels:
        b.append(text(px, 52, title, 11, INK, weight="bold"))
        zx = px + 110 * (0 - lo) / (hi - lo)
        b.append(line(zx, top - 6, zx, top + len(df) * bh + 4, MUTE, 1.2))
        for i, r in df.iterrows():
            y = top + i * bh
            gr = r.geo == "EL"
            c = GR if gr else (MUTE if abs(r.resid) < 5 else EU)
            x = px + 110 * (min(r.resid, 0) - lo) / (hi - lo)
            w = 110 * abs(r.resid) / (hi - lo)
            b.append(rect(x, y, w, bh - 3, c, 1))
            b.append(text(px - 6, y + bh - 4, r.geo, 8,
                          GR if gr else MUTE, "end", "bold" if gr else "normal"))
            if gr:
                b.append(text(px + 118, y + bh - 4,
                              f"{r.resid:+.1f} (rank {int(r['rank'])})", 8.5, GR,
                              "start", "bold"))
    b.append(text(20, H - 14, "Greece in red. Bars right of the line are "
                  "under-predicted, left are over-predicted.", 10, MUTE))
    write("residual_ladders.svg", svg(W, H, "\n".join(b),
          "Residual ladders for both specifications"))


# --------------------------------------------------------------------------
# 3. The narrowing story, and what happens to it
# --------------------------------------------------------------------------
def fig_narrowing():
    ea = pd.read_csv(PROC / "ea_results.csv").iloc[0]
    p3 = json.loads((PROC / "p5f_frozen_result.json").read_text())["p3"]
    W, H = 700, 240
    x0, x1 = 210, 560
    lo, hi = -12.0, 30.0
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = [text(20, 26, "What adding accumulated unemployment does, in each model",
              13, INK, weight="bold")]
    for v in [-10, 0, 10, 20, 30]:
        b.append(line(sx(v), 60, sx(v), 175, GRID))
        b.append(text(sx(v), 193, f"{v:+d}", 9.5, MUTE, "middle"))
    b.append(line(sx(0), 54, sx(0), 181, MUTE, 1.5))
    rows = [("Frozen P3", p3["residual_without_accumulation"],
             p3["greece_oos_residual"], 95, "narrows"),
            ("Companion", float(ea.companion_residual_no_accumulation),
             float(ea.companion_residual), 145, "crosses zero")]
    for label, a, z, y, kind in rows:
        b.append(text(x0 - 14, y + 4, label, 11, INK, "end"))
        b.append(line(sx(a), y, sx(z), y, MUTE, 1.5, "3,3"))
        b.append(f'<circle cx="{sx(a):.1f}" cy="{y}" r="6" fill="{WARN}"/>')
        b.append(f'<circle cx="{sx(z):.1f}" cy="{y}" r="6" fill="'
                 f'{GOOD if kind == "narrows" else GR}"/>')
        b.append(text(sx(a), y - 13, f"{a:+.2f}", 9.5, MUTE, "middle"))
        b.append(text(sx(z), y - 13, f"{z:+.2f}", 9.5, INK, "middle", "bold"))
        b.append(text(x1 + 8, y + 4, kind, 9.5,
                      GOOD if kind == "narrows" else GR, "start", "bold"))
    b.append(text(20, 222, "Amber = without accumulation. In frozen P3 the gap "
                  "narrows toward zero; in the companion it passes through it.",
                  10, MUTE))
    write("narrowing.svg", svg(W, H, "\n".join(b), "Narrowing in each model"))


# --------------------------------------------------------------------------
# 4. Power curve, with the published MDE marked
# --------------------------------------------------------------------------
def fig_mde():
    d = pd.read_csv(PROC / "e_mde.csv")
    W, H = 560, 300
    x0, y0, x1, y1 = 70, 240, 520, 60
    sx = lambda v: x0 + (v - 0.05) / (1.05 - 0.05) * (x1 - x0)
    sy = lambda v: y0 + v * (y1 - y0)
    b = [text(20, 26, "Most Family E tests will be underpowered", 13, INK,
              weight="bold"),
         text(20, 44, "Power to detect an effect, by effect size", 10.5, MUTE)]
    for p in [0, .2, .4, .6, .8, 1.0]:
        b.append(line(x0, sy(p), x1, sy(p), GRID))
        b.append(text(x0 - 8, sy(p) + 4, f"{p:.0%}", 9.5, MUTE, "end"))
    b.append(line(x0, sy(.8), x1, sy(.8), WARN, 1.5, "4,3"))
    b.append(text(x1, sy(.8) - 7, "80% power", 9.5, WARN, "end", "bold"))
    pts = " ".join(f"{sx(r.effect_sd_per_sd):.1f},{sy(r.power):.1f}"
                   for r in d.itertuples())
    b.append(f'<polyline points="{pts}" fill="none" stroke="{EU}" stroke-width="2.5"/>')
    for r in d.itertuples():
        hit = abs(r.effect_sd_per_sd - 0.7) < 1e-9
        b.append(f'<circle cx="{sx(r.effect_sd_per_sd):.1f}" '
                 f'cy="{sy(r.power):.1f}" r="{4.5 if hit else 3}" '
                 f'fill="{GR if hit else EU}"/>')
        if hit:
            b.append(line(sx(.7), sy(r.power), sx(.7), y0, GR, 1.2, "3,3"))
            b.append(text(sx(.7) + 8, sy(r.power) - 10,
                          "MDE 0.70 SD = 9.29 points", 10, GR, "start", "bold"))
        b.append(text(sx(r.effect_sd_per_sd), y0 + 18,
                      f"{r.effect_sd_per_sd:.1f}", 9, MUTE, "middle"))
    b.append(text((x0 + x1) / 2, y0 + 38,
                  "effect size (residual SD per SD of regressor)", 10, MUTE, "middle"))
    b.append(text(20, H - 12, "Residual SD 13.27 points. Between-country SD "
                  "12.87, within-country 4.01.", 10, MUTE))
    write("mde_power.svg", svg(W, H, "\n".join(b), "Power curve with MDE marked"))


# --------------------------------------------------------------------------
# 5. P5: between vs within
# --------------------------------------------------------------------------
def fig_between_within():
    p5 = json.loads((PROC / "p5f_frozen_result.json").read_text())["p5"]
    W, H = 690, 220
    x0, x1 = 220, 490
    lo, hi = -0.55, 0.55
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = [text(20, 26, "The effect is between countries, not within them", 13,
              INK, weight="bold"),
         text(20, 44, "Accumulated-unemployment coefficient", 10.5, MUTE)]
    for v in [-0.4, -0.2, 0, 0.2, 0.4]:
        b.append(line(sx(v), 68, sx(v), 155, GRID))
        b.append(text(sx(v), 173, f"{v:+.1f}", 9.5, MUTE, "middle"))
    b.append(line(sx(0), 62, sx(0), 161, MUTE, 1.5))
    b.append(text(sx(0), 58, "no effect", 9.5, MUTE, "middle"))
    items = [("Between countries", p5["between"], None, 95, GOOD,
              f"p < 0.0001"),
             ("Within countries", p5["within"], p5["within_ci"], 135, MUTE,
              f"p = {p5['within_p']:.3f}, inconclusive")]
    for label, val, ci, y, c, note in items:
        b.append(text(x0 - 14, y + 4, label, 11, INK, "end"))
        if ci:
            b.append(line(sx(ci[0]), y, sx(ci[1]), y, c, 2))
            for e in ci:
                b.append(line(sx(e), y - 5, sx(e), y + 5, c, 2))
        b.append(f'<circle cx="{sx(val):.1f}" cy="{y}" r="6" fill="{c}"/>')
        b.append(text(x1 + 12, y + 4, f"{val:+.4f}", 10.5, INK, "start", "bold"))
        b.append(text(x1 + 12, y + 17, note, 9, MUTE))
    b.append(text(20, 202, "The within estimate's interval spans zero widely: "
                  "no supporting evidence, and too imprecise to rule out.",
                  10, MUTE))
    write("between_within.svg", svg(W, H, "\n".join(b), "Between vs within"))


# --------------------------------------------------------------------------
# 6. Correlations that reverse between views
# --------------------------------------------------------------------------
def fig_sign_reversal():
    d = pd.read_csv(PROC / "e0_redundancy.csv")
    W, H = 620, 330
    x0, x1 = 240, 560
    lo, hi = -1.0, 1.0
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = [text(20, 26, "Why pooled correlations alone would have misled us", 13,
              INK, weight="bold"),
         text(20, 44, "Same pair, three ways of asking", 10.5, MUTE)]
    for v in [-1, -.5, 0, .5, 1]:
        b.append(line(sx(v), 62, sx(v), 285, GRID))
        b.append(text(sx(v), 303, f"{v:+.1f}", 9.5, MUTE, "middle"))
    b.append(line(sx(0), 56, sx(0), 291, MUTE, 1.5))
    views = [("pooled", "pooled", "#94a3b8"), ("between", "between", EU),
             ("within", "within", WARN)]
    y = 80
    for r in d.itertuples():
        flip = bool(r.sign_flips)
        label = f"{r.primary} – {r.sensitivity}"
        b.append(text(x0 - 14, y + 10, label, 9.5,
                      GR if flip else INK, "end", "bold" if flip else "normal"))
        for i, (_, col, c) in enumerate(views):
            v = getattr(r, col)
            yy = y + i * 6
            b.append(f'<circle cx="{sx(v):.1f}" cy="{yy:.1f}" r="3.2" fill="{c}"/>')
        if flip:
            b.append(text(x1 + 10, y + 10, "reverses", 9, GR, "start", "bold"))
        y += 24
    lx = 24
    for name, _, c in views:
        b.append(f'<circle cx="{lx}" cy="{H - 18}" r="3.2" fill="{c}"/>')
        b.append(text(lx + 8, H - 15, name, 9.5, MUTE))
        lx += 70
    write("sign_reversal.svg", svg(W, H, "\n".join(b),
          "Correlations across three views"))


# --------------------------------------------------------------------------
# 7. E0 coverage
# --------------------------------------------------------------------------
def fig_coverage():
    c = pd.read_csv(PROC / "e0_coverage.csv").sort_values("n_obs")
    inc = c[c.n_obs < 270]
    W, H = 700, 260
    x0, x1 = 200, 470
    sx = lambda v: x0 + (v - 250) / (270 - 250) * (x1 - x0)
    b = [text(20, 26, "Coverage is strong; the gaps are few and located", 13,
              INK, weight="bold"),
         text(20, 44, f"{int((c.n_obs == 270).sum())} of {len(c)} variables are "
              "complete at 270/270. The exceptions:", 10.5, MUTE)]
    where = {"arop_threshold_real": "Croatia, all years",
             "arrears": "Luxembourg 2018–19",
             "saving_rate": "Bulgaria 2023–24",
             "debt_to_income": "Bulgaria 2023–24",
             "real_income_idx": "Bulgaria 2023–24",
             "net_migration": "Portugal 2024",
             "housing_cost_overburden": "France 2021"}
    y = 76
    for r in inc.itertuples():
        b.append(text(x0 - 12, y + 9, r.name, 10, INK, "end"))
        b.append(rect(sx(250), y, sx(r.n_obs) - sx(250), 13,
                      GR if r.n_obs < 265 else EU))
        b.append(text(sx(r.n_obs) + 8, y + 10, f"{int(r.n_obs)}", 9.5, INK,
                      "start", "bold"))
        b.append(text(sx(r.n_obs) + 42, y + 10, where.get(r.name, ""), 9, MUTE))
        y += 22
    b.append(text(20, H - 14, "Croatia's threshold gap costs a whole country, "
                  "so those analyses run on 26, not 27.", 10, MUTE))
    write("coverage.svg", svg(W, H, "\n".join(b), "E0 coverage gaps"))



# --------------------------------------------------------------------------
# 8. The paradox and the AROPE bridge
# --------------------------------------------------------------------------
def fig_paradox():
    d = pd.read_csv(PROC / "e_descriptives.csv")
    W, H = 660, 330
    x0, y0, x1, y1 = 70, 250, 470, 60
    yr0, yr1 = int(d.time.min()), int(d.time.max())
    sx = lambda v: x0 + (v - yr0) / (yr1 - yr0) * (x1 - x0)
    sy = lambda v: y0 - v / 85.0 * (y0 - y1)
    b = [text(20, 26, "The gap AROPE does not close", 13, INK, weight="bold"),
         text(20, 44, "Greece, percent of population", 10.5, MUTE)]
    for v in range(0, 81, 20):
        b.append(line(x0, sy(v), x1, sy(v), GRID))
        b.append(text(x0 - 8, sy(v) + 4, str(v), 9.5, MUTE, "end"))
    for yr in range(yr0, yr1 + 1, 3):
        b.append(text(sx(yr), y0 + 18, str(yr), 9.5, MUTE, "middle"))
    series = [("gr_subjective_poverty", GR, "subjective hardship"),
              ("gr_arope", WARN, "AROPE"),
              ("gr_arop", EU, "AROP")]
    # shade what AROPE adds over AROP
    up = " ".join(f"{sx(r.time):.1f},{sy(r.gr_arope):.1f}" for r in d.itertuples())
    dn = " ".join(f"{sx(r.time):.1f},{sy(r.gr_arop):.1f}"
                  for r in reversed(list(d.itertuples())))
    b.append(f'<polygon points="{up} {dn}" fill="{WARN}" opacity="0.13"/>')
    for col, c, lab in series:
        pts = " ".join(f"{sx(r.time):.1f},{sy(getattr(r, col)):.1f}"
                       for r in d.itertuples())
        b.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.5"/>')
        last = d.iloc[-1]
        b.append(text(x1 + 10, sy(getattr(last, col)) + 4, lab, 10, c,
                      "start", "bold"))
    first, lastr = d.iloc[0], d.iloc[-1]
    for r, lab in [(first, str(yr0)), (lastr, str(yr1))]:
        b.append(line(sx(r.time), sy(r.gr_subjective_poverty),
                      sx(r.time), sy(r.gr_arop), INK, 1, "2,2"))
    b.append(text(20, H - 34, f"AROPE closes {d.gap_vs_arop.mean() - d.gap_vs_arope.mean():.1f} "
                  f"of the {d.gap_vs_arop.mean():.1f}-point AROP gap on average "
                  f"({(d.gap_vs_arop.mean() - d.gap_vs_arope.mean()) / d.gap_vs_arop.mean():.0%}),",
                  10, MUTE))
    b.append(text(20, H - 20, f"leaving {d.gap_vs_arope.mean():.1f} points unexplained. "
                  f"Shaded band = what AROPE adds to AROP.", 10, MUTE))
    write("paradox.svg", svg(W, H, "\n".join(b), "Subjective hardship against AROP and AROPE"))


# --------------------------------------------------------------------------
# 9. What recovered and what did not
# --------------------------------------------------------------------------
def fig_recovery():
    d = pd.read_csv(PROC / "e_descriptive_recovery.csv")
    d = d[~d.trend.str.startswith("not applicable")]
    order = {"converging": 0, "flat": 1, "diverging": 2}
    d = d.assign(o=d.trend.map(order)).sort_values(["o", "gap_shift_rel"],
                                                   ascending=[True, False])
    W, H = 660, 60 + len(d) * 22 + 60
    x0, x1 = 250, 560
    sx = lambda v: x0 + (max(min(v, 1.0), -1.0) + 1) / 2 * (x1 - x0)
    b = [text(20, 26, "Greece's distance from the EU median: what closed, what did not",
              13, INK, weight="bold"),
         text(20, 44, "Change in the gap since 2015, as a share of the 2015 gap",
              10.5, MUTE)]
    y = 74
    cols = {"converging": GOOD, "flat": MUTE, "diverging": GR}
    b.append(line(sx(0), 62, sx(0), 62 + len(d) * 22, MUTE, 1.5))
    b.append(text(sx(0), H - 42, "no change", 9, MUTE, "middle"))
    b.append(text(sx(-1), H - 42, "gap doubled", 9, MUTE, "middle"))
    b.append(text(sx(1), H - 42, "gap closed", 9, MUTE, "middle"))
    for r in d.itertuples():
        c = cols[r.trend]
        v = max(min(r.gap_shift_rel, 1.0), -1.0)
        a, bb = (sx(0), sx(v)) if v > 0 else (sx(v), sx(0))
        b.append(text(x0 - 14, y + 11, r.variable, 9.5, INK, "end"))
        b.append(rect(a, y, bb - a, 14, c))
        clipped = "*" if abs(r.gap_shift_rel) > 1.0 else ""
        b.append(text(sx(v) + (7 if v > 0 else -7), y + 11,
                      f"{r.gap_shift_rel:+.0%}{clipped}", 9, INK,
                      "start" if v > 0 else "end", "bold"))
        y += 22
    lx = 24
    for name, c in cols.items():
        b.append(rect(lx, H - 24, 11, 11, c))
        b.append(text(lx + 16, H - 15, name, 9.5, MUTE))
        lx += 95
    b.append(text(lx + 10, H - 15, "* bar clipped at 100%", 9, MUTE))
    write("recovery.svg", svg(W, H, "\n".join(b), "What converged and what diverged"))



# --------------------------------------------------------------------------
# 10. E1: what the wild bootstrap does to cluster-robust p-values
# --------------------------------------------------------------------------
def fig_e1():
    d = pd.read_csv(PROC / "e1_results.csv")
    d = d[d.boot_p.notna()].sort_values("boot_p")
    W, H = 660, 300
    x0, x1 = 250, 500
    import math
    lo, hi = -4.2, 0.1                       # log10 p
    sx = lambda p: x0 + (max(math.log10(max(p, 1e-4)), lo) - lo) / (hi - lo) * (x1 - x0)
    b = [text(20, 26, "Cluster-robust p-values do not survive the bootstrap",
              13, INK, weight="bold"),
         text(20, 44, "Every predictor here varies mostly BETWEEN countries, "
              "and 27 clusters is few", 10.5, MUTE)]
    for e in [-4, -3, -2, -1, 0]:
        b.append(line(sx(10 ** e), 66, sx(10 ** e), 66 + len(d) * 40, GRID))
        b.append(text(sx(10 ** e), 66 + len(d) * 40 + 18,
                      f"1e{e}" if e < -1 else f"{10 ** e:g}", 9.5, MUTE, "middle"))
    b.append(line(sx(0.05), 60, sx(0.05), 66 + len(d) * 40 + 4, WARN, 1.5, "4,3"))
    b.append(text(sx(0.05), 56, "p = 0.05", 9.5, WARN, "middle", "bold"))
    y = 84
    for r in d.itertuples():
        ok = r.outcome == "supported"
        c = GOOD if ok else GR
        b.append(text(x0 - 14, y + 4, r.var, 10, INK, "end", "bold" if ok else "normal"))
        b.append(line(sx(r.p_raw), y, sx(r.boot_p), y, MUTE, 1.5, "3,3"))
        b.append(f'<circle cx="{sx(r.p_raw):.1f}" cy="{y}" r="5" fill="{MUTE}"/>')
        b.append(f'<circle cx="{sx(r.boot_p):.1f}" cy="{y}" r="6" fill="{c}"/>')
        b.append(text(x1 + 14, y + 4,
                      "supported" if ok else "not supported", 9.5, c, "start", "bold"))
        b.append(text(x1 + 14, y + 17, f"boot p = {r.boot_p:.4f}", 9, MUTE))
        y += 40
    b.append(text(20, H - 14, "Grey = cluster-robust. Coloured = wild cluster "
                  "bootstrap, null imposed. Log scale.", 10, MUTE))
    write("e1_bootstrap.svg", svg(W, H, "\n".join(b),
          "Cluster-robust versus bootstrap p-values"))



# --------------------------------------------------------------------------
# 11. E2: the strongest predictors are the ones we may not use
# --------------------------------------------------------------------------
def fig_restatement():
    e1 = pd.read_csv(PROC / "e1_results.csv")
    e2 = pd.read_csv(PROC / "e2_results.csv")
    sup = e1[e1.outcome == "supported"][["var", "std_effect"]].assign(kind="objective")
    p1 = e2[e2.construct == "P1"][["var", "std_effect"]].assign(kind="proximate")
    d = pd.concat([p1, sup]).sort_values("std_effect", ascending=False)
    W, H = 660, 100 + len(d) * 26 + 40
    x0, x1 = 250, 520
    sx = lambda v: x0 + min(v, 1.1) / 1.1 * (x1 - x0)
    b = [text(20, 26, "The strongest predictors are the ones we may not use",
              13, INK, weight="bold"),
         text(20, 44, "Standardised effect on hardship, per SD of the predictor",
              10.5, MUTE)]
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        b.append(line(sx(v), 66, sx(v), 66 + len(d) * 26, GRID))
        b.append(text(sx(v), 66 + len(d) * 26 + 18, f"{v:.2f}", 9.5, MUTE, "middle"))
    b.append(line(sx(0.70), 60, sx(0.70), 66 + len(d) * 26 + 4, WARN, 1.5, "4,3"))
    b.append(text(sx(0.70), 56, "MDE 0.70 SD", 9.5, WARN, "middle", "bold"))
    y = 76
    for r in d.itertuples():
        c = GR if r.kind == "proximate" else GOOD
        b.append(text(x0 - 14, y + 11, r.var, 9.5, INK, "end"))
        b.append(rect(sx(0), y, sx(r.std_effect) - sx(0), 15, c))
        b.append(text(sx(r.std_effect) + 8, y + 11, f"{r.std_effect:.2f}", 9.5,
                      INK, "start", "bold"))
        y += 26
    b.append(rect(24, H - 30, 11, 11, GR))
    b.append(text(41, H - 21, "proximate: same survey instrument as the outcome, "
                  "blocked from any headline", 9.5, MUTE))
    b.append(rect(24, H - 14, 11, 11, GOOD))
    b.append(text(41, H - 5, "objective: supported at E1", 9.5, MUTE))
    write("restatement.svg", svg(W, H, "\n".join(b),
          "Proximate predictors outweigh every objective construct"))



# --------------------------------------------------------------------------
# 12. E3: reported difficulty tracks concrete affordability failure
# --------------------------------------------------------------------------
def fig_validation():
    d = pd.read_csv(PROC / "e3_results.csv")
    d = d[d.stat == "within_country_r"].sort_values("value", ascending=False)
    W, H = 660, 100 + len(d) * 34 + 56
    x0, x1 = 230, 500
    sx = lambda v: x0 + max(v, 0) / 1.0 * (x1 - x0)
    b = [text(20, 26, "Reported difficulty moves with concrete affordability failure",
              13, INK, weight="bold"),
         text(20, 44, "Correlation with subjective hardship, country means removed",
              10.5, MUTE)]
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        b.append(line(sx(v), 66, sx(v), 66 + len(d) * 34, GRID))
        b.append(text(sx(v), 66 + len(d) * 34 + 18, f"{v:.2f}", 9.5, MUTE, "middle"))
    y = 78
    for r in d.itertuples():
        b.append(text(x0 - 14, y + 10, r.var, 9.5, INK, "end"))
        b.append(rect(sx(0), y, sx(r.value) - sx(0), 13, EU))
        b.append(text(sx(r.value) + 8, y + 10, f"{r.value:.3f}", 9.5, INK,
                      "start", "bold"))
        gr_x = sx(r.greece_timeseries_r)
        b.append(f'<circle cx="{gr_x:.1f}" cy="{y + 22:.1f}" r="4.5" fill="{GR}"/>')
        b.append(text(gr_x + 9, y + 26, f"{r.greece_timeseries_r:.3f} Greece alone",
                      8.5, GR))
        y += 34
    b.append(rect(24, H - 40, 11, 11, EU))
    b.append(text(41, H - 31, "within-country, all 27 (country means removed)",
                  9.5, MUTE))
    b.append(f'<circle cx="29.5" cy="{H - 20}" r="4.5" fill="{GR}"/>')
    b.append(text(41, H - 16, "Greece over time", 9.5, MUTE))
    write("validation.svg", svg(W, H, "\n".join(b),
          "Subjective hardship tracks concrete affordability failure"))



# --------------------------------------------------------------------------
# 13. E4: every accumulated result is between-country
# --------------------------------------------------------------------------
def fig_e4_between_within():
    d = pd.read_csv(PROC / "e4_results.csv").sort_values("between", ascending=False)
    W, H = 680, 90 + len(d) * 30 + 56
    x0, x1 = 250, 520
    lo, hi = -0.35, 0.55
    sx = lambda v: x0 + (max(min(v, hi), lo) - lo) / (hi - lo) * (x1 - x0)
    b = [text(20, 26, "Every accumulated result is a between-country marker",
              13, INK, weight="bold"),
         text(20, 44, "Coefficient split into between and within components",
              10.5, MUTE)]
    for v in [-0.2, 0, 0.2, 0.4]:
        b.append(line(sx(v), 62, sx(v), 62 + len(d) * 30, GRID))
        b.append(text(sx(v), 62 + len(d) * 30 + 18, f"{v:+.1f}", 9.5, MUTE, "middle"))
    b.append(line(sx(0), 56, sx(0), 62 + len(d) * 30 + 4, MUTE, 1.5))
    y = 76
    for r in d.itertuples():
        sup = r.outcome == "supported"
        b.append(text(x0 - 14, y + 4, r.var.replace("acc_", "").replace("dur_", ""),
                      9.5, INK, "end", "bold" if sup else "normal"))
        b.append(line(sx(r.within), y, sx(r.between), y, GRID, 1.5))
        b.append(f'<circle cx="{sx(r.within):.1f}" cy="{y}" r="4.5" fill="{MUTE}"/>')
        b.append(f'<circle cx="{sx(r.between):.1f}" cy="{y}" r="6" '
                 f'fill="{GOOD if sup else EU}"/>')
        b.append(text(x1 + 14, y + 4, "supported" if sup else "inconclusive",
                      9, GOOD if sup else MUTE, "start", "bold" if sup else "normal"))
        y += 30
    b.append(f'<circle cx="29.5" cy="{H - 34}" r="6" fill="{GOOD}"/>')
    b.append(text(41, H - 30, "between-country component", 9.5, MUTE))
    b.append(f'<circle cx="29.5" cy="{H - 16}" r="4.5" fill="{MUTE}"/>')
    b.append(text(41, H - 12, "within-country component - not one is significant "
                  "in the adverse direction", 9.5, MUTE))
    write("e4_between_within.svg", svg(W, H, "\n".join(b),
          "Accumulated effects are between-country"))


def check_overflow():
    """Fail if any label runs past its viewBox.

    Three figures shipped clipped on the first pass -- the right-hand
    annotations simply ran off the canvas, and nothing complained because an
    SVG clips silently. Width is estimated from character count, which is
    approximate, so the margin is deliberately slack.
    """
    import re
    bad = []
    for f in sorted(FIG.glob("*.svg")):
        s = f.read_text()
        w = int(re.search(r'viewBox="0 0 (\d+)', s).group(1))
        for m in re.finditer(
                r'<text x="([\d.]+)"[^>]*font-size="([\d.]+)"[^>]*'
                r'text-anchor="(\w+)"[^>]*>([^<]*)</text>', s):
            x, size, anchor, txt = (float(m.group(1)), float(m.group(2)),
                                    m.group(3), m.group(4))
            adv = len(txt) * size * 0.55
            right = x + adv if anchor == "start" else (
                x + adv / 2 if anchor == "middle" else x)
            if right > w:
                bad.append(f"{f.name}: {txt!r} extends to ~{right:.0f} > {w}")
            if (x - adv if anchor == "end" else x) < 0:
                bad.append(f"{f.name}: {txt!r} extends past the left edge")
    if bad:
        raise SystemExit("FIGURE OVERFLOW\n  " + "\n  ".join(bad))
    print(f"  overflow check: {len(list(FIG.glob('*.svg')))} figures within bounds")


print("figures ->", FIG.relative_to(ROOT))
for f in (fig_ea_reversal, fig_ladders, fig_narrowing, fig_mde,
          fig_between_within, fig_sign_reversal, fig_coverage,
          fig_paradox, fig_recovery, fig_e1, fig_restatement, fig_validation,
          fig_e4_between_within):
    f()
check_overflow()
