# Update Process

How upstream Material Design changes reach this repo. Manual, never automatic.

## Why Manual

- No runtime downloads. Builds work offline.
- Every update is reviewed before it lands.
- No surprise breakage from upstream.

## Steps

1. Pull the upstream repo locally.
2. Diff against the vendored copy in `design/material-design-3/`.
3. Copy changed guides. Never bulk-copy source.
4. Scan for brand-specific references. Sanitize.
5. Run tests: `pytest tests/`.
6. Commit: `design: sync Material Design updates (<date>)`.
7. Open PR `design/sync-<date>` to `dev`. Merge after CI green.

## What Gets Synced

- Getting-started and theming guides.
- New component overview docs.
- `REPOSITORIES.md` links.

## What Never Syncs

- Source code trees.
- Test and mock files.
- CI and infra configs.
- Changelogs.
