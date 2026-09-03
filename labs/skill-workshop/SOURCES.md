# SOURCES

최초 확인일은 2026-08-30이며, 실행 스크립트와 핵심 공식 문서는 2026-09-02에 다시 확인했다.

## 1차 자료

| 자료 | 무엇을 확인했나 |
| --- | --- |
| [Agent Skills 규격](https://agentskills.io/specification) | `SKILL.md` frontmatter 필드와 이름 규칙 — fixture skill 작성 기준 |
| [Claude Code 공식 문서 "Extend Claude with skills"](https://code.claude.com/docs/en/slash-commands) | `skillOverrides`, `--allowedTools`, `-p`·`--output-format stream-json`, 우선순위(개인 > 프로젝트), "skill을 끈 새 세션과 비교하라"는 평가 지침 |
| [Codex 공식 문서 "Build skills"](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills`·`$HOME/.agents/skills` 경로, `$name` 호출 |
| `claude --help`, `codex exec --help` | `-p`, `--output-format`, `--max-turns`, `-o/--output-last-message`, `--skip-git-repo-check` |
| 직접 실행 | 각 단계의 "작성 환경의 실제 결과" 전부 |

## 2차 자료

없음.
