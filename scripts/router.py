#!/usr/bin/env python3
"""Operational Wiki router."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRIES_FILE = SKILL_DIR / "registries.json"

VALID_SUBCOMMANDS = {"init", "ingest", "query", "lint", "test", "help"}
NO_KB_REQUIRED = {"init", "help"}
NEEDS_SCHEMA = {"ingest", "query", "lint"}


def load_registries() -> dict:
    if not REGISTRIES_FILE.exists():
        return {"default": None, "registries": {}}
    with open(REGISTRIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def make_kb_info(kb_id: str, kb_data: dict) -> dict:
    root = kb_data["path"]
    return {
        "id": kb_id,
        "name": kb_data["name"],
        "root": root,
        "wiki": f"{root}/wiki",
        "raw": f"{root}/raw",
        "lang": kb_data.get("language", "zh"),
    }


def route(args: list[str]) -> dict:
    if not args:
        return {
            "status": "ok",
            "subcommand": "help",
            "args": "",
            "workflow": None,
            "schema": None,
            "kb": None,
            "skill_dir": str(SKILL_DIR),
        }

    subcommand = args[0].lower()
    remaining = " ".join(args[1:]) if len(args) > 1 else ""

    if subcommand not in VALID_SUBCOMMANDS:
        return {
            "status": "error",
            "message": f"未知子命令: {subcommand}",
            "valid_subcommands": sorted(VALID_SUBCOMMANDS),
            "skill_dir": str(SKILL_DIR),
        }

    result = {
        "status": "ok",
        "subcommand": subcommand,
        "args": remaining,
        "workflow": f"workflows/{subcommand}.md" if subcommand != "help" else None,
        "schema": "SCHEMA.md" if subcommand in NEEDS_SCHEMA else None,
        "kb": None,
        "skill_dir": str(SKILL_DIR),
    }

    if subcommand in NO_KB_REQUIRED:
        return result

    registries = load_registries()
    kbs = registries.get("registries", {})

    if not kbs:
        return {
            "status": "no_kb",
            "message": "尚未注册任何知识库。请先运行 /opwiki init 创建一个知识库。",
            "skill_dir": str(SKILL_DIR),
        }

    if len(kbs) == 1:
        kb_id = next(iter(kbs))
        kb_data = kbs[kb_id]
        root = Path(kb_data["path"])
        if not root.exists():
            return {
                "status": "error",
                "message": f"知识库路径不存在: {kb_data['path']}",
                "skill_dir": str(SKILL_DIR),
            }
        result["kb"] = make_kb_info(kb_id, kb_data)
        return result

    default_id = registries.get("default")
    if default_id and default_id in kbs:
        result["kb"] = make_kb_info(default_id, kbs[default_id])
        result["multiple_kbs"] = True
        result["kb_list"] = [
            {"id": kid, "name": kd["name"], "path": kd["path"], "is_default": kid == default_id}
            for kid, kd in kbs.items()
        ]
        return result

    result["status"] = "select"
    result["message"] = "有多个知识库，请询问用户选择。"
    result["kb_list"] = [
        {"id": kid, "name": kd["name"], "path": kd["path"]}
        for kid, kd in kbs.items()
    ]
    return result


def main() -> None:
    print(json.dumps(route(sys.argv[1:]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
