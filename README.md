# FUND-IT — reproducibility artifacts

Reproducibility bundle for *"Concentration at the Top, Development at the Base: A Convergent
Mixed-Methods Study of Federal Research Funding in Clinical Departments and Veterans Affairs
Medical Centers"* (Pietrobon, Machiavelli, Teixeira, Kuo). USF IRB Study 009006.

The submitted draft described its analysis in prose and pinned its software versions, but
shipped no code and no data. This repository supplies both, and audits which reported numbers
regenerate and which do not.

## Two tracks, deliberately kept separate

The repository holds two independent checks built by two parallel working sessions. They ask
different questions and it is worth keeping both.

| Track | Question | Entry point | Result |
|---|---|---|---|
| **Conformance** | Is the manuscript internally consistent with the data it was written from? | `src/reproduce.py` | 79 checks, all pass |
| **Source verification** | Does that data match the public record at NIH RePORTER? | `scripts/01_site_profiles.py` | 15 of 15 site totals and shares match; **3 of 5 growth ratios do not** |

A number can pass conformance and fail source verification — three do. That gap is the
substance of **[REPRODUCIBILITY.md](REPRODUCIBILITY.md)**, finding R-3, and it is the reason
`src/reproduce.py` has not been edited to "fix" the three assertions: it is supposed to encode
the manuscript as published, so that the divergence stays visible.

**Read [REPRODUCIBILITY.md](REPRODUCIBILITY.md) first.** Seven findings, one of which changes
a reported result.

## Layout

```
src/reproduce.py        conformance track: 79 assertions against the published values
scripts/
  reporter_client.py    NIH RePORTER API v2 client; the VA-administered award filter
  01_site_profiles.py   site profiles regenerated from the live public source
  02_concentration.py   concentration statistics; asserts all 25 values
  03_h1_audit.py        Strand 1 audit; asserts 22 aggregates, documents what is missing
data/*.csv              derived tables behind the published numbers (conformance track)
data/derived/*.json     the same data as extracted (source-verification track)
data/references_pubmed_verified.json   42 PubMed-verified references, none retracted
figures/                Figure 1, Lorenz curves for awards and dollars
qualitative/            interview guide domains, codebook, joint display, data availability
docs/PROVENANCE.md      extraction path for the CSVs
data/derived/PROVENANCE.md   per-file status: verified, superseded, or terminal
```

## Run

```bash
conda env create -f environment.yml && conda activate fund-it
bash run_all.sh
```

Everything except `scripts/01_site_profiles.py` runs offline. That one queries
`api.reporter.nih.gov` and prints a per-site comparison against the manuscript.

## What reproduces

- All 25 concentration statistics for VA awards and NIH dollars, exactly.
- All 15 site award totals and activity-code shares — verified against the live public source,
  not only against the project's own derived files.
- All 22 aggregates describing the Strand 1 cross-correlation table.
- 42 references, all PubMed-verified, none retracted.

## What does not

- The Strand 1 cross-correlations themselves — no per-department annual series survive (R-4).
- Three of five site growth ratios, for a documented reason that is a real defect (R-3).
- Rank mobility and the percentile ranks (R-5).
- The qualitative strand, which cannot be deposited under the approved protocol (R-7).

See [COORDINATION.md](COORDINATION.md) and [MANIFEST.md](MANIFEST.md) before pushing.
