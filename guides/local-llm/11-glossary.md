# 11 — 용어집

전 문서의 **참조 부록**이다. 순서대로 읽는 문서가 아니라, 모르는 용어가 나왔을 때 여는 문서다.
정의는 이 가이드의 서술 기준을 따르며, 상세 설명이 있는 본문 위치를 함께 적었다.

← [10 운영](10-operations.md) · [README로](README.md)

---

## 1. 모델 구조

| 용어 | 뜻 |
| --- | --- |
| **파라미터(parameter)** | 모델이 학습으로 얻은 가중치 숫자. 7B = 70억 개 |
| **dense** | 모든 파라미터가 매 토큰 계산에 참여하는 구조 |
| **MoE (Mixture of Experts)** | 전문가 집합 중 일부만 골라 쓰는 구조. **총**과 **활성** 파라미터가 다르다 ([02 §3](02-model-anatomy.md)) |
| **총 파라미터 / 활성 파라미터** | MoE에서 memory는 전체 weight 기준으로 계획한다. active parameter는 연산량에 영향을 주지만 속도를 단독으로 결정하지 않는다. `35B-A3B` 표기의 정확한 뜻은 model card 확인 |
| **레이어(layer)** | 모델을 이루는 반복 블록. 토큰이 레이어를 차례로 통과하며 계산된다. 개수는 `config.json`의 `num_hidden_layers` ([02 §2](02-model-anatomy.md)) |
| **어텐션 헤드 / KV 헤드 / 헤드 차원** | 앞 토큰들을 돌아보는 병렬 "시선"의 수 / 그중 KV를 실제 저장하는 벌 수(GQA) / 시선 하나의 폭. KV 캐시 산식의 세 변수 ([02 §2·§5](02-model-anatomy.md)) |
| **임베딩 / 출력층** | 토큰을 내부 표현으로 바꾸는 첫 층 / 내부 표현을 토큰 확률로 되돌리는 끝 층. 양자화에서 더 높은 정밀도로 보존된다 ([02 §2](02-model-anatomy.md)) |
| **컨텍스트 길이(context length)** | 모델이 한 번에 다루도록 설계된 token 수. 실제 사용 상한은 architecture·runtime 설정·memory의 영향을 모두 받는다 ([02 §6](02-model-anatomy.md)) |
| **토큰(token)** | tokenizer가 text를 나눈 단위. 같은 한국어 문장도 model별 tokenizer에 따라 개수가 달라진다. 그림은 [02 §0](02-model-anatomy.md) |
| **GQA (Grouped Query Attention)** | KV 헤드 수를 줄여 KV 캐시를 크게 절감하는 어텐션 구조 ([02 §5](02-model-anatomy.md)) |
| **채팅 템플릿(chat template)** | 대화(역할·메시지)를 모델이 학습한 형식의 단일 텍스트로 조립하는 규칙(Jinja 템플릿 형식). 어긋나면 출력이 이상해진다 ([10 §3](10-operations.md)) |
| **모델 카드(model card)** | HF 모델 페이지의 공식 설명 문서. 파라미터·컨텍스트·라이선스의 **1차 출처** ([09 §6](09-model-landscape.md)) |

## 2. 메모리·성능

| 용어 | 뜻 |
| --- | --- |
| **KV 캐시** | 이미 만든 토큰의 중간 결과 저장분. **컨텍스트 길이에 비례해 자란다** ([02 §5](02-model-anatomy.md)) |
| **VRAM** | GPU 전용 메모리. 이 안에 들어가야 빠르다 |
| **통합메모리(unified memory)** | CPU·GPU가 공유하는 memory(Apple Silicon 등). OS와 다른 application도 함께 사용하므로 전체 용량을 model에 쓸 수는 없다 ([04 §3.3](04-hardware-tiers.md)) |
| **메모리 대역폭** | 초당 전송할 수 있는 data 양(GB/s). token 생성 성능에 영향을 주지만 compute·runtime·model 구조도 함께 작용한다 ([04 §1](04-hardware-tiers.md)) |
| **활성화 메모리(activation)** | 추론 중 계산 중간값을 담는 버퍼. 가중치·KV와 함께 메모리 예산의 세 번째 항이며 "오버헤드"의 주성분 ([02 §1](02-model-anatomy.md), [08 §4](08-setup-multi-gpu-server.md)) |
| **오프로딩(offloading)** | VRAM에 못 넣은 부분을 CPU/RAM에 두는 것. 동작은 하지만 급격히 느려진다 ([07 §3](07-setup-nvidia-workstation.md)) |
| **스왑(swap)** | OS가 부족한 RAM의 일부를 storage로 옮기는 것. model workload에서는 큰 지연과 system memory pressure를 일으킬 수 있다 ([06 §6](06-setup-apple-silicon.md)) |
| **TTFT** | 첫 토큰까지 걸린 시간. prefill 비용 ([10 §1](10-operations.md)) |
| **TPS** | 초당 생성 토큰 수. decode 속도 ([10 §1](10-operations.md)) |
| **prefill / decode** | 프롬프트를 통째로 처리하는 단계 / 토큰을 하나씩 만드는 단계. 생성 루프 그림은 [02 §0](02-model-anatomy.md) |
| **prefix caching** | 매 요청 동일한 프롬프트 앞부분(시스템 프롬프트 등)의 KV를 재사용해 TTFT를 줄이는 기법 ([02 §5](02-model-anatomy.md) 팁) |

## 3. 양자화·포맷

| 용어 | 뜻 |
| --- | --- |
| **양자화(quantization)** | 파라미터 정밀도를 낮춰 용량을 줄이는 압축 ([03 §2](03-quantization.md)) |
| **FP16 / BF16 / FP8 / INT8 / INT4** | 이름상 bit width가 16 / 16 / 8 / 8 / 4인 수치 표현. 실제 model file은 scale·metadata 등으로 단순 계산과 차이 날 수 있다 |
| **bpw (bits per weight)** | 파라미터당 실효 비트 수. "Q4"도 배율 저장분 때문에 실제로는 ~4.8bpw ([03 §4](03-quantization.md)) |
| **GGUF** | 가중치·토크나이저·메타데이터를 한 파일에 담는 **포맷**. llama.cpp 계열 |
| **safetensors** | Hugging Face 표준 가중치 저장 형식. 디렉터리 단위로 배포 |
| **GPTQ / AWQ / EXL2** | 양자화 **알고리즘**. 결과는 safetensors로 저장 ([03 §3](03-quantization.md)) |
| **Q4_K_M** | GGUF의 4bit 계열 K-quant 변형 중 하나. runtime 지원과 task quality를 확인해 선택한다 |
| **K-quant** | GGUF의 개선 양자화 계열(`_K`). 상위 블록에 배율을 이중 저장하고 텐서별로 비트를 차등 배분 ([03 §4](03-quantization.md)) |
| **imatrix / IQ 계열** | importance matrix를 활용하는 양자화 계열. 같은 용량에서도 model·calibration·task에 따라 결과가 달라진다 ([03 §4](03-quantization.md)) |
| **캘리브레이션 데이터** | 양자화 시 "어느 가중치가 중요한가"를 재는 샘플 텍스트. 배포자 간 품질 차이의 주요 원인 ([03 §2](03-quantization.md) 팁) |
| **NVFP4 / MXFP4** | 4bit 부동소수 형식. Blackwell 네이티브이며 일부 모델(gpt-oss 등)의 기본 배포 형식 ([03 §3](03-quantization.md)) |
| **perplexity** | 모델이 다음 토큰을 얼마나 "덜 놀라며" 맞히는가의 지표. 낮을수록 좋다. 양자화 품질 비교에 자주 쓰인다 ([03 §4](03-quantization.md)) |
| **MLX** | Apple Silicon용 array·machine learning framework. `mlx-lm`은 이를 이용해 LLM을 실행·변환하는 도구다 ([05 §2](05-stack-map.md)) |

## 4. 실행·서빙

| 용어 | 뜻 |
| --- | --- |
| **경험층 / 엔진 / 서빙 시스템** | Ollama·LM Studio / llama.cpp·MLX / vLLM·SGLang. **층이 다르다** ([05 §1](05-stack-map.md)) |
| **프런트엔드** | 실행 스택 위에 얹는 채팅 화면(Open WebUI 등). "ChatGPT 같은 화면"의 정체 ([05 §2](05-stack-map.md)) |
| **Modelfile** | Ollama에서 기반 모델 + 파라미터(컨텍스트 등)를 묶어 파생 모델을 정의하는 파일 ([06 §2](06-setup-apple-silicon.md)) |
| **venv (가상환경)** | Python 패키지를 프로젝트별로 격리하는 표준 도구 ([06 §5](06-setup-apple-silicon.md)) |
| **연속 배칭(continuous batching)** | 생성 중인 요청 사이에 새 요청을 끼워 GPU를 채우는 기법 ([05 §3](05-stack-map.md)) |
| **PagedAttention** | KV cache를 block 단위로 관리해 memory 낭비를 줄이는 기법 ([05 §3](05-stack-map.md)) |
| **텐서 병렬(TP)** | 각 layer의 tensor 연산을 여러 GPU가 나누는 방식. model·runtime에 따라 head 수 등 제약이 있다 ([08 §2](08-setup-multi-gpu-server.md)) |
| **파이프라인 병렬(PP)** | 레이어를 구간별로 GPU에 배치 ([08 §2](08-setup-multi-gpu-server.md)) |
| **버블(bubble)** | 파이프라인 병렬에서 앞 단계를 기다리느라 GPU가 노는 빈 시간 — PP의 대가 ([08 §2](08-setup-multi-gpu-server.md)) |
| **OpenAI 호환 API** | 여러 runtime이 OpenAI API와 비슷한 request shape로 제공하는 interface. 지원 endpoint와 세부 동작은 서로 다를 수 있다 ([05 §4](05-stack-map.md)) |
| **open-weight** | 가중치만 공개. **학습 데이터·코드 공개와 자유 라이선스를 뜻하지 않는다** ([01 §2](01-orientation.md)) |
| **hosted LLM / local LLM** | 사업자 서버의 모델을 API로 호출 / 가중치를 내 장비에서 직접 실행 ([01 §0](01-orientation.md)) |
| **hybrid** | 게이트웨이가 요청 성격(민감도·빈도·난도)에 따라 local 모델과 hosted API로 라우팅하는 기업 도입 구성 ([01 §0](01-orientation.md)) |

## 5. 인프라·하드웨어

셋업 문서(06~08)에서 주로 만나는 용어다.

| 용어 | 뜻 |
| --- | --- |
| **Metal** | Apple의 GPU 프로그래밍 프레임워크. Mac에서 "GPU 가속이 된다"의 실체 ([06](06-setup-apple-silicon.md)) |
| **CUDA** | NVIDIA의 GPU computing platform. 많은 AI runtime이 우선 지원한다. "CUDA toolkit"은 `nvcc` 등을 포함한 개발 도구 모음이다 ([07 §2](07-setup-nvidia-workstation.md)) |
| **ROCm** | AMD GPU용 open software stack. model·GPU·OS별 지원 범위를 확인해야 한다 ([04 §3.1](04-hardware-tiers.md)) |
| **HBM** | 데이터센터 GPU에 쓰이는 초고대역 메모리 ([04 §3.2](04-hardware-tiers.md)) |
| **NVLink / NVSwitch** | NVIDIA 카드 간 고속 직결 / 그것을 여러 장으로 묶는 스위치. 현행 라인업 기준 SXM 카드에 있다 ([08 §3](08-setup-multi-gpu-server.md)) |
| **SXM** | 데이터센터 GPU의 보드 직결 폼팩터(카드를 꽂는 방식 자체가 다르다). PCIe 카드 형태와 대비된다 |
| **PCIe** | 카드·주변장치를 잇는 범용 버스. NVLink가 없는 다중 GPU 구성의 통신 경로이자 병목 지점 ([08 §3](08-setup-multi-gpu-server.md)) |
| **NCCL** | NVIDIA의 다중 GPU 통신 라이브러리. 멀티 GPU 문제 진단의 첫 관문 ([08 §3](08-setup-multi-gpu-server.md) 팁) |
| **WSL2** | Windows 안에서 Linux 환경을 실행하는 기능. Windows에서 Linux 중심 GPU runtime을 쓰는 주요 선택지 중 하나다 ([07 §2](07-setup-nvidia-workstation.md)) |
| **systemd / launchd** | Linux / macOS의 서비스 관리자. 서버를 "항상 떠 있게" 만드는 수단 ([10 §5](10-operations.md) 팁) |

## 6. 혼동하기 쉬운 쌍 ★

| 쌍 | 차이 |
| --- | --- |
| **hosted LLM vs local LLM** | 사업자 서버에서 실행 ↔ 내 장비에서 실행. 데이터 흐름과 비용 구조가 다르다 ([01 §0](01-orientation.md)) |
| **총 파라미터 vs 활성 파라미터** | 메모리 ↔ 속도. MoE에서 섞으면 계산이 통째로 틀린다 |
| **open-weight vs open-source** | 가중치만 ↔ 학습 코드·데이터까지 |
| **open-weight vs 자유 라이선스** | 공개 여부 ↔ 사용 허용 범위. **별개다** |
| **GGUF vs AWQ** | 파일 포맷 ↔ 양자화 알고리즘. 층이 다르다 |
| **VRAM 용량 vs 대역폭** | 가부(可否) ↔ 속도 |
| **처리량(throughput) vs 지연(latency)** | system 전체가 단위 시간에 처리하는 총량 ↔ 요청 하나가 걸리는 시간. benchmark는 concurrency·batch·hardware 조건과 함께 읽는다 ([05 §3](05-stack-map.md)) |
| **Ollama vs vLLM** | 둘 다 model server 기능이 있지만 초점이 다르다. Ollama는 local 사용 편의, vLLM은 동시 요청 서빙·처리량 운영에 더 초점을 둔다 |
| **스펙상 컨텍스트 vs 실제 컨텍스트** | 아키텍처 상한 ↔ 남은 메모리가 정하는 상한 |
| **오프로딩 vs 스왑** | GPU→RAM ↔ RAM→디스크. 둘 다 급격히 느려진다 |

---

**← [README로 돌아가기](README.md)**
