"""Publication-quality matplotlib figures.

Each `*_fig` function returns a matplotlib Figure (for Streamlit / in-notebook
use); the plain wrappers add file saving for the batch pipeline.
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Light theme friendly; high-contrast, explicit colours (no reliance on theme classes)
C_OBS = "#1f77b4"
C_FIT = "#9467bd"
C_FC = "#d62728"
C_POS = "#2ca02c"
C_NEG = "#d62728"


def plot_trend_forecast_fig(region: str, metric: str, series, fc: dict):
    yrs, val, lo, hi = series
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=130)

    ax.fill_between(yrs, lo, hi, color=C_OBS, alpha=0.18, label="95% UI (observed)")
    ax.plot(yrs, val, color=C_OBS, marker="o", ms=3, lw=1.6, label="Observed (ASR)")

    ax.plot(fc["hist_years"], fc["hist_fit"], color=C_FIT, ls="--", lw=1.3,
            label="Model fit (log-linear)")

    fy = fc["fc_years"]
    ax.plot(fy, fc["fc_point"], color=C_FC, lw=1.8, label="Forecast (to 2035)")
    ax.fill_between(fy, fc["fc_lower"], fc["fc_upper"], color=C_FC, alpha=0.20,
                    label="95% CI (forecast)")

    ax.axvline(fc["forecast_start_year"] - 0.5, color="gray", ls=":", lw=1)

    ax.set_title(f"{region} — {metric.capitalize()} (per 100,000)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Age-standardized rate")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig


def plot_decomposition_fig(region: str, contrib: dict):
    drivers = list(contrib.keys())
    vals = [contrib[d] for d in drivers]
    colors = [C_POS if v >= 0 else C_NEG for v in vals]
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=130)
    ax.barh(drivers, vals, color=colors)
    for i, v in enumerate(vals):
        ax.text(v + (1 if v >= 0 else -1) * 1.5, i, f"{v:.2f}%",
                va="center", ha="left" if v >= 0 else "right", fontsize=9)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_title(f"Decomposition of burden change — {region}")
    ax.set_xlabel("% contribution to total change")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return fig


# --- file-saving wrappers (used by the batch pipeline) ---
def plot_trend_forecast(region, metric, series, fc, outpath):
    fig = plot_trend_forecast_fig(region, metric, series, fc)
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_decomposition(region, contrib, outpath):
    fig = plot_decomposition_fig(region, contrib)
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
