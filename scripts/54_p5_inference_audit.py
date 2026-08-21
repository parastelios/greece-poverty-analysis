"""P5: inference and influence audit of the frozen P3 objective-only model.

Interpretation rules committed at 80001ac, BEFORE this script was written.
See scripts/mundlak_rule.py and docs/project_description_v3.md §5b.1.

P5 audits the accumulation coefficient. It cannot assign a P3 branch: country
fixed effects absorb exactly the Greek intercept the leave-Greece-out
prediction needs.
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, ".")
from outcome import official_hardship
from mundlak_rule import classify, instability_flags, downgrade_warranted, OUTCOMES

OUT = "../data/processed"
V = "cum_excess_unemployment"
OBJECTIVE = ["severe_mat_soc_deprivation", "housing_cost_overburden", "ltu_rate",
             "aic_pps_pc_k", "wage_years_below_2008", V]

p = pd.read_csv(f"{OUT}/persistence_share_panel.csv")
off = official_hardship().rename(columns={"value": "hardship"})[["geo", "time", "hardship"]]
d = (p.merge(off, on=["geo", "time"], how="left")
       .query("2015 <= time <= 2024")
       .dropna(subset=OBJECTIVE + ["hardship"]).copy())
F = "hardship ~ " + " + ".join(OBJECTIVE) + " + C(time)"
base = smf.ols(F, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
b0 = base.params[V]
print(f"frozen P3 coefficient on {V}: {b0:+.4f} (se {base.bse[V]:.4f})\n")

# ---------------------------------------------------------------- 1. country FE ----
print("=" * 74); print("1. COUNTRY + YEAR FIXED EFFECTS"); print("=" * 74)
F_fe = F + " + C(geo)"
fe = smf.ols(F_fe, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["geo"]})
print(f"  {V}: {fe.params[V]:+.4f} (se {fe.bse[V]:.4f}, p {fe.pvalues[V]:.4f})")
print(f"  vs no-country-FE {b0:+.4f}  -> change {100*(fe.params[V]-b0)/abs(b0):+.0f}%")
print("  NOTE: this specification cannot produce the leave-Greece-out residual.")

# ---------------------------------------------------------------- 2. Mundlak ----
print("\n" + "=" * 74); print("2. MUNDLAK WITHIN/BETWEEN DECOMPOSITION"); print("=" * 74)
dm = d.copy()
dm[f"{V}_bar"] = dm.groupby("geo")[V].transform("mean")          # between
dm[f"{V}_dev"] = dm[V] - dm[f"{V}_bar"]                          # within
others = [v for v in OBJECTIVE if v != V]
F_m = ("hardship ~ " + " + ".join(others) +
       f" + {V}_dev + {V}_bar + C(time)")
mu = smf.ols(F_m, data=dm).fit(cov_type="cluster", cov_kwds={"groups": dm["geo"]})
w_c, w_p = mu.params[f"{V}_dev"], mu.pvalues[f"{V}_dev"]
b_c, b_p = mu.params[f"{V}_bar"], mu.pvalues[f"{V}_bar"]
print(f"  WITHIN  (deviation from country mean) {w_c:+.4f}  se {mu.bse[f'{V}_dev']:.4f}  p {w_p:.4f}")
print(f"  BETWEEN (country mean)                {b_c:+.4f}  se {mu.bse[f'{V}_bar']:.4f}  p {b_p:.4f}")

# ---------------------------------------------------------------- 3. influence ----
print("\n" + "=" * 74); print("3. INFLUENCE DIAGNOSTICS BY COUNTRY"); print("=" * 74)
rows = []
for c in sorted(d.geo.unique()):
    m = smf.ols(F, data=d[d.geo != c]).fit()
    rows.append({"dropped": c, "coef": m.params[V],
                 "pct": 100 * (m.params[V] - b0) / abs(b0)})
inf = pd.DataFrame(rows).sort_values("pct", key=abs, ascending=False)
print(inf.head(6).round(3).to_string(index=False))
sign_rev = bool((np.sign(inf.coef) != np.sign(b0)).any())
max_loo = float(inf.pct.abs().max())
gr_pct = float(inf[inf.dropped == "EL"].pct.iloc[0])
print(f"\n  max |change| {max_loo:.1f}% ({inf.iloc[0]['dropped']}) | "
      f"Greece dropped: {gr_pct:+.1f}% | sign reversal: {sign_rev}")
top3 = set(inf.head(3).dropped)
crisis = {"EL", "ES", "IT", "PT", "CY", "IE"}
lev_conc = len(top3 & crisis) >= 3 and float(inf.head(3).pct.abs().sum()) > 60
print(f"  top-3 influential: {sorted(top3)} | leverage concentrated in crisis countries: {lev_conc}")

# ---------------------------------------------------------------- 4. bootstrap ----
print("\n" + "=" * 74); print("4. BOOTSTRAP: WEIGHTS, SEEDS, REPLICATIONS"); print("=" * 74)
geos = d.geo.unique()
restricted = [x for x in OBJECTIVE if x != V]
m_r = smf.ols("hardship ~ " + " + ".join(restricted) + " + C(time)", data=d).fit()
fit_null, res_null = m_r.predict(d), d["hardship"] - m_r.predict(d)
t_obs = b0 / base.bse[V]
WEIGHTS = {
    "rademacher": lambda r, n: r.choice([-1.0, 1.0], size=n),
    "webb":       lambda r, n: r.choice([-np.sqrt(1.5), -1.0, -np.sqrt(.5),
                                          np.sqrt(.5), 1.0, np.sqrt(1.5)], size=n),
    "mammen":     lambda r, n: np.where(r.random(n) < (np.sqrt(5)+1)/(2*np.sqrt(5)),
                                        -(np.sqrt(5)-1)/2, (np.sqrt(5)+1)/2),
}
boot = []
for wname, wf in WEIGHTS.items():
    for seed in (20250821, 7, 99):
        rng = np.random.default_rng(seed)
        ts = []
        for _ in range(999):
            w = pd.Series(wf(rng, len(geos)), index=geos)
            db = d.copy()
            db["hardship"] = fit_null + res_null.values * d.geo.map(w).values
            mb = smf.ols(F, data=db).fit(cov_type="cluster", cov_kwds={"groups": db["geo"]})
            ts.append(abs(mb.params[V] / mb.bse[V]))
        n_ex = int(np.sum(np.array(ts) >= abs(t_obs)))
        boot.append({"weights": wname, "seed": seed, "reps": 999,
                     "n_extreme": n_ex, "p_MC": (n_ex + 1) / 1000})
bt = pd.DataFrame(boot)
print(bt.to_string(index=False))
consistent = bool((bt.p_MC < 0.05).all())
print(f"\n  p_MC = {bt.p_MC.max():.4f}; {bt.n_extreme.max()} of 999 bootstrap statistics "
      f"were at least as extreme as observed;")
print(f"  {1/1000:.4f} is the simulation resolution floor.")
print(f"  consistent below 0.05 across all {len(bt)} weight/seed combinations: {consistent}")

# ---------------------------------------------------------------- 5. sensitivities ----
print("\n" + "=" * 74); print("5. PRE-DECLARED SENSITIVITIES"); print("=" * 74)
dd = d.sort_values(["geo", "time"]).copy()
for c in ["hardship", V] + others:
    dd[f"d_{c}"] = dd.groupby("geo")[c].diff()
fd = dd.dropna(subset=[f"d_{c}" for c in ["hardship", V] + others])
F_fd = "d_hardship ~ " + " + ".join(f"d_{c}" for c in others) + f" + d_{V} + C(time)"
m_fd = smf.ols(F_fd, data=fd).fit(cov_type="cluster", cov_kwds={"groups": fd["geo"]})
print(f"  first differences: d_{V} {m_fd.params[f'd_{V}']:+.4f} "
      f"(se {m_fd.bse[f'd_{V}']:.4f}, p {m_fd.pvalues[f'd_{V}']:.4f}), n={int(m_fd.nobs)}")
dt = d.copy(); dt["t"] = dt.time - dt.time.min()
m_tr = smf.ols(F + " + C(geo) + C(geo):t", data=dt).fit(
    cov_type="cluster", cov_kwds={"groups": dt["geo"]})
print(f"  country trends:    {V} {m_tr.params[V]:+.4f} "
      f"(se {m_tr.bse[V]:.4f}, p {m_tr.pvalues[V]:.4f})")
print(f"                     collapse/reverse? "
      f"{'YES' if (np.sign(m_tr.params[V]) != np.sign(b0) or abs(m_tr.params[V]) < 0.5*abs(b0)) else 'no'}")

# ---------------------------------------------------------------- verdict ----
print("\n" + "=" * 74); print("VERDICT (rules committed at 80001ac)"); print("=" * 74)
flags = instability_flags(sign_reversed=sign_rev, max_loo_change_pct=max_loo,
                          greece_change_pct=gr_pct, bootstrap_consistent=consistent,
                          leverage_concentrated=lev_conc)
key, expl = classify(w_c, w_p, b_c, b_p, stable=not flags)
print(f"  instability flags: {flags if flags else 'none'}")
print(f"  MUNDLAK OUTCOME {key}: {expl}")
print(f"  downgrade P3 branch 2? {'YES' if downgrade_warranted(flags) else 'NO'}")
pd.DataFrame([{"within": w_c, "within_p": w_p, "between": b_c, "between_p": b_p,
               "fe_coef": fe.params[V], "outcome": key, "flags": "; ".join(flags),
               "downgrade": downgrade_warranted(flags), "max_loo_pct": max_loo,
               "greece_pct": gr_pct, "p_MC_max": bt.p_MC.max()}]
             ).to_csv(f"{OUT}/p5_audit.csv", index=False)
bt.to_csv(f"{OUT}/p5_bootstrap.csv", index=False)
inf.to_csv(f"{OUT}/p5_influence.csv", index=False)
print(f"\nWritten to {OUT}/p5_*.csv")
