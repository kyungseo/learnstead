# 출처

**RAG는 왜 틀리는가에서** version에 따라 달라질 수 있는 핵심 정보와 그 근거가 되는 자료를 연결합니다.

- 마지막 확인일: 2026-08-30
- `문서 확인`은 공식 문서·model card·논문 원문을 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다. 직접 실행한 결과는 [VALIDATION.md](VALIDATION.md)에 있습니다.

## 실행 도구

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| Ollama OpenAI 호환 | `/v1/chat/completions`, `/v1/embeddings`, `response_format`(JSON schema) 지원 | [Ollama OpenAI compatibility](https://github.com/ollama/ollama/blob/main/docs/openai.md) | 문서 확인 |
| Ollama 구조화 출력 | JSON schema로 출력 형식 강제 (`graph_minimal.py`의 트리플) | [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | 문서 확인 |
| OpenAI Python SDK | `base_url` 교체, `embeddings.create`, `chat.completions.create` | [openai-python](https://github.com/openai/openai-python) | 문서 확인 |
| NetworkX | `DiGraph`, `to_undirected`, 이웃 탐색 | [NetworkX documentation](https://networkx.org/documentation/stable/) | 문서 확인 |

## 모델

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| bge-m3 | 다국어, 1,024차원 | [BAAI/bge-m3 model card](https://huggingface.co/BAAI/bge-m3) · [Ollama library bge-m3](https://ollama.com/library/bge-m3) | 문서 확인 |
| gemma3:4b | 실습용 대화·추출 모델 태그 | [Ollama library gemma3](https://ollama.com/library/gemma3) | 문서 확인 |

## 방법·원리

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| BM25 | `k1`·`b` 기본값, IDF 식 (`rag_minimal.py`의 구현) | Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond* (2009) | 문서 확인 |
| RRF | 순위 기반 결과 융합, k≈60 | [Cormack et al., Reciprocal Rank Fusion (SIGIR 2009)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) | 문서 확인 |
| GraphRAG 원형 | 개체·관계 추출, local search | [Edge et al., From Local to Global (2024)](https://arxiv.org/abs/2404.16130) | 문서 확인 |
| RAG 평가 지표 | recall@k, faithfulness의 구분 | [Ragas documentation](https://docs.ragas.io/) | 문서 확인 |

## Source ledger를 갱신하는 규칙

1. 스크립트의 모델·API claim을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.
