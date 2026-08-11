# 09 — 내 장비에 맞는 모델 고르기

model 목록은 빠르게 낡습니다. 이 장은 순위표 대신 **후보를 안전하게 줄이는 방법**을 설명하고, 마지막에
2026-08-10 기준의 작은 snapshot만 둡니다.

← [08 멀티 GPU·서버](08-setup-multi-gpu-server.md) · 다음 → [10 운영](10-operations.md)

> **검증 상태:** model 이름·tag·license·runtime 지원은 모두 변할 수 있습니다. 내려받기 전에 model card와
> runtime library를 다시 확인하고, 확인한 URL과 날짜를 기록하세요. 이 장의 근거는 [출처](SOURCES.md),
> 실행 범위는 [검증 기록](VALIDATION.md)에 정리합니다.

---

## 1. 먼저 답할 다섯 가지

model 이름을 검색하기 전에 아래를 적으면 후보가 빠르게 줄어듭니다.

1. **용도:** 대화, 요약, coding, vision 중 무엇이 필요한가?
2. **언어:** 실제 한국어 prompt에서 충분한가?
3. **memory:** model weight, KV cache, runtime 여유를 합쳐 장비에 들어가는가?
4. **runtime:** Ollama·llama.cpp·MLX·vLLM 중 내가 쓸 경로가 지원하는가?
5. **license:** 개인 실험이 아닌 배포·상업 이용 조건을 충족하는가?

benchmark 순위는 그다음입니다. 높은 평균 점수가 내 한국어 document·codebase·output format에서 좋은 결과를
보장하지 않습니다. `[원리]`

---

## 2. 장비에서 시작하는 후보 축소

정확한 memory는 [02의 산식](02-model-anatomy.md)으로 계산합니다. 아래 범위는 **첫 검색 범위**일 뿐,
장비별 보증이나 구매 권고가 아닙니다.

| 사용 가능한 memory | 첫 후보 | 다음 확인 |
| --- | --- | --- |
| 8~16 GB | 3B~8B급 4bit | 실제 file size, context 4K에서 memory pressure |
| 16~24 GB | 8B~14B급부터 시작 | 20B급 이상은 weight·KV를 직접 계산 |
| 24~48 GB | 14B~32B급 후보 | 긴 context와 다른 application 몫 포함 |
| 64 GB 이상 | 32B~70B급도 계산 가능 | runtime overhead와 목표 context·동시성 |
| 다중 GPU | 단일 GPU에 안 들어가는 model | TP/PP와 카드 간 통신 비용([08](08-setup-multi-gpu-server.md)) |

**MoE 주의:** `총 35B / 활성 3B`처럼 표시돼도 weight memory는 총 parameter를 기준으로 잡습니다. 활성
parameter만 보고 작은 장비에 들어간다고 판단하지 않습니다([02 §3](02-model-anatomy.md)).

---

## 3. 이름보다 model card를 읽는 법

model page에서 최소한 아래 필드를 확인합니다.

| 확인 항목 | 왜 필요한가 |
| --- | --- |
| 정확한 repository와 revision | 비슷한 이름의 base·instruct·파생 model 혼동 방지 |
| architecture와 총/활성 parameter | weight memory와 runtime 지원 판단 |
| context length | architecture 상한 확인. 실제 상한은 장비 memory로 다시 계산 |
| chat template | 대화 format 불일치 방지 |
| dtype·quantization | file size와 지원 kernel 판단 |
| license 전문 | 사용·배포·파생물 조건 판단 |
| model 작성자가 밝힌 limitation | 지원 언어, task, safety 경계 확인 |

`Base` model은 다음 token 예측용 원형이고, `Instruct`·`Chat` model은 대화 지시를 따르도록 조정된 판입니다.
처음 대화형 local LLM을 구성한다면 보통 Instruct/Chat 변형이 출발점입니다. `[원리]`

---

## 4. 양자화판은 별도 제품처럼 확인한다

같은 원본 model의 `Q4`, `AWQ`, `GPTQ`, `MLX` 변환본이라도 다음이 다를 수 있습니다.

- 변환 도구와 version
- calibration data와 방식
- chat template·tokenizer 포함 여부
- 원본 revision
- runtime compatibility

그래서 “4bit니까 같다”가 아니라 **원본 model + 변환본 + runtime** 세 항목을 함께 기록합니다. 출처가 불명확한
재배포본보다 개발사 또는 provenance를 명시한 배포본을 우선하고, file hash나 digest를 남깁니다.

---

## 5. license는 기술 선택보다 먼저 거른다

`open-weight`는 weight를 받을 수 있다는 뜻이지, 모든 용도의 자유 사용을 뜻하지 않습니다. model repository의
license 식별자만 보지 말고 연결된 전문을 읽습니다.

조직에서 확인할 항목은 다음과 같습니다.

- 상업 이용과 서비스 제공 허용 여부
- 사용자·매출·용도에 따른 추가 조건
- 파생 model과 fine-tuning 결과물의 의무
- 출력물 사용 및 다른 model 학습 관련 제한
- 고지·표시·재배포 의무

이 가이드는 법률 자문이 아닙니다. 실제 제품·고객 업무에 투입할 때는 조직의 법무·compliance 절차로
확인합니다. `[원리]`

---

## 6. 작은 snapshot — 확인 경로를 보여 주는 예

아래는 장기 추천 순위가 아니라 2026-08-10에 **공식 page에서 다시 확인할 후보의 예**입니다. 정확한 tag,
file size와 license는 링크된 page를 내려받는 날 다시 확인합니다. `[변동]`

| 후보 | 이 가이드에서의 용도 | 확인할 1차 page |
| --- | --- | --- |
| `gemma3:4b` | Ollama 첫 성공 경로. 작은 download로 설치·대화·GPU load 확인 | Ollama Gemma 3 library |
| `Qwen/Qwen3.6-27B` | 24GB 이상 장비에서 계산해 볼 중형 후보 | Hugging Face model card |
| `openai/gpt-oss-20b` | MoE·MXFP4 계열을 검토할 때의 후보 | OpenAI 안내와 model card |
| Gemma 4 계열 | 현재 Gemma의 크기·multimodal 선택지를 검토할 때 | Google Gemma documentation |

직접 URL과 확인 결과는 [SOURCES.md](SOURCES.md)의 Source ledger(출처 확인 기록)에 있습니다. snapshot에 새
model을 추가할 때는 “좋다”는 평가보다 **정확한 식별자·공식 page·확인일·실행 가능 범위**를 먼저 적습니다.

---

## 7. 내 작업으로 비교하는 최소 평가

후보를 2~3개로 좁힌 뒤 같은 조건으로 비교합니다.

1. 실제 작업에서 개인정보를 제거한 한국어 prompt 5~10개를 준비합니다.
2. system prompt, temperature, context와 output 길이를 맞춥니다.
3. 정답성·형식 준수·누락·환각을 사람이 같은 rubric으로 평가합니다.
4. TTFT, TPS, peak memory와 실패 여부를 함께 기록합니다([10 §1](10-operations.md)).
5. model repository, revision·digest, quantization, runtime version을 남깁니다.

점수 하나로 합치기보다 **quality gate를 통과한 후보 중 속도와 memory가 맞는 것**을 고르는 편이 해석하기
쉽습니다. prompt에 민감정보·저작권 자료를 넣지 말고, 조직 자료라면 승인된 evaluation 환경을 사용합니다.

---

## 8. 개정 시점

- 첫 성공 경로의 model tag가 사라지거나 필요한 Ollama version이 바뀌었을 때
- snapshot model의 공식 card·license·repository가 바뀌었을 때
- runtime이 새 quantization 또는 architecture를 지원했을 때
- 마지막 확인일부터 3개월이 지났을 때

개정할 때는 본문 날짜, [SOURCES.md](SOURCES.md), [VALIDATION.md](VALIDATION.md), item
[CHANGELOG.md](CHANGELOG.md)를 함께 갱신합니다.

---

**다음 →** [10 운영](10-operations.md)
