# ShipQuick v0.14.2 (13 Nov 2026)

A patch release (`pm/agile/RELEASE_GUIDE.md`). It fixes two things a child hit: the tdd check rejected test files of most runners, and the screens doc example did not run the check. Nothing else changes.

## What a child gains

- **The tdd check reads other runners' test names.** A `## Red` section may name a test file of Python (`*_test.py`), js/jsx/ts/tsx/mjs/cjs (`*.test.*`, `*.spec.*`), Go (`*_test.go`), Kotlin (`*Test.kt`, `*Tests.kt`) and Swift (`*Test.swift`, `*Tests.swift`). The names live in one list, `TEST_NAMES`, one line per runner (#502, feedback #501).
- **The tdd check matches the changed test paths.** A path with brackets, symbols, or a space in it, such as `app/[id]/page.test.tsx`, is matched as a whole path. A test file that names no test is refused with a clear message, not a guess (#502).
- **The screens wiring example runs the check.** The "Wiring CI" example in `docs/SCREENS.md` runs `screens.sh --check` before the upload step, as `check_screens_wired.py` requires. The section says how to split a shared e2e run. The check's message names that section (#503, feedback #500).

## What breaks for children on the bump

Nothing. A child whose tests use `test_*.py` or `*.test.js` sees the same result as before.

## What a child does after the bump

1. A PR that names a test file of another runner in `## Red` now passes the tdd check, if that file is in the PR diff.
2. If your `docs/SCREENS.md` wiring copies the old example, move the check step above the upload step.

## Not yet

- The child's own CI has no tdd job yet. A child runs the check only through its pre-push hook (follow-up row, 13 Nov 2026).
- Every changed file counts as code unless it is `.md`, `.txt`, or under `docs/` or `pm/`. A config-only PR still needs `## Red` (follow-up row, 13 Nov 2026).
- Git quotes non-ASCII paths in the diff list, so a non-ASCII test file name is not matched yet. Fix: read the diff with `git diff -z` (#502 body).
- The tdd check trusts the test names a PR writes. It checks that the file exists in the diff, not that the test fails first (assumption row, 13 Nov 2026).
