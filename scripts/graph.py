#!/usr/bin/env python3
"""
Operational Wiki 关系图谱 — 从 typed relations 生成 Mermaid 图。

Usage:
    python graph.py --wiki-dir /path/to/kb/wiki [--focus concept-name] [--output graph.md]
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

CONTENT_DIRS = ["sources", "concepts", "tools", "apis", "analyses"]

TYPE_COLORS = {
    "source": "#e8d5b7",
    "concept": "#c8e6c9",
    "tool": "#bbdefb",
    "api": "#f3e5f5",
    "analysis": "#ffe0b2",
}

MATURITY_COLORS = {
    "stub": "#eeeeee",
    "partial": "#fff9c4",
    "mature": "#c8e6c9",
}


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


def get_all_pages(wiki_dir: Path) -> list[Path]:
    pages: list[Path] = []
    for dirname in CONTENT_DIRS:
        base = wiki_dir / dirname
        if base.exists():
            pages.extend(sorted(base.rglob("*.md")))
    return sorted(pages)


def build_page_index(pages: list[Path], wiki_dir: Path) -> dict[str, dict]:
    """Build a lookup: page_stem -> {rel, title, type, maturity}."""
    index: dict[str, dict] = {}
    for page in pages:
        fm, _ = parse_frontmatter(page)
        rel = str(page.relative_to(wiki_dir))
        stem = page.stem
        index[stem] = {
            "rel": rel,
            "title": fm.get("title", stem) if fm else stem,
            "type": fm.get("type", "unknown") if fm else "unknown",
            "maturity": fm.get("maturity", "") if fm else "",
        }
    return index


def extract_relations(page: Path) -> list[tuple[str, str, str]]:
    """Extract typed relations: (source_stem, relation_type, target_stem)."""
    text = page.read_text(encoding="utf-8")
    source_stem = page.stem
    relations: list[tuple[str, str, str]] = []

    # Find ## Related section
    match = re.search(r"## Related\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if not match:
        return relations

    for line in match.group(1).splitlines():
        line = line.strip()
        rel_match = re.match(r"- ([a-z_]+): \[\[([^\]|]+)(?:\|[^\]]+)?\]\]", line)
        if rel_match:
            relations.append((source_stem, rel_match.group(1), rel_match.group(2)))

    return relations


def build_node_id(stem: str) -> str:
    """Mermaid-safe node ID."""
    return stem.replace("-", "_")


def generate_mermaid(
    pages: list[Path],
    wiki_dir: Path,
    focus: str | None = None,
) -> str:
    """Generate Mermaid flowchart from typed relations."""
    page_index = build_page_index(pages, wiki_dir)

    # Collect all relations
    all_relations: list[tuple[str, str, str]] = []
    for page in pages:
        all_relations.extend(extract_relations(page))

    # Deduplicate
    all_relations = list(set(all_relations))

    # Determine visible nodes
    visible: set[str] = set()
    if focus:
        focus_stem = focus.rsplit("/", 1)[-1].replace(".md", "")
        if focus_stem not in page_index:
            # Try matching by title substring
            for stem, info in page_index.items():
                if focus.lower() in info["title"].lower():
                    focus_stem = stem
                    break
        visible.add(focus_stem)
        for src, rel_type, tgt in all_relations:
            if src == focus_stem or tgt == focus_stem:
                visible.add(src)
                visible.add(tgt)
    else:
        for src, rel_type, tgt in all_relations:
            visible.add(src)
            visible.add(tgt)

    # Group visible nodes by type
    groups: dict[str, list[str]] = {}
    for stem in visible:
        info = page_index.get(stem)
        if not info:
            continue
        ptype = info["type"]
        groups.setdefault(ptype, []).append(stem)

    lines: list[str] = []
    lines.append("```mermaid")
    lines.append("graph LR")

    # Helper: escape special chars in labels
    def esc(s: str) -> str:
        return s.replace('"', "&quot;").replace("\n", " ")

    # Node style definitions
    for ptype, stems in groups.items():
        lines.append(f"  %% --- {ptype} ---")
        for stem in stems:
            info = page_index[stem]
            node_id = build_node_id(stem)
            title = esc(info["title"])
            maturity = info.get("maturity", "")

            # Style by maturity for concepts, by type otherwise
            if ptype == "concept" and maturity:
                color = MATURITY_COLORS.get(maturity, "#eeeeee")
                tag = f" ({maturity})"
            else:
                color = TYPE_COLORS.get(ptype, "#ffffff")
                tag = ""

            lines.append(f'  {node_id}["{title}{tag}"]')
            lines.append(f"  style {node_id} fill:{color}")

    lines.append("")

    # Edge definitions
    label_abbrev = {
        "explained_by": "in",
        "implemented_by": "impl",
        "implemented_in": "impl",
        "documented_in": "doc",
        "documents": "doc",
        "exposes": "api",
        "uses": "use",
        "depends_on": "dep",
        "compares_with": "cf",
        "see_also": "see",
        "evidence_for": "ev",
    }

    edge_count = 0
    for src, rel_type, tgt in all_relations:
        if src not in visible or tgt not in visible:
            continue
        src_id = build_node_id(src)
        tgt_id = build_node_id(tgt)
        label = label_abbrev.get(rel_type, rel_type[:4])
        lines.append(f"  {src_id} -- {label} --> {tgt_id}")
        edge_count += 1

    lines.append("```")

    header = f"# Wiki 关系图谱  \n"
    if focus:
        header += f"> Focus: {focus}  \n"
    header += f"> {len(visible)} nodes, {edge_count} edges  \n\n"
    return header + "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate wiki relation graph")
    parser.add_argument("--wiki-dir", required=True, help="Path to wiki directory")
    parser.add_argument("--focus", help="Focus on a specific concept name or page stem")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir).resolve()
    if not wiki_dir.exists():
        print(f"Error: wiki directory not found: {wiki_dir}", file=sys.stderr)
        return 2

    pages = get_all_pages(wiki_dir)
    if not pages:
        print("No pages found.", file=sys.stderr)
        return 1

    mermaid = generate_mermaid(pages, wiki_dir, args.focus)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(mermaid, encoding="utf-8")
        print(f"Graph saved to {out_path}")
    else:
        print(mermaid)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
