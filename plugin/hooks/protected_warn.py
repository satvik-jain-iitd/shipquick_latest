#!/usr/bin/env python3
"""PreToolUse (Edit|Write): warn when a protected path is edited in auto mode (story #321, A5b).

Reads the protected-paths list that review_merge.sh judges by in auto mode (the vendored copy under
knowledge/shipquick_latest in a child, else scripts/ in ShipQuick), and matches the
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
    # The edited file's own checkout is the root: a coder edits in a git worktree, and CLAUDE_PROJECT_DIR
    # names the session's checkout (the main one), which would turn the worktree path into a non-match.
    top = _git_dirs(Path(file_path).parent)[0] if file_path else None
    top = top or _git_dirs(base)[0]
    root = Path(top or base).resolve()
    rel = None
    if file_path:
        try:
            rel = Path(file_path).resolve().relative_to(root).as_posix()
        except ValueError:
            rel = None   # outside this repo: nothing to warn about
    # A child reads the list it is judged by: the vendored ShipQuick copy. ShipQuick reads its own.
    vendored = root / "knowledge" / "shipquick_latest" / "scripts" / "protected_paths.txt"
    listed = vendored if vendored.is_file() else root / "scripts" / "protected_paths.txt"
    if rel and listed.is_file() and current_mode(str(root)) == "auto":
        for line in listed.read_text(encoding="utf-8").splitlines():
            pat = line.split("#", 1)[0].strip()
            if pat and fnmatch.fnmatchcase(rel, pat):
                msg = "protected path, owner merges: " + rel
                # additionalContext reaches the model; systemMessage shows only in the UI. No permissionDecision: never blocks.
                print(json.dumps({"systemMessage": msg, "hookSpecificOutput": {
                    "hookEventName": "PreToolUse", "additionalContext": msg}}))
                break
except Exception:
    pass
sys.exit(0)
