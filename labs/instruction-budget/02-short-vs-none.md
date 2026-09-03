# 02. 짧은 지시문 vs 없음 — 코드가 규칙을 따르지 않을 때

> 이전 ← [`01-inferable-baseline.md`](01-inferable-baseline.md) · 다음 → [`03-long-and-pointer.md`](03-long-and-pointer.md)

## 목표

fixture(라운드 2 상태)로 V0와 V1을 돌려 지시문의 효과를 분리하고, 놓친 항목을 파일에서 확인합니다.

## 1. 돌리기

```bash
cd ~/ctx-workshop && rm -rf runs results.tsv
$FIX/scripts/batch.sh claude "V0 V1" 3
$FIX/scripts/batch.sh codex  "V0 V1" 3
python3 $FIX/scripts/summarize.py results.tsv
for d in runs/*/; do printf "%-14s %s\n" "$(basename $d)" "$(grep FAIL $d/check.txt | tr '\n' ',')"; done
```

## 2. 놓친 항목 보기

```bash
cat runs/claude-V1-1/src/textkit/slug.py
head -12 runs/claude-V1-1/tests/test_slug.py
```

규칙은 "모든 함수"인데 어느 함수에 적용됐는지 봅니다.

## 3. 기록

| 변형 | Claude | 놓친 규칙 | Codex | 놓친 규칙 |
| --- | --- | --- | --- | --- |
| V0 | | | | |
| V1 | | | | |

## 작성 환경의 실제 결과

| 변형 | Claude | 놓친 규칙 | Codex | 놓친 규칙 |
| --- | --- | --- | --- | --- |
| V0 없음 | **0/15** | 전부 | **0/15** | 전부 |
| V1 짧게 | 11/15 (3·5·3) | R2 한국어 docstring, R3 타입 힌트 — 2회 | **15/15** | 없음 |

Claude V1-1의 파일을 보면 `slug.py`는 owner·한국어 docstring·타입 힌트를 모두 갖췄습니다. `tests/test_slug.py`에는 owner 주석이 있지만 `def test_slugify_basic():`에 docstring과 반환 타입이 없습니다. 규칙 "모든 함수"를 **구현 함수에만** 적용한 것입니다. 3회 중 1회는 테스트까지 적용해 5/5를 받았고, Codex는 3회 모두 테스트 함수에도 적용했습니다.

여기서 배우는 것: 준수율이 낮을 때 첫 의심은 길이가 아니라 **규칙 문장의 포함 범위다**. "테스트 함수를 포함한 모든 함수"라고 썼다면 달랐을 가능성이 크다(실험하지 않음 — 재현 시 V1의 규칙 2·3을 그렇게 고쳐 비교해 보라).

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| V0에서 점수가 남 | 기존 코드가 일부 규칙을 따름 | `fixture/project`의 세 파일이 라운드 2 상태인지 확인 |
| `check.py`가 `과제 자체 FAIL` | 모델이 다른 파일명을 씀 | 과제 문장의 경로를 그대로 두고 다시. 결과를 그대로 기록 |
