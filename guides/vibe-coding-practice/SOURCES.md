# 출처

**AI와 함께 만들기 — 바이브 코딩에서 Agentic Engineering으로** 가이드의 근거 자료를 연결합니다.

- 마지막 확인일: 2026-09-01 (초판 조사 2026-08-24)
- 이 가이드는 **작업 방식을** 다루므로 대부분이 `해석`(저자의 정리)입니다. 명령·도구 동작·웹앱 구조만 아래에 근거를 둡니다.
- AI 코딩·개발·배포 도구의 화면과 기능은 빠르게 바뀝니다. 00장은 2026-09-01 기준의 역할만 소개하며 단계별 사용법이나 제품
  순위를 다루지 않습니다.

## 도구·명령

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| Git 명령 | `add`·`commit`·`restore`·`revert`·`status`·`diff`·`log`의 동작 | [Git Reference](https://git-scm.com/docs) | 문서 확인 |
| `.gitignore` | 패턴 규칙 | [gitignore](https://git-scm.com/docs/gitignore) | 문서 확인 |
| GitHub 공개 범위 | Private/Public 선택과 변경 | [GitHub Docs — Repositories](https://docs.github.com/repositories) | 문서 확인 |
| GitHub Secret scanning | 알려진 Secret 형식 탐지 범위와 한계 | [GitHub Docs — About secret scanning](https://docs.github.com/code-security/secret-scanning/introduction/about-secret-scanning) | 문서 확인 |
| 컨텍스트 창의 크기 | 모델이 선언한 창과 runtime이 적용한 창이 다를 수 있음 | [Local LLM을 내 프로그램에 연결하기 04 §2](../local-llm-app-integration/04-parameters-and-context.md) (자체 가이드, 실행 검증 포함) | 문서 확인 |
| 창이 찼을 때의 동작 — 자동 요약(compaction) | 여러 AI 코딩 도구가 창이 차기 전 앞부분을 요약해 압축함 | [Claude Code — context window](https://code.claude.com/docs/en/context-window) · [Cursor — summarization](https://docs.cursor.com/en/agent/chat/summarization) | 자료 확인 |
| 창이 찼을 때의 동작 — 오류 | 모델을 직접 호출하면 입력이 너무 길다는 오류가 남 | 공개 이슈 사례 ([claude-code#57296](https://github.com/anthropics/claude-code/issues/57296)) | 자료 확인 |
| 규칙 파일 자동 읽기 | 프로젝트 폴더의 규칙 파일을 대화 시작 시 자동으로 읽는 기능 | [Claude Code — memory](https://code.claude.com/docs/en/memory) · [Cursor — rules](https://docs.cursor.com/en/context/rules) | 문서 확인 |

## 웹앱 구조와 개발·배포 도구

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| 웹앱의 큰 그림 | Frontend의 HTML·CSS·JavaScript, Backend 언어, database, web server가 함께 앱을 구성하며 실제 production stack은 더 복잡할 수 있음 | [MDN — Workflows and processes](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Soft_skills/Workflows_and_processes) | 문서 확인 |
| Client–Server–Database | 브라우저가 HTTP로 server에 요청하고, 동적 사이트는 application과 database에서 데이터를 가져와 응답함 | [MDN — Client-Server overview](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview) | 문서 확인 |
| 검증의 범위 | architecture·요구사항·보안 제어·자동/수동 test와 도구를 함께 검토하는 범위 | [OWASP Developer Guide — Verification](https://devguide.owasp.org/en/06-verification/) | 문서 확인 |
| Replit | Agent와 project editor에서 계획·code·preview·version control을 다루고, 별도 deployment로 공개 URL에 올림 | [Build with Agent](https://docs.replit.com/learn/build-with-agent) · [Project editor](https://docs.replit.com/learn/projects-and-artifacts/project-editor) · [Deployments](https://docs.replit.com/learn/projects-and-artifacts/replit-deployments) | 문서 확인 |
| Lovable | Lovable Cloud 또는 Supabase backend, publish, GitHub sync를 제공함 | [Quick start](https://docs.lovable.dev/introduction/getting-started) · [Supabase](https://docs.lovable.dev/integrations/supabase) · [GitHub](https://docs.lovable.dev/integrations/github) · [Publish](https://docs.lovable.dev/features/publish) | 문서 확인 |
| Bolt | browser 기반 개발 환경과 database·hosting을 제공하고, publish 시 공개 범위와 domain을 설정함 | [Introduction to Bolt](https://support.bolt.new/building/intro-bolt) · [Publish](https://support.bolt.new/cloud/hosting/publish) · [Supabase](https://support.bolt.new/integrations/supabase) | 문서 확인 |
| v0 + Vercel | full-stack Next.js app과 backend endpoint를 만들고 Vercel에 배포할 수 있음 | [v0 — Full-stack apps](https://v0.dev/docs/full-stack-apps) · [v0 — Deployments](https://api2.v0.dev/docs/deployments) | 문서 확인 |
| Supabase·Firebase | database·인증·저장·server 기능을 관리형 service로 제공함 | [Supabase Auth architecture](https://supabase.com/docs/guides/auth/architecture) · [Firebase products](https://firebase.google.com/products-build) · [Firebase App Hosting](https://firebase.google.com/docs/app-hosting) | 문서 확인 |
| Netlify | Git repository나 web 개발 도구에서 만든 앱을 build·deploy·hosting하는 경로를 제공함 | [Netlify Docs — Deploy overview](https://docs.netlify.com/deploy/deploy-overview/) | 문서 확인 |

## 개념·배경

| 범위 | 확인한 내용 | 자료 | 상태 |
| --- | --- | --- | --- |
| 바이브 코딩의 유래 | Andrej Karpathy가 2025-02-02 공개한 원문과 1년 뒤 회고 | [원문](https://x.com/karpathy/status/1886192184808149383) · [1년 뒤 회고](https://x.com/karpathy/status/2019137879310836075) | 문서 확인 |
| Agentic Engineering 제안 | Agent가 구현하고 사람이 조율·감독하며 품질을 타협하지 않는 전문 workflow라는 구분 | [Karpathy의 1년 뒤 회고](https://x.com/karpathy/status/2019137879310836075) · [Sequoia AI Ascent 2026 대담](https://www.youtube.com/watch?v=96jN2OCOfLs) | 문서 확인 |
| 용어의 사전 수록 | 바이브 코딩의 정의·어원·최초 사용 시점 | [Merriam-Webster — vibe coding](https://www.merriam-webster.com/dictionary/vibe%20coding) | 문서 확인 |
| Agentic Engineering의 후속 정리 | 목표 정의·작업 분할·Agent 조율·사람의 검토와 통합이라는 workflow | [IBM — What is agentic engineering?](https://www.ibm.com/think/topics/agentic-engineering) | 자료 확인 |
| 실패 패턴 | 컨텍스트 관리 어려움, 의존성 변화, 디버깅 도구 부재 — 이 가이드의 상황 목록은 검증된 보편 법칙이 아니라 작업 절차를 구성하기 위한 `해석` | (정량적 근거 없음 — 본문에서 `해석`으로 표기) | 해석 |

## 자체 가이드 참조

이 가이드는 다음 가이드의 검증된 내용에 기댑니다.

| 주제 | 문서 |
| --- | --- |
| Git 기초·되돌리기·Secret 사고 | [AI로 코딩하는 사람을 위한 Git](../git-for-vibe-coders/README.md) (실행 검증 포함) |
| 다섯 가지 확인의 실행 | [실습: 다섯 가지 확인](../../labs/five-checks/README.md) (fixture 3판, 실행 검증) |
| 컨텍스트 창의 크기 | [Local LLM을 내 프로그램에 연결하기 04](../local-llm-app-integration/04-parameters-and-context.md) |

## Source ledger를 갱신하는 규칙

1. 명령이나 도구 동작 설명을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 특정 AI 코딩·개발·배포 도구의 기능은 바뀌기 쉬우므로 본문에는 역할만 넣고, 공식 자료와 마지막 확인일을 함께 표기합니다.
3. 작업 방식에 대한 주장은 `해석`으로 표기하고 근거를 본문에 함께 적습니다.
4. 바이브 코딩과 Agentic Engineering은 공식 표준 용어가 아니므로, 업계 전체가 같은 경계로 사용한다고 단정하지 않습니다.
5. 개발·배포 서비스의 역할·가격·제한은 발행 전에 공식 문서를 다시 확인하고, 대표 예시를 인기 순위나 구매 권고로 제시하지 않습니다.
