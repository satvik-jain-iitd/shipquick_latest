"""Story #120: scripts/check_environments.sh fails a child project whose CLAUDE.md has an empty
`Dev link:` or `Production link:` line, once the project is past milestone D0. At D0 it always passes
(nothing is deployed yet)."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_environments.sh"

FILLED = """# demo: Project Facts

## Environments
- Dev link: https://demo-dev.vercel.app
- Production link: https://demo.example.com
"""

EMPTY_DEV = """# demo: Project Facts

## Environments
- Dev link:
- Production link: https://demo.example.com
"""

PLACEHOLDER_PROD = """# demo: Project Facts

## Environments
- Dev link: https://demo-dev.vercel.app
- Production link: <url>
"""

NO_SECTION = """# demo: Project Facts

## Stack
- Language: Python
"""


def claude_md(tmp_path, text, name="CLAUDE.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def run(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def test_s120_d0_always_passes_even_with_nothing_filled(tmp_path):
    f = claude_md(tmp_path, NO_SECTION)
    r = run("--claude-md", str(f), "--milestone", "D0")
    assert r.returncode == 0, (r.stdout, r.stderr)


@pytest.mark.parametrize("milestone", ["D1", "D2", "D6"])
def test_s120_past_d0_both_links_filled_passes(tmp_path, milestone):
    f = claude_md(tmp_path, FILLED)
    r = run("--claude-md", str(f), "--milestone", milestone)
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_s120_past_d0_an_empty_dev_link_fails_and_names_it(tmp_path):
    f = claude_md(tmp_path, EMPTY_DEV)
    r = run("--claude-md", str(f), "--milestone", "D1")
    assert r.returncode == 1 and "Dev link" in r.stderr


def test_s120_past_d0_a_placeholder_production_link_fails_and_names_it(tmp_path):
    f = claude_md(tmp_path, PLACEHOLDER_PROD)
    r = run("--claude-md", str(f), "--milestone", "D2")
    assert r.returncode == 1 and "Production link" in r.stderr


def test_s120_past_d0_a_missing_section_fails_and_names_both(tmp_path):
    f = claude_md(tmp_path, NO_SECTION)
    r = run("--claude-md", str(f), "--milestone", "D1")
    assert r.returncode == 1
    assert "Dev link" in r.stderr and "Production link" in r.stderr


def test_s120_an_unknown_milestone_is_a_usage_error(tmp_path):
    f = claude_md(tmp_path, FILLED)
    r = run("--claude-md", str(f), "--milestone", "D9")
    assert r.returncode == 2 and "usage" in r.stderr.lower()


# ---- story #357: checks.yml takes the milestone from a caller input, default D1 (today's gate) ----
def test_s357_checks_yml_environments_job_reads_the_milestone_input():
    text = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
    assert "      milestone:\n" in text and "type: string\n        default: D1" in text
    assert "MILESTONE: ${{ inputs.milestone }}" in text and '--milestone "$MILESTONE"' in text
    assert "--milestone D1" not in text and "--milestone ${{" not in text    # never expanded inside run:
    assert "exempts" in text and "blocks a project" not in text


# ---- story #463: the environments job reads CLAUDE.md from the caller's kit_branch when set (as rule-copies does) ----
def _env_step():
    import yaml
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8"))
    return next(s for s in wf["jobs"]["environments"]["steps"] if "check_environments.sh" in s.get("run", ""))["run"]


def _git(cwd, *a):
    subprocess.run(["git", "-C", str(cwd), "-c", "user.email=t@t", "-c", "user.name=t", *a], check=True, capture_output=True)


def _env_run(tmp_path, *, kit, target, branch_claude, kit_claude):
    """Run the job's real shell step: a project checkout on `target` plus an origin that has a kit branch `documents`."""
    origin, work = tmp_path / "origin.git", tmp_path / "project"
    subprocess.run(["git", "init", "-q", "-b", "documents", str(origin)], check=True)
    if kit_claude is not None:
        (origin / "CLAUDE.md").write_text(kit_claude, encoding="utf-8")
        _git(origin, "add", "-A")
    _git(origin, "commit", "-q", "--allow-empty", "-m", "kit")
    if target != "documents":
        _git(origin, "branch", "-q", target)
    subprocess.run(["git", "clone", "-q", "-b", target, str(origin), str(work)], check=True)
    if branch_claude is not None:
        (work / "CLAUDE.md").write_text(branch_claude, encoding="utf-8")
    elif (work / "CLAUDE.md").exists():
        (work / "CLAUDE.md").unlink()
    (tmp_path / ".shipquick").mkdir()
    (tmp_path / ".shipquick" / "scripts").symlink_to(ROOT / "scripts")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "MILESTONE": "D1",
           "KIT_BRANCH": kit, "TARGET": target, "RUNNER_TEMP": str(tmp_path)}
    return subprocess.run(["bash", "-c", _env_step()], cwd=tmp_path, env=env, capture_output=True, text=True)


def test_s463_a_pr_into_a_branch_with_no_claude_md_reads_the_kit_branch_file(tmp_path):
    r = _env_run(tmp_path, kit="documents", target="main", branch_claude=None, kit_claude=FILLED)
    assert r.returncode == 0 and "environments OK" in r.stdout, r.stdout + r.stderr


def test_s463_the_kit_branch_file_decides_not_the_unfilled_copy_on_the_target_branch(tmp_path):
    r = _env_run(tmp_path, kit="documents", target="dev", branch_claude=EMPTY_DEV, kit_claude=FILLED)
    assert r.returncode == 0, r.stdout + r.stderr


def test_s463_an_unfilled_kit_branch_file_still_fails(tmp_path):
    r = _env_run(tmp_path, kit="documents", target="main", branch_claude=FILLED, kit_claude=EMPTY_DEV)
    assert r.returncode == 1 and "Dev link" in r.stderr


def test_s463_no_claude_md_on_the_kit_branch_fails_and_names_the_fix(tmp_path):
    r = _env_run(tmp_path, kit="documents", target="main", branch_claude=None, kit_claude=None)
    assert r.returncode == 1 and "no CLAUDE.md on kit branch documents" in r.stdout + r.stderr


def test_s463_without_a_kit_branch_the_job_reads_the_checkout_as_before(tmp_path):
    r = _env_run(tmp_path, kit="", target="main", branch_claude=EMPTY_DEV, kit_claude=FILLED)
    assert r.returncode == 1 and "Dev link" in r.stderr


def test_s463_a_pr_into_the_kit_branch_itself_reads_its_own_checkout(tmp_path):
    r = _env_run(tmp_path, kit="documents", target="documents", branch_claude=EMPTY_DEV, kit_claude=FILLED)
    assert r.returncode == 1 and "Dev link" in r.stderr
