# ShipQuick v0.6.1 (27 Oct 2026)

A patch release, so it ships as `v0.6.1` (`pm/agile/RELEASE_GUIDE.md`).

## New
- **Merge method.** `scripts/review_merge.sh <pr> [--method squash|rebase|merge]`.
  - No flag: the gate reads the base branch. If it requires linear history, the gate squashes. Otherwise it makes a merge commit, as before.
  - The flag wins over the setting. Any other value is a usage error and nothing is merged.
  - Why: GoServe `dev`, `documents` and `staging` refuse a merge commit, so the gate could not merge there.

## Fixed
- The scripts read the default branch of the repo named by `GH_REPO` (#88).

## For child projects
1. Move the submodule to `v0.6.1`.
2. Nothing else. The mode is yours to set; this release does not change it.
