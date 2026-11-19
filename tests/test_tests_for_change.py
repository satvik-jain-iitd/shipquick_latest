"""Story #570: scripts/tests_for_change.py and `check_local.sh tests`."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "tests_for_change.py"
CHECK = ROOT / "scripts" / "check_local.sh"


def pick(repo, changed):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(repo), "--changed", *changed],
                          capture_output=True, text=True)


def make_repo(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("# names check_a.py\ndef test_a():\n    assert True\n")
    (tmp_path / "tests" / "test_b.py").write_text("# names check_b only\ndef test_b():\n    assert True\n")
    (tmp_path / "tests" / "test_doc.py").write_text("# reads docs/NOTE.md\ndef test_doc():\n    assert True\n")
    return tmp_path


def test_a_changed_script_picks_the_tests_that_name_it(tmp_path):
    r = pick(make_repo(tmp_path), ["scripts/check_a.py"])
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["tests/test_a.py"]
    # whole word: check_a must not match check_ab
    (tmp_path / "tests" / "test_c.py").write_text("# check_ab.py\n")
    assert pick(tmp_path, ["scripts/check_a.py"]).stdout.split() == ["tests/test_a.py"]
    # a changed md that no test names is ignored; one a test names picks it
    assert pick(tmp_path, ["docs/OTHER.md"]).stdout.split() == []
    assert pick(tmp_path, ["docs/NOTE.md"]).stdout.split() == ["tests/test_doc.py"]


def test_an_unnamed_file_picks_the_full_suite(tmp_path):
    r = pick(make_repo(tmp_path), ["scripts/check_a.py", "scripts/nobody.py"])
    assert r.stdout.splitlines()[0].startswith("full suite")
    assert "nobody.py" in r.stdout
    assert {"tests/test_a.py", "tests/test_b.py", "tests/test_doc.py"} <= set(r.stdout.split())


def test_a_changed_test_picks_itself(tmp_path):
    r = pick(make_repo(tmp_path), ["tests/test_b.py"])
    assert r.stdout.split() == ["tests/test_b.py"]


def test_check_local_tests_runs_the_picked_files(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "tests" / "test_b.py").write_text("# names check_b\ndef test_b():\n    assert False\n")
    env = {**os.environ, "BASE": "dev", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def git(*a):
        subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, env=env)

    git("init", "-q", "-b", "dev")
    git("add", "-A")
    git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    (repo / "tests" / "test_a.py").write_text("# names check_a.py\ndef test_a():\n    assert True\n# x\n")
    r = subprocess.run(["bash", str(CHECK), "tests"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tests/test_a.py" in r.stdout and "test_b.py" not in r.stdout
    (repo / "tests" / "test_a.py").write_text("def test_a():\n    assert False\n")
    r = subprocess.run(["bash", str(CHECK), "tests"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode != 0


def test_an_unreadable_change_list_picks_every_test(tmp_path):
    repo = make_repo(tmp_path)  # not a git repo: the change list cannot be read
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(repo)], capture_output=True, text=True)
    assert r.stdout.splitlines()[0].startswith("full suite")
    assert {"tests/test_a.py", "tests/test_b.py", "tests/test_doc.py"} <= set(r.stdout.split())


def test_check_local_tests_skips_a_repo_without_python_tests(tmp_path):
    env = {**os.environ, "BASE": "dev", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for a in (["init", "-q", "-b", "dev"], ["-c", "core.hooksPath=/dev/null", "commit", "-q", "--allow-empty", "-m", "b"],
              ["update-ref", "refs/remotes/origin/dev", "HEAD"]):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True, env=env)
    (tmp_path / "code.py").write_text("x = 1\n")
    r = subprocess.run(["bash", str(CHECK), "tests"], cwd=tmp_path, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "skip tests: no python test files in this repo" in r.stdout
    assert "full suite" not in r.stdout and "ok   tests" not in r.stdout


def test_check_local_has_no_disable_comment():
    assert "shellcheck disable" not in CHECK.read_text()
