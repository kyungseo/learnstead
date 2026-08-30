#!/usr/bin/env python3
"""rag_skeleton.py 의 저장소를 Python 리스트에서 Chroma(파일 기반 vector store)로 바꾼 버전.

사용법:
  python3 rag_chroma.py --index                 # 색인 시점: 조각을 임베딩해 ./chroma_db 에 저장
  python3 rag_chroma.py "연차는 며칠까지 이월할 수 있나요?"   # 질의 시점
  python3 rag_chroma.py --reset                 # 색인 삭제 (초기화)

전제: rag_skeleton.py 와 같은 디렉터리, `pip install openai chromadb`
"""

import argparse
import shutil
import sys
from pathlib import Path

import chromadb

from rag_skeleton import answer, embed, load_chunks

DB_DIR = Path(__file__).parent / "chroma_db"
COLLECTION = "company-docs"


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    # cosine 공간으로 만들면 distance = 1 - cosine 유사도 (Chroma 1.x: configuration으로 지정)
    return client.get_or_create_collection(COLLECTION, configuration={"hnsw": {"space": "cosine"}})


def index():
    chunks = load_chunks()
    col = get_collection()
    col.upsert(
        ids=[str(c["id"]) for c in chunks],
        embeddings=embed([c["text"] for c in chunks]),
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    print(f"색인 완료: {col.count()}개 조각 → {DB_DIR}")


def ask(question: str, top_k: int):
    col = get_collection()
    if col.count() == 0:
        sys.exit("색인이 비어 있습니다. 먼저 --index 를 실행하세요.")
    res = col.query(query_embeddings=embed([question]), n_results=top_k, include=["documents", "metadatas", "distances"])
    hits = [
        {"id": cid, "text": doc, "source": meta["source"], "score": 1 - dist}
        for cid, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]
    print("답변:", answer(question, hits), "\n")
    print("근거:")
    for i, h in enumerate(hits, start=1):
        print(f" [{i}] #{h['id']} {h['source']}  (score {h['score']:.2f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--top-k", type=int, default=3)
    args = ap.parse_args()

    if args.reset:
        shutil.rmtree(DB_DIR, ignore_errors=True)
        print("색인을 삭제했습니다.")
    elif args.index:
        index()
    elif args.question:
        ask(args.question, args.top_k)
    else:
        ap.error("--index, --reset 또는 질문 중 하나가 필요합니다")


if __name__ == "__main__":
    main()
