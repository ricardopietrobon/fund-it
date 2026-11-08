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
| Conformance (session f1621013) | `src/reproduce.py`, `data/*.csv`, `data/references_pubmed_verified.json`, `figures/*`, `docs/PROVENANCE.md` | complete, 116 checks passing; synced to manuscript v6 on 2026-11-05 | 2026-11-05 |
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

The three growth-ratio divergences R-3 reported were **resolved on 2026-11-05**: the manuscript
adopted the facility-only values and `src/reproduce.py` was updated in step, as R-3 required.
See "R-3 resolved" at the end of REPRODUCIBILITY.md. `scripts/01_site_profiles.py` should now
agree with the published values; a fresh divergence is a real finding, not an expected one, and
`src/reproduce.py` must still never be edited to hide one.

## Hypothesis 3 added, 2026-11-09

The topic model that tests hypothesis 3 (topical depth versus breadth) is now in the
conformance track:

| File | What it is |
|---|---|
| `scripts/05_fetch_abstracts.py` | pulls project titles and abstracts for the 26 department categories, FY2020-2024, from the NIH RePORTER v2 API |
| `scripts/04_h3_topic_model.py` | fits the LDA, tunes the topic number on perplexity and UMass coherence, and writes the four derived files below |
| `data/h3_tuning.csv` | the 7 candidate topic numbers with perplexity, coherence and the combined score |
| `data/h3_topics.csv` | the 40 topics with their 12 highest-probability terms |
| `data/h3_dept_specialization.csv` | per-department entropy, HHI, projects, PIs and funding |
| `data/h3_results.json` | every test statistic quoted in the Results |

`src/reproduce.py` now runs 116 checks, up from 86. Two of the new ones exist specifically to
stop a retracted claim from returning: manuscript v13 briefly stated that the three broadest
topic portfolios were the three largest departments. They are not, and psychiatry, the third
largest by award count, is among the narrowest. The checks assert both facts.
