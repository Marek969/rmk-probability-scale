"""Plot a horizontal probability scale on a logarithmic axis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_probability_scale_figure(data: pd.DataFrame, title: str) -> plt.Figure:
    """Create stylized probability scale with alternating callouts."""

    fig, ax = plt.subplots(figsize=(16, 9), constrained_layout=True)
    fig.patch.set_facecolor("#05070d")
    ax.set_facecolor("#05070d")

    probs = data["probability"].to_numpy()
    labels = data["event"].tolist()

    ax.hlines(0, xmin=min(probs) * 0.6, xmax=min(1.0, max(probs) * 1.4), color="#d7dde6", linewidth=2)
    ax.scatter(probs, np.zeros_like(probs), s=30, color="#e6edf7", zorder=3)

    for i, (p, label) in enumerate(zip(probs, labels)):
        direction = 1 if i % 2 == 0 else -1
        y_mid = 0.3 * direction
        y_txt = 0.7 * direction

        ax.plot([p, p * 1.15, p * 1.6], [0, y_mid, y_mid], color="#a9b3c2", linewidth=1.5)

        prob_txt = f"{p:.6f}".rstrip("0").rstrip(".")
        ax.text(
            p * 1.63,
            y_txt,
            f"{prob_txt}\n{label}",
            color="#f3f7ff",
            fontsize=11,
            va="center",
            ha="left",
        )

    ax.set_xscale("log")
    ax.set_xlim(max(min(probs) * 0.4, 1e-6), 1.05)
    ax.set_ylim(-1.1, 1.1)

    ax.set_yticks([])
    ax.set_xlabel("Probability (log scale)", color="#d7dde6", fontsize=12)
    ax.set_title(title, color="#f8fbff", fontsize=20, pad=18)

    ax.tick_params(axis="x", colors="#d7dde6")
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(axis="x", color="#2a3341", linestyle="--", linewidth=0.8, alpha=0.7)

    return fig


def save_figure(fig: plt.Figure, out_png: Path, out_svg: Path) -> None:
    """Write plot in raster and vector formats."""

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    fig.savefig(out_svg)
    plt.close(fig)
