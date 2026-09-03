#!/bin/bash
# Codex 비-대화형 실행 + MCP 호출 줄 추출
# 사용법: scripts/run-codex.sh <라벨> <프롬프트…>   → logs/<라벨>.codex.txt, logs/<라벨>.out
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
codex exec --skip-git-repo-check -o "logs/$label.out" "$*" < /dev/null > "logs/$label.codex.txt" 2>&1 || rc=$?
tokens=$(grep -A1 'tokens used' "logs/$label.codex.txt" | tail -1 | tr -d ' ' || true)
echo "[$label] cli_rc=$rc tokens=$tokens"
grep -nE "^mcp:|cancelled MCP|approval:" "logs/$label.codex.txt" | head -12 || true
exit "$rc"
