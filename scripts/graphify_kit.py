"""ShipQuick wrapper around the Graphify CLI (ADR-022).

Usage:
  python3 scripts/graphify_kit.py build [path] [--force]      code-only extract, no LLM, no viz
  python3 scripts/graphify_kit.py update [path]               re-extract code files, update graph
  python3 scripts/graphify_kit.py check [path]                freshness check (delegates to check_graph_fresh.py)
  python3 scripts/graphify_kit.py affected [path] "X"          reverse-dependency impact
  python3 scripts/graphify_kit.py query [path] "question"      BFS traversal
  python3 scripts/graphify_kit.py path [path] "A" "B"          shortest path
  python3 scripts/graphify_kit.py explain [path] "X"           explain a node
  python3 scripts/graphify_kit.py hook-install [path]          install git hooks
  python3 scripts/graphify_kit.py hook-uninstall [path]        remove git hooks
  python3 scripts/graphify_kit.py hook-status [path]           check hook status
  python3 scripts/graphify_kit.py version                      print pinned vs installed version
All graphify calls set GRAPHIFY_NO_AUTO_REFRESH=1 to avoid skill auto-refresh noise in CI.
Exit codes mirror the underlying graphify command.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PINNED = (HERE / "graphify_version.txt").read_text().strip() if (HERE / "graphify_version.txt").exists() else "0.9.112"
ENV = {**os.environ, "GRAPHIFY_NO_AUTO_REFRESH": "1"}


def run_graphify(args: list[str]) -> int:
    try:
        proc = subprocess.run(["graphify", *args], env=ENV)
        return proc.returncode
    except FileNotFoundError:
        print("graphify CLI not found. Install with: pip install graphifyy=={}".format(PINNED), file=sys.stderr)
        return 127


def cmd_build(args):
    path = args.path or "."
    cmd = ["extract", path, "--code-only", "--no-cluster", "--no-viz"]
    if args.force:
        cmd.append("--force")
    return run_graphify(cmd)


def cmd_update(args):
    path = args.path or "."
    cmd = ["update", path]
    if args.force:
        cmd.append("--force")
    return run_graphify(cmd)


def cmd_check(args):
    fresh = HERE / "check_graph_fresh.py"
    graph_dir = Path(args.path or ".") / "graphify-out"
    if not graph_dir.is_absolute():
        graph_dir = (Path.cwd() / graph_dir).resolve()
    if not fresh.exists():
        print("check_graph_fresh.py not found; skipping freshness check")
        return 0
    return subprocess.run([sys.executable, str(fresh), "--graph", str(graph_dir), "--require"]).returncode


def cmd_affected(args):
    path = args.path or "."
    return run_graphify(["affected", args.target, "--graph", str(Path(path) / "graphify-out" / "graph.json")])


def cmd_query(args):
    path = args.path or "."
    return run_graphify(["query", args.question, "--graph", str(Path(path) / "graphify-out" / "graph.json")])


def cmd_path(args):
    path = args.path or "."
    return run_graphify(["path", args.a, args.b, "--graph", str(Path(path) / "graphify-out" / "graph.json")])


def cmd_explain(args):
    path = args.path or "."
    return run_graphify(["explain", args.target, "--graph", str(Path(path) / "graphify-out" / "graph.json")])


def cmd_hook_install(args):
    path = args.path or "."
    return run_graphify(["hook", "install"])


def cmd_hook_uninstall(args):
    return run_graphify(["hook", "uninstall"])


def cmd_hook_status(args):
    return run_graphify(["hook", "status"])


def cmd_version(args):
    try:
        out = subprocess.run(["graphify", "--version"], capture_output=True, text=True, env=ENV)
        installed = (out.stdout + out.stderr).strip()
    except FileNotFoundError:
        installed = "NOT INSTALLED"
    print(f"pinned:    {PINNED}")
    print(f"installed: {installed}")
    return 0 if installed.startswith(PINNED) or PINNED in installed else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="graphify_kit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("build")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("update")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("check")
    p.add_argument("path", nargs="?", default=".")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("affected")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("target")
    p.set_defaults(func=cmd_affected)

    p = sub.add_parser("query")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("question")
    p.set_defaults(func=cmd_query)

    p = sub.add_parser("path")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("a")
    p.add_argument("b")
    p.set_defaults(func=cmd_path)

    p = sub.add_parser("explain")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("target")
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("hook-install")
    p.add_argument("path", nargs="?", default=".")
    p.set_defaults(func=cmd_hook_install)

    p = sub.add_parser("hook-uninstall")
    p.add_argument("path", nargs="?", default=".")
    p.set_defaults(func=cmd_hook_uninstall)

    p = sub.add_parser("hook-status")
    p.add_argument("path", nargs="?", default=".")
    p.set_defaults(func=cmd_hook_status)

    p = sub.add_parser("version")
    p.set_defaults(func=cmd_version)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
