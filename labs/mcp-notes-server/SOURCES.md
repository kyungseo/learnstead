# SOURCES

최초 확인일은 2026-08-30이며, 설정·실행 스크립트와 핵심 공식 문서는 2026-09-02에 다시 확인했다.

## 1차 자료

| 자료 | 무엇을 확인했나 |
| --- | --- |
| [MCP 규격 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) (Tools · Transports · stdio) | tool 정의·결과·오류 형식, annotations 신뢰 경고, stdio MUST 규칙 |
| [Python SDK v2 migration guide](https://py.sdk.modelcontextprotocol.io/migration/) · 설치본 introspection (mcp 2.1.1) | `MCPServer`·`@server.tool(annotations=…)`·`ToolError`·`run(transport="stdio")`·`Client(StdioServerParameters)` |
| [Claude Code 공식 문서 "MCP"](https://code.claude.com/docs/en/mcp) (2.1.251) | `.mcp.json`·scope·`-p` 로드·`mcp__server__tool` 권한·변수 치환·`--strict-mcp-config` |
| Codex CLI 공식 문서 "MCP" (0.144.1) | `codex mcp add`·`config.toml` 필드·`default_tools_approval_mode` |
| `claude --help`, `claude mcp add --help`, `codex mcp add --help`, `codex exec --help` | 옵션 |
| 직접 실행 | 각 단계의 "작성 환경의 실제 결과" |

## 2차 자료

없음.
