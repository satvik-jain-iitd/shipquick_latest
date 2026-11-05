"""Story #131: a child's pinned ShipQuick commit must be reachable from `dev` or `main`, or be a
release tag -- not just any commit that exists in ShipQuick's history, which would let a PR pin a
throwaway branch commit that never merged (and so never passed ShipQuick's own review).

Usage: python3 scripts/check_adoption_ancestor.py --repo <owner/repo> --sha <sha>
Needs network (the GitHub REST API, unauthenticated reads of a public repo; set GH_TOKEN to raise
the rate limit). Exit 0 and "adoption ancestor OK", or exit 1 and the reason.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def decide(sha: str, compare_dev: str | None, compare_main: str | None, tags: list) -> str | None:
    """compare_dev/compare_main: the GitHub compare API's "status" for base...sha (None when that
    compare call itself failed, e.g. the branch does not exist). tags: commit SHAs of every repo
    tag. Returns None when sha is merged into dev/main or tagged; otherwise the refusal reason."""
    if compare_dev in ("identical", "behind") or compare_main in ("identical", "behind") or sha in tags:
        return None
    return (f"pinned ShipQuick commit {sha[:7]} is not on dev or main, and is not a release tag "
            "(an unmerged commit never passed ShipQuick's own review) -- run: "
            "bash knowledge/shipquick_latest/scripts/adopt.sh .")


def _get_json(url: str, token: str | None):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"} if token else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError:
        return None
    except urllib.error.URLError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--sha", required=True)
    a = ap.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    def compare(base):
        data = _get_json(f"https://api.github.com/repos/{a.repo}/compare/{base}...{a.sha}", token)
        return data.get("status") if data else None

    tags_data = _get_json(f"https://api.github.com/repos/{a.repo}/tags?per_page=100", token) or []
    tags = [t["commit"]["sha"] for t in tags_data if "commit" in t]

    why = decide(a.sha, compare("dev"), compare("main"), tags)
    print(why or "adoption ancestor OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
