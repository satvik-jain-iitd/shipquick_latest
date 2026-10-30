"""Story #126: scripts/freeze.sh on/off/status. Real git against a local bare "origin", no network
(FREEZE_NO_PUSH=1 stops right after the local commit)."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FREEZE = ROOT / "scripts" / "freeze.sh"


def run(repo, *args, extra_env=None):
    env = dict(os.environ)
    env["FREEZE_NO_PUSH"] = "1"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(["bash", str(FREEZE), *args], cwd=repo, capture_output=True, text=True, env=env)


@pytest.fixture
def repo(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    work = tmp_path / "work"
    subprocess.run(["git", "clone", "-q", str(remote), str(work)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=work, check=True)
    (work / "README.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=work, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: init"], cwd=work, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main", "-q"], cwd=work, check=True)
    return work


def freeze_main_directly(repo, reason="incident", until="2026-12-31"):
    """Simulate an already-merged freeze on origin/main, bypassing freeze.sh's own PR step."""
    subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, check=True)
    (Path(repo) / ".shipquick").mkdir(exist_ok=True)
    (Path(repo) / ".shipquick" / "freeze").write_text(f"reason: {reason}\nuntil: {until}\n", encoding="utf-8")
    subprocess.run(["git", "add", ".shipquick/freeze"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: freeze release — " + reason], cwd=repo, check=True)
    subprocess.run(["git", "push", "-q", "origin", "main"], cwd=repo, check=True)


def test_on_writes_the_freeze_file_and_commits_on_a_chore_branch(repo):
    r = run(repo, "on", "a holiday freeze", "--until", "2026-11-15")
    assert r.returncode == 0, r.stderr
    content = (repo / ".shipquick" / "freeze").read_text(encoding="utf-8")
    assert "reason: a holiday freeze" in content and "until: 2026-11-15" in content
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert branch.startswith("chore/freeze-on-")
    msg = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert msg.startswith("chore: freeze release")


def test_on_refuses_a_bad_until_date(repo):
    r = run(repo, "on", "x", "--until", "not-a-date")
    assert r.returncode == 2
    assert "bad --until date" in r.stderr


def test_on_refuses_a_dirty_working_tree(repo):
    (repo / "scratch.txt").write_text("uncommitted\n", encoding="utf-8")
    r = run(repo, "on", "x", "--until", "2026-12-01")
    assert r.returncode == 1
    assert "not clean" in r.stderr


def test_on_requires_a_reason_and_an_until_date(repo):
    assert run(repo, "on").returncode == 2
    assert run(repo, "on", "x").returncode == 2


def test_off_removes_the_freeze_file_and_commits_on_a_chore_branch(repo):
    freeze_main_directly(repo)
    r = run(repo, "off")
    assert r.returncode == 0, r.stderr
    assert not (repo / ".shipquick" / "freeze").exists()
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert branch.startswith("chore/freeze-off-")
    msg = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert msg == "chore: lift release freeze"


def test_off_refuses_when_main_is_not_frozen(repo):
    r = run(repo, "off")
    assert r.returncode == 1
    assert "nothing to lift" in r.stderr


def test_status_with_no_local_freeze_file_says_not_frozen(repo):
    r = run(repo, "status")
    assert r.returncode == 0
    assert "not frozen" in r.stdout


def test_status_with_a_local_freeze_file_says_frozen(repo):
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "freeze").write_text("reason: x\nuntil: 2099-01-01\n", encoding="utf-8")
    r = run(repo, "status")
    assert r.returncode == 1
    assert "frozen until 2099-01-01" in r.stdout


def _commit_roles_yml(repo, text):
    """A clean working tree is required before `on`/`off`, so roles.yml must already be committed."""
    (repo / ".shipquick").mkdir(exist_ok=True)
    (repo / ".shipquick" / "roles.yml").write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", ".shipquick/roles.yml"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "chore: roles.yml"], cwd=repo, check=True)
    subprocess.run(["git", "push", "-q", "origin", "main"], cwd=repo, check=True)


# ---- story #140 (reviewer): BUILD_USER defaults to the repo's own first coder account ----
def test_build_user_defaults_to_the_repos_first_coder_account(repo):
    _commit_roles_yml(repo, "coder:\n  - repo-coder\n  - repo-coder-2\nreviewer:\n  - repo-reviewer\nowner: repo-reviewer\n")
    r = run(repo, "on", "incident", "--until", "2099-01-01")
    assert r.returncode == 0, r.stderr
    assert "build account: repo-coder)" in r.stdout


def test_shipquick_build_user_env_var_overrides_roles_yml(repo):
    _commit_roles_yml(repo, "coder:\n  - repo-coder\nreviewer:\n  - repo-reviewer\nowner: repo-reviewer\n")
    r = run(repo, "on", "incident", "--until", "2099-01-01", extra_env={"SHIPQUICK_BUILD_USER": "override-acct"})
    assert r.returncode == 0, r.stderr
    assert "build account: override-acct)" in r.stdout


def test_with_no_roles_yml_the_old_literal_default_is_unchanged(repo):
    r = run(repo, "on", "incident", "--until", "2099-01-01")
    assert r.returncode == 0, r.stderr
    assert "build account: klickbae8yt-star)" in r.stdout
