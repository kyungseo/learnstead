# VALIDATION

## 작성 환경

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-08-30~31 |
| OS | macOS (Apple Silicon), Python 3.14 |
| Claude Code | 2.1.251, claude-fable-5, `claude -p --output-format json --max-turns 25`, 사용자 설정 `permissions.defaultMode: "auto"` |
| Codex CLI | 0.144.1, gpt-5.6 계열, `codex exec -s workspace-write` |

2026-09-02 문서 재검토: Claude Code 2.1.258, Codex CLI 0.144.1. Claude Code import 깊이와 Codex local memory의 현재 문서를 다시 확인했습니다.

같은 날 V1을 현재 설치본으로 한 번씩 다시 실행했습니다. Claude Code는 3/5로 테스트 함수의 한국어 docstring과 반환 타입을 놓쳤고, Codex(`gpt-5.6-sol`)는 5/5였습니다. 기존 3회 기록의 실패 유형과 모순되지 않지만 표본 1회이므로 추세 갱신에는 쓰지 않습니다. 실행·판정 스크립트의 정상 경로와 잘못된 인자 거부도 함께 확인했습니다.

## 2026-09-03 공개 전 재검증

- Claude Code 2.1.259로 `batch.sh claude "V0 V1" 1`을 실행했습니다. V0이 0/5, V1이 3/5여도 두 실행이 모두 기록돼 비만점에서 batch가 중단되지 않았습니다.
- 새 작업 디렉터리에서 V3를 실행해 추적되지 않던 `docs/`가 자동 생성되고 pointer fixture가 복사되는 것을 확인했습니다.
- label `.`, `..`, `../escape`, `a/b`는 모두 파일 삭제 전에 종료 코드 2로 거부됐습니다.
- 판정기는 `async def`, 위치 전용 인자, 한국어 `슬러그`를 포함한 예시에서 5/5를 반환했습니다. 문법 오류가 있는 Python 파일에서는 crash 없이 2/5와 종료 코드 1을 반환했습니다.
- runner는 CLI 종료 코드와 판정 종료 코드를 분리해 남기고, batch 요약에도 CLI 종료 코드를 포함했습니다.

## 실행 검증 목록

| # | 항목 | 방법 | 결과 |
| --- | --- | --- | --- |
| 1 | 라운드 1 — 규칙이 코드에서 추론 가능 | V0·V1·V2·V3·V3i·V4 × 3회 × 2도구 = 36회 | 전부 15/15. Claude 턴 수 V0 8 / V1 4 / V2 7, 캐시 읽기 16.9만 / 7.6만 / 17.0만 |
| 2 | 라운드 2 — 기존 코드가 규칙을 따르지 않음 | V0~V4(6종) × 3회 × 2도구 = 36회 | Claude 0·11·11·9·13·13 / Codex 0·15·10·14·14·6 |
| 3 | 실패 항목 분석 | 각 run의 `check.txt`·생성 파일 | Claude 실패는 전부 테스트 함수 docstring·타입 힌트. Codex V2 실패는 한국어 docstring(3/3)·타입 힌트(2/3). Codex V4 실패는 owner·docstring·타입 힌트 |
| 4 | pointer 읽기 여부 | 결과 텍스트에 `RULES` 언급 | Claude V3·V3i 6/6회 언급 |
| 5 | Codex 중첩 AGENTS.md 로드 | transcript의 `src/AGENTS.md` 읽기 줄 | 3/3회 모델이 파일로 읽음(자동 로드 아님) |
| 6 | Claude 경로 규칙 로드 | 결과 JSON에 `python.md` 언급 | 확인 |
| 7 | 토큰 | 결과 JSON `usage` / transcript `tokens used` | 06장 표 |
| 8 | Claude Code auto memory 존재 | 작성 장비 디렉터리 확인 | `MEMORY.md` + 주제 파일 1개 |

## 정적 검사

- 한국어 강조 직후 조사 0건, GFM 렌더 후 literal `**` 0건 (실습 fixture `variants/V4-rule-python.md`의 YAML frontmatter glob `**/*.py` 1건은 강조가 아니라 glob이므로 제외)
- 상대 링크 전수 확인, 후행 공백·절대 경로·내부 식별자 0
- SVG 3종은 `svg-infographic` lint 오류·경고 0건, Chrome 152의 2배 PNG 렌더와 육안 검사를 통과

## 한계

- 3회 반복. 2~3점 차이는 잡음일 수 있습니다.
- 과제·규칙·모델이 하나씩입니다. 수치는 경향으로 읽습니다.
- Claude Code의 `defaultMode: "auto"`는 편집 승인을 생략해 턴 수에 영향을 줄 수 있습니다.
- compaction·Codex local memory는 실행하지 않았습니다. 해당 내용은 문서 확인으로 구분했습니다.
- 2026-09-03 재검증은 회귀 확인을 위한 대표 실행입니다. 기존 3회 실험의 결과표를 새 표본으로 대체하지 않습니다.
