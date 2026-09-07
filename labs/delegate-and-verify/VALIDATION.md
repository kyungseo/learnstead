# VALIDATION

## 작성 환경

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-09-06 |
| OS · Python | macOS(Apple M4 Pro 24GB), Python 3.14 (표준 라이브러리만) |
| Claude Code | 2.1.263, s01·s02·s04는 claude-fable-5-1, s02-delegate-explicit도 Fable 5.1, s03·s04-cross-review는 Opus 5(`CLAUDE_MODEL=opus`, subagent는 메인이 고른 Sonnet 5로 실행됨), `claude -p --output-format stream-json --verbose --max-budget-usd 3`, `--disallowedTools Agent`(직접 시나리오), 프로젝트 `.claude/agents/` |
| Codex CLI | 0.153.4, `codex exec --json --sandbox workspace-write|read-only -C <실행 폴더> </dev/null`, 프로젝트 `.codex/agents/`. 모델은 지정하지 않아 계정 기본값이 쓰였고 rollout의 `turn_context`로 확인한 실제 값은 **`gpt-6-astra`·reasoning `medium`**(전 시나리오), 단 `s01-task-direct` 3회만 `gpt-5.6-sol`·`high`(실행 사이에 계정 기본값이 바뀐 것으로 보임). 같은 조건으로 돌리려면 `CODEX_MODEL=gpt-6-astra CODEX_EFFORT=medium` |
| git | worktree 시나리오는 `git worktree add ../wt-x -b task-x` |

각 시나리오를 도구당 3회 실행했습니다. 표본이 작으므로 중앙값과 회차별 값을 함께 적습니다.

## 실행 결과 요약

`python3 scripts/summarize.py runs/main --md` 기존 실행의 요약(2026-09-07에 아래 정정 반영. 중앙값, 적중·골든셋 밖 지적·테스트는 회차별. 이어 가기 시나리오의 메인 입력량·총 경과 시간은 검토 턴만). Claude Code의 s01·s02·s04는 Fable 5.1, s03과 s04-cross-review는 Opus 5. Codex 토큰의 `input`은 캐시 포함 총량이라 Claude Code의 값과 직접 비교하지 않습니다.

| 도구 | 시나리오 | n | 메인 컨텍스트 끝 | 메인 입력 누적 | 위임 입력 누적 | 출력 | 총 경과 시간(초) | 위치 일치 | 골든셋 밖 지적 | 골든셋 무결함 파일 지적 | 테스트 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude | s01-review-direct | 3 | 25,143 | 69,457 | 0 | 722 | 17.1 | 3/3/3 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s01-task-direct | 3 | 24,225 | 69,010 | 0 | 1,721 | 34.1 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s02-delegate-explicit | 3 | 25,627 | 74,177 | 42,765 | 4,507 | 76.7 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s02-delegate-history | 3 | 26,262 | 74,234 | 41,143 | 4,029 | 73.8 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s02-review-delegate | 3 | 24,441 | 48,022 | 28,757 | 1,950 | 32.6 | 3/3/3 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s03-parallel | 3 | 35,155 | 73,985 | 373,573 | 15,695 | 150.1 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s03-samefile | 3 | 30,812 | 152,191 | 258,334 | 15,978 | 170.4 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s03-samefile-worktree | 3 | 33,699 | 98,492 | 494,768 | 17,992 | 210.9 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s03-sequential | 3 | 35,418 | 234,678 | 260,755 | 16,278 | 256.3 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s04-cross-review | 3 | 25,150 | 115,968 | 0 | 1,619 | 30.6 | 0/0/0 | 1/1/1 | 0/0/0 | PASS/PASS/PASS |
| claude | s04-fresh-review | 3 | 23,583 | 45,350 | 0 | 561 | 12.2 | 0/0/0 | 1/1/1 | 0/0/0 | PASS/PASS/PASS |
| claude | s04-gaps-direct | 3 | 25,708 | 72,433 | 0 | 3,650 | 68.2 | 3/3/3 | 22/28/22 | 8/9/10 | PASS/PASS/PASS |
| claude | s04-writer-only | 3 | 25,620 | 94,658 | 0 | 2,374 | 36.0 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| claude | s04-writer-selfreview | 3 | 29,754 | 30,075 | 0 | 384 | 6.3 | 0/0/0 | 1/2/1 | 0/0/0 | PASS/PASS/PASS |
| codex | s01-review-direct | 3 | 25,291 | 119,121 | 0 | 604 | 111.3 | 3/3/3 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s01-task-direct | 3 | 25,527 | 194,516 | 0 | 2,282 | 86.7 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s02-delegate-explicit | 3 | 24,290 | 143,660 | 124,967 | 1,359 | 72.9 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s02-delegate-history | 3 | 26,316 | 249,412 | 136,122 | 1,766 | 123.5 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s02-review-delegate | 3 | 23,439 | 115,646 | 130,481 | 1,026 | 80.1 | 3/3/3 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s03-parallel | 3 | 24,646 | 282,832 | 398,951 | 3,849 | 223.2 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/FAIL |
| codex | s03-samefile | 3 | 28,027 | 388,044 | 408,049 | 4,044 | 193.5 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s03-samefile-worktree | 3 | — | — | — | — | 72.1¹ | — | — | — | 통합 미완료 3/3² |
| codex | s03-sequential | 3 | 28,651 | 462,757 | 455,401 | 4,713 | 343.5 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s04-cross-review | 3 | 23,715 | 46,474 | 0 | 143 | 16.0 | 0/0/0 | 1/1/1 | 0/0/0 | PASS/PASS/PASS |
| codex | s04-fresh-review | 3 | 22,234 | 43,479 | 0 | 194 | 64.9 | 0/0/0 | 1/1/1 | 0/0/0 | PASS/PASS/PASS |
| codex | s04-gaps-direct | 3 | 27,522 | 127,268 | 0 | 2,297 | 105.8 | 3/3/3 | 21/16/16 | 6/5/5 | PASS/PASS/PASS |
| codex | s04-writer-only | 3 | 23,726 | 90,619 | 0 | 873 | 106.3 | 0/0/0 | 0/0/0 | 0/0/0 | PASS/PASS/PASS |
| codex | s04-writer-selfreview | 3 | 27,564 | 54,375 | 0 | 122 | 13.1 | 0/0/0 | 1/1/1 | 0/0/0 | PASS/PASS/PASS |

`s03-samefile-worktree`의 Codex 행은 `run-codex-worktrees.sh`가 스트림 두 개(`stream-x`·`stream-y`)를 남겨 채점기가 토큰을 합산하지 않습니다. ¹ 72.1초는 두 편집 프로세스 종료까지의 시간으로, 충돌 해결·최종 통합 시간을 포함하지 않습니다. ² 기존 `PASS`는 통합 실패 뒤 메인 작업 폴더에서 실행한 테스트이며 두 기능의 통합 성공을 뜻하지 않습니다. `merge.txt`에서는 content conflict 3/3을 확인했습니다. Codex `s01-review-direct` 총 경과 시간 111초는 재실행 값이며 첫 배치에서는 18.6·22.9·28.5초였습니다(재실행 회차의 stderr에 모델 목록 갱신 시간 초과 기록).

## 관측 노트

- **위임(02):** 메인 컨텍스트 끝 크기는 Claude Code 25,143 → 24,441(−3%), Codex 25,291 → 23,439(−7%). 이 조건에서는 메인 컨텍스트 감소 폭이 작았다. 차이를 시스템 프롬프트·지시문·왕복 비용별로 분리해 측정하지는 않았다. 위임 쪽 누적 입력은 Claude 28,757, Codex 130,481.
- **이력 의존 위임(02):** Claude Code는 지시대로 한 문장만 넘겼고 subagent는 추측 없이 되물었다(1·2회차 미수정). 3회차는 subagent가 후보 세 개를 보고하자 메인이 `SendMessage`로 재개하며 파일·함수·검사 명령을 보태 수정했다. Codex는 3회 모두 수정했다. 3회차 호출에서 `task_name: fix_month_end`와 `fork_turns: "all"`을 확인했으나, 세 회차 모두 같은 이력 전달 설정이었다고 단정하지 않는다. Codex rollout의 `spawn_agent` 메시지 본문은 암호화돼 읽을 수 없다.
- **자기완결 대조군(02, `s02-delegate-explicit`):** 두 도구 3/3 수정. Claude Code(Fable)의 자기완결 조건 중앙값은 메인 74,177·위임 42,765·76.7초였다. 이력 의존 조건은 미수정 회차가 포함돼 같은 결과의 비용 비교가 아니며, Codex는 메인 14.4만·위임 12.5만·73초로 이력 의존(24.9만·13.6만·124초)보다 메인 토큰 42%·시간 41% 적었다.
- **검토자 컨텍스트(04):** 작성 세션 이어 가기·새 세션·교차 검토가 두 도구 모두 3/3 규격 위반을 잡았다. 작성 단계에서는 어느 도구도 지시와 README의 충돌을 먼저 말하지 않았다. 검토 턴만 세면 Claude 이어 가기 30,075·6.3초 vs 새 세션 45,350·12.2초, Codex 이어 가기 54,375·13.1초 vs 새 스레드 43,479·64.9초(프로세스 시작 포함). 검출 결과는 같았다. Claude는 이어 가기가 입력·시간 모두 적었고, Codex는 새 스레드의 입력이 적고 이어 가기의 시간이 짧았다.
- **"모든 gap"(04):** 적중은 3/3 그대로, 골든셋 밖 지적 Claude 22·28·22 / Codex 21·16·16, 결함 없는 `store.py`·`cli.py` 지적 8·9·10 / 6·5·5. 출력 토큰은 결함만 프롬프트의 4~5배.
- **Codex 병렬·같은 파일(03, 첫 배치):** 병렬 3 총 경과 시간 218·223·232초 vs 순차 425·344·277초. 병렬 3회차는 subagent C가 규격 기준으로 쓴 `--json` 테스트가 심어 둔 부호 결함을 드러내 FAIL. 같은 파일 과제는 격리 없이도 `title`·`top` 두 기능이 최종 파일에 모두 남고 테스트 통과(3/3). worktree 둘 + `codex exec` 둘은 `report.py` content conflict 3/3.
- **Claude Code 병렬·같은 파일(03, Opus 5):** 동시 3 총 경과 시간 150·154·146초 vs 순차 242·272·256초. subagent transcript 시각으로 병렬 구간 겹침(9~13초 간격 시작)과 순차의 비겹침을 확인. 같은 파일 격리 없음은 3회 모두 두 기능 보존·테스트 통과. `isolation: worktree`는 결과가 `.claude/worktrees/` 아래 두 branch에 남았고 메인이 통합한 것은 3회 중 1회(16개 테스트 통과), 2회는 "합쳐지지 않았다"고 보고하고 종료.
- **Opus 5 메인의 subagent 모델:** `--model opus`로 돌린 s03에서 `modelUsage`에 `claude-sonnet-5`가 함께 잡혔다. implementer 정의에 `model`이 없어 메인이 호출 시 Sonnet을 골랐다. 위임 토큰은 그 모델의 값이다.

## 채택한 값의 원천

- 표와 본문의 값은 `runs/main/` 아래 **현재 남아 있는 실행에서** `summarize.py`가 계산한 중앙값이며, `runs/main-scores.tsv`·`runs/main-summary.md`는 최종 상태에서 다시 생성했습니다(한도로 비었던 실행은 재실행으로 덮어썼고, `summarize.py`는 입력 0·5초 미만 실행을 제외합니다).
- 예외 하나: Codex `s01-review-direct`의 총 경과 시간은 첫 배치 값(18.6·22.9·28.5초, 중앙값 22.9초)을 본문에 썼습니다. 첫 배치 실행은 runner 결함으로 채점 파일만 빠졌고, 재실행(현재 `runs/main`에 남은 것)은 stderr에 모델 목록 갱신 시간 초과가 기록된 채 110초 안팎이라 시간만 부풀었습니다. 토큰·적중은 두 배치가 같은 방향입니다.
- 이어 가기 검토 시나리오의 `main_*`·`wall_s`는 검토 턴만의 값입니다. 첫 배치에서 검토 턴 시간을 따로 기록하지 않아 Claude Code는 `result.duration_ms`, Codex는 rollout의 마지막 사용자 턴 이후 경과로 소급 계산해 `wall_followup_seconds.txt`에 적었습니다. 이후 runner는 이 파일을 직접 기록합니다.

## 재실행 기록

- Claude Code는 첫 배치 도중 구독 세션 한도("You've hit your session limit")에 걸려 `s02-review-delegate` 2회차부터 빈 결과가 됐습니다. 한도 해제 뒤 s02·s04를 Fable로 재실행했고, `s03-parallel` 1회차 뒤 다시 한도에 걸려 **s03 4종과 Codex→Claude 교차 검토는 Opus 5(`--model opus`)로** 다시 쟀습니다. 시나리오 블록 안에서는 같은 모델을 썼고, 표에 모델을 병기합니다.
- Codex `s01-review-direct`는 runner의 `pipefail` 결함(자식 rollout이 없을 때 `grep -l`이 1을 반환)으로 첫 배치에서 채점 파일이 빠져 재실행했습니다. 실행 자체는 첫 배치에서도 정상이었습니다.
- Codex worktree 시나리오 첫 배치는 fixture에 `.gitignore`가 없어 `__pycache__`가 함께 커밋돼 merge 잡음이 섞였습니다. `report.py` content conflict는 3회 모두 그와 무관하게 발생했습니다. 이후 `.gitignore`를 추가했습니다.

## 2026-09-07 — 검토 후 수정 검증

- Claude 자기완결 조건의 메인 입력 중앙값을 원본 세 값(48,967·74,252·74,177)으로 다시 계산해 74,177로 정정했습니다. 기존 실측을 재사용했으며 모델 실험을 새로 실행하지 않았습니다.
- runner는 기존 결과 덮어쓰기 거부, 입력 사전 검사, 프로세스 종료 코드 기록, 실패 시 후속 턴 중단, 단일 도구 배치 실행을 지원합니다.
- worktree runner는 워커별 검사·통합 상태·편집/통합 시도/전체 시간을 나눠 기록합니다. 통합 실패 뒤 최종 검사는 `SKIPPED_NOT_INTEGRATED`이며, merge 성공 뒤에도 요청 기능 보존은 사람이 확인합니다.
- `python3 -m unittest discover -s scripts -p 'test_*.py' -v`: 고정 출력을 내는 모형 CLI와 임시 Git 저장소로 11개 검사 통과. 실제 모델 성능·도구 버전 호환성의 검증 근거는 아닙니다.

## 정적 검사

- GFM 파서로 Markdown 42개를 렌더링한 뒤 코드 밖에 남은 리터럴 `**` 0건. 2026-09-07
- 상대 링크 0 깨짐(hero 제외)·후행 공백 0·절대 경로 0·내부 추적 식별자 0, `python3 -m py_compile scripts/*.py`·`bash -n scripts/*.sh` 통과, `git diff --check` 통과. 2026-09-07

## 한계

- 과제 하나(가계부 CLI, 파일 5개, 결함 3개)와 도구당 3회. 추세가 아니라 방향입니다.
- 도구 간 토큰 비교는 하지 않습니다. Claude Code는 캐시 읽기·쓰기를 포함한 입력 총량, Codex는 `input_tokens`(캐시 포함)를 썼습니다.
- 채점기의 "골든셋 밖 지적"(`fp`)은 지적의 타당성을 판정하지 않습니다. 심어 둔 결함 세 개 밖의 지적을 전부 세며, 같은 함수를 다른 이유로 지적해도 적중으로 셉니다. "오탐"으로 읽지 마세요.
- 이어 가기 검토와 새 컨텍스트 검토의 비교는 결함 하나·3회입니다. 검출 결과는 같았지만 입력량과 시간은 달랐으며, 이 결과만으로 새 컨텍스트의 일반적 우열을 정할 수 없습니다.
- 총 경과 시간에는 API 응답을 기다리는 시간과 네트워크 지연도 포함됩니다. Codex는 실행 초기에 모델 목록 갱신 시간 초과가 stderr에 기록된 회차가 있어 시간이 부풀었을 수 있습니다.
- Claude Code 대화형 세션의 fork 모드·백그라운드 subagent, agent teams, Codex 데스크톱 앱 worktree는 실행하지 않았습니다.

## 2026-09-07 Hero 추가 후 최종 검사

- 내장 imagegen으로 hero를 생성하고 한글 제목·구도를 확인한 뒤 WebP로 저장했습니다(1672×941, cwebp 품질 90).
- 기존 hero 누락 4건을 해소했습니다. 두 팩 공개 레이아웃 배치 후 `python3 tools/validate.py --public` 최종 결과: PASS. 앞의 누락·FAIL 기록은 이미지 추가 전 검사입니다.

## 2026-09-07 — 문장·용어 보완 확인

- 두 가이드와 두 실습의 독자용 본문 28개를 검토·수정했습니다. 명령·코드 예제·실제 출력 블록과 표의 숫자는 보존했습니다. Mermaid의 표시 문구와 독자용 기록 양식은 설명에 맞춰 수정했습니다.
- GFM 렌더 후 코드 밖에 남은 리터럴 `**` 0건. 공개 레이아웃의 링크·구조 검사(`python3 tools/validate.py --public`)와 `git diff --check` 통과. 원본과 공개용 작업본은 상대 링크 매핑을 제외하고 일치합니다.
- 변경된 SVG 5개는 소스 검사 0 error·0 warning, Chrome 152.0.7977.76의 2× 렌더와 시각 확인을 통과했습니다. 렌더러: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.
- 문서와 도식 설명을 보완한 검증입니다. 모델 실험을 다시 실행하지 않았으며, 실제 초심자를 대상으로 이해도를 측정한 결과는 아닙니다.
