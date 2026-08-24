# 내 연결 카드

응답이 왔다는 사실만이 아니라 **무엇을 호출했는지(Call), 출력을 어떻게 고정했는지(Shape), 무엇을 막았는지(Guard)**를 한 장에
남기는 기록 양식입니다. 모델·파라미터·도구를 바꿀 때마다 아래 template을 복사해 사용하세요.

← [가이드 README](README.md) · 다음 → [01 연결의 해부](01-integration-anatomy.md)

---

## 기록 원칙

- API key, 내부 주소, 개인 경로, 사용자 메시지 원문은 적지 않습니다.
- "잘 됨" 대신 runtime·모델 버전, 파라미터, 적용된 context 창, 관찰한 `finish_reason`·토큰 수를 적습니다.
- 구성을 바꿀 때는 **한 번에 하나만** 바꾸고 같은 질문 묶음으로 비교합니다.
- 공개 자료로만 확인한 내용과 직접 실행한 결과를 구분합니다.

## 복사해서 쓰는 template

```md
# 연결 카드 — <앱 이름>

## 목적

- 앱이 하는 일:
- 성공 기준:

## Call — 무엇을 호출하는가

- runtime과 버전 · `base_url`(호스트는 가려도 됨):
- 모델 태그와 ID:
- 적용된 context 창(`ollama ps` CONTEXT) · `keep_alive`:
- 파라미터: temperature · max_tokens · stop · seed:
- 시스템 프롬프트 요약(한 줄):
- 대화 기록 전략: (최근 N개 / 토큰 예산 / 요약):
- 스트리밍: 예 / 아니오

## Shape — 출력을 어떻게 고정하는가

- 구조화 출력: 없음 / json_schema(필수 필드 목록):
- 내용 검증: (필수 필드 · 범위 · 원문 대조 · confidence 문턱)
- tools: (이름 목록) · tool 지원 확인(`ollama show` Capabilities):

## Guard — 무엇을 막는가

- 도구 집합: 읽기 전용 / 쓰기 포함(사람 확인: 예·아니오)
- 도구 구현 검증: (경로 경계 · 인자 검증 · 길이 상한)
- 루프: max_steps · 시간 제한 · 반복 감지
- endpoint 노출: localhost / 프록시+인증
- 08 시나리오 ①~④ 재현 여부와 막은 겹:

## Prove — 무엇으로 확인했는가

- 골든셋 질문 수 · 통과/실패:
- 관찰한 `finish_reason`·토큰 수·TTFT:
- 확인일:

## 한계와 다음 조치

- 아직 확인하지 않은 것:
- 이번에 바꾼 한 가지와 그 결과:
- 다음에 바꿔 볼 한 가지:
```

## 가장 짧은 예시

아래는 03·07·08 실습 구성을 적은 예시입니다. Apple M4 Pro·24GB Mac, Ollama 0.32.7에서 관찰한 값입니다. `[실행 검증 · 2026-08-23]`

| 단계 | 기록 |
| --- | --- |
| Call | Ollama `/v1` · gemma3:4b(대화) / qwen3:4b(도구) · system 1줄 · 최근 20개 · stream · temperature 0.3/0 |
| Shape | json_schema 5필드(회의 추출) · tools 4개(calculate·list_docs·read_doc·search_docs) |
| Guard | 읽기 전용 · docs/ 경로 경계 · ast 계산기 · max_steps 6 · localhost |
| Prove | 03 판정 4/4 · 05 스키마 ○/부탁 ✗/환각 confidence 0.9 · 08: ② 호출 없음·형식 누출, ③ 가짜 도구 실행 텍스트, ①④ 정상 · prompt 52→81 토큰 |
| 경계 | 개인 PC의 실습 구성이며 동시 사용자·인증·쓰기 도구는 다루지 않음 |

---

**다음 →** [01 연결의 해부](01-integration-anatomy.md)
