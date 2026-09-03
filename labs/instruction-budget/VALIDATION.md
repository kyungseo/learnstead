# VALIDATION

## 작성 환경

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-08-30~31 |
| OS | macOS (Apple Silicon), Python 3.14 |
| Claude Code | 2.1.251, claude-fable-5, `defaultMode: "auto"`, `--max-turns 25` |
| Codex CLI | 0.144.1, gpt-5.6 계열, `-s workspace-write` |

## 실행 결과 요약

| 라운드 | 변형 | Claude | Codex |
| --- | --- | --- | --- |
| 1 (추론 가능) | V0 / V1 / V2 / V3 / V3i / V4 | 15 / 15 / 15 / 15 / 15 / 15 | 15 / 15 / 15 / 15 / 15 / 15 |
| 2 | V0 / V1 / V2 / V3 / V3i / V4 | 0 / 11 / 11 / 9 / 13 / 13 | 0 / 15 / 10 / 14 / 14 / 6 |

원본: [`results/round1-inferable.tsv`](results/round1-inferable.tsv), [`results/round2.tsv`](results/round2.tsv). 각 행은 라벨·턴·토큰·점수.

## 2026-09-02 재검증

| 도구·변형 | 결과 | 관측 |
| --- | --- | --- |
| Claude Code 2.1.258 · V1 · 1회 | 3/5 | 테스트 함수의 한국어 docstring·반환 타입 누락. 기존 V1 실패 유형과 같음 |
| Codex CLI 0.144.1 (`gpt-5.6-sol`) · V1 · 1회 | 5/5 | 규칙 5개와 과제 자체 모두 통과 |

판정 스크립트의 `sys.argv` 직접 처리를 `argparse`와 대상 디렉터리 검사로 바꿨습니다. 두 현재 실행 결과에 다시 적용해 Claude의 3/5와 Codex의 5/5가 예외 없이 반환되는 것을 확인했습니다.

## 2026-09-03 공개 전 재검증

| 항목 | 결과 |
| --- | --- |
| `batch.sh claude "V0 V1" 1` | V0 0/5·V1 3/5를 모두 기록하고 batch 완료 |
| 새 디렉터리의 V3 | `docs/` 생성 뒤 `RULES.md` 복사·실행 완료, 3/5 |
| label `.`, `..`, `../escape`, `a/b` | 모두 삭제 전에 종료 코드 2로 거부 |
| async·위치 전용 인자·한국어 `슬러그` | 판정 5/5 |
| 문법 오류가 있는 Python 파일 | crash 없이 2/5, 종료 코드 1 |

runner와 batch 요약에는 CLI 종료 코드를 별도 필드로 남깁니다. 판정 실패는 실험 결과로 기록하고, CLI 자체 실패만 종료 코드 2로 구분합니다.

## 정적 검사

- 한국어 강조 직후 조사 0건, GFM 렌더 후 literal `**` 0건 (실습 fixture `variants/V4-rule-python.md`의 YAML frontmatter glob `**/*.py` 1건은 강조가 아니라 glob이므로 제외)
- 상대 링크 전수 확인, 후행 공백·절대 경로·내부 식별자 0
- 2026-09-02: `run-variant.sh`의 잘못된 tool·variant·경로 이동 label 거부, `batch.sh`의 잘못된 반복 수 거부 확인
- `bash -n` 스크립트 2종, `python3 -m py_compile` 2종

## 한계

- 3회 반복. 과제·규칙·모델 각 하나.
- `--max-turns 25` 안에서 모두 끝났습니다.
- 실행마다 새 git 저장소를 만들므로 `~/.claude.json`에 프로젝트 항목이 쌓인다(무해).
