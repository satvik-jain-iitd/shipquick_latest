"""Story #140: the PR author and every commit author must be a coder account -- the #114 case, a
PR opened by the reviewer account, caught in CI instead of relying on GitHub's own self-approval
refusal. Dependabot is exempt (it is neither role). A merge commit (2+ parents) may instead be
authored by a reviewer or owner account: a dev -> main release PR carries the local `git merge`
commits of whoever merged dev into their branch each day (rule 23), and those are never the PR's
own coder-authored work.

Story #139 (ADR-011): with `coder_sessions` set in roles.yml, every non-merge commit also carries a
`Built-by: <session>` trailer naming a coder session, and the approving review names its own
session (`Reviewed-by: <session>`, or the block header `from <session>`), which must be a reviewer
session that built none of the PR's commits. Self-declared: it stops the accident, not forgery.

Usage: python3 scripts/check_roles.py --author <login> --commit-authors <login:parents[:session],...> \
    --coders <x,y> [--reviewers <a,b>] [--owner <acct>] [--coder-sessions <s,t>]
       python3 scripts/check_roles.py --review-body-file <f> --built-by <s,t> --reviewer-sessions <q>
A commit with no `:parents` suffix is treated as a non-merge commit (parents=1).
Exit 0 and "roles OK", or exit 1 and the reason.
"""
import argparse
import re
import sys

DEPENDABOT = ("dependabot[bot]", "app/dependabot")


REVIEWED_BY = re.compile(r"^\s*Reviewed-by:\s*(\S+)", re.M)
BLOCK_FROM = re.compile(r"^To [^,\n]+, from ([a-z][a-z0-9-]*), re ", re.M)


def check(author: str, commits: list, coders: list, reviewers=(), owner=None, coder_sessions=()) -> str | None:
    """commits: an iterable of (login, parent_count[, session]) tuples."""
    if author in DEPENDABOT:
        return None
    if author not in coders:
        return f"PR author {author} is not a coder account ({', '.join(coders)})"
    merge_exempt = set(reviewers) | ({owner} if owner else set())
    for a, parents, *rest in commits:
        if a in DEPENDABOT:
            continue
        if coder_sessions and parents < 2 and (rest[0] if rest else "") not in coder_sessions:
            got = rest[0] if rest and rest[0] else "no Built-by: trailer"
            return (f"a commit by {a} names {got}, not a coder session ({', '.join(coder_sessions)}); "
                    "set the session once (source scripts/role.sh coder) and the hook adds Built-by:")
        if not a or a in coders:
            continue
        if parents >= 2 and a in merge_exempt:
            continue
        return f"commit author {a} is not a coder account ({', '.join(coders)})"
    return None


def review_session(body: str, built_by: list, reviewer_sessions: list) -> str | None:
    """The approving review's own session must be a reviewer session that built no commit here."""
    m = REVIEWED_BY.search(body or "") or BLOCK_FROM.search(body or "")
    if not m:
        return "the approving review names no session: add a 'Reviewed-by: <session>' line (ADR-011)"
    s = m.group(1).strip("`'\".,")
    if s not in reviewer_sessions:
        return f"the approving review is from {s}, not a reviewer session ({', '.join(reviewer_sessions)})"
    if s in built_by:
        return f"{s} built a commit on this PR and cannot approve it: hand the review to another session (ADR-011)"
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", default="")
    ap.add_argument("--commit-authors", default="")
    ap.add_argument("--coders", default="")
    ap.add_argument("--coder-sessions", default="")
    ap.add_argument("--review-body-file")
    ap.add_argument("--built-by", default="")
    ap.add_argument("--reviewer-sessions", default="")
    ap.add_argument("--reviewers", default="")
    ap.add_argument("--owner", default="")
    a = ap.parse_args(argv)
    split = lambda s: [x for x in s.split(",") if x]  # noqa: E731
    if a.review_body_file:
        with open(a.review_body_file, encoding="utf-8") as f:
            why = review_session(f.read(), split(a.built_by), split(a.reviewer_sessions))
        print(why or "roles OK")
        return 1 if why else 0
    if not a.author or not a.coders:
        ap.error("--author and --coders are required")
    commits = []
    for c in split(a.commit_authors):
        login, _, rest = c.partition(":")
        parents, _, session = rest.partition(":")
        commits.append((login, int(parents) if parents else 1, session))
    why = check(a.author, commits, split(a.coders), reviewers=split(a.reviewers), owner=a.owner or None,
                coder_sessions=split(a.coder_sessions))
    print(why or "roles OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
