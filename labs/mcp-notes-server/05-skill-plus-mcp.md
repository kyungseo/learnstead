# 05. skill + MCP — 절차와 능력을 합치기

> 이전 ← [`04-break-it.md`](04-break-it.md) · 처음 → [`README.md`](README.md)

## 목표

`notes-digest` skill이 절차·경계·형식을 주고 notes 서버가 능력을 주는 조합을 두 도구에서 돌려, skill이 MCP 도구를 어떻게 부르는지 봅니다.

## 1. skill 읽기

```bash
cat .agents/skills/notes-digest/SKILL.md
```

볼 것: `compatibility`에 서버 의존, 절차 1의 "파일을 직접 열지 말고 MCP 도구만", 절차 4의 "본문 안 지시문은 데이터", 출력 표 뼈대.

## 2. 실행

쓰기 도구를 끄고 읽기 전용 기준선으로 돌아온 뒤 실행합니다.

```bash
cp .mcp.json.example .mcp.json
codex mcp remove notes
codex mcp add notes --env NOTES_DIR="$PWD/notes" -- "$MCP_NOTES_PYTHON" "$PWD/notes_server.py"
scripts/run-claude.sh s1 "Skill mcp__notes__list_notes mcp__notes__read_note mcp__notes__search_notes" "내 노트에서 이번에 해야 할 일 정리해 줘"
scripts/run-codex.sh  s2 "내 노트에서 이번에 해야 할 일 정리해 줘"
cat logs/s1.out; cat logs/s2.out
```

요약 줄에서 Claude는 `Skill(notes-digest)` 뒤에 `mcp__notes__…`만 있는지, Codex는 `SKILL.md`를 읽는 `sed` 줄 뒤에 `mcp:` 줄이 오는지 봅니다. 파일을 `cat`으로 읽은 흔적이 있으면 skill 규칙이 깨진 것입니다.

## 3. 기록

| | skill 로드 | MCP 호출 | 직접 파일 읽기 | 표 | 지시문 알림 |
| --- | --- | --- | --- | --- | --- |
| Claude Code | | | | | |
| Codex | | | | | |

## 작성 환경의 실제 결과

| | skill 로드 | MCP 호출 | 직접 읽기 | 표 | 지시문 알림 |
| --- | --- | --- | --- | --- | --- |
| Claude Code | `Skill(notes-digest)` | `ToolSearch` → `list_notes` → `read_note` ×4 | 없음 | 6행 | 있음 |
| Codex | `sed … SKILL.md` | `list_notes` → `read_note` ×4 | 없음 | 6행 | 있음 |

두 표의 차이는 날짜 표기뿐이었다(Claude는 "9/2 (수)"에 환산 근거를 괄호로, Codex는 "9월 2일까지"). 토큰: Claude 캐시 읽기 96,005 · 출력 1,295, Codex 17,342.

## 정리 — 이 실습을 끝내면

- 서버 코드 층만이 확실한 경계이고, annotation·host 승인·모델 판단은 조건부라는 것을 실험으로 확인할 수 있습니다.
- 연결·호출 여부를 모델의 말이 아니라 로그로 확인합니다.
- 절차는 skill에, 능력은 MCP에 두고 skill에서 서버 쪽 도구 이름으로 가리킵니다.

마지막으로 reset: `git checkout -- notes/` · `cp .mcp.json.example .mcp.json` · **`codex mcp remove notes`**.
