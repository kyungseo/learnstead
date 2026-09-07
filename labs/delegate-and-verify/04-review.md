# 04. 검토 — 누가 보느냐, 무엇을 찾으라 하느냐

> 이전 ← [`03-parallel.md`](03-parallel.md) · 다음 → [`05-decide.md`](05-decide.md)

## 목표

코드를 작성한 세션, 같은 도구의 새 세션, 다른 도구가 각각 코드를 검토했을 때 규격 위반을 발견하는지 비교합니다. 또한 "결함만" 찾으라는 요청과 "모든 개선점(gap)"을 찾으라는 요청이 정답 목록(골든셋) 밖의 지적을 얼마나 만드는지 측정합니다. 지적의 타당성은 별도로 확인합니다. 이 단계에서 `expected/golden.json`을 열어도 됩니다.

## 1. 돌리기

```bash
./scripts/batch.sh main 3 s04-gaps-direct s04-writer-selfreview s04-writer-only s04-fresh-review s04-cross-review
```

| 시나리오 | 무엇을 | 검토자의 컨텍스트 |
| --- | --- | --- |
| `s04-gaps-direct` | `review-gaps.md` — "개선이 필요한 모든 지점" (01의 `review-correctness`와 대조) | 직접 |
| `s04-writer-selfreview` | `writer-misled-fix.md`(환불을 지출처럼 **음수로** 저장하라는 규격 위반 지시)로 고친 뒤, 같은 세션이 `self-review.md` | 작성 세션 (`--continue` · `resume`) |
| `s04-writer-only` | 위와 같은 작성만 | — |
| `s04-fresh-review` | `s04-writer-only`의 작업 트리를 **같은 도구의 새 프로세스가** `fresh-review-diff.md`로 검토 | 새 컨텍스트 |
| `s04-cross-review` | `s04-writer-only`의 작업 트리를 **다른 도구가** 검토 | 새 컨텍스트·다른 모델 |

README 규격 위반의 정답은 하나입니다: `parse_rows`(또는 `parse_amount`)가 memo에 "환불"이 있으면 음수로 바꾸는 것이 README의 "환불·수입은 양수"와 어긋난다.

## 2. 채점

```bash
python3 scripts/score.py --tsv runs/main/*-s04-*
```

`s04-*-review` 계열에서는 미리 심어 둔 결함 목록 대신 **검토 답변에 `parse_rows`·`parse_amount`·"환불"이 지적됐는가를** 봅니다. `answer_excerpt`를 직접 읽습니다. 이어 가기 시나리오의 `main_*` 열은 검토 턴(`stream-followup`)만의 값이고 작성 턴은 `writer_*`로 따로 나옵니다. `s04-gaps-direct`는 골든셋 대조가 그대로 적용되며 `fp` 열은 "골든셋 밖 지적"입니다.

## 3. 기록

| 도구 | 검토자 | README 규격 위반 적중 (3회 중) | 검토 턴 입력·시간 |
| --- | --- | --- | --- |
| Claude Code | 작성 세션 자신 | | |
| Claude Code | 새 세션 | | |
| Claude Code | Codex가 작성, Claude가 검토 | | |
| Codex | 작성 스레드 자신 | | |
| Codex | 새 스레드 | | |
| Codex | Claude가 작성, Codex가 검토 | | |

| 도구 | 프롬프트 | 위치 일치/3 | 골든셋 밖 지적 | 결함 없는 파일 지적 |
| --- | --- | --- | --- | --- |
| Claude Code | 결함만(01) | | | |
| Claude Code | 모든 gap | | | |
| Codex | 결함만(01) | | | |
| Codex | 모든 gap | | | |

## 작성 환경의 실제 결과

| 도구 | 검토자 | README 규격 위반 적중 (3회 중) | 검토 턴 입력 | 검토 턴 시간 |
| --- | --- | --- | --- | --- |
| Claude Code | 작성 세션 이어 가기(검토 턴만) | 3/3 (2회차는 `apply_sign`·`parse_rows` 두 지점) | 30,075 | 6.3초 |
| Claude Code | 새 세션 | 3/3 | 45,350 | 12.2초 |
| Claude Code (Opus 5) | Codex가 작성, Claude가 검토 | 3/3 | 115,968 | 30.6초 |
| Codex | 작성 스레드 이어 가기(검토 턴만) | 3/3 | 54,375 | 13.1초 |
| Codex | 새 스레드 | 3/3 | 43,479 | 64.9초(프로세스 시작 포함) |
| Codex | Claude가 작성, Codex가 검토 | 3/3 | 46,474 | 16.0초 |

| 도구 | 프롬프트 | 위치 일치/3 | 골든셋 밖 지적 | 결함 없는 파일 지적 |
| --- | --- | --- | --- | --- |
| Claude Code | 결함만(01) | 3·3·3 | 0·0·0 | 0·0·0 |
| Claude Code | 모든 gap | 3·3·3 | 22·28·22 | 8·9·10 |
| Codex | 결함만(01) | 3·3·3 | 0·0·0 | 0·0·0 |
| Codex | 모든 gap | 3·3·3 | 21·16·16 | 6·5·5 |

- 작성 세션을 이어 가도 규격 위반을 전부 잡았습니다. 작성 단계에서는 두 도구 모두 지시와 README의 충돌을 말하지 않고 "테스트 통과"만 보고했지만, README 기준 검토를 요청받자 즉시 지적했습니다. 검토 턴 시간은 이어 가기가 짧았습니다. 입력 토큰은 Claude Code에서 이어 가기가, Codex에서 새 세션이 적었습니다. 캐시와 모델 단가를 반영한 청구 금액 비교는 하지 않았습니다. 이번 조건에서는 위반 발견 횟수의 차이를 관측하지 못했습니다.
- "모든 gap"은 적중을 더하지 못하고 골든셋 밖 지적만 16~28건 더했습니다. 결함이 없는 파일에서도 매 회 5~10건이 나왔습니다. 이 수는 지적의 타당성을 판정한 것이 아닙니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| `s04-fresh-review`가 "원본 실행 없음" | `s04-writer-only` 같은 회차가 먼저 없음 | 순서대로 돌리거나 `batch.sh`에 함께 넣기 |
| 작성 세션이 지시를 거부하고 규격대로 고침 | 모델이 README와 충돌을 알아챔 | 그 자체가 관측. `answer_excerpt`에 이유가 있는지 기록 |
| `--continue`가 다른 세션을 이어 감 | 같은 폴더의 더 최근 세션 | 실행 폴더마다 새 프로젝트 폴더라 보통 해당 없음. 직접 돌릴 때는 `--resume <세션>` |
