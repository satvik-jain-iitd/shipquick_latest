# ShipQuick v0.13.0 (11 Nov 2026)

D8 ships as a minor release (`pm/agile/RELEASE_GUIDE.md`). Every ShipQuick feature can be switched on or off by the owner, the Desk shows them and can propose a change, and a child's bump is checked before it is pushed.

## New

- **Feature switches (epic #86).** One file, `.shipquick/features.json`, holds an on or off per feature. One reader, `scripts/features.py`; the owner's setter, `scripts/features.sh set <id> on|off`, which only prepares the change: the file is a protected path, so the owner merges the PR. `adoption` and `gate` are locked on. Off means the owner does more by hand, never that a check is silently skipped, and an error is never read as "on". CI reads the flags from the base branch. See `docs/FEATURES.md` and rule 39.
- **The Desk with working switches (epic #91).** The page follows the approved frame D: every feature in groups with plain words, an error card when the file is broken, cards for what waits on the owner, and the roadmap link. A switch asks for a confirm inside its row, then opens a PR through one guarded route (same origin and a per-start token, 127.0.0.1 only). The row says "Turning off, merge PR N" until the PR lands.
- **A preflight for a child's bump (#446).** `adopt.sh` installs the git hooks when they are configured and missing. `adopt.sh --check` fails on uninstalled hooks, on a commit subject over 72 characters since the base, and on empty Dev or Production links at the caller's milestone, with the words CI uses. The session-start hook warns in any project whose hooks are configured but not installed.
- **A `commit-subjects` gate job (#446).** `checks.yml` fails a PR with a commit subject over 72 characters. It has its own feature flag. Dependabot and git's exact `Revert "<subject>"` form are exempt.
- **Bench results (#312).** The full run of the kit rules against no kit and the vibe baseline are in `docs/research/experiments.md`. In short: the kit block does not save tokens (output tokens 1.37 on haiku and 1.25 on sonnet, kit over no-kit), and it makes agents draw far fewer hand-made screens (27 of 30 clean against 12 of 30 on haiku).

## What breaks for children on the bump

- **The new `commit-subjects` job** fails a PR with a commit subject over 72 characters. Reword before you push, or switch the feature off through a PR the owner merges (`scripts/features.sh set commit-subjects off`).
- **`adopt.sh` writes `.shipquick/features.json`** and installs the git hooks (it needs `pre-commit` on the machine; without it, it prints the install line). Commit the new file in the bump PR.
- **`adopt.sh --check` is stricter.** It fails on uninstalled hooks, on long commit subjects since the base, and on an empty or placeholder Dev link or Production link past milestone D0. Run it before you push a bump branch.
- **The kit's merge and close scripts read two flags at the base ref** (`merge-gate`, `close-on-merge`). A broken `.shipquick/features.json` on a base branch now refuses an agent merge instead of being ignored.

## Not yet

- The two Desk follow-ups: delete the local branch on the unchanged and error paths, and name the GitHub account a Desk PR is opened with (`docs/follow-ups.md`).
- A live run of the new `commit-subjects` job and of `adopt.sh` with the real `pre-commit` on a child. The tests use a stand-in.

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.13.0`. Run `scripts/adopt.sh <path>` and then `scripts/adopt.sh <path> --check`. See `docs/ADOPTION.md`.
