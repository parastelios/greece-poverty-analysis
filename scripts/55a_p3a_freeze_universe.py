"""P3a step 1: freeze the Family D indicator universe, domains, weights and
baseline BEFORE any outcome testing.

Emits data/processed/p3a_frozen_universe.json, committed before 55b runs.
Nothing in it may be revised after seeing results.
"""
import json
import sys

sys.path.insert(0, ".")
from validate_outputs import json_safe

series = json.load(open("../data/processed/appendix_series_core.json"))["series"]
src = open("46_appendix_data.py").read()
WORSE_HIGH = eval("{" + src.split("WORSE_HIGH = {")[1].split("}")[0] + "}")
CIRCULAR = eval("{" + src.split("CIRCULAR = {")[1].split("}")[0] + "}")

# Tier 0 -- proximate to the outcome, excluded from the PRIMARY composite.
# arrears, unexpected and housing_overburden are already out via CIRCULAR;
# financial expectations is not, and must be.
TIER0 = {"fin_expectations"}
LABOUR = {"unemployment", "youth_unemployment", "employment_rate", "ltu",
          "work_effort_squeeze", "working_hours", "hourly_comp"}

indep = sorted(k for k in WORSE_HIGH if k not in CIRCULAR and k in series)
primary = sorted(k for k in indep if k not in TIER0)

frozen = {
    "status": "FROZEN before outcome testing. Not revisable after seeing results.",
    "baseline": "each country's own mean breadth over 2008-2009",
    "construction": ("per indicator, worst-quintile flag with the worse-direction "
                     "declared ex ante; averaged WITHIN domain, then averaged "
                     "ACROSS domains with equal domain weight; excess over the "
                     "country's own baseline, floored at zero, cumulated"),
    "weighting": "equal by DOMAIN, not by indicator",
    "window": "2008 onward for accumulation; model window 2015-2024",
    "min_indicators_per_country_year": 8,
    "variants": {
        "primary_objective_only": primary,
        "sensitivity_all_indicators": indep,
        "sensitivity_non_labour": sorted(k for k in primary if k not in LABOUR),
    },
    "domains": {},
    "tier0_excluded": sorted(TIER0),
    "circular_excluded": sorted(CIRCULAR),
    "fdr_family": ("the individual accumulated indicators in the PRIMARY variant, "
                   "corrected together with Benjamini-Hochberg at 5%"),
    "outcomes": ["hardship level (primary)", "hardship minus AROP (secondary)"],
}
for k in indep:
    frozen["domains"].setdefault(series[k]["group"], []).append(k)
for g in frozen["domains"]:
    frozen["domains"][g] = sorted(frozen["domains"][g])

json_safe(frozen)
open("../data/processed/p3a_frozen_universe.json", "w").write(json.dumps(frozen, indent=2))
print(f"primary (objective-only): {len(primary)} indicators")
print(f"all-indicator sensitivity: {len(indep)}")
print(f"non-labour sensitivity:    {len(frozen['variants']['sensitivity_non_labour'])}")
print(f"\ndomains ({len(frozen['domains'])}), equal-weighted:")
for g, ks in sorted(frozen["domains"].items()):
    print(f"  {len(ks):2}  {g}")
print(f"\nTier 0 excluded from primary: {sorted(TIER0)}")
