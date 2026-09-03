#!/bin/bash
# 지시문 변형 하나로 과제를 돌리고 판정한다.
# 사용법: scripts/run-variant.sh <claude|codex> <V0|V1|V2|V3|V3i|V4> <라벨>
#   → runs/<라벨>/ 에 프로젝트 사본·로그·판정. 표준 출력에 한 줄 요약.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "사용법: $0 <claude|codex> <V0|V1|V2|V3|V3i|V4> <라벨>" >&2
  exit 2
fi

TOOL="$1"
VAR="$2"
LABEL="$3"
FIX="$(cd "$(dirname "$0")/.." && pwd)"
RUN_ROOT="$PWD/runs"

case "$TOOL" in
  claude) INS="CLAUDE.md" ;;
  codex) INS="AGENTS.md" ;;
  *) echo "오류: tool은 claude 또는 codex여야 한다: $TOOL" >&2; exit 2 ;;
esac

case "$VAR" in
  V0|V1|V2|V3|V3i|V4) ;;
  *) echo "오류: 알 수 없는 변형: $VAR" >&2; exit 2 ;;
esac

if [[ ! "$LABEL" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "오류: 라벨은 영문자나 숫자로 시작하고 영문자·숫자·점·밑줄·하이픈만 사용할 수 있다: $LABEL" >&2
  exit 2
fi

mkdir -p "$RUN_ROOT"
RUN_ROOT_ABS="$(cd "$RUN_ROOT" && pwd)"
RUN="$RUN_ROOT_ABS/$LABEL"
case "$RUN" in
  "$RUN_ROOT_ABS"/*) ;;
  *) echo "오류: 실행 경로가 runs 밖을 가리킨다: $RUN" >&2; exit 2 ;;
esac
if [ -e "$RUN" ]; then
  case "$RUN" in
    "$RUN_ROOT_ABS"|"$RUN_ROOT_ABS/"|"/"|"") echo "오류: 삭제할 수 없는 실행 경로다: $RUN" >&2; exit 2 ;;
  esac
  find "$RUN" -mindepth 1 -delete
fi
mkdir -p "$RUN"
cp -R "$FIX/project/." "$RUN/"
cd "$RUN"

case "$VAR" in
  V0) ;;
  V1) cp "$FIX/variants/V1-short.md" "$INS" ;;
  V2) cp "$FIX/variants/V2-long.md" "$INS" ;;
  V3) mkdir -p docs; cp "$FIX/variants/V3-pointer.md" "$INS"; cp "$FIX/RULES.md" docs/RULES.md ;;
  V3i) mkdir -p docs; cp "$FIX/variants/V3i-import.md" "$INS"; cp "$FIX/RULES.md" docs/RULES.md ;;
  V4)
    if [ "$TOOL" = "claude" ]; then
      mkdir -p .claude/rules
      cp "$FIX/variants/V4-rule-python.md" .claude/rules/python.md
      printf '# textkit\n\n작은 텍스트 유틸리티 패키지. `src/textkit/`에 모듈, `tests/`에 pytest.\n' > CLAUDE.md
    else
      printf '# textkit\n\n작은 텍스트 유틸리티 패키지. `src/textkit/`에 모듈, `tests/`에 pytest.\n' > AGENTS.md
      tail -n +2 "$FIX/RULES.md" | { printf '# src 규칙\n'; cat; } > src/AGENTS.md
    fi
    ;;
esac

git init -q
git add -A
git -c user.name="Learnstead Lab" -c user.email="lab@example.invalid" commit -qm base
TASK='src/textkit/slug.py 에 slugify(text) 함수를 추가해 줘. 소문자로 바꾸고 공백과 특수문자를 하이픈 하나로 치환하며 앞뒤 하이픈은 제거한다. 테스트도 추가하고, 프로젝트 관례를 따라 마무리해 줘.'
cli_rc=0
if [ "$TOOL" = claude ]; then
  claude -p "$TASK" --output-format json --max-turns 25 > out.json 2> err.txt || cli_rc=$?
  python3 - <<'PY'
import json
from pathlib import Path

try:
    d = json.loads(Path("out.json").read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    d = {}
u = d.get("usage", {})
print(f"turns={d.get('num_turns')} cache_w={u.get('cache_creation_input_tokens')} cache_r={u.get('cache_read_input_tokens')} out={u.get('output_tokens')}")
PY
else
  codex exec --skip-git-repo-check -s workspace-write -o out.md "$TASK" < /dev/null > transcript.txt 2>&1 || cli_rc=$?
  tokens=$(grep -A1 'tokens used' transcript.txt | tail -1 | tr -d ' ' || true)
  read_rules=$(grep -c 'RULES.md\|AGENTS.md' transcript.txt || true)
  echo "tokens=$tokens read_rules=$read_rules"
fi
echo "cli_rc=$cli_rc"
check_rc=0
python3 "$FIX/scripts/check.py" . | tee check.txt | tail -1 || check_rc=$?
if [ "$cli_rc" -ne 0 ]; then
  exit 2
fi
exit "$check_rc"
