"""Bug #79: scripts/check_md_blocks.py reads only the markdown files git knows (tracked, or new and not ignored),
so a gitignored file with a broken block never fails the local hook while CI passes. Outside a git repo it reads every .md."""
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_md_blocks.py"
BROKEN = "text\n```\nno end\n"
FINE = "text\n```\ncode\n```\n"


def run(cwd):
    return subprocess.run(["python3", str(SCRIPT)], cwd=cwd, capture_output=True, text=True)


def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "dev", str(tmp_path)], check=True)
    return tmp_path


def test_s79_an_ignored_md_with_a_broken_block_is_skipped(tmp_path):
    repo(tmp_path)
    (tmp_path / ".gitignore").write_text("results/\n", encoding="utf-8")
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "README.md").write_text(BROKEN, encoding="utf-8")
    (tmp_path / "ok.md").write_text(FINE, encoding="utf-8")
    r = run(tmp_path)
    assert r.returncode == 0 and "Markdown blocks OK" in r.stdout, r.stdout + r.stderr


def test_s79_a_tracked_md_with_a_broken_block_still_fails(tmp_path):
    repo(tmp_path)
    (tmp_path / "bad.md").write_text(BROKEN, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "bad.md"], check=True)
    r = run(tmp_path)
    assert r.returncode == 1 and "bad.md" in r.stdout, r.stdout + r.stderr


def test_s79_a_new_unignored_md_with_a_broken_block_still_fails(tmp_path):
    repo(tmp_path)
    (tmp_path / "new.md").write_text(BROKEN, encoding="utf-8")
    r = run(tmp_path)
    assert r.returncode == 1 and "new.md" in r.stdout, r.stdout + r.stderr


def test_s79_a_tracked_file_deleted_from_the_tree_does_not_crash(tmp_path):
    repo(tmp_path)
    (tmp_path / "gone.md").write_text(FINE, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "gone.md"], check=True)
    (tmp_path / "gone.md").unlink()
    assert run(tmp_path).returncode == 0


def test_s79_outside_a_git_repo_every_md_is_read_as_before(tmp_path):
    (tmp_path / "bad.md").write_text(BROKEN, encoding="utf-8")
    r = run(tmp_path)
    assert r.returncode == 1 and "bad.md" in r.stdout, r.stdout + r.stderr
