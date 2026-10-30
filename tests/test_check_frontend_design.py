"""Story #121: a PR that touches a project's own frontend paths (docs/frontend-paths.txt, one shell
glob per line) must name the approved design board in its body, or the check fails. A PR that says
"no screen change" but still touches those paths also fails. Nothing configured: always passes."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_frontend_design.sh"


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def commit(repo, files, msg):
    for name, content in files.items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def base_repo(tmp_path, paths_file_text=None):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "T")
    files = {"README.md": "# demo\n"}
    if paths_file_text is not None:
        files["docs/frontend-paths.txt"] = paths_file_text
    commit(tmp_path, files, "feat: base")
    git(tmp_path, "checkout", "-q", "-b", "work")   # the PR's own branch; main stays at the base commit
    return tmp_path


def body_file(tmp_path, text, name="body.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def run(repo, body_text, paths_file=None):
    f = body_file(repo, body_text)
    args = ["--repo", str(repo), "--body-file", str(f), "--base", "main"]
    if paths_file:
        args += ["--paths-file", paths_file]
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def test_nothing_configured_always_passes(tmp_path):
    repo = base_repo(tmp_path, paths_file_text=None)
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "no board here\n")
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_a_pr_that_does_not_touch_frontend_paths_passes_with_no_board(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="frontend/*\n")
    commit(repo, {"backend/api.py": "x\n"}, "feat: an api change")
    r = run(repo, "no board here\n")
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_a_pr_touching_a_frontend_path_with_an_approved_board_passes(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="frontend/*\n")
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "Design board: Production/Login\n")
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_a_pr_touching_a_frontend_path_with_no_board_fails(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="frontend/*\n")
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "## What\nJust a screen.\n")
    assert r.returncode == 1 and "frontend/screen.tsx" in r.stdout


def test_a_pr_touching_a_frontend_path_with_a_placeholder_board_fails(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="frontend/*\n")
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "Design board: <name>\n")
    assert r.returncode == 1


def test_a_pr_touching_a_frontend_path_that_says_no_screen_change_fails(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="frontend/*\n")
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "no screen change\n")
    assert r.returncode == 1 and "no screen change" in r.stdout.lower()


def test_a_pr_with_no_screen_change_and_no_touched_paths_passes(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="frontend/*\n")
    commit(repo, {"backend/api.py": "x\n"}, "feat: an api change")
    r = run(repo, "no screen change\n")
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_comment_and_blank_lines_in_the_paths_file_are_ignored(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="# comment\n\nfrontend/*\n")
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "## What\nno board\n")
    assert r.returncode == 1


def test_an_empty_paths_file_is_the_same_as_nothing_configured(tmp_path):
    repo = base_repo(tmp_path, paths_file_text="# only comments\n")
    commit(repo, {"frontend/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "## What\nno board\n")
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_a_custom_paths_file_location(tmp_path):
    repo = base_repo(tmp_path, paths_file_text=None)
    commit(repo, {"config/frontend-globs.txt": "ui/*\n"}, "chore: config")
    commit(repo, {"ui/screen.tsx": "x\n"}, "feat: a screen")
    r = run(repo, "## What\nno board\n", paths_file="config/frontend-globs.txt")
    assert r.returncode == 1 and "ui/screen.tsx" in r.stdout
