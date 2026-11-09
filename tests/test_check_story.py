"""Story #155: a story names who does it in real life (actor, app or screen, how often) before it is Ready.
The GoServe case: a kitchen-remove feature was built for the cook on the kitchen app, when the owner,
on the admin app, had the pain. Nothing in the story asked who."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_story.py"


def run(body, *args):
    return subprocess.run(["python3", str(SCRIPT), *args], input=body, capture_output=True, text=True)


@pytest.mark.parametrize("body", [
    "## Value\nRemove a kitchen.\n\nWho does it: the admin, on the admin app City screen, about twice a month\n",
    "### Who does it\n\nthe admin, admin app City screen, twice a month\n",   # how a GitHub issue form renders the field
    "- **Who does it:** the cook, kitchen app home, every morning\n",
])
def test_s155_a_story_with_actor_screen_and_how_often_passes(body):
    r = run(body)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout


@pytest.mark.parametrize("body", [
    "## Value\nRemove a kitchen.\n",                                    # no line at all
    "Who does it:\n",                                                  # empty
    "Who does it: <actor>, <app or screen>, <how often>\n",            # template placeholder left in
    "### Who does it\n\n_No response_\n",                              # issue form left blank
    "Who does it: the admin\n",                                        # actor only, no screen, no how often
    "Who does it: the admin, admin app\n",                             # no how often
])
def test_s155_a_story_without_a_full_who_does_it_line_fails_and_says_why(body):
    r = run(body)
    assert r.returncode == 1 and "Who does it" in r.stdout, r.stdout


def test_s155_the_story_template_and_the_issue_form_both_carry_the_field():
    template = (ROOT / "pm" / "agile" / "templates" / "story.md").read_text(encoding="utf-8")
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "user-story.yml").read_text(encoding="utf-8")
    assert "Who does it:" in template
    assert "label: Who does it" in form and form.split("label: Who does it", 1)[1].split("- type:", 1)[0].count("required: true") == 1


def test_s155_ci_checks_every_linked_user_story_issue():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "scripts/check_story.py --pr-body-file" in ci and "issues: read" in ci


def test_s155_check_local_runs_the_story_check():
    text = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "check_story.py" in text and "story)" in text


def test_s155_pr_body_mode_skips_a_body_with_no_linked_issue(tmp_path):
    f = tmp_path / "body.md"
    f.write_text("## What\nNo link.\n", encoding="utf-8")
    r = run("", "--pr-body-file", str(f))
    assert r.returncode == 0, r.stdout
