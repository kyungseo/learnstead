# 출처

**여러 AI를 엮어 일하게 하기 — Agent와 오케스트레이션에서** 버전에 따라 달라질 수 있는 정보와 그 근거를 연결합니다.

- 마지막 확인일: 2026-08-30 (초판 조사 2026-08-23)
- `문서 확인`은 공식 문서를 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다.
- 패턴 이름과 프레임워크 API는 빠르게 바뀝니다. **패턴의 모양은** 오래가지만 이름은 다를 수 있습니다.

## 실행 환경

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| OpenAI 호환 호출 | `chat.completions.create`, `response_format`, `usage` 필드 | [OpenAI API reference](https://platform.openai.com/docs/api-reference/chat) | 문서 확인 |
| 구조화 출력 | JSON schema로 출력 강제 | [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | 문서 확인 |
| Ollama 동시 처리 | 동시 요청 슬롯 `OLLAMA_NUM_PARALLEL`(기본값은 메모리에 따라 자동, 지정하지 않으면 요청이 큐에서 순차 처리될 수 있음) | [Ollama FAQ](https://docs.ollama.com/faq) | 문서 확인 |
| 실습 모델 | `gemma3:4b` 태그·라이선스 | [Ollama library gemma3](https://ollama.com/library/gemma3) | 문서 확인 |

## 패턴

| 범위 | 확인한 내용 | 자료 | 상태 |
| --- | --- | --- | --- |
| 워크플로와 agent의 구분, 기본 패턴 | 프롬프트 체이닝·라우팅·병렬화·오케스트레이터-워커·평가자-최적화기 | [Building effective agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents) | 문서 확인 |
| 멀티 agent 아키텍처 선택 | 서브에이전트·핸드오프·라우터의 트레이드오프 | [Choosing the right multi-agent architecture (LangChain)](https://www.langchain.com/blog/choosing-the-right-multi-agent-architecture) | 자료 확인 |
| 컨텍스트 격리의 효과 | 서브에이전트가 토큰을 줄이는 구조적 이유 | 공개 비교 자료 (아래 2차 자료) | 자료 확인 |
| 오케스트레이션 패턴 성능·트레이드오프 | 코디네이터 패턴 비교 | [Orchestration patterns for multi-agent systems (Microsoft ISE)](https://devblogs.microsoft.com/ise/coordinator-patterns-multi-agent-systems/) | 자료 확인 |

## 프레임워크 (2026-08-30 조회)

| 범위 | 확인한 내용 | 자료 | 상태 |
| --- | --- | --- | --- |
| AutoGen → Microsoft Agent Framework | AutoGen이 maintenance mode로 전환되고 Agent Framework 1.0(2026-04 GA)에 흡수됨 | [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) · [AutoGen repository](https://github.com/microsoft/autogen) | 자료 확인 |
| OpenAI Swarm → Agents SDK | Swarm(실험)이 Agents SDK로 대체됨 | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | 문서 확인 |
| LangGraph | subagent·handoff·router를 1급 개념으로 제공 | [LangGraph docs](https://langchain-ai.github.io/langgraph/) | 문서 확인 |

## Source ledger를 갱신하는 규칙

1. 본문의 패턴·API claim을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 블로그·비교 글은 탐색에만 쓰고, 확정 설명은 공식 문서로 확인합니다.
3. 직접 실행한 결과는 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.
4. **이 가이드의 수치는 전부 자체 실행 결과이며**, 다른 모델·환경에서 재현된다는 보장은 없습니다.

## 2026-09-07 보강 시 재확인

[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)의 고정 경로 workflow·동적 agent 구분, 고정 병렬 분배와 동적 작업 분해의 차이, 반복 후보 비교·평가 피드백의 활용을 확인했습니다. 이 실습의 `workers`는 고정 분배 구현입니다. 기존 프레임워크·실행 환경 항목의 확인일은 유지합니다.
