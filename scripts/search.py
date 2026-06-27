#!/usr/bin/env python3
"""
Operational Wiki 全文搜索。

Usage:
    python search.py --wiki-dir /path/to/kb/wiki "query" [--type concept] [--limit 10] [--json]
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
ROOT_PAGES = ["overview.md", "conventions.md"]


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
    for name in ROOT_PAGES:
        path = wiki_dir / name
        if path.exists():
            pages.append(path)
    for dirname in CONTENT_DIRS:
        base = wiki_dir / dirname
        if base.exists():
            pages.extend(sorted(base.rglob("*.md")))
    return sorted(pages)


def find_section(text: str, line_idx: int) -> str:
    """Walk backwards from line_idx to find the nearest ## heading."""
    lines = text.splitlines()
    for i in range(line_idx, -1, -1):
        if re.match(r"^##\s+", lines[i]):
            return lines[i].lstrip("#").strip()
    return "(top)"


def extract_snippet(text: str, line_idx: int, query_lower: str, window: int = 60) -> str:
    """Extract a snippet around a matching line."""
    lines = text.splitlines()
    match_line = lines[line_idx]
    pos = match_line.lower().find(query_lower)
    if pos >= 0:
        start = max(0, pos - window)
        end = min(len(match_line), pos + len(query_lower) + window)
        snippet = match_line[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(match_line):
            snippet = snippet + "..."
        return snippet
    # Fallback: just return the line truncated
    return match_line[: window * 2]


def score_match(filepath: Path, fm: dict | None, body: str, query_lower: str) -> tuple[float, list[dict]]:
    """Score a page against query and return matches with snippets."""
    score = 0.0
    matches: list[dict] = []

    # Title match (exact substring)
    if fm and fm.get("title", "").lower().find(query_lower) >= 0:
        score += 3.0
        matches.append({"section": "title", "snippet": fm["title"], "weight": 3.0})

    # Alias match
    if fm and fm.get("aliases"):
        for alias in fm["aliases"]:
            if query_lower in alias.lower():
                score += 2.0
                matches.append({"section": "alias", "snippet": alias, "weight": 2.0})

    # Frontmatter tags match
    if fm and fm.get("tags"):
        for tag in fm["tags"]:
            if query_lower in tag.lower():
                score += 1.5
                matches.append({"section": "tag", "snippet": f"tag: {tag}", "weight": 1.5})

    # Body: search line by line
    lines = body.splitlines()
    evidence_section = False
    for i, line in enumerate(lines):
        # Track if we're in an Evidence section
        if re.match(r"^## Evidence\b", line):
            evidence_section = True
            continue
        elif re.match(r"^## ", line) and not re.match(r"^## Evidence\b", line):
            evidence_section = False

        if query_lower in line.lower():
            section = find_section(body, i)
            snippet = extract_snippet(body, i, query_lower)

            if evidence_section:
                w = 1.5
                label = "evidence"
            elif re.match(r"^## ", line):
                w = 1.2
                label = "heading"
            else:
                w = 1.0
                label = "body"

            score += w
            # Avoid duplicates within same section
            if not any(m["section"] == section for m in matches):
                matches.append({"section": section, "snippet": snippet, "weight": w})

    return score, matches


def search(wiki_dir: Path, query: str, page_type: str | None = None, limit: int = 10) -> dict:
    """Search all wiki pages and return ranked results."""
    query_lower = query.lower()
    pages = get_all_pages(wiki_dir)
    results: list[dict] = []

    for page in pages:
        rel = str(page.relative_to(wiki_dir))
        fm, body = parse_frontmatter(page)

        # Type filter
        if page_type and fm and fm.get("type") != page_type:
            continue

        # Skip index/log pages from content dirs
        is_special = page.parent == wiki_dir and page.stem in {"index", "log"}
        if is_special:
            continue

        score, matches = score_match(page, fm, body, query_lower)
        if score > 0:
            page_type_val = fm.get("type", "unknown") if fm else "unknown"
            title = fm.get("title", page.stem) if fm else page.stem
            results.append(
                {
                    "file": rel,
                    "title": title,
                    "type": page_type_val,
                    "score": round(score, 2),
                    "matches": matches[:10],  # top 10 matches per page
                }
            )

    # Sort by score descending
    results.sort(key=lambda r: r["score"], reverse=True)
    results = results[:limit]

    return {
        "query": query,
        "total_pages_searched": len(pages),
        "results_found": len(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Operational Wiki full-text search")
    parser.add_argument("--wiki-dir", required=True, help="Path to wiki directory")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--type", dest="page_type", help="Filter by page type (concept, tool, api, source, analysis)")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default 10)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output JSON only")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir).resolve()
    if not wiki_dir.exists():
        print(f"Error: wiki directory not found: {wiki_dir}", file=sys.stderr)
        return 2

    result = search(wiki_dir, args.query, args.page_type, args.limit)

    if args.output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    # Human-readable output
    print(f"Search: \"{result['query']}\" — {result['results_found']} results (searched {result['total_pages_searched']} pages)")
    if args.page_type:
        print(f"Filter: type={args.page_type}")
    print()
    for r in result["results"]:
        print(f"  [{r['type'].upper()}] {r['title']} (score: {r['score']})")
        print(f"         {r['file']}")
        for m in r["matches"][:3]:
            print(f"         [{m['section']}] {m['snippet'][:100]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
