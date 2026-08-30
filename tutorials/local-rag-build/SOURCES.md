# 출처

**내 문서에 답하는 Local RAG 만들기에서** version에 따라 달라질 수 있는 핵심 정보와 그 근거가 되는 자료를 연결합니다.

- 마지막 확인일: 2026-08-30
- `문서 확인`은 공식 문서·model card를 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다. 직접 실행한 결과는 [VALIDATION.md](VALIDATION.md)에 있습니다.
- URL의 내용이 바뀔 수 있으므로 중요한 구성 변경 전에는 다시 확인합니다.

## 실행 도구

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| Ollama OpenAI 호환 | `/v1/chat/completions`, `/v1/embeddings`, `api_key` 임의 문자열 | [Ollama OpenAI compatibility](https://github.com/ollama/ollama/blob/main/docs/openai.md) | 문서 확인 |
| Ollama context 창 | 기본 context, `ollama ps`의 CONTEXT 열 | [Ollama FAQ](https://docs.ollama.com/faq) | 문서 확인 |
| OpenAI Python SDK | `base_url` 교체, `embeddings.create`, `chat.completions.create` | [openai-python](https://github.com/openai/openai-python) | 문서 확인 |
| Chroma | `PersistentClient`, 컬렉션 `configuration={"hnsw": {"space": "cosine"}}`(1.x; `metadata={"hnsw:space"}`는 호환용), `upsert`/`query`와 distance = 1 − cosine | [Chroma docs — Configure collections](https://docs.trychroma.com/docs/collections/configure) | 문서 확인 |

## 모델

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| bge-m3 | 다국어, 1,024차원, 8,192 토큰 입력 | [BAAI/bge-m3 model card](https://huggingface.co/BAAI/bge-m3) · [Ollama library bge-m3](https://ollama.com/library/bge-m3) | 문서 확인 |
| gemma3:4b | 튜토리얼용 대화 모델 태그·라이선스 | [Ollama library gemma3](https://ollama.com/library/gemma3) | 문서 확인 |

## 원리

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| 코사인 유사도 | 정규화된 벡터에서 내적과 동일 | 일반 선형대수 — 별도 출처 없음 | 원리 |

## Source ledger를 갱신하는 규칙

1. 스크립트의 모델·API claim을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.
