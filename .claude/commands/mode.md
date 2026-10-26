---
description: Show or set how much the agents do alone (manual, semi or auto)
argument-hint: [manual|semi|auto]
---

Show or change the mode of this project. The three modes are in `docs/MODES.md`.

1. With no argument: run `scripts/mode.sh get` (in a child project: `knowledge/shipquick_latest/scripts/mode.sh get`) and tell the owner the word. If it exits 3, the mode is not set: ask the owner to pick `manual`, `semi` or `auto`.
2. With an argument `$ARGUMENTS` that is `manual`, `semi` or `auto`: run `scripts/mode.sh set $ARGUMENTS` (in a child project: `knowledge/shipquick_latest/scripts/mode.sh set $ARGUMENTS`). Any other word: refuse and list the three.
3. After a change, tell the peer session with SendMessage, in one line: "mode is now <word>". Every worktree reads the same file, so no other step is needed.
4. Auto mode lets an agent merge, but only with `scripts/review_merge.sh <pr>`. Never ask the owner to confirm Auto for someone else: the owner types `/mode auto` himself.
