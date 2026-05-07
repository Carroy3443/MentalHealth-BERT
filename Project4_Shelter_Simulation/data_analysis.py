"""
Data analysis for Project 4: Stephen Center Shelter Front Office Simulation.

Reads the observation CSVs, computes summary statistics, generates the
charts used in the presentation, and runs a Kolmogorov-Smirnov test for
an exponential fit on the inter-arrival distribution.

Usage
-----
    python data_analysis.py

Outputs (written to ./figures/):
    - interarrival_histogram.png
    - service_time_by_type.png
    - request_type_pie.png
    - service_time_distribution.png
    - scenario_comparison.png

Also prints a text summary that can be copy-pasted into the report.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)

REQUEST_TYPES = ["QQ", "SR", "RA", "LA"]
REQUEST_LABELS = {
    "QQ": "Quick Question",
    "SR": "Supply / Item",
    "RA": "Room Access",
    "LA": "Longer Assistance",
}
TRIANGULAR = {
    "QQ": (1, 3, 5),
    "SR": (4, 6, 9),
    "RA": (8, 12, 15),
    "LA": (10, 14, 20),
}
COLORS = {
    "QQ": "#4C9AFF",
    "SR": "#36B37E",
    "RA": "#FFAB00",
    "LA": "#FF5630",
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    obs = pd.read_csv(HERE / "observation_data.csv")
    inter = pd.read_csv(HERE / "interarrival_times.csv")
    return obs, inter


def summary_stats(obs: pd.DataFrame, inter: pd.DataFrame) -> dict:
    inter_minutes = inter["InterarrivalMinutes"].to_numpy(dtype=float)
    service = obs["ServiceTimeMin"].to_numpy(dtype=float)
    wait = obs["WaitTimeMin"].to_numpy(dtype=float)

    by_type = (
        obs.groupby("RequestType")["ServiceTimeMin"]
        .agg(["count", "mean", "min", "max"])
        .reindex(REQUEST_TYPES)
    )
    by_type["share"] = by_type["count"] / by_type["count"].sum()

    by_server = obs.groupby("Server")["ClientNumber"].count()

    return {
        "n_clients": int(len(obs)),
        "interarrival_mean": float(inter_minutes.mean()),
        "interarrival_std": float(inter_minutes.std(ddof=1)),
        "interarrival_min": float(inter_minutes.min()),
        "interarrival_max": float(inter_minutes.max()),
        "service_mean": float(service.mean()),
        "service_std": float(service.std(ddof=1)),
        "wait_mean": float(wait.mean()),
        "wait_max": float(wait.max()),
        "by_type": by_type,
        "by_server": by_server,
    }


def ks_exponential_test(inter: pd.DataFrame) -> tuple[float, float, float]:
    """Fit an exponential distribution to the inter-arrival times and run KS."""
    x = inter["InterarrivalMinutes"].to_numpy(dtype=float)
    # MLE for exponential location-shifted to 0:
    loc, scale = stats.expon.fit(x, floc=0)
    stat, p = stats.kstest(x, "expon", args=(loc, scale))
    return float(scale), float(stat), float(p)


def plot_interarrival_histogram(inter: pd.DataFrame, mean: float) -> Path:
    x = inter["InterarrivalMinutes"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    bins = np.arange(0.5, x.max() + 1.5, 1.0)
    ax.hist(x, bins=bins, color="#4C9AFF", edgecolor="white", alpha=0.85,
            density=True, label="Observed inter-arrivals")

    # Use the rounded-up "model" mean of 3.9 min that we feed into AnyLogic.
    # The empirical mean is shown only in the printed summary.
    model_mean = 3.9
    grid = np.linspace(0.1, x.max() + 2, 200)
    ax.plot(grid, stats.expon.pdf(grid, loc=0, scale=model_mean),
            color="#172B4D", linewidth=2,
            label=f"Exponential(mean={model_mean:.1f} min)")

    ax.set_title("Inter-Arrival Times (6:00–8:00 PM)")
    ax.set_xlabel("Minutes between arrivals")
    ax.set_ylabel("Density")
    ax.legend(loc="upper right", frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIG_DIR / "interarrival_histogram.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_service_time_by_type(obs: pd.DataFrame) -> Path:
    means = (
        obs.groupby("RequestType")["ServiceTimeMin"].mean().reindex(REQUEST_TYPES)
    )
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    bars = ax.bar(
        [REQUEST_LABELS[t] for t in REQUEST_TYPES],
        means.values,
        color=[COLORS[t] for t in REQUEST_TYPES],
        edgecolor="white",
    )
    for bar, val in zip(bars, means.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.15,
                f"{val:.1f} min", ha="center", va="bottom", fontsize=10)
    ax.set_title("Average Service Time by Request Type")
    ax.set_ylabel("Minutes")
    ax.set_ylim(0, max(means.values) * 1.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIG_DIR / "service_time_by_type.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_request_type_pie(obs: pd.DataFrame) -> Path:
    counts = obs["RequestType"].value_counts().reindex(REQUEST_TYPES)
    fig, ax = plt.subplots(figsize=(5.5, 5.5), dpi=150)
    wedges, _, _ = ax.pie(
        counts.values,
        labels=[f"{REQUEST_LABELS[t]}\n({c} clients)" for t, c in counts.items()],
        autopct="%1.0f%%",
        colors=[COLORS[t] for t in REQUEST_TYPES],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.set_title("Request Type Distribution (n=30)")
    fig.tight_layout()
    out = FIG_DIR / "request_type_pie.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_service_time_distribution() -> Path:
    """Show triangular density curves for each request type side-by-side."""
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    grid = np.linspace(0, 22, 400)
    for t in REQUEST_TYPES:
        a, c, b = TRIANGULAR[t]
        c_norm = (c - a) / (b - a)
        pdf = stats.triang.pdf(grid, c_norm, loc=a, scale=b - a)
        ax.plot(grid, pdf, color=COLORS[t], linewidth=2,
                label=f"{REQUEST_LABELS[t]}: tri({a},{c},{b})")
    ax.set_title("Service Time Distributions by Request Type")
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Density")
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIG_DIR / "service_time_distribution.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_scenario_comparison() -> Path:
    """Bar chart comparing base vs. improvement 1 vs. improvement 2."""
    metrics = ["Avg Wait (min)", "Max Wait (min)", "Avg Queue", "Utilization (%)"]
    base = [4.5, 11.0, 1.5, 85.0]
    imp1 = [2.8, 7.0, 1.0, 82.0]
    imp2 = [1.5, 5.0, 0.5, 68.0]
    x = np.arange(len(metrics))
    width = 0.27

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    b1 = ax.bar(x - width, base, width, color="#4C9AFF", label="Base")
    b2 = ax.bar(x, imp1, width, color="#36B37E", label="Dedicated Lanes")
    b3 = ax.bar(x + width, imp2, width, color="#FFAB00", label="3rd Staff")

    for bars in (b1, b2, b3):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.0,
                    f"{bar.get_height():.1f}", ha="center", va="bottom",
                    fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_title("Scenario Comparison (30 replications, 120 min each)")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    out = FIG_DIR / "scenario_comparison.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def print_summary(stats_dict: dict, ks: tuple[float, float, float]) -> None:
    print("=" * 60)
    print("Stephen Center Shelter Front Office — Data Summary")
    print("=" * 60)
    print(f"Clients observed:           {stats_dict['n_clients']}")
    print(f"Mean inter-arrival time:    {stats_dict['interarrival_mean']:.2f} min "
          f"(sd {stats_dict['interarrival_std']:.2f})")
    print(f"Inter-arrival range:        {stats_dict['interarrival_min']:.0f}"
          f"–{stats_dict['interarrival_max']:.0f} min")
    print(f"Mean service time:          {stats_dict['service_mean']:.2f} min "
          f"(sd {stats_dict['service_std']:.2f})")
    print(f"Mean wait time:             {stats_dict['wait_mean']:.2f} min "
          f"(max {stats_dict['wait_max']:.0f})")
    print()
    print("By request type:")
    print(stats_dict["by_type"].round(2))
    print()
    print("Clients served per server:")
    print(stats_dict["by_server"])
    print()
    scale, stat, p = ks
    print(f"Exponential fit: lambda^-1 = {scale:.2f} min")
    print(f"Kolmogorov-Smirnov: D = {stat:.3f}, p = {p:.3f}")
    if p > 0.05:
        print("=> Fail to reject H0: inter-arrivals are consistent with Exponential.")
    else:
        print("=> Reject H0: deviation from Exponential is statistically detectable.")


def main() -> None:
    obs, inter = load_data()
    stats_dict = summary_stats(obs, inter)
    ks = ks_exponential_test(inter)

    paths = [
        plot_interarrival_histogram(inter, stats_dict["interarrival_mean"]),
        plot_service_time_by_type(obs),
        plot_request_type_pie(obs),
        plot_service_time_distribution(),
        plot_scenario_comparison(),
    ]
    print_summary(stats_dict, ks)
    print()
    print("Figures written:")
    for p in paths:
        print(f"  - {p.relative_to(HERE)}")


if __name__ == "__main__":
    main()
