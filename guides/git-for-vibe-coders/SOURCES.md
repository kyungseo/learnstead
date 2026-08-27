# 출처

**AI로 코딩하는 사람을 위한 Git에서** 버전에 따라 달라질 수 있는 정보와 그 근거 자료를 연결합니다.

- 마지막 확인일: 2026-08-27
- `문서 확인`은 공식 문서를 읽었다는 뜻이며, 명령 실행 성공을 뜻하지 않습니다.
- Git 명령의 동작은 오래 안정적이지만, GitHub 웹 화면과 인증 방식은 바뀝니다.

## Git 본체

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| 명령 레퍼런스 전반 | `add`·`commit`·`restore`·`revert`·`reset`·`switch`·`merge`·`stash`의 정의와 옵션 | [Git Reference](https://git-scm.com/docs) | 문서 확인 |
| `git restore` / `git switch` | 2.23에서 도입된 새 명령. `checkout`의 두 역할을 분리 | [git-restore](https://git-scm.com/docs/git-restore) · [git-switch](https://git-scm.com/docs/git-switch) | 문서 확인 |
| `git reset` 모드 | `--soft`/`--mixed`/`--hard`의 차이와 `--hard`의 파괴성 | [git-reset](https://git-scm.com/docs/git-reset) | 문서 확인 |
| `git revert` | 취소 커밋을 새로 만드는 동작 | [git-revert](https://git-scm.com/docs/git-revert) | 문서 확인 |
| `git stash` | push/pop/apply/drop과 충돌 시 stash 유지 동작 | [git-stash](https://git-scm.com/docs/git-stash) | 문서 확인 |
| `git pull` | fetch 후 설정에 따라 merge 또는 rebase로 통합되는 동작 | [git-pull](https://git-scm.com/docs/git-pull) | 문서 확인 |
| `git worktree` | 여러 branch의 동시 checkout, worktree별 HEAD·index, add/list/remove/prune, 같은 branch 중복 checkout 보호, submodule 제약 | [git-worktree](https://git-scm.com/docs/git-worktree) | 문서 확인 |
| `.gitignore` 문법 | 패턴 규칙, `check-ignore` | [gitignore](https://git-scm.com/docs/gitignore) | 문서 확인 |
| 설치 (Windows) | Git for Windows 설치 옵션과 Git Bash | [Git 다운로드](https://git-scm.com/download/win) | 문서 확인 |
| 설치 (macOS) | Xcode 명령줄 도구 경유 설치 | [Git 다운로드 (macOS)](https://git-scm.com/download/mac) | 문서 확인 |
| 기본 브랜치 이름 | `init.defaultBranch` 설정 | [git-config](https://git-scm.com/docs/git-config) | 문서 확인 |
| 개념 전반 | 스냅샷 모델, 세 상태, 브랜치 | [Pro Git (한국어)](https://git-scm.com/book/ko/v2) | 문서 확인 |

## GitHub

| 범위 | 확인한 내용 | 1차 자료 | 상태 |
| --- | --- | --- | --- |
| 저장소 만들기·공개 범위 | Private/Public, README 초기화 옵션 | [GitHub Docs — Create a repo](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-new-repository) | 문서 확인 |
| 인증 | 비밀번호 인증 폐지, Personal Access Token, Credential Manager | [GitHub Docs — Authentication](https://docs.github.com/authentication) | 문서 확인 |
| PR | Pull Request의 개념과 만드는 흐름 | [GitHub Docs — Pull requests](https://docs.github.com/pull-requests) | 문서 확인 |
| Collaborator | 개인 저장소에 협업자 초대 | [GitHub Docs — Collaborators](https://docs.github.com/account-and-profile) | 문서 확인 |
| Secret scanning | 유출된 키 자동 감지 기능의 범위 | [GitHub Docs — Secret scanning](https://docs.github.com/code-security/secret-scanning) | 문서 확인 |
| `gh` CLI | `gh pr create` | [GitHub CLI manual](https://cli.github.com/manual/) | 문서 확인 |
| 저장소 공개 범위 변경 | visibility 변경 전 영향과 보안 기능 차이 | [GitHub Docs — Setting repository visibility](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility) | 문서 확인 |
| Release | tag를 기반으로 한 GitHub Release 생성과 asset | [GitHub Docs — Managing releases](https://docs.github.com/repositories/releasing-projects-on-github/managing-releases-in-a-repository) | 문서 확인 |

## 공개 release 점검 skill

| 범위 | 확인한 내용 | 자료 | 상태 |
| --- | --- | --- | --- |
| `github-release-guide` 0.9.0 | 기존 Private github.com 저장소의 첫 Public 전환과 공개 저장소의 version release, Assess·Guided mode, 변경별 승인과 사후 검증 경계 | [Skillstead — github-release-guide](https://github.com/kyungseo/skillstead/tree/main/skills/github-release-guide) | 자료 확인 |

## 관례·전략

| 범위 | 확인한 내용 | 자료 | 상태 |
| --- | --- | --- | --- |
| Conventional Commits | `feat:`·`fix:` 등 접두어 규격 | [conventionalcommits.org](https://www.conventionalcommits.org/ko/) | 문서 확인 |
| 트렁크 기반 개발 | main 중심·짧은 브랜치 모델의 정의 | [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/) | 자료 확인 |
| GitFlow | 2010년 제안된 브랜치 모델 | [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/) | 자료 확인 |
| VCS 세대 구분 (CVS·SVN·Git) | 중앙 집중식과 분산형의 차이 | [Pro Git 1.1 — 버전 관리란?](https://git-scm.com/book/ko/v2) | 문서 확인 |

## Source ledger를 갱신하는 규칙

1. 본문의 명령·화면 설명을 바꾸면 같은 commit에서 이 표를 갱신합니다.
2. 블로그·요약 글은 탐색에만 쓰고, 확정 설명은 공식 문서로 확인합니다.
3. 직접 실행한 결과는 이 문서가 아니라 [VALIDATION.md](VALIDATION.md)에 환경·명령·결과를 남깁니다.
4. GitHub 화면 설명은 바뀌기 쉬우므로 `문서 확인` 이상으로 올리지 않습니다.
