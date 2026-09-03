# SOURCES

실행은 2026-08-30~31, 문서 재확인은 2026-09-02에 수행했다.

## 1차 자료 — 공식 문서·직접 실행

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| [Claude Code 공식 문서 "How Claude remembers your project"](https://code.claude.com/docs/en/memory) (2.1.258에서 재확인) | `CLAUDE.md` 계층(managed·user·project·local)·상위 로드·하위 on-demand·연결 순서·`@import`(5단계·코드 span 제외·외부 import 승인)·200줄 권고·4 MiB 상한·HTML 주석 제거·`claudeMdExcludes`·`.claude/rules`와 `paths`·사용자 규칙·symlink·auto memory(종류·경로·200줄/25 KB·주제 파일·`/memory`·끄기)·"컨텍스트이지 강제 아님"·`/context`·`InstructionsLoaded` hook·`/doctor` 트림 | 01, 02, 03, 04, 05, 07 |
| [Claude Code 공식 문서 "Explore the context window"](https://code.claude.com/docs/en/context-window) (2.1.251) | 시작 컨텍스트의 대표 범위·작업 중 항목 비용·서브에이전트 격리·압축 후 생존표·`/compact`·`/clear`·skill 재주입 상한 | 01, 05 |
| [Claude Code 공식 Hooks reference](https://code.claude.com/docs/en/hooks#instructionsloaded) | `InstructionsLoaded`의 발생 시점과 관측 전용 성격 | 02, 03 |
| [Codex 공식 문서 "AGENTS.md"](https://learn.chatgpt.com/docs/agent-configuration/agents-md) (0.144.1) | `~/.codex/AGENTS.override.md`→`AGENTS.md`, 루트→cwd 연결, "가까운 파일이 덮음", `project_doc_max_bytes` 32 KiB, fallback 이름, "guidance only" | 02, 03 |
| [Codex 공식 문서 "Local memories"](https://learn.chatgpt.com/docs/customization/memories) (0.144.1에서 확인) | opt-in 기본값, `~/.codex/memories`, `/memories`, 색인과 주제별 기록 | 01, 04 |
| 직접 실행 — `claude -p`, `codex exec -s workspace-write`, `check.py` | 실습 [`labs/instruction-budget`](../../labs/instruction-budget/README.md) 라운드 1·2 전 결과 | 01, 02, 03, 05, 06 |
| 작성 장비의 `~/.claude/projects/<repo>/memory/` | auto memory 디렉터리·`MEMORY.md` 존재 확인 | 04 |

## 2차 자료

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| [Anthropic Engineering, "Effective context engineering for AI agents"](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29) | 컨텍스트 엔지니어링 정의, 주의 예산·context rot, system prompt의 "적절한 고도", just-in-time retrieval, compaction·structured note-taking·서브에이전트, "가장 작은 고신호 토큰 집합" | 01, 04, 05 |
| [Gemini CLI 문서](https://geminicli.com/docs/)·[Cursor Rules 문서](https://docs.cursor.com/context/rules-for-ai) (agent-skills 가이드 작성 시 확인) | `GEMINI.md`·Cursor `AGENTS.md` 지원 | 02 |

## 확인하지 못한 것

- Codex의 compaction 세부 동작과 local memory 실실행.
- 200줄을 넘는 지시문에서의 희석 정도(V2는 176줄).
- Claude Code에서 규칙 문장을 "테스트 함수 포함"으로 고쳤을 때의 점수(해석으로만 남김).
- Gemini CLI·Cursor 실측.
