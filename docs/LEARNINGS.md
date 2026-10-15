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
