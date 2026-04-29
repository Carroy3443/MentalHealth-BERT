#!/usr/bin/env bash
# Build the paper PDF from main.tex + refs.bib.
# Run from the repo root or from paper/.

set -euo pipefail
cd "$(dirname "$0")"

# Generate LaTeX result tables from results/metrics.json.
python ../scripts/make_paper_tables.py

# Compile.
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
echo "OK: paper/main.pdf"
