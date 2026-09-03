# SOURCES

초판 실행은 2026-08-30, 문서 재확인은 2026-09-02에 수행했다.

## 1차 자료 — 규격·공식 문서·직접 실행

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| [MCP 규격 2026-07-28 — Specification 개요](https://modelcontextprotocol.io/specification/2026-07-28/basic) | host/client/server 정의, 세 primitive, JSON-RPC, 보안 원칙(사용자 동의·데이터 프라이버시·도구 안전), 확장(Tasks·Skills over MCP·Apps) | 01, 05 |
| [MCP 규격 2026-07-28 — Server Features: Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | `tools/list`·`tools/call` 형식, tool 정의 필드, 이름 규칙, annotations 신뢰 경고, 결과 content 종류·`structuredContent`·`outputSchema`, `input_required`, 상태 핸들 지침, 프로토콜 오류 vs 실행 오류, 서버 MUST·클라이언트 SHOULD 보안 항목 | 02, 05 |
| [MCP 규격 2026-07-28 — Base Protocol: Transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports) | 두 전송 binding, stdio의 MUST/SHOULD(stdout 금지·stderr 로그·EOF 종료·재시작), `_meta` 요청 메타데이터, 하위 호환 probe | 03 |
| [MCP 규격 2025-03-26 — Transports](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)·[2025-06-18 — Transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) | HTTP+SSE에서 Streamable HTTP로 바뀐 시점과 호환 경로 | 03 |
| [Python SDK v2 migration guide](https://py.sdk.modelcontextprotocol.io/migration/) | `FastMCP`→`MCPServer`, `@server.tool()`, 전송 옵션 `run()` 이동, snake_case 필드, `Client` 사용법 | 01, 02, 03 |
| Python SDK 2.1.1 설치본 introspection | `MCPServer.__init__`·`tool`·`run` 서명, `ToolAnnotations` 필드, `ToolError`, `Client(StdioServerParameters)` | 02, 03 |
| [Claude Code 공식 문서 "MCP"](https://code.claude.com/docs/en/mcp) (2.1.258에서 재확인) | `claude mcp add` 문법·scope·`.mcp.json`·승인 프롬프트와 `-p` 무프롬프트 로드, `mcp__server__tool` 권한, `/mcp`, 변수 치환(`${VAR}`·`${VAR:-default}`), tool search·discovery cache, 출력 상한·timeout·자동 백그라운드, 보안 경고 | 04, 05, 07 |
| [Claude Code 공식 권한 문서](https://code.claude.com/docs/en/permissions)·[Agent SDK MCP 문서](https://code.claude.com/docs/en/agent-sdk/mcp) | MCP tool 권한 이름, wildcard 문법, 명시적 허용 범위 | 04, 05 |
| Codex CLI 공식 문서 "MCP" (0.144.1 기준) | `codex mcp add` 문법, `config.toml` 필드(`command`·`args`·`env`·`cwd`·`url`·`startup_timeout_sec`·`tool_timeout_sec`·`enabled`·`enabled_tools`·`disabled_tools`·`default_tools_approval_mode`), OAuth login, `/mcp`, 프로젝트 `.codex/config.toml` | 04, 05 |
| 직접 실행 — `claude -p`, `codex exec`, SDK `Client` | 실습 [`labs/mcp-notes-server`](../../labs/mcp-notes-server/README.md)의 전 관측 | 전체 |

## 2차 자료

없음.

## 확인하지 못한 것

- Gemini CLI·Cursor의 MCP 연결.
- 이전 판 클라이언트나 다른 host가 stdout 오염을 어떻게 처리하는지.
- Codex의 `default_tools_approval_mode`가 annotation 외에 무엇을 보는지(관측은 `auto` 기본값에서 정직/거짓 annotation 각 1회).
- Codex에서 서버 `instructions`가 모델에게 어떻게 전달되는지.
