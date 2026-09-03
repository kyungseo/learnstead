# 04. 조건부 로드 — Claude 경로 규칙 vs Codex 중첩 AGENTS.md

> 이전 ← [`03-long-and-pointer.md`](03-long-and-pointer.md) · 다음 → [`05-tokens.md`](05-tokens.md)

## 목표

"특정 파일 종류에서만 켜지는 규칙"을 두 도구의 기제로 만들어 봅니다. Claude Code는 `.claude/rules/python.md`에 `paths: **/*.py`, Codex는 `src/AGENTS.md`(중첩). 진입 지시문에는 규칙을 두지 않습니다.

## 1. 변형 보기

```bash
cat $FIX/variants/V4-rule-python.md
```

`run-variant.sh`가 Codex용으로는 같은 규칙을 `src/AGENTS.md`에 넣는다(frontmatter 없이).

## 2. 돌리기

```bash
$FIX/scripts/batch.sh claude "V4" 3
$FIX/scripts/batch.sh codex  "V4" 3
python3 $FIX/scripts/summarize.py results.tsv
grep -c "python.md" runs/claude-V4-1/out.json                 # 규칙 파일이 언급되나
grep -n "src/AGENTS.md" runs/codex-V4-1/transcript.txt | head  # 모델이 파일로 읽었나
```

## 3. 기록

| 도구 | 점수 | 놓친 규칙 | 로드 방식 |
| --- | --- | --- | --- |
| Claude 경로 규칙 | | | |
| Codex 중첩 AGENTS.md | | | |

## 작성 환경의 실제 결과

| 도구 | 점수 | 놓친 규칙 | 로드 방식 |
| --- | --- | --- | --- |
| Claude 경로 규칙 | **13/15** (3·5·5) | 1회 테스트 함수 | `.py`를 읽는 순간 규칙 로드(결과에 `python.md` 언급) |
| Codex 중첩 AGENTS.md | **6/15** (2·2·2) | owner 주석·docstring·타입 힌트 3/3회 | 자동 로드 없음. transcript에 `sed -n '1,220p' src/AGENTS.md` — 모델이 **파일로** 읽음 |

Codex 문서에 설명된 동작과 같습니다. 중첩 `AGENTS.md`는 **루트→cwd 경로에** 있을 때만 합쳐집니다. 루트에서 실행했으므로 `src/AGENTS.md`는 일반 파일이었고, 모델이 읽고도 테스트 위치·CHANGELOG만 지켰습니다. `src/`로 `cd`해서 실행하면 로드될 것으로 보이지만 실험하지 않았습니다. 과제가 루트의 `tests/`·`CHANGELOG.md`를 건드리므로 cwd를 옮기면 과제 자체가 달라지기 때문입니다. Claude Code의 경로 규칙은 실행 위치와 무관하게 파일을 읽는 순간 들어왔습니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| Claude V4가 낮음 | `.py`를 읽기 전에 파일을 만듦(규칙이 늦게 로드) | 정상 범위. 3회 결과를 그대로 기록 |
| Codex V4가 높음 | 모델이 읽은 파일을 지시로 취급 | 그대로 기록. transcript로 자동 로드 여부를 구분 |
