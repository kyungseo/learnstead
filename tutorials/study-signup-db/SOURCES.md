# 출처와 확인 범위

확인일은 2026-09-13입니다. 아래는 공식 문서를 읽어 확인한 내용이며, 이 예제의 실제 실행 결과는 [VALIDATION.md](VALIDATION.md)에서 따로 확인합니다. 문서의 `current` 주소는 나중에 다른 버전을 가리킬 수 있습니다.

| 주제 | 공식 출처 | 사용한 범위 | 상태 |
| --- | --- | --- | --- |
| Node.js 버전 | [Node.js Releases](https://nodejs.org/en/about/previous-releases) | Node.js 24의 LTS 상태. 예제 실행 기준은 검증한 24.19.0 | 문서 확인 |
| 로컬 Supabase | [Local Development](https://supabase.com/docs/guides/local-development) | CLI·Docker 전제, 로컬 서비스, 외부 공개 금지 | 문서 확인 |
| 행 단위 접근 | [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) | 테이블 권한·행 정책, 사용자별 제한 | 문서 확인 |
| API 키 | [API keys](https://supabase.com/docs/guides/getting-started/api-keys) | 공개용 키와 서버의 높은 권한 키 구분 | 문서 확인 |
| DB 구조 변경 | [Database Migrations](https://supabase.com/docs/guides/deployment/database-migrations) | 순서 있는 SQL 변경, seed·reset의 역할 | 문서 확인 |
| DB 백업 | [Database Backups](https://supabase.com/docs/guides/platform/backups) | DB 백업과 Storage 파일 본체의 범위 차이 | 문서 확인 |
| 제약조건 | [PostgreSQL Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) | 기본 키·외래 키·고유값·값 검사 | 문서 확인 |
| 트랜잭션 | [PostgreSQL Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html) | 성공 시 확정, 실패 시 부분 변경 취소 | 문서 확인 |
| SQLite 메모리 DB | [In-Memory Databases](https://www.sqlite.org/inmemorydb.html) | 메모리 DB와 연결 수명 | 문서 확인 |

## 자료 자체의 선택

가상의 스터디 모임, 두 사용자, 정원 경쟁, 메모 열 추가는 학습을 위해 설계한 예제입니다. 특정 제품이 이 앱을 추천했다는 뜻은 아닙니다. AI 요청문도 이 자료의 작성 예이며, 기술적으로 접근을 강제하는 장치나 모델 성능의 근거가 아닙니다.

## 다시 확인할 조건

Supabase CLI·Auth·API·DB 버전, Docker의 포트 공개 방식, 호스팅·백업 조건이 달라지면 해당 공식 문서와 실행 경로를 다시 확인합니다. 가격표·무료 제공량·클라우드 운영 보장은 이 자료의 주장 범위에 넣지 않았습니다.

[← 자료 목차](README.md)
