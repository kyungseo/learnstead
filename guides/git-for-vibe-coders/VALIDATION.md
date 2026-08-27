# 검증 기록

이 문서는 **AI로 코딩하는 사람을 위한 Git의** 명령을 어디까지 실제로 확인했는지 기록합니다. 공식 문서를 확인한 것과 명령을
직접 실행한 것은 구분합니다.

## 현재 요약

| 경로 | 상태 | 확인 범위 |
| --- | --- | --- |
| 문서 구조와 내부 링크 | 통과 | 2026-08-27 링크·이미지 경로 전수 검사 |
| 03 설치 확인·설정 명령 | 실행 검증 | `git --version`, `git config --global user.name/email` |
| README 10분 경로 (`init`→ignore 확인→`add`→staged diff→`commit`→`log`) | 실행 검증 | 2026-08-27 새 저장소에서 전 과정 재확인 |
| 05 되돌리기 (`restore`·`revert`·`reset --hard`) | 실행 검증 | 세 명령의 실제 결과와 파괴성 확인 |
| 06 브랜치 (생성·이동·병합·삭제) | 실행 검증 | 두 시안 브랜치 비교 후 병합 |
| 06 §4 병합 충돌 | 실행 검증 | 충돌 유도 → 표시 확인 → 해결 → 병합 커밋 |
| 07 worktree | 실행 검증 | add/list, branch·working tree 분리, commit 공유, main merge, remove, branch 삭제 |
| 10 S1~S6 (혼자 시나리오) | 실행 검증 | 여섯 시나리오 전부 |
| 10 S6 stash 충돌 | 실행 검증 | 의도치 않게 발생 → 재현 확인 후 문서화 |
| 11 S8 clone | 실행 검증 | 로컬 저장소를 원격 삼아 clone, 기록·remote 확인 |
| 11 S10 Secret 파일 (② add 후 / ③ commit 후) | 실행 검증 | `restore --staged`, `rm --cached` + `amend`, `check-ignore` |
| 11 S7 GitHub push / S9 협업 / 09 PR | 문서 확인 | 실제 GitHub 계정 조작은 하지 않음 |
| 11 S10 ④ push 후 대응 | 문서 확인 | key 교체 원칙. 실제 유출 실험은 하지 않음 |
| 11 S11 첫 Public 전환·version release | 문서·자료 확인 | GitHub 공식 문서와 `github-release-guide` 0.9.0 확인. 실제 공개 변경은 하지 않음 |
| Windows / Git Bash 경로 | 문서 확인 | 작성 환경은 macOS. Windows에서 직접 실행하지 않음 |
| SVG 다이어그램 | 통과 | 17종 소스 lint 0 error, Chromium 2× PNG 렌더, 시각 QA (아래) |

## 기준 장비

| 항목 | 값 |
| --- | --- |
| 확인일 | 2026-08-23 |
| 하드웨어 | Apple M4 Pro, 통합 메모리 24GB |
| OS | macOS 26.6.2 |
| 셸 | zsh (bash 스크립트로 시나리오 실행) |
| Git | 2.50.1 (Apple Git-155), `/usr/bin/git` |
| GitHub CLI | 2.96.0 (설치돼 있으나 이번 검증에서 원격 조작에 사용하지 않음) |

일련번호, 계정 정보, 개인 디렉터리 경로는 기록하지 않습니다.

## 실행 결과 (2026-08-23)

임시 폴더에 저장소 네 개를 만들어 시나리오를 순서대로 실행했습니다. 문서에 실린 출력은 전부 이때의 화면입니다.

| 확인 항목 | 결과 |
| --- | --- |
| `git init` → `add` → `commit` → `log --oneline` | `b975e6c 첫 저장: AI와 만든 초기 버전` |
| `git status --short` 세 덩어리 | ` M index.html` / `?? app.js` / `?? style.css` |
| `git restore index.html` | 지목한 파일만 복원, 새 파일 둘은 그대로 남음 |
| `git revert --no-edit <해시>` | `Revert "…"` 커밋이 추가되고 해당 변경만 파일에서 제거. 원 커밋은 로그에 유지 |
| `git reset --hard HEAD` | **커밋하지 않은 변경이 사라짐** — reflog에도 없음 |
| `git reflog` | `353732b HEAD@{0}: reset: moving to HEAD` 등 이동 기록 확인 |
| 브랜치 두 개 생성·전환 | `git switch try-blue` 시 `style.css`가 파랑, `try-green` 시 초록으로 실제 변경 |
| `git merge try-green` | main이 움직이지 않아 **Fast-forward** (`-m` 무시됨) |
| 병합 충돌 유도 | `CONFLICT (content): Merge conflict in style.css`, 파일에 `<<<<<<< HEAD` / `=======` / `>>>>>>> try-blue` 표시 |
| 충돌 해결 후 로그 | `*   7f2d148 병합: 시안 A 채택` 갈래 그래프 확인 |
| `git stash push` → 다른 파일 수정 → `pop` | 충돌 없이 복원 |
| `git stash push` → **같은 파일** 수정 → `pop` | `CONFLICT` 발생, `Updated upstream` / `Stashed changes` 표시. **stash entry는 유지됨** |
| `git diff` / `--stat` / `git show --stat HEAD` | 각각 줄 단위 / 요약 / 커밋 단위 출력 확인 |
| `.env` add 후 `restore --staged` + `.gitignore` | `git check-ignore -v .env` → `.gitignore:1:.env` |
| Secret 파일 커밋 후 `rm --cached` + `commit --amend` | 커밋 목록에서 파일 제거, **디스크의 파일은 유지** |
| `git clone`(로컬 경로) | 커밋 4개 전부 복제, `git remote -v`에 origin 등록, 무시된 Secret 파일은 따라오지 않음 |

## README 10분 경로 재검증 (2026-08-27)

| 확인 항목 | 결과 |
| --- | --- |
| `git status --short` | `.gitignore`, `index.html`만 untracked로 표시 |
| `git check-ignore -v .env` | `.gitignore:1:.env`로 제외 규칙 확인 |
| `git add .` → `git diff --staged --stat` | `.gitignore`, `index.html` 2개 file·3개 추가 line 표시, `.env` 제외 |
| `git commit` → `git log --oneline -1` | `432d16a 첫 저장: AI 작업 전 상태` |

## worktree 실행 결과 (2026-08-27)

별도 임시 저장소에서 `main`과 `add-login`을 두 작업 폴더에 동시에 펼치고, commit 공유와 working tree 분리를 확인했습니다.

| 확인 항목 | 결과 |
| --- | --- |
| `git worktree add ../repo-login -b add-login` | 새 branch와 linked worktree 생성 |
| `git worktree list` | 원래 폴더 `[main]`, 추가 폴더 `[add-login]`이 서로 다른 경로에 표시 |
| 추가 폴더에 `login.txt` 생성 | 추가 폴더에서만 `?? login.txt`; 원래 main 폴더는 clean |
| 추가 폴더에서 commit | main 폴더의 `git log --all`에서 `7af923f login worktree commit` 확인, main 파일에는 아직 없음 |
| main에서 `git merge add-login` | Fast-forward 후 main 폴더에 `login.txt` 생성 |
| `git worktree remove` → `git branch -d` | clean worktree 제거와 merge된 branch 삭제 성공, 목록에는 main만 남음 |

### 검증 중 발견한 것

1. **`git revert`에는 `-q` 옵션이 없습니다.** 스크립트 작성 중 `git revert -q`가 usage 오류를 냈습니다. 문서에는 `--no-edit`만 씁니다.
2. **stash pop 충돌은 의도치 않게 발생했습니다.** 처음 작성한 시나리오에서 같은 파일 끝을 두 번 건드려 충돌이 났고, 이것이
   초심자가 실제로 만날 상황이라 판단해 10 S6에 정식 절로 편입했습니다.
3. **Fast-forward 병합에서는 `-m` 메시지가 무시됩니다.** 06 §2에 주석으로 남겼습니다.

## 실행하지 않은 것

- 실제 GitHub 계정으로 저장소 생성·push·PR·Collaborator 초대 (09, 11 S7·S9) — 공식 문서로만 확인
- 실제 Private→Public visibility 변경, tag·GitHub Release 생성, repository 설정 변경 (11 S11) — 문서와 skill만 확인
- Windows 환경에서의 설치와 Git Bash 실행 (03 §3) — macOS에서 작성
- push된 비밀값의 기록 삭제 도구(`git filter-repo` 등) — 범위 밖으로 명시

이 항목들을 직접 확인하면 다음을 기록해 주세요: OS·Git 버전, 실행한 명령 전문, 화면 출력(비밀값 제거), 성공 판정 충족 여부.

## SVG 다이어그램 검증 (2026-08-27)

| 항목 | 결과 |
| --- | --- |
| 소스 lint | 17/17 파일 0 error 0 warning |
| 렌더 | Google Chrome 151.0.7922.175 (headless) · 2× PNG 17/17 · viewBox의 정확히 2배 크기 확인 |
| 시각 QA | fit-to-page와 확대 두 단계로 전건 확인. 신규 3종의 box 간격·화살표 시작과 끝·head 방향·text overflow를 확인하고, 브랜치 두 도식은 전역 시간 방향과 선의 분기·병합 형태로 단순화. 되돌리기와 명령 신호등의 위험 분류를 본문과 맞춤 |
| 본문·alt·title/desc 대조 | 각 SVG의 `<title>`·`<desc>`와 Markdown 대체 텍스트가 같은 범위의 주장을 하도록 작성 |

PNG는 검증용으로만 생성했고 저장소에는 SVG 원본만 둡니다.

## 정적 검증

- 내부 링크·이미지 경로: Markdown 링크 대상을 파일 존재 여부로 전수 검사
- 셸 명령: 시나리오를 bash 스크립트로 묶어 실제 실행
- SVG: svg-infographic 소스 lint + Chromium 2× 렌더

정적 검증 통과는 GitHub 웹 조작의 성공을 대신하지 않습니다.
