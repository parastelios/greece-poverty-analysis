"""Detailed figures that belong in the appendix rather than the report.

Three kinds of thing land here. Views the report simplified away, because the
simplification was right for a reader following an argument and wrong for one
checking it: the raw affordability observations behind the binned European
view, and the hardship-against-income-poverty scatter for every year rather
than the latest. And the full correlation matrix, which at 35 variables shows
almost nothing to a reader and is exactly what someone auditing variable
selection wants.

These are built the same way as the report's figures, through the shared
engine, so the appendix can carry them beside the report's own without a second
rendering path.
"""
import json
import re
from pathlib import Path

import pandas as pd

import chart_engine as ce

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
panel = pd.read_csv(PROC / "e0_extended_panel.csv")

NAMES = {"EL": "Greece", "BG": "Bulgaria", "RO": "Romania", "HU": "Hungary",
         "LU": "Luxembourg", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
         "EE": "Estonia", "ES": "Spain", "PT": "Portugal", "IT": "Italy",
         "FR": "France", "DE": "Germany", "NL": "Netherlands", "BE": "Belgium",
         "AT": "Austria", "IE": "Ireland", "FI": "Finland", "SE": "Sweden",
         "DK": "Denmark", "PL": "Poland", "CZ": "Czechia", "SK": "Slovakia",
         "SI": "Slovenia", "HR": "Croatia", "MT": "Malta"}
ITEMS = [("unexpected_expenses", "Cannot meet an unexpected expense"),
         ("severe_mat_soc_deprivation", "Material deprivation"),
         ("arrears", "Arrears on bills"),
         ("warm", "Cannot keep the home warm")]

FIGS = {}

# ---- A1: every observation behind the binned European view ----------------
panels_raw, fA1 = [], ce.Series(["Country-years", "Pooled correlation"], dp=3)
for col, label in ITEMS:
    d = panel.dropna(subset=[col, "subjective_poverty"]).copy()
    for c in [col, "subjective_poverty"]:
        d[c + "_w"] = d[c] - d.groupby("geo")[c].transform("mean")
    r = float(d["subjective_poverty_w"].corr(d[col + "_w"]))
    sx = d[col + "_w"].std()
    sy = d["subjective_poverty_w"].std()
    fA1.add(label, [float(len(d)), r])
    panels_raw.append({
        "label": label, "r": round(r, 3), "xLabel": "",
        "points": [{"x": round(float(a) / sx, 2), "y": round(float(b) / sy, 2),
                    "highlight": g == "EL"}
                   for g, a, b in zip(d.geo, d[col + "_w"],
                                      d["subjective_poverty_w"])]})

FIGS["A1"] = dict(
    caption="Every country-year behind the binned European view",
    kind="multiples",
    payload={"panels": panels_raw,
             "xMin": -4, "xMax": 4, "yMin": -4, "yMax": 4,
             "xTicks": [-2, 0, 2], "yTicks": [-2, 0, 2],
             "yLabel": "Reported hardship, standard deviations from the "
                       "country's own average",
             "alt": "The raw country-year observations the report's binned "
                    "view summarises, with Greek observations marked"},
    series=fA1, first="Measure",
    extra_caveat=(
        "These are the observations the report's second view bins. Both axes "
        "are in standard deviations from each country's own average. Greek "
        "observations are marked. At this density the cloud shows spread "
        "rather than shape, which is why the report bins it."))

# ---- A4: the European relationship, binned --------------------------------
# This was a second view of the report's Figure 7. It needs standard
# deviations, demeaned observations, bins and a pooled correlation explained
# before it can be read, which is appendix work rather than report work.
panels_eu, fA4 = [], ce.Series(["Bins", "Country-years", "Pooled correlation"], dp=3)
for col, label in ITEMS:
    d = panel.dropna(subset=[col, "subjective_poverty"]).copy()
    for c in [col, "subjective_poverty"]:
        d[c + "_w"] = d[c] - d.groupby("geo")[c].transform("mean")
    r = float(d["subjective_poverty_w"].corr(d[col + "_w"]))
    d[col + "_z"] = d[col + "_w"] / d[col + "_w"].std()
    d["hard_z"] = d["subjective_poverty_w"] / d["subjective_poverty_w"].std()
    d["_bin"] = pd.qcut(d[col + "_z"], 9, labels=False, duplicates="drop")
    b = d.groupby("_bin").agg(x=(col + "_z", "mean"),
                              y=("hard_z", "mean")).reset_index()
    sxx = ((b.x - b.x.mean()) ** 2).sum()
    b1 = (((b.x - b.x.mean()) * (b.y - b.y.mean())).sum() / sxx) if sxx else 0.0
    fA4.add(label, [float(len(b)), float(len(d)), r])
    panels_eu.append({
        "label": label, "r": round(r, 3), "xLabel": "",
        "points": [{"x": round(float(x), 2), "y": round(float(y), 2)}
                   for x, y in zip(b.x, b.y)],
        "fit": {"b1": round(b1, 4),
                "b0": round(float(b.y.mean() - b1 * b.x.mean()), 4)}})

FIGS["A4"] = dict(
    caption="The European relationship, as binned country-year averages",
    kind="multiples",
    payload={"panels": panels_eu,
             "xMin": -2.2, "xMax": 2.2, "yMin": -2.2, "yMax": 2.2,
             "xTicks": [-1, 0, 1], "yTicks": [-1, 0, 1],
             "yLabel": "Reported hardship, standard deviations from the "
                       "country's own average",
             "alt": "Nine binned averages per measure, each grouping "
                    "country-years where the measure sat similarly above or "
                    "below that country's normal level"},
    series=fA4, first="Measure",
    extra_caveat=(
        "Both axes are in standard deviations from each country's own average, "
        "so one step means the same thing in all four panels. The line is "
        "fitted through the nine plotted bins while the correlation in each "
        "title is computed from all country-years: they are not the same "
        "calculation."))

# ---- A2: the cross-section, every year ------------------------------------
both = panel.dropna(subset=["subjective_poverty", "arop"])
years = [int(y) for y in sorted(both.time.unique())
         if both[both.time == y].geo.nunique() >= 25]
frames = []
for y in years:
    s = both[both.time == y]
    frames.append({"label": str(y), "points": [
        {"x": round(float(r.arop), 1), "y": round(float(r.subjective_poverty), 1),
         "label": NAMES.get(r.geo, r.geo), "highlight": r.geo == "EL"}
        for r in s.itertuples()]})

fA2 = ce.Series(["Greece: income poverty", "Greece: reported hardship",
                 "Median country: income poverty",
                 "Median country: reported hardship"], dp=1)
for y in years:
    s = both[both.time == y]
    g = s[s.geo == "EL"].iloc[0]
    fA2.add(str(y), [float(g.arop), float(g.subjective_poverty),
                     float(s.arop.median()), float(s.subjective_poverty.median())])

FIGS["A2"] = dict(
    caption="Where every country stood, year by year",
    kind="scatter",
    payload={"frames": frames, "dp": 1, "aspect": 0.52,
             "xLabel": "Income poverty, percent of people",
             "yLabel": "Reported hardship, percent of households",
             "fitExcludesHighlight": True,
             "fitLabel": "Peer relationship, Greece excluded",
             "points": frames[-1]["points"],
             "alt": "Every EU country placed by income poverty and reported "
                    "hardship, with a selector for each year from "
                    f"{years[0]} to {years[-1]}"},
    series=fA2, first="Year",
    extra_caveat=(
        "The report carries the latest year only. The axes here are fixed "
        "across every year, so switching year moves the countries and not the "
        "scale. The fitted line excludes Greece in each year."))

# ---- A3: the full correlation matrix --------------------------------------
for label, fname in [("Within countries", "e0_corr_within.csv"),
                     ("Between countries", "e0_corr_between.csv"),
                     ("All country-years", "e0_corr_pooled.csv")]:
    m = pd.read_csv(PROC / fname, index_col=0)
    keep = list(m.index)
    s = ce.Series([ce.name(c) for c in keep], dp=3, title=label)
    for r in keep:
        s.add(ce.name(r), [float(m.loc[r, c]) for c in keep])
    FIGS[f"A3{label[0]}"] = dict(
        caption=f"The full {len(keep)}-variable correlation matrix, {label.lower()}",
        kind="heatmap",
        payload={"cols": [ce.name(c) for c in keep],
                 "rows": [{"label": ce.name(r),
                           "values": [round(float(m.loc[r, c]), 3) if i != j else None
                                      for j, c in enumerate(keep)]}
                          for i, r in enumerate(keep)],
                 "flags": [[0] * len(keep) for _ in keep],
                 "flagLabel": "", "flagExplain": "",
                 "alt": f"All {len(keep)} variables correlated {label.lower()}, "
                        "diagonal blank"},
        series=s, first="Variable",
        extra_caveat=(
            "The report shows ten construct representatives because at this "
            "size a matrix contains everything and shows almost nothing. It is "
            "here for anyone checking which variables duplicate which."))


# ===========================================================================
#  HEALTH EXTENSION (exploratory, post-freeze)
#
#  Built here rather than embedded as the standalone PNGs the write-up carried,
#  so the appendix keeps one rendering path and these charts get the same
#  checksum, fallback table and caveat treatment as everything else.
#
#  The point of A5 and A6 is the SIGN. The first write-up tabulated unsigned
#  standardised effects beside a figure that plotted signed ones; three of the
#  four measures are negative, which read as near-misses in the expected
#  direction. Both charts here show the sign and say what it means.
# ===========================================================================
_hp = pd.read_csv(ROOT / "data" / "raw" / "health_panel.csv")
if not (PROC / "health_current.csv").exists():
    # Fail loudly rather than dropping three figures quietly. The superset gate
    # compares the appendix against the REPORT, so an appendix that is short on
    # appendix-only figures would pass every check.
    raise SystemExit(
        "health_*.csv missing: run scripts/93_health_extension.py before "
        "47_build_appendix.py (the Makefile hoists it via STAGE_HEALTH)")
_hcur = pd.read_csv(PROC / "health_current.csv")
_hacc = pd.read_csv(PROC / "health_accumulated.csv")
_hbw = pd.read_csv(PROC / "health_between_within.csv")

# ---- A5: unmet medical care, Greece against every member state -------------
_hyrs = [int(y) for y in sorted(_hp.time.unique())
         if _hp[(_hp.time == y)].unmet_care.notna().sum() >= 20]
_uc = _hp[_hp.time.isin(_hyrs)].pivot_table(index="time", columns="geo",
                                            values="unmet_care")
_gr_uc = [None if pd.isna(v) else round(float(v), 1) for v in _uc.get("EL", [])]
_med_uc = [None if pd.isna(v) else round(float(v), 1)
           for v in _uc.median(axis=1)]

fA5 = ce.Series([str(y) for y in _hyrs], dp=1)
fA5.add("Greece", _gr_uc)
fA5.add("EU country median", _med_uc)

FIGS["A5"] = dict(
    caption="Unmet medical care: Greece against every other member state",
    kind="panel",
    payload={"years": _hyrs, "dp": 1, "yLabel": "% of people aged 16+",
             "context": [{"label": NAMES.get(c, c),
                          "values": [None if pd.isna(v) else round(float(v), 1)
                                     for v in _uc[c]]}
                         for c in _uc.columns if c != "EL"],
             "contextLabel": "Each other EU country",
             "series": [{"label": "Greece", "tone": "gr", "weight": "strong",
                         "values": _gr_uc},
                        {"label": "EU country median", "tone": "eu",
                         "style": "dashed", "values": _med_uc}],
             "alt": "The share reporting unmet medical need because of cost, "
                    "waiting lists or distance. Greece runs far above the EU "
                    "median throughout and is worst of 27 in 2024"},
    series=fA5, first="Year",
    extra_caveat=(
        "DESCRIPTIVE ONLY. This is health-care ACCESS, not health status, and "
        "it is not evidence that unmet care explains the hardship gap: tested "
        "as a predictor it is the one correctly signed measure of four and "
        "also the weakest, its leave-one-country-out refits change sign, and "
        "adding it makes Greece's out-of-sample residual larger. The line is "
        "the median MEMBER STATE, not a population-weighted EU aggregate. This "
        "chart runs one year beyond the 2016-2024 model sample, because the "
        "appendix shows the full series; the tests and the write-up's own "
        "figure stop at 2024."))

# ---- A6: the model estimates, signed --------------------------------------
_rows6, fA6 = [], ce.Series(["Estimate", "Low", "High", "Bootstrap p"], dp=3)
for _src, _role in ((_hcur, "current level"), (_hacc, "accumulated")):
    for _r in _src.itertuples():
        _sd = _r.std_effect / _r.coef if _r.coef else 0.0
        _lo, _hi = sorted([_r.ci_lo * _sd, _r.ci_hi * _sd])
        _lab = f"{_r.name} ({_role})"
        _wrong = _r.std_effect < 0
        _rows6.append({
            "label": _lab, "est": round(_r.std_effect, 3),
            "lo": round(_lo, 3), "hi": round(_hi, 3),
            # Wrong-signed results are marked, not just plotted left of zero.
            "tone": "chart-warn" if _wrong else "chart-neutral",
            "right": "wrong sign" if _wrong else "",
            "detail": (f"<b>{_lab}</b><br>{_r.std_effect:+.2f} residual SD "
                       f"[{_lo:+.2f}, {_hi:+.2f}]<br>"
                       f"FDR p = {_r.p_fdr:.3f}, bootstrap p = {_r.boot_p:.3f}"
                       f"<br><span style='opacity:.65'>{_r.outcome.replace('_', ' ')}"
                       f"</span>")})
        fA6.add(_lab, [_r.std_effect, _lo, _hi, _r.boot_p])

FIGS["A6"] = dict(
    caption="No health measure supports the hypothesis, and most point against it",
    kind="coefficient",
    payload={"rows": _rows6, "dp": 2,
             "xLabel": "standardised association with reported hardship, "
                       "residual SD (positive = worse health, more hardship)",
             "alt": "Eight estimates with cluster-robust intervals. Six are "
                    "negative, meaning worse health is associated with LESS "
                    "reported hardship, which is the opposite of the "
                    "pre-registered direction"},
    series=fA6, first="Estimate",
    extra_caveat=(
        "Every measure is pre-registered as higher-is-worse, so only a "
        "POSITIVE estimate can support the hypothesis. Six of the eight are "
        "negative. Intervals are country-clustered; the wild-cluster bootstrap "
        "in the tooltip, not the interval, decides support. None clears it. "
        "Read alongside A7: the negative pooled estimates are cross-country "
        "composition, and the within-country sign is the expected one."))

# ---- A7: the between/within reversal --------------------------------------
_rows7, fA7 = [], ce.Series(["Between countries", "Within countries"], dp=3)
for _r in _hbw.itertuples():
    fA7.add(f"{_r.name} ({'access' if _r.var == 'unmet_care' else 'health status'})",
            [_r.between, _r.within])
    # Name the kind of measure on the row. "Every health-status measure
    # reverses" is true and was still misread, because the chart carries four
    # rows and unmet care -- an ACCESS measure, not a status one -- is not
    # among them. The distinction now travels with the data instead of
    # depending on the reader knowing the term.
    _kind = "access" if _r.var == "unmet_care" else "health status"
    _rows7.append({
        "label": f"{_r.name} ({_kind})",
        "a": round(_r.between, 3), "b": round(_r.within, 3),
        "tone": "chart-warn" if _r.sign_reversal else "chart-neutral",
        "right": "reverses" if _r.sign_reversal else "consistent",
        "strong": bool(_r.sign_reversal),
        "detail": (f"<b>{_r.name}</b><br>between {_r.between:+.3f} "
                   f"(p = {_r.between_p:.3f})<br>within {_r.within:+.3f} "
                   f"(p = {_r.within_p:.3f}, bootstrap {_r.within_boot_p:.3f})")})

FIGS["A7"] = dict(
    caption="The three health-STATUS measures reverse sign between countries "
            "and within them; the access measure does not",
    kind="dumbbell",
    payload={"rows": _rows7, "dp": 2,
             "toneA": "chart-neutral", "toneB": "chart-gr",
             "legendA": "Between countries", "legendB": "Within countries",
             "xLabel": "coefficient on reported hardship",
             "alt": "Four measures, each with its between-country and "
                    "within-country coefficient. All three health-status "
                    "measures cross zero between the two comparisons; unmet "
                    "medical care, the access measure, is positive in both"},
    series=fA7, first="Measure",
    extra_caveat=(
        "Country means and annual deviations are entered together, so the two "
        "ends come from ONE model rather than two. The reading is that the "
        "negative between-country coefficients are composition: richer "
        "countries report worse health AND less hardship, so pooling the "
        "comparisons yields a sign describing neither. Within a country the "
        "direction is the expected one. This is the same limitation the main "
        "report documents, and it does not establish a mechanism: both sides "
        "come from EU-SILC, so common survey method remains live. THREE OF "
        "FOUR ROWS REVERSE, not all four: unmet medical care measures access "
        "to care rather than health status, and it is positive in both "
        "comparisons. It is also the only measure whose leave-one-country-out "
        "refits change sign, so consistent here does not mean supported."))


# ---- A11: arrears against reported hardship --------------------------------
# The one direct pairing the appendix was missing. It belongs here and nowhere
# else: arrears and reported hardship are BOTH EU-SILC self-reports from the
# same household in the same interview, so their agreement is corroboration
# within one instrument and can never be explanation.
_arr = panel.dropna(subset=["arrears", "subjective_poverty"])
_ayrs = [int(y) for y in sorted(_arr.time.unique())
         if _arr[_arr.time == y].geo.nunique() >= 25]
_frames11 = [{"label": str(y), "points": [
    {"x": round(float(r.arrears), 1),
     "y": round(float(r.subjective_poverty), 1),
     "label": NAMES.get(r.geo, r.geo),
     "shortLabel": "Greece" if r.geo == "EL" else None,
     "highlight": r.geo == "EL"}
    for r in _arr[_arr.time == y].itertuples()]} for y in _ayrs]

fA11 = ce.Series(["Greece: arrears", "Greece: reported hardship",
                  "Pooled correlation", "Countries"], dp=2)
for y in _ayrs:
    s = _arr[_arr.time == y]
    g = s[s.geo == "EL"]
    fA11.add(str(y), [
        float(g.arrears.iloc[0]) if len(g) else None,
        float(g.subjective_poverty.iloc[0]) if len(g) else None,
        round(float(s.arrears.corr(s.subjective_poverty)), 3),
        float(s.geo.nunique())])

FIGS["A11"] = dict(
    caption="Falling behind on bills against reported hardship, year by year",
    kind="scatter",
    payload={"frames": _frames11, "dp": 1, "aspect": 0.55,
             "xLabel": "Households in arrears, percent",
             "yLabel": "Reported hardship, percent of households",
             "fitExcludesHighlight": True,
             "fitLabel": "European relationship, Greece excluded",
             "fitLabelShort": "European relationship",
             "alt": "Every member state placed by arrears and reported "
                    "hardship, one frame per year, with Greece marked"},
    series=fA11, first="Year",
    extra_caveat=(
        "SAME-INSTRUMENT CORROBORATION, NOT EXPLANATION. Both axes are "
        "EU-SILC self-reports collected from the same household in the same "
        "interview, so agreement between them is partly the interview. "
        "Arrears also depend on HAVING credit and obligations to fall behind "
        "on: a household that has lost access to credit, or never had it, can "
        "be in severe difficulty and register no arrears at all, which is why "
        "this is the weakest of the four affordability items in the report's "
        "own tracking figure. The fitted line excludes Greece."))


def payload_tag(d, kind="", label=""):
    body = json.dumps(d).replace("</", "<\\/")
    a = (f' data-kind="{kind}"' if kind else "") + \
        (f' data-label="{label}"' if label else "")
    return f'<script type="application/json"{a}>{body}</script>'


def build(fid, spec):
    body = spec["series"].fallback_table(spec.get("first", ""))
    shell = ce.figure(fid, spec["caption"], spec.get("question", ""),
                      "appendix", spec["kind"], {}, body,
                      caveat=spec.get("extra_caveat", ""),
                      checksum=spec["series"].checksum())
    return shell.replace(payload_tag({}), payload_tag(spec["payload"]))


def cards():
    """The detail figures as HTML, in declaration order.

    Called by the appendix builder. Nothing is written here: an intermediate
    page would be a second appendix document, and the whole point of the
    superset rule is that there is one.
    """
    return "\n".join(build(k, v) for k, v in FIGS.items())


if __name__ == "__main__":
    print(f"{len(FIGS)} appendix detail figures ready: {', '.join(FIGS)}")
    print("built into output/statistical_appendix.html by 47_build_appendix.py")
