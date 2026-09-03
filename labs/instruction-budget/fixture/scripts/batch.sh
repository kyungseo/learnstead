#!/bin/bash
# 사용법: scripts/batch.sh <claude|codex> "<V0 V1 …>" <반복 수> → runs/<tool>-<V>-<i>/ 와 results.tsv 누적
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "사용법: $0 <claude|codex> \"<V0 V1 V2 V3 V3i V4>\" <반복 수>" >&2
  exit 2
fi

TOOL="$1"
VARS="$2"
N="$3"
FIX="$(cd "$(dirname "$0")/.." && pwd)"

case "$TOOL" in
  claude|codex) ;;
  *) echo "오류: tool은 claude 또는 codex여야 한다: $TOOL" >&2; exit 2 ;;
esac

if [[ ! "$N" =~ ^[1-9][0-9]*$ ]]; then
  echo "오류: 반복 수는 1 이상의 정수여야 한다: $N" >&2
  exit 2
fi

for V in $VARS; do
  case "$V" in
    V0|V1|V2|V3|V3i|V4) ;;
    *) echo "오류: 알 수 없는 변형: $V" >&2; exit 2 ;;
  esac
  for i in $(seq 1 "$N"); do
    LABEL="$TOOL-$V-$i"
    rc=0
    output=$("$FIX/scripts/run-variant.sh" "$TOOL" "$V" "$LABEL" 2>&1) || rc=$?
    line=$(printf '%s\n' "$output" | grep -E "^turns=|^tokens=|^cli_rc=|^score" | tr '\n' ' ' || true)
    printf '%s\trc=%s %s\n' "$LABEL" "$rc" "$line" | tee -a results.tsv
    if [ "$rc" -gt 1 ]; then
      printf '%s\n' "$output" >&2
      exit "$rc"
    fi
  done
done
