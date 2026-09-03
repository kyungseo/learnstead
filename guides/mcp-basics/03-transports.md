# 03. 연결 — stdio와 Streamable HTTP

> 이전 ← [`02-what-a-server-offers.md`](02-what-a-server-offers.md) · 다음 → [`04-connecting-to-tools.md`](04-connecting-to-tools.md)

## 이 장에서 답하는 질문

- 서버는 어떻게 떠 있고 host는 어떻게 말을 거는가
- stdio 서버가 지켜야 할 규칙은 무엇이고 어기면 무슨 일이 나는가
- 언제 HTTP로 가는가

## 1. 두 전송

규격은 전송(transport)을 "메시지를 어떻게 싣고 나르는가"의 binding으로만 정의합니다. 메시지의 의미는 전송 방식과 무관하게 같습니다 [문서 확인 · 규격 2026-07-28].

| | stdio | Streamable HTTP |
| --- | --- | --- |
| 서버 위치 | host가 **서브프로세스로 띄운다** | 어딘가에서 이미 떠 있는 HTTP endpoint |
| 메시지 | stdin/stdout에 한 줄에 하나(newline-delimited JSON-RPC) | 단일 endpoint에 POST, 응답은 JSON 또는 요청 단위 SSE 스트림 |
| 수명 | host가 켜고 끈다. stdin 닫힘 = 종료 신호 | 서버가 독립. 인증(OAuth 등) 필요 |
| 적합 | 내 장비의 파일·DB·CLI를 감싸는 개인 도구 | 팀·원격·다중 사용자, 이미 서비스로 돌아가는 것 |
| 실습 | ✓ (`notes_server.py`) | 범위 밖 |

Streamable HTTP는 2025-03-26 개정판에서 기존 HTTP+SSE 전송을 대체했습니다. 2026-07-28 개정판에서는 서버→클라이언트 요청이
폐지되어 전송 흐름이 더 단순해졌습니다 [문서 확인].

## 2. stdio 규칙

host는 설정에 적힌 명령(`python notes_server.py`)을 실행하고 그 프로세스의 stdin에 요청을 쓰고 stdout에서 응답을 읽습니다. 규칙 [문서 확인]:

- 서버는 **stdout에 MCP 메시지가 아닌 것을 쓰면 안 된다(MUST NOT)**. 로그는 **stderr로**.
- 메시지 하나가 한 줄. 줄바꿈을 포함하면 안 된다(SDK가 처리한다).
- 클라이언트는 stdin을 닫아 종료를 알리고, 서버는 EOF를 받으면 즉시 종료해야 한다(SHOULD).
- 서버가 예기치 않게 죽으면 클라이언트는 재시작해야 한다(SHOULD). 무상태라 진행 중 요청은 그냥 다시 보냅니다.

실습 서버는 다음과 같이 이 규칙을 지킵니다.

```python
def log(msg): print(f"[notes] {msg}", file=sys.stderr, flush=True)   # stdout 금지
...
server.run(transport="stdio")
```

### 어기면 무슨 일이 나나 — 관측

`print("starting notes server")`를 stdout에 한 줄 넣어 봤습니다 [실행 검증 · 실습 04].

- SDK 2.1.1 client: `ValidationError: Invalid JSON … input_value='starting notes server'`를 stderr에 찍고 **그 줄을 버린 뒤 계속 진행**. 도구 목록 정상.
- Claude Code 2.1.251: 연결 `connected`, 도구 호출 정상. 도구 실행 중간에 `print()`를 넣어도 같았습니다.

즉 최신 클라이언트 둘은 잘못된 줄을 **건너뜁니다.** 그러나 이것은 규격 위반이고, 줄을 버리는 것은 클라이언트 재량입니다. 다른 host나 이전 판 클라이언트가 어떻게 하는지는 확인하지 못했습니다 [미검증]. 지금 동작하더라도 **stdout은 비워 두는 것이** 규칙입니다. 특히 서버가 import하는 라이브러리가 stdout에 무언가를 찍는 경우가 흔해서, 로그 설정을 stderr로 돌려 두는 습관이 필요합니다.

## 3. 무상태와 `_meta`

2026-07-28 판은 연결 단위 세션이 없습니다. 요청마다 `_meta`에 프로토콜 버전과 클라이언트 capability가 실려 옵니다 [문서 확인]. 서버 입장에서는 "이 요청이 첫 요청인가"를 따질 필요가 없고, 클라이언트 입장에서는 서버가 죽어도 다시 띄워 재요청하면 됩니다. 실습에서 Claude Code를 실행할 때마다 서버 프로세스가 새로 뜨고 끝났으며, stderr 로그의 `serving … write=off`도 매번 찍혔습니다 [실행 검증].

결과에는 서버 정보도 함께 들어옵니다.

```json
"meta": {"io.modelcontextprotocol/serverInfo": {"name": "notes", "version": "1.0"}}
```

## 4. 언제 HTTP로 가나

- 서버를 **여러 사람·여러 장비가** 써야 합니다.
- 서버가 이미 **서비스로** 실행되고 있습니다(사내 API 앞단).
- 인증·권한을 서버 쪽에서 통제해야 합니다 → OAuth. Claude Code는 `claude mcp login`, Codex는 `codex mcp login`으로 연결합니다 [문서 확인].

개인 도구는 stdio로 시작합니다. SDK 2.x는 같은 서버 객체를 `server.run(transport="streamable-http", host="127.0.0.1", port=8000)`로 띄울 수 있어 나중에 바꾸기 쉽습니다 [문서 확인 · SDK v2 migration]. HTTP로 전환할 때는 규격에 따라 `Origin`을 검증하고, 로컬 서버는 localhost에만 bind하며, 인증을 적용해야 합니다 [문서 확인].

## 이 장을 끝내면

- stdio 서버의 세 규칙(stdout 금지·한 줄 한 메시지·EOF 종료)을 말할 수 있습니다.
- 잘못된 stdout이 최신 클라이언트에서 "살아남는" 이유와 그래도 규칙을 지켜야 하는 이유를 설명할 수 있습니다.
- 개인 도구는 stdio, 공유·서비스는 HTTP로 구분할 수 있습니다.
