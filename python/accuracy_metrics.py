#!/usr/bin/env python3
"""
accuracy_metrics.py
-------------------
Accuracy metrics for the Lake Chad open-water maps (manuscript Section 2.5, Table 4).

Sampling design: 100 points in the mapped-water stratum and 100 in the mapped
non-water stratum per year. Confusion-matrix convention used throughout:

                        reference water   reference non-water
    mapped water               TP                  FP
    mapped non-water           FN                  TN

(rows = mapped classes / sampling strata, columns = reference classes)

Metrics (sample-based, NOT area-adjusted):
    OA    overall accuracy = (TP + TN) / N
    CI    95% Wilson score interval for OA
    Kappa Cohen's kappa
    UA    water user's accuracy     = TP / (TP + FP)
    PA    water producer's accuracy = TP / (TP + FN)

Usage
-----
    # from confusion-matrix counts (default)
    python python/accuracy_metrics.py

    # or directly from the labelled reference points
    python python/accuracy_metrics.py --points data/reference_points_labelled.csv
        (columns: year, mapped, reference; 1 = water, 0 = non-water)
"""
import argparse
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
Z95 = 1.959963984540054  # standard normal quantile for a 95% interval


def wilson_interval(k: int, n: int, z: float = Z95):
    """Wilson score interval for a binomial proportion (returns proportions)."""
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def metrics(tp: int, fp: int, fn: int, tn: int) -> dict:
    n = tp + fp + fn + tn
    oa = (tp + tn) / n
    lo, hi = wilson_interval(tp + tn, n)
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / n**2
    kappa = (oa - pe) / (1 - pe)
    return {
        "n": n,
        "OA_pct": 100 * oa,
        "OA_CI_lower_pct": 100 * lo,
        "OA_CI_upper_pct": 100 * hi,
        "Kappa": kappa,
        "Water_UA_pct": 100 * tp / (tp + fp),
        "Water_PA_pct": 100 * tp / (tp + fn),
    }


def confusion_from_points(path: Path) -> pd.DataFrame:
    pts = pd.read_csv(path)
    rows = []
    for year, g in pts.groupby("year"):
        rows.append({
            "year": int(year),
            "TP": int(((g.mapped == 1) & (g.reference == 1)).sum()),
            "FP": int(((g.mapped == 1) & (g.reference == 0)).sum()),
            "FN": int(((g.mapped == 0) & (g.reference == 1)).sum()),
            "TN": int(((g.mapped == 0) & (g.reference == 0)).sum()),
        })
    return pd.DataFrame(rows)


def build_summary(cm: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, r in cm.iterrows():
        m = metrics(int(r.TP), int(r.FP), int(r.FN), int(r.TN))
        out.append({"year": int(r.year), **m})
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--points", type=Path, default=None,
                    help="labelled reference points CSV (year, mapped, reference)")
    ap.add_argument("--confusion", type=Path, default=ROOT / "data" / "confusion_matrices.csv",
                    help="confusion-matrix counts CSV (year, TP, FP, FN, TN)")
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "accuracy_summary.csv")
    args = ap.parse_args()

    if args.points is not None:
        cm = confusion_from_points(args.points)
        cm.to_csv(args.confusion, index=False)
        print(f"Confusion matrices written to {args.confusion}")
    else:
        cm = pd.read_csv(args.confusion)

    summary = build_summary(cm).round(2)
    summary.to_csv(args.out, index=False)
    print(summary.to_string(index=False))
    print(f"\nSaved: {args.out}")


if __name__ == "__main__":
    main()
