"""Story #315 (A12): the loop and cost guard of the ShipQuick plugin.

`python3 guard.py post` (PostToolUse, every tool) records the call and warns when the last 5 calls
were identical, or when the session cost is over the warn line.
`python3 guard.py pre` (PreToolUse, Edit, Write and Bash) denies a call that would repeat the last 5
identical calls when the tool is Edit or Write (a Bash poll only warns, in post), and any call while
the session cost is over the block line.

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

# shortcut: list prices typed here in dollars per million tokens, checked by hand once a year, upgrade to a pricing file when more models are used. Unknown models price as sonnet.
RATES = {
    "haiku": {"input": 1.0, "output": 5.0, "cache_write": 1.25, "cache_read": 0.10},
    "sonnet": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30},
    "opus": {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.5},
}
WINDOW = 5
SEEN = 20      # message ids kept for the duplicate check; a repeated line sits next to its first one
CHUNK = 8 * 1024 * 1024   # shortcut: at most 8 MB of transcript is read per hook call, the rest on later calls; upgrade to a cost file when a session passes several hundred MB
DEFAULT_WARN = 2.0
DEFAULT_BLOCK = 4.0
LOOP_TEXT = "loop: the same call 5 times"
LOOP_DENY_TOOLS = ("Edit", "Write")   # Bash polls (CI checks) repeat on purpose; they only warn in post


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
    name = str(model or "").lower()
    for family in ("opus", "haiku"):
        if family in name:
            return RATES[family]
    return RATES["sonnet"]


def session_cost(transcript_path, state):
    """(dollars, state). Reads only the whole lines after the saved offset, at most CHUNK bytes per call.
    The state keeps the offset, the running total and the last message ids, so the file is never re-read."""
    state = dict(state or {})
    if not transcript_path:
        return 0.0, state
    try:
        size = os.path.getsize(transcript_path)
        offset = int(state.get("offset") or 0)
        total = float(state.get("total") or 0.0)
        seen = list(state.get("seen") or [])
        if offset > size:   # the transcript was cut or replaced: count it again from the start
            offset, total, seen = 0, 0.0, []
        with open(transcript_path, "rb") as f:
            f.seek(offset)
            data = f.read(min(CHUNK, size - offset))
    except (OSError, ValueError, TypeError):
        return 0.0, state
    nl = data.rfind(b"\n")
    if nl >= 0:
        end = nl + 1
    elif len(data) == CHUNK:   # one line longer than the chunk: skip it
        end = CHUNK
    else:                      # the last line is still being written: wait for its newline
        end = 0
    for line in data[:end].splitlines():
        try:
            msg = json.loads(line).get("message")
        except (ValueError, AttributeError):
            continue
        if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
            continue
        msg_id = msg.get("id")
        if msg_id and msg_id in seen:   # one API reply can be written as several lines with the same usage
            continue
        if msg_id:
            seen.append(msg_id)
        u, r = msg["usage"], rate_for(msg.get("model"))
        total += (_number(u, "input_tokens") * r["input"] + _number(u, "output_tokens") * r["output"]
                  + _number(u, "cache_creation_input_tokens") * r["cache_write"]
                  + _number(u, "cache_read_input_tokens") * r["cache_read"]) / 1_000_000
    state.update({"offset": offset + end, "total": total, "seen": seen[-SEEN:]})
    return total, state


def call_key(payload):
    body = json.dumps(payload.get("tool_input"), sort_keys=True, default=str)
    return f"{payload.get('tool_name') or ''}:{hashlib.sha256(body.encode('utf-8')).hexdigest()}"


def state_path(session):
    folder = Path(os.environ.get("SHIPQUICK_GUARD_DIR") or Path(tempfile.gettempdir()) / "shipquick-guard")
    safe = "".join(c for c in session if c.isalnum() or c in "-_")[:120] or "nosession"
    return folder / f"{safe}.json"


def load_state(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_calls(state):
    calls = state.get("calls")
    return [c for c in calls if isinstance(c, str)] if isinstance(calls, list) else []


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**state, "calls": load_calls(state)[-WINDOW:]}), encoding="utf-8")


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
    state = load_state(path)
    calls = load_calls(state)
    transcript = payload.get("transcript_path")
    if event == "pre":
        looped = len(calls) >= WINDOW and all(c == key for c in calls[-WINDOW:])
        if looped and payload.get("tool_name") in LOOP_DENY_TOOLS:
            emit("PreToolUse", "deny", f"{LOOP_TEXT} in a row. This call is stopped; change the input or the approach.")
            return
        cost, state = session_cost(transcript, state)
        save_state(path, {**state, "calls": calls})
        if cost > block_at:
            emit("PreToolUse", "deny", f"{cost_line(cost, warn_at, block_at)}. This call is stopped.")
        return
    if event == "post":
        calls = (calls + [key])[-WINDOW:]
        save_state(path, {**state, "calls": calls})   # the call is recorded before the cost is read
        cost, state = session_cost(transcript, state)
        notes = []
        if is_loop(calls):
            notes.append(f"{LOOP_TEXT} in a row ({payload.get('tool_name') or 'tool'}).")
        warned = state.get("warned")   # the last whole dollar the cost warning was printed at
        if cost > warn_at and (warned is None or int(cost) > warned):
            notes.append(cost_line(cost, warn_at, block_at) + ".")
            state["warned"] = int(cost)
        save_state(path, {**state, "calls": calls})
        if notes:
            emit("PostToolUse", warning=" ".join(notes))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:   # the guard never blocks on its own error
        pass
    sys.exit(0)
