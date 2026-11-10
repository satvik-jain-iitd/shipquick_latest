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

# GoServe: public, rule 24, kit branch `documents`. Bump PR GoServe#1298 (re-pinned 10 Nov 2026 to v0.11.1, f66e41a, milestone D1, roles.yml added); held by its own freeze. Its CLAUDE.md has no `- Dev link:` or `- Production link:` lines, so the environments job stays red until the owner gives the links (owner, 10 Nov 2026). Next: merge it, run the gate ruleset command and protect `documents`, then take `shipquick-call.yml` to `main` in a release and copy `CLAUDE.md` to `dev` and `staging`.
satvik-jain-iitd/GoServe
# job-search: private, base `main`. Bump PR job-search#294 merged 10 Nov 2026 (pin v0.11.1, f66e41a, milestone D0, roles.yml, its own `mode.md` kept, timeouts added to seven jobs; see feedback #359). The gate ruleset was refused with HTTP 403 "Upgrade to GitHub Pro or make this repository public to enable this feature": on a private Free repo the gate reports only and nothing is enforced, until Pro or public. Next: nothing until the plan changes.
klickbae8yt-star/job-search private
# bhavna-ai: public, base `dev`. Bump PR bhavna-ai#130 merged 10 Nov 2026 (pin v0.11.1, f66e41a, milestone D0, roles.yml, test job has a timeout). The ruleset "shipquick gate" was created and is active on `main` (10 Nov 2026), so the gate is enforced there. Next: promote `dev` to `main` so the caller runs from the default branch.
# This file is the one file the hygiene test lets hold that name (tests/test_repo_hygiene.py, owner, 9 Nov 2026).
satvik-jain-iitd/bhavna-ai
# Miraya: private. Pushed by the owner on 10 Nov 2026 as a clean orphan root without history: `operations/` (client data, 16 tracked files) and `.beads/` are not in it and are in `.gitignore`; Telegram chat and user ids in the n8n exports are redacted. Bump PR Miraya#1 merged 10 Nov 2026 (pin v0.11.1, f66e41a, milestone D0, roles.yml klickbae8yt-star / satvik-jain-iitd). The gate ruleset was refused with HTTP 403 "Upgrade to GitHub Pro or make this repository public to enable this feature": the gate reports only, nothing is enforced, until Pro or public. Next: promote `dev` to `main`.
satvik-jain-iitd/Miraya private
