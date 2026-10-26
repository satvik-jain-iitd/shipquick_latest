# ShipQuick v0.5.0 "Process v2" (26 Oct 2026)

This is the first tagged release. It brings back what GoServe and job-search learned.
D5 is a minor bump, so it ships as `v0.5.0` (`pm/agile/RELEASE_GUIDE.md`). It also carries the D4 work, which was never tagged.

## New
- CI must-haves (#43). Read `docs/research/ci-checks.md`.
  - A secret scan runs on every PR. It reads the PR's own commits. A push reads the whole history.
  - The workflow token is read-only.
  - Actions are pinned to a full SHA. Dependabot keeps them fresh.
  - A dependency review runs on every PR. It needs the repo's Dependency graph to be on.
  - Every hygiene check also runs on the Mac before a push (`scripts/check_local.sh`).
  - The merge-marker check only looks at the start of a line.
- A live roadmap on GitHub Actions (#49). Read `docs/LIVE_ROADMAP.md`. Each project gets `ROADMAP.md` on a `roadmap` branch.
  It needs no n8n, no server and no secret.
- New rules 20 to 30 in `CLAUDE.md`. They cover:
  - radar first, the live roadmap, two GitHub accounts and one open stack;
  - run code on `main`, the phase gate and notes that never stay in a head;
  - the two-session pair, the runtime rule, useful checks only and the review loop.
- `docs/TEAM_ROSTER.md` shows the two-session pattern. One session codes. One session reviews. Each has its own folder.
- A block to the owner says when to act (PR #40).

## For child projects
1. Move the submodule to `v0.5.0`.
2. Add `roadmap.json` and the caller workflow (`docs/LIVE_ROADMAP.md`, "A child project joins in three steps").
3. Read rules 20 to 30.
