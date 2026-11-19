"""Story #579: the coverage ratchet judges each changed file. Reports are built in the test's temp folder."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_coverage.py"
sys.path.insert(0, str(SCRIPT.parent))
import check_coverage as cc  # noqa: E402


def report(files):
    return {"files": {p: {"summary": {"percent_covered": v}} for p, v in files.items()}}


def run(tmp_path, baseline, current, changed, extra=()):
    b, c, ch = tmp_path / "base.json", tmp_path / "cur.json", tmp_path / "changed.txt"
    for f, data in ((b, baseline), (c, current)):
        if data is not None:
            f.write_text(data if isinstance(data, str) else json.dumps(data))
    ch.write_text("\n".join(changed) + ("\n" if changed else ""))
    return subprocess.run([sys.executable, str(SCRIPT), "--baseline", str(b), "--current", str(c),
                           "--changed", str(ch), *extra], capture_output=True, text=True)


def rows(base, cur, changed, min_new=80.0):
    return {r["path"]: r for r in cc.judge(base, cur, changed, min_new)}


def test_a_drop_below_the_baseline_fails(tmp_path):
    r = run(tmp_path, report({"scripts/a.py": 90.0}), report({"scripts/a.py": 85.5}), ["scripts/a.py"])
    assert r.returncode == 1
    assert "scripts/a.py" in r.stdout and "90.0" in r.stdout and "85.5" in r.stdout and "fail" in r.stdout


def test_a_file_at_or_above_its_baseline_passes(tmp_path):
    r = run(tmp_path, report({"a.py": 90.0, "b.py": 70.0}), report({"a.py": 90.0, "b.py": 75.0}), ["a.py", "b.py"])
    assert r.returncode == 0, r.stdout
    assert r.stdout.count("pass") >= 2


@pytest.mark.parametrize("bad", [None, "not json", "{}", json.dumps({"files": {"a.py": {"summary": {}}}}),
                                 json.dumps({"files": {"a.py": {"summary": {"percent_covered": "x"}}}})])
def test_a_bad_current_report_fails_and_is_never_skipped(tmp_path, bad):
    r = run(tmp_path, report({"a.py": 50.0}), bad, ["a.py"])
    assert r.returncode == 1
    assert "skip" not in (r.stdout + r.stderr).lower()
    assert "cur.json" in r.stdout + r.stderr


@pytest.mark.parametrize("bad", [None, "not json", "{}", json.dumps({"files": {"a.py": {"summary": {}}}})])
def test_a_bad_baseline_fails_and_is_never_empty(tmp_path, bad):
    r = run(tmp_path, bad, report({"a.py": 99.0}), ["a.py"])
    assert r.returncode == 1
    assert "base.json" in r.stdout + r.stderr


def test_a_file_not_in_the_baseline_must_reach_the_floor():
    got = rows({}, {"new.py": 79.9, "ok.py": 80.0}, ["new.py", "ok.py"], 80.0)
    assert got["new.py"]["verdict"] == "fail" and "new file" in got["new.py"]["reason"]
    assert got["ok.py"]["verdict"] == "pass"


def test_a_changed_file_not_in_the_report_fails(tmp_path):
    got = rows({"a.py": 50.0}, {}, ["a.py"])
    assert got["a.py"]["verdict"] == "fail" and "not in the current report" in got["a.py"]["reason"]
    r = run(tmp_path, report({"a.py": 50.0}), report({"b.py": 99.0}), ["a.py"])
    assert r.returncode == 1


def test_no_changed_files_passes_only_after_both_reports_are_read(tmp_path):
    for name in ("a", "b", "c"):
        (tmp_path / name).mkdir()
    assert run(tmp_path / "a", report({}), report({}), []).returncode == 0
    assert run(tmp_path / "b", report({}), "not json", []).returncode == 1
    assert run(tmp_path / "c", None, report({}), []).returncode == 1


# ---- story #586: the local check `check_local.sh coverage` (step 2 of 3) ----
import os  # noqa: E402

LOCAL = SCRIPT.parent / "check_local.sh"
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def make_repo(tmp_path, files=("a.py", "b.py")):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {**os.environ, **GIT_ENV}

    def git(*a):
        subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "dev")
    for f in files:
        (repo / f).write_text("x = 1\n")
    git("add", "-A")
    git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")

    def commit(msg="change"):   # the change list is origin/BASE...HEAD: only committed work counts
        git("add", "-A")
        git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", msg)
    git.commit = commit
    return repo, git


def local_cov(repo, tmp_path, base=None, cur=None, extra_env=None):
    env = {**os.environ, "BASE": "dev", **(extra_env or {})}
    env.pop("COVERAGE_BASE", None), env.pop("COVERAGE_CURRENT", None)
    for key, name, data in (("COVERAGE_BASE", "base.json", base), ("COVERAGE_CURRENT", "cur.json", cur)):
        if data is not None:
            p = tmp_path / name
            p.write_text(json.dumps(data))
            env[key] = str(p)
    return subprocess.run(["bash", str(LOCAL), "coverage"], cwd=repo, capture_output=True, text=True, env=env)


def test_check_local_coverage_fails_on_a_drop(tmp_path):
    repo, git = make_repo(tmp_path)
    (repo / "a.py").write_text("x = 2\n")
    git.commit()
    r = local_cov(repo, tmp_path, report({"a.py": 90.0, "b.py": 50.0}), report({"a.py": 80.0, "b.py": 50.0}))
    assert r.returncode != 0, r.stdout + r.stderr
    assert "a.py" in r.stdout and "FAIL coverage" in r.stdout
    r = local_cov(repo, tmp_path, report({"a.py": 90.0}), report({"a.py": 90.0}))
    assert r.returncode == 0 and "ok   coverage" in r.stdout, r.stdout + r.stderr


@pytest.mark.parametrize("which", ["base", "cur", "both", "missing_file"])
def test_check_local_coverage_fails_without_a_report(tmp_path, which):
    repo, git = make_repo(tmp_path)
    (repo / "a.py").write_text("x = 2\n")
    git.commit()
    rep = report({"a.py": 90.0})
    if which == "missing_file":
        env = {"COVERAGE_BASE": str(tmp_path / "nope.json"), "COVERAGE_CURRENT": str(tmp_path / "nope2.json")}
        r = local_cov(repo, tmp_path, extra_env=env)
    else:
        r = local_cov(repo, tmp_path, base=rep if which == "base" else None, cur=rep if which == "cur" else None)
    assert r.returncode != 0, r.stdout + r.stderr
    assert "FAIL coverage" in r.stdout and "skip" not in r.stdout.lower()


def test_check_local_coverage_runs_no_tests(tmp_path):
    repo, git = make_repo(tmp_path)
    (repo / "a.py").write_text("x = 2\n")
    git.commit()
    shim = tmp_path / "bin"
    shim.mkdir()
    log = tmp_path / "calls.log"
    (shim / "python3").write_text(f'#!/bin/sh\necho "$@" >> {log}\nexec {sys.executable} "$@"\n')
    (shim / "python3").chmod(0o755)
    (shim / "coverage").write_text(f'#!/bin/sh\necho "coverage $@" >> {log}\n')
    (shim / "coverage").chmod(0o755)
    r = local_cov(repo, tmp_path, report({"a.py": 90.0}), report({"a.py": 90.0}),
                  {"PATH": f"{shim}:{os.environ['PATH']}"})
    assert r.returncode == 0, r.stdout + r.stderr
    calls = log.read_text()
    assert "check_coverage.py" in calls and "-m pytest" not in calls and "coverage run" not in calls and "coverage json" not in calls


def test_check_local_coverage_leaves_out_a_deleted_file(tmp_path):
    repo, git = make_repo(tmp_path)
    (repo / "b.py").unlink()
    (repo / "a.py").write_text("x = 3\n")
    git.commit()
    r = local_cov(repo, tmp_path, report({"a.py": 90.0, "b.py": 90.0}), report({"a.py": 90.0}))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "b.py" not in r.stdout


def test_check_local_coverage_fails_with_no_origin_base(tmp_path):
    repo, git = make_repo(tmp_path)
    git("update-ref", "-d", "refs/remotes/origin/dev")
    r = local_cov(repo, tmp_path, report({"a.py": 90.0}), report({"a.py": 90.0}))
    assert r.returncode != 0 and "FAIL coverage" in r.stdout and "skip" not in r.stdout.lower()


def test_check_local_coverage_removes_its_temp_file(tmp_path):
    repo, git = make_repo(tmp_path)
    (repo / "a.py").write_text("x = 2\n")
    git.commit()
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    local_cov(repo, tmp_path, report({"a.py": 90.0}), report({"a.py": 10.0}), {"TMPDIR": str(tmpdir)})
    assert list(tmpdir.iterdir()) == []


def test_check_local_coverage_is_skipped_when_the_feature_is_off(tmp_path):
    repo, git = make_repo(tmp_path)
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {"coverage": {"on": False}}}))
    r = local_cov(repo, tmp_path)   # no reports at all: off still passes
    assert r.returncode == 0, r.stdout + r.stderr
    assert "skipped: coverage is off" in r.stdout and "FAIL" not in r.stdout


def test_coverage_is_not_in_the_default_list():
    text = LOCAL.read_text(encoding="utf-8")
    default = next(l for l in text.split("\n") if l.startswith("[ $# -eq 0 ] && checks=("))
    assert "coverage" not in default.replace("ui-coverage", "")
    assert "coverage" in next(l for l in text.split("\n") if l.startswith("#   checks:")).replace("ui-coverage", "")
    assert "coverage" in next(l for l in text.split("\n") if "unknown check:" in l).replace("ui-coverage", "")
