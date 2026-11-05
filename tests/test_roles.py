"""Story #140: scripts/roles.py -- the one parser for .shipquick/roles.yml. No account name lives
anywhere else; every script that needs one calls this."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import roles  # noqa: E402

GOOD = """coder:
  - account-one
  - account-two
reviewer:
  - account-three
owner: account-three
shipquick_repo: owner/repo
"""


def test_parse_reads_lists_and_scalars():
    data = roles.parse(GOOD)
    assert data == {
        "coder": ["account-one", "account-two"],
        "reviewer": ["account-three"],
        "owner": "account-three",
        "shipquick_repo": "owner/repo",
    }


def test_parse_ignores_comments_and_blank_lines():
    text = "# a header\ncoder:\n  - a\n\n  # inline note\nreviewer:\n  - b\nowner: b\n"
    data = roles.parse(text)
    assert data == {"coder": ["a"], "reviewer": ["b"], "owner": "b"}


def test_parse_of_empty_text_is_an_empty_dict():
    assert roles.parse("") == {}
    assert roles.parse("   \n\n") == {}


def test_load_raises_file_not_found_with_a_clear_reason(tmp_path):
    with pytest.raises(FileNotFoundError, match="adopt.sh"):
        roles.load(str(tmp_path / "no-such-file.yml"))


def test_load_raises_value_error_when_a_required_field_is_missing(tmp_path):
    f = tmp_path / "roles.yml"
    f.write_text("coder:\n  - a\n", encoding="utf-8")   # no reviewer, no owner
    with pytest.raises(ValueError, match="reviewer"):
        roles.load(str(f))


def test_load_succeeds_when_coder_reviewer_and_owner_are_all_set(tmp_path):
    f = tmp_path / "roles.yml"
    f.write_text(GOOD, encoding="utf-8")
    data = roles.load(str(f))
    assert data["coder"] == ["account-one", "account-two"]


def test_cli_get_coder_prints_accounts_comma_separated(tmp_path, capsys):
    f = tmp_path / "roles.yml"
    f.write_text(GOOD, encoding="utf-8")
    assert roles.main(["get", "coder", "--file", str(f)]) == 0
    assert capsys.readouterr().out.strip() == "account-one,account-two"


def test_cli_get_owner_prints_the_scalar(tmp_path, capsys):
    f = tmp_path / "roles.yml"
    f.write_text(GOOD, encoding="utf-8")
    assert roles.main(["get", "owner", "--file", str(f)]) == 0
    assert capsys.readouterr().out.strip() == "account-three"


def test_cli_get_shipquick_repo_prints_the_scalar(tmp_path, capsys):
    f = tmp_path / "roles.yml"
    f.write_text(GOOD, encoding="utf-8")
    assert roles.main(["get", "shipquick_repo", "--file", str(f)]) == 0
    assert capsys.readouterr().out.strip() == "owner/repo"


def test_cli_get_a_field_not_in_the_file_exits_1(tmp_path, capsys):
    f = tmp_path / "roles.yml"
    f.write_text(GOOD, encoding="utf-8")   # no shipquick_repo omitted here -- try removing it
    f.write_text(GOOD.replace("shipquick_repo: owner/repo\n", ""), encoding="utf-8")
    assert roles.main(["get", "shipquick_repo", "--file", str(f)]) == 1
    assert "not set" in capsys.readouterr().err


def test_cli_missing_file_exits_1_with_a_clear_message(tmp_path, capsys):
    assert roles.main(["get", "coder", "--file", str(tmp_path / "missing.yml")]) == 1
    assert "adopt.sh" in capsys.readouterr().err


# ---- no account name lives in the scripts that decide who may code, review or merge ----
ACCOUNTS = ("satvik-jain-iitd", "klickbae8yt-star")
GATE_FILES = (
    "scripts/roles.py",
    "scripts/role.sh",
    "scripts/mode.sh",
    "scripts/review_merge.sh",
    "scripts/check_roles.py",
)


@pytest.mark.parametrize("rel", GATE_FILES)
def test_s140_no_account_name_lives_in_a_gate_script(rel):
    """These scripts decide who may code, review or merge: they must read .shipquick/roles.yml
    through roles.py, never carry an account literal of their own. (Other files -- adopt.sh,
    feedback.sh, freeze.sh, adoption_scan.py, ci.yml, checks.yml -- keep a default ShipQuick
    home-repo or build-account name behind SHIPQUICK_REPO/SHIPQUICK_BUILD_USER or a workflow input
    default; that default is a convenience for a fork, not a role decision, so it is out of scope
    here.)"""
    text = (ROOT / rel).read_text(encoding="utf-8")
    for acct in ACCOUNTS:
        assert acct not in text, f"{rel} hardcodes {acct}"
