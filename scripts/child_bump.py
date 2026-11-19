"""Child bump planner (M6): reads docs/children.md and prints what a release would do.

Dry-run by default. Does NOT create PRs or push. --apply is reserved for when a write-capable
credential (GitHub App) is provisioned; without it, --apply prints instructions and exits.

Usage:
  python3 scripts/child_bump.py --release-tag v0.15.0 [--dry-run] [--json]
  python3 scripts/child_bump.py --release-tag v0.15.0 --apply   (requires SHIPQUICK_CHILD_WRITE_TOKEN)
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd() if (Path.cwd() / 'docs' / 'children.md').exists() else HERE.parent
REGISTRY = ROOT / "docs" / "children.md"


def run_gh(args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def parse_registry(text):
    """Return list of (repo, private) from docs/children.md."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 1 or "/" not in parts[0]:
            continue
        if len(parts) > 2:
            continue
        if len(parts) == 2 and parts[1] != "private":
            continue
        repo = parts[0]
        private = "private" in parts[1:]
        out.append((repo, private))
    return out


def child_info(repo, private):
    """Query gh API for visibility/default branch/latest commit. Returns dict or error."""
    token = os.environ.get("SHIPQUICK_CHILD_TOKEN") if private else None
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    # repo metadata
    rc, out, err = run_gh(["api", f"repos/{repo}", "--jq", "{visibility:.visibility, default_branch:.default_branch}"])
    if rc != 0:
        return {"repo": repo, "private": private, "error": f"cannot read repo: {err or out}"}
    try:
        meta = json.loads(out)
    except Exception:
        meta = {"visibility": "unknown", "default_branch": "main"}
    branch = meta.get("default_branch", "main")
    # latest commit sha on default branch
    rc2, out2, err2 = run_gh(["api", f"repos/{repo}/commits/{branch}", "--jq", ".sha"])
    sha = out2 if rc2 == 0 else None
    return {
        "repo": repo,
        "private": private,
        "visibility": meta.get("visibility"),
        "default_branch": branch,
        "head_sha": sha,
        "error": (err2 if rc2 != 0 else None),
    }


def plan_for(info, release_tag):
    branch = info.get("default_branch", "main")
    bump_branch = f"shipquick-bump-{release_tag}"
    return {
        "repo": info["repo"],
        "private": info["private"],
        "default_branch": branch,
        "bump_branch": bump_branch,
        "target_release": release_tag,
        "actions": [
            f"git fetch origin {branch}",
            f"git checkout -b {bump_branch} origin/{branch}",
            f"git submodule set-url ... {release_tag}  (update shipquick pin to {release_tag})",
            "run adopt.sh with --ref " + release_tag + " (kit_branch preserved)",
            f"git commit -m 'chore: bump shipquick to {release_tag}'",
            f"open PR: {bump_branch} -> {branch} (title: 'chore: bump shipquick to {release_tag}')",
        ],
        "pr_title": f"chore: bump shipquick to {release_tag}",
        "head_sha": info.get("head_sha"),
        "error": info.get("error"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-tag", required=True, help="e.g. v0.15.0")
    ap.add_argument("--apply", action="store_true", help="create PRs (requires write credential)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    if not REGISTRY.exists():
        print(f"registry not found: {REGISTRY}")
        return 1
    repos = parse_registry(REGISTRY.read_text())
    infos = [child_info(r, p) for r, p in repos]
    plans = [plan_for(i, args.release_tag) for i in infos]

    if args.apply:
        # Requires SHIPQUICK_CHILD_WRITE_TOKEN (GitHub App installation token) with
        # contents:write + pull-requests:write on the registered children.
        token = os.environ.get("SHIPQUICK_CHILD_WRITE_TOKEN")
        if not token:
            print("SHIPQUICK_CHILD_WRITE_TOKEN not set; cannot apply. Provision a GitHub App first (see docs).")
            return 1
        print("--apply is not implemented yet: requires the write credential + end-to-end tests (M6b).")
        return 1

    if args.json:
        print(json.dumps({"release_tag": args.release_tag, "plans": plans}, indent=2))
    else:
        print(f"Release: {args.release_tag}")
        print(f"Children: {len(plans)}")
        for p in plans:
            print()
            print(f"== {p['repo']} ({'private' if p['private'] else 'public'}) ==")
            if p["error"]:
                print(f"  ERROR: {p['error']}")
                continue
            print(f"  default branch: {p['default_branch']}")
            print(f"  head sha:       {p['head_sha']}")
            print(f"  bump branch:    {p['bump_branch']}")
            print(f"  PR title:       {p['pr_title']}")
            for a in p["actions"]:
                print(f"    - {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
