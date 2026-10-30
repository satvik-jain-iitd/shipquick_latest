"""Story #140: scripts/check_roles.py -- the PR author and every commit author must be a coder
account (the #114 case: a PR opened by the reviewer account)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_roles as cr  # noqa: E402

CODERS = ["coder-one", "coder-two"]


def test_a_pr_authored_and_committed_by_coders_passes():
    assert cr.check("coder-one", ["coder-one", "coder-two"], CODERS) is None


def test_a_pr_authored_by_the_reviewer_account_fails_the_114_case():
    why = cr.check("reviewer-one", ["reviewer-one"], CODERS)
    assert why and "reviewer-one" in why and "not a coder account" in why


def test_a_commit_authored_by_a_non_coder_fails_even_if_the_pr_author_is_fine():
    why = cr.check("coder-one", ["coder-one", "reviewer-one"], CODERS)
    assert why and "reviewer-one" in why


def test_dependabot_is_exempt_as_author_and_as_a_commit_author():
    assert cr.check("dependabot[bot]", ["dependabot[bot]"], CODERS) is None
    assert cr.check("coder-one", ["coder-one", "dependabot[bot]"], CODERS) is None


def test_the_app_dependabot_login_form_is_also_exempt():
    assert cr.check("app/dependabot", [], CODERS) is None


def test_an_empty_commit_authors_list_is_fine_when_the_pr_author_is_a_coder():
    assert cr.check("coder-one", [], CODERS) is None


def test_cli_exit_codes(capsys):
    assert cr.main(["--author", "coder-one", "--commit-authors", "coder-one", "--coders", "coder-one,coder-two"]) == 0
    assert "roles OK" in capsys.readouterr().out
    assert cr.main(["--author", "reviewer-one", "--coders", "coder-one"]) == 1
