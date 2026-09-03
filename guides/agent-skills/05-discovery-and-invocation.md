# 05. 발견과 호출 — description이 하는 일

> 이전 ← [`04-tool-differences.md`](04-tool-differences.md) · 다음 → [`06-canonical-and-adapters.md`](06-canonical-and-adapters.md)

## 이 장에서 답하는 질문

- 모델은 어떤 근거로 skill을 고르는가
- 자동 호출을 막거나 사람 호출을 막으려면 어떻게 하는가
- 인자는 어떻게 넘어가고, 호출된 본문은 언제까지 남는가

## 1. Skill을 발견하게 만드는 description

세션이 시작되면 도구는 모든 skill의 `name`과 `description`을 목록으로 만들어 모델에게 줍니다. 이 목록에는 본문이 없습니다. 모델은 사용자의 요청과 목록을 대조해 "지금 열어 볼 skill"을 고릅니다. 따라서 발견의 품질은 **description 한 줄과 사용자 요청의 어휘가 얼마나 겹치는가에 따라** 달라집니다.

실습에서 확인한 세 장면 [실행 검증 · 실습 02]:

| description | 요청 | 결과 (3회) |
| --- | --- | --- |
| "회의록에서 액션 아이템을 뽑아 … 표로 정리한다. 회의록·미팅 노트·액션 아이템·할 일 추출을 말하면 사용한다. 일반 문서 요약이나 일정 계산에는 쓰지 않는다." | "회의록에서 액션 아이템을 정리해 줘" | 3/3 호출 |
| 위와 같음 | "세 문장으로 요약해 줘" | 0/1 호출 (요약만 답함) |
| "문서·회의록·노트를 읽고 정리한다. 요약, 정리, 핵심 추출, 액션 아이템 등 문서 작업 전반에 사용한다." | "세 문장으로 요약해 줘" | **3/3 호출** — 과호출. 1회는 모델이 description과 본문의 모순을 지적 |

같은 본문과 요청을 사용해도 description 한 줄이 결과를 바꿨습니다. description이 겹치는 두 skill(`meeting-actions`: 액션 아이템 / `notes-summary`: 회의록 정리)을 함께 두었을 때는 요청의 단어("정리해 줘" vs "액션 아이템을 정리해 줘")에 따라 3/3, 1/1로 갈렸습니다 [실행 검증 · 2026-08-30 · Claude Code 2.1.251, Codex CLI 0.144.1 · 실습 04]. 이 실험에서는 모델이 description의 어휘를 선택 근거로 사용했습니다.

### description 쓰기

```text
[무엇을 한다]  회의록에서 액션 아이템을 뽑아 담당자·기한·항목 표로 정리한다.
[언제 쓴다]    사용자가 회의록·미팅 노트·회의 정리·액션 아이템·할 일 추출을 말하거나 회의 기록 파일을 주면 사용한다.
[언제 안 쓴다]  일반 문서 요약이나 일정 계산에는 쓰지 않는다.
```

- **사용자가 실제로 쓸 단어를** 넣습니다. "회의록", "액션 아이템"처럼 기술 용어보다 요청 문장의 어휘를 우선합니다.
- **제외 조건을** 한 줄 넣어 이웃한 작업(요약)으로 새는 것을 막습니다.
- **본문과 모순되지 않게** 씁니다. 과호출 실험에서 모델이 그 모순을 찾아냈듯, 모순은 오동작이나 혼란으로 나타납니다.
- Codex는 초기 skill 목록을 컨텍스트 창의 최대 2% 또는 창 크기를 모를 때 8,000자로 제한하고, 넘으면 설명을 먼저 줄입니다.
  따라서 **핵심 용도와 trigger 단어를 앞에** 둡니다 [문서 확인 · 2026-09-02].

## 2. 트리거 제어

| 원하는 것 | Claude Code | Codex | Gemini CLI | Cursor |
| --- | --- | --- | --- | --- |
| 사람만 부른다 | `disable-model-invocation: true` (목록에서도 빠짐) | `agents/openai.yaml`의 `policy.allow_implicit_invocation: false` | `/skills disable`은 전체 비활성 | `disable-model-invocation: true` |
| 모델만 쓴다 | `user-invocable: false` | — | — | — |
| 특정 skill 끄기(파일 수정 없이) | settings `skillOverrides: {"name": "off"}` (`/skills` 메뉴에서 Space로 전환) | `[[skills.config]] path=… enabled=false` | `/skills disable <name>` | — |
| 모델의 skill 사용 자체를 막기 | permission deny `Skill` 또는 `Skill(name)` | — | — | — |

`skillOverrides`는 실습의 기준선 측정에 사용했습니다. `.claude/settings.local.json`에 `{"skillOverrides": {"meeting-actions": "off"}}`를 두자 목록에서 사라졌고, 같은 요청이 skill 없이 처리됐습니다 [실행 검증 · 실습 05]. 저장소에 들어온 다른 사람의 skill을 고치지 않고 끄는 방법으로 기억해 둘 만합니다.

## 3. 인자

명시 호출 뒤에 붙인 텍스트가 인자입니다. Claude Code는 `$ARGUMENTS`(전체), `$0`·`$1`(위치), 이름 있는 인자를 치환하고, 본문에 자리표시자가 없으면 끝에 `ARGUMENTS: …`를 덧붙입니다 [문서 확인]. 실습의 skill은 자리표시자 없이 "입력 파일 경로"를 인자로 받았습니다. Claude Code는 `Skill` tool 호출에 `"args": "input/meeting-notes.md"`를 실었고 모델은 그 경로를 읽었습니다 [실행 검증]. Codex에서는 `$name` 뒤의 텍스트가 그대로 프롬프트의 일부가 됩니다.

여러 도구용 skill이라면 **자리표시자에 기대지 말고** "인자로 파일 경로가 오면 그 파일을 읽는다"처럼 말로 적는 편이 이식성이 높습니다.

## 4. 호출된 본문은 언제까지 남는가

Claude Code 기준 [문서 확인 · 2.1.251]:

- 본문은 대화에 **메시지로 남아 이후 턴에도 유효합니다.** 도구가 파일을 다시 읽지는 않습니다. 그러므로 "이번 한 번만" 적용되는 표현보다 **상시 지시로** 씁니다.
- 같은 skill을 다시 부르면 내용이 같을 때는 "이미 로드됨" 한 줄만 붙고, 인자나 동적 컨텍스트가 달라 내용이 바뀌면 다시 붙습니다.
- 컨텍스트 압축(auto-compaction) 후에는 최근 호출된 skill부터 각 5,000 토큰, 합계 25,000 토큰까지만 다시 붙습니다. 많이 부른 세션에서는 오래된 skill이 빠질 수 있지만, **다시 호출하면 복구됩니다.**
- `allowed-tools` 사전 승인은 본문과 달리 **호출한 턴에서만** 유효합니다.

Codex는 모델이 파일을 읽는 방식이므로 "남는다"의 의미가 다릅니다. 읽은 내용은 그 tool 결과로 대화에 남지만, 압축할 때 어떻게 취급되는지는 확인하지 못했습니다 [미검증].

## 5. 동적 컨텍스트 (Claude Code)

Claude Code는 본문의 `` !`명령` ``을 모델에 보내기 전에 실행해 출력으로 치환합니다. PR 요약 skill이 `` !`gh pr diff` ``로 실제 diff를 끼워 넣는 식입니다 [문서 확인]. 다음 두 가지를 주의해야 합니다.

- 명령 하나라도 실패(0이 아닌 종료)하면 **호출 전체가 중단되고** 모델은 본문을 보지 못합니다. 실패해도 되는 검사 명령은 `|| true`를 붙입니다.
- 권한 확인이 "allow"가 아니면(물어봐야 하는 규칙 포함) 역시 중단됩니다. `allowed-tools`로 사전 승인하거나 설정에서 허용합니다.

이 기능은 Claude Code 전용입니다. `.agents/skills`에 두는 다중 도구 skill에 쓰면 다른 도구에서는 **명령이 문자 그대로** 모델에게 전달됩니다.

## 6. 발견이 안 될 때 확인 순서

1. 목록에 있는가 — "What skills are available?" / `/skills`
2. frontmatter가 파싱되는가 — `skills-ref validate <skill-dir>`로 공통 규격을 검사한다. plugin에 넣는 Skill이면 `claude plugin validate <plugin-dir>`도 실행한다 [문서 확인]
3. 폴더 이름과 `name`이 같은가
4. description에 요청의 단어가 있는가 — 요청을 description 표현에 맞춰 바꿔 보고, 그래도 안 되면 description을 고친다
5. 목록 예산에 밀렸는가 — Codex의 생략 경고, Claude Code `/context`의 Skills 항목을 확인 [문서 확인]
6. 상위 우선순위 사본이 가리는가 — [`04`](04-tool-differences.md) 3절

## 이 장을 끝내면

- description을 "무엇/언제/언제 아님" 구조로 쓰고, 과호출·미호출을 요청 문장으로 시험할 수 있습니다.
- 도구별로 자동 호출을 끄고 켜는 방법을 알 수 있습니다.
- 호출된 본문이 남는 방식과 압축 시 한계를 이해하고, 필요하면 다시 부를 수 있습니다.
