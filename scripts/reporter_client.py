"""Minimal NIH RePORTER API v2 client used by the FUND-IT reproduction scripts.

The manuscript's Method section specifies the ExPORTER bulk files. The bulk files and
the v2 API expose the same project records; the API is used here because it is
queryable without a multi-gigabyte download and because every number this repository
reproduces was verified against it on 2026-10-31. See REPRODUCIBILITY.md.
"""
import time
import requests

ENDPOINT = "https://api.reporter.nih.gov/v2/projects/search"
FIELDS = ["ProjectNum", "FiscalYear", "Organization", "ActivityCode", "AwardAmount"]


def fetch_projects(org_names=None, org_cities=None, org_states=None,
                   fiscal_years=tuple(range(2011, 2025)), fields=FIELDS,
                   page=500, pause=0.4, timeout=120):
    """Return every project record matching the criteria, following pagination."""
    criteria = {"fiscal_years": list(fiscal_years)}
    if org_names:
        criteria["org_names"] = list(org_names)
    if org_cities:
        criteria["org_cities"] = list(org_cities)
    if org_states:
        criteria["org_states"] = list(org_states)

    records, offset = [], 0
    while True:
        resp = requests.post(
            ENDPOINT,
            json={"criteria": criteria, "include_fields": list(fields),
                  "offset": offset, "limit": page},
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
        records.extend(payload["results"])
        total = payload["meta"]["total"]
        offset += page
        if offset >= total or not payload["results"]:
            return records
        time.sleep(pause)


def va_administered(records):
    """VA-administered awards only.

    VA activity codes all begin with 'I' (I01 merit review, IK1/IK2 career
    development, IK6 senior research career scientist, I21 pilot, I50 center,
    IS1 shared equipment, IP1 program project). Awards held by a site's
    affiliated nonprofit corporation carry NIH codes (R01, R21, U10, ...) and
    are excluded by this filter. The distinction is load-bearing: see
    REPRODUCIBILITY.md, finding R-2.
    """
    return [r for r in records if (r.get("activity_code") or "").startswith("I")]
