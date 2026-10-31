# Manifest and coordination

This repository is written to by more than one working session. To avoid two sessions
overwriting each other, follow these rules.

## Rules

1. **Check before you write.** Read this file and `git log` before adding anything. If a track
   below is already claimed and dated, do not rewrite its files; open a branch or add a new
   track.
2. **One track, one directory.** A track owns its paths. Shared paths are `README.md` and this
   file, and both are append-only in practice: add your track, do not rewrite someone else's.
3. **Record what you did.** Add a row to the track table in the same commit as the work.

## Tracks

| Track | Owns | Status | Date |
|---|---|---|---|
| Conformance (session f1621013) | `src/reproduce.py`, `data/*.csv`, `data/references_pubmed_verified.json`, `figures/*`, `docs/PROVENANCE.md` | complete, 79 checks passing | 2026-10-31 |
| Source verification (session 74e37c7b) | `scripts/*`, `data/derived/*`, `qualitative/*`, `REPRODUCIBILITY.md`, `COORDINATION.md`, `environment.yml`, `run_all.sh` | complete; 3 documented divergences from the published growth ratios | 2026-10-31 |

The two tracks ask different questions and are both kept. Conformance checks the manuscript
against the data it was written from; source verification checks that data against NIH
RePORTER. See README.md and REPRODUCIBILITY.md R-3 for the three numbers where they disagree.

## Verifying the repository is intact

```bash
bash run_all.sh           # both tracks
python src/reproduce.py   # conformance only; exit 0 means every published number still reproduces
```

Run this after any merge. A failing check in `src/reproduce.py` means a data file and the
manuscript have diverged, and the divergence should be resolved before anything else is added.

The three growth-ratio divergences that `scripts/01_site_profiles.py` reports are **expected**
and documented (REPRODUCIBILITY.md R-3). They are not a merge failure, and `src/reproduce.py`
must not be edited to hide them.
