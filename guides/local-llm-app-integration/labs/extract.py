#!/usr/bin/env python3
"""구조화 출력 — 자유 문장을 JSON 스키마로 강제해 프로그램이 읽게 한다.

사용법:
  python3 extract.py "다음 주 화요일 오후 3시에 김서연 팀장과 검색 고도화 프로젝트 중간 점검 회의, 대회의실 D"
  python3 extract.py "..." --no-schema     # 스키마 강제 없이 '프롬프트로만' 요청 (비교용)

전제: Ollama 실행 중, `ollama pull gemma3:4b`, `pip install openai`
"""

import argparse
import json
import sys

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=120.0, max_retries=0)
MODEL = "gemma3:4b"

# (1) 스키마: 프로그램이 읽을 '모양'을 먼저 정한다. required 로 빠지면 안 되는 필드를 고정한다.
MEETING_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "회의 제목"},
        "when": {"type": "string", "description": "일시. 원문에 있는 표현 그대로"},
        "where": {"type": "string", "description": "장소. 없으면 빈 문자열"},
        "attendees": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "0~1. 원문에서 확실히 읽어낸 정도"},
    },
    "required": ["title", "when", "where", "attendees", "confidence"],
    "additionalProperties": False,
}

SYSTEM = "문장에서 회의 정보를 추출한다. 원문에 없는 값은 지어내지 말고 빈 문자열 또는 빈 배열로 둔다."


def extract(text: str, use_schema: bool) -> dict:
    kwargs = {}
    if use_schema:
        # (2) 런타임이 토큰 단위로 스키마를 강제한다 — 형식 오류가 구조적으로 사라진다
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "meeting", "schema": MEETING_SCHEMA},
        }
        user = text
    else:
        user = f"{text}\n\n위 문장을 title, when, where, attendees, confidence 키를 가진 JSON으로만 답하라."
    resp = client.chat.completions.create(
        model=MODEL, temperature=0, messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], **kwargs
    )
    raw = resp.choices[0].message.content
    if not raw:
        raise ValueError("응답 본문이 비어 있습니다")
    print("원문 응답:", raw, "\n")
    # (3) 파싱 — 스키마 강제 시 여기서 실패하지 않아야 정상. 프롬프트만 쓰면 코드 펜스·설명문이 섞여 실패할 수 있다
    return json.loads(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--no-schema", action="store_true")
    args = ap.parse_args()
    try:
        data = extract(args.text, use_schema=not args.no_schema)
    except json.JSONDecodeError as e:
        sys.exit(f"JSON 파싱 실패: {e}  ← 프롬프트만으로는 형식을 보장할 수 없다")
    # (4) 내용 검증 — 형식은 런타임이 보장하지만 '값이 맞는가'는 내 코드가 본다
    missing = [k for k in MEETING_SCHEMA["required"] if k not in data]
    if missing:
        sys.exit(f"필수 필드 누락: {missing}")
    if not isinstance(data.get("attendees"), list) or not all(isinstance(v, str) for v in data["attendees"]):
        sys.exit("필드 형식 오류: attendees는 문자열 배열이어야 합니다")
    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        sys.exit("필드 범위 오류: confidence는 0~1 숫자여야 합니다")
    print("파싱 결과:")
    for k, v in data.items():
        print(f"  {k:11} = {v!r}")
    if data["confidence"] < 0.5:
        print("\n(confidence 낮음 — 사람 확인 경로로 보낼 값)")


if __name__ == "__main__":
    main()
