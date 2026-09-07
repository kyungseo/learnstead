# ledger — 가계부 집계 CLI (실습용 fixture)

CSV 거래 내역을 읽어 월별·분류별 합계를 표로 출력하는 작은 프로그램입니다.
실습 `delegate-and-verify`의 고정 입력이며, 일부 함수에 **의도된 결함이** 있습니다.
결함 목록은 `../expected/golden.json`에 있고, 실습 04 전에는 열지 않습니다.

## 규격

- 입력 CSV 열: `date,category,amount,memo` (헤더 포함). `date`는 `YYYY-MM-DD`.
- `amount`는 정수 원 단위. 지출은 음수, 환불·수입은 양수.
- 월별 합계는 해당 월 1일부터 말일까지 포함한다.
- 보고서의 분류는 합계 절댓값이 큰 순서로 정렬한다.
- 저장소(`store.py`)는 파일에 JSON Lines로 append만 한다.

## 실행

```bash
PYTHONPATH=src python3 -m ledger.cli data/sample.csv --month 2026-08
PYTHONPATH=src python3 -m unittest -q
```
