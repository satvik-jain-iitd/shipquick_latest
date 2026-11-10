#!/usr/bin/env python3
"""PreToolUse (Write): warn when a new scratch markdown file is made outside docs/ (story #322, A5c).

A file named NOTES*, TODO*, SCRATCH*, DRAFT*, WIP* or TEMP* with .md, outside docs/, .claude/ and
.github/, gets a warning that names the single-source file to use instead. It never blocks: exit 0.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
PREFIXES = ("NOTES", "TODO", "SCRATCH", "DRAFT", "WIP", "TEMP")
EXEMPT_FOLDERS = ("docs", ".claude", ".github")


def target_for(file_path, cwd):
    """The warning text for a scratch file, or "" when the file is not one."""
    path = Path(file_path)
    name = path.name.upper()
    if path.suffix.lower() != ".md" or not name.startswith(PREFIXES):
        return ""
    try:
        rel = path.resolve().relative_to(Path(cwd).resolve())
    except (ValueError, OSError):
        rel = path
    if rel.parts and rel.parts[0] in EXEMPT_FOLDERS:
        return ""
    # ponytail: name prefix only, no content check; upgrade to a content check if a false hit shows up
    dest = "docs/plans/" if name.startswith("DRAFT") else "docs/follow-ups.md"
    return (f"Scratch file {path.name}: keep open work in one place. Use {dest} instead of a new "
            "markdown file, so the next session finds it.")


try:
    from common import read_payload
    payload = read_payload()
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if file_path:
        text = target_for(file_path, payload.get("cwd") or os.getcwd())
        if text:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                     "additionalContext": text}}))
except Exception:
    pass
sys.exit(0)
