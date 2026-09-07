# 출처

**나눴더니 틀렸다 — 패턴별 실측과 실패 재현에서** version에 따라 달라질 수 있는 정보와 그 근거를 연결합니다.

- 마지막 확인일: 2026-08-30
- `문서 확인`은 공식 문서를 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다. 직접 실행한 결과는 [VALIDATION.md](VALIDATION.md)에 있습니다.
- **이 실습의 수치는 전부 자체 실행 결과이며,** 다른 모델·환경·버전에서 재현된다는 보장은 없습니다.

## 실행 환경

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| OpenAI 호환 호출 | `chat.completions.create`, `response_format`, `usage` 필드 | [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) | 문서 확인 |
| 구조화 출력 | JSON schema로 출력 강제 (라우터·평가자) | [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | 문서 확인 |
| Ollama 동시 처리 | `OLLAMA_NUM_PARALLEL` — 지정하지 않으면 메모리에 따라 자동, 요청이 큐에서 순차 처리될 수 있음 | [Ollama FAQ](https://docs.ollama.com/faq) | 문서 확인 |
| 실습 모델 | `gemma3:4b` 태그·라이선스 | [Ollama library gemma3](https://ollama.com/library/gemma3) | 문서 확인 |
| 문자열 유사도 | `difflib.SequenceMatcher.ratio()` (`--stop-on-repeat`) | [Python difflib](https://docs.python.org/3/library/difflib.html) | 문서 확인 |

## 패턴

| 범위 | 확인한 내용 | 자료 | 상태 |
| --- | --- | --- | --- |
| 기본 패턴 정의 | 프롬프트 체이닝·라우팅·병렬화·오케스트레이터-워커·평가자-최적화기 | [Building effective agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents) | 문서 확인 |

## Source ledger를 갱신하는 규칙

1. 스크립트의 모델·API claim을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.

## 2026-09-07 보강 시 재확인

[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)의 고정 경로 workflow·동적 agent 구분, 고정 병렬 분배와 동적 작업 분해의 차이, 반복 후보 비교·평가 피드백의 활용을 확인했습니다. 이 실습의 `workers`는 고정 분배 구현입니다. 기존 프레임워크·실행 환경 항목의 확인일은 유지합니다.
