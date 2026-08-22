"""Pre-registration for the construct-mapping analysis (E).

Committed BEFORE any E model runs. The commit introducing this file contains no
E results. E maps and tests constructs; it does not search for a combined model
and it may not alter p5f-frozen.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "data" / "processed"
CMAP = json.load(open(OUT / "construct_map_frozen.json"))

# ---------------------------------------------------------------- 1. outcomes ----
OUTCOMES = {
 "primary": dict(
   name="hardship level",
   formula="subjective_poverty ~ arop + C(time) + <construct>",
   note="AROP enters as a covariate. This is the estimand every headline claim uses."),
 "secondary": dict(
   name="hardship minus AROP",
   formula="(subjective_poverty - arop) ~ C(time) + <construct>",
   note=("AROP is NOT added again on the right-hand side: it is already inside the "
         "outcome by subtraction, and regressing the gap on AROP is algebraically "
         "valid but not interpretable."),
   authority="A secondary result CANNOT override a primary null. It may qualify or "
             "illustrate a primary finding; it may never create one."),
}

# ---------------------------------------------------------------- 2. transformations ----
# adverse direction, baseline, floor and exact formula for every primary.
# All cumulations are RUNNING (value at year t uses only years <= t). No future
# information is carried backward -- verified on the panel before any model runs.
T = {
 "aic_pps_pc": dict(construct="C1", adverse="lower_is_worse",
   current="level, PPS per capita",
   accumulated="sum over years >= 2008 of max(0, 100 - 100*x_t/x_2008)",
   baseline=2008, floor=True, estimand_note="current = standing; accumulated = damage"),
 "ltu_rate": dict(construct="C2", adverse="higher_is_worse",
   current="level, % of active population", accumulated=None, baseline=None, floor=None,
   estimand_note="current-snapshot representative only"),
 "cum_excess_unemployment": dict(construct="C2", adverse="higher_is_worse",
   current=None, accumulated="sum over years >= 2009 of max(0, u_t - u_2009)",
   baseline=2009, floor=True,
   estimand_note="accumulated representative only; base 2009 on coverage. ALREADY "
                 "BUILT AND FROZEN -- reused, not reconstructed"),
 **{v: dict(construct="C3", adverse="lower_is_worse",
   current="index, own 2008 = 100",
   accumulated="sum over years >= 2008 of max(0, 100 - x_t); duration = count of "
               "consecutive years with x_t < 100",
   baseline=2008, floor=True,
   estimand_note="shortfall AREA and DURATION are separate quantities and are "
                 "reported separately, never summed")
   for v in ["real_wages_idx", "real_income_idx", "arop_threshold_real"]},
 "pct_below_peak": dict(construct="C3", adverse="higher_is_worse",
   current="% below own running GDP peak",
   accumulated="sum over years >= 2008 of x_t (already non-negative by construction)",
   baseline=2008, floor=False,
   estimand_note="area under the shortfall curve; the series is already a shortfall"),
 "wadj_a01": dict(construct="C4", adverse="higher_is_worse",
   current="index, EU27 = 100",
   accumulated="sum over years >= 2008 of max(0, x_t - 100)",
   baseline="EU27 = 100 benchmark, years >= 2008", floor=True,
   estimand_note="excess above the EU-relative benchmark, not above the country's own past"),
 "hicp": dict(construct="C5", adverse="higher_is_worse",
   current="% annual change",
   accumulated="compounded: prod over years 2008..t of (1 + r_s/100) - 1",
   baseline=2008, floor=False,
   estimand_note="COMPOUNDED, NOT SUMMED. See the wording rules: this is cumulative "
                 "price growth, not affordability and not hardship"),
 "housing_cost_overburden": dict(construct="C6", adverse="higher_is_worse",
   current="% of people",
   accumulated="sum over years >= 2010 of max(0, x_t - x_2010)",
   baseline=2010, floor=True,
   estimand_note="See the wording rules: deterioration SINCE 2010, not total burden"),
 "severe_mat_soc_deprivation": dict(construct="P1", adverse="higher_is_worse",
   current="% of people",
   accumulated="sum over years >= 2008 of max(0, x_t - x_2008)",
   baseline=2008, floor=True,
   estimand_note="DIAGNOSTIC ONLY; never a headline explanation"),
}

# ---------------------------------------------------------------- wording rules ----
WORDING = [
 ("housing_accumulated",
  "Summing excess above the 2010 country baseline measures ACCUMULATED DETERIORATION "
  "SINCE 2010, not total accumulated housing burden. A country already heavily "
  "overburdened in 2010 receives no credit for that initial level. Never describe it "
  "as 'total housing burden' or 'how overburdened a country has been'."),
 ("inflation_accumulated",
  "Compounded HICP since 2008 measures CUMULATIVE PRICE GROWTH, not affordability and "
  "not hardship. Prices rising says nothing on its own about whether households can "
  "afford them; wage-adjusted affordability is a separate construct (C4) and is where "
  "that question is addressed. Never describe C5 as an affordability or hardship measure."),
 ("estimand_labelling",
  "Current and accumulated versions of a construct are DIFFERENT ESTIMANDS and are "
  "always labelled as such. They are never presented as two measurements of one thing."),
]

# ---------------------------------------------------------------- 3. samples ----
SAMPLES = dict(
 window="2015-2024",
 equal_sample_rule=("Any current-versus-accumulated comparison MUST run on identical "
                    "observations. Where the two differ in coverage, both are refit on "
                    "the intersection and the intersection result is the one compared."),
 reporting="Every result reports countries, years and observations.",
 coverage_sensitivity=("Where a construct's coverage differs from the common sample, a "
                       "common-sample sensitivity is reported alongside."),
 frozen_p3=("The frozen P3 specification stays on its ORIGINAL 269-row sample and is "
            "not refit to any E sample."))

# ---------------------------------------------------------------- 4. multiplicity ----
MULTIPLICITY = dict(
 families=["BH family 1: current primary representatives, primary outcome",
           "BH family 2: accumulated primary representatives, primary outcome",
           "BH family 3: secondary outcome, corrected separately"],
 sensitivity_rule=("A sensitivity variant CANNOT become a discovery when its primary "
                   "representative fails. Sensitivities qualify a supported primary; "
                   "they never substitute for a failed one."),
 scope=("Correction does NOT span the project's earlier searches. Families A, B, C and D "
        "were separate exploratory episodes; E's correction covers E only, and E's "
        "results inherit exploratory status from that fact."))

# ---------------------------------------------------------------- 5-6. inference ----
INFERENCE = ["Country-clustered point estimates.",
             "Wild cluster bootstrap for ANYTHING described as supported.",
             "Leave-one-country-out sign and coefficient stability.",
             "Between/within decomposition for every accumulated result.",
             "First differences REQUIRED before any dynamic wording is permitted."]

DECISION = ["direction matches the pre-registration",
            "FDR-adjusted result survives within its declared family",
            "wild-cluster bootstrap supports it",
            "coefficient is leave-one-country-out stable in sign",
            "Greece's EQUAL-SAMPLE absolute residual improves",
            "no proximity or construction-overlap rule is violated"]

# ---------------------------------------------------------------- 7-8 ----
MDE = ("Minimum detectable effects are computed by simulation on the actual cluster "
       "structure and published BEFORE any E result. Reported in standardized effect "
       "units and, where useful, translated into original units. A null whose effect "
       "size sits below available power is labelled INCONCLUSIVE UNDER AVAILABLE POWER, "
       "not unsupported with adequate sensitivity.")
COMBINED = ("E maps and tests constructs. The combined specification REMAINS FROZEN P3. "
            "No pairwise combination search, no alternative combined-model search, no "
            "forward or backward selection.")
FROZEN = ("Nothing in E may alter p5f-frozen. E's purpose is to make the path to that "
          "result transparent and to document which competing constructs survive or fail. "
          "If an E result appears to contradict a frozen claim, the frozen claim stands "
          "and the contradiction is reported as an open question.")

prereg = dict(
 status="PRE-REGISTERED. The commit introducing this file contains no E results.",
 construct_map_source="data/processed/construct_map_frozen.json",
 outcomes=OUTCOMES, transformations=T, wording_rules=dict(WORDING), samples=SAMPLES,
 multiplicity=MULTIPLICITY, inference=INFERENCE, decision_rule_all_must_hold=DECISION,
 mde=MDE, combined_model=COMBINED, frozen_protection=FROZEN,
 committed_at=subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip())
json.dump(prereg, open(OUT / "e_preregistration.json", "w"), indent=2)

print("E PRE-REGISTRATION LOCKED\n")
print(f"  primary outcome   : {OUTCOMES['primary']['formula']}")
print(f"  secondary outcome : {OUTCOMES['secondary']['formula']}")
print(f"  transformations   : {len(T)} primaries, each with direction, baseline and floor")
print(f"  wording rules     : {len(WORDING)}")
print(f"  BH families       : {len(MULTIPLICITY['families'])}")
print(f"  decision rule     : {len(DECISION)} conditions, ALL must hold")
print("\n  accumulated constructions by type:")
for v, t in T.items():
    if t["accumulated"]:
        kind = ("compounded" if "prod" in t["accumulated"] else
                "area, no floor" if not t["floor"] else "floored excess")
        print(f"    {v:28} base {str(t['baseline']):>4}  {kind}")
print(f"\n  combined model: frozen P3, no search")
print(f"  p5f-frozen: protected; a contradicting E result does not override it")
