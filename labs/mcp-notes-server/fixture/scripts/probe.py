#!/usr/bin/env python3
"""LLM 없이 서버를 직접 호출한다. tools/list와 tools/call의 원문을 본다.

사용법: python3 scripts/probe.py [--allow-write] [--call TOOL JSON_ARGS]
예:     python3 scripts/probe.py
        python3 scripts/probe.py --call read_note '{"name": "장보기"}'
        python3 scripts/probe.py --call read_note '{"name": "../notes_server.py"}'
"""
import argparse, asyncio, json, sys
from pathlib import Path
from mcp import Client
from mcp.client.stdio import StdioServerParameters

HERE = Path(__file__).resolve().parent.parent


async def main(allow_write: bool, call):
    args = [str(HERE / "notes_server.py")] + (["--allow-write"] if allow_write else [])
    params = StdioServerParameters(command=sys.executable, args=args)
    async with Client(params) as client:
        tools = await client.list_tools()
        print("== tools/list")
        for t in tools.tools:
            ann = t.annotations.model_dump(exclude_none=True) if t.annotations else {}
            print(f"- {t.name}: {t.description}\n    input_schema={json.dumps(t.input_schema, ensure_ascii=False)}\n    annotations={ann}")
        if call:
            name, raw = call
            print(f"== tools/call {name} {raw}")
            res = await client.call_tool(name, json.loads(raw))
            print(json.dumps(res.model_dump(exclude_none=True), ensure_ascii=False, indent=1)[:1500])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-write", action="store_true")
    ap.add_argument("--call", nargs=2, metavar=("TOOL", "JSON_ARGS"))
    a = ap.parse_args()
    asyncio.run(main(a.allow_write, a.call))
