"""Story #186: scripts/check_component_request.py. A custom component needs a component-approved label and an
`Owner yes:` comment, both by a reviewer account. The issue reads are injected, so no network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_component_request as c  # noqa: E402

REV = {"satvik-jain-iitd"}
YES = 'Owner yes: 10 Nov 2026 "haan, bana do"'


def issue(label_by="satvik-jain-iitd", comment_by="satvik-jain-iitd", comment=YES, label="component-approved"):
    events = [{"event": "labeled", "label": {"name": label}, "actor": {"login": label_by}}] if label_by else []
    comments = [{"user": {"login": comment_by}, "body": comment}] if comment_by else []
    return lambda n: {"events": events, "comments": comments}


ROW = {"name": "Stepper", "platform": "android", "base": "Slider", "request": 12, "twin": 13}


def test_s1_a_custom_row_with_no_approval_fails():
    why = c.check_row(ROW, issue(label_by=None, comment_by=None), REV)
    assert why and "component-approved" in why and "12" in why


def test_s2_label_and_owner_yes_comment_by_a_reviewer_pass():
    assert c.check_row(ROW, issue(), REV) is None


def test_label_only_fails_and_names_the_missing_comment():
    why = c.check_row(ROW, issue(comment_by=None), REV)
    assert why and "Owner yes" in why


def test_comment_only_fails_and_names_the_missing_label():
    why = c.check_row(ROW, issue(label_by=None), REV)
    assert why and "label" in why


def test_a_label_added_by_the_coder_does_not_count():
    why = c.check_row(ROW, issue(label_by="klickbae8yt-star"), REV)
    assert why and "label" in why


def test_an_owner_yes_comment_by_the_coder_does_not_count():
    why = c.check_row(ROW, issue(comment_by="klickbae8yt-star"), REV)
    assert why and "Owner yes" in why


def test_a_comment_that_is_not_the_exact_shape_does_not_count():
    assert c.check_row(ROW, issue(comment="Owner yes"), REV)
    assert c.check_row(ROW, issue(comment="looks good, Owner yes: 10 Nov 2026 \"x\""), REV)


def test_a_different_label_does_not_count():
    assert c.check_row(ROW, issue(label="component-request"), REV)


def test_a_row_with_no_request_issue_fails():
    why = c.check_row({"name": "X", "platform": "ios", "base": "Y"}, issue(), REV)
    assert why and "request" in why


def test_s3_parity_lists_a_component_on_one_platform_only():
    rows = [ROW, {"name": "Stepper", "platform": "ios", "base": "Slider", "request": 13}, {"name": "Dial", "platform": "ios", "request": 14}]
    assert c.parity(rows) == {"Dial": ["ios"]}


def test_parity_is_empty_when_every_component_has_a_twin():
    assert c.parity([ROW, {**ROW, "platform": "ios"}]) == {}


def test_main_exits_1_on_a_missing_approval_and_0_on_an_empty_registry(tmp_path):
    reg = tmp_path / "r.json"
    reg.write_text(json.dumps({"components": []}))
    assert c.run(reg, REV, issue()) == 0
    reg.write_text(json.dumps({"components": [ROW]}))
    assert c.run(reg, REV, issue(label_by=None, comment_by=None)) == 1
    assert c.run(reg, REV, issue()) == 0


def test_main_with_no_registry_file_passes_since_a_child_may_have_no_custom_components(tmp_path):
    assert c.run(tmp_path / "none.json", REV, issue()) == 0


def test_the_kit_registry_is_valid_json_with_a_components_list():
    data = json.loads((ROOT / "ui" / "registry.json").read_text())
    assert isinstance(data["components"], list)


def test_the_gate_is_wired_into_ci_and_the_docs_name_it():
    assert "check_component_request.py" in (ROOT / ".github/workflows/ci.yml").read_text()
    assert "check_component_request.py" in (ROOT / "docs/COMPONENT_LIBRARY.md").read_text()
