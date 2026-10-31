# Provenance of the derived datasets

These five files are the inputs behind the manuscript's tables. **Their own provenance is
incomplete, and that is itself an audit finding.** They were reconstructed from the tables
carried in the project's Google Drive analysis documents (the VA master reports, the
per-site reports and the hypothesis-1 results document), not emitted by a logged pipeline
run. The original ExPORTER extraction code was not archived with the project.

| File | Contents | Chain to public source |
|---|---|---|
| `va_org_awards_fy2020_2024.json` | 76 VA organizations with FY2020–2024 award counts | Not independently re-verified against RePORTER; all 14 derived statistics are internally consistent with the manuscript |
| `npc_nih_awards_fy2020_2024.json` | 22 VA-affiliated organizations: award counts and NIH dollars | As above, 11 statistics |
| `site_awards_by_year.json` | FY-by-FY award counts for the five interviewed sites | **Superseded** — mixes facility and nonprofit awards, and the Pacific Islands series includes FY2010. Use `scripts/01_site_profiles.py` instead. Retained because it is the series the manuscript's growth ratios were computed on (see REPRODUCIBILITY.md R-3) |
| `site_activity_codes.json` | Activity-code breakdown per site, facility and nonprofit rows | **Verified**: facility rows (`I`-prefixed codes) reproduce exactly against the live RePORTER API for all five sites |
| `h1_crosscorrelation_table.json` | 26 departments: junior/senior PI counts, peak lag, peak *r* | **Terminal** — these are reported results, not regenerable outputs (REPRODUCIBILITY.md R-4) |

## Recommended replacement

`scripts/01_site_profiles.py` fetches the site data directly from
`api.reporter.nih.gov/v2/projects/search`, with the exact organization-name strings and the
VA-administered filter pinned in code. That path was verified on 2026-10-31 and is the one
to cite in a data availability statement. The two files marked superseded or terminal above
should be regenerated from a logged extraction before the manuscript is resubmitted.
