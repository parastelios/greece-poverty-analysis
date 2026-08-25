"""Health extension: does health status or health-care access inform hardship?

EXPLORATORY, POST-FREEZE. This cannot create a headline claim and does not
reopen the model search. It exists to answer one feasibility question and to
make its own answer checkable.

WHY THIS SCRIPT EXISTS. The analysis was first written up in
docs/health_preliminary_analysis.md with no code behind it. About half its
numbers -- the conditional tests, the VIFs, the first-difference stage, the
leave-one-out claim, the companion checks -- had no artifact at all, and the
results table reported UNSIGNED standardised effects while the figure beside it
plotted signed ones. Three of the four health measures are negative: worse
health associated with LESS reported hardship. Read from the table alone they
looked like near-misses in the expected direction.

So every number the document cites is produced here, and the pre-registered
decision rule in e_rule.py is applied rather than described -- its `direction`
gate is exactly the one those three measures fail, and it labels them
`contradicts_direction` rather than filing them as quiet nulls.

Offline by default: reads data/raw/health_panel.csv. Pass --fetch to
re-acquire that panel from Eurostat, which moves the data vintage.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_rule import benjamini_hochberg, decide  # noqa: E402
from eu_membership import eu_members  # noqa: E402
from outcome import official_hardship  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PANEL = RAW / "health_panel.csv"
SEED = 20260825
REPS = 999
Y = "hardship"

# The four measures, with the direction each must point to count as evidence.
# All are "more of this is worse", so a positive coefficient is the only sign
# that can support the hypothesis. Stating this here is what makes a negative
# result a contradiction rather than a null.
MEASURES = [
    ("unmet_care", "Unmet medical care", "higher_is_worse"),
    ("not_good_health", "Not good or very good health", "higher_is_worse"),
    ("chronic_illness", "Long-standing illness", "higher_is_worse"),
    ("activity_limitation", "Activity limitation", "higher_is_worse"),
]
# Health status begins in 2016; unmet care begins in 2008. The common sample is
# the intersection, so every stage compares like with like.
FIRST, LAST = 2016, 2024
BASE = f"{Y} ~ arop + C(time)"
# The report's proximity-clean working model: P3 with the same-instrument
# deprivation measure removed. Health is tested against this too, because
# adding to a two-term baseline is a much easier bar than adding to the model
# the report actually uses.
COMPANION = ["housing_cost_overburden", "ltu_rate", "aic_pps_pc_k",
             "wage_years_below_2008", "cum_excess_unemployment"]


# --------------------------------------------------------------- fetch ------
def fetch_panel():
    """Re-acquire the four indicators from Eurostat and rebuild the panel."""
    from eurostat import fetch

    members = sorted(eu_members(2025))
    yrs = list(range(2008, 2026))

    def tidy(df, name):
        d = df.rename(columns={"value": name})[["geo", "time", name]]
        d["time"] = d.time.astype(int)
        return d[d.geo.isin(members)]

    # sdg_03_60 is published as the unmet-need share directly.
    unmet = tidy(fetch("sdg_03_60", geo=members, time=yrs,
                       unit="PC", sex="T", age="Y_GE16", reason="TOTAL"),
                 "unmet_care")
    # hlth_silc_01 reports the GOOD-health share; the adverse direction is its
    # complement, so it is inverted here rather than in the model.
    good = tidy(fetch("hlth_silc_01", geo=members, time=yrs,
                      unit="PC", sex="T", age="Y_GE16", levels="VGOOD_GOOD",
                      isced11="TOTAL"), "good_health")
    good["not_good_health"] = 100.0 - good.good_health
    good = good[["geo", "time", "not_good_health"]]
    chron = tidy(fetch("hlth_silc_04", geo=members, time=yrs,
                       unit="PC", sex="T", age="Y_GE16", isced11="TOTAL"),
                 "chronic_illness")
    limit = tidy(fetch("hlth_silc_06", geo=members, time=yrs,
                       unit="PC", sex="T", age="Y_GE16", isced11="TOTAL",
                       lev_limit="SM_SEV"), "activity_limitation")

    p = unmet
    for d in (good, chron, limit):
        p = p.merge(d, on=["geo", "time"], how="outer")
    return add_accumulations(p.sort_values(["geo", "time"]))


def add_accumulations(p):
    """Running total of adverse percentage points above the same-year EU median.

    Accumulation is defined on the EXCESS over the contemporaneous median, not
    on the level, so a country that is merely high in a year when everyone is high
    accumulates nothing. Negative excess is not netted off: this is a stock of
    adverse exposure, and letting good years erase bad ones would measure
    something else.
    """
    for k, _, _ in MEASURES:
        if k not in p:
            continue
        med = p.groupby("time")[k].transform("median")
        p[f"{k}_excess_eu"] = (p[k] - med).clip(lower=0)
        p[f"acc_{k}"] = (p.sort_values("time")
                          .groupby("geo")[f"{k}_excess_eu"]
                          .cumsum())
    return p


# ---------------------------------------------------------------- fit -------
def fit(formula, d):
    return smf.ols(formula, data=d).fit(cov_type="cluster",
                                        cov_kwds={"groups": d.geo})


def greece_residual(formula, d):
    """Greece's residual from a fit that never saw Greece -- out of sample.

    An in-sample residual is partly the model accommodating Greece, which is
    the thing being measured.
    """
    tr, te = d[d.geo != "EL"], d[d.geo == "EL"]
    if te.empty or tr.empty:
        return np.nan
    m = smf.ols(formula, data=tr).fit()
    return float((te[Y] - m.predict(te)).mean())


def wild_bootstrap(formula, d, var, seed, reps=REPS):
    """Restricted (null-imposed) wild cluster bootstrap, Rademacher weights."""
    rng = np.random.default_rng(seed)
    t_obs = (lambda m: m.params[var] / m.bse[var])(fit(formula, d))
    m_r = smf.ols(BASE, data=d).fit()
    fitted, resid = m_r.predict(d), d[Y] - m_r.predict(d)
    geos = d.geo.unique()
    ts = []
    for _ in range(reps):
        w = pd.Series(rng.choice([-1.0, 1.0], size=len(geos)), index=geos)
        db = d.copy()
        db[Y] = fitted + resid.values * d.geo.map(w).values
        mb = fit(formula, db)
        ts.append(abs(mb.params[var] / mb.bse[var]))
    return float(t_obs), float((np.sum(np.array(ts) >= abs(t_obs)) + 1) / (reps + 1))


def loo(formula, d, var):
    """Refit dropping each country in turn; report the sign-stability."""
    cs = []
    for g in sorted(d.geo.unique()):
        sub = d[d.geo != g]
        if sub.geo.nunique() < 10:
            continue
        cs.append(float(smf.ols(formula, data=sub).fit().params[var]))
    return (min(cs), max(cs), bool(min(cs) > 0 or max(cs) < 0))


def stage(d, tests, label, seed0):
    """One family: fit, FDR within the family, bootstrap, LOO, then decide."""
    rows = []
    for i, (var, formula, name, adverse, extra) in enumerate(tests):
        sub = d.dropna(subset=[var, Y, "arop"]).copy()
        m, m0 = fit(formula, sub), fit(BASE, sub)
        coef, se, p = m.params[var], m.bse[var], m.pvalues[var]
        ci = m.conf_int().loc[var]
        sd_x = sub[var].std()
        resid_sd = float(np.std(m0.resid, ddof=1))
        # SIGNED. The earlier write-up reported abs() here, which is what let
        # three negative coefficients read as near-misses in the right
        # direction. The magnitude is recoverable; the sign is not.
        std_effect = coef * sd_x / resid_sd
        lo, hi, stable = loo(formula, sub, var)
        _, bp = wild_bootstrap(formula, sub, var, seed0 + i)
        rb = greece_residual(BASE, sub)
        rf = greece_residual(formula, sub)
        rows.append(dict(stage=label, var=var, name=name, adverse=adverse,
                         n=len(sub), countries=sub.geo.nunique(),
                         coef=coef, se=se, ci_lo=ci[0], ci_hi=ci[1], p_raw=p,
                         std_effect=std_effect,
                         ci_abs_std_upper=max(abs(ci[0]), abs(ci[1])) * sd_x / resid_sd,
                         boot_p=bp, loo_min=lo, loo_max=hi, loo_sign_stable=stable,
                         greece_resid_base=rb, greece_resid_full=rf,
                         greece_improves=abs(rf) < abs(rb), **extra))
    out = pd.DataFrame(rows)
    adj, rej = benjamini_hochberg(list(out.p_raw))
    out["p_fdr"], out["fdr_rejected"] = adj, rej
    verdicts = [decide(r.coef, r.adverse, r.fdr_rejected, r.boot_p,
                       r.loo_sign_stable, r.greece_improves, False,
                       r.ci_abs_std_upper) for r in out.itertuples()]
    out["outcome"] = [v[0] for v in verdicts]
    out["failed_gate"] = [v[2] for v in verdicts]
    out["notes"] = ["; ".join(v[1]) for v in verdicts]
    return out


def vif_max(d, cols):
    x = d[cols].dropna().assign(_const=1.0)
    vals = [variance_inflation_factor(x.values, i) for i in range(len(cols))]
    return float(max(vals)), dict(zip(cols, [float(v) for v in vals]))


# --------------------------------------------------------------- figures ----
# Hand-written SVG, matching 65_record_figures.py. The two figures this
# document carried were matplotlib PNGs produced by no script in the repo,
# which is both off the project's house rule ("a reproducible-build project
# should not acquire matplotlib just to draw seven pictures") and the reason
# they could drift from the numbers beside them. These are generated from the
# artifacts above, so they cannot.
FIGDIR = ROOT / "docs" / "health_figures"
INK, MUTE, GRID, BG = "#1f2933", "#6b7280", "#e5e7eb", "#ffffff"
GR, EU, WARN = "#3d6fb4", "#b7791f", "#c0392b"


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _txt(x, y, s, size=11, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>')


def _ln(x1, y1, x2, y2, stroke=GRID, w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>')


def _svg(w, h, body, title, path):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
         f'width="{w}" height="{h}" role="img" aria-label="{_esc(title)}" '
         f'font-family="Helvetica,Arial,sans-serif">\n'
         f'<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n')
    path.write_text(s)
    return path


def figure_unmet(panel, members):
    W, H, L, R, T, B = 900, 460, 62, 150, 56, 46
    # Capped at LAST so the figure's endpoint is the same year the tables and
    # the prose describe. The panel runs a year further; letting the chart end
    # there put "11.5%" on the picture beside "12.1%" in the text.
    d = panel[panel.geo.isin(members) & (panel.time <= LAST)]
    yrs = sorted(int(y) for y in d.time.unique()
                 if d[d.time == y].unmet_care.notna().sum() >= 20)
    piv = d[d.time.isin(yrs)].pivot_table(index="time", columns="geo",
                                          values="unmet_care")
    hi = float(np.nanmax(piv.values)) * 1.05
    xs = lambda v: L + (v - yrs[0]) / (yrs[-1] - yrs[0]) * (W - L - R)
    ys = lambda v: H - B - v / hi * (H - B - T)
    b = [_txt(L, 26, "Unmet medical care remains exceptionally high in Greece",
              16, INK, weight="bold"),
         _txt(L, 44, "Share reporting unmet need because of cost, waiting "
                     "lists or distance", 12, MUTE)]
    for g in range(0, int(hi) + 1, 4):
        b.append(_ln(L, ys(g), W - R, ys(g)))
        b.append(_txt(L - 8, ys(g) + 4, str(g), 10, MUTE, "end"))
    for y in yrs[::2]:
        b.append(_txt(xs(y), H - B + 18, str(y), 10, MUTE, "middle"))

    def path(vals, col, wid, dash=None):
        pts = [(xs(y), ys(v)) for y, v in zip(yrs, vals) if v == v]
        if len(pts) < 2:
            return ""
        dd = " ".join(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}"
                      for i, (x, y) in enumerate(pts))
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<path d="{dd}" fill="none" stroke="{col}" '
                f'stroke-width="{wid}" stroke-linejoin="round"{ds}/>')

    for c in piv.columns:
        if c != "EL":
            b.append(path(list(piv[c]), "#c9ced6", 1))
    med = list(piv.median(axis=1))
    b.append(path(med, EU, 2.4))
    gr = list(piv["EL"])
    b.append(path(gr, GR, 3.2))
    last_gr = [v for v in gr if v == v][-1]
    last_med = [v for v in med if v == v][-1]
    b.append(_txt(W - R + 8, ys(last_gr) - 4, f"Greece {last_gr:.1f}%",
                  12, GR, weight="bold"))
    # Derived, not asserted: the rank claim on the picture has to come from
    # the same column the picture is drawn from.
    _fin = piv.loc[yrs[-1]].dropna().sort_values(ascending=False)
    _rk = list(_fin.index).index("EL") + 1
    b.append(_txt(W - R + 8, ys(last_gr) + 12,
                  f"{'worst' if _rk == 1 else f'{_rk}nd worst'} of {len(_fin)}",
                  12, GR, weight="bold"))
    b.append(_txt(W - R + 8, ys(last_med) + 4, f"EU median {last_med:.1f}%",
                  12, EU, weight="bold"))
    b.append(_txt(14, T + (H - B - T) / 2, "Percent of people aged 16+", 11,
                  MUTE, "middle") .replace("<text ",
                  f'<text transform="rotate(-90 14 {T + (H - B - T) / 2:.1f})" '))
    b.append(_txt(L, H - 10, "Other EU countries in grey. Descriptive context, "
                             "not a model result. Source: Eurostat sdg_03_60.",
                  10, MUTE))
    return _svg(W, H, "\n".join(b), "Unmet medical care in Greece and the EU",
                FIGDIR / "health_01_unmet_care_eu.svg")


def figure_estimates(cur, acc):
    rows = []
    for src, role in ((cur, "current level"), (acc, "accumulated")):
        for r in src.itertuples():
            sd = r.std_effect / r.coef if r.coef else 0.0
            lo, hi = sorted([r.ci_lo * sd, r.ci_hi * sd])
            rows.append((f"{r.name} ({role})", r.std_effect, lo, hi,
                         r.boot_p, r.std_effect < 0))
    W, L, R, T, B, RH = 940, 250, 200, 62, 62, 30
    H = T + len(rows) * RH + B
    lo_ = min(r[2] for r in rows); hi_ = max(r[3] for r in rows)
    sp = (hi_ - lo_) * .08; lo_ -= sp; hi_ += sp
    xs = lambda v: L + (v - lo_) / (hi_ - lo_) * (W - L - R)
    b = [_txt(24, 26, "No health measure supports the hypothesis, and most "
                      "point against it", 16, INK, weight="bold"),
         _txt(24, 44, "Positive means worse health goes with MORE hardship, "
                      "the only sign that can support it", 12, MUTE)]
    b.append(_ln(xs(0), T - 8, xs(0), T + len(rows) * RH, MUTE, 1.5))
    for v in (lo_, 0, hi_):
        b.append(_txt(xs(v), H - B + 18, f"{v:+.2f}", 10, MUTE, "middle"))
    for i, (lab, est, lo, hi, bp, wrong) in enumerate(rows):
        y = T + i * RH + RH / 2
        col = WARN if wrong else GR
        b.append(_ln(xs(lo), y, xs(hi), y, col, 2.2))
        b.append(f'<circle cx="{xs(est):.1f}" cy="{y:.1f}" r="5" fill="{col}"/>')
        b.append(_txt(L - 12, y + 4, lab, 11, INK, "end"))
        b.append(_txt(W - R + 10, y + 4,
                      f"boot p={bp:.3f}" + ("   wrong sign" if wrong else ""),
                      10, col if wrong else MUTE))
    b.append(_txt((L + W - R) / 2, H - B + 34,
                  "standardised association with reported hardship, residual SD",
                  11, MUTE, "middle"))
    b.append(_txt(24, H - 10, "Exploratory. Controls for AROP and year effects; "
                              "intervals country-clustered; the wild-cluster "
                              "bootstrap decides support. None clears it.",
                  10, MUTE))
    return _svg(W, H, "\n".join(b), "Health model estimates",
                FIGDIR / "health_02_model_results.svg")


# --------------------------------------------------------------- build ------
if __name__ == "__main__":
    if "--fetch" in sys.argv:
        print("fetching the health panel from Eurostat (moves the vintage)")
        fetch_panel().to_csv(PANEL, index=False)

    panel = pd.read_csv(PANEL)
    out = official_hardship().rename(columns={"value": Y})[["geo", "time", Y]]
    arop = pd.read_csv(RAW / "arop_all_countries.csv")
    arop = (arop.rename(columns={"value": "arop"})[["geo", "time", "arop"]]
                .assign(time=lambda x: x.time.astype(int)))
    d = (panel.merge(out, on=["geo", "time"])
              .merge(arop, on=["geo", "time"])
              .query(f"{FIRST} <= time <= {LAST}")
              .copy())
    members = set(eu_members(2025))
    d = d[d.geo.isin(members)]

    bar = "=" * 78
    print(bar); print("HEALTH EXTENSION (exploratory, post-freeze)"); print(bar)
    print(f"  sample {d.time.min()}-{d.time.max()}, {d.geo.nunique()} countries, "
          f"{len(d)} rows\n  baseline: {BASE}\n")

    # ---- descriptive ----
    desc = []
    for k, name, _ in MEASURES:
        for y in (FIRST, 2019, 2022, LAST):
            s = panel[(panel.time == y) & panel.geo.isin(members)][["geo", k]].dropna()
            if s.empty or "EL" not in set(s.geo):
                continue
            s = s.sort_values(k, ascending=False).reset_index(drop=True)
            desc.append(dict(var=k, name=name, time=y,
                             greece=float(s.loc[s.geo == "EL", k].iloc[0]),
                             eu_median=float(s[k].median()),
                             rank_worst_first=int(s.index[s.geo == "EL"][0]) + 1,
                             n_countries=len(s)))
    desc = pd.DataFrame(desc)
    desc.to_csv(PROC / "health_descriptive.csv", index=False)
    print("  descriptive:")
    for r in desc[desc.time == LAST].itertuples():
        print(f"    {r.name[:30]:32s} EL {r.greece:5.1f}  median {r.eu_median:5.1f}"
              f"  rank {r.rank_worst_first}/{r.n_countries}")

    # ---- stage 1: current levels ----
    cur = stage(d, [(k, f"{BASE} + {k}", n, a, {}) for k, n, a in MEASURES],
                "current", SEED)
    cur.to_csv(PROC / "health_current.csv", index=False)

    # ---- stage 2: accumulated, alone ----
    acc = stage(d, [(f"acc_{k}", f"{BASE} + acc_{k}", n, a, {})
                    for k, n, a in MEASURES], "accumulated", SEED + 100)
    acc.to_csv(PROC / "health_accumulated.csv", index=False)

    # ---- stage 3: accumulated, controlling for its current counterpart ----
    cond = stage(d, [(f"acc_{k}", f"{BASE} + {k} + acc_{k}", n, a,
                      {"controls_for": k}) for k, n, a in MEASURES],
                 "accumulated_given_current", SEED + 200)
    cond.to_csv(PROC / "health_conditional.csv", index=False)

    for nm, t in (("current", cur), ("accumulated", acc),
                  ("accumulated | current", cond)):
        print(f"\n  {nm}:")
        for r in t.itertuples():
            print(f"    {r.name[:30]:32s} {r.std_effect:+6.2f}  FDR {r.p_fdr:.3f}"
                  f"  boot {r.boot_p:.3f}  {r.outcome}")

    # ---- between vs within ----
    #
    # The write-up reported pooled estimates in one section and within-country
    # estimates in another and connected neither. Three of the four reverse
    # sign between the two, which is this project's signature limitation
    # (see the Mundlak treatment in the main report). Reporting the halves
    # separately without naming the reversal is what made the pooled negatives
    # look like noise rather than composition.
    bw = []
    for k, name, _ in MEASURES:
        s = d.dropna(subset=[k, Y, "arop"]).copy()
        s["mn"] = s.groupby("geo")[k].transform("mean")
        s["dv"] = s[k] - s["mn"]
        m = fit(f"{BASE} + mn + dv", s)
        _, bpw = wild_bootstrap(f"{BASE} + mn + dv", s, "dv", SEED + 300)
        _, _, stable = loo(f"{BASE} + mn + dv", s, "dv")
        gr = s[s.geo == "EL"][[Y, k]].dropna()
        bw.append(dict(var=k, name=name, n=len(s), countries=s.geo.nunique(),
                       between=float(m.params["mn"]), between_p=float(m.pvalues["mn"]),
                       within=float(m.params["dv"]), within_p=float(m.pvalues["dv"]),
                       within_boot_p=bpw, within_loo_sign_stable=stable,
                       sign_reversal=bool(m.params["mn"] * m.params["dv"] < 0),
                       greece_within_r=float(gr[Y].corr(gr[k])), greece_n=len(gr)))
    bw = pd.DataFrame(bw)
    bw.to_csv(PROC / "health_between_within.csv", index=False)
    print("\n  between vs within:")
    for r in bw.itertuples():
        print(f"    {r.name[:30]:32s} between {r.between:+.3f} (p={r.between_p:.3f})"
              f"  within {r.within:+.3f} (p={r.within_p:.3f})"
              f"{'  SIGN REVERSAL' if r.sign_reversal else ''}"
              f"   Greece r={r.greece_within_r:+.2f}")

    # ---- first differences ----
    fd_rows = []
    for i, (k, name, adverse) in enumerate(MEASURES):
        s = d.dropna(subset=[k, Y, "arop"]).sort_values(["geo", "time"]).copy()
        for c in (Y, "arop", k):
            s[f"d_{c}"] = s.groupby("geo")[c].diff()
        s = s.dropna(subset=[f"d_{Y}", "d_arop", f"d_{k}"])
        m = fit(f"d_{Y} ~ d_arop + C(time) + d_{k}", s)
        fd_rows.append(dict(var=k, name=name, n=len(s), countries=s.geo.nunique(),
                            coef=float(m.params[f"d_{k}"]),
                            se=float(m.bse[f"d_{k}"]),
                            p_raw=float(m.pvalues[f"d_{k}"])))
    fd = pd.DataFrame(fd_rows)
    fd["p_fdr"], fd["fdr_rejected"] = benjamini_hochberg(list(fd.p_raw))
    fd.to_csv(PROC / "health_first_differences.csv", index=False)
    print("\n  first differences:")
    for r in fd.itertuples():
        print(f"    {r.name[:30]:32s} {r.coef:+.3f}  FDR {r.p_fdr:.3f}")

    # ---- collinearity of the blocks ----
    blocks = {
        "current_health_block": [k for k, _, _ in MEASURES],
        "accumulated_health_block": [f"acc_{k}" for k, _, _ in MEASURES],
        "current_plus_accumulated": ([k for k, _, _ in MEASURES]
                                     + [f"acc_{k}" for k, _, _ in MEASURES]),
    }
    vrows = []
    for name, cols in blocks.items():
        mx, each = vif_max(d, cols)
        # Greece's residual under the whole block, out of sample.
        sub = d.dropna(subset=cols + [Y, "arop"])
        f = BASE + " + " + " + ".join(cols)
        vrows.append(dict(block=name, n_vars=len(cols), max_vif=mx,
                          interpretable=bool(mx < 10),
                          greece_resid_base=greece_residual(BASE, sub),
                          greece_resid_block=greece_residual(f, sub),
                          worst_var=max(each, key=each.get)))
    vif = pd.DataFrame(vrows)
    vif.to_csv(PROC / "health_blocks.csv", index=False)
    print("\n  blocks:")
    for r in vif.itertuples():
        print(f"    {r.block:28s} max VIF {r.max_vif:6.1f}"
              f"  {'interpretable' if r.interpretable else 'NOT interpretable'}"
              f"  Greece {r.greece_resid_base:+.2f} -> {r.greece_resid_block:+.2f}")

    # ---- incremental against the proximity-clean companion ----
    #
    # The companion is the five-predictor model with the same-instrument
    # deprivation measure removed. If health adds anything to the report's
    # actual working model rather than to a two-term baseline, it shows here.
    comp_p = pd.read_csv(PROC / "persistence_share_panel.csv")
    comp_p = comp_p.merge(out, on=["geo", "time"], how="left")
    comp = (comp_p[comp_p.time.isin(range(2015, 2025))]
            .dropna(subset=COMPANION + [Y])
            .merge(panel, on=["geo", "time"], how="left"))
    crows = []
    for i, (k, name, adverse) in enumerate(MEASURES):
        for role, v in (("current", k), ("accumulated", f"acc_{k}")):
            sub = comp.dropna(subset=[v] + COMPANION + [Y]).copy()
            base_f = f"{Y} ~ " + " + ".join(COMPANION) + " + C(time)"
            f = base_f + f" + {v}"
            m = smf.ols(f, data=sub).fit(cov_type="cluster",
                                         cov_kwds={"groups": sub.geo})
            rng = np.random.default_rng(SEED + 400 + i)
            m_r = smf.ols(base_f, data=sub).fit()
            fitted, resid = m_r.predict(sub), sub[Y] - m_r.predict(sub)
            t_obs = m.params[v] / m.bse[v]
            geos, ts = sub.geo.unique(), []
            for _ in range(REPS):
                w = pd.Series(rng.choice([-1.0, 1.0], size=len(geos)), index=geos)
                db = sub.copy()
                db[Y] = fitted + resid.values * sub.geo.map(w).values
                mb = smf.ols(f, data=db).fit()
                ts.append(abs(mb.params[v] / mb.bse[v]))
            bp = float((np.sum(np.array(ts) >= abs(t_obs)) + 1) / (REPS + 1))
            crows.append(dict(var=v, name=name, role=role, n=len(sub),
                              countries=sub.geo.nunique(),
                              coef=float(m.params[v]), se=float(m.bse[v]),
                              p_raw=float(m.pvalues[v]), boot_p=bp,
                              adverse=adverse,
                              direction_ok=bool(m.params[v] > 0)))
    cmp_ = pd.DataFrame(crows)
    cmp_["p_fdr"], cmp_["fdr_rejected"] = benjamini_hochberg(list(cmp_.p_raw))
    cmp_.to_csv(PROC / "health_companion_incremental.csv", index=False)
    print("\n  incremental against the five-predictor companion:")
    for r in cmp_.itertuples():
        print(f"    {r.name[:26]:28s} {r.role:12s} {r.coef:+.3f}"
              f"  FDR {r.p_fdr:.3f}  boot {r.boot_p:.3f}"
              f"  {'' if r.direction_ok else 'WRONG SIGN'}")

    f1 = figure_unmet(panel, members)
    f2 = figure_estimates(cur, acc)
    print(f"\n  wrote 8 artifacts to {PROC.relative_to(ROOT)}/health_*.csv")
    print(f"  wrote {f1.name} and {f2.name} to {FIGDIR.relative_to(ROOT)}")
