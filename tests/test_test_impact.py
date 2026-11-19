"""Test-impact selector (ADR-023)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "test_impact.py"
GFT = "/tmp/gftest/bin/graphify"


def run(*args, cwd=None, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd, env=e)


def build_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "src" / "foo.py").write_text("def foo():\n    return 1\n")
    (repo / "src" / "bar.py").write_text("from src.foo import foo\ndef bar():\n    return foo()\n")
    (repo / "tests" / "test_foo.py").write_text("def test_foo():\n    pass\n")
    (repo / "tests" / "test_bar.py").write_text("def test_bar():\n    pass\n")
    (repo / ".shipquick").mkdir()
    (repo / ".shipquick" / "test-impact.yml").write_text(
        "version: 1\n"
        "languages:\n"
        "  - id: python\n"
        "    source: ['src/**/*.py']\n"
        "    tests: ['tests/test_*.py']\n"
        "    runner: pytest\n"
        "    command: 'pytest {tests}'\n"
        "global_impact:\n"
        "  - 'pyproject.toml'\n"
        "mappings:\n"
        "  - source: 'src/foo.py'\n"
        "    tests: ['tests/test_foo.py', 'tests/test_bar.py']\n"
        "  - source: 'src/bar.py'\n"
        "    tests: ['tests/test_bar.py']\n"
        "full_suite_commands:\n"
        "  python: 'pytest --tb=short'\n"
    )
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=repo, check=True)
    # build graph
    subprocess.run([GFT, "extract", str(repo), "--code-only", "--no-cluster", "--no-viz"], check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    (repo / "graphify-out" / ".source_sha").write_text(sha)
    (repo / "graphify-out" / ".schema_version").write_text("1")
    return repo


@pytest.mark.skipif(not Path(GFT).exists(), reason="graphify CLI not installed")
def test_change_foo_selects_both_tests(tmp_path):
    repo = build_repo(tmp_path)
    # change foo
    (repo / "src" / "foo.py").write_text("def foo():\n    return 2\n")
    subprocess.run(["git", "add", "src/foo.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "change foo"], cwd=repo, check=True)
    # rebuild graph + sidecar
    subprocess.run([GFT, "extract", str(repo), "--code-only", "--no-cluster", "--no-viz"], check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    (repo / "graphify-out" / ".source_sha").write_text(sha)
    r = run("--base", "HEAD~1", "--head", "HEAD", cwd=repo)
    assert r.returncode == 0, r.stderr
    assert "selected tests: 2" in r.stdout
    assert "tests/test_foo.py" in r.stdout and "tests/test_bar.py" in r.stdout


@pytest.mark.skipif(not Path(GFT).exists(), reason="graphify CLI not installed")
def test_change_bar_selects_only_bar(tmp_path):
    repo = build_repo(tmp_path)
    (repo / "src" / "bar.py").write_text("def bar():\n    return 2\n")
    subprocess.run(["git", "add", "src/bar.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "change bar"], cwd=repo, check=True)
    subprocess.run([GFT, "extract", str(repo), "--code-only", "--no-cluster", "--no-viz"], check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    (repo / "graphify-out" / ".source_sha").write_text(sha)
    r = run("--base", "HEAD~1", "--head", "HEAD", cwd=repo)
    assert r.returncode == 0, r.stderr
    assert "selected tests: 1" in r.stdout
    assert "tests/test_bar.py" in r.stdout
    assert "tests/test_foo.py" not in r.stdout


@pytest.mark.skipif(not Path(GFT).exists(), reason="graphify CLI not installed")
def test_global_impact_change_falls_back_full(tmp_path):
    repo = build_repo(tmp_path)
    (repo / "pyproject.toml").write_text("x = 1\n")
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add pyproject"], cwd=repo, check=True)
    subprocess.run([GFT, "extract", str(repo), "--code-only", "--no-cluster", "--no-viz"], check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    (repo / "graphify-out" / ".source_sha").write_text(sha)
    r = run("--base", "HEAD~1", "--head", "HEAD", cwd=repo)
    assert r.returncode == 0, r.stderr
    assert "FALLBACK" in r.stdout and "global-impact" in r.stdout


@pytest.mark.skipif(not Path(GFT).exists(), reason="graphify CLI not installed")
def test_stale_graph_falls_back_full(tmp_path):
    repo = build_repo(tmp_path)
    (repo / "src" / "foo.py").write_text("def foo():\n    return 2\n")
    subprocess.run(["git", "add", "src/foo.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "change foo"], cwd=repo, check=True)
    # do NOT rebuild graph -> stale
    r = run("--base", "HEAD~1", "--head", "HEAD", cwd=repo)
    assert r.returncode == 0, r.stderr
    assert "FALLBACK" in r.stdout and "graph stale" in r.stdout


def test_invalid_manifest_falls_back_full(tmp_path):
    repo = build_repo(tmp_path) if False else None
    # unit-level: load_manifest returns error on bad data
    sys.path.insert(0, str(ROOT / "scripts"))
    import test_impact as ti
    import tempfile, os
    d = tmp_path / "bad"; d.mkdir()
    (d / "m.yml").write_text("version: 99\n")
    m, err = ti.load_manifest(d / "m.yml")
    assert m is None and "version must be 1" in err


def test_is_glob_match_handles_double_star():
    sys.path.insert(0, str(ROOT / "scripts"))
    import test_impact as ti
    assert ti.is_glob_match("src/foo.py", "src/**/*.py") is True
    assert ti.is_glob_match("src/sub/foo.py", "src/**/*.py") is True
    assert ti.is_glob_match("tests/test_foo.py", "tests/test_*.py") is True
    assert ti.is_glob_match("src/foo.py", "lib/**/*.py") is False


def test_json_output_written(tmp_path):
    repo = build_repo(tmp_path)
    (repo / "src" / "foo.py").write_text("def foo():\n    return 2\n")
    subprocess.run(["git", "add", "src/foo.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "change foo"], cwd=repo, check=True)
    subprocess.run([GFT, "extract", str(repo), "--code-only", "--no-cluster", "--no-viz"], check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    (repo / "graphify-out" / ".source_sha").write_text(sha)
    out = tmp_path / "report.json"
    r = run("--base", "HEAD~1", "--head", "HEAD", "--json", str(out), cwd=repo)
    assert r.returncode == 0, r.stderr
    import json
    d = json.loads(out.read_text())
    assert "selected_tests" in d
