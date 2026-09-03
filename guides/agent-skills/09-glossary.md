# 09. 용어집

> 이전 ← [`08-sharing-and-boundaries.md`](08-sharing-and-boundaries.md) · 처음 → [`README.md`](README.md)

가나다·알파벳 순이 아니라 **가이드에서 등장한 순서로** 배열했다. 처음 나온 장을 함께 적는다.

| 용어 | 뜻 | 장 |
| --- | --- | --- |
| **런타임(runtime)** | 모델을 반복 호출하고, 권한 규칙을 적용해 도구 실행과 결과 전달을 이어 주는 실행기 | 00 |
| **하네스(harness)** | 정책·작업 순서·검증·기록을 묶어 런타임이 따를 운영 방식을 정하는 장치. 제품에 따라 런타임 자체를 가리키기도 함 | 00 |
| **Agent loop(에이전트 루프)** | 모델의 판단 → 도구 호출 제안 → 런타임 실행 → 결과 전달을 목표 달성까지 반복하는 흐름 | 00 |
| **framework/SDK** | 내 프로그램에 Agent loop와 도구 연결을 구현하도록 돕는 코드 라이브러리 | 00 |
| **skill** | 폴더 하나에 담긴, 필요할 때 로드되는 절차 지시문. `SKILL.md`가 필수 | 01 |
| **진입 지시문** | 세션마다 항상 로드되는 프로젝트 문서. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | 01 |
| **progressive disclosure (점진적 공개)** | 이름·설명 → 본문 → 부속 파일 순으로 필요한 만큼만 컨텍스트에 넣는 설계 원칙 | 01 |
| **Agent Skills 규격** | agentskills.io가 정한 `SKILL.md` 구조. 필수 필드 2개와 선택 필드를 여러 도구가 공통으로 읽음 | 02 |
| **frontmatter** | `SKILL.md` 첫머리의 YAML 블록. `name`·`description` 필수 | 02 |
| **description** | skill이 무엇을·언제 하는지 적은 한 줄. 항상 컨텍스트에 있는 유일한 부분이며 자동 호출의 근거 | 02 |
| **확장 필드** | 규격 밖에서 도구가 더 읽는 frontmatter 키. Claude Code의 `context: fork` 등 | 02 |
| **slash command** | 사람이 `/name`으로 부르는 프롬프트 템플릿. Claude Code·Cursor에서 skill로 통합됨 | 03 |
| **rule (경로 조건)** | 파일 경로 glob에 따라 켜지는 지시문. Cursor `.mdc`, Claude Code skill `paths` | 03 |
| **hook** | 이벤트(tool 실행 전후 등)에 묶여 모델 판단 없이 실행되는 명령 | 03 |
| **subagent** | 별도 컨텍스트와 tool 집합으로 작업을 위임받는 에이전트. skill의 `context: fork`가 이를 사용 | 03 |
| **MCP** | Model Context Protocol. 외부 프로세스가 모델에게 tool(능력)을 제공하는 규약 | 03 |
| **plugin** | skill·command·agent·hook·MCP 설정을 manifest와 함께 묶은 배포 단위. skill 이름에 `plugin:` 접두 | 03 |
| **명시 호출 / 자동 호출** | 사람이 이름으로 부름(`/name`, `$name`) / 모델이 description을 보고 선택 | 04 |
| **`.agents/skills`** | Codex·Gemini CLI·Cursor가 공유하는 프로젝트 skill 경로. Claude Code에서는 `.claude/skills` symlink로 연결 가능 | 04 |
| **우선순위 (precedence)** | 같은 이름이 여러 경로에 있을 때 채택 규칙. Claude Code 개인 > 프로젝트, Codex 저장소 우선(관측) | 04 |
| **`skillOverrides`** | Claude Code 설정으로 skill 파일을 고치지 않고 표시 상태를 바꾸는 키(`on`/`name-only`/`user-invocable-only`/`off`) | 05 |
| **`disable-model-invocation`** | 모델의 자동 호출을 막고 사람 호출만 허용하는 frontmatter 키 (Claude Code·Cursor) | 03 |
| **`allowed-tools`** | skill 호출 턴 동안 특정 tool을 사전 승인하는 키. 규격상 실험적, 도구별 동작 다름 | 02 |
| **동적 컨텍스트** | Claude Code에서 본문의 `` !`명령` ``을 전송 전에 실행해 출력으로 치환하는 기능 | 05 |
| **compaction (압축)** | 대화가 길어질 때 도구가 요약으로 컨텍스트를 줄이는 동작. 호출된 skill은 상한 안에서 다시 붙음 | 05 |
| **canonical + adapter** | 절차 본체 한 파일(canonical)과 도구별 얇은 진입 파일(adapter)로 나누는 배치 | 06 |
| **발견 실패 / 로드 실패 / 준수 실패** | skill 오동작의 세 층. 목록·선택 → 본문 삽입 → 출력 준수 | 07 |
| **신뢰 경계** | 저장소에 들어온 skill이 내 장비에서 명령을 실행하거나 권한을 얻는 지점 | 07 |
| **managed / marketplace** | 조직 단위 배포 경로. Claude Code managed settings, plugin marketplace | 08 |
| **`metadata.version`** | skill 버전을 적는 관례 자리. 규격에 버전 필드는 없음 | 08 |
