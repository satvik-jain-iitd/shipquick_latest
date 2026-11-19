"""Story #580: a dry-run planner. Which child repo pins a kit commit other than a release commit?

Usage: python3 scripts/child_bump.py --release-sha <40 hex> [--children docs/children.md]
Prints one line per child (`bump`, `current` or `unread`), then `summary: <n> bump, <n> current, <n> unread`.
Exit 1: the registry is missing or empty, or any child is unread. Exit 2: the release sha is not 40 hex letters.

Known limit: `bump` means "the pin is not the release commit". It does not check whether the pin is older or newer.
Dry run only: it writes nothing and reads GitHub with the login the scan already uses. A child marked `private` is
read with the token in SHIPQUICK_CHILD_TOKEN (passed to `fetch(path, token=...)`), as the daily scan does. The registry and the pin are read
with `read_children` and `read_pin` of scripts/adoption_scan.py.
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adoption_scan  # noqa: E402


def plan(rows, release_sha):
    """rows: (child, pin, why). Returns (child, "bump" | "current" | "unread", detail) per child. No network."""
    out = []
    for child, pin, why in rows:
        if not pin:
            out.append((child, "unread", why))
        elif pin == release_sha:
            out.append((child, "current", pin))
        else:
            out.append((child, "bump", f"{pin} -> {release_sha}"))
    return out


def run(children_path, release_sha, fetch, token=None) -> int:
    try:
        children = adoption_scan.read_children(children_path)
    except OSError as e:
        print(f"cannot read the registry {children_path}: {e}", file=sys.stderr)
        return 1
    if not children:
        print(f"no child in {children_path}: nothing to plan", file=sys.stderr)
        return 1
    rows = [
        (c, *adoption_scan.read_pin(c, (lambda p: fetch(p, token=token)) if private else fetch))
        for c, private in children
    ]
    result = plan(rows, release_sha)
    for child, word, detail in result:
        print(f"{word}: {child}: {detail}")
    n = {w: sum(1 for r in result if r[1] == w) for w in ("bump", "current", "unread")}
    print(f"summary: {n['bump']} bump, {n['current']} current, {n['unread']} unread")
    return 1 if n["unread"] else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="child_bump")
    ap.add_argument("--release-sha", required=True)
    ap.add_argument("--children", default=str(adoption_scan.ROOT / "docs" / "children.md"))
    args = ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.release_sha):
        print("--release-sha must be 40 hex letters", file=sys.stderr)
        return 2
    return run(args.children, args.release_sha, adoption_scan.gh_api, os.environ.get(adoption_scan.CHILD_TOKEN_ENV))


if __name__ == "__main__":
    sys.exit(main())
