# Provenance and known limitations

## Chain of custody

1. **Upstream source.** NIH RePORTER / ExPORTER bulk files, https://reporter.nih.gov. The bulk
   files were used rather than the RePORTER web export, which caps a single download at
   approximately 15,000 records, omits the tables linking projects to investigators, and
   truncates narrative fields.
2. **Primary extraction.** Performed by the study team and recorded in the FUND-IT analysis
   documents (the VA funding master document, the per-site reports, and the hypothesis 1
   results document).
3. **Derived files in `data/`.** Parsed directly from those documents, then independently
   recomputed. Where a published figure and the recomputation differ, the recomputation is
   reported in the manuscript and the difference is noted below.

## Recomputation against the original analysis

| Quantity | Original document | Recomputed here | Status |
|---|---|---|---|
| Gini, VA-administered awards, non-umbrella | 0.53 | 0.524 | agrees to the reported precision |
| Top 10 organization share | about 40% | 40.3% | agrees |
| Organizations holding 80% of awards | about 30 | 29 | agrees |
| Organizations holding 90% of awards | about 40 | 38 | agrees |

## Known limitations of the extraction

1. **No dollar amounts for VA-administered awards.** RePORTER reports no funding amount when the
   administering agency is Veterans Affairs. Dollar concentration is therefore computable only
   for NIH-administered awards held by VA-affiliated organizations.
2. **Two misclassified entities.** `VA DIVISION CONSOLIDATED LAB SRVS` and
   `VA ST DEPT AGRICULTURE AND CONSUMER SRVS` are Virginia state agencies that entered a
   VA-affiliated organization list through matching on the string `VA`. Both are retained in the
   raw file and excluded in the corrected analysis; `reproduce.py` checks both versions.
3. **Umbrella records.** Five catch-all organization records aggregate activity across sites and
   are excluded from concentration analysis. They are listed in `reproduce.py` and in
   Supplemental Digital Appendix 1.
4. **Junior investigator definition.** A junior PI is an investigator whose first appearance as a
   PI falls in a later year. This conflates newly hired faculty with existing faculty who are
   newly funded, and the manuscript says so.
5. **Varying denominators.** Per-site national ranks in the original site reports were computed
   against denominators ranging from 73 to 117 facilities depending on the activity filter
   applied. Percentile ranks should be read as approximate.
6. **An unresolved discrepancy in a non-manuscript document.** The project's recruitment one-pager
   states that five nonprofit corporations, including Ocean State Research Institute and Albany
   Research Institute, together received over $130 million in NIH funding in fiscal years 2020 to
   2024. Neither organization appears in the NIH-administered extraction in
   `data/va_affiliated_nih_fy2020_2024.csv`, whose five largest recipients total $106.5 million
   as extracted and $82.1% of $129.7 million after correction. The one-pager figure is not used
   anywhere in the manuscript.

## Reference integrity

All 42 references were retrieved from PubMed, carry a DOI where PubMed holds one (40 of 42), and
were checked for retraction status. Three references carried in an earlier draft of this study
could not be resolved in PubMed by structured citation lookup or by title and author search, and
were removed rather than reused:

- Basson MD, Langer JC. JAMA. 2021;326(11):1081-2.
- Levine AS. Acad Med. 2018;93(4):490-4.
- Dimick JB, Greenberg CC. JAMA Surg. 2013;148(2):171-2.
