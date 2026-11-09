"""Story #140: scripts/check_roles.py -- the PR author and every commit author must be a coder
account (the #114 case: a PR opened by the reviewer account). A merge commit (2+ parents) may be
authored by a reviewer or owner account instead -- a dev -> main release PR carries the local
`git merge` commits of whoever did the daily dev-merge (PR #103's shape: klickbae8yt-star and
satvik-jain-iitd both show up as commit authors, and only the review account's commits there are
merges)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_roles as cr  # noqa: E402

CODERS = ["coder-one", "coder-two"]
REVIEWERS = ["reviewer-one"]
OWNER = "owner-one"


def commit(login, parents=1):
    return (login, parents)


def test_a_pr_authored_and_committed_by_coders_passes():
    assert cr.check("coder-one", [commit("coder-one"), commit("coder-two")], CODERS) is None


def test_a_pr_authored_by_the_reviewer_account_fails_the_114_case():
    why = cr.check("reviewer-one", [commit("reviewer-one")], CODERS)
    assert why and "reviewer-one" in why and "not a coder account" in why


def test_a_commit_authored_by_a_non_coder_fails_even_if_the_pr_author_is_fine():
    why = cr.check("coder-one", [commit("coder-one"), commit("reviewer-one")], CODERS)
    assert why and "reviewer-one" in why


def test_dependabot_is_exempt_as_author_and_as_a_commit_author():
    assert cr.check("dependabot[bot]", [commit("dependabot[bot]")], CODERS) is None
    assert cr.check("coder-one", [commit("coder-one"), commit("dependabot[bot]")], CODERS) is None


def test_the_app_dependabot_login_form_is_also_exempt():
    assert cr.check("app/dependabot", [], CODERS) is None


def test_an_empty_commit_authors_list_is_fine_when_the_pr_author_is_a_coder():
    assert cr.check("coder-one", [], CODERS) is None


# ---- story #140 (reviewer): a merge commit may be authored by a reviewer or owner account ----
def test_a_reviewer_authored_merge_commit_passes_pr_103s_shape():
    commits = [commit("coder-one") for _ in range(12)] + [commit("reviewer-one", parents=2) for _ in range(3)]
    assert cr.check("coder-one", commits, CODERS, reviewers=REVIEWERS, owner=OWNER) is None


def test_a_reviewer_authored_non_merge_commit_still_fails():
    why = cr.check("coder-one", [commit("coder-one"), commit("reviewer-one", parents=1)], CODERS, reviewers=REVIEWERS, owner=OWNER)
    assert why and "reviewer-one" in why


def test_an_owner_authored_merge_commit_passes():
    assert cr.check("coder-one", [commit("coder-one"), commit(OWNER, parents=2)], CODERS, reviewers=REVIEWERS, owner=OWNER) is None


def test_a_merge_commit_by_someone_in_neither_role_still_fails():
    why = cr.check("coder-one", [commit("coder-one"), commit("stranger", parents=2)], CODERS, reviewers=REVIEWERS, owner=OWNER)
    assert why and "stranger" in why


def test_with_no_reviewers_or_owner_given_the_old_behavior_is_unchanged():
    why = cr.check("coder-one", [commit("coder-one"), commit("reviewer-one", parents=2)], CODERS)
    assert why and "reviewer-one" in why


def test_cli_exit_codes(capsys):
    assert cr.main(["--author", "coder-one", "--commit-authors", "coder-one:1", "--coders", "coder-one,coder-two"]) == 0
    assert "roles OK" in capsys.readouterr().out
    assert cr.main(["--author", "reviewer-one", "--coders", "coder-one"]) == 1


def test_cli_accepts_reviewers_and_owner_and_allows_a_merge_commit(capsys):
    rc = cr.main([
        "--author", "coder-one",
        "--commit-authors", "coder-one:1,reviewer-one:2",
        "--coders", "coder-one",
        "--reviewers", "reviewer-one",
        "--owner", "owner-one",
    ])
    assert rc == 0
    assert "roles OK" in capsys.readouterr().out


def test_cli_a_bare_login_with_no_colon_is_treated_as_a_non_merge_commit(capsys):
    rc = cr.main([
        "--author", "coder-one",
        "--commit-authors", "coder-one,reviewer-one",
        "--coders", "coder-one",
        "--reviewers", "reviewer-one",
    ])
    assert rc == 1
    assert "reviewer-one" in capsys.readouterr().out


# Story #139 (ADR-011): maker and checker are different sessions, not only different accounts.
CODER_SESSIONS = ["proj-dev"]
REVIEWER_SESSIONS = ["proj-qa"]


def test_with_session_lists_every_commit_must_name_a_coder_session():
    why = cr.check("coder-one", [("coder-one", 1, "proj-qa")], CODERS, coder_sessions=CODER_SESSIONS)
    assert why and "proj-qa" in why and "Built-by" in why


def test_a_commit_with_no_built_by_trailer_fails_and_names_the_fix():
    why = cr.check("coder-one", [("coder-one", 1, "")], CODERS, coder_sessions=CODER_SESSIONS)
    assert why and "Built-by" in why


def test_a_merge_commit_needs_no_session():
    assert cr.check("coder-one", [("coder-one", 1, "proj-dev"), ("reviewer-one", 2, "")], CODERS,
                    REVIEWERS, OWNER, coder_sessions=CODER_SESSIONS) is None


def test_without_session_lists_the_session_is_not_checked():
    assert cr.check("coder-one", [("coder-one", 1, "")], CODERS) is None


def test_an_approval_from_a_reviewer_session_that_built_nothing_passes():
    assert cr.review_session("Reviewed-by: proj-qa\nLooks good.", ["proj-dev"], REVIEWER_SESSIONS) is None


def test_the_teammate_block_header_names_the_reviewer_session():
    body = "```\nTo proj-dev, from proj-qa, re PR #9:\n1. ok\nNothing needed from you.\n```"
    assert cr.review_session(body, ["proj-dev"], REVIEWER_SESSIONS) is None


def test_an_approval_naming_no_session_is_refused():
    why = cr.review_session("LGTM", ["proj-dev"], REVIEWER_SESSIONS)
    assert why and "Reviewed-by" in why


def test_an_approval_from_a_session_that_is_not_a_reviewer_is_refused():
    why = cr.review_session("Reviewed-by: proj-dev", ["proj-dev"], REVIEWER_SESSIONS)
    assert why and "not a reviewer session" in why


def test_the_reviewer_session_that_built_a_commit_cannot_approve_it():
    why = cr.review_session("Reviewed-by: proj-qa", ["proj-dev", "proj-qa"], REVIEWER_SESSIONS)
    assert why and "built" in why and "proj-qa" in why


def test_a_reviewed_by_name_in_backticks_or_with_a_period_is_read():
    assert cr.review_session("Reviewed-by: `proj-qa`.", ["proj-dev"], REVIEWER_SESSIONS) is None
