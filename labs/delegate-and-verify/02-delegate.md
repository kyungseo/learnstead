# 02. 위임 — 메인 컨텍스트는 줄었는가

> 이전 ← [`01-baseline.md`](01-baseline.md) · 다음 → [`03-parallel.md`](03-parallel.md)

## 목표

같은 검토를 `reviewer` subagent에 위임해 메인 토큰과 위임 토큰을 나눠 재고, 대화 이력에 기대는 한 문장 위임이 어떻게 되는지 본다.

## 1. 돌리기

```bash
./scripts/batch.sh main 3 s02-review-delegate s02-delegate-history s02-delegate-explicit
```

`s02-review-delegate`는 실행 폴더에 `agents/*/reviewer.*`를 복사한 뒤 "아래 검토를 reviewer subagent 하나에게 그대로 위임하고 직접 읽지 마라"를 앞에 붙입니다. `s02-delegate-history`(`prompts/delegate-history.md`)는 메인이 결함을 확인한 뒤 **"우리가 확인한 그 결함을 고치고 테스트를 추가해"** 한 문장만으로 `implementer`에게 위임하게 시킵니다. `s02-delegate-explicit`(`prompts/delegate-explicit.md`)은 같은 결함을 파일·함수·규격·검사 명령까지 적은 자기완결 프롬프트로 위임하는 대조군입니다.

## 2. 채점과 근거 찾기

```bash
python3 scripts/score.py --tsv runs/main/*-s02-*
```

위임이 실제로 일어났는지는 스트림이 아니라 기록에서 확인합니다.

- Claude Code: `runs/main/claude-s02-*/transcripts/<세션>/subagents/agent-*.jsonl` — subagent의 도구 호출과 결과 원문. 스트림의 `Agent` 도구 입력에 메인이 넘긴 프롬프트가 있습니다.
- Codex: `runs/main/codex-s02-*/rollouts/` — `parent_thread_id`가 있는 파일이 자식. `--json` 스트림에는 `wait`만 나옵니다.

## 3. 기록

| 도구 | 구성 | 메인 입력 | 위임 입력 | 합계 | 벽시계 | 위치 일치/3 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code | 직접(01) | | 0 | | | |
| Claude Code | 위임 | | | | | |
| Codex | 직접(01) | | 0 | | | |
| Codex | 위임 | | | | | |

이력 의존 위임과 자기완결 대조군: 메인이 넘긴 프롬프트 원문을 확인할 수 있는 범위에서 기록하고(본문이 보이지 않으면 확인 불가), subagent가 고친 함수 이름과 비용을 적습니다.

| 도구 | 메인이 넘긴 프롬프트 (요약) | subagent가 고친 것 | 테스트 |
| --- | --- | --- | --- |
| Claude Code | | | |
| Codex | | | |

## 작성 환경의 실제 결과

| 도구 | 구성 | 메인 컨텍스트(끝) | 메인 누적 | 위임 누적 | 벽시계 | 위치 일치/3 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code | 직접(01) | 25,143 | 69,457 | 0 | 17.1초 | 3/3 |
| Claude Code | 위임 | 24,441 | 48,022 | 28,757 | 32.6초 | 3/3 |
| Codex | 직접(01) | 25,291 | 119,121 | 0 | 22.9초 | 3/3 |
| Codex | 위임 | 23,439 | 115,646 | 130,481 | 80.1초 | 3/3 |

| 도구 | 메인이 넘긴 프롬프트 | subagent가 고친 것 | 테스트 |
| --- | --- | --- | --- |
| Claude Code 1·2회차 | "우리가 확인한 그 결함을 고치고 테스트를 추가해." 그대로 | 없음. 후보 세 개를 보고하며 되물음 | 통과(변경 없음) |
| Claude Code 3회차 | 위와 같음 → 되묻자 `SendMessage`로 재개하며 파일·함수·검사 명령을 보탬 | `in_month` + `tests/test_summarize.py` | 통과 |
| Codex 3회 | `spawn_agent`(`task_name: fix_month_end`, 3회차 `fork_turns: "all"`). 본문은 rollout에 암호화 | `in_month` + `tests/test_summarize.py` | 통과 |

| 도구 | 프롬프트 | 수정 성공 | 메인 누적 | 위임 누적 | 벽시계 |
| --- | --- | --- | --- | --- | --- |
| Claude Code | 이력 의존 | 1/3 | 74,234 | 41,143 | 73.8초 |
| Claude Code | 자기완결 | 3/3 | 74,177 | 42,765 | 76.7초 |
| Codex | 이력 의존 | 3/3 | 249,412 | 136,122 | 123.5초 |
| Codex | 자기완결 | 3/3 | 143,660 | 124,967 | 72.9초 |

- 메인 컨텍스트 끝 크기는 Claude Code −3%, Codex −7%에 그쳤고, 위임 쪽에 각각 2.9만·13만 토큰이 새로 들었습니다. 이번 작은 읽기에서는 컨텍스트 절감이 작고 누적 입력은 늘었습니다. 위임 여부는 다른 목적과 비용도 함께 보고 판단합니다.
- 이력 의존 위임은 Claude Code에서 결핍이 그대로 드러났고(추측하지 않고 되물음), Codex에서는 이력을 통째로 넘겨 가려졌습니다. 같은 결함을 자기완결 프롬프트로 위임한 대조군은 두 도구 모두 3/3이었고, Claude Code는 비용이 같았으며 Codex는 메인 토큰과 시간이 40% 줄었습니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| `agent_or_spawn`이 0 | 위임하지 않았거나 호출 기록을 수집하지 못함 | 프롬프트의 "직접 읽지 마라"가 있는지 확인. 도구가 위임을 건너뛴 것도 관측으로 기록 |
| Codex `rollouts/`에 자식 파일이 없음 | 세션 폴더가 다른 위치(`CODEX_HOME`) | `run-codex.sh`의 `$HOME/.codex/sessions` 경로를 환경에 맞게 수정 |
| subagent가 "파일을 찾을 수 없다"(worktree 격리 시) | worktree는 커밋에서 갈라지므로 미커밋 파일이 없음 | 이 실습은 매 실행이 커밋된 fixture에서 시작하므로 해당 없음. 자기 저장소에서는 먼저 커밋하고, feature branch 위면 `worktree.baseRef: "head"` |
