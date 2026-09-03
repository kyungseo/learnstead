# 07. 잘못되는 방식

> 이전 ← [`06-skills-and-mcp.md`](06-skills-and-mcp.md) · 다음 → [`08-glossary.md`](08-glossary.md)

## 이 장에서 답하는 질문

- "연결이 안 된다", "도구를 안 쓴다", "이상하게 쓴다"를 어떻게 좁히는가
- 실측에서 실제로 걸린 것들은 무엇이었나

## 1. 세 단계로 좁히기

| 단계 | 대표 증상 | 먼저 확인할 것 |
| --- | --- | --- |
| ① 연결 | 서버가 안 뜨거나 곧바로 종료된다 | 설정의 실행 명령, 경로, 환경 변수 |
| ② 발견 | 연결됐지만 모델이 도구를 고르지 않는다 | 도구 설명, 실제 transcript의 호출 기록 |
| ③ 호출 | 도구를 골랐지만 거부되거나 결과가 이상하다 | 권한 규칙, 입력 검증, 서버 오류 |

## 2. ① 연결 실패

| 증상 | 원인 후보 | 확인 · 조치 |
| --- | --- | --- |
| `CONNECTION_CLOSED` / `Connection closed` | 명령이 바로 종료됨 — 경로 오류, 인터프리터에 `mcp` 없음, import 오류 | 터미널에서 설정의 명령을 **그대로** 실행해 본다. 실습에서는 기본값 없는 `${CLAUDE_PROJECT_DIR}`가 환경에 없어 실패한 적이 있다 [2026-08-30 실행 검증] |
| `Missing environment variables: X` (Claude Code) | `.mcp.json`의 `${X}`가 환경에 없음 | 환경 변수를 내보내거나 `${X:-default}`로 기본값을 둔다. `claude mcp list`에서 경고를 확인한다 |
| `⏸ Pending approval` | project scope 서버 미승인 | 대화형 `claude`에서 승인. `-p`는 승인 없이 로드됨 |
| `No module named 'mcp.server.fastmcp'` | SDK 2.x에서 v1 예제 사용 | `from mcp.server.mcpserver import MCPServer` |
| startup timeout (Codex 기본 10초) | 서버 시작이 느림(무거운 import) | `startup_timeout_sec` 상향, import 지연 로드 |
| 도구는 있는데 결과가 깨짐 | stdout 오염 | 3장 2절. 최신 클라이언트는 줄을 버리지만 규격 위반. 로그를 stderr로 |
| 서버가 연결마다 다시 뜬다 | 정상 | stdio + 무상태. 시작 비용을 줄인다 |

## 3. ② 발견 실패

| 증상 | 원인 후보 | 확인 · 조치 |
| --- | --- | --- |
| 모델이 "MCP 도구가 없다"고 답함 (Codex) | 자기 보고 오류. 실제로는 호출 가능 [실행 검증] | 목록을 묻지 말고 **작업을 시켜** transcript의 `mcp:` 줄을 본다 |
| 모델이 도구 설명을 모름 (Claude Code) | 지연 로드 — `ToolSearch` 전에는 이름만 | 정상. 요청을 주면 알아서 로드 |
| 도구를 안 고르고 파일을 직접 읽음 | 서버 실패 후 우회, 또는 description이 요청 어휘와 안 맞음 | 서버 상태 먼저. 다음은 docstring에 사용자 어휘 |
| 엉뚱한 skill·도구로 감 (Codex가 "메모 앱"에 컴퓨터 조작 skill을 먼저 염) | 요청 어휘가 다른 능력의 설명과 겹침 | 요청에 서버 이름을 넣거나 skill로 라우팅 |
| 도구가 너무 많아 목록이 잘림 | 서버 여러 개 × 도구 수십 개 | Claude Code는 tool search로 완화. 안 쓰는 서버는 끈다(`/mcp`, `enabled=false`) |

## 4. ③ 호출 실패

| 증상 | 원인 후보 | 확인 · 조치 |
| --- | --- | --- |
| `permission_denials` (Claude Code) | 허용 목록에 없음 + `permission-mode default` | `--allowedTools mcp__notes__read_note …` 또는 설정 allow 규칙 |
| 거부가 전혀 없음 (Claude Code) | `defaultMode: "auto"` 등 자동 승인 설정 | 5장 4절. 비-대화형은 mode를 명시 |
| `user cancelled MCP tool call` (Codex exec) | 쓰기 도구 + 승인할 사람 없음 | 의도한 것. 자동 실행하려면 `default_tools_approval_mode`·annotation 검토 |
| 쓰기 도구가 승인 없이 실행됨 (Codex) | 서버의 거짓 annotation | 남의 서버는 `prompt` 또는 `enabled_tools` |
| `Error executing tool X` 만 나오고 이유가 없음 | 서버가 일반 예외를 던짐 | `ToolError`로 문구를 노출. 다음 행동을 적는다 |
| 결과가 잘림 / 경고 | 출력이 Claude Code 상한(기본 25,000 토큰, 경고 10,000)을 넘음 | 도구가 페이지네이션·요약을 지원하게. `MAX_MCP_OUTPUT_TOKENS` [문서 확인] |
| 오래 걸리는 호출이 백그라운드로 감 | 2분 초과 시 Claude Code 자동 백그라운드(2.1.212+) | 정상. `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` [문서 확인] |
| 주입된 지시문을 따름 | 모델 판단 실패 | 구조적으로 막는다 — 쓰기 도구 미노출·허용 목록 제외 |
| 경계 밖 파일을 읽음 | 서버 경로 검사 없음 | `_safe_path` 같은 검사. 모델을 믿지 않는다 |

## 5. 신뢰 경계 실패

- `.mcp.json`은 저장소에 들어옵니다. **남의 저장소를 `-p`로 돌리면 그 안의 서버가 내 장비에서 실행됩니다** [실행 검증 · 문서 확인]. 필요하면 `--strict-mcp-config`나 `disabledMcpjsonServers`로 제한합니다.
- 서버가 외부 콘텐츠를 가져오면 그 콘텐츠가 프롬프트 주입 경로가 됩니다 [문서 확인 · Claude Code]. 실습의 노트가 그 축소판입니다.
- `headersHelper`·환경 변수로 자격 증명을 넘기는 서버는 어떤 변수가 제거·전달되는지 확인합니다 [문서 확인].

## 6. 진단 순서

1. `claude mcp list` / `codex mcp list` — 상태와 경고.
2. 설정의 명령을 터미널에서 직접 실행 — 즉시 종료되면 ①.
3. SDK client(`probe.py`)로 LLM 없이 `tools/list` — 서버 문제와 host 문제를 분리.
4. 실제 요청을 주고 로그의 호출 줄을 본다 — 모델의 말은 근거가 아니다.
5. 거부·취소 줄이 있으면 ③의 권한 표.

## 이 장을 끝내면

- 연결·발견·호출 세 층으로 증상을 나누고 첫 확인 명령을 선택할 수 있습니다.
- 모델의 자기 보고 대신 로그를 봅니다.
- 남의 `.mcp.json`이 내 장비에서 실행되는 경계를 이해할 수 있습니다.
