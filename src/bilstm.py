"""Baseline 2: Bidirectional LSTM over learned word embeddings.

This is the older sequence model in the comparison: each token is mapped
to a learned dense vector, the resulting sequence is read forward and
backward by an LSTM, and the final hidden states are pooled for
classification. Unlike TF-IDF, the BiLSTM has access to word order, so
it can model short-range context. Unlike the transformer, it has no
self-attention: information must flow through the recurrent state, which
limits how well it can use long-range or non-local context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

from .data import NUM_CLASSES, Splits, make_splits
from .evaluate import (
    FIGURE_DIR,
    compute_metrics,
    per_class_metrics,
    plot_confusion_matrix,
    update_metrics,
)

VOCAB_SIZE = 20000
SEQ_LEN = 64
EMBED_DIM = 128
LSTM_UNITS = 64
BATCH_SIZE = 64
EPOCHS = 6
LR = 1e-3


def build_text_vectorizer(train_texts) -> layers.TextVectorization:
    vectorizer = layers.TextVectorization(
        max_tokens=VOCAB_SIZE,
        output_mode="int",
        output_sequence_length=SEQ_LEN,
        standardize="lower_and_strip_punctuation",
    )
    vectorizer.adapt(np.asarray(train_texts, dtype=object))
    return vectorizer


def build_model() -> models.Model:
    inputs = tf.keras.Input(shape=(SEQ_LEN,), dtype=tf.int32, name="tokens")
    x = layers.Embedding(
        input_dim=VOCAB_SIZE,
        output_dim=EMBED_DIM,
        mask_zero=True,
        name="embedding",
    )(inputs)
    x = layers.Bidirectional(layers.LSTM(LSTM_UNITS, return_sequences=True))(x)
    x = layers.GlobalMaxPooling1D()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)
    model = models.Model(inputs, outputs, name="BiLSTM")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _vectorize(vectorizer, texts) -> np.ndarray:
    return vectorizer(np.asarray(texts, dtype=object)).numpy()


def train_and_evaluate(splits: Splits, seed: int = 42) -> Tuple[models.Model, Dict[str, Dict]]:
    tf.random.set_seed(seed)
    np.random.seed(seed)

    vectorizer = build_text_vectorizer(splits.x_train)
    model = build_model()

    x_train = _vectorize(vectorizer, splits.x_train)
    x_val = _vectorize(vectorizer, splits.x_val)
    x_test = _vectorize(vectorizer, splits.x_test)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=2, restore_best_weights=True
        )
    ]

    history = model.fit(
        x_train,
        splits.y_train,
        validation_data=(x_val, splits.y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=2,
    )

    val_pred = np.argmax(model.predict(x_val, batch_size=BATCH_SIZE, verbose=0), axis=1)
    test_pred = np.argmax(model.predict(x_test, batch_size=BATCH_SIZE, verbose=0), axis=1)

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
        title="BiLSTM — test set",
        out_path=FIGURE_DIR / "cm_bilstm.png",
    )
    update_metrics("BiLSTM", metrics)
    return model, metrics


def main(per_class: int = 2000, seed: int = 42) -> None:
    splits = make_splits(per_class=per_class, seed=seed)
    _, metrics = train_and_evaluate(splits, seed=seed)
    print("BiLSTM test metrics:", metrics["test"])


if __name__ == "__main__":
    main()
