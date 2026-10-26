# Modes: how much the agents do alone

The owner picks one mode per project. The mode is one word (`manual`, `semi` or `auto`) in `$(git rev-parse --git-common-dir)/shipquick-mode`.
Every worktree of the repo shares it, and git does not track it. Agents only read it: `scripts/mode.sh get` (in a child project: `knowledge/shipquick_latest/scripts/mode.sh get`), at session start. `/mode` shows it.
**Only the owner sets it.** If the mode is not set, the agent asks the owner, and the owner sets it by typing `! bash scripts/mode.sh set <word>` himself (a `!` line is his own shell input, never an agent's tool call). An agent never runs `set`: if it could set auto, it could merge through the gate on its own.

| Mode | Who codes | Who reviews | Who merges | What still stops for the owner |
|---|---|---|---|---|
| Manual | the agents | the owner | the owner | everything: the agents code and open pull requests |
| Semi | the agents | the agents review each other (the reviewer approves) | the owner | the merge |
| Auto | the agents | the agents review and approve | the agents, with `scripts/review_merge.sh` only | money, secrets, and posts or messages to people |

## The merge gate (Auto only)
`scripts/review_merge.sh <pr> [owner/repo]` is the only way an agent merges. It refuses, and says which rule, unless all of these hold:
1. The mode is `auto`.
2. The pull request is open, not a draft, and has no conflicts.
3. `satvik-jain-iitd` approved the latest commit. An approval of an older commit, or a later request for changes, does not count.
4. No review thread is unresolved.
5. Every check is `SUCCESS` (`SKIPPED` and `NEUTRAL` count as passed, the way GitHub counts them). No checks at all is a refusal.
6. The body has `Closes #n`.

Then it runs `gh pr merge --merge` with the review account's own token. It never changes the active `gh` account. In Semi or Manual the script refuses with "mode is semi" or "mode is manual".
An agent in Auto mode never merges with any other command. The owner turns Auto on himself, with `! bash scripts/mode.sh set auto`.

**Known limit.** The gate cannot tell the two sessions apart. That the session which wrote a pull request does not approve it rests on rule 30 (the author never reviews their own PR), not on code. Dependabot pull requests carry no `Closes #n`; story #70 decides how the gate treats them.

## What Auto never does alone
Spend money, touch secrets, and post or send messages to people (LinkedIn, email, chat). Those stop for the owner in every mode.
