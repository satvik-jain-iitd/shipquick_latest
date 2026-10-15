# Team Protocol: Teammate Blocks

The owner is the gate between the agents. Agents never talk to each other directly.
They talk through the owner, in short blocks the owner can read, approve, and paste as they are.

## Roles

| Role | Session | Writes to the repo | Talks to |
|---|---|---|---|
| Owner | human | merges, decides | everyone |
| Coder | one Claude session, dev account | commits, pushes, opens PRs | reviewer, owner |
| Reviewer | one Claude session, review account | comments, reviews, approves | coder, owner |

A project with more roles (designer, QA, ops) adds a row. The rule stays the same.

## The rule

When you finish a unit of work (a PR, a review, a sync, a deploy), end your reply with
**one fenced block per other teammate**. Not one block for all. One each.

- First line: `To <role>, from <role>, re <PR or issue>:`
- Under 120 words. English. Numbered imperatives: what my work changes for you, what you do next.
- Last line: what I need from you, or `Nothing needed from you.`
- A teammate with nothing to do still gets a one-line block. Nobody is left guessing.
- Facts only. No secrets, no tokens, no pasted keys.

The owner reads each block, approves it, and pastes it to that teammate. The owner changes
nothing inside a block. If the owner disagrees, the owner replies to the author, not to the receiver.

## Where the blocks live on GitHub

Chat is not the record. The PR is.

- The coder's block to the reviewer goes in the PR body under `## For the reviewer`.
- The reviewer's block to the coder is the review body (the approve or comment review).
- Replies on threads are replies on threads. A block tells the other side the threads exist.

So the owner relays by link when the block is already on the PR, and by paste when it is not.

## Example (three roles)

Coder finishes PR #33:

```
To reviewer, from coder, re PR #33:
1. New script scripts/close_linked_issues.py with a fake-gh test, 8 of 8 green.
2. Rule written into PR_RULES section 6, the PR template, and ADR-003.
3. Dry run on PR #29 and #23 pasted in the PR body.
Need from you: review 33.
```

```
To owner, from coder, re PR #33:
1. Merge after the reviewer approves.
Need from you: one yes to close #32 after the merge.
```

Reviewer approves:

```
To coder, from reviewer, re PR #33:
1. Approved on 7160c63. Reply on the 2 threads.
2. Next PR: move S0.5 under S0.4 in docs/test-cases.md.
Need from you: the reply block when the threads are answered.
```

```
To owner, from reviewer, re PR #33:
1. Squash and merge.
Nothing else needed from you.
```

## How a child project inherits this

See `docs/PLAN.md`, section D2. Short version: bump the submodule, copy rule 19 into your
own `CLAUDE.md`, fill the roles table with your sessions and accounts.
