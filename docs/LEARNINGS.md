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
| 2026-10-26 | n8n | A webhook path with a parameter (`roadmap/:slug`) gets an id put into its production URL, and the id changes on a re-import. A link meant to live in READMEs would break. | Use one fixed path and put the project in the query (`?s=<slug>&k=<key>`). |
| 2026-10-26 | CI | `node --test roadmap/` fails on Node 22 (`Cannot find module`): a folder is no longer expanded. The story text said it. | Use a glob, `node --test roadmap/*.test.js`, and check a command on the real Node before you write it into a story. |
| 2026-10-26 | CI | The note said to delete .gitleaksignore after PR #46 merged, as if it were a squash. It was a merge commit, so the fake-key commit is still in the history of dev. | Test the claim: move the file away and run `gitleaks git .` on dev. It reported 1 leak, so the file stays. |
| 2026-10-26 | n8n | A webhook whose link carries a key saves every request in the n8n execution history by default, key and page included. Hashing the key in the repo did not help. | Set `saveDataSuccessExecution: none` on any MAIN that serves a secret link, and test the setting. |
| 2026-10-26 | Design | The roadmap was built on n8n first. A kit's users may have no n8n, so every child project would have depended on a tool the kit does not ship. The first story lost its deploy work. | Before a story picks a runtime, ask what a kit user already has. For a kit that is GitHub itself. |
| 2026-10-26 | CI | Scheduled and issue-triggered workflows start only from the default branch (main). A workflow merged into dev does not fire on a new issue until a release moves it to main. | Test a new trigger on a pull request first, and say in the story that the timer needs the promotion to main. |
| 2026-10-26 | CI | The first dogfood caller had a `pull_request` trigger, so a PR would run its own unreviewed script with `contents: write`, and the run was green, so it looked fine. | A workflow with write rights must never run code from the change that triggers it. Use triggers that start from the default branch (workflow_run, issues, schedule). |
