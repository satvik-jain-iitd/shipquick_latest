"""Story #418 (F1, epic #86): one features file and one reader. `scripts/features.py` answers "is this feature on?"
from `.shipquick/features.json`, with the kit's own defaults in `scripts/features_default.json`. Real files in a tmp folder."""
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES = ROOT / "scripts" / "features.py"
DEFAULTS = ROOT / "scripts" / "features_default.json"


def run(root, *args):
    return subprocess.run([sys.executable, str(FEATURES), "--root", str(root), *args], capture_output=True, text=True)


def write(root, features):
    (root / ".shipquick").mkdir(exist_ok=True)
    (root / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": features}), encoding="utf-8")


def test_get_prints_on_and_exits_0_or_off_and_exits_1(tmp_path):
    write(tmp_path, {"roadmap": {"on": True}, "pre-commit": {"on": False}})
    r = run(tmp_path, "get", "roadmap")
    assert (r.returncode, r.stdout.strip()) == (0, "on")
    r = run(tmp_path, "get", "pre-commit")
    assert (r.returncode, r.stdout.strip()) == (1, "off")


def test_no_file_means_every_feature_at_its_default(tmp_path):
    d = json.loads(DEFAULTS.read_text(encoding="utf-8"))["features"]
    assert d["hosted-roadmap"]["default"] is False and d["roadmap"]["default"] is True
    assert run(tmp_path, "get", "roadmap").returncode == 0
    r = run(tmp_path, "get", "hosted-roadmap")
    assert (r.returncode, r.stdout.strip()) == (1, "off")


def test_an_unknown_id_exits_2_and_names_it_never_on(tmp_path):
    r = run(tmp_path, "get", "nosuch")
    assert r.returncode == 2 and "nosuch" in r.stderr and r.stdout.strip() == ""


def test_a_locked_feature_is_always_on_even_when_the_file_says_off(tmp_path):
    write(tmp_path, {"gate": {"on": False}, "adoption": {"on": False}})
    for fid in ("gate", "adoption"):
        r = run(tmp_path, "get", fid)
        assert (r.returncode, r.stdout.strip()) == (0, "on"), fid


def test_json_prints_the_whole_map_with_on_default_locked_and_the_words(tmp_path):
    write(tmp_path, {"roadmap": {"on": False}})
    m = json.loads(run(tmp_path, "json").stdout)["features"]
    assert m["roadmap"]["on"] is False and m["roadmap"]["default"] is True and m["roadmap"]["locked"] is False
    assert m["gate"]["locked"] is True and m["gate"]["on"] is True
    for fid, f in m.items():
        assert all(f.get(k) for k in ("name", "what", "if_off", "group")), f"{fid} lacks its plain words"


def test_a_file_that_is_not_json_exits_2_with_the_line_never_defaults(tmp_path):
    (tmp_path / ".shipquick").mkdir()
    (tmp_path / ".shipquick" / "features.json").write_text('{\n  "version": 1,\n  "features": {oops}\n}\n', encoding="utf-8")
    for args in (("get", "roadmap"), ("json",)):
        r = run(tmp_path, *args)
        assert r.returncode == 2 and "line 3" in r.stderr, (args, r.stderr)
        assert r.stdout.strip() == ""


def test_a_non_boolean_value_is_an_error_not_a_guess(tmp_path):
    write(tmp_path, {"roadmap": {"on": "yes"}})
    assert run(tmp_path, "get", "roadmap").returncode == 2


def test_an_id_the_kit_does_not_know_in_the_file_is_listed_not_obeyed(tmp_path):
    write(tmp_path, {"old-thing": {"on": True}})
    j = json.loads(run(tmp_path, "json").stdout)
    assert j["unknown"] == ["old-thing"] and "old-thing" not in j["features"]


def test_the_default_list_has_the_ids_the_plan_names():
    d = json.loads(DEFAULTS.read_text(encoding="utf-8"))["features"]
    for fid in ("roadmap", "modes", "merge-gate", "close-on-merge", "lanes", "pre-commit", "hosted-roadmap",
                "disable-comments", "roles", "team-block", "frontend-design", "uat-on-main", "freeze", "environments",
                "component-registry", "design-tokens", "rule-copies", "commit-subjects", "story", "adoption", "gate"):
        assert fid in d, fid
    assert {k for k, v in d.items() if v.get("locked")} == {"adoption", "gate"}


def test_the_three_files_are_protected_paths():
    globs = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    for rel in ("scripts/features.py", "scripts/features_default.json", "scripts/features_anything_later.sh"):   # the glob covers features.sh of the next story too
        assert any(fnmatch.fnmatchcase(rel, g) for g in globs), rel


def test_the_decision_record_exists():
    adr = (ROOT / "docs" / "decisions" / "ADR-016.md").read_text(encoding="utf-8")
    assert "features" in adr.lower() and "locked" in adr.lower()


def test_an_invalid_utf8_byte_exits_2_with_empty_stdout_never_1(tmp_path):
    """Exit 1 means off, so a crash must never leak as 1 (review of #431)."""
    (tmp_path / ".shipquick").mkdir()
    (tmp_path / ".shipquick" / "features.json").write_bytes(b'{"version": 1, "features": {"roadmap": {"on": true}}}\n\xff')
    for args in (("get", "roadmap"), ("json",)):
        r = run(tmp_path, *args)
        assert r.returncode == 2 and r.stdout.strip() == "" and "Traceback" not in r.stderr, (args, r.returncode, r.stderr)


def test_a_bad_defaults_file_is_an_error_not_a_crash(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import features
    for bad in ('{}', '{"features": {"a": {"name": "A"}}}', '{"features": []}', '{"features": {"a": {"default": "yes"}}}'):
        d = tmp_path / "d.json"
        d.write_text(bad, encoding="utf-8")
        try:
            features.read(tmp_path, defaults=d)
        except features.FeaturesError:
            continue
        raise AssertionError(f"accepted {bad}")


def test_any_unexpected_crash_still_exits_2(tmp_path, monkeypatch, capsys):
    """A real crash inside read() (not a FeaturesError) must come out as 2, never 1 (review of #431)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import features

    def boom(root, defaults=None):
        raise RuntimeError("boom")
    monkeypatch.setattr(features, "read", boom)
    assert features.main(["--root", str(tmp_path), "get", "roadmap"]) == 2
    out = capsys.readouterr()
    assert out.out == "" and "boom" in out.err

def test_a_directory_or_dangling_link_at_the_file_path_is_an_error_not_defaults(tmp_path):
    (tmp_path / ".shipquick").mkdir()
    f = tmp_path / ".shipquick" / "features.json"
    f.mkdir()
    r = run(tmp_path, "get", "roadmap")
    assert r.returncode == 2 and r.stdout.strip() == ""
    f.rmdir()
    f.symlink_to(tmp_path / "nowhere.json")
    r = run(tmp_path, "get", "roadmap")
    assert r.returncode == 2 and r.stdout.strip() == ""


def test_no_git_and_no_root_exits_2_never_1_never_defaults_from_dot(tmp_path):
    import os
    env = dict(os.environ, PATH="/nonexistent")
    r = subprocess.run([sys.executable, str(FEATURES), "get", "roadmap"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 2 and r.stdout.strip() == "" and "git" in r.stderr
    r = subprocess.run([sys.executable, str(FEATURES), "get", "roadmap"], cwd=tmp_path, capture_output=True, text=True)   # git present, not a repo
    assert r.returncode == 2 and r.stdout.strip() == ""


def test_a_defaults_row_with_a_non_boolean_locked_is_an_error(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import features
    d = tmp_path / "d.json"
    d.write_text('{"features": {"a": {"default": true, "locked": "yes"}}}', encoding="utf-8")
    try:
        features.read(tmp_path, defaults=d)
    except features.FeaturesError:
        return
    raise AssertionError("accepted a string locked")


def test_help_flags_are_not_answers_they_exit_2_never_0(tmp_path):
    """`get -h` printing help and exiting 0 would read as "on" (review of #431)."""
    for args in (("get", "-h"), ("get", "--help"), ("-h",), ("--help",), ("json", "-h")):
        r = run(tmp_path, *args)
        assert r.returncode == 2 and r.stdout.strip() == "", (args, r.returncode, r.stdout)
