"""Audit Strand 1 (senior-to-junior PI cross-correlation, Table 1).

Every aggregate the manuscript reports ABOUT the cross-correlation table is
recomputed here and asserted. The cross-correlations themselves are NOT
recomputed, because the per-department annual senior/junior PI count series that
produce them do not exist in this repository or anywhere in the project archive --
only the final (lag, r) pairs survive. See REPRODUCIBILITY.md finding R-4.

Run:  python scripts/03_h1_audit.py
Writes: outputs/h1_audit.json
"""
import json
import os

import numpy as np

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, os.pardir, "data", "derived")
OUT = os.path.join(HERE, os.pardir, "outputs")


def check(label, got, expected, tol=0):
    ok = abs(got - expected) <= tol
    print(f"  {'ok ' if ok else 'FAIL'} {label:<46} computed={got!r:<10} reported={expected!r}")
    assert ok, f"{label}: computed {got}, manuscript reports {expected}"
    return got


def main():
    os.makedirs(OUT, exist_ok=True)
    table = json.load(open(os.path.join(DATA, "h1_crosscorrelation_table.json")))

    print("Strand 1 aggregates recomputed from the reported per-department table")
    check("department categories", len(table), 26)
    check("junior PI records", sum(d["junior"] for d in table), 56581)
    check("senior PI records", sum(d["senior"] for d in table), 8971)
    check("junior-to-senior ratio",
          round(sum(d["junior"] for d in table) / sum(d["senior"] for d in table), 1), 6.3, 0.05)

    computable = [d for d in table if d["r"] is not None and d["junior"] > 0 and d["senior"] > 0]
    check("departments with computable series", len(computable), 22)
    check("departments peaking at a negative lag", sum(1 for d in computable if d["lag"] < 0), 19)
    check("departments peaking at lag zero", sum(1 for d in computable if d["lag"] == 0), 3)

    rs = [d["r"] for d in computable]
    check("minimum peak correlation", round(min(rs), 3), -0.142, 0.0005)
    check("maximum peak correlation", round(max(rs), 3), 0.594, 0.0005)
    check("median peak correlation", round(float(np.median(rs)), 3), 0.379, 0.0005)
    check("departments with r >= 0.40", sum(1 for r in rs if r >= 0.40), 9)

    named = {"NEUROLOGY": (-3, 0.594), "PSYCHIATRY": (-2, 0.577), "PEDIATRICS": (-5, 0.569),
             "SURGERY": (-5, 0.420), "UROLOGY": (-4, -0.142), "OPHTHALMOLOGY": (0, 0.092)}
    print("\n  Departments named in the Results text")
    for dept, (lag, r) in named.items():
        row = next(d for d in table if d["dept"] == dept)
        check(f"{dept} lag", row["lag"], lag)
        check(f"{dept} r", round(row["r"], 3), r, 0.0005)

    excluded = [d for d in table if d not in computable]
    print("\n  Excluded from the 22 computable departments:")
    for d in excluded:
        print(f"    {d['dept']:<28} junior={d['junior']:<5} senior={d['senior']}")

    print("\n  NOT RECOMPUTABLE: the (lag, r) pairs above are inputs to this audit, not")
    print("  outputs of it. Reproducing them requires the per-department annual senior and")
    print("  junior PI count series, which are not available. See REPRODUCIBILITY.md R-4.")

    with open(os.path.join(OUT, "h1_audit.json"), "w") as fh:
        json.dump({"table": table, "computable": len(computable),
                   "recomputable_correlations": False}, fh, indent=1)


if __name__ == "__main__":
    main()
