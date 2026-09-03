# 03. 같은 skill을 Codex에서 — `$name`, 파일 읽기, 경로 탐침

> 이전 ← [`02-description-experiments.md`](02-description-experiments.md) · 다음 → [`04-tighten-and-collide.md`](04-tighten-and-collide.md)

## 목표

같은 `SKILL.md`를 Codex가 어떻게 부르고 읽는지 보고, Codex와 Claude Code가 **어느 경로를 읽는지** 탐침 skill로 표를 채운다. 그리고 같은 본문에 두 도구가 다르게 답하는 지점을 찾는다.

## 1. 명시 호출과 자동 호출

Codex의 명시 호출은 `$name`이다. 프롬프트에 `$`가 있으므로 **작은따옴표로** 감싼다.

```bash
scripts/run-codex.sh c1 '$meeting-actions input/meeting-notes.md'
scripts/run-codex.sh c2 'input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘'
for l in c1 c2; do python3 .agents/skills/meeting-actions/scripts/check.py logs/$l.out; done
```

요약 줄의 "SKILL.md 읽음: N회"를 본다. transcript도 직접 본다.

```bash
grep -v '^hook:' logs/c2.codex.txt | head -40
```

## 2. 관측 포인트

- Codex는 `Skill` 같은 전용 tool 없이 **모델이 shell로 `SKILL.md`를 읽는다.** transcript에 `sed -n '1,240p' .agents/skills/meeting-actions/SKILL.md` 같은 줄이 남는다. Claude Code가 본문을 메시지로 삽입하는 것과 다른 방식이다.
- transcript 머리에 `sandbox: read-only`, `approval: never`가 찍힌다. 읽기만 하는 실습이라 문제없다.
- 출력의 **행 수를** Claude Code 결과와 비교한다.

## 3. 경로 탐침

각 후보 경로에 이름만 다른 탐침 skill을 두고, 두 도구에 목록을 물어 어느 것이 보이는지 적는다. 홈 디렉터리에도 하나 둔다 — **끝나면 지운다.**

```bash
mk() { mkdir -p "$1/$2"; printf -- '---\nname: %s\ndescription: Probe skill to test discovery. Never use.\n---\nProbe.\n' "$2" > "$1/$2/SKILL.md"; }
mk ~/.agents/skills        ws-probe-home-agents
mk .claude/skills          ws-probe-claude-only
mk .agents/skills          ws-probe-repo-agents

scripts/run-codex.sh  paths-codex  'Which skills are available to you right now? List only their names, one per line, and for each the directory path it was loaded from.'
scripts/run-claude.sh paths-claude "What skills are available? List only their names, one per line."
grep ws-probe logs/paths-codex.out; echo ---; grep ws-probe logs/paths-claude.out

rm -rf ~/.agents/skills/ws-probe-home-agents .claude/skills/ws-probe-claude-only .agents/skills/ws-probe-repo-agents
rmdir ~/.agents/skills ~/.agents 2>/dev/null   # 원래 없었다면 정리
```

symlink도 시험한다.

```bash
mk .agents/skills ws-link-probe
ln -s ../../.agents/skills/ws-link-probe .claude/skills/ws-link-probe
scripts/run-claude.sh link-claude "What skills are available? List only their names, one per line."
grep ws-link logs/link-claude.out
rm .claude/skills/ws-link-probe; rm -rf .agents/skills/ws-link-probe
```

## 4. 기록

| 경로 | Codex | Claude Code |
| --- | --- | --- |
| `.agents/skills` (저장소) | | |
| `.claude/skills` (저장소) | | |
| `~/.agents/skills` (홈) | | |
| `.claude/skills/<name>` → `.agents/skills/<name>` symlink | — | |

| 실행 | SKILL.md 읽음 | 판정 | 행 수 |
| --- | --- | --- | --- |
| c1 `$name` | | | |
| c2 자동 | | | |

## 작성 환경의 실제 결과

| 경로 | Codex 0.144.1 | Claude Code 2.1.251 |
| --- | --- | --- |
| `.agents/skills` | ✓ | ✗ |
| `.claude/skills` | ✗ | ✓ |
| `~/.agents/skills` | ✓ | ✗ |
| `~/.codex/skills` (당시 호환 경로) | ✓ | — |
| `~/.claude/skills` | ✗ | ✓ |
| symlink `.claude/skills/x → .agents/skills/x` | — | ✓ |

Codex 목록에는 plugin skill이 `browser:control-in-app-browser`처럼 `plugin:name` 형식으로, Claude Code 목록에는 내장 skill(`code-review`, `loop` 등)이 함께 나왔다.

> 이 표는 2026-08-30 관측 기록이다. 2026-09-02 현재 Codex 공식 사용자 경로는 `$HOME/.agents/skills`이며, 새 Skill을 `~/.codex/skills`에 설치하는 방법은 권하지 않는다.

| 실행 | SKILL.md 읽음 | 판정 | 행 수 |
| --- | --- | --- | --- |
| c1 `$meeting-actions` | 1회 (`sed -n '1,240p' …`) | **FAIL** | 5 |
| c2 자동 | 1회 | **FAIL** | 5 |

Codex는 두 번 모두 "검색 고도화 중간 보고회를 대회의실에서 개최 — 담당 미정 — 2026-09-15"를 1행으로 넣었다. 본문 규칙 1은 "결정·약속 문장을 찾는다"였고, 보고회 날짜·장소 확정은 분명 **결정이다**. Claude Code는 이것을 액션이 아니라고 봤고(4행), Codex는 액션으로 봤다(5행). 어느 쪽도 규칙을 어기지 않았다 — **규칙이 모호했다.** 이 지점이 04의 출발점이다.

Codex 실행 토큰은 약 15,000(c1·c2), 목록 요청은 약 20,000이었다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| 과거 실행에서 `codex exec`가 `Reading additional input from stdin...` 뒤 멈춤 | 스크립트 안에서 stdin이 열려 있었음 | 현재 버전에서 먼저 재현 여부를 확인하고, 필요할 때만 stdin을 닫는다 |
| `$meeting-actions`가 빈 문자열로 들어감 | 큰따옴표로 감싸 shell이 `$meeting`을 변수로 확장 | 작은따옴표 |
| `codex_models_manager` ERROR 줄이 보임 | 모델 캐시 갱신 경고 | 결과에 영향 없음. 무시 |
| Codex가 skill을 안 읽고 바로 답함 | 자동 호출 판단이 다름 | `$name`으로 명시 호출. 결과를 그대로 기록 |
| 홈의 탐침을 지우는 것을 잊음 | — | README의 reset 절 |
