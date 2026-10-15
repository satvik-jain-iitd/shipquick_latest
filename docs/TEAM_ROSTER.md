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
