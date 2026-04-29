# Attention-Based NLP for Mental-Health Text Classification

A capstone study comparing three text-classification approaches —
TF-IDF + Logistic Regression, a Bidirectional LSTM, and a fine-tuned
DistilBERT (an attention-based transformer) — on a four-class
mental-health corpus (`Anxiety`, `Depression`, `Normal`, `Suicidal`).

> **Disclaimer.** This project is an academic exercise. The trained
> models are **not** clinical decision tools. They must not be used to
> screen, diagnose, triage, or otherwise make decisions about real
> people. If you or someone you know is in crisis, contact the 988
> Suicide and Crisis Lifeline (US) or your local emergency number.

---

## Course context

- **Course**: AIML 4970 — AI/ML Capstone (Spring 2026)
- **Topic**: Attention modules / NLP / mental-health text classification
- **Project type**: Application project
- **Research question**: *Can an attention-based transformer model
  improve mental-health text classification compared with simpler
  baseline models?*

---

## Repository layout

```
MentalHealth-BERT/
├── src/
│   ├── data.py              # HF dataset loader, cleaning, balanced subsampling
│   ├── baseline_logreg.py   # TF-IDF + Logistic Regression baseline
│   ├── bilstm.py            # Keras BiLSTM model
│   ├── bert_finetune.py     # DistilBERT fine-tuning (Keras)
│   └── evaluate.py          # metrics, confusion matrices, comparison plots
├── scripts/
│   └── run_all.py           # end-to-end runner (trains + evaluates all models)
├── results/
│   ├── metrics.json         # all metrics (val + test, per class, history)
│   └── figures/             # confusion matrices and comparison plots
├── paper/
│   ├── main.tex             # IEEE-style report source
│   └── main.pdf             # compiled paper (8 pages excl. references)
├── requirements.txt
└── README.md
```

---

## Dataset

We use the public Hugging Face dataset
[`ihsansaad24/Mental-Health_Text-Classification_Dataset`](https://huggingface.co/datasets/ihsansaad24/Mental-Health_Text-Classification_Dataset),
a 4-class corpus assembled and re-labeled from three public mental-health
text resources. Labels: `Anxiety`, `Depression`, `Normal`, `Suicidal`.

- Training file (`mental_heath_unbanlanced.csv`): 49,612 examples,
  naturally unbalanced.
- Test file (`mental_health_combined_test.csv`): 992 examples,
  strictly balanced (248 per class).

To make BERT fine-tuning tractable on CPU and to keep all three models
directly comparable, we draw a **class-balanced subsample of 1,500
examples per class** from the training file (6,000 total), then split
off 10 % for validation in a class-stratified manner. The held-out test
set is the dataset's own balanced 992-example test file and is never
touched during training.

---

## Models

| Model | Representation | Context | Approx. parameters |
|-------|----------------|---------|--------------------|
| Logistic Regression | TF-IDF (uni- + bi-grams, ≤50k features, sublinear TF) | none (bag of words) | ≈ 0.2 M (sparse) |
| BiLSTM | learned word embeddings (dim 128, vocab 20k) | local sequential | ≈ 2.7 M |
| DistilBERT (fine-tuned) | WordPiece tokens + pretrained transformer | full self-attention | ≈ 66 M |

All three classifiers are trained on the *same* 6,000-example balanced
subsample, with the *same* class-stratified 90/10 train/val split, and
evaluated on the *same* 992-example balanced held-out test set.

---

## Reproducing the results

### 1. Set up the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Train and evaluate all three models

```bash
TF_USE_LEGACY_KERAS=1 python -m scripts.run_all --per-class 1500 --seed 42
```

Flags:
- `--per-class N` — number of examples per class to subsample for training (default `2000`)
- `--seed S`     — random seed for subsampling, train/val split, and model init
- `--models {logreg,bilstm,bert}+` — train only a subset of models

The dataset is downloaded (and cached) automatically from the Hugging
Face Hub via `huggingface_hub.hf_hub_download`. No HF token is required
for this public dataset, but setting `HF_TOKEN` will give you a higher
rate limit.

Outputs:
- `results/metrics.json`           — accuracy / precision / recall / F1 (macro and weighted), per-class metrics, training history, and timings
- `results/figures/cm_*.png`       — confusion matrix per model
- `results/figures/comparison_bar.png` — overall comparison bar chart
- `results/figures/per_class_f1.png`   — per-class F1 by model

### 3. Compile the paper

```bash
cd paper
latexmk -pdf main.tex
```

The compiled `paper/main.pdf` is also committed to the repo.

---

## Key design choices

- **Balanced training subsample**: keeps the three models directly
  comparable, controls the substantial class imbalance in the raw
  training file (Normal 18.4k vs. Anxiety 5.5k), and keeps DistilBERT
  fine-tuning tractable on CPU. The held-out balanced test set is the
  dataset's own test file, so test-time results are not affected by
  subsampling.
- **DistilBERT instead of BERT-base**: DistilBERT retains ≈97 % of
  BERT's GLUE performance, with ≈40 % fewer parameters and ≈60 %
  faster inference, and uses the same multi-head self-attention
  architecture. The fine-tuning recipe is identical.
- **Sequence length of 64 WordPiece tokens**: median text length in the
  corpus is 47 whitespace tokens; 64 WordPiece tokens covers the
  majority of examples without paying transformer cost on extremely
  long, rare outliers.
- **Macro-averaged F1 as the headline metric**: in mental-health
  classification, missing a `Suicidal` post is worse than misclassifying
  a `Normal` one. Macro F1 weights all four classes equally; recall is
  also reported per class.

---

## Ethics and safety

This work is academic. The dataset is *user-generated text from public
forums*, not clinical records, and the labels were assigned by other
researchers, not licensed clinicians. The trained models can therefore
**not** be used as a screening, diagnostic, triage, or crisis-detection
tool, and any operational use of mental-health text classifiers
requires (at minimum) clinician oversight, calibrated risk thresholds,
fairness audits across demographic groups, careful handling of false
negatives, and a human-in-the-loop escalation pathway. None of those
are in scope here.

---

## License

MIT License. See `LICENSE` for details.
