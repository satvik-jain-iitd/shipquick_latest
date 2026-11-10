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


# ---- review of #345: the mode like mode.sh, the dense rules, the manifest, the ADR ----
def git_repo(path):
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def hook_mode(cwd, extra_env=None, payload=None):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN), **(extra_env or {})}
    p = subprocess.run([sys.executable, str(HOOKS / "session_start.py")], input=json.dumps(payload or {}),
                       capture_output=True, text=True, cwd=cwd, env=env, timeout=10)
    assert p.returncode == 0, p.stderr
    return context_of(p)


def test_the_mode_is_read_from_the_git_common_dir_like_mode_sh(tmp_path):
    repo = git_repo(tmp_path / "repo")
    (repo / ".git" / "shipquick-mode").write_text("auto\n")
    assert "mode: auto" in hook_mode(repo)


def test_a_tracked_mode_file_wins_over_the_common_dir_file(tmp_path):
    repo = git_repo(tmp_path / "repo")
    (repo / ".git" / "shipquick-mode").write_text("auto\n")
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "mode").write_text("semi\n")
    assert "mode: semi" in hook_mode(repo)


def test_the_mode_is_found_from_a_subfolder_and_a_worktree(tmp_path):
    repo = git_repo(tmp_path / "repo")
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@e.x", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)
    (repo / ".git" / "shipquick-mode").write_text("manual\n")
    sub = repo / "a" / "b"
    sub.mkdir(parents=True)
    assert "mode: manual" in hook_mode(sub)
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", "w"], check=True)
    assert "mode: manual" in hook_mode(wt)      # every worktree shares the common dir


def test_claude_project_dir_is_preferred_when_set(tmp_path):
    repo = git_repo(tmp_path / "repo")
    (repo / ".git" / "shipquick-mode").write_text("semi\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert "mode: semi" in hook_mode(elsewhere, extra_env={"CLAUDE_PROJECT_DIR": str(repo)})


def test_a_word_that_is_not_a_mode_reads_as_not_set(tmp_path):
    repo = git_repo(tmp_path / "repo")
    (repo / ".git" / "shipquick-mode").write_text("banana\n")
    assert "mode: not set" in hook_mode(repo)


def test_the_dense_rules_keep_the_instruction_each_rule_exists_for():
    dense = (PLUGIN / "rules-dense.md").read_text(encoding="utf-8")
    for must in ("end your reply with one fenced block",          # rule 19
                 "an agent never runs set",                       # rule 0
                 "The coder opens every PR",                      # rule 4
                 "The author never reviews their own PR"):        # rule 30
        assert must in dense, must


def test_the_dense_text_is_still_short_enough_to_inject_every_session():
    assert len((PLUGIN / "rules-dense.md").read_text(encoding="utf-8")) < 6000


def test_the_session_matcher_covers_fork_and_the_manifest_names_an_author():
    hooks = json.loads((HOOKS / "hooks.json").read_text())["hooks"]
    assert "fork" in hooks["SessionStart"][0]["matcher"].split("|")
    assert json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text()).get("author")


def test_adr_015_states_the_time_budget_honestly():
    adr = (ROOT / "docs" / "decisions" / "ADR-015.md").read_text(encoding="utf-8")
    assert "in-process" in adr and "whole-process" in adr and "interpreter" in adr and "200 ms" in adr
