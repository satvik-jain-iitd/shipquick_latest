# ShipQuick v0.13.1 (12 Nov 2026)

A patch release (`pm/agile/RELEASE_GUIDE.md`). It fixes what the first real bumps to v0.13.0 showed. No breaking change.

## What a child gains

- **A kit bump passes the pre-push hook without `SKIP`.** A PR that changes only the ShipQuick pin and the files `adopt.sh` writes is a kit bump, and the tdd check no longer asks for a failing test. The exact list of those files is `scripts/adopt_files.txt`; it is a protected path. The secrets scan in the hook now reads only the commits you are pushing, not the whole history.
- **`adopt.sh --check` reads the caller's milestone.** The environments test runs at the milestone in the caller (`shipquick-call.yml`) and at D1 when there is none, the same as CI. A bad `milestone:` line is refused with exit 2.
- **`--check` fails when the child has no `CLAUDE.md`**, because CI reads the Dev link and the Production link from it. A child that keeps its `CLAUDE.md` on another branch (the rule-24 flow) is not failed for it.
- **The gate message is clearer.** It says the gate gap is one test only, and every other failure prints its own "not adopted:" line.
- **Desk follow-ups.** The Desk deletes its local branch on every path, names the GitHub account in the PR body, and refuses an account that `.shipquick/roles.yml` marks as review-only.

## What breaks for children on the bump

Nothing. A child whose `--check` passed on v0.13.0 can fail now only for a real reason: an environments test at its milestone, or a missing `CLAUDE.md`.

## Not yet

- The rule-24 read in `--check` looks only at the files in the checkout; it does not read the other branches (`docs/follow-ups.md`).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.13.1`. Run `scripts/adopt.sh <path>` and then `scripts/adopt.sh <path> --check`, and paste the output in the bump PR. See `docs/ADOPTION.md`.
