"""S0.18: one command adopts ShipQuick in a child project (story #68). Real git in a throwaway child repo; no network."""
import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ADOPT = ROOT / "scripts" / "adopt.sh"
HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
CALL = "satvik-jain-iitd/shipquick_latest/.github/workflows/roadmap.yml"


def adopt(child, *args):
    return subprocess.run(["bash", str(ADOPT), str(child), *args], capture_output=True, text=True)


def snapshot(child):
    return {str(p.relative_to(child)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(child.rglob("*")) if p.is_file() and ".git" not in p.relative_to(child).parts}


@pytest.fixture
def child(tmp_path):
    c = tmp_path / "my-child"
    (c / ".github" / "workflows").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "dev", str(c)], check=True)
    (c / ".github" / "workflows" / "ci.yml").write_text('name: Child CI\non:\n  push:\n', encoding="utf-8")
    return c


def test_s18_the_five_files_appear_and_the_workflow_is_pinned_with_the_childs_own_ci_name(child):
    r = adopt(child)
    assert r.returncode == 0, r.stderr
    call = (child / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")
    assert f"uses: {CALL}@{HEAD}" in call and f"shipquick_ref: {HEAD}" in call
    assert 'workflows: ["Child CI"]' in call
    triggers = call.split("\npermissions:", 1)[0]
    assert "\n  pull_request" not in triggers and "\n  issues:" in triggers and "\n  workflow_dispatch:" in triggers
    attrs = (child / ".gitattributes").read_text(encoding="utf-8")
    assert "docs/process-trace.md merge=union" in attrs and "docs/LEARNINGS.md merge=union" in attrs
    assert (child / ".claude" / "commands" / "mode.md").read_text(encoding="utf-8") == (ROOT / ".claude" / "commands" / "mode.md").read_text(encoding="utf-8")
    assert '"title"' in (child / "roadmap.json").read_text(encoding="utf-8")
    assert "check_local.sh" in (child / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "created" in r.stdout and "my-child" not in r.stderr


def test_s18_a_second_run_changes_nothing_and_says_so(child):
    adopt(child)
    before = snapshot(child)
    r = adopt(child)
    assert r.returncode == 0 and snapshot(child) == before
    assert "created" not in r.stdout and "updated" not in r.stdout and r.stdout.count("unchanged") >= 4


def test_s18_the_childs_own_roadmap_json_is_never_overwritten(child):
    (child / "roadmap.json").write_text('{"title": "Mine", "vision": "My own words."}\n', encoding="utf-8")
    r = adopt(child)
    assert (child / "roadmap.json").read_text(encoding="utf-8") == '{"title": "Mine", "vision": "My own words."}\n'
    assert "kept" in r.stdout and "roadmap.json" in r.stdout


def test_s18_the_childs_own_gitattributes_lines_stay_and_ours_are_added_once(child):
    (child / ".gitattributes").write_text("*.png binary\n", encoding="utf-8")
    adopt(child); adopt(child)
    lines = (child / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "*.png binary" in lines and lines.count("docs/process-trace.md merge=union") == 1 and lines.count("docs/LEARNINGS.md merge=union") == 1


def test_s18_a_childs_own_precommit_config_is_kept_and_the_hook_is_printed(child):
    (child / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    r = adopt(child)
    assert (child / ".pre-commit-config.yaml").read_text(encoding="utf-8") == "repos: []\n"
    assert "kept" in r.stdout and "check_local.sh" in r.stdout
    assert adopt(child).stdout.count("kept      .pre-commit-config.yaml") == 1


def test_s18_without_a_ci_yml_the_workflow_has_no_workflow_run_and_the_output_says_so(child):
    (child / ".github" / "workflows" / "ci.yml").unlink()
    r = adopt(child)
    call = (child / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")
    assert "\n  workflow_run:" not in call and "\n  issues:" in call and "ci.yml" in r.stdout


def test_s18_ref_picks_the_commit_and_a_bad_ref_or_path_is_refused(child, tmp_path):
    assert adopt(child, "--ref", "HEAD").returncode == 0 and f"@{HEAD}" in (child / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")
    assert adopt(child, "--ref", "no-such-ref").returncode == 2
    assert adopt(tmp_path / "missing").returncode == 2
    plain = tmp_path / "not-git"; plain.mkdir()
    assert adopt(plain).returncode == 2


def test_s18_the_generated_workflow_matches_shipquicks_own_caller_except_for_the_pin_and_the_ci_name(child):
    adopt(child)
    ours = (ROOT / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")
    expect = ours.replace("uses: ./.github/workflows/roadmap.yml", f"uses: {CALL}@{HEAD}").replace("shipquick_ref: ${{ github.sha }}", f"shipquick_ref: {HEAD}").replace('workflows: ["shipquick_latest CI"]', 'workflows: ["Child CI"]')
    got = (child / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")

    def body(text):   # the lines that are code, not the header comments
        return [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    assert [l.split(" #")[0] for l in body(got)] == [l.split(" #")[0] for l in body(expect)]


def test_s18_the_manual_steps_are_replaced_by_the_command_in_the_docs():
    for path in ("docs/TEAM_PROTOCOL.md", "docs/LIVE_ROADMAP.md"):
        assert "scripts/adopt.sh" in (ROOT / path).read_text(encoding="utf-8"), path


@pytest.mark.parametrize("line", ["name: CI", 'name: "CI"', "name: 'CI'", "name:   'Child CI'   ", 'name: "Child CI"  '])
def test_s18_the_ci_name_is_read_with_either_kind_of_quote_or_none(child, line):
    (child / ".github" / "workflows" / "ci.yml").write_text(line + "\non:\n  push:\n", encoding="utf-8")
    adopt(child)
    call = (child / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")
    name = line.split(":", 1)[1].strip().strip("\"'")   # computed first: a backslash inside an f-string expression is a SyntaxError before Python 3.12
    assert f'workflows: ["{name}"]' in call


def test_s18_the_printed_next_step_says_to_run_the_checks_with_the_childs_base_branch(child):
    r = adopt(child)
    assert "BASE=" in r.stdout and "check_local.sh" in r.stdout


def test_s18_mode_md_mentions_the_owners_one_step_skill_next_to_the_bang_line():
    text = (ROOT / ".claude" / "commands" / "mode.md").read_text(encoding="utf-8")
    assert "shipquick-mode" in text and "! bash scripts/mode.sh set" in text


# Story 3 of epic #97: adopt.sh puts the one pointer line in the child's CLAUDE.md.
def pointer(child):
    import os
    return f"follow {os.path.relpath(ROOT, child)}/CLAUDE.md"


def test_s97_no_claude_md_gets_one_made_from_the_template_with_the_pointer(child):
    r = adopt(child)
    text = (child / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.count(pointer(child)) == 1 and "knowledge/shipquick_latest/CLAUDE.md" not in text
    assert "## Stack" in text and "created   CLAUDE.md" in r.stdout


def test_s97_an_existing_claude_md_keeps_every_line_and_gains_the_pointer_once(child):
    mine = "# My project\n\nStack: Rust.\n1. My own numbered line.\n"
    (child / "CLAUDE.md").write_text(mine, encoding="utf-8")
    r = adopt(child)
    text = (child / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith("# My project\n") and pointer(child) in text
    for line in mine.splitlines():
        assert line in text.splitlines()
    assert "updated   CLAUDE.md" in r.stdout
    again = adopt(child)
    assert (child / "CLAUDE.md").read_text(encoding="utf-8") == text and "unchanged CLAUDE.md" in again.stdout
