"""Plot probability scale visualizations.

Provides a simple dark-theme log-scale horizontal plot suitable for the
probability scale. Accepts a list of event dictionaries with `probability`
and `event` fields.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def plot_probability_scale(rows: list[dict[str, object]], out_png: Path, title: str = "Probability Scale") -> None:
    import matplotlib.pyplot as plt

    probs = np.array([float(row["probability"]) for row in rows])
    labels = [str(row["event"]) for row in rows]

    # Dark canvas for the exported figure.
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    fig.patch.set_facecolor("#0b0f1a")
    ax.set_facecolor("#0b0f1a")

    ax.hlines(0, xmin=max(probs.min() * 0.4, 1e-6), xmax=1.05, color="#cfe3ff", linewidth=2)
    ax.scatter(probs, np.zeros_like(probs), color="#ffd54f", s=50, zorder=5)

    for i, (p, label) in enumerate(zip(probs, labels)):
        # Alternate label direction to reduce overlap.
        direction = 1 if i % 2 == 0 else -1
        y = 0.25 * direction
        ax.plot([p, p * 1.3], [0, y], color="#8fa8c8")
        ax.text(p * 1.35, y, f"{label}\n{p:.6g}", color="#ffffff", va="center", fontsize=10)

    # Log scale keeps rare and common events visible together.
    ax.set_xscale("log")
    ax.set_xlim(max(probs.min() * 0.4, 1e-6), 1.05)
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.set_xlabel("Probability (log scale)", color="#cfe3ff")
    ax.set_title(title, color="#fff")
    ax.tick_params(colors="#cfe3ff")

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
