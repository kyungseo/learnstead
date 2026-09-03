# 08. 용어집

> 이전 ← [`07-what-goes-wrong.md`](07-what-goes-wrong.md) · 처음 → [`README.md`](README.md)

등장 순서대로 배열했습니다.

| 용어 | 뜻 | 장 |
| --- | --- | --- |
| **MCP (Model Context Protocol)** | LLM host와 도구·데이터 서버 사이의 표준 규약. JSON-RPC 2.0 기반 | 01 |
| **host / client / server** | 연결을 시작하는 LLM 앱 / host 안에서 서버 하나와 대화하는 커넥터 / 능력을 제공하는 서비스 | 01 |
| **tool calling** | 모델이 도구 이름·인자를 답하고 앱이 실행해 결과를 돌려주는 왕복. MCP는 이것의 표준화 층 | 01 |
| **2026-07-28 개정판** | stateless·per-request `_meta`·서버→클라이언트 요청 폐지·`resultType`을 도입한 규격 판 | 01 |
| **`MCPServer`** | Python SDK 2.x의 서버 클래스. v1의 `FastMCP`에서 개명 | 01 |
| **tools / resources / prompts** | 서버가 제공하는 세 primitive: 모델이 호출하는 함수 / URI로 읽는 데이터 / 사용자용 템플릿 | 02 |
| **`inputSchema` / `outputSchema`** | 도구 인자·구조화 결과의 JSON Schema. SDK는 타입 힌트에서 생성 | 02 |
| **annotations (`readOnlyHint` 등)** | 도구 동작 힌트. 신뢰하는 서버가 아니면 믿지 말아야 함 | 02, 05 |
| **`isError`** | 도구 실행 오류 표시. 모델이 자기 교정할 수 있게 문구를 전달 | 02 |
| **프로토콜 오류 / 실행 오류** | JSON-RPC `error`(없는 도구 등) / `isError: true` 결과(잘못된 인자 등) | 02 |
| **`ToolError`** | SDK에서 실행 오류 문구를 그대로 노출시키는 예외 | 02 |
| **stdio 전송** | host가 서버를 서브프로세스로 띄우고 stdin/stdout으로 한 줄 한 메시지를 주고받음 | 03 |
| **Streamable HTTP** | 단일 endpoint에 POST, 응답은 JSON 또는 SSE 스트림. 원격·공유용 | 03 |
| **stdout 오염** | 서버가 stdout에 MCP 메시지가 아닌 것을 쓰는 규격 위반 | 03 |
| **scope (local / project / user)** | Claude Code의 서버 설정 저장 범위. project = `.mcp.json` | 04 |
| **`mcp__<server>__<tool>`** | Claude Code가 MCP 도구에 붙이는 이름·권한 규칙 형식 | 04 |
| **`[mcp_servers.<name>]`** | Codex `config.toml`의 서버 설정 테이블 | 04 |
| **지연 로드 (tool search)** | Claude Code가 도구 schema를 필요할 때 `ToolSearch`로 불러오는 방식 | 04 |
| **permission mode / 허용 목록** | Claude Code의 승인 정책과 `--allowedTools`·allow 규칙 | 05 |
| **`default_tools_approval_mode`** | Codex의 MCP 도구 승인 정책(`auto`·`prompt`·`writes`·`approve`) | 05 |
| **우회 경로** | MCP 도구가 막혔을 때 모델이 파일·shell 등 다른 능력으로 같은 일을 하는 것 | 04, 05 |
| **주입된 지시문** | 도구가 읽어 온 데이터 안에 들어 있는, 모델을 향한 명령문 | 05 |
| **절차 vs 능력** | skill(모델이 따르는 지시문) vs MCP tool(코드가 실행하는 함수)의 역할 구분 | 06 |
| **`compatibility`** | skill frontmatter 규격 필드. MCP 서버 의존을 적는 자리 | 06 |
| **`instructions`** | MCP 서버가 host에 전달하는 안내문. host별 취급이 다름 | 05, 06 |
