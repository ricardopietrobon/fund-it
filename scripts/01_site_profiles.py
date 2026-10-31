"""Regenerate Table 4 (five interviewed sites) from NIH RePORTER and compare with
the values reported in the manuscript.

Run:  python scripts/01_site_profiles.py
Writes: outputs/site_profiles.json
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from reporter_client import fetch_projects, va_administered

OUT = os.path.join(os.path.dirname(__file__), os.pardir, "outputs")

# org_name strings as they appear in RePORTER. These are NOT interchangeable with
# the facility's common name; see REPRODUCIBILITY.md finding R-1.
SITES = {
    "Bedford": dict(
        org_names=["EDITH NOURSE ROGERS MEMORIAL VETERANS HOSPITAL"], org_cities=None),
    "Gainesville": dict(
        org_names=["VETERANS HEALTH ADMINISTRATION"], org_cities=["GAINESVILLE"]),
    "Minneapolis": dict(
        org_names=["MINNEAPOLIS VA MEDICAL CENTER"], org_cities=None),
    "Lexington": dict(
        org_names=["VA MEDICAL CENTER LEXINGTON KY"], org_cities=None),
    "VA Pacific Islands": dict(
        org_names=["VA PACIFIC ISLANDS HEALTH CARE SYSTEM"], org_cities=None),
}

# Values as printed in the manuscript: (total awards, % I01, % IK1+IK2, growth ratio)
REPORTED = {
    "Bedford": (269, 56.9, 17.5, 2.79),
    "Gainesville": (296, 55.7, 19.3, 1.08),
    "Minneapolis": (419, 71.4, 12.4, 1.46),
    "Lexington": (131, 83.2, 7.6, 1.26),
    "VA Pacific Islands": (7, 85.7, 0.0, 0.58),
}

EARLY = range(2011, 2018)   # FY2011-2017
LATE = range(2018, 2025)    # FY2018-2024


def profile(records):
    awards = va_administered(records)
    n = len(awards)
    codes = collections.Counter(r["activity_code"] for r in awards)
    years = collections.Counter(r["fiscal_year"] for r in awards)
    early = sum(c for y, c in years.items() if y in EARLY)
    late = sum(c for y, c in years.items() if y in LATE)
    return dict(
        n_awards=n,
        pct_i01=round(codes["I01"] / n * 100, 1) if n else None,
        pct_career_dev=round((codes["IK1"] + codes["IK2"]) / n * 100, 1) if n else None,
        early_fy2011_2017=early,
        late_fy2018_2024=late,
        growth_ratio=round(late / early, 2) if early else None,
        by_activity_code=dict(codes.most_common()),
        by_fiscal_year=dict(sorted(years.items())),
    )


def main():
    os.makedirs(OUT, exist_ok=True)
    results, mismatches = {}, []
    header = f"{'site':<20} {'n':>5} {'I01%':>7} {'CD%':>6} {'growth':>7}   vs manuscript"
    print(header)
    print("-" * len(header))
    for site, cfg in SITES.items():
        recs = fetch_projects(org_names=cfg["org_names"], org_cities=cfg["org_cities"])
        p = profile(recs)
        results[site] = p
        exp_n, exp_i01, exp_cd, exp_g = REPORTED[site]
        checks = [
            ("n_awards", p["n_awards"], exp_n, 0),
            ("pct_i01", p["pct_i01"], exp_i01, 0.05),
            ("pct_career_dev", p["pct_career_dev"], exp_cd, 0.05),
            ("growth_ratio", p["growth_ratio"], exp_g, 0.005),
        ]
        bad = [c[0] for c in checks
               if c[1] is None or abs(c[1] - c[2]) > c[3]]
        mismatches.extend((site, b) for b in bad)
        print(f"{site:<20} {p['n_awards']:>5} {p['pct_i01']:>7} {p['pct_career_dev']:>6} "
              f"{p['growth_ratio']:>7}   {'MATCHES' if not bad else 'differs on ' + ', '.join(bad)}")

    with open(os.path.join(OUT, "site_profiles.json"), "w") as fh:
        json.dump(results, fh, indent=1)

    print()
    if mismatches:
        print("Known, documented discrepancies (REPRODUCIBILITY.md findings R-2, R-3):")
        for site, field in mismatches:
            print(f"  - {site}: {field}")
    else:
        print("All reported site values reproduced from source.")


if __name__ == "__main__":
    main()
