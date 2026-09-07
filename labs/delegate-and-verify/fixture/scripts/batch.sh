#!/usr/bin/env bash
# 사용: LAB_TOOLS=claude|codex|both scripts/batch.sh <실행이름> <반복수> <시나리오...>
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
NAME="${1:?실행이름}"; N="${2:?반복수}"; shift 2
[[ "$N" =~ ^[1-9][0-9]*$ ]] || { echo "반복수는 양의 정수여야 합니다." >&2; exit 2; }
[ "$#" -gt 0 ] || { echo "시나리오를 하나 이상 지정하세요." >&2; exit 2; }
case "${LAB_TOOLS:-both}" in
  both) TOOLS=(claude codex) ;;
  claude|codex) TOOLS=("$LAB_TOOLS") ;;
  *) echo "LAB_TOOLS는 claude, codex, both 중 하나입니다." >&2; exit 2 ;;
esac
for tool in "${TOOLS[@]}"; do
  command -v "$tool" >/dev/null || { echo "$tool 명령을 찾을 수 없습니다." >&2; exit 2; }
done
# 알 수 없는 시나리오 때문에 일부만 실행되는 일을 막는다.
for s in "$@"; do (source "$HERE/scenario.sh" "$s") || exit 2; done
failed=0
for s in "$@"; do
  if [ "$s" = s04-cross-review ] && [ "${#TOOLS[@]}" -eq 1 ]; then
    echo "교차 검토는 두 도구가 필요하여 건너뜁니다: $s"
    continue
  fi
  for i in $(seq 1 "$N"); do
    for tool in "${TOOLS[@]}"; do
      echo "$tool $s r$i"
      if [ "$tool" = codex ] && [ "$s" = s03-samefile-worktree ]; then
        "$HERE/run-codex-worktrees.sh" "$NAME" "$i" || failed=1
      else
        "$HERE/run-$tool.sh" "$s" "$NAME" "$i" || failed=1
      fi
    done
  done
done
if [ "$failed" -ne 0 ]; then
  echo "일부 실행이 완료되지 않았습니다: $NAME" >&2
else
  echo "실행 수집 완료: $NAME (검사·기능·검토 결과는 별도 판정)"
fi
exit "$failed"
