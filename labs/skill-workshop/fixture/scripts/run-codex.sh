#!/bin/bash
# Codex 비-대화형 실행
# 사용법: scripts/run-codex.sh <라벨> <프롬프트…>
#   → logs/<라벨>.codex.txt (transcript), logs/<라벨>.out (마지막 메시지)
# 프롬프트에 $name을 쓰려면 작은따옴표로 감싼다:  scripts/run-codex.sh c1 '$meeting-actions input/meeting-notes.md'
# 2026-08-30 호환을 위해 stdin을 닫는다. 현재 명령의 필수 문법은 아니다.
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
skill_mentions=$(grep -c 'SKILL.md' "logs/$label.codex.txt" || true)
echo "[$label] cli_rc=$rc tokens=$tokens  SKILL.md 언급: ${skill_mentions}회"
exit "$rc"
