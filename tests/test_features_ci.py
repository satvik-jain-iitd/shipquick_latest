"""Story #421 (F4, epic #86): every gated job in checks.yml reads its feature flag from the BASE branch (or the caller's
kit branch), never from the PR head, and a flag that is off makes its job `skipped`. Text checks on the workflow (CI has
no PyYAML) and real git for `features.py flags`."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
FEATURES = ROOT / "scripts" / "features.py"
IDS = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]
JOB_FLAG = {"disable-comments": "disable-comments", "design-tokens": "design-tokens", "roles": "roles", "team-block": "team-block",
            "frontend-design": "frontend-design", "uat-on-main": "uat-on-main", "freeze-on-main": "freeze",
            "environments": "environments", "component-registry": "component-registry", "rule-copies": "rule-copies", "story": "story"}


def job(name):
    body = CHECKS.split("\njobs:\n", 1)[1]
    m = re.search(rf"^  {re.escape(name)}:\s*\n(.*?)(?=^  [a-z][a-z-]*:\s*$|\Z)", body, re.M | re.S)
    assert m, name
    return m.group(1)


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *a], cwd=cwd, capture_output=True, text=True, check=True)


def flags(project, ref):
    return subprocess.run([sys.executable, str(FEATURES), "flags", "--git", str(project), "--ref", ref], capture_output=True, text=True)


def repo(tmp_path, base_features=None):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    if base_features is not None:
        (tmp_path / ".shipquick").mkdir()
        (tmp_path / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": base_features}), encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


def test_flags_reads_the_file_from_the_ref_not_the_working_tree(tmp_path):
    repo(tmp_path, {"roles": {"on": True}})
    (tmp_path / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {"roles": {"on": False}}}), encoding="utf-8")   # the PR head turns it off
    r = flags(tmp_path, "main")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["roles"] is True, "the base says on; the PR's own edit must not count"


def test_flags_with_no_file_on_the_ref_is_every_default_and_locked_ids_are_on(tmp_path):
    repo(tmp_path)
    m = json.loads(flags(tmp_path, "main").stdout)
    assert set(m) == set(IDS) and m["gate"] is True and m["adoption"] is True
    assert m["roles"] is True and m["hosted-roadmap"] is False


def test_flags_fails_with_exit_2_on_a_bad_ref_or_a_broken_file(tmp_path):
    repo(tmp_path)
    r = flags(tmp_path, "origin/nosuch")
    assert r.returncode == 2 and r.stdout.strip() == ""
    (tmp_path / ".shipquick").mkdir()
    (tmp_path / ".shipquick" / "features.json").write_bytes(b"{oops")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "broken")
    r = flags(tmp_path, "main")
    assert r.returncode == 2 and r.stdout.strip() == ""


def test_a_features_job_exists_reads_the_base_and_outputs_the_flags():
    j = job("features")
    assert "if: github.event_name == 'pull_request'" in j
    assert "features.py" in j and "flags" in j and "github.base_ref" in j
    assert "inputs.kit_branch" in j or "KIT_BRANCH" in j
    assert re.search(r"outputs:\s*\n\s+flags: \$\{\{ steps\.\w+\.outputs\.flags \}\}", j)
    assert "github.head_ref" not in j and "pull_request.head" not in j


def test_every_gated_job_needs_features_and_reads_its_own_flag():
    for name, fid in JOB_FLAG.items():
        j = job(name)
        assert re.search(r"needs:\s*(\[features\]|features)(\s|$)", j), name
        assert f"fromJSON(needs.features.outputs.flags)['{fid}']" in j, name
        assert "needs.features.result == 'success'" in j, name


def test_adoption_and_gate_have_no_flag_and_gate_needs_features():
    assert "fromJSON" not in job("adoption")
    g = job("gate")
    assert "fromJSON" not in g
    assert re.search(r"needs: \[[^\]]*\bfeatures\b", g)
    assert 'echo "features: ${{ needs.features.result }}"' in g
    assert "contains(needs.*.result, 'failure')" in g


def test_every_flag_a_job_reads_exists_in_the_defaults_file():
    for fid in re.findall(r"flags\)\['([a-z-]+)'\]", CHECKS):
        assert fid in IDS, fid
