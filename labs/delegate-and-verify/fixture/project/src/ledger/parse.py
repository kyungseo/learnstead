"""CSV 한 줄을 Record로 바꾼다."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Iterator


@dataclass(frozen=True)
class Record:
    day: date
    category: str
    amount: int
    memo: str


def parse_amount(text: str) -> int:
    """'-12,000' 같은 문자열을 정수 원으로 바꾼다. 지출은 음수여야 한다."""
    cleaned = text.strip().replace(",", "").replace("원", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    return abs(int(cleaned))


def parse_date(text: str) -> date:
    y, m, d = (int(p) for p in text.strip().split("-"))
    return date(y, m, d)


def parse_rows(rows: Iterable[dict[str, str]]) -> Iterator[Record]:
    for row in rows:
        yield Record(
            day=parse_date(row["date"]),
            category=row["category"].strip(),
            amount=parse_amount(row["amount"]),
            memo=row.get("memo", "").strip(),
        )


def load_csv(path: str) -> list[Record]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(parse_rows(csv.DictReader(f)))
