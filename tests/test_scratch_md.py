"""Story #322 (A5c): the PreToolUse Write hook warns about a new scratch markdown file.

A file named NOTES*, TODO*, SCRATCH*, DRAFT*, WIP* or TEMP* with .md, outside docs/, .claude/ and
.github/, gets a warning that names the single-source file to use instead. The hook never blocks.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
HOOK = PLUGIN / "hooks" / "scratch_md.py"


def run_write(file_path, cwd):
    payload = {"hook_event_name": "PreToolUse", "tool_name": "Write",
               "tool_input": {"file_path": str(file_path), "content": "x"}, "cwd": str(cwd)}
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                       capture_output=True, text=True, cwd=cwd, env=env, timeout=10)
    assert p.returncode == 0, p.stderr
    return p.stdout


def warning_of(stdout):
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]


def test_a_new_todo_file_outside_docs_warns_and_names_follow_ups(tmp_path):
    out = run_write(tmp_path / "TODO-plan.md", tmp_path)
    assert "docs/follow-ups.md" in warning_of(out)
    assert json.loads(out)["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_a_draft_file_names_docs_plans(tmp_path):
    assert "docs/plans/" in warning_of(run_write(tmp_path / "DRAFT-release.md", tmp_path))


def test_a_write_to_an_existing_todo_file_is_silent(tmp_path):
    (tmp_path / "TODO.md").write_text("- [ ] keep\n", encoding="utf-8")
    assert run_write(tmp_path / "TODO.md", tmp_path) == ""


def test_a_file_outside_the_pattern_is_silent(tmp_path):
    assert run_write(tmp_path / "README.md", tmp_path) == ""
    assert run_write(tmp_path / "src" / "notes_parser.py", tmp_path) == ""


def test_a_pattern_file_inside_docs_is_silent(tmp_path):
    assert run_write(tmp_path / "docs" / "NOTES-2026.md", tmp_path) == ""


def test_a_pattern_file_inside_claude_or_github_is_silent(tmp_path):
    assert run_write(tmp_path / ".claude" / "TEMP-x.md", tmp_path) == ""
    assert run_write(tmp_path / ".github" / "WIP-x.md", tmp_path) == ""


def test_bad_stdin_exits_zero_and_prints_nothing(tmp_path):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    p = subprocess.run([sys.executable, str(HOOK)], input="not json",
                       capture_output=True, text=True, cwd=tmp_path, env=env, timeout=10)
    assert p.returncode == 0 and p.stdout == ""


def test_the_hook_is_registered_for_write_before_use():
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
    pre = hooks["PreToolUse"]
    assert pre[0]["matcher"] == "Write"
    assert "scratch_md.py" in pre[0]["hooks"][0]["command"]
