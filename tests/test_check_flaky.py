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


# ---- #562 review point 2: the check runs before a push, from check_local.sh, on the repo's own registry ----
def local_flaky(tmp_path, entries=None):
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "dev"], check=True)
    if entries is not None:
        (repo / ".shipquick").mkdir()
        (repo / ".shipquick" / "flaky-tests.json").write_text(json.dumps(entries), encoding="utf-8")
    return subprocess.run(["bash", str(ROOT / "scripts" / "check_local.sh"), "flaky"], cwd=repo, capture_output=True, text=True)


def test_check_local_flaky_passes_a_valid_registry_of_the_repo(tmp_path):
    r = local_flaky(tmp_path, [entry()])
    assert r.returncode == 0 and "ok   flaky" in r.stdout, (r.stdout, r.stderr)


def test_check_local_flaky_fails_an_expired_quarantine_of_the_repo(tmp_path):
    r = local_flaky(tmp_path, [entry(expires_on="2020-01-01")])
    assert r.returncode == 1 and "FAIL flaky" in r.stdout, (r.stdout, r.stderr)


def test_check_local_flaky_passes_when_the_repo_has_no_registry(tmp_path):
    """A child has no registry file: a missing file is a pass, never a read of the kit's own file."""
    r = local_flaky(tmp_path)
    assert r.returncode == 0 and "ok   flaky" in r.stdout, (r.stdout, r.stderr)


# ---- #562 review point 3: one short doc says what the registry is and is not ----
def flaky_doc():
    return (ROOT / "docs" / "FLAKY_TESTS.md").read_text(encoding="utf-8")


def test_the_doc_names_every_field_of_a_registry_row():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_flaky
    text = flaky_doc()
    for field in sorted(check_flaky.REQUIRED):
        assert f"`{field}`" in text, field


def test_the_doc_says_it_is_a_list_with_an_expiry_and_not_a_skip_switch():
    text = flaky_doc()
    assert "not a skip switch" in text and "no test runner reads" in text.lower()


def test_the_doc_says_who_adds_a_row_and_what_expired_blocks():
    text = flaky_doc()
    assert ".shipquick/flaky-tests.json" in text and "check_local.sh flaky" in text
    assert "the coder" in text and "protected path" in text and "owner merges" in text
    assert "`quarantined`" in text and "`fixed`" in text and "expires_on" in text and "fails" in text


# ---- story #569: CI runs the check, the doc says so ----
def test_ci_runs_the_flaky_check():
    """AC-1: a step in the pre-commit job (the gate needs it, it runs on a push to dev) runs the check; no pull_request-only if on it."""
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    job = text.split("\n  pre-commit:\n", 1)[1].split("\n  commit-msg:\n", 1)[0]
    i = job.index("python3 scripts/check_flaky.py --file .shipquick/flaky-tests.json")
    step = job[job.rfind("      - ", 0, i):].split("\n      - ", 1)[0]
    assert "if:" not in step, step
    gate = text.split("\n  gate:\n", 1)[1]
    assert "needs: [pre-commit," in gate


def test_the_doc_names_the_optional_fields_and_where_it_runs():
    text = flaky_doc()
    for field in ("tier", "last_failure", "run_url"):
        assert f"`{field}`" in text, field
    assert "before a push and in CI" in text
