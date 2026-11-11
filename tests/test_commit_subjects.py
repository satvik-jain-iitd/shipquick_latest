"""Story #446 (CI side): a commit subject over 72 characters fails on the PR's own commits, in the reusable checks.yml, behind its
own feature flag `commit-subjects`, in the gate, and in check_local.sh (rule 29). Real git in a tmp repo; text checks on workflows."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_commit_subjects.py"
CHECKS = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
DEFAULTS = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]


def git(c, *a):
    return subprocess.run(["git", "-c", "user.name=T", "-c", "user.email=t@example.test", *a], cwd=c, capture_output=True, text=True, check=True).stdout


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "dev", ".")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "chore: base " + "b" * 90)   # a long subject BEFORE the base: not this branch's
    git(tmp_path, "update-ref", "refs/remotes/origin/dev", "HEAD")
    return tmp_path


def run(c, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=c, capture_output=True, text=True)


def test_72_characters_passes_and_73_fails_naming_the_commit(repo):
    git(repo, "commit", "-q", "--allow-empty", "-m", "chore: " + "a" * 65)   # 72
    r = run(repo, "--base", "origin/dev")
    assert r.returncode == 0 and "commit subjects OK" in r.stdout
    git(repo, "commit", "-q", "--allow-empty", "-m", "chore: " + "c" * 66)   # 73
    r = run(repo, "--base", "origin/dev")
    assert r.returncode == 1 and "over 72 characters (73)" in r.stdout and "c" * 20 in r.stdout


def test_merge_subjects_are_ignored(repo):
    git(repo, "commit", "-q", "--allow-empty", "-m", "Merge " + "m" * 100)
    assert run(repo, "--base", "origin/dev").returncode == 0


def test_a_missing_base_is_an_error_never_a_pass(repo):
    r = run(repo, "--base", "origin/nope")
    assert r.returncode == 2 and "origin/nope" in r.stderr


def test_the_feature_is_listed_on_by_default_with_plain_words():
    d = DEFAULTS["commit-subjects"]
    assert d["default"] is True and not d.get("locked") and d["group"] == "Checks on every pull request"
    assert d["name"] and d["what"] and d["if_off"]


def job(name):
    return re.split(r"\n  [A-Za-z_][A-Za-z0-9_-]*:\n", CHECKS.split(f"\n  {name}:\n", 1)[1], maxsplit=1)[0]


def test_checks_yml_has_the_job_behind_the_flag_with_full_history():
    j = job("commit-subjects")
    assert "needs: [features]" in j and "fromJSON(needs.features.outputs.flags)['commit-subjects']" in j
    assert "needs.features.result == 'success'" in j and "github.event_name == 'pull_request'" in j
    assert "fetch-depth: 0" in j and "check_commit_subjects.py" in j and "github.base_ref" in j
    assert "timeout-minutes:" in j


def test_the_gate_waits_for_the_job_and_prints_it():
    gate = CHECKS.split("\n  gate:\n", 1)[1]
    assert "commit-subjects" in gate.split("if: always()", 1)[0]
    assert 'echo "commit-subjects: ${{ needs.commit-subjects.result }}"' in gate


def test_check_local_runs_it_behind_the_same_flag():
    t = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "commit-subjects) echo commit-subjects ;;" in t
    assert "check_commit_subjects.py" in t and "commit-subjects)" in t


def test_the_wiring_check_passes_on_the_real_workflow():
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_features_wiring.py")], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
