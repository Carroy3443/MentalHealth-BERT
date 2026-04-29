"""Generate LaTeX fragments for the paper from results/metrics.json.

Produces:
- paper/tables/overall_metrics.tex
- paper/tables/per_class_f1.tex
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "results" / "metrics.json"
OUT_DIR = ROOT / "paper" / "tables"
LABELS = ["Anxiety", "Depression", "Normal", "Suicidal"]
MODEL_ORDER = ["LogReg-TFIDF", "BiLSTM", "BERT-FineTuned"]
PRETTY = {
    "LogReg-TFIDF": "TF-IDF + LogReg",
    "BiLSTM": "BiLSTM",
    "BERT-FineTuned": "DistilBERT (FT)",
}


def fmt(x: float) -> str:
    return f"{x:.3f}"


def overall_table(metrics):
    rows = []
    rows.append("\\begin{tabular}{lcccc}")
    rows.append("\\toprule")
    rows.append("Model & Accuracy & Precision & Recall & F1 \\\\")
    rows.append("\\midrule")
    for name in MODEL_ORDER:
        if name not in metrics:
            continue
        t = metrics[name]["test"]
        rows.append(
            f"{PRETTY[name]} & {fmt(t['accuracy'])} & "
            f"{fmt(t['precision_macro'])} & {fmt(t['recall_macro'])} & "
            f"{fmt(t['f1_macro'])} \\\\"
        )
    rows.append("\\bottomrule")
    rows.append("\\end{tabular}")
    return "\n".join(rows) + "\n"


def per_class_table(metrics):
    header = " & ".join([""] + LABELS) + " \\\\"
    rows = ["\\begin{tabular}{l" + "c" * len(LABELS) + "}", "\\toprule", header, "\\midrule"]
    for name in MODEL_ORDER:
        if name not in metrics:
            continue
        per = metrics[name]["per_class"]
        cells = [PRETTY[name]] + [fmt(per[lbl]["f1-score"]) for lbl in LABELS]
        rows.append(" & ".join(cells) + " \\\\")
    rows.append("\\bottomrule")
    rows.append("\\end{tabular}\n")
    return "\n".join(rows)


def per_class_recall_table(metrics):
    header = " & ".join([""] + LABELS) + " \\\\"
    rows = ["\\begin{tabular}{l" + "c" * len(LABELS) + "}", "\\toprule", header, "\\midrule"]
    for name in MODEL_ORDER:
        if name not in metrics:
            continue
        per = metrics[name]["per_class"]
        cells = [PRETTY[name]] + [fmt(per[lbl]["recall"]) for lbl in LABELS]
        rows.append(" & ".join(cells) + " \\\\")
    rows.append("\\bottomrule")
    rows.append("\\end{tabular}\n")
    return "\n".join(rows)


def main() -> None:
    metrics = json.loads(METRICS.read_text())
    metrics = {k: v for k, v in metrics.items() if not k.startswith("_")}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "overall_metrics.tex").write_text(overall_table(metrics))
    (OUT_DIR / "per_class_f1.tex").write_text(per_class_table(metrics))
    (OUT_DIR / "per_class_recall.tex").write_text(per_class_recall_table(metrics))
    print(
        f"wrote {OUT_DIR}/overall_metrics.tex, per_class_f1.tex, per_class_recall.tex"
    )


if __name__ == "__main__":
    main()
