# Release Guide

How we version and ship.

## Versioning

We use **Semantic Versioning**: `vMAJOR.MINOR.PATCH`.

| Part | Bumps when | Example |
|---|---|---|
| MAJOR | A breaking change | `v1.0.0` → `v2.0.0` |
| MINOR | A new feature, backward compatible | `v0.2.0` → `v0.3.0` |
| PATCH | A bug fix, backward compatible | `v0.3.0` → `v0.3.1` |

A **D increment** is a MINOR bump. So D4 ships as `v0.4.0`.
A **hotfix** is a PATCH bump.
A breaking change is a MAJOR bump.

## Tag names

Use `vX.Y.Z`. Example: `v0.4.0`.
Keep the demo note at `docs/demos/<tag>.md` (for example `docs/demos/v0.4.0.md`).

## Release branch and back-merge (lesson from v0.5.0, PRs #55 to #57)

`dev` and `main` must share history, or the release PR is BEHIND and GitHub will not update it.
1. Cut `release/vX.Y.Z` from `dev`. Merge `main` into it. The tree stays the same as `dev`, so the diff to `main` is only the release.
2. Open the release PR from `release/vX.Y.Z` into `main`. Merge it with **Create a merge commit**, never Squash or Rebase.
3. Tag `vX.Y.Z` on `main`, then publish the GitHub Release.
4. Back-merge: open a PR that merges `main` into `dev` and merge it with a merge commit too. Every new branch starts from that `dev`.

## Release checklist

1. All sprint stories are merged and Done.
2. CI is green on `main`.
3. The demo note exists at `docs/demos/<tag>.md`.
4. `CHANGELOG.md` is updated.
5. `docs/PROGRESS.md` is updated.
6. Create the tag `vX.Y.Z`.
7. Publish the GitHub Release. Paste the changelog section as the notes.

## Rollback

If a release is bad:
1. Revert the bad commit with a new PR. Do not force-push.
2. Tag a new PATCH version with the fix.
3. Delete the broken tag if it was never used. Otherwise leave it and tag forward.

## Never

- Never force-push `main` or a release tag.
- Never tag a release with a red CI.
- Never skip the changelog.
