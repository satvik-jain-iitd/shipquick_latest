"""S0.8 to S0.10: the CI must-have checks (story #43). Text checks only: CI installs pytest and nothing else."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
SCRIPT = ROOT / "scripts" / "check_local.sh"
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


def _jobs():
    """Job names of ci.yml: the two-space keys under `jobs:`."""
    return re.findall(r"^  ([a-z][a-z-]*):\s*$", CI.split("\njobs:\n", 1)[1], re.M)


# ---- S0.8 ----
def test_s08_every_workflow_token_is_read_only():
    for path in WORKFLOWS:
        text = path.read_text(encoding="utf-8")
        assert re.search(r"^permissions:\n  contents: read\n", text, re.M), path.name


def test_s08_every_action_is_pinned_to_a_full_sha_with_its_tag_in_a_comment():
    for path in WORKFLOWS:
        uses = re.findall(r"^\s*-?\s*uses: (\S+)(.*)$", path.read_text(encoding="utf-8"), re.M)
        assert uses, path.name
        for ref, rest in uses:
            assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", ref), f"{path.name}: {ref}"
            assert re.search(r"#\s*v\d+(\.\d+)*", rest), f"{path.name}: {ref} has no tag comment"


def test_s08_dependabot_updates_github_actions_weekly():
    text = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    assert re.search(r'package-ecosystem: "?github-actions"?', text)
    assert re.search(r'directory: "?/"?', text)
    assert re.search(r'interval: "?weekly"?', text)


# ---- S0.9 ----
def test_s09_ci_has_a_secret_scan_job_that_checks_the_binary_checksum():
    assert "\n  secret-scan:\n" in CI
    section = CI.split("\n  secret-scan:\n", 1)[1].split("\n  test:", 1)[0]
    assert "gitleaks git" in section and "sha256sum -c" in section and "fetch-depth: 0" in section


def test_s09_dependency_review_runs_on_pull_requests():
    assert "dependency-review" in _jobs()
    assert "actions/dependency-review-action@" in CI
    assert re.search(r"dependency-review:\n(?:    .*\n)*?    if: github\.event_name == 'pull_request'", CI)


def test_s09_the_gate_waits_for_the_new_jobs():
    gate = CI.split("\n  gate:\n", 1)[1]
    needs = re.search(r"needs: \[([^\]]*)\]", gate).group(1)
    for job in ("secret-scan", "dependency-review"):
        assert job in needs, job


# ---- S0.10: scripts/check_local.sh, run in a throwaway git repo ----
def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    """A repo whose `origin/dev` is the first commit, so check_local.sh has a base to compare with."""
    _git(tmp_path, "init", "-q", "-b", "work")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "T")
    (tmp_path / "README.md").write_text("# base\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "docs: base")
    _git(tmp_path, "update-ref", "refs/remotes/origin/dev", "HEAD")
    return tmp_path


def run(repo, *checks):
    proc = subprocess.run(["bash", str(SCRIPT), *checks], cwd=repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def commit(repo, files, msg="feat: change"):
    for name, content in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(content, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", msg)


def test_s10_merge_marker_at_line_start_fails(repo):
    commit(repo, {"a.py": "x = 1\n<<<<<<< HEAD\ny = 2\n"})
    code, out = run(repo, "markers")
    assert code == 1 and "a.py" in out


def test_s10_marker_named_inside_a_string_passes(repo):
    commit(repo, {"a.py": 'MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")\n'})
    assert run(repo, "markers")[0] == 0


def test_s10_unclosed_markdown_block_fails_closed_one_passes(repo):
    commit(repo, {"a.md": "```\ncode\n"})
    assert run(repo, "md-blocks")[0] == 1
    commit(repo, {"a.md": "```\ncode\n```\n"})
    assert run(repo, "md-blocks")[0] == 0


def test_s10_file_over_500kb_fails(repo):
    commit(repo, {"big.txt": "x" * 512001})
    code, out = run(repo, "sizes")
    assert code == 1 and "big.txt" in out


def test_s10_non_conventional_commit_subject_fails(repo):
    commit(repo, {"a.txt": "1\n"}, "bad message on purpose")
    code, out = run(repo, "commits")
    assert code == 1 and "bad message on purpose" in out


def test_s10_conventional_commit_subjects_pass(repo):
    commit(repo, {"a.txt": "1\n"}, "fix(ci): one")
    assert run(repo, "commits")[0] == 0


def test_s10_pr_over_fifty_files_fails_fifty_passes(repo):
    commit(repo, {f"p/f{i}.txt": "x\n" for i in range(51)})
    assert run(repo, "pr-size")[0] == 1
    _git(repo, "reset", "-q", "--hard", "origin/dev")
    commit(repo, {f"p/f{i}.txt": "x\n" for i in range(50)})
    assert run(repo, "pr-size")[0] == 0


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is installed on the Mac; CI runs the secret-scan job instead")
def test_s09_a_planted_secret_fails_and_a_clean_repo_passes(repo):
    assert run(repo, "secrets")[0] == 0
    commit(repo, {"cfg.py": 'API_SECRET_KEY = "k9Zx3QpL7vB2nM8tR5wY1cD6hJ4aS0fG"\n'})
    code, out = run(repo, "secrets")
    assert code == 1 and "generic-api-key" in out


def test_s10_ci_and_the_script_use_the_same_marker_pattern():
    pattern = r"'^(<<<<<<< |=======$|>>>>>>> )'"
    assert pattern in CI
    assert pattern in SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r'grep -r "<<<<<<<\\\|', CI), "the old unanchored grep is still in ci.yml"


def test_s10_pre_commit_runs_the_local_checks():
    text = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "scripts/check_local.sh" in text
    assert "pre-push" in text


def test_s10_this_repo_passes_its_own_marker_and_markdown_checks():
    for check in ("markers", "md-blocks"):
        code, out = run(ROOT, check)
        assert code == 0, out
