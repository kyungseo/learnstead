#!/usr/bin/env python3
"""가장 작은 Local RAG 뼈대 — 임베딩 + 리스트 + 코사인 유사도 + 근거 규칙.

사용법:
  python3 rag_skeleton.py "연차는 며칠까지 이월할 수 있나요?"
  python3 rag_skeleton.py "질문" --top-k 8
  python3 rag_skeleton.py --show                       # 조각 목록만 출력 (모델 호출 없음)

전제: Ollama 실행 중, `ollama pull bge-m3`, `ollama pull gemma3:4b`, `pip install openai`
"""

import argparse
import math
from pathlib import Path

from openai import OpenAI

EMBED_MODEL = "bge-m3"
CHAT_MODEL = "gemma3:4b"
DOCS_DIR = Path(__file__).parent / "docs"
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

RULES = (
    "너는 사내 문서 도우미다. 아래 <근거>에 있는 내용만으로 답한다. "
    "근거에 없는 내용은 '문서에서 찾지 못했습니다'라고 답한다. "
    "답의 각 문장 끝에 사용한 근거 번호를 [1], [2]처럼 붙인다."
)


def positive_int(value: str) -> int:
    """argparse용 1 이상의 정수 검사."""
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("1 이상의 정수를 입력하세요") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("1 이상의 정수를 입력하세요")
    return number


# ------------------------------------------------ (1)(2) 파싱·청킹: 단락마다 한 조각, 앞에 [파일 › 절] 출처
def load_chunks() -> list[dict]:
    chunks = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        section = ""
        for block in path.read_text(encoding="utf-8").split("\n\n"):
            block = block.strip()
            if not block or block.startswith("# "):
                continue
            if block.startswith("## "):
                section = block[3:].strip()
                continue
            source = f"{path.stem} › {section}"
            chunks.append({"id": len(chunks) + 1, "source": source, "text": f"[{source}]\n{block}"})
    return chunks


# ------------------------------------------------ (3)(5) 임베딩: 색인과 질의가 같은 함수·같은 모델을 쓴다
def embed(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


# ------------------------------------------------ (6) 검색: 질문 벡터와 가까운 조각 k개
def search(question: str, chunks: list[dict], top_k: int) -> list[dict]:
    qvec = embed([question])[0]
    for c in chunks:
        c["score"] = cosine(qvec, c["vec"])
    return sorted(chunks, key=lambda c: -c["score"])[:top_k]


# ------------------------------------------------ (7)(8) 프롬프트 조립·생성: 규칙 → 번호 붙인 근거 → 질문
def answer(question: str, hits: list[dict]) -> str:
    evidence = "\n".join(f"[{i}] {h['text']}" for i, h in enumerate(hits, start=1))
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": RULES},
            {"role": "user", "content": f"<근거>\n{evidence}\n</근거>\n\n질문: {question}"},
        ],
    )
    return resp.choices[0].message.content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--top-k", type=positive_int, default=3, help="검색할 조각 수 (1 이상)")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    chunks = load_chunks()
    if args.show:
        for c in chunks:
            print(f"--- #{c['id']} {c['source']} ({len(c['text'])}자)\n{c['text']}\n")
        return
    if not args.question:
        ap.error("질문을 입력하세요")

    for c, v in zip(chunks, embed([c["text"] for c in chunks])):  # 색인 시점 (문서가 작아 매번 다시 계산)
        c["vec"] = v
    hits = search(args.question, chunks, args.top_k)  # 질의 시점

    print("답변:", answer(args.question, hits), "\n")
    print("근거:")
    for i, h in enumerate(hits, start=1):
        print(f" [{i}] #{h['id']} {h['source']}  (score {h['score']:.2f})")
    print("\n판정 힌트: 답에 인용된 번호의 조각 안에 그 내용이 실제로 있는가?")


if __name__ == "__main__":
    main()
