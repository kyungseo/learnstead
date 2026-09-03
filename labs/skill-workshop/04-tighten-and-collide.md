# 04. 본문 보강과 충돌 — v1.1로 수렴, 겹치는 description, 같은 이름

> 이전 ← [`03-same-skill-in-codex.md`](03-same-skill-in-codex.md) · 다음 → [`05-skill-vs-prompt.md`](05-skill-vs-prompt.md)

## 목표

03에서 갈린 경계 사례를 규칙 한 줄로 명시해 두 도구를 수렴시킨다. 그다음 두 종류의 충돌을 만든다: description이 겹치는 **다른 이름의** skill, 그리고 **같은 이름이** 개인·프로젝트 경로에 동시에 있는 경우.

## 1. 규칙을 좁힌다 (v1.0 → v1.1)

`setup.sh`가 설치한 `SKILL.md`는 이미 v1.1이다. `git log`나 본문 규칙 1을 보면 v1.0과의 차이가 보인다.

```text
v1.0  1. 입력에서 "~하기로 함", "~가 맡음", "~까지" 같은 결정·약속 문장을 찾는다.
      논의만 하고 결정하지 않은 것은 뽑지 않는다.

v1.1  1. 입력에서 "~가 ~하기로 함", "~가 맡음", "~까지 ~한다" 같은 **사람이 할 일을 약속한 문장을** 찾는다.
      논의만 하고 결정하지 않은 것, 그리고 날짜·장소를 정했을 뿐 누군가가 할 일이 아닌 것
      (예: "보고회는 9/15에 연다", "다음 회의는 9/4")은 액션 아이템이 아니므로 뽑지 않는다.
```

v1.0으로 03을 재현하고 싶으면 규칙 1을 위 v1.0 문장으로 바꿔 돌린 뒤 되돌린다. 여기서는 v1.1로 두 도구를 다시 돌린다.

```bash
scripts/run-codex.sh  v11-c1 '$meeting-actions input/meeting-notes.md'
scripts/run-codex.sh  v11-c2 'input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘'
scripts/run-claude.sh v11-e1 "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘"
scripts/run-claude.sh v11-e2 "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘"
for l in v11-c1 v11-c2 v11-e1 v11-e2; do printf '%-8s %s\n' $l "$(python3 .agents/skills/meeting-actions/scripts/check.py logs/$l.out)"; done
```

## 2. description이 겹치는 두 번째 skill

`variants/notes-summary`는 "회의록 정리"에 반응하는 다른 skill이다. 첫 줄에 `[notes-summary]`를 찍으므로 어느 것이 잡혔는지 출력만 봐도 안다.

```bash
cp -R variants/notes-summary .agents/skills/notes-summary
ln -s ../../.agents/skills/notes-summary .claude/skills/notes-summary

for i in 1 2 3; do scripts/run-claude.sh ovl-$i "input/meeting-notes.md 회의록 정리해 줘"; done
scripts/run-claude.sh ovl-actions "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘"
scripts/run-codex.sh  ovl-codex  'input/meeting-notes.md 회의록 정리해 줘'
for l in ovl-1 ovl-2 ovl-3 ovl-actions ovl-codex; do printf '%-12s %s\n' $l "$(head -c 60 logs/$l.out | tr '\n' ' ')"; done

rm .claude/skills/notes-summary; rm -rf .agents/skills/notes-summary
```

## 3. 같은 이름이 두 곳에

기존 개인 skill을 건드리지 않도록 실험 전용 이름 `ws-dup-meeting-actions`를 쓴다. 같은 이름의 프로젝트 사본과 개인 사본을 만든 뒤 어느 쪽이 채택되는지 확인하고, 끝나면 실험용 사본만 지운다.

```bash
mkdir -p .agents/skills/ws-dup-meeting-actions ~/.claude/skills/ws-dup-meeting-actions ~/.agents/skills/ws-dup-meeting-actions
printf -- '---\nname: ws-dup-meeting-actions\ndescription: (project copy) 우선순위 실험용 skill.\n---\n\n첫 줄에 정확히 `[PROJECT-COPY]`라고 쓰고 "project"라고만 답한다.\n' > .agents/skills/ws-dup-meeting-actions/SKILL.md
ln -sfn ../../.agents/skills/ws-dup-meeting-actions .claude/skills/ws-dup-meeting-actions
printf -- '---\nname: ws-dup-meeting-actions\ndescription: (personal copy) 우선순위 실험용 skill.\n---\n\n첫 줄에 정확히 `[PERSONAL-COPY]`라고 쓰고 "personal"이라고만 답한다.\n' > ~/.claude/skills/ws-dup-meeting-actions/SKILL.md
printf -- '---\nname: ws-dup-meeting-actions\ndescription: (home copy) 우선순위 실험용 skill.\n---\n\n첫 줄에 정확히 `[HOME-COPY]`라고 쓰고 "home"이라고만 답한다.\n' > ~/.agents/skills/ws-dup-meeting-actions/SKILL.md

scripts/run-claude.sh dup-claude "/ws-dup-meeting-actions"
scripts/run-claude.sh dup-claude-list "What skills are available? List names one per line; if a name appears more than once, list it each time with its source."
scripts/run-codex.sh  dup-codex '$ws-dup-meeting-actions'
scripts/run-codex.sh  dup-codex-list 'Which skills are available? List names one per line with the directory path each was loaded from. If a name appears more than once, list every copy.'
head -2 logs/dup-claude.out; grep ws-dup logs/dup-claude-list.out; head -2 logs/dup-codex.out; grep ws-dup logs/dup-codex-list.out

rm -rf .agents/skills/ws-dup-meeting-actions .claude/skills/ws-dup-meeting-actions
rm -rf ~/.claude/skills/ws-dup-meeting-actions ~/.agents/skills/ws-dup-meeting-actions
rmdir ~/.agents/skills ~/.agents 2>/dev/null
```

## 4. 기록

| 실행 | 판정 |
| --- | --- |
| v11-c1 / v11-c2 (Codex) | |
| v11-e1 / v11-e2 (Claude Code) | |

| 요청 | Claude Code가 고른 skill (3회) | Codex |
| --- | --- | --- |
| "회의록 정리해 줘" | | |
| "액션 아이템을 정리해 줘" | | — |

| 도구 | 채택된 사본 | 목록에 보인 사본 |
| --- | --- | --- |
| Claude Code | | |
| Codex | | |

## 작성 환경의 실제 결과

**v1.1 수렴**: Codex 2/2 PASS, Claude Code 2/2 PASS. 규칙 한 줄로 5행이 4행이 됐다. Codex 토큰은 v1.0 약 15,000에서 v1.1 약 13,500으로 오히려 줄었다(본문은 길어졌지만 출력이 짧아짐).

**겹치는 description**: "회의록 정리해 줘" → Claude Code 3/3 `notes-summary`, Codex 1/1 `notes-summary`(transcript에 `.agents/skills/notes-summary/SKILL.md` 읽는 줄). "액션 아이템을 정리해 줘" → `meeting-actions`. 두 description이 각자 "정리"와 "액션 아이템"을 갖고 있었고, 모델은 요청의 단어를 그대로 대조했다.

**같은 이름**:

| 도구 | 채택된 사본 | 목록 |
| --- | --- | --- |
| Claude Code | 개인 `~/.claude/skills` — 출력 첫 줄 `[PERSONAL-COPY]` | 모델이 "세 곳에 있고 개인 사본만 Skill tool에 노출, 프로젝트 사본은 가려짐"이라고 설명 |
| Codex | 저장소 `.agents/skills` — 정상 표 출력, `[HOME-COPY]` 없음 (1회) | 저장소·홈 사본 **둘 다** 경로와 함께 나열 |

Claude Code는 문서의 우선순위(개인 > 프로젝트)와 일치했다. Codex는 문서가 "둘 다 표시"라고만 하는데, 호출은 저장소 사본으로 갔다. 1회 관측이므로 [부분 검증]이다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| v1.1에서도 Codex가 5행 | 모델·버전 차이 | 규칙 1의 예를 더 구체적으로. 결과를 그대로 기록 |
| ovl에서 매번 다른 skill | description 어휘가 요청과 반반 겹침 | 각 description에 "언제 안 쓴다"를 추가하고 재시험 |
| dup 실험 후 다른 프로젝트에서 `ws-dup-meeting-actions`가 보임 | 실험용 사본을 안 지움 | 프로젝트와 홈의 `ws-dup-meeting-actions` 폴더만 지운다 |
