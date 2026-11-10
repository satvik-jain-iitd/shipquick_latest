"""Story #320 (A5a): the PreToolUse Bash hook blocks git hook bypasses.

`git commit --no-verify`, `git push --no-verify` and `core.hooksPath` redirects exit 2 with the reason
on stderr (Claude Code reads exit 2 as block). Everything else exits 0 and prints nothing. Each case is
run the way Claude Code runs a hook: JSON on stdin, the Bash command in tool_input.command.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "plugin" / "hooks" / "git_guard.py"


def run_guard(command, tool_name="Bash"):
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool_name,
               "tool_input": {"command": command}}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=10)


BLOCKED = [
    'git commit -m "fix" --no-verify',
    "git commit --no-verify -m fix",
    "git commit --no-verify",
    "git push --no-verify",
    "git push origin dev --no-verify",
    "git -c core.hooksPath=/dev/null commit -m fix",
    "git config core.hooksPath .husky",
    "git config --local core.hooksPath=/dev/null",
    "git config core.HooksPath /dev/null",
    "cd repo && git commit --no-verify -m fix",
    'echo "run it" && git push --no-verify',
    "git commit -n -m fix",
    "git commit -m fix \\\n--no-verify",
    "git commit -m fix \\\n  --no-verify -q",
    "GIT_CONFIG_PARAMETERS=\"'core.hooksPath=/dev/null'\" git commit -m fix",
    "GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m fix",
    "git --config-env=core.hooksPath=HOOKS_DIR commit -m fix",
    "git --config-env core.hooksPath=HOOKS commit -m fix",
    "git commit --no-veri -m fix",
    "git commit --no-verif -m fix",
    "git push --no-veri origin dev",
]


@pytest.mark.parametrize("command", BLOCKED)
def test_bypass_is_blocked_with_reason(command):
    p = run_guard(command)
    assert p.returncode == 2, command
    assert p.stderr.startswith("git_guard: blocked"), p.stderr
    assert p.stdout == ""


HARMLESS = [
    'git commit -m "fix the parser"',
    "git push origin dev",
    "git push -n origin dev",  # -n is --dry-run for push, not --no-verify
    "git status",
    "git config user.name klickbae8yt-star",
    "git config --get core.hooksPath",  # a read is not a redirect
    "ls -la",
]


@pytest.mark.parametrize("command", HARMLESS)
def test_harmless_command_passes_silently(command):
    p = run_guard(command)
    assert p.returncode == 0, command
    assert p.stdout == "" and p.stderr == ""


QUOTED = [
    'echo "git commit --no-verify"',
    "grep -rn '--no-verify' docs/",
    "python3 -c \"print('git push --no-verify')\"",
    'git commit -m "docs: say never use --no-verify"',
    'gh pr create --body "core.hooksPath is not allowed"',
]


@pytest.mark.parametrize("command", QUOTED)
def test_bypass_text_inside_a_quoted_argument_passes(command):
    p = run_guard(command)
    assert p.returncode == 0, command
    assert p.stderr == ""


def test_other_tools_and_broken_input_pass():
    assert run_guard("git push --no-verify", tool_name="Edit").returncode == 0
    p = subprocess.run([sys.executable, str(HOOK)], input="not json",
                       capture_output=True, text=True, timeout=10)
    assert p.returncode == 0


def test_hook_is_registered_for_bash_pre_tool_use():
    hooks = json.loads((ROOT / "plugin" / "hooks" / "hooks.json").read_text())["hooks"]
    entries = [e for e in hooks["PreToolUse"] if e.get("matcher") == "Bash"]
    commands = [h["command"] for e in entries for h in e["hooks"]]
    assert any("git_guard.py" in c for c in commands)
