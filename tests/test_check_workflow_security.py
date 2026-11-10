"""Story #325 (A7): scripts/check_workflow_security.py. A workflow triggered by pull_request_target or
workflow_run must not check out the PR head, and no npm ci or npm install may run without --ignore-scripts.
Fixtures: tests/fixtures/workflow_security (bad checkout, bad npm line, clean file)."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_workflow_security.py"
FIX = ROOT / "tests" / "fixtures" / "workflow_security"


def run(*args, cwd=ROOT):
    return subprocess.run(["python3", str(SCRIPT), *map(str, args)], capture_output=True, text=True, cwd=cwd)


def line_of(path, needle):
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if needle in line:
            return i
    raise AssertionError(f"{needle!r} not in {path}")


def test_s325_a_clean_file_passes():
    r = run(FIX / "clean.yml")
    assert r.returncode == 0, r.stdout + r.stderr


def test_s325_a_pull_request_target_checkout_of_the_pr_head_fails_and_names_file_and_line():
    f = FIX / "bad_checkout.yml"
    r = run(f)
    assert r.returncode == 1, r.stdout + r.stderr
    assert f"bad_checkout.yml:{line_of(f, 'pull_request.head.sha')}" in r.stdout, r.stdout


def test_s325_an_npm_ci_without_ignore_scripts_fails_and_names_file_and_line():
    f = FIX / "bad_npm.yml"
    r = run(f)
    assert r.returncode == 1, r.stdout + r.stderr
    assert f"bad_npm.yml:{line_of(f, 'npm ci --no-audit')}" in r.stdout, r.stdout


def test_s325_the_repo_own_workflows_pass():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr


def test_s325_workflow_run_checkout_of_the_head_sha_fails(tmp_path):
    f = tmp_path / "wr.yml"
    f.write_text(
        "on:\n  workflow_run:\n    workflows: [CI]\n    types: [completed]\n"
        "jobs:\n  b:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    steps:\n"
        "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1\n"
        "        with:\n          ref: ${{ github.event.workflow_run.head_sha }}\n",
        encoding="utf-8",
    )
    r = run(f)
    assert r.returncode == 1 and "wr.yml:" in r.stdout, r.stdout


def test_s325_a_plain_pull_request_checkout_of_the_head_is_normal_and_passes(tmp_path):
    f = tmp_path / "pr.yml"
    f.write_text(
        "on:\n  pull_request:\n"
        "jobs:\n  t:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    steps:\n"
        "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1\n"
        "        with:\n          ref: ${{ github.event.pull_request.head.sha }}\n",
        encoding="utf-8",
    )
    assert run(f).returncode == 0


def test_s325_a_pull_request_target_checkout_of_the_base_passes(tmp_path):
    f = tmp_path / "base.yml"
    f.write_text(
        "on: [pull_request_target]\n"
        "jobs:\n  t:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    steps:\n"
        "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1\n",
        encoding="utf-8",
    )
    assert run(f).returncode == 0


def test_s325_an_npm_install_in_a_comment_or_a_name_is_not_a_run(tmp_path):
    f = tmp_path / "c.yml"
    f.write_text(
        "on: push\njobs:\n  t:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    steps:\n"
        "      - name: npm install the deps\n        run: echo ok\n"
        "      # run: npm ci\n",
        encoding="utf-8",
    )
    assert run(f).returncode == 0


def test_s325_ci_has_the_job_gate_needs_it_and_check_local_runs_it():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "scripts/check_workflow_security.py" in ci
    assert "needs.workflow-security.result" in ci and re.search(r"needs: \[.*\bworkflow-security\b.*\]", ci)
    local = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "check_workflow_security.py" in local and "workflow-security)" in local


# ---- review of #337: three wrong answers, each reproduced ----
CRON_THEN_PATHS_FILTER = """name: x
on:
  schedule:
    - cron: "0 0 * * *"
  pull_request_target:
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: dorny/paths-filter@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}
"""

LIST_FORM_ON = """name: x
on:
  - pull_request_target
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}
"""

REAL_HEAD_CHECKOUT_AFTER_CRON = CRON_THEN_PATHS_FILTER.replace(
    "      - uses: actions/checkout@v4\n        with:\n          persist-credentials: false\n",
    "      - uses: actions/checkout@v4\n        with:\n          ref: ${{ github.event.pull_request.head.sha }}\n")


def wf(tmp_path, text):
    f = tmp_path / "w.yml"
    f.write_text(text, encoding="utf-8")
    return f


def test_s325_a_later_step_with_a_head_ref_is_not_blamed_on_a_clean_checkout(tmp_path):
    for text in (CRON_THEN_PATHS_FILTER, LIST_FORM_ON):
        r = run(wf(tmp_path, text))
        assert r.returncode == 0, text + r.stdout


def test_s325_a_real_head_checkout_after_a_cron_list_still_fails(tmp_path):
    r = run(wf(tmp_path, REAL_HEAD_CHECKOUT_AFTER_CRON))
    assert r.returncode == 1 and "checks out the PR head" in r.stdout


def npm_job(run_value):
    return f"name: x\non: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: {run_value}\n"


def test_s325_the_flag_must_sit_on_each_install_command(tmp_path):
    for cmd in ("npm ci --ignore-scripts && npm install",
                "cd ui/tool && npm ci --ignore-scripts && cd ../web && npm ci",
                "npm ci --ignore-scripts; npm i",
                "npm ci --ignore-scripts || npm install"):
        f = wf(tmp_path, npm_job(cmd))
        r = run(f)
        assert r.returncode == 1, cmd + r.stdout
        assert f"{f}:7" in r.stdout, r.stdout


def test_s325_every_install_with_the_flag_passes_even_when_chained(tmp_path):
    r = run(wf(tmp_path, npm_job("cd ui/tool && npm ci --ignore-scripts && npm install --ignore-scripts")))
    assert r.returncode == 0, r.stdout


def test_s325_a_folded_block_joins_its_lines_with_a_space(tmp_path):
    folded = "name: x\non: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: >\n          npm ci\n          --ignore-scripts\n"
    assert run(wf(tmp_path, folded)).returncode == 0
    folded_bad = folded.replace("          --ignore-scripts\n", "          --prefix ui\n")
    assert run(wf(tmp_path, folded_bad)).returncode == 1


def test_s325_a_literal_block_still_checks_each_line(tmp_path):
    literal = "name: x\non: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: |\n          npm ci\n          --ignore-scripts\n"
    assert run(wf(tmp_path, literal)).returncode == 1       # a literal block is two commands, the first has no flag


def test_s325_check_local_usage_and_unknown_list_name_workflow_security():
    lines = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8").splitlines()
    usage = next(ln for ln in lines if ln.startswith("#   checks:"))
    unknown = next(ln for ln in lines if "unknown check:" in ln)
    assert "workflow-security" in usage and "workflow-security" in unknown
