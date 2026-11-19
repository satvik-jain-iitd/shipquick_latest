"""Child bump planner (M6a)."""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "child_bump.py"


def run(*args, cwd=None, env=None):
    import os
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd or ROOT, env=e)


def test_help_runs():
    r = run("--help")
    assert r.returncode == 0


def test_dry_run_prints_plan(tmp_path, monkeypatch):
    # build a fake registry
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "children.md").write_text("satvik-jain-iitd/GoServe\nklickbae8yt-star/job-search private\n")
    # stub gh
    stub = tmp_path / "stub"; stub.mkdir()
    (stub / "gh").write_text(
        '#!/usr/bin/env bash\n'
        'if [ "$1" = "api" ]; then\n'
        '  if echo "$*" | grep -q "commits/"; then echo "abc123"; exit 0; fi\n'
        '  echo "{\\"visibility\\": \\"public\\", \\"default_branch\\": \\"main\\"}"; exit 0\n'
        'fi\n'
        'exit 9\n'
    )
    (stub / "gh").chmod(0o755)
    env = {"PATH": f"{stub}:{__import__('os').environ['PATH']}"}
    r = run("--release-tag", "v0.15.0", cwd=tmp_path, env=env)
    # registry path is ROOT/docs/children.md; ROOT is cwd. But script uses ROOT=HERE.parent. HERE is scripts/. So ROOT=tmp_path. Good.
    assert r.returncode == 0, r.stdout + r.stderr
    assert "v0.15.0" in r.stdout
    assert "GoServe" in r.stdout


def test_apply_without_token_fails(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "children.md").write_text("satvik-jain-iitd/GoServe\n")
    stub = tmp_path / "stub"; stub.mkdir()
    (stub / "gh").write_text("#!/usr/bin/env bash\nexit 0\n")
    (stub / "gh").chmod(0o755)
    env = {"PATH": f"{stub}:{__import__('os').environ['PATH']}", "SHIPQUICK_CHILD_WRITE_TOKEN": ""}
    r = run("--release-tag", "v0.15.0", "--apply", cwd=tmp_path, env=env)
    assert r.returncode == 1


def test_json_output_valid(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "children.md").write_text("satvik-jain-iitd/GoServe\n")
    stub = tmp_path / "stub"; stub.mkdir()
    (stub / "gh").write_text(
        '#!/usr/bin/env bash\n'
        'if [ "$1" = "api" ]; then\n'
        '  if echo "$*" | grep -q "commits/"; then echo "abc123"; exit 0; fi\n'
        '  echo "{\\"visibility\\": \\"public\\", \\"default_branch\\": \\"main\\"}"; exit 0\n'
        'fi\n'
        'exit 9\n'
    )
    (stub / "gh").chmod(0o755)
    env = {"PATH": f"{stub}:{__import__('os').environ['PATH']}"}
    r = run("--release-tag", "v0.15.0", "--json", cwd=tmp_path, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    import json
    d = json.loads(r.stdout)
    assert d["release_tag"] == "v0.15.0"
    assert len(d["plans"]) == 1
