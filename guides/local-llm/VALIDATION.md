# 검증 기록

이 문서는 **내 장비에서 LLM 직접 실행하기**의 명령을 어디까지 실제로 확인했는지 기록합니다. 공식 문서를 확인한
것과 명령을 직접 실행한 것은 구분합니다.

## 현재 요약

| 경로 | 상태 | 확인 범위 |
| --- | --- | --- |
| 문서 구조와 내부 링크 | 통과 | 2026-08-11 `python3 tools/validate.py` |
| Apple Silicon + Ollama | 실행 검증 | 설치·모델 내려받기·한국어 생성·GPU 적재·OpenAI 호환 API 확인 |
| Apple Silicon + llama.cpp | 미검증 | 명령과 옵션을 공식 문서에서만 확인 |
| Apple Silicon + MLX LM | 미검증 | 명령과 서버 주의사항을 공식 저장소에서만 확인 |
| NVIDIA 단일 GPU | 미검증 | WSL, CUDA, llama.cpp, vLLM 공식 문서 대조 |
| multi-GPU vLLM | 미검증 | 병렬 처리·지표·KV cache 공식 문서 대조 |

## 기준 장비

공개 가능한 최소 정보만 기록합니다.

| 항목 | 값 |
| --- | --- |
| 확인일 | 2026-08-11 |
| 하드웨어 | Apple M4 Pro, 통합 메모리 24GB |
| OS | macOS 26.6.1 |
| 설치 확인 | Homebrew, Python 3, Ollama 0.32.7 |
| 실행 모델 | `gemma3:4b` (`a2af6cc3eb7f`, 3.3GB) |
| 아직 설치하지 않은 도구 | `llama-cli`, `llama-server`, `mlx_lm` |

일련번호, 하드웨어 UUID, 장치 식별자와 개인 디렉터리는 기록하지 않습니다.

## Apple Silicon + Ollama 실행 결과

2026-08-11, Homebrew로 Ollama 0.32.7을 설치하고 서버를 현재 터미널의 프로세스로 실행했습니다. 로그인 시 자동 시작되는
서비스는 등록하지 않았습니다. 이어서 다음 명령과 OpenAI 호환 API를 확인했습니다.

```bash
ollama --version
ollama run gemma3:4b
ollama show gemma3:4b
ollama ps
```

### 관찰 결과

| 확인 항목 | 결과 |
| --- | --- |
| 모델 내려받기와 적재 | 통과. `gemma3:4b`, ID `a2af6cc3eb7f`, 파일 크기 3.3GB |
| 모델 정보 | Gemma 3, 4.3B 파라미터, Q4_K_M, 최대 컨텍스트 131,072로 표시 |
| 한국어 생성 | 통과. 짧은 한국어 질문에 응답을 끝까지 생성 |
| GPU 적재 | `ollama ps`에서 `100% GPU`, 실행 중 컨텍스트 4,096, 적재 크기 3.7GB로 표시 |
| OpenAI 호환 API | `/v1/chat/completions`가 HTTP 응답과 정답 `2`를 반환 |

`ollama show`의 컨텍스트 131,072는 모델이 선언한 상한이고, `ollama ps`의 4,096는 이 실행에 적용된 값입니다.
두 수치를 같은 의미로 읽지 않아야 합니다. 또한 모델 파일의 사용 조건은 이 저장소의 Apache-2.0과 별개인
**Gemma Terms of Use**입니다.

### 1회성 속도 관찰

모델이 이미 적재된 상태에서 짧은 한국어 프롬프트를 `--verbose`로 한 번 실행했습니다.

| 지표 | 관찰값 |
| --- | --- |
| 입력 처리 | 26토큰, 약 209.47 tokens/s |
| 생성 | 36토큰, 약 63.09 tokens/s |
| 전체 소요 시간 | 약 0.94초 |

이 값은 짧은 프롬프트 한 건의 **환경 확인용 관찰값**입니다. 반복 측정, 워밍업 통제, 고정 시드와 긴 컨텍스트를
갖춘 벤치마크가 아니므로 다른 장비나 모델의 성능 비교 근거로 사용하지 않습니다.

## 실행하지 않은 경로를 읽는 법

NVIDIA와 multi-GPU 절차에는 `성공 판정`을 함께 적었지만, 이 작성 환경에서 성공했다는 뜻은 아닙니다. 독자는
자기 환경에서 다음 정보를 기록해야 재현 가능한 issue를 만들 수 있습니다.

- OS·kernel 또는 WSL version
- GPU 이름·개수·VRAM과 driver version
- 런타임 버전과 정확한 모델 저장소·revision·quantization
- 실행 명령과 전체 오류 중 비밀값을 제거한 부분
- 컨텍스트 길이, 최대 메모리, TTFT·TPS 또는 처리량

API 토큰, 내부 hostname·IP, 개인 경로와 모델 접근 토큰은 공개 이슈에 넣지 않습니다.

## 정적 검증

저장소 루트에서 다음 명령으로 필수 파일, 내부 링크, 공개 금지 식별자, 후행 공백과 SVG XML을
확인합니다.

```bash
python3 tools/validate.py
```

공개 직전에는 초안 상태 표기까지 검사합니다.

```bash
python3 tools/validate.py --public
```

2026-08-11 공개 전 `python3 tools/validate.py`와 `python3 tools/validate.py --public`을 실행해 통과했습니다.
정적 검증 통과는 런타임 명령의 실행 성공을 대신하지 않습니다.
