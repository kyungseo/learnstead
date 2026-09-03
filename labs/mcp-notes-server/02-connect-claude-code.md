# 02. Claude Code에 꽂기

> 이전 ← [`01-build-and-probe.md`](01-build-and-probe.md) · 다음 → [`03-connect-codex.md`](03-connect-codex.md)

## 목표

project scope 설정(`.mcp.json`)으로 서버를 등록하고, 비-대화형 `claude -p`에서 서버 상태·도구 호출을 로그로 확인합니다. 환경마다 다른 Python 경로는 변수로 분리합니다.

## 1. 설정 확인

```bash
cat .mcp.json
claude mcp list
claude mcp get notes
```

`setup.sh`가 만든 `.mcp.json`은 `${MCP_NOTES_PYTHON:-python3}`과 `${CLAUDE_PROJECT_DIR:-.}`을 사용합니다. 먼저 `MCP_NOTES_PYTHON`이 현재 shell에 설정됐는지 확인합니다. `claude mcp list`는 project 서버를 `⏸ Pending approval`로 보여 줄 수 있습니다. 대화형 세션에서 승인하는 항목이지만 `-p`에서는 그대로 로드됩니다.

## 2. 변수와 기본값 확인

```bash
printf '%s\n' "$MCP_NOTES_PYTHON"
claude mcp list
```

`${VAR:-default}`는 변수가 없을 때 기본값을 쓴다는 뜻입니다. `CLAUDE_PROJECT_DIR`가 제공되지 않는 실행 환경에서도 `.`을 사용하므로 저장소 안의 `notes_server.py`와 `notes/`를 찾을 수 있습니다. Python 가상환경 경로는 장비마다 다르므로 `.mcp.json`에 박아 두지 않고 `MCP_NOTES_PYTHON`으로 전달합니다.

## 3. 호출

```bash
scripts/run-claude.sh e0 - "What MCP servers and MCP tools are available to you? List server name, tool names, and each tool's description. Do not call any tool."
scripts/run-claude.sh e1 "mcp__notes__list_notes mcp__notes__read_note mcp__notes__search_notes" "장보기 노트에 뭐가 적혀 있어?"
```

요약 줄에서 `mcp=[('notes', 'connected'), …]`, `tools=`의 `ToolSearch` → `mcp__notes__…` 순서를 봅니다. e0의 답에서 도구 설명이 "로드되지 않음"이라고 나오면 지연 로드입니다.

## 4. 기록

| 실행 | `mcp=` 상태 | 호출된 MCP 도구 | 비고 |
| --- | --- | --- | --- |
| e0 | | | |
| e1 | | | |

## 작성 환경의 실제 결과

| 실행 | 상태 | 호출 | 비고 |
| --- | --- | --- | --- |
| e0 | `connected` | 없음 | 서버 이름·`instructions` 인용·도구 이름 3개. 설명은 "Not loaded — 지연 로드" |
| e1 | `connected` | `ToolSearch(select:mcp__notes__…)` → `list_notes` → `search_notes("장보기")` → `read_note("장보기.md")` | 정답. **검색 중 `여행-계획.md`의 주입 지시문을 발견해 "무시했다"고 보고** |

e1 토큰: 캐시 읽기 69,605 · 출력 687. `--allowedTools` 없이 돌린 같은 요청도 작성 환경에서는 거부 없이 같은 경로로 답했습니다. 사용자 설정 `defaultMode: "auto"` 때문이며 04에서 다룹니다.

> 2026-08-30에는 기본값 없는 `${CLAUDE_PROJECT_DIR}`를 썼다가 환경 변수가 없어 `CONNECTION_CLOSED`가 발생했습니다. 당시 모델은 MCP 대신 파일을 직접 읽었습니다. 현재 실습은 `${CLAUDE_PROJECT_DIR:-.}`로 이 경로를 고쳤습니다. 같은 오류가 보이면 `claude mcp list`의 `Missing environment variables` 경고와 `MCP_NOTES_PYTHON` 값을 먼저 확인합니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| `mcp=[('notes','failed')]` | 명령이 바로 죽음 | `.mcp.json`의 `command`·`args`를 터미널에서 그대로 실행 |
| `needs-auth`인 다른 서버가 보임 | 계정에 연결된 커넥터 | 무관. 무시 |
| 이미 Claude Code 세션 안 | 중첩 실행 제한 | 별도 터미널 또는 `env -u CLAUDECODE` |
