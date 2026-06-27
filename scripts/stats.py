#!/usr/bin/env python3
"""
Operational Wiki 统计 — 输出页面计数和覆盖度指标。

Usage:
    python stats.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw [--json]
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


def count_evidence(text: str) -> int:
    """Count evidence entries (non-empty lines starting with - in ## Evidence)."""
    match = re.search(r"## Evidence\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if not match:
        return 0
    count = 0
    for line in match.group(1).splitlines():
        if line.strip().startswith("- ") and "source=[[" in line:
            count += 1
    return count


def get_stats(wiki_dir: Path, raw_dir: Path) -> dict:
    counts: dict[str, int] = {}
    concepts: list[dict] = []
    sources: list[dict] = []

    for dirname in CONTENT_DIRS:
        base = wiki_dir / dirname
        if base.exists():
            pages = sorted(base.rglob("*.md"))
            counts[dirname] = len(pages)

            for page in pages:
                fm, body = parse_frontmatter(page)
                if dirname == "concepts" and fm:
                    evidence_count = count_evidence(body)
                    concepts.append(
                        {
                            "file": str(page.relative_to(wiki_dir)),
                            "title": fm.get("title", page.stem),
                            "maturity": fm.get("maturity", ""),
                            "evidence_count": evidence_count,
                        }
                    )
                elif dirname == "sources" and fm:
                    sources.append(
                        {
                            "file": str(page.relative_to(wiki_dir)),
                            "title": fm.get("title", page.stem),
                            "source_kind": fm.get("source_kind", ""),
                            "has_raw_hash": "raw_hash" in fm,
                        }
                    )

    # Raw files count
    raw_files = 0
    if raw_dir.exists():
        raw_files = sum(1 for f in raw_dir.rglob("*") if f.is_file())

    # Maturity breakdown
    maturity_breakdown = {"stub": 0, "partial": 0, "mature": 0, "unlabeled": 0}
    for c in concepts:
        m = c["maturity"]
        if m in maturity_breakdown:
            maturity_breakdown[m] += 1
        else:
            maturity_breakdown["unlabeled"] += 1

    # Concepts with zero evidence
    stubs = [c for c in concepts if c["evidence_count"] == 0]
    well_evidenced = [c for c in concepts if c["evidence_count"] >= 4]

    return {
        "counts": {
            "sources": counts.get("sources", 0),
            "concepts": counts.get("concepts", 0),
            "tools": counts.get("tools", 0),
            "apis": counts.get("apis", 0),
            "analyses": counts.get("analyses", 0),
            "raw_files": raw_files,
        },
        "maturity": maturity_breakdown,
        "orphan_concepts": len(stubs),
        "orphan_concept_list": [c["title"] for c in stubs],
        "well_evidenced_concepts": len(well_evidenced),
        "well_evidenced_list": [c["title"] for c in well_evidenced],
        "sources_without_hash": len([s for s in sources if not s["has_raw_hash"]]),
        "concepts_detail": concepts,
        "sources_detail": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Wiki statistics")
    parser.add_argument("--wiki-dir", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--json", action="store_true", dest="output_json")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir).resolve()
    raw_dir = Path(args.raw_dir).resolve()

    if not wiki_dir.exists():
        print(f"Error: wiki dir not found: {wiki_dir}", file=sys.stderr)
        return 2

    stats = get_stats(wiki_dir, raw_dir)

    if args.output_json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    c = stats["counts"]
    m = stats["maturity"]
    print("=== Wiki Stats ===")
    print(f"Sources:  {c['sources']}")
    print(f"Concepts: {c['concepts']}")
    print(f"Tools:    {c['tools']}")
    print(f"APIs:     {c['apis']}")
    print(f"Analyses: {c['analyses']}")
    print(f"Raw:      {c['raw_files']}")
    print()
    print("=== Concept Maturity ===")
    print(f"stub:      {m['stub']}")
    print(f"partial:   {m['partial']}")
    print(f"mature:    {m['mature']}")
    print(f"unlabeled: {m['unlabeled']}")
    print(f"(orphan {stats['orphan_concepts']} / well-evidenced {stats['well_evidenced_concepts']})")

    if stats["orphan_concepts"]:
        print()
        print("Orphan concepts (zero evidence):")
        for name in stats["orphan_concept_list"]:
            print(f"  - {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
