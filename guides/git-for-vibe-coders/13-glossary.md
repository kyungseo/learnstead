# 13 — 용어집

전 문서의 **참조 부록입니다.** 순서대로 읽는 문서가 아니라, 모르는 단어가 나왔을 때 여는 문서입니다.

← [12 AI에게 Git 작업을 지시하는 법](12-asking-ai.md) · [README로](README.md)

---

## 1. 기본

| 용어 | 뜻 |
| --- | --- |
| **버전 관리 (VCS)** | 언제·누가·무엇을·왜 바꿨는지 기록하고 되돌릴 수 있게 하는 것 ([01](01-what-is-version-control.md)) |
| **Git** | 내 컴퓨터에서 도는 버전 관리 프로그램. 인터넷 불필요 ([02](02-git-vs-github.md)) |
| **GitHub / GitLab / Bitbucket** | Git 저장소를 올려 두는 인터넷 서비스 ([02](02-git-vs-github.md)) |
| **저장소 (repository, repo)** | Git이 관리하는 프로젝트 하나. 폴더 안 `.git`에 기록이 들어 있음 |
| **터미널 / 셸 (zsh·bash)** | 명령을 글자로 입력하는 창과 그 프로그램. macOS 기본은 zsh ([03](03-setup-mac-windows.md)) |
| **Git Bash** | Windows에서 Git과 함께 설치되는 터미널. 이 가이드의 권장 창 ([03 §3](03-setup-mac-windows.md)) |

## 2. 네 공간과 이동

| 용어 | 뜻 |
| --- | --- |
| **작업 폴더 (working directory)** | 지금 편집 중인 실제 파일들 ([04](04-four-areas.md)) |
| **스테이징 (staging area, index)** | "다음 커밋에 담겠다"고 골라 둔 변경 |
| **로컬 저장소 (local repository)** | 내 컴퓨터에 있는 모든 커밋 기록 |
| **원격 저장소 (remote)** | GitHub 등에 올린 복사본. 보통 별명이 `origin` |
| **`git add`** | 작업 폴더 → 스테이징 |
| **`git commit`** | 스테이징 → 로컬 저장소 (저장 지점 만들기) |
| **`git push`** | 로컬 저장소 → 원격 |
| **`git pull`** | 원격 기록을 받은 뒤 설정된 방식으로 현재 branch에 통합 |
| **`git clone`** | 원격 저장소를 통째로 내려받아 시작 |
| **`git status`** | 지금 어느 칸에 뭐가 있는지 보기 |
| **untracked** | Git이 아직 한 번도 본 적 없는 파일. `add` 전에는 커밋되지 않음 ([04 §4](04-four-areas.md)) |
| **`.gitignore`** | Git이 무시할 파일 목록. Secret 파일·라이브러리 폴더 ([04 §5](04-four-areas.md)) |

## 3. 커밋과 되돌리기

| 용어 | 뜻 |
| --- | --- |
| **커밋 (commit)** | 그 시점의 프로젝트 전체 상태 + 메시지 + 이전 커밋 연결 ([05](05-commits-and-undo.md)) |
| **해시 (hash)** | 커밋을 가리키는 ID. `b975e6c…` 앞 7글자만 써도 됨 |
| **HEAD** | "지금 내가 있는 위치". `HEAD~1`은 그 하나 앞 커밋 |
| **`git log`** | 커밋 기록 보기. `--oneline`으로 한 줄씩 |
| **`git diff`** | 바뀐 줄 보기. `+`는 추가, `−`는 삭제 ([10 S5](10-scenarios-solo.md)) |
| **`git restore 파일`** | 그 파일의 미커밋 변경을 버리고 기준 commit 상태로 되돌림 |
| **`git revert 해시`** | 그 commit을 취소하는 **새 commit을** 만들어 기존 기록을 보존 |
| **`git reset --hard`** ⛔ | 기록과 파일을 지움. **커밋 안 된 작업은 영구 삭제** ([05 §4](05-commits-and-undo.md)) |
| **`git commit --amend`** | 마지막 커밋을 다시 쓰기. push 전에만 |
| **`git stash`** | 하던 작업을 임시 서랍에 치워 두기 ([10 S6](10-scenarios-solo.md)) |
| **`git reflog`** | HEAD가 거쳐 온 기록. 실수로 날린 **커밋**을 되찾을 때 |

## 4. 브랜치

| 용어 | 뜻 |
| --- | --- |
| **브랜치 (branch)** | 같은 프로젝트의 평행 세계. 오가면 폴더 내용이 바뀜 ([06](06-branches.md)) |
| **main (예전 master)** | 기본 브랜치. "항상 돌아가는 상태"로 유지 |
| **`git switch -c 이름`** | 브랜치를 만들며 이동 (예전 `checkout -b`) |
| **`git merge 이름`** | 그 브랜치를 지금 브랜치에 합치기 |
| **충돌 (conflict)** | 두 브랜치가 같은 줄을 다르게 고쳤을 때. `<<<<<<<` 표시로 나타남 ([06 §4](06-branches.md)) |
| **Fast-forward** | 갈라진 적이 없어 포인터만 앞으로 옮기는 병합 |
| **트렁크 기반 (trunk-based)** | main 하나 + 짧게 사는 브랜치. 이 가이드의 권장 전략 ([06 §3](06-branches.md)) |
| **GitFlow** | develop·release·hotfix 등 여러 장수 브랜치를 쓰는 모델. 큰 팀용 |
| **working tree** | 현재 branch의 파일을 펼쳐 놓고 고치는 작업 폴더 |
| **worktree** | 같은 repository에 연결된 추가 working tree. commit·branch 기록은 공유하고 미커밋 변경·staging은 분리 ([07](07-worktrees.md)) |
| **`git worktree add`** | 새 작업 폴더를 repository에 연결하고 branch를 checkout |
| **`git worktree list`** | 연결된 worktree의 경로·commit·branch를 표시 |
| **`git rebase`** | 커밋을 다른 지점 위로 옮겨 붙이기. 이 가이드 범위 밖 |
| **cherry-pick** | 특정 커밋 하나만 골라 가져오기. 범위 밖 |

## 5. 공유

| 용어 | 뜻 |
| --- | --- |
| **origin** | 원격 저장소의 기본 별명 |
| **PR (Pull Request)** | "내 브랜치를 main에 합쳐 주세요" 요청서 겸 검토 화면 ([09 §3](09-github-and-pr.md)) |
| **Merge Request (MR)** | GitLab에서 PR을 부르는 이름. 같은 것 |
| **Private / Public 저장소** | 접근 범위가 제한된 저장소 / 누구나 볼 수 있는 저장소 |
| **GitHub Release** | 특정 tag를 설명·asset과 함께 배포하는 GitHub의 release object |
| **Personal Access Token** | GitHub push 시 비밀번호 대신 쓰는 토큰 ([09 §2](09-github-and-pr.md)) |
| **Collaborator** | 내 저장소에 쓰기 권한을 준 사람 ([11 S9](11-scenarios-share.md)) |
| **Conventional Commits** | `feat:`, `fix:` 접두어를 쓰는 커밋 메시지 관례 ([08 §3](08-commit-messages.md)) |

## 6. 혼동하기 쉬운 쌍 ★

| 쌍 | 차이 |
| --- | --- |
| **Git vs GitHub** | 내 컴퓨터의 도구 ↔ 인터넷 서비스. GitHub 없이도 Git은 완전히 동작 |
| **저장(Ctrl+S) vs 커밋** | 파일을 바꿈 ↔ 되돌릴 수 있는 지점을 남김 |
| **`add` vs `commit`** | 담을 것 고르기 ↔ 담은 것으로 지점 만들기 |
| **`commit` vs `push`** | 내 컴퓨터에 저장 ↔ 인터넷에 올리기. 커밋만 하면 백업 아님 |
| **`restore` vs `reset --hard`** | 지목한 파일만 되돌림 ↔ 전부 지움(복구 불가) |
| **`revert` vs `reset`** | 취소 커밋을 **쌓음**(안전) ↔ 기록을 **지움**(위험) |
| **`fetch` vs `pull`** | 받아만 둠 ↔ 받아서 내 파일에 합침 |
| **`stash pop` vs `apply`** | 꺼내고 서랍 비움 ↔ 꺼내되 서랍에 남김 |
| **`switch -c` vs `switch`** | 만들며 이동 ↔ 있는 브랜치로 이동 |
| **branch vs worktree** | commit 기록의 갈래 ↔ 그 갈래를 별도 폴더에 펼친 작업 공간 |
| **merge 충돌 vs 오류** | 사람에게 고르라는 **질문** ↔ 고장. 충돌은 정상적인 상황 |
| **untracked vs modified** | Git이 모르는 새 파일 ↔ 알고 있는데 바뀐 파일 |
| **커밋 전 비밀값 vs push 후 비밀값** | 지우면 끝 ↔ **키를 바꿔야 함** ([11 S10](11-scenarios-share.md)) |

---

**← [README로 돌아가기](README.md)**
