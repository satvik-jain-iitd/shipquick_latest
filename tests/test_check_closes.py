"""S0.17: the pull request body must link its issue with Closes #n (story #70). The script reads the body on stdin."""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_closes.py"
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


def run(body, title="feat(x): a story (#70)", author="klickbae8yt-star"):
    return subprocess.run(["python3", str(SCRIPT), "--title", title, "--author", author], input=body, capture_output=True, text=True)


def test_s17_a_body_with_closes_and_a_number_passes():
    r = run("## What\nSomething.\n\nCloses #70\n")
    assert r.returncode == 0 and "OK" in r.stdout


@pytest.mark.parametrize("body", ["Fixes #70\n", "Resolves #70\n", "closed #70\n", "Closes #70 and fixes #5\n"])
def test_s17_fixes_and_resolves_count_like_the_closer_script_so_the_two_use_one_rule(body):
    assert run(body).returncode == 0


def test_s17_check_closes_imports_the_link_regex_of_close_linked_issues():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "from close_linked_issues import LINK" in text and "CLOSES" not in text and "re.compile(" in text   # the exempt-title regex stays; there is no second link regex


@pytest.mark.parametrize("body", ["", "## What\nSomething.\n", "See #70 for the story.\n", "Closes #\n", "Closes #N\n", "- [x] Issue linked with `Closes #N`\n", "Disclosesure #70\n"])
def test_s17_a_body_without_a_real_closes_line_fails_and_says_why(body):
    r = run(body)
    assert r.returncode == 1 and "Closes #" in r.stdout


@pytest.mark.parametrize("title", ["release: v0.5.0 Process v2 (#41)", "chore: merge main into dev before v0.5.0 (#41)", "chore(deps): bump the github-actions group with 6 updates", "release(v0.6.0): notes"])
def test_s17_release_sync_and_chore_pull_requests_are_exempt_by_title_prefix(title):
    assert run("no link here\n", title=title).returncode == 0


@pytest.mark.parametrize("title", ["feat: release the thing (#1)", "fix: chore removal", "docs: release notes", "Release v1", "chorefix: x"])
def test_s17_a_title_that_only_mentions_the_word_is_not_exempt(title):
    assert run("no link here\n", title=title).returncode == 1


def test_s17_dependabot_is_exempt_whatever_its_title_says():
    assert run("bumps x\n", title="Bump x from 1 to 2", author="dependabot[bot]").returncode == 0
    assert run("bumps x\n", title="Bump x from 1 to 2", author="someone-else").returncode == 1


def test_s17_the_team_block_job_runs_the_check_with_the_title_author_and_body():
    job = CI.split("\n  team-block:\n", 1)[1].split("\n  secret-scan:", 1)[0]
    assert "scripts/check_closes.py" in job and "PR_TITLE" in job and "PR_AUTHOR" in job and "PR_BODY" in job
    assert '--title "$PR_TITLE"' in job and '--author "$PR_AUTHOR"' in job   # through env, never expanded into the script text


def test_s17_the_pr_rules_and_the_template_name_the_exemptions():
    rules = (ROOT / "docs" / "PR_RULES.md").read_text(encoding="utf-8")
    assert "check_closes.py" in rules and "release:" in rules and "chore:" in rules and "dependabot" in rules.lower()
    assert "Fixes" in rules and "Resolves" in rules
    assert "Closes #" in (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")


def test_s17_idea_224_is_taken():
    ideas = (ROOT / "docs" / "ideas.md").read_text(encoding="utf-8")
    assert re.search(r"ID224:.*\(taken", ideas)
