"""Graphify freshness (ADR-022): a stub `graphify` on PATH builds a graph; the kit records the commit; the check reads it."""
import os
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "scripts" / "graphify_kit.py"
CHECK = ROOT / "scripts" / "check_graph_fresh.py"
PIN = (ROOT / "scripts" / "graphify_version.txt").read_text().strip()

STUB = """#!/bin/sh
# stub graphify: --version prints $STUB_VERSION; extract/update <path> write <path>/graphify-out/graph.json
case "$1" in
  --version) echo "graphify ${STUB_VERSION:-%s}" ;;
  extract|update) mkdir -p "$2/graphify-out" && echo '{"nodes":[{}],"edges":[]}' > "$2/graphify-out/graph.json" ;;
esac
""" % PIN


def env_with_stub(tmp_path, version=None):
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    g = bindir / "graphify"
    g.write_text(STUB)
    g.chmod(g.stat().st_mode | stat.S_IEXEC)
    e = {**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"}
    if version:
        e["STUB_VERSION"] = version
    return e


def sh(args, cwd, env):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)


def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    for c in (["init", "-q"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "one"]):
        subprocess.run(["git", *c], cwd=r, check=True, capture_output=True)
    return r


def head(r):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=r, capture_output=True, text=True).stdout.strip()


def test_build_writes_source_sha_and_check_is_fresh(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    assert sh(["python3", KIT, "build", str(r)], r, e).returncode == 0
    assert (r / "graphify-out" / ".source_sha").read_text().strip() == head(r)
    assert not (r / "graphify-out" / ".schema_version").exists()
    c = sh(["python3", CHECK, "--require"], r, e)
    assert c.returncode == 0, c.stdout + c.stderr
    assert "graph fresh" in c.stdout


def test_update_rewrites_source_sha(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    sh(["python3", KIT, "build", str(r)], r, e)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "two"], cwd=r, check=True)
    assert sh(["python3", CHECK, "--require"], r, e).returncode == 1  # stale after a new commit
    assert sh(["python3", KIT, "update", str(r)], r, e).returncode == 0
    assert (r / "graphify-out" / ".source_sha").read_text().strip() == head(r)
    assert sh(["python3", CHECK, "--require"], r, e).returncode == 0


def test_a_new_commit_makes_the_graph_stale(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    sh(["python3", KIT, "build", str(r)], r, e)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "two"], cwd=r, check=True)
    c = sh(["python3", CHECK, "--require"], r, e)
    assert c.returncode == 1
    assert "graph stale" in c.stdout


def test_no_source_sha_is_not_fresh_under_require(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    sh(["graphify", "extract", str(r)], r, e)  # a graph built by graphify itself, no sha file
    c = sh(["python3", CHECK, "--require"], r, e)
    assert c.returncode == 1
    assert ".source_sha" in c.stdout


def test_a_version_mismatch_only_warns(tmp_path):
    e, r = env_with_stub(tmp_path, version="0.0.1"), repo(tmp_path)
    sh(["python3", KIT, "build", str(r)], r, e)
    c = sh(["python3", CHECK, "--require"], r, e)
    assert c.returncode == 0, c.stdout + c.stderr
    assert "warn" in c.stdout and "0.0.1" in c.stdout


def test_a_missing_graph_without_require_passes_and_with_require_fails(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    assert sh(["python3", CHECK], r, e).returncode == 0
    assert sh(["python3", CHECK, "--require"], r, e).returncode == 1


def test_an_empty_graph_fails(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    (r / "graphify-out").mkdir()
    (r / "graphify-out" / "graph.json").write_text("{}")
    assert sh(["python3", CHECK, "--require"], r, e).returncode == 1


def local(r, e):
    return sh(["bash", str(ROOT / "scripts" / "check_local.sh"), "graph-fresh"], r, e)


def test_local_check_only_warns_on_a_stale_graph(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    sh(["python3", KIT, "build", str(r)], r, e)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "two"], cwd=r, check=True)
    c = local(r, e)
    assert c.returncode == 0, c.stdout + c.stderr
    assert "warn graph-fresh" in c.stdout and "stale" in c.stdout


def test_local_check_only_warns_without_source_sha(tmp_path):
    e, r = env_with_stub(tmp_path), repo(tmp_path)
    sh(["graphify", "update", str(r)], r, e)  # plain graphify, no .source_sha
    c = local(r, e)
    assert c.returncode == 0, c.stdout + c.stderr
    assert "warn graph-fresh" in c.stdout and ".source_sha" in c.stdout
