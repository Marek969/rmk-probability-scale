"""Plot probability scale visualizations."""

from __future__ import annotations

from pathlib import Path
from textwrap import fill

import numpy as np


PALETTE = {
    "Probability benchmark": "#a78bfa",
    "Estonian Rescue Board open data": "#34d399",
    "Derived from Rescue Board open data": "#22c55e",
    "Statistics Estonia MM03": "#60a5fa",
    "Statistics Estonia MM10": "#60a5fa",
    "Statistics Estonia RV046": "#60a5fa",
    "Statistics Estonia TT0151": "#60a5fa",
    "Statistics Estonia TH77": "#60a5fa",
    "Statistics Estonia (MM03)": "#60a5fa",
    "Statistics Estonia (MM10)": "#60a5fa",
    "Statistics Estonia (RV021)": "#60a5fa",
    "Statistics Estonia (RV11U)": "#60a5fa",
    "Statistics Estonia (RV047 + RV021)": "#60a5fa",
    "Statistics Estonia (RV57)": "#60a5fa",
    "Statistics Estonia (TS093 + RV021)": "#60a5fa",
    "Statistics Estonia (TT0151)": "#60a5fa",
}


def _format_probability(probability: float) -> str:
    pct = probability * 100
    if pct < 0.1:
        return f"{pct:.3f}%"
    if pct < 10:
        return f"{pct:.2f}%"
    return f"{pct:.1f}%"


def _format_odds(probability: float) -> str:
    n = 1 / probability
    if n < 10:
        return f"1 in {n:.1f}"
    if n < 100:
        return f"1 in {n:.0f}"
    return f"1 in {n:,.0f}"


def _spread_log_positions(target_logs: list[float], low: float, high: float, min_gap: float) -> list[float]:
    """Keep sorted x positions ordered with a minimum log-distance."""
    if not target_logs:
        return []

    placed: list[float] = []
    for i, target in enumerate(target_logs):
        lower_bound = low + i * min_gap
        val = max(target, lower_bound)
        if placed:
            val = max(val, placed[-1] + min_gap)
        placed.append(val)

    upper_overflow = placed[-1] - high
    if upper_overflow > 0:
        placed = [p - upper_overflow for p in placed]

    # Backward and forward passes keep values inside bounds and ordered.
    for i in range(len(placed) - 1, -1, -1):
        upper_bound = high - (len(placed) - 1 - i) * min_gap
        placed[i] = min(placed[i], upper_bound)
    for i in range(len(placed)):
        lower_bound = low + i * min_gap
        if i == 0:
            placed[i] = max(placed[i], lower_bound)
        else:
            placed[i] = max(placed[i], max(lower_bound, placed[i - 1] + min_gap))
    return placed


def plot_probability_scale(rows: list[dict[str, object]], out_png: Path, title: str = "Probability Scale") -> None:
    """Render events as callouts positioned on one logarithmic probability scale."""

    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    probs = np.array([float(row["probability"]) for row in rows])
    sources = [str(row["source_name"]) for row in rows]
    colors = [PALETTE.get(source, "#94a3b8") for source in sources]

    fig, ax = plt.subplots(figsize=(26, 15), constrained_layout=True)
    bg = "#070b14"
    panel = "#101827"
    line = "#dbeafe"
    grid = "#25344f"
    text = "#e8eef8"
    muted = "#9fb0c9"

    fig.patch.set_facecolor(bg)
    ax.set_facecolor(panel)
    ax.set_xscale("log")
    min_prob = max(float(np.min(probs)), 1e-6)
    x_min = max(min_prob * 0.55, 1e-6)
    ax.set_xlim(x_min, 0.9)
    ax.set_ylim(-5.4, 5.4)
    ax.set_yticks([])

    # Central probability ruler.
    ax.hlines(0, xmin=x_min, xmax=0.82, color=line, linewidth=3.2, alpha=0.95)
    ticks = [1e-4, 1e-3, 1e-2, 1e-1]
    tick_labels = ["1 in 10,000", "1 in 1,000", "1 in 100", "1 in 10"]
    for tick, tick_label in zip(ticks, tick_labels):
        ax.vlines(tick, -0.18, 0.18, color=line, linewidth=2)
        if x_min <= tick <= 0.82:
            ax.text(tick, -0.58, tick_label, color=muted, ha="center", va="top", fontsize=13)
    ax.text(x_min, -0.58, "rare", color=muted, ha="left", va="top", fontsize=13)
    ax.text(0.8, -0.58, "common", color=muted, ha="right", va="top", fontsize=13)

    # Place labels in sorted order across four lanes to avoid overlaps.
    order = sorted(range(len(probs)), key=lambda i: probs[i])
    lanes = [
        {"indices": order[0::4], "label_y": 4.2, "offset_sign": -1.0, "shift_base": 0.18, "shift_step": 0.12},
        {"indices": order[1::4], "label_y": -4.2, "offset_sign": -1.0, "shift_base": 0.38, "shift_step": 0.22},
        {"indices": order[2::4], "label_y": 2.8, "offset_sign": 1.0, "shift_base": 0.18, "shift_step": 0.12},
        {"indices": order[3::4], "label_y": -2.8, "offset_sign": 1.0, "shift_base": 0.32, "shift_step": 0.18},
    ]

    low_log = np.log10(max(x_min * 1.15, 1e-6))
    high_log = np.log10(0.78)
    min_gap = 0.62

    def draw_label(idx: int, x_label: float, y_label: float):
        row = rows[idx]
        p = float(row["probability"])
        color = colors[idx]
        ax.scatter(p, 0, color=color, s=135, zorder=5, edgecolor="#f8fafc", linewidth=1.3)
        # Draw a single soft diagonal connector (no staircase).
        ax.plot([p, x_label], [0, y_label], color=color, linewidth=1.6, alpha=0.95)
        event_text = fill(str(row["event"]), width=27)
        probability_str = _format_probability(p)
        odds_str = _format_odds(p)
        label_content = f"{event_text}\n{probability_str}  |  {odds_str}"
        if x_label < x_min * 6:
            align = "left"
            text_x = x_label * 1.16
        elif x_label > 0.62:
            align = "right"
            text_x = min(x_label / 1.05, 0.65)
        else:
            align = "center"
            text_x = x_label
        ax.text(
            text_x,
            y_label,
            label_content,
            color=text,
            ha=align,
            va="center",
            fontsize=18.5,
            linespacing=1.28,
            clip_on=False,
            bbox={
                "boxstyle": "round,pad=0.82,rounding_size=0.22",
                "facecolor": "#0b1220",
                "edgecolor": color,
                "linewidth": 1.7,
                "alpha": 0.95,
            },
        )

    for lane in lanes:
        idxs = lane["indices"]
        targets = [float(np.log10(probs[idx])) for idx in idxs]
        placed_logs = _spread_log_positions(targets, low_log, high_log, min_gap)
        xs = [10 ** value for value in placed_logs]
        for pos, (idx, x) in enumerate(zip(idxs, xs)):
            # Special case: "Being born in Tallinn" (index 7) goes straight down
            if idx == 7:
                shifted_x = float(x)
            else:
                # Side shift pushes labels further from center: left labels left, right labels right
                shift = 1 + lane["offset_sign"] * (lane["shift_base"] + lane["shift_step"] * pos)
                shifted_x = float(x) * shift
                # Clamp to keep inside chart bounds
                if lane["offset_sign"] < 0:
                    shifted_x = min(0.50, max(x_min * 2.4, shifted_x))
                else:
                    shifted_x = min(0.68, max(x_min * 2.4, shifted_x))
            draw_label(int(idx), shifted_x, float(lane["label_y"]))

    ax.set_xlabel("Probability, logarithmic scale", color=muted, fontsize=19, labelpad=20)
    ax.set_title(title, color=text, fontsize=36, fontweight="bold", pad=32)
    ax.text(
        0.5,
        1.02,
        "Events are placed by probability; familiar exact odds act as anchors for intuition",
        transform=ax.transAxes,
        color=muted,
        fontsize=18,
        ha="center",
    )

    ax.grid(axis="x", color=grid, linewidth=0.8, alpha=0.65)
    ax.tick_params(axis="x", colors=muted, labelsize=16)
    for spine in ax.spines.values():
        spine.set_color("#1f2a44")
        spine.set_linewidth(1.2)

    legend_items = [
        Line2D([0], [0], marker="o", color="none", label="Benchmark", markerfacecolor=PALETTE["Probability benchmark"], markersize=9),
        Line2D([0], [0], marker="o", color="none", label="Fire data", markerfacecolor=PALETTE["Derived from Rescue Board open data"], markersize=9),
        Line2D([0], [0], marker="o", color="none", label="Statistics Estonia", markerfacecolor=PALETTE.get("Statistics Estonia (TS093 + RV021)", PALETTE.get("Statistics Estonia (MM03)", "#60a5fa")), markersize=9),
    ]
    ax.legend(handles=legend_items, loc="lower right", frameon=False, labelcolor=muted, fontsize=16)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
