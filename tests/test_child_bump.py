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


def test_the_script_has_no_apply():
    src = (ROOT / "scripts" / "child_bump.py").read_text()
    assert "--apply" not in src and "write_text" not in src


def test_the_fixtures_use_made_up_names_only():
    import re
    text = Path(__file__).read_text()
    owners = re.findall(r"([\w.-]+)/child-[a-z]\b", text)
    assert owners and all(o.endswith("example-org") for o in owners)


def test_each_child_costs_two_reads_in_read_pin_and_in_check_child():
    import datetime
    calls = []
    inner = fake_fetch({"child-a": OLD})

    def counting(path):
        calls.append(path)
        return inner(path)

    scan.read_pin("example-org/child-a", counting)
    assert len(calls) == 2
    calls.clear()
    scan.check_child("example-org/child-a", counting, 14, datetime.datetime.now(datetime.timezone.utc))
    assert [c for c in calls if "contents" in c or c == "repos/example-org/child-a"] == calls[:2]
    assert calls[:2].count("repos/example-org/child-a") == 1 and len([c for c in calls if "shipquick-call.yml" in c]) == 1


WF = ROOT / ".github" / "workflows" / "child-bump-plan.yml"


def test_a_private_child_is_read_with_the_child_token(tmp_path):
    reg = tmp_path / "children.md"
    reg.write_text("example-org/child-a private\nexample-org/child-b\n")
    seen = []
    inner = fake_fetch({"child-a": OLD, "child-b": OLD})

    def fetch(path, token=None):
        seen.append((path, token))
        return inner(path)

    assert cb.run(str(reg), NEW, fetch, token="T0KEN") == 0
    assert seen and all(t == "T0KEN" for p, t in seen if "child-a" in p)
    assert all(t is None for p, t in seen if "child-b" in p)


def test_the_workflow_runs_the_planner_on_a_release_tag():
    text = WF.read_text()
    assert 'tags: ["v*"]' in text and "workflow_dispatch:" in text and "tag:" in text
    assert "timeout-minutes:" in text and "uses: actions/checkout@" in text
    assert "python3 scripts/child_bump.py --release-sha" in text
    assert "${{ inputs.tag" not in text.split("run:", 1)[1]  # the tag goes through env, never into script text
    assert "SHIPQUICK_CHILD_TOKEN: ${{ secrets.SHIPQUICK_CHILD_TOKEN }}" in text


def test_the_workflow_is_read_only_and_writes_nothing():
    text = WF.read_text()
    assert "permissions:\n  contents: read\n" in text and "write" not in text.replace("writes", "")
    for word in ("gh issue", "gh pr", "git push", "upload-artifact", "git branch"):
        assert word not in text


def test_the_workflow_fails_on_a_tag_with_no_commit():
    text = WF.read_text()
    assert 'git rev-parse --verify "refs/tags/$TAG^{commit}"' in text
    assert '-z "$TAG"' in text and "exit 1" in text
    assert "|| true" not in text and "continue-on-error" not in text


def test_the_workflow_step_keeps_the_planner_exit_code():
    text = WF.read_text()
    assert "set -o pipefail" in text and "GITHUB_STEP_SUMMARY" in text
    assert "|| true" not in text and "continue-on-error" not in text


def test_the_workflow_step_has_the_workflow_token_for_public_children():
    # without GH_TOKEN, gh cannot read any public child on a runner and every child is `unread`
    text = WF.read_text()
    assert "GH_TOKEN: ${{ github.token }}" in text.split("env:", 1)[1].split("run:", 1)[0]
