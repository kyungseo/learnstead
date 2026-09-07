#!/usr/bin/env bash
# 사용: scripts/run-claude.sh <시나리오> <실행이름> [반복번호]   (CLAUDE_MODEL=opus 등으로 모델 지정 가능)
# 시나리오 이름은 scripts/scenario.sh 참조. 결과는 fixture/runs/<실행이름>/ 아래에 남는다.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FX="$(dirname "$HERE")"
SCEN="${1:?시나리오}"; NAME="${2:?실행이름}"; REP="${3:-1}"
RUN="$FX/runs/$NAME/claude-$SCEN-r$REP"
source "$HERE/scenario.sh" "$SCEN"   # PROMPT_FILE, AGENTS, PRE_PROMPT, EXTRA_FLAGS, FOLLOWUP_FILE, CROSS 설정
case "$NAME" in
  ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._-]*) echo "실행 이름은 영숫자로 시작하고 영숫자·점·밑줄·하이픈만 사용하세요." >&2; exit 2 ;;
esac
[[ "$REP" =~ ^[1-9][0-9]*$ ]] || { echo "반복번호는 양의 정수여야 합니다." >&2; exit 2; }
if [ -e "$RUN" ]; then
  echo "기존 실행을 보존합니다: $RUN (새 실행 이름을 사용하세요)" >&2
  exit 2
fi
mkdir -p "$(dirname "$RUN")"
mkdir "$RUN"
if [ -n "${SRC_SCEN:-}" ]; then
  # 앞선 실행의 작업 트리(미커밋 변경 포함)를 이어받는다. SRC_claude=other면 다른 도구의 결과를 검토한다.
  OTHER=$([ "$SRC_TOOL" = other ] && ([ "claude" = claude ] && echo codex || echo claude) || echo claude)
  SRC="$FX/runs/$NAME/$OTHER-$SRC_SCEN-r$REP/proj"
  [ -d "$SRC" ] || { echo "원본 실행 없음: $SRC" >&2; exit 3; }
  rsync -a --exclude .claude --exclude .codex --exclude .git "$SRC/" "$RUN/proj/"
else
  cp -R "$FX/project" "$RUN/proj"
fi
cd "$RUN/proj"
if [ -n "${SRC_SCEN:-}" ]; then
  git init -q; mkdir -p "$RUN/.base"; cp -R "$FX/project/." "$RUN/.base/"; git --work-tree="$RUN/.base" add -A; git -c user.email=lab@example.com -c user.name=lab commit -qm "fixture baseline"; rm -rf "$RUN/.base"; git reset -q
else
  git init -q && git add -A && git -c user.email=lab@example.com -c user.name=lab commit -qm "fixture baseline"
fi
if [ -n "${AGENTS:-}" ]; then
  mkdir -p .claude/agents
  for a in $AGENTS; do cp "$FX/agents/claude/$a.md" .claude/agents/; done
fi
PROMPT="$(cat "$FX/prompts/$PROMPT_FILE")"
[ -n "${PRE_PROMPT:-}" ] && PROMPT="$PRE_PROMPT
$PROMPT"
printf '%s\n' "$PROMPT" > "$RUN/prompt.txt"
EXIT_CODE=0
START=$(python3 -c "import time; print(time.monotonic())")
# shellcheck disable=SC2086
claude -p "$PROMPT" --output-format stream-json --verbose --max-budget-usd 3 ${CLAUDE_MODEL:+--model "$CLAUDE_MODEL"} ${EXTRA_FLAGS:-} \
  </dev/null > "$RUN/stream.jsonl" 2> "$RUN/stderr.txt" || EXIT_CODE=$?
printf '%s\n' "$EXIT_CODE" > "$RUN/exit_code.txt"
END=$(python3 -c "import time; print(time.monotonic())")
if [ -n "${FOLLOWUP_FILE:-}" ] && [ "$EXIT_CODE" -eq 0 ]; then
  F="$(cat "$FX/prompts/$FOLLOWUP_FILE")"; printf '%s\n' "$F" > "$RUN/followup.txt"
  python3 -c "print(f'{$END-$START:.1f}')" > "$RUN/wall_seconds.txt"   # 작성 턴
  FSTART=$(python3 -c "import time; print(time.monotonic())")
  claude -p --continue "$F" --output-format stream-json --verbose --max-budget-usd 3 ${CLAUDE_MODEL:+--model "$CLAUDE_MODEL"} ${EXTRA_FLAGS:-} \
    </dev/null > "$RUN/stream-followup.jsonl" 2>> "$RUN/stderr.txt" || EXIT_CODE=$?
  printf '%s\n' "$EXIT_CODE" > "$RUN/exit_code_followup.txt"
  END=$(python3 -c "import time; print(time.monotonic())"); python3 -c "print(f'{$END-$FSTART:.1f}')" > "$RUN/wall_followup_seconds.txt"   # 검토 턴
fi
[ -f "$RUN/wall_followup_seconds.txt" ] || python3 -c "print(f'{$END-$START:.1f}')" > "$RUN/wall_seconds.txt"
# 세션 transcript(subagent transcript 포함)를 근거로 복사한다.
SID="$(python3 -c "import json,sys
for l in open('$RUN/stream.jsonl'):
    e=json.loads(l)
    if e.get('type')=='result': print(e.get('session_id',''))" 2>/dev/null | tail -1)"
SLUG="$(echo "$RUN/proj" | sed 's#[/.]#-#g')"
if [ -n "$SID" ] && [ -d "$HOME/.claude/projects/$SLUG" ]; then
  mkdir -p "$RUN/transcripts"
  cp "$HOME/.claude/projects/$SLUG/$SID.jsonl" "$RUN/transcripts/" 2>/dev/null || true
  [ -d "$HOME/.claude/projects/$SLUG/$SID" ] && cp -R "$HOME/.claude/projects/$SLUG/$SID" "$RUN/transcripts/" || true
fi
git -c user.email=lab@example.com -c user.name=lab add -A >/dev/null 2>&1 || true
git diff --cached --stat > "$RUN/diff-stat.txt" || true
git diff --cached > "$RUN/diff.patch" || true
git worktree list > "$RUN/worktrees.txt" 2>/dev/null || true
(PYTHONPATH=src python3 -m unittest -q > "$RUN/tests.txt" 2>&1 && echo PASS || echo FAIL) >> "$RUN/tests.txt"
echo "$RUN"
exit "$EXIT_CODE"
