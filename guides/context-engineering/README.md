# AI Agent가 놓치지 않게 정보 설계하기 — Context Engineering 기초

![여러 출처의 정보 카드 가운데 필요한 것만 골라 순서를 정한 뒤 AI Agent의 컨텍스트로 보내는 손그림](assets/context-engineering-hero.webp)

> 같은 모델을 써도 어떤 정보를 언제 보여 주느냐에 따라 답과 행동은 달라집니다. 코딩 에이전트가 읽는 지시문·Skills·MCP 결과·기억·작업 기록을 한 흐름으로 정리하고, 지시문의 크기와 위치가 실제 결과에 미친 영향도 살펴봅니다.

## 먼저 보는 큰 그림

Context Engineering은 긴 프롬프트 하나를 잘 쓰는 일보다 넓습니다. 모델이 판단할 때 필요한 정보를 **고르고, 가져오고, 순서를 정하고, 작업이 길어져도 유지하는 일에** 가깝습니다.

| 앞선 가이드 | Context Engineering에서 맡는 자리 |
| --- | --- |
| [내 장비에서 LLM 직접 실행하기](../local-llm/README.md) | 모델이 한 번에 볼 수 있는 물리적 범위와 실행 환경 |
| [Local LLM을 내 프로그램에 연결하기](../local-llm-app-integration/README.md) | 대화 이력·system message·tool result를 모델 요청으로 조립하는 곳 |
| [내 문서와 대화하는 AI 이해하기 — RAG와 Graph](../local-rag/README.md) | 질문에 맞는 근거를 그때그때 찾아오는 방법 |
| [Agent Skills 기초](../agent-skills/README.md) | 필요한 작업 절차만 선택해 읽히는 방법 |
| [MCP 기초](../mcp-basics/README.md) | 외부 도구와 데이터의 설명·실행 결과가 들어오는 통로 |

이 가이드는 이 재료들을 모델 앞에 무조건 쌓지 않습니다. 지금 필요한 정보인지, 신뢰할 수 있는지, 언제 다시 읽어야 하는지를 정하는 기준을 만듭니다.

## 학습 달성 목표(Learning Objective)

이 가이드를 끝내면:

- 컨텍스트의 출처와 수명 주기를 구분하고, 필요한 정보를 어느 시점에 넣을지 정할 수 있습니다.
- Claude Code·Codex의 **진입 지시문 발견 규칙**(계층·연결·크기)을 표로 그릴 수 있습니다.
- 조건부 로드 네 형태의 켜지는 조건을 알고, **pointer가 조건부 로드가 아님을** 실측으로 설명할 수 있습니다.
- Claude Code와 Codex의 로컬 memory 구조와 한계를 알고 팀 규칙을 개인 memory에 두지 않는 이유를 말할 수 있습니다.
- 압축(compaction) 후 각 층의 운명을 알고 살아남아야 할 지시를 파일로 옮길 수 있습니다.
- 지시문의 크기·위치·모호함이 준수율에 미친 영향을 수치로 말하고, 넣지 말 것 목록으로 지시문을 감사할 수 있습니다.

## 누구를 위한 가이드인가

- `CLAUDE.md`·`AGENTS.md`가 길어져 무엇이 지켜지고 무엇이 무시되는지 모르는 사람.
- "압축되고 나니 아까 말한 걸 잊었다"를 겪은 사람.
- skill·MCP를 만들고 나서 "그럼 진입 지시문에는 뭘 남기지"가 궁금한 사람.

필요한 배경은 코딩 에이전트로 파일을 읽고 고쳐 본 경험입니다. [Agent Skills](../agent-skills/README.md)의 "항상 vs 필요할 때" 구분을 알면 1장을 더 빠르게 읽을 수 있지만, 이 가이드부터 시작해도 됩니다.

## 읽는 순서

| 장 | 파일 | 한 줄 |
| --- | --- | --- |
| 01 | [`01-what-the-agent-reads.md`](01-what-the-agent-reads.md) | 컨텍스트의 출처와 수명 주기, Context Engineering의 역할 |
| 02 | [`02-entry-instructions.md`](02-entry-instructions.md) | `CLAUDE.md`·`AGENTS.md` 발견·연결·import·크기, "로드됐는데 안 지킨다" |
| 03 | [`03-always-vs-conditional.md`](03-always-vs-conditional.md) | 경로 규칙·하위 지시문·skill·pointer, 같은 규칙을 어디에 두느냐 실측 |
| 04 | [`04-memory.md`](04-memory.md) | 지시문 vs auto memory vs 작업 문서, 두지 말 것 |
| 05 | [`05-budget-and-compaction.md`](05-budget-and-compaction.md) | 무엇이 컨텍스트를 채우나, 압축 후 생존표, 손잡이 |
| 06 | [`06-size-vs-adherence.md`](06-size-vs-adherence.md) | 변형 6 × 3회 × 2도구 실측과 해석, 한계 |
| 07 | [`07-what-not-to-put-in.md`](07-what-not-to-put-in.md) | 넣지 말 것 12, 감사 순서 7, 꼭 넣을 것 4 |
| 08 | [`08-glossary.md`](08-glossary.md) | 등장 순서대로 정리한 용어 |
| — | [`CONTEXT-CARD.md`](CONTEXT-CARD.md) | 한 장 요약 |

## 함께 보는 실습

수치는 모두 **[실습: 지시문 예산](../../labs/instruction-budget/README.md)** 에서 나왔습니다. 작은 Python 프로젝트에 검사 가능한 규칙 5개를 정하고, 지시문 없음·짧게·길게·pointer·import·조건부 여섯 변형을 두 도구에서 3회씩 돌려 기계 판정했습니다. 1라운드는 규칙이 코드에서 추론 가능한 상태라 모든 변형이 만점이었고, 이 결과를 바탕으로 2라운드에서는 기존 코드가 규칙을 따르지 않도록 실험 조건을 바꿨습니다.

## 가이드 작성 중 직접 확인한 검증 기록

작성 환경: macOS, Claude Code 2.1.251(claude-fable-5, 사용자 설정 `permissions.defaultMode: "auto"`), Codex CLI 0.144.1(gpt-5.6 계열), 2026-08-30~31. 세부는 [`VALIDATION.md`](VALIDATION.md).

- 지시문 없음 0/15(두 도구) · 짧은 지시문 Claude 11 / Codex 15 · 긴 지시문(176줄) Claude 11 / Codex 10 · pointer Claude 9 / Codex 14 · import Claude 13 / Codex 14 · 조건부 Claude 경로 규칙 13 / Codex 중첩 AGENTS.md 6.
- 기존 코드가 규칙을 따르는 1라운드에서는 모든 변형이 15/15 — 모델은 코드에서 관례를 추론합니다.
- 지시문 없을 때 Claude Code 턴 수·캐시 읽기가 약 두 배(8턴·16.8만 vs 4턴·7.5만).
- Claude Code가 놓친 항목은 전부 테스트 함수의 docstring·타입 힌트 — "모든 함수"를 좁게 읽음.
- Codex 중첩 `src/AGENTS.md`는 루트에서 실행 시 자동 로드되지 않았다(모델이 파일로 읽음).
- Claude Code auto memory 디렉터리와 `MEMORY.md`가 작성 장비에 존재함을 확인했습니다. Codex의 local memory는 2026-09-02 현재 opt-in 기능이며, 두 도구의 memory를 팀 규칙의 유일한 저장소로 쓰지 않습니다.

## 검증 표기

| 표기 | 뜻 |
| --- | --- |
| [원리] | 설계 원칙·정의에서 따라오는 내용 |
| [실행 검증] | 작성 환경에서 실제로 실행해 관측 |
| [부분 검증] | 일부 조건에서만 실행 확인 |
| [문서 확인] | 공식 문서에서 확인, 미실행 |
| [자료 확인] | 2차 자료에서 확인 |
| [미검증] | 확인하지 못한 추정 |
| [해석] | 관측에 대한 작성자의 해석 |

## 관련 자료

- Anthropic, "Effective context engineering for AI agents" (2025-09-29) — 정의·주의 예산·just-in-time·compaction·note-taking
- 이 가이드가 다루지 않는 것: RAG 구현(→ [rag-and-graph](../local-rag/README.md)), Skill 작성(→ [agent-skills](../agent-skills/README.md)), MCP 서버 구현(→ [mcp-basics](../mcp-basics/README.md)), Gemini CLI·Cursor 실측.
