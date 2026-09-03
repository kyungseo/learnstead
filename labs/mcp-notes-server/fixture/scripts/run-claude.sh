#!/bin/bash
# Claude Code 비-대화형 실행 + MCP 관측 요약
# 사용법: scripts/run-claude.sh <라벨> "<허용 도구 목록 또는 ->" <프롬프트…>
#   PERM=default scripts/run-claude.sh …   → --permission-mode default 로 실행 (허용 목록 밖 도구를 거부)
#   → logs/<라벨>.jsonl, logs/<라벨>.out, 표준 출력에 MCP 서버 상태·tool 호출·권한 거부·토큰
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "사용법: $0 <라벨> \"<허용 도구 목록 또는 ->\" <프롬프트…>" >&2
  exit 2
fi
label="$1"
allowed="$2"
shift 2
if [[ ! "$label" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "오류: 라벨은 영문자나 숫자로 시작하고 영문자·숫자·점·밑줄·하이픈만 사용할 수 있다: $label" >&2
  exit 2
fi

mkdir -p logs
claude_args=(-p "$*" --output-format stream-json --verbose --max-turns 8)
if [ -n "${PERM:-}" ]; then
  claude_args+=(--permission-mode "$PERM")
fi
if [ "$allowed" != "-" ]; then
  claude_args+=(--allowedTools "$allowed")
fi
rc=0
claude "${claude_args[@]}" > "logs/$label.jsonl" 2> "logs/$label.err" || rc=$?
python3 - "logs/$label" <<'PY'
import json, sys
base = sys.argv[1]; tools = []; result = None; usage = None; turns = None; denials = None; mcp = None
for line in open(base + ".jsonl", encoding="utf-8"):
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get("type") == "system" and ev.get("subtype") == "init":
        mcp = [(s.get("name"), s.get("status")) for s in ev.get("mcp_servers", [])]
    if ev.get("type") == "assistant":
        for c in ev["message"].get("content", []):
            if c.get("type") == "tool_use":
                tools.append((c["name"], json.dumps(c.get("input", {}), ensure_ascii=False)[:60]))
    if ev.get("type") == "result":
        result = ev.get("result"); usage = ev.get("usage", {}); turns = ev.get("num_turns"); denials = ev.get("permission_denials")
open(base + ".out", "w", encoding="utf-8").write(result or "")
u = usage or {}
print(f"[{base}] mcp={mcp} turns={turns}\n  tools={tools}\n  denials={[d.get('tool_name') for d in (denials or [])]}\n  cache_read={u.get('cache_read_input_tokens')} out={u.get('output_tokens')}")
PY
echo "[$label] cli_rc=$rc"
exit "$rc"
