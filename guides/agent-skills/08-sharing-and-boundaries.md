# 08. 배포·공유·버전·공개 경계

> 이전 ← [`07-what-goes-wrong.md`](07-what-goes-wrong.md) · 다음 → [`09-glossary.md`](09-glossary.md)

## 이 장에서 답하는 질문

- 혼자 쓰던 skill을 팀·조직·공개로 넓힐 때 무엇이 달라지는가
- 버전은 어디에 적고 어떻게 올리는가
- 공개 저장소에 올리기 전에 무엇을 지워야 하는가

## 1. 범위 네 단계

| 범위 | 두는 곳 | 특징 |
| --- | --- | --- |
| 개인 | `~/.claude/skills`, `$HOME/.agents/skills` | 모든 프로젝트에서 보임. Claude Code 2.1.251의 1회 충돌 실험에서는 프로젝트 사본보다 **우선해** 팀 skill과 이름이 겹치면 팀 것이 가려졌다 |
| 프로젝트 | `.claude/skills`, `.agents/skills` (git에 커밋) | 저장소를 여는 모두에게 같은 절차. 협업자의 도구가 다르면 [`06`](06-canonical-and-adapters.md) 배치 |
| 팀·조직 | plugin(marketplace), Claude Code managed settings, Gemini extension, `gemini skills install <url>` | 설치·갱신을 도구가 관리. 이름 공간(`plugin:skill`)으로 충돌 방지 |
| 공개 | 공개 git 저장소, skill 모음 저장소 | 아래 3절의 경계 검사 필수 |

개인 폴더에 둔 skill은 **자기 장비에만** 있습니다. Cursor 문서는 사용자 레벨 skill이 클라우드 에이전트·원격 SSH·관리형 워커에 복사되지 않는다고 명시합니다 [문서 확인]. 팀과 나눌 skill은 프로젝트에 둡니다.

## 2. plugin으로 묶기

skill이 셋 이상이고 command·hook·MCP 설정이 함께 가야 한다면 plugin으로 묶을 수 있습니다. Claude Code 기준 최소 구조는 다음과 같습니다 [문서 확인].

```text
my-plugin/
├── .claude-plugin/plugin.json      # name, version, description
├── skills/<name>/SKILL.md
├── commands/                       # 선택
├── agents/                         # 선택
└── hooks/hooks.json                # 선택
```

- 개발 중에는 `claude --plugin-dir ./my-plugin`으로 설치 없이 로드하고, `/reload-plugins`로 다시 읽습니다.
- `claude plugin validate ./my-plugin`으로 manifest와 skill frontmatter를 검사합니다.
- Codex도 `codex plugin` 명령과 plugin skill을 제공합니다. 실습의 목록 출력에서 `browser:control-in-app-browser`처럼 plugin 이름이 앞에 붙은 skill들을 관측했습니다 [실행 검증].

## 3. 버전

규격에는 버전 필드가 없습니다. 주로 다음 두 곳에 버전을 기록합니다.

- `metadata.version: "1.1"` — skill 자체의 버전. 실습에서 규칙을 좁힌 v1.1이 이 자리에 해당합니다.
- plugin의 `plugin.json` `version` — 배포 단위의 버전.

버전을 올릴 때는 다음 작업을 함께 진행합니다.

1. **재검증** — 같은 프롬프트 묶음을 새 세션에서 돌려 결과를 비교합니다. Claude Code의 `skill-creator` plugin은 with/without, 버전 A/B, description 적중률까지 자동화합니다 [문서 확인].
2. **CHANGELOG** — 무엇이 왜 바뀌었는지 기록합니다. 실습 v1.0 → v1.1의 변경 이유는 "Codex가 일정 확정을 액션으로 뽑았다"입니다. 이유가 남아야 다음 사람이 규칙을 잘못 되돌리는 일을 막을 수 있습니다.
3. Claude Code는 skill 파일 변경을 **세션 중에도** 감지합니다 [문서 확인]. 편집 후 재시작이 필요 없지만, 이미 대화에 삽입된 본문은 바뀌지 않으므로 다시 호출해야 합니다.

## 4. 공개 전 경계 검사

공개 저장소에 올리기 전에 skill 폴더에서 다음 항목을 찾아 제거하거나 안전한 값으로 바꿉니다.

| 항목 | 이유 | 찾는 법 |
| --- | --- | --- |
| 홈 디렉터리 절대 경로 (macOS·Linux의 사용자 폴더 전체 경로) | 남의 장비에서 깨지고 사용자명이 새어 나감 | `grep -rn "$HOME" <dir>` 로 자기 홈 경로를 찾는다 |
| 내부 식별자 (작업 ID, 티켓 번호, 사내 저장소 이름) | 맥락 없이 노출되면 무의미하거나 정보 유출 | 프로젝트 관례에 맞는 패턴 grep |
| Secret·토큰·URL 파라미터 | 외부에 공개되면 계정과 시스템이 노출될 수 있음 | secret scanner |
| 광범위한 `allowed-tools` (`Bash(*)`) | 받는 쪽이 검토 없이 실행하면 위험 | frontmatter 검토. 필요한 명령 prefix만 |
| 동적 명령 `` !`…` `` | 받는 쪽 장비에서 실행됨 | 정말 필요한지, 실패 시 `\|\| true`인지 |
| 특정 도구 이름·경로 의존 | 다른 도구·환경에서 조용히 다르게 동작 | [`06`](06-canonical-and-adapters.md) 2절 표 |
| `license` 누락 | 재사용 조건 불명 | frontmatter에 명시 |

이 검사는 skill의 **본문뿐 아니라 `scripts/`·`references/`에도** 적용합니다. 특히 스크립트 안의 하드코딩된 경로를 놓치기 쉽습니다.

## 5. 남의 skill을 받을 때

다른 사람이 만든 skill을 받을 때는 같은 표를 반대로 살펴봅니다. 저장소를 clone해서 열기 전에 다음 내용을 확인하세요.

1. `.claude/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`의 `allowed-tools`와 `` !`…` ``을 확인한다.
2. `scripts/`에 무엇이 있는지 본다. skill 본문이 "이 스크립트를 실행하라"고 하면 모델이 실행을 요청하고 런타임이 권한 규칙에 따라 실행한다.
3. 믿기 전까지는 `skillOverrides: off`(Claude Code)로 끄거나, `disable-model-invocation`을 붙여 사람 호출만 허용한다.

공개 저장소의 첫 공개나 새 버전 발행은 파일 검사만으로 끝나지 않습니다. 저장소 공개 범위, 릴리스 자산, GitHub 설정, 발행 뒤
노출까지 함께 확인하려면 공개 절차를 점검하는 체크리스트나 `github-release-guide` 같은 skill을 함께 사용할 수 있습니다.

## 이 장을 끝내면

- 개인·프로젝트·조직·공개 네 범위의 저장 위치와 우선순위 함정을 알 수 있습니다.
- 버전을 `metadata.version`과 plugin 버전 중 어디에 적을지, 올릴 때 무엇을 재검증할지 판단할 수 있습니다.
- 공개 전 검사 항목 7개를 grep으로 확인할 수 있습니다.
