"""월별·분류별 합계."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from calendar import monthrange

from .parse import Record


def month_range(year: int, month: int) -> tuple[date, date]:
    """해당 월의 첫날과 마지막 날."""
    last = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last)


def in_month(rec: Record, year: int, month: int) -> bool:
    start, end = month_range(year, month)
    return start <= rec.day < end


def totals_by_category(records: list[Record], year: int, month: int) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for rec in records:
        if in_month(rec, year, month):
            out[rec.category] += rec.amount
    return dict(out)


def grand_total(totals: dict[str, int]) -> int:
    return sum(totals.values())
