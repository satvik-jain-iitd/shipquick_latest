# Team Protocol: Teammate Blocks

One short block, one fixed shape, for every handoff between teammates.
It works for any team: humans, Claude Code sessions, OpenCode agents, n8n bots.
Any number of roles. Any kind of work.

The canonical text lives in the global skill `~/.claude/skills/team-protocol/SKILL.md`.
This file is the copy that ships with ShipQuick. Sync by full copy, never by partial edit.

## Roles

The roles live in `docs/TEAM_ROSTER.md`. One row per role: name, who, account, what it writes, who it talks to.
A project with more roles adds rows. The rule below never changes.

## The gate

The owner is the gate between the agents. Agents never talk to each other directly.
They talk through the owner, in blocks the owner can read, approve, and paste as they are.

The owner reads each block, approves it, and pastes it to that teammate. The owner changes
nothing inside a block. If the owner disagrees, the owner replies to the author, not to the receiver.

## The unit of work

A unit of work is anything one teammate finishes that another must act on or know about.
A PR. A review. A deploy. A research doc. An n8n workflow. A content draft.

## The rule

When you finish a unit of work, end your reply with **one fenced block per other teammate**.
Not one block for all. One each. A teammate with nothing to do still gets a one-line block.

The shape:

```
To <role>, from <role>, re <ref>:
1. <what my work changes for you, or what you do next>
2. <next step>
Need from you: <one thing>.
```

- `<role>` is a lowercase name from the roster.
- `<ref>` is any stable handle: `PR #33`, `issue #35`, `workflow lead-engine-v3`, `docs/research/x.md`.
- Numbered imperatives. Under 120 words. English always.
- Last line is `Need from you: ...` or `Nothing needed from you.`
- Facts only. No secrets, no tokens, no pasted keys.

Lines for the owner in Romanized Hindi (3 at most) go in chat above the block, never inside it.
A machine checks the block, so the shape has to be exact.

## Where the blocks live

Chat is not the record.

With a PR:

- The coder's block to the reviewer goes in the PR body under `## For the reviewer`. CI checks it.
- The reviewer's block to the coder is the review body (the approve or comment review).
- Any other block is a PR or issue comment.
- The owner relays by link when the block is already on GitHub, and by paste when it is not.

Without GitHub (an n8n project, a content project):

- The owner's chat is the record.
- The sender adds one row to `docs/process-trace.md`. The Step column holds the block's header line.

## The check

`python3 scripts/check_block.py [file]` reads a block (stdin if no file) and prints `Block OK`,
or one reason and exit 1: `empty block`, `bad header`, `no numbered line`, `bad last line`,
`over 120 words`, `looks like a secret`. Run it before you post. CI runs it on every PR body.

## Examples

A PR (coder to reviewer):

```
To reviewer, from coder, re PR #33:
1. New script scripts/close_linked_issues.py with a fake-gh test, 8 of 8 green.
2. Rule written into PR_RULES section 6, the PR template, and ADR-003.
Need from you: review 33.
```

An n8n workflow (builder to owner, no GitHub):

```
To owner, from builder, re workflow lead-engine-v3:
1. Deployed SUB "score-lead" with dry_run on. 12 test items passed.
2. Turn dry_run off in Config when you have checked the Telegram alert.
Need from you: one test lead sent through the form.
```

A content draft (writer to editor):

```
To editor, from writer, re docs/drafts/kirana-growth-story.md:
1. Draft 2 is ready, 900 words, grade 6.
2. Check the three claims marked [source?] against the research table.
Need from you: the edited draft or a comment per claim.
```

## How a child project inherits this

See `docs/PLAN.md`, section D2. Short version: bump the submodule, copy rule 19 into your own
`CLAUDE.md`, copy and fill `docs/TEAM_ROSTER.md`, copy the `team-block` job into your CI.
