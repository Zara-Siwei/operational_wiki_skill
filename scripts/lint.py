#!/usr/bin/env python3
"""
Operational Wiki deterministic lint.

Usage:
    python lint.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw
    python lint.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REQUIRED_FRONTMATTER = {"title", "type", "created", "updated", "tags"}
VALID_TYPES = {"source", "concept", "tool", "api", "analysis", "overview", "conventions"}
SPECIAL_PAGES = {"index.md", "log.md"}
RELATED_RELATIONS = {
    "documents",
    "explained_by",
    "implements",
    "implemented_by",
    "documented_in",
    "exposes",
    "uses",
    "depends_on",
    "compares_with",
    "see_also",
    "evidence_for",
}

WIKI_DIR: Path
RAW_DIR: Path


def parse_frontmatter(filepath: Path) -> tuple[dict | None, str]:
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?\n)---\n(.*)", text, re.DOTALL)
    if not match:
        return None, text
    try:
        fm = yaml.safe_load(match.group(1))
        return fm if isinstance(fm, dict) else None, match.group(2)
    except yaml.YAMLError:
        return None, text


def extract_wikilinks(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)


def resolve_wikilink(target: str) -> Path | None:
    for subdir in ["sources", "concepts", "tools", "apis", "analyses", ""]:
        candidate = WIKI_DIR / subdir / f"{target}.md" if subdir else WIKI_DIR / f"{target}.md"
        if candidate.exists():
            return candidate
    return None


def get_wiki_pages() -> list[Path]:
    return sorted([p for p in WIKI_DIR.rglob("*.md") if p.name not in SPECIAL_PAGES])


def check_broken_links(pages: list[Path]) -> list[dict]:
    issues = []
    all_ids = {p.stem for p in pages}
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for target in extract_wikilinks(text):
            if target.startswith("raw/"):
                continue
            if target not in all_ids:
                issues.append({"level": "P0", "type": "broken_link", "file": str(page.relative_to(WIKI_DIR)), "detail": f"[[{target}]] 指向不存在的页面"})
    return issues


def check_raw_wikilinks(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for match in re.findall(r"\[\[(raw/[^\]|]+)(?:\|[^\]]+)?\]\]", text):
            issues.append({"level": "P0", "type": "raw_wikilink", "file": str(page.relative_to(WIKI_DIR)), "detail": f"[[{match}]] 应改为普通 Markdown 链接"})
    return issues


def check_frontmatter(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        rel = str(page.relative_to(WIKI_DIR))
        fm, _ = parse_frontmatter(page)
        if fm is None:
            issues.append({"level": "P0", "type": "no_frontmatter", "file": rel, "detail": "缺少 YAML frontmatter"})
            continue
        missing = REQUIRED_FRONTMATTER - set(fm.keys())
        if missing:
            issues.append({"level": "P0", "type": "incomplete_frontmatter", "file": rel, "detail": f"缺少字段: {', '.join(sorted(missing))}"})
        if fm.get("type") and fm["type"] not in VALID_TYPES:
            issues.append({"level": "P1", "type": "invalid_type", "file": rel, "detail": f"type '{fm['type']}' 不在合法值 {VALID_TYPES} 中"})
        if fm.get("type") == "source":
            for field in ("source_kind", "raw_path"):
                if field not in fm:
                    issues.append({"level": "P1", "type": "source_metadata_missing", "file": rel, "detail": f"source 页面缺少 {field}"})
        if fm.get("type") in ("tool", "api", "concept") and not fm.get("sources"):
            issues.append({"level": "P1", "type": "missing_sources", "file": rel, "detail": f"type={fm.get('type')} 缺少 sources 字段"})
        if fm.get("type") == "tool" and "tool_kind" not in fm:
            issues.append({"level": "P1", "type": "tool_metadata_missing", "file": rel, "detail": "tool 页面缺少 tool_kind"})
        if fm.get("type") == "api":
            for field in ("api_kind", "api_path"):
                if field not in fm:
                    issues.append({"level": "P1", "type": "api_metadata_missing", "file": rel, "detail": f"api 页面缺少 {field}"})
    return issues


def check_index_consistency(pages: list[Path]) -> list[dict]:
    issues = []
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return [{"level": "P0", "type": "missing_index", "file": "index.md", "detail": "index.md 不存在"}]
    index_text = index_path.read_text(encoding="utf-8")
    index_refs = set(re.findall(r"\]\(([^)]+\.md)\)", index_text))
    content_pages = set()
    for page in pages:
        rel = str(page.relative_to(WIKI_DIR))
        if any(rel.startswith(prefix) for prefix in ("sources/", "concepts/", "tools/", "apis/", "analyses/")):
            content_pages.add(rel)
    for ref in index_refs:
        if ref != "overview.md" and not (WIKI_DIR / ref).exists():
            issues.append({"level": "P0", "type": "index_dangling", "file": "index.md", "detail": f"索引引用 {ref} 但文件不存在"})
    for rel in content_pages:
        if rel not in index_refs:
            issues.append({"level": "P0", "type": "index_missing", "file": "index.md", "detail": f"文件 {rel} 存在但未在索引中列出"})
    return issues


def check_related_format(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        match = re.search(r"## Related\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
        if not match:
            continue
        for raw_line in match.group(1).splitlines():
            line = raw_line.strip()
            if not line or not line.startswith("- "):
                continue
            rel_match = re.match(r"- ([a-z_]+): \[\[([^\]|]+)(?:\|[^\]]+)?\]\](?: .*)?$", line)
            if not rel_match:
                issues.append({"level": "P1", "type": "invalid_related_format", "file": str(page.relative_to(WIKI_DIR)), "detail": f"Related 行格式无效: {line}"})
                continue
            if rel_match.group(1) not in RELATED_RELATIONS:
                issues.append({"level": "P1", "type": "unknown_related_relation", "file": str(page.relative_to(WIKI_DIR)), "detail": f"未知 relation: {rel_match.group(1)}"})
            if not resolve_wikilink(rel_match.group(2)):
                issues.append({"level": "P0", "type": "related_target_missing", "file": str(page.relative_to(WIKI_DIR)), "detail": f"Related 引用不存在: [[{rel_match.group(2)}]]"})
    return issues


def check_evidence_format(pages: list[Path]) -> list[dict]:
    issues = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        match = re.search(r"## Evidence\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
        if not match:
            continue
        for raw_line in match.group(1).splitlines():
            line = raw_line.strip()
            if not line or not line.startswith("- "):
                continue
            if "| source=[[" not in line or "| locator=" not in line:
                issues.append({"level": "P1", "type": "invalid_evidence_format", "file": str(page.relative_to(WIKI_DIR)), "detail": f"Evidence 行缺少 source 或 locator: {line}"})
                continue
            source_match = re.search(r"\| source=\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", line)
            if source_match and not resolve_wikilink(source_match.group(1)):
                issues.append({"level": "P0", "type": "missing_evidence_source", "file": str(page.relative_to(WIKI_DIR)), "detail": f"Evidence 引用的页面不存在: [[{source_match.group(1)}]]"})
    return issues


def run_all_checks() -> list[dict]:
    pages = get_wiki_pages()
    issues = []
    issues += check_broken_links(pages)
    issues += check_raw_wikilinks(pages)
    issues += check_frontmatter(pages)
    issues += check_index_consistency(pages)
    issues += check_related_format(pages)
    issues += check_evidence_format(pages)
    level_order = {"P0": 0, "P1": 1, "P2": 2}
    issues.sort(key=lambda item: (level_order.get(item["level"], 9), item["file"]))
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Operational Wiki lint")
    parser.add_argument("--wiki-dir", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--json", action="store_true", dest="output_json")
    args = parser.parse_args()

    global WIKI_DIR, RAW_DIR
    WIKI_DIR = Path(args.wiki_dir).resolve()
    RAW_DIR = Path(args.raw_dir).resolve()

    if not WIKI_DIR.exists():
        print(f"错误: wiki 目录不存在: {WIKI_DIR}", file=sys.stderr)
        raise SystemExit(2)

    issues = run_all_checks()
    if args.output_json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
        return

    pages = get_wiki_pages()
    print(f"Operational Wiki 健康检查 — {WIKI_DIR}")
    print(f"共 {len(pages)} 个页面\n")
    if not issues:
        print("✅ 未发现问题！")
        return

    p0 = [i for i in issues if i["level"] == "P0"]
    p1 = [i for i in issues if i["level"] == "P1"]

    if p0:
        print(f"🔴 P0 — 需要修复 ({len(p0)})")
        for item in p0:
            print(f"  [{item['type']}] {item['file']}: {item['detail']}")
        print()
    if p1:
        print(f"🟡 P1 — 建议改进 ({len(p1)})")
        for item in p1:
            print(f"  [{item['type']}] {item['file']}: {item['detail']}")
        print()
    print(f"总计: {len(p0)} P0 / {len(p1)} P1")
    if p0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
