# 출처

**내 문서와 대화하는 AI 이해하기 — RAG와 Graph에서** version에 따라 달라질 수 있는 핵심 정보와 그 근거가 되는 자료를 연결합니다.

- 마지막 확인일: 2026-08-30 (초안 조사 2026-08-23)
- `문서 확인`은 공식 문서·model card·논문 원문을 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다.
- `자료 확인`은 2차 정리 자료(블로그·비교 글)로만 확인한 항목입니다. 선택의 출발점으로만 쓰고, 확정 전에는 1차 자료로 다시 확인합니다.
- URL의 내용이 바뀔 수 있으므로 중요한 구성 변경 전에는 다시 확인합니다.

## 실행 도구

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| Ollama 임베딩 API | `/api/embed` 요청·응답, 여러 입력 일괄 처리 | [Ollama API — embed](https://github.com/ollama/ollama/blob/main/docs/api.md) | 문서 확인 |
| Ollama OpenAI 호환 | `/v1/chat/completions`, `/v1/embeddings`, `response_format` 지원 범위 | [Ollama OpenAI compatibility](https://github.com/ollama/ollama/blob/main/docs/openai.md) | 문서 확인 |
| Ollama 구조화 출력 | JSON schema로 출력 형식 강제 | [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | 문서 확인 |
| Ollama context 창 | 메모리에 따른 기본 context, `OLLAMA_CONTEXT_LENGTH`, `ollama ps`의 CONTEXT 열 | [Ollama context length](https://docs.ollama.com/context-length) | 문서 확인 |
| Ollama 입력 조정 | 적용 context를 넘을 때 system과 최신 메시지를 보존하며 오래된 메시지를 제외하는 현재 구현 | [Ollama `server/prompt.go`](https://github.com/ollama/ollama/blob/main/server/prompt.go) | 코드 확인 |
| OpenAI Python SDK | `base_url` 교체, `embeddings.create`, `chat.completions.create` | [openai-python](https://github.com/openai/openai-python) | 문서 확인 |
| Chroma | `PersistentClient`, 컬렉션 `configuration={"hnsw": {"space": ...}}`(1.x, `metadata={"hnsw:space"}`는 호환용), `upsert`/`query`와 distance 의미 | [Chroma docs — Configure collections](https://docs.trychroma.com/docs/collections/configure) | 문서 확인 |
| NetworkX | `DiGraph`, 이웃 탐색 | [NetworkX documentation](https://networkx.org/documentation/stable/) | 문서 확인 |

## 모델

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| bge-m3 | 다국어, 1,024차원, 8,192 토큰 입력, dense·sparse·multi-vector | [BAAI/bge-m3 model card](https://huggingface.co/BAAI/bge-m3) · [Ollama library bge-m3](https://ollama.com/library/bge-m3) | 문서 확인 |
| bge-reranker-v2-m3 | 다국어 cross-encoder reranker | [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 문서 확인 |
| Qwen3-Embedding | 크기별 라인업, 가변 출력 차원, 질문 쪽 instruction 사용 | [Qwen/Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B) | 문서 확인 |
| nomic-embed-text | 경량, 긴 입력 | [nomic-ai/nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) | 문서 확인 |
| 한국어 특화 임베딩 | 존재와 용도 | 공개 비교 자료 (아래 2차 자료) | 자료 확인 |
| gemma3:4b | 실습용 대화 모델 태그·라이선스 | [Ollama library gemma3](https://ollama.com/library/gemma3) | 문서 확인 |

## 방법·원리

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| RRF | 순위 기반 결과 융합, k≈60 | [Cormack et al., Reciprocal Rank Fusion (SIGIR 2009)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) | 문서 확인 |
| 긴 입력에서의 주의력 저하 | 중간 위치 정보 활용 저하 | [Liu et al., Lost in the Middle (2023)](https://arxiv.org/abs/2307.03172) | 문서 확인 |
| GraphRAG 원형 | 개체·관계 추출, 커뮤니티 요약, local/global search | [Edge et al., From Local to Global (2024)](https://arxiv.org/abs/2404.16130) · [Microsoft GraphRAG docs](https://microsoft.github.io/graphrag/) | 문서 확인 |
| LazyGraphRAG | 질의 시점 요약으로 색인 비용 절감 | [Microsoft Research blog](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/) | 문서 확인 |
| LightRAG | 그래프+벡터 이중 인덱스, 증분 갱신 | [LightRAG repository](https://github.com/HKUDS/LightRAG) · [arXiv 2410.05779](https://arxiv.org/abs/2410.05779) | 문서 확인 |
| HippoRAG 2 | PageRank 기반 multi-hop 검색 | [HippoRAG repository](https://github.com/OSU-NLP-Group/HippoRAG) | 문서 확인 |
| Cypher | 패턴 매칭 문법 | [Neo4j Cypher manual](https://neo4j.com/docs/cypher-manual/current/) | 문서 확인 |
| RAG 평가 지표 | faithfulness·relevance·context precision/recall | [Ragas documentation](https://docs.ragas.io/) | 문서 확인 |

## 2차 자료 (2026-08-23 조회)

아래는 본문의 `자료 확인` 항목 — hybrid·reranker 비교, 청킹 전략의 보편화, vector database 선택 기준,
GraphRAG 변형 비교, 한국어 임베딩 선택) — 의 출처입니다. 전부 2차 정리 자료이며, 숫자나 순위를 인용해야 하면 위 1차 자료로
다시 확인합니다.

| 주제 | 자료 |
| --- | --- |
| GraphRAG vs vector RAG, 결합 우위 | VentureBeat "Stop graphing everything: When GraphRAG actually beats vector RAG" · "RAG vs GraphRAG: A 2026 Decision Framework" (cruxdigits.nl) · "GraphRAG vs. Vector RAG: The Architecture Decision Teams Make Too Late" (tianpan.co) |
| RAG 관행 2026 (hybrid·reranker·late chunking·agentic) | "Hybrid Search: BM25, Vector & Reranking Reference 2026" (digitalapplied.com) · "Advanced RAG Chunking Techniques in 2026" (futureagi.com) · "RAG Best Practices 2026" (callmissed.com) |
| 임베딩 모델 비교 | "The Best Open-Source Embedding Models in 2026" (bentoml.com) · "Best Local Embedding Models for RAG in 2026" (recal.so) · "임베딩 모델 선택 가이드 — 개념부터 한국어 벤치마크까지" (data-dynamics.io) · "임베딩과 리랭커, RAG에서 실제로 중요한 것" (youngju.dev, 2026-08-12) |
| vector database 비교 | "Vector Database Comparison 2026: ChromaDB vs. Qdrant vs. pgvector vs. Pinecone vs. LanceDB" (4xxi.com) · "Best Vector Databases in 2026" (firecrawl.dev) |
| GraphRAG 로컬 구성 | "Building GraphRAG Locally" (Neo4j Developer Blog) · "GraphRAG and LightRAG in 2026" (callsphere.ai) |
| Kuzu 개발 중단 (2026-08-30 조회) | "KuzuDB graph database abandoned, community mulls options" (The Register, 2025-10-14) · "Kuzu's Legacy and the New Wave of Embedded Graph Databases" (gdotv.com) — upstream 저장소 2025-10-10 archive, 커뮤니티 포크(LadybugDB 등) |

## Source ledger를 갱신하는 규칙

1. 본문의 모델·도구·API claim을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 블로그·비교 글은 탐색에만 쓰고, 확정 claim은 공식 문서·model card·논문으로 다시 확인합니다.
3. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.
4. 자료가 서로 충돌하면 하나를 임의로 택하지 않고 본문 claim을 좁히거나 `자료 확인`으로 낮춥니다.
