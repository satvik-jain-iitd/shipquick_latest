# Roadmap

Increments D0 to D6. Every issue and PR gets a milestone. Every increment gets a demo note in `docs/demos/D<n>.md`.

## Planning model

- A **PI** is a D increment (an epic). It takes about 3 to 4 sprints.
- A **sprint** is one week and one GitHub milestone named `S<nn>`.
- A **story** or **bug** is one issue and one PR.
- Steps are in `pm/agile/PI_PLANNING.md` and `pm/agile/SPRINT_PLANNING.md`.

## D0 Foundations (Done)

- Repo, branches, CI, docs.

## D1 Architecture (Done)

- Architecture patterns, ADRs, usage guides. Folder now `backend/`.

## D2 Design System (Done)

- Material Design 3 guides, REPOSITORIES.md, design tokens.

## D3 CI Hardening (Done)

- Ubuntu runners, branch protection, pre-commit hooks, hygiene tests.

## D4 Bug Tracking and PM/Agile (Now)

- Labels, templates, triage guide, active tracker.
- PM and agile layer under `pm/agile/`: guides, templates, sprint records.

## D5 Demo Showcase (Now)

- Demo epics, stories, bugs. Board populated for showcase.

## v1.0.0 Process v2 (Now, milestone D5, epic #41)

- CI must-haves: secret scan, read-only token, SHA-pinned actions with Dependabot, dependency review, local checks (#43).
- Live roadmap page on n8n for every project (#44).
- Rules 20 to 29 and the two-session pattern (#42). Release notes: `docs/RELEASE_NOTES_v1.0.0.md`.

## D6 Template Ready (Future)

- Full clone-ready template. New projects start here.
