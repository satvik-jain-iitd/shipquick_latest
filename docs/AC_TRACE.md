# AC traceability: every acceptance line has a test

A story says what done looks like in acceptance lines, one per line, with a stable id. The check makes sure each line points at a test that exists.

## The rule

A story a pull request closes must have:

1. One or more acceptance lines. A line that starts with `AC-1:` (then `AC-2:`, and so on) defines an id. An id mentioned inside a sentence does not define one.
2. A `Tests:` line that maps every id to a test: `AC-1 -> path::test_name`. Write several mappings on one line, separated by `;`. A test title with spaces goes in quotes: `AC-1 -> src/a.test.ts::"adds two numbers"`.

The check fails when:

- an id has no mapping (the message names the id);
- the `Tests:` line maps an id the story does not define;
- a mapped file does not exist in the repo tree, or a path points outside it;
- a mapped file does not hold the test name.

Every story made on or after 2026-11-19 is checked. A story made before that day is skipped, never failed.

## What "holds the test name" means

It is a name search, not a parse. The check opens the file and looks for the name as a whole word, so `def test_x`, `test("x"`, `it('x'` and `fun x` all count in Python, TypeScript and Kotlin, and `test_foo_bar` does not satisfy `test_foo`. It does not know whether the name is a test, only that the name is in the file. A review still decides whether the test proves the line.

## Where it runs

- Before a push: `scripts/check_local.sh ac-trace`. It reads the linked stories with `gh`, and the test files from your own repo tree.
- On a pull request: a CI step, only on pull requests. A child's CI runs it too, through checks.yml (job `ac-trace`), on the child's own tree.
- To turn it off: the feature `ac-trace` (see `docs/FEATURES.md`).

The loop that finds the linked stories is `scripts/linked_stories.py`. The other story checks still carry their own copy; moving them onto it is a separate story.
