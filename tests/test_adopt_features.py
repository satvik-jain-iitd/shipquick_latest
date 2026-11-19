"""Story #420 (F3, epic #86): adopt.sh writes `.shipquick/features.json` with every default, keeps the owner's values on a
second run, adds only new ids, and honours `pre-commit` and `roadmap` when they are off. Real git in a tmp child; no network."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adopt import adopt, snapshot  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]


@pytest.fixture
def child(tmp_path):
    c = tmp_path / "kid"
    (c / ".github" / "workflows").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "dev", str(c)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=c, check=True)   # the CI runner has no git identity
    subprocess.run(["git", "config", "user.name", "Test"], cwd=c, check=True)
    (c / ".github" / "workflows" / "ci.yml").write_text("name: Kid CI\non:\n  push:\n", encoding="utf-8")
    return c


def feats(c):
    return json.loads((c / ".shipquick" / "features.json").read_text(encoding="utf-8"))["features"]


def test_first_run_writes_every_feature_at_its_default(child):
    r = adopt(child)
    assert r.returncode == 0, r.stderr
    f = feats(child)
    assert set(f) == set(DEFAULTS)
    assert all(f[k] == {"on": d["default"], "default": d["default"]} for k, d in DEFAULTS.items())
    assert "created   .shipquick/features.json" in r.stdout


def test_a_second_run_keeps_the_owners_values_and_writes_nothing(child):
    adopt(child)
    f = feats(child)
    f["lanes"]["on"] = False
    (child / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": f}, indent=2) + "\n", encoding="utf-8")
    before = snapshot(child)
    r = adopt(child)
    assert r.returncode == 0 and snapshot(child) == before
    assert feats(child)["lanes"]["on"] is False
    assert "unchanged .shipquick/features.json" in r.stdout


def test_a_new_kit_id_is_added_at_its_default_and_printed(child):
    adopt(child)
    f = feats(child)
    del f["rule-copies"]
    (child / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": f}), encoding="utf-8")
    r = adopt(child)
    assert "added feature rule-copies (on)" in r.stdout
    assert feats(child)["rule-copies"] == {"on": True, "default": True}


def test_an_id_the_kit_dropped_is_kept_and_printed_as_ignored(child):
    adopt(child)
    f = feats(child)
    f["old-thing"] = {"on": True, "default": True}
    (child / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": f}), encoding="utf-8")
    r = adopt(child)
    assert "old-thing" in r.stdout and "unknown to this kit, ignored" in r.stdout
    assert feats(child)["old-thing"]["on"] is True


def test_pre_commit_off_installs_no_hooks_and_roadmap_off_writes_no_caller(child):
    (child / ".shipquick").mkdir()
    (child / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {"pre-commit": {"on": False, "default": True}, "roadmap": {"on": False, "default": True}}}), encoding="utf-8")
    r = adopt(child)
    assert r.returncode == 0, r.stderr
    assert not (child / ".pre-commit-config.yaml").exists()
    assert not (child / ".github" / "workflows" / "roadmap-call.yml").exists()
    assert "skipped: pre-commit is off" in r.stdout and "skipped: roadmap is off" in r.stdout
    assert (child / ".github" / "workflows" / "shipquick-call.yml").exists(), "the checks caller is never optional"


def test_a_broken_features_file_stops_adopt_before_it_writes_anything(child):
    (child / ".shipquick").mkdir()
    (child / ".shipquick" / "features.json").write_bytes(b"{oops")
    before = snapshot(child)
    r = adopt(child)
    assert r.returncode == 2 and "features" in r.stderr and snapshot(child) == before


# ---- review of #434: the locked adoption check must accept "pre-commit is off" ----
from test_adopt import add_fake_submodule, gh, with_origin, HEAD  # noqa: E402,F401


def _off(c, **flags):
    (c / ".shipquick").mkdir(exist_ok=True)
    f = {k: {"on": v, "default": True} for k, v in flags.items()}
    (c / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": f}), encoding="utf-8")


def test_check_accepts_pre_commit_off_and_says_hooks_skipped(child, gh):
    with_origin(child)
    _off(child, **{"pre-commit": False})
    assert adopt(child).returncode == 0
    add_fake_submodule(child, HEAD)
    r = adopt(child, "--check", env=gh)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "no ShipQuick hooks" not in r.stdout
    assert "hooks skipped: pre-commit is off" in r.stdout


def test_check_still_fails_a_missing_hook_when_pre_commit_is_on(child, gh):
    with_origin(child)
    adopt(child)
    add_fake_submodule(child, HEAD)
    (child / ".pre-commit-config.yaml").unlink()   # after the commit: with no config the hooks refuse one (story #479)
    r = adopt(child, "--check", env=gh)
    assert r.returncode == 1 and "no ShipQuick hooks" in r.stdout


def test_check_fails_with_the_readers_message_when_the_features_file_is_broken(child, gh):
    with_origin(child)
    adopt(child)
    add_fake_submodule(child, HEAD)
    (child / ".shipquick" / "features.json").write_bytes(b"{oops")
    r = adopt(child, "--check", env=gh)
    assert r.returncode == 1 and "features" in r.stdout and "not valid JSON" in r.stdout
