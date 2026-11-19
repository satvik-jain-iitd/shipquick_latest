"""ShipQuick Graphify wrapper (ADR-022, M1b)."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "graphify_kit.py"
VENV_GRAPHIFY = "/tmp/gftest/bin/graphify"


def run(*args, cwd=None, env=None):
    e = dict(__import__("os").environ)
    e["GRAPHIFY_NO_AUTO_REFRESH"] = "1"
    if env:
        e.update(env)
    return subprocess.run(["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd, env=e)


@pytest.mark.skipif(not Path(VENV_GRAPHIFY).exists(), reason="graphify CLI not installed")
def test_build_creates_graph_json(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "a.py").write_text("def foo():\n    return 1\n")
    r = run("build", str(repo))
    assert r.returncode == 0, r.stderr
    assert (repo / "graphify-out" / "graph.json").exists()


@pytest.mark.skipif(not Path(VENV_GRAPHIFY).exists(), reason="graphify CLI not installed")
def test_affected_finds_dependents(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "a.py").write_text("def foo():\n    return 1\n")
    (repo / "b.py").write_text("from a import foo\ndef bar():\n    return foo()\n")
    r = run("build", str(repo))
    assert r.returncode == 0
    r2 = run("affected", str(repo), "a.py")
    assert r2.returncode == 0
    assert "b.py" in r2.stdout


def test_version_prints_pinned():
    r = run("version")
    assert "pinned:" in r.stdout
    assert "0.9.112" in r.stdout


def test_unknown_subcommand_fails():
    r = run("nope")
    assert r.returncode != 0


def test_check_skips_when_fresh_script_missing(tmp_path, monkeypatch):
    # graphify_kit.check should not crash if check_graph_fresh.py is absent
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "graphify-out").mkdir()
    (repo / "graphify-out" / "graph.json").write_text('{"nodes":[],"edges":[]}')
    r = run("check", str(repo))
    # either skips or runs; must not traceback
    assert "Traceback" not in (r.stdout + r.stderr)
