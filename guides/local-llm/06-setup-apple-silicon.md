# 06 — 설정: Apple Silicon Mac

M-series Mac에서 model을 실행하는 절차입니다. 24GB unified memory를 예시로 쓰지만, 실제 판단은 model file,
context와 runtime log를 자기 장비에서 확인해야 합니다.

← [05 스택 지도](05-stack-map.md) · 다음 → [07 NVIDIA 워크스테이션 셋업](07-setup-nvidia-workstation.md)

> **검증 상태:** Ollama 경로는 M4 Pro·통합 메모리 24GB 환경에서 설치, 한국어 생성, GPU 적재와 OpenAI 호환
> API까지 확인했습니다. LM Studio, llama.cpp와 MLX 직접 실행 경로는 공식 자료만 대조했으며 아직 실행하지
> 않았습니다. 세부 환경과 수치는 [검증 기록](VALIDATION.md)을 확인하세요. `[부분 검증 · 2026-08-11]`

---

## 1. 시작 전 — 내 장비 확인

```bash
sysctl -n machdep.cpu.brand_string          # 칩 (예: Apple M4 Pro)
system_profiler SPHardwareDataType | grep Memory   # 통합메모리 용량
sw_vers                                      # macOS 버전
```

**전제 조건:** 최신 macOS 권장. 경로별로 요건이 다르다 — MLX 계열(경로 A의 MLX 엔진·경로 D)은
macOS 13.3 이상이 일반적 요건이고, llama.cpp의 Metal 가속은 그보다 낮은 버전에서도 동작한다. `[변동]` 조회 2026-08-10

### 예산 계산 — 24GB 예시

24GB 전부를 model이 사용할 수는 없습니다. macOS, 다른 application, KV cache와 runtime overhead가 같은 unified
memory를 나눠 씁니다. 첫 시도는 4B급 model로 성공 경로를 확인하고, 8~14B급으로 단계적으로 올리며 Activity
Monitor와 runtime log를 확인하는 편이 안전합니다. 20B 이상은 model 구조·quantization·context에 따라 차이가 커서
[02 산식](02-model-anatomy.md)으로 따로 계산합니다. `[해석]`

bandwidth가 높은 chip이 decode에 유리할 수 있지만 실제 속도는 model·format·engine·prompt 길이에 따라 달라집니다.
서로 다른 Mac을 제품명만으로 비교하지 말고 [10의 측정 항목](10-operations.md)을 같은 조건으로 기록하세요.

---

## 2. 경로 A — Ollama (권장 시작점)

**가장 짧게 결과를 보는 경로입니다.** Ollama는 Apple Silicon GPU를 사용할 수 있지만 실제 백엔드와 적재 방식은
버전과 모델 태그에 따라 달라질 수 있습니다. 성공 여부는 `ollama ps`와 로그로 확인합니다.
`[실행 검증 · 2026-08-11]`

### 설치

```bash
brew install ollama          # Homebrew 사용 시
# 또는 https://ollama.com 에서 macOS 앱 내려받기
```

### 서버 기동과 모델 실행

Homebrew 설치 경로에서는 첫 번째 터미널에서 서버를 현재 프로세스로 실행하고 창을 열어 둡니다.

```bash
ollama serve
```

앱으로 설치했다면 서버가 이미 실행 중일 수 있습니다. 이때 `ollama serve`에서
`Error: listen tcp 127.0.0.1:11434: bind: address already in use`가 나오면 서버를 중복 실행한 것이므로 기존
서버를 그대로 사용합니다.

두 번째 터미널에서 모델을 실행합니다.

```bash
ollama run gemma3:4b         # 첫 실행에서 model을 내려받고 대화 시작
```

다른 model을 고를 때는 [09 model 선택 지도](09-model-landscape.md)와 Ollama library에서 tag, file size, license와
필요한 Ollama version을 확인합니다.

### ★ 성공 판정

```bash
ollama ps
```

`PROCESSOR` 열은 모델이 GPU·CPU 메모리에 어떻게 배치됐는지 보여 줍니다. Apple Silicon에서 GPU가 전혀 표시되지
않으면 버전, 모델 호환성과 로그를 확인합니다. `[실행 검증 · 2026-08-11]`

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma3:4b","messages":[{"role":"user","content":"1+1?"}]}'
```

응답 JSON이 오면 **OpenAI 호환 API가 동작한다**는 뜻입니다([05 §4](05-stack-map.md)).

이번 검증에서는 다음 결과를 확인했습니다.

| 항목 | 결과 |
| --- | --- |
| Ollama | 0.32.7 |
| 모델 | `gemma3:4b`, 4.3B 파라미터, Q4_K_M, 파일 3.3GB |
| 적재 상태 | 3.7GB, `100% GPU`, 실행 중 컨텍스트 4,096 |
| 한국어 생성 | 짧은 질문에 응답을 끝까지 생성 |
| API | `/v1/chat/completions`가 정상 JSON과 답변을 반환 |

`ollama show`에는 모델의 최대 컨텍스트가 131,072로 표시됐지만, 실제 실행 시 `ollama ps`에 표시된 값은
4,096였습니다. 긴 컨텍스트가 필요하다면 기본값이나 모델 상한만 믿지 말고 실제 실행 값을 확인한 뒤 메모리 사용량을
다시 측정해야 합니다. 상세 수치와 한계는 [검증 기록](VALIDATION.md)에 남겼습니다.

> 🔧 **한 단계 더 — 알아두면 좋은 Ollama 환경변수.** `OLLAMA_KEEP_ALIVE`(유휴 시 모델을 내리기까지의
> 시간 — 기본 5분이라 오랜만의 질문이 느린 이유), `OLLAMA_MODELS`(모델 저장 경로 이전 — 디스크 관리는
> [10 §5](10-operations.md)), `OLLAMA_HOST`(다른 기기에서 접속 허용), `OLLAMA_KV_CACHE_TYPE`(KV 캐시
> 양자화 — [03 §7](03-quantization.md)). 서버 기동 전에 export 해 둔다. `[자료 확인 · 2026-08-10]`

### 컨텍스트 길이 조정 — 메모리가 모자랄 때

Ollama의 기본 context와 model별 상한은 version에 따라 달라질 수 있습니다. 긴 context는 KV memory를 늘리므로
model은 load되지만 실제 request에서 memory가 부족할 수 있습니다([02 §5](02-model-anatomy.md)).

**방법 ① — 대화 세션 한정.** 아래는 셸 명령이 아니라 **`ollama run <model>`로 들어간 대화 프롬프트
안에서** 치는 명령이다(터미널에 그대로 치면 `command not found`가 난다):

```text
>>> /set parameter num_ctx 4096
```

**방법 ② — 고정.** `Modelfile`이라는 파일을 만들어 파생 모델로 등록한다:

```bash
cat > Modelfile <<'EOF'
FROM <model>
PARAMETER num_ctx 4096
EOF

ollama create <model>-4k -f Modelfile   # 파생 모델 등록
ollama run <model>-4k                   # 이후 이 이름으로 실행
```
`[자료 확인 · 2026-08-10]`

---

## 3. 경로 B — LM Studio (GUI)

모델을 **둘러보며 고르고 싶을 때** 적합하다. MLX를 네이티브로 지원한다. `[자료 확인 · 2026-08-10]`

1. `https://lmstudio.ai` 에서 앱 설치
2. 검색 탭에서 모델 검색 — **MLX 빌드와 GGUF 빌드가 함께 나온다**. Apple Silicon이면 MLX 쪽을 고른다
3. 다운로드 후 대화 탭에서 로드
4. 필요하면 **Local Server** 기능으로 OpenAI 호환 엔드포인트를 노출

### ★ 성공 판정

- 모델 로드 후 앱에 표시되는 **메모리 사용량이 §1의 예산(규칙 ②) 안**에 들어온다
- 대화에 응답이 오고, 생성 중 Activity Monitor의 **GPU 사용률이 올라간다** (안 올라가면 CPU로 돌고 있는 것 — 모델 설정에서 GPU 오프로딩 확인)

**한계:** 기본적으로 GUI 워크플로 중심이다. 자동화가 필요해지면 경로 A나 C가 자연스럽다
(LM Studio도 헤드리스 서버 모드·`lms` CLI를 제공하긴 한다 — [05 §6](05-stack-map.md)). `[해석]`

---

## 4. 경로 C — llama.cpp 직접 (세밀한 제어)

옵션을 직접 다뤄야 할 때, 또는 **아주 새로운 모델 아키텍처**를 빨리 써야 할 때. `[해석]`

```bash
brew install llama.cpp
```

### 서버 기동

```bash
llama-server -hf <hf-repo>:<quant-tag> --jinja -ngl 99 -c 8192
```

| 플래그 | 의미 |
| --- | --- |
| `-hf` | Hugging Face 저장소에서 GGUF를 직접 받아 실행 |
| `--jinja` | 모델의 채팅 템플릿 적용 |
| `-ngl 99` | **GPU에 올릴 레이어 수.** 99 = 전부. Metal 가속의 핵심 플래그 |
| `-c 8192` | 컨텍스트 길이. 메모리가 모자라면 여기를 줄인다 |

포트를 지정하지 않으면 **기본 8080**에 뜬다 (아래 판정 curl이 8080인 이유). 바꾸려면 `--port`. `[자료 확인 · 2026-08-10]`

### KV 캐시 양자화 — 컨텍스트를 늘리고 싶을 때

```bash
llama-server ... -fa on --cache-type-k q8_0 --cache-type-v q8_0
```

KV 캐시의 바이트 수를 줄이는 선택지다. 절감 폭과 품질 영향은 캐시 정밀도·모델·컨텍스트에 따라 달라지므로,
적용 전후의 메모리와 응답 품질을 함께 비교한다([03 §7](03-quantization.md)). **V 캐시 양자화는
Flash Attention(`-fa`) 활성이 전제**다 — 빼면 V 쪽이 적용되지 않는다. `[문서 확인 · 2026-08-10]`

> 🔧 **한 단계 더 — 플래그 스윕은 llama-bench로.** `-ngl`·`-c`·양자화 조합별 속도는 감이 아니라
> `llama-bench -m <model.gguf>`로 잰다. 메모리가 넉넉하면 `--mlock`(모델을 스왑 대상에서 제외)도
> 시도할 가치가 있다. `[자료 확인 · 2026-08-10]`

### ★ 성공 판정

기동 로그에 **Metal 백엔드 초기화**와 **GPU에 올라간 레이어 수**가 표시된다. `offloaded 99/99 layers to GPU` 형태의 줄이 보이면 정상이다.
`0/99`면 CPU로만 도는 것이다. `[해석]`

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"1+1?"}]}'
```

---

## 5. 경로 D — MLX 직접 (Python에서 세밀하게 제어)

Apple 자체 프레임워크를 직접 쓰는 경로. **Python 환경이 필요하다.** `[자료 확인 · 2026-08-10]`

먼저 **venv(가상환경)를** 만든다 — 시스템 Python을 건드리지 않고 패키지를 격리하는 표준 방법이다.
새 터미널을 열면 `source` 줄만 다시 실행하면 된다.

```bash
python3 -m venv ~/.venvs/mlx && source ~/.venvs/mlx/bin/activate
pip install mlx-lm

# 단발 생성
mlx_lm.generate --model mlx-community/<model>-4bit --prompt "안녕하세요"

# OpenAI 호환 서버
mlx_lm.server --model mlx-community/<model>-4bit --port 8080
```

**모델은 Hugging Face의 `mlx-community` 계정(organization)에서 찾는다** — MLX 전용으로 변환된 빌드가 모여 있다. `[자료 확인 · 2026-08-10]`

### ★ 성공 판정

- `mlx_lm.generate`가 프롬프트에 이어 **생성 텍스트와 토큰 속도 통계**를 출력한다
- 생성 중 Activity Monitor의 **GPU 사용률이 올라간다**
- 서버를 띄웠다면 경로 C와 같은 형식의 curl(포트 8080)에 응답한다

> **언제 D를 고르나:** Ollama의 간단한 실행 흐름보다 model load·generation parameter·Python integration을
> 직접 제어하고 싶을 때다. 같은 model이라도 runtime·format·version에 따라 속도가 달라지므로 MLX가 언제나
> 더 빠르다고 가정하지 말고 같은 조건에서 측정한다. `[해석]`

> 🔧 **한 단계 더 — 원하는 모델의 MLX 빌드가 없으면 직접 변환한다.**
> `mlx_lm.convert --hf-path <repo> -q` 한 줄로 HF 모델을 4bit MLX로 변환할 수 있다.
> 파인튜닝(`mlx_lm.lora`)도 같은 패키지에 있으나 이 가이드 범위 밖이다. `[자료 확인 · 2026-08-10]`

---

## 6. memory가 빠듯할 때 안전한 순서

undocumented `sysctl`이나 boot-time 설정으로 GPU memory 한도를 바꾸는 방법도 공유되지만, OS version별 동작과
복구 위험을 이 가이드에서 검증하지 않았습니다. 초급자 경로에는 포함하지 않습니다. 다음 순서로 줄이는 편이
안전합니다.

1. `ollama stop <model>` 또는 사용 중인 runtime을 종료해 memory를 돌려받습니다.
2. browser, IDE와 다른 큰 application을 종료합니다.
3. context length를 줄입니다.
4. 더 작은 quantization을 시험하되 실제 task quality를 다시 확인합니다.
5. 그래도 부족하면 더 작은 model로 바꿉니다.

Activity Monitor의 Memory Pressure가 계속 yellow/red이거나 swap이 빠르게 늘면 성공으로 보지 않습니다. model이
간신히 load되는 것보다 OS와 함께 안정적으로 쓸 수 있는 구성을 선택합니다. `[해석]`

---

## 7. Apple Silicon에서 자주 보는 증상

| 증상 | 원인 | 대응 |
| --- | --- | --- |
| `ollama ps`가 `CPU`로 표시 | Metal 가속 미적용 | macOS 버전 확인, Ollama 재설치 |
| 로드는 되는데 매우 느림 | **스왑 발생** — 메모리 예산 초과 | 모델을 한 단계 작게, 컨텍스트 축소 |
| Activity Monitor 메모리 압박이 노랑·빨강 | 압박 ≠ 스왑이지만 지속되면 성능 저하 | 다른 앱 종료, 모델 축소 `[자료 확인 · 2026-08-10]` |
| 긴 prompt에서 첫 응답이 느림 | prefill 처리량, context와 model 영향 | input token 수를 기록하고 TTFT 비교 |
| 같은 model인데 다른 Mac보다 느림 | chip·bandwidth 외 engine·format·version 차이 | 조건을 맞춘 뒤 [10의 형식](10-operations.md)으로 측정 |

`[해석]` — 일반 진단 절차는 [10 §3](10-operations.md).

---

## 8. 체크리스트

- [ ] macOS 버전이 Metal 요건을 만족한다
- [ ] 통합메모리 용량을 확인하고 §1로 예산을 계산했다
- [ ] model file·KV·overhead가 OS와 다른 application 몫을 남기고 들어간다
- [ ] `ollama ps`가 `GPU`를 표시한다 (또는 llama.cpp 로그에 레이어가 GPU로 올라갔다)
- [ ] OpenAI 호환 엔드포인트에 curl이 응답한다
- [ ] 실사용할 컨텍스트 길이로 한 번 테스트했다 (짧은 대화만 테스트하면 KV memory 한계를 확인하기 어렵다)

---

**다음 →** [07 NVIDIA 워크스테이션 셋업](07-setup-nvidia-workstation.md)
