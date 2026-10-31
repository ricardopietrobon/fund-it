#!/usr/bin/env bash
# Run both tracks: conformance against the manuscript, then verification against the source.
set -euo pipefail
cd "$(dirname "$0")"

echo "############ CONFORMANCE TRACK ############"
echo "Is the manuscript internally consistent with the data it was written from?"
echo
python src/reproduce.py

echo
echo "############ SOURCE VERIFICATION TRACK ############"
echo
echo "== Concentration statistics (offline, asserts all 25 values) =="
python scripts/02_concentration.py

echo
echo "== Strand 1 cross-correlation audit (offline, asserts all aggregates) =="
python scripts/03_h1_audit.py

echo
echo "== Five sites, regenerated from the live NIH RePORTER API =="
python scripts/01_site_profiles.py

echo
echo "Outputs in outputs/. The three growth-ratio divergences above are expected and"
echo "documented: see REPRODUCIBILITY.md finding R-3."
