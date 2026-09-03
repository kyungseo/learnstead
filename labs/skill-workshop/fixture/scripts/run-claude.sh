#!/bin/bash
# Claude Code 비-대화형 실행 + 관측 요약
# 사용법: scripts/run-claude.sh <라벨> <프롬프트…>
#   → logs/<라벨>.jsonl (stream-json 전체), logs/<라벨>.out (최종 답), 표준 출력에 tool 호출·토큰 요약
# 워크숍 저장소 루트에서 실행한다.
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "사용법: $0 <라벨> <프롬프트…>" >&2
  exit 2
fi
label="$1"
shift
if [[ ! "$label" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "오류: 라벨은 영문자나 숫자로 시작하고 영문자·숫자·점·밑줄·하이픈만 사용할 수 있다: $label" >&2
  exit 2
fi
mkdir -p logs
rc=0
claude -p "$*" --allowedTools "Read Skill" --output-format stream-json --verbose --max-turns 6 > "logs/$label.jsonl" 2> "logs/$label.err" || rc=$?
python3 - "logs/$label" <<'PY'
import json, sys
base = sys.argv[1]; tools = []; result = None; usage = None; turns = None
for line in open(base + ".jsonl", encoding="utf-8"):
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") == "assistant":
        for c in ev["message"].get("content", []):
            if c.get("type") == "tool_use":
                tools.append((c["name"], json.dumps(c.get("input", {}), ensure_ascii=False)[:100]))
    if ev.get("type") == "result":
        result = ev.get("result"); usage = ev.get("usage", {}); turns = ev.get("num_turns")
open(base + ".out", "w", encoding="utf-8").write(result or "")
if usage:
    u = usage
    print(f"[{base}] turns={turns} tools={tools} cache_read={u.get('cache_read_input_tokens')} cache_write={u.get('cache_creation_input_tokens')} out={u.get('output_tokens')}")
else:
    print(f"[{base}] 결과 없음 — {base}.err 확인")
PY
echo "[$label] cli_rc=$rc"
exit "$rc"
