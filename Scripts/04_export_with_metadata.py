"""Export the regression CSV to an SPSS .sav with metadata:
- Convert date columns to datetime so SPSS sees them as dates
- Encode selected categorical columns to numeric codes and attach value labels
- Add variable (column) labels for key variables
- Write a labeled .sav ready for SPSS

Usage:
  python Scripts/04_export_with_metadata.py --input Exports/snacks_regression.csv --output Exports/snacks_regression_labeled.sav
"""
import pathlib
import sys
from typing import Dict

import pandas as pd

try:
    import pyreadstat
except Exception:
    pyreadstat = None


def build_value_labels(series: pd.Series) -> Dict[int, str]:
    """Return mapping code->label using pandas categorical codes starting at 1."""
    cat = series.astype("category")
    categories = list(cat.cat.categories)
    # map 1..N to category labels
    return {i + 1: str(label) for i, label in enumerate(categories)}


def main(argv=None):
    import argparse

    p = argparse.ArgumentParser(description="Export regression CSV to SPSS .sav with metadata")
    p.add_argument("-i", "--input", default="Exports/snacks_regression.csv")
    p.add_argument("-o", "--output", default="Exports/snacks_regression_labeled.sav")
    args = p.parse_args(argv)

    inp = pathlib.Path(args.input)
    out = pathlib.Path(args.output)

    if not inp.exists():
        print(f"Input not found: {inp}", file=sys.stderr)
        return 2
    if pyreadstat is None:
        print("pyreadstat is required. Install it in the venv: pip install pyreadstat", file=sys.stderr)
        return 3

    print(f"Loading {inp}...")
    df = pd.read_csv(inp, low_memory=False)
    print(f"Loaded {len(df):,} rows x {len(df.columns)} cols")

    # 1) Convert date columns
    date_cols = ["time_period_end_date", "time_period"]
    for dc in date_cols:
        if dc in df.columns:
            print(f"Converting {dc} to datetime...")
            df[dc] = pd.to_datetime(df[dc], errors="coerce")

    # 2) Prepare categorical encodings and value labels
    cat_cols = ["product_level", "subcategory", "brand", "unit_of_measure"]
    variable_value_labels = {}
    # We'll write new numeric code columns with suffix _code
    for c in cat_cols:
        if c in df.columns:
            s = df[c].fillna("<MISSING>").astype(str)
            s_cat = s.astype("category")
            codes = s_cat.cat.codes + 1  # make codes 1..N
            code_col = f"{c}_code"
            df[code_col] = codes
            variable_value_labels[code_col] = build_value_labels(s_cat)
            print(f"Encoded {c} -> {code_col} (n_levels={len(s_cat.cat.categories)})")

    # 3) Column (variable) labels
    column_labels = {
        "dollars": "Total dollars (USD)",
        "tdp": "TDP (time distribution parameter)",
        "units": "Units sold",
        "velocity_dollars_per_tdp": "Velocity (Dollars per TDP)",
        "growth_1y": "1-year growth (fraction)",
        "cagr_2y": "2-year CAGR (fraction)",
        "time_period_end_date": "Period end date",
        "time_period": "Time period label",
        "upc": "UPC code",
        "brand": "Brand name",
        "product_level": "Product level (string)",
    }

    # 4) Ensure columns we label actually exist in df
    column_labels = {k: v for k, v in column_labels.items() if k in df.columns}

    # 5) Write .sav using pyreadstat with column_labels and variable_value_labels
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing SPSS .sav to {out} with variable labels and value labels (this may take a moment)...")
    # Use the DataFrame including both original string columns and code columns.
    pyreadstat.write_sav(df, str(out), column_labels=column_labels, variable_value_labels=variable_value_labels)

    print("Done: wrote", out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
