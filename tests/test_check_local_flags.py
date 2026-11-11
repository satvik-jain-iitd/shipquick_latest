"""Story #423 (F6, epic #86): check_local.sh skips each check whose feature is off and says `skipped: <id> is off`, the same
words CI's features job prints. A broken features file fails the run; it never reads as on. Real git, a tmp project."""
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "scripts" / "check_local.sh"
CHECKS_YML = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")


@pytest.fixture
def proj(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "dev", str(tmp_path)], check=True)
    return tmp_path


def local(cwd, *checks):
    return subprocess.run(["bash", str(LOCAL), *checks], cwd=cwd, capture_output=True, text=True)


def flags(proj, **f):
    (proj / ".shipquick").mkdir(exist_ok=True)
    (proj / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {k: {"on": v} for k, v in f.items()}}), encoding="utf-8")


def test_a_check_whose_feature_is_off_is_skipped_with_the_ci_words(proj):
    flags(proj, **{"rule-copies": False})
    r = local(proj, "rule-copies")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "skipped: rule-copies is off" in r.stdout and "ok   rule-copies" not in r.stdout and "FAIL" not in r.stdout


def test_the_same_check_runs_when_its_feature_is_on_or_no_file_exists(proj):
    r = local(proj, "rule-copies")                       # no file: default on, the check really runs
    assert "skipped" not in r.stdout and ("ok   rule-copies" in r.stdout or "FAIL rule-copies" in r.stdout)
    flags(proj, **{"rule-copies": True})
    assert "skipped" not in local(proj, "rule-copies").stdout


def test_only_the_named_feature_is_skipped(proj):
    flags(proj, **{"rule-copies": False})
    r = local(proj, "rule-copies", "md-blocks")
    assert "skipped: rule-copies is off" in r.stdout and "ok   md-blocks" in r.stdout


def test_every_flagged_check_maps_to_a_real_feature():
    t = LOCAL.read_text(encoding="utf-8")
    ids = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]
    m = re.search(r"feature_of\(\) \{(.*?)\n\}", t, re.S)
    assert m, "feature_of() is missing"
    mapped = dict(re.findall(r"^\s*([a-z-]+)\) echo ([a-z-]+) ;;", m.group(1), re.M))
    assert {"rule-copies", "story", "design-tokens", "disable-comments", "frontend-design", "roadmap", "ui-registry"} <= set(mapped)
    for check, fid in mapped.items():
        assert fid in ids and not ids[fid].get("locked"), (check, fid)


def test_a_broken_features_file_fails_the_run_never_reads_as_on(proj):
    (proj / ".shipquick").mkdir()
    (proj / ".shipquick" / "features.json").write_bytes(b"{oops")
    r = local(proj, "rule-copies")
    assert r.returncode == 1 and "FAIL features" in r.stdout and "not valid JSON" in r.stdout


def test_ci_prints_the_same_words_for_a_skipped_feature():
    assert 'print("skipped: %s is off" % k)' in CHECKS_YML
