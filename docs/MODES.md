# Modes: how much the agents do alone

The owner picks one mode per project. The mode is one word (`manual`, `semi` or `auto`), kept one of two
places (`scripts/mode.sh get` reads in this order, story #140):
1. `.shipquick/mode` in the repo, when it exists. Tracked by git, listed in `scripts/protected_paths.txt`:
   changing it needs a PR touching a protected path, so only the owner's own merge can flip it, never an
   agent's `Bash` call. This is the only way to set the mode once this file exists.
2. Else, the old `$(git rev-parse --git-common-dir)/shipquick-mode`: one word, every worktree of the repo
   shares it, git does not track it.

Agents only read it: `scripts/mode.sh get` (in a child project: `knowledge/shipquick_latest/scripts/mode.sh get`), at session start. `/mode` shows it.
**Only the owner sets it.** Before `.shipquick/mode` exists, the agent asks the owner, and the owner sets it
by typing `! bash scripts/mode.sh set <word>` himself (a `!` line is his own shell input, never an agent's tool
call); `mode.sh set` refuses outright once `.shipquick/mode` exists, and tells the owner to edit that file and
open a PR instead. An agent never runs `set`: if it could set auto, it could merge through the gate on its own.

`.shipquick/roles.yml` (story #140) names which GitHub accounts may be `coder`, `reviewer` and `owner` for the
project. The table below is per role, not per session: any account listed as `coder` may code, any account
listed as `reviewer` may review and approve, and the same account can never do both on one pull request.

| Mode | Who codes | Who reviews | Who merges | What still stops for the owner |
|---|---|---|---|---|
| Manual | a coder account | the owner | the owner | everything: the agents code and open pull requests |
| Semi | a coder account | a reviewer account (not the author) approves | the owner | the merge |
| Auto | a coder account | a reviewer account (not the author) approves | a reviewer account, with `scripts/review_merge.sh` only; this includes dev to main (owner yes, 27 Oct 2026) | money, secrets, and posts or messages to people |

One account listed as both the only `coder` and the only `reviewer` can never run Auto (`mode.sh set auto`
refuses it): with one account playing both roles, the gate's "approver is not the author" check can never
pass, so Auto would just stop on every pull request. Manual and Semi still work; the owner reviews by hand.

## The merge gate (Auto only)
`scripts/review_merge.sh <pr> [owner/repo]` is the only way an agent merges. It refuses, and says which rule, unless all of these hold:
1. The mode is `auto`.
2. The pull request is open, not a draft, and has no conflicts.
3. `satvik-jain-iitd` approved the latest commit. An approval of an older commit, or a later request for changes, does not count.
4. No review thread is unresolved.
5. Every check is `SUCCESS` (`SKIPPED` and `NEUTRAL` count as passed, the way GitHub counts them). No checks at all is a refusal.
6. The body has `Closes #n` (or Fixes, Resolves), by the same rule as CI. Release, sync (`chore:`) and Dependabot pull requests are exempt.
7. **(story #131)** A check named exactly `gate` (ShipQuick) or `shipquick-checks / gate` (a child calling the reusable workflow) exists and is itself `SUCCESS`. Rule 5's generic loop cannot be trusted alone: a PR that deletes a job from its own caller never produces a *bad* result for that job, it simply has none — so the gate's own existence is checked too.
8. **(story #131)** The PR touches no path in `scripts/protected_paths.txt` (CI config, lint baselines, path lists a check reads its own rules from). Any such PR is refused outright, "protected path, owner merges" — a check's rules can never be loosened by the PR that check is judging.

Then it runs `gh pr merge` with the method `--squash` when the base branch requires linear history, or the one given by `--method squash|rebase|merge` (the flag wins), and `--merge` otherwise, with the review account's own token, and right after it closes the story issues the PR links, with `scripts/close_linked_issues.py <pr> --yes` (GitHub does that only for a merge into `main`). So the roadmap updates at merge time. If the merge worked but the closing failed, the gate exits 4 and prints the command to run. It never changes the active `gh` account. In Semi or Manual the script refuses with "mode is semi" or "mode is manual".
An agent in Auto mode never merges with any other command. The owner turns Auto on himself, with `! bash scripts/mode.sh set auto`.

**Known limit.** The gate cannot tell the two sessions apart. That the session which wrote a pull request does not approve it rests on rule 30 (the author never reviews their own PR), not on code. Dependabot, `release:` and `chore:` pull requests carry no `Closes #n`: the gate uses the same rule as CI (`scripts/check_closes.py`), which exempts them, so they can merge in Auto.

**Dev to main in Auto** (owner, 27 Oct 2026: "why do I need to merge if it is auto"): the coder opens the dev to main PR, the reviewer approves and merges it with the gate. The dev to main PR title starts with `release:`, so `scripts/check_closes.py` and `scripts/review_merge.sh` do not demand a `Closes #n` line. In manual and semi the owner still merges main. The owner confirmed this line (owner yes, 27 Oct 2026).

## What Auto never does alone
Spend money, touch secrets, and post or send messages to people (LinkedIn, email, chat). Those stop for the owner in every mode.
