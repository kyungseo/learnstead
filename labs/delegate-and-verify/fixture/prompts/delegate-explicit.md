implementer subagent 하나에게 정확히 다음 프롬프트를 주어 위임하세요. 당신이 직접 고치지는 마세요. subagent가 돌아오면 무엇을 고쳤는지 파일·함수 이름으로 보고하세요.

"`src/ledger/summarize.py`의 `in_month`가 `start <= rec.day < end`로 비교해 월 마지막 날 거래를 빠뜨린다. `README.md` 규격은 말일 포함이다. `<=`로 고치고 `tests/test_summarize.py`에 월말 포함·인접 월 제외 unittest를 추가한 뒤 `PYTHONPATH=src python3 -m unittest -q`로 통과를 확인해. 다른 파일은 건드리지 마."
