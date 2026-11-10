"""Story #186: scripts/check_component_request.py. A custom component needs its request issue to carry, live:
the label `component-approved` (last label event by a reviewer, label still on the issue), and a reviewer comment
`Owner yes: <YYYY-MM-DD> "<3+ words>"` dated at most 14 days ago and never edited. Reviewers come from roles.py;
the repo from `gh repo view`. Issue reads are injected: no network."""
import datetime
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_component_request as c  # noqa: E402

YES = 'Owner yes: 2026-11-10 "haan, bana do ab"'
REV = {"alice"}
ROW = {"name": "Stepper", "platform": "android", "base": "Slider", "request": 12, "twin": 13}


def issue(labeled_by="alice", label_live=True, comment_by="alice", comment=YES, edited=False, unlabel=False,
          created="2026-11-10T09:00:00Z", title="Stepper: a slider with steps"):
    events = []
    if labeled_by is not None:
        events.append({"event": "labeled", "label": {"name": "component-approved"}, "actor": {"login": labeled_by}})
    if unlabel:
        events.append({"event": "unlabeled", "label": {"name": "component-approved"}, "actor": {"login": "alice"}})
    labels = [{"name": "component-approved"}] if label_live else []
    comments = []
    if comment_by is not None:
        updated = "2026-11-10T10:00:00Z" if edited else created
        comments.append({"user": {"login": comment_by}, "body": comment, "created_at": created, "updated_at": updated})
    data = {"title": title, "labels": labels, "events": events, "comments": comments}
    return lambda n: data


def test_s1_a_custom_row_with_no_approval_fails():
    why = c.check_row(ROW, issue(labeled_by=None, label_live=False, comment_by=None), REV)
    assert why and "component-approved" in why and "12" in why


def test_s2_label_and_owner_yes_by_a_reviewer_pass():
    assert c.check_row(ROW, issue(), REV) is None


def test_label_only_fails_and_names_the_missing_comment():
    why = c.check_row(ROW, issue(comment_by=None), REV)
    assert why and "Owner yes" in why


def test_comment_only_fails_and_names_the_missing_label():
    why = c.check_row(ROW, issue(labeled_by=None, label_live=False), REV)
    assert why and "label" in why


def test_a_label_added_by_the_coder_does_not_count():
    assert c.check_row(ROW, issue(labeled_by="coder"), REV)


def test_an_owner_yes_comment_by_the_coder_does_not_count():
    assert c.check_row(ROW, issue(comment_by="coder"), REV)


def test_a_label_removed_after_approval_does_not_count():
    why = c.check_row(ROW, issue(label_live=False, unlabel=True), REV)
    assert why and "label" in why


def test_a_label_still_live_but_last_event_unlabeled_does_not_count():
    assert c.check_row(ROW, issue(label_live=True, unlabel=True), REV)


@pytest.mark.parametrize("body", [
    "Owner yes",
    'Owner yes: 10 Nov 2026 "haan bana do ab"',
    'Owner yes: 2026-11-10 "two words"',
    'Owner yes: 2026-11-10 "haan, bana do" and more text',
    'looks good. Owner yes: 2026-11-10 "haan bana do ab"',
    'Owner yes: 2026-13-45 "haan bana do ab"',
])
def test_a_comment_outside_the_exact_shape_does_not_count(body):
    assert c.check_row(ROW, issue(comment=body), REV)


def test_a_yes_older_than_14_days_at_the_time_it_was_written_does_not_count_and_14_days_does():
    # the window is counted from the comment's own created_at, not from the day CI runs
    old = "2026-10-26"   # 15 days before the comment
    assert c.check_row(ROW, issue(comment=f'Owner yes: {old} "haan bana do ab"', created="2026-11-10T09:00:00Z"), REV)
    edge = "2026-10-27"  # 14 days
    assert c.check_row(ROW, issue(comment=f'Owner yes: {edge} "haan bana do ab"', created="2026-11-10T09:00:00Z"), REV) is None


def test_a_yes_stays_valid_on_a_later_ci_run():
    # written 10 Nov, checked on 20 Dec: the 14-day window is not counted from today, so it still passes
    assert c.check_row(ROW, issue(created="2026-11-10T09:00:00Z", comment='Owner yes: 2026-11-10 "haan bana do ab"'), REV) is None


def test_the_date_allows_one_day_of_slack_for_utc_and_ist():
    # the comment is 20:00 UTC on 10 Nov, which is 11 Nov in IST: a yes written 11 Nov is fine, 12 Nov is not
    assert c.check_row(ROW, issue(created="2026-11-10T20:00:00Z", comment='Owner yes: 2026-11-11 "haan bana do ab"'), REV) is None
    assert c.check_row(ROW, issue(created="2026-11-10T20:00:00Z", comment='Owner yes: 2026-11-12 "haan bana do ab"'), REV)


def test_a_row_name_must_be_in_the_request_issue_title():
    why = c.check_row(ROW, issue(title="Dial: a rotary control"), REV)
    assert why and "title" in why and "Stepper" in why
    assert c.check_row(ROW, issue(title="stepper: the slider with steps"), REV) is None


def test_an_edited_yes_comment_does_not_count():
    assert c.check_row(ROW, issue(edited=True), REV)


def test_null_users_and_actors_fail_cleanly_and_do_not_raise():
    fetch = lambda n: {"title": "Stepper: a slider with steps", "labels": [{"name": "component-approved"}],
                       "events": [{"event": "labeled", "label": {"name": "component-approved"}, "actor": None}],
                       "comments": [{"user": None, "body": YES, "created_at": "x", "updated_at": "x"}]}
    why = c.check_row(ROW, fetch, REV)
    assert why and "label" in why and "Owner yes" in why


def test_a_row_with_no_request_issue_fails():
    why = c.check_row({"name": "X", "platform": "ios", "base": "Y"}, issue(), REV)
    assert why and "request" in why


def test_s3_parity_lists_a_component_on_one_platform_only():
    rows = [ROW, {"name": "Stepper", "platform": "ios", "base": "Slider", "request": 13}, {"name": "Dial", "platform": "ios", "request": 14}]
    assert c.parity(rows) == {"Dial": ["ios"]}


def test_parity_is_empty_when_every_component_has_a_twin():
    assert c.parity([ROW, {**ROW, "platform": "ios"}]) == {}


def test_run_exits_0_for_an_empty_registry_and_1_for_an_unapproved_row(tmp_path):
    reg = tmp_path / "r.json"
    reg.write_text(json.dumps({"components": []}))
    assert c.run(reg, REV, issue()) == 0
    reg.write_text(json.dumps({"components": [ROW]}))
    assert c.run(reg, REV, issue(labeled_by=None, label_live=False, comment_by=None)) == 1
    assert c.run(reg, REV, issue()) == 0


def test_no_registry_file_passes_since_a_child_may_have_no_custom_components(tmp_path):
    assert c.run(tmp_path / "none.json", REV, issue()) == 0


def test_reviewers_come_from_the_roles_file_not_from_a_name_in_the_script(tmp_path):
    roles = tmp_path / "roles.yml"
    roles.write_text("coder:\n  - bob\nreviewer:\n  - alice\nowner: alice\n", encoding="utf-8")
    assert c.reviewers_from(roles) == {"alice"}


def test_repo_comes_from_gh_repo_view():
    def runner(cmd, **kw):
        assert cmd[:3] == ["gh", "repo", "view"]
        return subprocess.CompletedProcess(cmd, 0, stdout="someone/child\n", stderr="")
    assert c.repo_name(runner) == "someone/child"


def test_the_script_names_no_account_and_no_repo():
    src = (ROOT / "scripts" / "check_component_request.py").read_text(encoding="utf-8")
    assert "satvik-jain-iitd" not in src and "shipquick_latest" not in src


def test_the_kit_registry_is_valid_json_with_a_components_list():
    data = json.loads((ROOT / "ui" / "registry.json").read_text())
    assert isinstance(data["components"], list)


def test_the_gate_is_wired_into_both_ci_files_and_the_docs_name_it():
    for f in [".github/workflows/ci.yml", ".github/workflows/checks.yml"]:
        assert "check_component_request.py" in (ROOT / f).read_text(encoding="utf-8"), f
    assert "ui-registry" in (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "component-registry" in (ROOT / ".github/workflows/checks.yml").read_text(encoding="utf-8")
    assert "check_component_request.py" in (ROOT / "docs/COMPONENT_LIBRARY.md").read_text(encoding="utf-8")
