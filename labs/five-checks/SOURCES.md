# 출처

**다섯 가지 확인 — 코드를 읽지 않고 세 판을 판정하기에서** 근거가 되는 자료를 연결합니다.

- 마지막 확인일: 2026-08-30
- 이 실습은 **작업 방식을** 연습합니다. 실행으로 확인한 것은 [VALIDATION.md](VALIDATION.md)에, 명령과 도구 동작의 근거는 아래에 둡니다.

## 도구·명령

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| Git 명령 | `init`·`add`·`commit`·`status --short`·`diff --stat`·`restore`·`log --oneline`의 동작 | [Git Reference](https://git-scm.com/docs) | 문서 확인 |
| `git restore .`와 새 파일 | `restore`는 추적 중인 파일만 되돌리고, 새로 생긴(추적되지 않은) 파일은 남긴다 | [git-restore](https://git-scm.com/docs/git-restore) | 문서 확인 |
| 브라우저 저장소 | `localStorage`는 같은 출처(origin)의 페이지끼리 공유된다 — v1에서 넣은 항목이 v3에 보이는 이유 | [MDN — Window.localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) | 문서 확인 |
| 고유 ID 생성 | `crypto.randomUUID()` — 항목마다 겹치지 않는 번호를 붙여 삭제가 정확히 그 항목만 지우게 함 | [MDN — Crypto.randomUUID()](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/randomUUID) | 문서 확인 |

## 자체 가이드 참조

| 주제 | 문서 |
| --- | --- |
| 다섯 가지 확인의 정의와 이유 | [가이드 05 코드를 몰라도 하는 확인](../../guides/vibe-coding-practice/05-verify-without-reading.md) |
| 되돌리기와 `reset --hard`의 위험 | [AI로 코딩하는 사람을 위한 Git](../../guides/git-for-vibe-coders/README.md) (실행 검증 포함) |

## Source ledger를 갱신하는 규칙

1. fixture의 동작이나 명령을 바꾸면 같은 commit에서 이 표와 VALIDATION을 갱신합니다.
2. fixture는 특정 AI 도구의 출력이 아니라 저자가 만든 예제입니다 — "AI가 이렇게 만든다"는 주장이 아니라 "이런 결과를 다섯 확인이 잡는다"는 연습입니다.
