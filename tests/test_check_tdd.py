"""Story #319 (A15): a PR that changes code names the test it turned red first, and that test file is in the PR diff.
Docs-only PRs and dev <-> main PRs are exempt. Tests use a real throwaway git repo, not a stubbed diff."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_tdd.py"

RED_OK = "Summary.\n\n## Red\n\n- tests/test_widget.py::test_widget_rejects_empty (failed first)\n\n## Local proof\nran it\n"


def make_repo(tmp_path, files):
    """A repo with a dev base commit, origin/dev pointing at it, and one feature commit adding `files`."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("checkout", "-q", "-b", "feat/319-x")
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "feat: x")
    return repo


def run(tmp_path, repo, body, *extra):
    body_file = tmp_path / "body.md"
    body_file.write_text(body, encoding="utf-8")
    return subprocess.run(
        ["python3", str(SCRIPT), "--body-file", str(body_file), "--base", "origin/dev", "--repo", str(repo), *extra],
        capture_output=True, text=True,
    )


CODE = {"scripts/widget.py": "def widget():\n    return 1\n", "tests/test_widget.py": "def test_widget_rejects_empty():\n    pass\n"}


def test_s319_a_code_pr_whose_body_has_no_red_section_fails(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nA widget.\n")
    assert r.returncode == 1 and "## Red" in r.stdout, r.stdout


def test_s319_a_red_section_naming_a_test_file_in_the_diff_passes(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, RED_OK)
    assert r.returncode == 0 and "tdd OK" in r.stdout, r.stdout


def test_s319_a_red_section_naming_a_test_not_in_the_diff_fails(tmp_path):
    repo = make_repo(tmp_path, {"scripts/widget.py": "x = 1\n"})
    r = run(tmp_path, repo, RED_OK)
    assert r.returncode == 1 and "tests/test_widget.py" in r.stdout and "not in the PR diff" in r.stdout, r.stdout


def test_s319_a_red_section_that_names_no_test_fails(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## Red\n\nI wrote it first, trust me.\n")
    assert r.returncode == 1 and "names no test" in r.stdout, r.stdout


def test_s319_a_test_file_deleted_in_the_diff_is_not_evidence(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    git("init", "-q", "-b", "dev")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_widget.py").write_text("def test_w():\n    pass\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "chore: base")
    git("update-ref", "refs/remotes/origin/dev", "HEAD")
    git("checkout", "-q", "-b", "feat/319-x")
    git("rm", "-q", "tests/test_widget.py")
    (repo / "scripts").mkdir()
    (repo / "scripts" / "widget.py").write_text("x = 1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "feat: drop a test")
    r = run(tmp_path, repo, "## Red\n\n- tests/test_widget.py\n")
    assert r.returncode == 1 and "not in the PR diff" in r.stdout, r.stdout


@pytest.mark.parametrize("files", [
    {"docs/guide.md": "# Guide\n", "pm/agile/notes.txt": "plan\n"},
    {"README.md": "# Readme\n"},
])
def test_s319_a_docs_only_pr_is_exempt_and_needs_no_red_section(tmp_path, files):
    repo = make_repo(tmp_path, files)
    r = run(tmp_path, repo, "## What\nDocs only.\n")
    assert r.returncode == 0 and "exempt" in r.stdout and "docs" in r.stdout, r.stdout


def test_s319_a_dev_into_main_promotion_is_exempt(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nPromotion.\n", "--base-branch", "main", "--head-branch", "dev")
    assert r.returncode == 0 and "exempt" in r.stdout, r.stdout


def test_s319_a_main_into_dev_back_merge_is_exempt(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nBack-merge.\n", "--base-branch", "dev", "--head-branch", "main")
    assert r.returncode == 0 and "exempt" in r.stdout, r.stdout


def test_s319_a_feature_pr_into_dev_is_not_exempt(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## What\nNo red.\n", "--base-branch", "dev", "--head-branch", "feat/319-x")
    assert r.returncode == 1, r.stdout


def test_s81_a_node_test_file_in_the_red_section_passes(tmp_path):
    # story #81: the roadmap tests are node:test files, so `roadmap/x.test.js` is a test path too
    repo = make_repo(tmp_path, {"roadmap/render.js": "module.exports = {};\n", "roadmap/golden.test.js": "require('node:test');\n"})
    r = run(tmp_path, repo, "## What\nx\n\n## Red\n\n- roadmap/golden.test.js (28 failed first)\n\n## Tests\nok\n")
    assert r.returncode == 0 and "tdd OK: roadmap/golden.test.js" in r.stdout, r.stdout


def test_s319_a_pytest_node_id_names_its_file(tmp_path):
    repo = make_repo(tmp_path, CODE)
    r = run(tmp_path, repo, "## Red\n\n- tests/test_widget.py::test_widget_rejects_empty\n")
    assert r.returncode == 0, r.stdout


def test_s319_ci_has_a_tdd_job_on_every_pr_and_the_gate_waits_for_it():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "\n  tdd:\n" in ci and "scripts/check_tdd.py" in ci
    gate = ci.split("\n  gate:\n", 1)[1]
    assert "tdd" in gate.split("needs: [", 1)[1].split("]", 1)[0].split(", ")


def test_s319_check_local_runs_the_tdd_check():
    text = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "tdd)" in text and "check_tdd.py" in text


# ---- review of #336 ----
import re  # noqa: E402


def _tdd_job():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    m = re.search(r"^  tdd:\n(.*?)(?=^  [a-z][a-z-]*:\n|\Z)", text, re.M | re.S)
    assert m, "no tdd job in ci.yml"
    return m.group(1)


def test_s319_dependabot_is_exempt_in_the_tdd_job_like_team_block():
    job = _tdd_job()
    assert "PR_AUTHOR: ${{ github.event.pull_request.user.login }}" in job
    assert 'case "$PR_AUTHOR" in' in job
    assert r"dependabot\[bot\]|app/dependabot" in job
    # the exemption comes before the check runs
    assert job.index('case "$PR_AUTHOR"') < job.index("check_tdd.py")


def test_s319_check_local_usage_and_header_name_tdd():
    lines = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8").splitlines()
    usage = next(ln for ln in lines if ln.startswith("#   checks:"))
    assert " tdd " in usage + " ", usage
    header = "\n".join(ln for ln in lines[:15] if ln.startswith("#"))
    assert "tdd (story #319):" in header
    assert "commit body" in header and "## Red" in header


def test_s319_commit_guidelines_say_a_code_branch_carries_a_red_line():
    text = (ROOT / "COMMIT_GUIDELINES.md").read_text(encoding="utf-8")
    assert "## Red" in text and "commit body" in text


def test_s319_the_pr_template_has_a_red_section_above_test_output():
    text = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    assert "## Red" in text and "## Test Output" in text
    assert text.index("## Red") < text.index("## Test Output")
    assert "tests/test_widget.py::test_widget_rejects_empty" in text


# ---- story #454: a kit bump (the pin plus files adopt.sh writes) is not code to test ----
BUMP = {
    "knowledge/shipquick_latest": "gitlink stand-in\n",
    ".github/workflows/shipquick-call.yml": "name: ShipQuick checks\n",
    ".github/workflows/roadmap-call.yml": "name: Roadmap\n",
    ".shipquick/features.json": "{}\n",
    ".shipquick/roles.yml": "coders: []\n",
    ".pre-commit-config.yaml": "repos: []\n",
    ".gitattributes": "docs/LEARNINGS.md merge=union\n",
    "roadmap.json": "{}\n",
    ".claude/commands/mode.md": "mode\n",
    "CLAUDE.md": "pointer\n",
}


def test_s454_the_bump_list_is_exact_paths_a_file_under_shipquick_is_code(tmp_path):
    repo = make_repo(tmp_path, {"knowledge/shipquick_latest": "x\n", ".shipquick/hook.sh": "echo hi\n"})
    r = run(tmp_path, repo, "chore: bump\n")
    assert r.returncode == 1 and "## Red" in r.stdout, r.stdout


def test_s454_every_code_file_adopt_writes_is_on_the_bump_list(tmp_path):
    """One list, scripts/adopt_files.txt: adopt.sh at its widest writes nothing outside it (md and txt files are never code)."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_tdd
    from test_adopt import adopt, with_origin, gh as _gh  # noqa: F401
    child = tmp_path / "kid"
    (child / ".github" / "workflows").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "dev", str(child)], check=True)
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(child), "config", k, v], check=True)
    r = adopt(child, "--platforms", "android,ios,web", "--coder", "a", "--reviewer", "b", "--owner", "c")
    assert r.returncode == 0, r.stderr
    written = subprocess.run(["git", "-C", str(child), "ls-files", "-o", "--exclude-standard"], capture_output=True, text=True).stdout.split()
    code = [f for f in written if check_tdd.is_code(f)]
    assert code, "adopt wrote no code file; the test is not looking at anything"
    stray = [f for f in code if not check_tdd.is_bump_file(f)]
    assert stray == [], "adopt.sh writes these but scripts/adopt_files.txt does not list them: %s" % stray


def test_s454_a_diff_of_only_the_pin_and_adopt_files_is_exempt_without_a_red_section(tmp_path):
    repo = make_repo(tmp_path, BUMP)
    r = run(tmp_path, repo, "chore: bump\n", "--head-branch", "chore/shipquick-v0.13.0")
    assert r.returncode == 0 and "tdd exempt" in r.stdout and "kit bump" in r.stdout, r.stdout


def test_s454_the_same_bump_plus_one_code_file_still_needs_a_red_section(tmp_path):
    repo = make_repo(tmp_path, {**BUMP, "src/app.py": "x = 1\n"})
    r = run(tmp_path, repo, "chore: bump\n", "--head-branch", "chore/shipquick-v0.13.0")
    assert r.returncode == 1 and "## Red" in r.stdout, r.stdout


def test_s454_adopt_files_without_the_pin_are_not_a_bump(tmp_path):
    repo = make_repo(tmp_path, {k: v for k, v in BUMP.items() if k != "knowledge/shipquick_latest"})
    r = run(tmp_path, repo, "chore: x\n")
    assert r.returncode == 1 and "## Red" in r.stdout, r.stdout


# ---- story #491 (feedback #490): the gate-files PR is exempt from tdd, read from the same lists as the gate files ----
GATE_PATHS = [l.strip() for l in (ROOT / "scripts" / "gate_files.txt").read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]


def _check_tdd():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_tdd
    return check_tdd


def test_s491_a_gate_files_pr_with_the_pin_and_gitmodules_is_exempt_without_a_red_section():
    """Feedback #490: the gate files of a kit-branch child include .gitmodules, which the bump list did not have."""
    ct = _check_tdd()
    changed = [ct.BUMP_PIN] + [p for p in GATE_PATHS if p != ct.BUMP_PIN]
    assert ".gitmodules" in changed
    assert ct.exempt_reason(changed, "dev", "feat/491-x"), "a gate-files PR must be exempt, as a kit bump is"


def test_s491_every_path_of_gate_files_is_on_the_exempt_list():
    ct = _check_tdd()
    missing = [p for p in GATE_PATHS if not ct.is_bump_file(p)]
    assert missing == [], "scripts/gate_files.txt lists these, but check_tdd.py does not exempt them: %s" % missing


def test_s491_gate_files_plus_one_other_code_file_still_needs_a_red_section():
    ct = _check_tdd()
    changed = [ct.BUMP_PIN] + GATE_PATHS + ["scripts/other.py"]
    assert ct.exempt_reason(changed, "dev", "feat/491-x") is None


def test_s491_gate_files_without_the_pin_still_need_a_red_section():
    ct = _check_tdd()
    changed = [p for p in GATE_PATHS if p != ct.BUMP_PIN]
    assert ct.exempt_reason(changed, "dev", "feat/491-x") is None


def test_s491_the_exempt_list_reads_the_gate_file_and_types_no_path_twice():
    src = (ROOT / "scripts" / "check_tdd.py").read_text(encoding="utf-8")
    assert "gate_files.txt" in src and "adopt_files.txt" in src
    assert ".gitmodules" not in src, "the gate files live in scripts/gate_files.txt only"


def test_s491_a_missing_list_file_exits_one_with_one_line_naming_it(tmp_path):
    # Round two of #492 (QA): a missing list is a clear one-line stop, never a traceback and never a guessed exempt set.
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_tdd.py").write_text((ROOT / "scripts" / "check_tdd.py").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "scripts" / "adopt_files.txt").write_text((ROOT / "scripts" / "adopt_files.txt").read_text(encoding="utf-8"), encoding="utf-8")
    body = tmp_path / "body.md"
    body.write_text("no red\n", encoding="utf-8")
    r = subprocess.run(["python3", str(tmp_path / "scripts" / "check_tdd.py"), "--body-file", str(body), "--base", "origin/dev"],
                       capture_output=True, text=True)
    assert r.returncode == 1, (r.stdout, r.stderr)
    assert "Traceback" not in r.stdout + r.stderr
    lines = r.stdout.strip().splitlines()
    assert len(lines) == 1 and "gate_files.txt" in lines[0], lines


# ---- story #502 (feedback #501): the test names of other runners are accepted, one list in the script ----

def _red(*names):
    return "Summary.\n\n## Red\n\n" + "".join(f"- {n} (failed first)\n" for n in names) + "\n## Local proof\nran it\n"


@pytest.mark.parametrize("name", [
    "app/tests/unit/x.test.ts",          # TypeScript unit test (feedback #501)
    "app/tests/e2e/x.spec.ts",           # TypeScript e2e spec (feedback #501)
    "web/src/Button.test.tsx",
    "web/src/Button.spec.jsx",
    "lib/index.test.mjs",
    "lib/index.spec.cjs",
    "internal/parser_test.go",           # Go
    "src/test/kotlin/ParserTest.kt",     # Kotlin
    "src/test/kotlin/ParserTests.kt",
    "Tests/ParserTest.swift",            # Swift
    "Tests/ParserTests.swift",
    "pkg/x_test.py",                     # pytest or unittest, another folder
])
def test_s502_a_known_test_file_name_in_red_passes(tmp_path, name):
    repo = make_repo(tmp_path, {"app/src/x.ts": "x\n", name: "red\n"})
    r = run(tmp_path, repo, _red(name))
    assert r.returncode == 0 and "tdd OK" in r.stdout, r.stdout + r.stderr


def test_s502_a_typescript_red_test_that_is_not_in_the_diff_still_fails(tmp_path):
    repo = make_repo(tmp_path, {"app/src/x.ts": "x\n"})
    r = run(tmp_path, repo, _red("app/tests/unit/x.test.ts"))
    assert r.returncode == 1 and "not in the PR diff" in r.stdout, r.stdout


def test_s502_a_fixture_in_a_tests_folder_is_not_a_test_and_says_so(tmp_path):
    repo = make_repo(tmp_path, {"app/src/x.ts": "x\n", "tests/fixtures/data.json": "{}\n"})
    r = run(tmp_path, repo, _red("tests/fixtures/data.json"))
    assert r.returncode == 1, r.stdout
    assert "tests/fixtures/data.json" in r.stdout and "not a known test file name" in r.stdout, r.stdout


def test_s502_the_name_list_is_one_line_per_runner_in_the_script():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_tdd", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert len(mod.TEST_NAMES) >= 8, mod.TEST_NAMES
    assert all(isinstance(p, str) and p for p in mod.TEST_NAMES)
