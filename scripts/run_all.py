"""End-to-end runner: trains all three models on the same balanced subsample
and writes metrics + figures to results/.

Usage:
    python -m scripts.run_all --per-class 2000 --seed 42
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.baseline_logreg import train_and_evaluate as run_logreg
from src.bert_finetune import train_and_evaluate as run_bert
from src.bilstm import train_and_evaluate as run_bilstm
from src.data import class_distribution, make_splits
from src.evaluate import (
    FIGURE_DIR,
    METRICS_PATH,
    load_metrics,
    plot_comparison_bar,
    plot_per_class_f1,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-class", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--models",
        nargs="+",
        default=["logreg", "bilstm", "bert"],
        choices=["logreg", "bilstm", "bert"],
    )
    args = parser.parse_args()

    splits = make_splits(per_class=args.per_class, seed=args.seed)
    print(
        f"Train={len(splits.x_train)}  Val={len(splits.x_val)}  Test={len(splits.x_test)}"
    )
    print("Train class distribution:", class_distribution(splits.y_train))
    print("Test class distribution :", class_distribution(splits.y_test))

    timings = {}
    if "logreg" in args.models:
        t0 = time.time()
        run_logreg(splits)
        timings["LogReg-TFIDF"] = time.time() - t0
    if "bilstm" in args.models:
        t0 = time.time()
        run_bilstm(splits, seed=args.seed)
        timings["BiLSTM"] = time.time() - t0
    if "bert" in args.models:
        t0 = time.time()
        run_bert(splits, seed=args.seed)
        timings["BERT-FineTuned"] = time.time() - t0

    metrics = load_metrics()
    metrics.setdefault("_run", {})["timings_seconds"] = {
        k: round(v, 1) for k, v in timings.items()
    }
    metrics["_run"]["per_class_train_samples"] = args.per_class
    metrics["_run"]["seed"] = args.seed
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    model_metrics = {k: v for k, v in metrics.items() if not k.startswith("_")}
    if model_metrics:
        plot_comparison_bar(model_metrics)
        plot_per_class_f1(model_metrics)

    print(f"Results written to {METRICS_PATH}")
    print(f"Figures written to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
