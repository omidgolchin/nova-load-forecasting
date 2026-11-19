"""Draw the README charts from the saved score files.

Usage (from the repo root): python scripts/make_charts.py
Reads results/scores_main.csv and results/scores_sensitivity2_metrics.csv;
writes results/chart_mase.png and results/chart_coverage.png.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

R = Path("results")
main = pd.read_csv(R / "scores_main.csv")
sens = pd.read_csv(R / "scores_sensitivity2_metrics.csv")
sens = sens[sens.method == "sarimax_alt2_nofuture"].assign(method="sarimax_posthoc")
df = pd.concat([main, sens], ignore_index=True)

ROWS = [  # (method id, label), top to bottom
    ("snaive", "Seasonal naive (same hour last week)"),
    ("naive", "Naive (same hour yesterday)"),
    ("sarimax_oracle", "SARIMAX, observed weather (ceiling)"),
    ("sarimax_nofuture", "SARIMAX, no future weather (pre-registered)"),
    ("sarimax_posthoc", "SARIMAX, no future weather (post-hoc order)"),
    ("lstm", "LSTM (3 seeds)"),
    ("chronos", "Chronos-Bolt (zero-shot, 168 h)"),
    ("timesfm", "TimesFM 2.5 (zero-shot, 168 h)"),
    ("llm", "Qwen2.5-7B (26 origins only)"),
]
YEARS = {1: ("Year 1 (Nov 2024 – Oct 2025)", "#2a78d6", "o"),
         2: ("Year 2 (Nov 2025 – Oct 2026)", "#eb6834", "s")}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dddcd7"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "font.family": "DejaVu Sans"})


def panel(ax, h, col, lo=None, hi=None, ref=None, ref_label=None):
    rows = ROWS
    for i, (m, _) in enumerate(rows):
        if not ((df.method == m) & (df.horizon_h == h)).any():
            ax.text(0.02, i, "24 h only", transform=ax.get_yaxis_transform(),
                    va="center", fontsize=8, color=MUTED, style="italic")
        for half, (_, color, marker) in YEARS.items():
            r = df[(df.method == m) & (df.horizon_h == h) & (df.half == half)]
            if r.empty:
                continue
            r = r.iloc[0]
            y = i + (-0.17 if half == 1 else 0.17)
            hollow = m == "sarimax_posthoc"
            if lo:
                ax.errorbar(r[col], y, xerr=[[r[col] - r[lo]], [r[hi] - r[col]]], fmt="none",
                            ecolor=color, elinewidth=1.5, capsize=0)
            ax.plot(r[col], y, marker=marker, ms=7, color=color,
                    mfc="white" if hollow else color, mew=1.8, ls="none")
    ax.set_yticks(range(len(rows)), [l for _, l in rows])
    ax.set_ylim(len(rows) - 0.5, -0.5)
    if ref is not None:
        ax.axvline(ref, color=MUTED, lw=1, ls=(0, (4, 3)))
        if ref_label:
            ax.text(ref, -0.75, ref_label, color=MUTED, ha="center", va="bottom", fontsize=8)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_title(f"{h} h ahead", loc="left", fontsize=10, color=INK, pad=14)


def legend(fig):
    handles = [plt.Line2D([], [], marker=mk, color=c, ls="none", ms=7, label=l)
               for l, c, mk in YEARS.values()]
    handles.append(plt.Line2D([], [], marker="o", color=MUTED, mfc="white", mew=1.8,
                              ls="none", ms=7, label="Hollow: post-hoc order (DEVIATIONS.md)"))
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=8.5)


# MASE
fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharex=True, sharey=True)
for ax, h in zip(axes, (24, 168)):
    panel(ax, h, "mase", "mase_ci_lo", "mase_ci_hi", ref=1.0)
    ax.set_xlabel("MASE, lower is better", color=MUTED, fontsize=8.5)
axes[1].tick_params(axis="y", labelleft=False)
fig.text(0.01, 0.905, "1 = the training-period error of 'same hour last week' (dashed line)",
         fontsize=8.5, color=MUTED)
fig.suptitle("Forecast error by method, with 95% block-bootstrap intervals",
             x=0.01, ha="left", fontsize=11.5, color=INK)
fig.tight_layout(rect=(0, 0.07, 1, 0.97))
legend(fig)
fig.savefig(R / "chart_mase.png", dpi=180, facecolor="white")
plt.close(fig)

# Coverage
fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharex=True, sharey=True)
for ax, h in zip(axes, (24, 168)):
    panel(ax, h, "coverage80", ref=0.8, ref_label="80% target")
    ax.set_xlim(0.3, 1.0)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("Share of actual hours inside the 80% interval", color=MUTED, fontsize=8.5)
axes[1].tick_params(axis="y", labelleft=False)
axes[0].plot([0.667, 0.667], [7.65, 8.35], color=MUTED, lw=1.5)
axes[0].text(0.68, 8, "0.67: the most a calibrated\n5-sample range covers", va="center",
             fontsize=7.5, color=MUTED)
fig.suptitle("Are the 80% prediction intervals honest?",
             x=0.01, ha="left", fontsize=11.5, color=INK)
fig.tight_layout(rect=(0, 0.07, 1, 0.97))
legend(fig)
fig.savefig(R / "chart_coverage.png", dpi=180, facecolor="white")
plt.close(fig)
print("wrote results/chart_mase.png and results/chart_coverage.png")
