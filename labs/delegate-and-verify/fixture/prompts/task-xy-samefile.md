아래 두 과제를 implementer subagent 두 개에게 **동시에** 하나씩 맡기세요. 당신은 파일을 직접 고치지 마세요. 둘이 모두 끝나면 `PYTHONPATH=src python3 -m unittest -q`를 실행하고, `src/ledger/report.py`의 최종 상태에 두 기능이 모두 들어 있는지와 테스트 결과를 보고하세요.

과제 X: `src/ledger/report.py`의 `render`에 `title: str | None = None` 인자를 추가. 주어지면 첫 줄 위에 제목 줄을 넣는다. 기존 호출은 그대로 동작.
과제 Y: `src/ledger/report.py`의 `render`에 `top: int | None = None` 인자를 추가. 주어지면 상위 `top`개 분류만 표에 넣고 나머지는 `기타` 한 줄로 합친다. 기존 호출은 그대로 동작.
