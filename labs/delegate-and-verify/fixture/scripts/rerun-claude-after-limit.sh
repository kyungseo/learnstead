#!/usr/bin/env bash
# Claude Code 세션 한도 해제 시각까지 기다렸다가 Claude 시나리오만 다시 돌린다.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
UNTIL="${1:?HH:MM}"; NAME="${2:-main}"; N="${3:-3}"; shift 3 || true
while [ "$(date +%H:%M)" \< "$UNTIL" ]; do sleep 60; done
for s in "$@"; do for i in $(seq 1 "$N"); do echo "== claude $s r$i $(date +%H:%M)"; "$HERE/run-claude.sh" "$s" "$NAME" "$i" || echo "claude $s r$i 실패"; done; done
echo "claude rerun done $(date +%H:%M)"
