# SOURCES

최초 확인일은 2026-08-30이며, 핵심 규격과 Claude Code·Codex 문서는 2026-09-02에 다시 확인했습니다.

## 1차 자료 — 규격·공식 문서

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| [Agent Skills 규격](https://agentskills.io/specification) | `SKILL.md` 구조, 필수 2필드와 선택 4필드(`allowed-tools`는 실험적), name·description·compatibility 제약, `skills-ref validate` | 01, 02, 06 |
| [Claude Code 공식 문서 "Extend Claude with skills"](https://code.claude.com/docs/en/slash-commands) (v2.1.258에서 재확인) | 경로와 우선순위, 하위 디렉터리 Skill의 동적 발견, command 통합, 확장 frontmatter, `$ARGUMENTS`, 동적 컨텍스트와 실패 규칙, `context: fork`, `allowed-tools` 수명, `skillOverrides`, 본문 수명과 압축 상한, 트러블슈팅 | 01, 02, 03, 04, 05, 07, 08 |
| [Claude Code 공식 문서 "Plugins"](https://code.claude.com/docs/en/plugins) | `.claude-plugin/plugin.json`, `--plugin-dir`, `/reload-plugins`, plugin 이름 공간 | 03, 08 |
| [Codex 공식 문서 "Build skills"](https://learn.chatgpt.com/docs/build-skills) | 공식 skill 경로, symlink, `$name`·`/skills`, 초기 목록 2%·8,000자 예산, `agents/openai.yaml`, `[[skills.config]]`, plugin 배포 | 00, 01, 03, 04, 05, 08 |
| [Gemini CLI 공식 문서 "Agent Skills"](https://geminicli.com/docs/cli/using-agent-skills/) (문서 갱신일 2026-04-30) | 경로와 우선순위, `activate_skill`과 동의 프롬프트, 삽입 내용, `/skills` 명령, `gemini skills install`, GEMINI.md와의 구분 | 03, 04, 05 |
| [Cursor 공식 문서 "Agent Skills"](https://prod.cursor.com/docs/skills) (Cursor 2.4 기준) | 경로(`.cursor/skills`, `.agents/skills`, 호환 경로), frontmatter(`paths`, `disable-model-invocation`, `icon`, `color`), 호출 방식, `/migrate-to-skills`, 사용자 레벨 skill의 원격 미복사 | 03, 04, 08 |
| [Cursor 공식 문서 "Rules"](https://docs.cursor.com/context/rules-for-ai) | `.mdc`의 적용 범위와 규칙 방식 | 03 |
| 직접 실행 — Claude Code 2.1.251 `claude -p`, Codex CLI 0.144.1 `codex exec` | 실습 [`labs/skill-workshop`](../../labs/skill-workshop/README.md)의 전 관측. [`VALIDATION.md`](VALIDATION.md) 참조 | 전체 |

## 2차 자료

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| Codex 시스템 skill `skill-creator`의 본문(설치본에서 열람) | "Codex는 이미 유능하다고 가정하고 결정을 바꾸는 정보만 담아라", 발견은 싸고 정확하게, 점진적 공개 | 02 |
| 개인 skill 저장소의 `agents/openai.yaml` 실물 | `interface.display_name`·`short_description`·`default_prompt` 형식 | 04 |

## 확인하지 못한 것

- Gemini CLI·Cursor의 실제 실행 결과. 문서만 확인했다.
- Codex에서 압축 시 읽어 둔 `SKILL.md` 내용의 세부 취급.
- 2026-08-30에 관측한 `~/.codex/skills` 탐색은 현재 공식 문서에 없는 호환 동작이다.
- Codex 이름 충돌 시 호출 대상은 1회 관측에 그친다.
- Gemini CLI custom command(`.toml`)와 skill의 관계는 문서에서 직접 비교하지 않아 이 가이드도 단정하지 않았다.
