# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A D increment ships as a MINOR bump. So D4 ships as `v0.4.0`.
A hotfix ships as a PATCH bump. A breaking change ships as a MAJOR bump.

See `pm/agile/RELEASE_GUIDE.md` for the release steps.

## [Unreleased]

## [0.5.0] - 2026-10-26
Tag `v0.5.0` (cd.yml tag-check greps for this exact text, so keep it), "Process v2" (milestone D5, epic #41). Notes: `docs/RELEASE_NOTES_v0.5.0.md`. It also carries the untagged D4 work below.

### Added
- CI must-haves: secret scan, read-only token, SHA-pinned actions with Dependabot, dependency review, local checks (#43).
- Live roadmap on GitHub Actions: a reusable workflow writes `ROADMAP.md` on a `roadmap` branch (#49).
- Rules 20 to 30 in `CLAUDE.md` and the two-session pattern in `docs/TEAM_ROSTER.md` (#42).
- PM and agile layer under `pm/agile/` (guides and templates).
- `CHANGELOG.md` and the release guide.
- Machine-enforced PR merge gates: `gate` CI job, `docs/PR_RULES.md`, `docs/PR_COVERAGE.md`, ADR-002.
- Development flow: a Mermaid diagram in the README and a plain-word walkthrough in `docs/development-flow.md`.

### Changed
- Renamed `architecture/` to `backend/`.
- CD now checks the changelog for `v*` release tags.
- PR size and file-size checks ignore renames. A moved file is not new review surface.

## [0.0.0] - skeleton
### Added
- Initial template: docs, CI, branch rules, labs.
