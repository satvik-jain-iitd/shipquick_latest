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
    assert data["features"]["roadmap"]["on"] is False and data["features"]["roadmap"]["default"] is True
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
