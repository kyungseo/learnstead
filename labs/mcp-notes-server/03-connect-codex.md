# 03. Codex에 꽂기

> 이전 ← [`02-connect-claude-code.md`](02-connect-claude-code.md) · 다음 → [`04-break-it.md`](04-break-it.md)

## 목표

`codex mcp add`로 같은 서버를 등록하고 `codex exec`에서 호출을 transcript로 확인합니다. 모델의 자기 보고와 실제 호출이 다를 수 있음을 봅니다.

## 1. 등록

`setup.sh`가 출력한 명령을 그대로 실행한다(형태):

```bash
codex mcp add notes --env NOTES_DIR=<워크숍 절대 경로>/notes -- <python 절대 경로> <워크숍 절대 경로>/notes_server.py
codex mcp list
codex mcp get notes
grep -n -A5 "mcp_servers.notes" ~/.codex/config.toml
```

`~/.codex/config.toml`에 `[mcp_servers.notes]`와 `[mcp_servers.notes.env]`가 생깁니다. **전역이므로** 실습 후 `codex mcp remove notes`로 지웁니다.

## 2. 호출

```bash
scripts/run-codex.sh c0 "Which MCP servers and MCP tools are available to you right now? List server name, tool names and descriptions. Do not call any tool."
scripts/run-codex.sh c1 "장보기 노트에 뭐가 적혀 있어?"
grep -v '^hook:' logs/c1.codex.txt | head -60
```

요약 줄이 뽑는 `mcp: notes/<tool> started` · `(completed)` 줄을 봅니다. transcript 머리의 `approval:`·`sandbox:` 값도 적어 둡니다.

## 3. 기록

| 실행 | transcript의 `mcp:` 줄 | 답 | 비고 |
| --- | --- | --- | --- |
| c0 | | | 모델이 도구를 안다고 했나 |
| c1 | | | |

## 작성 환경의 실제 결과

`codex exec` 머리: `approval: never`, `sandbox: read-only`.

| 실행 | `mcp:` 줄 | 답 |
| --- | --- | --- |
| c0 | 없음 | "`mcp__<server>__<tool>` 형태의 도구가 **보이지 않는다**"고 답함. host의 `list_mcp_resources` 같은 일반 도구만 나열 |
| c1 | `notes/list_notes started`·`(completed)`, `notes/read_note started`·`(completed)` | 정답 |

c0의 자기 보고는 틀렸습니다. 같은 서버가 c1에서 호출됐습니다. c1은 1회 실행에서 "메모 앱"이라는 표현에 반응해 컴퓨터 조작 skill을 먼저 열어 본 뒤 MCP로 넘어왔습니다. 토큰: c0 11,660 · c1 22,735.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| `mcp:` 줄이 없고 답도 못 함 | 등록 실패 / startup timeout(기본 10초) | `codex mcp get notes`, `startup_timeout_sec` 상향 |
| stdin 대기로 멈춤 | `< /dev/null` 누락 | `run-codex.sh` 사용 |
| `$` 때문에 프롬프트가 깨짐 | 큰따옴표 | 작은따옴표 |
