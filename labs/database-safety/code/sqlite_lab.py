"""가상 독서 기록: 명령마다 새 연결을 열어 저장과 재조회를 관찰한다."""
from contextlib import contextmanager, closing
import argparse
import json
import sqlite3
import tempfile
from pathlib import Path


@contextmanager
def connect(path):
    db = sqlite3.connect(path)
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT NOT NULL UNIQUE)')
    db.commit()
    try:
        with db:
            yield db
    finally:
        db.close()


def demo():
    with tempfile.TemporaryDirectory(prefix='learnstead-sqlite-') as folder:
        path = Path(folder) / 'practice.sqlite'
        with connect(':memory:') as db:
            db.execute('INSERT INTO books(title) VALUES (?)', ('데이터 이야기',))
        with connect(':memory:') as reopened:
            assert reopened.execute('SELECT count(*) FROM books').fetchone()[0] == 0
        print('PASS 메모리 저장 실패 관찰: 새 연결은 0행')
        with connect(path) as db:
            db.execute('INSERT INTO books(title) VALUES (?)', ('데이터 이야기',))
        with connect(path) as reopened:
            assert reopened.execute('SELECT title FROM books').fetchall() == [('데이터 이야기',)]
        print('PASS 파일 저장 수정: 새 연결에서도 1행 유지')
        with connect(path) as db:
            try:
                with db:
                    db.execute('INSERT INTO books(title) VALUES (?)', ('다음 책',))
                    db.execute('INSERT INTO books(title) VALUES (?)', ('데이터 이야기',))
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError('중복 제목이 허용됨')
            assert db.execute('SELECT count(*) FROM books').fetchone()[0] == 1
            print('PASS UNIQUE 위반 및 두 INSERT의 transaction rollback')
            db.execute("ALTER TABLE books ADD COLUMN note TEXT NOT NULL DEFAULT ''")
            assert db.execute('SELECT id,title,note FROM books').fetchall() == [(1, '데이터 이야기', '')]
            print('PASS 기존 데이터가 있는 migration: ID·제목 보존 및 메모 기본값')
            backup_path = Path(folder) / 'backup.sqlite'
            with closing(sqlite3.connect(backup_path)) as backup:
                db.backup(backup)
            with db:
                db.execute('DELETE FROM books')
            assert db.execute('SELECT count(*) FROM books').fetchone()[0] == 0
            print('PASS 삭제 실패 fixture: 원본 0행 관찰')
        with closing(sqlite3.connect(backup_path)) as restored:
            assert restored.execute('SELECT id,title,note FROM books').fetchall() == [(1, '데이터 이야기', '')]
            assert restored.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        print('PASS 별도 백업 파일 조회: 1행 및 integrity_check 정상')
    print('검증 완료: 6개 판정 PASS · 임시 연습 파일 정리 완료')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', default='demo', choices=['demo', 'add', 'list', 'reset'])
    parser.add_argument('--db', type=Path, default=Path('practice.sqlite'))
    parser.add_argument('--title', default='데이터 이야기')
    parser.add_argument('--confirm-local-reset', action='store_true')
    args = parser.parse_args()
    if args.action == 'demo':
        demo()
        return
    if args.action == 'reset' and not args.confirm_local_reset:
        parser.error('reset은 --confirm-local-reset을 명시해야 합니다. 지정한 DB의 books 행을 지웁니다.')
    args.db.parent.mkdir(parents=True, exist_ok=True)
    with connect(args.db) as db:
        if args.action == 'add':
            try:
                db.execute('INSERT INTO books(title) VALUES (?)', (args.title,))
            except sqlite3.IntegrityError as error:
                parser.exit(1, f'저장 거절: {error}\n')
            print('저장 완료: ' + str(args.db.resolve()))
        if args.action == 'reset':
            db.execute('DELETE FROM books')
            print('초기화 완료: books 0행')
        rows = db.execute('SELECT id,title FROM books ORDER BY id').fetchall()
        print(json.dumps([{'id': row[0], 'title': row[1]} for row in rows], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
