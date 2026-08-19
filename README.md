# Snack King — Salty Snacks Category Regression Analysis

A statistical analysis of the salty snacks category (retail syndicated data) built for the **Snack King** case study: cleaning and preparing category-level sales data, then exporting it to SPSS for regression analysis of what drives dollar sales (TDP distribution, unit velocity, growth trends, and category/brand mix).

## Project overview

Retail category data (dollars, TDP, units, velocity, YoY growth, CAGR) is cleaned and filtered, then exported into SPSS `.sav` format — with proper variable labels and value labels for categorical fields (product level, subcategory, brand, unit of measure) — so it can be run through a regression model (`snacks_regression.sps`) to identify the key drivers of sales performance.

## Pipeline

1. **`Scripts/02_export_spss.py`** — Converts a cleaned CSV export into a base SPSS `.sav` file using `pyreadstat`.
   ```bash
   python Scripts/02_export_spss.py -i Exports/snacks_clean.csv -o Exports/snacks_clean.sav
   ```

2. **`Scripts/03_prepare_for_regression.py`** — Filters the cleaned data down to the columns needed for regression (default dependent variable: `dollars`; default predictors: `tdp`, `units`), dropping rows with missing (and optionally zero) values.
   ```bash
   python Scripts/03_prepare_for_regression.py --dep dollars --predictors tdp,units --drop-zero --sav
   ```

3. **`Scripts/04_export_with_metadata.py`** — Takes the regression-ready CSV and writes a fully labeled SPSS `.sav` file: converts date fields, encodes categorical fields (product level, subcategory, brand, unit of measure) into numeric codes with value labels, and attaches human-readable variable labels.
   ```bash
   python Scripts/04_export_with_metadata.py --input Exports/snacks_regression.csv --output Exports/snacks_regression_labeled.sav
   ```

4. **`Scripts/snacks_regression.sps`** — SPSS syntax file that runs the regression analysis on the labeled dataset produced above.

5. **`Scripts/OUTPUT.docx`** — Final write-up / output summary of the regression results.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `pandas`, `numpy`, `pyreadstat`.

## About this project

This is part of a portfolio of data analysis work applying applied statistics and causal/regression methods to real-world business questions — here, understanding what drives dollar sales performance in a retail category.
