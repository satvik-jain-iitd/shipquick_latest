"""Flaky registry (M5b)."""
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_flaky.py"


def run(*args, cwd=None):
    return subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd or ROOT)


def entry(**kw):
    base = {
        "test_id": "tests/test_foo.py::test_bar",
        "path": "tests/test_foo.py",
        "owner": "example-owner",
        "issue": "https://github.com/x/y/issues/1",
        "reason": "timing",
        "quarantined_on": date.today().isoformat(),
        "expires_on": (date.today() + timedelta(days=30)).isoformat(),
        "status": "quarantined",
    }
    base.update(kw)
    return base


def test_empty_registry_passes(tmp_path):
    f = tmp_path / "r.json"; f.write_text("[]")
    r = run("--file", str(f))
    assert r.returncode == 0, r.stdout + r.stderr


def test_valid_entry_passes(tmp_path):
    f = tmp_path / "r.json"; f.write_text(json.dumps([entry()]))
    r = run("--file", str(f))
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_required_field_fails(tmp_path):
    e = entry(); del e["owner"]
    f = tmp_path / "r.json"; f.write_text(json.dumps([e]))
    r = run("--file", str(f))
    assert r.returncode == 1 and "missing" in r.stdout


def test_expired_quarantine_fails(tmp_path):
    e = entry(expires_on="2020-01-01")
    f = tmp_path / "r.json"; f.write_text(json.dumps([e]))
    r = run("--file", str(f))
    assert r.returncode == 1 and "expired" in r.stdout


def test_invalid_status_fails(tmp_path):
    e = entry(status="bogus")
    f = tmp_path / "r.json"; f.write_text(json.dumps([e]))
    r = run("--file", str(f))
    assert r.returncode == 1 and "invalid status" in r.stdout


def test_duplicate_test_id_fails(tmp_path):
    f = tmp_path / "r.json"; f.write_text(json.dumps([entry(), entry()]))
    r = run("--file", str(f))
    assert r.returncode == 1 and "duplicate test_id" in r.stdout


def test_missing_registry_passes(tmp_path):
    r = run("--file", str(tmp_path / "nope.json"))
    assert r.returncode == 0, r.stdout + r.stderr


def test_json_output_valid(tmp_path):
    f = tmp_path / "r.json"; f.write_text(json.dumps([entry()]))
    r = run("--file", str(f), "--json")
    d = json.loads(r.stdout)
    assert d["ok"] is True


def test_the_entry_dates_follow_today_so_the_suite_has_no_time_bomb():
    """#562 review point 1: a literal expiry date in entry() fails the whole suite on that day. Dates come from today."""
    body = Path(__file__).read_text(encoding="utf-8").split("def entry(", 1)[1].split("\ndef test_", 1)[0]
    assert "date.today()" in body and "timedelta" in body, body
    assert "2026" not in body and "2025" not in body, body


@pytest.mark.parametrize("status", ["active", "expired"])
def test_statuses_nobody_can_explain_are_rejected(tmp_path, status):
    """#562 review point 4: keep quarantined and fixed; active and expired are not defined anywhere."""
    f = tmp_path / "r.json"; f.write_text(json.dumps([entry(status=status)]))
    r = run("--file", str(f))
    assert r.returncode == 1 and "invalid status" in r.stdout, r.stdout


def test_no_aliased_json_import_and_a_neutral_owner_in_the_test_entry():
    """#562 review point 4: no aliased json import in the script or the test, and no real login as the owner."""
    needle = "import json" + " as "   # built here so this file does not contain it
    for rel in ("scripts/check_flaky.py", "tests/test_check_flaky.py"):
        assert needle not in (ROOT / rel).read_text(encoding="utf-8"), rel
    assert entry()["owner"] == "example-owner"
