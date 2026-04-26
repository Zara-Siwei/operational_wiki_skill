#!/usr/bin/env python3
"""
Segment a large Markdown or HTML source into heading-based chunks.

Usage:
    python segment_source.py <path> [--max-chars 8000] [--json-out out.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_html(raw: str) -> str:
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</(p|div|section|article|li|ul|ol|table|tr|h[1-6])>", "\n", raw, flags=re.IGNORECASE)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return clean_text(unescape(raw))


def segment_markdown(text: str) -> list[dict]:
    sections: list[dict] = []
    current = {"title": "Document Start", "level": 0, "text_parts": []}
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            if current["text_parts"]:
                sections.append(
                    {
                        "title": current["title"],
                        "level": current["level"],
                        "text": clean_text("\n".join(current["text_parts"])),
                    }
                )
            current = {"title": match.group(2).strip(), "level": len(match.group(1)), "text_parts": []}
        else:
            current["text_parts"].append(line)
    if current["text_parts"]:
        sections.append(
            {
                "title": current["title"],
                "level": current["level"],
                "text": clean_text("\n".join(current["text_parts"])),
            }
        )
    return [s for s in sections if s["text"]]


def segment_html(text: str) -> list[dict]:
    tokens = re.split(r"(<h[1-6][^>]*>.*?</h[1-6]>)", text, flags=re.IGNORECASE | re.DOTALL)
    sections: list[dict] = []
    current_title = "Document Start"
    current_level = 0
    current_parts: list[str] = []
    for token in tokens:
        heading = re.match(r"<h([1-6])[^>]*>(.*?)</h\1>", token, flags=re.IGNORECASE | re.DOTALL)
        if heading:
            if current_parts:
                sections.append(
                    {
                        "title": clean_text(strip_html(current_title)),
                        "level": current_level,
                        "text": clean_text(strip_html(" ".join(current_parts))),
                    }
                )
            current_level = int(heading.group(1))
            current_title = heading.group(2)
            current_parts = []
        else:
            current_parts.append(token)
    if current_parts:
        sections.append(
            {
                "title": clean_text(strip_html(current_title)),
                "level": current_level,
                "text": clean_text(strip_html(" ".join(current_parts))),
            }
        )
    return [s for s in sections if s["text"]]


def chunk_sections(sections: list[dict], max_chars: int) -> list[dict]:
    chunks: list[dict] = []
    for section in sections:
        text = section["text"]
        if len(text) <= max_chars:
            chunks.append(section)
            continue
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        part = 1
        current: list[str] = []
        current_len = 0
        for paragraph in paragraphs:
            extra = len(paragraph) + (2 if current else 0)
            if current and current_len + extra > max_chars:
                chunks.append({"title": f"{section['title']} (part {part})", "level": section["level"], "text": "\n\n".join(current)})
                part += 1
                current = [paragraph]
                current_len = len(paragraph)
            else:
                current.append(paragraph)
                current_len += extra
        if current:
            chunks.append(
                {
                    "title": f"{section['title']} (part {part})" if part > 1 else section["title"],
                    "level": section["level"],
                    "text": "\n\n".join(current),
                }
            )
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Segment large Markdown/HTML files.")
    parser.add_argument("path", help="Path to a Markdown or HTML file")
    parser.add_argument("--max-chars", type=int, default=8000)
    parser.add_argument("--json-out", help="Optional output JSON path")
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8", errors="ignore")
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown", ".mdx", ".txt", ".rst"}:
        sections = segment_markdown(text)
    elif suffix in {".html", ".htm"}:
        sections = segment_html(text)
    else:
        print(f"Unsupported suffix: {suffix}", file=sys.stderr)
        return 2

    chunks = chunk_sections(sections, args.max_chars)
    payload = {
        "path": str(path),
        "size_chars": len(text),
        "section_count": len(sections),
        "chunk_count": len(chunks),
        "chunks": [
            {"index": idx, "title": chunk["title"], "level": chunk["level"], "chars": len(chunk["text"]), "preview": chunk["text"][:220]}
            for idx, chunk in enumerate(chunks, start=1)
        ],
    }

    if args.json_out:
        out_path = Path(args.json_out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
