# VALIDATION

## 작성 환경

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-08-30 |
| OS | macOS (Apple Silicon) |
| Claude Code | 2.1.251, 모델 claude-fable-5, `claude -p --output-format stream-json --allowedTools "Read Skill"` |
| Codex CLI | 0.144.1, 모델 gpt-5.6 계열(transcript 표기), `codex exec --skip-git-repo-check -o … < /dev/null`, sandbox read-only |
| Gemini CLI · Cursor | 미실행 (문서 확인만) |

## 2026-09-02 재검토

- 현재 설치본: Claude Code 2.1.258, Codex CLI 0.144.1, Node 18.20.5, Python 3.14.7.
- Agent Skills 규격과 Claude Code·Codex 공식 문서를 다시 확인해 필수·선택 필드, Codex 공식 경로, 목록 예산을 갱신했습니다.
- fixture setup·판정·runner의 정상 경로와 잘못된 입력 거부를 다시 확인했습니다. 비어 있지 않은 디렉터리와 경로 이동 label은 실행 전에 거부됐습니다.
- SVG 5종은 `svg-infographic` lint에서 오류·경고 0건이었고 Chrome 152로 2배 PNG 렌더와 육안 검사를 통과했습니다.
- 아래 실행 결과는 2026-08-30의 동일 fixture 기록이며 재실행 결과로 소급하지 않습니다.

## 2026-09-03 공개 전 재검증

- 현재 설치본 Claude Code 2.1.259와 Codex CLI 0.144.1로 같은 이름의 skill 충돌 경로를 다시 실행했습니다.
- 실험용 이름을 `ws-dup-meeting-actions`로 격리한 상태에서 Claude Code는 개인 사본, Codex는 저장소 사본을 선택했습니다. 각 1회 관측이며 일반 규칙으로 확대하지 않습니다.
- reset 뒤 프로젝트와 사용자 홈의 실험용 skill 경로 네 곳이 모두 사라졌음을 확인했습니다. 기존 `meeting-actions` 경로는 만들거나 지우지 않았습니다.
- runner는 CLI 종료 코드를 기록하고, 성공 여부와 무관하게 관측 요약을 출력했습니다.

## 실행 검증 목록

| # | 검증 항목 | 방법 | 결과 |
| --- | --- | --- | --- |
| 1 | 규격 필드만 쓴 skill의 명시 호출 | Claude Code `/meeting-actions <파일>` · Codex `$meeting-actions <파일>` | 두 도구 모두 로드·적용. Claude Code는 명시 호출 시 `Skill` tool 이벤트 없이 본문이 펼쳐짐 |
| 2 | 자동 호출 | "회의록에서 액션 아이템을 정리해 줘" | Claude Code `Skill` tool 호출 3/3 · Codex 모델이 `sed`로 SKILL.md 읽음 2/2 |
| 3 | 오호출 방지 | "세 문장으로 요약해 줘" | Claude Code 0/1 호출 (요약만 답함) |
| 4 | 넓은 description의 과호출 | description을 "문서 작업 전반"으로 바꾸고 요약 요청 3회 | 3/3 호출. 1회는 모델이 description·본문 모순 지적 |
| 5 | description 겹침 시 선택 | `notes-summary` 추가 후 "회의록 정리해 줘" / "액션 아이템을 정리해 줘" | Claude Code 3/3 `notes-summary` · 1/1 `meeting-actions` · Codex 1/1 `notes-summary` |
| 6 | 경로 발견 | 각 경로에 탐침 skill을 두고 목록 요청 | 2026-08-30 Codex: `.agents/skills` ✓ `~/.agents/skills` ✓ 당시 호환 경로 `~/.codex/skills` ✓ `.claude/skills` ✗ · Claude Code: `.claude/skills` ✓ `.agents/skills` ✗ symlink ✓ |
| 7 | 같은 이름 충돌 | 개인·홈 경로에 표식을 넣은 사본 배치 | Claude Code: 개인 사본 채택(프로젝트 가려짐) · Codex: 목록에 둘 다, `$name` 호출은 저장소 사본 (1회) |
| 8 | 본문 규칙 보강(v1.0 → v1.1) | 규칙 1에 경계 사례 명시 후 재실행 | v1.0: Claude Code 4/4 통과, Codex 0/2 (5행) → v1.1: Claude Code 2/2, Codex 2/2 통과 |
| 9 | skill vs 프롬프트 직접 지시 | `skillOverrides: off` 상태에서 같은 본문을 프롬프트에 붙여 3회 | 0/3 통과(열 추가·기한 환산) vs skill 3/3 통과 |
| 10 | 비-대화형 stdin | 당시 `codex exec`를 스크립트 안에서 실행 | stdin 미리다이렉트 시 10분 대기. `< /dev/null`로 해결(2026-08-30 관측) |

## 정적 검사

- 한국어 강조 직후 조사 0건, GFM 렌더 후 literal `**` 0건
- 상대 링크 전수 확인
- 후행 공백 0, 절대 경로·내부 식별자 0

## 한계

- 반복 횟수가 적다(대부분 1~3회). 수치는 경향으로만 읽는다.
- 모델·버전이 바뀌면 자동 호출 판단과 충돌 규칙이 달라질 수 있다. 표의 날짜를 확인한다.
- Codex 실행에는 `codex_models_manager` 캐시 경고가 함께 출력됐으나 결과에 영향은 없었다.
- 2026-09-03의 이름 충돌 재검증도 도구별 1회다. 선택 우선순위는 버전과 설정에 따라 달라질 수 있다.
