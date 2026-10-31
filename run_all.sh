#!/usr/bin/env bash
# Regenerate every reproducible quantity in the manuscript and check it against the draft.
set -euo pipefail
cd "$(dirname "$0")"

echo "== Strand 2: concentration (offline, asserts all values) =="
python scripts/02_concentration.py

echo
echo "== Strand 1: cross-correlation audit (offline, asserts all aggregates) =="
python scripts/03_h1_audit.py

echo
echo "== Table 4: five sites, regenerated from the live NIH RePORTER API =="
python scripts/01_site_profiles.py

echo
echo "Outputs written to outputs/. See REPRODUCIBILITY.md for the three known discrepancies."
