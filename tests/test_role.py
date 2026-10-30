"""Story #140: scripts/role.sh -- one role, one GitHub account, per session. A stub `gh` on PATH
(no network); role.sh is SOURCED inside a fresh bash subprocess so its exports are observable."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ROLE = ROOT / "scripts" / "role.sh"
STUB = """#!/usr/bin/env bash
case "$1" in
  auth) [ "$2" = token ] && { echo "tok-$4"; exit 0; } ;;
esac
exit 9
"""


@pytest.fixture
def repo(tmp_path):
    c = tmp_path / "repo"
    c.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "dev", str(c)], check=True)
    (c / ".shipquick").mkdir()
    (c / ".shipquick" / "roles.yml").write_text(
        "coder:\n  - coder-one\n  - coder-two\nreviewer:\n  - reviewer-one\nowner: reviewer-one\n",
        encoding="utf-8",
    )
    return c


@pytest.fixture
def stub(tmp_path):
    s = tmp_path / "stub"
    s.mkdir()
    (s / "gh").write_text(STUB, encoding="utf-8")
    (s / "gh").chmod(0o755)
    return s


def source(repo, stub, *cmds):
    env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}"}
    script = "set -u\n" + "\n".join(cmds) + "\n"
    script += 'echo "RC:$?"\nenv | grep -E "^(SHIPQUICK_|GH_TOKEN=)" | sort\n'
    return subprocess.run(["bash", "-c", script], cwd=repo, capture_output=True, text=True, env=env)


def test_running_it_directly_instead_of_sourcing_refuses(repo, stub):
    r = subprocess.run(["bash", str(ROLE), "coder"], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 2
    assert "must be sourced" in r.stderr


def test_coder_role_exports_the_first_coder_accounts_token(repo, stub):
    r = source(repo, stub, f"source {ROLE} coder")
    assert "SHIPQUICK_ROLE=coder" in r.stdout
    assert "SHIPQUICK_ACCOUNT=coder-one" in r.stdout
    assert "GH_TOKEN=tok-coder-one" in r.stdout


def test_reviewer_role_exports_the_reviewer_account(repo, stub):
    r = source(repo, stub, f"source {ROLE} reviewer")
    assert "SHIPQUICK_ACCOUNT=reviewer-one" in r.stdout
    assert "GH_TOKEN=tok-reviewer-one" in r.stdout


def test_an_explicit_second_coder_account_is_honored(repo, stub):
    r = source(repo, stub, f"source {ROLE} coder coder-two")
    assert "SHIPQUICK_ACCOUNT=coder-two" in r.stdout


def test_an_account_not_listed_for_the_role_refuses(repo, stub):
    r = source(repo, stub, f"source {ROLE} coder some-other-account")
    assert "RC:1" in r.stdout
    assert "not a coder account" in r.stderr


def test_the_same_role_twice_in_one_session_is_a_no_op(repo, stub):
    r = source(repo, stub, f"source {ROLE} coder", f"source {ROLE} coder")
    assert "RC:0" in r.stdout
    assert "SHIPQUICK_ROLE=coder" in r.stdout


def test_a_different_role_in_the_same_session_refuses(repo, stub):
    r = source(repo, stub, f"source {ROLE} coder", f"source {ROLE} reviewer")
    assert "RC:1" in r.stdout
    assert "one role per session" in r.stderr
    assert "SHIPQUICK_ROLE=coder" in r.stdout   # the first role's exports are never overwritten


def test_no_roles_yml_at_all_refuses_with_a_clear_reason(tmp_path, stub):
    c = tmp_path / "bare"
    c.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "dev", str(c)], check=True)
    r = source(c, stub, f"source {ROLE} coder")
    assert "RC:1" in r.stdout
    assert "adopt.sh" in r.stderr
