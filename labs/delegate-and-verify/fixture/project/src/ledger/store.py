"""JSON Lines append 저장소. 결함 없는 대조 모듈."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .parse import Record


def append_records(path: str | Path, records: list[Record]) -> int:
    """레코드를 JSON Lines로 append하고 쓴 줄 수를 돌려준다."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for rec in records:
            row = asdict(rec)
            row["day"] = rec.day.isoformat()
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(records)


def count_lines(path: str | Path) -> int:
    p = Path(path)
    if not p.exists():
        return 0
    with p.open(encoding="utf-8") as f:
        return sum(1 for _ in f)
