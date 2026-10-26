# Team Roster

One row per role. Role names are lowercase and are the names used in teammate blocks
(`To <role>, from <role>, re <ref>:`). See `docs/TEAM_PROTOCOL.md`.

A child project copies this file and fills it with its own sessions and accounts.
More roles = more rows. The rule does not change.

## Template

| Role | Who (tool / session) | Account | Writes | Talks to |
|---|---|---|---|---|
| owner | human | | merges, decides | everyone |
| coder | | | commits, PRs | reviewer, owner |
| reviewer | | | reviews, approves | coder, owner |

## ShipQuick

| Role | Who (tool / session) | Account | Writes | Talks to |
|---|---|---|---|---|
| owner | human, Satvik | satvik-jain-iitd | merges, decides | everyone |
| coder | Claude Code session (this repo) | satvik-jain-iitd | commits, PRs | reviewer, owner |
| reviewer | Claude Code session (tpm-pr-review) | satvik-jain-iitd | reviews, approves | coder, owner |

Child projects with two GitHub accounts put the build account on the coder row and the review
account on the reviewer row (GoServe: `klickbae8yt-star` builds, `satvik-jain-iitd` reviews).

## The two-session pair (owner, 26 Oct 2026)

| Role | Who (tool / session) | Model | Account | Writes | Talks to |
|---|---|---|---|---|---|
| owner | human, Satvik | — | satvik-jain-iitd | merges in the UI, decides | everyone |
| coder | Claude Code session `<project>-dev` | Sonnet | klickbae8yt-star | branches, tests, code, PRs | reviewer, owner |
| reviewer | Claude Code session `<project>-qa` (also the orchestrator: plan, stories, architecture) | Opus | satvik-jain-iitd | reviews, approves, stories | coder, owner |

- The two sessions talk with `ListAgents` + `SendMessage`, in teammate-block shape. The owner is not the relay.
- Each session has its own folder: the coder in the main checkout, the reviewer in a git worktree. Never edit the other's folder.
- Parallel work (owner, 26 Oct 2026): one reviewer session and up to 3 coder sessions (`<project>-dev`, `<project>-dev2`, `<project>-dev3`), one per lane, each in its own git worktree. The lanes come from `pm/agile/templates/sprint-lanes.md`. The reviewer reviews every lane.
- Live example: job-search (`job-search-dev` and `job-search-qa`), GoServe (`GoServe-dev` and `GoServe-qa`).
