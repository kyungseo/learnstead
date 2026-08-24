#!/usr/bin/env python3
"""작은 대화 프로그램 — 대화 기록을 내 프로그램이 들고, 스트리밍으로 출력한다.

사용법:
  python3 chat.py                       # 대화 시작. /reset 기록 초기화, /history 기록 보기, /quit 종료
  python3 chat.py --model qwen3:4b      # 모델 바꾸기
  python3 chat.py --no-stream           # 스트리밍 끄기 (응답을 한 번에 받음)
  python3 chat.py --max-history 6       # 기록에 남길 최근 메시지 수 (system 제외)

전제: Ollama 실행 중, `ollama pull gemma3:4b`, `pip install openai`
"""

import argparse
import sys

from openai import OpenAI

SYSTEM = "너는 간결하게 답하는 한국어 도우미다. 모르는 것은 모른다고 말한다."


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("1 이상의 정수를 입력하세요")
    return parsed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma3:4b")
    ap.add_argument("--base-url", default="http://localhost:11434/v1")
    ap.add_argument("--no-stream", action="store_true")
    ap.add_argument("--max-history", type=positive_int, default=20, help="system 제외 최근 N개 메시지만 보냄")
    ap.add_argument("--max-tokens", type=positive_int, default=512)
    args = ap.parse_args()

    client = OpenAI(base_url=args.base_url, api_key="ollama", timeout=120.0, max_retries=0)
    history: list[dict] = []  # system 을 제외한 대화 기록 — 이 리스트가 '대화 상태'의 전부다

    print(f"모델 {args.model} · /reset /history /quit")
    while True:
        try:
            user = input("\n나> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user == "/quit":
            break
        if user == "/reset":
            history.clear()
            print("(기록을 비웠습니다)")
            continue
        if user == "/history":
            for m in history:
                print(f"  [{m['role']}] {m['content'][:60]}")
            continue

        history.append({"role": "user", "content": user})
        # (1) 매 요청에 system + 최근 기록 전체를 보낸다 — runtime은 이전 요청을 기억하지 않는다
        messages = [{"role": "system", "content": SYSTEM}] + history[-args.max_history :]

        print("AI> ", end="", flush=True)
        try:
            if args.no_stream:
                resp = client.chat.completions.create(
                    model=args.model, messages=messages, temperature=0.3, max_tokens=args.max_tokens
                )
                text = resp.choices[0].message.content or ""
                print(text)
                finish = resp.choices[0].finish_reason
                usage = resp.usage
            else:
                # (2) 스트리밍: 조각(delta)을 받는 대로 출력하고, 전체를 이어 붙여 기록에 넣는다
                stream = client.chat.completions.create(
                    model=args.model, messages=messages, temperature=0.3, max_tokens=args.max_tokens,
                    stream=True, stream_options={"include_usage": True},
                )
                parts, finish, usage = [], None, None
                for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta.content or ""
                        parts.append(delta)
                        print(delta, end="", flush=True)
                        finish = chunk.choices[0].finish_reason or finish
                    if chunk.usage:
                        usage = chunk.usage
                print()
                text = "".join(parts)
        except Exception as e:  # 연결 거부, 모델 없음 등 — 10 문서의 오류 유형 참조
            print(f"\n[오류] {type(e).__name__}: {e}")
            history.pop()  # 실패한 user 메시지는 기록에서 제거
            continue

        # (3) 모델의 답을 assistant 메시지로 기록에 추가 — 다음 요청에 함께 보내진다
        history.append({"role": "assistant", "content": text})
        note = f"finish={finish}"
        if usage:
            note += f" · prompt {usage.prompt_tokens} / completion {usage.completion_tokens} 토큰"
        if finish == "length":
            note += "  ← max_tokens 에 걸려 잘렸다"
        print(f"   ({note})")


if __name__ == "__main__":
    sys.exit(main())
