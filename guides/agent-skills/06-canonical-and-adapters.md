# 06. 한 절차를 여러 도구에 — canonical + adapter

> 이전 ← [`05-discovery-and-invocation.md`](05-discovery-and-invocation.md) · 다음 → [`07-what-goes-wrong.md`](07-what-goes-wrong.md)

## 이 장에서 답하는 질문

- Claude Code와 Codex(그리고 Gemini CLI·Cursor)에서 같은 절차를 쓰려면 파일을 몇 벌 두어야 하는가
- 규격 안에서만 쓰면 정말 그대로 이식되는가
- 도구 전용 기능이 필요할 때는 어떻게 나누는가

## 1. 규격 안에서 쓰면 한 벌로 끝난다

실습의 `meeting-actions`는 규격 필드(`name`, `description`, `license`, `metadata`)만 사용했습니다. 같은 폴더를 `.claude/skills/`와 `.agents/skills/`에 두었더니 Claude Code와 Codex 모두 읽었고, 본문을 한 줄 고친 v1.1은 두 도구에서 모두 판정을 통과했습니다 [실행 검증 · 실습 03·04]. **본문이 규격 안에 있으면 이식은 경로 문제로 줄어듭니다.**

경로 문제의 답은 [`04`](04-tool-differences.md) 1절에 있습니다. `.agents/skills`는 Codex·Gemini CLI·Cursor가 공유하고 Claude Code만 `.claude/skills`를 읽습니다. Claude Code는 **symlink도 따라갑니다** [실행 검증]. 따라서 가장 단순한 배치는 다음과 같습니다.

```text
프로젝트/
├── .agents/skills/
│   └── meeting-actions/          ← 실제 파일 (canonical)
│       ├── SKILL.md
│       └── scripts/check.py
└── .claude/skills/
    └── meeting-actions -> ../../.agents/skills/meeting-actions    ← symlink
```

symlink 대신 복사해도 되지만, 시간이 지나면 두 사본의 내용이 달라질 수 있습니다. 실습에서도 `.claude`·`.agents` 두 사본을 복사로 유지하다가 한 번에 고쳐야 했습니다. git은 symlink를 그대로 저장하므로 저장소에 넣을 수 있습니다. 단 Windows 협업자가 있으면 symlink가 깨질 수 있습니다. 이때는 복사본과 "동기화 검사 스크립트"를 함께 두는 방법이 현실적입니다.

## 2. 어디까지가 "규격 안"인가

| 써도 되는 것 | 피해야 하는 것 (도구 전용) |
| --- | --- |
| `name` `description` `license` `compatibility` `metadata`와 신중하게 쓴 `allowed-tools` | Claude Code: `context: fork`, `agent`, `hooks`, `paths`, `!`명령`` 동적 컨텍스트, `${CLAUDE_SKILL_DIR}` 치환 |
| 본문 Markdown, 상대 경로로 가리키는 `scripts/` `references/` `assets/` | Codex: `agents/openai.yaml`의 정책·표시 정보 |
| "인자로 파일 경로가 오면 읽는다" 같은 **말로 쓴** 인자 처리 | `$ARGUMENTS`, `$1` 자리표시자 |
| 실행 명령을 **폴더 기준 상대 경로로** 서술 | 특정 tool 이름(`Bash`, `Read`)에 의존한 지시 |

기준은 "다른 도구에서 그 줄이 **문자 그대로** 모델에게 보였을 때 해가 없는가"입니다. `!`명령``이 Codex에서 문자 그대로 보이면 모델은 그것을 지시로 오해할 수 있습니다. 반대로 `metadata.version` 같은 필드는 무시돼도 동작에 영향을 주지 않습니다.

## 3. 도구 전용 기능이 필요할 때 — canonical + adapter

절차의 본체는 하나지만 도구마다 다르게 감싸야 하는 경우가 있습니다.

- Claude Code에서는 서브에이전트로 격리 실행(`context: fork`)하고 싶다.
- Codex에서는 `$name` 명시 호출만 허용(`allow_implicit_invocation: false`)하고 싶다.
- Cursor에서는 특정 경로에서만 켜고 싶다(`paths`).

이때 본체를 복제하지 않는 방법이 **canonical + adapter입니다.**

```text
skills/
└── release-notes.md                 ← canonical: 절차 본문 전체. 도구 무관

.claude/skills/release-notes/SKILL.md   ← adapter: frontmatter(context: fork 등) + "skills/release-notes.md를 읽고 따른다"
.agents/skills/release-notes/SKILL.md   ← adapter: 규격 frontmatter + 같은 한 줄
.agents/skills/release-notes/agents/openai.yaml   ← Codex 정책
.cursor/rules/release-notes.mdc         ← adapter: paths/globs + 같은 한 줄
```

adapter는 짧게 유지합니다. 도구별 frontmatter와 "canonical을 읽어라"는 한 줄, 그리고 그 도구에서만 뜻이 있는 진입 규약(인자 자리표시자, 동적 컨텍스트)만 담습니다. 절차를 고칠 때는 canonical 파일 하나만 수정합니다.

이 방식에는 **간접 참조 한 번이라는 비용이** 있습니다. 모델이 adapter를 읽고 다시 canonical을 읽어야 하므로 tool 호출이 한 턴 늘고, canonical 경로가 바뀌면 adapter가 모두 깨집니다. 따라서 adapter마다 canonical 경로를 검사하는 스크립트(예: 각 adapter가 가리키는 파일이 존재하는지, 이름이 일치하는지)를 두는 편이 좋습니다. 이 가이드를 만든 저장소는 그 검사를 테스트 러너에 넣어 두었습니다.

## 4. 선택 기준

| 상황 | 권장 배치 |
| --- | --- |
| 도구 전용 기능이 없음 | 규격 필드만 쓴 `SKILL.md` 한 벌 + `.agents/skills` + Claude Code용 symlink |
| 한 도구에서만 전용 기능이 필요 | 그 도구 경로에만 두고 호환 범위를 명시 |
| 여러 도구에서 서로 다른 전용 기능이 필요 | canonical + 얇은 adapter + 경로 검사 |

처음부터 canonical + adapter로 시작하면 필요 이상으로 복잡해질 수 있습니다. 실습의 skill처럼 규격 안에서 끝나는 절차가 대부분이며, 도구별 기능이 실제로 필요해졌을 때 adapter를 도입해도 늦지 않습니다.

## 5. 진입 지시문과의 연결

skill이 여럿이 되면 진입 지시문(`CLAUDE.md`·`AGENTS.md`)에 **라우팅 한 줄을** 둡니다. "릴리스 노트를 쓸 땐 `release-notes` skill을 쓴다"처럼 적을 수 있습니다. 절차는 skill에 있고 지시문은 가리키기만 하므로 지시문이 무거워지지 않습니다. 반대로 지시문에 절차를 복제하면 두 곳의 내용이 달라질 수 있습니다. [`03`](03-same-thing-different-names.md) 3절에서 설명한 원칙입니다.

## 이 장을 끝내면

- 규격 필드만 쓴 skill을 `.agents/skills` + symlink로 네 도구에 한 벌로 배치할 수 있습니다.
- 도구 전용 필드를 canonical에서 adapter로 분리하는 기준을 알 수 있습니다.
- adapter의 비용(간접 참조, 경로 검사)을 설명할 수 있습니다.
