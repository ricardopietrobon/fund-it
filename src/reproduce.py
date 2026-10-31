"""
Reproduce every quantitative claim in:

  Pietrobon R, Machiavelli A, Teixeira L, Kuo PC.
  Concentration at the Top, Development at the Base: A Convergent Mixed-Methods Study of
  Federal Research Funding in Clinical Departments and Veterans Affairs Medical Centers.

Run:  python src/reproduce.py
Exit code 0 means every published number was regenerated from data/ and matched.

The derived CSVs in data/ were extracted from the FUND-IT RePORTER analysis documents.
The upstream source is the public NIH RePORTER/ExPORTER bulk files (https://reporter.nih.gov);
see docs/PROVENANCE.md for the extraction path and its known limitations.

ROLE OF THIS SCRIPT, AND WHY IT IS NOT "FIXED"
----------------------------------------------
This is the CONFORMANCE track: it asks whether the manuscript is internally consistent with
the data it was written from. It is not a check that the data is right.

Independent verification against the live NIH RePORTER API (scripts/01_site_profiles.py)
reproduces all five sites' award totals and activity-code shares exactly, but shows that
three growth ratios asserted below were computed on a different award universe than the
percentage columns in the same table rows:

    site                 asserted here   facility-only from source
    Lexington            1.26 (62->78)   1.30 (57->74)
    Minneapolis          1.46 (171->249) 1.45 (171->248)
    VA Pacific Islands   0.58 (12->7)    2.50 (2->5)   <- direction reverses

The assertions are left exactly as they are on purpose. They encode the manuscript AS
PUBLISHED, which is what makes the divergence visible. Do not edit them to make the
discrepancy go away; if the manuscript is corrected, update these values and
REPRODUCIBILITY.md finding R-3 in the same commit.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
FAIL = []


def check(label, got, want, tol=0.0005):
    ok = abs(got - want) <= tol if isinstance(want, float) else got == want
    print(f"{'PASS' if ok else 'FAIL'} | {label:62s} got={got!r:>22} published={want!r}")
    if not ok:
        FAIL.append(label)


def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    return float(2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum()) - (n + 1) / n)


UMBRELLA = {
    "VETERANS HEALTH ADMINISTRATION",
    "VA MEDICAL CENTER",
    "VETERANS AFFAIRS UNITED STATES DEPARTMENT OF",
    "U S DEPT VETS AFFAIRS MEDICAL CENTER",
    "VA VETERANS ADMINISTRATION HOSPITAL",
}
VIRGINIA_STATE = {
    "VA DIVISION CONSOLIDATED LAB SRVS",
    "VA ST DEPT AGRICULTURE AND CONSUMER SRVS",
}


def strand1():
    print("\n--- Table 1 / Results: senior and junior principal investigators ---")
    d = pd.read_csv(DATA / "departments_senior_junior.csv")
    check("department categories", len(d), 26)
    check("total junior PI records", int(d.junior_pis.sum()), 56581)
    check("total senior PI records", int(d.senior_pis.sum()), 8971)
    check("junior:senior ratio", round(d.junior_pis.sum() / d.senior_pis.sum(), 1), 6.3)
    a = d.dropna(subset=["peak_correlation"])
    a = a[a.junior_pis > 0]
    check("departments with computable series", len(a), 22)
    check("peak lag negative", int((a.peak_lag_years < 0).sum()), 19)
    check("peak lag zero", int((a.peak_lag_years == 0).sum()), 3)
    check("min peak correlation", round(a.peak_correlation.min(), 3), -0.142)
    check("max peak correlation", round(a.peak_correlation.max(), 3), 0.594)
    # median of an even-numbered set: mean of the 11th and 12th values, 0.378 and 0.379.
    # The text rounds 0.3785 to 0.379; the check is against the unrounded value.
    check("median peak correlation (unrounded)", round(float(a.peak_correlation.median()), 4), 0.3785)
    check("departments with r >= 0.40", int((a.peak_correlation >= 0.40).sum()), 9)
    s = d[d.department == "SURGERY"].iloc[0]
    check("surgery peak correlation", round(float(s.peak_correlation), 3), 0.420)
    check("surgery peak lag", int(s.peak_lag_years), -5)
    check("surgery junior PIs", int(s.junior_pis), 2368)
    check("surgery senior PIs", int(s.senior_pis), 301)


def strand2_awards():
    print("\n--- Table 2 Panel A / Figure 1: VA-administered award concentration ---")
    d = pd.read_csv(DATA / "va_organizations_fy2020_2024.csv")
    check("organizations, all", len(d), 76)
    check("awards, all", int(d.awards_fy2020_2024.sum()), 10608)
    nu = d[~d.organization.isin(UMBRELLA)]
    v = np.sort(nu.awards_fy2020_2024.values)[::-1]
    tot = v.sum()
    check("organizations, non-umbrella", len(nu), 71)
    check("awards, non-umbrella", int(tot), 8991)
    check("top 10 share, %", round(100 * v[:10].sum() / tot, 1), 40.3)
    check("Gini, non-umbrella", round(gini(v), 3), 0.524)
    check("Gini, all organizations", round(gini(d.awards_fy2020_2024.values), 3), 0.571)
    cum = np.cumsum(v) / tot
    check("organizations for 80% of awards", int(np.searchsorted(cum, 0.80) + 1), 29)
    check("organizations for 90% of awards", int(np.searchsorted(cum, 0.90) + 1), 38)
    check("median awards per organization", float(np.median(v)), 74.0)
    check("Q1 awards per organization", float(np.percentile(v, 25)), 24.5)
    check("Q3 awards per organization", float(np.percentile(v, 75)), 207.5)
    check("mean awards per organization", round(float(np.mean(v)), 1), 126.6)
    top = nu.sort_values("awards_fy2020_2024", ascending=False)
    check("largest organization awards (San Diego)", int(top.iloc[0].awards_fy2020_2024), 495)
    check("second largest (Boston)", int(top.iloc[1].awards_fy2020_2024), 422)
    check("third largest (Palo Alto)", int(top.iloc[2].awards_fy2020_2024), 393)


def strand2_dollars():
    print("\n--- Table 2 Panel B / Figure 1: NIH dollars to VA-affiliated organizations ---")
    d = pd.read_csv(DATA / "va_affiliated_nih_fy2020_2024.csv")
    check("organizations as extracted", len(d), 22)
    check("awards as extracted", int(d.nih_awards.sum()), 368)
    check("dollars as extracted", int(d.nih_dollars.sum()), 143723164)
    c = d[~d.organization.isin(VIRGINIA_STATE)]
    o = c.sort_values("nih_dollars", ascending=False)
    check("organizations corrected", len(c), 20)
    check("awards corrected", int(c.nih_awards.sum()), 319)
    check("dollars corrected", int(c.nih_dollars.sum()), 129711431)
    check("top 3 dollar share, %", round(100 * o.nih_dollars[:3].sum() / c.nih_dollars.sum(), 1), 72.5)
    check("top 5 dollar share, %", round(100 * o.nih_dollars[:5].sum() / c.nih_dollars.sum(), 1), 82.1)
    check("Gini dollars corrected", round(gini(c.nih_dollars.values), 3), 0.724)
    check("Gini awards corrected", round(gini(c.nih_awards.values), 3), 0.656)
    check("Palo Alto NIH dollars", int(o.iloc[0].nih_dollars), 53670124)


def sites():
    print("\n--- Table 3 / Table 4: the 5 interviewed sites ---")
    s = pd.read_csv(DATA / "site_award_series.csv")
    expect = {"Bedford (Edith Nourse Rogers Memorial Veterans Hospital)": (71, 198, 2.79, 36),
              "Minneapolis VA Health Care System": (171, 249, 1.46, 43),
              "Lexington VA Health Care System": (62, 78, 1.26, None),
              "Gainesville (Malcolm Randall VA Medical Center)": (142, 154, 1.08, None),
              "VA Pacific Islands Health Care System": (12, 7, 0.58, None)}
    for site, (e_early, e_late, e_ratio, e_peak) in expect.items():
        d = s[s.site == site]
        early = int(d[(d.fiscal_year >= 2011) & (d.fiscal_year <= 2017)].awards.sum())
        late = int(d[(d.fiscal_year >= 2018) & (d.fiscal_year <= 2024)].awards.sum())
        check(f"{site[:34]} FY2011-2017", early, e_early)
        check(f"{site[:34]} FY2018-2024", late, e_late)
        check(f"{site[:34]} growth ratio", round(late / early, 2), e_ratio)
        if e_peak is not None:
            check(f"{site[:34]} 2024 awards", int(d[d.fiscal_year == 2024].awards.sum()), e_peak)

    a = pd.read_csv(DATA / "site_activity_codes.csv")
    va = a[a.activity_code.str.startswith("I")]
    shares = {}
    for site, g in va.groupby("site"):
        tot = g.awards.sum()
        shares[site] = {
            "I01": round(100 * g[g.activity_code == "I01"].awards.sum() / tot, 1),
            "CD": round(100 * g[g.activity_code.isin(["IK1", "IK2"])].awards.sum() / tot, 1),
        }
    exp = {"Bedford (Edith Nourse Rogers Memorial Veterans Hospital)": (56.9, 17.5),
           "Gainesville (Malcolm Randall VA Medical Center)": (55.7, 19.3),
           "Minneapolis VA Health Care System": (71.4, 12.4),
           "Lexington VA Health Care System": (83.2, 7.6),
           "VA Pacific Islands Health Care System": (85.7, 0.0)}
    for site, (i01, cd) in exp.items():
        check(f"{site[:34]} I01 share, %", shares[site]["I01"], i01)
        check(f"{site[:34]} IK1+IK2 share, %", shares[site]["CD"], cd)


def comparative_claims():
    print("\n--- Comparative claims asserted in the text ---")
    p = pd.read_csv(DATA / "site_profiles.csv")
    p["growth"] = p.growth_ratio.astype(float)
    big = p[p.va_awards > 100]
    check("highest I01 among >100-award sites is Lexington",
          big.loc[big.I01_pct.idxmax(), "site"].startswith("VA Medical Center Lexington"), True)
    check("lowest IK1+IK2 among >100-award sites is Lexington",
          big.loc[big.IK1_IK2_pct.idxmin(), "site"].startswith("VA Medical Center Lexington"), True)
    check("Bedford is 2nd lowest I01 among >100-award sites",
          sorted(big.I01_pct).index(56.9) == 1, True)
    check("highest IK1+IK2 in full sample is Gainesville",
          p.loc[p.IK1_IK2_pct.idxmax(), "site"].startswith("Malcolm Randall"), True)
    check("Bedford is 2nd highest IK1+IK2 in full sample",
          sorted(p.IK1_IK2_pct, reverse=True).index(17.5) == 1, True)
    check("Bedford has the fastest growth",
          p.loc[p.growth.idxmax(), "site"].startswith("Edith Nourse"), True)
    grew = p[p.growth > 1]
    check("Gainesville has the smallest increase of the sites that grew",
          grew.loc[grew.growth.idxmin(), "site"].startswith("Malcolm Randall"), True)
    check("VA Pacific Islands is the only site in decline",
          len(p[p.growth < 1]) == 1 and p[p.growth < 1].iloc[0]["site"].startswith("VA Pacific"), True)


def references():
    print("\n--- References ---")
    r = json.load(open(DATA / "references_pubmed_verified.json"))
    check("verified PubMed records", len(r), 42)
    retracted = [k for k, v in r.items() if any("Retract" in t for t in (v.get("article_types") or []))]
    check("retracted references", len(retracted), 0)
    no_doi = [k for k, v in r.items() if not (v.get("identifiers") or {}).get("doi")]
    print(f"     note: {len(no_doi)} record(s) without a DOI: {no_doi}")


if __name__ == "__main__":
    strand1(); strand2_awards(); strand2_dollars(); sites(); comparative_claims(); references()
    print("\n" + "=" * 86)
    if FAIL:
        print(f"{len(FAIL)} CHECK(S) FAILED:")
        for f in FAIL:
            print("  -", f)
        sys.exit(1)
    print("All published numbers reproduced from data/.")
