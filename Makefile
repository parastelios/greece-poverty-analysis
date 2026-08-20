# Greece Poverty Analysis — reproducible build
#
# Targets:
#   make verify   Check that published headline numbers match pipeline outputs (fast, no network)
#   make fetch    Re-acquire the formerly-orphaned raw inputs (CHECK mode: compares, writes nothing)
#   make build    Full pipeline rerun from data/raw/ through the published report (network required)
#   make all      fetch (check) -> build -> verify
#
# Default is `verify` because it is fast, offline, and answers the question that
# matters most day to day: do the documents still match the data?

PY := python3
SCRIPTS := scripts

.DEFAULT_GOAL := verify
.PHONY: all verify fetch fetch-write build clean-check

verify:
	cd $(SCRIPTS) && $(PY) verify_build.py

fetch:
	cd $(SCRIPTS) && $(PY) 00_fetch_missing_raw.py

fetch-write:
	cd $(SCRIPTS) && $(PY) 00_fetch_missing_raw.py --write

# Ordered rerun. Scripts are numbered in dependency order; 04 must be followed by
# every write-back script (05, 21), which running in full numeric order guarantees.
# 09 + inject_data are re-run at the end so the published report picks up any change.
build:
	cd $(SCRIPTS) && set -e; \
	for s in $$(ls [0-9][0-9]_*.py | sort); do \
	  echo "=== $$s ==="; $(PY) $$s || exit 1; \
	done; \
	echo "=== 09_export_report_data.py (final) ==="; $(PY) 09_export_report_data.py; \
	echo "=== inject_data.py ==="; $(PY) inject_data.py
	$(MAKE) verify

all: fetch build
