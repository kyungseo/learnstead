# 노트 MCP 서버 — 만들고, 꽂고, 깨뜨리기

![두 AI 코딩 도구가 읽기 전용 노트 서버에 연결되고 쓰기와 경로 이탈은 차단되는 손그림](assets/mcp-notes-server-hero.webp)

> Python 80줄짜리 읽기 전용 노트 서버를 만들어 LLM 없이 호출하고, Claude Code와 Codex에 꽂고, **권한 밖 호출·거짓 annotation·주입 지시문·stdout 오염을** 재현한 뒤 skill과 결합합니다. 가이드 [AI Agent에 내 도구를 연결하는 법 — MCP 기초](../../guides/mcp-basics/README.md)의 실습편.

## 학습 달성 목표(Learning Objective)

- SDK 2.x `MCPServer`로 서버를 만들고 SDK `Client`로 `tools/list`·`tools/call` 원문을 봅니다.
- 두 도구에 서버를 등록하고 비-대화형으로 호출해 로그에서 호출·거부 줄을 찾습니다.
- 권한 세 겹(서버 코드·annotation·host 승인) 중 무엇이 실제로 막는지 실험으로 구분합니다.
- skill이 절차·경계를, MCP가 능력을 맡는 조합을 돌려 봅니다.

## 완료 조건

1. 01: `probe.py`로 도구 3개와 `is_error` 두 경우(경로 탈출·없는 도구)를 본다.
2. 02: Claude Code에서 `mcp_servers … connected`와 `mcp__notes__read_note` 호출을 로그로 확인한다.
3. 03: Codex transcript에서 `mcp: notes/read_note started`를 확인한다.
4. 04: 실패 경로 4종의 결과를 표에 적는다.
5. 05: skill 경유 실행에서 표가 나오고 MCP 도구만 쓰였는지 확인한다.

## 지원 환경 · 준비

| 필요 | 확인 |
| --- | --- |
| Python 3.10+ 와 `mcp==2.1.1` | `python3 -c "import mcp"` — 없으면 `pip install "mcp==2.1.1"` (가상환경 권장) |
| Claude Code CLI 로그인 | `claude --version` |
| Codex CLI 로그인 | `codex --version` |
| git | — |

한 도구만 있어도 01·02(또는 03)·04 대부분·05는 진행할 수 있습니다.

```bash
# 워크숍 저장소 만들기 (이 실습 폴더에서). 두 번째 인자는 mcp가 설치된 python의 절대 경로
bash fixture/scripts/setup.sh ~/mcp-workshop /절대/경로/venv/bin/python
cd ~/mcp-workshop
export MCP_NOTES_PYTHON=/절대/경로/venv/bin/python
```

준비가 중간에 실패했다면 오류를 고친 뒤, 방금 만들다 만 `~/mcp-workshop`만 지우고 다시 실행합니다. 기존 작업 폴더를 대상으로 재실행하지 않습니다.

`setup.sh`가 만드는 것:

```text
~/mcp-workshop/
├── notes_server.py           ← 서버 (읽기 3도구, --allow-write 시 write_note)
├── notes/                    ← 노트 4편. 여행-계획.md 끝에 주입 지시문(HTML 주석)
├── .mcp.json.example         ← Claude Code project scope 기준 파일
├── .mcp.json                 ← 기준 파일의 실행용 사본. 환경 변수와 프로젝트 상대 경로 사용
├── .gitignore                ← .mcp.json·logs/ 제외
├── .agents/skills/notes-digest/  + .claude/skills/notes-digest (symlink)   ← 05에서 사용
├── scripts/probe.py · run-claude.sh · run-codex.sh
└── logs/
```

`.mcp.json.example`은 재설정할 수 있는 기준 파일로 git에 넣고, 실제 `.mcp.json`은 프로젝트마다 실행 파일 경로가 달라질 수 있어 제외합니다. `setup.sh`가 안내한 `MCP_NOTES_PYTHON`을 현재 shell에 설정하고, 마지막에 출력되는 Codex 등록 명령은 03에서 사용합니다.

비용: Claude Code 실행 1회는 캐시 포함 입력 4~13만 토큰, Codex는 1~3만 토큰이었습니다. 전 과정은 각 도구에서 10~15회 실행합니다.

## 고정 시나리오

노트 4편(회의·장보기·독서·여행)은 고정입니다. 기본 요청은 "장보기 노트에 뭐가 적혀 있어?"(읽기)와 "장보기 노트 맨 끝에 '- 치즈' 한 줄을 추가해 줘. 반드시 notes MCP 서버의 write_note 도구로 써."(쓰기)입니다. 판정은 로그의 호출·거부 줄과 `notes/장보기.md`의 변경 여부로 합니다. 쓰기 실험 뒤에는 `git checkout -- notes/`로 되돌립니다.

## 단계

| 단계 | 파일 | 관측 |
| --- | --- | --- |
| 01 | [`01-build-and-probe.md`](01-build-and-probe.md) | 서버 코드 읽기, LLM 없이 `tools/list`·`tools/call`, 오류 두 종류 |
| 02 | [`02-connect-claude-code.md`](02-connect-claude-code.md) | `.mcp.json`, `claude mcp list`, `-p` 호출, 지연 로드, 환경 변수 기본값 |
| 03 | [`03-connect-codex.md`](03-connect-codex.md) | `codex mcp add`, transcript의 `mcp:` 줄, 모델 자기 보고와 실제 |
| 04 | [`04-break-it.md`](04-break-it.md) | 권한 밖 쓰기(두 도구) · 거짓 annotation · 주입 지시문 · stdout 오염 |
| 05 | [`05-skill-plus-mcp.md`](05-skill-plus-mcp.md) | `notes-digest` skill로 절차 + MCP 능력 결합 |

## 정상 경로와 실패 경로

정상: 01의 읽기 호출, 02·03의 읽기 요청, 05의 다이제스트. 04의 실패는 의도된 것입니다.

- 04: `--permission-mode default` 거부, Codex `user cancelled`, 거짓 annotation 통과, stdout 오염(살아남지만 규격 위반)

## reset

```bash
git checkout -- notes/                    # 노트 되돌리기
cp .mcp.json.example .mcp.json            # Claude Code 설정 되돌리기
codex mcp remove notes                    # Codex 전역 설정에서 제거 (03에서 등록한 것)
rm -f .claude/settings.local.json
```

Codex 등록은 `~/.codex/config.toml`(전역)에 남습니다. **실습이 끝나면 반드시 제거해야 합니다.** 제거 후에도 파일의 키 순서·숫자 표기가 바뀔 수 있습니다. Claude Code는 project 신뢰·MCP 상태를 `~/.claude.json`의 프로젝트 항목에 남길 수 있습니다.

## 실행 기록

작성 환경(2026-08-30, macOS, Python 3.14, mcp 2.1.1, Claude Code 2.1.251, Codex CLI 0.144.1)의 결과는 각 단계의 "작성 환경의 실제 결과"와 [`VALIDATION.md`](VALIDATION.md)에 있습니다. 2026-09-02에는 설정 생성과 LLM 없는 probe를 다시 검증했습니다. 작성 환경의 Claude Code 사용자 설정은 `permissions.defaultMode: "auto"`였습니다. 04의 권한 결과를 읽을 때 자기 설정과 비교합니다.

## 버전

[`CHANGELOG.md`](CHANGELOG.md) · 출처 [`SOURCES.md`](SOURCES.md)
