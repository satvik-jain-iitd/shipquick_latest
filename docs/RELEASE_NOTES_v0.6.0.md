# ShipQuick v0.6.0 "Auto mode" (26 Oct 2026)

D6 is a minor bump, so it ships as `v0.6.0` (`pm/agile/RELEASE_GUIDE.md`).

## New
- **Three modes.** Read `docs/MODES.md`.
  - Manual: the agents code, and the owner reviews and merges.
  - Semi: the agents review each other, and the owner merges.
  - Auto: the agents review, approve and merge. Only money, secrets and posts stop for the owner.
  - Only the owner sets the mode, with `! bash scripts/mode.sh set <word>` or the `/shipquick-mode` skill.
- **The merge gate.** `scripts/review_merge.sh <pr>` is the only way an agent merges.
  - It checks the mode, the approval on the latest commit, open threads, checks and `Closes #n`.
  - Right after the merge it closes the story issues, so the roadmap updates at once.
- **One-command setup.** `bash knowledge/shipquick_latest/scripts/adopt.sh .` sets a child project up.
- **Parallel lanes.** Up to 3 stories at once, in lanes that touch different files (rule 23).
- **A tested clone path.** The README tree and the Quick Start are checked on every PR.

## For child projects
1. Move the submodule to `v0.6.0`.
2. Run `bash knowledge/shipquick_latest/scripts/adopt.sh . --ref v0.6.0`, then commit what it changed.
3. Pick a mode: `/shipquick-mode semi` (or `manual`, `auto`).
