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


# ---- story #454: the secrets check reads the commits being pushed, not the history below the base ----
FAKE_PAT = "ghp_" + "aB3dE5gH7jK9mN1pQ3sT5vW7yZ9bC1dE3fG5"   # shaped like a GitHub token, made up


def secrets_repo(tmp_path, old_secret, pushed_secret):
    repo = tmp_path / "r"
    repo.mkdir()
    g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    g("init", "-q", "-b", "dev"); g("config", "user.email", "t@example.com"); g("config", "user.name", "t")
    (repo / "old.py").write_text(f'token = "{FAKE_PAT}"\n' if old_secret else "x = 1\n", encoding="utf-8")
    g("add", "-A"); g("commit", "-q", "-m", "chore: base")
    g("update-ref", "refs/remotes/origin/dev", "HEAD")
    g("checkout", "-q", "-b", "chore/bump")
    (repo / "new.py").write_text(f'token = "{FAKE_PAT}"\n' if pushed_secret else "y = 2\n", encoding="utf-8")
    g("add", "-A"); g("commit", "-q", "-m", "chore: pushed")
    return repo


@pytest.mark.skipif(not __import__("shutil").which("gitleaks"), reason="gitleaks is not installed")
def test_s454_an_old_finding_below_the_base_does_not_block_a_clean_push(tmp_path):
    r = local(secrets_repo(tmp_path, old_secret=True, pushed_secret=False), "secrets")
    assert r.returncode == 0 and "ok   secrets" in r.stdout, r.stdout + r.stderr


@pytest.mark.skipif(not __import__("shutil").which("gitleaks"), reason="gitleaks is not installed")
def test_s454_a_finding_in_a_pushed_commit_still_fails(tmp_path):
    r = local(secrets_repo(tmp_path, old_secret=False, pushed_secret=True), "secrets")
    assert r.returncode == 1 and "FAIL secrets" in r.stdout, r.stdout + r.stderr


def fake_gitleaks(tmp_path):
    """A stand-in gitleaks that only records its arguments, so the range logic is tested on a machine without it."""
    b = tmp_path / "fakebin"
    b.mkdir()
    g = b / "gitleaks"
    g.write_text('#!/usr/bin/env bash\necho "$@" > "%s"\nexit 0\n' % (tmp_path / "gl.args"), encoding="utf-8")
    g.chmod(0o755)
    return b


def test_s454_secrets_passes_the_pushed_range_to_gitleaks(tmp_path):
    repo = secrets_repo(tmp_path, old_secret=False, pushed_secret=False)
    env = {**__import__("os").environ, "PATH": f"{fake_gitleaks(tmp_path)}:{__import__('os').environ['PATH']}"}
    r = subprocess.run(["bash", str(LOCAL), "secrets"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "--log-opts origin/dev..HEAD" in (tmp_path / "gl.args").read_text(encoding="utf-8")


def test_s454_secrets_scans_the_whole_history_when_there_is_no_origin_base(tmp_path):
    repo = tmp_path / "plain"
    subprocess.run(["git", "init", "-q", "-b", "dev", str(repo)], check=True)
    env = {**__import__("os").environ, "PATH": f"{fake_gitleaks(tmp_path)}:{__import__('os').environ['PATH']}"}
    r = subprocess.run(["bash", str(LOCAL), "secrets"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "--log-opts" not in (tmp_path / "gl.args").read_text(encoding="utf-8")
