#!/usr/bin/env python3
"""The component-request gate (story #186, rule 38). Stdlib only, calls `gh api`.

Every custom component in the registry (ui/registry.json, {"components": [{name, platform, base, request, twin}]})
must trace to a request issue that carries BOTH: the label `component-approved` added by a reviewer account, and an
issue comment by a reviewer account that starts with `Owner yes: <date> "<his words>"`. The issue body never counts,
since the coder writes it. Then a parity report names components that exist on one platform only (report, never a fail).
No registry file means no custom components, so it passes.
usage: check_component_request.py [--registry ui/registry.json] [--reviewers a,b] [--repo owner/name]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = "satvik-jain-iitd/shipquick_latest"
REVIEWERS = {"satvik-jain-iitd"}
YES = re.compile(r'^Owner yes: .+ ".+"')


def check_row(row, fetch, reviewers):
    """None when approved, else why not."""
    n = row.get("request")
    name = f"{row.get('name', '?')} ({row.get('platform', '?')})"
    if not isinstance(n, int):
        return f"{name}: no `request` issue number in the registry row"
    data = fetch(n)
    labeled = any(e.get("event") == "labeled" and e.get("label", {}).get("name") == "component-approved"
                  and e.get("actor", {}).get("login") in reviewers for e in data["events"])
    said = any(c.get("user", {}).get("login") in reviewers and YES.match(c.get("body") or "") for c in data["comments"])
    missing = []
    if not labeled:
        missing.append(f"label `component-approved` added by a reviewer ({', '.join(sorted(reviewers))})")
    if not said:
        missing.append('a reviewer comment `Owner yes: <date> "<words>"`')
    return f"{name}: request issue #{n} lacks " + " and ".join(missing) if missing else None


def parity(rows):
    """{name: [platforms]} for each component present on one platform only."""
    seen = {}
    for r in rows:
        seen.setdefault(r.get("name"), set()).add(r.get("platform"))
    return {k: sorted(v) for k, v in seen.items() if len(v) == 1}


def gh_fetch(repo):
    def get(path):
        out = subprocess.run(["gh", "api", "--paginate", "--slurp", path], capture_output=True, text=True)
        if out.returncode:
            raise SystemExit(f"cannot read {path}: {out.stderr.strip()}")
        return [item for page in json.loads(out.stdout) for item in page]
    return lambda n: {"events": get(f"repos/{repo}/issues/{n}/events"), "comments": get(f"repos/{repo}/issues/{n}/comments")}


def run(registry, reviewers, fetch):
    registry = Path(registry)
    rows = json.loads(registry.read_text(encoding="utf-8"))["components"] if registry.exists() else []
    bad = [w for w in (check_row(r, fetch, reviewers) for r in rows) if w]
    for w in bad:
        print(f"FAIL {w}")
    for name, plats in parity(rows).items():
        print(f"parity: {name} exists on {plats[0]} only, no twin yet")
    print(f"component-request: {len(rows)} custom, {len(bad)} unapproved")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=str(KIT / "ui" / "registry.json"))
    ap.add_argument("--reviewers", default=",".join(REVIEWERS))
    ap.add_argument("--repo", default=REPO)
    a = ap.parse_args()
    return run(a.registry, set(a.reviewers.split(",")), gh_fetch(a.repo))


if __name__ == "__main__":
    sys.exit(main())
