# PR Rules

One PR is one change. One change solves one issue.

## 1. When to raise a PR

Raise a PR when the issue is done and tests pass on your machine.

- Branch from `dev`: `feat/<issue>-<slug>`.
- Open the PR against `dev`.
- Do not wait for the end of a sprint.

The coder opens every PR, feature to dev and dev to main. The reviewer never opens one; it reviews and merges (see section 8).

## 2. How big a PR should be

- Max 50 files.
- Moved files (renames) do not count. Only added and changed files count.
- Recorded reference images (`ui/ios/ShipQuickUITests/__Snapshots__/*.png`, story #219) do not count. Only that exact folder: a `__Snapshots__/` folder anywhere else still counts. They are looked at, not read, and their folder is a protected path, so the owner merges a change to them anyway.
- Target about 400 lines changed.
- Bigger than that means split it.

## 3. Draft and Ready

- Use a **Draft PR** while work is in progress.
- Mark it **Ready for review** only when self review is done and tests are green.

## 4. When to review

- Review the same day the PR is marked Ready.
- The reviewer must not be the author.
- In this repo the reviewer is the second account.
- All comments must be resolved.
- The coder's block to the reviewer sits in the PR body under `## For the reviewer`. The CI job `team-block` checks its shape with `scripts/check_block.py`.
- The reviewer's block to the coder is the review body (the approve or comment review). Shape: `To coder, from reviewer, re PR #N:`, numbered, last line = what the reviewer needs. See `docs/TEAM_PROTOCOL.md`.
- A frontend PR, in a project with `docs/screens.txt`: the approval body also carries `Render: <board> -- matches`, written after the reviewer put the render beside the board. `scripts/review_merge.sh` refuses without it (story #153, `docs/SCREENS.md`).

## 5. When to merge

Merge only when all six gates are true:

1. CI is green. The required check is `gate`, which passes only when every CI job passes.
2. One approval, and the approver is not the author.
3. Zero unresolved comments.
4. Branch is up to date with the base branch.
5. PR is not a Draft and has no `do-not-merge` or `WIP` label.
6. The PR links its issue with `Closes #N`. CI checks it (`scripts/check_closes.py`, a step of the `team-block` job). `Fixes #N` and `Resolves #N` count too: the check uses the link rule of `scripts/close_linked_issues.py`, and `scripts/review_merge.sh` uses the same check, so the merge gate and CI never disagree. Release, sync and back-merge pull requests are exempt by title prefix (`release:` or `chore:`, also `chore(deps):`), and so is Dependabot (author `dependabot[bot]`, or `app/dependabot` as `gh` prints it). The roadmap counts a story as done only when its issue is closed. To run it by hand: `gh pr view <pr> --json body,title,author --jq .body | python3 scripts/check_closes.py --title "<title>" --author <login>`.

Formula:

```
merge = CI AND approval AND no-open-comments AND up-to-date AND not-draft AND linked-issue
```

If any gate is false, do not merge.

## 6. Closing the issue after merge

GitHub closes `Closes #N` issues only when the PR merges into the default branch (`main`).
A feature PR merges into `dev`, so its issues stay open. We close them by hand.

- The PR body still says `Closes #N`. It works for PRs into `main`.
- When the base is not the default branch, the PR checklist adds: "Close issue #N by hand after merge, with a comment linking this PR."
- After the owner says the PR is merged, run `python3 scripts/close_linked_issues.py <pr>`. It checks `gh pr view <pr> --json state,baseRefName`.
- Dry run first. It prints the issues it would close and the ones it skips. Nothing changes.
- The owner gives one yes. Then `--yes` closes each issue with the comment: `Done in PR #X (merged to <base>).` In Auto mode `scripts/review_merge.sh` runs this script with `--yes` right after its merge, so the issue closes at merge time and the roadmap updates then.
- It never closes an epic (label `epic`). It closes only the story issues linked by `Closes #N`.
- It never closes an issue whose PR is still open, or closed without a merge.

## 7. Merge method

| PR | Method |
|---|---|
| feature -> dev | Squash |
| dev -> main | Merge commit |

## 8. Auto-merge

- GitHub auto-merge is off.
- In manual and semi mode the owner merges by hand, after the approval. Nothing merges without the owner's approval.
- In auto mode the reviewer merges, feature to dev and dev to main, only through `scripts/review_merge.sh` and only when every gate in section 5 is true. The owner is not asked. The dev to main PR title starts with `release:`, so the gate does not demand a `Closes #n` line (section 5, gate 6).

## 9. Coverage

Coverage means: how many issues have a linked PR.

- Every PR should link its issue.
- The report lives in `docs/PR_COVERAGE.md`.
- Update the report when a PR is opened or merged.

## 10. Emergency bypass

Protection applies to admins too. For a real emergency:

1. Turn the branch protection off.
2. Do the urgent fix.
3. Turn protection back on at once.
4. Write a note in `docs/journal/`.

## 11. Rollback

- Remove rule: `DELETE .../branches/{branch}/protection`.
- Turn auto-merge off in repo settings.

## 12. Release freeze (story #126)

A freeze is a file, not a note in chat. `scripts/freeze.sh on "<reason>" --until <date>` writes
`.shipquick/freeze` on `main` through its own PR; `freeze.sh off` removes it the same way;
`freeze.sh status` prints what it would decide, reading `origin/main` (never the local checkout's
own uncommitted or unpushed files -- bug #142) or any `owner/repo` given with `--repo`.

While `.shipquick/freeze` exists on `main`:
- `scripts/review_merge.sh` refuses every merge into `main`, with the freeze's reason and until-date
  in the refusal. `.shipquick/freeze` is also a protected path (story #131): even the PR that only
  lifts the freeze needs the owner's own merge, never an auto-merge — lifting a freeze is the
  owner's decision too, the same as changing it.
- The `freeze` job in `ci.yml` (and the reusable `checks.yml` a child calls, story #124) fails a PR
  into `main` the same way, reading the already-checked-out file — a PR that only removes the file
  already shows it gone in the merge-commit checkout, so no separate exemption is needed there.

A freeze past its `until:` date does not lift itself: `scripts/check_freeze.py` still refuses, now
flagged STALE, until someone runs `freeze.sh off` or a fresh `freeze.sh on ... --until <later date>`.

## 13. Hardening the gate (story #131, epic #130)

A gate is only as strong as the merge. Three things close the gap where a PR could otherwise switch
its own gate off from inside itself:

- **A required `gate` check.** `checks.yml` (and `ci.yml`) has a `gate` job that `needs:` every
  other job and fails on any failure or cancellation. `scripts/review_merge.sh` refuses unless a
  check named exactly `gate` (ShipQuick) or `shipquick-checks / gate` (a child calling the reusable
  workflow) itself ran and is `SUCCESS` — a generic "every check is SUCCESS or SKIPPED" loop cannot
  be trusted alone, since a PR that deletes a job from its own caller never produces a *bad* result
  for that job, it simply has none.
- **Protected paths.** `scripts/protected_paths.txt` lists the paths whose own rules can't be
  loosened by a PR under those rules: CI workflow files, the ShipQuick submodule pin, lint configs
  and baselines, token files, and the path lists other checks read their own scope from
  (`docs/frontend-paths.txt`, `docs/architecture-paths.txt`, `docs/guard.yml`). In auto mode,
  `review_merge.sh` refuses any PR touching one of them outright — "protected path, owner merges" —
  so the owner reviews and merges that PR by hand, never an agent.
- **A protected PR with the owner's yes (story #180, ADR-013).** The reviewer merges it with the gate only when
  the approving review records `Second review: <who, findings>` and `Owner yes: <YYYY-MM-DD> "<his words>"`.
  `.shipquick/*` stays the owner's own merge.
- **Adoption ancestor.** The adoption job (`scripts/check_adoption_ancestor.py`) also requires the
  pinned ShipQuick commit to be merged into `dev` or `main`, or be a release tag — not just any
  commit that exists in ShipQuick's history, which would let a PR pin a throwaway branch commit that
  never passed ShipQuick's own review.
- **Disable-comment guard.** `scripts/check_disable_comments.py` fails a PR that adds an
  `eslint-disable`, `stylelint-disable`, `swiftlint:disable`, `@ts-nocheck`, `@Suppress(`, or a new
  ignore-file entry on an added line — unless the PR's body names the ADR that justifies it
  (`ADR: docs/decisions/ADR-NNN.md`).
- **Design literal guard (story #133).** `scripts/check_design_literals.py` fails a PR that adds a hex,
  `rgb()`, `hsl()` or font-family literal (a Tailwind `bg-[#...]` too) on a new line of a `.css`, `.ts`,
  `.tsx`, `.astro`, `.vue` or `.svelte` file. The look comes from the tokens, so app code says
  `var(--color-primary)` or `theme.fonts.body`. The token files themselves are listed in
  `scripts/design_token_files.txt` (a protected path, so a PR cannot allowlist its own file). The same
  `design-tokens` job then runs stylelint on the changed CSS files with `--report-needless-disables`: it installs
  the project's own dependencies first (`npm ci`, when a lockfile exists) and runs the project's stylelint, with
  pinned `npx` as the fallback, since a config's `extends` and `plugins` resolve from the project's node_modules.
  It skips when no CSS changed or the project has no stylelint config (a file or a `stylelint` key in package.json).
  Comment text on a line (`// story #133`, `/* ... */`) is never a literal.

## 14. CI runs what a change can break (story #484)

- `ci.yml` has one run per PR. A new run of the same PR (a push, an edited body) cancels the old one. A push run on `dev` or `main` and a manual run are never cancelled.
- The phone jobs (`ui-android-*`, `ui-ios-*`) run only when their area of `scripts/change_map.json` is on (story #485, ADR-018); the reader is `scripts/change_map.py`, and the gate checks every result against it. `ci.yml` itself is not in those rules, so a PR that only edits `ci.yml` does not wait for a macOS machine.
- A PR that edits the steps of a `ui-*` job inside `ci.yml` turns that job's area on (story #485, ADR-018 rule 4). A push is decided from its own diff: the base is `github.event.before`, and only a manual run, a schedule or an unreadable `before` turns every area on (story #485, ADR-018). The manual full run asked of the reviewer in #484 is no longer needed.
- How to read the manual run: on its own run page, never on the PR's checks list. A manual run puts checks with the same names on the head commit, skips every PR-only job (`tdd`, `roles`, `team-block` and others) and starts later, so on the PR it can show a green `gate` over a red PR run. So after the manual run, a PR-event run (a push or a body edit) must be the last run before the approval, and `scripts/review_merge.sh` then reads that one.
- The `gate` job keeps `if: always()` and fails on a cancelled job. GitHub counts a skipped required check as passed, so a gate that did not run would let a run with a cancelled job look green.

## Test file names in `## Red` (story #502, feedback #501)

The tdd check (`scripts/check_tdd.py`) accepts a `## Red` path only when its file name is one of the runner names in `TEST_NAMES`, and the file is in the PR diff:

- pytest and unittest: `test_*.py`, `*_test.py`
- node:test, jest, vitest, playwright, jasmine: `*.test.{js,jsx,ts,tsx,mjs,cjs}`, `*.spec.{js,jsx,ts,tsx,mjs,cjs}`
- go test: `*_test.go`
- kotlin: `*Test.kt`, `*Tests.kt`
- swift (XCTest): `*Test.swift`, `*Tests.swift`

The pytest `::test_name` form still works. A path in the diff that no name accepts (a fixture, a JSON file) fails with a line that says so. To add a runner, add one line to `TEST_NAMES`; a project config file is not read.

## 15. The merge script counts the PR's own, newest runs (story #496, epic #485 items 15 and 16)

- `scripts/review_merge.sh` reads the workflow runs of the PR head (`gh api repos/<repo>/actions/runs?head_sha=<sha>`) and `scripts/check_pr_runs.py --pr <number>` decides which check rows count. The run of a row is in its `detailsUrl`.
- A `pull_request` run counts only when its `pull_requests` list is exactly this PR. The list holds every open PR on the head, so another PR in it (alone or beside this one) refuses with "two pull requests share this head". An empty list (a pull request from a fork, or a run after the merge) names nobody and is not counted. A fork PR is therefore not merged by the script: the owner merges it.
- The rows of a `push` or a `workflow_dispatch` run are dropped. Such a run skips the PR-only jobs and starts later, so its green `gate` can never replace a red PR result. Rows of every other event (for example `pull_request_target`) count as before.
- Of the `pull_request` runs of one workflow, only the newest (highest `run_number`) counts. A run that a newer run of the same workflow and event replaced leaves stale rows (a `test` cancelled before the matrix expanded, next to `test (3.12)` of the next run, seen on #509); they are not counted, so a new commit is no longer needed to clear them. The newest run still counts when it is red or cancelled, and a newest run with no rows yet leaves no `gate`, so the merge is refused.
- A row with no run id (a commit status from another app) counts as before. A run list that cannot be read, or a row whose run the list does not name, refuses the merge.
- Every job of `ci.yml` is in the `needs` of `gate`, or is named as exempt in `tests/test_gate_needs.py`. `shortcut-ledger` is in the list. It stays warn-only through `continue-on-error` on its step, so the job and its check row end green.

## 16. The nightly full run on dev (story #497, epic #485 item 7)

- The change map skips slow jobs by path (section 14). Once a night every job runs on `dev`, so a hole in the map shows within a day. `.github/workflows/nightly.yml` is only a timer (01:23 UTC) and one call to `scripts/nightly_full_run.py`; the decision lives in the script and its tests (`tests/test_nightly_full_run.py`).
- A scheduled run uses the workflow files of the default branch, not `dev`. So the script dispatches `ci.yml` on `dev` itself (`gh api -X POST .../workflows/ci.yml/dispatches -f ref=dev`): every job checks out `dev`. The change map already turns every area on for an event that is not a pull request or a push, so there is no second rule. The PR-only jobs (`tdd`, `roles`, `team-block` and the rest) are skipped on such a run, as on any manual run.
- A green night opens nothing. A red night opens one issue (label `nightly`, title "nightly: the full CI run on dev is red") that names each bad job and says, for each, whether it **failed**, **never got a machine** (only a job still queued or waiting at the deadline) or was **cancelled before it started** (a completed job no runner took, cancelled together with its run). The `gate` job is not listed beside the real job it failed for. A second red night comments on the same open issue. The reviewer closes the issue when `dev` is green; the next red night then opens a new one. The label is created by the script when it is missing.
- The script waits up to 150 minutes for the run. A job still queued at the deadline never got a machine; a job still running at the deadline failed. A dispatched run that does not appear in ten minutes is one problem, not a green night.
- **A night the script cannot read or report ends red** (exit 1), so GitHub shows it to someone: a failed dispatch, run list, run state (three reads in a row), jobs list or issue list, or an issue or comment that did not land. A failed read is never taken for "no run yet" or "no open issue" (that would report a red night that may be green, or open a second issue). The adoption scan follows the same rule: it reports every child, then ends red when a report did not land. A failed `gh label create` alone is a warning; the issue create fails when the label is really missing.
- `nightly.yml` has a `concurrency` group (`nightly-full-run`, never cancelling), so a manual start beside the timer waits and cannot open two issues.
- `python3 scripts/nightly_full_run.py --dry-run` dispatches nothing and changes nothing: it reads the latest dispatched run and prints what it would do.
- The timer file runs from the default branch, so the nightly starts only once `nightly.yml` is on `main` (the next `dev` to `main` promotion). It is a protected path (`.github/workflows/*`): the owner merges the PR.
- Issue opening is one helper, `scripts/issue_notice.py`, used by this script and by `scripts/adoption_scan.py`.
