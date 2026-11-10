"""Story #319 (A15): a PR that changes code names the test it turned red first, and that test file is in the PR diff.
Docs-only PRs and dev <-> main PRs are exempt. Tests use a real throwaway git repo, not a stubbed diff."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_tdd.py"

RED_OK = "Summary.\n\n## Red\n\n- tests/test_widget.py::test_widget_rejects_empty (failed first)\n\n## Local proof\nran it\n"


def make_repo(tmp_path, files):
    """A repo with a dev base commit, origin/dev pointing at it, and one feature commit adding `files`."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("checkout", "-q", "-b", "feat/319-x")
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "feat: x")
    return repo


def run(tmp_path, repo, body, *extra):
    body_file = tmp_path / "body.md"
    body_file.write_text(body, encoding="utf-8")
    return subprocess.run(
        ["python3", str(SCRIPT), "--body-file", str(body_file), "--base", "origin/dev", "--repo", str(repo), *extra],
        capture_output=True, text=True,
    )


CODE = {"scripts/widget.py": "def widget():\n    return 1\n", "tests/test_widget.py": "def test_widget_rejects_empty():\n    pass\n"}


def test_s319_a_code_pr_whose_body_has_no_red_section_fails(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nA widget.\n")
    assert r.returncode == 1 and "## Red" in r.stdout, r.stdout


def test_s319_a_red_section_naming_a_test_file_in_the_diff_passes(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, RED_OK)
    assert r.returncode == 0 and "tdd OK" in r.stdout, r.stdout


def test_s319_a_red_section_naming_a_test_not_in_the_diff_fails(tmp_path):
    repo = make_repo(tmp_path, {"scripts/widget.py": "x = 1\n"})
    r = run(tmp_path, repo, RED_OK)
    assert r.returncode == 1 and "tests/test_widget.py" in r.stdout and "not in the PR diff" in r.stdout, r.stdout


def test_s319_a_red_section_that_names_no_test_fails(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## Red\n\nI wrote it first, trust me.\n")
    assert r.returncode == 1 and "names no test" in r.stdout, r.stdout


def test_s319_a_test_file_deleted_in_the_diff_is_not_evidence(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_widget.py").write_text("def test_w():\n    pass\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("checkout", "-q", "-b", "feat/319-x")
    git("rm", "-q", "tests/test_widget.py")
    (repo / "scripts").mkdir()
    (repo / "scripts" / "widget.py").write_text("x = 1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "feat: drop a test")
    r = run(tmp_path, repo, "## Red\n\n- tests/test_widget.py\n")
    assert r.returncode == 1 and "not in the PR diff" in r.stdout, r.stdout


@pytest.mark.parametrize("files", [
    {"docs/guide.md": "# Guide\n", "pm/agile/notes.txt": "plan\n"},
    {"README.md": "# Readme\n"},
])
def test_s319_a_docs_only_pr_is_exempt_and_needs_no_red_section(tmp_path, files):
    repo = make_repo(tmp_path, files)
    r = run(tmp_path, repo, "## What\nDocs only.\n")
    assert r.returncode == 0 and "exempt" in r.stdout and "docs" in r.stdout, r.stdout


def test_s319_a_dev_into_main_promotion_is_exempt(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nPromotion.\n", "--base-branch", "main", "--head-branch", "dev")
    assert r.returncode == 0 and "exempt" in r.stdout, r.stdout


def test_s319_a_main_into_dev_back_merge_is_exempt(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nBack-merge.\n", "--base-branch", "dev", "--head-branch", "main")
    assert r.returncode == 0 and "exempt" in r.stdout, r.stdout


def test_s319_a_feature_pr_into_dev_is_not_exempt(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nNo red.\n", "--base-branch", "dev", "--head-branch", "feat/319-x")
    assert r.returncode == 1, r.stdout


def test_s319_a_pytest_node_id_names_its_file(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## Red\n\n- tests/test_widget.py::test_widget_rejects_empty\n")
    assert r.returncode == 0, r.stdout


def test_s319_ci_has_a_tdd_job_on_every_pr_and_the_gate_waits_for_it():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "\n  tdd:\n" in ci and "scripts/check_tdd.py" in ci
    gate = ci.split("\n  gate:\n", 1)[1]
    assert "tdd" in gate.split("needs: [", 1)[1].split("]", 1)[0].split(", ")


def test_s319_check_local_runs_the_tdd_check():
    text = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "tdd)" in text and "check_tdd.py" in text
