"""Prepare cleaned data for regression by removing rows with missing values in key columns.

Usage examples:
  python Scripts/03_prepare_for_regression.py 
  python Scripts/03_prepare_for_regression.py --dep dollars --predictors tdp,units --drop-zero --sav

Defaults:
  dep = dollars
  predictors = tdp,units

The script writes:
  Exports/snacks_regression.csv
  Exports/snacks_regression.sav  (if --sav)
"""
import argparse
import pathlib
import sys
from typing import List

import pandas as pd

try:
    import pyreadstat
except Exception:
    pyreadstat = None


def normalize_name(s: str) -> str:
    return s.strip().lower().replace(" ", "_")


def main(argv: List[str] = None) -> int:
    p = argparse.ArgumentParser(description="Filter cleaned data for regression (drop rows missing key cols)")
    p.add_argument("-i", "--input", default="Exports/snacks_clean.csv", help="Input cleaned CSV")
    p.add_argument("-o", "--output", default="Exports/snacks_regression.csv", help="Output CSV")
    p.add_argument("--dep", default="dollars", help="Dependent variable (default: dollars)")
    p.add_argument("--predictors", default="tdp,units", help="Comma-separated predictor columns (default: tdp,units)")
    p.add_argument("--drop-zero", action="store_true", help="Also drop rows where dep or predictors are exactly zero")
    p.add_argument("--sav", action="store_true", help="Also write an SPSS .sav file alongside the CSV (requires pyreadstat)")
    args = p.parse_args(argv)

    inp = pathlib.Path(args.input)
    out = pathlib.Path(args.output)

    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        return 2

    df = pd.read_csv(inp, low_memory=False)
    print(f"Loaded cleaned data: {df.shape[0]:,} rows x {df.shape[1]} cols")

    dep = normalize_name(args.dep)
    preds = [normalize_name(x) for x in args.predictors.split(",") if x.strip()]

    # map provided names to existing columns (try fuzzy match: exact or substring)
    cols_map = {c.lower(): c for c in df.columns}

    def find_col(name: str):
        if name in cols_map:
            return cols_map[name]
        # try substring match
        for k, orig in cols_map.items():
            if name in k:
                return orig
        return None

    dep_col = find_col(dep)
    pred_cols = [find_col(p) for p in preds]

    missing = [p for p, col in zip([dep] + preds, [dep_col] + pred_cols) if col is None]
    if missing:
        print("Warning: the following requested columns were not found in the data:", missing, file=sys.stderr)
        print("Available sample columns:", list(df.columns)[:20], file=sys.stderr)

    required = [c for c in [dep_col] + pred_cols if c]
    if not required:
        print("No matching required columns found; aborting.", file=sys.stderr)
        return 2

    before = len(df)
    df_filtered = df.dropna(subset=required)

    if args.drop_zero:
        for c in required:
            # keep rows where value is not exactly zero (works for numeric columns)
            df_filtered = df_filtered[~((df_filtered[c] == 0))]

    after = len(df_filtered)
    print(f"Filtered rows: {before:,} -> {after:,} (dropped {before-after:,})")

    out.parent.mkdir(parents=True, exist_ok=True)
    df_filtered.to_csv(out, index=False)
    print(f"Wrote filtered CSV to: {out}")

    if args.sav:
        if pyreadstat is None:
            print("pyreadstat not available in this environment. Install it to write .sav files.", file=sys.stderr)
            return 3
        sav_out = out.with_suffix(".sav")
        print(f"Writing SPSS file to {sav_out}...")
        pyreadstat.write_sav(df_filtered, str(sav_out))
        print(f"Wrote SPSS .sav to: {sav_out}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
