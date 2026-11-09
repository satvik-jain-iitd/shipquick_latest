# ShipQuick children registry (story #124)

One `owner/repo` per line, optionally followed by `private`. `# ` comments and blank lines are
ignored. Read by `scripts/adoption_scan.py` (a scheduled ShipQuick workflow) to open a `feedback`
issue for any child whose default branch has no `.github/workflows/shipquick-call.yml`, or pins a
ShipQuick commit more than 14 days old.

A `private` child is read with the `SHIPQUICK_CHILD_TOKEN` secret, not the workflow's own
`github.token` (which only ever sees this repo). See `docs/ADOPTION.md` for how to mint and set
that token. With no token configured, a private child prints one line and is skipped — never a
daily issue, since a 404 from a missing token looks identical to "not adopted".

satvik-jain-iitd/GoServe
klickbae8yt-star/job-search private
# One more child (public, under satvik-jain-iitd) is not listed: its name is on this repo's forbidden-names
# list (tests/test_repo_hygiene.py). The owner decides how to list it (story #260).
# Miraya is private and empty on GitHub (9 Nov 2026): nothing was pushed yet. With no token the scan names it as skipped; with one it reports "no caller" until the repo is pushed and adopted.
satvik-jain-iitd/Miraya private
