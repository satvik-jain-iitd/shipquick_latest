"""Story #321 (A5b): the PreToolUse Edit|Write hook warns about a protected path in auto mode. Never blocks."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
HOOK = PLUGIN / "hooks" / "protected_warn.py"
WARN = "protected path, owner merges: "


def make_repo(tmp_path, mode):
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    shutil.copy(ROOT / "scripts" / "protected_paths.txt", repo / "scripts" / "protected_paths.txt")
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "mode").write_text(mode + "\n")
    return repo


def run_hook(repo, file_path, tool="Edit"):
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": str(repo),
               "tool_input": {"file_path": str(file_path)}}
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
    env.pop("CLAUDE_PROJECT_DIR", None)
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True,
                          text=True, cwd=repo, env=env, timeout=10)


def test_editing_a_listed_path_in_auto_mode_prints_the_warning(tmp_path):
    repo = make_repo(tmp_path, "auto")
    p = run_hook(repo, repo / "scripts" / "review_merge.sh")
    assert p.returncode == 0, p.stderr
    assert WARN + "scripts/review_merge.sh" in p.stdout


def test_a_glob_line_matches_a_nested_path(tmp_path):
    repo = make_repo(tmp_path, "auto")
    p = run_hook(repo, repo / ".github" / "workflows" / "ci.yml", tool="Write")
    assert p.returncode == 0, p.stderr
    assert WARN + ".github/workflows/ci.yml" in p.stdout


def test_an_unlisted_path_prints_nothing(tmp_path):
    repo = make_repo(tmp_path, "auto")
    p = run_hook(repo, repo / "src" / "app.py")
    assert p.returncode == 0, p.stderr
    assert p.stdout.strip() == ""


def test_a_listed_path_in_manual_mode_prints_nothing(tmp_path):
    repo = make_repo(tmp_path, "manual")
    p = run_hook(repo, repo / "scripts" / "review_merge.sh")
    assert p.returncode == 0, p.stderr
    assert p.stdout.strip() == ""


def test_a_file_outside_the_repo_prints_nothing(tmp_path):
    repo = make_repo(tmp_path, "auto")
    p = run_hook(repo, tmp_path / "elsewhere.sh")
    assert p.returncode == 0, p.stderr
    assert p.stdout.strip() == ""


def test_bad_stdin_exits_zero_and_never_blocks(tmp_path):
    repo = make_repo(tmp_path, "auto")
    p = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True,
                       cwd=repo, timeout=10)
    assert p.returncode == 0
    assert p.stdout.strip() == ""


def test_the_hook_is_registered_on_pretooluse_edit_and_write():
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
    entry = hooks["PreToolUse"][0]
    assert entry["matcher"] == "Edit|Write"
    assert "protected_warn.py" in entry["hooks"][0]["command"]


def make_child_repo(tmp_path, mode):
    """A child project: ShipQuick vendored under knowledge/shipquick_latest, no root copy of the list."""
    repo = tmp_path / "child"
    vendored = repo / "knowledge" / "shipquick_latest" / "scripts"
    vendored.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    shutil.copy(ROOT / "scripts" / "protected_paths.txt", vendored / "protected_paths.txt")
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "mode").write_text(mode + "\n")
    return repo


def test_a_child_with_the_vendored_list_gets_the_warning(tmp_path):
    # Red for review finding 1 (PR #350): the hook read only root scripts/, so a child never warned.
    repo = make_child_repo(tmp_path, "auto")
    p = run_hook(repo, repo / ".github" / "workflows" / "ci.yml")
    assert p.returncode == 0, p.stderr
    assert WARN + ".github/workflows/ci.yml" in p.stdout


def test_the_warning_reaches_the_model_as_additional_context(tmp_path):
    # Red for review finding 2 (PR #350): systemMessage shows only in the UI, never to the model.
    repo = make_repo(tmp_path, "auto")
    p = run_hook(repo, repo / "scripts" / "review_merge.sh")
    assert p.returncode == 0, p.stderr
    out = json.loads(p.stdout)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "PreToolUse"
    assert WARN + "scripts/review_merge.sh" in hso["additionalContext"]
    assert "permissionDecision" not in hso


def run_hook_with_project_dir(repo, file_path, project_dir, tool="Edit"):
    """Like run_hook, but Claude Code sets CLAUDE_PROJECT_DIR to the session's checkout, not the edited file's."""
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": str(repo),
               "tool_input": {"file_path": str(file_path)}}
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN), "CLAUDE_PROJECT_DIR": str(project_dir)}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True,
                          text=True, cwd=repo, env=env, timeout=10)


def test_an_edit_in_a_worktree_warns_when_the_session_points_at_the_main_checkout(tmp_path):
    # Red for review finding 3 (PR #350): the root came from CLAUDE_PROJECT_DIR (the main checkout), so the
    # worktree path became .claude/worktrees/lane-x/scripts/review_merge.sh and matched nothing.
    repo = make_repo(tmp_path, "auto")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t.t", "commit", "-q", "-m", "base"],
                   cwd=repo, check=True)
    wt = repo / ".claude" / "worktrees" / "lane-x"
    subprocess.run(["git", "worktree", "add", "-q", str(wt)], cwd=repo, check=True)
    p = run_hook_with_project_dir(repo, wt / "scripts" / "review_merge.sh", repo)
    assert p.returncode == 0, p.stderr
    assert WARN + "scripts/review_merge.sh" in p.stdout
