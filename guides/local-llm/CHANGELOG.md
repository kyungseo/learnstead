# 변경 기록

**내 장비에서 LLM 직접 실행하기**의 독자 대상 내용과 검증 범위 변화를 기록합니다.

## 2026-08-25 — Markdown 강조 수정

- 한국어 조사·어미가 강조 구문 바로 뒤에 붙어 GitHub에서 별표가 노출되던 16곳을 수정했습니다.
- 문장의 의미와 기술적 주장, 명령, 실행 검증 범위는 변경하지 않았습니다.
- 전체 Markdown 문서를 GFM 호환 parser로 다시 렌더해 코드 밖에 literal `**`가 남지 않았음을 확인했습니다.

## 2026-08-11 — 초판

- Local·Hosted와 Open-weight를 서로 다른 분류 축으로 설명하고, 조직의 hybrid 구성까지 소개했습니다.
- Apple Silicon, NVIDIA 단일 GPU와 멀티 GPU 서버의 선택·설정 경로를 정리했습니다.
- model·quantization·context와 memory의 관계를 계산하고 장비·runtime을 선택하는 기준을 담았습니다.
- Apple Silicon에서 Ollama 0.32.7과 `gemma3:4b`의 설치·한국어 생성·GPU 적재·OpenAI 호환 API를 실행 검증했습니다.
- 실행하지 않은 경로는 문서 확인 또는 미검증으로 구분하고, 독자가 확인할 성공 조건을 함께 적었습니다.
- Fit → Run → Prove 흐름과 재사용 가능한 Local LLM 실행 카드를 추가했습니다.
- 초급자를 위한 가장 짧은 실행 경로, 종료·정리 방법, 용어집과 기본 운영 수칙을 제공했습니다.
