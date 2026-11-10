"""Story #324 (A6): scripts/release.sh tags vX.Y.Z only when the notes, the gate and the tag all agree.
Real git in throwaway repos with a bare origin; gh is a fake on PATH that serves check runs for one sha."""
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RELEASE = ROOT / "scripts" / "release.sh"
TAG = "v1.2.3"
REPO = "satvik-jain-iitd/shipquick_latest"

FAKE_GH = """#!/usr/bin/env bash
echo "$*" >> "$FAKE_GH_LOG"
case "$*" in
  *"/commits/$FAKE_GH_SHA/check-runs"*) cat "$FAKE_GH_JSON" ;;
  *"/check-runs"*) echo '{"check_runs":[]}' ;;
  *) echo "fake gh: unexpected $*" >&2; exit 1 ;;
esac
"""


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def check_runs(*runs):
    return json.dumps({"total_count": len(runs), "check_runs": [
        {"id": i + 1, "name": name, "status": status, "conclusion": conclusion}
        for i, (name, status, conclusion) in enumerate(runs)]})


@pytest.fixture
def world(tmp_path):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "dev", str(origin)], check=True)
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "-b", "dev", str(work)], check=True)
    git(work, "config", "user.email", "test@example.com")
    git(work, "config", "user.name", "Test")
    git(work, "remote", "add", "origin", str(origin))
    (work / "docs").mkdir()
    (work / "docs" / f"RELEASE_NOTES_{TAG}.md").write_text(f"# ShipQuick {TAG} (10 Nov 2026)\n\nNotes.\n", encoding="utf-8")
    (work / "app.txt").write_text("v1\n", encoding="utf-8")
    git(work, "add", ".")
    git(work, "commit", "-q", "-m", "feat: first")
    old = git(work, "rev-parse", "HEAD")
    (work / "app.txt").write_text("v2\n", encoding="utf-8")
    git(work, "commit", "-qam", "feat: second")
    git(work, "push", "-q", "origin", "dev")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    checks = tmp_path / "checks.json"
    checks.write_text(check_runs(("gate", "completed", "success")), encoding="utf-8")
    log = tmp_path / "gh.log"
    log.write_text("", encoding="utf-8")
    return {"work": work, "origin": origin, "old": old, "bin": bin_dir, "checks": checks, "log": log,
            "head": git(work, "rev-parse", "HEAD")}


def run(w, *args, sha=None, checks=None, repo=REPO):
    env = dict(os.environ)
    env.update({"PATH": f"{w['bin']}{os.pathsep}{env['PATH']}", "FAKE_GH_LOG": str(w["log"]),
                "FAKE_GH_JSON": str(checks or w["checks"]), "FAKE_GH_SHA": sha or w["head"]})
    if repo:
        env["RELEASE_REPO"] = repo
    else:
        env.pop("RELEASE_REPO", None)
    return subprocess.run(["bash", str(RELEASE), *args], cwd=w["work"], capture_output=True, text=True, env=env)


def no_tag_anywhere(w):
    assert git(w["work"], "tag", "-l", TAG) == ""
    assert git(w["origin"], "tag", "-l", TAG) == ""


def test_s324_a_green_gate_on_head_dry_run_prints_the_plan_and_tags_nothing(world):
    r = run(world, TAG, "--dry-run")
    assert r.returncode == 0, r.stderr
    assert f"would tag {TAG} at {world['head']}" in r.stdout
    no_tag_anywhere(world)


def test_s324_a_green_gate_on_head_tags_annotated_at_head_and_pushes_the_tag(world):
    r = run(world, TAG)
    assert r.returncode == 0, r.stderr
    assert git(world["work"], "cat-file", "-t", f"refs/tags/{TAG}") == "tag"
    assert git(world["work"], "rev-parse", f"{TAG}^{{commit}}") == world["head"]
    assert f"refs/tags/{TAG}" in git(world["origin"], "show-ref")


def test_s324_the_check_is_read_for_the_exact_head_sha_and_the_repo_comes_from_origin(world):
    git(world["work"], "remote", "set-url", "origin", "https://klickbae8yt-star@github.com/satvik-jain-iitd/shipquick_latest.git")
    r = run(world, TAG, "--dry-run", repo=None)
    assert r.returncode == 0, r.stderr
    assert f"repos/{REPO}/commits/{world['head']}/check-runs" in world["log"].read_text(encoding="utf-8")


def test_s324_the_shipquick_checks_gate_name_also_counts(world):
    world["checks"].write_text(check_runs(("shipquick-checks / gate", "completed", "success")), encoding="utf-8")
    r = run(world, TAG, "--dry-run")
    assert r.returncode == 0, r.stderr


def test_s324_a_missing_notes_file_refuses_and_tags_nothing(world):
    (world["work"] / "docs" / f"RELEASE_NOTES_{TAG}.md").unlink()
    r = run(world, TAG)
    assert r.returncode == 1 and "does not exist" in r.stderr
    no_tag_anywhere(world)


def test_s324_a_notes_version_line_that_is_not_the_tag_refuses(world):
    (world["work"] / "docs" / f"RELEASE_NOTES_{TAG}.md").write_text("# ShipQuick v1.2.2 (9 Nov 2026)\n", encoding="utf-8")
    r = run(world, TAG)
    assert r.returncode == 1 and "version" in r.stderr and TAG in r.stderr
    no_tag_anywhere(world)


def test_s324_a_tag_that_exists_locally_refuses(world):
    git(world["work"], "tag", "-a", TAG, "-m", "old", world["old"])
    r = run(world, TAG)
    assert r.returncode == 1 and "already exists locally" in r.stderr
    assert git(world["origin"], "tag", "-l", TAG) == ""


def test_s324_a_tag_that_exists_only_on_origin_refuses(world):
    git(world["work"], "tag", "-a", TAG, "-m", "old", world["old"])
    git(world["work"], "push", "-q", "origin", TAG)
    git(world["work"], "tag", "-d", TAG)
    r = run(world, TAG)
    assert r.returncode == 1 and "already exists on origin" in r.stderr


def test_s324_no_gate_check_on_head_refuses(world):
    world["checks"].write_text(check_runs(("ci", "completed", "success")), encoding="utf-8")
    r = run(world, TAG)
    assert r.returncode == 1 and "no check named gate" in r.stderr
    no_tag_anywhere(world)


def test_s324_a_failed_gate_refuses_and_says_its_result(world):
    world["checks"].write_text(check_runs(("gate", "completed", "failure")), encoding="utf-8")
    r = run(world, TAG)
    assert r.returncode == 1 and "failure, not success" in r.stderr
    no_tag_anywhere(world)


def test_s324_a_gate_still_running_refuses(world):
    world["checks"].write_text(check_runs(("gate", "in_progress", None)), encoding="utf-8")
    r = run(world, TAG)
    assert r.returncode == 1 and "in_progress, not success" in r.stderr
    no_tag_anywhere(world)


def test_s324_a_green_gate_on_an_older_commit_does_not_count_for_head(world):
    r = run(world, TAG, sha=world["old"])
    assert r.returncode == 1 and "no check named gate" in r.stderr
    no_tag_anywhere(world)


def test_s324_a_version_that_is_not_vX_Y_Z_refuses_before_any_gh_call(world):
    r = run(world, "v1.2")
    assert r.returncode == 1 and "vX.Y.Z" in r.stderr
    assert world["log"].read_text(encoding="utf-8") == ""
