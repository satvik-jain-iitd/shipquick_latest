#!/usr/bin/env python3
"""Story #497: open one issue, or comment on the open one that already says the same thing.

One helper for every scheduled script that reports a problem: scripts/adoption_scan.py (a child that never adopted the
kit) and scripts/nightly_full_run.py (a red night on dev). An open issue with the label whose title holds the key gets a
comment; no such issue gets a new one. Needs: gh, authenticated as the build account (GH_TOKEN).
"""
import json
import os
import subprocess


def gh_api(path, token=None):
    """GET one API path through gh. None when the call fails or the answer is not JSON."""
    env = dict(os.environ)
    if token:
        env["GH_TOKEN"] = token
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def open_or_comment(repo, label, title, body, key, dry_run, api=gh_api, run=subprocess.run, note=None):
    """Return "dry-run", "commented #<n>" or "opened". `key` is looked up in the titles of the open issues with `label`."""
    existing = api(f"repos/{repo}/issues?labels={label}&state=open") or []
    match = next((i for i in existing if key.lower() in i.get("title", "").lower()), None)
    if dry_run:
        print(f"[dry-run] would {'comment on #' + str(match['number']) if match else 'open'}: {note or title}")
        return "dry-run"
    if match:
        run(["gh", "issue", "comment", str(match["number"]), "-R", repo, "--body", body], check=False)
        return f"commented #{match['number']}"
    run(["gh", "issue", "create", "-R", repo, "--label", label, "--title", title, "--body", body], check=False)
    return "opened"
