"""Story #424 (F7, epic #86): the roadmap workflow and the Closes rules read their flags. `roadmap` off: roadmap.yml writes
nothing. `close-on-merge` off: close_linked_issues.py closes nothing and the Closes link is not required. A broken features
file is an error, never "on". Real git, a fake gh, text checks on the workflows."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CLOSES = ROOT / "scripts" / "check_closes.py"
CLOSER = ROOT / "scripts" / "close_linked_issues.py"
ROADMAP_YML = (ROOT / ".github" / "workflows" / "roadmap.yml").read_text(encoding="utf-8")
CHECKS_YML = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "dev", str(tmp_path)], check=True)
    return tmp_path


def flag(repo, **f):
    (repo / ".shipquick").mkdir(exist_ok=True)
    (repo / ".shipquick" / "features.json").write_text(json.dumps({"version": 1, "features": {k: {"on": v} for k, v in f.items()}}), encoding="utf-8")


def closes(cwd, body, *args, title="feat: x"):
    return subprocess.run([sys.executable, str(CLOSES), "--title", title, "--author", "me", *args], cwd=cwd, input=body, capture_output=True, text=True)


def test_check_closes_off_flag_needs_no_link_on_flag_still_does(repo):
    assert closes(repo, "no link here\n", "--close-on-merge", "off").returncode == 0
    r = closes(repo, "no link here\n", "--close-on-merge", "on")
    assert r.returncode == 1 and "Closes" in r.stdout


def test_check_closes_with_no_option_reads_the_repo_features_file(repo):
    assert closes(repo, "no link\n").returncode == 1            # no file: default on
    flag(repo, **{"close-on-merge": False})
    r = closes(repo, "no link\n")
    assert r.returncode == 0 and "close-on-merge is off" in r.stdout


def test_check_closes_with_a_broken_features_file_fails_never_passes(repo):
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "features.json").write_bytes(b"{oops")
    r = closes(repo, "Closes #1\n")
    assert r.returncode == 1 and "features" in r.stdout


def fake_gh(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    log = tmp_path / "gh.log"
    g = bindir / "gh"
    g.write_text(f'#!/usr/bin/env bash\necho "$@" >> {log}\ncase "$*" in\n  "api repos/{{owner}}/{{repo}}") echo \'{{"default_branch":"main"}}\' ;;\n  "pr view"*) echo \'{{"state":"MERGED","baseRefName":"dev","body":"Closes #5"}}\' ;;\n  "issue view"*) echo \'{{"state":"OPEN","labels":[]}}\' ;;\nesac\n', encoding="utf-8")
    g.chmod(0o755)
    return bindir, log


def run_closer(repo, tmp_path, *args):
    bindir, log = fake_gh(tmp_path)
    env = dict(os.environ, PATH=f"{bindir}:{os.environ['PATH']}")
    r = subprocess.run([sys.executable, str(CLOSER), "7", *args], cwd=repo, env=env, capture_output=True, text=True)
    return r, (log.read_text(encoding="utf-8") if log.exists() else "")


def test_the_closer_with_close_on_merge_off_closes_nothing_and_calls_no_gh(repo, tmp_path):
    flag(repo, **{"close-on-merge": False})
    r, log = run_closer(repo, tmp_path, "--yes")
    assert r.returncode == 0 and "close-on-merge is off" in r.stdout
    assert log == "", "it must not even look at GitHub"


def test_the_closer_with_the_flag_on_still_works(repo, tmp_path):
    r, log = run_closer(repo, tmp_path)   # dry run
    assert r.returncode == 0 and "close #5" in r.stdout and "issue close" not in log


def test_the_closer_with_a_broken_features_file_exits_2_and_closes_nothing(repo, tmp_path):
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "features.json").write_bytes(b"{oops")
    r, log = run_closer(repo, tmp_path, "--yes")
    assert r.returncode == 2 and "features" in r.stderr and log == ""


def test_roadmap_yml_reads_the_flag_first_and_every_later_step_waits_for_it():
    steps = ROADMAP_YML.split("    steps:\n", 1)[1]
    assert "sparse-checkout: |" in steps and "scripts" in steps.split("Read issues", 1)[0]
    flag_at = steps.index("id: flag")
    assert "features.py" in steps[flag_at:] and "roadmap is off" in steps[flag_at:]
    for name in ("Read issues and pull requests", "Write ROADMAP.md", "Write roadmap.html", "Save it on the roadmap branch", "Set up Node for wrangler", "Deploy to Cloudflare Pages"):
        block = steps.split(f"- name: {name}", 1)[1].split("\n      - name:", 1)[0]
        assert "steps.flag.outputs.on == 'true'" in block, name


def test_the_checks_team_block_passes_the_close_on_merge_flag():
    block = CHECKS_YML.split("\n  team-block:\n", 1)[1].split("\n  frontend-design:", 1)[0]
    assert "check_closes.py --close-on-merge" in block
    assert "fromJSON(needs.features.outputs.flags)['close-on-merge']" in block
