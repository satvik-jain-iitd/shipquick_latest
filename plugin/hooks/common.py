"""Shared pieces of the ShipQuick plugin hooks (story #313, A2).

Every hook: read the JSON payload from stdin, print one JSON object, exit 0. On any error the hook
prints nothing and exits 0, so it never blocks a session. The rules come from rules-dense.md,
which plugin/gen_rules_dense.py writes from CLAUDE.md and CI checks for drift.

Hook layout (SessionStart + SubagentStart, hookSpecificOutput.additionalContext, one script per
hook) borrowed from DietrichGebert/ponytail hooks/ponytail-subagent.js (MIT). Recorded in
docs/research/repo-radar.md, 10 Nov 2026, story #313.
"""
import json
import os
import re
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
RULES_FILE = PLUGIN_DIR / "rules-dense.md"


def read_payload():
    try:
        data = json.loads(sys.stdin.read() or "{}")
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


MODES = ("manual", "semi", "auto")


def _git_dirs(base):
    """(top-level folder, git common dir) of the repo that holds base, or (None, None). Reads the .git entry the
    way git does and starts no process: a .git folder is its own common dir; a .git file (a worktree) points at a
    gitdir whose `commondir` file names the shared one. A git call here cost 50 to 320 ms; this costs under 1 ms."""
    try:
        here = Path(base).resolve()
        for cur in (here, *here.parents):
            entry = cur / ".git"
            if entry.is_dir():
                return cur, entry
            if entry.is_file():
                m = re.match(r"gitdir:\s*(.+)", entry.read_text(encoding="utf-8"))
                if not m:
                    return cur, None
                gitdir = Path(m.group(1).strip())
                gitdir = gitdir if gitdir.is_absolute() else cur / gitdir
                pointer = gitdir / "commondir"
                if pointer.is_file():
                    common = Path(pointer.read_text(encoding="utf-8").strip())
                    return cur, (common if common.is_absolute() else (gitdir / common).resolve())
                return cur, gitdir
    except OSError:
        pass
    return None, None


def current_mode(project_dir):
    """The mode the way scripts/mode.sh get reads it: the tracked .shipquick/mode first, then the untracked
    <git-common-dir>/shipquick-mode that every worktree shares. CLAUDE_PROJECT_DIR is preferred when set.
    Anything that is not manual, semi or auto reads as not set."""
    base = os.environ.get("CLAUDE_PROJECT_DIR") or project_dir
    top, common = _git_dirs(base)
    candidates = [(top or Path(base)) / ".shipquick" / "mode"]
    if common:
        candidates.append(common / "shipquick-mode")
    for path in candidates:
        if path.is_file():   # the first file that exists decides, as in mode.sh
            try:
                word = "".join(path.read_text(encoding="utf-8").split())
            except OSError:
                return "not set"
            return word if word in MODES else "not set"
    return "not set"


def hooks_warning(project_dir):
    """Story #446: one line when this project's git hooks are configured but not installed. Never raises."""
    try:
        from hooks_state import warning
        top, _ = _git_dirs(os.environ.get("CLAUDE_PROJECT_DIR") or project_dir)
        return warning(top or project_dir)
    except Exception:
        return ""


def context_for(event, project_dir, extra=""):
    rules = RULES_FILE.read_text(encoding="utf-8")
    text = f"ShipQuick mode: {current_mode(project_dir)}\n\n{rules}"
    if event == "SessionStart" and (warn := hooks_warning(project_dir)):
        text = f"{warn}\n\n{text}"
    if extra:  # the codebase map (story #314), SessionStart only
        text += f"\n\n{extra}"
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def emit(event, project_dir, extra=""):
    print(json.dumps(context_for(event, project_dir, extra)))
