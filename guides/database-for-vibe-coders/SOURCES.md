# 출처와 근거

[가이드 목차](README.md) · [검증 기록](VALIDATION.md)

## 문서 확인 · 2026-09-13

아래 공식 문서를 직접 열어 확인했습니다. 모두 문서 확인이며 제품의 실행 결과를 뜻하지 않습니다. 문서의 최신 수정일이 일관되게 제공되지 않아 확인일을 기준으로 남겼습니다. `current` 링크는 이후 다른 버전을 가리킬 수 있습니다. PostgreSQL은 확인 당시 18, MySQL은 8.4 문서를 사용했습니다.

| 공식 출처 | 본문에서 사용한 범위 | 장 |
| --- | --- | --- |
| [SQLite 사용 범위](https://www.sqlite.org/whentouse.html) | 서버 사용 가능, 동시 쓰기와 네트워크 파일 접근 제약 | 02 |
| [SQLite 외래키](https://www.sqlite.org/foreignkeys.html) | 외래키 집행은 연결 설정을 확인해야 함 | 03 |
| [PostgreSQL 제약조건](https://www.postgresql.org/docs/current/ddl-constraints.html) | NOT NULL, CHECK, UNIQUE, 외래키와 삭제 동작 | 03·05 |
| [PostgreSQL 트랜잭션](https://www.postgresql.org/docs/current/tutorial-transactions.html) | 여러 DB 작업의 확정·취소와 원자성 | 05 |
| [MySQL InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-introduction.html) | InnoDB의 트랜잭션과 외래키 기능 | 02 |
| [MongoDB 스키마 검증](https://www.mongodb.com/docs/manual/core/schema-validation/) | 유연한 문서 구조와 검증 규칙은 함께 사용 가능 | 02·03 |
| [Firestore 데이터 모델](https://firebase.google.com/docs/firestore/data-model) | 문서·컬렉션을 통한 모델링 | 02·03 |
| [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started) | 클라이언트 규칙과 서버 접근 경로의 구분 | 06 |
| [Firestore 과금](https://firebase.google.com/docs/firestore/pricing) | 읽기·쓰기 등의 사용량, 리스너 읽기 비용 | 08 |
| [Supabase API 키](https://supabase.com/docs/guides/getting-started/api-keys) | publishable과secret/service-role의 권한 차이 | 06 |
| [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) | 행 단위 정책, 역할별 접근, 사용자 권한으로 확인 | 06 |
| [Supabase migration](https://supabase.com/docs/guides/deployment/database-migrations) | 파일로 DB 변경 관리, 로컬과 원격 적용의 구분 | 07 |
| [Supabase 백업](https://supabase.com/docs/guides/platform/backups) | DB 백업에 Storage 파일 본체가 포함되지 않는 범위 | 08 |
| [OWASP SQL injection 예방](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) | 매개변수화된 쿼리로 명령과 입력값을 구분 | 04 |
| [Vercel SQLite 안내](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel) | 로컬 SQLite 파일과 서버리스 실행 공간의 제약 | 01 |
| [SQLite backup API](https://www.sqlite.org/backup.html) | 작동 중인 DB의 일관된 백업을 위한 API | 08 |
| [PostgreSQL 인덱스](https://www.postgresql.org/docs/current/indexes-intro.html) | 조회 도움과 유지 비용을 함께 고려 | 08 |
| [PostgreSQL LIMIT과 OFFSET](https://www.postgresql.org/docs/current/queries-limit.html) | 명시적 순서가 없으면 반환 부분집합을 예측할 수 없음 | 08 |

## 원리와 해석

메모리·화면·저장소의 구분, 데이터 구조와 변경 절차, 코드·구조·데이터 복원의 구분은 원리를 설명한 것입니다. 제품별 CLI의 실행 증거가 아닙니다. 스터디 신청 앱을 중심으로 관계형 DB를 선택한 경로는 학습 목적에 맞춘 해석이며 제품의 보편적 우열을 주장하지 않습니다.

가격 수치·무료 한도·시장 점유율은 비교 근거로 사용하지 않았습니다. 결제나 실제 서비스 운영을 결정할 때는 현재 제공 조건을 다시 확인해야 합니다.

---

[가이드 목차](README.md) · [검증 기록](VALIDATION.md)
