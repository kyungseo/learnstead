#!/usr/bin/env python3
"""골든셋 20문항으로 검색 품질을 숫자로 잰다. 모델(생성)은 호출하지 않는다.

사용법:
  python3 recall.py                          # dense · top-k 3
  python3 recall.py --search hybrid --top-k 5
  python3 recall.py --chunk fixed:60         # 청킹을 바꾸면 recall이 어떻게 변하나

goldenset.json: 질문 20개. gold = 단락 청킹 기준 정답 조각 번호(`rag_minimal.py --show`의 #, 참고용), must = 정답에 꼭 있어야
하는 구절. 둘 다 비면 "문서에 없는 질문".
판정: top-k 조각 본문을 합쳤을 때 must 구절이 **모두** 들어 있으면 question success — 청킹을 바꿔 조각 번호가 달라져도 같은 기준으로 잰다.
각 must 구절을 몇 개 찾았는지는 phrase recall@k로 따로 센다.
문서에 없는 질문은 recall에서 빼고, 상위 점수만 따로 보고한다(점수 하한 고르기용).
"""

import argparse
import json
from pathlib import Path

from rag_minimal import bm25_rank, dense_rank, embed, load_chunks, rrf

GOLDEN = Path(__file__).parent / "goldenset.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--search", choices=["dense", "bm25", "hybrid"], default="dense")
    ap.add_argument("--chunk", default="paragraph")
    args = ap.parse_args()
    if args.top_k < 1:
        ap.error("--top-k는 1 이상이어야 합니다")

    chunks = load_chunks(args.chunk)
    for c, v in zip(chunks, embed([c["text"] for c in chunks])):
        c["vec"] = v
    items = json.loads(GOLDEN.read_text(encoding="utf-8"))
    qvecs = embed([it["q"] for it in items])

    question_hits, question_total = 0, 0
    phrase_hits, phrase_total = 0, 0
    absent, gold_scores = [], []
    print(f"검색: {args.search} · top-k {args.top_k} · chunk {args.chunk}\n")
    for it, qvec in zip(items, qvecs):
        dense = dense_rank(qvec, chunks)
        if args.search == "dense":
            ranking = dense
        elif args.search == "bm25":
            ranking = bm25_rank(it["q"], chunks)
        else:
            ranking = rrf(dense, bm25_rank(it["q"], chunks))
        top = [cid for cid, _ in ranking[: args.top_k]]
        top_dense = dict(dense)[top[0]]
        by_id = {c["id"]: c for c in chunks}
        if not it["must"]:
            absent.append((it["q"], top_dense))
            print(f"  [없음]  {it['q']}  → 상위 dense {top_dense:.2f}")
            continue
        question_total += 1
        joined = "\n".join(by_id[cid]["text"] for cid in top)
        found = [phrase for phrase in it["must"] if phrase in joined]
        ok = len(found) == len(it["must"])
        question_hits += ok
        phrase_hits += len(found)
        phrase_total += len(it["must"])
        dense_of = dict(dense)
        phrase_best_scores = []
        for phrase in it["must"]:
            candidates = [dense_of[c["id"]] for c in chunks if phrase in c["text"]]
            if candidates:
                phrase_best_scores.append(max(candidates))
        if len(phrase_best_scores) == len(it["must"]):
            gold_scores.append((min(phrase_best_scores), it["q"]))
        print(f"  [{'O' if ok else 'X'}]  {it['q']}  must {it['must']} → top {top}")

    question_rate = question_hits / question_total if question_total else 0.0
    phrase_rate = phrase_hits / phrase_total if phrase_total else 0.0
    print(f"\nquestion success@{args.top_k} = {question_hits}/{question_total} = {question_rate:.2f}")
    print(f"phrase recall@{args.top_k} = {phrase_hits}/{phrase_total} = {phrase_rate:.2f}")
    if gold_scores:
        lo, lo_q = min(gold_scores)
        print(f"정답 조각의 최저 dense 점수: {lo:.2f}  ({lo_q})")
    if absent:
        hi, hi_q = max((s, q) for q, s in absent)
        print(f"문서에 없는 질문 {len(absent)}건의 상위 dense 점수: " + ", ".join(f"{s:.2f}" for _, s in absent) + f"  (최고 {hi:.2f}: {hi_q})")
        print("→ 점수 하한은 '없는 질문의 최고'보다 높고 '정답 조각의 최저'보다 낮아야 한다. 그 틈이 좁거나 뒤집혀 있으면 하한만으로는 못 거른다.")


if __name__ == "__main__":
    main()
