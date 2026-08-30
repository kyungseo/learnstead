#!/usr/bin/env python3
"""가장 작은 GraphRAG — LLM으로 (주어, 관계, 목적어) 트리플을 뽑아 그래프를 만들고, 질문의 개체에서 이웃을 따라간다.

사용법:
  python3 graph_minimal.py --build                 # 색인 시점: graph_docs/*.md → 트리플 추출 → graph.json
  python3 graph_minimal.py "검색 고도화 프로젝트 담당자가 속한 팀의 팀장은 누구인가요?"
  python3 graph_minimal.py "질문" --hops 2         # 탐색 깊이 조절 (기본 3)
  python3 graph_minimal.py --reset

전제: Ollama 실행 중, `ollama pull gemma3:4b`, `pip install openai networkx`
"""

import argparse
import json
import sys
from pathlib import Path

import networkx as nx
from openai import OpenAI

CHAT_MODEL = "gemma3:4b"
DOCS_DIR = Path(__file__).parent / "graph_docs"
GRAPH_FILE = Path(__file__).parent / "graph.json"

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

TRIPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "triples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "relation": {"type": "string"},
                    "object": {"type": "string"},
                },
                "required": ["subject", "relation", "object"],
            },
        }
    },
    "required": ["triples"],
}


# ---------------------------------------------------------------- (3') 개체·관계 추출
def extract_triples(text: str) -> list[dict]:
    """한 단락에서 (주어, 관계, 목적어) 목록을 JSON으로 받는다. 구조화 출력으로 형식을 강제한다."""
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        response_format={"type": "json_schema", "json_schema": {"name": "triples", "schema": TRIPLE_SCHEMA}},
        messages=[
            {
                "role": "system",
                "content": (
                    "문장에서 사실을 (subject, relation, object) 트리플로 추출한다. "
                    "subject와 object는 문장에 나온 고유 명칭을 그대로 쓴다(예: '플랫폼팀', '김서연', '검색 고도화 프로젝트'). "
                    "relation은 '팀장', '소속', '담당자', '예산', '종료', '검토'처럼 짧은 명사로 쓴다."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return json.loads(resp.choices[0].message.content)["triples"]


def build():
    graph = nx.DiGraph()
    for path in sorted(DOCS_DIR.glob("*.md")):
        for block in path.read_text(encoding="utf-8").split("\n\n"):
            block = block.strip()
            if not block or block.startswith("#"):
                continue
            for t in extract_triples(block):
                graph.add_edge(t["subject"], t["object"], relation=t["relation"], source=f"{path.stem}")
                print(f"  {t['subject']} --{t['relation']}--> {t['object']}")
    edges = [[u, v, d["relation"], d["source"]] for u, v, d in graph.edges(data=True)]
    GRAPH_FILE.write_text(json.dumps({"edges": edges}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n그래프 저장: 노드 {graph.number_of_nodes()}개, 엣지 {graph.number_of_edges()}개 → {GRAPH_FILE}")


def load() -> nx.DiGraph:
    if not GRAPH_FILE.exists():
        sys.exit("그래프가 없습니다. 먼저 --build 를 실행하세요.")
    graph = nx.DiGraph()
    for u, v, relation, source in json.loads(GRAPH_FILE.read_text(encoding="utf-8"))["edges"]:
        graph.add_edge(u, v, relation=relation, source=source)
    return graph


# ---------------------------------------------------------------- (6') 그래프 탐색
def seed_entities(question: str, graph: nx.DiGraph) -> list[str]:
    """질문 문자열에 이름이 그대로 등장하는 노드를 출발점으로 삼는다 (가장 단순한 entity linking)."""
    return [n for n in graph.nodes if n in question]


def neighborhood(graph: nx.DiGraph, seeds: list[str], hops: int) -> list[tuple[str, str, str, str]]:
    und = graph.to_undirected(as_view=True)
    reached = set(seeds)
    frontier = set(seeds)
    for _ in range(hops):
        frontier = {m for n in frontier for m in und.neighbors(n)} - reached
        reached |= frontier
    facts = []
    for u, v, d in graph.edges(data=True):
        if u in reached and v in reached:
            facts.append((u, d["relation"], v, d["source"]))
    return facts


def ask(question: str, hops: int):
    graph = load()
    seeds = seed_entities(question, graph)
    facts = neighborhood(graph, seeds, hops)
    print(f"출발 개체: {seeds}  ·  {hops}홉 이내 사실 {len(facts)}개\n")
    if not facts:
        print("답변: 질문에서 그래프의 개체를 찾지 못했습니다.")
        return
    evidence = "\n".join(
        f"[{i}] {s} —{r}→ {o} (출처: {source})"
        for i, (s, r, o, source) in enumerate(facts, start=1)
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "아래 <사실>만으로 답한다. 없는 내용은 '찾지 못했습니다'라고 답한다. 사용한 사실 번호를 [n]으로 붙인다.",
            },
            {"role": "user", "content": f"<사실>\n{evidence}\n</사실>\n\n질문: {question}"},
        ],
    )
    print("답변:", resp.choices[0].message.content, "\n")
    print("근거 사실:\n" + evidence)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--hops", type=int, default=3)
    args = ap.parse_args()
    if args.reset:
        GRAPH_FILE.unlink(missing_ok=True)
        print("graph.json 을 삭제했습니다.")
    elif args.build:
        build()
    elif args.question:
        ask(args.question, args.hops)
    else:
        ap.error("--build, --reset 또는 질문 중 하나가 필요합니다")


if __name__ == "__main__":
    main()
