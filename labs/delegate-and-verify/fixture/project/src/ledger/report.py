"""텍스트 보고서."""
from __future__ import annotations


def sort_for_report(totals: dict[str, int]) -> list[tuple[str, int]]:
    """규격: 합계 절댓값이 큰 순서."""
    return sorted(totals.items(), key=lambda kv: kv[0])


def render(totals: dict[str, int], year: int, month: int) -> str:
    lines = [f"{year}-{month:02d} 분류별 합계", "-" * 24]
    for name, total in sort_for_report(totals):
        lines.append(f"{name:<10}{total:>14,}")
    lines.append("-" * 24)
    lines.append(f"{'합계':<10}{sum(totals.values()):>14,}")
    return "\n".join(lines)
