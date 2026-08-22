# Greece Poverty Analysis — reproducible build
#
#   make verify      Check published headline numbers against pipeline outputs (fast, offline)
#   make fetch       Re-acquire formerly-orphaned raw inputs, CHECK mode (compares, writes nothing)
#   make fetch-write Re-acquire them for real, overwriting data/raw/ (moves the data vintage)
#   make build       Rerun the analysis pipeline over existing data/raw/, then verify
#   make reproduce   TRUE end-to-end test: fresh clone in a temp dir, fetch-write, build, verify.
#                    Leaves this working copy completely untouched.
#
# Default is `verify` because it is fast, offline, and answers the day-to-day
# question: do the published documents still match the data behind them?

# Prefer the pinned project environment when it exists. Command-line PY still
# overrides this, which is useful in CI or another clean environment.
PY ?= $(if $(wildcard .venv/bin/python),$(abspath .venv/bin/python),python3)
SCRIPTS := scripts

.DEFAULT_GOAL := verify
.PHONY: all verify fetch fetch-write build reproduce

# ---------------------------------------------------------------------------
# BUILD ORDER IS NOT FILENAME ORDER.
#
# 04_merge_all.py rebuilds analysis_dataset.csv from scratch every run. Two
# later-numbered scripts write derived columns BACK into that same file:
#   05_threshold_hypothesis.py -> gr_arop_threshold_real_idx2008
#   21_arope.py                -> gr_arope, eu_arope, gr_eu_arope_gap
# and 10_robustness_correlations.py READS gr_arope (it is one of the 19
# variables in the published correlation table).
#
# Running in plain numeric order therefore executes 10 before 21 and silently
# produces an 18-variable table instead of 19 — exactly the stale-output bug
# this project already hit once. The write-back scripts are hoisted to run
# immediately after 04, before any consumer.
# ---------------------------------------------------------------------------
STAGE_CORE     := 01_fetch_core.py 02_build_master_table.py 03_fetch_supplementary.py 04_merge_all.py
STAGE_WRITEBACK := 05_threshold_hypothesis.py 21_arope.py
STAGE_REST := $(filter-out $(STAGE_CORE) $(STAGE_WRITEBACK) 00_fetch_missing_raw.py, \
                $(notdir $(wildcard $(SCRIPTS)/[0-9][0-9]_*.py)))

# `verify` runs all three gates. The branch-rule tests are included because a
# test file nothing invokes is documentation, not enforcement -- and the P3
# branch bug (a default `else` returning the strongest conclusion) is exactly
# the class of error that a passing-but-unrun test suite fails to catch.
verify:
	cd $(SCRIPTS) && $(PY) test_branch_rule.py
	cd $(SCRIPTS) && $(PY) test_mundlak_rule.py
	cd $(SCRIPTS) && $(PY) test_ea_rule.py
	cd $(SCRIPTS) && $(PY) test_validate_outputs.py
	cd $(SCRIPTS) && $(PY) test_claim_containers.py
	cd $(SCRIPTS) && $(PY) audit_reported_outputs.py
	cd $(SCRIPTS) && $(PY) verify_build.py
	cd $(SCRIPTS) && $(PY) audit_parity.py
	cd $(SCRIPTS) && $(PY) 62_refresh_research_record.py
	$(PY) $(SCRIPTS)/65_record_figures.py
	$(PY) $(SCRIPTS)/66_build_record_html.py

# Strict gate for shipping V2. Everything `verify` runs, plus: no pending V2
# claim, no unfilled required document slot, no undecided disposition. A green
# `make verify` must never be mistaken for a shippable release.
# Atomic acceptance for the V2 technical report. Separate from `verify` because
# it gates one deliverable, not the whole build -- but it IS enforced: it runs
# inside release-verify, so an incomplete report cannot ship.
verify-report-v2:
	$(PY) $(SCRIPTS)/verify_report_v2.py

release-verify:
	cd $(SCRIPTS) && $(PY) test_branch_rule.py
	cd $(SCRIPTS) && $(PY) test_mundlak_rule.py
	cd $(SCRIPTS) && $(PY) test_ea_rule.py
	cd $(SCRIPTS) && $(PY) test_validate_outputs.py
	cd $(SCRIPTS) && $(PY) test_claim_containers.py
	cd $(SCRIPTS) && $(PY) audit_reported_outputs.py
	cd $(SCRIPTS) && $(PY) verify_build.py
	cd $(SCRIPTS) && $(PY) audit_parity.py --release
	$(PY) $(SCRIPTS)/verify_report_v2.py
	@echo "RELEASE VERIFICATION PASSED"

fetch:
	cd $(SCRIPTS) && $(PY) 00_fetch_missing_raw.py

fetch-write:
	cd $(SCRIPTS) && $(PY) 00_fetch_missing_raw.py --write

build:
	@cd $(SCRIPTS) && set -e; \
	for s in $(STAGE_CORE) $(STAGE_WRITEBACK) $(sort $(STAGE_REST)); do \
	  echo "=== $$s ==="; $(PY) $$s > /dev/null || { echo "FAILED: $$s"; exit 1; }; \
	done; \
	echo "=== 09_export_report_data.py (final export) ==="; $(PY) 09_export_report_data.py; \
	echo "=== inject_data.py ==="; $(PY) inject_data.py
	@$(MAKE) --no-print-directory verify

# True from-scratch reproduction, isolated from this working copy: exports the
# committed tree into a temp dir, re-fetches raw inputs there for real, builds,
# and verifies. Nothing here is modified, so a failure is diagnostic rather than
# destructive.
reproduce:
	@set -e; \
	D=$$(mktemp -d -t greece-repro-XXXXXX); \
	echo "Isolated reproduction in $$D"; \
	git archive HEAD | tar -x -C $$D; \
	$(MAKE) -C $$D PY="$(abspath $(PY))" fetch-write; \
	$(MAKE) -C $$D PY="$(abspath $(PY))" build; \
	echo ""; \
	echo "Isolated reproduction succeeded. Artifacts left in $$D for inspection."; \
	echo "(This working copy was not modified.)"

all: fetch build
