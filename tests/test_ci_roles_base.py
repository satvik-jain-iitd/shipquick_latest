"""Story #590: the kit's own ci.yml reads roles.yml from the base branch, never from the PR's tree
(step 2 of 2; step 1 is checks.yml, story #589)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
READ = 'gh api -H "Accept: application/vnd.github.raw" "repos/$GH_REPO/contents/.shipquick/roles.yml?ref=$BASE"'


def _job(name):
    return CI.split(f"\n  {name}:\n", 1)[1].split("\n  uat-checklist:\n" if name == "team-block" else "\n  team-block:\n", 1)[0]


def _intent_step():
    return CI.split("- name: Check every linked user story has intent verified by QA (ADR-021)", 1)[1].split("\n      - name:", 1)[0]


def _reads_base(text):
    assert "BASE: ${{ github.base_ref }}" in text
    assert READ in text and '> "$RUNNER_TEMP/roles.yml"' in text
    assert "no .shipquick/roles.yml on branch $BASE" in text


def test_the_roles_job_reads_roles_yml_from_the_base_branch():
    job = _job("roles")
    assert "GH_REPO: ${{ github.repository }}" in job
    _reads_base(job)
    gets = re.findall(r"roles\.py get .*", job)
    assert len(gets) == 4 and all('--file "$RUNNER_TEMP/roles.yml"' in g for g in gets)


def test_the_intent_step_reads_reviewers_from_the_base_branch():
    step = _intent_step()
    assert "GH_REPO: ${{ github.repository }}" in step
    _reads_base(step)
    gets = re.findall(r"roles\.py get .*", step)
    assert len(gets) == 1
    # no roles.py get in the whole file is left without --file
    assert all('--file "$RUNNER_TEMP/roles.yml"' in g for g in re.findall(r"roles\.py get .*", CI))


def test_a_base_branch_with_no_roles_file_fails_at_once():
    for text in (_job("roles"), _intent_step()):
        assert "|| true" not in text
        assert "404" not in text and "HEAD_SHA" not in text and "kit_branch" not in text  # no first-adoption fallback
        assert re.search(r'no \.shipquick/roles\.yml on branch \$BASE.*\n\s*echo "\$err"\n\s*exit 1', text)


def test_roles_py_is_a_protected_path():
    lines = (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()
    assert "scripts/roles.py" in lines
