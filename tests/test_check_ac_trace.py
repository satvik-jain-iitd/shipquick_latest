"""AC traceability (M5d)."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_ac_trace.py"


def run(body, *args):
    return subprocess.run(["python3", str(SCRIPT), *args], input=body, capture_output=True, text=True)


def tree(tmp_path, **files):
    """A repo tree: {"tests/test_x.py": "def test_foo(): ..."} as keyword-free dict via tree(tmp_path, **{"a/b.py": text})."""
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def run_root(tmp_path, body):
    return subprocess.run(["python3", str(SCRIPT), "--root", str(tmp_path)], input=body, capture_output=True, text=True)


XTREE = {"tests/test_x.py": "def test_foo():\n    pass\n\ndef test_bar():\n    pass\n"}


def test_a_story_with_every_ac_mapped_passes(tmp_path):
    tree(tmp_path, **XTREE)
    r = run_root(tmp_path, "## Scenarios\nAC-1: foo\nAC-2: bar\nTests: AC-1 -> tests/test_x.py::test_foo; AC-2 -> tests/test_x.py::test_bar\n")
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout


def test_an_unmapped_ac_fails_and_is_named():
    r = run("AC-1: a\nAC-2: b\nTests: AC-1 -> tests/test_x.py::test_foo\n")
    assert r.returncode == 1 and "AC-2" in r.stdout and "AC-1" not in r.stdout.split("AC-2")[0], r.stdout


def test_a_tests_line_that_maps_nothing_fails():
    r = run("AC-1: a\nAC-2: b\nTests: later\n")
    assert r.returncode == 1 and "AC-1" in r.stdout and "AC-2" in r.stdout, r.stdout


def test_a_mapping_for_an_ac_the_story_does_not_define_fails():
    r = run("AC-1: a\nTests: AC-1 -> tests/test_x.py::test_foo; AC-9 -> tests/test_x.py::test_nine\n")
    assert r.returncode == 1 and "AC-9" in r.stdout and "does not define" in r.stdout, r.stdout


def test_a_mention_of_an_ac_in_prose_does_not_define_it(tmp_path):
    tree(tmp_path, **XTREE)
    r = run_root(tmp_path, "This story replaces AC-7 of the old one.\nAC-1: a\nTests: AC-1 -> tests/test_x.py::test_foo\n")
    assert r.returncode == 0, r.stdout


def test_a_story_without_ac_ids_fails():
    r = run("## Scenarios\nfoo\nTests: tests/test_x.py\n")
    assert r.returncode == 1 and "acceptance-criteria IDs" in r.stdout, r.stdout


def test_a_story_without_tests_mapping_fails():
    r = run("## Scenarios\nAC-1: foo\n")
    assert r.returncode == 1 and "Tests:" in r.stdout, r.stdout


def test_pr_body_mode_skips_no_link(tmp_path):
    f = tmp_path / "body.md"; f.write_text("## What\nNo link.\n", encoding="utf-8")
    r = run("", "--pr-body-file", str(f))
    assert r.returncode == 0, r.stdout


STUB = """#!/usr/bin/env bash
case "$1 $2" in
  "auth status") [ -n "${STUB_NO_AUTH:-}" ] && { echo "You are not logged into any GitHub hosts." >&2; exit 1; }; exit 0 ;;
  "issue view") cat "$STUB_DIR/issue.json"; exit 0 ;;
esac
exit 9
"""


def stub_env(tmp_path, issue=None, no_auth=False):
    stub = tmp_path / "stub"; stub.mkdir()
    (stub / "gh").write_text(STUB, encoding="utf-8"); (stub / "gh").chmod(0o755)
    if issue is not None:
        (stub / "issue.json").write_text(json.dumps(issue), encoding="utf-8")
    return {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub), "STUB_NO_AUTH": "1" if no_auth else ""}


def story_issue(created, body):
    return {"labels": [{"name": "user-story"}], "body": body, "createdAt": created}


def test_old_story_skipped(tmp_path):
    f = tmp_path / "body.md"; f.write_text("Closes #12\n", encoding="utf-8")
    issue = story_issue("2026-11-18T10:00:00Z", "## Value\nNo AC.\n")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, issue))
    assert r.returncode == 0, r.stdout
    assert "skip #12" in r.stdout


def test_new_story_without_ac_fails(tmp_path):
    f = tmp_path / "body.md"; f.write_text("Closes #12\n", encoding="utf-8")
    issue = story_issue("2026-11-20T09:00:00Z", "## Value\nNo AC IDs.\n")
    r = subprocess.run(["python3", str(SCRIPT), "--pr-body-file", str(f)], capture_output=True, text=True, env=stub_env(tmp_path, issue))
    assert r.returncode == 1, r.stdout


def test_check_local_skips_when_gh_not_logged_in(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "feat: x\n\nCloses #12")
    issue = story_issue("2026-11-20T09:00:00Z", "## Value\nNo AC.\n")
    env = stub_env(tmp_path, issue, no_auth=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "ac-trace"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skip ac-trace: gh is not logged in" in r.stdout


# ---- #564 review point 2: the mapped test is real: the file is in the tree and holds the name as a whole word ----
def test_a_mapping_to_a_missing_test_fails(tmp_path):
    tree(tmp_path, **XTREE)
    missing_file = run_root(tmp_path, "AC-1: a\nTests: AC-1 -> tests/test_gone.py::test_foo\n")
    assert missing_file.returncode == 1 and "tests/test_gone.py" in missing_file.stdout and "AC-1" in missing_file.stdout, missing_file.stdout
    missing_name = run_root(tmp_path, "AC-1: a\nTests: AC-1 -> tests/test_x.py::test_nope\n")
    assert missing_name.returncode == 1 and "test_nope" in missing_name.stdout, missing_name.stdout


def test_the_name_is_a_whole_word_so_a_longer_name_does_not_satisfy_it(tmp_path):
    tree(tmp_path, **{"tests/test_x.py": "def test_foo_bar():\n    pass\n"})
    r = run_root(tmp_path, "AC-1: a\nTests: AC-1 -> tests/test_x.py::test_foo\n")
    assert r.returncode == 1 and "test_foo" in r.stdout, r.stdout


@pytest.mark.parametrize("rel,text,name", [
    ("src/a.test.ts", 'test("adds two numbers", () => {});\n', "adds two numbers"),
    ("src/a.test.ts", "it('shows', () => {});\n", "shows"),
    ("app/src/test/AppTest.kt", "class AppTest { @Test fun greets() {} }\n", "greets"),
    ("tests/test_x.py", "async def test_async():\n    pass\n", "test_async"),
])
def test_a_child_may_test_in_another_language(tmp_path, rel, text, name):
    tree(tmp_path, **{rel: text})
    ref = f'"{name}"' if " " in name else name   # a title with spaces is written in quotes
    r = run_root(tmp_path, f"AC-1: a\nTests: AC-1 -> {rel}::{ref}\n")
    assert r.returncode == 0, r.stdout


@pytest.mark.parametrize("path", ["../outside.py", "/etc/hosts", "tests/../../x.py"])
def test_a_path_outside_the_tree_fails(tmp_path, path):
    tree(tmp_path, **XTREE)
    r = run_root(tmp_path, f"AC-1: a\nTests: AC-1 -> {path}::test_foo\n")
    assert r.returncode == 1 and "outside" in r.stdout, r.stdout


# ---- #564 review point 5: a feature id, `have_base ac-trace`, a local check on the repo's own tree, a CI step on pull requests, named in the walk ----
STORY_OK = ("## Value\nx\nAC-1: a\nTests: AC-1 -> tests/test_x.py::test_foo\n")
STORY_BAD = ("## Value\nx\nAC-1: a\nAC-2: b\nTests: AC-1 -> tests/test_x.py::test_foo\n")


def local_repo(tmp_path, with_base=True):
    repo = tmp_path / "repo"; repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev"); git("config", "user.email", "t@example.com"); git("config", "user.name", "t")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text("def test_foo():\n    pass\n", encoding="utf-8")
    git("add", "-A"); git("commit", "-q", "-m", "chore: base")
    if with_base:
        git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "feat: x\n\nCloses #12")
    return repo


def run_local(tmp_path, repo, issue, *, no_auth=False):
    env = stub_env(tmp_path, issue, no_auth=no_auth)
    return subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "ac-trace"], cwd=repo, capture_output=True, text=True, env=env)


def test_check_local_passes_a_story_whose_acs_are_mapped_to_real_tests(tmp_path):
    r = run_local(tmp_path, local_repo(tmp_path), story_issue("2026-11-20T09:00:00Z", STORY_OK))
    assert r.returncode == 0 and "ok   ac-trace" in r.stdout, (r.stdout, r.stderr)


def test_check_local_fails_a_story_with_an_unmapped_ac_and_names_it(tmp_path):
    r = run_local(tmp_path, local_repo(tmp_path), story_issue("2026-11-20T09:00:00Z", STORY_BAD))
    assert r.returncode == 1 and "FAIL ac-trace" in r.stdout and "AC-2" in r.stdout, (r.stdout, r.stderr)


def test_check_local_reads_the_tree_of_the_repo_not_the_kit(tmp_path):
    repo = local_repo(tmp_path)
    (repo / "tests" / "test_x.py").write_text("def test_other():\n    pass\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "commit", "-qam", "chore: rename the test"], check=True, capture_output=True)
    r = run_local(tmp_path, repo, story_issue("2026-11-20T09:00:00Z", STORY_OK))
    assert r.returncode == 1 and "test_foo" in r.stdout, (r.stdout, r.stderr)


def test_check_local_skip_line_names_ac_trace_when_there_is_no_base(tmp_path):
    r = run_local(tmp_path, local_repo(tmp_path, with_base=False), story_issue("2026-11-20T09:00:00Z", STORY_OK))
    assert "skip ac-trace: no origin/dev here" in r.stdout, (r.stdout, r.stderr)


def test_the_ac_trace_feature_is_on_by_default_and_switches_the_local_check_off(tmp_path):
    d = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]["ac-trace"]
    assert d["default"] is True and d["locked"] is False and d["name"] and d["what"] and d["if_off"] and d["group"]
    repo = local_repo(tmp_path)
    r = subprocess.run(["python3", str(ROOT / "scripts" / "features.py"), "--root", str(repo), "set", "ac-trace", "off"], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout, r.stderr)
    r = run_local(tmp_path, repo, story_issue("2026-11-20T09:00:00Z", STORY_BAD))
    assert "skipped: ac-trace is off" in r.stdout, (r.stdout, r.stderr)


def test_the_ci_step_runs_only_on_pull_requests():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    step = ci.split("check_ac_trace.py", 1)[0].rsplit("      - name:", 1)[1]
    assert "if: github.event_name == 'pull_request'" in step, step


def test_the_sample_child_walk_names_the_check():
    walk = (ROOT / "tests" / "test_sample_child_walk.py").read_text(encoding="utf-8")
    assert '"ac-trace":' in walk
