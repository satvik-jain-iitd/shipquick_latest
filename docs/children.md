# ShipQuick children registry (story #124)

One `owner/repo` per line, optionally followed by `private`. `# ` comments and blank lines are
ignored. Read by `scripts/adoption_scan.py` (a scheduled ShipQuick workflow) to open a `feedback`
issue for any child whose default branch has no `.github/workflows/shipquick-call.yml`, or pins a
ShipQuick commit more than 14 days old.

A `private` child is read with the `SHIPQUICK_CHILD_TOKEN` secret, not the workflow's own
`github.token` (which only ever sees this repo). See `docs/ADOPTION.md` for how to mint and set
that token. With no token configured, a private child prints one line and is skipped — never a
daily issue, since a 404 from a missing token looks identical to "not adopted".

Each child has one note above its line: `# <name>: <what GitHub shows, with the date>. Next: <step>`.
The steps are the checklist in docs/ADOPTION.md.

# GoServe: public, rule 24, kit branch `documents` pins edd3c26, no caller on main (9 Nov 2026). Next: bump `documents` to the release tag, run adopt.sh with --kit-branch documents, copy the caller to main.
satvik-jain-iitd/GoServe
# job-search: private, pins edd3c26 on main, has roadmap-call.yml but no shipquick-call.yml (9 Nov 2026). Next: bump main to the release tag, run adopt.sh.
klickbae8yt-star/job-search private
# bhavna-ai: public, pins e0bee8a, has no caller (9 Nov 2026). Next: bump to the release tag, run adopt.sh, then the printed ruleset command.
# This file is the one file the hygiene test lets hold that name (tests/test_repo_hygiene.py, owner, 9 Nov 2026).
satvik-jain-iitd/bhavna-ai
# Miraya: private and empty on GitHub; the local repo has a caller but was never pushed (9 Nov 2026). Next: push the local repo, then bump to the release tag.
satvik-jain-iitd/Miraya private
