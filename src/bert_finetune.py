"""Attention model: fine-tuned DistilBERT.

DistilBERT is a distilled variant of BERT-base that retains 97% of
BERT's GLUE performance while running roughly 60% faster and using 40%
fewer parameters. It preserves the multi-head self-attention mechanism
that defines the BERT family — every output token attends, through
scaled dot-product attention, to every input token in the same
sequence. We use DistilBERT here for compute reasons (CPU training);
the fine-tuning recipe — load pretrained weights, append a small
classification head over the [CLS] pooled representation, and train
end-to-end with a small learning rate — is identical to the recipe used
for full BERT-base.
"""

from __future__ import annotations

# Force the legacy tf.keras API so the transformers TF stack works smoothly.
import os

os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

from typing import Dict, Tuple

import numpy as np
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification

from .data import ID2LABEL, LABEL2ID, NUM_CLASSES, Splits, make_splits
from .evaluate import (
    FIGURE_DIR,
    compute_metrics,
    per_class_metrics,
    plot_confusion_matrix,
    update_metrics,
)

MODEL_NAME = "distilbert-base-uncased"
SEQ_LEN = 64
BATCH_SIZE = 16
EPOCHS = 2
LR = 2e-5


def encode(tokenizer, texts):
    return tokenizer(
        list(texts),
        padding="max_length",
        truncation=True,
        max_length=SEQ_LEN,
        return_tensors="tf",
    )


def to_dataset(enc, labels, batch_size, shuffle=False, seed=42):
    ds = tf.data.Dataset.from_tensor_slices(
        ({"input_ids": enc["input_ids"], "attention_mask": enc["attention_mask"]}, labels)
    )
    if shuffle:
        ds = ds.shuffle(buffer_size=min(len(labels), 4096), seed=seed)
    return ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)


def build_model():
    model = TFAutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_CLASSES,
        id2label={i: lbl for i, lbl in ID2LABEL.items()},
        label2id={lbl: i for lbl, i in LABEL2ID.items()},
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy(name="accuracy")],
    )
    return model


def _predict(model, ds) -> np.ndarray:
    logits = model.predict(ds, verbose=0).logits
    return np.argmax(logits, axis=1)


def train_and_evaluate(splits: Splits, seed: int = 42) -> Tuple[object, Dict[str, Dict]]:
    tf.random.set_seed(seed)
    np.random.seed(seed)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    enc_train = encode(tokenizer, splits.x_train)
    enc_val = encode(tokenizer, splits.x_val)
    enc_test = encode(tokenizer, splits.x_test)

    train_ds = to_dataset(enc_train, splits.y_train, BATCH_SIZE, shuffle=True, seed=seed)
    val_ds = to_dataset(enc_val, splits.y_val, BATCH_SIZE)
    test_ds = to_dataset(enc_test, splits.y_test, BATCH_SIZE)

    model = build_model()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=1, restore_best_weights=True
        )
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=2,
    )

    val_pred = _predict(model, val_ds)
    test_pred = _predict(model, test_ds)

    metrics = {
        "val": compute_metrics(splits.y_val, val_pred),
        "test": compute_metrics(splits.y_test, test_pred),
        "per_class": per_class_metrics(splits.y_test, test_pred),
        "history": {
            k: [float(v) for v in vs] for k, vs in history.history.items()
        },
    }
    plot_confusion_matrix(
        splits.y_test,
        test_pred,
        title="Fine-tuned DistilBERT — test set",
        out_path=FIGURE_DIR / "cm_bert.png",
    )
    update_metrics("BERT-FineTuned", metrics)
    return model, metrics


def main(per_class: int = 2000, seed: int = 42) -> None:
    splits = make_splits(per_class=per_class, seed=seed)
    _, metrics = train_and_evaluate(splits, seed=seed)
    print("BERT test metrics:", metrics["test"])


if __name__ == "__main__":
    main()
