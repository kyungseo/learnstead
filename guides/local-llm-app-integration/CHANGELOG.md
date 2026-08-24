# 변경 기록

**Local LLM을 내 프로그램에 연결하기**의 공개 변경을 기록합니다.

## 2026-08-24 — 초판

- HTTP 호출에서 시작해 대화 상태, context, 구조화 출력, tool calling, 읽기 전용 agent까지 Call → Shape → Guard 순서로 구성했습니다.
- Python 대화·추출·agent 실습과 재현용 문서 fixture를 제공하고, 계산 크기·경로·파일 형식·호출 횟수·응답 크기에 상한을 두었습니다.
- prompt injection, 가짜 도구 실행, 형식은 맞지만 내용은 틀리는 출력을 실제 관찰 로그와 판정 기준으로 설명했습니다.
- OpenAI 호환성을 기본 채팅 경로와 runtime별 가장자리 기능으로 구분하고, context 기본값·Responses API 등 공식 문서를 2026-08-24 기준으로 다시 확인했습니다.
- 개념 흐름과 파일 구조를 SVG로 통일하고, 재현 환경·실행 결과·미검증 경계를 [검증 기록](VALIDATION.md)에 분리했습니다.
