"""Small helper to convert cleaned CSV to SPSS .sav using pyreadstat.

Usage:
    python 'Scripts/02_export_spss.py' -i Exports/snacks_clean.csv -o Exports/snacks_clean.sav
"""
import argparse
import pathlib
import sys

import pandas as pd

try:
    import pyreadstat
except Exception as e:
    print("pyreadstat is required. Please install it in your venv (pip install pyreadstat).", file=sys.stderr)
    raise


def main(argv=None):
    p = argparse.ArgumentParser(description="Export cleaned CSV to SPSS .sav")
    p.add_argument("-i", "--input", default="Exports/snacks_clean.csv")
    p.add_argument("-o", "--output", default="Exports/snacks_clean.sav")
    args = p.parse_args(argv)

    inp = pathlib.Path(args.input)
    out = pathlib.Path(args.output)

    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        return 2

    print(f"Loading {inp}...")
    df = pd.read_csv(inp, low_memory=False)
    print(f"Loaded {len(df):,} rows x {len(df.columns)} columns")

    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing SPSS file to {out} (this may take a moment)...")

    # Let pyreadstat infer variable types. For very large string columns, SPSS has limits;
    # pyreadstat will handle conversion but you can pre-truncate or convert to categorical if needed.
    pyreadstat.write_sav(df, str(out))

    print("Done: wrote", out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
