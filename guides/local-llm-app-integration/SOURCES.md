# 출처

**Local LLM을 내 프로그램에 연결하기**에서 버전에 따라 달라질 수 있는 핵심 정보와 공식 근거를 연결합니다.

- 마지막 확인일: 2026-08-24
- `문서 확인`은 공식 문서를 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다.
- URL과 지원 범위는 바뀔 수 있으므로 runtime·SDK를 올리거나 백엔드를 바꿀 때 다시 확인합니다.

## runtime API

| 범위 | 확인한 내용 | 공식 자료 | 상태 |
| --- | --- | --- | --- |
| Ollama OpenAI 호환 | Chat Completions·Models·Embeddings, 구조화 출력·tools·streaming, Responses API의 현재 범위, API key 값은 로컬에서 무시 | [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) | 문서 확인 |
| Ollama context | VRAM 구간별 기본 context, 큰 창의 메모리 비용, `ollama ps` 확인 | [Context length](https://docs.ollama.com/context-length) | 문서 확인 |
| Ollama 자체 API | `/api/chat` 옵션과 `keep_alive` | [API reference](https://docs.ollama.com/api/introduction) | 문서 확인 |
| Ollama 구조화 출력 | JSON schema 사용법과 파싱 뒤 검증 권고 | [Structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | 문서 확인 |
| Ollama tool calling | 도구 명세, 병렬 호출, 다중 턴 agent loop | [Tool calling](https://docs.ollama.com/capabilities/tool-calling) | 문서 확인 |
| Ollama 운영 | 기본 loopback 주소, `OLLAMA_HOST`, `keep_alive` | [FAQ](https://docs.ollama.com/faq) | 문서 확인 |
| vLLM | OpenAI 호환 서버, 인증, 구조화 출력과 tool calling 설정 | [OpenAI-compatible server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server/) | 문서 확인 |
| llama.cpp server | Chat Completions·Responses·Embeddings, API key, JSON schema·tool calling | [llama-server README](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) | 문서 확인 |
| LM Studio | OpenAI 호환 endpoint와 structured output·tool use의 현재 범위 | [OpenAI compatibility](https://lmstudio.ai/docs/developer/openai-compat) | 문서 확인 |

## SDK·프레임워크·프로토콜

| 범위 | 확인한 내용 | 공식 자료 | 상태 |
| --- | --- | --- | --- |
| OpenAI Python SDK | `base_url`, Chat Completions, streaming, 예외 클래스 | [openai-python](https://github.com/openai/openai-python) | 문서 확인 |
| OpenAI Node SDK | `baseURL`과 동일 호출 형식 | [openai-node](https://github.com/openai/openai-node) | 문서 확인 |
| OpenAI API 참조 | messages 역할, `finish_reason`, `tool_calls`, `usage` | [Chat Completions](https://platform.openai.com/docs/api-reference/chat) | 문서 확인 |
| Spring AI | Ollama 모델, `ChatClient`, tool calling, MCP | [Spring AI reference](https://docs.spring.io/spring-ai/reference/) | 문서 확인 |
| LangChain4j | Ollama 통합, tools·agents, MCP | [LangChain4j docs](https://docs.langchain4j.dev/) | 문서 확인 |
| MCP | host·client·server 역할과 도구 연결 | [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro) | 문서 확인 |

## 모델과 안전 원리

| 범위 | 확인한 내용 | 공식·원문 자료 | 상태 |
| --- | --- | --- | --- |
| gemma3·qwen3 | 예시 모델 태그와 현재 배포 정보 | [gemma3](https://ollama.com/library/gemma3) · [qwen3](https://ollama.com/library/qwen3) | 문서 확인 |
| prompt injection | 외부 콘텐츠에 심어진 간접 지시와 최소 권한·승인·입력/출력 검증 | [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | 문서 확인 |
| grammar-constrained decoding | 문법과 JSON schema로 생성 토큰을 제한하는 방식 | [llama.cpp grammars](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md) | 문서 확인 |

## Source ledger를 갱신하는 규칙

1. 본문의 runtime·모델·API 주장을 바꾸면 같은 변경에서 이 표를 갱신합니다.
2. 블로그·비교 글은 탐색에만 쓰고, 확정 주장은 공식 문서나 원문으로 다시 확인합니다.
3. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.
4. 자료가 충돌하면 하나를 임의로 택하지 않고 본문 주장을 좁히거나 검증 상태를 낮춥니다.
