#!/usr/bin/env python3
"""과제 결과를 규칙 5개로 판정한다.  사용법: python3 check.py <프로젝트 디렉터리>
과제: src/textkit/slug.py 에 slugify(text: str) -> str 추가 + 테스트 + CHANGELOG.
출력: 규칙별 PASS/FAIL 과 점수 n/5. 종료 코드 0 = 5/5.
"""
import argparse
import ast
import re
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description="지시문 실습 결과를 규칙 5개로 판정한다.")
parser.add_argument("project", type=Path, help="판정할 프로젝트 디렉터리")
args = parser.parse_args()

root = args.project.resolve()
if not root.is_dir():
    parser.error(f"프로젝트 디렉터리가 없다: {root}")
res = {}
py_new = [p for p in root.rglob("*.py") if p.name not in ("__init__.py", "wordcount.py", "test_wordcount.py") and ".venv" not in p.parts]
impl = root / "src" / "textkit" / "slug.py"
# R1 owner 첫 줄 (새 .py 전부)
res["R1 owner 주석"] = bool(py_new) and all(p.read_text(encoding="utf-8").splitlines()[:1] == ["# owner: platform-team"] for p in py_new)
# 함수 수집. 하나라도 문법이 깨졌으면 함수 관련 규칙은 실패로 판정한다.
funcs = []
syntax_ok = True
for p in py_new:
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        syntax_ok = False
        continue
    funcs += [f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
def korean(s): return bool(s) and re.search(r"[가-힣]", s.splitlines()[0]) is not None
res["R2 한국어 docstring"] = syntax_ok and bool(funcs) and all(korean(ast.get_docstring(f) or "") for f in funcs)
def typed(f):
    args = [a for a in f.args.posonlyargs + f.args.args + f.args.kwonlyargs if a.arg not in ("self", "cls")]
    return all(a.annotation is not None for a in args) and f.returns is not None
res["R3 타입 힌트"] = syntax_ok and bool(funcs) and all(typed(f) for f in funcs)
# R4 테스트 위치·이름
tests = [p for p in py_new if p.parent.name == "tests" and p.name.startswith("test_")]
test_funcs = []
tests_syntax_ok = True
for p in tests:
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        tests_syntax_ok = False
        continue
    test_funcs.extend(
        f for f in ast.walk(tree)
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test")
    )
res["R4 테스트 위치·이름"] = tests_syntax_ok and any(p.name == "test_slug.py" for p in tests) and bool(test_funcs) and all(re.match(r"test_slugify_\w+$", f.name) for f in test_funcs)
# R5 CHANGELOG
cl = (root / "CHANGELOG.md").read_text(encoding="utf-8") if (root / "CHANGELOG.md").exists() else ""
m = re.search(r"## \[Unreleased\]\n(.*?)(?=\n## |\Z)", cl, re.S)
res["R5 CHANGELOG"] = bool(m) and bool(re.search(r"^- .*(?:slug|슬러그).*추가", m.group(1), re.M | re.I))
res["과제 자체"] = impl.exists() and "def slugify" in impl.read_text(encoding="utf-8")
score = sum(v for k, v in res.items() if k.startswith("R"))
for k, v in res.items(): print(f"  {'PASS' if v else 'FAIL'}  {k}")
print(f"score {score}/5")
sys.exit(0 if score == 5 else 1)
