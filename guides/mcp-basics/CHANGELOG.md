# 변경 기록

**AI Agent에 내 도구를 연결하는 법 — MCP 기초** 가이드의 독자 대상 내용과 검증 범위를 기록합니다.

## 2026-09-03 — 초판

- MCP가 필요한 이유부터 host·client·server, tools·resources·prompts, stdio·Streamable HTTP를 순서대로 설명합니다.
- 모델은 도구 호출을 제안하고 실제 실행과 권한 확인은 모델 밖에서 이뤄진다는 경계를 분명히 했습니다.
- Claude Code와 Codex의 연결·확인·제거 절차를 직접 실행한 기록과 Gemini CLI·Cursor의 문서 확인 범위를 구분했습니다.
- 서버 코드·annotation·host 승인으로 이어지는 권한 경계와 경로 탈출·주입 지시문·stdout 오염 같은 실패를 다룹니다.
- 읽기 전용 노트 MCP 서버 실습과 Agent Skills·Context Engineering 가이드로 이어지는 경로를 연결했습니다.
