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
                "component-registry", "design-tokens", "rule-copies", "story", "adoption", "gate"):
        assert fid in d, fid
    assert {k for k, v in d.items() if v.get("locked")} == {"adoption", "gate"}


def test_the_three_files_are_protected_paths():
    globs = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    for rel in ("scripts/features.py", "scripts/features_default.json", "scripts/features.sh"):
        assert any(fnmatch.fnmatchcase(rel, g) for g in globs), rel


def test_the_decision_record_exists():
    adr = (ROOT / "docs" / "decisions" / "ADR-016.md").read_text(encoding="utf-8")
    assert "features" in adr.lower() and "locked" in adr.lower()
