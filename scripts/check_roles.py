"""Story #140: the PR author and every commit author must be a coder account -- the #114 case, a
PR opened by the reviewer account, caught in CI instead of relying on GitHub's own self-approval
refusal. Dependabot is exempt (it is neither role).

Usage: python3 scripts/check_roles.py --author <login> --commit-authors <a,b,c> --coders <x,y>
Exit 0 and "roles OK", or exit 1 and the reason.
"""
import argparse
import sys

DEPENDABOT = ("dependabot[bot]", "app/dependabot")


def check(author: str, commit_authors: list, coders: list) -> str | None:
    if author in DEPENDABOT:
        return None
    if author not in coders:
        return f"PR author {author} is not a coder account ({', '.join(coders)})"
    for a in commit_authors:
        if a and a not in coders and a not in DEPENDABOT:
            return f"commit author {a} is not a coder account ({', '.join(coders)})"
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", required=True)
    ap.add_argument("--commit-authors", default="")
    ap.add_argument("--coders", required=True)
    a = ap.parse_args(argv)
    commit_authors = [c for c in a.commit_authors.split(",") if c]
    coders = [c for c in a.coders.split(",") if c]
    why = check(a.author, commit_authors, coders)
    print(why or "roles OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
