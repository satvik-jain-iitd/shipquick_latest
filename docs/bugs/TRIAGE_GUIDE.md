# Bug Triage Guide

## One Bug = One Scope

A bug report covers exactly one broken thing. Multiple symptoms go in separate issues.

## Triage Steps

1. Read the report. Does it describe one thing?
2. Assign severity: critical, high, medium, or low.
3. Link to user story. Which story does it break?
4. Assign owner. Who owns the fix?
5. Add `triaged` label. Bug is reviewed.
6. Move to board column. Backlog, Triage, In Progress, Review, Done.

## Severity Rules

| Severity | Definition |
|---|---|
| critical | Data loss, security hole, total outage |
| high | Core feature broken, user blocked |
| medium | Feature degraded, workaround exists |
| low | Cosmetic, minor, nice-to-have |

## When to Split a Bug

Split if any is true:

- Two different components are broken.
- Two different user stories are affected.
- Fix needs two separate code changes.
- Evidence shows two different root causes.

## When to Club Bugs

Club only if all are true:

- Same root cause.
- Same user story.
- Same fix.
- Same component.

## Monitoring

Every bug has: severity, user story, owner, status, date opened, date closed. Track in `docs/bugs/ACTIVE_BUGS.md`. Update on every triage and every close.
