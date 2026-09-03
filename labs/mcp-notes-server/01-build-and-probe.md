# 01. 서버 만들고 LLM 없이 호출하기

> 다음 → [`02-connect-claude-code.md`](02-connect-claude-code.md)

## 목표

`notes_server.py`를 읽고, SDK `Client`로 서버를 서브프로세스로 띄워 `tools/list`와 `tools/call`의 원문을 봅니다. 모델이 끼기 전에 서버 혼자 무엇을 하는지 확정합니다.

## 1. 서버 읽기

```bash
cat notes_server.py
```

볼 것:

- `MCPServer(name="notes", instructions=…)` — 서버 하나.
- `@server.tool(annotations=READ_ONLY)` 세 개 — docstring이 description, 타입 힌트가 `inputSchema`.
- `_safe_path()` — `resolve()`한 경로의 부모가 노트 폴더인지 확인. **경계는 여기서 강제됩니다.**
- `ToolError` — 오류 문구를 모델에게 그대로 전달.
- `enable_write()` — `--allow-write`일 때만 `write_note`를 등록. 없으면 도구 자체가 없습니다.
- `log()`는 stderr, `server.run(transport="stdio")`.

## 2. 도구 목록

```bash
"$MCP_NOTES_PYTHON" scripts/probe.py
```

서버 프로세스가 뜨고(stderr에 `[notes] serving … write=off`), `tools/list` 결과가 도구별로 description·`input_schema`·annotations와 함께 나옵니다. `write_note`가 **없는지** 확인합니다.

## 3. 호출 세 가지

```bash
"$MCP_NOTES_PYTHON" scripts/probe.py --call read_note '{"name": "장보기"}'
"$MCP_NOTES_PYTHON" scripts/probe.py --call read_note '{"name": "../notes_server.py"}'
"$MCP_NOTES_PYTHON" scripts/probe.py --call write_note '{"name": "x", "content": "y"}'
```

각 결과의 `content[0].text`, `is_error`, `result_type`을 봅니다. 그리고:

```bash
"$MCP_NOTES_PYTHON" scripts/probe.py --allow-write | grep "^- "
```

`write_note`가 목록에 나타납니다.

## 4. 기록

| 호출 | `is_error` | text 첫 줄 |
| --- | --- | --- |
| read_note 장보기 | | |
| read_note ../notes_server.py | | |
| write_note (플래그 없음) | | |

## 작성 환경의 실제 결과

```text
== tools/list
- list_notes: 노트 폴더의 파일 이름을 나열한다.
    input_schema={"type": "object", "properties": {}, "title": "list_notesArguments"}
    annotations={'read_only_hint': True, 'destructive_hint': False, 'open_world_hint': False}
- read_note: 이름으로 노트 한 편의 본문을 돌려준다. name은 '회의-0828' 또는 '회의-0828.md'.
    input_schema={"type": "object", "properties": {"name": {"title": "Name", "type": "string"}}, "required": ["name"], …}
- search_notes: 모든 노트에서 query를 포함한 줄을 찾는다. [{name, line, text}] 목록.
```

| 호출 | `is_error` | text |
| --- | --- | --- |
| read_note 장보기 | false | `# 장보기\n\n- 우유, 달걀, 두부 …` (+ `structured_content: {"result": …}`, `result_type: complete`) |
| read_note ../notes_server.py | **true** | `Error executing tool read_note: 허용되지 않는 경로: ../notes_server.py.md. 노트 폴더 안의 파일 이름만 받는다.` |
| write_note (플래그 없음) | **true** | `Unknown tool: write_note` |

처음 서버는 `ValueError`를 던졌고 그때 text는 `Error executing tool read_note`뿐이었습니다. `ToolError`로 바꾸자 문구가 전달됐습니다. 결과의 `meta`에는 `io.modelcontextprotocol/serverInfo: {name: notes, version: 1.0}`이 함께 왔습니다.

## 흔한 실패 · 복구

| 증상 | 원인 | 복구 |
| --- | --- | --- |
| `No module named 'mcp.server.mcpserver'` | SDK 1.x 설치 | `pip install "mcp==2.1.1"` |
| `No module named 'mcp'` | 다른 python | `setup.sh`에 준 python 경로로 실행 |
| probe가 멈춤 | 서버가 stdout에 무언가 씀 / import 오류 | 터미널에서 `"$MCP_NOTES_PYTHON" notes_server.py`를 직접 띄워 stderr 확인, Ctrl-C |
