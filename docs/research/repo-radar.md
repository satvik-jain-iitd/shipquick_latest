# Radar log (rule 20)

One block per run. Never delete a row.

## 26 Oct 2026, story #43: secret scanning for git commits in CI
- Need: find a secret in a commit before it is merged, free, no account.
- Run: `scout.py --need "secret scanning for git commits in CI"`. The keyword search gave only unrelated repos (score 0, ignored).
- Adopted by name: `gitleaks/gitleaks`. MIT, about 30k stars, last push 23 Oct 2026, release v8.30.1 (GitHub API, tier A for the numbers).
  Named in `docs/research/ci-checks.md`.
- How it is used: the pinned Linux binary, SHA-256 checked in the `secret-scan` job, not `gitleaks-action` (that action needs a license key for
  organization accounts). Locally: `scripts/check_local.sh secrets` (`brew install gitleaks`).
- Result on this repo: full history, 38 commits, 0 findings.
- Confidence that it fits: 0.85. Test: a planted key must go red once on GitHub (shown in the PR).
