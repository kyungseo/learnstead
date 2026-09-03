# 03. 긴 지시문과 pointer — 희석과 간접 참조

> 이전 ← [`02-short-vs-none.md`](02-short-vs-none.md) · 다음 → [`04-conditional.md`](04-conditional.md)

## 목표

같은 규칙 5개를 176줄 속에 흩어 놓았을 때(V2), 진입 지시문이 "규칙은 `docs/RULES.md`"라고 가리키기만 할 때(V3), `@docs/RULES.md`로 import할 때(V3i)의 점수를 비교합니다.

## 1. 변형 보기

```bash
grep -n "owner: platform-team\|한국어 docstring\|타입 힌트\|test_<함수>\|Unreleased" $FIX/variants/V2-long.md   # 규칙이 몇 번째 줄에 있나
cat $FIX/variants/V3-pointer.md; cat $FIX/variants/V3i-import.md
```

V2에서 규칙 5개는 31·74·96·139·161행에 있고, 그 사이는 빌드·DB·API·프런트·로깅·보안·협업·문서 규칙 60여 개와 배경 문단입니다.

## 2. 돌리기

```bash
$FIX/scripts/batch.sh claude "V2 V3 V3i" 3
$FIX/scripts/batch.sh codex  "V2 V3 V3i" 3
python3 $FIX/scripts/summarize.py results.tsv
grep -l RULES runs/claude-V3-*/out.json | wc -l      # pointer를 읽었나(결과 텍스트 언급)
```

## 3. 기록

| 변형 | Claude | 놓친 규칙 | Codex | 놓친 규칙 |
| --- | --- | --- | --- | --- |
| V2 길게 | | | | |
| V3 pointer | | | | |
| V3i import | | | | |

## 작성 환경의 실제 결과

| 변형 | Claude | 놓친 규칙 | Codex | 놓친 규칙 |
| --- | --- | --- | --- | --- |
| V2 길게 | 11/15 (3·3·5) | 테스트 함수 docstring·타입 힌트 | **10/15** (4·3·3) | 한국어 docstring 3/3회(영어로 씀), 타입 힌트 2/3회 |
| V3 pointer | **9/15** (3·3·3) | 테스트 함수 docstring·타입 힌트 | 14/15 (5·5·4) | docstring 1회 |
| V3i import | 13/15 (5·5·3) | 1회만 테스트 함수 | 14/15 (5·4·5) | docstring 1회 |

- **Codex는 희석됐습니다.** V1 15 → V2 10. 176줄 속의 "한국어 docstring"을 3회 모두 놓치고 `"""Convert text to a lowercase, hyphen-separated slug."""`처럼 영어로 썼습니다.
- **Claude는 V1과 V2가 같았다**(11 = 11). 놓친 항목도 같다(테스트 함수). 길이 효과가 있었더라도 이 실험의 규칙 모호함에 가려졌을 수 있습니다.
- **Claude의 pointer(9) < import(13).** V3 3회 모두 결과 텍스트에 "RULES.md를 따랐다"는 언급이 있었는데도 점수는 낮았습니다. 읽었지만 덜 따랐습니다. Codex는 `@`가 문자 그대로라 V3와 V3i가 같은 조건이었고 둘 다 14점이었습니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| Codex V2가 만점 | 모델·버전 차이 | 그대로 기록. V2를 250줄 이상으로 늘려 재시도 |
| Claude V3가 pointer를 안 읽음 | 판단에 맡긴 결과 | 정상. pointer 문장에 "`.py`를 만들기 전에 읽는다"를 붙여 비교해 보라 |
