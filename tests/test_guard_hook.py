"""Story #315 (A12): the loop and cost guard. A PostToolUse hook warns; a PreToolUse hook denies.

Each test runs the hook as Claude Code runs it: JSON on stdin, JSON on stdout, exit 0.
The state folder and the cost lines come from env vars, so every test stays in its own tmp_path.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
HOOKS = PLUGIN / "hooks"
GUARD = HOOKS / "guard.py"
LOOP_TEXT = "loop: the same call 5 times"
ZERO_USAGE = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}


def run_guard(event, payload, tmp_path, extra_env=None):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN), "SHIPQUICK_GUARD_DIR": str(tmp_path / "state"),
           "SHIPQUICK_COST_WARN": "", "SHIPQUICK_COST_BLOCK": "", **(extra_env or {})}
    p = subprocess.run([sys.executable, str(GUARD), event], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=tmp_path, env=env, timeout=10)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout) if p.stdout.strip() else {}


def edit_call(session, n=0, tool="Edit"):
    return {"session_id": session, "hook_event_name": "PostToolUse", "tool_name": tool,
            "tool_input": {"file_path": "docs/a.md", "old_string": "x", "new_string": f"y{n}"},
            "transcript_path": "/nonexistent/transcript.jsonl"}


def pre_call(session, n=0, transcript=None):
    payload = {**edit_call(session, n), "hook_event_name": "PreToolUse"}
    if transcript is not None:
        payload["transcript_path"] = str(transcript)
    return payload


def deny_reason(out):
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    return out["hookSpecificOutput"]["permissionDecisionReason"]


def write_transcript(path, usage_records):
    lines = [json.dumps({"type": "assistant", "message": {"model": model, "usage": usage}})
             for model, usage in usage_records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def sonnet_input(millions):
    """Sonnet input tokens: each million is one usage record of 1,000,000 tokens."""
    return ("claude-sonnet-4-5", {**ZERO_USAGE, "input_tokens": 1_000_000}) if millions == 1 else None


def test_the_hooks_file_registers_the_guard_on_post_and_pre():
    hooks = json.loads((HOOKS / "hooks.json").read_text())["hooks"]
    post = [h["command"] for m in hooks["PostToolUse"] for h in m["hooks"]]
    pre = [(m["matcher"], h["command"]) for m in hooks["PreToolUse"] for h in m["hooks"]]
    assert any("guard.py" in c and c.endswith("post") for c in post)
    assert any(match == "Edit|Write|Bash" and "guard.py" in c and c.endswith("pre") for match, c in pre)


def test_four_different_calls_are_no_loop(tmp_path):
    for n in range(4):
        out = run_guard("post", edit_call("s-four", n), tmp_path)
        assert LOOP_TEXT not in json.dumps(out)


def test_five_identical_calls_warn_loop(tmp_path):
    out = {}
    for _ in range(5):
        out = run_guard("post", edit_call("s-five"), tmp_path)
    assert LOOP_TEXT in json.dumps(out)
    assert "systemMessage" in out


def test_a_sixth_identical_call_is_denied_before_it_runs(tmp_path):
    for _ in range(5):
        run_guard("post", edit_call("s-deny"), tmp_path)
    assert LOOP_TEXT in deny_reason(run_guard("pre", pre_call("s-deny"), tmp_path))


def test_a_different_call_breaks_the_streak(tmp_path):
    for _ in range(5):
        run_guard("post", edit_call("s-break"), tmp_path)
    assert run_guard("pre", pre_call("s-break", n=9), tmp_path) == {}


def test_the_same_input_on_another_tool_is_not_a_loop(tmp_path):
    for i in range(5):
        run_guard("post", edit_call("s-tool", tool="Edit" if i % 2 else "Write"), tmp_path)
    assert LOOP_TEXT not in json.dumps(run_guard("post", edit_call("s-tool", tool="Bash"), tmp_path))


def test_under_the_warn_line_prints_nothing(tmp_path):
    haiku_half_million = ("claude-haiku-4-5", {**ZERO_USAGE, "input_tokens": 500_000})  # $0.50 at list input
    t = write_transcript(tmp_path / "small.jsonl", [haiku_half_million])
    out = run_guard("post", {**edit_call("s-under"), "transcript_path": str(t)}, tmp_path)
    assert out == {}


def test_over_the_warn_line_warns_about_cost(tmp_path):
    t = write_transcript(tmp_path / "t.jsonl", [sonnet_input(1), sonnet_input(1)])  # $6 at Sonnet input
    out = run_guard("post", {**edit_call("s-warn"), "transcript_path": str(t)}, tmp_path,
                    {"SHIPQUICK_COST_BLOCK": "100"})
    text = json.dumps(out)
    assert "cost:" in text and "warn line" in text
    assert "permissionDecision" not in text


def test_over_the_block_line_denies_edit_before_it_runs(tmp_path):
    t = write_transcript(tmp_path / "t.jsonl", [sonnet_input(1), sonnet_input(1)])  # $6
    reason = deny_reason(run_guard("pre", pre_call("s-block", transcript=t), tmp_path))
    assert "cost:" in reason and "block line" in reason


def test_the_block_line_comes_from_the_env(tmp_path):
    t = write_transcript(tmp_path / "t.jsonl", [sonnet_input(1)])  # $3
    out = run_guard("pre", pre_call("s-env", transcript=t), tmp_path, {"SHIPQUICK_COST_BLOCK": "2.5"})
    assert "block line" in deny_reason(out)


def test_cost_is_priced_per_model_and_per_token_class(tmp_path):
    sys.path.insert(0, str(HOOKS))
    try:
        import guard
    finally:
        sys.path.remove(str(HOOKS))
    haiku_out = ("claude-haiku-4-5", {**ZERO_USAGE, "output_tokens": 1_000_000})
    sonnet_cache = ("claude-sonnet-4-5", {**ZERO_USAGE, "cache_read_input_tokens": 1_000_000})
    t = write_transcript(tmp_path / "rates.jsonl", [haiku_out, sonnet_cache])
    expected = guard.RATES["haiku"]["output"] + guard.RATES["sonnet"]["cache_read"]
    assert abs(guard.session_cost(str(t), {})[0] - expected) < 1e-9
    assert guard.RATES["haiku"]["output"] > guard.RATES["haiku"]["input"]


def test_a_missing_transcript_costs_nothing_and_never_blocks(tmp_path):
    out = run_guard("pre", pre_call("s-none", transcript=tmp_path / "gone.jsonl"), tmp_path)
    assert out == {}


def test_a_bad_threshold_falls_back_to_the_default(tmp_path):
    t = write_transcript(tmp_path / "t.jsonl", [sonnet_input(1)])  # $3, over the default $2 warn
    out = run_guard("post", {**edit_call("s-bad"), "transcript_path": str(t)}, tmp_path,
                    {"SHIPQUICK_COST_WARN": "two dollars"})
    assert "warn line" in json.dumps(out)


def test_a_grown_transcript_is_read_from_the_saved_offset(tmp_path):
    # Red for review finding 1 (PR #347): the second call must read only the new bytes. The first
    # bytes are rewritten to a bigger number of the same length; a full re-read would count them again.
    t = write_transcript(tmp_path / "grow.jsonl", [sonnet_input(1)])  # $3
    env = {"SHIPQUICK_COST_WARN": "1", "SHIPQUICK_COST_BLOCK": "100"}
    run_guard("post", {**edit_call("s-grow"), "transcript_path": str(t)}, tmp_path, env)
    extra = write_transcript(tmp_path / "extra.jsonl", [sonnet_input(1)]).read_text(encoding="utf-8")
    t.write_text(t.read_text(encoding="utf-8").replace('"input_tokens": 1000000', '"input_tokens": 2000000', 1)
                 + extra, encoding="utf-8")
    out = run_guard("post", {**edit_call("s-grow", n=1), "transcript_path": str(t)}, tmp_path, env)
    assert "$6.00" in json.dumps(out)   # $3 saved from call one, plus $3 of new bytes; a re-read gives $9.00


def test_opus_is_priced_at_opus_list_not_sonnet(tmp_path):
    # Red for review finding 2 (PR #347): an opus output million costs the opus output rate, $75.
    sys.path.insert(0, str(HOOKS))
    try:
        import guard
    finally:
        sys.path.remove(str(HOOKS))
    t = write_transcript(tmp_path / "opus.jsonl", [("claude-opus-4-1", {**ZERO_USAGE, "output_tokens": 1_000_000})])
    assert guard.RATES["opus"]["output"] == 75.0
    assert guard.rate_for("claude-opus-4-1") is guard.RATES["opus"]
    assert abs(guard.session_cost(str(t), {})[0] - 75.0) < 1e-9


def test_six_identical_bash_calls_are_not_denied_by_the_loop(tmp_path):
    # Red for review finding 1 (PR #347): the loop deny is for Edit and Write only. A CI poll that
    # repeats one Bash command must warn in post, not get stopped in pre.
    for _ in range(5):
        run_guard("post", edit_call("s-bash", tool="Bash"), tmp_path)
    sixth = {**edit_call("s-bash", tool="Bash"), "hook_event_name": "PreToolUse"}
    assert run_guard("pre", sixth, tmp_path) == {}


def test_six_identical_write_calls_are_still_denied_by_the_loop(tmp_path):
    for _ in range(5):
        run_guard("post", edit_call("s-write", tool="Write"), tmp_path)
    sixth = {**edit_call("s-write", tool="Write"), "hook_event_name": "PreToolUse"}
    assert LOOP_TEXT in deny_reason(run_guard("pre", sixth, tmp_path))


def test_a_cost_warning_is_printed_once_per_dollar(tmp_path):
    # Red for review finding 2 (PR #347): a $3 session warns on the first call, then stays quiet.
    t = write_transcript(tmp_path / "once.jsonl", [sonnet_input(1)])  # $3
    first = run_guard("post", {**edit_call("s-once"), "transcript_path": str(t)}, tmp_path)
    second = run_guard("post", {**edit_call("s-once", n=1), "transcript_path": str(t)}, tmp_path)
    assert "warn line" in json.dumps(first)
    assert second == {}
