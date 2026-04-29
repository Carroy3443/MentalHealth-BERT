"""Data loading and preprocessing for the mental-health text classification task.

The corpus is the public Hugging Face dataset
``ihsansaad24/Mental-Health_Text-Classification_Dataset`` (4-class:
Anxiety, Depression, Normal, Suicidal). The training file is naturally
unbalanced; the test file is strictly balanced (248 examples per class).

To keep BERT fine-tuning tractable on CPU and to keep all three models
directly comparable, we take a class-balanced subsample of the training
corpus.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from sklearn.model_selection import train_test_split

DATASET_REPO = "ihsansaad24/Mental-Health_Text-Classification_Dataset"
TRAIN_FILE = "mental_heath_unbanlanced.csv"
TEST_FILE = "mental_health_combined_test.csv"

LABELS = ["Anxiety", "Depression", "Normal", "Suicidal"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for label, i in LABEL2ID.items()}
NUM_CLASSES = len(LABELS)

_WS_RE = re.compile(r"\s+")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")


@dataclass
class Splits:
    x_train: np.ndarray
    y_train: np.ndarray
    x_val: np.ndarray
    y_val: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray


def _clean(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = _URL_RE.sub(" ", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = _WS_RE.sub(" ", text).strip()
    return text


def _download() -> Tuple[Path, Path]:
    train_path = Path(hf_hub_download(DATASET_REPO, TRAIN_FILE, repo_type="dataset"))
    test_path = Path(hf_hub_download(DATASET_REPO, TEST_FILE, repo_type="dataset"))
    return train_path, test_path


def load_raw() -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_path, test_path = _download()
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    train_df = train_df[["text", "status"]].dropna()
    test_df = test_df[["text", "status"]].dropna()
    train_df["text"] = train_df["text"].astype(str).map(_clean)
    test_df["text"] = test_df["text"].astype(str).map(_clean)
    train_df = train_df[train_df["text"].str.len() > 0]
    test_df = test_df[test_df["text"].str.len() > 0]
    train_df = train_df[train_df["status"].isin(LABELS)]
    test_df = test_df[test_df["status"].isin(LABELS)]
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def make_splits(
    per_class: int = 2000,
    val_size: float = 0.1,
    seed: int = 42,
) -> Splits:
    """Build a balanced subsample from the (unbalanced) training file.

    For each of the four classes we sample ``per_class`` examples without
    replacement (capped at the available count for that class), then split
    off ``val_size`` for validation in a class-stratified manner. The
    held-out test set is the dataset's own balanced test file (248 per
    class) and is never touched during training.
    """
    rng = np.random.default_rng(seed)
    train_df, test_df = load_raw()

    chunks = []
    for label in LABELS:
        sub = train_df[train_df["status"] == label]
        n = min(per_class, len(sub))
        idx = rng.choice(len(sub), size=n, replace=False)
        chunks.append(sub.iloc[idx])
    balanced = pd.concat(chunks, ignore_index=True).sample(
        frac=1.0, random_state=seed
    ).reset_index(drop=True)

    y = balanced["status"].map(LABEL2ID).to_numpy()
    x = balanced["text"].to_numpy()

    x_train, x_val, y_train, y_val = train_test_split(
        x, y, test_size=val_size, random_state=seed, stratify=y
    )

    y_test = test_df["status"].map(LABEL2ID).to_numpy()
    x_test = test_df["text"].to_numpy()

    return Splits(
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        x_test=x_test,
        y_test=y_test,
    )


def class_distribution(y: np.ndarray) -> dict:
    unique, counts = np.unique(y, return_counts=True)
    return {ID2LABEL[int(u)]: int(c) for u, c in zip(unique, counts)}
