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
