"""Story #485 (PR 1): one change map decides which slow CI jobs run, and the gate proves it.

The map is scripts/change_map.json. The reader is scripts/change_map.py: `decide` (stdout JSON) and `gate` (exit 1 on a
wrong result). Both fail closed: any doubt turns every slow area on. Real git in a throwaway repo; no network.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / "scripts" / "change_map.py"
MAP = ROOT / "scripts" / "change_map.json"
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
MAP_TEXT = MAP.read_text(encoding="utf-8") if MAP.exists() else "{}\n"   # red state: the map is not written yet

# Every path that turned a phone job on before story #485 (ci.yml aside: story #484). A drop needs a reason in ADR-018.
TODAY_UI = ["ui/android/build.gradle.kts", "ui/ios/templates/ListTemplate.swift", "ui/tool/package.json", "tests/fixtures/ios/Bad/BadScreen.swift",
            "scripts/ui_proof.py", "scripts/emit_contracts.py", "scripts/emit_tokens.py", "design/tokens.json"]
TODAY_IOS = ["ui/ios/templates/ListTemplate.swift", "design/tokens.json", "scripts/emit_tokens.py"]
TODAY_NONE = ["docs/x.md", "scripts/other.py", "tests/test_ui_proof.py", ".github/workflows/ci.yml", "CHANGELOG.md"]


def git(repo, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=check)


def make_repo(tmp_path, files=None):
    """A repo with origin/dev at the first commit and a PR branch to change. Returns the path."""
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "dev")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    for path, text in (files or BASE_FILES).items():
        p = repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "update-ref", "refs/remotes/origin/dev", "HEAD")
    git(repo, "switch", "-q", "-c", "feat/x")
    return repo


BASE_FILES = {
    "scripts/change_map.json": MAP_TEXT,
    "scripts/change_map.py": READER.read_text(encoding="utf-8") if READER.exists() else "# placeholder\n",
    ".github/workflows/ci.yml": CI,
    "docs/x.md": "doc\n",
    "ui/android/build.gradle.kts": "a\n",
    "ui/ios/templates/ListTemplate.swift": "i\n",
    "ui/tool/package.json": "t\n",
    "tests/fixtures/ios/Bad/BadScreen.swift": "b\n",
    "scripts/ui_proof.py": "p\n", "scripts/emit_contracts.py": "c\n", "scripts/emit_tokens.py": "e\n",
    "design/tokens.json": "d\n", "scripts/other.py": "o\n", "tests/test_ui_proof.py": "t\n", "CHANGELOG.md": "c\n",
}


def decide(repo, event="pull_request", base="origin/dev"):
    env = dict(os.environ, GITHUB_EVENT_NAME=event)
    r = subprocess.run([sys.executable, str(READER), "decide", "--base", base, "--head", "HEAD", "--event", event,
                        "--map", "scripts/change_map.json"], cwd=repo, capture_output=True, text=True, env=env)
    assert r.returncode == 0, (r.stdout, r.stderr)
    return json.loads(r.stdout)


def change(repo, path, text=None, delete=False, move_to=None):
    if move_to:
        (repo / move_to).parent.mkdir(parents=True, exist_ok=True)
        git(repo, "mv", path, move_to)
    elif delete:
        git(repo, "rm", "-q", path)
    else:
        p = repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text if text is not None else p.read_text(encoding="utf-8") + "x\n", encoding="utf-8")
        git(repo, "add", path)
    git(repo, "commit", "-q", "-m", f"change {path}")


def on(d):
    return {"android": d["android"], "ios": d["ios"]}


# ---- the map and its rows ----
def test_s485_the_map_is_json_with_two_areas_and_the_free_paths_and_no_yaml_reader():
    m = json.loads(MAP_TEXT)
    assert set(m["areas"]) == {"android", "ios"}
    assert m["areas"]["android"]["jobs"] == ["ui-android-compile", "ui-android-lint"]
    assert m["areas"]["ios"]["jobs"] == ["ui-ios-compile", "ui-ios-lint", "ui-ios-snapshots"]
    assert "docs/**" in m["free"] and "*.md" in m["free"]
    assert "import yaml" not in READER.read_text(encoding="utf-8")


def test_s485_every_path_that_turned_a_job_on_before_still_turns_it_on_ci_yml_aside(tmp_path):
    """Table test (#485 review point 2): today's two regexes, as one table. A drop needs a reason in ADR-018."""
    repo = make_repo(tmp_path)
    for path in TODAY_UI:
        change(repo, path)
    d = decide(repo)
    assert d["android"] and d["ios"], d

    for i, path in enumerate(TODAY_IOS):
        repo2 = make_repo(tmp_path / f"ios{i}")
        change(repo2, path)
        assert decide(repo2)["ios"], path


def test_s485_no_path_that_was_free_before_turns_a_job_on(tmp_path):
    repo = make_repo(tmp_path)
    for path in TODAY_NONE:
        change(repo, path)   # appends a line: a ci.yml edit at the end still leaves every job block as it was
    d = decide(repo)
    assert not d["android"] and not d["ios"] and not d["all"], d


# ---- splitting: an Android-only PR does not wait on iOS, and the shared ui/ paths still reach both ----
def test_s485_an_android_only_change_leaves_ios_off(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "ui/android/build.gradle.kts")
    assert on(decide(repo)) == {"android": True, "ios": False}


def test_s485_an_ios_only_change_leaves_android_off(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "ui/ios/templates/ListTemplate.swift")
    assert on(decide(repo)) == {"android": False, "ios": True}


def test_s485_a_shared_ui_path_turns_both_on(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "ui/tool/package.json")
    assert on(decide(repo)) == {"android": True, "ios": True}


def test_s485_a_new_file_inside_a_named_folder_needs_no_map_row(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "ui/android/brandnew/Thing.kt", text="new\n")
    assert on(decide(repo)) == {"android": True, "ios": False}


def test_s485_a_new_top_level_folder_turns_every_area_on_and_names_the_row_to_add(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "newfolder/tool.py", text="x\n")
    d = decide(repo)
    assert d["android"] and d["ios"] and d["all"]
    assert any("newfolder/tool.py" in r and "add a row" in r for r in d["reasons"]), d["reasons"]


def test_s485_a_docs_only_change_turns_nothing_on(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "docs/x.md", text="more\n")
    assert on(decide(repo)) == {"android": False, "ios": False}


# ---- fail closed (done-when 4): every doubt turns every area on, each case with its own test ----
def test_s485_fail_closed_when_the_event_is_not_a_pull_request(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "docs/x.md", text="more\n")
    d = decide(repo, event="push")
    assert d["android"] and d["ios"] and d["all"]


def test_s485_fail_closed_when_the_diff_cannot_be_read(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "docs/x.md", text="more\n")
    d = decide(repo, base="origin/no-such-branch")
    assert d["android"] and d["ios"] and d["all"]


def test_s485_fail_closed_when_the_map_is_missing_empty_or_broken(tmp_path):
    for i, content in enumerate((None, "", "{not json")):
        repo = make_repo(tmp_path / f"map{i}")
        change(repo, "docs/x.md", text="more\n")
        if content is None:
            git(repo, "rm", "-q", "scripts/change_map.json"); git(repo, "commit", "-q", "-m", "no map")
        else:
            (repo / "scripts/change_map.json").write_text(content, encoding="utf-8")
            git(repo, "add", "-A"); git(repo, "commit", "-q", "-m", "broken map")
        d = decide(repo)
        assert d["all"] and d["android"] and d["ios"], (content, d)


def test_s485_fail_closed_when_the_map_or_its_reader_changed_in_the_pr(tmp_path):
    for path in ("scripts/change_map.json", "scripts/change_map.py"):
        repo = make_repo(tmp_path / path.replace("/", "_"))
        change(repo, path, text=(repo / path).read_text(encoding="utf-8") + "\n")
        d = decide(repo)
        assert d["all"] and d["android"] and d["ios"], path


def test_s485_a_renamed_file_counts_under_its_old_path_and_its_new_path(tmp_path):
    repo = make_repo(tmp_path)
    change(repo, "ui/ios/templates/ListTemplate.swift", move_to="docs/ListTemplate.md")
    assert on(decide(repo)) == {"android": False, "ios": True}, "the old path turns ios on"
    repo2 = make_repo(tmp_path / "b")
    change(repo2, "docs/x.md", move_to="ui/android/moved/x.kt")
    assert on(decide(repo2)) == {"android": True, "ios": False}, "the new path turns android on"


# ---- rule 5: a job's own steps turn that job's area on; another part of ci.yml does not ----
def edit_ci(repo, old, new):
    p = repo / ".github/workflows/ci.yml"
    text = p.read_text(encoding="utf-8")
    assert old in text, old[:60]
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    git(repo, "add", "-A"); git(repo, "commit", "-q", "-m", "ci edit")


def test_s485_a_change_to_a_phone_job_s_own_steps_turns_its_area_on(tmp_path):
    repo = make_repo(tmp_path)
    edit_ci(repo, "CI= bash ui/tool/ios_lint.sh tests/fixtures/ios/Bad/BadScreen.swift", "CI= bash ui/tool/ios_lint.sh tests/fixtures/ios/Bad/BadScreen.swift  # changed")
    d = decide(repo)
    assert on(d) == {"android": False, "ios": True}, d
    assert any("ui-ios-lint" in r for r in d["reasons"]), d["reasons"]


def test_s485_a_change_to_another_part_of_ci_yml_turns_nothing_on(tmp_path):
    repo = make_repo(tmp_path)
    edit_ci(repo, "  gate:\n    name: gate\n", "  gate:\n    name: gate\n    # a comment in the gate job\n")
    assert on(decide(repo)) == {"android": False, "ios": False}


def test_s485_ci_yml_has_no_inline_path_rule_left():
    ui = re.search(r"^  ui-changes:\n((?:    .*\n|\n)*)", CI, re.M).group(1)
    assert "grep -qE '^(ui/" not in ui and "change_map.py" in ui


# ---- done-when 6: the gate proves the result of every phone job ----
def gate(tmp_path, decision, needs):
    d = tmp_path / "d.json"; n = tmp_path / "n.json"
    d.write_text(json.dumps(decision), encoding="utf-8"); n.write_text(json.dumps(needs), encoding="utf-8")
    return subprocess.run([sys.executable, str(READER), "gate", "--decision", str(d), "--needs", str(n), "--map", str(MAP)],
                          capture_output=True, text=True)


ALL_ON = {"android": True, "ios": True, "all": True, "reasons": []}
PHONE = ["ui-android-compile", "ui-android-lint", "ui-ios-compile", "ui-ios-lint", "ui-ios-snapshots"]


def needs(results):
    return {name: {"result": results.get(name, "success")} for name in PHONE}


def test_s485_gate_passes_when_every_job_of_an_on_area_succeeded(tmp_path):
    assert gate(tmp_path, ALL_ON, needs({})).returncode == 0


def test_s485_gate_fails_when_a_job_of_an_on_area_was_skipped(tmp_path):
    r = gate(tmp_path, {"android": False, "ios": True, "all": False, "reasons": []}, needs({"ui-ios-lint": "skipped"}))
    assert r.returncode == 1 and "ui-ios-lint" in r.stdout + r.stderr


def test_s485_gate_passes_a_skipped_job_of_an_off_area(tmp_path):
    r = gate(tmp_path, {"android": True, "ios": False, "all": False, "reasons": []},
             needs({"ui-ios-compile": "skipped", "ui-ios-lint": "skipped", "ui-ios-snapshots": "skipped"}))
    assert r.returncode == 0, r.stdout + r.stderr


def test_s485_gate_fails_a_missing_job_result_of_an_on_area(tmp_path):
    n = needs({}); del n["ui-android-lint"]
    r = gate(tmp_path, ALL_ON, n)
    assert r.returncode == 1 and "ui-android-lint" in r.stdout + r.stderr


def test_s485_gate_fails_a_cancelled_job_of_an_on_area(tmp_path):
    r = gate(tmp_path, ALL_ON, needs({"ui-ios-snapshots": "cancelled"}))
    assert r.returncode == 1


def test_s485_a_pr_that_sets_a_job_if_to_false_fails_the_gate(tmp_path):
    """Done-when 6: the change map says the job must run; a PR that makes it skip still fails the gate."""
    r = gate(tmp_path, {"android": True, "ios": False, "all": False, "reasons": []},
             needs({"ui-android-compile": "skipped", "ui-android-lint": "skipped"}))
    assert r.returncode == 1 and "ui-android-compile" in r.stdout + r.stderr


def test_s485_the_gate_job_reads_the_decision_and_the_needs_and_keeps_always_and_the_cancel_check():
    gate_job = re.search(r"^  gate:\n((?:    .*\n|\n)*)", CI, re.M).group(1)
    assert "if: always()" in gate_job
    assert "change_map.py gate" in gate_job and "toJSON(needs)" in gate_job
    assert "contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')" in gate_job


def test_s485_a_change_to_the_decision_job_or_the_top_of_ci_yml_turns_every_area_on(tmp_path):
    """#485 PR 1 review (fail closed): the ui-changes job and the file header decide the others; a change there can skip
    a needed job, so nothing is skipped on that run. A change to another job (the gate) still turns nothing on."""
    repo = make_repo(tmp_path)
    edit_ci(repo, "Which slow jobs must run? (story #485, one map)", "Which slow jobs must run? (story #485, one map) edited")
    d = decide(repo)
    assert on(d) == {"android": True, "ios": True}, d
    assert any("ci.yml" in r for r in d["reasons"]), d["reasons"]
    repo2 = make_repo(tmp_path / "top")
    edit_ci(repo2, 'name: "shipquick_latest CI"', 'name: "shipquick_latest CI (edited)"')
    assert on(decide(repo2)) == {"android": True, "ios": True}


def test_s485_all_true_turns_every_area_on_in_the_gate(tmp_path):
    """#499 review point 2 (fail open): decision={"all": true} is the fail-closed answer; the gate must read it as every area on."""
    r = gate(tmp_path, {"all": True}, needs({"ui-android-compile": "skipped", "ui-ios-lint": "skipped"}))
    assert r.returncode == 1 and "ui-android-compile" in r.stdout + r.stderr, r.stdout + r.stderr


def test_s485_a_map_job_with_no_block_in_head_ci_yml_turns_every_area_on(tmp_path):
    """#499 review point 3: a job the map names but head ci.yml does not have cannot be judged; every area turns on."""
    repo = make_repo(tmp_path)
    edit_ci(repo, "  ui-ios-lint:\n", "  ui-ios-lint-renamed:\n")
    assert on(decide(repo)) == {"android": True, "ios": True}, decide(repo)
