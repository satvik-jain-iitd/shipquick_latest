#!/usr/bin/env python3
"""SessionStart: print the mode, the dense rules and the codebase map (stories #313 A2, #314 A9).

Exit 0 on any error: a failed map is left out, the rules still reach the session.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def codebase_map(cwd):
    try:
        from map import build_map
        return build_map(cwd)
    except Exception:
        return ""


try:
    from common import emit, read_payload
    payload = read_payload()
    cwd = payload.get("cwd") or os.getcwd()
    emit("SessionStart", cwd, codebase_map(cwd))
except Exception:
    pass
sys.exit(0)
