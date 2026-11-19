"""Story #124: .github/workflows/checks.yml is the reusable workflow every child calls; it carries
every PR gate (team block, Closes, design-first, UAT on main, environments) plus an adoption job
that fails loudly on a pin mismatch or missing pre-commit hooks. shipquick-call.yml is ShipQuick's
own template, kept inert (workflow_dispatch) so it never breaks ShipQuick's own CI."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
CALL_TEMPLATE = (ROOT / ".github" / "workflows" / "shipquick-call.yml").read_text(encoding="utf-8")


def _jobs(text):
    return re.findall(r"^  ([a-z][a-z-]*):\s*$", text.split("\njobs:\n", 1)[1], re.M)


def test_s124_checks_yml_is_a_workflow_call_with_a_required_ref_input():
    on_block = CHECKS.split("\npermissions:", 1)[0]
    assert re.search(r"^  workflow_call:\s*$", on_block, re.M)
    section = on_block.split("shipquick_ref:", 1)[1]
    assert re.search(r"^\s*required:\s*true\s*$", section, re.M)


def test_s124_checks_yml_has_every_gate_as_its_own_job():
    jobs = _jobs(CHECKS)
    for j in ("adoption", "disable-comments", "team-block", "frontend-design", "uat-on-main", "freeze-on-main", "environments", "gate"):
        assert j in jobs, j


# ---- story #131: harden the merge gate ----
def test_s131_checks_yml_has_a_gate_job_that_needs_every_other_job():
    gate = CHECKS.split("\n  gate:\n", 1)[1]
    needs = re.search(r"needs: \[([^\]]*)\]", gate).group(1)
    for j in ("adoption", "disable-comments", "team-block", "frontend-design", "uat-on-main", "freeze-on-main", "environments"):
        assert j in needs, j
    assert "if: always()" in gate
    assert "contains(needs.*.result, 'failure')" in gate and "contains(needs.*.result, 'cancelled')" in gate


def test_s131_the_adoption_job_checks_the_pin_is_an_ancestor_or_a_tag():
    section = CHECKS.split("\n  adoption:\n", 1)[1].split("\n  disable-comments:", 1)[0]
    assert "check_adoption_ancestor.py" in section
    assert "inputs.shipquick_repo" in section and "inputs.shipquick_ref" in section


def test_s131_disable_comments_job_runs_on_every_pr_and_reuses_the_script():
    section = CHECKS.split("\n  disable-comments:\n", 1)[1].split("\n  team-block:", 1)[0]
    assert "if: github.event_name == 'pull_request'" in section
    assert "check_disable_comments.py" in section


def test_s126_the_freeze_job_is_scoped_to_main_and_reuses_check_freeze():
    section = CHECKS.split("\n  freeze-on-main:\n", 1)[1].split("\n  environments:", 1)[0]
    assert "github.base_ref == 'main'" in section
    assert "check_freeze.py" in section
    assert ".shipquick/freeze" in section


def test_s124_the_adoption_job_fails_on_a_pin_mismatch_and_says_what_to_run():
    section = CHECKS.split("\n  adoption:\n", 1)[1].split("\n  team-block:", 1)[0]
    assert "knowledge/shipquick_latest" in section
    assert "inputs.shipquick_ref" in section
    assert "adopt.sh" in section
    assert "check_local.sh" in section   # the pre-commit-hooks marker, same string adopt.sh itself checks


def test_s146_the_adoption_job_checks_screens_txt_is_wired_into_the_childs_own_ci():
    section = CHECKS.split("\n  adoption:\n", 1)[1].split("\n  disable-comments:", 1)[0]
    assert "check_screens_wired.py" in section
    assert "project/docs/screens.txt" in section and "project/.github/workflows" in section


def test_s124_frontend_design_and_uat_jobs_reuse_the_same_scripts_as_ci_yml():
    assert "check_frontend_design.sh" in CHECKS
    assert "check_uat.py" in CHECKS and "has_dev_link.sh" in CHECKS
    assert "check_environments.sh" in CHECKS


def test_s124_shipquick_call_template_is_inert_here_and_points_at_checks_yml():
    on_block = CALL_TEMPLATE.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
    assert re.search(r"^  workflow_dispatch:\s*$", on_block, re.M)
    assert "pull_request" not in on_block
    assert "uses: ./.github/workflows/checks.yml" in CALL_TEMPLATE
    assert "shipquick_ref: ${{ github.sha }}" in CALL_TEMPLATE


# ---- story #225: kit_branch, so a rule-24 child keeps only the caller on main ----
def test_s225_checks_yml_takes_an_optional_kit_branch_input():
    on_block = CHECKS.split("\npermissions:", 1)[0]
    section = on_block.split("kit_branch:", 1)[1]
    assert "type: string" in section and "default: ''" in section and "required: true" not in section


def test_s225_the_adoption_job_reads_the_pin_and_hooks_from_the_kit_branch_not_the_checkout():
    section = CHECKS.split("\n  adoption:\n", 1)[1].split("\n  disable-comments:", 1)[0]
    assert "KIT_BRANCH: ${{ inputs.kit_branch }}" in section   # via env, never pasted into the script
    assert "git -C project fetch" in section
    assert 'rev-parse -q --verify "$ref:knowledge/shipquick_latest"' in section
    assert 'show "$ref:.pre-commit-config.yaml"' in section


def test_s225_the_roles_job_reads_roles_yml_from_the_kit_branch_too():
    section = CHECKS.split("\n  roles:\n", 1)[1].split("\n  team-block:", 1)[0]
    assert "KIT_BRANCH: ${{ inputs.kit_branch }}" in section
    assert 'branches/$KIT_BRANCH' in section and 'contents/.shipquick/roles.yml?ref=$1' in section


def test_s225_the_roles_job_says_clearly_when_the_kit_branch_or_its_roles_yml_is_missing():
    # review of PR #227, fix 3
    section = CHECKS.split("\n  roles:\n", 1)[1].split("\n  team-block:", 1)[0]
    assert "kit branch $KIT_BRANCH not found" in section
    assert "no .shipquick/roles.yml on branch $ref" in section


# ---- review of #335: a rule-24 child keeps its rules on its kit branch ----
def _job_block(text, name):
    m = re.search(r"^  " + re.escape(name) + r":\n(.*?)(?=^  [a-z][a-z-]*:\n|\Z)", text, re.M | re.S)
    assert m, f"job {name} not found"
    return m.group(1)


def test_s316_rule_copies_reads_the_child_claude_md_from_the_kit_branch():
    text = (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
    job = _job_block(text, "rule-copies")
    assert "KIT_BRANCH: ${{ inputs.kit_branch }}" in job
    assert "TARGET: ${{ github.base_ref }}" in job
    assert 'git -C project show "$ref:CLAUDE.md"' in job
    assert "skills" in job.split("sparse-checkout:", 1)[1], "the phrase check needs the skills folder"


# ---- story #175: the story check reaches children ----
def test_s175_checks_yml_has_a_story_job_that_runs_check_story_with_issues_read():
    job = _job_block(CHECKS, "story")
    assert "if: github.event_name == 'pull_request'" in job
    assert "issues: read" in job   # a reusable workflow cannot read issues unless the job asks and the caller grants it
    assert "check_story.py --pr-body-file" in job
    assert "GH_TOKEN: ${{ github.token }}" in job and "GH_REPO: ${{ github.repository }}" in job   # the child's own issues, never the kit's


def test_s175_the_gate_needs_the_story_job_and_echoes_its_result():
    gate = CHECKS.split("\n  gate:\n", 1)[1]
    needs = re.search(r"needs: \[([^\]]*)\]", gate).group(1)
    assert "story" in [n.strip() for n in needs.split(",")]
    assert 'echo "story: ${{ needs.story.result }}"' in gate


# ---- story #576: the intent gate reaches children ----
def test_checks_yml_runs_the_intent_gate_on_a_childs_pr():
    job = _job_block(CHECKS, "intent-verify")
    assert "if: github.event_name == 'pull_request'" in job
    assert "timeout-minutes:" in job
    assert "check_intent_verify.py --pr-body-file" in job and '--reviewers "$reviewers"' in job
    assert "PR_AUTHOR: ${{ github.event.pull_request.user.login }}" in job
    assert "PR_BODY: ${{ github.event.pull_request.body }}" in job
    assert "GH_TOKEN: ${{ github.token }}" in job and "GH_REPO: ${{ github.repository }}" in job
    assert "roles.py get reviewer --file" in job


def test_the_intent_job_reads_its_own_flag_and_the_gate_waits_for_it():
    job = _job_block(CHECKS, "intent-verify")
    assert "needs: [features]" in job
    assert "fromJSON(needs.features.outputs.flags)['intent-verify']" in job
    assert "['roles']" not in job   # the roles feature can be off in a child
    gate = CHECKS.split("\n  gate:\n", 1)[1]
    needs = re.search(r"needs: \[([^\]]*)\]", gate).group(1)
    assert "intent-verify" in [n.strip() for n in needs.split(",")]
    assert 'echo "intent-verify: ${{ needs.intent-verify.result }}"' in gate


def test_the_intent_job_reads_reviewers_from_the_kit_branch():
    job = _job_block(CHECKS, "intent-verify")
    assert "KIT_BRANCH: ${{ inputs.kit_branch }}" in job
    assert "TARGET: ${{ github.base_ref }}" in job
    assert '"$KIT_BRANCH" != "$TARGET"' in job
    assert 'branches/$KIT_BRANCH' in job and 'contents/.shipquick/roles.yml?ref=$1' in job
    assert "kit branch $KIT_BRANCH not found" in job


def test_a_missing_roles_file_gives_the_intent_job_an_empty_reviewer_list():
    job = _job_block(CHECKS, "intent-verify")
    assert 'reviewers=$(python3 .shipquick/scripts/roles.py get reviewer --file "$roles_file" || true)' in job
    assert "exit 1" in job.split("not found", 1)[1].split("\n", 1)[0]   # a missing kit branch still fails
    step = job.split("Read roles.yml", 1)[1].split("- name: Check a reviewer", 1)[0]
    miss = step.split("(the reviewer list stays empty)", 1)[1].split("\n", 1)[0]
    assert "exit" not in miss   # no hard exit on a missing file


def test_the_intent_job_asks_for_issues_read_only():
    job = _job_block(CHECKS, "intent-verify")
    perms = job.split("permissions:", 1)[1].split("env:", 1)[0]
    assert "issues: read" in perms and "contents: read" in perms
    assert "write" not in perms


def test_the_intent_flag_words_say_a_child_runs_it():
    for f in ("scripts/features_default.json", "docs/FEATURES.md", "docs/decisions/ADR-021.md"):
        text = (ROOT / f).read_text(encoding="utf-8")
        assert "Kit CI only" not in text and "The check is kit CI only" not in text, f
        assert "child's CI" in text, f


# ---- story #577: the AC trace reaches children ----
def test_checks_yml_runs_the_ac_trace_on_the_childs_own_tree():
    job = _job_block(CHECKS, "ac-trace")
    assert "if: github.event_name == 'pull_request'" in job
    assert "timeout-minutes:" in job
    assert "check_ac_trace.py --pr-body-file" in job and "--root project" in job
    assert "path: project" in job and "persist-credentials: false" in job
    assert "path: .shipquick" in job


def test_the_ac_trace_job_reads_its_own_flag_and_the_gate_waits_for_it():
    job = _job_block(CHECKS, "ac-trace")
    assert "needs: [features]" in job
    assert "fromJSON(needs.features.outputs.flags)['ac-trace']" in job
    gate = CHECKS.split("\n  gate:\n", 1)[1]
    needs = re.search(r"needs: \[([^\]]*)\]", gate).group(1)
    assert "ac-trace" in [n.strip() for n in needs.split(",")]
    assert 'echo "ac-trace: ${{ needs.ac-trace.result }}"' in gate


def test_the_ac_trace_job_asks_for_issues_read_only():
    job = _job_block(CHECKS, "ac-trace")
    perms = job.split("permissions:", 1)[1].split("env:", 1)[0]
    assert "issues: read" in perms and "contents: read" in perms and "write" not in perms
    assert "GH_TOKEN: ${{ github.token }}" in job and "GH_REPO: ${{ github.repository }}" in job
    assert "PR_BODY: ${{ github.event.pull_request.body }}" in job


# ---- story #589: roles.yml comes from the base branch, never from the pull request ----
import os
import subprocess
import tempfile

_JOBS = ("roles", "intent-verify")


def _read_step(job):
    blk = _job_block(CHECKS, job).split("Read roles.yml", 1)[1]
    return blk.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0]


def _run_read(job, gh_script, kit="", target="main"):
    """Runs the real shell of the read step with a fake `gh` that logs its args and answers by `gh_script`."""
    with tempfile.TemporaryDirectory() as d:
        gh = Path(d) / "gh"
        gh.write_text('#!/bin/bash\necho "$*" >> "$RUNNER_TEMP/calls"\n' + gh_script, encoding="utf-8")
        gh.chmod(0o755)
        env = {**os.environ, "PATH": f"{d}:{os.environ['PATH']}", "RUNNER_TEMP": d, "GH_REPO": "o/r",
               "KIT_BRANCH": kit, "TARGET": target, "HEAD_SHA": "abc123"}
        r = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", _read_step(job)], env=env, capture_output=True, text=True)
        roles = Path(d, "roles.yml")
        calls = Path(d, "calls").read_text() if Path(d, "calls").exists() else ""
        return r, (roles.read_text() if roles.exists() else None), calls


_BASE_OK = 'case "$*" in *ref=main*) echo "reviewer: [base]"; exit 0;; *ref=abc123*) echo "reviewer: [pr]"; exit 0;; esac; exit 1'
_NOT_FOUND = 'echo "gh: Not Found (HTTP 404)" >&2; exit 1'


def test_the_roles_and_intent_jobs_read_roles_yml_from_the_base_branch():
    for j in _JOBS:
        blk = _job_block(CHECKS, j)
        assert "project/.shipquick/roles.yml" not in blk, j
        assert "TARGET: ${{ github.base_ref }}" in blk and "GH_TOKEN: ${{ github.token }}" in blk, j
        assert 'gh api -H "Accept: application/vnd.github.raw" "repos/$GH_REPO/contents/.shipquick/roles.yml?ref=$1"' in blk, j
        r, roles, calls = _run_read(j, _BASE_OK)
        assert r.returncode == 0 and "ref=main" in calls and "ref=abc123" not in calls and "[base]" in roles, (j, r.stderr)


def test_the_roles_and_intent_jobs_still_read_the_kit_branch_when_it_is_set():
    script = 'case "$*" in *branches/kitb*) exit 0;; *ref=kitb*) echo "reviewer: [kit]"; exit 0;; esac; exit 1'
    for j in _JOBS:
        r, roles, calls = _run_read(j, script, kit="kitb")
        assert r.returncode == 0 and "[kit]" in roles and "ref=main" not in calls, (j, r.stderr)
        r, roles, calls = _run_read(j, _NOT_FOUND, kit="gone")
        assert r.returncode == 1 and "kit branch gone not found" in r.stdout, j


def test_the_roles_and_intent_jobs_do_not_check_out_the_project():
    for j in _JOBS:
        blk = _job_block(CHECKS, j)
        assert "Check out the project" not in blk and "path: project" not in blk and "git fetch" not in blk and "git -C" not in blk, j


def test_a_base_branch_with_no_roles_file_fails_closed():
    r, roles, _ = _run_read("roles", _NOT_FOUND)   # base and PR head both without the file
    assert r.returncode == 1 and "no .shipquick/roles.yml on branch main" in r.stdout and roles is None
    r, roles, _ = _run_read("intent-verify", _NOT_FOUND)
    assert r.returncode == 0 and "no .shipquick/roles.yml on branch main" in r.stdout and roles is None
    # a kit branch with no file never falls back to the PR's own file
    kit = 'case "$*" in *branches/*) exit 0;; esac; ' + _NOT_FOUND
    r, roles, calls = _run_read("roles", kit, kit="kitb")
    assert r.returncode == 1 and "branch kitb" in r.stdout and "abc123" not in calls


def test_the_roles_and_intent_jobs_ask_for_no_write_permission():
    for j in _JOBS:
        assert "write" not in _job_block(CHECKS, j).split("steps:", 1)[0], j
    assert "GH_REPO: ${{ github.repository }}" in _job_block(CHECKS, "roles").split("steps:", 1)[0]


def test_the_prs_own_roles_file_is_read_only_on_a_404_from_the_base():
    first = 'case "$*" in *ref=abc123*) echo "reviewer: [pr]"; exit 0;; esac; ' + _NOT_FOUND
    for j in _JOBS:
        r, roles, calls = _run_read(j, first)
        assert r.returncode == 0 and "[pr]" in roles and "ref=abc123" in calls, j
        assert "first roles file: the base branch has none, reading the pull request's own" in r.stdout, j
        # a 500, or a missing token, never reads the PR's own file
        for bad in ('echo "gh: Internal Server Error (HTTP 500)" >&2; exit 1',
                    'echo "gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN" >&2; exit 4'):
            r, roles, calls = _run_read(j, 'case "$*" in *ref=abc123*) echo "reviewer: [pr]"; exit 0;; esac; ' + bad)
            assert "abc123" not in calls and roles is None and r.returncode == (1 if j == "roles" else 0), (j, bad)
