"""Story #146 (epic #130, GoServe feedback #146; validated shape: GoServe story #821, PR #823).
scripts/screens.sh orchestrates the project's own `npx playwright test` against its screens spec:
bare = render only, --check = render and compare, --update = replace the accepted pictures. A stub
`npx` on PATH stands in for the real Playwright CLI (no network, no browser) and logs every
invocation so tests can assert the orchestration, not the rendering."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "screens.sh"

STUB_NPX_OK = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
printf '%s\\n' "$SCREENS_OUT" >> "$STUB_DIR/env.log"
printf '%s\\n' "${SCREENS_RENDER_ONLY:-}" >> "$STUB_DIR/env.log"
exit 0
"""

STUB_NPX_FAILS = """#!/usr/bin/env bash
echo "$*" >> "$STUB_DIR/calls.log"
exit 1
"""


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "docs").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(r)], check=True)   # screens.sh finds its root via git
    return r


def stub(tmp_path, script):
    d = tmp_path / "stub"
    d.mkdir()
    (d / "npx").write_text(script, encoding="utf-8")
    (d / "npx").chmod(0o755)
    return d


def run(repo, tmp_path, script, *args, env_extra=None):
    d = stub(tmp_path, script)
    env = {**os.environ, "PATH": f"{d}:{os.environ['PATH']}", "STUB_DIR": str(d),
            "SCREENS_APP_DIR": str(repo), **(env_extra or {})}
    r = subprocess.run(["bash", str(SCRIPT), *args], cwd=repo, capture_output=True, text=True, env=env)
    r.calls = (d / "calls.log").read_text(encoding="utf-8") if (d / "calls.log").exists() else ""
    r.envlog = (d / "env.log").read_text(encoding="utf-8") if (d / "env.log").exists() else ""
    return r


def write_screens(repo, text):
    (repo / "docs" / "screens.txt").write_text(text, encoding="utf-8")


SCREENS = "welcome | /welcome | 390x844 | welcome\n"


def test_with_no_screens_file_the_run_is_skipped(repo, tmp_path):
    r = run(repo, tmp_path, STUB_NPX_OK)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skipped" in r.stdout
    assert r.calls == ""


def test_an_empty_screens_file_is_skipped_like_none_configured(repo, tmp_path):
    write_screens(repo, "# nothing yet\n")
    r = run(repo, tmp_path, STUB_NPX_OK)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "skipped" in r.stdout
    assert r.calls == ""


def test_bare_call_renders_only_and_sets_the_render_only_env_var(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_OK)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "playwright test tests/e2e/screens.spec.ts --project=chromium" in r.calls
    assert "--update-snapshots" not in r.calls
    assert "1" in r.envlog.splitlines()   # SCREENS_RENDER_ONLY was set


def test_check_compares_without_the_render_only_env_var(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_OK, "--check")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "playwright test tests/e2e/screens.spec.ts --project=chromium" in r.calls
    assert "--update-snapshots" not in r.calls
    lines = r.envlog.splitlines()
    assert lines[-1] == ""   # SCREENS_RENDER_ONLY not set this time


def test_update_passes_update_snapshots(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_OK, "--update")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "--update-snapshots" in r.calls


def test_an_unknown_flag_is_refused(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_OK, "--bogus")
    assert r.returncode == 2
    assert r.calls == ""


def test_a_failing_check_exits_nonzero_and_still_reports_where_the_renders_are(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_FAILS, "--check")
    assert r.returncode != 0
    assert "renders:" in r.stdout


def test_screens_out_defaults_under_the_app_dir(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_OK)
    assert r.returncode == 0, (r.stdout, r.stderr)
    out_dir = r.envlog.splitlines()[0]
    assert out_dir == str(repo / "screens-out")


def test_screens_out_env_var_overrides_the_default(repo, tmp_path):
    write_screens(repo, SCREENS)
    custom = str(tmp_path / "custom-out")
    r = run(repo, tmp_path, STUB_NPX_OK, env_extra={"SCREENS_OUT": custom})
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert r.envlog.splitlines()[0] == custom


def test_a_custom_spec_path_is_used(repo, tmp_path):
    write_screens(repo, SCREENS)
    r = run(repo, tmp_path, STUB_NPX_OK, env_extra={"SCREENS_SPEC": "e2e/custom.spec.ts"})
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "playwright test e2e/custom.spec.ts --project=chromium" in r.calls
