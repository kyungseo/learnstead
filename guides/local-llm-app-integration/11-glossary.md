# 11 — 용어집

전 문서의 **참조 부록**입니다. 순서대로 읽는 문서가 아니라, 모르는 용어가 나왔을 때 여는 문서입니다. 정의는 이 가이드의
서술 기준을 따르며, 상세 설명이 있는 본문 위치를 함께 적었습니다.

← [10 신뢰성과 운영](10-reliability-and-operations.md) · [README로](README.md)

---

## 1. 연결·API

| 용어 | 뜻 |
| --- | --- |
| **runtime** | 모델을 메모리에 올리고 HTTP로 요청을 받는 프로그램 (Ollama, vLLM, llama-server, LM Studio) ([01 §1](01-integration-anatomy.md)) |
| **OpenAI 호환 API** | OpenAI의 요청·응답 JSON 형식을 흉내 낸 endpoint. 기본 경로(`/v1/chat/completions`, `/v1/embeddings`)는 거의 같고 가장자리는 다름 ([02](02-openai-compatible-api.md)) |
| **`base_url`** | SDK가 요청을 보낼 주소. 백엔드 전환 시 `model`·키·지원 기능과 함께 바꾸고 확인함 ([01 §0](01-integration-anatomy.md)) |
| **endpoint** | 특정 기능의 URL 경로 (`/v1/chat/completions` 등) ([02 §0](02-openai-compatible-api.md)) |
| **SDK** | 요청 JSON을 대신 만들어 주는 라이브러리 (`openai` 패키지) ([01 §2](01-integration-anatomy.md)) |
| **프레임워크** | 여러 호출·부품을 엮는 층 (LangChain, LlamaIndex, Spring AI, LangChain4j) ([09 §1](09-frameworks-and-architecture.md)) |
| **게이트웨이** | 여러 백엔드 앞에서 인증·라우팅·로그를 맡는 층. 앱에는 `base_url` 하나로 보임 ([09 §3](09-frameworks-and-architecture.md)) |
| **in-process 바인딩** | HTTP 없이 라이브러리로 모델을 직접 로드하는 방식. 이 가이드 범위 밖 ([01 §2](01-integration-anatomy.md)) |
| **SSE (Server-Sent Events)** | 스트리밍 응답에 쓰이는 HTTP 기반 단방향 이벤트 전송 ([02 §3](02-openai-compatible-api.md)) |

## 2. 요청·응답

| 용어 | 뜻 |
| --- | --- |
| **messages** | 역할이 붙은 메시지 배열. 대화 전체를 매 요청에 보냄 ([02 §2](02-openai-compatible-api.md)) |
| **role (system / user / assistant / tool)** | 규칙 / 사용자 입력 / 모델의 이전 답 / 도구 실행 결과 ([02 §2](02-openai-compatible-api.md)) |
| **stateless** | runtime이 이전 요청을 기억하지 않음. 대화 상태는 내 프로그램의 책임 ([04 §4](04-parameters-and-context.md)) |
| **temperature / top_p** | 다음 토큰 선택의 무작위성 ([04 §1](04-parameters-and-context.md)) |
| **max_tokens** | 생성 토큰 상한. 도달하면 `finish_reason: length` ([04 §1](04-parameters-and-context.md)) |
| **finish_reason** | 생성이 끝난 이유 — `stop`(정상) / `length`(잘림) / `tool_calls`(도구 요청) ([02 §3](02-openai-compatible-api.md)) |
| **usage** | 입력·생성 토큰 수. context 예산과 비용의 근거 ([02 §3](02-openai-compatible-api.md)) |
| **stream / delta / chunk** | 토큰 단위 전송 / 조각의 증분 내용 / 조각 하나 ([03 §2](03-lab-chat-program.md)) |
| **stop** | 이 문자열이 나오면 생성을 멈추는 설정 ([04 §1](04-parameters-and-context.md)) |
| **seed** | 난수 시드. 재현성을 높이지만 보장하지 않음 ([04 §1](04-parameters-and-context.md)) |

## 3. context

| 용어 | 뜻 |
| --- | --- |
| **context 창(context window)** | 모델이 한 번에 읽을 수 있는 토큰 수. 프롬프트 + 답변 여지가 모두 들어가야 함 ([04 §2](04-parameters-and-context.md)) |
| **선언 상한 vs 적용 창** | 모델 구조상 최대 / runtime이 이번 실행에 적용한 값. `ollama show` vs `ollama ps` ([04 §2.1](04-parameters-and-context.md)) |
| **num_ctx** | Ollama의 적용 창 설정. 자체 API·환경변수·Modelfile로 지정 ([04 §2.3](04-parameters-and-context.md)) |
| **keep_alive** | 마지막 요청 후 모델을 메모리에 유지하는 시간 ([04 §3](04-parameters-and-context.md)) |
| **기록 자르기 / 요약 압축** | 대화 기록을 창 안에 맞추는 전략 ([04 §4](04-parameters-and-context.md)) |
| **prefix cache** | 같은 앞부분(시스템 프롬프트 등)의 계산을 runtime이 재사용하는 것 ([09 §2](09-frameworks-and-architecture.md)) |

## 4. 구조화 출력·도구

| 용어 | 뜻 |
| --- | --- |
| **구조화 출력(structured output)** | 출력을 JSON 스키마로 강제하는 것. `response_format: json_schema` ([05](05-structured-output.md)) |
| **grammar-constrained decoding** | 생성 단계에서 문법에 맞지 않는 토큰을 배제하는 기법. 구조화 출력의 원리 ([05 §1](05-structured-output.md)) |
| **JSON Schema / required / enum** | 출력 모양 정의 / 필수 필드 / 허용 값 목록 ([05 §3·§4](05-structured-output.md)) |
| **tool calling (function calling)** | 모델이 함수 이름+인자를 출력하면 내 코드가 실행하고 결과를 돌려주는 왕복 ([06 §1](06-tool-calling-workflow-agent.md)) |
| **tools / tool_calls / tool_call_id** | 도구 명세(메뉴) / 모델의 호출 요청 / 요청과 결과를 짝짓는 ID ([06 §1](06-tool-calling-workflow-agent.md)) |
| **workflow** | 호출 순서를 내 코드가 고정한 구성 ([06 §2](06-tool-calling-workflow-agent.md)) |
| **agent** | 다음 행동을 모델이 정하는 루프 ([06 §2](06-tool-calling-workflow-agent.md)) |
| **MCP (Model Context Protocol)** | 도구 서버와 모델 호스트 사이의 연결 표준 ([06 §4](06-tool-calling-workflow-agent.md)) |
| **human-in-the-loop** | 쓰기·전송 같은 행동을 사람이 승인한 뒤 실행하는 패턴 ([06 §3](06-tool-calling-workflow-agent.md)) |

## 5. 경계·신뢰성

| 용어 | 뜻 |
| --- | --- |
| **prompt injection** | 모델이 읽는 텍스트(문서·웹·도구 결과)에 심어진 지시를 모델이 따르는 문제 ([06 §3](06-tool-calling-workflow-agent.md), [08 ②](08-lab-prompt-injection.md)) |
| **권한 경계(네 겹)** | 도구 집합 · 도구 구현 · 루프 · 실행 환경. 프롬프트는 안내일 뿐 ([06 §3](06-tool-calling-workflow-agent.md)) |
| **호출 상한(max steps)** | agent 루프의 반복 횟수 제한 ([07 §3.4](07-lab-readonly-agent.md)) |
| **경로 경계** | 도구가 접근할 수 있는 디렉터리를 제한하는 검증 ([07 §2](07-lab-readonly-agent.md)) |
| **환각(hallucination)** | 도구 결과·근거에 없는 내용을 지어내는 것 ([08 ④](08-lab-prompt-injection.md)) |
| **골든셋** | 질문과 기대 결과를 짝지은 회귀 테스트 데이터 ([10 §4](10-reliability-and-operations.md)) |
| **모킹** | 모델 클라이언트를 가짜로 바꿔 내 코드의 분기를 테스트하는 것 ([10 §4](10-reliability-and-operations.md)) |
| **추적(tracing)** | 요청 단위로 메시지·응답·지연·도구 호출을 묶어 기록하는 것 ([10 §3](10-reliability-and-operations.md)) |
| **TTFT** | 첫 토큰까지의 시간. 모델 적재 여부의 지표 ([10 §3](10-reliability-and-operations.md)) |

## 6. 혼동하기 쉬운 쌍 ★

| 쌍 | 차이 |
| --- | --- |
| **모델 vs runtime** | 가중치 ↔ 그것을 띄우고 HTTP로 받는 프로그램. 같은 모델을 여러 runtime이 띄움 |
| **OpenAI 호환 vs OpenAI** | 형식 ↔ 회사의 서비스. 호환 runtime은 키 검증을 안 하거나 자체 키를 씀 |
| **messages vs 기록** | 요청에 담는 배열 ↔ 내 프로그램이 보관하는 리스트. 전자는 후자에서 매번 만든다 |
| **선언 상한 vs 적용 창** | 128k라고 써 있어도 이번 실행은 4,096일 수 있다 |
| **"JSON으로 답해" vs 구조화 출력** | 부탁 ↔ 강제. 전자는 가끔 깨진다 |
| **형식 보장 vs 내용 보장** | 구조화 출력은 전자만. 후자는 내 검증 코드 |
| **tool calling vs 실행** | 모델은 요청만, 실행은 내 코드. 모델은 주방에 못 들어간다 |
| **workflow vs agent** | 순서를 코드가 쥠 ↔ 모델이 쥠 |
| **프롬프트 vs 경계** | 안내 ↔ 코드. 프롬프트는 시도를 줄이고, 경계는 결과를 막는다 |
| **재시도할 오류 vs 안 할 오류** | 연결·타임아웃 ↔ 4xx·잘린 답·틀린 답 |
| **200 OK vs 맞는 답** | 호출 성공 ↔ 내용 정확. LLM 앱에서는 다르다 |

---

**← [README로 돌아가기](README.md)**
