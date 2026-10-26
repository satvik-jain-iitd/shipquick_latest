# CI checks every project must have (research, 26 Oct 2026)

Question: which CI checks keep a child project of ShipQuick clean, and which only cost time?
Method: `~/.claude/skills/web-research/SKILL.md`. Tiers: A primary, B big data from a seller, C blog, S our own data.

## Sources
| Source | What it says | Tier | Confidence |
|---|---|---|---|
| GitHub Docs, "Security hardening for GitHub Actions" | "Pinning an action to a full length commit SHA is currently the only way to use an action as an immutable release." A tag can move. Dependabot does not alert on SHA-pinned actions, so pinned actions need a Dependabot `github-actions` update job. Give `GITHUB_TOKEN` minimal permissions | A | 0.9 that GitHub says this |
| OpenSSF Scorecard, default checks (via its README copies and Microsoft's .NET post) | Checks: Token-Permissions (read-only tokens, high risk), Branch-Protection (high), Pinned-Dependencies, CI-Tests, SAST, Dangerous-Workflow, Dependency-Update-Tool, Vulnerabilities, Security-Policy and more | A for "Scorecard checks it", C for the risk labels (Microsoft's) | 0.8 |
| ICST 2024 industrial case study, "Cost of Flaky Tests in CI" | Flaky tests took at least 2.5 percent of productive developer time in the studied project | A for that case | 0.6 in general |
| Our own data: job-search, PRs #1 to #10 | 19 inherited checks; 13 protected nothing we run. Red CI for weeks was ignored because it was never ours to fix. Cut to 6, all green | S | 0.9 for us |

Opposite view: more checks are not more safety. A check that never fails for a real reason trains everyone to
ignore red. Flaky checks cost real time. So every check below must protect this project, or it is removed.

## The must-have set (ShipQuick v0.5.0)
| # | Check | Protects against | Where |
|---|---|---|---|
| 1 | Tests run in CI | a change that breaks behaviour | `test` job, per project language |
| 2 | Lint and typecheck | broken code that tests miss | per project |
| 3 | Secret scan (gitleaks) | a key or token in a commit (rule 15) | `secret-scan` job |
| 4 | Read-only token by default (`permissions: contents: read`) | a hijacked workflow writing to the repo | workflow top |
| 5 | Actions pinned to full SHAs + Dependabot for `github-actions` | a moved tag running new code | every `uses:` |
| 6 | Dependency review on PRs | a new vulnerable package | `dependency-review` job |
| 7 | Hygiene: file size, merge markers (anchored to line start), markdown blocks, commit message, PR size 50 files, teammate block | the slow rot that makes review hard | existing jobs |
| 8 | Every check also runs on the Mac before a push (`scripts/check_local.sh`) | learning the same CI lesson twice (idea ID158) | pre-commit hook |

Limits: the whole CI stays under 10 minutes. Branch protection needs GitHub Pro on private repos, so the owner's
review is the gate there.

Sources: https://docs.github.com/en/enterprise-cloud@latest/actions/security-guides/security-hardening-for-github-actions ·
https://github.com/ossf/scorecard · https://devblogs.microsoft.com/nuget/openssf-scorecard-for-net-nuget/ ·
https://conf.researchr.org/details/icst-2024/icst-2024-industry/1/Cost-of-Flaky-Tests-in-CI-An-Industrial-Case-Study

## Notes for child projects (story #43, 26 Oct 2026)
- **Secret scan.** On a PR it reads only the PR's own commits. On a push it reads the whole history. A child with a long or forked
  history (job-search is a fork with 300+ upstream commits) must not go red on an old commit it cannot rewrite.
- **Dependency review needs the Dependency graph.** Without it the job warns and passes. On 26 Oct 2026 the probe returned
  HTTP 404 on this repo too, although it is public, and Dependabot alerts are off. So a green dependency-review means
  "skipped" until the job log shows the review step ran. Private repos on a free plan will keep warning. The owner turns the
  graph on in the repo settings (Advanced Security).
- **A fake key in a test is flagged like a real one.** Build it at run time. If an old commit still holds one, put its
  fingerprint in `.gitleaksignore` with a reason and a date when the line can go.
- **Fast on commit, full on push.** `scripts/check_local.sh secrets-staged` reads only staged files. The full scan runs on push.

