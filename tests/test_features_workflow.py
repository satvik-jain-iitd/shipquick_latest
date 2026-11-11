"""Story #422 (F5, epic #86): a check that every job in checks.yml is wired to exactly one feature flag, so a new job cannot
escape the switch, and that a disabled job is skipped, never failed. `scripts/check_features_wiring.py` is the check; it also
runs in scripts/check_local.sh (rule 29)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_features_wiring as W  # noqa: E402

CHECKS = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
DEFAULTS = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]


def test_the_real_workflow_has_no_wiring_problems():
    assert W.problems(CHECKS, DEFAULTS) == []


def test_every_gated_job_maps_to_one_unlocked_flag_and_the_gate_needs_it():
    jobs = W.gated_jobs(CHECKS)
    assert set(jobs) >= {"roles", "team-block", "story", "freeze-on-main"}
    assert {"features", "adoption", "gate"}.isdisjoint(jobs)
    for name, fid in jobs.items():
        assert fid in DEFAULTS and not DEFAULTS[fid].get("locked"), name
    gate_needs = W.gate_needs(CHECKS)
    assert set(jobs) <= set(gate_needs) and "features" in gate_needs


def test_a_flag_off_skips_only_its_own_job():
    jobs = W.gated_jobs(CHECKS)
    for name, fid in jobs.items():
        flags = {k: True for k in DEFAULTS}
        flags[fid] = False
        for other in jobs:
            ran = W.job_runs(CHECKS, other, flags, event="pull_request", base_ref="main")
            assert ran == (other != name), (name, other)


def test_a_job_added_with_no_flag_fails_naming_the_job():
    bad = CHECKS.replace("\n  gate:\n", "\n  sneaky-new-check:\n    runs-on: ubuntu-latest\n    timeout-minutes: 10\n    if: github.event_name == 'pull_request'\n    steps:\n      - run: echo hi\n  gate:\n", 1)
    out = W.problems(bad, DEFAULTS)
    assert any("sneaky-new-check" in p for p in out), out


def test_a_job_that_names_an_unknown_or_locked_flag_fails():
    unknown = CHECKS.replace("['roles']", "['nosuch']", 1)
    assert any("nosuch" in p for p in W.problems(unknown, DEFAULTS))
    locked = CHECKS.replace("['roles']", "['gate']", 1)
    assert any("locked" in p for p in W.problems(locked, DEFAULTS))


def test_a_job_the_gate_does_not_wait_for_fails():
    bad = CHECKS.replace("needs: [adoption, features, disable-comments,", "needs: [adoption, features,", 1)
    assert any("disable-comments" in p and "gate" in p for p in W.problems(bad, DEFAULTS))


def test_the_gate_fails_only_on_failure_or_cancelled_never_on_skipped():
    assert W.problems(CHECKS.replace("contains(needs.*.result, 'cancelled')", "contains(needs.*.result, 'skipped')", 1), DEFAULTS)
    assert W.problems(CHECKS.replace("contains(needs.*.result, 'failure') ||", "contains(needs.*.result, 'failure') || contains(needs.*.result, 'skipped') ||", 1), DEFAULTS)


def test_the_cli_exits_0_on_the_real_workflow_and_1_with_the_problem_named(tmp_path):
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_features_wiring.py")], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    f = tmp_path / "checks.yml"
    f.write_text(CHECKS.replace("\n  gate:\n", "\n  sneaky:\n    runs-on: ubuntu-latest\n    steps:\n      - run: x\n  gate:\n", 1), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_features_wiring.py"), "--workflow", str(f)], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 1 and "sneaky" in r.stdout


def test_check_local_runs_it():
    t = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "check_features_wiring.py" in t and "features-wiring" in t
