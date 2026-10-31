# FUND-IT — reproducibility artifacts

Reproducibility bundle for *"Concentration at the Top, Development at the Base: A Convergent
Mixed-Methods Study of Federal Research Funding in Clinical Departments and Veterans Affairs
Medical Centers"* (Pietrobon, Machiavelli, Teixeira, Kuo). USF IRB Study 009006.

The submitted draft described its analysis in prose and pinned its software versions, but
shipped no code and no data. This repository supplies the code, the derived datasets, and an
explicit audit of which reported numbers regenerate and which do not.

## Start here

**[REPRODUCIBILITY.md](REPRODUCIBILITY.md)** — the audit. Seven findings, one of which
(R-3) changes a reported result.

## Layout

```
scripts/
  reporter_client.py      NIH RePORTER API v2 client; the VA-administered award filter
  01_site_profiles.py     Table 4 regenerated from the live public source
  02_concentration.py     Strand 2 concentration statistics; asserts all 25 values
  03_h1_audit.py          Strand 1 audit; asserts 22 aggregates, documents what is missing
data/derived/             the five datasets behind the reported tables (see PROVENANCE.md)
qualitative/              interview guide domains, codebook, joint display, data availability
outputs/                  written by the scripts
```

## Run

```bash
conda env create -f environment.yml && conda activate fund-it
bash run_all.sh
```

`02` and `03` need no network and exit non-zero if any manuscript value fails to reproduce.
`01` queries `api.reporter.nih.gov` and prints a per-site comparison against the manuscript.

## What reproduces

- All 25 Strand 2 concentration statistics, exactly.
- All 15 Table 4 award totals and activity-code shares, verified against the live public
  source rather than only against the project's own derived files.
- All 22 Strand 1 aggregates that describe the cross-correlation table.

## What does not

- The Strand 1 cross-correlations themselves (no per-department annual series survive).
- Three of five site growth ratios, for a documented reason that is a real defect (R-3).
- Table 3 rank mobility and the Table 4 percentile ranks.
- The qualitative strand, which cannot be deposited under the approved protocol.

See [COORDINATION.md](COORDINATION.md) before pushing to this repository.
