#!/usr/bin/env python3
"""명시한 읽기 순서로 Learnstead 문서의 상하 탐색을 동기화한다."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = ("guides", "tutorials", "labs")
MARKERS = ("<!-- learnstead:nav:start -->", "<!-- learnstead:nav:end -->",
           "<!-- learnstead:footer:start -->", "<!-- learnstead:footer:end -->")
IMAGE = re.compile(r"!\[[^\]]+\]\(([^)]+)\)")


def outside_fences(text):
    fence = None
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            token = match[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line.strip().strip(token[0]):
                fence = None
            yield ""
        else:
            yield line if fence is None else ""


def title(path):
    headings = [line[2:].strip() for line in outside_fences(path.read_text()) if line.startswith("# ")]
    if len(headings) != 1:
        raise ValueError(f"H1은 하나여야 합니다: {path.name}")
    return headings[0]


def safe_path(root, relative):
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError(f"저장소 밖 경로: {relative}")
    return path


def load_index(root):
    data = json.loads((root / "docs/content-index.json").read_text())
    if data.get("version") != 1 or not isinstance(data.get("items"), list):
        raise ValueError("문서 목록 version/items 오류")
    seen = set()
    actual = {str(p.relative_to(root)) for kind in KINDS for p in (root / kind).glob("*/*.md")}
    for item in data["items"]:
        folder = item["path"]
        parts = Path(folder).parts
        if len(parts) != 2 or parts[0] not in KINDS or item["type"] != parts[0][:-1]:
            raise ValueError(f"자료 경로/유형 오류: {folder}")
        directory = safe_path(root, folder)
        files = ["README.md"] + item["chapters"] + item["support"]
        if len(files) != len(set(files)):
            raise ValueError(f"중복 문서: {folder}")
        for name in files:
            if Path(name).name != name or not name.endswith(".md"):
                raise ValueError(f"최상위 Markdown만 등록: {folder}/{name}")
            path = safe_path(root, f"{folder}/{name}")
            relative = str(path.relative_to(root.resolve()))
            if relative in seen or not path.is_file():
                raise ValueError(f"중복 또는 없는 문서: {relative}")
            seen.add(relative)
            title(path)
        hero = safe_path(directory, item["hero"])
        if not hero.is_file() or hero.suffix not in (".webp", ".png"):
            raise ValueError(f"대표 표지 오류: {folder}")
        diagram = item.get("first_diagram")
        if diagram:
            if diagram["page"] not in files:
                raise ValueError(f"도식 페이지 미등록: {folder}")
            asset = safe_path(directory, diagram["asset"])
            if asset.suffix != ".svg" or not asset.is_file():
                raise ValueError(f"첫 SVG 오류: {folder}")
        elif not item.get("diagram_note", "").strip():
            raise ValueError(f"첫 SVG 또는 생략 이유 필요: {folder}")
    if seen != actual:
        raise ValueError(f"문서 목록 불일치: 미등록 {sorted(actual-seen)}, 누락 {sorted(seen-actual)}")
    return data


def label(value):
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("`", "")


def navigation(root, item, name):
    directory = root / item["path"]
    chapters = item["chapters"]
    def link(prefix, target):
        return f"[{prefix}{label(title(directory / target))}]({target})"
    if name == "README.md":
        links = ["[← 학습 자료 목록](../../README.md)"]
        if chapters:
            links.append(link("시작: ", chapters[0]))
        links.append("[검증 기록](VALIDATION.md)")
    elif name in chapters:
        i = chapters.index(name)
        previous = chapters[i-1] if i else "README.md"
        links = [(link("← 이전: ", previous) if i else "[← 이전: 자료 소개](README.md)"), "[목차](README.md)"]
        if i+1 < len(chapters):
            links.append(link("다음: ", chapters[i+1]))
    else:
        links = ["[← 자료 소개](README.md)", "[학습 자료 목록](../../README.md)"]
    return " · ".join(links)


def strip_managed(text):
    # Only whole blocks outside code fences are owned by this tool.
    lines = text.splitlines()
    visible = list(outside_fences(text))
    remove = set()
    for start, end in ((MARKERS[0], MARKERS[1]), (MARKERS[2], MARKERS[3])):
        starts = [i for i,l in enumerate(visible) if l == start]
        ends = [i for i,l in enumerate(visible) if l == end]
        if len(starts) != len(ends) or len(starts) > 1 or (starts and starts[0] >= ends[0]):
            raise ValueError("관리 구간 주석이 손상되었습니다")
        if starts:
            remove.update(range(starts[0], ends[0]+1))
    return "\n".join(l for i,l in enumerate(lines) if i not in remove).strip()+"\n"


def render(text, nav):
    body = strip_managed(text)
    lines = body.splitlines()
    visible = list(outside_fences(body))
    heads = [i for i,l in enumerate(visible) if l.startswith("# ")]
    if len(heads) != 1 or any(l.strip() for l in visible[:heads[0]]):
        raise ValueError("페이지 첫 블록은 H1 하나여야 합니다")
    i = heads[0]
    content = "\n".join(lines[i+1:]).strip()
    return (lines[i]+"\n\n"+MARKERS[0]+"\n"+nav+"\n"+MARKERS[1]+"\n\n"
            +content+"\n\n"+MARKERS[2]+"\n\n---\n\n"+nav+"\n\n"+MARKERS[3]+"\n")


def run(root, sync=False):
    data = load_index(root)
    errors, updates = [], []
    catalog = (root / "README.md").read_text()
    catalog_images = IMAGE.findall(catalog) + re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', catalog)
    for item in data["items"]:
        directory = root / item["path"]
        overview = (directory / "README.md").read_text()
        if item["hero"] not in IMAGE.findall(overview):
            errors.append(f"소개 표지 참조 없음: {item['path']}")
        if f"{item['path']}/{item['hero']}" not in catalog_images:
            errors.append(f"목록 표지 불일치: {item['path']}")
        diagram = item.get("first_diagram")
        if diagram and diagram["asset"] not in IMAGE.findall((directory / diagram["page"]).read_text()):
            errors.append(f"첫 SVG 참조 없음: {item['path']}")
        for name in ["README.md"]+item["chapters"]+item["support"]:
            path = directory / name
            text = path.read_text()
            expected = render(text, navigation(root, item, name))
            if text != expected:
                updates.append((path, expected))
                if not sync:
                    errors.append(f"상하 탐색/마감 불일치: {path.relative_to(root)}")
            if name == "README.md":
                body = strip_managed(text).splitlines()[1:]
                first = next((line for line in body if line.strip()), "")
                if item["hero"] not in IMAGE.findall(first):
                    errors.append(f"소개 표지는 탐색 바로 아래: {item['path']}")
    # All input is validated before writing anything.
    if sync and not errors:
        for path, text in updates:
            path.write_text(text)
    return errors, len(updates)


def register(root, folder):
    directory = safe_path(root, folder)
    parts = Path(folder).parts
    if len(parts) != 2 or parts[0] not in KINDS or not directory.is_dir():
        raise ValueError("등록 경로는 guides|tutorials|labs/<slug>입니다")
    path = root / "docs/content-index.json"
    data = json.loads(path.read_text())
    if any(item["path"] == folder for item in data["items"]):
        raise ValueError("이미 등록된 자료입니다. 목록을 검토해 직접 수정하세요")
    text = (directory / "README.md").read_text()
    heroes = [s for s in IMAGE.findall(text) if s.endswith((".webp", ".png"))]
    if not heroes:
        raise ValueError("README 대표 표지를 먼저 연결하세요")
    files = sorted(p.name for p in directory.glob("*.md"))
    chapters = [p for p in files if re.match(r"^\d+[-.]", p)]
    item = dict(path=folder, type=parts[0][:-1], hero=heroes[0], chapters=chapters,
                support=[p for p in files if p not in chapters+["README.md"]],
                first_diagram=None, diagram_note="")
    for name in ["README.md"]+chapters:
        svgs = [s for s in IMAGE.findall((directory / name).read_text()) if s.endswith(".svg")]
        if svgs:
            item["first_diagram"] = dict(page=name, asset=svgs[0])
            break
    data["items"].append(item)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n")
    print("등록했습니다. 장 순서·지원 문서·첫 SVG 또는 생략 이유를 검토한 뒤 sync/check를 실행하세요.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sync", "register"))
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    try:
        if args.command == "register":
            if not args.path:
                raise ValueError("register에는 자료 경로가 필요합니다")
            register(ROOT, args.path)
            return 0
        errors, count = run(ROOT, args.command == "sync")
        for error in errors:
            print("ERROR:", error)
        if errors:
            return 1
        print(f"PASS: 문서 구조 확인 ({count}개 갱신)" if args.command == "sync" else "PASS: 문서 구조 확인")
        return 0
    except (ValueError, KeyError, OSError, TypeError) as error:
        print("ERROR:", error)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
