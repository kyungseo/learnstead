#!/usr/bin/env python3
"""가장 작은 Local RAG — 임베딩 + 리스트 + 코사인 유사도.

사용법:
  python3 rag_minimal.py "연차는 며칠까지 이월할 수 있나요?"
  python3 rag_minimal.py "질문" --top-k 3 --threshold 0.5 --search hybrid
  python3 rag_minimal.py "질문" --chunk fixed:120      # 고정 길이 청킹 (실패 ② 재현용)
  python3 rag_minimal.py "질문" --no-rules              # 근거 제한 규칙 제거 (실패 ④ 재현용)
  python3 rag_minimal.py --show                        # 조각 목록만 출력
  python3 rag_minimal.py "질문" --docs graph_docs      # 다른 문서 묶음으로 색인 (실습 ⑤ 벡터 비교용)

전제: Ollama 실행 중, `ollama pull bge-m3`, `ollama pull gemma3:4b`, `pip install openai`
"""

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

from openai import OpenAI

EMBED_MODEL = "bge-m3"
CHAT_MODEL = "gemma3:4b"
DOCS_DIR = Path(__file__).parent / "docs"

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


# ---------------------------------------------------------------- (1)(2) 파싱·청킹
def load_chunks(mode: str, docs_dir: Path = DOCS_DIR) -> list[dict]:
    """docs/*.md 를 읽어 조각 목록을 만든다. 각 조각은 출처 메타데이터를 가진다."""
    chunks = []
    for path in sorted(docs_dir.glob("*.md")):
        title = path.stem
        section = ""
        for block in path.read_text(encoding="utf-8").split("\n\n"):
            block = block.strip()
            if not block or block.startswith("# "):
                continue
            if block.startswith("## "):
                section = block[3:].strip()
                continue
            if mode == "paragraph":
                pieces = [block]
            else:  # fixed:N — 문장·단락 경계를 무시하고 N자마다 자른다
                n = int(mode.split(":")[1])
                pieces = [block[i : i + n] for i in range(0, len(block), n)]
            for piece in pieces:
                chunks.append(
                    {
                        "id": len(chunks) + 1,
                        "source": f"{title} › {section}",
                        "text": f"[{title} › {section}]\n{piece}",
                    }
                )
    return chunks


# ---------------------------------------------------------------- (3)(5) 임베딩
def embed(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


# ---------------------------------------------------------------- (6) 검색
def dense_rank(query_vec, chunks) -> list[tuple[int, float]]:
    scored = [(c["id"], cosine(query_vec, c["vec"])) for c in chunks]
    return sorted(scored, key=lambda x: -x[1])


def bigrams(text: str) -> list[str]:
    """한국어 BM25용 단순 토큰화: 공백·기호를 제거한 2-gram + 영숫자 토큰."""
    words = re.findall(r"[A-Za-z0-9\-]+", text)
    compact = re.sub(r"[^가-힣A-Za-z0-9]", "", text)
    return words + [compact[i : i + 2] for i in range(len(compact) - 1)]


def bm25_rank(query: str, chunks, k1=1.5, b=0.75) -> list[tuple[int, float]]:
    docs = [bigrams(c["text"]) for c in chunks]
    avgdl = sum(len(d) for d in docs) / len(docs)
    df = Counter(t for d in docs for t in set(d))
    n = len(docs)
    scored = []
    for c, d in zip(chunks, docs):
        tf = Counter(d)
        score = 0.0
        for t in bigrams(query):
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avgdl))
        scored.append((c["id"], score))
    return sorted(scored, key=lambda x: -x[1])


def rrf(*rankings, k=60) -> list[tuple[int, float]]:
    fused = Counter()
    for ranking in rankings:
        for rank, (cid, _) in enumerate(ranking, start=1):
            fused[cid] += 1 / (k + rank)
    return fused.most_common()


# ---------------------------------------------------------------- (7)(8) 프롬프트·생성
RULES = (
    "너는 사내 문서 도우미다. 아래 <근거>에 있는 내용만으로 답한다. "
    "근거에 없는 내용은 '문서에서 찾지 못했습니다'라고 답한다. "
    "답의 각 문장 끝에 사용한 근거 번호를 [1], [2]처럼 붙인다."
)
NO_RULES = "너는 친절한 도우미다. 질문에 답한다."


def answer(question: str, hits: list[dict], rules: bool) -> str:
    evidence = "\n".join(f"[{i}] {h['text']}" for i, h in enumerate(hits, start=1))
    user = f"<근거>\n{evidence}\n</근거>\n\n질문: {question}"
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": RULES if rules else NO_RULES},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=0.0, help="dense 점수 하한 (0이면 끔)")
    ap.add_argument("--search", choices=["dense", "bm25", "hybrid"], default="dense")
    ap.add_argument("--chunk", default="paragraph", help="paragraph | fixed:N")
    ap.add_argument("--no-rules", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--docs", default="docs", help="문서 디렉터리 (기본 docs)")
    args = ap.parse_args()

    chunks = load_chunks(args.chunk, Path(__file__).parent / args.docs)
    if args.show:
        for c in chunks:
            print(f"--- #{c['id']} {c['source']} ({len(c['text'])}자)\n{c['text']}\n")
        return
    if not args.question:
        ap.error("질문을 입력하세요")

    # 색인 시점: 조각 임베딩 (문서가 작으므로 매 실행 시 다시 계산)
    for c, v in zip(chunks, embed([c["text"] for c in chunks])):
        c["vec"] = v

    # 질의 시점: 검색
    by_id = {c["id"]: c for c in chunks}
    dense = dense_rank(embed([args.question])[0], chunks)
    dense_score = dict(dense)
    if args.search == "dense":
        ranking = dense
    elif args.search == "bm25":
        ranking = bm25_rank(args.question, chunks)
    else:
        ranking = rrf(dense, bm25_rank(args.question, chunks))

    hits = []
    for cid, _ in ranking[: args.top_k]:
        if args.threshold and dense_score[cid] < args.threshold:
            continue
        hits.append(by_id[cid])

    print(f"검색: {args.search} · top-k {args.top_k} · threshold {args.threshold} · chunk {args.chunk}\n")
    if not hits:
        print("답변: 관련 문서를 찾지 못했습니다. (점수 하한 미달 — 모델을 호출하지 않음)")
        return

    print("답변:", answer(args.question, hits, rules=not args.no_rules), "\n")
    print("근거:")
    for i, h in enumerate(hits, start=1):
        print(f" [{i}] #{h['id']} {h['source']}  (dense {dense_score[h['id']]:.2f})")
    print("\n판정 힌트: 답에 인용된 번호의 조각 안에 그 내용이 실제로 있는가?")


if __name__ == "__main__":
    sys.exit(main())
