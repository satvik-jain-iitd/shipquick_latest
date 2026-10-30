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
    for j in ("adoption", "team-block", "frontend-design", "uat-on-main", "environments"):
        assert j in jobs, j


def test_s124_the_adoption_job_fails_on_a_pin_mismatch_and_says_what_to_run():
    section = CHECKS.split("\n  adoption:\n", 1)[1].split("\n  team-block:", 1)[0]
    assert "knowledge/shipquick_latest" in section
    assert "inputs.shipquick_ref" in section
    assert "adopt.sh" in section
    assert "check_local.sh" in section   # the pre-commit-hooks marker, same string adopt.sh itself checks


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
