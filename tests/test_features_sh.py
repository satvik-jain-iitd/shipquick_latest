"""Story #419 (F2, epic #86): the owner sets a feature with one line he types himself, like mode.sh.
`scripts/features.sh get|set`, real git in a tmp repo. `set` is the only writer; it goes through features.py."""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SH = ROOT / "scripts" / "features.sh"


def sh(cwd, *args):
    return subprocess.run(["bash", str(SH), *args], cwd=cwd, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "dev", str(tmp_path)], check=True)
    return tmp_path


def test_get_lists_every_feature_and_get_id_prints_one(repo):
    r = sh(repo, "get")
    assert r.returncode == 0
    lines = dict(l.split(None, 1) for l in r.stdout.strip().splitlines())
    assert lines["roadmap"] == "on" and lines["hosted-roadmap"] == "off" and lines["gate"] == "on"
    r = sh(repo, "get", "hosted-roadmap")
    assert (r.returncode, r.stdout.strip()) == (1, "off")


def test_set_rewrites_the_file_and_says_the_owner_merges_a_pr(repo):
    r = sh(repo, "set", "roadmap", "off")
    assert r.returncode == 0, r.stderr
    assert "protected path" in r.stdout and "owner merges" in r.stdout
    data = json.loads((repo / ".shipquick" / "features.json").read_text(encoding="utf-8"))
    assert data["features"] == {"roadmap": {"on": False}}   # only the id being set: untouched ids keep following the kit
    assert sh(repo, "get", "roadmap").returncode == 1
    sh(repo, "set", "roadmap", "on")
    assert sh(repo, "get", "roadmap").returncode == 0


def test_set_keeps_other_values_and_unknown_ids(repo):
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {"old-thing": {"on": True, "default": True}, "lanes": {"on": False, "default": True}}}), encoding="utf-8")
    assert sh(repo, "set", "roadmap", "off").returncode == 0
    f = json.loads((repo / ".shipquick" / "features.json").read_text(encoding="utf-8"))["features"]
    assert f["lanes"]["on"] is False and f["old-thing"]["on"] is True and f["roadmap"]["on"] is False


def test_locked_features_refuse_and_name_the_reason(repo):
    for fid in ("gate", "adoption"):
        r = sh(repo, "set", fid, "off")
        assert r.returncode == 1 and "locked" in r.stderr and fid in r.stderr
        assert not (repo / ".shipquick" / "features.json").exists()


def test_bad_id_or_word_refuses_with_usage(repo):
    for args in (("set", "nosuch", "off"), ("set", "roadmap", "maybe"), ("set", "roadmap"), ("set",), ("frob",)):
        r = sh(repo, *args)
        assert r.returncode == 2 and "usage" in r.stderr.lower(), (args, r.stderr)
    assert not (repo / ".shipquick" / "features.json").exists()


def test_a_broken_file_is_never_overwritten(repo):
    (repo / ".shipquick").mkdir()
    p = repo / ".shipquick" / "features.json"
    p.write_text("{oops", encoding="utf-8")
    r = sh(repo, "set", "roadmap", "off")
    assert r.returncode == 2 and p.read_text(encoding="utf-8") == "{oops"


def test_the_docs_say_agents_only_get_and_the_owner_types_set():
    t = SH.read_text(encoding="utf-8")
    assert "Agents only run `get`" in t and "! bash" in t


def test_every_command_exits_2_on_an_invalid_utf8_file_never_1(repo):
    """Exit 1 means off (review of #431): a crash must never read as off."""
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "features.json").write_bytes(b'{"features": {}}\n\xff')
    for args in (("get", "roadmap"), ("get",), ("set", "roadmap", "off")):
        r = sh(repo, *args)
        assert r.returncode == 2 and r.stdout.strip() == "" and "Traceback" not in r.stderr, (args, r.returncode, r.stderr)


def test_features_sh_is_a_protected_path():
    import fnmatch
    globs = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    assert any(fnmatch.fnmatchcase("scripts/features.sh", g) for g in globs)


def test_set_pins_only_the_id_it_sets(repo):
    sh(repo, "set", "roadmap", "off")
    sh(repo, "set", "lanes", "off")
    f = json.loads((repo / ".shipquick" / "features.json").read_text(encoding="utf-8"))["features"]
    assert set(f) == {"roadmap", "lanes"}


def test_set_writes_atomically_a_failed_replace_leaves_the_old_file_and_no_temp(repo, monkeypatch):
    import os
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import features
    sh(repo, "set", "roadmap", "off")
    p = repo / ".shipquick" / "features.json"
    before = p.read_text(encoding="utf-8")

    def boom(*a, **k):
        raise OSError("killed mid-write")
    monkeypatch.setattr(features.os, "replace", boom)
    try:
        features.set_feature(str(repo), "lanes", "off")
    except OSError:
        pass
    assert p.read_text(encoding="utf-8") == before
    assert [x.name for x in p.parent.iterdir()] == ["features.json"], "a temp file was left behind"


def test_a_null_row_is_an_error_for_get_and_set_alike(repo):
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {"roadmap": None}}), encoding="utf-8")
    for args in (("get", "roadmap"), ("set", "roadmap", "off"), ("get",)):
        r = sh(repo, *args)
        assert r.returncode == 2 and r.stdout.strip() == "" and "Traceback" not in r.stderr, (args, r.stderr)
