# SOURCES

핵심 주장의 1차 출처와 확인일입니다. 도구 사실은 전부 공식 문서를 2026-09-06에 확인했고, 실측은 실습 [`VALIDATION.md`](../../labs/delegate-and-verify/VALIDATION.md)에 있습니다.

## 1차 자료 — Claude Code (2.1.263 기준, 2026-09-06 확인)

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| Claude Code Docs — Subagents (`code.claude.com/docs/en/sub-agents`) | frontmatter 필드(`tools`·`disallowedTools`·`model`·`permissionMode`·`isolation`·`memory` 등), 내장 Explore·Plan·general-purpose, 비-fork subagent가 대화 이력·auto memory를 받지 않음, 깊이 3·동시 20 한도, `SendMessage` 재개, 출력 스캔 | 02·03·06 |
| Claude Code Docs — Worktrees (`/docs/en/worktrees`) | `--worktree`, `.claude/worktrees/`·`worktree-<이름>`, base = 원격 default branch(`worktree.baseRef`), 격리 강제 4종, 정리·잠금·sweep, `.worktreeinclude`, `isolation: worktree` | 04 |
| Claude Code Docs — Run agents in parallel (`/docs/en/agents`) | 네 층 비교와 세 질문(누가 조정·워커 간 대화·같은 파일), `/batch` | 02·07 |
| Claude Code Docs — Agent teams (`/docs/en/agent-teams`) | 실험·`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, 공유 task list·mailbox, worktree 격리 없음, teammate plan 자동 승인, 3~5명 권장, 제한 | 02·04·05 |
| Claude Code Docs — Dynamic workflows (`/docs/en/workflows`) | `agent()`·`parallel()`·`pipeline()`, `ultracode` 옵트인, 동시 16·실행당 1,000, "누가 계획을 쥐는가" 표 | 02 |
| Claude Code Docs — Cross-session messaging (`/docs/en/cross-session-messaging`) | `ListAgents`·`SendMessage`, 수신 메시지는 승인 대행 불가·설정 변경 불가, `crossSessionInbound` | 02·06 |
| Claude Code Docs — Best practices (`/docs/en/best-practices`) | plan mode 4단계와 "diff를 한 문장으로 설명할 수 있으면 건너뛴다", Writer/Reviewer, adversarial review subagent와 과잉 설계 경고, `/goal`·Stop hook, 실패 패턴 | 05·07 |
| Claude Code Docs — Costs (`/docs/en/costs`) | agent teams 약 7배, 위임으로 verbose 출력을 subagent에 | 02·06 |
| Claude Code CLI 출력 (`claude -p --output-format json`) | `usage`(메인)와 `modelUsage`(전체)가 따로 보고됨. 실측에서 확인 | 03·실습 |

## 1차 자료 — Codex CLI (0.153.4 기준, 2026-09-06 확인)

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| Codex Docs — Subagents (`learn.chatgpt.com/docs/agent-configuration/subagents`) | `[agents]` 설정(`enabled`·`max_concurrent_threads_per_session`·`default_subagent_model`), `.codex/agents/*.toml`(`name`·`description`·`developer_instructions`·`sandbox_mode`), 내장 `default`·`worker`·`explorer`, 부모 sandbox·approval·AGENTS.md·skills 상속, 읽기 위주 권장·쓰기 병렬 신중, `/agent`, 결과 통합 반환 | 02·03·06 |
| Codex Docs — Configuration reference (`/docs/config-file/config-reference`) | `features.multi_agent`(기본 on)와 도구 `spawn_agent`·`send_input`·`resume_agent`·`wait_agent`·`close_agent`, `agents.<이름>.config_file` | 03 |
| Codex Docs — Worktrees (`/docs/environments/git-worktrees`) | 데스크톱 앱 전용, `$CODEX_HOME/worktrees`, detached HEAD, 최근 15개 보존 | 04 |
| Codex Docs — Best practices (`/guides/best-practices`) | "bounded work"를 subagent에, 한 chat = 한 작업 단위, plan 먼저, `/compact` | 05 |
| Codex CLI 출력 (`codex exec --json`, 세션 rollout) | 스트림에 `wait`만 나오고 `spawn_agent`는 rollout에만 기록됨. `spawn_agent` 메시지 본문은 rollout에서 암호화됨. `fork_turns` 인자로 이력 전달. 실측에서 확인 | 03·06·실습 |

## 2026-09-07 재확인 범위

- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents): fork의 초기 이력과 이후 별도 기록, skills 사전 적재와 도구 권한의 차이, 부모 권한 모드의 영향.
- [Claude Code Worktrees](https://code.claude.com/docs/en/worktrees): 원격 기본 브랜치와 원격이 없을 때 HEAD 기준의 차이.
- [Claude Code 병렬 실행](https://code.claude.com/docs/en/agents): 조정 형태 비교. 본 가이드에서는 이를 성숙도 단계로 해석하지 않습니다.
- [Codex Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): 정의 파일·상속·쓰기 병렬 경계.

나머지 항목의 확인일은 위 표의 2026-09-06을 유지합니다.

## 2차 자료

| 자료 | 무엇을 확인했나 | 쓰인 장 |
| --- | --- | --- |
| 이 저장소 — [Agent Skills 가이드](../../guides/agent-skills/README.md) 00·03·06·09 | Agent loop·harness·runtime 정의, subagent 행, `context: fork` | 01·03·08 |
| 이 저장소 — [Context Engineering 가이드](../../guides/context-engineering/README.md) 04·05 | 서브에이전트는 memory 미상속, 큰 읽기 위임 "6,100 읽고 420 반환" | 01·03 |
| 이 저장소 — [Git 가이드 07](../../guides/git-for-vibe-coders/07-worktrees.md) | worktree 개념·절차·"AI 세션 하나에 worktree 하나", "worktree는 충돌을 없애지 않는다" | 04 |
| 이 저장소 — [여러 AI를 엮어 일하게 하기](../../guides/agent-orchestration/README.md) | Split→Isolate→Stop, 다섯 실패 모드, 다섯 질문, "나누기는 최적화, 측정 뒤에", 평가 루프 수렴 실패 | 01·05·06·07 |
| 이 저장소 — [바이브 코딩 가이드](../../guides/vibe-coding-practice/README.md) 04·05 | "한 요청 = 한 가지 변화", AI에게 시킬 수 없는 확인 | 04·05 |

## 확인하지 못한 것

- Codex subagent의 중첩 깊이 한도, 대화 이력 상속의 기본값(문서에 명시 없음. 실측에서 `fork_turns: "all"`이 관측됐으나 기본 동작인지는 확인하지 못함).
- agent teams·dynamic workflows·agent view의 실제 동작. 문서로만 확인했고 실행하지 않았습니다.
- Claude Code 데스크톱 앱과 Codex 데스크톱 앱의 worktree 동작. CLI만 실측했습니다.
