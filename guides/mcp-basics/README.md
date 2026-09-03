# AI Agent에 내 도구를 연결하는 법 — MCP 기초

![AI Agent가 권한을 확인하는 연결 허브를 거쳐 문서와 데이터베이스와 도구를 사용하는 손그림](assets/mcp-basics-hero.webp)

AI Agent가 내 노트·데이터베이스·사내 API를 사용하게 하려면 무엇을 연결해야 할까요? MCP(Model Context Protocol)는 이런 도구와
데이터를 여러 AI 앱이 공통 방식으로 사용할 수 있게 하는 연결 규약입니다.

이 가이드는 설정법보다 한 단계 앞에서 시작합니다. 모델은 도구 호출을 **제안하고**, host 런타임과 MCP 서버가 권한을 확인해
**실행합니다.** Python으로 작은 노트 서버를 만들고 Claude Code와 Codex에 연결한 뒤, 잘못된 경로·거짓 권한 힌트·문서 속
주입 지시·stdout 오염까지 직접 재현합니다.

## 학습 달성 목표(Learning Objective)

이 가이드를 끝내면:

- MCP의 **host · client · server를** 구분하고 모델과 실제 실행 사이의 경계를 설명할 수 있습니다.
- 서버가 주는 **tools · resources · prompts와** tool 정의·결과·오류 두 종류를 구분할 수 있습니다.
- **stdio와** **Streamable HTTP를** 구분하고 stdio 서버의 규칙(stdout 금지)을 지킬 수 있습니다.
- Claude Code·Codex에 서버를 **등록·확인·제거하고** 비-대화형으로 호출할 수 있습니다.
- 권한을 **서버·데이터 권한 · annotation · host 승인** 세 겹으로 보고, 어느 층이 실제로 막는지 실측으로 확인할 수 있습니다.
- skill(절차)과 MCP(능력)를 역할로 구분하고 함께 쓸 수 있습니다.

## 누구를 위한 가이드인가

- 코딩 에이전트에 내 파일·DB·사내 API를 붙이고 싶은 사람.
- `.mcp.json`이나 `mcp_servers` 설정을 봤는데 무엇이 어디서 실행되는지 모르는 사람.
- [agent-skills 가이드](../agent-skills/README.md)에서 "MCP = 능력"이라는 칸을 보고 실체를 알고 싶은 사람.

Python 함수를 읽을 수 있으면 실습까지 진행할 수 있습니다. [tool calling](../local-llm-app-integration/06-tool-calling-workflow-agent.md)의
왕복을 알면 1장이 빠르고, skill이 낯설다면 [Agent Skills 기초](../agent-skills/README.md)의 00~03장을 먼저
읽는 편이 좋습니다.

## 읽는 순서

| 장 | 파일 | 한 줄 |
| --- | --- | --- |
| 01 | [`01-the-problem-mcp-solves.md`](01-the-problem-mcp-solves.md) | MCP가 필요한 때, M×N 문제, 세 역할, 2026-07-28 개정판 |
| 02 | [`02-what-a-server-offers.md`](02-what-a-server-offers.md) | tools·resources·prompts, tool 정의 필드, 결과·오류 두 종류, `ToolError` |
| 03 | [`03-transports.md`](03-transports.md) | stdio 규칙과 stdout 오염 관측, 무상태, HTTP로 가는 때 |
| 04 | [`04-connecting-to-tools.md`](04-connecting-to-tools.md) | 등록·scope·설정 파일·도구 이름·지연 로드·`-p`/`exec`, 환경 변수와 기본값 |
| 05 | [`05-permission-boundaries.md`](05-permission-boundaries.md) | 세 겹 경계, 거짓 annotation·permission mode·주입 실측, 우회 경로 |
| 06 | [`06-skills-and-mcp.md`](06-skills-and-mcp.md) | 절차 vs 능력, skill+MCP 실측, 어디에 두면 안 되는가 |
| 07 | [`07-what-goes-wrong.md`](07-what-goes-wrong.md) | 연결·발견·호출 세 층의 실패 지도, 신뢰 경계, 진단 순서 |
| 08 | [`08-glossary.md`](08-glossary.md) | 등장 순서대로 정리한 용어 |
| — | [`MCP-CARD.md`](MCP-CARD.md) | 한 장 요약 |

## 함께 보는 실습

수치와 관측은 모두 **[실습: 노트 MCP 서버](../../labs/mcp-notes-server/README.md)** 에서 나왔습니다. Python 80줄 읽기 전용 노트 서버를 만들어 LLM 없이 호출하고, Claude Code·Codex에 연결합니다. 이어서 권한 밖 호출·거짓 annotation·주입 지시문·stdout 오염을 재현한 뒤 skill과 결합합니다.

가이드 01~03 → 실습 01 → 가이드 04 → 실습 02~03 → 가이드 05 → 실습 04 → 가이드 06 → 실습 05 → 가이드 07~08 순서로 오가며 읽으면 개념과 실행 결과가 바로 이어집니다.

## 가이드 작성 중 직접 확인한 검증 기록

최초 작성 환경은 macOS, Python 3.14, `mcp==2.1.1`, Claude Code 2.1.251, Codex CLI 0.144.1, 2026-08-30입니다.
2026-09-02에 MCP 규격과 현재 도구 문서를 다시 확인했습니다. 세부는 [`VALIDATION.md`](VALIDATION.md)에 있습니다.

- 규격 필드만 쓴 stdio 서버가 두 도구에서 등록·호출됐습니다. Claude Code는 project scope `.mcp.json`을 `-p`에서 승인 없이 로드했습니다.
- 2026-08-30에는 `.mcp.json`의 `${CLAUDE_PROJECT_DIR}` 단독 사용이 연결에 실패했습니다. 현재 문서는 project/user scope에서
  `${CLAUDE_PROJECT_DIR:-.}`처럼 기본값을 붙이도록 안내하므로 실습 설정을 이 방식으로 갱신했습니다.
- Codex는 정직한 쓰기 도구를 `approval: never`에서 취소했지만 거짓 `read_only_hint`를 단 쓰기 도구는 실행했습니다. Claude Code는 annotation과 무관하게 permission mode·허용 목록으로만 거부했습니다(작성 환경의 `defaultMode: "auto"`에서는 거부 0건).
- 주입 지시문은 Claude Code 2/2·Codex 1/1·skill 경유 2/2에서 모두 무시됐습니다. 발견 사실까지 알린 것은 Claude Code 단독 2/2와 skill 경유 2/2였습니다.
- stdout에 잘못된 줄을 써도 SDK client와 Claude Code는 건너뛰고 동작했습니다.
- Gemini CLI·Cursor는 확인하지 않았습니다.

## 검증 표기

| 표기 | 뜻 |
| --- | --- |
| [원리] | 설계 원칙·정의에서 따라오는 내용 |
| [실행 검증] | 작성 환경에서 실제로 실행해 관측 |
| [부분 검증] | 일부 조건에서만 실행 확인 |
| [문서 확인] | 규격·공식 문서에서 확인, 미실행 |
| [자료 확인] | 2차 자료에서 확인 |
| [미검증] | 확인하지 못한 추정 |
| [해석] | 관측에 대한 작성자의 해석 |

## 관련 자료

- 규격: [Model Context Protocol](https://modelcontextprotocol.io) — 2026-07-28 개정판
- 다음 학습: [Context Engineering 기초](../context-engineering/README.md) — MCP 도구 결과까지 포함해 모델이
  무엇을 얼마나 읽을지 설계합니다.
- 이 가이드가 다루지 않는 것: 원격 HTTP 서버 배포와 OAuth, MCP Apps·Tasks 확장, host(client 쪽) 앱 개발, Gemini CLI·Cursor 연결.

**시작 →** [01 MCP가 푸는 문제](01-the-problem-mcp-solves.md)
