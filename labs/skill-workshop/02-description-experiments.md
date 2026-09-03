# 02. description 실험 — 과호출과 끄기

> 이전 ← [`01-first-skill.md`](01-first-skill.md) · 다음 → [`03-same-skill-in-codex.md`](03-same-skill-in-codex.md)

## 목표

본문은 그대로 두고 description 한 줄만 넓혀서, 01에서 skill을 부르지 않던 요약 요청이 skill을 부르게 되는 것을 본다. 그리고 파일을 고치지 않고 skill을 끄는 방법을 익힌다.

## 1. description을 넓힌다

`variants/meeting-actions-broad/SKILL.md`는 description만 다음과 같이 바꾼 사본이다.

```text
문서·회의록·노트를 읽고 정리한다. 요약, 정리, 핵심 추출, 액션 아이템 등 문서 작업 전반에 사용한다.
```

이것을 실제 skill 자리에 덮어쓴다(원본은 git에 있다).

```bash
cp variants/meeting-actions-broad/SKILL.md .agents/skills/meeting-actions/SKILL.md
```

## 2. 요약 요청을 세 번

```bash
for i in 1 2 3; do scripts/run-claude.sh broad-$i "input/meeting-notes.md 를 세 문장으로 요약해 줘"; done
```

요약 줄의 `tools=`에서 `Skill` 호출 횟수를 센다. 그리고 출력을 읽는다.

```bash
head -c 300 logs/broad-3.out
```

## 3. 되돌린다

```bash
git checkout -- .agents/skills/meeting-actions/SKILL.md
```

## 4. 파일을 고치지 않고 끄기

저장소에 들어온 남의 skill을 끄고 싶을 때 쓰는 방법이다. Claude Code는 설정의 `skillOverrides`로 표시 상태를 바꾼다.

```bash
printf '{"skillOverrides": {"meeting-actions": "off"}}\n' > .claude/settings.local.json
scripts/run-claude.sh off-list "What skills are available? List only their names, one per line."
grep -c meeting-actions logs/off-list.out     # 0이면 꺼진 것
```

이 상태는 05에서 기준선을 잴 때 다시 쓴다. 지금은 원상 복구한다.

```bash
rm .claude/settings.local.json
```

## 5. 기록

| 실행 | Skill 호출 | 출력 |
| --- | --- | --- |
| broad-1 | | |
| broad-2 | | |
| broad-3 | | |
| off-list에 meeting-actions | (0이어야 함) | |

## 작성 환경의 실제 결과

- broad-1·2·3: **3/3 Skill 호출**. 인자는 `"input/meeting-notes.md 를 세 문장으로 요약"`으로 넘어갔다.
- broad-1·2의 출력은 요약 세 문장이었다. skill 본문("표 하나만, 요약 금지")을 로드하고도 사용자 요청을 따랐다.
- broad-3의 출력 첫 문단: "불러온 `meeting-actions` skill의 본문은 '액션 아이템 표만 출력하고 요약은 쓰지 않는다'로 되어 있어, description('요약·정리 전반에 사용')과 어긋납니다. 요청하신 것은 요약이므로 사용자 요청을 우선해 세 문장 요약을 드립니다." — 모델이 description과 본문의 모순을 지적했다.
- `skillOverrides: off` 후 목록에서 `meeting-actions`가 사라졌다(0건).

해석 [해석]: description은 "이 skill을 열까"의 근거일 뿐이고, 열린 뒤 무엇을 할지는 본문과 사용자 요청이 겨룬다. 넓은 description의 비용은 **불필요한 로드(토큰)와 모순으로 인한 혼란이지**, 항상 잘못된 출력은 아니다. 그래서 과호출은 출력만 봐서는 잘 안 보이고 로그의 tool 호출을 봐야 한다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| broad에서도 Skill 호출이 0회 | 모델·버전 차이. 또는 목록 예산에 밀려 description이 잘림 | `claude`에서 `/context`의 Skills 행 확인. 결과를 그대로 기록 |
| 되돌린 뒤에도 넓은 description이 보임 | Claude Code가 파일 변경을 감지하기 전 | 새 프로세스(`claude -p`)는 매번 다시 읽으므로 대개 문제없음. `git diff`로 파일 확인 |
| `settings.local.json` 때문에 다음 단계가 이상함 | 삭제를 잊음 | `rm .claude/settings.local.json` |
