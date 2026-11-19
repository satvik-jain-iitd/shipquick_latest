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


def test_s327_ci_job_is_warn_only_and_since_496_in_the_gate_needs():
    """Story #496 (epic #485 item 16) put the job in the gate's needs. It stays warn-only: continue-on-error makes its result
    success even when the step fails, so the gate cannot be blocked by it."""
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "check_shortcuts.py" in ci
    gate = ci.split("  gate:", 1)[1]
    assert "shortcut-ledger" in gate.split("steps:", 1)[0]
    job = ci.split("  shortcut-ledger:", 1)[1].split("  tdd:", 1)[0]
    head, steps = job.split("    steps:", 1)
    assert "continue-on-error" not in head, "on the job, a failed step may still show a FAILURE check row"
    assert "continue-on-error: true" in steps, "on the step, the job itself ends green"


# ---- review of #338: wrapped comments, string literals, a missing file, a second table ----
import re  # noqa: E402

FOLLOW_HEADER = "| Date | Follow-up | Why it is open | Owner | Status |\n|---|---|---|---|---|\n"


def test_s327_a_wrapped_comment_is_joined_and_the_trigger_on_line_two_counts(tmp_path):
    root = make_repo(tmp_path, {
        "a.py": "# ponytail: reads block-style YAML by indent, one line per hit. A\n# flow-style file is never passed; swap for a parser if that matters.\nx = 1\n",
        "b.js": "// shortcut: linear scan over the list. add an index\n// when the list passes 10000 rows.\nlet y = 1;\n",
    })
    out = run(root).stdout
    lines = [ln for ln in out.splitlines() if ln.startswith(("a.py", "b.js"))]
    assert len(lines) == 2, out
    assert all(" ok " in ln for ln in lines), out
    assert "swap for a parser if that matters" in lines[0] and "when the list passes 10000 rows" in lines[1]
    assert "0 no-trigger" in out


def test_s327_a_new_marker_on_the_next_line_is_its_own_comment(tmp_path):
    root = make_repo(tmp_path, {"a.py": "# shortcut: one. add x when y matters.\n# shortcut: two without a way forward.\n"})
    out = run(root).stdout
    assert out.count("a.py:") == 2 and "1 no-trigger" in out, out


def test_s327_a_marker_inside_a_string_is_not_a_comment_and_a_closer_cuts_the_text(tmp_path):
    root = make_repo(tmp_path, {
        "s.py": 'print("# shortcut: in a string")\nrows = ["    // ponytail: fixed sizes, wrap later.", "    public enum T {"]\n',
        "p.html": "<html><!-- ponytail: inline styles. add a stylesheet when a second page needs it. --></html>\n",
    })
    out = run(root).stdout
    assert "s.py" not in out, out
    line = next(ln for ln in out.splitlines() if ln.startswith("p.html"))
    assert "-->" not in line and "</html>" not in line and "when a second page needs it." in line, line


def test_s327_write_without_a_follow_ups_file_says_so_and_writes_nothing(tmp_path):
    root = make_repo(tmp_path, {"a.py": "# shortcut: x\n"})
    r = run(root, "--write")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "docs/follow-ups.md is missing" in r.stdout
    assert "Traceback" not in r.stderr and not (root / "docs" / "follow-ups.md").exists()


def test_s327_rows_land_right_after_the_follow_ups_table_not_a_later_table(tmp_path):
    fu = ("# Follow-ups\n\n" + FOLLOW_HEADER + "| 2026-11-01 | old row | why | me | open |\n\n"
          "## Closed\n\n| Date | Item |\n|---|---|\n| 2026-10-01 | done thing |\n")
    root = make_repo(tmp_path, {"a.py": "# shortcut: global lock.\n", "docs/follow-ups.md": fu})
    assert run(root, "--write").returncode == 0
    lines = (root / "docs" / "follow-ups.md").read_text(encoding="utf-8").splitlines()
    new = next(i for i, ln in enumerate(lines) if "[sc:" in ln)
    old = next(i for i, ln in enumerate(lines) if "old row" in ln)
    closed = next(i for i, ln in enumerate(lines) if ln.startswith("## Closed"))
    assert old < new < closed, lines


def test_s327_a_follow_ups_file_without_the_header_row_is_refused_clearly(tmp_path):
    root = make_repo(tmp_path, {"a.py": "# shortcut: global lock.\n", "docs/follow-ups.md": "# Follow-ups\n\nnothing here\n"})
    before = (root / "docs" / "follow-ups.md").read_text(encoding="utf-8")
    r = run(root, "--write")
    assert r.returncode == 0 and "header row" in r.stdout, r.stdout
    assert (root / "docs" / "follow-ups.md").read_text(encoding="utf-8") == before


def test_s327_the_ci_job_cannot_block_a_merge_and_check_local_usage_names_it():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    job = re.search(r"^  shortcut-ledger:\n(.*?)(?=^  [a-z][a-z-]*:\n|\Z)", ci, re.M | re.S).group(1)
    assert "continue-on-error: true" in job
    lines = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8").splitlines()
    usage = next(ln for ln in lines if ln.startswith("#   checks:"))
    unknown = next(ln for ln in lines if "unknown check:" in ln)
    assert "shortcuts" in usage and "shortcuts" in unknown
