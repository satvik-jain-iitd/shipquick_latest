# ShipQuick v0.11.1 (10 Nov 2026)

A patch release, so it ships as `v0.11.1` (`pm/agile/RELEASE_GUIDE.md`).
A child can now tell the `environments` check which milestone it is at.

## New

- **A milestone input for the `environments` job (#357, PR #358).** `checks.yml` takes `milestone` from the child's caller.
  `adopt.sh . --milestone D0` writes `milestone: D0` under `shipquick_ref:` in `shipquick-call.yml`, so a project that has deployed
  nothing yet no longer needs a Dev link and a Production link. The value goes into the job through `env:`, not inline in `run:`.
- `docs/ADOPTION.md` has a section on the milestone; `docs/children.md` has the v0.11.0 bump notes (#356).

## What breaks for children on the bump

Nothing. The default is `D1`, which is what v0.11.0 did, so a caller with no `milestone:` line behaves as before.
One note: `adopt.sh` refuses a `milestone:` line in the caller that is not exactly `milestone: D0` to `milestone: D6` (quoted, lowercase,
D7 or a trailing comment), and says which line. Fix the line or pass `--milestone D<n>`.

## Not yet

- `adopt.sh` still overwrites a child's customised `.claude/commands/mode.md` (feedback #359).
- The items of v0.11.0: a live bench run (#312, cancelled), generated files in the codebase map.

## How a child moves up

Bump `knowledge/shipquick_latest` to `v0.11.1`. Run `scripts/adopt.sh <path>` (add `--milestone D0` if nothing is deployed yet). See `docs/ADOPTION.md`.
