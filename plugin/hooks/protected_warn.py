#!/usr/bin/env python3
"""PreToolUse (Edit|Write): warn when a protected path is edited in auto mode (story #321, A5b).

Reads scripts/protected_paths.txt, the list review_merge.sh refuses in auto mode, and matches the
edited file with the same glob rule (bash [[ == ]]: `*` crosses `/`). Prints a warning only in auto
mode; it never blocks, and any error prints nothing. Exit 0 always.
"""
import fnmatch
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from common import _git_dirs, current_mode, read_payload

    payload = read_payload()
    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    base = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    top, _ = _git_dirs(base)
    root = Path(top or base).resolve()
    rel = None
    if file_path:
        try:
            rel = Path(file_path).resolve().relative_to(root).as_posix()
        except ValueError:
            rel = None   # outside this repo: nothing to warn about
    listed = root / "scripts" / "protected_paths.txt"
    # shortcut: reads the project's own list only; a child that vendors ShipQuick gets no warning until it is adopted (add the knowledge/shipquick_latest path when that matters)
    if rel and listed.is_file() and current_mode(base) == "auto":
        for line in listed.read_text(encoding="utf-8").splitlines():
            pat = line.split("#", 1)[0].strip()
            if pat and fnmatch.fnmatchcase(rel, pat):
                print(json.dumps({"systemMessage": "protected path, owner merges: " + rel}))
                break
except Exception:
    pass
sys.exit(0)
