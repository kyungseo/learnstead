"""python3 -m ledger.cli data/sample.csv --month 2026-08"""
from __future__ import annotations

import argparse

from .parse import load_csv
from .report import render
from .summarize import totals_by_category


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--month", required=True, help="YYYY-MM")
    args = ap.parse_args(argv)
    year, month = (int(p) for p in args.month.split("-"))
    records = load_csv(args.csv)
    print(render(totals_by_category(records, year, month), year, month))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
