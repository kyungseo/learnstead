#!/usr/bin/env python3
"""단일 호출과 네 가지 오케스트레이션 패턴을 같은 과제로 비교 실행한다.

과제: 사내 문의에 답하기 (docs/ 의 규정 3편 사용)

사용법:
  python3 patterns.py single   "관리자는 연차를 며칠까지 이월할 수 있나요?"   # 비교 기준선 — 단일 호출
  python3 patterns.py pipeline "관리자는 연차를 며칠까지 이월할 수 있나요?"   # 순서 고정 (분류 → 답변 → 다듬기)
  python3 patterns.py router   "노트북은 언제까지 반납하나요?"                # 분류 후 담당자에게 위임
  python3 patterns.py workers  "규정 세 편의 핵심을 각각 한 줄로 정리해 줘"    # 오케스트레이터-워커 (병렬)
  python3 patterns.py loop     "신입에게 보낼 휴가 안내문을 써 줘"             # 평가-개선 루프
  python3 patterns.py all      "..."                                        # 전부 실행해 비교
  python3 patterns.py router --batch questions.json                         # 라우터 분류 정확도 (정답 라벨 파일)

옵션:
  --model gemma3:4b     사용할 모델
  --rounds 3            loop 패턴의 최대 반복 횟수
  --fallback            router: 담당이 "찾지 못했습니다"라고 하면 전체 문맥으로 한 번 더 (폴백)
  --stop-on-repeat      loop: 평가자의 지적이 직전과 사실상 같으면 중단 (같은 지적 반복 감지)
  --max-workers N       workers: 동시에 돌릴 워커 수 (1이면 순차 — 병렬 효과 대조용)
  --budget-tokens N     보고된 누적 토큰이 N 이상이면 다음 호출 중단 (0이면 끔, 진행 중 호출은 초과 가능)
  --quiet               중간 단계 로그 숨김

전제: Ollama 실행 중, `ollama pull gemma3:4b`, `pip install openai`
"""

import argparse
import concurrent.futures as futures
import difflib
import json
import sys
import time
import threading
from pathlib import Path

DOCS = Path(__file__).parent / "docs"
client = None  # 입력 검증과 회귀 검사는 SDK·서버 없이 가능하게 한다.

STATS = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "usage_missing": 0}
STATS_LOCK = threading.Lock()
BUDGET = {"tokens": 0}  # 0 = 상한 없음


class BudgetExceeded(RuntimeError):
    pass


def warn(msg: str) -> None:
    print(f"  ⚠ {msg}", file=sys.stderr)


# ---------------------------------------------------------------- 공통: 모델 한 번 호출
def ask(system: str, user: str, model: str, label: str = "", quiet: bool = False,
        schema: dict | None = None) -> str:
    """LLM 한 번 호출. 모든 패턴이 이 함수만 쓴다 — 패턴의 차이는 '언제 몇 번 부르는가'뿐이다."""
    global client
    # 검사와 집계를 각각 잠근다. API 대기 중에는 잠그지 않아 병렬 실행을 유지한다.
    # 토큰은 응답 뒤에만 알 수 있으므로 진행 중 호출의 초과 사용은 막지 못한다.
    with STATS_LOCK:
        used = STATS["prompt_tokens"] + STATS["completion_tokens"]
        if BUDGET["tokens"] and STATS["usage_missing"]:
            raise BudgetExceeded("사용량 미수집으로 예산을 판단할 수 없어 다음 호출 중단")
        if BUDGET["tokens"] and used >= BUDGET["tokens"]:
            raise BudgetExceeded(f"누적 토큰 {used} ≥ 중단 기준 {BUDGET['tokens']}")
        if client is None:
            from openai import OpenAI
            client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    kwargs = {}
    if schema:
        kwargs["response_format"] = {"type": "json_schema",
                                     "json_schema": {"name": "out", "schema": schema}}
    t0 = time.monotonic()
    resp = client.chat.completions.create(
        model=model, temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        **kwargs,
    )
    took = time.monotonic() - t0
    usage = resp.usage
    usage_known = usage is not None and all(
        type(getattr(usage, field, None)) is int and getattr(usage, field) >= 0
        for field in ("prompt_tokens", "completion_tokens")
    )
    with STATS_LOCK:
        STATS["calls"] += 1
        if usage_known:
            STATS["prompt_tokens"] += usage.prompt_tokens
            STATS["completion_tokens"] += usage.completion_tokens
        else:
            STATS["usage_missing"] += 1
    if not usage_known:
        warn("사용량 미수집: 누적 토큰은 수집된 호출만의 합계")
        if BUDGET["tokens"]:
            raise BudgetExceeded("사용량 미수집으로 예산을 판단할 수 없어 중단")
    text = (resp.choices[0].message.content or "").strip()
    if label and not quiet:
        used = f"{resp.usage.prompt_tokens}→{resp.usage.completion_tokens}" if usage_known else "미수집"
        print(f"  [{label}] {took:.1f}초 · 토큰 {used} · {text[:70]}{'…' if len(text) > 70 else ''}")
    return text


def load_docs() -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(DOCS.glob("*.md"))}


ANSWER_RULE = ("주어진 <규정>만 근거로 한국어로 간결하게 답한다. "
               "규정에 없으면 '규정에서 찾지 못했습니다'라고 답한다.")


# ---------------------------------------------------------------- ① 단일 호출 (비교 기준선)
def run_single(q: str, model: str, quiet: bool) -> str:
    """모든 문서를 한 프롬프트에 넣고 한 번 부른다. 가장 단순하고, 자주 이걸로 충분하다."""
    docs = load_docs()
    ctx = "\n\n".join(f"[{k}]\n{v}" for k, v in docs.items())
    return ask(ANSWER_RULE, f"<규정>\n{ctx}\n</규정>\n\n질문: {q}", model, "단일", quiet)


# ---------------------------------------------------------------- ② 파이프라인 (순서 고정)
def run_pipeline(q: str, model: str, quiet: bool) -> str:
    """내 코드가 순서를 정한다: 분류 → 답변 → 다듬기. 각 단계가 모델 호출 한 번."""
    docs = load_docs()
    # 1단계 — 어느 규정을 볼지 고르기
    topic = ask("질문이 어느 규정에 속하는지 다음 중 하나로만 답한다: 휴가-규정, 장비-규정, 회의실-예약",
                q, model, "1.분류", quiet)
    key = next((k for k in docs if k in topic), None)
    if key is None:  # 분류가 목록 밖의 답을 냈다 — 조용히 첫 문서로 가지 않고 알린 뒤 전체 문맥으로
        warn(f"분류 결과 '{topic}'가 목록에 없음 → 전체 문맥으로 답변")
        return run_single(q, model, quiet)
    # 2단계 — 그 규정만 넣고 답변
    draft = ask(ANSWER_RULE, f"<규정>\n{docs[key]}\n</규정>\n\n질문: {q}", model, "2.답변", quiet)
    # 3단계 — 사용자에게 보낼 형태로 다듬기
    final = ask("초안을 사내 안내 말투로 한 문단으로 다듬는다. 내용을 추가하지 않는다.",
                f"질문: {q}\n초안: {draft}", model, "3.다듬기", quiet)
    return final


# ---------------------------------------------------------------- ③ 라우터 (분류 후 위임)
SPECIALISTS = {
    "휴가-규정": "너는 휴가 담당자다. 연차·이월·경조 휴가만 다룬다. " + ANSWER_RULE,
    "장비-규정": "너는 자산 담당자다. 노트북 지급·반납·분실만 다룬다. " + ANSWER_RULE,
    "회의실-예약": "너는 총무 담당자다. 회의실 예약·취소만 다룬다. " + ANSWER_RULE,
}


ROUTE_SCHEMA = {"type": "object",
                "properties": {"topic": {"type": "string", "enum": list(SPECIALISTS)},
                               "reason": {"type": "string"}},
                "required": ["topic", "reason"]}
NOT_FOUND = "찾지 못했습니다"


def classify(q: str, model: str, quiet: bool) -> str | None:
    """라우터의 분류 한 번. 파싱 실패는 None으로 돌려 호출자가 알고 처리하게 한다."""
    raw = ask("질문을 담당 분야로 분류한다.", q, model, "라우터", quiet, schema=ROUTE_SCHEMA)
    try:
        result = json.loads(raw)
        topic = result.get("topic") if isinstance(result, dict) else None
        if not isinstance(topic, str) or topic not in SPECIALISTS or not isinstance(result.get("reason"), str):
            raise ValueError("topic·reason 형식 불일치")
        return topic
    except (json.JSONDecodeError, ValueError):
        warn(f"분류 결과를 읽지 못함: {raw[:60]!r}")
        return None


def run_router(q: str, model: str, quiet: bool, fallback: bool = False) -> str:
    """라우터가 분야를 정하고, 그 분야 전담 agent에게만 넘긴다. 전담은 자기 문서만 본다.

    --fallback: 담당이 "찾지 못했습니다"라고 하면 전체 문맥(단일 호출)으로 한 번 더 — 오분류를 되돌릴 길.
    """
    docs = load_docs()
    topic = classify(q, model, quiet)
    if topic is None:
        return run_single(q, model, quiet)
    if not quiet:
        print(f"  → '{topic}' 담당에게 위임")
    answer = ask(SPECIALISTS[topic], f"<규정>\n{docs[topic]}\n</규정>\n\n질문: {q}",
                 model, f"담당:{topic}", quiet)
    if fallback and NOT_FOUND in answer:
        if not quiet:
            print("  → 담당이 찾지 못함 → 폴백: 전체 문맥으로 한 번 더")
        return run_single(q, model, quiet)
    return answer


def load_questions(path: str) -> list[dict]:
    """전체 파일을 먼저 검증해 잘못된 뒷부분 때문에 일부만 실행하지 않는다."""
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise ValueError("질문 목록은 비어 있지 않은 JSON 배열이어야 합니다")
    for i, item in enumerate(items, 1):
        if (not isinstance(item, dict) or not isinstance(item.get("q"), str)
                or not item["q"].strip() or not isinstance(item.get("topic"), str)
                or item["topic"] not in SPECIALISTS):
            raise ValueError(f"질문 {i}: 비어 있지 않은 q와 허용된 topic이 필요합니다")
    return items


def run_router_batch(items: list[dict], model: str, quiet: bool) -> None:
    """검증된 질문 목록으로 분류 정확도를 잰다 (담당 호출 없음)."""
    hits = 0
    for it in items:
        got = classify(it["q"], model, True)
        ok = got == it["topic"]
        hits += ok
        print(f"  [{'O' if ok else 'X'}] {it['q']}  → {got}  (정답 {it['topic']})")
    print(f"\n라우터 정확도: {hits}/{len(items)} = {hits / len(items):.2f}")


# ---------------------------------------------------------------- ④ 오케스트레이터-워커 (병렬 subagent)
def run_workers(q: str, model: str, quiet: bool, max_workers: int = 0) -> str:
    """문서마다 워커를 하나씩 붙여 병렬 처리하고, 오케스트레이터가 결과만 모아 합친다.

    핵심은 '각 워커가 자기 문서만 본다'는 점 — 컨텍스트가 격리된다.
    --max-workers 1 로 돌리면 순차 실행이 되어, 병렬이 실제로 시간을 줄였는지 대조할 수 있다.
    """
    docs = load_docs()
    t0 = time.monotonic()

    def worker(item):
        name, body = item
        return name, ask(f"너는 '{name}' 담당 워커다. 주어진 규정만 보고 요청에 답한다. 다른 분야는 모른다.",
                         f"<규정>\n{body}\n</규정>\n\n요청: {q}", model, f"워커:{name}", quiet)

    with futures.ThreadPoolExecutor(max_workers=max_workers or len(docs)) as ex:
        results = list(ex.map(worker, docs.items()))
    if not quiet:
        print(f"  → 워커 {len(docs)}개 완료 (동시 {max_workers or len(docs)}) · 벽시계 {time.monotonic() - t0:.1f}초")
    merged = "\n".join(f"- {n}: {r}" for n, r in results)
    if not quiet:
        print("  → 오케스트레이터가 결과 취합")
    return ask("워커들의 결과를 중복 없이 한국어로 정리한다. 없는 내용을 만들지 않는다.",
               f"요청: {q}\n\n워커 결과:\n{merged}", model, "취합", quiet)


# ---------------------------------------------------------------- ⑤ 평가-개선 루프
CHECK_SCHEMA = {"type": "object",
                "properties": {"pass": {"type": "boolean"}, "problem": {"type": "string"}},
                "required": ["pass", "problem"]}


def run_loop(q: str, model: str, quiet: bool, rounds: int = 3, stop_on_repeat: bool = False) -> str:
    """작성자가 쓰고 평가자가 검사한다. 통과하거나 상한에 닿을 때까지 반복.

    --stop-on-repeat: 평가자의 지적이 직전 지적과 사실상 같으면(유사도 0.8 이상) 더 돌지 않는다.
    """
    docs = load_docs()
    ctx = "\n\n".join(f"[{k}]\n{v}" for k, v in docs.items())
    draft = ask(ANSWER_RULE, f"<규정>\n{ctx}\n</규정>\n\n요청: {q}", model, "작성 1회", quiet)
    last_problem = ""
    for i in range(1, rounds + 1):
        raw = ask("초안이 규정에 없는 내용을 말하거나 요청을 벗어났는지 검사한다. "
                  "문제가 없으면 pass=true, 있으면 pass=false와 problem을 한 문장으로.",
                  f"<규정>\n{ctx}\n</규정>\n\n요청: {q}\n초안: {draft}",
                  model, f"평가 {i}회", quiet, schema=CHECK_SCHEMA)
        try:
            verdict = json.loads(raw)
            if (not isinstance(verdict, dict) or type(verdict.get("pass")) is not bool
                    or not isinstance(verdict.get("problem"), str)
                    or (not verdict["pass"] and not verdict["problem"].strip())):
                raise ValueError("pass·problem 형식 불일치")
        except (json.JSONDecodeError, ValueError):  # 평가를 읽지 못했으면 '통과'로 치지 않는다 — 알리고 현재 초안으로 멈춘다
            warn(f"평가 결과를 읽지 못함 → 루프 중단, 현재 초안 반환: {raw[:60]!r}")
            return draft
        if verdict.get("pass"):
            if not quiet:
                print(f"  → {i}회차에서 통과")
            return draft
        problem = verdict.get("problem", "")
        if not quiet:
            print(f"  → 지적: {problem[:60]}")
        if stop_on_repeat and last_problem and difflib.SequenceMatcher(None, last_problem, problem).ratio() >= 0.8:
            if not quiet:
                print(f"  → 직전과 같은 지적 (유사도 {difflib.SequenceMatcher(None, last_problem, problem).ratio():.2f}) → 중단, 현재 초안 반환")
            return draft
        last_problem = problem
        draft = ask(ANSWER_RULE + " 지적된 문제를 고쳐 다시 쓴다.",
                    f"<규정>\n{ctx}\n</규정>\n\n요청: {q}\n이전 초안: {draft}\n"
                    f"지적: {problem}", model, f"재작성 {i}회", quiet)
    if not quiet:
        print(f"  → 상한({rounds}회) 도달, 마지막 초안 반환")
    return draft


PATTERNS = {"single": run_single, "pipeline": run_pipeline, "router": run_router,
            "workers": run_workers, "loop": run_loop}


def positive_int(value: str) -> int:
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError("1 이상의 정수여야 합니다")
    return n


def nonnegative_int(value: str) -> int:
    n = int(value)
    if n < 0:
        raise argparse.ArgumentTypeError("0 이상의 정수여야 합니다")
    return n


def reset_stats() -> None:
    # 이전 패턴의 워커가 모두 종료된 뒤 다음 비교를 시작한다.
    with STATS_LOCK:
        STATS.update(calls=0, prompt_tokens=0, completion_tokens=0, usage_missing=0)


def print_stats(name: str, took: float) -> None:
    with STATS_LOCK:
        stats = dict(STATS)
    missing = f" · 사용량 미수집 {stats['usage_missing']}회(토큰 합계 불완전)" if stats['usage_missing'] else ""
    print(f"[{name}] 완료 호출 {stats['calls']}회 · 입력 {stats['prompt_tokens']} + 출력 "
          f"{stats['completion_tokens']} 토큰 · {took:.1f}초{missing}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", choices=list(PATTERNS) + ["all"])
    ap.add_argument("question", nargs="?")
    ap.add_argument("--model", default="gemma3:4b")
    ap.add_argument("--rounds", type=positive_int, default=3)
    ap.add_argument("--fallback", action="store_true")
    ap.add_argument("--stop-on-repeat", action="store_true")
    ap.add_argument("--max-workers", type=nonnegative_int, default=0)
    ap.add_argument("--budget-tokens", type=nonnegative_int, default=0)
    ap.add_argument("--batch", help="router 전용: 정답 분야가 적힌 질문 목록(JSON)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    BUDGET["tokens"] = args.budget_tokens

    if args.batch:
        if args.pattern != "router" or args.question is not None:
            ap.error("--batch는 질문 위치 인자 없이 router에서만 사용합니다")
        try:
            items = load_questions(args.batch)
        except (OSError, ValueError) as e:
            ap.error(str(e))
        reset_stats()
        t0 = time.monotonic()
        status = 0
        try:
            run_router_batch(items, args.model, args.quiet)
        except BudgetExceeded as e:
            warn(f"배치 중단: {e} (전체 정확도 미산출)")
            status = 1
        print_stats("router-batch", time.monotonic() - t0)
        return status
    if not args.question or not args.question.strip():
        ap.error("질문을 입력하세요 (또는 router --batch questions.json)")

    names = list(PATTERNS) if args.pattern == "all" else [args.pattern]
    status = 0
    for name in names:
        reset_stats()
        print(f"\n===== {name} =====")
        t0 = time.monotonic()
        try:
            if name == "loop":
                out = run_loop(args.question, args.model, args.quiet, args.rounds, args.stop_on_repeat)
            elif name == "router":
                out = run_router(args.question, args.model, args.quiet, args.fallback)
            elif name == "workers":
                out = run_workers(args.question, args.model, args.quiet, args.max_workers)
            else:
                out = PATTERNS[name](args.question, args.model, args.quiet)
        except BudgetExceeded as e:
            out = f"(중단) {e}"
            status = 1
        took = time.monotonic() - t0
        print(f"\n답변: {out}")
        print_stats(name, took)
    return status


if __name__ == "__main__":
    sys.exit(main())
