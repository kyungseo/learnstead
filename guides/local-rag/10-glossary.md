# 10 — 용어집

전 문서의 **참조 부록입니다**. 순서대로 읽는 문서가 아니라, 모르는 용어가 나왔을 때 여는 문서입니다. 정의는 이 가이드의
서술 기준을 따르며, 상세 설명이 있는 본문 위치를 함께 적었습니다.

← [09 개인 RAG와 기업 RAG](09-personal-vs-enterprise.md) · [README로](README.md)

---

## 1. RAG 기본

| 용어 | 뜻 |
| --- | --- |
| **RAG (Retrieval-Augmented Generation, 검색 증강 생성)** | 질문 시점에 관련 문서 조각을 찾아 프롬프트에 넣고 답하게 하는 방식. 모델 가중치는 바꾸지 않음 ([01 §0](01-ecosystem-map.md)) |
| **검색(retrieval)** | 질문과 관련된 조각을 찾아오는 단계. RAG 품질의 대부분이 여기서 갈림 ([03](03-pipeline-anatomy.md)) |
| **생성(generation)** | 찾아온 조각을 읽고 답을 쓰는 단계. LLM의 역할 ([06](06-generation-and-grounding.md)) |
| **색인 시점 / 질의 시점(indexing / query time)** | 문서를 준비하는 파이프라인과 질문에 답하는 파이프라인. 같은 embedding model을 공유 ([03 §0](03-pipeline-anatomy.md)) |
| **근거 고정(grounding)** | 답을 제공된 조각 안의 내용으로만 쓰게 하고 출처를 붙이는 것 ([06 §2](06-generation-and-grounding.md)) |
| **환각(hallucination)** | 모델이 근거 없는 내용을 그럴듯하게 생성하는 현상 ([02 §0](02-rag-vs-long-context-vs-finetuning.md)) |
| **Long Context** | 검색 없이 문서를 통째로 프롬프트에 넣는 방식. 문서가 적을 때의 대안 ([02 §1.2](02-rag-vs-long-context-vs-finetuning.md)) |
| **Fine-tuning(미세 조정)** | 문서로 모델을 추가 학습해 가중치를 바꾸는 것. 사실 주입보다 행동·형식 교정에 적합. 이 가이드 범위 밖 ([02 §1.3](02-rag-vs-long-context-vs-finetuning.md)) |
| **context window(컨텍스트 창)** | 모델이 한 번에 읽을 수 있는 토큰 수. 프롬프트 + 조각 + 답이 모두 들어가야 함 ([06 §3](06-generation-and-grounding.md)) |
| **num_ctx** | Ollama에서 이 실행에 적용할 컨텍스트 창 크기 설정. 모델 선언 상한보다 작을 수 있음 ([06 §3](06-generation-and-grounding.md)) |

## 2. 임베딩·검색

| 용어 | 뜻 |
| --- | --- |
| **임베딩(embedding)** | 텍스트의 의미를 고정 길이 숫자 벡터로 바꾼 것. 뜻이 비슷하면 벡터가 가까움 ([04 §1](04-embeddings-and-vector-search.md)) |
| **embedding model** | 임베딩을 만드는 전용 모델(예: bge-m3). 대화 모델과 다름 ([04 §4](04-embeddings-and-vector-search.md)) |
| **차원(dimension)** | 벡터의 숫자 개수(예: 1,024). 모델이 정함 ([04 §1](04-embeddings-and-vector-search.md)) |
| **코사인 유사도(cosine similarity)** | 두 벡터 사이 각도의 코사인. 1에 가까울수록 비슷 ([04 §2](04-embeddings-and-vector-search.md)) |
| **top-k** | 검색에서 가져오는 조각 수 ([05 §3](05-chunking-and-retrieval-quality.md)) |
| **점수 하한(threshold)** | 이 점수 아래의 조각은 버리는 기준. 관련 없는 문서를 차단 ([05 §3](05-chunking-and-retrieval-quality.md)) |
| **dense 검색** | 임베딩 벡터의 가까움으로 찾는 검색. 표현이 달라도 뜻이 같으면 찾음 ([05 §2](05-chunking-and-retrieval-quality.md)) |
| **sparse 검색 / BM25** | 단어 일치로 찾는 검색. 코드·고유명사에 강함 ([05 §2](05-chunking-and-retrieval-quality.md)) |
| **hybrid 검색** | dense와 sparse를 함께 쓰고 결과를 합치는 방식 ([05 §2.1](05-chunking-and-retrieval-quality.md)) |
| **RRF (Reciprocal Rank Fusion)** | 여러 검색 결과를 순위 기반으로 합치는 방법. 점수 단위가 달라도 됨 ([05 §2.1](05-chunking-and-retrieval-quality.md)) |
| **reranker(재정렬기)** | 1차 검색 후보를 질문과 함께 다시 읽어 순위를 정교하게 매기는 모델 ([05 §4](05-chunking-and-retrieval-quality.md)) |
| **bi-encoder / cross-encoder** | 질문과 조각을 따로 벡터화해 비교 / 한 쌍으로 함께 읽어 점수 계산. 전자가 임베딩 검색, 후자가 reranker ([05 §4](05-chunking-and-retrieval-quality.md)) |
| **쿼리 변환(query transformation)** | 재작성·multi-query·HyDE 등 질문 쪽을 손보는 기법 ([05 §5](05-chunking-and-retrieval-quality.md)) |
| **ANN (Approximate Nearest Neighbor) / HNSW** | "거의 가장 가까운" 벡터를 빠르게 찾는 근사 탐색과 그 대표 인덱스 구조 ([04 §5.1](04-embeddings-and-vector-search.md)) |
| **vector store / vector database** | 벡터와 원문·메타데이터를 저장하고 가까운 k개를 찾아 주는 저장소 ([04 §5](04-embeddings-and-vector-search.md)) |

## 3. 문서·청킹

| 용어 | 뜻 |
| --- | --- |
| **파싱(parsing)** | PDF·HWP·HTML 등에서 텍스트를 꺼내는 단계 ([03 §1](03-pipeline-anatomy.md)) |
| **청킹(chunking) / 조각(chunk)** | 문서를 검색 단위로 자르는 일과 그 결과물 ([05 §1](05-chunking-and-retrieval-quality.md)) |
| **겹침(overlap)** | 인접 조각이 경계 부분을 공유하게 하는 것. 경계에서 문맥이 잘리는 것을 완화 ([05 §1.3](05-chunking-and-retrieval-quality.md)) |
| **재귀 분할(recursive splitting)** | 절→단락→문장 순으로 경계를 찾아 자르는 방식. 기본값 ([05 §1.2](05-chunking-and-retrieval-quality.md)) |
| **부모-자식 청킹(parent-child)** | 작은 조각으로 검색하고 큰 단위를 생성에 넣는 방식 ([05 §1.2](05-chunking-and-retrieval-quality.md)) |
| **late chunking** | 문서 전체를 임베딩한 뒤 조각 단위로 벡터를 나누는 방식 ([05 §1.2](05-chunking-and-retrieval-quality.md)) |
| **메타데이터(metadata)** | 조각에 붙는 출처·절·날짜·권한 정보. 출처 제시와 필터의 근거 ([03 §1](03-pipeline-anatomy.md)) |

## 4. 그래프

| 용어 | 뜻 |
| --- | --- |
| **그래프(graph)** | 노드(점)와 엣지(선)로 이루어진 구조 ([07 §1](07-graph-basics.md)) |
| **지식 그래프(knowledge graph)** | 노드가 개체, 엣지가 관계인 그래프 ([07 §1](07-graph-basics.md)) |
| **트리플(triple)** | `(주어, 관계, 목적어)` — 사실의 최소 단위 ([07 §2](07-graph-basics.md)) |
| **홉(hop)** | 그래프에서 엣지를 하나 건너는 단위. multi-hop = 여러 관계를 연쇄 ([07 §2](07-graph-basics.md)) |
| **개체 통합(entity resolution)** | "김서연"·"김 팀장"처럼 다르게 적힌 같은 개체를 하나로 합치는 것 ([07 §3](07-graph-basics.md)) |
| **graph database** | 노드·엣지를 저장하고 경로·패턴으로 질의하는 저장소(예: Neo4j) ([07 §4](07-graph-basics.md)) |
| **Cypher** | Neo4j 계열의 그래프 질의 언어. `(노드)-[:관계]->(노드)` 패턴 ([07 §4](07-graph-basics.md)) |
| **GraphRAG** | 지식 그래프를 검색에 활용하는 RAG의 변형 ([08](08-graphrag.md)) |
| **local search / global search** | 개체 주변을 탐색해 답함 / 커뮤니티 요약으로 전체 질문에 답함 ([08 §2](08-graphrag.md)) |
| **커뮤니티 요약(community summary)** | 촘촘히 연결된 개체 묶음마다 LLM이 만든 요약. global search의 재료 ([08 §2](08-graphrag.md)) |
| **LazyGraphRAG / LightRAG / HippoRAG** | 색인 비용·갱신·탐색 방식을 개선한 GraphRAG 변형들 ([08 §3](08-graphrag.md)) |

## 5. 평가·운영

| 용어 | 뜻 |
| --- | --- |
| **골든셋(golden set)** | 질문과 정답(정답 조각·기대 답)을 짝지은 평가용 데이터 ([09 §4](09-personal-vs-enterprise.md)) |
| **recall@k / precision** | 정답 조각이 top-k에 들어온 비율 / 들어온 조각 중 관련 비율 ([09 §4](09-personal-vs-enterprise.md)) |
| **faithfulness(근거 충실도)** | 답이 제공된 근거에만 기반했는가 ([09 §4](09-personal-vs-enterprise.md)) |
| **LLM 판정자(LLM-as-judge)** | 다른 모델에게 답의 근거 충실도 등을 채점시키는 방법 ([09 §4](09-personal-vs-enterprise.md)) |
| **추적(tracing)** | 한 질문이 거친 검색 결과·프롬프트·응답을 기록해 되짚는 것 ([09 §2](09-personal-vs-enterprise.md)) |
| **권한 필터(pre-filter)** | 사용자가 볼 수 있는 조각만 검색 대상으로 좁히는 것. 검색 **전에** 적용 ([09 §3](09-personal-vs-enterprise.md)) |
| **증분 색인(incremental indexing)** | 바뀐 문서만 다시 색인하는 것 ([09 §2](09-personal-vs-enterprise.md)) |
| **게이트웨이(gateway)** | 인증·라우팅·마스킹을 한곳에서 처리하는 중간 계층. 이 가이드 범위 밖 ([09 §2](09-personal-vs-enterprise.md)) |

## 6. 혼동하기 쉬운 쌍 ★

| 쌍 | 차이 |
| --- | --- |
| **검색 실패 vs 생성 실패** | 근거에 정답이 없음 ↔ 근거에 있는데 답이 다름. 고칠 부품이 다름 ([실습](../../labs/why-rag-fails/README.md)) |
| **embedding model vs 대화 모델** | 벡터를 만드는 전용 모델 ↔ 답을 쓰는 모델. 대체 불가 |
| **유사도 vs 거리** | 높을수록 가까움 ↔ 낮을수록 가까움. 도구마다 보고 방식이 다름 ([04 §2](04-embeddings-and-vector-search.md)) |
| **top-k vs 점수 하한** | 몇 개를 가져올지 ↔ 어느 점수 아래는 버릴지. 둘 다 필요 |
| **dense vs sparse** | 뜻으로 찾음 ↔ 단어로 찾음. 서로 다른 실패를 보완 |
| **reranker vs 더 큰 embedding model** | 후보를 다시 읽어 순위 개선 ↔ 1차 검색 자체 개선. 전자가 보통 비용 대비 효과 큼 |
| **vector store vs graph database** | 비슷한 조각의 창고 ↔ 관계의 지도. 푸는 질문이 다름 |
| **local search vs global search** | 개체 주변 탐색 ↔ 전체 요약. GraphRAG의 두 질의 방식 |
| **Long Context vs RAG** | 통째로 넣기 ↔ 찾아서 넣기. 문서 규모·출처 추적·비용으로 선택 |
| **모델이 선언한 context vs runtime이 적용한 context** | 상한 ↔ 이번 실행의 실제 값. 후자를 넘기면 runtime이 입력 일부를 제외할 수 있음 |
| **검색 전 필터 vs 검색 후 필터** | 권한은 반드시 전자. 후자는 품질 저하 + 누락 위험 |

---

**← [README로 돌아가기](README.md)**
