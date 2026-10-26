# Sprint Lanes — S<nn>

Rule 23 (`CLAUDE.md`): up to 3 stacks open, in separate lanes. Fill this in at sprint planning, next to `sprint-plan.md`.

A **lane** is a set of stories that touch the same files. Stories in one lane run one after the other.
Stories in different lanes run at the same time, each lane with its own coder session and git worktree.

## Foundation first
Work that other stories build on (shared types, API shape, database tables, a shared config) goes first and merges before the lanes start.

| Issue | Title | Files touched | Merged? |
|---|---|---|---|
| # |  |  |  |

## Stories and the files they touch

| Issue | Title | Files touched | Lane |
|---|---|---|---|
| # |  | path/one, path/two | A |

## Check for overlap
For every pair of stories in different lanes: do the "Files touched" lists share a file? If yes, move one story into the other's lane, or split the shared change into a foundation story.
The append-only logs (`docs/process-trace.md`, `docs/LEARNINGS.md`) do not count: they merge on their own (`merge=union`).

## Lanes

| Lane | Stories in order | Coder session | Worktree |
|---|---|---|---|
| A | #, # | `<project>-dev` | main checkout |
| B | # | `<project>-dev2` | `../<project>-dev2` |
| C | # | `<project>-dev3` | `../<project>-dev3` |

Make a worktree: `git worktree add ../<project>-dev2 -b feat/<issue>-<slug> origin/dev`.

## First merge of a branch made before `.gitattributes` existed
Git reads the union setting from the branch you merge into, and the file arrives with that same merge, so that one merge still conflicts in the logs.
Put `docs/process-trace.md merge=union` and `docs/LEARNINGS.md merge=union` (one per line) in `.git/info/attributes`, run the merge, then delete that file. After it the branch has `.gitattributes` and every later merge works. Tested on 26 Oct 2026.

## Every day
GitHub's merge button ignores `merge=union`, so do this with Git on the Mac, not with "Update branch".
Each coder merges `dev` into every open branch of its lane (`git fetch && git merge origin/dev`), fixes any conflict that day, and pushes.
