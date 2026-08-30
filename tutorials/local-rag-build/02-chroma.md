# 02 — 선택: 저장소를 Chroma로 바꾸기

조각이 수만 개가 되면 매번 전부 임베딩하고 비교할 수 없습니다. 색인을 파일에 저장하고 가까운 것만 찾아 주는 vector store를
붙입니다. `rag_chroma.py`는 `rag_skeleton.py`의 함수를 그대로 가져다 쓰고 **저장소만** 바꿉니다.

← [01 단계별로 만들기](01-build.md) · [README](README.md)

> **검증 상태:** 색인 → 질의 → 초기화 전 경로를 Apple M4 Pro·24GB Mac, Ollama 0.33.0, `chromadb` 1.5.9에서 실행했습니다.
> `[실행 검증 · 2026-08-30]`

---

## 1. 색인하고 질문하기

```bash
pip install chromadb
python3 rag_chroma.py --index
python3 rag_chroma.py "연차는 며칠까지 이월할 수 있나요?"
```

**★ 성공 판정:** `색인 완료: 17개 조각`이 출력되고, 질문의 근거 상위가 01 §3과 같은 조각(#15·#16·#14)입니다. 점수는 Chroma가
`1 − distance`로 환산한 값이므로 소수점 아래가 조금 다를 수 있습니다. 작성 환경에서는 점수까지 동일(0.72·0.72·0.67)했고 답도
같았습니다. `[실행 검증 · 2026-08-30]`

## 2. 바뀐 것과 바뀌지 않은 것

| | 리스트 (`rag_skeleton.py`) | Chroma (`rag_chroma.py`) |
| --- | --- | --- |
| 색인 시점 | 매 실행 시 재계산 | `--index` 한 번, `chroma_db/`에 저장 |
| 검색 | 전부 비교 | HNSW 인덱스로 근사 탐색 |
| 임베딩 모델·프롬프트·생성 | **같음** | **같음** — `rag_skeleton`에서 그대로 import |

`[원리]` 저장소를 바꿔도 파이프라인의 나머지는 그대로입니다. 반대로 임베딩 모델을 바꾸면 저장소의 벡터를 전부 다시 만들어야
합니다([가이드 03 §4](../../guides/local-rag/03-pipeline-anatomy.md)).

`rag_chroma.py`는 컬렉션을 만들 때 코사인 공간을 `configuration={"hnsw": {"space": "cosine"}}`로 지정합니다. Chroma 1.x의 방식이며,
예전 글에 자주 보이는 `metadata={"hnsw:space": "cosine"}`는 호환용으로 남아 있지만 권장되지 않습니다. `[문서 확인 · 2026-08-30]`
API가 바뀌어 오류가 나면 [출처](SOURCES.md)의 공식 문서를 확인합니다.

## 3. 초기화

```bash
python3 rag_chroma.py --reset     # ./chroma_db 삭제
```

`색인을 삭제했습니다.`가 출력되면 01을 시작하기 전 상태로 돌아간 것입니다. `[실행 검증 · 2026-08-30]`

---

**다음 →** [실습: RAG는 왜 틀리는가](../../labs/why-rag-fails/README.md) — 같은 스크립트로 다섯 가지 실패를 일부러 만들어 봅니다.
