"""Story #124, second layer: scripts/adoption_scan.py flags a child whose default branch has no
shipquick-call.yml, or pins a ShipQuick commit older than 14 days. The gh-api calls are injected
so the decision logic is tested without network."""
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import adoption_scan as scan  # noqa: E402

TODAY = datetime.datetime(2026, 10, 30, tzinfo=datetime.timezone.utc)
FRESH_SHA = "a" * 40
STALE_SHA = "b" * 40


def api(repo_info=None, call_content=None, fresh=True):
    def fetch(path):
        if path == "repos/owner/child":
            return repo_info or {"default_branch": "main"}
        if path.startswith("repos/owner/child/contents/.github/workflows/shipquick-call.yml"):
            return call_content
        if path.startswith(f"repos/{scan.REPO}/commits/"):
            sha = path.rsplit("/", 1)[1]
            days_ago = 1 if fresh else 20
            d = TODAY - datetime.timedelta(days=days_ago)
            return {"commit": {"committer": {"date": d.isoformat().replace("+00:00", "Z")}}}
        return None
    return fetch


def test_adopted_and_fresh_is_none():
    fetch = api(call_content={"content": _b64(f"  shipquick_ref: {FRESH_SHA}\n")}, fresh=True)
    assert scan.check_child("owner/child", fetch, days=14, today=TODAY) is None


def test_no_caller_at_all_is_flagged():
    fetch = api(call_content=None)
    why = scan.check_child("owner/child", fetch, days=14, today=TODAY)
    assert why and "shipquick-call.yml" in why


def test_a_caller_with_no_pin_is_flagged():
    fetch = api(call_content={"content": _b64("name: x\n")})
    why = scan.check_child("owner/child", fetch, days=14, today=TODAY)
    assert why and "pin" in why.lower()


def test_a_stale_pin_over_14_days_is_flagged():
    fetch = api(call_content={"content": _b64(f"  shipquick_ref: {STALE_SHA}\n")}, fresh=False)
    why = scan.check_child("owner/child", fetch, days=14, today=TODAY)
    assert why and "days old" in why


def test_a_pin_exactly_at_the_boundary_is_not_flagged():
    def fetch(path):
        if path == "repos/owner/child":
            return {"default_branch": "main"}
        if path.startswith("repos/owner/child/contents"):
            return {"content": _b64(f"  shipquick_ref: {FRESH_SHA}\n")}
        if path.startswith(f"repos/{scan.REPO}/commits/"):
            d = TODAY - datetime.timedelta(days=14)
            return {"commit": {"committer": {"date": d.isoformat().replace("+00:00", "Z")}}}
        return None
    assert scan.check_child("owner/child", fetch, days=14, today=TODAY) is None


def test_cannot_read_the_child_repo_is_flagged():
    def fetch(path):
        return None
    why = scan.check_child("owner/child", fetch, days=14, today=TODAY)
    assert why and "cannot read" in why.lower()


def test_read_children_strips_comments_and_blanks(tmp_path):
    f = tmp_path / "children.md"
    f.write_text("# header\nowner/a\n\n  owner/b  # trailing comment\n", encoding="utf-8")
    assert scan.read_children(f) == [("owner/a", False), ("owner/b", False)]


def test_read_children_marks_a_line_ending_in_private(tmp_path):
    f = tmp_path / "children.md"
    f.write_text("owner/a\nowner/b private\n", encoding="utf-8")
    assert scan.read_children(f) == [("owner/a", False), ("owner/b", True)]


def test_a_private_child_with_no_token_is_skipped_with_no_issue_filed():
    fetch = api(call_content=None)
    why, should_file = scan.scan_child("owner/child", True, fetch, 14, TODAY, has_token=False)
    assert why and "no" in why and "SHIPQUICK_CHILD_TOKEN" in why
    assert should_file is False


def test_a_private_child_with_a_token_is_checked_normally():
    fetch = api(call_content={"content": _b64(f"  shipquick_ref: {FRESH_SHA}\n")}, fresh=True)
    why, should_file = scan.scan_child("owner/child", True, fetch, 14, TODAY, has_token=True)
    assert why is None
    assert should_file is True


def test_a_public_child_ignores_has_token():
    fetch = api(call_content=None)
    why, should_file = scan.scan_child("owner/child", False, fetch, 14, TODAY, has_token=False)
    assert why and "shipquick-call.yml" in why
    assert should_file is True


def _b64(text):
    import base64
    return base64.b64encode(text.encode()).decode()
