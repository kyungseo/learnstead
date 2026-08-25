# 03 — 실습: 작은 Python 대화 프로그램 만들기

README의 첫 호출 코드에 **대화 기록·스트리밍·시스템 프롬프트·오류 처리**를 추가해 터미널 대화 프로그램을 만듭니다.
60줄 남짓의 코드이며, 이후 실습도 같은 기본 구조를 사용합니다.

← [02 OpenAI 호환 API](02-openai-compatible-api.md) · 다음 → [04 파라미터·context·대화 상태](04-parameters-and-context.md)

> **왜 읽나:** 모델은 사용자의 이름을 스스로 기억하지 않습니다. 기억하는 것처럼 보이는 이유는 내 프로그램이 매번 대화 전체를 다시 보내기 때문이며, 실습에서 토큰 수로 확인합니다.
>
> **읽고 나면:** 기록·스트리밍·잘린 답·오류 처리를 포함한 60줄짜리 대화 프로그램을 직접 실행하고, 이후 실습의 공통 구조를 이해할 수 있습니다.

> **검증 상태:** 네 가지 성공 판정(기록·스트리밍·잘린 답·오류)을 Apple M4 Pro·24GB Mac, Ollama 0.32.7, `gemma3:4b`에서 실제로 확인했습니다. `[실행 검증 · 2026-08-23]`
> 아래 출력은 그때의 실제 값입니다. 상세는 [검증 기록](VALIDATION.md).

---

## 0. 학습 목표와 완료 조건

| 목표 | 완료 조건 |
| --- | --- |
| 대화 상태가 내 프로그램에 있음을 본다 | `/history`로 기록을 보고, `/reset` 후 모델이 이전 대화를 "잊는" 것을 확인했다 |
| 스트리밍을 다룬다 | 첫 글자가 전체 답보다 먼저 화면에 나타나는 것을 봤다 |
| 잘린 답을 감지한다 | `finish=length`를 한 번 일부러 만들어 봤다 |
| 오류를 프로그램이 처리한다 | Ollama를 끈 상태에서 실행해 오류 메시지가 프로그램을 죽이지 않는 것을 봤다 |

## 1. 준비

- Ollama 실행 중, `ollama pull gemma3:4b`, `pip install openai` `[문서 확인 · 2026-08-23]`
- 이 가이드의 `labs/chat.py`를 복사합니다.

## 2. 코드 읽기 — 세 군데

`labs/chat.py`에서 번호 주석 (1)(2)(3)을 찾습니다.

| 번호 | 무엇 | 왜 중요한가 |
| --- | --- | --- |
| (1) `messages = [system] + history[-N:]` | 매 요청에 시스템 규칙 + 최근 기록 전체를 보냄 | runtime은 이전 요청을 기억하지 않음. **이 리스트가 대화 상태의 전부** |
| (2) `stream=True` 루프 | 조각(`delta.content`)을 받는 대로 출력하고 이어 붙임 | 사용자 체감 지연을 줄임. 전체 텍스트는 내가 모아야 함 |
| (3) `history.append(assistant)` | 모델의 답을 기록에 추가 | 빠뜨리면 다음 턴에 모델이 자기 말을 모름 |

그 밖에도 `max_tokens`와 `finish_reason`을 확인하고, 예외가 나면 실패한 `user` 메시지를 기록에서 제거합니다(`history.pop()`).
이는 [10 신뢰성과 운영](10-reliability-and-operations.md)에서 설명하는 오류 처리 원칙입니다.

## 3. 실행

```bash
cd labs
python3 chat.py
```

```text
모델 gemma3:4b · /reset /history /quit

나> 내 이름은 박지호야. 기억해 줘.
AI> 네, 박지호님이라고 기억하겠습니다.
   (finish=stop · prompt 52 / completion 11 토큰)

나> 내 이름이 뭐라고 했지?
AI> 박지호입니다.
   (finish=stop · prompt 81 / completion 6 토큰)

나> /reset
(기록을 비웠습니다)

나> 내 이름이 뭐라고 했지?
AI> 모르겠습니다.
   (finish=stop · prompt 46 / completion 5 토큰)
```

**★ 성공 판정 1 — 기록:** 두 번째 질문에서 이름을 맞히고, `prompt` 토큰 수가 첫 턴보다 **커져** 있습니다(52 → 81 — 기록이
함께 갔다는 증거). `/reset` 후 같은 질문에는 "모르겠습니다"(46 토큰 — 기록이 없으니 다시 작아집니다). 모델이 기억한 것이
아니라 **내 리스트가** 기억한 것입니다. `[실행 검증 · 2026-08-23]`

**★ 성공 판정 2 — 스트리밍:** 긴 답을 요청(예: "로컬 LLM의 장단점을 5가지씩")했을 때 글자가 흘러나오듯 출력됩니다.
`--no-stream`으로 다시 실행하면 한참 기다린 뒤 한 번에 나옵니다.

**★ 성공 판정 3 — 잘린 답:** `python3 chat.py --max-tokens 30`으로 실행하고 긴 답을 요청하면 `finish=length · prompt 55 /
completion 30 토큰 ← max_tokens 에 걸려 잘렸다`가 표시됩니다. 앱에서는 이 신호를 보고 "이어서 답해 줘"를 보내거나 예산을
늘립니다. `[실행 검증 · 2026-08-23]`

**★ 성공 판정 4 — 오류:** Ollama를 종료(또는 `--base-url http://localhost:9/v1`)하고 질문하면 `[오류] APIConnectionError:
Connection error.`가 출력되고 프로그램은 다음 입력을 기다립니다. `[실행 검증 · 2026-08-23]`

### 실패했을 때

| 증상 | 확인 |
| --- | --- |
| `APIConnectionError` | Ollama 실행 여부, 포트, `--base-url` |
| `NotFoundError … model` | `ollama list`에 모델이 있는가, 태그 철자 |
| 답이 영어로 나옴 | `SYSTEM`에 "한국어로 답한다"가 있는지. 모델에 따라 규칙 준수가 약함 |
| 두 번째 턴부터 답이 이상함 | (3)이 빠졌는지. 또는 기록이 context 창을 넘었는지 — [04 §2](04-parameters-and-context.md) |

## 4. 바꿔 보기

- `SYSTEM`을 "너는 해적처럼 말한다"로 바꿔 시스템 프롬프트가 답에 미치는 영향을 확인합니다.
- `--max-history 2`로 실행하고 세 턴 전 정보를 물어봅니다 — 기록 자르기가 무엇을 잃게 하는지 봅니다.
- `--model qwen3:4b`로 바꿔 봅니다. 코드는 한 줄도 바뀌지 않습니다.

> 🔧 **한 단계 더 — 외부 API로 전환**
>
> `--base-url`을 외부 OpenAI 호환 API 주소로, `api_key`를 실제 키로 바꾸면 기본 대화 호출은 같은 구조로 전환할 수 있습니다.
> 구조화 출력과 tool calling 같은 세부 기능은 새 백엔드에서도 같은지 별도로 확인해야 합니다([09 §3](09-frameworks-and-architecture.md)).
> 키는 코드가 아니라 환경변수에 둡니다.

## 5. 이 코드가 아직 못 하는 것

- 기록이 길어지면 context 창을 넘습니다 — 자르기·요약 전략은 [04 §4](04-parameters-and-context.md)
- 답을 프로그램이 **읽지** 못합니다(문자열일 뿐) — [05 구조화 출력](05-structured-output.md)
- 모델이 무언가를 **하지** 못합니다(계산·검색) — [06 tool calling](06-tool-calling-workflow-agent.md)

## 6. 기록하기

[APP-CARD](APP-CARD.md)의 Call 칸에 이 시점의 구성을 적어 둡니다.

```text
Call: Ollama /v1 · gemma3:4b · system 1줄 · 최근 20개 기록 · stream · max_tokens 512 · temperature 0.3
```

---

**다음 →** [04 파라미터·context·대화 상태 — 무엇이 무엇을 바꾸는가](04-parameters-and-context.md)
