"""Story #126: scripts/freeze.sh on/off/status. Real git against a local bare "origin", no network
(FREEZE_NO_PUSH=1 stops right after the local commit).

Bug #142: on/off must never touch the caller's own checkout or branch, and must never leave a
stray chore/freeze-* branch behind on a refusal. on/off do their work in a scratch git worktree,
removed (and its branch deleted) on exit via a trap. Under FREEZE_NO_PUSH=1 the scratch branch is
kept (nothing was pushed, so it is the only record of what would have happened) -- tests read it
directly with `git show <branch>:...` instead of inspecting the caller's own tree.

Reviewer nit on PR #144: no literal account fallback. With no $SHIPQUICK_BUILD_USER and no coder
account in .shipquick/roles.yml, on/off refuse and say to run adopt.sh."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FREEZE = ROOT / "scripts" / "freeze.sh"


def run(repo, *args, extra_env=None):
    env = dict(os.environ)
    env["FREEZE_NO_PUSH"] = "1"
    env["SHIPQUICK_BUILD_USER"] = "test-build-acct"   # most tests don't care about account resolution
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


def current_branch(repo):
    return subprocess.run(["git", "branch", "--show-current"], cwd=repo, capture_output=True, text=True).stdout.strip()


def scratch_branches(repo, prefix):
    out = subprocess.run(["git", "branch", "--list", f"{prefix}*"], cwd=repo, capture_output=True, text=True).stdout
    return [l.lstrip("* ").strip() for l in out.splitlines() if l.strip()]


def show(repo, ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=repo, capture_output=True, text=True).stdout


def test_on_writes_the_freeze_file_in_a_scratch_worktree_without_touching_the_caller(repo):
    r = run(repo, "on", "a holiday freeze", "--until", "2026-11-15")
    assert r.returncode == 0, r.stderr
    assert current_branch(repo) == "main"   # bug #142: the caller's own checkout is untouched
    assert not (repo / ".shipquick" / "freeze").exists()   # never written to the caller's own tree
    [branch] = scratch_branches(repo, "chore/freeze-on-")   # kept around under FREEZE_NO_PUSH=1
    content = show(repo, branch, ".shipquick/freeze")
    assert "reason: a holiday freeze" in content and "until: 2026-11-15" in content
    msg = subprocess.run(["git", "log", "-1", "--format=%s", branch], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert msg.startswith("chore: freeze release")


def test_on_refuses_a_bad_until_date(repo):
    r = run(repo, "on", "x", "--until", "not-a-date")
    assert r.returncode == 2
    assert "bad --until date" in r.stderr
    assert scratch_branches(repo, "chore/freeze-on-") == []   # refused before any worktree was made


def test_on_refuses_a_dirty_working_tree(repo):
    (repo / "scratch.txt").write_text("uncommitted\n", encoding="utf-8")
    r = run(repo, "on", "x", "--until", "2026-12-01")
    assert r.returncode == 1
    assert "not clean" in r.stderr


def test_on_requires_a_reason_and_an_until_date(repo):
    assert run(repo, "on").returncode == 2
    assert run(repo, "on", "x").returncode == 2


def test_off_removes_the_freeze_file_in_a_scratch_worktree_without_touching_the_caller(repo):
    freeze_main_directly(repo)
    r = run(repo, "off")
    assert r.returncode == 0, r.stderr
    assert current_branch(repo) == "main"
    [branch] = scratch_branches(repo, "chore/freeze-off-")
    rm = subprocess.run(["git", "show", f"{branch}:.shipquick/freeze"], cwd=repo, capture_output=True, text=True)
    assert rm.returncode != 0   # the file no longer exists on the scratch branch
    msg = subprocess.run(["git", "log", "-1", "--format=%s", branch], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert msg == "chore: lift release freeze"


def test_off_refuses_when_main_is_not_frozen_and_leaves_no_stray_branch(repo):
    r = run(repo, "off")
    assert r.returncode == 1
    assert "nothing to lift" in r.stderr
    assert current_branch(repo) == "main"
    assert scratch_branches(repo, "chore/freeze-off-") == []   # bug #142: checked before any branch was made


def test_status_with_nothing_frozen_on_origin_main_says_not_frozen(repo):
    r = run(repo, "status")
    assert r.returncode == 0
    assert "not frozen" in r.stdout


def test_status_with_an_uncommitted_local_file_is_not_frozen(repo):
    """Bug #142: status (no --repo) reads origin/main, not the local checkout."""
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "freeze").write_text("reason: x\nuntil: 2099-01-01\n", encoding="utf-8")
    r = run(repo, "status")
    assert r.returncode == 0
    assert "not frozen" in r.stdout


def test_status_reads_origin_main_even_when_the_local_checkout_has_not_fetched_it(repo, tmp_path):
    other = tmp_path / "other-clone"
    subprocess.run(["git", "clone", "-q", str(repo.parent / "remote.git"), str(other)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=other, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=other, check=True)
    freeze_main_directly(other, until="2099-01-01")   # pushed from a different clone; repo's own local main is stale
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
    r = run(repo, "on", "incident", "--until", "2099-01-01", extra_env={"SHIPQUICK_BUILD_USER": ""})
    assert r.returncode == 0, r.stderr
    assert "build account: repo-coder)" in r.stdout


def test_shipquick_build_user_env_var_overrides_roles_yml(repo):
    _commit_roles_yml(repo, "coder:\n  - repo-coder\nreviewer:\n  - repo-reviewer\nowner: repo-reviewer\n")
    r = run(repo, "on", "incident", "--until", "2099-01-01", extra_env={"SHIPQUICK_BUILD_USER": "override-acct"})
    assert r.returncode == 0, r.stderr
    assert "build account: override-acct)" in r.stdout


# ---- reviewer nit on PR #144: no literal account fallback ----
def test_with_no_roles_yml_and_no_env_var_on_refuses_and_says_to_run_adopt(repo):
    r = run(repo, "on", "incident", "--until", "2099-01-01", extra_env={"SHIPQUICK_BUILD_USER": ""})
    assert r.returncode == 1
    assert "adopt.sh" in r.stdout + r.stderr
    assert current_branch(repo) == "main"
    assert scratch_branches(repo, "chore/freeze-on-") == []


def test_shipquick_build_user_env_var_still_works_with_no_roles_yml(repo):
    r = run(repo, "on", "incident", "--until", "2099-01-01", extra_env={"SHIPQUICK_BUILD_USER": "override-acct"})
    assert r.returncode == 0, r.stderr
    assert "build account: override-acct)" in r.stdout
