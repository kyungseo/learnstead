# CONTEXT-CARD — 한 장 요약

## 한 문장

**모델이 보는 토큰 집합을 설계한다** — 항상 넣을 것, 조건부로 넣을 것, 세션을 넘겨 남길 것, 넣지 않을 것.

## 네 가지 출처

| 층 | 언제 | 파일 (Claude Code / Codex) | 압축 후 |
| --- | --- | --- | --- |
| 진입 지시문 | 항상 | `CLAUDE.md`(+`@import`, `.claude/rules` 무조건) / `AGENTS.md`(루트→cwd 연결, 32 KiB) | 재주입 |
| 조건부 | 파일 읽을 때·cwd·호출 | `.claude/rules` `paths` · 하위 `CLAUDE.md` · skill / 하위 `AGENTS.md`(cwd만) · skill | 재읽기 시 |
| memory | 색인 먼저, 본문 필요 시 | Claude Code auto memory / Codex opt-in local memory | 제품별로 확인 |
| 동적 | 작업 중 | Read·Grep·MCP·RAG·서브에이전트 요약 | Claude Code는 일부 재주입, 제품별로 다름 |

## 실측 (규칙 5개 × 3회, 15점)

| | Claude Code | Codex |
| --- | --- | --- |
| 지시문 없음 | 0 | 0 |
| 짧게(10줄) | 11 | 15 |
| 길게(176줄, 흩어 놓음) | 11 | 10 |
| pointer만 | 9 | 14 |
| `@import` | 13 | 14 |
| 경로 규칙 / 중첩 AGENTS.md | 13 | 6 |

- 기존 코드가 규칙을 따르면 지시문 없이도 15 → **코드에서 추론 가능한 것은 적지 않는다**
- 짧은 지시문의 첫 효과는 준수율이 아니라 **탐색 턴 감소**(8턴 → 4턴)
- 이 실험의 Claude는 "모든 함수"를 구현 함수로 좁게 읽고, Codex는 테스트 함수까지 적용함 → **모호함이 길이보다 먼저**

> 2026-08-30~31, 과제 1개·도구별 3회 실행의 관측이다. 모델·과제·규칙이 바뀌면 결과도 달라질 수 있다.
- pointer < import · Codex 중첩 AGENTS.md는 cwd 조건 → **조건부는 도구 기제로**

## 넣지 말 것

코드로 읽을 수 있는 것 · 절차(→ skill) · 경로별 규칙(→ 조건부) · 충돌 · 애매한 문장 · 강제할 것(→ hook) · Secret·절대 경로 · 대화로만 준 규칙 · 팀 규칙을 memory에 · 참고 전문 · "X를 봐"만

## 꼭 넣을 것

하지 말 것 · 왜 · 명령 · 아직 코드가 안 따르는 새 관례

## Claude Code의 압축 손잡이

`/context` 확인 · `/compact <초점>` · `/autocompact` · `/clear` 작업 전환 · 큰 읽기는 서브에이전트 · 살아남을 지시는 파일로
