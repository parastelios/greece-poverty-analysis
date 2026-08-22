"""Minimum detectable effects for E, by simulation on the actual cluster structure.

Pre-registered at a747e7a. Published BEFORE any E result. A null whose effect
size sits below available power is labelled INCONCLUSIVE UNDER AVAILABLE POWER,
not unsupported with adequate sensitivity.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "data" / "processed"
sys.path.insert(0, str(HERE))
from validate_outputs import scalar

d = pd.read_csv(OUT / "e0_extended_panel.csv")
d = d.dropna(subset=["subjective_poverty", "arop"]).copy()
rng = np.random.default_rng(20260822)
N_SIM, ALPHA = 400, 0.05

# residual scale under the pre-registered primary specification with no construct
base = smf.ols("subjective_poverty ~ arop + C(time)", data=d).fit()
resid_sd = float(np.std(base.resid, ddof=1))
print(f"panel: {d.geo.nunique()} countries, {d.time.nunique()} years, {len(d)} obs")
print(f"residual SD under the primary baseline: {resid_sd:.2f} points\n")


# Variance components of the baseline residual. Simulated noise is drawn from
# these rather than resampled from the data, because permuting residuals WITHIN
# country preserves the country mean -- which is correlated with any regressor
# that varies mainly between countries. That correlation biased the first
# version badly: a planted +5.31 came back as -2.35.
_r = base.resid
_cm = _r.groupby(d["geo"]).transform("mean")
SD_BETWEEN = float(np.std(_r.groupby(d["geo"]).mean(), ddof=1))
SD_WITHIN = float(np.std(_r - _cm, ddof=1))
print(f"residual variance components: between-country SD {SD_BETWEEN:.2f}, "
      f"within-country SD {SD_WITHIN:.2f}")
GEOS = d["geo"].unique()


def power_at(effect_sd, xcol, n_sim=N_SIM):
    """Share of simulations detecting a planted effect at alpha WITH THE RIGHT SIGN.
    Sign is required: a significant coefficient of the wrong sign is not detection."""
    x = d[xcol]
    xs = ((x - x.mean()) / x.std()).values
    beta = effect_sd * resid_sd
    fitted = base.fittedvalues.values
    sim = d.assign(xs=xs)
    hits = 0
    for _ in range(n_sim):
        ce = pd.Series(rng.normal(0, SD_BETWEEN, len(GEOS)), index=GEOS)
        noise = d["geo"].map(ce).values + rng.normal(0, SD_WITHIN, len(d))
        sim["y"] = fitted + beta * xs + noise
        m = smf.ols("y ~ arop + C(time) + xs", data=sim).fit(
            cov_type="cluster", cov_kwds={"groups": sim["geo"]})
        if m.pvalues["xs"] < ALPHA and np.sign(m.params["xs"]) == np.sign(beta):
            hits += 1
    return hits / n_sim


# one representative continuous regressor; MDE is a property of the design, not the variable
rows = []
for eff in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]:
    p = power_at(eff, "aic_pps_pc")
    rows.append(dict(effect_sd_per_sd=eff,
                     effect_points_per_sd=round(eff * resid_sd, 2),
                     power=round(p, 3)))
    print(f"  effect {eff:.2f} residual SD per 1 SD of x "
          f"({eff*resid_sd:5.2f} points)  ->  power {p:.2f}")
mde = next((r for r in rows if r["power"] >= 0.80), None)
mde80 = mde["effect_sd_per_sd"] if mde else None
print(f"\n  MDE at 80% power: "
      + (f"{mde80:.2f} residual SD per SD ({mde80*resid_sd:.2f} points)"
         if mde80 else f"> {rows[-1]['effect_sd_per_sd']:.2f} SD -- not reached in the grid"))

pd.DataFrame(rows).to_csv(OUT / "e_mde.csv", index=False)
print(f"\nWritten to {OUT/'e_mde.csv'}")
print("\nRULE: any E null whose plausible effect is below the MDE is reported as")
print("INCONCLUSIVE UNDER AVAILABLE POWER, not as unsupported with adequate sensitivity.")
