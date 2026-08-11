#!/usr/bin/env python3
"""Learnstead 공개 문서의 구조와 정적 품질을 검사한다."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "docs/CONTENT-TYPES.md",
    "docs/AUTHORING.md",
    "docs/VALIDATION.md",
    "docs/VISUALS.md",
    "guides/local-llm/README.md",
    "guides/local-llm/CHANGELOG.md",
    "guides/local-llm/SOURCES.md",
    "guides/local-llm/VALIDATION.md",
)
FORBIDDEN_FILES = ("AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md")
FORBIDDEN_TEXT = {
    "machine-local path": re.compile(r"/Users/"),
    "private engagement path": re.compile(r"engagements/", re.IGNORECASE),
    "legacy verification label": re.compile(r"\[검증\s+\d{4}-\d{2}\]"),
    "internal tracking identifier": re.compile(r"\b(?:FEAT|PATCH|HOTFIX|CHORE)-\d{8}-\d{3}\b|\bDR-\d{3,4}\b"),
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
DRAFT_PATTERNS = (
    re.compile(r"(?m)^## 미공개\s*$"),
    re.compile(r"(?m)^(?:\*\*)?초판 준비 중"),
    re.compile(r"\|\s*작성 중\s*\|"),
)


def text_files() -> list[Path]:
    suffixes = {".md", ".svg", ".py", ".txt", ".yml", ".yaml"}
    return [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in suffixes]


def validate_required(errors: list[str]) -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"필수 파일 없음: {relative}")
    for relative in FORBIDDEN_FILES:
        if (ROOT / relative).exists():
            errors.append(f"초기 공개 surface에 두지 않는 파일: {relative}")


def validate_text(errors: list[str], public: bool) -> None:
    for path in text_files():
        relative = path.relative_to(ROOT)
        content = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(content.splitlines(), 1):
            if line != line.rstrip():
                errors.append(f"후행 공백: {relative}:{line_number}")
        if relative != Path("tools/validate.py"):
            for label, pattern in FORBIDDEN_TEXT.items():
                if pattern.search(content):
                    errors.append(f"공개 경계 위반({label}): {relative}")
        if public and any(pattern.search(content) for pattern in DRAFT_PATTERNS):
            errors.append(f"공개 전 제거할 상태 표기: {relative}")


def validate_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(content):
            target = raw_target.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            file_target = unquote(target.split("#", 1)[0])
            if not file_target:
                continue
            resolved = (path.parent / file_target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"저장소 밖을 가리키는 link: {path.relative_to(ROOT)} -> {target}")
                continue
            if not resolved.exists():
                errors.append(f"깨진 link: {path.relative_to(ROOT)} -> {target}")


def validate_svg(errors: list[str]) -> None:
    for path in ROOT.rglob("*.svg"):
        try:
            ET.parse(path)
        except ET.ParseError as error:
            errors.append(f"SVG XML 오류: {path.relative_to(ROOT)}: {error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true", help="공개 직전 상태 표기도 함께 검사")
    args = parser.parse_args()

    errors: list[str] = []
    validate_required(errors)
    validate_text(errors, args.public)
    validate_links(errors)
    validate_svg(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)}개 문제")
        return 1

    print("PASS: Learnstead 정적 검증")
    return 0


if __name__ == "__main__":
    sys.exit(main())
