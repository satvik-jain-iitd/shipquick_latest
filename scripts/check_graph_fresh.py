"""Graphify freshness check (ADR-022): verify that graphify-out/graph.json is fresh and usable.

Checks:
  - graphify-out/graph.json exists and parses as JSON with nodes/edges.
  - the graph's source SHA (graphify-out/.source_sha, written by graphify_kit.py build/update) matches HEAD.
  - the pinned CLI version (scripts/graphify_version.txt) vs the installed `graphify`: a mismatch only warns.

Usage:
  python3 scripts/check_graph_fresh.py [--graph DIR] [--require] [--json]
  --require: fail (exit 1) if the graph is missing or stale (default: warn only).
Exit 0 on fresh/missing-without-require, 1 on stale/missing-with-require.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED = (HERE / "graphify_version.txt").read_text().strip()


def installed_version() -> str | None:
    try:
        out = subprocess.run(["graphify", "--version"], capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    txt = (out.stdout + out.stderr).strip()
    # graphify prints "graphify X.Y.Z" or just the version
    for tok in txt.split():
        if tok[0].isdigit() and "." in tok:
            return tok.strip("v")
    return txt or None


def head_sha(repo: Path) -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def check(graph_dir: Path, require: bool) -> tuple[bool, list[str]]:
    messages = []
    ok = True
    graph_path = graph_dir / "graph.json"
    if not graph_path.exists():
        messages.append(f"graph missing: {graph_path}")
        if require:
            ok = False
        return ok, messages

    try:
        data = json.loads(graph_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        messages.append(f"graph unreadable: {e}")
        return False, messages
    if not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
        messages.append("graph has no nodes/edges")
        return False, messages
    messages.append(f"graph OK: {len(data['nodes'])} nodes, {len(data['edges'])} edges")

    stored_sha = (graph_dir / ".source_sha").read_text().strip() if (graph_dir / ".source_sha").exists() else None
    cur_sha = head_sha(graph_dir.parent)
    if not stored_sha:
        messages.append("no .source_sha: freshness unverified (run python3 scripts/graphify_kit.py build)")
        ok = ok and not require
    elif cur_sha and stored_sha != cur_sha:
        messages.append(f"graph stale: stored={stored_sha[:8]}, HEAD={cur_sha[:8]}")
        ok = ok and not require

    iv = installed_version()
    if iv is None:
        messages.append("warn: graphify CLI not installed (pip install graphifyy)")
    elif iv != PINNED:
        messages.append(f"warn: graphify version mismatch: installed={iv}, pinned={PINNED}")

    return ok, messages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="graphify-out", help="graph output directory")
    ap.add_argument("--require", action="store_true", help="fail if missing or stale")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    graph_dir = Path(args.graph)
    if not graph_dir.is_absolute():
        graph_dir = (Path.cwd() / graph_dir).resolve()
    ok, messages = check(graph_dir, args.require)
    if args.json:
        print(json.dumps({"ok": ok, "messages": messages}))
    else:
        for m in messages:
            print(m)
        print("graph fresh" if ok else "graph NOT fresh")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
