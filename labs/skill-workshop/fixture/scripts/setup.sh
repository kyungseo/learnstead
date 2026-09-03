#!/bin/bash
# 워크숍 저장소를 만든다. 사용법: bash fixture/scripts/setup.sh <대상 디렉터리>
set -euo pipefail

FIX="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:?대상 디렉터리}"

if [ -e "$DEST" ] && [ -n "$(find "$DEST" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  echo "오류: 대상 디렉터리가 비어 있지 않다: $DEST"
  exit 1
fi

mkdir -p "$DEST/.claude/skills" "$DEST/.agents/skills" "$DEST/input" "$DEST/logs" "$DEST/scripts"
cp -R "$FIX/skills/meeting-actions" "$DEST/.agents/skills/"
ln -sfn ../../.agents/skills/meeting-actions "$DEST/.claude/skills/meeting-actions"
cp "$FIX/input/meeting-notes.md" "$DEST/input/"
cp "$FIX/scripts/run-claude.sh" "$FIX/scripts/run-codex.sh" "$DEST/scripts/"
chmod +x "$DEST/scripts/"*.sh
cp -R "$FIX/variants" "$DEST/variants"
cp -R "$FIX/expected" "$DEST/expected"
(
  cd "$DEST"
  git init -q
  git add -A
  git -c user.name="Learnstead Lab" -c user.email="lab@example.invalid" commit -qm "skill workshop fixture"
)
echo "준비 완료: $DEST"
