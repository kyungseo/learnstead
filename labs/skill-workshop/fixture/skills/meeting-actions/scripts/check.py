#!/usr/bin/env python3
"""meeting-actions 출력을 판정한다.

통과 조건: Markdown 표 하나 · 4열(#, 액션 아이템, 담당, 기한) · 데이터 4행 · 담당·기한이 기대값과 정확히 일치 ·
결정만 하고 행동이 없는 항목(보고회 일정, 채용 보류, 다음 회의)은 포함하지 않음.

사용법: python3 check.py output.md   (또는 stdin)
종료 코드 0 = PASS, 1 = FAIL (사유 출력)
"""
import re
import sys

EXPECT = [  # (담당, 기한, 액션 키워드)
    ("박지호", "2026-09-12", "발표"),
    ("이도윤", "다음 주 수요일", "재현"),
    ("정하은", "미정", "검토"),
    ("김서연", "2026-09-03", "분기"),
]
MUST_NOT = {
    "채용 보류": re.compile(r"채용.*(?:보류|예산|논의)"),
    "보고회 일정": re.compile(r"중간 보고회(?:는|를).*?(?:9월 15일|2026-09-15).*?(?:열|개최)"),
    "다음 회의 일정": re.compile(r"다음 회의.*?(?:9월 4일|2026-09-04)"),
}

text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
rows = []
for line in text.splitlines():
    s = line.strip()
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if all(set(c) <= set("-: ") for c in cells) or cells[0] in ("#", "번호"):
        continue  # 구분선·헤더
    rows.append(cells)

problems = []
if len(rows) != 4:
    problems.append(f"행 수 {len(rows)} (기대 4)")
bad_cols = [r for r in rows if len(r) != 4]
if bad_cols:
    problems.append(f"4열이 아닌 행 {len(bad_cols)}개 (예: {len(bad_cols[0])}열)")
for who, due, kw in EXPECT:
    hit = [r for r in rows if len(r) >= 4 and who in r[2] and kw in r[1]]
    if not hit:
        problems.append(f"항목 없음: {who}/{kw}")
    elif hit[0][3] != due:
        problems.append(f"기한 불일치: {who} → '{hit[0][3]}' (기대 '{due}')")
for label, pattern in MUST_NOT.items():
    if any(pattern.search(r[1]) for r in rows if len(r) >= 2):
        problems.append(f"행동 없는 결정 포함: {label}")
if problems:
    print("FAIL: " + " · ".join(problems))
    sys.exit(1)
print("PASS: 4열 4행 · 담당·기한 일치 · 행동 없는 결정 없음")
