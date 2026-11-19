# Flaky tests: the registry

A flaky test passes and fails with no change in the code. The registry is a list of the flaky tests we know about, each with an owner and an
expiry date. It makes a quarantine visible and short. It is a list with an expiry, not a skip switch: no test runner reads it today, so a test in
the list still runs and can still fail.

## Where it is

`.shipquick/flaky-tests.json`: a JSON list. An empty list `[]` means no known flaky test. A repo with no file passes the check, so a child that has
no registry is fine.

## One row

| Field | What it holds |
|---|---|
| `test_id` | The test, as `path::name`. One row per test; a duplicate fails. |
| `path` | The file that holds the test. |
| `owner` | The person who fixes it. |
| `issue` | The link to the issue that tracks the fix. |
| `reason` | Why it is flaky, in one short line. |
| `quarantined_on` | The day it went in the list, `YYYY-MM-DD`. |
| `expires_on` | The day the quarantine ends, `YYYY-MM-DD`. It cannot be before `quarantined_on`. |
| `status` | `quarantined` (known flaky, waiting for the fix) or `fixed` (the fix landed; the row stays as history). |

Optional fields, never required: `tier` (where it was seen: `pr`, `post-merge`, `nightly` or `manual`), `last_failure` (the day it last failed, `YYYY-MM-DD`) and `run_url` (the link to
a CI run that failed).

## Who adds a row

A row is added by the coder, in a pull request, with the issue that tracks the fix. The file is a protected path, so the owner merges that pull request.

## What expired blocks

`scripts/check_flaky.py` fails when a row with status `quarantined` has an `expires_on` in the past. The check runs before a push and in CI
(`scripts/check_local.sh flaky`; in CI, a step of the `pre-commit` job). A failing check blocks the push until the test is fixed (set `fixed`) or the owner agrees to a new date.
