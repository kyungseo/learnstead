# 04. 도구별 차이 — Claude Code · Codex · Gemini CLI · Cursor

> 이전 ← [`03-same-thing-different-names.md`](03-same-thing-different-names.md) · 다음 → [`05-discovery-and-invocation.md`](05-discovery-and-invocation.md)

## 이 장에서 답하는 질문

- 같은 `SKILL.md`를 네 도구는 각각 어디서 읽고 어떻게 부르는가
- 같은 이름이 두 곳에 있으면 누가 이기는가
- 어느 도구가 어떤 확장 필드를 읽는가

이 장은 2026-08-30 실행 기록을 2026-09-02 공식 문서와 대조해 갱신했습니다. Claude Code 2.1.251과 Codex CLI 0.144.1은 직접
실행했고 [실행 검증], 현재 설치본은 Claude Code 2.1.258과 Codex CLI 0.144.1입니다. Gemini CLI와 Cursor는 공식 문서만
확인했습니다 [문서 확인]. 경로와 우선순위는 버전에 따라 달라질 수 있으므로 사용 전에 4절의 방법으로 확인하세요.

## 1. 어디서 읽는가

| 도구 | 개인 | 프로젝트 | 그 외 |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/`; 하위 경로는 해당 파일을 읽을 때 발견 | plugin skills, managed |
| Codex | `$HOME/.agents/skills/` | cwd부터 저장소 루트까지 각 `.agents/skills/` | plugin, `/etc/codex/skills`, bundled system skills |
| Gemini CLI | `~/.gemini/skills/`, `~/.agents/skills/` | `.gemini/skills/`, `.agents/skills/` | extension, built-in |
| Cursor | `~/.cursor/skills/`, `~/.agents/skills/` | `.cursor/skills/`, `.agents/skills/` | 호환 경로 |

실측으로 갈린 지점 [실행 검증 · 실습 03]:

- Codex는 `.agents/skills`(저장소)·`~/.agents/skills`·`~/.codex/skills`를 읽었고, **`.claude/skills`는 읽지 않았습니다.**
- Claude Code는 `.claude/skills`를 읽었고, **`.agents/skills`는 읽지 않았습니다.** 단, `.claude/skills/<name>`이 `.agents/skills/<name>`을 가리키는 symlink이면 읽습니다. 이 결과는 [`06-canonical-and-adapters.md`](06-canonical-and-adapters.md)의 근거입니다.
- `~/.codex/skills/`도 당시 설치본에서 읽혔지만 현재 공식 문서의 사용자 경로에는 없습니다. 새 skill은 `$HOME/.agents/skills/`에
  두고, 이 결과는 0.144.1의 호환 관측으로만 해석합니다.

`.agents/skills`는 Codex·Gemini CLI·Cursor 세 도구가 공유하는 자리이고, Claude Code만 예외입니다. 여러 도구용 skill을 둘 자리로 `.agents/skills`를 택하는 이유가 여기에 있습니다.

## 2. 어떻게 부르는가

| | 명시 호출 | 모델 자동 호출 | 본문이 들어가는 방식 | 동의 절차 |
| --- | --- | --- | --- | --- |
| Claude Code | `/name 인자` | `Skill` tool 호출 (목록에서 설명 보고 선택) | 렌더링된 본문이 대화에 **메시지로 삽입**, 이후 턴에도 남음 | 없음 (`allowed-tools`는 신뢰 여부와 무관하게 적용) |
| Codex | `$name 인자` 또는 TUI `/skills` | 모델이 설명 보고 선택 (`policy.allow_implicit_invocation`으로 끌 수 있음) | 모델이 **파일을 직접 읽음** (`sed -n '1,240p' .agents/skills/…/SKILL.md` 관측) | 없음 |
| Gemini CLI | — (모델 경유) | `activate_skill` tool 호출 | 본문 + 폴더 구조가 대화에 삽입, skill 폴더가 허용 경로에 추가 | **있음** — 이름·목적·접근 경로를 보여 주고 확인 요청 |
| Cursor | `/`로 검색·선택, custom mode | 설명 보고 선택 | (문서에 미기재) | 없음 |

Claude Code와 Codex의 삽입 방식 차이는 실습 로그에서 그대로 보입니다. Claude Code는 `Skill` tool 호출 한 번으로 본문이 들어오고, Codex는 shell 명령으로 `SKILL.md`를 읽는 단계가 transcript에 남습니다 [실행 검증 · 실습 01·03]. 결과는 같아도 **비용 구조가 다릅니다.** Codex는 파일을 읽는 tool 호출 한 턴이 더 듭니다.

## 3. 같은 이름이 둘이면

| | 규칙 | 실측 |
| --- | --- | --- |
| Claude Code | managed(조직) > 개인 > 프로젝트. plugin skill은 `plugin:name`으로 분리 | 개인 `~/.claude/skills/meeting-actions`가 프로젝트 사본을 가렸다. 목록 요청 시 모델이 "세 곳에 있고 개인 사본만 활성"이라고 설명했다 [실행 검증 · 실습 04] |
| Codex | 문서: 모든 사본을 표시 | 목록에 저장소·홈 사본이 **둘 다** 나타났고, `$meeting-actions` 호출은 **저장소 사본으로** 갔다(1회 관측) [실행 검증 · 실습 04] |
| Gemini CLI | 워크스페이스 > 사용자 > extension > built-in. 높은 쪽이 이김 | [문서 확인] |
| Cursor | (문서에 미기재) | — |

Claude Code와 Codex의 방향이 **반대라는** 점을 기억해 두면 좋습니다. Claude Code는 개인 사본이 프로젝트 사본을 덮고, Codex는 관측상 저장소 사본이 홈 사본보다 먼저 선택됐습니다. 팀 skill을 개인 폴더에 복사해 두고 잊으면 Claude Code에서는 팀 버전이 조용히 무시됩니다.

## 4. 무엇이 있는지 확인하는 법

| | 대화 안 | 터미널 |
| --- | --- | --- |
| Claude Code | `/skills` 메뉴, 또는 "사용 가능한 skill 이름과 출처를 알려 줘" | `claude -p "What skills are available? List names and sources."` |
| Codex | `/skills` | `codex exec "Which skills are available? List names and paths."` |
| Gemini CLI | `/skills list [all]`, `/skills enable|disable <name>`, `/skills reload` | `gemini skills list --all`, `gemini skills install <url>` |
| Cursor | `/` 입력 후 검색 | — |

"목록을 물어보는" 방식은 모델의 답이므로 100% 신뢰할 수는 없지만, 실습에서 Claude Code·Codex 모두 실제 로드된 경로까지 정확히 답했습니다 [실행 검증]. 2026-08-30 스크립트 실행에서는 Codex가 stdin의 추가 입력을 기다린 적이 있어 `< /dev/null`을 호환 장치로 사용했습니다. 현재 명령의 필수 문법은 아닙니다.

## 5. 확장 필드와 부가 파일

| | 공통 규격 외 확장 | 부가 파일 |
| --- | --- | --- |
| Claude Code | `disable-model-invocation`, `user-invocable`, `argument-hint`, `model`, `context: fork`, `agent`, `hooks`, `paths` 등 | — (frontmatter) |
| Codex | frontmatter는 규격대로 | `agents/openai.yaml`: `interface`(표시 이름·기본 프롬프트), `policy.allow_implicit_invocation`, `dependencies.tools` |
| Gemini CLI | (문서에 `name`·`description`만 기재) | — |
| Cursor | `paths`, `disable-model-invocation`, `icon`, `color` | — |

`allowed-tools`는 공통 규격의 선택 필드지만 아직 실험적이므로 도구별 지원과 문법을 확인해야 합니다. 그 밖의 Claude Code 전용 필드를 넣은 skill을 `.agents/skills`에 두면 Codex·Gemini는 그 필드를 **무시합니다.** 대개 무해하지만, `context: fork`처럼 **동작을 바꾸는** 필드는 다른 도구에서 다른 결과를 냅니다. 규격 필드만으로 해결할 수 없을 때만 확장을 사용하고, 그 skill은 해당 도구 전용 경로에 둡니다.

## 6. 비-대화형 실행

실습은 모두 터미널에서 실행했습니다. 두 도구의 최소 명령은 다음과 같습니다.

```bash
# Claude Code — 결과 JSON, tool 호출까지 보려면 stream-json
claude -p "/meeting-actions input/meeting-notes.md" --allowedTools "Read Skill" --output-format json
claude -p "…" --output-format stream-json --verbose     # Skill tool 호출이 assistant 이벤트에 기록됨

# Codex — 마지막 메시지를 파일로
codex exec --skip-git-repo-check -o out.md '$meeting-actions input/meeting-notes.md'
```

Claude Code에서 skill이 실제로 호출됐는지는 `stream-json` 출력의 `tool_use` 이벤트에서 `"name": "Skill"`과 `"skill": "meeting-actions"`를 찾으면 알 수 있습니다. 실습의 판정 스크립트도 이 방법을 사용합니다. 단, `/name`으로 **명시 호출하면** `Skill` tool 이벤트가 나오지 않습니다. 도구가 모델에게 보내기 전에 본문을 펼치기 때문입니다 [실행 검증 · 실습 01].

## 이 장을 끝내면

- 네 도구의 skill 경로를 확인하고, `.agents/skills`가 왜 여러 도구의 공통 자리인지 설명할 수 있습니다.
- Claude Code와 Codex의 충돌 규칙이 반대 방향임을 알 수 있습니다.
- 내 환경에 어떤 skill이 로드됐는지 터미널에서 확인할 수 있습니다.
