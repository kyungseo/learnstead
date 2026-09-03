# 05. skill vs 프롬프트 직접 지시 — 3회씩 판정

> 이전 ← [`04-tighten-and-collide.md`](04-tighten-and-collide.md) · 처음 → [`README.md`](README.md)

## 목표

"skill 없이 프롬프트에 절차를 붙이면 되지 않나?"에 숫자로 답한다. 같은 본문을 (A) skill로 두고 요청만 보낸 경우, (B) skill을 끄고 본문을 프롬프트에 붙인 경우, (C) skill도 지시도 없이 요청만 보낸 경우를 각 3회 돌려 판정한다.

## 1. (A) skill on — 3회

01·04에서 이미 돌렸다면 그 로그를 쓴다. 아니면:

```bash
for i in 1 2 3; do scripts/run-claude.sh A-$i "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘"; done
```

## 2. (B) skill off + 본문을 프롬프트에 — 3회

skill을 켜 둔 채 본문을 붙이면 **모델이 skill을 다시 부른다**(작성 환경에서 3/3). 그래서 반드시 끈다.

```bash
printf '{"skillOverrides": {"meeting-actions": "off"}}\n' > .claude/settings.local.json
BODY=$(sed '1,/^---$/d' .agents/skills/meeting-actions/SKILL.md | sed '1,/^---$/d')   # frontmatter 제거
for i in 1 2 3; do scripts/run-claude.sh B-$i "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘. 다음 지시를 따라라:

$BODY"; done
```

## 3. (C) 아무 지시 없이 — 1회 이상

```bash
scripts/run-claude.sh C-1 "input/meeting-notes.md 회의록에서 액션 아이템을 정리해 줘"
rm .claude/settings.local.json
```

## 4. 판정

```bash
for l in A-1 A-2 A-3 B-1 B-2 B-3 C-1; do printf '%-5s %s\n' $l "$(python3 .agents/skills/meeting-actions/scripts/check.py logs/$l.out)"; done
```

## 5. 기록

| 조건 | 통과 / 시도 | 대표 실패 사유 | 캐시 읽기 토큰(1회차) |
| --- | --- | --- | --- |
| A skill on | /3 | | |
| B off + 프롬프트 지시 | /3 | | |
| C off, 지시 없음 | /1 | | |

## 작성 환경의 실제 결과

| 조건 | 통과 / 시도 | 실패 사유 | 토큰(캐시 읽기/쓰기/출력, 1회차) |
| --- | --- | --- | --- |
| A skill on (v1.0) | **3/3** | — | 48,245 / 16,004 / 503 |
| B off + 프롬프트 지시 (v1.0 본문) | **0/3** | 5열(비고 열 추가), 기한을 `2026-09-12 (금)`·`2026-09-02 (수)`로 환산, `**미정**`으로 꾸밈, 또는 표 대신 다른 형식 | 33,935 / 7,896 / 1,060 |
| C off, 지시 없음 | 0/1 | 5열, "다음 주 수요일"을 `2026-09-02 (추정)`으로 환산 | 33,764 / 7,460 / 1,050 |

세 조건의 출력 토큰을 보면 A(503)가 B·C(약 1,050)의 절반이다. skill은 "표 하나만, 설명 금지"를 지켰고 B·C는 표 뒤에 결정 사항·보류·확인 필요 절을 덧붙였다.

해석 [해석]: B가 0/3인 것이 가장 뜻밖이다. 같은 문장을 프롬프트에 넣었는데 왜 다른가. 확실한 설명은 없다. 관측된 차이는 (1) skill 본문은 별도 메시지로 들어가고 프롬프트 지시는 요청과 한 덩어리로 들어간다, (2) B는 "정리해 줘" 다음에 규칙이 이어져 요청의 무게가 규칙을 눌렀을 수 있다, 정도다. n=3이라 경향으로만 읽되, **"프롬프트에 붙이면 같다"는 가정은 이 실습에서 성립하지 않았다.**

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| B에서 `tools=`에 Skill 호출이 있다 | `settings.local.json`이 없거나 잘못됨 | 파일 내용 확인, 목록에서 `meeting-actions`가 빠졌는지 먼저 확인 |
| B가 3/3 통과 | 모델·버전 차이 | 그대로 기록. 이 경우 skill의 이점은 토큰과 재사용성으로 좁혀진다 |
| A에서 FAIL | 04를 건너뛰어 v1.0 규칙 | `git diff`로 본문 확인 |

## 이 실습을 끝내면

- skill의 효과를 "있다/없다"가 아니라 **판정 통과 수와 토큰으로** 말할 수 있다.
- 기준선을 잴 때 skill을 **꺼야** 하는 이유를 안다.
- 다음 skill을 만들 때 description·본문·판정기를 함께 만든다.
