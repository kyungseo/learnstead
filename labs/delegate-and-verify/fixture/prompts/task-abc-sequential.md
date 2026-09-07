아래 세 과제를 implementer subagent 세 개에게 **하나씩 순서대로** 맡기고, 앞의 것이 끝난 뒤 다음을 시작하세요. 당신은 파일을 직접 고치지 마세요. 셋이 모두 끝나면 `PYTHONPATH=src python3 -m unittest -q`를 한 번 실행하고, 바뀐 파일 목록과 테스트 결과를 보고하세요.

과제 A: `src/ledger/parse.py`에 `parse_memo(text: str) -> str`를 추가(앞뒤 공백 제거, 연속 공백 하나로). `parse_rows`가 memo에 이 함수를 쓰게 하고 `tests/test_parse_memo.py`에 unittest 3개 추가.
과제 B: `src/ledger/store.py`에 `read_records(path) -> list[Record]`를 추가(JSON Lines를 Record 목록으로, `day`는 ISO 문자열에서 date로). `tests/test_store.py`에 왕복 테스트 1개 추가.
과제 C: `src/ledger/cli.py`에 `--json` 플래그 추가(`{"month": "YYYY-MM", "totals": {...}, "grand_total": N}` 한 줄 JSON). `tests/test_cli.py`에 검증 unittest 1개 추가.
각 subagent는 자기 과제의 파일과 테스트 파일만 수정합니다.
