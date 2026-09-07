#!/usr/bin/env bash
# 시나리오 정의. run-claude.sh / run-codex.sh가 source한다.
# 변수: PROMPT_FILE(필수) AGENTS PRE_PROMPT EXTRA_FLAGS(claude 전용) FOLLOWUP_FILE CODEX_SANDBOX SRC_SCEN/SRC_TOOL(앞 실행 이어받기)
case "${1:?}" in
  s01-review-direct)      PROMPT_FILE=review-correctness.md; EXTRA_FLAGS="--disallowedTools Agent"; CODEX_SANDBOX=read-only ;;
  s01-task-direct)        PROMPT_FILE=task-a-parse-memo.md; EXTRA_FLAGS="--disallowedTools Agent" ;;
  s02-review-delegate)    PROMPT_FILE=review-correctness.md; AGENTS="reviewer"
                          PRE_PROMPT="아래 검토를 reviewer subagent 하나에게 그대로 위임하고, 당신은 src/ 파일을 직접 읽지 마세요. subagent가 돌려준 JSON을 그대로 출력하세요."; CODEX_SANDBOX=read-only ;;
  s02-delegate-history)   PROMPT_FILE=delegate-history.md; AGENTS="implementer" ;;
  s02-delegate-explicit)  PROMPT_FILE=delegate-explicit.md; AGENTS="implementer" ;;
  s03-parallel)           PROMPT_FILE=task-abc-parallel.md; AGENTS="implementer" ;;
  s03-sequential)         PROMPT_FILE=task-abc-sequential.md; AGENTS="implementer" ;;
  s03-samefile)           PROMPT_FILE=task-xy-samefile.md; AGENTS="implementer" ;;
  s03-samefile-worktree)  PROMPT_FILE=task-xy-samefile.md; AGENTS="implementer-worktree" ;;
  s04-gaps-direct)        PROMPT_FILE=review-gaps.md; EXTRA_FLAGS="--disallowedTools Agent"; CODEX_SANDBOX=read-only ;;
  s04-writer-selfreview)  PROMPT_FILE=writer-misled-fix.md; FOLLOWUP_FILE=self-review.md; EXTRA_FLAGS="--disallowedTools Agent" ;;
  s04-writer-only)        PROMPT_FILE=writer-misled-fix.md; EXTRA_FLAGS="--disallowedTools Agent" ;;
  s04-fresh-review)       PROMPT_FILE=fresh-review-diff.md; EXTRA_FLAGS="--disallowedTools Agent"; CODEX_SANDBOX=read-only; SRC_SCEN=s04-writer-only; SRC_TOOL=same ;;
  s04-cross-review)       PROMPT_FILE=fresh-review-diff.md; EXTRA_FLAGS="--disallowedTools Agent"; CODEX_SANDBOX=read-only; SRC_SCEN=s04-writer-only; SRC_TOOL=other ;;
  *) echo "알 수 없는 시나리오: $1" >&2; exit 2 ;;
esac
