# 02. 진입 지시문 — CLAUDE.md · AGENTS.md의 계층과 발견

> 이전 ← [`01-what-the-agent-reads.md`](01-what-the-agent-reads.md) · 다음 → [`03-always-vs-conditional.md`](03-always-vs-conditional.md)

## 이 장에서 답하는 질문

- 도구는 어느 파일을 어떤 순서로 읽어 하나의 지시문으로 만드는가
- 크기·형식의 한계는 무엇이고 어떻게 확인하는가
- 무엇을 여기에 적고 무엇을 다른 층으로 보내는가

이 장의 실행 기록은 **2026-08-30** Claude Code 2.1.251과 Codex CLI 0.144.1에서 관측했고, 문서 내용은 2026-09-02 Claude Code 2.1.258과 Codex CLI 0.144.1 기준으로 다시 확인했습니다.

## 1. 발견 규칙

| | Claude Code | Codex |
| --- | --- | --- |
| 조직 | managed `CLAUDE.md` (macOS `/Library/Application Support/ClaudeCode/`) 또는 managed settings의 `claudeMd` — 제외 불가 | — |
| 사용자 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.override.md` 있으면 그것, 없으면 `~/.codex/AGENTS.md` |
| 프로젝트 | `./CLAUDE.md` 또는 `./.claude/CLAUDE.md`, 개인용 `./CLAUDE.local.md`(gitignore) | 프로젝트 루트(git root)부터 cwd까지 각 디렉터리의 `AGENTS.override.md` → `AGENTS.md` → fallback 이름 |
| 상위 디렉터리 | cwd와 그 **위** 모든 디렉터리의 파일을 시작 시 로드 | 루트→cwd 경로상의 파일만 |
| 하위 디렉터리 | 시작 시 로드하지 않음. 그 디렉터리의 파일을 **읽을 때** 로드 | 로드하지 않음(cwd 경로 밖). 실습 확인은 3장 |
| 합치는 방식 | 전부 **연결**(override 아님). 루트 → cwd 순서, 같은 디렉터리에서는 `CLAUDE.local.md`가 뒤 | 루트 → cwd 순서로 연결. "가까운 파일이 뒤에 오므로 앞의 지침을 덮는다" |
| import | `@path/to/file` — 시작 시 함께 로드, **5단계까지** 재귀, 코드 span 안은 무시. 프로젝트 파일이 작업 디렉터리 밖을 import하면 승인 대화 | 없음 (`@`는 문자 그대로) |
| 크기 | 4 MiB 초과 파일은 건너뜀. **200줄 미만 권장** | 합계 **32 KiB** (`project_doc_max_bytes`) |
| 제외 | `claudeMdExcludes` glob (managed는 제외 불가) | — |
| 확인 | `/context`의 Memory files, `/memory`, `InstructionsLoaded` hook | — |
| 성격 | "system prompt 뒤에 **사용자 메시지로** 전달. 강제 아님" | "guidance only, 강제 아님" |

같은 내용을 두 도구에 주려면 `AGENTS.md`를 두고 `CLAUDE.md`에 `@AGENTS.md` 한 줄(또는 symlink)을 두는 것이 문서의 권장이다 [문서 확인]. Gemini CLI는 `GEMINI.md`, Cursor는 `AGENTS.md`(중첩 지원)를 읽는다 [문서 확인 · agent-skills 가이드에서 확인한 범위].

## 2. 로드는 됐는데 지켜지지 않는 이유

두 문서 모두 같은 원칙을 설명합니다. 지시문은 **컨텍스트이지 강제 수단은 아닙니다.** 실습에서도 같은 결과가 나왔습니다 [실행 검증 · 실습 02].

| 조건 (규칙 5개, 코드에서 추론 불가) | Claude Code | Codex |
| --- | --- | --- |
| 지시문 없음 | 0/15 | 0/15 |
| 짧은 지시문(10줄, 규칙 5개만) | 11/15 | **15/15** |

Claude Code가 짧은 지시문에서도 4/15를 놓친 항목은 두 가지였습니다. 테스트 함수에 한국어 docstring을 쓰지 않았고 반환 타입 힌트도 붙이지 않았습니다. 규칙은 "모든 함수"라고 썼지만 이 실험의 Claude Code는 구현 함수에만 적용했고, Codex는 테스트 함수까지 적용했습니다. **애매한 범위는 도구마다 다르게 해석될 수 있습니다.** "테스트 함수를 포함한 모든 함수"라고 썼다면 달랐을 가능성이 있습니다 [해석]. 강제가 필요한 규칙은 hook·lint·CI로 보냅니다(Claude Code 문서: "무조건 막으려면 PreToolUse hook").

## 3. 무엇을 적나

Claude Code 문서의 기준 [문서 확인]: "매 세션 다시 설명해야 할 것" — 빌드·테스트 명령, 관례, 프로젝트 배치, "항상 X" 규칙. 넣지 말 것: 여러 단계 절차(→ skill), 코드 일부에만 해당하는 것(→ 경로 조건 규칙), 코드에서 읽어 낼 수 있는 것(`/doctor`가 디렉터리 구조·의존성 목록·아키텍처 개요를 잘라 내라고 제안한다).

실습 라운드 1의 결과가 마지막 항목을 뒷받침합니다. 규칙이 기존 코드에 이미 드러나 있을 때 지시문 없이도 5/5였다 [실행 검증 · 실습 01]. 그러니 적어야 할 것은 **코드가 보여 주지 못하는 것이다**:

- 새 파일에만 적용될 관례(기존 코드가 아직 안 따르는 것)
- 왜 그렇게 하는지(rationale) — 코드에는 결과만 있습니다
- 하지 말 것 — 코드에 없는 것은 코드에서 배울 수 없습니다
- 명령과 경로 — 매번 찾으면 탐색 비용

## 4. 형식

- **200줄 미만**, 헤더·불릿으로 묶기, 검증 가능한 구체성("2칸 들여쓰기" > "깔끔하게"), 충돌 없애기 [문서 확인]. 충돌하면 "임의로 하나를 고른다".
- Claude Code는 블록 HTML 주석(`<!-- -->`)을 **제거하고** 넣습니다. 유지보수자 메모를 토큰 없이 남길 수 있다 [문서 확인]. Codex 문서에는 이 언급이 없습니다.
- Codex는 32 KiB 합계 제한이 있어 긴 파일은 잘립니다. 실습의 긴 변형(176줄, 12.5 KB)은 한도 안이었습니다.

## 5. 라우팅 한 줄

지시문이 길어지는 첫 원인은 절차입니다. 절차는 skill로 빼고 지시문에는 **가리키는 한 줄만** 둡니다. [agent-skills 06장](../agent-skills/06-canonical-and-adapters.md)과 [mcp-basics 06장](../mcp-basics/06-skills-and-mcp.md)의 "진입 지시문은 라우팅만"이 그 원칙입니다. 단, 가리키기만 하면 읽지 않는 경우도 있습니다. 3장의 pointer 실험에서 확인합니다.

## 이 장을 끝내면

- 두 도구의 지시문 발견 순서와 합치는 방식, 크기 한계를 말할 수 있습니다.
- "로드됐는데 안 지킨다"를 강제 부재와 규칙의 모호함으로 나눠 봅니다.
- 코드가 보여 주지 못하는 것만 적을 수 있습니다.
