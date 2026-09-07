#!/usr/bin/env bash
# 사용: scripts/run-codex.sh <시나리오> <실행이름> [반복번호]   (CODEX_MODEL=gpt-6-astra CODEX_EFFORT=medium 으로 모델·effort 지정 가능)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FX="$(dirname "$HERE")"
SCEN="${1:?시나리오}"; NAME="${2:?실행이름}"; REP="${3:-1}"
RUN="$FX/runs/$NAME/codex-$SCEN-r$REP"
source "$HERE/scenario.sh" "$SCEN"
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
  # 앞선 실행의 작업 트리(미커밋 변경 포함)를 이어받는다. SRC_codex=other면 다른 도구의 결과를 검토한다.
  OTHER=$([ "$SRC_TOOL" = other ] && ([ "codex" = claude ] && echo codex || echo claude) || echo codex)
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
  mkdir -p .codex/agents
  for a in $AGENTS; do cp "$FX/agents/codex/$a.toml" .codex/agents/; done
fi
PROMPT="$(cat "$FX/prompts/$PROMPT_FILE")"
[ -n "${PRE_PROMPT:-}" ] && PROMPT="$PRE_PROMPT
$PROMPT"
printf '%s\n' "$PROMPT" > "$RUN/prompt.txt"
SANDBOX="${CODEX_SANDBOX:-workspace-write}"
DIRECT_FLAGS=()
[ -n "${AGENTS:-}" ] || DIRECT_FLAGS=(-c agents.enabled=false)
MARK="$(mktemp)"
EXIT_CODE=0
START=$(python3 -c "import time; print(time.monotonic())")
codex exec --json ${DIRECT_FLAGS[@]+"${DIRECT_FLAGS[@]}"} --sandbox "$SANDBOX" -C "$RUN/proj" ${CODEX_MODEL:+-m "$CODEX_MODEL"} ${CODEX_EFFORT:+-c "model_reasoning_effort=\"$CODEX_EFFORT\""} "$PROMPT" \
  </dev/null > "$RUN/stream.jsonl" 2> "$RUN/stderr.txt" || EXIT_CODE=$?
printf '%s\n' "$EXIT_CODE" > "$RUN/exit_code.txt"
END=$(python3 -c "import time; print(time.monotonic())")
if [ -n "${FOLLOWUP_FILE:-}" ] && [ "$EXIT_CODE" -eq 0 ]; then
  F="$(cat "$FX/prompts/$FOLLOWUP_FILE")"; printf '%s\n' "$F" > "$RUN/followup.txt"
  python3 -c "print(f'{$END-$START:.1f}')" > "$RUN/wall_seconds.txt"   # 작성 턴
  FSTART=$(python3 -c "import time; print(time.monotonic())")
  codex exec resume --last --json ${DIRECT_FLAGS[@]+"${DIRECT_FLAGS[@]}"} "$F" </dev/null > "$RUN/stream-followup.jsonl" 2>> "$RUN/stderr.txt" || EXIT_CODE=$?
  printf '%s\n' "$EXIT_CODE" > "$RUN/exit_code_followup.txt"
  END=$(python3 -c "import time; print(time.monotonic())"); python3 -c "print(f'{$END-$FSTART:.1f}')" > "$RUN/wall_followup_seconds.txt"   # 검토 턴
fi
[ -f "$RUN/wall_followup_seconds.txt" ] || python3 -c "print(f'{$END-$START:.1f}')" > "$RUN/wall_seconds.txt"
# 세션 rollout(부모+자식)을 복사한다. --json 스트림에는 spawn_agent가 나오지 않으므로 rollout이 근거다.
mkdir -p "$RUN/rollouts"
TID="$(grep -o '"type":"thread.started","thread_id":"[^"]*"' "$RUN/stream.jsonl" | head -1 | sed 's/.*thread_id":"//; s/"$//' || true)"
if [ -n "$TID" ]; then
  find "${CODEX_HOME:-$HOME/.codex}/sessions" -name "rollout-*-$TID.jsonl" -exec cp {} "$RUN/rollouts/" \; 2>/dev/null || true
  grep -l "\"parent_thread_id\":\"$TID\"" $(find "${CODEX_HOME:-$HOME/.codex}/sessions" -name 'rollout-*.jsonl' -newer "$MARK" 2>/dev/null) 2>/dev/null \
    | while read -r f; do cp "$f" "$RUN/rollouts/"; done || true
fi
rm -f "$MARK"
git -c user.email=lab@example.com -c user.name=lab add -A >/dev/null 2>&1 || true
git diff --cached --stat > "$RUN/diff-stat.txt" || true
git diff --cached > "$RUN/diff.patch" || true
(PYTHONPATH=src python3 -m unittest -q > "$RUN/tests.txt" 2>&1 && echo PASS || echo FAIL) >> "$RUN/tests.txt"
echo "$RUN"
exit "$EXIT_CODE"
