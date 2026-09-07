# VALIDATION

## 작성 환경

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-09-06 |
| OS · 하드웨어 | macOS, Apple M4 Pro 24GB |
| Claude Code | 2.1.263, 모델 claude-fable-5-1(구독 기본), `claude -p --output-format stream-json`, 기본 권한 모드, subagent는 프로젝트 `.claude/agents/`에 정의 |
| Codex CLI | 0.153.4, 계정 기본 모델, `codex exec --json --sandbox workspace-write` 또는 `read-only`, subagent는 프로젝트 `.codex/agents/`에 정의, `[agents]` 설정 기본값 |
| 문서 확인 | Claude Code·Codex 공식 문서를 2026-09-06에 확인. 항목별 출처는 [`SOURCES.md`](SOURCES.md) |

## 실행 검증 목록

가이드의 실측 표는 실습 [`VALIDATION.md`](../../labs/delegate-and-verify/VALIDATION.md)의 실행 결과에서 옮겼습니다. 여기서는 가이드 본문의 주장 단위로 근거를 연결합니다.

| # | 주장 (장) | 근거 | 결과 |
| --- | --- | --- | --- |
| 1 | 읽을 것이 작을 때 위임은 메인 컨텍스트를 거의 줄이지 않고 전체 토큰을 늘린다 (03 §4) | 실습 02 `s02-review-delegate` vs `s01-review-direct`, 두 도구 3회 | 확인. 메인 컨텍스트 끝 크기 Claude −3%(25,143→24,441)·Codex −7%(25,291→23,439), 위임 누적 2.9만·13만 추가. 적중은 3/3 유지 |
| 2 | 이력이 빠진 위임에 도구마다 다르게 대응한다 (03 §5) | 실습 02 `s02-delegate-history` | 확인. Claude Code는 한 문장 그대로 전달 → subagent가 추측 없이 되물음(2회 미수정, 1회는 메인이 `SendMessage`로 재개해 수정). Codex는 3/3 수정했고 3회차에서 `fork_turns: "all"` 확인, 프롬프트 본문은 암호화. 자기완결 대조군(`s02-delegate-explicit`)은 두 도구 3/3, Claude 입력·시간 중앙값 유사(미수정 회차 포함)·Codex 메인 토큰 −42%·시간 −41% |
| 3 | 동시 실행 여부와 순차 대비 시간 절감은 따로 확인한다 (04 §3) | 실습 03 `s03-parallel` vs `s03-sequential`, Claude Code는 Opus 5 | 확인. Claude 150초 vs 256초, Codex 223초 vs 344초. subagent transcript 시각으로 구간 겹침 확인(병렬 9~13초 간격 시작, 순차는 겹침 없음) |
| 4 | worktree는 덮어쓰기를 막고 merge를 미룬다 (04 §4) | 실습 03 `s03-samefile` vs `s03-samefile-worktree` | 부분 확인. 격리 없이도 두 도구 6회 모두 두 기능 보존(덮어쓰기 미관측). Claude worktree는 3회 중 1회만 메인이 통합, Codex worktree 둘은 merge 충돌 3/3. "덮어쓰기를 막는다"는 이 규모에서 검증할 사건이 없었고, "merge를 미룬다"는 확인 |
| 5 | 검토자의 컨텍스트에 따라 규격 위반 적중이 달라진다 (05 §3) | 실습 04 `s04-writer-selfreview`·`s04-fresh-review`·`s04-cross-review` | **이번 조건(결함 하나·3회)에서는 관측되지 않음.** 이어 가기·새 세션·교차(양방향) 모두 3/3 적중. Claude는 이어 가기의 입력·시간이 모두 적음. Codex는 새 세션 입력이 적지만 이어 가기가 빠름(54,375·13.1초 vs 43,479·64.9초). 가이드는 이 범위로 서술 |
| 6 | "빠짐없이 찾아라"는 골든셋 밖 지적을 늘린다 (05 §4) | 실습 04 `s04-gaps-direct` vs `s01-review-direct` | 확인. 적중 3/3 동일, 골든셋 밖 지적 Claude 22·28·22 / Codex 21·16·16, 결함 없는 파일 지적 8·9·10 / 6·5·5. 지적의 타당성은 판정하지 않음 |
| 7 | Codex `exec --json` 스트림에 `spawn_agent`가 나오지 않는다 (06 §2) | Spike와 실습 02 rollout 대조 | 확인. `wait`만 `collab_tool_call`로 나오고 `spawn_agent`는 rollout에만 |
| 8 | Claude Code `result.usage`는 메인만, `modelUsage`는 전체 (03·실습) | Explore를 다른 모델로 돌린 spike에서 두 값이 분리됨 | 확인 |

## 2026-09-07 검토

- 첫 실행 경로·위임 예시·선택 기준을 보강하고 형태/격리 축, 검토 컨텍스트, 비용 해석을 구분했습니다.
- 기존 실측의 중앙값 오류와 통합 미완료 표시를 바로잡았습니다. 모델 실험은 새로 실행하지 않았습니다.
- 공식 문서 재확인 범위는 `SOURCES.md`에 기록했습니다. runner 수정 검증은 실습 `VALIDATION.md`를 따릅니다.

## 정적 검사

- GFM 파서로 Markdown 42개를 렌더링한 뒤 코드 밖에 남은 리터럴 `**` 0건. 2026-09-07
- 상대 링크 0 깨짐(hero 4장은 발행 단계 제작으로 제외)·후행 공백 0·절대 경로 0·내부 추적 식별자 0·`git diff --check` 통과. 2026-09-07
- 공개 저장소 레이아웃으로 임시 배치해 링크 매핑을 적용한 뒤 저장소 검증 스크립트(`--public`)를 예행: hero 항목 외 통과. 2026-09-07
- SVG 4종 lint 0 error·0 warning, Chromium 2배 PNG 렌더로 겹침·잘림·CJK 대체 글꼴 육안 확인. 2026-09-07

## 한계

- 과제가 하나(파일 5개·결함 3개)이고 도구당 3회라 방향만 읽습니다. 다른 규모·다른 저장소로 일반화하지 않습니다.
- 두 도구의 토큰 단위·캐시 회계가 달라 도구 간 토큰 비교는 하지 않았습니다. 같은 도구 안의 구성 간 비교만 합니다.
- Claude Code는 구독 사용량 한도로 실행이 한 번 중단돼 한도 해제 뒤 재실행했습니다. 재실행 회차는 실습 VALIDATION에 표시합니다.
- agent teams·dynamic workflows·agent view·데스크톱 앱의 worktree는 실행하지 않았습니다.
- 비대화형(`-p`·`exec`)에서만 실측했습니다. 대화형 세션의 fork 모드·백그라운드 subagent 동작은 문서 확인에 그칩니다.
- Claude Code는 시나리오 블록에 따라 Fable 5.1과 Opus 5를, Codex는 계정 기본값(`gpt-6-astra`/`medium`, 과제 A 직접 구현만 `gpt-5.6-sol`/`high`)을 썼습니다. 모델이 다른 블록끼리는 비교하지 않았습니다. 상세는 실습 VALIDATION 작성 환경.

## 2026-09-07 Hero 추가 후 최종 검사

- 내장 imagegen으로 hero를 생성하고 한글 제목·구도를 확인한 뒤 WebP로 저장했습니다(1672×941, cwebp 품질 90).
- 기존 hero 누락 4건을 해소했습니다. 두 팩 공개 레이아웃 배치 후 `python3 tools/validate.py --public` 최종 결과: PASS. 앞의 누락·FAIL 기록은 이미지 추가 전 검사입니다.
