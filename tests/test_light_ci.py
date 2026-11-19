"""Story #592: light CI. A PR whose base is a train/ branch skips the six heavy jobs; the gate says so."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
LIGHT = "github.event_name == 'pull_request' && startsWith(github.base_ref, 'train/')"
HEAVY = {"test": None, "ui-android-compile": "android", "ui-android-lint": "android",
         "ui-ios-compile": "ios", "ui-ios-lint": "ios", "ui-ios-snapshots": "snapshot"}


def _job(name):
    body = CI.split("\njobs:\n", 1)[1]
    m = re.search(rf"^  {re.escape(name)}:\n(.*?)(?=^  [a-z][a-z-]*:\n|\Z)", body, re.M | re.S)
    assert m, name
    return m.group(1)


def _if(name):
    m = re.search(r"^    if: (.*)$", _job(name), re.M)
    return m.group(1) if m else ""


def test_the_six_heavy_jobs_do_not_run_on_a_light_run():
    for name, area in HEAVY.items():
        cond = _if(name)
        assert f"!({LIGHT})" in cond, name
        if area:
            assert f"needs.ui-changes.outputs.{area} != 'false'" in cond, name


def test_the_light_run_rule_reads_the_base_branch_never_the_head():
    assert "head_ref" not in LIGHT
    assert all("head_ref" not in ln for ln in CI.splitlines() if "train/" in ln)
    assert CI.count(LIGHT) == 9  # six heavy jobs, the gate change-map step, the gate LIGHT env, the gate name


def test_the_gate_on_a_light_run_says_so_and_still_fails_on_a_failed_job():
    gate = _job("gate")
    assert "if: always()" in gate
    step = gate.split("change_map.py gate")[0].rsplit("- name:", 1)[1]
    assert f"if: ${{{{ !({LIGHT}) }}}}" in step
    assert "light run: the heavy jobs did not run; they run on the train pull request into dev" in gate
    assert "toJSON(needs)" in gate
    assert "contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')" in gate


def test_the_gate_on_a_full_run_needs_test_to_succeed():
    gate = _job("gate")
    assert "TEST_RESULT: ${{ needs.test.result }}" in gate
    assert 'LIGHT: ${{ ' + LIGHT + ' }}' in gate
    assert '"$TEST_RESULT" != "success"' in gate


def test_the_cheap_jobs_and_checks_yml_are_not_touched():
    assert "startsWith(github.base_ref" not in (ROOT / ".github/workflows/checks.yml").read_text(encoding="utf-8")
    jobs = re.findall(r"^  ([a-z][a-z-]*):\s*$", CI.split("\njobs:\n", 1)[1], re.M)
    for name in set(jobs) - set(HEAVY) - {"gate"}:
        assert "startsWith(github.base_ref" not in _job(name), name


def test_the_adr_and_the_rule_page_name_the_trade():
    adr = (ROOT / "docs/decisions/ADR-023.md").read_text(encoding="utf-8")
    for word in ("What gets weaker", "How to undo", "What stays safe"):
        assert word in adr
    assert "## 17. Light CI and the train" in (ROOT / "docs/PR_RULES.md").read_text(encoding="utf-8")


def test_a_light_run_never_makes_a_check_named_gate():
    # dev's branch protection reads a check named exactly `gate` by commit; a light result must not carry that name
    name = re.search(r"^    name: (.*)$", _job("gate"), re.M).group(1)
    assert LIGHT in name and "'gate-light'" in name and "'gate'" in name
    assert name.index("'gate-light'") < name.index("|| 'gate'")
