# Follow-ups

Every follow-up that is not in a story goes here. Never delete a row; mark it done.

| Date | Follow-up | Why it is open | Owner | Status |
|---|---|---|---|---|
| 2026-11-10 | `scripts/check_local.sh` `secrets` scans the whole history, so it fails here on the planted test secret in `refs/remotes/pr/47` (commit `be6fd3c`) and on the 131 `refs/remotes/pr/*` refs of this clone. Scope it to the branch's own commits in one flag (for example `--log-opts="origin/dev..HEAD"`). | `scripts/check_*.sh` is on the protected list, so the change needs the owner's merge. The CI secret-scan still covers the full history, so the gate is not weakened today. | owner (merge) | open |
