# 01. 추론 가능한 기준선 — 코드가 이미 규칙을 따를 때

<!-- learnstead:nav:start -->
[← 이전: 자료 소개](README.md) · [목차](README.md) · [다음: 02. 짧은 지시문 vs 없음 — 코드가 규칙을 따르지 않을 때](02-short-vs-none.md)
<!-- learnstead:nav:end -->

## 목표

실험의 첫 함정을 직접 확인합니다. 기존 코드가 규칙 5개를 이미 따르는 상태에서 지시문 없이 과제를 시키면 어떻게 되는지 살펴봅니다.

## 1. fixture를 라운드 1 상태로

`fixture/project/`는 라운드 2 상태(규칙을 따르지 않음)입니다. 라운드 1 상태를 만들려면 기존 파일 세 개를 규칙대로 고칩니다.

```bash
cd ~/ctx-workshop
cp -R "$FIX" fixture-r1
FIX_R1="$PWD/fixture-r1"
cd "$FIX_R1/project"
# src/textkit/wordcount.py: 첫 줄 '# owner: platform-team', 한국어 docstring, 타입 힌트
# tests/test_wordcount.py: 첫 줄 owner, 함수 이름 test_word_count_<경우>, 한국어 docstring, -> None
# src/textkit/__init__.py: 첫 줄 owner
```

(작성 환경에서는 이 상태가 fixture의 첫 버전이었습니다.)

## 2. 돌리기

`run-variant.sh`는 스크립트가 있는 fixture의 `project/`를 복사합니다. 따라서 방금 수정한 사본의 스크립트를 실행합니다. 결과도 별도 디렉터리에 두어 라운드 2와 구분합니다. 재실행할 때는 기존 `fixture-r1/`과 `round1/` 기록을 먼저 다른 이름으로 보관하세요.

```bash
mkdir -p ~/ctx-workshop/round1 && cd ~/ctx-workshop/round1
"$FIX_R1/scripts/batch.sh" claude "V0 V1 V2" 3
"$FIX_R1/scripts/batch.sh" codex  "V0 V1 V2" 3
python3 "$FIX_R1/scripts/summarize.py" results.tsv
cp results.tsv ../results-round1.tsv
```

## 3. 기록

| 변형 | Claude 점수/15 | Claude 턴 | Codex 점수/15 |
| --- | --- | --- | --- |
| V0 | | | |
| V1 | | | |
| V2 | | | |

## 작성 환경의 실제 결과

| 변형 | Claude | 턴(평균) | 캐시 읽기(평균) | Codex | 토큰(평균) |
| --- | --- | --- | --- | --- | --- |
| V0 없음 | **15/15** | 8 | 168,548 | **15/15** | 37,605 |
| V1 짧게 | 15/15 | 4 | 75,845 | 15/15 | 32,555 |
| V2 길게 | 15/15 | 7 | 170,047 | 15/15 | 34,887 |

세 변형이 모두 만점입니다. 지시문이 없어도 모델은 `wordcount.py`와 `test_wordcount.py`를 읽고 owner 주석·한국어 docstring·타입 힌트·테스트 이름·CHANGELOG 형식을 **따랐습니다.** 준수율 실험으로는 실패했지만 두 가지를 배웠습니다.

- **이 과제에서는 기존 코드만으로도 규칙을 따랐습니다.** 중복 설명을 줄일 후보이지만, 탐색을 줄여 주는 명령·경로까지 없애야 한다는 뜻은 아닙니다.
- 지시문이 없을 때 Claude Code는 8턴·16.8만 토큰, 있을 때는 4턴·7.6만 토큰을 사용했습니다. 이 조건에서는 준수율 차이 없이 **턴 수와 캐시 읽기 토큰의 차이가 관측됐습니다.** 반복 수가 적어 지시문만의 효과로 단정할 수는 없습니다. 긴 지시문(V2)은 7턴으로 다시 늘었습니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| V0에서 낮은 점수 | 기존 파일이 규칙을 다 따르지 않음 | 세 파일을 다시 확인 |
| `claude -p`가 편집 권한을 물어 멈춤 | permission mode | `--permission-mode acceptEdits`를 `run-variant.sh`에 추가 |
| Codex가 파일을 못 씀 | sandbox read-only | 스크립트의 `-s workspace-write` 확인 |

<!-- learnstead:footer:start -->

---

[← 이전: 자료 소개](README.md) · [목차](README.md) · [다음: 02. 짧은 지시문 vs 없음 — 코드가 규칙을 따르지 않을 때](02-short-vs-none.md)

<!-- learnstead:footer:end -->
