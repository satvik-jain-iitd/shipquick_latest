"""Story #120: scripts/env_drift.sh prints what is only on dev after a promotion, so main and dev
can be checked to point at the same app code."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "env_drift.sh"


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def commit(repo, name, content, msg):
    (repo / name).write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def run(repo, *args):
    return subprocess.run(["bash", str(SCRIPT), "--repo", str(repo), *args], capture_output=True, text=True)


def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "T")
    commit(tmp_path, "a.txt", "1\n", "feat: base")
    git(tmp_path, "branch", "dev")
    return tmp_path


def test_s120_no_drift_when_dev_and_main_are_the_same(tmp_path):
    r = run(repo(tmp_path))
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "no drift" in r.stdout.lower()


def test_s120_a_commit_only_on_dev_is_printed_with_the_changed_files(tmp_path):
    rp = repo(tmp_path)
    git(rp, "checkout", "-q", "dev")
    commit(rp, "b.txt", "2\n", "feat: not yet promoted")
    r = run(rp)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "feat: not yet promoted" in r.stdout
    assert "b.txt" in r.stdout


def test_s120_custom_branch_names(tmp_path):
    rp = repo(tmp_path)
    git(rp, "branch", "-m", "dev", "staging")
    r = run(rp, "--dev", "staging")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "no drift" in r.stdout.lower()


def test_s120_an_unknown_branch_is_an_error(tmp_path):
    r = run(repo(tmp_path), "--dev", "no-such-branch")
    assert r.returncode == 2
