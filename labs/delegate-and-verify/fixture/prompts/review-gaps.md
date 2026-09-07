`README.md`의 규격을 기준으로 `src/ledger/` 전체를 철저히 검토해 **개선이 필요한 모든 지점(gap)** 을 찾으세요. 결함, 누락된 검증, 엣지 케이스, 명명, 문서화, 테스트 부족을 빠짐없이 나열합니다.

출력은 아래 JSON 하나만, 설명 없이:

{"findings": [{"file": "src/ledger/xxx.py", "function": "name", "reason": "한 문장"}]}
