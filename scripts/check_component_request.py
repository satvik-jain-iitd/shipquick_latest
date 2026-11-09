#!/usr/bin/env python3
"""The component-request gate (story #186, rule 38). Stdlib only, calls `gh`.

Every custom component in ui/registry.json (relative to the repo root: {"components": [{name, platform, base,
request, twin}]}) must trace to a request issue that shows, live:
  - the label `component-approved`: its last label event is a `labeled` by a reviewer, and the label is still on the issue;
  - a reviewer's comment `Owner yes: <YYYY-MM-DD> "<3 or more words>"`, dated at most 14 days ago, never edited.
The issue body never counts (the coder writes it). Reviewers come from .shipquick/roles.yml (scripts/roles.py);
the repo from `gh repo view`. Parity (a component on one platform only) is a report, never a fail.
No registry file, or an empty one, means no custom components: it passes.
usage: check_component_request.py [--registry ui/registry.json] [--roles .shipquick/roles.yml]
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roles  # noqa: E402  (the one parser for .shipquick/roles.yml)

LABEL = "component-approved"
MAX_AGE_DAYS = 14
YES = re.compile(r'Owner yes: (\d{4}-\d{2}-\d{2}) "([^"<>]+)"')


def reviewers_from(path):
    return set(roles.load(path)["reviewer"])


def repo_name(runner=subprocess.run):
    out = runner(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
                 capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"cannot read this repo's name with gh: {out.stderr.strip()}")
    return out.stdout.strip()


def _valid_yes(body, today):
    m = YES.fullmatch((body or "").strip())
    if not m:
        return False
    try:
        day = datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return False
    age = (today - day).days
    return 0 <= age <= MAX_AGE_DAYS and len(m.group(2).split()) >= 3


def check_row(row, fetch, reviewers, today):
    """None when approved, else why not."""
    n = row.get("request")
    name = f"{row.get('name', '?')} ({row.get('platform', '?')})"
    if not isinstance(n, int):
        return f"{name}: no `request` issue number in the registry row"
    data = fetch(n)
    last = [e for e in data.get("events", []) if (e.get("label") or {}).get("name") == LABEL and e.get("event") in ("labeled", "unlabeled")]
    labeled = bool(last) and last[-1]["event"] == "labeled" \
        and ((last[-1].get("actor") or {}).get("login") in reviewers) \
        and any((l or {}).get("name") == LABEL for l in data.get("labels", []))
    said = any(((c.get("user") or {}).get("login") in reviewers) and _valid_yes(c.get("body"), today)
               and c.get("created_at") == c.get("updated_at") for c in data.get("comments", []))
    missing = []
    if not labeled:
        missing.append(f"label `{LABEL}` on the issue, last added by a reviewer ({', '.join(sorted(reviewers))})")
    if not said:
        missing.append('a reviewer comment `Owner yes: <YYYY-MM-DD> "<3+ words>"`, at most 14 days old, not edited')
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

    def fetch(n):
        issue = json.loads(subprocess.run(["gh", "api", f"repos/{repo}/issues/{n}"], capture_output=True, text=True).stdout or "{}")
        return {"labels": issue.get("labels", []), "events": get(f"repos/{repo}/issues/{n}/events"),
                "comments": get(f"repos/{repo}/issues/{n}/comments")}
    return fetch


def run(registry, reviewers, fetch, today=None):
    today = today or datetime.date.today()
    registry = Path(registry)
    rows = json.loads(registry.read_text(encoding="utf-8")).get("components", []) if registry.exists() else []
    bad = [w for w in (check_row(r, fetch, reviewers, today) for r in rows) if w]
    for w in bad:
        print(f"FAIL {w}")
    for name, plats in parity(rows).items():
        print(f"parity: {name} exists on {plats[0]} only, no twin yet")
    print(f"component-request: {len(rows)} custom, {len(bad)} unapproved")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="ui/registry.json")
    ap.add_argument("--roles", default=".shipquick/roles.yml")
    ap.add_argument("--repo", default="")
    a = ap.parse_args()
    if not Path(a.registry).exists() or not json.loads(Path(a.registry).read_text(encoding="utf-8")).get("components"):
        return run(a.registry, set(), None)   # nothing to check: no roles or repo needed
    try:
        reviewers = reviewers_from(a.roles)
    except (FileNotFoundError, ValueError) as e:
        print(f"component-request: {e}", file=sys.stderr)
        return 1
    return run(a.registry, reviewers, gh_fetch(a.repo or repo_name()))


if __name__ == "__main__":
    sys.exit(main())
