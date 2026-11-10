# Follow-ups

Every follow-up that is not in a story goes here. Never delete a row; mark it done.

| Date | Follow-up | Why it is open | Owner | Status |
|---|---|---|---|---|
| 2026-11-10 | `scripts/check_local.sh` `secrets` scans the whole history, so it fails here on the planted test secret in `refs/remotes/pr/47` (commit `be6fd3c`) and on the 131 `refs/remotes/pr/*` refs of this clone. Scope it to the branch's own commits in one flag (for example `--log-opts="origin/dev..HEAD"`). | `scripts/check_*.sh` is on the protected list, so the change needs the owner's merge. The CI secret-scan still covers the full history, so the gate is not weakened today. | owner (merge) | open |
| 2026-11-10 | rule 30 (CLAUDE.md): one line pointing to docs/REVIEW_SHAPE.md (the review finding shape, the Verdict and Not checked lines) | CLAUDE.md is on the protected list (owner merges), so the coder does not edit it | owner (merge) | open |
| 2026-11-10 | The codebase map (`plugin/hooks/map.py`) does not skip generated files such as `.d.ts` and `.min.js`, so their names can fill a folder line. Add a skip pattern and a test. | Found in the #351 review; not a blocker. | coder | open |
| 2026-11-10 | Prune `.claude/worktrees/` left by killed workflow runs (`wf_*` and `agent-*` folders and their local branches). Check each with `git worktree list` and an unpushed-commit check first; some local branches are stale copies of PR heads. | Killed workflow runs leave worktrees behind. | owner (yes before delete) | open |
