"""Regenerate the Strand 2 concentration statistics (Results paragraphs 2-3, Tables 2-3)
from the derived award-count datasets, and assert each against the manuscript.

Run:  python scripts/02_concentration.py
Writes: outputs/concentration.json
"""
import json
import os

import numpy as np

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, os.pardir, "data", "derived")
OUT = os.path.join(HERE, os.pardir, "outputs")

# Umbrella / catch-all records excluded from the concentration analysis, exactly as
# named in the manuscript Method.
UMBRELLA = {
    "VETERANS HEALTH ADMINISTRATION",
    "VETERANS AFFAIRS UNITED STATES DEPARTMENT OF",
    "U S DEPT VETS AFFAIRS MEDICAL CENTER",
    "VA VETERANS ADMINISTRATION HOSPITAL",
    "VA MEDICAL CENTER",
}

# Virginia state agencies that entered the VA-affiliated list by matching the
# string "VA". Removed before the dollar analysis.
NOT_VETERANS_AFFAIRS = {
    "VA DIVISION CONSOLIDATED LAB SRVS",
    "VA ST DEPT AGRICULTURE AND CONSUMER SRVS",
}


def gini(values):
    """Gini coefficient, standard mean-absolute-difference form on sorted values."""
    x = np.sort(np.asarray(values, dtype=float))
    n = x.size
    return float(np.sum((2 * np.arange(1, n + 1) - n - 1) * x) / (n * x.sum()))


def check(label, got, expected, tol):
    ok = abs(got - expected) <= tol
    print(f"  {'ok ' if ok else 'FAIL'} {label:<42} computed={got!r:<12} reported={expected!r}")
    assert ok, f"{label}: computed {got}, manuscript reports {expected}"
    return got


def main():
    os.makedirs(OUT, exist_ok=True)
    results = {}

    orgs = json.load(open(os.path.join(DATA, "va_org_awards_fy2020_2024.json")))["orgs"]
    print("VA award concentration, FY2020-2024")
    check("organizations before exclusions", len(orgs), 76, 0)
    check("awards before exclusions", sum(c for _, c in orgs), 10608, 0)

    kept = [(n, c) for n, c in orgs if n.strip().upper() not in UMBRELLA]
    counts = [c for _, c in kept]
    total = sum(counts)
    check("organizations after exclusions", len(kept), 71, 0)
    check("awards after exclusions", total, 8991, 0)

    ranked = sorted(counts, reverse=True)
    cum = np.cumsum(ranked) / total
    results["awards"] = dict(
        top10_pct=check("top 10 share of awards (%)", round(sum(ranked[:10]) / total * 100, 1), 40.3, 0.05),
        gini=check("Gini of award counts", round(gini(counts), 3), 0.524, 0.0005),
        n_for_80pct=check("organizations holding 80% of awards", int(np.searchsorted(cum, 0.80) + 1), 29, 0),
        n_for_90pct=check("organizations holding 90% of awards", int(np.searchsorted(cum, 0.90) + 1), 38, 0),
        median=check("median awards per organization", float(np.median(counts)), 74.0, 0.05),
        q1=check("first quartile", float(np.percentile(counts, 25)), 24.5, 0.05),
        q3=check("third quartile", float(np.percentile(counts, 75)), 207.5, 0.05),
        mean=check("mean awards per organization", round(float(np.mean(counts)), 1), 126.6, 0.05),
    )

    npc = json.load(open(os.path.join(DATA, "npc_nih_awards_fy2020_2024.json")))
    print("\nNIH dollars to VA-affiliated organizations, FY2020-2024")
    check("organizations before correction", len(npc), 22, 0)
    check("awards before correction", sum(a for _, a, _ in npc), 368, 0)
    check("dollars before correction ($M)", round(sum(d for _, _, d in npc) / 1e6, 1), 143.7, 0.05)

    corrected = [r for r in npc if r[0] not in NOT_VETERANS_AFFAIRS]
    dollars = [d for _, _, d in corrected]
    awards = [a for _, a, _ in corrected]
    total_d = sum(dollars)
    check("organizations after correction", len(corrected), 20, 0)
    check("awards after correction", sum(awards), 319, 0)
    check("dollars after correction ($M)", round(total_d / 1e6, 1), 129.7, 0.05)

    ranked_d = sorted(dollars, reverse=True)
    results["dollars"] = dict(
        top3_pct=check("top 3 share of dollars (%)", round(sum(ranked_d[:3]) / total_d * 100, 1), 72.5, 0.05),
        top5_pct=check("top 5 share of dollars (%)", round(sum(ranked_d[:5]) / total_d * 100, 1), 82.1, 0.05),
        gini_dollars=check("Gini of dollars", round(gini(dollars), 3), 0.724, 0.0005),
        gini_awards=check("Gini of award counts (NIH subset)", round(gini(awards), 3), 0.656, 0.0005),
    )

    palo_alto = next(d for n, _, d in corrected if "PALO ALTO" in n)
    check("Palo Alto dollars ($M)", round(palo_alto / 1e6, 1), 53.7, 0.05)
    bottom17 = sum(ranked_d[-17:])
    print(f"  {'ok ' if palo_alto > bottom17 else 'FAIL'} "
          f"{'Palo Alto exceeds bottom 17 combined':<42} "
          f"computed=${palo_alto/1e6:.1f}M > ${bottom17/1e6:.1f}M")
    assert palo_alto > bottom17
    results["palo_alto_dollars"] = palo_alto
    results["bottom17_dollars"] = bottom17

    with open(os.path.join(OUT, "concentration.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    print("\nAll Strand 2 statistics reproduced. -> outputs/concentration.json")


if __name__ == "__main__":
    main()
