"""Shared pieces of the ShipQuick plugin hooks (story #313, A2).

Every hook: read the JSON payload from stdin, print one JSON object, exit 0. On any error the hook
prints nothing and exits 0, so it never blocks a session. The rules come from rules-dense.md,
which scripts/gen_rules_dense.py writes from CLAUDE.md and CI checks for drift.
"""
import json
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


def current_mode(project_dir):
    try:
        value = (Path(project_dir) / ".shipquick" / "mode").read_text(encoding="utf-8").strip()
        return value or "not set"
    except OSError:
        return "not set"


def context_for(event, project_dir):
    rules = RULES_FILE.read_text(encoding="utf-8")
    text = f"ShipQuick mode: {current_mode(project_dir)}\n\n{rules}"
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def emit(event, project_dir):
    print(json.dumps(context_for(event, project_dir)))
