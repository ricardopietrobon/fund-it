# Reproducibility audit and bundle

Manuscript: *"Concentration at the Top, Development at the Base: A Convergent Mixed-Methods
Study of Federal Research Funding in Clinical Departments and Veterans Affairs Medical
Centers"* (Pietrobon, Machiavelli, Teixeira, Kuo). Audit performed 2026-10-31.

The manuscript's Method section describes a complete analysis pipeline and its Software
section pins Python 3.11.15, NumPy 2.4.6 and pandas 2.3.3 — but no code, no extraction
script and no derived dataset accompanied the draft. Every number was carried as prose.
This repository supplies what was missing and records, honestly, what still cannot be
regenerated.

**On table numbers.** This audit was written against the draft that carried five tables. The
manuscript has since moved to version 5, which carries four tables plus Figure 1 to fit
Academic Medicine's five-display-item limit, and the rank-mobility table became Supplemental
Digital Appendix 3. Where a table number below is ambiguous, the content is named too; the
findings are about quantities, not positions.

**On the two tracks.** `src/reproduce.py` checks the manuscript against the data it was
written from and passes 79 of 79. The findings below come from checking that data against the
public record, which is a different question. Both are kept; see README.md.

## Summary

| Strand | Reported quantities | Status |
|---|---|---|
| Strand 2 — VA award concentration (Results ¶2, Table 2) | 14 statistics | **Fully reproduced** from derived data (`scripts/02_concentration.py`) |
| Strand 2 — NIH dollar concentration (Results ¶3) | 11 statistics | **Fully reproduced** (`scripts/02_concentration.py`) |
| Table 4 — five interviewed sites, award totals and activity-code shares | 15 values | **Fully reproduced from the public source** via the RePORTER API (`scripts/01_site_profiles.py`) |
| Table 4 — five interviewed sites, growth ratios | 5 values | **2 of 5 reproduce**; 3 diverge — see R-3 |
| Strand 1 — senior-to-junior cross-correlation (Table 1) | 22 (lag, *r*) pairs | **Not reproducible** — see R-4 |
| Table 3 — rank mobility, and national percentile ranks | all | **Not reproducible** — see R-5 |
| Qualitative strand | 5 interviews | **Not shareable** by IRB protocol — see R-7 |

Running `bash run_all.sh` executes all three scripts. Scripts 02 and 03 assert every
value against the manuscript and exit non-zero on any mismatch; script 01 queries the
live RePORTER API and prints a per-site comparison.

---

## R-1 — Organization names are exact-match strings and were never pinned

RePORTER's `org_names` criterion is an exact string match. Two of the five interviewed
sites cannot be retrieved using the names carried in the project's own data files:

- The project data and the manuscript identify the Hawaii site as
  **`VA PACIFIC ISLANDS HEALTHCARE SYSTEM`**. That string returns **zero records**.
  The string in RePORTER is **`VA PACIFIC ISLANDS HEALTH CARE SYSTEM`** — "HEALTH CARE"
  as two words. A pipeline built on the first string would silently report a site with
  no awards rather than raising an error.
- The **Gainesville** facility's awards are filed under the generic umbrella name
  `VETERANS HEALTH ADMINISTRATION` and are separable only by adding `org_cities=["GAINESVILLE"]`.
  The manuscript's limitations paragraph notes that "VA facility records are split across
  city-level Veterans Health Administration entries"; it does not state the filter used
  to resolve them.

The exact strings and filters are now pinned in `scripts/01_site_profiles.py`.

## R-2 — The facility / nonprofit split rule was undocumented

Each site's record set mixes awards administered by the VA facility with awards held by
its affiliated nonprofit corporation (NPC). The manuscript reports portfolio shares on the
facility only, but the Method never states the rule that separates them.

The rule is recoverable and is now explicit in `reporter_client.va_administered()`: VA
activity codes all begin with `I` (I01, IK1, IK2, IK6, I21, I50, IS1, IP1); NPC awards
carry NIH codes (R01, R21, U10, UG3, N01, RF1, UF1). Applying it reproduces all five
sites' award totals and I01 / career-development shares exactly against the live source.

Applying the naive aggregation instead — counting every record returned for a site —
changes Lexington from 131 awards to 140, Minneapolis from 419 to 420, and VA Pacific
Islands from 7 to 25, and moves Pacific Islands' I01 share from 85.7% to 24.0%.

## R-3 — Table 4 uses inconsistent denominators across its own columns

This is the one finding that changes a reported result.

The activity-code share columns are computed facility-only (R-2). The growth-ratio column
is not. Recomputing growth facility-only from the public source:

| Site | Reported growth | Reported series | Facility-only growth | Facility-only series |
|---|---|---|---|---|
| Bedford | 2.79 | 71 → 198 | **2.79** | 71 → 198 |
| Gainesville | 1.08 | 142 → 154 | **1.08** | 142 → 154 |
| Minneapolis | 1.46 | 171 → 249 | **1.45** | 171 → 248 |
| Lexington | 1.26 | 62 → 78 | **1.30** | 57 → 74 |
| VA Pacific Islands | 0.58 | 12 → 7 | **2.50** | 2 → 5 |

- **Lexington**: the reported series sums to 140, which is the facility total (131) plus
  the nine R01 awards held by Lexington Biomedical Research Institute. The growth ratio
  therefore counts NPC awards that the same row's percentage columns exclude. Facility-only
  growth is 1.30.
- **Minneapolis**: a single award differs in fiscal-year assignment (248 vs 249).
- **VA Pacific Islands**: the reported series sums to 19, against a reported award total of
  7 in the same table row. The 12 → 7 series comes from a facility+NPC series that also
  includes FY2010, a year outside the stated FY2011–2024 window. On facility-only data the
  site has 7 awards across 14 years (FY2011, FY2015, FY2021×2, FY2022, FY2023, FY2024) and
  the ratio is 5/2 = 2.50 — **the direction of the reported change reverses**.

The manuscript uses Pacific Islands as the declining site, and the Discussion leans on it:
"the fastest-growing site held the second-highest share ... and the site in decline held
none." That sentence rests on the 0.58 ratio. The manuscript already declines to compare
Pacific Islands' percentages because they rest on 7 awards; the same reasoning applies with
more force to a growth ratio computed on 2 early awards, and the consistent fix is to
report no growth ratio for that site rather than a ratio from a differently-constructed
series.

## R-4 — Strand 1 cross-correlations cannot be recomputed

`data/derived/h1_crosscorrelation_table.json` holds the final `(department, junior, senior,
lag, r)` rows. Every aggregate the manuscript states about that table reproduces from it
(`scripts/03_h1_audit.py` checks 22 of them, including the 56,581 / 8,971 PI counts, the
6.3:1 ratio, 19 of 22 negative lags, the −0.142 to 0.594 range and the 0.379 median).

The correlations themselves are inputs to that audit, not outputs. Recomputing them needs
the per-department annual senior and junior PI count series, which exist nowhere in the
project. Four further specification gaps would block an independent re-run even with the
ExPORTER files in hand:

1. **PI disambiguation.** Senior PI is "the top decile of cumulative total cost" summed
   "for each principal investigator". ExPORTER carries PI names as strings and a separate
   profile identifier; which was used, and how multi-PI awards divide total cost between
   investigators, is unstated. This choice alone can move the senior decile substantially.
2. **Department classification.** "The standardized departmental classification carried in
   the project file" is not named as a field, and the 26 categories are not listed. The
   crosswalk is recoverable from the table's `dept` values and is reproduced in
   `data/derived/h1_crosscorrelation_table.json`, but the mapping from raw values to those
   26 categories is not.
3. **Cross-correlation convention.** Lags −5 to +5 on annual counts, but not whether the
   series were detrended or differenced before correlating, nor how the 14-year series is
   truncated at each lag. On a 14-point series a lag-5 correlation uses 9 points; left raw,
   these correlations are dominated by the shared secular funding trend. The manuscript's
   own Discussion concedes the analysis "is unadjusted for ... secular funding trends".
4. **Window.** Strand 1's fiscal-year window is not stated separately from Strand 2's.

Until the series are regenerated, Table 1 should be read as a reported result, not a
verified one.

## R-5 — Rank mobility and percentile ranks are not reproducible as specified

The rank-mobility table — the former Table 3, now Supplemental Digital Appendix 3 — reports
rank changes that require organization rankings computed separately for FY2020 and FY2024.
The available data is a single FY2020–2024 aggregate, so no rank change can be recovered from
it. Moving the table to an appendix does not change this: an appendix carries the same
evidentiary weight as a table for a reader trying to check it.

The national percentile ranks in Table 4 (25th of 116, 33rd, 34th, 51st, 100th) are
unreproducible by the manuscript's own account: "our per-site denominators varied between
73 and 117 facilities depending on the activity filter applied, so percentile ranks should
be read as approximate." A reproducible version requires the activity filter and the
facility universe to be fixed and stated.

## R-6 — Environment is now pinned

`environment.yml` reproduces the stated stack. Note that the manuscript's Software section
pins NumPy 2.4.6; that version postdates the analysis conventions used here only in
irrelevant respects, and all statistics in `02_concentration.py` use operations whose
behaviour is stable across NumPy 1.26–2.x.

## R-7 — Qualitative strand: not shareable, and the remedy

Interview recordings are deleted after transcription under the approved protocol
(USF IRB Study 009006), and the manuscript's data availability statement notes that
participating facilities are identifiable from their funding profiles. Neither transcripts
nor structured summaries can be deposited.

What can and should be deposited instead, and is in `qualitative/`: the eight interview
guide domains, the deductive-plus-inductive codebook, and the joint-display construction
rule. Two limitations already stated in the manuscript — single coder, no member checking,
saturation not reached — are not remediable by any artifact and remain limitations.

## Incidental prose defect

Results ¶2 reads "a distribution in which the mean exceeds the third of the median"
(mean 126.6, median 74.0, Q3 207.5). The sentence is garbled; the intended comparison
appears to be that the mean (126.6) exceeds the median (74.0) by roughly 70%, which is the
signature of right skew. Flagged here because it was found during numeric verification.
