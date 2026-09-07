# SOURCES

실습이 기대는 사실과 출처입니다. 도구 동작의 1차 출처는 가이드 [`SOURCES.md`](../../guides/agent-delegation/SOURCES.md)에 있고, 여기에는 실습 고유 항목만 둡니다.

## 1차 자료

| 자료 | 무엇을 확인했나 | 쓰인 단계 |
| --- | --- | --- |
| Claude Code CLI `claude -p --output-format stream-json --verbose` | `result` 이벤트의 `usage`는 메인 대화만, `modelUsage`는 subagent를 포함한 전체. assistant 메시지별 `usage`는 content block마다 같은 스냅샷이 반복되므로 합산하지 않음. `session_id`로 `~/.claude/projects/<경로 slug>/<세션>/subagents/`에서 subagent transcript를 찾음 | 01~04 |
| Claude Code CLI 플래그 | `--disallowedTools Agent`(위임 금지), `--continue`(같은 폴더의 직전 세션 이어 가기), `--max-budget-usd` | 01·04 |
| Codex CLI `codex exec --json` | `thread.started`·`item.completed`(`agent_message`·`command_execution`·`collab_tool_call`)·`turn.completed`(`usage`). stdin이 열려 있으면 `Reading additional input from stdin...`으로 대기 | 01~04 |
| Codex 세션 rollout (`~/.codex/sessions/<날짜>/rollout-*.jsonl`) | 부모에 `spawn_agent`·`wait_agent` 호출, 자식에 `parent_thread_id`·`agent_nickname`, 스레드별 `token_count`. `spawn_agent`의 `message`는 암호화돼 본문을 읽을 수 없음, `task_name`·`fork_turns`는 읽을 수 있음 | 02·03 |
| Codex CLI `codex exec resume --last` | 직전 스레드를 이어 비대화형으로 한 턴 더 실행 | 04 |
| git worktree | `git worktree add ../wt-x -b task-x`, 같은 함수를 두 branch에서 고친 뒤 merge하면 content conflict | 03 |

## 2차 자료

| 자료 | 무엇을 확인했나 | 쓰인 단계 |
| --- | --- | --- |
| 이 저장소 — 평가와 관측 실습 | 골든셋으로 위치 일치·골든셋 밖 지적을 기계 판정하는 설계 | 채점기 |
| 이 저장소 — [지시문 예산 실습](../../labs/instruction-budget/README.md) | 두 도구를 새 프로세스로 반복 실행하고 결과를 TSV로 모으는 방식 | 스크립트 |

## 확인하지 못한 것

- 두 도구의 토큰 단위와 캐시 회계가 다르므로 도구 간 토큰 비교는 하지 않았습니다.
- Codex `spawn_agent`가 기본적으로 대화 이력을 넘기는지(`fork_turns`의 기본값)는 문서에서 확인하지 못했습니다.
