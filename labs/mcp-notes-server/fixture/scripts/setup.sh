#!/bin/bash
# 워크숍 저장소를 만든다. 사용법: bash fixture/scripts/setup.sh <대상 디렉터리> [python 실행 파일]
# python 실행 파일은 mcp 패키지가 설치된 인터프리터의 절대 경로 (기본: 현재 python3)
set -euo pipefail

FIX="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:?대상 디렉터리}"
PYBIN="${2:-$(command -v python3)}"

"$PYBIN" -c "import mcp" 2>/dev/null || {
  echo "오류: $PYBIN 에 mcp 패키지가 없다. pip install 'mcp==2.1.1'"
  exit 1
}

if [ -e "$DEST" ] && [ -n "$(find "$DEST" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  echo "오류: 대상 디렉터리가 비어 있지 않다: $DEST"
  exit 1
fi

mkdir -p "$DEST/logs" "$DEST/scripts" "$DEST/.claude/skills" "$DEST/.agents/skills"
cp "$FIX/notes_server.py" "$DEST/"
cp -R "$FIX/notes" "$DEST/notes"
cp "$FIX/.mcp.json.example" "$DEST/.mcp.json.example"
cp "$FIX/.mcp.json.example" "$DEST/.mcp.json"
cp -R "$FIX/skills/notes-digest" "$DEST/.agents/skills/"
ln -sfn ../../.agents/skills/notes-digest "$DEST/.claude/skills/notes-digest"
cp "$FIX/scripts/probe.py" "$FIX/scripts/run-claude.sh" "$FIX/scripts/run-codex.sh" "$DEST/scripts/"
chmod +x "$DEST/scripts/"*.sh
DEST_ABS="$(cd "$DEST" && pwd)"

cat > "$DEST/.gitignore" <<'EOF'
.mcp.json
logs/
EOF

(
  cd "$DEST"
  git init -q
  git add -A
  git -c user.name="Learnstead Lab" -c user.email="lab@example.invalid" commit -qm "mcp workshop fixture"
)

echo "준비 완료: $DEST_ABS"
echo "Claude 실행 전: export MCP_NOTES_PYTHON=$PYBIN"
echo "Codex 등록:  codex mcp add notes --env NOTES_DIR=$DEST_ABS/notes -- $PYBIN $DEST_ABS/notes_server.py"
