# 08. 용어집

> 이전 ← [`07-when-not-to-split.md`](07-when-not-to-split.md) · 처음 → [`README.md`](README.md)

등장 순서대로 배열했습니다. 앞선 가이드에 정의가 있는 용어는 그 정의를 따르고 링크만 둡니다.

| 용어 | 뜻 | 정의한 곳 |
| --- | --- | --- |
| Agent loop | 한 번의 실행 안에서 모델과 도구가 결과를 주고받는 도구 호출 루프 | [agent-skills 00](../../guides/agent-skills/00-how-an-agent-works.md) |
| harness | 정책·완료 조건·작업 순서·검증·기록을 묶는 운영 장치 | [agent-skills 00 §3](../../guides/agent-skills/00-how-an-agent-works.md). [바이브 코딩 가이드 10](../../guides/vibe-coding-practice/10-glossary.md)의 "계획·규칙·검사 도구를 묶는 안전장치"와 같은 뜻 |
| subagent (서브에이전트) | 별도 실행 문맥에서 정해진 작업을 맡고 결과를 돌려주는 에이전트. 초기 이력·도구·권한의 상속은 구성에 따라 다름 | [agent-skills 09](../../guides/agent-skills/09-glossary.md) · [context-engineering 08](../../guides/context-engineering/08-glossary.md) |
| 컨텍스트 격리 | 각 실행에 제공할 입력과 이후 기록을 분리하는 것. 초기 이력을 복제해도 이후 작업 기록은 분리될 수 있음 | [코드 레벨 가이드 03](../../guides/agent-orchestration/03-context-isolation.md) |
| fork | 이 문서에서는 Claude Code의 이력 상속 subagent. 초기 이력·도구·모델을 물려받고 이후 작업 기록은 메인과 분리됨. 다른 도구의 fork와는 세부 동작을 별도 확인 | 이 가이드 03 |
| worktree | 같은 저장소의 별도 작업 폴더. branch 하나씩 | [Git 가이드 07](../../guides/git-for-vibe-coders/07-worktrees.md) |
| `isolation: worktree` | Claude Code subagent를 임시 worktree에서 돌리는 frontmatter 필드 | 이 가이드 04 |
| base branch (`worktree.baseRef`) | subagent worktree가 갈라져 나오는 커밋. 기본 `fresh` = 원격 default branch, `head` = 현재 HEAD(미푸시 커밋 포함, 미커밋 변경 제외) | 이 가이드 04 |
| agent teams | Claude Code의 실험 기능. lead 세션 + 독립 teammate, 공유 task list와 mailbox | 이 가이드 02 |
| dynamic workflow | Claude Code에서 subagent 여러 개를 JS 스크립트로 조율하는 기능. `ultracode`로 옵트인 | 이 가이드 02 |
| cross-session messaging | Claude Code 세션끼리 `SendMessage`로 텍스트를 주고받는 기능. 승인 대행 불가 | 이 가이드 02·06 |
| `spawn_agent` · `wait_agent` | Codex의 subagent 생성·대기 도구. `send_input`·`resume_agent`·`close_agent`와 한 묶음 | 이 가이드 03 |
| rollout | Codex가 스레드마다 남기는 세션 기록(`~/.codex/sessions/`). 자식은 `parent_thread_id`를 가짐 | 이 가이드 06 |
| plan mode | 탐색·계획을 편집과 분리하는 모드. 승인 주체와 전환 방식은 도구·구성에 따라 확인 | 이 가이드 05 |
| Writer/Reviewer | 작성과 검토를 다른 세션(컨텍스트)에 두는 구성 | 이 가이드 05 |
| 위임 프롬프트 결핍 | 이력을 못 받는 subagent(Claude Code 비-fork)에 이력에 기대는 프롬프트를 넘겨 생기는 실패. 이력을 넘기는 도구에서도 전달 범위와 비용을 확인해야 한다 | 이 가이드 06 |
| 조용한 손실 | 워커의 올바른 결과가 취합 과정에서 누락되거나 다른 의미로 바뀌는 실패 | [코드 레벨 가이드 04](../../guides/agent-orchestration/04-failure-modes.md) |
| 검토 과잉 | "빠짐없이 찾아라"가 낸 규격 밖 지적을 전부 반영해 코드가 불어나는 실패 | 이 가이드 05·06 |
| 위치 일치 (`hits`) | 골든셋의 파일·함수와 일치하는 지적 수. 결함 설명의 정확성은 판정하지 않음 | 실습 01·04 |
| 골든셋 밖 지적 (`fp`) | 심어 둔 결함 위치 밖의 지적 수. 실제 오류라는 뜻의 오탐과 다름 | 실습 01·04 |
| 골든셋 | 채점 기준이 되는 정답 목록. 이 실습에서는 심어 둔 결함 세 개 | 평가 가이드 |
| 기준선 | 작업 분담 전 한 세션이 직접 처리한 토큰 사용량·시간·결함 위치 일치 수 | 이 가이드 01 |

## 혼동하기 쉬운 쌍

| 쌍 | 구분 |
| --- | --- |
| non-fork subagent vs fork | 새 입력으로 시작 ↔ 초기 이력을 상속. 둘 다 이후 작업 기록을 메인과 분리할 수 있음 |
| 메인 컨텍스트 감소 vs 누적 토큰 감소 | 한 요청의 입력 크기 ↔ 여러 요청에 실린 입력량 합계. 청구 금액은 캐시·단가도 확인 |
| 동시에 실행했다 vs 빨리 완료했다 | 실행 구간의 겹침 ↔ 순차 대비 전체 시간 감소. 서로 따로 확인 |
| worktree vs 담당 파일 범위(파일 소유권) | 작업 폴더 분리 ↔ 각 작업의 쓰기 범위 지정. 둘 다 통합 검증은 필요 |
| 검토 vs 검사 | 모델이 읽고 판단 ↔ 코드가 돌리고 통과/실패. 검사가 먼저 |
| plan mode vs 읽기 전용 subagent | 계획 단계의 편집 제한 ↔ 위임받은 작업의 권한 제한. 사람의 승인 지점은 별도 지정 |
