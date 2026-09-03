# SKILL-CARD — 한 장 요약

> 가이드 전체의 압축판. 세부는 각 장으로.

## skill 한 문장

**필요할 때만 로드되는 절차 파일.** 폴더 이름 = `name`, `SKILL.md` 필수, 평소엔 description 한 줄만 컨텍스트에 있다.

## 만들기 — 최소

```yaml
---
name: meeting-actions            # 폴더 이름과 같게. 소문자·숫자·하이픈
description: [무엇을 한다]. [언제 쓴다]. [언제 안 쓴다].
---
# 목적 한 문단 (무엇을 하고 무엇을 안 하는지)
## 절차 (번호)
## 출력 형식 (실제 뼈대)
## 예 (입력 → 출력 한 쌍)
```

## 어디에 두나 (공식 문서 재확인 2026-09-02)

| | 프로젝트 | 개인 |
| --- | --- | --- |
| Claude Code | `.claude/skills/` (symlink 가능) | `~/.claude/skills/` |
| Codex | cwd부터 저장소 루트까지 `.agents/skills/` | `$HOME/.agents/skills/` |
| Gemini CLI | `.gemini/skills/` = `.agents/skills/` | `~/.gemini/skills/` = `~/.agents/skills/` |
| Cursor | `.cursor/skills/`, `.agents/skills/` | `~/.cursor/skills/`, `~/.agents/skills/` |

여러 도구용 → `.agents/skills/`에 두고 `.claude/skills/<name>` symlink. 도구 전용 기능이 생기면 canonical + adapter.

## 부르기

| | 사람 | 모델 |
| --- | --- | --- |
| Claude Code | `/name 인자` | `Skill` tool (description 보고 선택) |
| Codex | `$name 인자` | 자동 (`allow_implicit_invocation`으로 제어) |
| Gemini CLI | — | `activate_skill` + 동의 프롬프트 |

## 이름이 겹치면

Claude Code: **개인 > 프로젝트** · Codex: 둘 다 표시, 호출은 **저장소** (각 1회 관측 · 2026-08-30) · Gemini: 워크스페이스 > 사용자

## 네 칸

| 절차 | 강제 | 능력 | 상시 배경 |
| --- | --- | --- | --- |
| skill | hook | MCP | `CLAUDE.md` / `AGENTS.md` |

command = 사람만 부르는 skill · rule = 경로 조건 붙은 skill/지시문 · plugin = 묶음

## 실패 세 층

1. **발견** — 목록에 있나? description에 요청 단어가 있나? 상위 사본이 가리나?
2. **로드** — frontmatter 파싱? 동적 명령 실패? 압축 상한?
3. **준수** — 형식을 예로 줬나? 경계 사례를 규칙에 적었나? 부정 규칙이 있나?

## 실습에서 본 숫자

- 절차를 프롬프트에 붙임 0/3 통과 · skill로 둠 3/3 통과 (같은 본문, Claude Code)
- 넓은 description → 요약 요청에 3/3 과호출
- 규칙 한 줄 추가(v1.1) → Claude Code·Codex 모두 통과

## 공개 전

홈 절대 경로 · 내부 ID · Secret · 넓은 `allowed-tools` · 동적 명령 · 도구 전용 필드 · `license`
