"""Story #315 (A12): the loop and cost guard of the ShipQuick plugin.

`python3 guard.py post` (PostToolUse, every tool) records the call and warns when the last 5 calls
were identical, or when the session cost is over the warn line.
`python3 guard.py pre` (PreToolUse, Edit, Write and Bash) denies a call that would repeat the last 5
identical calls, and any call while the session cost is over the block line.

Calls are identical when the tool name and the sha256 of the input JSON are the same. The cost is
summed from the usage records of the transcript file (transcript_path in the hook payload).
Any error prints nothing and exits 0, so a broken guard never blocks a session (as in common.py).
"""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from common import read_payload

# shortcut: list prices typed here in dollars per million tokens, checked by hand once a year, upgrade to a pricing file when more models are used. Unknown models price as sonnet, the higher guess.
RATES = {
    "haiku": {"input": 1.0, "output": 5.0, "cache_write": 1.25, "cache_read": 0.10},
    "sonnet": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30},
}
WINDOW = 5
DEFAULT_WARN = 2.0
DEFAULT_BLOCK = 4.0
LOOP_TEXT = "loop: the same call 5 times"


def threshold(name, default):
    try:
        return float(os.environ.get(name) or default)
    except ValueError:
        return default


def _number(usage, key):
    try:
        return int(usage.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def rate_for(model):
    return RATES["haiku"] if "haiku" in str(model or "").lower() else RATES["sonnet"]


def session_cost(transcript_path):
    """Dollars spent so far in the transcript. The whole file is read on every call."""
    # shortcut: the whole transcript is read on every tool call, upgrade to a byte offset when a transcript passes a few MB.
    if not transcript_path:
        return 0.0
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return 0.0
    total, seen = 0.0, set()
    for line in lines:
        try:
            msg = json.loads(line).get("message")
        except (ValueError, AttributeError):
            continue
        if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
            continue
        msg_id = msg.get("id")
        if msg_id and msg_id in seen:   # one API reply can be written as several lines with the same usage
            continue
        seen.add(msg_id)
        u, r = msg["usage"], rate_for(msg.get("model"))
        total += (_number(u, "input_tokens") * r["input"] + _number(u, "output_tokens") * r["output"]
                  + _number(u, "cache_creation_input_tokens") * r["cache_write"]
                  + _number(u, "cache_read_input_tokens") * r["cache_read"]) / 1_000_000
    return total


def call_key(payload):
    body = json.dumps(payload.get("tool_input"), sort_keys=True, default=str)
    return f"{payload.get('tool_name') or ''}:{hashlib.sha256(body.encode('utf-8')).hexdigest()}"


def state_path(session):
    folder = Path(os.environ.get("SHIPQUICK_GUARD_DIR") or Path(tempfile.gettempdir()) / "shipquick-guard")
    safe = "".join(c for c in session if c.isalnum() or c in "-_")[:120] or "nosession"
    return folder / f"{safe}.json"


def load_calls(path):
    try:
        calls = json.loads(path.read_text(encoding="utf-8")).get("calls")
    except (OSError, ValueError, AttributeError):
        return []
    return [c for c in calls if isinstance(c, str)] if isinstance(calls, list) else []


def save_calls(path, calls):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"calls": calls[-WINDOW:]}), encoding="utf-8")


def is_loop(calls):
    return len(calls) >= WINDOW and len(set(calls[-WINDOW:])) == 1


def emit(event, decision=None, reason=None, warning=None):
    if decision:
        out = {"hookSpecificOutput": {"hookEventName": event, "permissionDecision": decision,
                                      "permissionDecisionReason": reason}}
    else:
        out = {"systemMessage": warning,
               "hookSpecificOutput": {"hookEventName": event, "additionalContext": warning}}
    print(json.dumps(out))


def cost_line(cost, warn, block):
    if cost > block:
        return f"cost: session is ${cost:.2f}, over the block line ${block:.2f}"
    return f"cost: session is ${cost:.2f}, over the warn line ${warn:.2f}"


def main(argv):
    event = argv[1] if len(argv) > 1 else ""
    payload = read_payload()
    path = state_path(str(payload.get("session_id") or "nosession"))
    key = call_key(payload)
    warn_at = threshold("SHIPQUICK_COST_WARN", DEFAULT_WARN)
    block_at = threshold("SHIPQUICK_COST_BLOCK", DEFAULT_BLOCK)
    calls = load_calls(path)
    cost = session_cost(payload.get("transcript_path"))
    if event == "pre":
        if len(calls) >= WINDOW and all(c == key for c in calls[-WINDOW:]):
            emit("PreToolUse", "deny", f"{LOOP_TEXT} in a row. This call is stopped; change the input or the approach.")
        elif cost > block_at:
            emit("PreToolUse", "deny", f"{cost_line(cost, warn_at, block_at)}. This call is stopped.")
        return
    if event == "post":
        calls = calls + [key]
        save_calls(path, calls)
        notes = []
        if is_loop(calls):
            notes.append(f"{LOOP_TEXT} in a row ({payload.get('tool_name') or 'tool'}).")
        if cost > warn_at:
            notes.append(cost_line(cost, warn_at, block_at) + ".")
        if notes:
            emit("PostToolUse", warning=" ".join(notes))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:   # the guard never blocks on its own error
        pass
    sys.exit(0)
