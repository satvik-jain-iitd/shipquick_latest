"""Story #313 (A2): the plugin's SessionStart and SubagentStart hooks inject the rules.

Each hook is a script run as Claude Code runs it: JSON on stdin, JSON on stdout, exit 0.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
HOOKS = PLUGIN / "hooks"


def run_hook(script, payload, cwd):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, str(HOOKS / script)], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=cwd, env=env, timeout=10)
    return p, time.monotonic() - t0


def context_of(p):
    return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]


def test_plugin_manifest_and_hooks_file_exist():
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "shipquick"
    hooks = json.loads((HOOKS / "hooks.json").read_text())["hooks"]
    assert "SessionStart" in hooks and "SubagentStart" in hooks


def test_session_start_injects_rules_and_mode(tmp_path):
    (tmp_path / ".shipquick").mkdir()
    (tmp_path / ".shipquick" / "mode").write_text("auto\n")
    p, _ = run_hook("session_start.py", {"hook_event_name": "SessionStart"}, tmp_path)
    assert p.returncode == 0
    out = json.loads(p.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "SessionStart"
    assert "mode: auto" in out["additionalContext"]
    assert "Radar first" in out["additionalContext"]


SUBAGENT_FIXTURE = {  # shape of a SubagentStart payload on stdin
    "session_id": "fixture-session",
    "transcript_path": "/tmp/fixture/transcript.jsonl",
    "cwd": "",  # filled per test with the project folder
    "hook_event_name": "SubagentStart",
    "agent_id": "fixture-agent",
    "agent_type": "general-purpose",
}


def test_subagent_start_injects_the_same_rules(tmp_path):
    (tmp_path / ".shipquick").mkdir()
    (tmp_path / ".shipquick" / "mode").write_text("semi\n")
    payload = {**SUBAGENT_FIXTURE, "cwd": str(tmp_path)}
    p, _ = run_hook("subagent_start.py", payload, tmp_path)
    assert p.returncode == 0
    out = json.loads(p.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "SubagentStart"
    assert "mode: semi" in out["additionalContext"]
    assert "Radar first" in out["additionalContext"]
    assert "Rule 30" in out["additionalContext"]


def test_missing_mode_file_still_injects_rules(tmp_path):
    p, _ = run_hook("session_start.py", {}, tmp_path)
    assert p.returncode == 0
    assert "mode: not set" in context_of(p)


def test_bad_stdin_exits_zero_and_never_blocks(tmp_path):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    p = subprocess.run([sys.executable, str(HOOKS / "subagent_start.py")], input="not json",
                       capture_output=True, text=True, cwd=tmp_path, env=env, timeout=10)
    assert p.returncode == 0


def test_each_hook_is_under_200_ms(tmp_path):
    """The hook's own work (read mode, read rules, build JSON) is timed in-process: the 200 ms
    budget excludes the Python interpreter start, which varies with machine load."""
    sys.path.insert(0, str(HOOKS))
    try:
        import common
    finally:
        sys.path.remove(str(HOOKS))
    for event in ("SessionStart", "SubagentStart"):
        common.context_for(event, tmp_path)  # warm the file cache once
        t0 = time.perf_counter()
        out = common.context_for(event, tmp_path)
        took = time.perf_counter() - t0
        assert "Radar first" in out["hookSpecificOutput"]["additionalContext"]
        assert took < 0.2, f"{event} work took {took:.3f}s"
    for script in ("session_start.py", "subagent_start.py"):  # whole process: a loose hang guard
        p, _ = run_hook(script, {}, tmp_path)
        assert p.returncode == 0 and p.stdout.strip(), f"{script} gave no output"


def test_rules_file_matches_claude_md(tmp_path):
    """Drift check: plugin/rules-dense.md is exactly what the generator makes from CLAUDE.md."""
    gen = subprocess.run([sys.executable, str(PLUGIN / "gen_rules_dense.py"), "--check"],
                         capture_output=True, text=True, cwd=ROOT)
    assert gen.returncode == 0, gen.stdout + gen.stderr


def test_drift_check_fails_when_a_rule_changes(tmp_path):
    src = (ROOT / "CLAUDE.md").read_text()
    edited = tmp_path / "CLAUDE.md"
    edited.write_text(src.replace("Radar first", "Radar second", 1))
    gen = subprocess.run([sys.executable, str(PLUGIN / "gen_rules_dense.py"), "--check",
                          "--source", str(edited)], capture_output=True, text=True, cwd=ROOT)
    assert gen.returncode == 1
    assert "rules-dense.md" in gen.stdout + gen.stderr
