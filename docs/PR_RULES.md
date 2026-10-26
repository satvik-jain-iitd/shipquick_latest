# PR Rules

One PR is one change. One change solves one issue.

## 1. When to raise a PR

Raise a PR when the issue is done and tests pass on your machine.

- Branch from `dev`: `feat/<issue>-<slug>`.
- Open the PR against `dev`.
- Do not wait for the end of a sprint.

## 2. How big a PR should be

- Max 50 files.
- Moved files (renames) do not count. Only added and changed files count.
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

## 5. When to merge

Merge only when all six gates are true:

1. CI is green. The required check is `gate`, which passes only when every CI job passes.
2. One approval, and the approver is not the author.
3. Zero unresolved comments.
4. Branch is up to date with the base branch.
5. PR is not a Draft and has no `do-not-merge` or `WIP` label.
6. The PR links its issue with `Closes #N`. CI checks it (`scripts/check_closes.py`, a step of the `team-block` job). Release, sync and back-merge pull requests are exempt by title prefix (`release:` or `chore:`, also `chore(deps):`), and so is Dependabot (author `dependabot[bot]`). The roadmap counts a story as done only when its issue is closed. To run it by hand: `gh pr view <pr> --json body,title,author --jq .body | python3 scripts/check_closes.py --title "<title>" --author <login>`.

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

- Auto-merge is off.
- The owner reviews, comments, approves, then merges by hand.
- Nothing merges without the owner's approval. The owner is always the last step.

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
