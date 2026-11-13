"""Story #504: the kit's own CI walks a made-up child project through the whole path a real child takes.

The child is generated here, with nothing from a real project: TypeScript-style test names, the kit on its own branch
(rule 24), a screens list, and a workflow written from the kit's own "Wiring CI" example. The walk runs the kit's own
scripts (adopt.sh, check_screens_wired.py, check_local.sh) and commits through the real git hooks.

WALK_KIT_SHA=<sha> walks the kit as it was at that commit. The red runs in the PR body use it (#478 at v0.13.3,
#490 at v0.14.0, #501 before #505, #500 before #506).
"""
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest

from test_adopt import GH_STUB, PROTECTED   # the stub gh and the protection of the default branch, reused (story #504)

ROOT = Path(__file__).resolve().parent.parent
PONYTAIL_ON = ROOT / "tests/fixtures/adopt/settings-ponytail-on.json"
# Every check a child runs: the named checks of scripts/check_local.sh and the jobs of .github/workflows/checks.yml.
# A check added to either file must be named here in the same PR, or test_the_walk_names_every_check fails (done-when 5).
WALK_CHECKS = {
    "check_local": {
        "sizes", "markers", "md-blocks", "rule-copies", "ui-docs", "ui-registry", "ui-topics", "ui-llms", "ui-proof",
        "ui-contracts", "ui-tokens", "ui-coverage", "workflow-security", "features-wiring", "commits", "commit-subjects",
        "pr-size", "frontend-design", "disable-comments", "design-tokens", "story", "tdd", "roadmap", "shortcuts",
        "secrets", "secrets-staged",
    },
    "checks.yml": {
        "adoption", "features", "disable-comments", "design-tokens", "roles", "team-block", "frontend-design",
        "uat-on-main", "freeze-on-main", "environments", "component-registry", "rule-copies", "commit-subjects",
        "story", "gate",
    },
}


GITMODULES = '[submodule "knowledge/shipquick_latest"]\n\tpath = knowledge/shipquick_latest\n\turl = https://github.com/owner/kit.git\n'
CHILD_CI = """name: Child CI
on:
  push:
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - run: npm test --if-present
"""


def git(cwd, *args):
    p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    assert p.returncode == 0, f"git {' '.join(args)} failed:\n{p.stderr}"
    return p.stdout.strip()


def run(args, cwd, env):
    return subprocess.run([str(a) for a in args], cwd=str(cwd), capture_output=True, text=True, env=env)


def step(name, p):
    out = (p.stdout or "") + (p.stderr or "")
    assert p.returncode == 0, f"walk step {name!r} failed with exit {p.returncode}:\n{out[-1500:]}"
    return out


def make_kit(dest):
    """The kit under test: this checkout, or (WALK_KIT_SHA) a clone of this repository checked out at that commit."""
    sha = os.environ.get("WALK_KIT_SHA", "").strip()
    if not sha:
        return ROOT, git(ROOT, "rev-parse", "HEAD")
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(dest)], check=True)
    git(dest, "checkout", "-q", "--detach", sha)
    return dest, git(dest, "rev-parse", "HEAD")


def stage(child):
    """git add -A, except the submodule path: its folder is empty here, and add -A would drop the pin (a real one is never empty)."""
    git(child, "add", "-A", "--", ".", ":!knowledge/shipquick_latest")


def publish(child, *branches):
    """A stand-in for origin/<branch>: check_local.sh compares with origin/<base>, and no network is used."""
    for b in branches:
        git(child, "update-ref", f"refs/remotes/origin/{b}", b)


def commit(child, env, subject, body=""):
    msg = child.parent / "commit-msg.txt"
    msg.write_text(subject + ("\n\n" + body if body else "") + "\n", encoding="utf-8")
    return run(["git", "commit", "-q", "-F", msg], child, env)


def wiring_example(kit):
    """The first yaml block of the "Wiring CI" section of the kit's own docs/SCREENS.md, as a child would copy it."""
    text = (kit / "docs/SCREENS.md").read_text(encoding="utf-8")
    section = re.search(r"^## Wiring CI\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert section, "docs/SCREENS.md has no '## Wiring CI' section"
    block = re.search(r"```yaml\n(.*?)```", section.group(1), re.S)
    assert block, "the 'Wiring CI' section has no yaml example"
    return block.group(1)


def child_screens_workflow(kit):
    """A child's own small workflow: one job, a checkout, then the steps of the kit's example, indented under it."""
    steps = "\n".join("      " + line if line else "" for line in wiring_example(kit).rstrip("\n").split("\n"))
    return ("name: Child screens\non:\n  pull_request:\njobs:\n  screens:\n    runs-on: ubuntu-latest\n"
            "    timeout-minutes: 15\n    steps:\n      - uses: actions/checkout@v4\n" + steps + "\n")


def test_the_walk_names_every_check():
    # Done-when 5: a new check in check_local.sh or checks.yml fails here until the walk names it.
    header = next(line for line in (ROOT / "scripts/check_local.sh").read_text(encoding="utf-8").split("\n")
                  if line.startswith("#   checks:"))
    local = set(header.split(":", 1)[1].split("(")[0].split())
    yml = (ROOT / ".github/workflows/checks.yml").read_text(encoding="utf-8")
    jobs = set(re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", yml.split("\njobs:", 1)[1], re.M))
    assert local - WALK_CHECKS["check_local"] == set(), "check_local.sh has a check the walk does not name"
    assert jobs - WALK_CHECKS["checks.yml"] == set(), "checks.yml has a job the walk does not name"


def test_a_sample_child_walks_the_whole_path_on_the_kit(tmp_path):
    started = time.monotonic()
    kit, kit_sha = make_kit(tmp_path / "kit")
    short = kit_sha[:7]
    # the first pin: a commit with the kit's own tree and no parent, made here, so the walk never needs history
    # (CI checks out a shallow merge commit, and its parent is not there)
    before = git(kit, "-c", "user.name=walk", "-c", "user.email=walk@example.com", "commit-tree",
                 git(kit, "rev-parse", f"{kit_sha}^{{tree}}"), "-m", "walk: the kit before the bump")
    stub = tmp_path / "stub"
    stub.mkdir()
    (stub / "gh").write_text(GH_STUB, encoding="utf-8")
    (stub / "gh").chmod(0o755)
    (stub / "protection.json").write_text(json.dumps(PROTECTED), encoding="utf-8")
    env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub),
           "SHIPQUICK_CLAUDE_SETTINGS": str(PONYTAIL_ON), "SHIPQUICK_SESSION": "shipquick-dev"}
    env.pop("CI", None)
    adopt = kit / "scripts/adopt.sh"
    check_local = kit / "scripts/check_local.sh"

    # 1. A child on main: a workflow and TypeScript-style test names, no Python tests.
    child = tmp_path / "child"
    child.mkdir()
    git(child, "init", "-q", "-b", "main")
    git(child, "config", "user.email", "walk@example.com")
    git(child, "config", "user.name", "Walk")
    (child / ".github/workflows").mkdir(parents=True)
    (child / ".github/workflows/ci.yml").write_text(CHILD_CI, encoding="utf-8")
    (child / "tests").mkdir()
    (child / "tests/app.test.ts").write_text("test('adds', () => {});\n", encoding="utf-8")
    (child / "tests/app.spec.ts").write_text("test('shows', () => {});\n", encoding="utf-8")
    stage(child)
    git(child, "commit", "-q", "-m", "chore: start the child")
    publish(child, "main")

    # 2. The kit on its own branch (rule 24), pinned as a submodule that the child has not adopted yet.
    git(child, "checkout", "-q", "-b", "kit")
    (child / "knowledge/shipquick_latest").mkdir(parents=True)
    git(child, "update-index", "--add", "--cacheinfo", f"160000,{before},knowledge/shipquick_latest")
    (child / ".gitmodules").write_text(GITMODULES, encoding="utf-8")   # a submodule has its entry, as in a real child
    git(child, "add", ".gitmodules")
    git(child, "commit", "-q", "-m", "chore: pin the kit")

    # 3. adopt.sh on the kit branch, then its files committed through the real hooks.
    step("adopt.sh", run(["bash", adopt, child, "--kit-branch", "kit", "--ref", before, "--coder", "shipquick-dev",
                          "--reviewer", "shipquick-qa", "--owner", "owner", "--milestone", "D0"], child, env))
    stage(child)
    step("commit adopt on kit", commit(child, env, "chore: adopt shipquick"))
    git(child, "remote", "add", "origin", "https://github.com/owner/child.git")
    publish(child, "kit")

    # 4. adopt.sh --check says adopted (the stub gh gives the required gate).
    out = step("adopt.sh --check", run(["bash", adopt, child, "--kit-branch", "kit", "--check"], child, env))
    assert "not adopted" not in out.lower(), out

    # 5. A bump branch cut from the kit: the pin moves to the kit under test, the commit passes the real hooks.
    git(child, "checkout", "-q", "-b", "bump/kit", "kit")
    step("adopt.sh --ref (bump)", run(["bash", adopt, child, "--kit-branch", "kit", "--ref", kit_sha, "--milestone", "D0"],
                                      child, env))
    git(child, "update-index", "--cacheinfo", f"160000,{kit_sha},knowledge/shipquick_latest")
    stage(child)
    step("commit bump", commit(child, env, f"chore: bump the kit to {short}"))
    publish(child, "bump/kit")
    step("check_local on the bump", run(["bash", check_local], child, {**env, "BASE": "kit"}))
    git(child, "checkout", "-q", "kit")
    git(child, "merge", "-q", "--no-ff", "-m", f"Merge bump the kit to {short}", "bump/kit")
    publish(child, "kit")

    # 6. A code branch from main: adopt.sh --gate-files copies the gate files and stages them (a gate-files PR).
    git(child, "checkout", "-q", "-b", "feat/1-app", "main")
    gate_out = step("adopt.sh --gate-files", run(["bash", adopt, child, "--kit-branch", "kit", "--gate-files"], child, env))
    stage(child)
    step("commit gate files", commit(child, env, "chore: gate files for this branch"))
    publish(child, "feat/1-app")
    step("check_local on the gate-files PR", run(["bash", check_local], child, {**env, "BASE": "kit"}))

    # 7. A code PR: a red test (TypeScript name), the screens list, and the workflow from the kit's own example.
    git(child, "checkout", "-q", "-b", "feat/2-greet")
    (child / "src").mkdir()
    (child / "src/greet.ts").write_text("export const greet = (name: string) => `hi ${name}`;\n", encoding="utf-8")
    (child / "tests/greet.spec.ts").write_text("test('greets', () => {});\n", encoding="utf-8")
    (child / "docs").mkdir(exist_ok=True)
    (child / "docs/screens.txt").write_text("Home\n", encoding="utf-8")
    (child / ".github/workflows/screens.yml").write_text(child_screens_workflow(kit), encoding="utf-8")
    step("check_screens_wired", run(["python3", kit / "scripts/check_screens_wired.py", "--screens-file",
                                     "docs/screens.txt", "--workflows-dir", ".github/workflows"], child, env))
    stage(child)
    step("commit the code PR",
         commit(child, env, "feat: greet the user", "## Red\n\ntests/greet.spec.ts names the greet test before src/greet.ts exists."))
    publish(child, "feat/2-greet")
    step("check_local on the code PR", run(["bash", check_local], child, {**env, "BASE": "kit"}))

    elapsed = time.monotonic() - started
    assert elapsed < 60, f"the walk took {elapsed:.0f} s; done-when 6 says under one minute"
