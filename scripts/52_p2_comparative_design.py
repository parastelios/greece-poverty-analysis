"""P2: comparative-case design for Greek subjective hardship.

Pre-registered in docs/archive/pre-v2-publication/project_description_v3.md §4.1, committed at 7cca9c2
BEFORE this script was written. Windows, donor rules, safeguards and every
numeric failure threshold were fixed in that commit.

  pre-period   2005-2008 (uncontaminated, excludes the 2009 transition year)
  transition   2009, plotted, excluded from fitting and from the main estimate
  post-period  2010 onward
  sensitivity  2005-2009 pre-period, reported regardless of fit

The design is allowed to fail, and failure is reported as failure.
"""
import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize

sys.path.insert(0, ".")
from outcome import official_hardship
from eurostat import fetch
from eu_membership import eu_members

OUT = "../data/processed"
PRE, POST, TRANS = list(range(2005, 2009)), list(range(2010, 2026)), 2009
# programme countries: cannot serve as unaffected donors
PROGRAMME = {"EL", "PT", "IE", "CY", "ES"}
MAX_W, MIN_EFF_DONORS = 0.50, 3.0

d = official_hardship()
piv = d.pivot(index="time", columns="geo", values="value")
elig = [c for c in piv.columns
        if c not in PROGRAMME and piv.loc[PRE, c].notna().all()
        and piv.loc[[y for y in POST if y in piv.index], c].notna().mean() > 0.9]
print(f"Donor pool: {len(elig)} eligible "
      f"(excluded as programme countries: {sorted(PROGRAMME - {'EL'})})")
print(f"  {elig}\n")

# ---- pre-declared covariates, averaged over the pre-period ----
# The pre-declared covariate set was AROP, income, unemployment and deprivation.
# Unemployment is DROPPED, and this is a coverage fact rather than a choice:
# une_rt_a for 2005-2008 returns only France and Sweden -- the same wall that
# withdrew P4. Recorded here so the departure from the pre-registration is
# visible rather than silent.
cov_specs = [("ilc_li02", dict(age=["TOTAL"], sex=["T"], unit=["PC"],
                               statinfo=["MED_EI"], rskpovth=["B_60"]), "arop"),
             ("ilc_mddd11", dict(age=["TOTAL"], sex=["T"], unit=["PC"]), "deprivation"),
             ("nama_10_pc", dict(na_item=["P41"], unit=["CP_PPS_EU27_2020_HAB"]), "income")]
covs = None
for code, filt, nm in cov_specs:
    c = fetch(code, time=PRE, **filt)[["geo", "time", "value"]].rename(columns={"value": nm})
    c = c.groupby("geo", as_index=False)[nm].mean()
    covs = c if covs is None else covs.merge(c, on="geo", how="outer")
covs = covs.set_index("geo")


def fit(pre_years, pool, lam=0.0):
    Y0 = piv.loc[pre_years, pool].values
    y1 = piv.loc[pre_years, "EL"].values
    n = len(pool)

    def loss(w):
        return np.sum((y1 - Y0 @ w) ** 2) + lam * np.sum(w ** 2)
    r = minimize(loss, np.repeat(1 / n, n), method="SLSQP",
                 bounds=[(0, 1)] * n,
                 constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}])
    w = pd.Series(r.x, index=pool).clip(lower=0)
    return w / w.sum()


def rmse(w, years, unit="EL"):
    if unit == "EL":
        actual = piv.loc[years, "EL"].values
    else:
        actual = piv.loc[years, unit].values
    synth = piv.loc[years, w.index].values @ w.values
    return float(np.sqrt(np.nanmean((actual - synth) ** 2)))


def run(label, pre_years, lam=0.0, verbose=True):
    w = fit(pre_years, elig, lam)
    pre_r = rmse(w, pre_years)
    post_years = [y for y in POST if y in piv.index]
    post_gap = float(np.nanmean(piv.loc[post_years, "EL"].values
                                - piv.loc[post_years, w.index].values @ w.values))
    post_r = rmse(w, post_years)
    ratio = post_r / pre_r if pre_r > 0 else np.inf
    top = w[w > 0.01].sort_values(ascending=False)
    eff = 1 / np.sum(w ** 2)
    if verbose:
        print(f"--- {label}")
        print(f"    pre-period RMSE {pre_r:6.2f} | post gap {post_gap:+6.1f} pp | "
              f"post/pre RMSPE {ratio:6.2f}")
        print(f"    weights: " + ", ".join(f"{g}:{v:.2f}" for g, v in top.items()))
        print(f"    max weight {w.max():.2f} (bar <={MAX_W}) | "
              f"effective donors {eff:.1f} (bar >={MIN_EFF_DONORS})")
    return dict(label=label, w=w, pre_rmse=pre_r, post_gap=post_gap,
                ratio=ratio, max_w=float(w.max()), eff=float(eff))


print("=" * 74); print("PRIMARY SPECIFICATION"); print("=" * 74)
main = run("2005-2008 pre-period, unpenalised", PRE)
reg = run("2005-2008, regularised (lam=0.5)", PRE, lam=0.5)
print()
print("=" * 74); print("PREDETERMINED SENSITIVITY (reported regardless of fit)"); print("=" * 74)
sens = run("2005-2009 pre-period", list(range(2005, 2010)))

# ---- placebo distribution: every eligible donor treated as if it were Greece ----
print("\n" + "=" * 74); print("PLACEBO DISTRIBUTION"); print("=" * 74)
rows = []
for g in elig:
    pool = [c for c in elig if c != g]
    Y0 = piv.loc[PRE, pool].values; y1 = piv.loc[PRE, g].values
    r = minimize(lambda w: np.sum((y1 - Y0 @ w) ** 2), np.repeat(1/len(pool), len(pool)),
                 method="SLSQP", bounds=[(0, 1)] * len(pool),
                 constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}])
    w = pd.Series(np.clip(r.x, 0, None), index=pool); w = w / w.sum()
    pr = float(np.sqrt(np.mean((y1 - Y0 @ w.values) ** 2)))
    py = [y for y in POST if y in piv.index]
    por = float(np.sqrt(np.nanmean((piv.loc[py, g].values
                                    - piv.loc[py, w.index].values @ w.values) ** 2)))
    rows.append({"geo": g, "pre_rmse": pr, "post_rmse": por,
                 "ratio": por / pr if pr > 0 else np.inf})
pl = pd.DataFrame(rows)
pl = pd.concat([pl, pd.DataFrame([{"geo": "EL", "pre_rmse": main["pre_rmse"],
                                   "post_rmse": main["ratio"] * main["pre_rmse"],
                                   "ratio": main["ratio"]}])], ignore_index=True)
pl = pl.sort_values("ratio", ascending=False).reset_index(drop=True)
pl["rank"] = pl.index + 1
# A placebo whose own pre-period fit is near-perfect produces an enormous
# post/pre ratio for arithmetic reasons, not substantive ones (Czechia 54262).
# Abadie's convention is to drop such units. NOTE: no numeric threshold for this
# was pre-declared in §4.1 -- that is a gap in the pre-registration. The filtered
# ranking below is therefore reported as a DIAGNOSTIC, and the gate is judged on
# the unfiltered ranking that was pre-declared.
gr_pre = main["pre_rmse"]
pl["degenerate_prefit"] = pl.pre_rmse < 0.2 * gr_pre
el = pl[pl.geo == "EL"].iloc[0]
print(f"  Greece pre-RMSE {main['pre_rmse']:.2f} vs placebo median "
      f"{pl[pl.geo!='EL'].pre_rmse.median():.2f}")
print(f"  post/pre RMSPE ratio rank: {int(el['rank'])} of {len(pl)}")
print(f"  top 5 by ratio: " + ", ".join(f"{r.geo}:{r.ratio:.1f}" for r in pl.head(5).itertuples()))
print(f"  minimum attainable p-value: 1/{len(pl)} = {1/len(pl):.3f}")
keep = pl[~pl.degenerate_prefit].sort_values("ratio", ascending=False).reset_index(drop=True)
keep["rank"] = keep.index + 1
n_drop = int(pl.degenerate_prefit.sum())
elk = keep[keep.geo == "EL"]
print(f"  [diagnostic, not a pre-declared gate] dropping {n_drop} placebos with "
      f"pre-RMSE < 20% of Greece's:")
print(f"     Greece ratio rank {int(elk['rank'].iloc[0]) if len(elk) else '-'} of {len(keep)}, "
      f"top: " + ", ".join(f"{r.geo}:{r.ratio:.1f}" for r in keep.head(4).itertuples()))

# ---- leave-one-donor-out ----
print("\n" + "=" * 74); print("LEAVE-ONE-DONOR-OUT"); print("=" * 74)
loo = []
for g in main["w"][main["w"] > 0.01].index:
    pool = [c for c in elig if c != g]
    w = fit(PRE, pool)
    py = [y for y in POST if y in piv.index]
    gap = float(np.nanmean(piv.loc[py, "EL"].values - piv.loc[py, w.index].values @ w.values))
    loo.append({"dropped": g, "post_gap": gap,
                "pct_change": 100 * (gap - main["post_gap"]) / abs(main["post_gap"])})
lo = pd.DataFrame(loo)
print(lo.round(2).to_string(index=False))
worst = lo["pct_change"].abs().max() if len(lo) else 0.0
flip = bool((np.sign(lo["post_gap"]) != np.sign(main["post_gap"])).any()) if len(lo) else False

# ---- covariate balance ----
print("\n" + "=" * 74); print("COVARIATE BALANCE (pre-declared, 2005-2008 means)"); print("=" * 74)
w = main["w"]
for nm in ["arop", "deprivation", "income"]:
    if nm in covs.columns:
        gr = covs.loc["EL", nm]
        sy = float(np.nansum([w.get(g, 0) * covs.loc[g, nm] for g in w.index if g in covs.index]))
        print(f"  {nm:8} Greece {gr:8.1f} | synthetic {sy:8.1f} | diff {gr-sy:+8.1f}")

# ---- verdict against the pre-declared thresholds ----
print("\n" + "=" * 74); print("VERDICT AGAINST PRE-DECLARED THRESHOLDS"); print("=" * 74)
checks = [
    (f"max weight <= {MAX_W}", main["max_w"] <= MAX_W, f"{main['max_w']:.2f}"),
    (f"effective donors >= {MIN_EFF_DONORS}", main["eff"] >= MIN_EFF_DONORS, f"{main['eff']:.1f}"),
    ("no LOO sign flip", not flip, "flip" if flip else "none"),
    ("LOO change <= 50%", worst <= 50, f"{worst:.0f}%"),
    ("pre-RMSE <= placebo median", main["pre_rmse"] <= pl[pl.geo != "EL"].pre_rmse.median(),
     f"{main['pre_rmse']:.2f} vs {pl[pl.geo!='EL'].pre_rmse.median():.2f}"),
    ("RMSPE ratio in top 3", int(el["rank"]) <= 3, f"rank {int(el['rank'])}"),
]
for name, ok, val in checks:
    print(f"  [{'PASS' if ok else 'FAIL'}]  {name:34} {val}")
passed = all(c[1] for c in checks)
print(f"\n  ==> DESIGN {'PASSES' if passed else 'FAILS'} its pre-registered gates")

pd.DataFrame([{"spec": r["label"], "pre_rmse": r["pre_rmse"], "post_gap": r["post_gap"],
               "ratio": r["ratio"], "max_w": r["max_w"], "eff_donors": r["eff"]}
              for r in (main, reg, sens)]).to_csv(f"{OUT}/p2_specifications.csv", index=False)
pl.to_csv(f"{OUT}/p2_placebo_distribution.csv", index=False)
main["w"].sort_values(ascending=False).to_csv(f"{OUT}/p2_donor_weights.csv")
print(f"\nWritten to {OUT}/p2_*.csv")
