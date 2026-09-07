#!/usr/bin/env python3
"""실행 디렉터리 하나를 채점한다.

사용: python3 scripts/score.py runs/<실행이름>/<도구-시나리오-rN> [...]
출력: 실행마다 JSON 한 줄(--tsv면 TSV 한 줄). 골든셋은 expected/golden.json.

Claude Code: result.usage(메인)와 modelUsage(전체)의 차로 위임 입력을 구한다.
hits = 결함 위치 일치, outside_golden = 골든셋 밖 지적. 설명의 정확성은 판정하지 않는다.
Codex: rollouts/*.jsonl에서 스레드별 token_count와 spawn_agent 호출 수를 센다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FX = Path(__file__).resolve().parent.parent
GOLDEN = json.loads((FX / "expected" / "golden.json").read_text(encoding="utf-8"))
BUGS = {(b["file"].split("/")[-1], b["function"]) for b in GOLDEN["bugs"]}
CLEAN = {c.split("/")[-1] for c in GOLDEN["clean"]}


def extract_findings(text: str) -> list[dict] | None:
    """본문에서 {"findings": [...]} JSON을 찾는다. 코드펜스 안이어도 된다."""
    for m in re.finditer(r"\{[^{}]*\"findings\"\s*:\s*\[.*?\]\s*\}", text, re.S):
        try:
            return json.loads(m.group(0))["findings"]
        except json.JSONDecodeError:
            continue
    return None


def judge(findings: list[dict] | None) -> dict:
    # false_positives는 과거 소비자용 alias다. 오탐의 진위를 판정하는 값이 아니다.
    contract = {"metric": "location_match", "semantic_correctness": "not_evaluated"}
    if not isinstance(findings, list) or not all(isinstance(f, dict) for f in findings):
        return {**contract, "parsed": False, "hits": 0, "outside_golden": 0,
                "false_positives": 0, "clean_flagged": 0, "n": 0}
    hits, fp, clean = set(), 0, 0
    for f in findings:
        key = (str(f.get("file", "")).split("/")[-1], str(f.get("function", "")).strip("`"))
        if key in BUGS:
            hits.add(key)
        else:
            fp += 1
            if key[0] in CLEAN:
                clean += 1
    return {**contract, "parsed": True, "hits": len(hits), "outside_golden": fp, "false_positives": fp, "clean_flagged": clean, "n": len(findings),
            "hit_names": sorted(k[1] for k in hits)}


def usage_claude(path: Path) -> dict:
    """result.usage = 메인 대화만. modelUsage 합계 = 메인 + subagent 전부. 차이가 위임분이다.
    (stream의 assistant 메시지별 usage는 content block마다 같은 스냅샷이 반복돼 합산하면 틀린다.)"""
    zero = {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0}
    main, total = dict(zero), dict(zero)
    turns, agent_calls, agent_types = 0, 0, []
    result_text, cost, models, session, last_ctx = "", None, [], None, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "assistant":
            if not ev.get("parent_tool_use_id"):
                u = ev.get("message", {}).get("usage", {}) or {}
                last_ctx = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            for c in ev.get("message", {}).get("content", []) or []:
                if c.get("type") == "tool_use" and c.get("name") in ("Agent", "Task"):
                    agent_calls += 1
                    agent_types.append((c.get("input") or {}).get("subagent_type", "?"))
        elif t == "result":
            result_text = ev.get("result", "") or ""
            cost = ev.get("total_cost_usd"); turns = ev.get("num_turns"); session = ev.get("session_id")
            u = ev.get("usage") or {}
            main = {"in": u.get("input_tokens", 0), "out": u.get("output_tokens", 0),
                    "cache_read": u.get("cache_read_input_tokens", 0), "cache_write": u.get("cache_creation_input_tokens", 0)}
            mu = ev.get("modelUsage") or {}
            models = sorted(mu.keys())
            total = {"in": sum(v.get("inputTokens", 0) for v in mu.values()), "out": sum(v.get("outputTokens", 0) for v in mu.values()),
                     "cache_read": sum(v.get("cacheReadInputTokens", 0) for v in mu.values()),
                     "cache_write": sum(v.get("cacheCreationInputTokens", 0) for v in mu.values())}
    sub = {k: max(total[k] - main[k], 0) for k in zero}
    return {"main": main, "sub": sub, "total": total, "main_ctx_last": last_ctx, "turns": turns, "agent_calls": agent_calls, "agent_types": agent_types,
            "cost_usd": cost, "models": models, "session_id": session, "result_text": result_text}


def usage_codex(run: Path) -> dict:
    stream = run / "stream.jsonl"
    result_text, turn_usage = "", None
    for line in stream.read_text(encoding="utf-8").splitlines() if stream.exists() else []:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "item.completed" and ev.get("item", {}).get("type") == "agent_message":
            result_text = ev["item"].get("text", "")
        elif ev.get("type") == "turn.completed":
            turn_usage = ev.get("usage")
    threads, spawns = {}, 0
    for f in sorted((run / "rollouts").glob("*.jsonl")) if (run / "rollouts").exists() else []:
        parent, last, last_ctx = None, None, 0
        for line in f.read_text(encoding="utf-8").splitlines():
            if '"parent_thread_id"' in line and parent is None:
                m = re.search(r'"parent_thread_id":"([^"]+)"', line); parent = m.group(1) if m else None
            if '"spawn_agent"' in line and '"name":"spawn_agent"' in line:
                spawns += 1
            if '"type":"token_count"' in line:
                try:
                    ev = json.loads(line); info = ev.get("payload", {}).get("info") or {}
                    tu = info.get("total_token_usage") or {}
                    if tu: last = tu
                    lu = info.get("last_token_usage") or {}
                    if lu: last_ctx = lu.get("input_tokens", 0)
                except json.JSONDecodeError:
                    pass
        threads[f.name] = {"parent": parent, "usage": last, "last_ctx": last_ctx}
    sub_threads = {k: v for k, v in threads.items() if v["parent"] is not None}
    tu = turn_usage or {}
    # Codex input_tokens는 cached 포함 총량. 메인은 스트림의 turn.completed, 위임분은 자식 rollout의 token_count 합.
    main = {"in": tu.get("input_tokens", 0), "out": tu.get("output_tokens", 0), "cached": tu.get("cached_input_tokens", 0)}
    sub = {"in": sum((v["usage"] or {}).get("input_tokens", 0) for v in sub_threads.values()),
           "out": sum((v["usage"] or {}).get("output_tokens", 0) for v in sub_threads.values()),
           "cached": sum((v["usage"] or {}).get("cached_input_tokens", 0) for v in sub_threads.values())}
    main_threads = {k: v for k, v in threads.items() if v["parent"] is None}
    main_ctx = max((v.get("last_ctx", 0) for v in main_threads.values()), default=0)
    return {"main": main, "sub": sub, "main_ctx_last": main_ctx, "threads": {"main": len(main_threads), "sub": len(sub_threads)},
            "spawn_calls": spawns, "result_text": result_text}


def score(run: Path) -> dict:
    tool = run.name.split("-")[0]
    out = {"run": run.name, "tool": tool}
    u = usage_claude(run / "stream.jsonl") if tool == "claude" else usage_codex(run)
    text = u.pop("result_text", "")
    fu = run / ("stream-followup.jsonl")
    if fu.exists():
        u2 = usage_claude(fu) if tool == "claude" else {"result_text": ""}
        if tool == "codex":
            for line in fu.read_text(encoding="utf-8").splitlines():
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "item.completed" and ev.get("item", {}).get("type") == "agent_message":
                    u2["result_text"] = ev["item"].get("text", "")
        text = u2.pop("result_text", "") or text
        # 이어 가기 시나리오: main_* = 검토 턴(followup)만, writer_* = 작성 턴
        if tool == "claude":
            u["writer"] = {"main": u["main"], "sub": u["sub"], "main_ctx_last": u.get("main_ctx_last")}
            u["main"], u["sub"], u["main_ctx_last"] = u2["main"], u2["sub"], u2.get("main_ctx_last")
        else:
            u["writer"] = {"main": u["main"], "main_ctx_last": u.get("main_ctx_last")}
            tu2 = {}
            for line in fu.read_text(encoding="utf-8").splitlines():
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "turn.completed":
                    tu2 = ev.get("usage") or {}
            u["main"] = {"in": tu2.get("input_tokens", 0), "out": tu2.get("output_tokens", 0), "cached": tu2.get("cached_input_tokens", 0)}
        u["followup"] = u2
    out.update(u)
    out["judge"] = judge(extract_findings(text))
    out["manual_review_required"] = True
    # worktree 2프로세스의 토큰은 기존 수집 계약으로 합산하지 않는다. 0 사용으로 표시하지 않는다.
    out["usage_available"] = not (run / "stream-x.jsonl").exists()
    out["exit_codes"] = {p.stem: int(p.read_text().strip()) for p in sorted(run.glob("exit_code*.txt"))}
    out["answer_excerpt"] = text[:400]
    out["wall_seconds"] = float((run / "wall_seconds.txt").read_text().strip()) if (run / "wall_seconds.txt").exists() else None
    if (run / "wall_followup_seconds.txt").exists():
        out["writer_wall_seconds"] = out["wall_seconds"]
        out["wall_seconds"] = float((run / "wall_followup_seconds.txt").read_text().strip())
    for field, filename in (("wall_edit_seconds", "wall_edit_seconds.txt"),
                            ("wall_integration_seconds", "wall_integration_seconds.txt"),
                            ("wall_total_seconds", "wall_total_seconds.txt")):
        out[field] = float((run / filename).read_text().strip()) if (run / filename).exists() else None
    out["integration_status"] = (run / "integration_status.txt").read_text().strip() if (run / "integration_status.txt").exists() else None
    out["worker_tests"] = {w: (run / f"tests-{w}.txt").read_text().strip().splitlines()[-1]
                           for w in ("x", "y") if (run / f"tests-{w}.txt").exists()}
    out["tests"] = (run / "tests.txt").read_text().strip().splitlines()[-1] if (run / "tests.txt").exists() else None
    out["diff_stat"] = (run / "diff-stat.txt").read_text().strip() if (run / "diff-stat.txt").exists() else ""
    out["stderr_tail"] = (run / "stderr.txt").read_text().strip().splitlines()[-1:] if (run / "stderr.txt").exists() else []
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--tsv", action="store_true")
    a = ap.parse_args()
    if a.tsv:
        print("run\tmain_in_total\tmain_ctx_last\tmain_out\tsub_in_total\tsub_out\tagent_or_spawn\thits\tfp\tclean_flagged\twall_s\ttests\twall_total_s\tintegration")
    for r in a.runs:
        s = score(Path(r))
        if a.tsv:
            j = s["judge"]; m, sb = s["main"], s["sub"]
            calls = s.get("agent_calls", s.get("spawn_calls"))
            mi = m['in'] + m.get('cache_read', 0) + m.get('cache_write', 0)
            si = sb['in'] + sb.get('cache_read', 0) + sb.get('cache_write', 0)
            if not s["usage_available"]:
                mi = si = "NA"
                s["main_ctx_last"] = m["out"] = sb["out"] = "NA"
            print(f"{s['run']}\t{mi}\t{s.get('main_ctx_last')}\t{m['out']}\t{si}\t{sb['out']}\t{calls}\t{j['hits']}\t{j['false_positives']}\t{j['clean_flagged']}\t{s['wall_seconds']}\t{s['tests']}\t{s['wall_total_seconds']}\t{s['integration_status']}")
        else:
            print(json.dumps(s, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
