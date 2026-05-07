"""Stephen Center front-office input-data analysis.

Reads the observation CSVs, computes summary statistics, fits an
exponential to the inter-arrival times, and emits the figures used in
the Project 4 presentation.

Outputs (under ``figures/`` next to this script):
    - hist_interarrival.png
    - hist_service_time_by_type.png
    - bar_request_type.png
    - bar_server_utilization.png
    - queue_length_over_time.png
    - summary_stats.txt

Usage:
    python data_analysis.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Brand-ish palette (UNO red + neutrals) so all figures look consistent.
COLOR_PRIMARY = "#C8102E"   # UNO red
COLOR_SECONDARY = "#8E9089"  # warm grey
COLOR_ACCENT = "#1F4E79"    # deep blue
COLOR_GREEN = "#2E7D32"
TYPE_COLORS = {
    "QQ": "#1F4E79",
    "SR": "#2E7D32",
    "RA": "#E07B00",
    "LA": "#C8102E",
}
TYPE_LABELS = {
    "QQ": "Quick Question",
    "SR": "Supply / Item Request",
    "RA": "Room Access",
    "LA": "Longer Assistance",
}

# Triangular service-time bounds quoted in the input-analysis section.
TRIANGULAR_BOUNDS = {
    "QQ": (1, 3, 5),
    "SR": (4, 6, 9),
    "RA": (8, 12, 15),
    "LA": (10, 14, 20),
}

OBSERVATION_WINDOW_MIN = 120.0  # 6:00 PM - 8:00 PM


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    obs = pd.read_csv(HERE / "observation_data.csv")
    ia = pd.read_csv(HERE / "interarrival_times.csv")
    return obs, ia


def summarize(obs: pd.DataFrame, ia: pd.DataFrame) -> dict:
    """Compute the per-type and overall summary statistics quoted in the
    presentation's input-data analysis slide and the validation slide."""
    summary: dict = {}

    summary["n_clients"] = len(obs)
    summary["mean_interarrival"] = ia["InterArrivalMin"].mean()
    summary["std_interarrival"] = ia["InterArrivalMin"].std(ddof=1)
    summary["min_interarrival"] = ia["InterArrivalMin"].min()
    summary["max_interarrival"] = ia["InterArrivalMin"].max()
    summary["arrival_rate_per_min"] = 1.0 / summary["mean_interarrival"]
    summary["arrival_rate_per_hour"] = 60.0 / summary["mean_interarrival"]

    summary["mean_wait"] = obs["WaitTimeMin"].mean()
    summary["max_wait"] = obs["WaitTimeMin"].max()
    summary["mean_service"] = obs["ServiceTimeMin"].mean()

    # Per-type stats.
    by_type = (
        obs.groupby("RequestType")
        .agg(
            count=("ClientNumber", "size"),
            mean_service=("ServiceTimeMin", "mean"),
            min_service=("ServiceTimeMin", "min"),
            max_service=("ServiceTimeMin", "max"),
        )
        .reindex(["QQ", "SR", "RA", "LA"])
    )
    by_type["empirical_prob"] = by_type["count"] / by_type["count"].sum()
    summary["by_type"] = by_type

    # Server utilization. We measure busy time only within [0, 120] so
    # service that bleeds past 8:00 PM is clipped (the observation window
    # genuinely ended at 8:00 PM even if the staff kept working).
    busy_time: dict[str, float] = {"A": 0.0, "B": 0.0}
    counts: dict[str, int] = {"A": 0, "B": 0}
    for _, row in obs.iterrows():
        start = row["ServiceStart"]
        end = min(row["ServiceEnd"], OBSERVATION_WINDOW_MIN)
        if end > start:
            busy_time[row["Server"]] += end - start
        counts[row["Server"]] += 1
    summary["server_busy_min"] = busy_time
    summary["server_clients"] = counts
    summary["server_util"] = {
        s: busy_time[s] / OBSERVATION_WINDOW_MIN for s in ("A", "B")
    }

    # Exponential MLE for inter-arrivals (rate = 1 / mean). Compare to a
    # Kolmogorov-Smirnov test as an informal goodness-of-fit check.
    rate = summary["arrival_rate_per_min"]
    ks_stat, ks_p = stats.kstest(
        ia["InterArrivalMin"].values, "expon", args=(0, 1.0 / rate)
    )
    summary["ks_stat"] = ks_stat
    summary["ks_p"] = ks_p

    return summary


def fig_interarrival_hist(ia: pd.DataFrame, summary: dict) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    values = ia["InterArrivalMin"].values
    bins = np.arange(0, values.max() + 2.0, 1.0)
    ax.hist(values, bins=bins, color=COLOR_PRIMARY, edgecolor="white",
            alpha=0.85, label="Observed inter-arrivals")

    rate = summary["arrival_rate_per_min"]
    x = np.linspace(0, values.max() + 1, 200)
    pdf = rate * np.exp(-rate * x)
    # Scale PDF to histogram counts (bin width = 1, n samples).
    ax.plot(x, pdf * len(values), color="black", linewidth=2.0,
            label=f"Exponential fit (λ = {rate:.3f} / min)")

    ax.set_title(
        "Inter-arrival times at Stephen Center front office\n"
        f"6:00 PM - 8:00 PM, n = {len(values)}; mean = "
        f"{summary['mean_interarrival']:.2f} min"
    )
    ax.set_xlabel("Inter-arrival time (minutes)")
    ax.set_ylabel("Number of clients")
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / "hist_interarrival.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def fig_service_time_by_type(obs: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    types = ["QQ", "SR", "RA", "LA"]
    data = [obs[obs["RequestType"] == t]["ServiceTimeMin"].values for t in types]
    parts = ax.boxplot(
        data,
        tick_labels=[TYPE_LABELS[t] for t in types],
        patch_artist=True,
        widths=0.5,
    )
    for patch, t in zip(parts["boxes"], types):
        patch.set_facecolor(TYPE_COLORS[t])
        patch.set_alpha(0.85)

    # Triangular bounds annotation
    for i, t in enumerate(types, 1):
        a, m, b = TRIANGULAR_BOUNDS[t]
        ax.scatter(i, (a + m + b) / 3.0, marker="D",
                   color="black", zorder=5,
                   label="Triangular mean" if i == 1 else None)

    ax.set_title("Service time by request type (observed n = 30)")
    ax.set_ylabel("Service time (minutes)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper left")
    fig.tight_layout()
    out = FIG_DIR / "hist_service_time_by_type.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def fig_request_type_bar(summary: dict) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    by_type = summary["by_type"]
    types = list(by_type.index)
    probs = by_type["empirical_prob"].values * 100.0
    colors = [TYPE_COLORS[t] for t in types]
    ax.bar(
        [TYPE_LABELS[t] for t in types],
        probs,
        color=colors,
        edgecolor="white",
    )
    for i, p in enumerate(probs):
        ax.text(i, p + 1.5, f"{p:.0f}%", ha="center", fontsize=11)
    ax.set_ylim(0, max(probs) + 10)
    ax.set_title("Empirical request-type mix (n = 30)")
    ax.set_ylabel("Share of clients (%)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    out = FIG_DIR / "bar_request_type.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def fig_server_utilization(summary: dict) -> Path:
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    util = summary["server_util"]
    counts = summary["server_clients"]
    bars = ax.bar(
        ["Server A (lead)", "Server B (helper)"],
        [util["A"] * 100, util["B"] * 100],
        color=[COLOR_PRIMARY, COLOR_ACCENT],
        edgecolor="white",
    )
    for bar, server in zip(bars, ["A", "B"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{bar.get_height():.1f}%\n(n={counts[server]})",
            ha="center", fontsize=11,
        )
    ax.set_ylim(0, 110)
    ax.axhline(100, linestyle="--", color="black", alpha=0.6,
               label="Capacity ceiling (100%)")
    ax.set_title("Server utilization during observation window")
    ax.set_ylabel("Utilization (%)")
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    out = FIG_DIR / "bar_server_utilization.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def fig_queue_length(obs: pd.DataFrame) -> Path:
    """Compute queue length L(t) = number of clients waiting at time t,
    sampled at 0.1-minute resolution, and plot it."""
    times = np.arange(0, OBSERVATION_WINDOW_MIN + 0.1, 0.1)
    L = np.zeros_like(times)
    for _, row in obs.iterrows():
        # Client is in the queue from arrival until service starts.
        in_q = (times >= row["ArrivalTime"]) & (times < row["ServiceStart"])
        L[in_q] += 1

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(times, L, color=COLOR_PRIMARY, linewidth=1.5)
    ax.fill_between(times, 0, L, color=COLOR_PRIMARY, alpha=0.25)
    ax.set_title(
        f"Observed queue length over time\n"
        f"mean L_q = {L.mean():.2f} clients, max = {int(L.max())}"
    )
    ax.set_xlabel("Minutes since 6:00 PM")
    ax.set_ylabel("Clients waiting")
    ax.set_xlim(0, OBSERVATION_WINDOW_MIN)
    ax.grid(linestyle="--", alpha=0.4)
    fig.tight_layout()
    out = FIG_DIR / "queue_length_over_time.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def fig_scenario_comparison() -> Path:
    """Bar chart comparing key metrics across the three scenarios.

    These values come from the AnyLogic simulation experiments described
    in the build guide and the presentation's results slides. The base
    model is calibrated to match the observation window; the two
    improvement scenarios are run in AnyLogic with 30 replications each.
    """
    time_metrics = ["Avg wait", "Max wait", "Avg queue\n(clients)"]
    base_time = [4.4, 11.0, 1.6]
    imp1_time = [2.7, 7.0, 1.0]
    imp2_time = [1.5, 5.0, 0.5]
    base_util = 95.0
    imp1_util = 82.0
    imp2_util = 67.0

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11.0, 4.8), gridspec_kw={"width_ratios": [3, 1.3]}
    )

    x = np.arange(len(time_metrics))
    width = 0.27
    ax1.bar(x - width, base_time, width,
            label="Base (1 shared queue, 2 servers)",
            color=COLOR_PRIMARY, edgecolor="white")
    ax1.bar(x, imp1_time, width, label="Imp. 1: dedicated lanes",
            color=COLOR_ACCENT, edgecolor="white")
    ax1.bar(x + width, imp2_time, width, label="Imp. 2: 3 servers at peak",
            color=COLOR_GREEN, edgecolor="white")
    for xi, vals in zip(x, zip(base_time, imp1_time, imp2_time)):
        for offset, v in zip([-width, 0, width], vals):
            ax1.text(xi + offset, v + 0.2, f"{v:.1f}",
                     ha="center", fontsize=9)
    ax1.set_xticks(x)
    ax1.set_xticklabels(time_metrics)
    ax1.set_ylabel("Minutes / clients")
    ax1.set_title("Wait and queue metrics")
    ax1.set_ylim(0, max(base_time + imp1_time + imp2_time) + 2)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.legend(loc="upper right", fontsize=9)

    util_x = np.array([0])
    ax2.bar(util_x - width, [base_util], width, color=COLOR_PRIMARY,
            edgecolor="white")
    ax2.bar(util_x, [imp1_util], width, color=COLOR_ACCENT, edgecolor="white")
    ax2.bar(util_x + width, [imp2_util], width, color=COLOR_GREEN,
            edgecolor="white")
    for offset, v in zip([-width, 0, width], [base_util, imp1_util, imp2_util]):
        ax2.text(util_x[0] + offset, v + 1.5, f"{v:.0f}%",
                 ha="center", fontsize=9)
    ax2.set_xticks(util_x)
    ax2.set_xticklabels(["Avg server\nutilization"])
    ax2.set_ylabel("Utilization (%)")
    ax2.set_title("Server load")
    ax2.set_ylim(0, 110)
    ax2.axhline(100, linestyle="--", color="black", alpha=0.5)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    fig.suptitle("Scenario comparison: base vs. dedicated lanes vs. extra staff",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    out = FIG_DIR / "scenario_comparison.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_system_flow_diagram() -> Path:
    """Simple block diagram of the real-world system: arrival → queue →
    one of two servers → exit. Used on the System Description slide."""
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(10.0, 4.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    def box(x, y, w, h, label, color):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.18",
            linewidth=1.5, edgecolor=color, facecolor="white",
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=11, color=color, fontweight="bold")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=1.6, color="black"))

    box(0.2, 1.4, 1.7, 1.2, "Client\narrives", COLOR_ACCENT)
    box(2.4, 1.4, 1.7, 1.2, "Shared\nFIFO queue", COLOR_PRIMARY)
    box(4.6, 2.5, 1.7, 1.0, "Server A\n(lead staff)", COLOR_GREEN)
    box(4.6, 0.5, 1.7, 1.0, "Server B\n(helper)", COLOR_GREEN)
    box(6.8, 1.4, 1.7, 1.2, "Service\ncomplete", COLOR_ACCENT)
    box(9.0, 1.4, 0.9, 1.2, "Exit", COLOR_SECONDARY)

    arrow(1.9, 2.0, 2.4, 2.0)
    arrow(4.1, 2.0, 4.6, 3.0)
    arrow(4.1, 2.0, 4.6, 1.0)
    arrow(6.3, 3.0, 6.8, 2.2)
    arrow(6.3, 1.0, 6.8, 1.8)
    arrow(8.5, 2.0, 9.0, 2.0)

    ax.set_title("Stephen Center front-office service system "
                 "(2 servers, 1 shared FIFO queue)",
                 fontsize=12)
    fig.tight_layout()
    out = FIG_DIR / "system_flow_diagram.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_anylogic_flowchart() -> Path:
    """Stylized rendering of the AnyLogic process flowchart (Source ->
    SelectOutput -> Queue -> Service -> Sink) for Slide 8."""
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(11.0, 2.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 2.6)
    ax.axis("off")

    def block(x, y, w, h, name, label, color):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=1.5, edgecolor=color, facecolor=color, alpha=0.18,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.7, name, ha="center", va="center",
                fontsize=10, color=color, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.3, label, ha="center", va="center",
                fontsize=8.5, color="black")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))

    block(0.1, 1.3, 1.7, 1.0, "Source",
          "exponential(1/3.9)", COLOR_PRIMARY)
    block(2.1, 1.3, 1.8, 1.0, "SelectOutput5",
          "0.37 / 0.27 /\n0.20 / 0.16", COLOR_ACCENT)
    block(4.2, 1.3, 1.6, 1.0, "Queue",
          "FIFO, cap 20", COLOR_GREEN)
    block(6.1, 1.3, 1.8, 1.0, "Service",
          "2 servers,\nagent.serviceTime", COLOR_PRIMARY)
    block(8.2, 1.3, 1.6, 1.0, "Sink",
          "totalServed++", COLOR_SECONDARY)

    arrow(1.8, 1.8, 2.1, 1.8)
    arrow(3.9, 1.8, 4.2, 1.8)
    arrow(5.8, 1.8, 6.1, 1.8)
    arrow(7.9, 1.8, 8.2, 1.8)

    # Annotation under SelectOutput showing what each branch does.
    ax.text(3.0, 0.85, "On exit (per branch):", fontsize=9,
            ha="center", style="italic")
    ax.text(3.0, 0.4,
            "QQ -> tri(1,3,5)   SR -> tri(4,6,9)\n"
            "RA -> tri(8,12,15)  LA -> tri(10,14,20)",
            fontsize=9, ha="center", color=COLOR_ACCENT)

    ax.set_title("Base-model AnyLogic flowchart: Source -> SelectOutput "
                 "-> Queue -> Service -> Sink", fontsize=12)
    fig.tight_layout()
    out = FIG_DIR / "anylogic_flowchart.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_imp1_flowchart() -> Path:
    """Mini-diagram of the dedicated quick-service lane (Imp. 1) used
    on the Improvement 1 slide."""
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(6.0, 4.5))
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    def block(x, y, w, h, name, sub, color):
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=1.5, edgecolor=color, facecolor=color, alpha=0.18,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.66, name, ha="center", va="center",
                fontsize=10, color=color, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                fontsize=8.5, color="black")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color="black"))

    block(0.1, 1.9, 1.35, 0.9, "Source", "exp(1/3.9)", COLOR_PRIMARY)
    block(1.65, 1.9, 1.6, 0.9, "SelectOutput",
          "by request type", COLOR_ACCENT)
    block(3.45, 3.0, 1.5, 0.9, "Queue A\n+ Server A",
          "QQ + SR (short)", COLOR_GREEN)
    block(3.45, 0.8, 1.5, 0.9, "Queue B\n+ Server B",
          "RA + LA (long)", COLOR_GREEN)
    block(5.05, 1.9, 0.85, 0.9, "Sink", "exit", COLOR_SECONDARY)

    arrow(1.45, 2.35, 1.65, 2.35)
    arrow(3.25, 2.35, 3.45, 3.45)
    arrow(3.25, 2.35, 3.45, 1.25)
    arrow(4.95, 3.45, 5.05, 2.45)
    arrow(4.95, 1.25, 5.05, 2.25)

    ax.set_title("Improvement 1: dedicated quick-service lane",
                 fontsize=11, color=COLOR_SECONDARY, fontweight="bold")
    fig.tight_layout()
    out = FIG_DIR / "imp1_flowchart.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def write_summary_text(summary: dict) -> Path:
    out = FIG_DIR / "summary_stats.txt"
    lines: list[str] = []
    lines.append("Stephen Center front-office observation - summary statistics")
    lines.append("=" * 64)
    lines.append(f"Observation window: 6:00 PM - 8:00 PM (120 min)")
    lines.append(f"Clients observed:   {summary['n_clients']}")
    lines.append("")
    lines.append("Inter-arrival times (n = 29):")
    lines.append(f"  mean = {summary['mean_interarrival']:.3f} min  "
                 f"std = {summary['std_interarrival']:.3f} min")
    lines.append(f"  min  = {summary['min_interarrival']:.2f} min  "
                 f"max = {summary['max_interarrival']:.2f} min")
    lines.append(f"  arrival rate lambda = {summary['arrival_rate_per_min']:.3f}"
                 f" / min  ({summary['arrival_rate_per_hour']:.1f} / hour)")
    lines.append(f"  KS test vs. Exp(lambda):  D = {summary['ks_stat']:.3f}, "
                 f"p = {summary['ks_p']:.3f}")
    lines.append("")
    lines.append("Wait and service times:")
    lines.append(f"  mean wait = {summary['mean_wait']:.2f} min  "
                 f"max wait = {summary['max_wait']:.2f} min")
    lines.append(f"  mean service = {summary['mean_service']:.2f} min")
    lines.append("")
    lines.append("By request type:")
    lines.append(summary["by_type"].round(2).to_string())
    lines.append("")
    lines.append("Server utilization (clipped to [0, 120] min):")
    for s in ("A", "B"):
        lines.append(f"  Server {s}: {summary['server_clients'][s]} clients,"
                     f" busy {summary['server_busy_min'][s]:.1f} min"
                     f"  ->  utilization {summary['server_util'][s]*100:.1f}%")
    out.write_text("\n".join(lines) + "\n")
    return out


def main() -> None:
    obs, ia = load_data()
    summary = summarize(obs, ia)

    paths = [
        fig_interarrival_hist(ia, summary),
        fig_service_time_by_type(obs),
        fig_request_type_bar(summary),
        fig_server_utilization(summary),
        fig_queue_length(obs),
        fig_scenario_comparison(),
        fig_system_flow_diagram(),
        fig_anylogic_flowchart(),
        fig_imp1_flowchart(),
        write_summary_text(summary),
    ]
    print("Wrote:")
    for p in paths:
        print(f"  {p.relative_to(HERE)}")


if __name__ == "__main__":
    main()
