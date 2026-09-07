# 03. 병렬 — 동시 실행과 시간 절감은 다르다

> 이전 ← [`02-delegate.md`](02-delegate.md) · 다음 → [`04-review.md`](04-review.md)

## 목표

서로 다른 파일을 고치는 과제 셋을 subagent 셋에 동시에 맡기고, 하나씩 처리할 때와 총 경과 시간을 비교합니다. 이어서 같은 함수를 고치는 과제 둘을 공유 폴더와 별도 작업 폴더(worktree)에서 각각 실행해, 최종 파일에 두 기능이 남았는지와 통합 과정에서 충돌이 생겼는지 확인합니다.

## 1. 돌리기

```bash
./scripts/batch.sh main 3 s03-parallel s03-sequential s03-samefile s03-samefile-worktree
```

| 시나리오 | 프롬프트 | subagent | 격리 |
| --- | --- | --- | --- |
| `s03-parallel` | `task-abc-parallel.md` — A·B·C를 **동시에** | `implementer` ×3 | 없음 |
| `s03-sequential` | `task-abc-sequential.md` — 하나씩 순서대로 | `implementer` ×3 | 없음 |
| `s03-samefile` | `task-xy-samefile.md` — `render`에 X·Y 인자를 동시에 | `implementer` ×2 | 없음 |
| `s03-samefile-worktree` | 같음 | Claude Code `implementer-worktree`(`isolation: worktree`) · Codex는 `run-codex-worktrees.sh`가 `git worktree add` 둘 + `codex exec` 둘 | worktree |

## 2. 채점

```bash
python3 scripts/score.py --tsv runs/main/*-s03-*
cat runs/main/codex-s03-samefile-worktree-r1/merge.txt
cat runs/main/claude-s03-samefile-worktree-r1/worktrees.txt
```

같은 파일 과제는 `diff-stat.txt`와 `tests.txt`, 그리고 `proj/src/ledger/report.py`를 직접 열어 **두 인자(`title`·`top`)가 모두 있는지** 봅니다.

## 3. 기록

| 도구 | 구성 | 벽시계(중앙값) | 메인 입력 | 위임 입력 | 테스트 | 바뀐 파일 수 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code | 동시 3 | | | | | |
| Claude Code | 순차 | | | | | |
| Codex | 동시 3 | | | | | |
| Codex | 순차 | | | | | |

| 도구 | 격리 | `title` 있음 | `top` 있음 | 테스트 | 메인/merge가 한 일 |
| --- | --- | --- | --- | --- | --- |
| Claude Code | 없음 | | | | |
| Claude Code | worktree | | | | |
| Codex | 없음 | | | | |
| Codex | worktree 둘 | | | | |

현재 runner의 Codex worktree 결과는 `tests-x.txt`·`tests-y.txt`에 각 폴더 검사, `integration_status.txt`에 통합 상태를 남깁니다. 편집·통합 시도·전체 시간은 각각 `wall_edit_seconds.txt`·`wall_integration_seconds.txt`·`wall_total_seconds.txt`입니다. 최종 `title`·`top` 기능은 직접 호출하거나 코드를 대조하세요. 충돌 후의 PASS를 통합 성공으로 읽지 않습니다.

## 작성 환경의 실제 결과

Claude Code는 이 단계를 Opus 5(`CLAUDE_MODEL=opus`)로 돌렸습니다. Fable 5.1로 시작했다가 구독 세션 한도에 걸려 블록 전체를 같은 모델로 다시 쟀습니다.

| 도구 | 구성 | 벽시계(중앙값) | 메인 컨텍스트(끝) | 메인 누적 | 위임 누적 | 테스트 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code (Opus 5) | 동시 3 | 150.1초 (146~154) | 35,155 | 73,985 | 373,573 | 통과 3/3 |
| Claude Code (Opus 5) | 순차 | 256.3초 (242~272) | 35,418 | 234,678 | 260,755 | 통과 3/3 |
| Codex | 동시 3 | 223.2초 (218~232) | 24,646 | 282,832 | 398,951 | 통과 2/3 |
| Codex | 순차 | 343.5초 (277~425) | 28,651 | 462,757 | 455,401 | 통과 3/3 |

| 도구 | 격리 | `title` 있음 | `top` 있음 | 테스트 | 메인/merge가 한 일 |
| --- | --- | --- | --- | --- | --- |
| Claude Code (Opus 5) | 없음 | 3/3 | 3/3 | 통과 3/3 | "편집 직전 다시 읽어 상대 변경을 보존" 보고 |
| Claude Code (Opus 5) | worktree | 1/3 | 1/3 | 통과(2회는 변경 없음) | 2회: worktree에 남았다고 보고만. 1회: 메인이 두 변경을 옮겨 통합 |
| Codex | 없음 | 3/3 | 3/3 | 통과 3/3 | 최종 파일 확인 |
| Codex | worktree 둘 | 각자 | 각자 | 기존 runner는 merge 시도 후 메인만 검사 | `report.py` content conflict 3/3 |

- 동시 3은 순차의 0.6~0.65배였고, `transcripts/<세션>/subagents/`의 시각으로 세 subagent 구간이 실제로 겹친 것을 확인했습니다(9~13초 간격 시작). Codex 병렬의 실패 1회는 subagent C가 규격 기준으로 쓴 `--json` 테스트가 심어 둔 부호 결함을 드러낸 것입니다.
- 같은 함수를 격리 없이 고친 여섯 실행 모두 두 기능이 살아남았습니다. worktree는 덮어쓰기 대신 "합치는 일"을 남겼고, Claude Code 메인은 3회 중 1회만 합쳤습니다. Codex worktree 둘은 merge에서 3회 모두 충돌했습니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| 동시 3의 벽시계가 순차와 같다 | 순차 실행·대기·요청 한도 등 여러 가능성 | 스트림에서 `Agent` 호출 시각을 보고 실제 동시성 확인. 겹치지 않았다면 그 사실도 결과에 기록 |
| worktree 실행 뒤 `proj/`에 변경이 없다 | 편집이 `.claude/worktrees/<이름>/`에 남음 | `worktrees.txt`로 위치 확인. 메인이 최종 작업 폴더로 변경을 통합했는지 확인 |
| `git worktree add` 실패 | 이전 실행 잔존 또는 Git 오류 | `stderr`를 확인하고 새 실행 이름으로 재시도. 보존할 기록을 먼저 확인 |
