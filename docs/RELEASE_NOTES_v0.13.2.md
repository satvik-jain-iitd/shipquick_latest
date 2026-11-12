# ShipQuick v0.13.2 (12 Nov 2026)

A patch release (`pm/agile/RELEASE_GUIDE.md`). It fixes one gate job. No breaking change.

## What a child gains

- **The `environments` job reads `CLAUDE.md` from the kit branch when the caller sets `kit_branch`.** A project that follows rule 24 keeps `CLAUDE.md` on its kit branch; its `main` holds only run-critical code and has no `CLAUDE.md`, and another branch may carry an unfilled copy. The job used to read the file from the PR's own checkout and failed such a PR for it. Now it reads the kit branch file, the same way the `rule-copies` job does. A PR into the kit branch itself, and a project with no `kit_branch`, read their own checkout as before. A missing kit branch, or no `CLAUDE.md` on it, fails with a line that names the fix.

## What breaks for children on the bump

Nothing. A project that sets no `kit_branch` sees no change. A project that sets one now has its Dev link and Production link checked in the kit branch file, so they must be filled there past D0.

## Not yet

- The `rule-copies` job fetches the kit branch after a checkout with `persist-credentials: false`, which cannot work on a private repository (`docs/follow-ups.md`).

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.13.2`. Run `scripts/adopt.sh <path>` and then `scripts/adopt.sh <path> --check`, and paste the output in the bump PR. See `docs/ADOPTION.md`.
