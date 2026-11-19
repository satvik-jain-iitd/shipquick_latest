"""Story #580: a dry-run planner that says which child needs a new kit pin. The fetch is a small fake; no network."""
import base64
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import adoption_scan as scan  # noqa: E402
import child_bump as cb  # noqa: E402

OLD = "a" * 40
NEW = "b" * 40
CALL = "repos/example-org/{}/contents/.github/workflows/shipquick-call.yml?ref=main"


def call_file(sha):
    return {"content": base64.b64encode(f"with:\n  shipquick_ref: {sha}\n".encode()).decode()}


def fake_fetch(pins):
    def fetch(path):
        for name, sha in pins.items():
            if path == f"repos/example-org/{name}":
                return {"default_branch": "main"}
            if path == CALL.format(name):
                return call_file(sha) if sha else None
        return None
    return fetch


def test_a_pin_that_differs_from_the_release_is_a_bump():
    rows = cb.plan([("example-org/child-a", OLD, "")], NEW)
    assert rows == [("example-org/child-a", "bump", f"{OLD} -> {NEW}")]


def test_a_pin_equal_to_the_release_is_current():
    assert cb.plan([("example-org/child-a", NEW, "")], NEW)[0][1] == "current"


def test_an_unread_child_is_named_and_the_run_exits_1(tmp_path, capsys):
    reg = tmp_path / "children.md"
    reg.write_text("example-org/child-a\nexample-org/child-b\n")
    fetch = fake_fetch({"child-a": OLD, "child-b": None})
    rc = cb.run(str(reg), NEW, fetch)
    out = capsys.readouterr().out
    assert rc == 1
    assert "example-org/child-a" in out and "bump" in out
    assert "example-org/child-b" in out and "unread" in out
    assert out.strip().splitlines()[-1] == "summary: 1 bump, 0 current, 1 unread"


def test_a_missing_or_empty_registry_exits_1(tmp_path, capsys):
    assert cb.run(str(tmp_path / "nope.md"), NEW, fake_fetch({})) == 1
    assert "nope.md" in capsys.readouterr().err
    empty = tmp_path / "children.md"
    empty.write_text("just prose\n")
    assert cb.run(str(empty), NEW, fake_fetch({})) == 1
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "child_bump.py"), "--release-sha", "xyz"], capture_output=True)
    assert r.returncode == 2


def test_the_planner_reuses_the_scan_reader_and_pin():
    src = (ROOT / "scripts" / "child_bump.py").read_text()
    assert "adoption_scan" in src and "read_children" in src and "read_pin" in src
    assert "re.compile" not in src and "CHILD_LINE" not in src
    assert scan.read_pin("example-org/child-a", fake_fetch({"child-a": OLD})) == (OLD, "")
    sha, why = scan.read_pin("example-org/child-b", fake_fetch({"child-b": None}))
    assert sha is None and "shipquick-call.yml" in why


def test_the_script_reads_no_token_and_has_no_apply():
    src = (ROOT / "scripts" / "child_bump.py").read_text()
    assert "environ" not in src and "getenv" not in src and "TOKEN" not in src.upper()
    assert "--apply" not in src


def test_the_fixtures_use_made_up_names_only():
    import re
    text = Path(__file__).read_text()
    owners = set(re.findall(r"\b([\w.-]+)/(?:child-[a-z])\b", text))
    assert owners == {"example-org"}
