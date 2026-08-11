# 출처

**내 장비에서 LLM 직접 실행하기**에서 version에 따라 달라질 수 있는 핵심 정보와 그 근거가 되는 1차 자료를 연결합니다.

- 마지막 확인일: 2026-08-10
- `문서 확인`은 아래 공식 문서·model card를 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다.
- URL의 내용이 바뀔 수 있으므로 중요한 구성 변경 전에는 다시 확인합니다.

## 실행 도구

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| Ollama 첫 실행 | 설치 흐름, `ollama run`, 지원 platform | [Ollama quickstart](https://docs.ollama.com/quickstart) | 문서 확인 |
| Ollama on macOS | macOS 설치와 hardware 지원 범위 | [Ollama macOS](https://docs.ollama.com/macos) | 문서 확인 |
| Ollama on Linux | 설치 script, 수동 설치, service 구성 | [Ollama Linux](https://docs.ollama.com/linux) | 문서 확인 |
| 첫 model | `gemma3:4b` tag, file size, 필요한 Ollama version | [Ollama Gemma 3 library](https://ollama.com/library/gemma3) | 문서 확인 |
| Ollama 운영 | `ollama ps`, keep-alive, context·KV cache, local/cloud privacy 설정 | [Ollama FAQ](https://docs.ollama.com/faq) | 문서 확인 |
| Ollama API | chat request와 response field | [Ollama chat API](https://docs.ollama.com/api/chat) | 문서 확인 |
| Ollama의 MLX 경로 | MLX engine 도입 범위와 preview 당시 제약 | [Ollama MLX](https://ollama.com/blog/mlx) | 문서 확인 |
| llama.cpp | 지원 backend와 `llama-server`·`llama-bench` 개요 | [llama.cpp repository](https://github.com/ggml-org/llama.cpp) | 문서 확인 |
| llama.cpp build | Metal 기본 build와 CUDA의 `GGML_CUDA=ON` | [llama.cpp build guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) | 문서 확인 |
| MLX LM | install, generate, convert, LoRA command | [MLX LM repository](https://github.com/ml-explore/mlx-lm) | 문서 확인 |
| MLX LM server | server command, port와 production security 경고 | [MLX LM server](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md) | 문서 확인 |
| LM Studio server | local server, CLI, compatibility endpoint | [LM Studio server](https://lmstudio.ai/docs/developer/core/server) | 문서 확인 |
| LM Studio security | authentication, local network와 MCP server 설정 | [LM Studio server settings](https://lmstudio.ai/docs/developer/core/server/settings) | 문서 확인 |

## vLLM과 NVIDIA

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| OpenAI-style server | server 실행과 지원 endpoint 범위 | [vLLM OpenAI-compatible server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server/) | 문서 확인 |
| 병렬화 | TP·PP 선택과 single-node·multi-node scaling | [vLLM parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/) | 문서 확인 |
| KV cache 양자화 | 지원 dtype, hardware 조건과 quality 주의 | [vLLM quantized KV cache](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/) | 문서 확인 |
| metric | metric lifecycle과 version 변경 가능성 | [vLLM metrics](https://docs.vllm.ai/en/latest/design/metrics/) | 문서 확인 |
| WSL2 CUDA | Windows driver와 WSL 안 toolkit·driver의 경계 | [NVIDIA CUDA on WSL](https://docs.nvidia.com/cuda/wsl-user-guide/contents.html) | 문서 확인 |
| multi-GPU 진단 | NCCL debug 환경변수와 production에 남기지 말아야 할 설정 | [NVIDIA NCCL environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html) | 문서 확인 |

## model·양자화·hardware

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| 양자화 개념 | Transformers가 지원하는 양자화 방법과 hardware별 차이 | [Hugging Face quantization](https://huggingface.co/docs/transformers/main_classes/quantization) | 문서 확인 |
| 양자화 판단 | weight·activation 양자화와 calibration의 개념 | [Hugging Face quantization concept guide](https://huggingface.co/docs/transformers/quantization/concept_guide) | 문서 확인 |
| Gemma | Gemma 계열의 현재 문서와 model card 연결 | [Google Gemma documentation](https://ai.google.dev/gemma/docs/core) | 문서 확인 |
| Gemma 4 | architecture, limitation, 사용 조건 확인 경로 | [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4) | 문서 확인 |
| Qwen snapshot | `Qwen/Qwen3.6-27B` repository의 config·license·usage | [Qwen3.6-27B model card](https://huggingface.co/Qwen/Qwen3.6-27B) | 문서 확인 |
| gpt-oss snapshot | model size, local 실행 대상, Apache 2.0 안내 | [OpenAI gpt-oss 안내](https://help.openai.com/en/articles/11870455) | 문서 확인 |
| Apple memory·bandwidth 예 | 현재 Mac Studio configuration별 공식 사양 | [Apple Mac Studio 사양](https://www.apple.com/mac-studio/specs/) | 문서 확인 |
| AMD memory·bandwidth 예 | Ryzen AI Max+ 395의 memory 상한과 공식 사양 | [AMD Ryzen AI Max+ 395](https://www.amd.com/en/products/processors/laptop/ryzen/ai-300-series/amd-ryzen-ai-max-plus-395.html) | 문서 확인 |
| NVIDIA VRAM·bandwidth 예 | RTX PRO 6000의 공식 memory 사양 | [NVIDIA RTX PRO 6000](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/) | 문서 확인 |

## Source ledger(출처 확인 기록)를 갱신하는 규칙

1. 본문의 version·model·hardware claim을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. blog·community benchmark는 탐색에만 쓰고, 확정 claim은 official documentation·model card로 다시 확인합니다.
3. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·command·result를 남깁니다.
4. source가 서로 충돌하면 하나를 임의로 택하지 않고 본문 claim을 좁히거나 `자료 확인`으로 낮춥니다.
