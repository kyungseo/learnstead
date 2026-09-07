#!/usr/bin/env bash
# 같은 파일 과제 X·Y를 worktree 둘에서 실행하고 편집·통합 시도·전체 시간을 분리한다.
# 사용: scripts/run-codex-worktrees.sh <실행이름> [반복번호]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; FX="$(dirname "$HERE")"
NAME="${1:?실행이름}"; REP="${2:-1}"
RUN="$FX/runs/$NAME/codex-s03-samefile-worktree-r$REP"
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
now() { python3 -c 'import time; print(time.monotonic())'; }
elapsed() { python3 -c "print(f'{$2-$1:.3f}')"; }
TOTAL_START=$(now)
cp -R "$FX/project" "$RUN/proj"
cd "$RUN/proj"
git init -q && git add -A && git -c user.email=lab@example.com -c user.name=lab commit -qm "fixture baseline"
git worktree add -q ../wt-x -b task-x
git worktree add -q ../wt-y -b task-y
MODEL_FLAGS=()
[ -z "${CODEX_MODEL:-}" ] || MODEL_FLAGS+=(-m "$CODEX_MODEL")
[ -z "${CODEX_EFFORT:-}" ] || MODEL_FLAGS+=(-c "model_reasoning_effort=\"$CODEX_EFFORT\"")
EDIT_START=$(now)
codex exec --json --sandbox workspace-write -c agents.enabled=false ${MODEL_FLAGS[@]+"${MODEL_FLAGS[@]}"} -C "$RUN/wt-x" "$(cat "$FX/prompts/task-x-report-header.md")" </dev/null > "$RUN/stream-x.jsonl" 2> "$RUN/stderr-x.txt" &
PX=$!
codex exec --json --sandbox workspace-write -c agents.enabled=false ${MODEL_FLAGS[@]+"${MODEL_FLAGS[@]}"} -C "$RUN/wt-y" "$(cat "$FX/prompts/task-y-report-top.md")" </dev/null > "$RUN/stream-y.jsonl" 2> "$RUN/stderr-y.txt" &
PY=$!
EXIT_X=0; EXIT_Y=0
wait "$PX" || EXIT_X=$?
wait "$PY" || EXIT_Y=$?
printf '%s\n' "$EXIT_X" > "$RUN/exit_code_x.txt"
printf '%s\n' "$EXIT_Y" > "$RUN/exit_code_y.txt"
EDIT_END=$(now)
elapsed "$EDIT_START" "$EDIT_END" > "$RUN/wall_edit_seconds.txt"
# 과거 wall_s와 비교 가능한 범위는 편집 프로세스 구간뿐이다.
cp "$RUN/wall_edit_seconds.txt" "$RUN/wall_seconds.txt"
INTEGRATION_START=$(now)
for w in x y; do
  (cd "$RUN/wt-$w" && PYTHONPATH=src python3 -m unittest -q > "$RUN/tests-$w.txt" 2>&1 && echo PASS || echo FAIL) >> "$RUN/tests-$w.txt"
done
STATUS=process_failed
if [ "$EXIT_X" -eq 0 ] && [ "$EXIT_Y" -eq 0 ]; then
  STATUS=merged
  for w in x y; do
    if ! (cd "$RUN/wt-$w" && git add -A && git -c user.email=lab@example.com -c user.name=lab commit -qm "task $w" && git diff HEAD~1 --stat) > "$RUN/diff-stat-$w.txt" 2>&1; then
      STATUS=commit_failed
      break
    fi
  done
  if [ "$STATUS" = merged ]; then
    for w in x y; do
      if git -c user.email=lab@example.com -c user.name=lab merge --no-edit "task-$w" >> "$RUN/merge.txt" 2>&1; then
        echo "merge $w: ok" >> "$RUN/merge.txt"
      else
        if [ -n "$(git diff --name-only --diff-filter=U)" ]; then
          STATUS=conflict
          git diff --name-only --diff-filter=U >> "$RUN/merge.txt"
        else
          STATUS=merge_failed
        fi
        git merge --abort >> "$RUN/merge.txt" 2>&1 || true
        break
      fi
    done
  fi
fi
printf '%s\n' "$STATUS" > "$RUN/integration_status.txt"
if [ "$STATUS" = merged ]; then
  (PYTHONPATH=src python3 -m unittest -q > "$RUN/tests.txt" 2>&1 && echo PASS || echo FAIL) >> "$RUN/tests.txt"
else
  echo SKIPPED_NOT_INTEGRATED > "$RUN/tests.txt"
fi
END=$(now)
elapsed "$INTEGRATION_START" "$END" > "$RUN/wall_integration_seconds.txt"
elapsed "$TOTAL_START" "$END" > "$RUN/wall_total_seconds.txt"
echo "$RUN"
# merge 충돌은 이 시나리오의 관측 대상. 프로세스·커밋·merge 명령 실패는 실행 실패다.
case "$STATUS" in merged|conflict) exit 0 ;; *) exit 1 ;; esac
