#!/usr/bin/env python3
"""runs/<이름>/ 전체를 시나리오·도구별 중앙값으로 요약한다.

사용: python3 scripts/summarize.py runs/main [--md]
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

root = Path(sys.argv[1]); md = "--md" in sys.argv
here = Path(__file__).resolve().parent
rows = []
for run in sorted(p for p in root.iterdir() if p.is_dir()):
    out = subprocess.run([sys.executable, str(here / "score.py"), str(run)], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        continue
    rows.append(json.loads(out.stdout.strip().splitlines()[-1]))
groups = defaultdict(list)
for r in rows:
    tool, rest = r["run"].split("-", 1)
    scen = rest.rsplit("-r", 1)[0]
    if r.get("usage_available", True) and not r.get("exit_codes") and r["main"]["in"] == 0 and r["sub"]["in"] == 0 and r.get("wall_seconds", 0) and r["wall_seconds"] < 5:
        print(f"기존 빈 실행 제외: {r['run']}", file=sys.stderr)
        continue  # 종료 코드를 기록하지 않던 과거 실행의 한도·오류 추정
    groups[(tool, scen)].append(r)
def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None
def total_in(u):
    return u["in"] + u.get("cache_read", 0) + u.get("cache_write", 0)
hdr = "| 도구 | 시나리오 | n | 메인 컨텍스트 끝 | 메인 입력 누적 | 위임 입력 누적 | 출력 | 실행 시간(초) | 위치 일치 | 골든셋 밖 지적 | 골든셋 무결함 파일 지적 | 테스트 | 전체 시간(초) | 통합 상태 | 프로세스 종료 코드 |"
print(hdr); print("| --- " * 15 + "|")
def shown(value):
    return f"{int(value):,}" if value is not None else "—"
for (tool, scen), rs in sorted(groups.items()):
    measured = [r for r in rs if r.get("usage_available", True)]
    mi = med([total_in(r["main"]) for r in measured]); si = med([total_in(r["sub"]) for r in measured])
    mo = med([r["main"]["out"] + r["sub"]["out"] for r in measured])
    w = med([r["wall_seconds"] for r in rs])
    hits = "/".join(str(r["judge"]["hits"]) for r in rs); fp = "/".join(str(r["judge"]["false_positives"]) for r in rs)
    cl = "/".join(str(r["judge"]["clean_flagged"]) for r in rs); t = "/".join(str(r["tests"]) for r in rs)
    ctx = med([r.get("main_ctx_last") for r in measured])
    total_wall = med([r.get("wall_total_seconds") for r in rs])
    integration = "/".join(r.get("integration_status") or "—" for r in rs)
    exits = "/".join(",".join(f"{k}={v}" for k, v in r.get("exit_codes", {}).items()) or "미기록" for r in rs)
    print(f"| {tool} | {scen} | {len(rs)} | {shown(ctx)} | {shown(mi)} | {shown(si)} | {shown(mo)} | {w} | {hits} | {fp} | {cl} | {t} | {total_wall if total_wall is not None else '—'} | {integration} | {exits} |")
