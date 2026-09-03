# 01. 첫 skill — 설치, 명시 호출, 자동 호출

> 다음 → [`02-description-experiments.md`](02-description-experiments.md)

## 목표

`meeting-actions` skill을 설치하고 Claude Code에서 세 가지를 관측한다: `/name`으로 부르기, 요청만으로 모델이 고르기, 관련 없는 요청에는 고르지 않기.

## 1. 설치 확인

`setup.sh`가 이미 `.agents/skills/meeting-actions`와 symlink `.claude/skills/meeting-actions`를 만들었다. 먼저 skill 파일을 읽어 본다.

```bash
cat .agents/skills/meeting-actions/SKILL.md
```

frontmatter의 `name`이 폴더 이름과 같은지, `description`이 "무엇을 / 언제 / 언제 아님" 세 부분인지 확인한다. 그리고 Claude Code가 이 skill을 목록에 올렸는지 묻는다.

```bash
scripts/run-claude.sh list "What skills are available? List only their names, one per line."
cat logs/list.out
```

`meeting-actions`가 보이면 된다. 개인 폴더(`~/.claude/skills`)의 skill과 Claude Code 내장 skill도 함께 나온다.

## 2. 명시 호출

```bash
scripts/run-claude.sh e1 "/meeting-actions input/meeting-notes.md"
cat logs/e1.out
python3 .agents/skills/meeting-actions/scripts/check.py logs/e1.out
```

`run-claude.sh`가 출력하는 요약 줄의 `tools=`를 본다. **`Skill` tool 호출이 없다.** `/name`으로 부르면 Claude Code가 모델에게 보내기 전에 본문을 펼치므로 모델 입장에서는 처음부터 지시가 있었던 것과 같다.

## 3. 자동 호출

이번에는 이름을 부르지 않는다.

```bash
scripts/run-claude.sh e2 "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘"
python3 .agents/skills/meeting-actions/scripts/check.py logs/e2.out
```

요약 줄의 `tools=`에 `('Skill', '{"skill": "meeting-actions", "args": "input/meeting-notes.md"}')`가 있으면 모델이 description을 보고 골라 부른 것이다. 인자로 파일 경로가 넘어간 것도 보인다.

## 4. 오호출 방지

```bash
scripts/run-claude.sh e3 "input/meeting-notes.md 를 세 문장으로 요약해 줘"
cat logs/e3.out
```

`tools=`에 `Skill`이 없고 세 문장 요약이 나오면 description의 "일반 문서 요약에는 쓰지 않는다"가 작동한 것이다. 판정기는 당연히 FAIL이다(표가 없으므로) — 여기서 FAIL은 정상이다.

## 5. 기록

| 실행 | Skill tool 호출 | 판정 | 비고 |
| --- | --- | --- | --- |
| e1 명시 | | | |
| e2 자동 | | | |
| e3 요약 | | FAIL이 정상 | |

## 작성 환경의 실제 결과

| 실행 | Skill tool 호출 | 판정 | 토큰(캐시 읽기/쓰기/출력) |
| --- | --- | --- | --- |
| e1 명시 | 없음 (본문이 미리 펼쳐짐) | PASS | 31,368 / 11,921 / 411 |
| e2 자동 | `meeting-actions`, args=`input/meeting-notes.md` | PASS | 48,245 / 16,004 / 503 |
| e3 요약 | 없음 | FAIL(정상) | 34,020 / 7,961 / 567 |

- 자동 호출은 명시 호출보다 한 턴(목록 보고 Skill tool 호출)이 더 들어 캐시 읽기가 약 1.7만 토큰 많았다.
- 모델은 파일을 읽을 때 `Read` tool 대신 `Bash(cat …)`를 썼다. `--allowedTools "Read Skill"`만 허용했는데도 읽기 전용 shell 명령은 실행됐다. 실습에는 영향 없다.
- e2를 두 번 더 돌려 3/3 모두 Skill 호출·PASS였다(05에서 사용).

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| `logs/e1.out`이 없거나 비어 있고 `.err`에 로그인 오류 | Claude Code 미로그인 | `claude`를 한 번 대화형으로 실행해 로그인 |
| 목록에 `meeting-actions`가 없다 | symlink가 깨졌거나 `.claude/skills`가 아닌 곳에 있음 | `ls -la .claude/skills/` 확인. `ln -sfn ../../.agents/skills/meeting-actions .claude/skills/meeting-actions` |
| 이미 Claude Code 세션 안에서 실행 중 | 중첩 실행 제한 | 별도 터미널에서 실행하거나 `env -u CLAUDECODE scripts/run-claude.sh …` |
| Skill 호출은 됐는데 FAIL | 모델·버전 차이로 형식이 어긋남 | 04에서 본문을 보강하는 방법을 따른다. 결과를 그대로 기록 |
