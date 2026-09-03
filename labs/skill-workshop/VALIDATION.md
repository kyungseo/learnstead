# VALIDATION

## 작성 환경

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-08-30 |
| OS | macOS (Apple Silicon) |
| Claude Code | 2.1.251, 모델 claude-fable-5 |
| Codex CLI | 0.144.1, 모델 gpt-5.6 계열(transcript 표기), sandbox read-only |
| Python | 3.14 (`check.py`는 표준 라이브러리만 사용) |

## 실행 결과 요약

| 단계 | 항목 | 결과 |
| --- | --- | --- |
| 01 | 명시 호출 / 자동 호출 / 요약 요청 | PASS / PASS(Skill 호출) / 미호출 |
| 01 | 자동 호출 반복 | 3/3 Skill 호출·PASS |
| 02 | 넓은 description + 요약 요청 3회 | 3/3 Skill 호출(과호출), 1회 모순 지적 |
| 02 | `skillOverrides: off` | 목록에서 제거됨 |
| 03 | Codex `$name` / 자동 | 둘 다 SKILL.md 읽음, v1.0 본문으로 5행 FAIL |
| 03 | 경로 탐침 | 2026-08-30 Codex: `.agents/skills`·`~/.agents/skills`·당시 호환 경로 `~/.codex/skills` ✓, `.claude/skills` ✗ / Claude Code: `.claude/skills` ✓, symlink ✓, `.agents/skills` ✗ |
| 04 | v1.1 재실행 | Codex 2/2, Claude Code 2/2 PASS |
| 04 | description 겹침 | "정리" → `notes-summary` 3/3(Claude)·1/1(Codex), "액션 아이템" → `meeting-actions` |
| 04 | 같은 이름 | Claude Code 개인 사본 채택, Codex 목록 둘 다·호출은 저장소 사본(1회) |
| 05 | A/B/C | 3/3 · 0/3 · 0/1 |
| — | `fixture/scripts/setup.sh` | 빈 디렉터리에 실행해 구조 생성·git 초기 commit 확인 |
| — | `check.py` | `expected/meeting-actions.md`로 PASS, 모든 실행 로그에 적용 |

## 2026-09-02 재검증

- 빈 임시 디렉터리에서 `setup.sh`를 실행해 fixture와 초기 git commit 생성을 확인했습니다.
- 같은 setup을 비어 있지 않은 디렉터리에 다시 실행하면 변경 전에 종료됐습니다.
- 기대 출력은 `check.py`를 통과했고, 경로 이동 문자가 포함된 실행 label은 runner가 거부했습니다.
- shell 스크립트 3종과 Python 판정 스크립트의 문법 검사를 다시 통과했습니다.

## 2026-09-03 공개 전 재검증

- 충돌 실험의 사용자 홈·프로젝트 skill 이름을 `ws-dup-meeting-actions`로 격리했습니다.
- Claude Code 2.1.259는 개인 사본의 `[PERSONAL-COPY] personal`, Codex CLI 0.144.1은 저장소 사본의 `[PROJECT-COPY] project`를 각각 1회 출력했습니다.
- reset 뒤 `~/.claude/skills/ws-dup-meeting-actions`, `~/.agents/skills/ws-dup-meeting-actions`와 두 프로젝트 사본이 모두 남지 않았음을 확인했습니다.
- runner 세 종은 CLI 실패를 종료 코드로 남기면서도 관측 요약과 판정 결과를 출력하도록 다시 확인했습니다.

## 정적 검사

- 한국어 강조 직후 조사 0건, GFM 렌더 후 literal `**` 0건
- 상대 링크 전수 확인
- 후행 공백 0, 절대 경로·내부 식별자 0 (fixture 스크립트 포함)
- `bash -n` 스크립트 3종, `python3 -m py_compile check.py`

## 한계

- 반복 1~3회. 자동 호출 판단은 모델·버전에 따라 달라질 수 있다.
- Codex 이름 충돌 시 호출 대상은 1회 관측.
- 두 도구 모두 실제 API 비용이 든다. 작성 환경 기준 전 과정 Claude Code 약 20회, Codex 약 10회.
- 충돌 재검증은 도구별 1회이며, 사용자 환경의 기존 skill은 실험 대상으로 사용하지 않았다.
