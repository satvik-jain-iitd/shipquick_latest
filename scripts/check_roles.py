"""Story #140: the PR author and every commit author must be a coder account -- the #114 case, a
PR opened by the reviewer account, caught in CI instead of relying on GitHub's own self-approval
refusal. Dependabot is exempt (it is neither role). A merge commit (2+ parents) may instead be
authored by a reviewer or owner account: a dev -> main release PR carries the local `git merge`
commits of whoever merged dev into their branch each day (rule 23), and those are never the PR's
own coder-authored work.

Usage: python3 scripts/check_roles.py --author <login> --commit-authors <login:parents,...> \
    --coders <x,y> [--reviewers <a,b>] [--owner <acct>]
A commit with no `:parents` suffix is treated as a non-merge commit (parents=1).
Exit 0 and "roles OK", or exit 1 and the reason.
"""
import argparse
import sys

DEPENDABOT = ("dependabot[bot]", "app/dependabot")


def check(author: str, commits: list, coders: list, reviewers=(), owner=None) -> str | None:
    """commits: an iterable of (login, parent_count) pairs."""
    if author in DEPENDABOT:
        return None
    if author not in coders:
        return f"PR author {author} is not a coder account ({', '.join(coders)})"
    merge_exempt = set(reviewers) | ({owner} if owner else set())
    for a, parents in commits:
        if not a or a in coders or a in DEPENDABOT:
            continue
        if parents >= 2 and a in merge_exempt:
            continue
        return f"commit author {a} is not a coder account ({', '.join(coders)})"
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", required=True)
    ap.add_argument("--commit-authors", default="")
    ap.add_argument("--coders", required=True)
    ap.add_argument("--reviewers", default="")
    ap.add_argument("--owner", default="")
    a = ap.parse_args(argv)
    commits = []
    for c in a.commit_authors.split(","):
        if not c:
            continue
        login, _, parents = c.partition(":")
        commits.append((login, int(parents) if parents else 1))
    coders = [c for c in a.coders.split(",") if c]
    reviewers = [r for r in a.reviewers.split(",") if r]
    why = check(a.author, commits, coders, reviewers=reviewers, owner=a.owner or None)
    print(why or "roles OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
