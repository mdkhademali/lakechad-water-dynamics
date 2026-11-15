#!/usr/bin/env python3
"""
make_figures.p
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from accuracy_metrics import metrics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

INK, MUTED, RED = "#1F2D3D", "#5F6B7A", "#B03A2E"
plt.rcParams["font.family"] = "DejaVu Sans"


# ------------------------------------------------------------------ Figure 3
def figure3(area_df: pd.DataFrame) -> None:
    years = area_df["year"].astype(str).tolist()
    area = area_df["water_area_km2"].to_numpy()
    sensor = area_df["sensor"].tolist()
    scenes = area_df["n_scenes"].tolist()
    chg_km = area - area[0]
    chg_pct = chg_km / area[0] * 100
    colors = ["#0A2F5C", "#1B5C9E", "#4A92CC", "#8DBFE3"]

    fig, ax = plt.subplots(figsize=(8.0, 4.64), dpi=300)
    fig.subplots_adjust(left=0.105, right=0.975, top=0.94, bottom=0.235)
    x = np.arange(len(area))
    ax.bar(x, area, width=0.58, color=colors, zorder=3, linewidth=0)

    ax.hlines(area[0], 0.29, 3.62, colors="#9AA5B1", linestyles=(0, (4, 3)), linewidth=1.0, zorder=2)
    ax.hlines(area[-1], 3.29, 3.62, colors="#9AA5B1", linestyles=(0, (4, 3)), linewidth=1.0, zorder=2)

    for i, (xi, v) in enumerate(zip(x, area)):
        ax.text(xi, v + 30, f"{v:,.2f}", ha="center", va="bottom", fontsize=10.5,
                fontweight="bold", color=INK, zorder=5)
        label, tc = ("baseline", MUTED) if i == 0 else (f"\u2212{abs(chg_pct[i]):.1f}%", RED)
        ax.text(xi, v - 85, label, ha="center", va="top", fontsize=9.5, color=tc, zorder=5,
                fontweight="bold" if i else "normal",
                bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.6", fc="white", ec="none", alpha=0.95))

    xa = 3.62
    ax.annotate("", xy=(xa, area[-1]), xytext=(xa, area[0]),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.5, shrinkA=0, shrinkB=0,
                                mutation_scale=11), zorder=6)
    ymid = (area[0] + area[-1]) / 2
    ax.text(xa + 0.12, ymid + 38, f"\u2212{abs(chg_pct[-1]):.1f}%", ha="left", va="bottom",
            fontsize=19, fontweight="bold", color=RED)
    ax.text(xa + 0.12, ymid + 18, f"\u2212{abs(chg_km[-1]):,.2f} km\u00b2", ha="left", va="top",
            fontsize=9.5, color=MUTED)
    ax.text(xa + 0.12, ymid - 78, f"{years[0]}\u2013{years[-1]}", ha="left", va="top",
            fontsize=9, color=MUTED)

    ax.set_xlim(-0.55, 4.45)
    ax.set_ylim(0, 2150)
    ax.set_yticks(np.arange(0, 2001, 500))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_ylabel("Open-water area (km\u00b2)", fontsize=10.5, color=INK, labelpad=8)
    ax.grid(axis="y", color="#E3E7EB", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#7B8794")
    ax.tick_params(axis="y", length=0, labelsize=9.5, colors=MUTED)
    ax.tick_params(axis="x", length=0, pad=6)
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=11.5, fontweight="bold", color=INK)
    for xi, s, n in zip(x, sensor, scenes):
        ax.text(xi, -0.115, f"{s}\nn = {n} scenes", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=8.5, color=MUTED, linespacing=1.5)

    fig.text(0.105, 0.035,
             "April\u2013June composites \u00b7 MNDWI > 0.2 \u00b7 scene cloud cover < 20% \u00b7 "
             "fixed study polygon (\u224818,315 km\u00b2)",
             fontsize=8, color=MUTED, ha="left", va="bottom")
    fig.savefig(FIG / "Figure3_open_water_area.png", dpi=300, facecolor="white")
    fig.savefig(FIG / "Figure3_open_water_area.pdf", facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ Figure 4
def figure4(cm: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, len(cm), figsize=(14.31, 4.05), dpi=300)
    for ax, (_, r) in zip(np.atleast_1d(axes), cm.iterrows()):
        m = np.array([[r.TP, r.FP], [r.FN, r.TN]])      # rows = mapped, cols = reference
        ax.imshow(m, cmap="Blues", vmin=0, vmax=100)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(int(m[i, j])), ha="center", va="center", fontsize=9,
                        color="white" if m[i, j] > 50 else "#1a1a1a")
        ax.set_title(str(int(r.year)), fontsize=11, fontweight="bold")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Water", "Non-water"], fontsize=8)
        ax.set_yticks([0, 1]); ax.set_yticklabels(["Water", "Non-water"], fontsize=8, rotation=90, va="center")
        ax.set_xlabel("Reference", fontsize=8.5); ax.set_ylabel("Mapped", fontsize=8.5)
        ax.set_xticks([0.5], minor=True); ax.set_yticks([0.5], minor=True)
        ax.grid(which="minor", color="white", linewidth=2); ax.tick_params(which="minor", length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle("Confusion Matrices for Lake Chad Water Classification",
                 fontsize=13, fontweight="bold", y=0.97)
    fig.subplots_adjust(left=0.04, right=0.99, bottom=0.17, top=0.84, wspace=0.18)
    fig.savefig(FIG / "Figure4_confusion_matrices.png", dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------ Figure 5
def figure5(cm: pd.DataFrame) -> None:
    res = [metrics(int(r.TP), int(r.FP), int(r.FN), int(r.TN)) for _, r in cm.iterrows()]
    years = cm["year"].astype(int).astype(str).tolist()
    oa = [m["OA_pct"] for m in res]
    ua = [m["Water_UA_pct"] for m in res]
    pa = [m["Water_PA_pct"] for m in res]
    x = np.arange(len(years)); w = 0.25

    fig, ax = plt.subplots(figsize=(10, 5.96), dpi=300)
    ax.bar(x - w, oa, w, label="OA (%)", color="#1f77b4")
    ax.bar(x, ua, w, label="Water UA (%)", color="#ff7f0e")
    ax.bar(x + w, pa, w, label="Water PA (%)", color="#2ca02c")
    ax.set_xticks(x); ax.set_xticklabels(years)
    ax.set_ylim(70, 105)
    ax.set_xlabel("Year"); ax.set_ylabel("Accuracy (%)")
    ax.set_title("Classification Accuracy Comparison", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3); ax.set_axisbelow(True)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "Figure5_accuracy_comparison.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    area_df = pd.read_csv(DATA / "water_area_summary.csv").sort_values("year")
    cm = pd.read_csv(DATA / "confusion_matrices.csv").sort_values("year")
    figure3(area_df)
    figure4(cm)
    figure5(cm)
    print(f"Figures written to {FIG}")
