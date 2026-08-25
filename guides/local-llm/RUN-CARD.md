# 내 Local LLM 실행 카드

model을 실행했다는 사실만이 아니라 **장비에 맞았는지(Fit), 어떻게 실행했는지(Run), 무엇으로 확인했는지(Prove)를**
한 장에 남기는 기록 양식입니다. 새 model이나 runtime을 시험할 때 아래 template을 복사해 사용하세요.

← [가이드 README](README.md) · 다음 → [01 오리엔테이션](01-orientation.md)

---

## 기록 원칙

- 비밀번호, API key, 내부 주소, 개인 경로와 장치 식별자는 적지 않습니다.
- “잘 됨” 대신 version, 명령, 관찰한 값과 성공 기준을 적습니다.
- 공개 자료로만 확인한 내용과 직접 실행한 결과를 구분합니다.
- 성능을 비교할 때는 model, quantization, context와 prompt 조건을 함께 고정합니다.

## 복사해서 쓰는 template

```md
# Local LLM 실행 카드 — <구성 이름>

## 목적

- 하려는 일:
- 성공 기준:

## Fit — 장비에 들어가는가

- hardware:
- 사용 가능한 memory / VRAM:
- model과 정확한 tag 또는 revision:
- quantization과 model file 크기:
- 목표 context length:
- 예상 memory와 남겨 둘 여유:
- 라이선스 확인 경로:

## Run — 어떻게 실행했는가

- OS:
- runtime과 version:
- 설치 방법:
- 서버 실행 명령:
- model 실행 명령:
- 사용한 prompt:

## Prove — 무엇으로 확인했는가

- 응답 완료: 통과 / 실패
- GPU 적재 확인 명령과 결과:
- 실제 context 확인 명령과 결과:
- API 확인 명령과 결과:
- TTFT / TPS 또는 전체 소요 시간(선택):
- 확인일:

## 한계와 다음 조치

- 아직 확인하지 않은 것:
- 재현 시 주의할 점:
- 다음에 바꿔 볼 한 가지:
```

## 가장 짧은 예시

아래 값은 이 가이드의 Apple Silicon 검증 환경에서 관찰한 결과입니다. 다른 Mac에서 같은 값을 보장하지 않습니다.

| 단계 | 기록 |
| --- | --- |
| Fit | Apple M4 Pro, 통합 memory 24GB / `gemma3:4b` Q4_K_M, model file 3.3GB |
| Run | Ollama 0.32.7 / `ollama serve` → `ollama run gemma3:4b` |
| Prove | 한국어 응답 완료 / `ollama ps`에서 3.7GB, `100% GPU`, context 4,096 / API JSON 응답 |
| 경계 | 짧은 prompt 한 건의 확인이며 장기 부하·긴 context·다른 장비는 검증하지 않음 |

세부 근거와 명령은 [검증 기록](VALIDATION.md), 성능을 비교하는 방법은 [10 운영과 문제 해결](10-operations.md)을
참고하세요.

---

**다음 →** [01 오리엔테이션 — 로컬 실행의 전체 지도](01-orientation.md)
