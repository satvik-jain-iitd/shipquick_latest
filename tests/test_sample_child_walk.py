"""Story #504: the kit's own CI walks a made-up child project through the whole path a real child takes.

The child is generated here, with nothing from a real project: TypeScript-style test names, a dev branch for the code,
the kit on its own branch (rule 24), a screens list, and a workflow written from the kit's own "Wiring CI" example.
The kit under test is a clone at one commit, placed where a real child keeps it: knowledge/shipquick_latest. The walk
runs the kit's own scripts from that folder, and pushes the gate-files PR and the code PR for real, so the pre-push
stage runs with the base the kit picks itself (story #469).

WALK_KIT_SHA=<sha> walks the kit as it was at that commit. The red runs in the PR body use it (#478 at v0.13.3,
#490 at v0.14.0, #501 before #505, #500 before #506).
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

from test_adopt import GH_STUB, PROTECTED   # the stub gh and the protection of the default branch, reused (story #504)

ROOT = Path(__file__).resolve().parent.parent
PONYTAIL_ON = ROOT / "tests/fixtures/adopt/settings-ponytail-on.json"
KIT_FOLDER = "knowledge/shipquick_latest"
GITMODULES = f'[submodule "{KIT_FOLDER}"]\n\tpath = {KIT_FOLDER}\n\turl = https://github.com/owner/kit.git\n'
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

# Every check of scripts/check_local.sh, and what the walk does with it. WALKED: the code PR's real push prints
# `ok   <name>`, and the walk asserts that line. NAMED: the walk does not run it, and the reason says why.
# A new check in check_local.sh must be in one of the two. A new job in checks.yml must be in CHECKS_YML.
WALKED = {
    "sizes", "markers", "md-blocks", "rule-copies", "workflow-security", "features-wiring", "commits",
    "commit-subjects", "pr-size", "frontend-design", "disable-comments", "design-tokens", "tdd", "roadmap",
}
NAMED = {
    "ui-docs": "needs the kit's own ui/ folder; a child has none",
    "ui-registry": "needs the kit's own ui/ folder; a child has none",
    "ui-topics": "needs the kit's own ui/ folder; a child has none",
    "ui-llms": "needs the kit's own ui/ folder; a child has none",
    "ui-proof": "needs the kit's own ui/ folder; a child has none",
    "ui-contracts": "needs the kit's own ui/ folder; a child has none",
    "ui-tokens": "needs the kit's own ui/ folder; a child has none",
    "ui-coverage": "needs the kit's own ui/ folder; a child has none",
    "story": "needs gh logged in to read the linked stories; CI runs it on GitHub",
    "shortcuts": "warn only: it prints a count and never passes or fails, so no 'ok' line exists to assert",
    "secrets": "needs gitleaks, which the CI test job does not install; the pre-commit job runs it on every commit",
    "secrets-staged": "the pre-commit stage; the walk's commits pass through it, but its gitleaks run is not asserted",
}
CHECKS_YML = {
    "adoption": "a GitHub job; adopt.sh --check is walked, the job reads the GitHub settings",
    "features": "a GitHub job; the feature wiring is in check_local features-wiring",
    "disable-comments": "a GitHub job; the local check is walked",
    "design-tokens": "a GitHub job; the local check is walked",
    "roles": "a GitHub job; reads .shipquick/roles.yml, which adopt writes",
    "team-block": "a GitHub job; reads the PR body, which the walk does not open",
    "frontend-design": "a GitHub job; the local check is walked",
    "uat-on-main": "a GitHub job; runs on a promotion into main",
    "freeze-on-main": "a GitHub job; runs on a merge into main",
    "environments": "a GitHub job; runs once a child is past D0",
    "component-registry": "a GitHub job; a child has no component registry",
    "rule-copies": "a GitHub job; the local check is walked",
    "commit-subjects": "a GitHub job; the local check is walked",
    "story": "a GitHub job; the local check needs gh, see NAMED",
    "gate": "a GitHub job; the required check that a PR merges through, not a step a child runs",
}


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
    """The kit under test: a clone of this repository at WALK_KIT_SHA, or at HEAD. Its history may be shallow (CI)."""
    sha = os.environ.get("WALK_KIT_SHA", "").strip() or git(ROOT, "rev-parse", "HEAD")
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(dest)], check=True)
    git(dest, "checkout", "-q", "--detach", sha)
    return git(dest, "rev-parse", "HEAD")


def commit(child, env, subject, body=""):
    msg = child.parent / "commit-msg.txt"
    msg.write_text(subject + ("\n\n" + body if body else "") + "\n", encoding="utf-8")
    return run(["git", "commit", "-q", "-F", msg], child, env)


def publish(child, *branches):
    """A stand-in for origin/<branch> for the bases (main, dev, kit): no push. The gate and code PRs are pushed for real."""
    for b in branches:
        git(child, "update-ref", f"refs/remotes/origin/{b}", b)


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
    assert local - WALKED - set(NAMED) == set(), "check_local.sh has a check the walk does not name"
    assert not (WALKED & set(NAMED)), "a check is both walked and named-only"
    yml = (ROOT / ".github/workflows/checks.yml").read_text(encoding="utf-8")
    jobs = set(re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", yml.split("\njobs:", 1)[1], re.M))
    assert jobs - set(CHECKS_YML) == set(), "checks.yml has a job the walk does not name"


def test_a_sample_child_walks_the_whole_path_on_the_kit(tmp_path):
    started = time.monotonic()
    stub = tmp_path / "stub"
    stub.mkdir()
    (stub / "gh").write_text(GH_STUB, encoding="utf-8")
    (stub / "gh").chmod(0o755)
    (stub / "protection.json").write_text(json.dumps(PROTECTED), encoding="utf-8")
    env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "STUB_DIR": str(stub),
           "SHIPQUICK_CLAUDE_SETTINGS": str(PONYTAIL_ON), "SHIPQUICK_SESSION": "shipquick-dev"}
    env.pop("BASE", None)   # the kit picks its own base (story #469); nothing here sets it
    env.pop("CI", None)

    # 1. A child on main, with a workflow and TypeScript-style test names. Its code lives on dev.
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
    git(child, "add", "-A")
    git(child, "commit", "-q", "-m", "chore: start the child")
    publish(child, "main")
    git(child, "checkout", "-q", "-b", "dev")
    publish(child, "dev")

    # 2. The kit under test, in the folder a real child keeps it. The first pin is a commit with the kit's own tree
    #    and no parent, made here, so the walk needs no history (CI checks out a shallow merge commit).
    kit_sha = make_kit(child / KIT_FOLDER)
    kit = child / KIT_FOLDER
    before = git(kit, "-c", "user.name=walk", "-c", "user.email=walk@example.com", "commit-tree",
                 git(kit, "rev-parse", f"{kit_sha}^{{tree}}"), "-m", "walk: the kit before the bump")
    git(kit, "checkout", "-q", "--detach", before)
    short = kit_sha[:7]

    # 3. The kit branch (rule 24): adopt.sh from the kit folder, then the files through the real hooks.
    git(child, "checkout", "-q", "-b", "kit", "dev")
    step("adopt.sh", run(["bash", kit / "scripts/adopt.sh", child, "--kit-branch", "kit", "--ref", before,
                          "--coder", "shipquick-dev", "--reviewer", "shipquick-qa", "--owner", "owner",
                          "--milestone", "D0"], child, env))
    (child / ".gitmodules").write_text(GITMODULES, encoding="utf-8")
    git(child, "add", "-A")
    step("commit adopt on kit", commit(child, env, "chore: adopt shipquick"))
    git(child, "remote", "add", "origin", "https://github.com/owner/child.git")
    publish(child, "kit")

    # 4. adopt.sh --check says adopted (the stub gh gives the required gate).
    out = step("adopt.sh --check", run(["bash", kit / "scripts/adopt.sh", child, "--kit-branch", "kit", "--check"],
                                       child, env))
    assert "not adopted" not in out.lower(), out

    # 5. A bump branch from the kit: the kit folder moves to the kit under test, the commit goes through the hooks,
    #    and check_local.sh picks the kit branch as its base by itself.
    git(child, "checkout", "-q", "-b", "bump/kit", "kit")
    git(kit, "checkout", "-q", "--detach", kit_sha)
    step("adopt.sh --ref (bump)", run(["bash", kit / "scripts/adopt.sh", child, "--kit-branch", "kit",
                                       "--ref", kit_sha, "--milestone", "D0"], child, env))
    git(child, "add", "-A")
    step("commit bump", commit(child, env, f"chore: bump the kit to {short}"))
    bump_out = step("check_local on the bump", run(["bash", kit / "scripts/check_local.sh"], child, env))
    assert "base: origin/kit" in bump_out, "check_local did not pick the kit branch as the bump's base:\n" + bump_out[-800:]
    git(child, "checkout", "-q", "kit")
    git(child, "merge", "-q", "--no-ff", "-m", f"Merge bump the kit to {short}", "bump/kit")
    publish(child, "kit")

    # 6. The gate-files PR: a branch from dev, adopt.sh --gate-files copies the gate files, and the real push runs
    #    the pre-push hooks with the base the kit picks.
    git(child, "checkout", "-q", "-b", "feat/1-app", "dev")
    step("adopt.sh --gate-files", run(["bash", kit / "scripts/adopt.sh", child, "--kit-branch", "kit",
                                       "--gate-files"], child, env))
    git(child, "add", "-A")
    step("commit gate files", commit(child, env, "chore: gate files for this branch"))
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "-q", "--bare", str(origin))
    git(child, "remote", "set-url", "--push", "origin", str(origin))
    step("push the gate-files PR", run(["git", "push", "-q", "-u", "origin", "feat/1-app"], child, env))

    # 7. The code PR: a red test (TypeScript name), the screens list and the workflow from the kit's own example.
    git(child, "checkout", "-q", "-b", "feat/2-greet", "feat/1-app")
    (child / "src").mkdir()
    (child / "src/greet.ts").write_text("export const greet = (name: string) => `hi ${name}`;\n", encoding="utf-8")
    (child / "tests/greet.spec.ts").write_text("test('greets', () => {});\n", encoding="utf-8")
    (child / "docs").mkdir(exist_ok=True)
    (child / "docs/screens.txt").write_text("Home\n", encoding="utf-8")
    (child / ".github/workflows/screens.yml").write_text(child_screens_workflow(kit), encoding="utf-8")
    step("check_screens_wired", run(["python3", kit / "scripts/check_screens_wired.py", "--screens-file",
                                     "docs/screens.txt", "--workflows-dir", ".github/workflows"], child, env))
    git(child, "add", "-A")
    step("commit the code PR",
         commit(child, env, "feat: greet the user", "## Red\n\ntests/greet.spec.ts names the greet test before src/greet.ts exists."))
    step("push the code PR", run(["git", "push", "-q", "-u", "origin", "feat/2-greet"], child, env))
    # The same pre-push hook, verbose, so the per-check lines show (pre-commit prints only "Passed" for a passing hook).
    verbose = step("pre-push stage of the code PR", run(["pre-commit", "run", "--hook-stage", "pre-push", "--verbose",
                                                          "check-local-push"], child, env))
    assert "base: origin/kit" not in verbose, "the code PR must not pick the kit branch as its base"
    walked_missing = sorted(n for n in WALKED if not re.search(rf"^ok\s+{re.escape(n)}\s*$", verbose, re.M))
    assert walked_missing == [], f"the code PR's pre-push stage did not print 'ok' for: {walked_missing}\n{verbose[-1200:]}"

    elapsed = time.monotonic() - started
    assert elapsed < 60, f"the walk took {elapsed:.0f} s; done-when 6 says under one minute"
