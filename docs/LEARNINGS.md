# ShipQuick: Learnings and Mistakes

This is the one place for what we learned and what we got wrong. Read it
together with `docs/process-trace.md` at the start of every session.

Rule: when you learn something or make a mistake, add one row here. Keep it
short. Say what happened and what to do next time.

## Mistakes we made, and the rule for next time

| Date | Area | What happened | Rule for next time |
|---|---|---|---|
| 2026-10-14 | GitHub | `Closes #N` did not close issues. Feature PRs merge into `dev`, and GitHub auto-closes only on a merge into the default branch. | Run `scripts/close_linked_issues.py <pr>` after a merge into `dev`. See ADR-003. |
| 2026-10-15 | Team | The owner relayed messages between the coder and the reviewer by hand, with no fixed shape. Things got lost and chat was the only record. | End every unit of work with one fenced block per other teammate. The coder's block to the reviewer lives in the PR body, the reviewer's in the review body. See `docs/TEAM_PROTOCOL.md`. |
| 2026-10-15 | Team | Three copies of the handoff rule lived on the Mac and said different things (block vs paragraph, English vs Hindi, STATE.md that never existed). | One canonical skill, copies only by full sync, pointers everywhere else. A regex check in CI keeps the shape honest. See ADR-004. |
| 2026-10-15 | Team | Blocks to the owner said "merge" every time but never when. The owner could not tell merge-then-relay from relay-then-merge. | Owner blocks carry a time word per line and one Merge: line. The merge moment is step 4 of the PR loop, once. See ADR-005. |
| 2026-10-26 | CI | `ci.yml` ran `pull_request` only into `dev` and `main`, so the upper layers of a stacked PR (rule 23) got no check at all. A PR showed "no checks reported". | A CI trigger must not name base branches. Run on every PR, and look at the checks list of a new stacked PR first. |
| 2026-10-26 | CI | The new secret scan flagged our own fake key inside a test fixture. A planted secret in a commit stays in the history, so a revert cannot make the scan green again. | Build fake secrets at run time from two parts. Prove a red scan in a throwaway PR, not on the real one. Document an old false positive in `.gitleaksignore` with a reason. |
| 2026-10-26 | CI | The upstream-style merge-marker grep matched any text that names the markers (test files, scripts). It would have been red on day one. | Anchor the pattern to the start of a line. Run a copied check on the real repo before you trust it. |
| 2026-10-26 | CI | A green `dependency-review` was a skip: the Dependency graph probe returned HTTP 404 even on this public repo, and Dependabot alerts are off. Green looked like "reviewed". | Read the job log for the step that ran, not the colour. Turn the graph on in the repo settings. |
