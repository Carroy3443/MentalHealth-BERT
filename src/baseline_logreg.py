"""Baseline 1: Logistic Regression over TF-IDF features.

This is the bag-of-words / context-free baseline: each document is
represented as a sparse vector of weighted word and bigram counts,
ignoring word order and surrounding context. It establishes a lower
bound that the sequence and attention models must beat to justify their
extra parameters and compute cost.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .data import Splits, make_splits
from .evaluate import (
    FIGURE_DIR,
    compute_metrics,
    per_class_metrics,
    plot_confusion_matrix,
    update_metrics,
)


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    max_features=50000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    C=1.0,
                    max_iter=2000,
                    n_jobs=-1,
                    class_weight="balanced",
                    solver="lbfgs",
                ),
            ),
        ]
    )


def train_and_evaluate(splits: Splits) -> Tuple[Pipeline, Dict[str, Dict]]:
    pipe = build_pipeline()
    pipe.fit(splits.x_train, splits.y_train)

    val_pred = pipe.predict(splits.x_val)
    test_pred = pipe.predict(splits.x_test)

    metrics = {
        "val": compute_metrics(splits.y_val, val_pred),
        "test": compute_metrics(splits.y_test, test_pred),
        "per_class": per_class_metrics(splits.y_test, test_pred),
    }
    plot_confusion_matrix(
        splits.y_test,
        test_pred,
        title="Logistic Regression (TF-IDF) — test set",
        out_path=FIGURE_DIR / "cm_logreg.png",
    )
    update_metrics("LogReg-TFIDF", metrics)
    return pipe, metrics


def main(per_class: int = 2000, seed: int = 42) -> None:
    splits = make_splits(per_class=per_class, seed=seed)
    print(f"Train={len(splits.x_train)} Val={len(splits.x_val)} Test={len(splits.x_test)}")
    _, metrics = train_and_evaluate(splits)
    print("LogReg test metrics:", metrics["test"])


if __name__ == "__main__":
    main()
