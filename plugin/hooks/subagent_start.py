#!/usr/bin/env python3
"""SubagentStart: print the mode and the dense rules (story #313, A2). Exit 0 on any error."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from common import emit, read_payload
    payload = read_payload()
    emit("SubagentStart", payload.get("cwd") or os.getcwd())
except Exception:
    pass
sys.exit(0)
