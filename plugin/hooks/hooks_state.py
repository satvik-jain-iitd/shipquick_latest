#!/usr/bin/env python3
"""Story #446: are a project's ShipQuick git hooks installed? One answer for adopt.sh, its `--check` and the session-start hook.

  hooks_state.py <project-dir>   prints one word and exits
    not-configured  exit 0   no .pre-commit-config.yaml with the ShipQuick hooks (check_local.sh): nothing to install
    off             exit 0   the `pre-commit` feature is off in .shipquick/features.json: nothing to install
    installed       exit 0   the pre-commit and commit-msg hooks exist in the git hooks folder and were written by pre-commit
    missing         exit 1   configured, but a hook is not installed: run `pre-commit install`
    error           exit 2   not a git repository or git cannot run; never read as installed

Stdlib only, no ShipQuick import: the plugin runs in projects that have no kit folder. The hooks folder is asked from git, so
core.hooksPath and worktrees are honoured."""
import json
import subprocess
import sys
from pathlib import Path

NEEDED = ("pre-commit", "commit-msg")   # the two that carry the checks; commit-msg is the subject-length guard


def hooks_state(project_dir):
    top = Path(project_dir)
    cfg = top / ".pre-commit-config.yaml"
    try:
        if not cfg.is_file() or "check_local.sh" not in cfg.read_text(encoding="utf-8"):
            return "not-configured"
    except OSError:
        return "error"
    try:
        feats = json.loads((top / ".shipquick" / "features.json").read_text(encoding="utf-8"))
        if feats["features"]["pre-commit"]["on"] is False:
            return "off"
    except (OSError, ValueError, KeyError, TypeError):
        pass   # no file, or a broken one: the hooks are still wanted (the features reader reports the broken file itself)
    try:
        p = subprocess.run(["git", "-C", str(top), "rev-parse", "--git-path", "hooks"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "error"
    if p.returncode != 0 or not p.stdout.strip():
        return "error"
    folder = Path(p.stdout.strip())
    folder = folder if folder.is_absolute() else top / folder
    for name in NEEDED:
        try:
            text = (folder / name).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "missing"
        if "pre-commit" not in text:
            return "missing"
    return "installed"


FIX = "pre-commit install"


def warning(project_dir):
    """One line for the session-start hook, or an empty string."""
    if hooks_state(project_dir) != "missing":
        return ""
    return ("ShipQuick: this project's git hooks are configured but not installed, so the commit checks (subject length, "
            "format) do not run here. Fix: run `%s` in the project folder." % FIX)


if __name__ == "__main__":
    s = hooks_state(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(s)
    sys.exit({"missing": 1, "error": 2}.get(s, 0))
