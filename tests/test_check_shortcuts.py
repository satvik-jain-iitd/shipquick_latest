"""Story #327 (A11): the shortcut ledger lists every shortcut: or ponytail: comment in tracked source,
tags one with no upgrade trigger as no-trigger, and --write logs each shortcut once in docs/follow-ups.md."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_shortcuts.py"
GOOD = "y = 1  # shortcut: naive linear scan; add a dict index when the list passes 10000 rows."
BAD = "z = 2  # shortcut: global lock for every write."


def make_repo(tmp: Path, files: dict) -> Path:
    for rel, text in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
    return tmp


def run(root: Path, *args):
    return subprocess.run(["python3", str(SCRIPT), "--root", str(root), *args], capture_output=True, text=True)


def test_s327_one_good_and_one_no_trigger_comment_are_listed_and_only_the_second_is_tagged(tmp_path):
    root = make_repo(tmp_path, {
        "app/job.py": GOOD + "\n" + BAD + "\n",
        "tests/test_job.py": "# shortcut: a test fixture, not source\n",
        "vendor/lib.py": "# ponytail: vendored code\n",
        "app/notes.md": "# ponytail: docs are not source\n",
    })
    r = run(root)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("app/job.py:")]
    assert r.returncode == 0, r.stdout + r.stderr
    assert len(lines) == 2, r.stdout
    good = next(ln for ln in lines if ":1:" in ln)
    bad = next(ln for ln in lines if ":2:" in ln)
    assert "no-trigger" not in good, good
    assert "no-trigger" in bad, bad
    assert "tests/" not in r.stdout and "vendor/" not in r.stdout and "notes.md" not in r.stdout, r.stdout
    assert "shortcut ledger: 2 comment(s), 1 no-trigger" in r.stdout, r.stdout


def test_s327_write_appends_one_row_per_shortcut_once_and_never_edits_old_rows(tmp_path):
    root = make_repo(tmp_path, {
        "app/job.py": GOOD + "\n" + BAD + "\n",
        "docs/follow-ups.md": "# Follow-ups\n\n| Date | Follow-up | Why it is open | Owner | Status |\n|---|---|---|---|---|\n| 2026-11-10 | old row | why | owner | open |\n",
    })
    fu = root / "docs" / "follow-ups.md"
    before = fu.read_text(encoding="utf-8")
    assert run(root, "--write").returncode == 0
    after_one = fu.read_text(encoding="utf-8")
    assert after_one.startswith(before.rstrip("\n")), "old rows must stay as they were"
    added = after_one[len(before.rstrip("\n")):].strip().splitlines()
    assert len(added) == 2 and all(ln.startswith("| ") for ln in added), added
    assert sum("no-trigger" in ln for ln in added) == 1
    assert run(root, "--write").returncode == 0
    assert fu.read_text(encoding="utf-8") == after_one, "a second --write must add nothing"


def test_s327_the_real_repo_scan_runs_and_prints_the_count():
    r = subprocess.run(["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0 and "shortcut ledger:" in r.stdout, r.stdout + r.stderr


def test_s327_check_local_warns_with_the_count_and_never_fails():
    text = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "check_shortcuts.py" in text and "shortcuts)" in text


def test_s327_ci_job_is_warn_only_and_not_in_the_gate():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "check_shortcuts.py" in ci
    gate = ci.split("  gate:", 1)[1]
    assert "shortcut-ledger" not in gate.split("steps:", 1)[0]
