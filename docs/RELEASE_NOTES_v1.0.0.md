# ShipQuick v1.0.0 "Process v2" (draft, 26 Oct 2026)

This is the first tagged release. It brings back what GoServe and job-search learned.

## New
- CI must-haves. Read `docs/research/ci-checks.md`.
  - A secret scan runs on every PR.
  - The workflow token is read-only.
  - Actions are pinned to a full SHA. Dependabot keeps them fresh.
  - A dependency review runs on every PR.
  - Every hygiene check also runs on the Mac before a push.
  - The merge-marker check only looks at the start of a line.
- A live roadmap on n8n. Read `docs/LIVE_ROADMAP.md`. Each project gets one link. It is fresh every 15 minutes.
- New rules 20 to 30 in `CLAUDE.md`. They cover radar first, the live roadmap, two GitHub accounts, one open stack,
  run code on `main`, the phase gate, notes that never stay in a head, the two-session pair, the runtime rule, and
  useful checks only, and the review loop.
- `docs/TEAM_ROSTER.md` shows the two-session pattern. One session codes. One session reviews. Each has its own folder.
- A block to the owner says when to act (PR #40).

## For child projects
1. Move the submodule to `v1.0.0`.
2. Add your repo to the roadmap Config.
3. Read rules 20 to 30.
