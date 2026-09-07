# 06. 용어집

> 이전 ← [`05-when-not-to.md`](05-when-not-to.md) · 처음 → [`README.md`](README.md)

모르는 단어가 나왔을 때 여는 참조 부록입니다. 서브에이전트·컨텍스트 격리처럼 앞선 가이드에 정의가 있는 용어는 그 정의를 따르고 링크를 둡니다.

## 1. 기본 구분

| 용어 | 뜻 |
| --- | --- |
| **워크플로 (workflow)** | 호출 **순서를 내 코드가** 정한 구성 ([02](02-pattern-map.md)) |
| **에이전트 (agent)** | 다음 행동을 **모델이** 정하는 루프 ([앱 연결 06](../../guides/local-llm-app-integration/06-tool-calling-workflow-agent.md)) |
| **서브에이전트 (subagent)** | 상위에서 일부 작업을 위임받는 agent. 전달받는 이력·자료·도구는 구현과 설정에 따라 달라짐 ([03](03-context-isolation.md) · 관련 정의는 [Agent Skills 용어집](../../guides/agent-skills/09-glossary.md) 참조) |
| **오케스트레이션 (orchestration)** | 여러 모델 호출·에이전트의 작업 순서와 결과 전달을 조정해 하나의 일을 완성하는 것 |
| **오케스트레이터 (orchestrator)** | 하위 작업을 정해 워커에게 배정하고 결과를 취합하는 구성 요소 ([실습 02](../../labs/when-splitting-fails/02-orchestrator-workers.md)) |
| **워커 (worker)** | 배정받은 하위 작업 하나를 수행하는 구성 요소 |
| **핸드오프 (handoff)** | 한 agent가 다른 agent에게 대화·작업을 넘기는 것. 해당 작업의 제어권 이전. 시스템의 다른 작업은 병렬일 수 있음 |

## 2. 네 패턴

| 용어 | 뜻 |
| --- | --- |
| **파이프라인 (pipeline / chain)** | 순서가 고정된 단계들. 각 단계가 다음의 입력을 좁힘 ([실습 01 §1](../../labs/when-splitting-fails/01-pipeline-router.md)) |
| **라우터 (router)** | 요청을 분류해 담당에게 위임. **오분류를 별도 평가** ([실습 01 §3](../../labs/when-splitting-fails/01-pipeline-router.md)) |
| **오케스트레이터-워커 (orchestrator-workers)** | 하위 과제를 배분하고 결과를 취합. 실습은 작업 분해를 코드가 고정 ([실습 02](../../labs/when-splitting-fails/02-orchestrator-workers.md)) |
| **평가-개선 루프 (evaluator-optimizer)** | 작성↔평가 반복. 평가 기준·피드백의 유용성과 반복의 이득을 확인해야 함 ([실습 03](../../labs/when-splitting-fails/03-evaluator-loop.md)) |
| **팬아웃/팬인 (fan-out / fan-in)** | 여러 워커에게 작업을 배정하기 / 완료된 결과를 모으기. 고정 작업 분배에도 쓰이는 흐름 |

## 3. 컨텍스트

| 용어 | 뜻 |
| --- | --- |
| **컨텍스트 격리 (context isolation)** | 각 구성 요소가 **필요한 것만** 보게 하는 것. 전달 자료로 확인 ([03](03-context-isolation.md)) |
| **컨텍스트 창 (context window)** | 한 번에 넣을 수 있는 토큰 한도 ([앱 연결 04 §2](../../guides/local-llm-app-integration/04-parameters-and-context.md)) |
| **prompt_tokens** | 한 호출의 입력 토큰 수. 입력 크기 지표이며 어떤 자료를 봤는지는 따로 확인 |
| **기준선 (baseline)** | 단일 호출로 만든 비교 기준. 여러 역할·단계를 적용한 구성은 이것과 비교 ([05 §4](05-when-not-to.md)) |

## 4. 실패와 방어

| 용어 | 뜻 |
| --- | --- |
| **오분류 전파** | 앞 단계의 틀린 판단 위에서 뒤가 정상 동작하는 실패 ([04 §1](04-failure-modes.md)) |
| **수렴 실패** | 루프가 통과를 못 받고 상한까지 반복 ([실습 03 §3](../../labs/when-splitting-fails/03-evaluator-loop.md)) |
| **조용한 손실** | 중간 결과는 맞았는데 취합에서 빠지는 것 |
| **상한 (cap)** | 호출 수·시간·토큰의 한계. 셋 다 필요 ([04 §3](04-failure-modes.md)) |
| **폴백 (fallback)** | 실패 시 되돌아갈 경로. 최후의 폴백은 **단일 호출** ([04 §4](04-failure-modes.md)) |
| **구조화 출력 (structured output)** | 단계 사이 전달을 스키마로 고정 ([앱 연결 05](../../guides/local-llm-app-integration/05-structured-output.md)) |

## 5. 혼동하기 쉬운 쌍 ★

| 쌍 | 차이 |
| --- | --- |
| **워크플로 vs agent** | 순서를 코드가 쥠 ↔ 모델이 쥠 |
| **서브에이전트 vs 함수 호출** | 하위 agent에 작업 위임 ↔ 코드 기능 실행. 함수가 별도 모델 호출을 시작할 수도 있음 |
| **라우터 vs 워커** | 담당 하나를 선택해 요청 ↔ 여러 워커 모두에게 작업을 배정 |
| **호출 수 vs 토큰** | 따로 움직임. 3회가 1회보다 쌀 수 있음 ([실습 01 §1](../../labs/when-splitting-fails/01-pipeline-router.md)) |
| **병렬 vs 빠름** | 병렬이어도 runtime이 동시 처리 안 하면 안 빨라짐 ([실습 02 §2](../../labs/when-splitting-fails/02-orchestrator-workers.md)) |
| **평가자 vs 테스트** | 같은 모델의 의견 ↔ 코드가 내리는 판정. **코드로 잴 수 있으면 코드로** |
| **작업 분담 vs 컨텍스트 격리** | 역할·단계를 구분해 처리 ↔ 각 호출에 전달할 자료를 제한. 별도 호출이라도 같은 자료 전체를 받을 수 있으므로 입력 범위와 비용을 따로 확인 |
| **오분류 vs 오류** | 예외 없이 정상처럼 보임 ↔ 예외가 남 |
