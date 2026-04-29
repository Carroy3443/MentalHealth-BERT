"""Evaluation utilities: metrics, confusion matrices, and comparison plots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from .data import LABELS

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
FIGURE_DIR = RESULTS_DIR / "figures"
METRICS_PATH = RESULTS_DIR / "metrics.json"


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(
            f1_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
    }


def per_class_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Dict[str, float]]:
    report = classification_report(
        y_true,
        y_pred,
        target_names=LABELS,
        labels=list(range(len(LABELS))),
        zero_division=0,
        output_dict=True,
    )
    return {label: report[label] for label in LABELS}


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    title: str,
    out_path: Path,
) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(LABELS))))
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    sns.heatmap(
        cm_norm,
        annot=cm,
        fmt="d",
        cmap="Blues",
        xticklabels=LABELS,
        yticklabels=LABELS,
        cbar=False,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def save_metrics(all_metrics: Mapping[str, Mapping]) -> None:
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(all_metrics, indent=2))


def load_metrics() -> Dict[str, Dict]:
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text())


def update_metrics(model_name: str, metrics: Mapping) -> Dict[str, Dict]:
    all_metrics = load_metrics()
    all_metrics[model_name] = dict(metrics)
    save_metrics(all_metrics)
    return all_metrics


def plot_comparison_bar(
    metrics_by_model: Mapping[str, Mapping[str, float]],
    metric_keys: Iterable[str] = ("accuracy", "precision_macro", "recall_macro", "f1_macro"),
    out_path: Path = FIGURE_DIR / "comparison_bar.png",
) -> None:
    models = list(metrics_by_model.keys())
    keys = list(metric_keys)
    values = np.array(
        [[metrics_by_model[m]["test"][k] for k in keys] for m in models]
    )
    x = np.arange(len(models))
    width = 0.2
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for i, k in enumerate(keys):
        ax.bar(x + (i - (len(keys) - 1) / 2) * width, values[:, i], width, label=k)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)
    ax.set_title("Test-set performance by model")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_per_class_f1(
    metrics_by_model: Mapping[str, Mapping],
    out_path: Path = FIGURE_DIR / "per_class_f1.png",
) -> None:
    models = list(metrics_by_model.keys())
    f1_table = np.array(
        [
            [metrics_by_model[m]["per_class"][label]["f1-score"] for label in LABELS]
            for m in models
        ]
    )
    x = np.arange(len(LABELS))
    width = 0.25
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for i, m in enumerate(models):
        ax.bar(x + (i - (len(models) - 1) / 2) * width, f1_table[i], width, label=m)
    ax.set_xticks(x)
    ax.set_xticklabels(LABELS)
    ax.set_ylim(0, 1)
    ax.set_ylabel("F1 score")
    ax.set_title("Per-class F1 score by model")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
