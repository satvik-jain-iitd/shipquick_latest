# Agile Guide

The model for how work moves. Lightweight Scrum with a Kanban flow.

## Levels

```
PI / Increment (D<n>)     a big goal. 3 to 4 weeks.
   └── Sprint (1 week)    a time box. One GitHub milestone.
         └── Story / Bug   one issue. One pull request.
```

| Level | In GitHub | Notes |
|---|---|---|
| PI | D increment, epic issue | `docs/pis/D<n>.md` holds the goal |
| Sprint | Milestone named `S<nn>` | due date = sprint end |
| Story | Issue | one story = one PR |
| Bug | Issue | one bug = one issue |

## Roles

- **Owner** = product owner and reviewer. Decides priority. Reviews and merges every PR.
- **Agent** = developer. Writes the code, tests, and the PR.

There is no separate manager. The owner is always the last step before merge.

## Why no effort estimates

AI writes the code. Coding time is roughly the same for every story.
The real limit is the owner's review and decision time.
So we rank by value, and we cut work into stories small enough to review.

## Cadence

| When | Ceremony |
|---|---|
| Start of PI | PI Planning |
| Each week, before the sprint | Refinement |
| Sprint day 1 | Sprint Planning |
| Every day | Board check |
| Sprint last day | Sprint Review (demo) |
| After the review | Retrospective |

## The board

Columns: `Backlog → Refined → Sprint Ready → In Progress → Review → Done`.

Rules:
- New issue goes to Backlog.
- Refined issue moves to Refined.
- Chosen for the sprint moves to Sprint Ready.
- Max 2 items In Progress at a time.
- A PR open moves the item to Review.
- Merged moves it to Done.

## Definitions

- **Definition of Ready** and **Definition of Done**: see `docs/PLAN.md` Part D.
- A story may start only when it is Ready.
- A story is done only when it is Done.
