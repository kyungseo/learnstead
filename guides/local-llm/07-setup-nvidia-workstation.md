# 07 — 셋업: NVIDIA 단일 GPU 워크스테이션

GPU를 붙인 데스크톱·워크스테이션(Linux 또는 Windows+WSL2)에서 모델을 띄우는 절차.

← [06 Apple Silicon 셋업](06-setup-apple-silicon.md) · 다음 → [08 멀티 GPU·서버](08-setup-multi-gpu-server.md)

> **검증 상태:** 공식 문서를 대조했지만 **이 가이드 작성 환경에서는 실행하지 않았다.** 설치 전
> [검증 기록](VALIDATION.md)에서 runtime·driver별 확인 범위를 먼저 확인한다. `[문서 확인 · 2026-08-10]`

---

## 1. Apple Silicon과 결정적으로 다른 점

| 항목 | Apple Silicon | NVIDIA GPU |
| --- | --- | --- |
| 메모리 | CPU·GPU가 같은 통합메모리를 공유 | GPU가 VRAM을 우선 사용. 시스템 RAM 오프로딩은 가능하지만 보통 성능 손실이 크다 |
| 초과 시 | 스왑 (느려짐) | **오프로딩** — PCIe를 타서 급격히 느려짐 |
| 필수 준비 | 없음 (Metal 내장) | **드라이버 + (경로에 따라) CUDA 스택** — §2 분기표 |
| 서빙 옵션 | `llama-server`·`mlx_lm.server` 등 | vLLM을 비롯해 CUDA를 우선 지원하는 서빙 도구가 많다 |

`[원리]` — 구조 비교는 [04 §3.3](04-hardware-tiers.md).

**따라서 첫 단계는 "VRAM이 몇 GB인가"이고, 그 값이 [04 §2 티어표](04-hardware-tiers.md)의 입력이 된다.**

---

## 2. 전제 조건 확인

```bash
# GPU 인식과 VRAM 확인 — 이것이 안 되면 나머지가 무의미하다
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv

# CUDA 툴킷 (vLLM·소스 빌드에 필요. Ollama만 쓸 거면 없어도 된다)
nvcc --version
```

### ★ 성공 판정

`nvidia-smi`가 카드 이름과 총 VRAM을 출력한다. **출력이 없으면** 이 순서로 좁힌다:
① `lspci | grep -i nvidia` — 카드가 하드웨어로 인식되는가 → 안 되면 장착·슬롯 문제
② 드라이버 설치 상태 확인(배포판 패키지) → 설치·재부팅
③ 재부팅 후에도 안 되면 Secure Boot의 서명 문제(Linux)가 흔한 원인이다

| 상황 | 필요한 것 |
| --- | --- |
| Linux | NVIDIA 독점 드라이버. 배포판 패키지 관리자 경로 권장 |
| Windows | **WSL2**(Windows 안의 Linux 환경) + **Windows용** NVIDIA 드라이버. WSL 안에 드라이버를 또 설치하지 않는다 — 단, **CUDA 툴킷이 필요한 경로라면 WSL 안에 툴킷은 설치**해야 한다 `[자료 확인 · 2026-08-10]` |
| 컨테이너 사용 | NVIDIA Container Toolkit (`--gpus all`로 컨테이너에 GPU를 노출하는 구성요소) |

### 경로별 필요 조건 — 전부 다 깔 필요 없다

| 경로 | 드라이버 | 빌드 도구(cmake·컴파일러) | CUDA 툴킷(`nvcc`) | Python |
| --- | --- | --- | --- | --- |
| A. Ollama | 필요 | — | — | — |
| B. llama.cpp 빌드 | 필요 | **필요** | **필요** | — |
| C. vLLM | 필요 | — | (pip 빌드가 필요한 경우만) | **필요** |

---

## 3. 경로 A — Ollama (가장 빠른 시작)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull <model>
ollama run  <model>
```

설치 방식과 service 등록 여부는 배포판·WSL 구성·설치 script version에 따라 달라질 수 있다. 설치 뒤 먼저
`ollama --version`과 service 상태를 확인하고, 서버가 떠 있지 않을 때만 `ollama serve`를 실행한다.
`curl | sh`가 불편하다면 script를 파일로 내려받아 내용을 확인한 뒤 실행한다([10 §4](10-operations.md)).
`[문서 확인 · 2026-08-10]`

### ★ 성공 판정

```bash
ollama ps          # PROCESSOR 열이 GPU 여야 한다
nvidia-smi         # 모델 로드 중 VRAM 사용량이 올라가야 한다
```

**둘 다 확인한다.** `ollama ps`가 GPU라도 `nvidia-smi`의 사용량이 미미하면 일부만 올라간 것이다.

### VRAM이 모자랄 때 — 오프로딩의 실체

Ollama는 VRAM에 다 안 들어가면 **일부 레이어를 자동으로 CPU/RAM에 남긴다** `[자료 확인 · 2026-08-10]`.
죽지 않고 동작하지만 **급격히 느려진다** — PCIe 왕복이 병목이 되기 때문이다 `[원리]`.

![가중치가 VRAM을 벗어날수록 데이터 이동 비용이 커질 수 있으므로 실제 처리량을 비교해야 한다](diagrams/07-offload-spectrum.svg)

**대응 순서:** ① 더 강한 양자화([03](03-quantization.md)) → ② 컨텍스트 축소 → ③ 더 작은 모델.
대화형 응답 속도가 중요하면 오프로딩된 큰 model과 VRAM에 들어가는 작은 model을 같은 prompt로 비교한 뒤
선택한다. `[해석]`

> 🔧 **한 단계 더 — Ollama의 오프로딩도 수동 개입이 가능하다.** 자동 배분이 아슬아슬하게 어긋날 때
> `num_gpu` 파라미터(Modelfile `PARAMETER num_gpu <N>` 또는 API 옵션)로 GPU에 올릴 레이어 수를 직접
> 고정할 수 있다 — 경로 B의 `-ngl`과 같은 손잡이다. MoE 모델이라면 [02 §3](02-model-anatomy.md)의
> 전문가 오프로딩도 참고. `[자료 확인 · 2026-08-10]`

---

## 4. 경로 B — llama.cpp (CUDA 빌드)

패키지로 제공되는 llama.cpp가 CUDA 지원 없이 빌드된 경우가 있다. 직접 빌드하면 확실하다.
**전제:** §2 분기표의 빌드 도구 + CUDA 툴킷. `cmake`가 없다는 에러, `nvcc not found`류 에러는 전제 미충족이다.

```bash
# 소스를 둘 아무 작업 디렉터리에서 (예: ~/src)
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j"$(nproc)"
```

**핵심은 `-DGGML_CUDA=ON`이다.** 이것이 빠지면 CPU 전용 바이너리가 나온다. `[자료 확인 · 2026-08-10]`
(`-j`에 숫자 없이 쓰면 무제한 병렬이라 메모리 부족으로 빌드가 죽을 수 있어 `$(nproc)`로 코어 수만큼 제한한다.)

### 기동

위에서 `cd llama.cpp` 한 디렉터리 기준 경로다.

```bash
./build/bin/llama-server \
  -hf <hf-repo>:<quant-tag> \
  --jinja \
  -ngl 99 \
  -c 8192 \
  --host 0.0.0.0 --port 8080
```

| 플래그 | 의미 |
| --- | --- |
| `-ngl 99` | GPU에 올릴 레이어 수. 99 = 전부. VRAM이 모자라면 이 값을 낮춘다 |
| `-c 8192` | 컨텍스트 길이 |
| `--host 0.0.0.0` | 다른 기기에서의 접속 허용 (로컬 전용이면 생략) |

**`-ngl`이 이 경로의 핵심 튜닝 손잡이다.** `[원리]`
전부 올리면 가장 빠르고, VRAM이 모자라면 숫자를 낮춰 일부를 CPU에 남긴다 — 위 §3의 오프로딩을 **수동으로 제어**하는 셈이다.

### ★ 성공 판정

기동 로그에 `offloaded N/N layers to GPU`가 나오고(`0/N`이면 CPU 전용 — 재빌드 확인),
`nvidia-smi`에 VRAM 점유가 잡히며, `curl http://localhost:8080/v1/models`가 응답한다.

> 🔧 **한 단계 더 — 빌드·기동 옵션.** `-DCMAKE_CUDA_ARCHITECTURES=<sm>`(내 카드 아키텍처만 지정해
> 빌드 시간 단축), `-fa on`(Flash Attention — KV 양자화의 전제이기도 하다, [06 §4](06-setup-apple-silicon.md)),
> `--parallel <N>`(동시 요청 슬롯). 카드가 2장 이상이면 `--split-mode`·`-ts`로 레이어를 카드에 나눌 수
> 있으나, 그 규모면 [08](08-setup-multi-gpu-server.md)의 vLLM 경로를 먼저 검토한다. `[자료 확인 · 2026-08-10]`

---

## 5. 경로 C — vLLM (단일 GPU 서빙)

**혼자 쓸 거면 필요 없다**([05 §3](05-stack-map.md)). 다음 중 하나에 해당할 때 의미가 있다.

- 여러 명이 동시에 붙는다
- 배치 처리(대량 문서 요약 등)를 돌린다
- 운영 구성을 미리 연습해 둔다

vLLM은 특정 CUDA·PyTorch 버전에 묶이므로 **venv로 격리 설치**한다(경로 D의 venv 설명은 [06 §5](06-setup-apple-silicon.md)와 동일).

```bash
python3 -m venv ~/.venvs/vllm && source ~/.venvs/vllm/bin/activate
pip install vllm

vllm serve <model> \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90
```

| 플래그 | 의미 |
| --- | --- |
| `<model>` | Hugging Face model repository 이름 — local cache에 없으면 내려받는다 |
| `--max-model-len 8192` | 요청당 컨텍스트 상한 |
| `--gpu-memory-utilization 0.90` | vLLM이 쓸 VRAM 비율 |

사전 양자화 checkpoint는 model config와 현재 vLLM이 지원하는 방법을 먼저 확인한다. 일부 형식은 자동으로
인식하지만, model·hardware·vLLM version에 따라 `--quantization` 지정이나 별도 설치가 필요할 수 있다.
비양자화 model을 load할 때 적용하는 동적 양자화와 사전 양자화 checkpoint는 기동 시간·memory·quality 특성이
다르므로 같은 것으로 보지 않는다. `[문서 확인 · 2026-08-10]`

### 세 플래그의 관계 ★

```text
  총 VRAM = 가중치 + KV 캐시 + 활성화 메모리     ← 제로섬 예산
```
`[원리]`

| 플래그 | 조정 방향 | 효과 |
| --- | --- | --- |
| `--gpu-memory-utilization` | 0.85 → 0.95 | vLLM이 쓸 VRAM 총량. 높이면 KV 여유↑, 너무 높이면 OOM |
| `--max-model-len` | 낮춤 | 요청당 KV 상한↓ → 더 많은 동시 요청 |
| `--quantization` | awq / fp8 | 가중치↓ → KV에 쓸 공간↑ |

**튜닝 순서:** 먼저 `--max-model-len`을 실제 필요한 값으로 **낮추고**, 그다음 `--gpu-memory-utilization`을 올린다. `[해석]`

KV 캐시가 빠듯하면 지원되는 hardware와 model에서 `--kv-cache-dtype fp8`을 검토할 수 있다. 절감 폭과
quality 영향은 설정에 따라 달라지므로 [03 §7](03-quantization.md)의 절차로 비교한다. `[문서 확인 · 2026-08-10]`

> 🔧 **한 단계 더 — 서빙 튜닝 플래그.** `--max-num-seqs`(동시 처리 요청 상한 — "더 많은 동시 요청"을
> 실제로 정하는 손잡이), `--enable-prefix-caching`(공통 시스템 프롬프트 재사용 시 TTFT 급감),
> `--swap-space`(KV를 시스템 RAM으로 밀어내는 완충). 측정 없이 돌리지 말고 [10 §1](10-operations.md)로
> 전후를 잰다. `[자료 확인 · 2026-08-10]`

### 양자화 선택

| GPU 세대 | 권장 |
| --- | --- |
| FP8을 지원하는 데이터센터 GPU | FP8 checkpoint 또는 지원되는 동적 FP8을 후보로 두고 BF16과 memory·quality·throughput 비교 |
| 소비자용 GPU | runtime이 지원하는 AWQ·GPTQ·GGUF 등에서 VRAM과 task quality를 만족하는 checkpoint 선택 |

어느 세대가 FP8을 지원하는지는 GPU 라인업 이야기라 세대교체로 바뀐다 `[변동]` 조회 2026-08-10 — [04 §3.2](04-hardware-tiers.md).

### ★ 성공 판정

```bash
curl http://localhost:8000/v1/models          # 모델 목록이 나온다
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"1+1?"}]}'
```

---

## 6. Docker로 돌릴 때

```bash
docker run --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model <model> --max-model-len 8192
```
`[자료 확인 · 2026-08-10]`

| 옵션 | 왜 필요한가 |
| --- | --- |
| `--gpus all` | 컨테이너에 GPU 노출. NVIDIA Container Toolkit 필요 |
| `-v ~/.cache/huggingface` | **모델 재다운로드 방지.** 수십 GB를 매번 받지 않으려면 필수 |
| `--ipc=host` (또는 `--shm-size`) | 프로세스 간 공유메모리. 부족할 때의 증상은 [08 §5](08-setup-multi-gpu-server.md) |

> 🔧 **한 단계 더 — 운영을 의식한다면.** 이미지 태그를 `latest` 대신 버전으로 고정(재현성),
> `--restart unless-stopped`(재부팅 후 자동 기동), 게이트 모델(Llama 계열 등)은
> `-e HF_TOKEN=<token>`으로 Hugging Face 토큰을 전달해야 받아진다. `[자료 확인 · 2026-08-10]`

---

## 7. 증상별 대응

| 증상 | 원인 | 대응 |
| --- | --- | --- |
| `CUDA out of memory` | 예산 초과 | `--max-model-len` 축소 → `--gpu-memory-utilization` 하향 → 더 강한 양자화 |
| 로드는 되는데 느림 | CPU 오프로딩 발생 | `nvidia-smi`로 VRAM 점유 확인. `-ngl` 상향 또는 모델 축소 |
| `nvidia-smi`는 되는데 도구가 GPU를 못 봄 | CUDA 런타임·컨테이너 툴킷 누락 | 툴킷 설치 확인, 컨테이너면 `--gpus all` 확인 |
| 빌드했는데 CPU로만 돔 | `-DGGML_CUDA=ON` 누락 | 재빌드 |
| 첫 응답만 느림 | prefill·cold load·queue 등 | [10 §1](10-operations.md)의 TTFT 구성요소를 분리 확인 |

---

## 8. 체크리스트

- [ ] `nvidia-smi`가 카드와 VRAM을 출력한다
- [ ] VRAM 값을 [04 §2](04-hardware-tiers.md) 티어표에 대입해 목표 모델을 정했다
- [ ] 모델 로드 중 `nvidia-smi`의 VRAM 점유가 예상 범위에 들어온다
- [ ] 오프로딩이 발생하지 않았다 (레이어가 전부 GPU에 올라갔다)
- [ ] OpenAI 호환 엔드포인트가 응답한다
- [ ] 실사용 컨텍스트 길이로 테스트했다

---

**다음 →** [08 멀티 GPU·사내 서버](08-setup-multi-gpu-server.md)
