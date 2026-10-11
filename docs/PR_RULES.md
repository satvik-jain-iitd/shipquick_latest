# PR Rules

One PR is one change. One change solves one issue.

## 1. When to raise a PR

Raise a PR when the issue is done and tests pass on your machine.

- Branch from `dev`: `feat/<issue>-<slug>`.
- Open the PR against `dev`.
- Do not wait for the end of a sprint.

## 2. How big a PR should be

- Max 50 files.
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

## 5. When to merge

Merge only when all six gates are true:

1. CI is green. The required check is `gate`, which passes only when every CI job passes.
2. One approval, and the approver is not the author.
3. Zero unresolved comments.
4. Branch is up to date with the base branch.
5. PR is not a Draft and has no `do-not-merge` or `WIP` label.
6. The PR links its issue with `Closes #N`.

Formula:

```
merge = CI AND approval AND no-open-comments AND up-to-date AND not-draft AND linked-issue
```

If any gate is false, do not merge.

## 6. Merge method

| PR | Method |
|---|---|
| feature -> dev | Squash |
| dev -> main | Merge commit |

## 7. Auto-merge

- Auto-merge is off.
- The owner reviews, comments, approves, then merges by hand.
- Nothing merges without the owner's approval. The owner is always the last step.

## 8. Coverage

Coverage means: how many issues have a linked PR.

- Every PR should link its issue.
- The report lives in `docs/PR_COVERAGE.md`.
- Update the report when a PR is opened or merged.

## 9. Emergency bypass

Protection applies to admins too. For a real emergency:

1. Turn the branch protection off.
2. Do the urgent fix.
3. Turn protection back on at once.
4. Write a note in `docs/journal/`.

## 10. Rollback

- Remove rule: `DELETE .../branches/{branch}/protection`.
- Turn auto-merge off in repo settings.
