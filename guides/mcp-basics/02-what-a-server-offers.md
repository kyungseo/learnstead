# 02. 서버가 주는 세 가지 — tools · resources · prompts

> 이전 ← [`01-the-problem-mcp-solves.md`](01-the-problem-mcp-solves.md) · 다음 → [`03-transports.md`](03-transports.md)

## 이 장에서 답하는 질문

- tool 정의에는 무엇이 들어가고 모델은 그중 무엇을 보는가
- 결과는 어떤 모양이고, 오류는 왜 두 종류인가
- resources·prompts는 tools와 무엇이 다르며 언제 쓰는가

## 1. 세 primitive

| primitive | 누가 쓰나 | 무엇 | 실습 서버에서 |
| --- | --- | --- | --- |
| **tools** | 모델 (model-controlled) | 모델이 판단해 호출하는 함수 | `list_notes` `read_note` `search_notes` (+`write_note`) |
| **resources** | 사용자·앱 (application-controlled) | URI로 식별되는 읽기 데이터. 파일·DB 행·설정 | (사용하지 않음 — 도구로 충분) |
| **prompts** | 사용자 (user-controlled) | 인자를 받아 메시지를 만드는 템플릿. `/` 메뉴에 노출 | (사용하지 않음) |

코딩 Agent 연동에서는 tools를 가장 자주 접합니다. Claude Code에서 resources는 `@server:resource/경로`로, prompts는 `/mcp__server__prompt`로 사용자가 직접 꺼냅니다 [문서 확인 · 2.1.251]. 모델이 상황에 따라 선택하는 것은 tools입니다. 이 가이드도 tools에 집중합니다. "읽기 데이터를 모델이 알아서 가져오게" 하려면 resources보다 **읽기 도구를** 만드는 편이 목적에 맞습니다. 실습 서버가 `read_note`를 tool로 둔 이유입니다.

## 2. tool 정의

서버는 `tools/list` 요청에 도구 목록을 돌려줍니다. 도구 하나의 정의 [문서 확인 · 규격 2026-07-28]:

| 필드 | 필수 | 뜻 | 모델이 보나 |
| --- | --- | --- | --- |
| `name` | ✓ | 1~128자, 영숫자·`_`·`-`·`.`. 서버 안에서 유일 | ✓ (host가 `mcp__server__name`처럼 접두를 붙임) |
| `description` | | 무엇을 하는지. **모델이 도구를 고르는 근거** | ✓ |
| `inputSchema` | ✓ | 인자의 JSON Schema. 인자 없으면 `{"type":"object","additionalProperties":false}` 권장 | ✓ |
| `outputSchema` | | 구조화 결과의 JSON Schema | ✓ |
| `title` `icons` | | 표시용 | UI |
| `annotations` | | 동작 힌트: `readOnlyHint` `destructiveHint` `idempotentHint` `openWorldHint` | host 정책에 쓰임 |

규격의 JSON 필드명은 `readOnlyHint`처럼 camelCase입니다. Python SDK 2.x에서는 같은 필드를 `read_only_hint`처럼 snake_case로 씁니다.

SDK 2.x에서는 이것을 함수 하나로 만듭니다. 실습 서버의 `read_note` [실행 검증]:

```python
@server.tool(annotations=ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False))
def read_note(name: str) -> str:
    """이름으로 노트 한 편의 본문을 돌려준다. name은 '회의-0828' 또는 '회의-0828.md'."""
    ...
```

SDK가 만들어 보낸 정의를 LLM 없이 client로 받아 보면 다음과 같습니다 [실행 검증 · 실습 01].

```text
- read_note: 이름으로 노트 한 편의 본문을 돌려준다. name은 '회의-0828' 또는 '회의-0828.md'.
    input_schema={"type": "object", "properties": {"name": {"title": "Name", "type": "string"}}, "required": ["name"], ...}
    annotations={'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': False}
```

**docstring이 곧 `description`이고, 타입 힌트가 곧 `inputSchema`입니다.** 그러므로 docstring은 주석이 아니라 모델에게 보여 주는 문장입니다. skill의 `description`과 같은 원리로 "무엇을 하는지 + 인자를 어떻게 주는지"를 적습니다. 실습에서 `name은 '회의-0828' 또는 '회의-0828.md'`라고 적어 두자 두 도구 모두 확장자 유무를 헷갈리지 않고 호출했습니다.

### annotations는 힌트입니다

`readOnlyHint` 같은 annotation은 host가 승인 정책을 정할 때 참고합니다. 규격은 **"클라이언트는 신뢰하는 서버가 아니면 annotation을 신뢰하지 말아야 한다(MUST)"라고** 명시합니다 [문서 확인]. 서버가 거짓말을 해도 규약 수준에서 막을 방법이 없기 때문입니다. 실습 04에서 쓰기 도구에 `read_only_hint=True`를 달자 Codex가 승인 없이 실행했습니다 [실행 검증]. 자세한 내용은 [`05-permission-boundaries.md`](05-permission-boundaries.md)에서 다룹니다.

## 3. 결과의 모양

`tools/call` 결과 [문서 확인]:

```json
{
  "resultType": "complete",
  "content": [ { "type": "text", "text": "# 장보기\n\n- 우유, 달걀, 두부\n…" } ],
  "structuredContent": { "result": "# 장보기\n…" },
  "isError": false
}
```

- `content`: 비구조화 내용. `text` 외에 `image`·`audio`·`resource_link`·`resource`(embedded)가 있습니다.
- `structuredContent`: `outputSchema`를 정했을 때의 JSON 값. SDK 2.x는 반환 타입에서 자동으로 만든다(위 예의 `{"result": …}`). 호환을 위해 같은 내용을 `content`의 text로도 넣도록 권장됩니다.
- `isError`: **도구 실행 오류의** 표시. 아래 참조.

## 4. 오류는 두 종류

| 종류 | 언제 | 어떻게 돌아오나 | 모델이 보나 |
| --- | --- | --- | --- |
| **프로토콜 오류** | 없는 도구, schema에 안 맞는 요청, 서버 내부 오류 | JSON-RPC `error` (예: `-32602 Unknown tool`) | host 재량(MAY). 모델이 고치기 어려움 |
| **도구 실행 오류** | 잘못된 인자 값, 없는 파일, 업무 규칙 위반 | 정상 결과에 `isError: true` + 설명 text | host가 전달해야 함(SHOULD). 모델이 **자기 교정할** 수 있음 |

실습 서버에서 두 경우를 모두 관측했습니다 [실행 검증 · 실습 01].

```text
tools/call write_note  (--allow-write 없이 → 도구가 목록에 없음)
  → "Unknown tool: write_note", is_error=true            ← SDK는 이것도 결과로 감싸 돌려줌

tools/call read_note {"name": "../notes_server.py"}
  → "Error executing tool read_note: 허용되지 않는 경로: ../notes_server.py.md. 노트 폴더 안의 파일 이름만 받는다.", is_error=true
```

두 번째가 핵심입니다. 처음에는 `ValueError`를 던졌더니 SDK가 문구를 감추고 `Error executing tool read_note`만 돌려줬습니다. **SDK의 `ToolError`로 바꾸자 문구가 그대로 모델에게 전달됐습니다** [실행 검증]. 모델이 "그럼 `list_notes`로 이름을 확인하자"고 교정할 수 있으려면 오류 문구에 **다음 행동을** 적어야 합니다. 예를 들면 `노트가 없다: X. list_notes로 이름을 확인하라`와 같이 씁니다.

## 5. 상태는 어디에 두나

2026-07-28 판은 세션이 없습니다. 그래서 "장바구니를 만들고 → 담고 → 결제" 같은 연속 작업은 서버가 **핸들(불투명 문자열)을** 결과로 돌려주고 모델이 다음 호출 인자로 다시 넘기는 방식으로 처리합니다 [문서 확인]. 핸들은 이름이지 권한이 아니므로 서버는 호출마다 권한을 다시 확인해야 합니다. 실습 서버는 상태가 없어 이 문제가 없습니다. 처음 만드는 서버는 **무상태 읽기 도구로** 시작하는 편이 쉽습니다.

## 이 장을 끝내면

- tool 정의의 필수 필드(`name`·`inputSchema`)와 모델이 보는 것(`description`)을 설명할 수 있습니다.
- `isError` 실행 오류에 다음 행동을 적어 모델이 자기 교정하게 만듭니다.
- resources·prompts를 언제 사용하지 않아도 되는지 판단할 수 있습니다.
